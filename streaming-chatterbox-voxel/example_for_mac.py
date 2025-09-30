import torch
import torchaudio as ta
from src.chatterbox.tts import ChatterboxTTS
import shutil
import os

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
os.makedirs(SAVE_DIR, exist_ok=True)


## load json data from file
import json
with open('./speech_variation/speech_schema.json') as f:
    data = json.load(f)
    # iterate over data
    for i in range(len(data)):
        text = data[i]['text']
        exaggeration = data[i]['exaggeration']
        cfg_weight = data[i]['cfg']

        # If you want to synthesize with a different voice, specify the audio prompt
        AUDIO_PROMPT_PATH = "./resources/clean_audio.mp3"
        
        # wav = model.generate(
        #     text,  
        #     audio_prompt_path=AUDIO_PROMPT_PATH,
        #     exaggeration=exaggeration,
        #     cfg_weight=cfg_weight
        #     )

        # wav = generate_tts_audio(
        #     text,
        #     "hi", 
        #     audio_prompt_path_input=AUDIO_PROMPT_PATH,
        #     exaggeration_input=exaggeration,
        #     temperature_input=0,
        #     cfgw_input=cfg_weight
        #     )

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
        print(result)            

        # filename = "./speech_variation/part_audio/"+str(i)+".wav"
        # ta.save(filename, wav, model.sr)

        # ta.save("test-sohel_talking_head1.wav", wav, model.sr)

## create a file (if not exist) part_tempt.txt
with open('./speech_variation/part_temp.txt', 'w') as f:
    # write all the file names in this file with a new line (file 'audio1.wav')
    for i in range(len(data)):
        f.write("file './part_audio/"+str(i)+".wav'\n")


import subprocess
subprocess.call(['ffmpeg', '-f', 'concat', '-safe', '0', '-i', './speech_variation/part_temp.txt', '-c', 'copy', './speech_variation/output/part_output.wav'])


# wav = generate_tts_audio(
#     text,
#     "hi", 
#     audio_prompt_path_input=AUDIO_PROMPT_PATH,
#     exaggeration_input=0.0,
#     temperature_input=0,
#     cfgw_input=0.5
#     )
# ta.save("test-hindi.wav", wav, model.sr)