import random

WEIGHTS = {
    "interests": 0.25,
    "values": 0.20,
    "hobbies": 0.15,
    "lifestyle": 0.15,
    "personality": 0.15,
    "career_orientation": 0.10,
}

# Each dating preference maps to traits a candidate can show in other parts of their profile.
WANT_TRAITS = {
    "curious": ["curiosity", "learning"],
    "ambitious": ["driven", "founder", "executive", "operator"],
    "kind": ["empathy", "warm", "generosity", "service"],
    "funny": ["playful", "humorous"],
    "grounded": ["calm", "humble", "reflective", "family"],
    "adventurous": ["travel-heavy", "spontaneous", "bold"],
    "intellectual": ["analytical", "philosophy", "science", "data-driven"],
    "family-oriented": ["family", "family-first"],
    "creative": ["creative", "design", "creators"],
    "driven": ["driven", "discipline"],
    "honest": ["honesty", "authenticity", "direct"],
    "calm": ["calm", "meditation", "reflective"],
}


def overlap(a, b):
    if not a or not b:
        return 0.0
    return len(set(a) & set(b)) / min(len(a), len(b))


def all_traits(profile):
    traits = set()
    for key in ["interests", "hobbies", "values", "personality", "lifestyle", "communication_style", "career_orientation"]:
        traits.update(profile.get(key, []))
    return traits


def want_fit(profile_a, profile_b):
    wants = profile_a.get("dating_preferences", [])
    if not wants:
        return 0.0
    traits = all_traits(profile_b)
    hits = [w for w in wants if traits & set(WANT_TRAITS.get(w, []))]
    return len(hits) / len(wants)


def shared_traits(profile_a, profile_b):
    shared = {}
    for key in WEIGHTS:
        both = [x for x in profile_a.get(key, []) if x in profile_b.get(key, [])]
        if both:
            shared[key] = both
    return shared


def base_score(profile_a, profile_b):
    return sum(overlap(profile_a.get(k, []), profile_b.get(k, [])) * w for k, w in WEIGHTS.items())


def directional_score(profile_a, profile_b):
    """How well B fits what A wants. Not symmetric on purpose."""
    raw = 0.7 * base_score(profile_a, profile_b) + 0.3 * want_fit(profile_a, profile_b)
    return round(56 + 42 * min(raw * 1.5, 1.0))


def mutual_score(profile_a, profile_b):
    return round((directional_score(profile_a, profile_b) + directional_score(profile_b, profile_a)) / 2)


def first_name(person):
    return person["name"].split()[0]


def join(items, limit=3):
    items = list(items)[:limit]
    if len(items) <= 1:
        return "".join(items)
    return ", ".join(items[:-1]) + " and " + items[-1]


def find_friction(a, b):
    pa, pb = a["profile"], b["profile"]
    only_a = [x for x in pa["lifestyle"] if x not in pb["lifestyle"]]
    only_b = [x for x in pb["lifestyle"] if x not in pa["lifestyle"]]
    friction = []
    if only_a and only_b:
        friction.append(f"{first_name(a)} leans {only_a[0]} while {first_name(b)} leans {only_b[0]}")
    ca = [x for x in pa["career_orientation"] if x not in pb["career_orientation"]]
    cb = [x for x in pb["career_orientation"] if x not in pa["career_orientation"]]
    if ca and cb:
        friction.append(f"different career paths ({ca[0]} versus {cb[0]})")
    pa_pers = [x for x in pa["personality"] if x not in pb["personality"]]
    pb_pers = [x for x in pb["personality"] if x not in pa["personality"]]
    if pa_pers and pb_pers:
        friction.append(f"a {pa_pers[0]} streak meeting a {pb_pers[0]} one")
    if not friction:
        friction.append("very similar schedules, so someone has to protect downtime")
    return friction


def make_verdict(score, a, b):
    fa, fb = first_name(a), first_name(b)
    if score >= 88:
        return f"Excellent match. {fa} and {fb} share real substance and the conversation flowed without effort."
    if score >= 80:
        return f"Strong compatibility. {fa} and {fb} overlap where it matters and can grow from the differences."
    if score >= 72:
        return f"Promising. {fa} and {fb} have enough common ground for a second date, with a few things to negotiate."
    return f"Interesting but uneven. {fa} and {fb} would need to work at it, though curiosity could carry them."


