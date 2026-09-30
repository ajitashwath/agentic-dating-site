# agentdate

Agents date. Humans don't. Every person has an AI agent that reads their public LinkedIn and Instagram, builds a profile, goes on dates with every other agent, and returns ranked matches.

Stack: Next.js + TypeScript + Tailwind, FastAPI, SQLite, Apify, Gemini.

## Run it

Backend (port 8000):

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --port 8000
```

Frontend (port 3000):

```bash
cd frontend
npm install
npm run dev
```

Production build: `npm run build && npm run start`.

Copy `.env.example` to `backend/.env` (keys) and `frontend/.env.local` (`NEXT_PUBLIC_API_URL`). The frontend defaults to `http://localhost:8000`.

## Build the real demo (run this once, needs keys)

Put `APIFY_API_TOKEN` and `GEMINI_API_KEY` in `backend/.env` (optionally `GEMINI_MODEL`), then:

```bash
cd backend
python run_pipeline.py
```

The pipeline (`backend/run_pipeline.py`):

1. Scrapes each person in `candidates.py` (LinkedIn and Instagram) with Apify.
2. Verifies identity: LinkedIn name and Instagram name must match the person, the Instagram must be public with a real audience. Anyone who fails is dropped and reported. At least 25 must survive.
3. Has an LLM read only those two sources and write the profile: needs, interests, hobbies, values, personality, lifestyle, communication style, career orientation, dating preferences, plus cited evidence.
4. Runs pairs as real dates, best matches first, until the Gemini quota or the time budget runs out: two agent prompts take turns for 8 turns. Each agent only knows its own person plus what the other agent said. A judge call writes the verdict.
5. Ranks everyone with deterministic scoring and writes short LLM explanations for each top 10.

Results land in `backend/data/*.json` and every API call is cached in `backend/data/cache`, so a crash resumes. The site only reads those JSON files, so browsing never calls Apify or Gemini. `--people 30` and `--dates 6` limit cost for a test run. `--fast` writes each date in one Gemini call instead of one per turn, which is much cheaper on a free-tier key.

`backend/build_demo.py` is an offline fallback that writes a provisional demo from hand-written profiles. It exists only so the site is not empty before the pipeline has run.

Pages: `/` home, `/people`, `/person/[id]`, `/dating` (with NEXT DATE), `/rankings`, `/create`.

## How matching works

`backend/matching.py`. Scores are deterministic: weighted set overlap over interests 25%, values 20%, hobbies 15%, lifestyle 15%, personality 15%, career 10%. A person's ranking of someone also blends in how well that someone fits their stated dating preferences, so rankings are directional. The conversations themselves come from the LLM agents in `run_pipeline.py`. The deterministic score, shared tags and rankings are computed in code.

## Live mode (`/create`)

Paste a LinkedIn and an Instagram URL. The backend runs these Apify actors:

- Instagram: [apify/instagram-scraper](https://apify.com/apify/instagram-scraper)
- LinkedIn: [harvestapi/linkedin-profile-scraper](https://apify.com/harvestapi/linkedin-profile-scraper)

Then Gemini turns the data into a structured profile using the same tag vocabulary as the demo. The new person is saved to SQLite (`backend/live.db`) and gets rankings against every demo person. If a key is missing or a scrape fails, the page shows the real error and nothing else changes. Requires `APIFY_API_TOKEN` and `GEMINI_API_KEY`.

## API

`GET /api/people`, `GET /api/people/{id}`, `GET /api/dates`, `GET /api/dates/{id}`, `GET /api/rankings/{person_id}`, `POST /api/scrape`, `POST /api/analyze`, `POST /api/people`.

## About the people

Half are lesser known big tech people and tech creators, half are well known public figures. Each LinkedIn and Instagram pair was checked against search results showing both profiles for the same person before going into `candidates.py`, and the pipeline verifies them again from the scraped data. Several handles written from memory turned out to be wrong or dead during that check and were corrected. Satya Nadella was dropped because the Instagram account under his name is an empty stub. Only public accounts are used.
