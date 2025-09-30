import torch
import torchaudio as ta
from chatterbox.tts import ChatterboxTTS
import shutil
import os
import subprocess
import json
import uuid
from pathlib import Path
from gradio_client import Client, handle_file
import sys

# -------- DEVICE SETUP --------
device = "cpu"
map_location = torch.device(device)

torch_load_original = torch.load
def patched_torch_load(*args, **kwargs):
    if "map_location" not in kwargs:
        kwargs["map_location"] = map_location
    return torch_load_original(*args, **kwargs)
torch.load = patched_torch_load

# Load model once per process
model = ChatterboxTTS.from_pretrained(device=device)

# -------- HELPERS --------
def generate_pause_with_breath(duration_ms: int, output_path: str, noise_level: float = -45.0):
    """Generate pause with light noise for breathing effect."""
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-t", f"{duration_ms/1000:.3f}",
        "-i", "anoisesrc=color=white:amplitude=0.1",
        "-f", "lavfi", "-t", f"{duration_ms/1000:.3f}",
        "-i", "anullsrc=r=24000:cl=mono",
        "-filter_complex", f"[0:a]volume={noise_level}dB[audionoise];"
                           f"[1:a][audionoise]amix=inputs=2:duration=shortest[out]",
        "-map", "[out]",
        "-ar", "24000", "-ac", "1",
        output_path
    ]
    subprocess.run(cmd, check=True)
    return output_path


def run_tts_pipeline(schema_path: str,reference_audio_path: str, output_tag: str):
    # -------- JOB-SPECIFIC DIRS --------
    job_id = output_tag+str(uuid.uuid4())[:8] 
    BASE_DIR = Path(f"speech_variation/run_{job_id}")
    PART_DIR = BASE_DIR / "part_audio"
    OUTPUT_DIR = BASE_DIR / "output"
    TEMP_PART_FILE = BASE_DIR / "part_temp.txt"
    OUTPUT_FILE_NAME = "output.wav"

    PART_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # -------- LOAD SCHEMA --------
    with open(schema_path) as f:
        data = json.load(f)

    client = Client("http://127.0.0.1:7860/")
    AUDIO_PROMPT_PATH = reference_audio_path

    # -------- SEQUENTIAL PROCESSING --------
    for i, entry in enumerate(data):
        target_path = PART_DIR / f"{i}.wav"

        if entry["text"] == "...":
            generate_pause_with_breath(entry["duration_ms"], str(target_path), noise_level=-40.0)
            print(f"[{job_id}] Added silence for {entry['duration_ms']} ms")
            continue

        result = client.predict(
            text_input=entry["text"],
            language_id="hi",
            audio_prompt_path_input=handle_file(AUDIO_PROMPT_PATH),
            exaggeration_input=entry["exaggeration"],
            temperature_input=0.8,
            seed_num_input=0,
            cfgw_input=entry["cfg"],
            api_name="/generate_tts_audio"
        )

        if isinstance(result, str):
            shutil.move(result, target_path)
        elif isinstance(result, list) and len(result) > 0:
            shutil.move(result[0], target_path)

        print(f"[{job_id}] Part audio saved: {target_path}")

    # -------- CONCAT --------
    with open(TEMP_PART_FILE, "w") as f:
        for i in range(len(data)):
            part_file = PART_DIR / f"{i}.wav"
            f.write(f"file '{part_file.resolve()}'\n")   # absolute path

    final_output = OUTPUT_DIR / OUTPUT_FILE_NAME
    subprocess.call([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(TEMP_PART_FILE), "-c", "copy", str(final_output)
    ])

    print(f"[{job_id}] Output file created: {final_output}")

    # -------- CLEANUP PARTS --------
    for filename in PART_DIR.iterdir():
        filename.unlink()
    PART_DIR.rmdir()
    TEMP_PART_FILE.unlink()
    print(f"[{job_id}] Cleaned temp audio: {PART_DIR}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tts_pipeline.py <schema.json>")
        sys.exit(1)

    schema_path = sys.argv[1]
    reference_audio_path = sys.argv[2]
    output_tag = sys.argv[3]
    run_tts_pipeline(schema_path,reference_audio_path,output_tag)
