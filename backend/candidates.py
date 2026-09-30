"""Candidate roster. Every link pair below was checked against search results that showed
the LinkedIn profile and the public Instagram profile for the same person.
run_pipeline.py then re-verifies each pair from the scraped data before a person is kept.
"""

L = "https://www.linkedin.com/in/"
I = "https://www.instagram.com/"

CANDIDATES = [
    # Less famous big tech people and tech creators
    ("Adam Mosseri", L + "mosseri", I + "mosseri/"),
    ("Scott Hanselman", L + "shanselman", I + "shanselman/"),
    ("Andrew Bosworth", L + "andrew-bosworth-8247a01", I + "boztank/"),
    ("Jeff Su", L + "jsu05", I + "j.sushie/"),
    ("Kevin Stratvert", L + "kevinstratvert", I + "kevinstratvert/"),
    ("Clement Mihailescu", L + "clementmihailescu", I + "clement_mihailescu/"),
    ("Ryan Roslansky", L + "ryanroslansky", I + "ryanroslanskylinkedin/"),
    ("Brian Chesky", L + "brianchesky", I + "bchesky/"),
    ("Sarah Drasner", L + "sarahdrasner", I + "sdrasner/"),
    ("Aishwarya Srinivasan", L + "aishwarya-srinivasan", I + "the.datascience.gal/"),
    ("Wes Bos", L + "wesbos", I + "wesbos/"),
    ("Lenny Rachitsky", L + "lennyrachitsky", I + "lennysan/"),
    # Well known people
    ("Sundar Pichai", L + "sundarpichai", I + "sundarpichai/"),
    ("Sheryl Sandberg", L + "sheryl-sandberg-5126652", I + "sherylsandberg/"),
    ("Reid Hoffman", L + "reidhoffman", I + "reidhoffman/"),
    ("Richard Branson", L + "rbranson", I + "richardbranson/"),
    ("Gary Vaynerchuk", L + "garyvaynerchuk", I + "garyvee/"),
    ("Brene Brown", L + "brenebrown", I + "brenebrown/"),
    ("Simon Sinek", L + "simonsinek", I + "simonsinek/"),
    ("Adam Grant", L + "adammgrant", I + "adamgrant/"),
    ("Tim Ferriss", L + "timferriss", I + "timferriss/"),
    ("Bill Gates", L + "williamhgates", I + "thisisbillgates/"),
    ("Melinda French Gates", L + "melindagates", I + "melindafrenchgates/"),
    ("Ankur Warikoo", L + "warikoo", I + "ankurwarikoo/"),
    ("Nikhil Kamath", L + "nikhilkamathcio", I + "nikhilkamathcio/"),
    ("Guy Kawasaki", L + "guykawasaki", I + "guykawasaki/"),
    ("Neil Patel", L + "neilkpatel", I + "neilpatel/"),
    ("Jay Shetty", L + "shettyjay", I + "jayshetty/"),
    ("Kevin Systrom", L + "kevinsystrom", I + "kevin/"),
    ("Mike Krieger", L + "mikekrieger", I + "mikeyk/"),
    ("Marques Brownlee", L + "mkbhd", I + "mkbhd/"),
    ("Ali Abdaal", L + "ali-abdaal", I + "aliabdaal/"),
    ("Codie Sanchez", L + "codiesanchez", I + "codiesanchez/"),
    ("Alex Hormozi", L + "alexhormozi", I + "hormozi/"),
    ("Emma Grede", L + "emmagrede", I + "emmagrede/"),
    ("Sara Blakely", L + "sarablakely27", I + "sarablakely/"),
]