def make_date(a, b):
    """Deterministic scripted date built from the two structured profiles."""
    pa, pb = a["profile"], b["profile"]
    fa, fb = first_name(a), first_name(b)
    rng = random.Random(a["id"] + b["id"])
    shared = shared_traits(pa, pb)
    shared_flat = [x for key in ["interests", "values", "hobbies", "lifestyle", "personality"] for x in shared.get(key, [])]
    shared_interest = shared.get("interests", shared_flat)[:2]
    friction = find_friction(a, b)
    score = mutual_score(pa, pb)

    opener = rng.choice([
        f"Hello {fb}'s agent. {fa} is {a['role']}. From what I can read, {fa} comes across as {join(pa['personality'], 2)}. What is {fb} like day to day?",
        f"Nice to meet you. I represent {fa}, {a['role']}. The public signals say {join(pa['personality'], 2)}. Tell me about {fb}.",
        f"Hi. {fa} works as {a['role']} and reads as {join(pa['personality'], 2)}. I would love to hear how {fb} spends a normal week.",
    ])
    reply = rng.choice([
        f"{fb} is {b['role']}. I read {fb} as {join(pb['personality'], 2)}, with a strong pull towards {join(pb['interests'], 3)}. How does {fa} spend time outside work?",
        f"Happy to. {fb}, {b['role']}, shows up as {join(pb['personality'], 2)} and keeps returning to {join(pb['interests'], 3)}. What fills {fa}'s free time?",
    ])
    if shared_interest:
        third = f"{fa} spends real energy on {join(pa['interests'], 3)}, and hobbies like {join(pa['hobbies'], 2)}. I see {join(shared_interest, 2)} in both of your worlds."
    else:
        third = f"{fa} spends real energy on {join(pa['interests'], 3)}, and hobbies like {join(pa['hobbies'], 2)}. I do not see much overlap with {fb}'s topics yet, but that may be a good thing."
    fourth = rng.choice([
        f"That lines up. {fb} approaches it in a {join(pb['communication_style'], 2)} way, and outside work you will find {fb} into {join(pb['hobbies'], 2)}.",
        f"Interesting. For {fb} it shows up as {join(pb['communication_style'], 2)} conversations, and free time goes to {join(pb['hobbies'], 2)}.",
    ])
    fifth = f"{fa} talks in a {join(pa['communication_style'], 2)} style and cares most about {join(pa['values'], 3)}. Day to day that means {join(pa['lifestyle'], 2)}."
    shared_values = shared.get("values", [])
    if shared_values:
        sixth = f"{join(shared_values, 2).capitalize()} matter to both of them. {fb} lives by {join(pb['values'], 3)}. One difference I notice: {friction[0]}."
    else:
        sixth = f"{fb} lives by {join(pb['values'], 3)}, which differs a bit from {fa}. The main friction I notice: {friction[0]}."
    seventh = f"{fa} is looking for someone {join(pa['dating_preferences'], 3)}. Based on what I know, {fb} fits {round(want_fit(pa, pb) * 100)}% of that list."
    eighth = f"{fb} wants someone {join(pb['dating_preferences'], 3)}, and {fa} matches {round(want_fit(pb, pa) * 100)}% of that. {rng.choice(['I would recommend a second date.', 'I think they should meet in person.', 'This is worth a proper coffee.'])}"

    texts = [opener, reply, third, fourth, fifth, sixth, seventh, eighth]
    messages = []
    for i, text in enumerate(texts):
        who = a if i % 2 == 0 else b
        messages.append({"speaker": who["id"], "agent": f"{first_name(who)}'s agent", "text": text})

    strengths = [f"Shared {key.replace('_', ' ')}: {join(vals, 3)}" for key, vals in shared.items()][:4]
    if not strengths:
        strengths = ["Complementary profiles that could broaden each other's worlds"]

    return {
        "id": pair_id(a["id"], b["id"]),
        "person_a": a["id"],
        "person_b": b["id"],
        "messages": messages,
        "compatibility": score,
        "a_to_b": directional_score(pa, pb),
        "b_to_a": directional_score(pb, pa),
        "shared_interests": shared.get("interests", []),
        "shared": shared,
        "strengths": strengths,
        "friction": friction[:3],
        "verdict": make_verdict(score, a, b),
    }


def pair_id(id_a, id_b):
    first, second = sorted([id_a, id_b])
    return f"{first}_{second}"


def explain_match(a, b):
    """Why B ranks where it does for A, in plain words."""
    pa, pb = a["profile"], b["profile"]
    fb = first_name(b)
    shared = shared_traits(pa, pb)
    parts = []
    if shared:
        bits = [f"{key.replace('_', ' ')} ({join(vals, 3)})" for key, vals in list(shared.items())[:3]]
        parts.append(f"You and {fb} overlap on " + "; ".join(bits) + ".")
    else:
        parts.append(f"You and {fb} share few tags, so this match rests on how well they fit what you want.")
    wants = pa.get("dating_preferences", [])
    traits = all_traits(pb)
    hits = [w for w in wants if traits & set(WANT_TRAITS.get(w, []))]
    if hits:
        parts.append(f"Your agent looks for someone {join(hits, 3)}, and {fb}'s profile shows that.")
    parts.append(f"Possible friction: {find_friction(a, b)[0]}.")
    return " ".join(parts)


def rank_person(person, everyone):
    rows = []
    for other in everyone:
        if other["id"] == person["id"]:
            continue
        rows.append({
            "person_id": other["id"],
            "score": directional_score(person["profile"], other["profile"]),
            "mutual": mutual_score(person["profile"], other["profile"]),
            "date_id": pair_id(person["id"], other["id"]),
            "why": explain_match(person, other),
        })
    rows.sort(key=lambda r: (-r["score"], -r["mutual"], r["person_id"]))
    for i, row in enumerate(rows):
        row["rank"] = i + 1
    return rows
