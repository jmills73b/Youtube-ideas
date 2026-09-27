"""Narration script for "The Falklands War, 1982".

Each segment is a chapter of the film. Sentences are voiced separately so the
renderer knows exactly when each one starts, which lets shots cut on sentence
boundaries and lets us emit accurate YouTube captions.

Facts and figures are sourced in RESEARCH.md.
"""

SEGMENTS = [
    {
        "id": "open",
        "chapter": "Introduction",
        "sentences": [
            "In the spring of 1982, two nations went to war over a windswept "
            "cluster of islands at the bottom of the world.",
            "Seventy-four days later, more than nine hundred people were dead.",
            "This is the story of the Falklands War.",
        ],
    },
    {
        "id": "geography",
        "chapter": "The Islands",
        "sentences": [
            "The Falkland Islands lie in the South Atlantic, about three hundred "
            "miles from Argentina, and almost eight thousand miles from Britain.",
            "In 1982, they were home to some eighteen hundred people, nearly all "
            "of British descent.",
        ],
    },
    {
        "id": "history",
        "chapter": "A Disputed Inheritance",
        "sentences": [
            "Sovereignty had been disputed for two centuries.",
            "France, Spain and Britain all planted settlements here in the 1760s, "
            "and after independence, Buenos Aires claimed the islands as Spain's "
            "heir.",
            "But in January 1833, a British warship arrived, the Argentine "
            "garrison left, and Britain has governed ever since.",
            "To Argentines, they remained Las Malvinas, a lost province.",
        ],
    },
    {
        "id": "road",
        "chapter": "The Road to War",
        "sentences": [
            "For years, the United Nations urged both sides to negotiate, but the "
            "islanders refused any transfer of sovereignty.",
            "Then a 1981 British defence review announced the withdrawal of HMS "
            "Endurance, the Royal Navy's only ship in the region.",
            "In Buenos Aires, it looked like Britain no longer cared.",
        ],
    },
    {
        "id": "junta",
        "chapter": "The Junta",
        "sentences": [
            "Argentina was ruled by a military junta under General Leopoldo "
            "Galtieri.",
            "Inflation topped one hundred percent, and thousands had vanished in "
            "the regime's Dirty War.",
            "Recovering the Malvinas promised to unite the nation behind its "
            "generals.",
        ],
    },
    {
        "id": "invasion",
        "chapter": "Invasion: 2 April 1982",
        "sentences": [
            "On the second of April, Argentine commandos and marines stormed "
            "ashore near Stanley.",
            "A small force of Royal Marines resisted for three hours, until "
            "Governor Rex Hunt ordered them to surrender.",
            "The next day, South Georgia fell too.",
        ],
    },
    {
        "id": "taskforce",
        "chapter": "The Task Force Sails",
        "sentences": [
            "Britain was stunned.",
            "Margaret Thatcher resolved to take the islands back, and on the fifth "
            "of April the carriers Hermes and Invincible sailed from Portsmouth.",
            "More than a hundred ships followed, including requisitioned liners, "
            "staging through Ascension Island on the long voyage south.",
        ],
    },
    {
        "id": "firstblows",
        "chapter": "First Blows",
        "sentences": [
            "On the twenty-fifth of April, British forces retook South Georgia.",
            "On the first of May, a lone Vulcan bomber, refuelled again and again "
            "in mid-air, flew an eight-thousand-mile round trip to bomb the runway "
            "at Stanley.",
        ],
    },
    {
        "id": "belgrano",
        "chapter": "Belgrano and Sheffield",
        "sentences": [
            "The next day, the submarine HMS Conqueror torpedoed the Argentine "
            "cruiser General Belgrano.",
            "Three hundred and twenty-three men died, the war's greatest single "
            "loss of life, and still its most controversial act.",
            "Two days later, an Exocet missile struck the destroyer HMS Sheffield, "
            "killing twenty.",
            "Argentina's navy now stayed in port. The war belonged to its pilots.",
        ],
    },
    {
        "id": "sancarlos",
        "chapter": "San Carlos: Bomb Alley",
        "sentences": [
            "On the twenty-first of May, British troops landed at San Carlos Water.",
            "Argentine jets attacked at wave-top height, through what sailors "
            "called Bomb Alley.",
            "Ardent, Antelope, Coventry and the Atlantic Conveyor were lost, but "
            "the beachhead held.",
        ],
    },
    {
        "id": "goosegreen",
        "chapter": "Goose Green and the Yomp",
        "sentences": [
            "On the twenty-eighth, Two Para took Goose Green. Their commander, "
            "Colonel H Jones, was killed, and awarded the Victoria Cross.",
            "With most of their helicopters gone, the marines and paratroopers "
            "marched across fifty miles of bog and rock towards Stanley.",
        ],
    },
    {
        "id": "fitzroy",
        "chapter": "Fitzroy",
        "sentences": [
            "On the eighth of June, Argentine Skyhawks caught the landing ship Sir "
            "Galahad at Fitzroy. Forty-eight men died, most of them Welsh Guards.",
        ],
    },
    {
        "id": "mountains",
        "chapter": "The Battle for Stanley",
        "sentences": [
            "The final battles were fought at night, in the mountains ringing "
            "Stanley.",
            "Mount Longdon, Two Sisters and Mount Harriet fell on the eleventh of "
            "June, then Tumbledown, Wireless Ridge and Mount William.",
        ],
    },
    {
        "id": "surrender",
        "chapter": "Surrender: 14 June 1982",
        "sentences": [
            "On the fourteenth of June, General Mario Menéndez surrendered to "
            "Major General Jeremy Moore.",
            "After seventy-four days, the war was over.",
        ],
    },
    {
        "id": "legacy",
        "chapter": "The Cost and the Legacy",
        "sentences": [
            "It had cost the lives of two hundred and fifty-five British "
            "servicemen, six hundred and forty-nine Argentines, and three "
            "islanders.",
            "Within days, Galtieri fell. Within eighteen months, Argentina was a "
            "democracy again.",
            "In 2013, the islanders voted by 99.8 percent to remain British. "
            "Argentina still claims the Malvinas.",
            "The dispute endures, and so does the memory of those who never came "
            "home.",
        ],
    },
]
