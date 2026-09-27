#!/usr/bin/env bash
# Build "The Battle of the Somme, 1916" end to end. Shares the TTS model and
# drawing engine with ../falklands.
#   ./build.sh            full build (narration, picture, audio, final encodes)
#   ./build.sh final      only mux/encode from existing build/video.mp4 + build/mix.wav
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p build output

if [[ "${1:-}" != "final" ]]; then
  if [[ ! -f ../falklands/models/kokoro-v1.0.onnx ]]; then
    (cd ../falklands && mkdir -p models && curl -L -o models/kokoro-v1.0.onnx https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx && curl -L -o models/voices-v1.0.bin https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin)
  fi
  python3 tts.py                    # narration.wav, timing.json, captions.srt
  python3 render.py                 # build/video.mp4 (picture only)
  python3 audio.py                  # build/mix.wav (voice + score + effects)
  python3 tools/thumbnail.py        # build/thumbnail.jpg
  python3 tools/metadata.py > /dev/null
fi

# 1) YouTube master: H.264 High, 1080p30, closed GOP of 15, AAC-LC 384k 48kHz, -14 LUFS, faststart
ffmpeg -y -loglevel error -i build/video.mp4 -i build/mix.wav \
  -map 0:v -map 1:a \
  -c:v libx264 -preset slow -crf 17 -profile:v high -level 4.1 -pix_fmt yuv420p \
  -r 30 -g 15 -keyint_min 15 -sc_threshold 0 -bf 2 -coder cabac \
  -color_primaries bt709 -color_trc bt709 -colorspace bt709 \
  -af "loudnorm=I=-14:TP=-1.5:LRA=11" -c:a aac -b:a 384k -ar 48000 -ac 2 \
  -movflags +faststart -metadata title="The Battle of the Somme, 1916" \
  output/battle_of_the_somme_1916_youtube_master.mp4

# 2) Compact copy that fits in a GitHub repository (< 100 MB)
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 build/video.mp4)
VBR=$(python3 -c "print(int((92*8*1024*1024/${DUR} - 160000)/1000))")
ffmpeg -y -loglevel error -i output/battle_of_the_somme_1916_youtube_master.mp4 -c:v libx264 -preset slow \
  -b:v ${VBR}k -g 15 -bf 2 -pass 1 -an -f mp4 -passlogfile build/x264pass /dev/null
ffmpeg -y -loglevel error -i output/battle_of_the_somme_1916_youtube_master.mp4 -c:v libx264 -preset slow \
  -b:v ${VBR}k -pass 2 -passlogfile build/x264pass -profile:v high -pix_fmt yuv420p -g 15 -bf 2 \
  -c:a aac -b:a 160k -movflags +faststart output/battle_of_the_somme_1916.mp4

cp build/captions.srt output/battle_of_the_somme_1916.en.srt
cp build/thumbnail.jpg output/thumbnail.jpg
cp build/youtube_metadata.txt output/youtube_metadata.txt
ls -la output
