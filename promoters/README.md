# The Promoters (a parody)

This is a 1 min 45 s animated mockumentary sketch in the style of a British workplace documentary. It is built on the real autumn-2026 public spat over whether Dana White can promote Anthony Joshua vs Tyson Fury: he says he is promoting it; Eddie Hearn says that, contractually, he can't.

It is made entirely in code: cartoon caricatures drawn with cairo, lip-synced to generic synthetic voices (Kokoro TTS), with office ambience and an original guitar sting. It shares the drawing engine and TTS model with `../falklands`.

## Output

All files are in `output/`.

| File | What it is |
|---|---|
| `the_promoters.mp4` | Repository copy (1080p30) |
| `the_promoters_youtube_master.mp4` | Upload master (not committed; rebuild with `./build.sh final`) |
| `the_promoters.en.srt` | Captions |
| `thumbnail.jpg` | 1280×720 thumbnail |
| `youtube_metadata.txt` | Title, description, tags, disclosures |

## Files

| File | What it does |
|---|---|
| `script.py` | The beats; `# REAL` marks lines that echo reported public statements (see `RESEARCH.md`) |
| `tts.py` | Voices each line and writes the timeline, per-frame mouth envelope and captions |
| `toons.py` | The characters (poses, blinks, glances, mouths) |
| `film.py` | Office sets, documentary camera, shots, render and sound mix |

## Build

```bash
./build.sh                  # ~8 min on 4 cores
python3 film.py --stills    # one PNG per shot, for review
```

## Before uploading

In YouTube Studio, under "Altered or synthetic content", answer **Yes**, because the film depicts real people speaking words they did not say. The description and end card also say it is a parody.
