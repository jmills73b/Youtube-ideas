# The Falklands War, 1982 — a 5-minute documentary made entirely in code

A 4 min 53 s, 1080p30 YouTube-ready short documentary on the Falklands War: the
sovereignty dispute and the road to war, the key events of the 74-day conflict,
and how it ended. Every frame, map, sound effect and note of music is generated
by the code in this folder. There is no stock footage and no samples.

**Output** (in `output/`):

| File | What it is |
|---|---|
| `falklands_war_1982.mp4` | Repository copy (1080p30, compact bitrate, < 100 MB) |
| `falklands_war_1982_youtube_master.mp4` | Full-quality upload master (not committed; rebuild with `./build.sh final`) |
| `falklands_war_1982.en.srt` | English captions, timed to the narration |
| `thumbnail.jpg` | 1280×720 YouTube thumbnail |
| `youtube_metadata.txt` | Title, description with chapters and sources, tags |

## Uploading to YouTube

1. Upload `falklands_war_1982_youtube_master.mp4` if you have it, otherwise `falklands_war_1982.mp4`.
   Both are H.264 High / AAC-LC 48 kHz, `+faststart`, BT.709, loudness-normalised to −14 LUFS, which matches YouTube's recommended upload settings.
2. Paste the title, description (with chapters) and tags from `youtube_metadata.txt`.
3. Under *Subtitles*, upload `falklands_war_1982.en.srt` (English, UK).
4. Set the thumbnail to `thumbnail.jpg`. Category: Education.

Rights: the narration voice (Kokoro, Apache-2.0), music and effects (synthesised here), fonts (OFL/Apache) and map data
(Natural Earth public domain, geoBoundaries CC BY 4.0, credited in the description) are all cleared for use
on a monetised channel.

## Style: "1982"

Scenes switch between period looks, each applied as a post-process in `engine/fx.py`:

- **16mm news film** for the painted scenes: warm or cool grade, clumpy grain, gate weave, dust and scratches, bloom.
- **Early-80s TV news graphics** for maps and captions: navy sea, sand-coloured land, condensed type, red and blue campaign arrows, scanlines and chroma bleed.
- **Teletext** pages (40×25 grid, double-height headlines, block-mosaic map of the islands).
- **Typewritten documents**, an **engraved 18th-century chart**, and a **halftone print poster**.

Ships, aircraft and vehicles are drawn from real profiles (Type 42 and Type 21, *Hermes*, the Brooklyn-class
*Belgrano*, *Canberra*, *Sir Galahad*, *Endurance*, Skyhawk, Super Étendard, Harrier, Vulcan, Victor, Sea King, LVTP-7).
Maps use real coastlines. See `RESEARCH.md` for sources and the historian's notes behind every figure.

## Building

```bash
pip install pillow numpy scipy pycairo soundfile kokoro-onnx fonttools
sudo apt-get install ffmpeg libcairo2-dev espeak-ng
./build.sh          # ~15 min on 4 cores
```

Pipeline:

1. `tts.py` voices `script.py` sentence by sentence and writes `build/timing.json` and captions.
2. `render.py` renders the picture. Each shot in `scenes/__init__.py` is anchored to a narration sentence, so picture and voice stay locked. Frames are drawn with Cairo, graded with numpy, and encoded by ffmpeg in parallel chunks. `python3 render.py --stills` renders one PNG per shot for review.
3. `audio.py` synthesises the score (detuned string pads, a war-time ostinato, timpani, a closing lament) and sound effects cued from the shots, ducks them under the voice and writes `build/mix.wav`.
4. `build.sh` muxes and encodes the final files.

```
falklands/
  script.py          narration (the historian's script)
  RESEARCH.md        sources, figures, contested points
  tts.py render.py audio.py build.sh
  engine/            core (canvas/text/noise), fx (period looks), art (skies, sea, smoke, fire...),
                     vessels (ships/aircraft), people (figures, flags, buildings), maps (globe + flat maps)
  scenes/            the 35 shots, in three parts, plus shared helpers (captions, teletext, documents)
  tools/             geo_prep.py (coastline simplification), thumbnail.py, metadata.py
  assets/            fonts and simplified coastline data
```
