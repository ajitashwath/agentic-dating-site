import os
import time

import httpx

# Actors: https://apify.com/apify/instagram-scraper and https://apify.com/harvestapi/linkedin-profile-scraper
INSTAGRAM_ACTOR = "apify~instagram-scraper"
LINKEDIN_ACTOR = "harvestapi~linkedin-profile-scraper"


def run_actor(actor, run_input):
    token = os.getenv("APIFY_API_TOKEN")
    if not token:
        raise RuntimeError("APIFY_API_TOKEN is not set. Add it to your .env file to enable live scraping.")
    url = os.getenv("APIFY_BASE_URL", "https://api.apify.com/v2") + f"/acts/{actor}/run-sync-get-dataset-items"
    response = None
    for attempt in range(6):
        try:
            response = httpx.post(url, params={"token": token}, json=run_input, timeout=240)
        except httpx.HTTPError as error:
            raise RuntimeError(f"Could not reach Apify: {error}")
        # 402 and 429 mean the account's concurrent memory or run limit is full right now, so wait and retry
        if response.status_code in (402, 429) and attempt < 5:
            time.sleep(10 * (attempt + 1))
            continue
        break
    if response.status_code >= 400:
        raise RuntimeError(f"Apify returned {response.status_code}: {response.text[:200]}")
    items = response.json()
    if not items:
        raise RuntimeError("Apify returned no data. The profile may be private or the URL may be wrong.")
    return items[0]


def scrape_linkedin(url):
    raw = run_actor(LINKEDIN_ACTOR, {"profileScraperMode": "Profile details no email ($4 per 1k)", "urls": [url]})
    if raw.get("error"):
        raise RuntimeError(f"LinkedIn actor error: {raw['error']}")
    name = f"{raw.get('firstName', '')} {raw.get('lastName', '')}".strip()
    experience = []
    for job in (raw.get("experience") or [])[:6]:
        experience.append(f"{job.get('position', '')} at {job.get('companyName', '')} {job.get('description') or ''}".strip())
    education = [f"{e.get('degree', '')} {e.get('fieldOfStudy', '')} at {e.get('schoolName', '')}".strip() for e in (raw.get("education") or [])[:3]]
    skills = [s.get("name") if isinstance(s, dict) else s for s in (raw.get("skills") or [])[:15]]
    location = raw.get("location")
    if isinstance(location, dict):
        location = location.get("linkedinText")
    return {
        "source": "linkedin",
        "url": url,
        "name": name,
        "headline": raw.get("headline") or "",
        "about": raw.get("about") or "",
        "location": location or "",
        "followers": raw.get("followerCount"),
        "top_skills": raw.get("topSkills"),
        "experience": experience,
        "education": education,
        "skills": skills,
    }


def scrape_instagram(url):
    raw = run_actor(INSTAGRAM_ACTOR, {"directUrls": [url], "resultsType": "details", "resultsLimit": 1, "addParentData": False})
    if raw.get("error"):
        raise RuntimeError(f"Instagram actor error: {raw.get('errorDescription') or raw['error']}")
    if raw.get("private"):
        raise RuntimeError("This Instagram profile is private, so no public data is available.")
    posts = raw.get("latestPosts") or []
    return {
        "source": "instagram",
        "url": url,
        "name": raw.get("fullName") or raw.get("username") or "",
        "username": raw.get("username") or "",
        "bio": raw.get("biography") or "",
        "verified": bool(raw.get("verified")),
        "followers": raw.get("followersCount"),
        "posts_count": raw.get("postsCount"),
        "category": raw.get("businessCategoryName") or "",
        "external_url": raw.get("externalUrl") or "",
        "captions": [p.get("caption") for p in posts if p.get("caption")][:12],
        "hashtags": sorted({h for p in posts for h in (p.get("hashtags") or [])})[:25],
        "locations": [p.get("locationName") for p in posts if p.get("locationName")][:8],
    }
