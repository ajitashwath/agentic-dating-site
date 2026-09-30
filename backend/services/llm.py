import json
import os
import re
import time

import httpx

VOCAB = """interests: AI, startups, technology, product, education, health, wellbeing, philosophy, psychology, leadership, writing, media, finance, investing, climate, philanthropy, design, sports, music, food, travel, learning, creators, marketing, science, family
hobbies: reading, running, meditation, podcasting, writing, cycling, gaming, photography, cooking, travel, hiking, gym, sailing, tennis, filming, cars, journaling, collecting, surfing
values: curiosity, authenticity, growth, service, impact, resilience, empathy, family, honesty, discipline, freedom, learning, generosity, optimism
personality: analytical, warm, driven, playful, reflective, bold, humble, energetic, calm, creative, direct
lifestyle: early riser, travel-heavy, family-first, structured days, public-facing, spontaneous, nature time, screen-heavy
communication_style: storyteller, direct, questioning, encouraging, data-driven, humorous, thoughtful, high-energy
career_orientation: founder, operator, executive, creator, author, investor, educator, advocate
dating_preferences: curious, ambitious, kind, funny, grounded, adventurous, intellectual, family-oriented, creative, driven, honest, calm"""

TAG_KEYS = ["interests", "hobbies", "values", "personality", "lifestyle", "communication_style", "career_orientation", "dating_preferences"]

TURNS = 8


# Free tier quotas are per model, so when one model is used up the next one in GEMINI_MODELS takes over.
model_state = {"index": 0}


class QuotaExhausted(RuntimeError):
    """The free tier daily request cap is used up, so retrying now is pointless."""


def gemini_contents(messages):
    """Maps chat style messages to Gemini: system text goes to systemInstruction, roles alternate user and model."""
    system = ""
    contents = []
    for m in messages:
        if m["role"] == "system" and not system and not contents:
            system = m["content"]
            continue
        role = "model" if m["role"] == "assistant" else "user"
        text = m["content"] if m["role"] != "system" else "Instruction for your next reply: " + m["content"]
        if contents and contents[-1]["role"] == role:
            contents[-1]["parts"][0]["text"] += "\n\n" + text
        else:
            contents.append({"role": role, "parts": [{"text": text}]})
    if not contents or contents[0]["role"] == "model":
        contents.insert(0, {"role": "user", "parts": [{"text": "Begin."}]})
    return system, contents


