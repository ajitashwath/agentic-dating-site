import difflib
import re


def norm(name):
    return re.sub(r"[^a-z ]", "", (name or "").lower().replace("é", "e")).strip()


def name_match(a, b):
    a, b = norm(a), norm(b)
    if not a or not b:
        return False
    if difflib.SequenceMatcher(None, a, b).ratio() >= 0.88:
        return True
    # Decorated display names such as "Aishwarya Srinivasan | Data & AI" or "Andrew Bosworth (Boz)":
    # match when every word of the shorter name appears in the longer one.
    short, long_ = sorted([a.split(), b.split()], key=len)
    return len(short) >= 2 and all(word in long_ for word in short)


def check_identity(name, li, ig, min_followers=500):
    """Confirms both scraped profiles belong to `name` and that the Instagram is a real public account."""
    notes, ok = [], True
    if name_match(name, li["name"]):
        notes.append(f"LinkedIn name matches: {li['name']}")
    else:
        ok = False
        notes.append(f"LinkedIn name mismatch: expected {name}, got {li['name']}")
    if name_match(name, ig["name"]) or name_match(li["name"], ig["name"]):
        notes.append(f"Instagram name matches: {ig['name']}")
    else:
        ok = False
        notes.append(f"Instagram name mismatch: expected {name}, got {ig['name']}")
    followers = ig.get("followers") or 0
    if followers >= min_followers:
        notes.append(f"Instagram is public with {followers:,} followers" + (", verified badge" if ig.get("verified") else ""))
    else:
        ok = False
        notes.append(f"Instagram has only {followers} followers, looks like a placeholder")
    return {"ok": ok, "notes": notes}
