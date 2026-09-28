"""Shot list for the Operation Mincemeat film. Each shot starts at a narration
anchor (segment, sentence[, fraction]) and runs until the next one starts.
look: newsreel (1940s b&w cinema) | noir (harder b&w) | print (paper) |
film (present day, colour)."""
from . import part1 as a
from . import part2 as b

SHOTS = [
    dict(name="dawn_sea", fn=a.dawn_sea, start=None, look="newsreel", sfx=[(0, "sea", 0.9), (0, "gulls", 0.5)]),
    dict(name="briefcase", fn=a.briefcase, start=("open", 1), offset=-0.3, look="newsreel",
         sfx=[(0, "sea", 0.8)]),
    dict(name="title", fn=a.title, start=("open", 2, 0.35), look="noir", sfx=[(0.5, "stamp", 1.0)]),
    dict(name="med_map", fn=a.med_map, start=("problem", 0), offset=-0.3, look="print"),
    dict(name="threats_map", fn=a.threats_map, start=("problem", 2), offset=-0.2, look="print"),
    dict(name="trout_memo", fn=a.trout_memo, start=("idea", 0), offset=-0.3, look="noir",
         sfx=[(0.2, "typewriter", 0.7)]),
    dict(name="office", fn=a.office, start=("idea", 2), offset=-0.2, look="noir", sfx=[(0, "clock", 0.6)]),
    dict(name="london", fn=a.london, start=("michael", 0), offset=-0.3, look="noir", sfx=[(0, "rain", 0.9)]),
    dict(name="wallet", fn=a.wallet, start=("martin", 0), offset=-0.3, look="noir",
         sfx=[(0.3, "typewriter", 0.5), (0, "clock", 0.4)]),
    dict(name="letters", fn=a.letters, start=("letters", 0), offset=-0.3, look="noir",
         sfx=[(0.2, "typewriter", 0.6)]),
    dict(name="night_drive", fn=b.night_drive, start=("seraph", 0), offset=-0.3, look="noir",
         sfx=[(0, "engine", 0.8)]),
    dict(name="seraph_sails", fn=b.seraph_sails, start=("seraph", 1), offset=-0.2, look="newsreel",
         sfx=[(0, "sea", 0.8), (0, "diesel", 0.8)]),
    dict(name="route_map", fn=b.route_map, start=("seraph", 2), offset=-0.2, look="print"),
    dict(name="release", fn=b.release, start=("seraph", 2, 0.4), look="noir",
         sfx=[(0, "sea", 0.7), (0, "wind", 0.4)]),
    dict(name="huelva", fn=b.huelva, start=("spain", 0), offset=-0.3, look="newsreel",
         sfx=[(0, "bells", 0.5), (0, "wind", 0.3)]),
    dict(name="photographing", fn=b.photographing, start=("spain", 2), offset=-0.2, look="noir",
         sfx=[(0.0, "shutter", 0.9), (2.2, "shutter", 0.9), (4.4, "shutter", 0.9)]),
    dict(name="signal", fn=b.signal, start=("swallowed", 0), offset=-0.3, look="noir",
         sfx=[(0, "teleprinter", 0.8)]),
    dict(name="german_moves", fn=b.german_moves, start=("swallowed", 2), offset=-0.2, look="print"),
    dict(name="landings", fn=b.landings, start=("husky", 0), offset=-0.3, look="newsreel",
         sfx=[(0, "sea", 0.7), (0, "guns_far", 0.8), (0, "planes", 0.6)]),
    dict(name="sicily_map", fn=b.sicily_map, start=("husky", 1), offset=-0.2, look="print"),
    dict(name="howard", fn=b.howard, start=("husky", 2, 0.35), look="noir"),
    dict(name="grave", fn=b.grave, start=("legacy", 0), offset=-0.3, look="film", warm=True, grain=0.6,
         sfx=[(0, "birds", 0.6), (0, "wind", 0.3)]),
    dict(name="end_card", fn=b.end_card, start=("legacy", "end"), offset=0.9, look="noir"),
]
