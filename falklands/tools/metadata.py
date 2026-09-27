"""Write YouTube upload metadata (title, description with chapters, tags).

  python3 tools/metadata.py  ->  build/youtube_metadata.txt
"""
import json
import os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(HERE, "build")

TITLE = "The Falklands War in 5 Minutes | 1982: Invasion, Task Force, Surrender"

INTRO = """In the spring of 1982, Argentina and Britain went to war over the Falkland Islands - Las Malvinas - 8,000 miles from London and 300 miles from the Argentine coast. In 74 days, 907 people were killed.

This short documentary covers the centuries-old sovereignty dispute, the road to war under Argentina's military junta, Operation Rosario, the British Task Force, the sinking of the General Belgrano and HMS Sheffield, the San Carlos landings, Goose Green, Fitzroy, the night battles for the mountains around Stanley, the surrender, and the war's legacy.

All illustrations, maps and music were generated for this film in a style inspired by 1982: 16mm news film, early-80s TV news maps and captions, and teletext. Illustrations are artistic reconstructions, not photographs."""

SOURCES = """SOURCES AND FURTHER READING
- Lawrence Freedman, The Official History of the Falklands Campaign, 2 vols (Routledge, 2005; rev. 2007)
- Max Hastings & Simon Jenkins, The Battle for the Falklands (1983)
- Martin Middlebrook, Operation Corporate (1985) and The Fight for the 'Malvinas': The Argentine Forces in the Falklands War (1989)
- Admiral Sandy Woodward, One Hundred Days (1992)
- Julian Thompson, No Picnic: 3 Commando Brigade in the South Atlantic (1985)
- Rowland White, Vulcan 607 (2006)
- Falkland Islands Review ('The Franks Report'), Cmnd 8787 (1983)
- The United Kingdom Defence Programme: The Way Forward, Cmnd 8288 (1981)
- Informe Rattenbach (Argentine armed forces commission report, 1983)
- UN General Assembly Resolution 2065 (XX), 16 Dec 1965; UN Security Council Resolution 502, 3 Apr 1982
- Falkland Islands Government, Referendum on the Political Status of the Falkland Islands, March 2013 (results)

MAP DATA: Natural Earth (public domain); geoBoundaries (CC BY 4.0) - Runfola et al. (2020), PLOS ONE 15(4): e0231866.
NARRATION: synthetic voice (Kokoro TTS, Apache-2.0). MUSIC & SOUND: original, synthesised for this film.
FONTS: SIL Open Font License / Apache-2.0 (Google Fonts)."""

TAGS = ["Falklands War", "Falklands", "Malvinas", "Guerra de Malvinas", "1982", "history", "documentary",
        "British history", "Argentina", "Margaret Thatcher", "Galtieri", "Task Force", "General Belgrano",
        "HMS Sheffield", "Exocet", "San Carlos", "Goose Green", "Tumbledown", "Mount Longdon", "Stanley",
        "Vulcan Black Buck", "Royal Navy", "Royal Marines", "Parachute Regiment", "Cold War",
        "military history", "short documentary"]


def ts(t):
    t = int(t)
    return f"{t // 60}:{t % 60:02d}"


def main():
    timing = json.load(open(os.path.join(BUILD, "timing.json")))
    segs = timing["segments"]
    chapters = []
    for i, s in enumerate(segs):
        start = 0.0 if i == 0 else s["start"] - 0.3
        chapters.append([start, s["chapter"]])
    # YouTube: chapters must be >= 10 s; fold short ones into the previous chapter
    merged = []
    for i, (st, name) in enumerate(chapters):
        nxt = chapters[i + 1][0] if i + 1 < len(chapters) else timing["total"]
        if merged and nxt - st < 10:
            merged[-1][1] += " / " + name
            continue
        merged.append([st, name])
    lines = [f"{ts(st)} {name}" for st, name in merged]
    desc = INTRO + "\n\nCHAPTERS\n" + "\n".join(lines) + "\n\n" + SOURCES + "\n\n#FalklandsWar #Malvinas #History"
    out = os.path.join(BUILD, "youtube_metadata.txt")
    with open(out, "w") as f:
        f.write("TITLE\n" + TITLE + "\n\nDESCRIPTION\n" + desc + "\n\nTAGS\n" + ", ".join(TAGS) + "\n")
        f.write("\nSETTINGS\nCategory: Education\nLanguage: English (United Kingdom)\n"
                "Captions: upload captions.srt (English)\nMade for kids: No\n")
    print(open(out).read())


if __name__ == "__main__":
    main()
