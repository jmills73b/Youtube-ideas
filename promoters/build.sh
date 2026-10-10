#!/usr/bin/env bash
# Build "The Promoters" end to end. Shares the TTS model and drawing engine with ../falklands.
#   ./build.sh          full build      ./build.sh final   only the encodes
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p build output
if [[ "${1:-}" != "final" ]]; then
  python3 tts.py          # build/dialogue.wav, timeline.json, env.npy (lip sync), captions.srt
  python3 film.py         # build/video.mp4 + build/mix.wav
  python3 thumbnail.py    # output/thumbnail.jpg
fi
# YouTube master: H.264 High 1080p30, closed GOP 15, AAC 384k 48 kHz, -14 LUFS, faststart
ffmpeg -y -loglevel error -i build/video.mp4 -i build/mix.wav -map 0:v -map 1:a \
  -c:v libx264 -preset slow -crf 17 -profile:v high -level 4.1 -pix_fmt yuv420p \
  -r 30 -g 15 -keyint_min 15 -sc_threshold 0 -bf 2 \
  -color_primaries bt709 -color_trc bt709 -colorspace bt709 \
  -af "loudnorm=I=-14:TP=-1.5:LRA=11" -c:a aac -b:a 384k -ar 48000 -ac 2 \
  -movflags +faststart -metadata title="The Promoters (a parody)" output/the_promoters_youtube_master.mp4
# Compact copy for the repository
ffmpeg -y -loglevel error -i output/the_promoters_youtube_master.mp4 -c:v libx264 -preset slow -crf 22 \
  -profile:v high -pix_fmt yuv420p -g 15 -bf 2 -c:a aac -b:a 160k -movflags +faststart output/the_promoters.mp4
cp build/captions.srt output/the_promoters.en.srt
ls -la output
