# Submission notes

## Overall explanation (under 200 characters)

Every person gets an AI agent that reads only their LinkedIn and Instagram, builds a profile, dates other agents turn by turn, and returns a ranked list of best matches.

## Technical section (under 500 characters)

Apify actors: harvestapi/linkedin-profile-scraper for LinkedIn and apify/instagram-scraper for Instagram, called from FastAPI with httpx. Both scrapes are cross-checked (names match, Instagram public with real followers). Gemini turns the raw data into a structured profile, then two agent prompts date turn by turn. Scoring is deterministic set overlap. Next.js and SQLite on top.

## Video script (3 minutes)

1. 0:00 Home page. "Every person has an agent. It reads exactly two sources, LinkedIn and Instagram." Show the counts.
2. 0:20 People page, click a lesser known person (for example Jeff Su). Show the Identity check card, the LinkedIn and Instagram signals, Needs, Interests, Hobbies, and the Agent interpretation.
3. 1:00 Dating page. Let the first date play in full so the turn by turn conversation is visible. Point out each agent only knows its own person. Show compatibility, shared interests, friction, verdict. Press NEXT DATE once.
4. 2:00 Rankings page. Pick a person, click the top match, read why, click View date. Then open the same pair from the other side to show rankings are directional.
5. 2:30 Create page. Paste a LinkedIn and Instagram URL, show the real progress steps and the finished profile with its matches.

## Submit checklist

- [ ] Run `python backend/run_pipeline.py` with real keys, confirm at least 25 people survive verification
- [ ] Deploy backend and frontend, set NEXT_PUBLIC_API_URL, GEMINI_API_KEY, APIFY_API_TOKEN on the backend host
- [ ] Open the live site and paste two public links yourself, confirm the create flow works
- [ ] Record the video, upload to YouTube
- [ ] Make the GitHub repo public (never commit .env)
