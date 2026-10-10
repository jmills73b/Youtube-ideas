"""THE PROMOTERS - a mockumentary parody.

Cartoon caricatures of two public figures, built on their real public spat
(September-October 2026) over whether Dana White can be involved in promoting
Anthony Joshua vs Tyson Fury. Lines marked REAL paraphrase or quote things
reported in the press (see RESEARCH.md); everything else is invented comedy.

Each beat: (shot, speaker, text, pause_after). speaker None = silent beat of
`pause_after` seconds. Voices are generic synthetic voices, not imitations.
"""

VOICES = {
    "DANA": ("am_michael", 1.02),
    "EDDIE": ("bm_lewis", 1.05),
    "INT": ("bf_emma", 1.0),      # off-camera documentary interviewer
    "GARY": ("bm_fable", 0.95),   # the office tea man
}

BEATS = [
    ("card_open", None, None, 5.0),
    # --- talking heads: the premise
    ("th_dana", "DANA", "I'm promoting the fight. Simple. I'm sitting here, right now, promoting it.", 0.9),  # REAL
    ("th_dana", None, None, 1.3),
    ("th_dana", "DANA", "This. This is promoting.", 0.8),
    ("th_eddie", "EDDIE", "He can't. Contractually. It's in the contract.", 0.4),  # REAL
    ("th_eddie_binder", "EDDIE", "Page forty. Highlighted. I did the highlighting myself.", 0.5),
    ("th_eddie_binder", "EDDIE", "Took most of August.", 0.9),
    # --- the ticket video
    ("office_phone", "DANA", "Tickets on sale now! Cardiff! December the eleventh! Let's go!", 0.4),  # REAL (promo video)
    ("office_look", None, None, 1.6),
    ("office_look", "EDDIE", "That's a breach.", 0.6),
    ("whiteboard", "EDDIE", "Six.", 0.3),  # REAL (Hearn: "breached roughly six times")
    ("whiteboard", "EDDIE", "Six breaches. And it's not even lunch.", 0.8),
    # --- the loophole
    ("th_dana", "INT", "Eddie says the contract bans you.", 0.3),
    ("th_dana_badge", "DANA", "Does it say Dana? Or does it say the company?", 0.4),  # REAL (White's side)
    ("th_dana_badge", "DANA", "Because I'm Dana. I'm not a company. I'm a guy.", 1.0),
    ("th_eddie", "EDDIE", "It says Dana White. First name, surname.", 0.4),  # REAL ("Dana White, Zuffa")
    ("th_eddie", "EDDIE", "I checked the spelling. Twice.", 0.9),
    # --- who's going to stop me
    ("th_dana", "DANA", "Who's going to stop me?", 1.0),  # REAL
    ("office_hand", None, None, 2.4),
    ("th_dana", "DANA", "Anyone else?", 1.0),
    # --- Netflix
    ("printer", None, None, 1.8),
    ("printer", "EDDIE", "Netflix have put him on the press release as a promoter.", 0.3),  # REAL
    ("printer_look", "EDDIE", "Which is a press release. Not a contract.", 0.4),
    ("printer_look", "EDDIE", "I have the contract. It's very heavy.", 0.9),
    # --- production
    ("th_dana", "DANA", "We're doing the TV production. Done.", 0.6),  # REAL
    ("th_eddie_binder2", "EDDIE", "They're not. I've got that in writing as well.", 0.3),  # REAL
    ("th_eddie_binder2", "EDDIE", "Different folder. Blue one.", 0.9),
    # --- the meeting
    ("th_eddie", "INT", "Are you two meeting?", 0.2),
    ("th_eddie", "EDDIE", "Wednesday. Los Angeles. Face to face. Sort it out like men.", 0.6),
    ("th_dana", "DANA", "We're not meeting Wednesday.", 1.2),  # REAL (White denied)
    ("card_wednesday", None, None, 1.8),
    ("meeting", None, None, 2.5),
    ("meeting", "GARY", "Do Joshua and Fury get a say in any of this?", 1.4),
    ("meeting", "EDDIE", "They're the fighters.", 1.1),
    ("meeting", "EDDIE", "So, no.", 1.8),
    ("card_end", None, None, 6.5),
]
