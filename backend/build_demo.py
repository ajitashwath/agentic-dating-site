"""OFFLINE FALLBACK ONLY. Generates a provisional demo from hand-written profiles.

The real demo comes from run_pipeline.py (Apify scrape, LLM analysis, LLM agent dates).
This file exists so the site is not empty before the pipeline has been run.

Run once with `python build_demo.py`. The site then reads the JSON files only,
so the demo works with no Apify, no Gemini and no internet.

Profiles are written by hand from widely known public information about each
person (their public role, books, companies and the themes of their public
accounts). Tags come from a shared vocabulary so the deterministic scoring works.
"""
import json
from pathlib import Path

from matching import make_date, rank_person

DATA = Path(__file__).parent / "data"


def tags(text):
    return [t.strip() for t in text.split(",") if t.strip()]


def person(name, role, linkedin, instagram, summary, interests, hobbies, values, personality,
           lifestyle, comm, career, wants, li_evidence, ig_evidence):
    return {
        "name": name,
        "role": role,
        "linkedin": linkedin,
        "instagram": instagram,
        "profile": {
            "summary": summary,
            "interests": tags(interests),
            "hobbies": tags(hobbies),
            "values": tags(values),
            "personality": tags(personality),
            "lifestyle": tags(lifestyle),
            "communication_style": tags(comm),
            "career_orientation": tags(career),
            "dating_preferences": tags(wants),
        },
        "source_evidence": {
            "linkedin": [s.strip() for s in li_evidence.split("|")],
            "instagram": [s.strip() for s in ig_evidence.split("|")],
        },
    }