def chat(messages, as_json=False, temperature=0.7):
    key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not key:
        raise RuntimeError("GEMINI_API_KEY is not set. Add it to backend/.env to enable live analysis.")
    models = [m.strip() for m in (os.getenv("GEMINI_MODELS") or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")).split(",") if m.strip()]
    model = models[min(model_state["index"], len(models) - 1)]
    base = os.getenv("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta")
    system, contents = gemini_contents(messages)
    config = {"temperature": temperature}
    if as_json:
        config["responseMimeType"] = "application/json"
    if model.startswith("gemini-2.5"):
        config["thinkingConfig"] = {"thinkingBudget": 0}  # plain answers, faster and cheaper
    body = {"contents": contents, "generationConfig": config}
    if system:
        body["systemInstruction"] = {"parts": [{"text": system}]}

    last_error = "unknown error"
    for attempt in range(12):
        try:
            response = httpx.post(f"{base}/models/{model}:generateContent", headers={"x-goog-api-key": key}, json=body, timeout=90)
        except httpx.HTTPError as error:
            last_error = f"Could not reach Gemini: {error}"
            time.sleep(2 ** attempt)
            continue
        if response.status_code == 429 and "PerDay" in response.text:
            if model_state["index"] < len(models) - 1:
                model_state["index"] += 1  # switch to the next model and retry this request
                return chat(messages, as_json, temperature)
            raise QuotaExhausted("Gemini daily request quota is used up for this model. Enable billing on the key's Google AI project, use another model via GEMINI_MODEL, or wait for the quota to reset.")
        if response.status_code in (429, 500, 502, 503, 504):
            last_error = f"Gemini returned {response.status_code}"
            wait = re.search(r"retry in ([\d.]+)s", response.text)  # per-minute limits say how long to wait
            time.sleep(float(wait.group(1)) + 1 if wait else min(2 ** attempt, 30))
            continue
        if response.status_code >= 400:
            raise RuntimeError(f"Gemini returned {response.status_code}: {response.text[:300]}")
        data = response.json()
        candidates = data.get("candidates") or []
        parts = candidates[0].get("content", {}).get("parts", []) if candidates else []
        text = "".join(p.get("text", "") for p in parts).strip()
        if not text:
            reason = candidates[0].get("finishReason") if candidates else data.get("promptFeedback", {}).get("blockReason")
            raise RuntimeError(f"Gemini returned no text (reason: {reason})")
        if not as_json:
            return text
        text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M).strip()
        result = json.loads(text)
        if isinstance(result, list) and result and isinstance(result[0], dict):
            result = result[0]  # JSON mode sometimes wraps the object in a list
        if not isinstance(result, dict):
            raise RuntimeError("Gemini did not return a JSON object")
        return result
    raise RuntimeError(f"Gemini request failed after retries: {last_error}")


def analyze_person(linkedin, instagram):
    """Reads the two scraped sources and returns a structured profile with cited evidence."""
    system = (
        "You are a dating agent that builds a profile of one person using ONLY their public LinkedIn data and public Instagram data. "
        "Never use outside knowledge. Return JSON with keys: name, role, summary (one sentence), "
        "needs (3 to 4 short phrases: what this person seems to need from life and a partner, inferred from the data), "
        "linkedin_signals and instagram_signals (each 3 to 5 strings; every string must point at a concrete fact in that source, "
        "quoting a short phrase from it where possible), and each of these lists of 2 to 4 tags: interests, hobbies, values, "
        "personality, lifestyle, communication_style, career_orientation, dating_preferences. "
        "Pick tags from this vocabulary whenever one fits:\n" + VOCAB +
        "\nIf a source is thin, say so in its signals instead of inventing. Do not use long dashes."
    )
    data = chat([{"role": "system", "content": system},
                 {"role": "user", "content": json.dumps({"linkedin": linkedin, "instagram": instagram})[:14000]}],
                as_json=True, temperature=0.3)
    profile = {"summary": data.get("summary", ""), "needs": [str(t) for t in data.get("needs", [])][:5]}
    for key in TAG_KEYS:
        profile[key] = [str(t) for t in data.get(key, [])][:5]
    return {
        "name": data.get("name") or linkedin.get("name") or instagram.get("name"),
        "role": data.get("role") or linkedin.get("headline", ""),
        "profile": profile,
        "source_evidence": {
            "linkedin": [str(x) for x in data.get("linkedin_signals", [])],
            "instagram": [str(x) for x in data.get("instagram_signals", [])],
        },
    }


def describe(person):
    p = person["profile"]
    lines = [f"{person['name']}, {person['role']}.", f"Summary: {p['summary']}"]
    for key in ["needs"] + TAG_KEYS:
        if p.get(key):
            lines.append(f"{key.replace('_', ' ')}: {', '.join(p[key])}")
    lines.append("Evidence from LinkedIn: " + " | ".join(person["source_evidence"]["linkedin"]))
    lines.append("Evidence from Instagram: " + " | ".join(person["source_evidence"]["instagram"]))
    return "\n".join(lines)


def agent_turn(person, history, instruction):
    first = person["name"].split()[0]
    system = (
        f"You are {first}'s dating agent, on a first date with another person's dating agent. You represent {person['name']} and only them. "
        f"You know only the profile below about {first}. About the other side you know only what their agent says in this conversation. "
        "Speak in first person as the agent. Write 2 or 3 sentences of plain text. Cite concrete details from your person's profile. "
        "React to what the other agent just said, be honest about differences, and ask one real question that tests compatibility "
        "(needs, values, lifestyle, ambition, communication). Do not use long dashes.\n\nYOUR PERSON:\n" + describe(person)
    )
    messages = [{"role": "system", "content": system}]
    for line in history:
        messages.append({"role": "assistant" if line["speaker"] == person["id"] else "user", "content": line["text"]})
    messages.append({"role": "system", "content": instruction})
    return chat(messages)


def generate_date_single(person_a, person_b):
    """Cheaper variant: one call writes the whole date. Used with --fast when API quota is tight."""
    system = (
        f"Write a first date between two dating agents. Agent A represents {person_a['name']} and agent B represents {person_b['name']}. "
        "Each agent may only use facts from its own person's profile, and learns about the other person only from what the other agent says. "
        f"Return JSON: {{\"messages\": [{{\"speaker\": \"a\" or \"b\", \"text\": \"2 or 3 sentences\"}}], \"verdict\": two sentences, "
        "\"strengths\": 3 short strings, \"friction\": 2 or 3 short strings}. "
        f"Exactly {TURNS} alternating messages starting with a. Agents ask real questions, disagree honestly, and end by saying whether to have a second date. No long dashes."
    )
    user = "PERSON A:\n" + describe(person_a) + "\n\nPERSON B:\n" + describe(person_b)
    data = chat([{"role": "system", "content": system}, {"role": "user", "content": user}], as_json=True, temperature=0.7)
    history = []
    for m in data["messages"][:TURNS]:
        who = person_a if str(m.get("speaker", "")).lower() == "a" else person_b
        history.append({"speaker": who["id"], "agent": who["name"].split()[0] + "'s agent", "text": str(m["text"])})
    if len(history) < 4:
        raise RuntimeError("Gemini returned too few messages for the date")
    return {
        "messages": history,
        "verdict": data.get("verdict", ""),
        "strengths": [str(x) for x in data.get("strengths", [])],
        "friction": [str(x) for x in data.get("friction", [])],
    }


def generate_date(person_a, person_b):
    """Two agents take turns. Each call only sees its own person's profile plus the conversation so far."""
    history = []
    for i in range(TURNS):
        speaker = person_a if i % 2 == 0 else person_b
        if i == 0:
            instruction = "Open the date: introduce yourself and who you represent, then ask an opening question."
        elif i == TURNS - 2:
            instruction = "Start wrapping up: say what stood out to you and raise the biggest concern."
        elif i == TURNS - 1:
            instruction = "Give your closing words and say whether you would recommend a second date, and why."
        else:
            instruction = "Continue the date naturally."
        text = agent_turn(speaker, history, instruction)
        history.append({"speaker": speaker["id"], "agent": speaker["name"].split()[0] + "'s agent", "text": text})

    transcript = "\n".join(f"{m['agent']}: {m['text']}" for m in history)
    judge = chat([
        {"role": "system", "content": (
            "You judge a first date between two dating agents. Use the transcript and both profiles. Return JSON: "
            "{\"verdict\": two sentences, \"strengths\": 3 short strings, \"friction\": 2 or 3 short strings}. No long dashes.")},
        {"role": "user", "content": f"PERSON A:\n{describe(person_a)}\n\nPERSON B:\n{describe(person_b)}\n\nTRANSCRIPT:\n{transcript}"},
    ], as_json=True, temperature=0.3)
    return {
        "messages": history,
        "verdict": judge.get("verdict", ""),
        "strengths": [str(x) for x in judge.get("strengths", [])],
        "friction": [str(x) for x in judge.get("friction", [])],
    }


def explain_match(person_a, person_b, score):
    system = (
        "In 2 or 3 sentences, explain to person a why person b is a good or weak match for them, citing specifics from both profiles. "
        "A deterministic score is given. Return JSON: {\"why\": \"...\"}. No long dashes."
    )
    user = f"A:\n{describe(person_a)}\n\nB:\n{describe(person_b)}\n\nScore: {score}%"
    return chat([{"role": "system", "content": system}, {"role": "user", "content": user}], as_json=True, temperature=0.3)["why"]
