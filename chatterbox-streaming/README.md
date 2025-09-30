# Chatterbox TTS Streaming
Chatterbox is an open source TTS model. Licensed under MIT, Chatterbox has been benchmarked against leading closed-source systems like ElevenLabs, and is consistently preferred in side-by-side evaluations.
Whether you're working on memes, videos, games, or AI agents, Chatterbox brings your content to life. It's also the first open source TTS model to support **emotion exaggeration control**, a powerful feature that makes your voices stand out. This fork adds a streaming implementation that achieves a realtime factor of 0.499 (target < 1) on a 4090 gpu and a latency to first chunk of around 0.472s

# Key Details
- SoTA zeroshot TTS
- 0.5B Llama backbone
- Unique exaggeration/intensity control
- Ultra-stable with alignment-informed inference
- Trained on 0.5M hours of cleaned data
- Watermarked outputs
- Easy voice conversion script
- **Real-time streaming generation**
- [Outperforms ElevenLabs]

# Tips
- **General Use (TTS and Voice Agents):**
- The default settings (`exaggeration=0.5`, `cfg_weight=0.5`) work well for most prompts.
- If the reference speaker has a fast speaking style, lowering `cfg_weight` to around `0.3` can improve pacing.
- **Expressive or Dramatic Speech:**
- Try lower `cfg_weight` values (e.g. `~0.3`) and increase `exaggeration` to around `0.7` or higher.
- Higher `exaggeration` tends to speed up speech; reducing `cfg_weight` helps compensate with slower, more deliberate pacing.

# Installation
```
python3.10 -m venv .venv
source .venv/bin/activate
pip install chatterbox-streaming
```

## Build for development
```
git clone https://github.com/davidbrowne17/chatterbox-streaming.git
pip install -e .
```

# Usage

## Basic TTS Generation
```python
import torchaudio as ta
from chatterbox.tts import ChatterboxTTS

model = ChatterboxTTS.from_pretrained(device="cuda")
text = "Ezreal and Jinx teamed up with Ahri, Yasuo, and Teemo to take down the enemy's Nexus in an epic late-game pentakill."
wav = model.generate(text)
ta.save("test-1.wav", wav, model.sr)

# If you want to synthesize with a different voice, specify the audio prompt
AUDIO_PROMPT_PATH = "YOUR_FILE.wav"
wav = model.generate(text, audio_prompt_path=AUDIO_PROMPT_PATH)
ta.save("test-2.wav", wav, model.sr)
```

## Streaming TTS Generation
For real-time applications where you want to start playing audio as soon as it's available:

```python
import torchaudio as ta
import torch
from chatterbox.tts import ChatterboxTTS

model = ChatterboxTTS.from_pretrained(device="cuda")
text = "Welcome to the world of streaming text-to-speech! This audio will be generated and played in real-time chunks."

# Basic streaming
audio_chunks = []
for audio_chunk, metrics in model.generate_stream(text):
    audio_chunks.append(audio_chunk)
    # You can play audio_chunk immediately here for real-time playback
    print(f"Generated chunk {metrics.chunk_count}, RTF: {metrics.rtf:.3f}" if metrics.rtf else f"Chunk {metrics.chunk_count}")

# Combine all chunks into final audio
final_audio = torch.cat(audio_chunks, dim=-1)
ta.save("streaming_output.wav", final_audio, model.sr)
```

## Streaming with Voice Cloning
```python
import torchaudio as ta
import torch
from chatterbox.tts import ChatterboxTTS

model = ChatterboxTTS.from_pretrained(device="cuda")
text = "This streaming synthesis will use a custom voice from the reference audio file."
AUDIO_PROMPT_PATH = "reference_voice.wav"

audio_chunks = []
for audio_chunk, metrics in model.generate_stream(
    text, 
    audio_prompt_path=AUDIO_PROMPT_PATH,
    exaggeration=0.7,
    cfg_weight=0.3,
    chunk_size=25  # Smaller chunks for lower latency
):
    audio_chunks.append(audio_chunk)
    
    # Real-time metrics available
    if metrics.latency_to_first_chunk:
        print(f"First chunk latency: {metrics.latency_to_first_chunk:.3f}s")

# Save the complete streaming output
final_audio = torch.cat(audio_chunks, dim=-1)
ta.save("streaming_voice_clone.wav", final_audio, model.sr)
```

