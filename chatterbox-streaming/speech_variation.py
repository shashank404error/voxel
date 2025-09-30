import torch
import torchaudio as ta
from chatterbox.tts import ChatterboxTTS
import shutil
import os
import subprocess

# Detect device (Mac with M1/M2/M3/M4)
# device = "mps" if torch.backends.mps.is_available() else "cpu"
device = "cpu"
map_location = torch.device(device)

torch_load_original = torch.load
def patched_torch_load(*args, **kwargs):
    if 'map_location' not in kwargs:
        kwargs['map_location'] = map_location
    return torch_load_original(*args, **kwargs)

torch.load = patched_torch_load

model = ChatterboxTTS.from_pretrained(device=device)

STORE_PART_AUDIO_DIR = "speech_variation/part_audio"
os.makedirs(STORE_PART_AUDIO_DIR, exist_ok=True)
TEMP_PART_AUDIO_DETAIL_FILE = "speech_variation/part_temp.txt"
OUTPUT_FILE_NAME = "output.wav"

def generate_pause_with_breath(duration_ms: int, output_path: str, noise_level: float = -45.0):
    """
    Generate a silent chunk with light noise (like breathing) using ffmpeg.

    Args:
        duration_ms (int): Duration of the pause in milliseconds.
        output_path (str): Path to save the generated audio file (wav).
        noise_level (float): Volume of noise in dB (default: -45 dB, very subtle).
    """

    # ffmpeg filter: combine silence with low-level white noise
    # - `anullsrc` = silence
    # - `anoisesrc` = noise generator
    # - mix with volume adjustment
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-t", f"{duration_ms/1000:.3f}",
        "-i", f"anoisesrc=color=white:amplitude=0.1",
        "-f", "lavfi", "-t", f"{duration_ms/1000:.3f}",
        "-i", "anullsrc=r=24000:cl=mono",  # silence at 24kHz mono
        "-filter_complex", f"[0:a]volume={noise_level}dB[audionoise];[1:a][audionoise]amix=inputs=2:duration=shortest[out]",
        "-map", "[out]",
        "-ar", "24000",  # sample rate 24kHz (adjust to match your TTS output)
        "-ac", "1",      # mono
        output_path
    ]

    subprocess.run(cmd, check=True)
    return output_path

## load json data from file
import json
with open('./speech_variation/speech_schema.json') as f:
    data = json.load(f)
    # iterate over data
    for i in range(len(data)):
        text = data[i]['text']
        exaggeration = data[i]['exaggeration']
        cfg_weight = data[i]['cfg']

        # Check if we need to add silence
        if text == "...":
            duration_ms = data[i]['duration_ms']
            generate_pause_with_breath(duration_ms, "./speech_variation/part_audio/"+str(i)+".wav", noise_level=-40.0)
            print("[VOXEL] Added silence for ",duration_ms," ms")
            continue

        # If you want to synthesize with a different voice, specify the audio prompt
        AUDIO_PROMPT_PATH = "./resources/sp.mp3"

        from gradio_client import Client, handle_file

        client = Client("http://127.0.0.1:7860/")
        result = client.predict(
                text_input=text,
                language_id="hi",
                audio_prompt_path_input=handle_file(AUDIO_PROMPT_PATH),
                exaggeration_input=exaggeration,
                temperature_input=0.8,
                seed_num_input=0,
                cfgw_input=cfg_weight,
                api_name="/generate_tts_audio"
        )
        
        if isinstance(result, str):
            filename = os.path.basename(result)
            target_path = os.path.join(STORE_PART_AUDIO_DIR, str(i)+".wav")
            shutil.move(result, target_path)
            print(f"[VOXEL] Part audio file moved to: {target_path}")
        elif isinstance(result, list):
            moved_files = []
            for f in result:
                filename = os.path.basename(f)
                target_path = os.path.join(STORE_PART_AUDIO_DIR, str(i)+".wav")
                shutil.move(f, target_path)
                moved_files.append(target_path)
            print("[VOXEL] Moved part audio files:", moved_files)

## create a file (if not exist) part_tempt.txt
with open(TEMP_PART_AUDIO_DETAIL_FILE, 'w') as f:
    # write all the file names in this file with a new line (file 'audio1.wav')
    for i in range(len(data)):
        f.write("file './part_audio/"+str(i)+".wav'\n")
print("[VOXEL] Part audio detail file created: ", TEMP_PART_AUDIO_DETAIL_FILE)

subprocess.call(['ffmpeg', '-f', 'concat', '-safe', '0', '-i', './speech_variation/part_temp.txt', '-c', 'copy', './speech_variation/output/'+OUTPUT_FILE_NAME])
print("[VOXEL] Output file created: ", './speech_variation/output/'+OUTPUT_FILE_NAME)

## Delete all the files in part_audio directory
for filename in os.listdir(STORE_PART_AUDIO_DIR):
    file_path = os.path.join(STORE_PART_AUDIO_DIR, filename)
    try:
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
    except Exception as e:
        print('[VOXEL] Failed to delete %s. Reason: %s' % (file_path, e))
print("[VOXEL] Part audio directory cleaned: ", STORE_PART_AUDIO_DIR)


