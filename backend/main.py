import json
import os
import re
import sqlite3
import uuid
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

from matching import make_date, pair_id, rank_person  # noqa: E402
from services import apify, llm  # noqa: E402
from services.identity import check_identity  # noqa: E402

BASE = Path(__file__).parent
DATA = Path(os.getenv("DATA_DIR", BASE / "data"))
# Vercel functions can only write to /tmp, so people added through /create are kept there (they reset on cold starts).
DB = Path(os.getenv("DB_PATH") or ("/tmp/live.db" if os.getenv("VERCEL") else BASE / "live.db"))

app = FastAPI(title="Agent Dating")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Demo data is precomputed so browsing never depends on Apify, Gemini or the internet.
demo_people = json.loads((DATA / "demo_people.json").read_text(encoding="utf-8"))
# Only conversations the Gemini agents actually had are served. Scripted placeholders are never shown as dates.
demo_dates = {d["id"]: d for d in json.loads((DATA / "demo_dates.json").read_text(encoding="utf-8")) if d.get("generated_by") != "template"}
demo_rankings = json.loads((DATA / "demo_rankings.json").read_text(encoding="utf-8"))

LINKEDIN_RE = re.compile(r"^https?://([a-z]{2,3}\.)?linkedin\.com/in/[\w\-%]+/?(\?.*)?$", re.I)
INSTAGRAM_RE = re.compile(r"^https?://(www\.)?instagram\.com/[\w.]+/?(\?.*)?$", re.I)
LIST_KEYS = ["interests", "hobbies", "values", "personality", "lifestyle", "communication_style", "career_orientation", "dating_preferences"]


def db():
    con = sqlite3.connect(DB)
    con.execute("create table if not exists people (id text primary key, body text not null)")
    return con


def live_people():
    con = db()
    rows = con.execute("select body from people order by rowid").fetchall()
    con.close()
    return [json.loads(r[0]) for r in rows]


def all_people():
    return demo_people + live_people()


def find_person(person_id):
    for p in all_people():
        if p["id"] == person_id:
            return p
    raise HTTPException(404, f"No person with id {person_id}")


@app.get("/api/health")
def health():
    return {"ok": True, "people": len(all_people())}


@app.get("/api/people")
def get_people():
    return all_people()


@app.get("/api/people/{person_id}")
def get_person(person_id: str):
    return find_person(person_id)


@app.get("/api/dates")
def get_dates():
    # Summaries only, the full conversation comes from /api/dates/{id}.
    keys = ["id", "person_a", "person_b", "compatibility"]
    return [{k: d[k] for k in keys} for d in demo_dates.values()]


@app.get("/api/dates/{date_id}")
def get_date(date_id: str):
    if date_id in demo_dates:
        return demo_dates[date_id]
    # Not precomputed, so at least one side is a live person. The agents date on demand.
    people = {p["id"]: p for p in all_people()}
    for a in people.values():
        for b in people.values():
            if a["id"] != b["id"] and pair_id(a["id"], b["id"]) == date_id:
                first, second = sorted([a, b], key=lambda p: p["id"])
                date = make_date(first, second)
                try:
                    live = llm.generate_date_single(first, second)
                except Exception as error:
                    raise HTTPException(502, f"The agents could not date right now: {error}")
                date["messages"] = live["messages"]
                date["verdict"] = live["verdict"] or date["verdict"]
                date["strengths"] = live["strengths"] or date["strengths"]
                date["friction"] = live["friction"] or date["friction"]
                return date
    raise HTTPException(404, f"No date with id {date_id}")


def with_date_links(person_id, rows):
    # A demo pair only links to a date if the agents really had one. Pairs with a live person are dated on demand.
    for row in rows:
        live_pair = person_id.startswith("live-") or row["person_id"].startswith("live-")
        row["date_id"] = row["date_id"] if live_pair or row["date_id"] in demo_dates else None
    return rows


@app.get("/api/rankings/{person_id}")
def get_rankings(person_id: str):
    person = find_person(person_id)
    live = live_people()
    if person_id not in demo_rankings:
        return with_date_links(person_id, rank_person(person, demo_people + live))
    rows = [dict(r) for r in demo_rankings[person_id]]
    if live:
        # Keep the precomputed Gemini explanations for demo people and add computed rows for live people.
        rows += [r for r in rank_person(person, demo_people + live) if r["person_id"].startswith("live-")]
        rows.sort(key=lambda r: (-r["score"], -r["mutual"], r["person_id"]))
        for i, row in enumerate(rows):
            row["rank"] = i + 1
    return with_date_links(person_id, rows)


@app.post("/api/scrape")
def scrape(body: dict):
    source, url = body.get("source"), (body.get("url") or "").strip()
    if source == "linkedin" and not LINKEDIN_RE.match(url):
        raise HTTPException(400, "That does not look like a LinkedIn profile URL. Expected https://www.linkedin.com/in/username")
    if source == "instagram" and not INSTAGRAM_RE.match(url):
        raise HTTPException(400, "That does not look like an Instagram profile URL. Expected https://www.instagram.com/username")
    if source not in ("linkedin", "instagram"):
        raise HTTPException(400, "source must be linkedin or instagram")
    try:
        return apify.scrape_linkedin(url) if source == "linkedin" else apify.scrape_instagram(url)
    except Exception as error:
        raise HTTPException(502, str(error))


@app.post("/api/analyze")
def analyze(body: dict):
    linkedin, instagram = body.get("linkedin") or {}, body.get("instagram") or {}
    if not linkedin.get("name") or not instagram.get("name"):
        raise HTTPException(400, "Both a LinkedIn and an Instagram scrape are required")
    identity = check_identity(linkedin["name"], linkedin, instagram, min_followers=0)
    if not identity["ok"]:
        raise HTTPException(400, "These two profiles do not look like the same person. " + "; ".join(n for n in identity["notes"] if "mismatch" in n))
    try:
        person = llm.analyze_person(linkedin, instagram)
    except Exception as error:
        raise HTTPException(502, str(error))
    person["linkedin"] = linkedin.get("url", "")
    person["instagram"] = instagram.get("url", "")
    person["verification"] = identity["notes"]
    return person


@app.post("/api/people")
def add_person(body: dict):
    profile = body.get("profile") or {}
    if not body.get("name") or not profile.get("summary") or any(not isinstance(profile.get(k), list) for k in LIST_KEYS):
        raise HTTPException(400, "name and a complete profile are required")
    for existing in live_people():
        if body.get("linkedin") and existing["linkedin"] == body["linkedin"]:
            return existing  # pasting the same person twice returns the saved one
    person = {
        "id": f"live-{uuid.uuid4().hex[:8]}",
        "name": body["name"],
        "role": body.get("role", ""),
        "linkedin": body.get("linkedin", ""),
        "instagram": body.get("instagram", ""),
        "profile": profile,
        "source_evidence": body.get("source_evidence") or {"linkedin": [], "instagram": []},
        "verification": body.get("verification") or [],
        "live": True,
    }
    con = db()
    con.execute("insert into people values (?, ?)", (person["id"], json.dumps(person)))
    con.commit()
    con.close()
    return person