## Streaming Parameters
- `audio_prompt_path`: Reference audio path for voice cloning
- `chunk_size`: Number of speech tokens per chunk (default: 50). Smaller values = lower latency but more overhead
- `print_metrics`: Enable automatic printing of latency and RTF metrics (default: True)
- `exaggeration`: Emotion intensity control (0.0-1.0+)
- `cfg_weight`: Classifier-free guidance weight (0.0-1.0)
- `temperature`: Sampling randomness (0.1-1.0)

See `example_tts_stream.py` for more examples.

## Lora Fine-tuning
To fine-tune Chatterbox all you need are some wav audio files with the speaker voice you want to train, just the raw wavs. Place them in a folder called audio_data and run lora.py. You can configure the exact training params such as batch size, number of epochs and learning rate by modifying the values at the top of lora.py. You will need a CUDA gpu with at least 18gb of vram depending on your dataset size and training params. You can monitor the training metrics via the dynamic png created called training_metrics. This contains various graphs to help you track the training progress. If you want to try a checkpoint you can use the loadandmergecheckpoint.py (make sure to set the same R and Alpha values as you used in the training)

## GRPO Fine-tuning
Just like the lora fine-tuning for Chatterbox all you need are some wav audio files with the speaker voice you want to train, just the raw wavs. Place them in a folder called audio_data and run grpo.py. You can configure the exact training params such as batch size, number of epochs and learning rate by modifying the values at the top of grpo.py. You will need a CUDA gpu with at least 12gb of vram depending on your dataset size and training params. You can monitor the training metrics via the dynamic png created called grpo_training_metrics. This contains various graphs to help you track the training progress.

## Example metrics
Here are the example metrics for streaming latency on a 4090 using Linux
- Latency to first chunk: 0.472s
- Received chunk 1, shape: torch.Size([1, 24000]), duration: 1.000s
- Audio playback started!
- Received chunk 2, shape: torch.Size([1, 24000]), duration: 1.000s
- Received chunk 3, shape: torch.Size([1, 24000]), duration: 1.000s
- Received chunk 4, shape: torch.Size([1, 24000]), duration: 1.000s
- Received chunk 5, shape: torch.Size([1, 24000]), duration: 1.000s
- Received chunk 6, shape: torch.Size([1, 20160]), duration: 0.840s
- Total generation time: 2.915s
- Total audio duration: 5.840s
- RTF (Real-Time Factor): 0.499 (target < 1)
- Total chunks yielded: 6

# Acknowledgements
- [Cosyvoice](https://github.com/FunAudioLLM/CosyVoice)
- [Real-Time-Voice-Cloning](https://github.com/CorentinJ/Real-Time-Voice-Cloning)
- [HiFT-GAN](https://github.com/yl4579/HiFTNet)
- [Llama 3](https://github.com/meta-llama/llama3)
- [S3Tokenizer](https://github.com/xingchensong/S3Tokenizer)

# Built-in PerTh Watermarking for Responsible AI
Every audio file generated by Chatterbox includes [Resemble AI's Perth (Perceptual Threshold) Watermarker](https://github.com/resemble-ai/perth) - imperceptible neural watermarks that survive MP3 compression, audio editing, and common manipulations while maintaining nearly 100% detection accuracy.

# Disclaimer
Don't use this model to do bad things. Prompts are sourced from freely available data on the internet.

## Streaming Implementation Author
David Browne

## Support me
Support this project on Ko-fi: https://ko-fi.com/davidbrowne17
