"""Write YouTube upload metadata (title, description with chapters, tags).

  python3 tools/metadata.py  ->  build/youtube_metadata.txt
"""
import json
import os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(HERE, "build")

TITLE = "The Battle of the Somme in 5 Minutes | 1916: The First Day, the Tanks, the Cost"

INTRO = """On 1 July 1916, the British Army suffered 57,470 casualties - the worst day in its history. Over the next 141 days, the Battle of the Somme cost more than a million men killed, wounded, missing or captured, for an advance of no more than seven miles.

This short documentary covers why the battle was fought (Chantilly and Verdun), Kitchener's volunteer army and the Pals battalions, the week-long bombardment and why it failed, the mines and zero hour, the Accrington Pals at Serre and the Newfoundland Regiment at Beaumont-Hamel, Bazentin Ridge, Delville Wood, Pozieres, the first tanks at Flers-Courcelette, the fall of Thiepval, the mud of autumn, and the debate over the battle's legacy.

All pictures, maps and music were generated for this film in the style of 1916: tinted silent film with intertitles, and British trench maps with German trenches in red. Illustrations are artistic reconstructions; front lines on maps are schematic."""

SOURCES = """SOURCES AND FURTHER READING
- J.E. Edmonds & W. Miles, Military Operations, France and Belgium, 1916 (British Official History, 1932-38)
- Martin Middlebrook, The First Day on the Somme (1971)
- William Philpott, Bloody Victory: The Sacrifice on the Somme (2009)
- Gary Sheffield, The Somme (2003)
- Robin Prior & Trevor Wilson, The Somme (2005)
- Peter Hart, The Somme (2005)
- Jack Sheldon, The German Army on the Somme 1914-1916 (2005)
- William Turner, Accrington Pals (1987)
- Imperial War Museums; National Army Museum; Commonwealth War Graves Commission (Thiepval Memorial)
- Veterans Affairs Canada (Beaumont-Hamel); Australian War Memorial (Pozieres); The Tank Museum (Flers)

Casualty figures: British Empire c. 420,000; French c. 200,000; German estimates range from c. 430,000 to 600,000 (the film uses "at least 450,000").
MAP DATA: Natural Earth (public domain); French commune boundaries, IGN via france-geojson (Licence Ouverte).
NARRATION: synthetic voice (Kokoro TTS, Apache-2.0). MUSIC & SOUND: original, synthesised for this film.
FONTS: IM Fell, Old Standard TT (SIL Open Font License)."""

TAGS = ["Battle of the Somme", "Somme", "1916", "First World War", "WW1", "World War One", "Great War",
        "history", "documentary", "first day of the Somme", "Accrington Pals", "Newfoundland Regiment",
        "Beaumont-Hamel", "Thiepval", "Lochnagar", "Delville Wood", "Pozieres", "Flers-Courcelette", "first tanks",
        "Mark I tank", "Douglas Haig", "Kitchener's Army", "Pals battalions", "Western Front", "military history",
        "short documentary"]


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
    desc = INTRO + "\n\nCHAPTERS\n" + "\n".join(lines) + "\n\n" + SOURCES + "\n\n#Somme #WW1 #History"
    out = os.path.join(BUILD, "youtube_metadata.txt")
    with open(out, "w") as f:
        f.write("TITLE\n" + TITLE + "\n\nDESCRIPTION\n" + desc + "\n\nTAGS\n" + ", ".join(TAGS) + "\n")
        f.write("\nSETTINGS\nCategory: Education\nLanguage: English (United Kingdom)\n"
                "Captions: upload captions.srt (English)\nMade for kids: No\n")
    print(open(out).read())


if __name__ == "__main__":
    main()
