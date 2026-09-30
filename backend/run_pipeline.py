"""Builds the real demo: scrape, verify, analyze, date, rank.

    python run_pipeline.py                 # everything (needs APIFY_API_TOKEN and GEMINI_API_KEY)
    python run_pipeline.py --people 30     # keep the first 30 verified people
    python run_pipeline.py --dates 6       # smoke test with only 6 dates

Every step caches to data/cache, so a crash or Ctrl+C just resumes where it stopped.
The website itself only reads the JSON this script writes, so it never calls an API when browsing.
"""
import argparse
import json
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from candidates import CANDIDATES  # noqa: E402
from matching import make_date, mutual_score, rank_person  # noqa: E402
from services import apify, llm  # noqa: E402
from services.identity import check_identity  # noqa: E402

DATA = Path(os.getenv("DATA_DIR", Path(__file__).parent / "data"))
CACHE = DATA / "cache"
CACHE.mkdir(parents=True, exist_ok=True)

MIN_FOLLOWERS = 500  # rejects empty placeholder accounts that copy a famous name


def cached(name, make):
    path = CACHE / name
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    value = make()
    path.write_text(json.dumps(value, indent=1, ensure_ascii=False), encoding="utf-8")
    return value


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def collect(candidate):
    name, linkedin, instagram = candidate
    try:
        li = cached(f"li-{slug(name)}.json", lambda: apify.scrape_linkedin(linkedin))
        ig = cached(f"ig-{slug(name)}.json", lambda: apify.scrape_instagram(instagram))
    except Exception as error:
        print(f"  DROP {name}: scrape failed: {error}")
        return None
    check = check_identity(name, li, ig)
    if not check["ok"]:
        print(f"  DROP {name}: " + "; ".join(n for n in check["notes"] if "mismatch" in n or "only" in n))
        return None
    print(f"  OK   {name}")
    return {"name": name, "linkedin": linkedin, "instagram": instagram, "li": li, "ig": ig, "verification": check["notes"]}


