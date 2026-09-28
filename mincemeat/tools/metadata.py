"""Write YouTube upload metadata (title, description with chapters, tags).

  python3 tools/metadata.py  ->  build/youtube_metadata.txt
"""
import json
import os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(HERE, "build")

TITLE = "Operation Mincemeat in 4 Minutes | The Dead Man Who Fooled Hitler (1943)"

INTRO = """In April 1943 a British submarine released a body off the coast of Spain. It was dressed as a Royal Marines officer, "Major William Martin", and carried secret letters suggesting the Allies would invade Greece and Sardinia. The real target was Sicily.

This short documentary tells the true story of Operation Mincemeat: the 1939 "Trout Memo", Charles Cholmondeley and Ewen Montagu, Glyndwr Michael - the Welshman whose body became Major Martin - the invented life in his pockets, the forged letters, HMS Seraph, the Germans in Huelva, the Ultra decrypts, the invasion of Sicily, and the grave in Huelva that finally bears his real name.

All pictures, maps and music were generated for this film in the style of 1943: black-and-white newsreel, secret files and War Office maps. Documents shown are reconstructions; quoted words follow published transcriptions. The body itself is never shown."""

SOURCES = """SOURCES AND FURTHER READING
- Ewen Montagu, The Man Who Never Was (1953)
- Ben Macintyre, Operation Mincemeat (2010)
- Denis Smyth, Deathly Deception: The Real Story of Operation Mincemeat (2010)
- Michael Howard, Strategic Deception in the Second World War (official history, 1990)
- Roger Morgan's research identifying Glyndwr Michael (1996)
- The National Archives, Kew (Mincemeat files)
- Commonwealth War Graves Commission: Huelva (Nuestra Senora de la Soledad) Cemetery
- Imperial War Museums; The National WWII Museum

MAP DATA: Natural Earth (public domain).
NARRATION: synthetic voice (Kokoro TTS, Apache-2.0). MUSIC & SOUND: original, synthesised for this film.
FONTS: Old Standard TT, Courier Prime, Stardos Stencil (SIL Open Font License)."""

TAGS = ["Operation Mincemeat", "The Man Who Never Was", "WW2", "World War II", "Second World War", "deception",
        "espionage", "MI5", "Ewen Montagu", "Charles Cholmondeley", "Ian Fleming", "Trout Memo", "Glyndwr Michael",
        "Major William Martin", "HMS Seraph", "Huelva", "Operation Husky", "invasion of Sicily", "Bletchley Park",
        "Ultra", "Abwehr", "history", "documentary", "military history", "short documentary"]


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
    desc = INTRO + "\n\nCHAPTERS\n" + "\n".join(lines) + "\n\n" + SOURCES + "\n\n#OperationMincemeat #WW2 #History"
    out = os.path.join(BUILD, "youtube_metadata.txt")
    with open(out, "w") as f:
        f.write("TITLE\n" + TITLE + "\n\nDESCRIPTION\n" + desc + "\n\nTAGS\n" + ", ".join(TAGS) + "\n")
        f.write("\nSETTINGS\nCategory: Education\nLanguage: English (United Kingdom)\n"
                "Captions: upload captions.srt (English)\nMade for kids: No\n")
    print(open(out).read())


if __name__ == "__main__":
    main()
