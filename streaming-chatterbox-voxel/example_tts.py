import torchaudio as ta
import torch
from src.chatterbox.tts import ChatterboxTTS
from src.chatterbox.mtl_tts import ChatterboxMultilingualTTS

# Automatically detect the best available device
if torch.cuda.is_available():
    device = "cuda"
elif torch.backends.mps.is_available():
    device = "mps"
else:
    device = "cpu"

print(f"Using device: {device}")

model = ChatterboxTTS.from_pretrained(device=device)

# text = "Ezreal and Jinx teamed up with Ahri, Yasuo, and Teemo to take down the enemy's Nexus in an epic late-game pentakill."
# wav = model.generate(text)
# ta.save("test-1.wav", wav, model.sr)

# multilingual_model = ChatterboxMultilingualTTS.from_pretrained(device=device)
# text = "Bonjour, comment ça va? Ceci est le modèle de synthèse vocale multilingue Chatterbox, il prend en charge 23 langues."
# wav = multilingual_model.generate(text, language_id="fr")
# ta.save("test-2.wav", wav, multilingual_model.sr)

## load json data from file
import json
with open('./speech_variation_test/speech_schema.json') as f:
    data = json.load(f)
    # iterate over data
    for i in range(len(data)):
        text = data[i]['text']
        exaggeration = data[i]['exaggeration']
        cfg_weight = data[i]['cfg']


        # text = "I know what you're thinking.. 'How the hell does this work???' 'Believe me, even I don't know...' Looks like one day you wake up and just start speaking. And you're like.... 'Oh, I know what you're thinking. How the hell does this work?'"

        # If you want to synthesize with a different voice, specify the audio prompt
        AUDIO_PROMPT_PATH = "./resources/audio5.mp3"
        wav = model.generate(
            text, 
            audio_prompt_path=AUDIO_PROMPT_PATH,
            exaggeration=exaggeration,
            cfg_weight=cfg_weight
            )

        filename = "./speech_variation_test/part_audio/"+str(i)+".wav"
        ta.save(filename, wav, model.sr)

        # ta.save("test-sohel_talking_head1.wav", wav, model.sr)

## create a file (if not exist) part_tempt.txt
with open('./speech_variation_test/part_temp.txt', 'w') as f:
    # write all the file names in this file with a new line (file 'audio1.wav')
    for i in range(len(data)):
        f.write("file './part_audio/"+str(i)+".wav'\n")


import subprocess
subprocess.call(['ffmpeg', '-f', 'concat', '-safe', '0', '-i', './speech_variation_test/part_temp.txt', '-c', 'copy', './speech_variation_test/output/part_output.wav'])


# # If you want to synthesize with a different voice, specify the audio prompt
# AUDIO_PROMPT_PATH = "YOUR_FILE.wav"
# wav = model.generate(text, audio_prompt_path=AUDIO_PROMPT_PATH)
# ta.save("test-3.wav", wav, model.sr)
