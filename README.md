# agentdate

**Agents date. Humans don't.**

Every person on agentdate is represented by an AI agent. The agent reads two public sources, the person's LinkedIn and their public Instagram, and nothing else. It works out who they are: what they need, what they're into, how they talk, what they'd want in a partner. Then it goes on dates with other people's agents, on their behalf, and the site ranks who fits whom.

It was built for a three hour challenge, so it favours things that actually run over things that look clever.

## What's in the demo

- **34 real people**, each with a LinkedIn and a public Instagram that belong to the same person. About a third are lesser known people in big tech and tech creators (Adam Mosseri, Scott Hanselman, Jeff Su, Kevin Stratvert and so on), the rest are well known public figures.
- **A profile page per person** with the agent's read: needs, interests, hobbies, values, personality, lifestyle, communication style, career orientation and dating preferences. Every profile shows the evidence it came from, split into LinkedIn signals and Instagram signals, and an identity check card.
- **Real agent dates.** Two agents talk for eight turns, each one only knowing its own person plus whatever the other agent says. A judge then writes a verdict, strengths and friction.
- **Rankings for everyone**, with a plain reason for each match. Rankings are directional: who Jeff ranks first doesn't have to rank Jeff first.
- **A create page.** Paste a LinkedIn and an Instagram link, and it scrapes, checks they're the same person, builds the profile and ranks them against everyone. It fails loudly and honestly if something goes wrong.

### What's not finished

Only some pairs have had a real date so far. The rest simply don't offer one ("Not dated yet" in the rankings) instead of showing a fake. The reason is boring: my Gemini key is on the free tier, which allows roughly 20 requests per model per day, and dating every pair takes hundreds. Run the pipeline again with a billed key and it fills in the gaps without redoing anything it already finished.

## How it works

```
LinkedIn + Instagram (public)
        |   Apify actors
        v
   raw profile data
        |   identity check: names match, Instagram is public with a real audience
        v
   Gemini reads it  ->  structured profile + cited evidence
        |
        v
   agent A  <-- 8 turns -->  agent B      (one Gemini call per turn)
        |
        v
   deterministic score + Gemini explanation  ->  rankings
```

A few decisions worth explaining:

- **Identity check.** Searching from memory gave me wrong Instagram handles more than once (one "official" account turned out to be an empty stub with 6 followers). So after scraping, the pipeline requires the LinkedIn name and Instagram name to match the person, and the Instagram to be public with at least 500 followers. Anyone who fails is dropped and reported. Two people were dropped this way: one Instagram handle didn't resolve, one account is private.
- **Two sources only.** The agents never get outside knowledge. The prompts say so, and the evidence shown on each profile quotes the scraped bio, headline and posts.
- **Scoring isn't left to the LLM.** Compatibility is weighted set overlap over shared tags: interests 25%, values 20%, hobbies 15%, lifestyle 15%, personality 15%, career 10%. A person's ranking of someone also blends in how well that someone fits their stated dating preferences, which is what makes it directional. Gemini only explains the result.
- **The site never calls an API while you browse.** Profiles, dates and rankings are precomputed into JSON (`backend/data/`). Apify and Gemini are only used by the pipeline and by the create page.
- **Nothing is faked.** If Apify or Gemini fails, you see the real error, and the precomputed demo keeps working.

## Tech

| Part | What |
| --- | --- |
| Scraping | Apify actors [`harvestapi/linkedin-profile-scraper`](https://apify.com/harvestapi/linkedin-profile-scraper) and [`apify/instagram-scraper`](https://apify.com/apify/instagram-scraper), called through Apify's run-sync REST endpoint with `httpx` |
| LLM | Gemini over plain REST (no SDK). Model rotation so each model's separate free quota gets used |
| Backend | Python, FastAPI, SQLite (only for people added through `/create`) |
| Frontend | Next.js 14, TypeScript, Tailwind |

## Run it locally

You need Python 3.11+ and Node 18+.

```bash
# backend, http://127.0.0.1:8000
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --port 8000
```

```bash
# frontend, http://localhost:3000
cd frontend
npm install
echo NEXT_PUBLIC_API_URL=http://127.0.0.1:8000 > .env.local
npm run dev
```

The demo works with no keys at all. To use the create page or rebuild the data, add `backend/.env` (see `.env.example`):

```
GEMINI_API_KEY=...
GEMINI_MODELS=gemini-flash-lite-latest,gemini-flash-latest
APIFY_API_TOKEN=...
```

`GEMINI_MODELS` is a comma separated list. When one model's daily quota runs out the next one takes over.

## Rebuild the data

The roster lives in `backend/candidates.py`. To scrape, verify, analyze, date and rank everyone:

```bash
cd backend
python run_pipeline.py --fast
```

| Flag | What it does |
| --- | --- |
| `--fast` | One Gemini call per date instead of one per turn. Much cheaper, slightly less "live" |
| `--people 30` | Keep at most this many verified people |
| `--dates 6` | Only date this many pairs, good for a cheap test |
| `--budget 7` | Stop calling Gemini for dates after 7 minutes, then write what exists |
| `--workers 8` | Parallel Gemini calls (scraping uses 3, free Apify plans cap concurrent runs) |

Pairs are dated best match first, so if quota runs out the dates you see first are the real ones. Every Apify and Gemini result is cached in `backend/data/cache/`, so a crash or a rerun picks up where it stopped. `backend/build_demo.py` is an old offline fallback that writes a provisional demo from hand-written profiles, only useful if the pipeline has never run.

## API

| Endpoint | Purpose |
| --- | --- |
| `GET /api/people`, `GET /api/people/{id}` | People and their profiles |
| `GET /api/dates`, `GET /api/dates/{id}` | Real agent dates and their full conversations |
| `GET /api/rankings/{person_id}` | Ranked matches with explanations |
| `POST /api/scrape` | Scrape one LinkedIn or Instagram URL through Apify |
| `POST /api/analyze` | Identity check, then Gemini builds the profile |
| `POST /api/people` | Save a created person |

## Project layout

```
backend/
  main.py            API
  matching.py        scoring, rankings, template helpers
  run_pipeline.py    scrape, verify, analyze, date, rank
  candidates.py      the roster of LinkedIn and Instagram links
  services/          apify.py, llm.py (Gemini), identity.py
  data/              precomputed people, dates, rankings (JSON)
frontend/
  app/               pages: home, people, person, dating, rankings, create
  components/        portraits, chat, profile analysis
vercel.json          one project, two services
```

## Deploy on Vercel

`vercel.json` defines two services in one project: `backend` (FastAPI) and `frontend` (Next.js). `/api/*` goes to the backend and everything else to the frontend, so both share one domain and the frontend calls `/api/...` on its own origin.

Set `GEMINI_API_KEY`, `GEMINI_MODELS` and `APIFY_API_TOKEN` as project environment variables, and leave `NEXT_PUBLIC_API_URL` unset. People added through `/create` are stored in `/tmp` on Vercel, so they disappear on cold starts, while the precomputed demo ships with the backend.

## Honest limitations

- Not every pair has had a real date yet, see above.
- The profiles are only as good as two public pages. A thin Instagram gives a thin read, and the agent says so instead of inventing things.
- Portraits are coloured monograms, not photos. I didn't want to hotlink real people's pictures.
- Scraping can be slow (several seconds per profile), and on Vercel a long scrape may hit the function time limit.
- The roster is public figures and creators who post publicly on purpose. Only public accounts are used.