def analyze(item):
    def run():
        return llm.analyze_person(item["li"], item["ig"])
    try:
        result = cached(f"profile-{slug(item['name'])}.json", run)
    except llm.QuotaExhausted as error:
        sys.exit(f"Stopped while analyzing {item['name']}: {error} Finished profiles are cached, rerun to resume.")
    result["name"] = item["name"]  # keep the roster spelling, the analysis may add titles
    return result


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # scraped names and errors can contain emoji
    parser = argparse.ArgumentParser()
    parser.add_argument("--people", type=int, default=36, help="keep at most this many verified people")
    parser.add_argument("--dates", type=int, default=0, help="only generate this many dates (smoke test)")
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--scrape-workers", type=int, default=3, help="Apify free plans cap concurrent runs")
    parser.add_argument("--budget", type=float, default=0, help="stop calling Gemini for dates after this many minutes")
    parser.add_argument("--fast", action="store_true", help="one Gemini call per date instead of one per turn")
    args = parser.parse_args()

    # Fail fast on a missing key or a wrong model name instead of after half an hour of scraping.
    if not os.getenv("APIFY_API_TOKEN"):
        sys.exit("APIFY_API_TOKEN is not set. Put it in backend/.env")
    try:
        llm.chat([{"role": "user", "content": "Reply with the single word ok."}])
    except Exception as error:
        model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        sys.exit(f"Gemini preflight failed (model {model}): {error}. Check GEMINI_API_KEY, or set GEMINI_MODEL to a model your key can use.")

    print("1/5 scraping and verifying identities")
    with ThreadPoolExecutor(args.scrape_workers) as pool:
        collected = [c for c in pool.map(collect, CANDIDATES) if c][: args.people]
    if len(collected) < 25:
        print(f"Only {len(collected)} people passed verification, the brief needs at least 25. Add candidates to candidates.py.")
        sys.exit(1)

    print(f"2/5 analyzing {len(collected)} people")
    with ThreadPoolExecutor(args.workers) as pool:
        profiles = list(pool.map(analyze, collected))

    people = []
    for i, (item, prof) in enumerate(zip(collected, profiles)):
        people.append({
            "id": f"person-{i + 1:03d}",
            "name": item["name"],
            "role": prof["role"],
            "linkedin": item["linkedin"],
            "instagram": item["instagram"],
            "profile": prof["profile"],
            "source_evidence": prof["source_evidence"],
            "verification": item["verification"],
        })

    pairs = [(people[i], people[j]) for i in range(len(people)) for j in range(i + 1, len(people))]
    # Best pairs first, so if quota runs out the dates people see first are the real ones.
    pairs.sort(key=lambda pr: -mutual_score(pr[0]["profile"], pr[1]["profile"]))
    if args.dates:
        pairs = pairs[: args.dates]
    print(f"3/5 agents dating: {len(pairs)} dates, 8 turns each")

    quota = {"out": False}
    deadline = time.time() + args.budget * 60 if args.budget else None

    def date(pair):
        a, b = pair
        base = make_date(a, b)  # deterministic score, shared tags and ids
        base["generated_by"] = "template"
        name = f"date-{slug(a['name'])}--{slug(b['name'])}.json"
        live = None
        if deadline and time.time() > deadline:
            quota["out"] = True
        if (CACHE / name).exists() or not quota["out"]:
            try:
                live = cached(name, lambda: (llm.generate_date_single if args.fast else llm.generate_date)(a, b))
            except llm.QuotaExhausted as error:
                if not quota["out"]:
                    print(f"  QUOTA: {error} Remaining pairs get a labeled scripted preview.")
                quota["out"] = True
            except Exception as error:
                print(f"  date failed for {a['name']} and {b['name']}: {error}")
        if live:
            base["messages"] = live["messages"]
            base["verdict"] = live["verdict"] or base["verdict"]
            base["strengths"] = live["strengths"] or base["strengths"]
            base["friction"] = live["friction"] or base["friction"]
            base["generated_by"] = "gemini"
        return base

    with ThreadPoolExecutor(args.workers) as pool:
        dates = list(pool.map(date, pairs))

    print("4/5 ranking")
    by_id = {p["id"]: p for p in people}
    rankings = {}
    for person in people:
        rows = rank_person(person, people)

        def explain(row, person=person):
            if row["rank"] > 10:
                return row  # deterministic explanation is kept below the top 10 to save calls
            other = by_id[row["person_id"]]
            name = f"why-{slug(person['name'])}--{slug(other['name'])}.json"
            if not (CACHE / name).exists() and quota["out"]:
                return row
            try:
                row["why"] = cached(name, lambda: {"why": llm.explain_match(person, other, row["score"])})["why"]
            except llm.QuotaExhausted:
                quota["out"] = True
            except Exception as error:
                print(f"  explanation failed for {person['name']} to {other['name']}: {error}")
            return row

        with ThreadPoolExecutor(args.workers) as pool:
            rankings[person["id"]] = list(pool.map(explain, rows))

    print("5/5 writing site data")
    (DATA / "demo_people.json").write_text(json.dumps(people, indent=2, ensure_ascii=False), encoding="utf-8")
    (DATA / "demo_dates.json").write_text(json.dumps(dates, indent=1, ensure_ascii=False), encoding="utf-8")
    (DATA / "demo_rankings.json").write_text(json.dumps(rankings, indent=1, ensure_ascii=False), encoding="utf-8")
    real = sum(1 for d in dates if d["generated_by"] == "gemini")
    print(f"done: {len(people)} people, {len(dates)} dates ({real} written by Gemini agents, {len(dates) - real} scripted previews)")
    if real < len(dates):
        print("Rerun the same command once Gemini quota is available, cached work is reused and previews are replaced.")


if __name__ == "__main__":
    main()