PEOPLE = [
    person("Sundar Pichai", "CEO, Google and Alphabet",
           "https://www.linkedin.com/in/sundarpichai", "https://www.instagram.com/sundarpichai",
           "A quiet, product-minded CEO who leads by listening and thinks in decades of technology.",
           "AI,technology,product,education,sports", "cricket,football,travel,reading", "learning,humility,impact,optimism",
           "calm,humble,analytical,warm", "structured days,public-facing,travel-heavy", "thoughtful,data-driven,questioning",
           "executive,operator", "curious,grounded,intellectual",
           "Joined Google in 2004 and led Chrome before becoming CEO|CEO of Google since 2015 and Alphabet since 2019|Frames Google as an AI-first company",
           "Shares product launches and team moments|Travel and meetings with communities around the world|Public enthusiasm for cricket and football"),
    person("Sheryl Sandberg", "Founder, Lean In and former COO, Meta",
           "https://www.linkedin.com/in/sheryl-sandberg-5126652", "https://www.instagram.com/sherylsandberg",
           "A resilient operator turned advocate who talks openly about ambition, grief and building community.",
           "leadership,philanthropy,media,family,writing", "writing,hiking,tennis,reading", "resilience,empathy,service,growth",
           "driven,warm,direct,reflective", "family-first,structured days,public-facing", "storyteller,direct,encouraging",
           "operator,author,advocate", "kind,ambitious,honest",
           "Former COO of Meta and earlier leader at Google|Founder of LeanIn.Org and author of Lean In and Option B|Public advocate for women in leadership and resilience",
           "Family moments and personal milestones|Lean In circles and Option B community|Messages about resilience and support"),
    person("Reid Hoffman", "Co-founder, LinkedIn and Partner, Greylock",
           "https://www.linkedin.com/in/reidhoffman", "https://www.instagram.com/reidhoffman",
           "A systems-thinking investor who treats every conversation as a chance to explore the future.",
           "AI,startups,philosophy,technology,investing", "podcasting,reading,writing,gaming", "curiosity,impact,optimism,learning",
           "analytical,bold,playful,curious", "public-facing,screen-heavy,travel-heavy", "questioning,storyteller,thoughtful",
           "founder,investor,author", "intellectual,curious,ambitious",
           "Co-founder of LinkedIn and Partner at Greylock|Host of the Masters of Scale and Possible podcasts|Author of Blitzscaling and Superagency",
           "Podcast guests and episodes|Conversations about AI and society|Investing and company-building themes"),
    person("Richard Branson", "Founder, Virgin Group",
           "https://www.linkedin.com/in/rbranson", "https://www.instagram.com/richardbranson",
           "An adventurous, playful founder who mixes business with kitesurfing and a taste for risk.",
           "startups,travel,philanthropy,sports,media", "kitesurfing,sailing,tennis,travel", "freedom,generosity,optimism,impact",
           "bold,playful,energetic,warm", "travel-heavy,spontaneous,nature time", "humorous,storyteller,high-energy",
           "founder,investor,advocate", "adventurous,funny,kind",
           "Founder of Virgin Group across music, airlines and space|Co-founder of Virgin Galactic|Active in philanthropy through Virgin Unite",
           "Adventure and kitesurfing moments|Necker Island and Virgin brand updates|Playful, upbeat captions"),
    person("Gary Vaynerchuk", "Chairman, VaynerX and CEO, VaynerMedia",
           "https://www.linkedin.com/in/garyvaynerchuk", "https://www.instagram.com/garyvee",
           "A high-energy entrepreneur who says the quiet part out loud and posts every day.",
           "marketing,startups,creators,media,sports", "collecting,sports,filming,gym", "honesty,discipline,growth,generosity",
           "energetic,direct,bold,driven", "screen-heavy,public-facing,spontaneous", "high-energy,direct,storyteller",
           "founder,creator,author", "honest,driven,funny",
           "Chairman of VaynerX and CEO of VaynerMedia|Co-founder of VeeFriends|Author of Crush It and Jab Jab Jab Right Hook",
           "Daily motivational and business clips|Advice for creators and entrepreneurs|Sports and collectibles interests"),
    person("Brene Brown", "Research Professor, University of Houston",
           "https://www.linkedin.com/in/brenebrown", "https://www.instagram.com/brenebrown",
           "A researcher of vulnerability and courage who leads with honesty and a good sense of humor.",
           "psychology,leadership,writing,media,education", "podcasting,writing,reading,cooking", "authenticity,empathy,courage,honesty",
           "warm,direct,reflective,playful", "family-first,structured days,public-facing", "storyteller,humorous,encouraging",
           "educator,author,advocate", "honest,kind,grounded",
           "Research professor at the University of Houston Graduate College of Social Work|Author of Daring Greatly and Dare to Lead|Host of the Unlocking Us and Dare to Lead podcasts",
           "Vulnerability and courage themes|Podcast episodes and book news|Family and Texas life"),
    person("Simon Sinek", "Author and Speaker",
           "https://www.linkedin.com/in/simonsinek", "https://www.instagram.com/simonsinek",
           "An optimistic leadership thinker who asks why before how.",
           "leadership,philosophy,writing,psychology,media", "writing,reading,travel,cycling", "optimism,purpose,empathy,honesty",
           "warm,reflective,direct,calm", "public-facing,travel-heavy,structured days", "questioning,storyteller,encouraging",
           "author,educator,advocate", "curious,kind,grounded",
           "Author of Start With Why and The Infinite Game|Widely watched TED talk on leadership|Speaks about trust and purpose at work",
           "Short leadership video clips|Reflections on optimism and trust|Book and podcast promotion"),
    person("Adam Grant", "Organizational Psychologist, Wharton",
           "https://www.linkedin.com/in/adammgrant", "https://www.instagram.com/adamgrant",
           "A playful psychologist who loves changing his mind and turning research into practical ideas.",
           "psychology,education,writing,science,leadership", "writing,podcasting,reading,running", "curiosity,learning,generosity,honesty",
           "playful,analytical,curious,warm", "structured days,public-facing,early riser", "humorous,data-driven,questioning",
           "educator,author", "curious,funny,intellectual",
           "Professor at the Wharton School of the University of Pennsylvania|Author of Give and Take, Originals, Think Again and Hidden Potential|Host of the WorkLife and Re:Thinking podcasts",
           "Research findings in short posts|Humor and book announcements|Teaching and speaking moments"),
    person("Tim Ferriss", "Author, Investor and Podcaster",
           "https://www.linkedin.com/in/timferriss", "https://www.instagram.com/timferriss",
           "A self-experimenter who interviews world-class performers to find repeatable tools.",
           "learning,startups,health,investing,writing", "reading,gym,journaling,travel", "curiosity,discipline,freedom,growth",
           "analytical,curious,playful,direct", "screen-heavy,structured days,travel-heavy", "questioning,data-driven,storyteller",
           "author,investor,creator", "curious,adventurous,intellectual",
           "Author of The 4-Hour Workweek and Tools of Titans|Early-stage angel investor|Host of The Tim Ferriss Show podcast",
           "Podcast guests and lessons|Fitness and self-experiments|Book and learning recommendations"),
    person("Bill Gates", "Co-founder, Microsoft and Chair, Gates Foundation",
           "https://www.linkedin.com/in/williamhgates", "https://www.instagram.com/thisisbillgates",
           "A voracious reader who applies engineering thinking to health and climate.",
           "science,technology,health,climate,philanthropy", "reading,tennis,bridge,cooking", "impact,curiosity,generosity,optimism",
           "analytical,humble,curious,direct", "structured days,public-facing,travel-heavy", "data-driven,thoughtful,questioning",
           "founder,advocate,author", "intellectual,curious,kind",
           "Co-founder of Microsoft|Chair of the Gates Foundation, focused on global health|Founder of Breakthrough Energy and author of How to Avoid a Climate Disaster",
           "Book recommendations and reading lists|Global health and climate posts|Family and personal glimpses"),
    person("Melinda French Gates", "Founder, Pivotal Ventures",
           "https://www.linkedin.com/in/melindagates", "https://www.instagram.com/melindafrenchgates",
           "A steady, purposeful philanthropist focused on lifting up women and families.",
           "philanthropy,health,education,technology,family", "reading,writing,travel,hiking", "empathy,impact,service,family",
           "warm,calm,driven,reflective", "family-first,public-facing,travel-heavy", "thoughtful,encouraging,storyteller",
           "advocate,author,investor", "kind,grounded,family-oriented",
           "Founder of Pivotal Ventures|Former co-chair of the Gates Foundation|Author of The Moment of Lift",
           "Women's empowerment and family themes|Philanthropy and field visits|Personal milestones"),
    person("Ankur Warikoo", "Entrepreneur and Content Creator",
           "https://www.linkedin.com/in/warikoo", "https://www.instagram.com/ankurwarikoo",
           "A candid creator who turns personal mistakes into money and career advice.",
           "finance,education,creators,startups,learning", "writing,reading,filming,travel", "honesty,growth,discipline,learning",
           "direct,energetic,humble,driven", "screen-heavy,public-facing,structured days", "direct,storyteller,encouraging",
           "founder,creator,educator", "honest,driven,curious",
           "Founder background including Nearbuy and WebVeda|Author of Do Epic Shit and Get Epic Shit Done|Creator of large personal finance and career audiences",
           "Short-form money and career advice|Personal growth themes|Behind the scenes of content creation"),
    person("Nikhil Kamath", "Co-founder, Zerodha and True Beacon",
           "https://www.linkedin.com/in/nikhilkamathcio", "https://www.instagram.com/nikhilkamathcio",
           "A restless investor and interviewer who learned finance by doing.",
           "investing,finance,startups,podcasting,travel", "podcasting,travel,running,reading", "curiosity,freedom,discipline,optimism",
           "curious,bold,direct,calm", "travel-heavy,spontaneous,screen-heavy", "questioning,direct,thoughtful",
           "founder,investor,creator", "adventurous,curious,ambitious",
           "Co-founder of Zerodha and True Beacon|Founder of the Gruhas investment platform|Host of the WTF is podcast",
           "Podcast guests and clips|Investing and business themes|Travel and outdoor moments"),
    person("Guy Kawasaki", "Chief Evangelist, Canva",
           "https://www.linkedin.com/in/guykawasaki", "https://www.instagram.com/guykawasaki",
           "A generous evangelist who loves design, surfing and telling a story with a slide deck.",
           "design,startups,technology,marketing,writing", "surfing,hockey,writing,podcasting", "generosity,optimism,authenticity,curiosity",
           "playful,warm,bold,energetic", "spontaneous,nature time,public-facing", "humorous,storyteller,high-energy",
           "author,advocate,founder", "funny,adventurous,creative",
           "Chief Evangelist of Canva and former Apple evangelist|Author of The Art of the Start and Wise Guy|Host of the Remarkable People podcast",
           "Foil surfing and hockey|Design and product enthusiasm|Playful captions"),
    person("Neil Patel", "Co-founder, NP Digital",
           "https://www.linkedin.com/in/neilkpatel", "https://www.instagram.com/neilpatel",
           "A hard-working marketer who shares what he learns about search and growth.",
           "marketing,startups,technology,creators,finance", "travel,writing,filming,podcasting", "discipline,generosity,growth,honesty",
           "driven,direct,energetic,humble", "screen-heavy,travel-heavy,structured days", "data-driven,direct,encouraging",
           "founder,creator,author", "driven,honest,ambitious",
           "Co-founder of NP Digital, a performance marketing agency|Co-founder of Crazy Egg and Kissmetrics|New York Times best-selling author",
           "Marketing tips and short videos|Entrepreneurship advice|Behind the scenes of travel and work"),
    person("Jay Shetty", "Author, Podcaster and Former Monk",
           "https://www.linkedin.com/in/shettyjay", "https://www.instagram.com/jayshetty",
           "A mindful storyteller who uses ancient ideas to talk about modern relationships.",
           "wellbeing,psychology,media,writing,philosophy", "meditation,podcasting,writing,gym", "empathy,purpose,service,optimism",
           "warm,calm,reflective,energetic", "early riser,public-facing,structured days", "storyteller,encouraging,thoughtful",
           "author,creator,educator", "kind,calm,grounded",
           "Author of Think Like a Monk and 8 Rules of Love|Host of the On Purpose podcast|Trained as a monk before becoming a creator",
           "Mindfulness and relationship videos|Purpose and gratitude themes|Podcast episodes"),
    person("Kevin Systrom", "Co-founder, Instagram and Artifact",
           "https://www.linkedin.com/in/kevinsystrom", "https://www.instagram.com/kevin",
           "A product-focused founder with an eye for photography and a serious coffee habit.",
           "product,technology,design,startups,food", "photography,travel,cooking,cycling", "curiosity,authenticity,growth,impact",
           "creative,humble,analytical,calm", "travel-heavy,nature time,structured days", "thoughtful,questioning,direct",
           "founder,operator,investor", "creative,curious,grounded",
           "Co-founder and former CEO of Instagram|Co-founder of the news app Artifact|Early product roles at Google and Odeo",
           "Photography and travel|Coffee and food|Product thinking"),
    person("Mike Krieger", "Chief Product Officer, Anthropic",
           "https://www.linkedin.com/in/mikekrieger", "https://www.instagram.com/mikeyk",
           "A builder who loves shipping products and getting outside afterward.",
           "AI,product,technology,design,startups", "photography,hiking,cycling,gaming", "curiosity,impact,growth,humility",
           "analytical,calm,creative,humble", "nature time,structured days,travel-heavy", "thoughtful,data-driven,direct",
           "founder,operator,executive", "curious,creative,grounded",
           "Co-founder of Instagram|Co-founder of Artifact|Chief Product Officer at Anthropic",
           "Photography and outdoors|Product and engineering themes|Travel moments"),
    person("Marques Brownlee", "Tech Reviewer, MKBHD",
           "https://www.linkedin.com/in/mkbhd", "https://www.instagram.com/mkbhd",
           "A meticulous reviewer who pairs high production quality with real enthusiasm for gadgets.",
           "technology,design,creators,media,sports", "filming,photography,cars,gaming", "authenticity,discipline,curiosity,honesty",
           "analytical,calm,humble,creative", "screen-heavy,public-facing,structured days", "data-driven,direct,humorous",
           "creator,founder", "creative,honest,funny",
           "Founder of MKBHD, one of the largest tech YouTube channels|Host of the Waveform podcast|Interviews executives and founders about products",
           "Tech gear and product photos|Electric cars and gadgets|Behind the scenes of video production"),
    person("Ali Abdaal", "Creator and Former Doctor",
           "https://www.linkedin.com/in/ali-abdaal", "https://www.instagram.com/aliabdaal",
           "A cheerful productivity nerd who left medicine to teach people how to feel good while working.",
           "education,learning,creators,health,startups", "reading,filming,gaming,journaling", "growth,curiosity,optimism,discipline",
           "warm,playful,analytical,energetic", "structured days,screen-heavy,early riser", "storyteller,humorous,data-driven",
           "creator,founder,educator", "curious,funny,kind",
           "Trained as a doctor at Cambridge|Author of Feel-Good Productivity|Founder of a creator business and learning products",
           "Productivity and study tips|Daily life and travel|Book and app recommendations"),
    person("Codie Sanchez", "Founder, Contrarian Thinking",
           "https://www.linkedin.com/in/codiesanchez", "https://www.instagram.com/codiesanchez",
           "A blunt investor who loves boring businesses and trades in no-nonsense advice.",
           "investing,finance,startups,media,marketing", "travel,gym,reading,filming", "freedom,honesty,discipline,growth",
           "bold,direct,playful,driven", "travel-heavy,public-facing,spontaneous", "direct,humorous,high-energy",
           "founder,investor,creator", "adventurous,honest,ambitious",
           "Founder of Contrarian Thinking and Unconventional Capital|Author of Main Street Millionaire|Invests in and teaches buying small businesses",
           "Small business and investing clips|Humor and memes|Travel and lifestyle snapshots"),
    person("Alex Hormozi", "Founder, Acquisition.com",
           "https://www.linkedin.com/in/alexhormozi", "https://www.instagram.com/hormozi",
           "An intense operator who explains business in plain math and keeps a gym schedule.",
           "startups,finance,marketing,health,investing", "gym,reading,filming,cooking", "discipline,honesty,generosity,family",
           "driven,direct,analytical,energetic", "structured days,early riser,family-first", "direct,data-driven,high-energy",
           "founder,investor,author", "driven,honest,family-oriented",
           "Founder of Acquisition.com and Gym Launch|Author of $100M Offers and $100M Leads|Invests in and advises scaling companies",
           "Business advice video clips|Fitness and discipline|Family time"),
    person("Emma Grede", "Co-founder, Skims and Good American",
           "https://www.linkedin.com/in/emmagrede", "https://www.instagram.com/emmagrede",
           "A fast-moving brand builder who balances big companies with a big family.",
           "design,startups,marketing,media,family", "travel,cooking,reading,gym", "resilience,family,discipline,growth",
           "driven,bold,warm,direct", "family-first,public-facing,travel-heavy", "direct,encouraging,storyteller",
           "founder,operator,investor", "driven,family-oriented,ambitious",
           "Co-founder of Skims and Good American|Investor on the TV show Shark Tank|Author of Fearless Business",
           "Fashion and brand moments|Family life|Business lessons"),
    person("Sara Blakely", "Founder, Spanx",
           "https://www.linkedin.com/in/sarablakely27", "https://www.instagram.com/sarablakely",
           "A funny, fearless founder who turned an idea and a lot of persistence into a global brand.",
           "startups,design,philanthropy,family,marketing", "cooking,reading,travel,journaling", "resilience,optimism,generosity,family",
           "playful,bold,warm,humble", "family-first,spontaneous,public-facing", "humorous,storyteller,encouraging",
           "founder,advocate,investor", "funny,kind,family-oriented",
           "Founder of Spanx and self-made billionaire|Sara Blakely Foundation supports women entrepreneurs|Known for the failure-sharing dinner table tradition",
           "Family and humor|Entrepreneurship stories|Philanthropy and women founders"),
]


def main():
    people = []
    for i, p in enumerate(PEOPLE):
        people.append({"id": f"person-{i + 1:03d}", **p})

    dates = []
    for i in range(len(people)):
        for j in range(i + 1, len(people)):
            dates.append(make_date(people[i], people[j]))

    rankings = {p["id"]: rank_person(p, people) for p in people}

    (DATA / "demo_people.json").write_text(json.dumps(people, indent=2, ensure_ascii=False), encoding="utf-8")
    (DATA / "demo_dates.json").write_text(json.dumps(dates, indent=1, ensure_ascii=False), encoding="utf-8")
    (DATA / "demo_rankings.json").write_text(json.dumps(rankings, indent=1, ensure_ascii=False), encoding="utf-8")
    print(len(people), "people,", len(dates), "dates")


if __name__ == "__main__":
    main()
