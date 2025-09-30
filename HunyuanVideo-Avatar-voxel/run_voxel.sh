#!/bin/bash

# Usage:
# ./run_voxel.sh -a <audio_file> -p <prompt> -f <fps> -i <image_path> -o <output_audio_dir> -d <csv_folder> -t <tag>
# bash run_voxel.sh -a assets/raw_audio/test_c.mp3 -p "This is an engineer talking with his audience with confidence." -f 25 -i assets/image/sp.jpg -o assets/audio -d assets -t sp_hyperchaos

while getopts "a:p:f:i:o:d:t:" flag; do
  case "$flag" in
    a) AUDIO_FILE="$OPTARG" ;;
    p) PROMPT="$OPTARG" ;;
    f) FPS="$OPTARG" ;;
    i) IMAGE_PATH="$OPTARG" ;;
    o) OUTPUT_DIR="$OPTARG" ;;
    d) CSV_FOLDER="$OPTARG" ;;
    t) TAG="$OPTARG" ;;
    *) 
       echo "Usage: $0 -a <audio_file> -p <prompt> -f <fps> -i <image_path> -o <output_audio_dir> -d <csv_folder> -t <tag>"
       exit 1 ;;
  esac
done

if [ -z "$AUDIO_FILE" ] || [ -z "$PROMPT" ] || [ -z "$FPS" ] || [ -z "$IMAGE_PATH" ] || [ -z "$OUTPUT_DIR" ] || [ -z "$CSV_FOLDER" ] || [ -z "$TAG" ]; then
    echo "All parameters are required."
    exit 1
fi

mkdir -p "$OUTPUT_DIR"
mkdir -p "$CSV_FOLDER"

UNIQUE_ID=$(date +%s%N)
CSV_FILE="$CSV_FOLDER/driver_${TAG}_${UNIQUE_ID}.csv"

# Write CSV header
echo "videoid,image,audio,prompt,fps" > "$CSV_FILE"

VIDEO_ID=1
EXT="${AUDIO_FILE##*.}"

# Split audio into 5-second chunks and rename sequentially
DURATION=$(ffprobe -i "$AUDIO_FILE" -show_entries format=duration -v quiet -of csv="p=0")
START=0
CHUNK_NUM=1

while (( $(echo "$START < $DURATION" | bc -l) )); do
    OUTPUT_FILE="$OUTPUT_DIR/${TAG}_${CHUNK_NUM}.${EXT}"
    ffmpeg -y -i "$AUDIO_FILE" -ss "$START" -t 5 "$OUTPUT_FILE"
    echo "$VIDEO_ID,$IMAGE_PATH,$OUTPUT_FILE,$PROMPT,$FPS" >> "$CSV_FILE"
    START=$(echo "$START + 5" | bc)
    ((CHUNK_NUM++))
    ((VIDEO_ID++))
done

echo "Audio chunks saved in $OUTPUT_DIR and CSV created at $CSV_FILE"
