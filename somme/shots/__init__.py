"""Shot list for the Somme film. Each shot starts at a narration anchor
(segment, sentence[, fraction]) and runs until the next one starts.
look: silent (1916 film print; tint sepia/night/grey) | print (paper maps and
documents) | poster (lithograph halftone) | film (present day, in colour).
fps_eff gives the jerky cadence of hand-cranked film."""
from . import part1 as a
from . import part2 as b

SIL = dict(look="silent", fps_eff=16)

SHOTS = [
    dict(name="card_open", fn=a.card_open, start=None, look="silent", grain=0.8, xfade=False,
         sfx=[(0, "projector", 0.6)]),
    dict(name="dawn_trench", fn=a.dawn_trench, start=("open", 0), offset=0.2, **SIL,
         sfx=[(0, "larks", 0.8), (0, "guns_far", 0.7), (lambda S: S.dur - 1.6, "whistle", 1.0)]),
    dict(name="title", fn=a.title, start=("open", 2), offset=-0.2, look="silent", grain=0.8,
         sfx=[(0, "projector", 0.6)]),
    dict(name="western_front", fn=a.western_front, start=("stalemate", 0), offset=-0.3, look="print"),
    dict(name="verdun", fn=a.verdun, start=("verdun", 0), offset=-0.2, tint="night", **SIL,
         sfx=[(0, "guns_far", 1.0)]),
    dict(name="verdun_map", fn=a.verdun_map, start=("verdun", 1), offset=-0.2, look="print"),
    dict(name="poster", fn=a.poster, start=("army", 0), offset=-0.2, look="poster"),
    dict(name="pals_march", fn=a.pals_march, start=("army", 1), offset=-0.2, **SIL,
         sfx=[(0, "crowd", 0.8), (0, "march", 0.8)]),
    dict(name="guns", fn=a.guns, start=("bombardment", 0), offset=-0.2, **SIL,
         sfx=[(0, "guns_near", 1.0)]),
    dict(name="dugout_section", fn=a.dugout_section, start=("bombardment", 2), offset=-0.2, look="print",
         sfx=[(0, "guns_far", 0.6)]),
    dict(name="mines", fn=b.mines, start=("zero", 0), offset=-0.4, **SIL,
         sfx=[(0.6, "mine", 1.0), (lambda S: S.word("zero", 1, "more mines") - 0.05, "mine", 0.8)]),
    dict(name="over_the_top", fn=b.over_the_top, start=("zero", 2), offset=-0.2, **SIL,
         sfx=[(0.0, "whistle", 0.9), (1.0, "mg", 0.9), (0, "guns_near", 0.5)]),
    dict(name="card_accrington", fn=b.card_accrington, start=("slaughter", 0), offset=-0.3, look="silent",
         grain=0.8, sfx=[(0, "projector", 0.6)]),
    dict(name="card_newfoundland", fn=b.card_newfoundland, start=("slaughter", 1), offset=-0.2, look="silent",
         grain=0.8, sfx=[(0, "projector", 0.6)]),
    dict(name="first_day_map", fn=b.first_day_map, start=("slaughter", 2), offset=-0.2, look="print"),
    dict(name="attrition_map", fn=b.attrition_map, start=("attrition", 0), offset=-0.3, look="print"),
    dict(name="delville", fn=b.delville, start=("attrition", 2), offset=-0.2, tint="grey", **SIL,
         sfx=[(0, "guns_near", 0.8)]),
    dict(name="pozieres", fn=b.pozieres, start=("attrition", 3), offset=-0.2, **SIL,
         sfx=[(0, "guns_near", 0.8)]),
    dict(name="tanks", fn=b.tanks, start=("tanks", 0), offset=-0.3, **SIL,
         sfx=[(0, "tank", 1.0), (0, "guns_far", 0.6)]),
    dict(name="thiepval_map", fn=b.thiepval_map, start=("mud", 0), offset=-0.3, look="print"),
    dict(name="mud", fn=b.mud, start=("mud", 1), offset=-0.2, tint="grey", **SIL,
         sfx=[(0, "rain", 1.0), (0, "wind", 0.6)]),
    dict(name="final_map", fn=b.final_map, start=("mud", 2), offset=-0.2, look="print",
         sfx=[(0, "wind", 0.5)]),
    dict(name="cost_map", fn=b.cost_map, start=("cost", 0), offset=-0.3, look="print"),
    dict(name="card_cost", fn=b.card_cost, start=("cost", 1), offset=-0.2, look="silent", grain=0.7,
         sfx=[(0, "projector", 0.5)]),
    dict(name="card_debate", fn=b.card_debate, start=("legacy", 0), offset=-0.3, look="silent", grain=0.7,
         sfx=[(0, "projector", 0.5)]),
    dict(name="card_quote", fn=b.card_quote, start=("legacy", 1), offset=-0.2, look="silent", grain=0.7,
         sfx=[(0, "projector", 0.5)]),
    dict(name="hindenburg_map", fn=b.hindenburg_map, start=("legacy", 1, 0.66), look="print"),
    dict(name="memorial", fn=b.memorial, start=("legacy", 2), offset=-0.3, look="film", warm=True, grain=0.6,
         sfx=[(0, "wind", 0.5), (0, "larks", 0.5)]),
    dict(name="poppies", fn=b.poppies, start=("legacy", 3), offset=-0.3, look="film", warm=True, grain=0.6,
         sfx=[(0, "larks", 0.7), (0, "wind", 0.4)]),
    dict(name="card_end", fn=b.card_end, start=("legacy", "end"), offset=0.9, look="silent", grain=0.6,
         sfx=[(0, "projector", 0.4)]),
]
