import queue
import torchaudio as ta
import torch
import threading
import time
from chatterbox.tts import ChatterboxTTS

# Try to import audio playback library
try:
    import sounddevice as sd
    import numpy as np
    AUDIO_AVAILABLE = True
    print("Using sounddevice for audio playback")
except ImportError:
    AUDIO_AVAILABLE = False
    print("sounddevice not available. Install with: pip install sounddevice")

class ContinuousAudioPlayer:
    """Continuous audio player that prevents chunk cutoffs"""
    def __init__(self, sample_rate, buffer_size=8192):
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        self.audio_buffer = np.array([], dtype=np.float32)
        self.stream = None
        self.playing = False
        self.lock = threading.Lock()
        
    def start(self):
        if not AUDIO_AVAILABLE:
            return
            
        def audio_callback(outdata, frames, time, status):
            with self.lock:
                if len(self.audio_buffer) >= frames:
                    outdata[:, 0] = self.audio_buffer[:frames]
                    self.audio_buffer = self.audio_buffer[frames:]
                else:
                    # Not enough data, pad with zeros
                    available = len(self.audio_buffer)
                    outdata[:available, 0] = self.audio_buffer
                    outdata[available:, 0] = 0
                    self.audio_buffer = np.array([], dtype=np.float32)
        
        self.stream = sd.OutputStream(
            samplerate=self.sample_rate,
            channels=1,
            callback=audio_callback,
            blocksize=self.buffer_size
        )
        self.stream.start()
        self.playing = True
        
    def add_audio(self, audio_chunk):
        """Add audio chunk to the continuous buffer"""
        if not AUDIO_AVAILABLE or not self.playing:
            return
            
        audio_np = audio_chunk.squeeze().numpy().astype(np.float32)
        with self.lock:
            self.audio_buffer = np.concatenate([self.audio_buffer, audio_np])
            
    def stop(self):
        if self.stream and self.playing:
            # Wait for buffer to empty
            while len(self.audio_buffer) > 0:
                time.sleep(0.1)
            self.stream.stop()
            self.stream.close()
            self.playing = False

def play_audio_chunk(audio_chunk, sample_rate):
    """Play audio chunk using sounddevice with proper sequencing"""
    if not AUDIO_AVAILABLE:
        return
    
    try:
        # Convert to numpy and play with sounddevice
        audio_np = audio_chunk.squeeze().numpy()
        sd.play(audio_np, sample_rate)
        sd.wait()  # Wait for this chunk to finish before returning
    except Exception as e:
        print(f"Error playing audio: {e}")

def audio_player_worker(audio_queue, sample_rate):
    """Worker thread that plays audio chunks from queue"""
    while True:
        try:
            audio_chunk = audio_queue.get(timeout=1.0)
            if audio_chunk is None:  # Sentinel to stop
                break
            play_audio_chunk(audio_chunk, sample_rate)
            audio_queue.task_done()
        except queue.Empty:
            continue
        except Exception as e:
            print(f"Audio player error: {e}")

# Automatically detect the best available device
if torch.cuda.is_available():
    device = "cuda"
elif torch.backends.mps.is_available():
    device = "mps"
else:
    device = "cpu"

print(f"Using device: {device}")
model = ChatterboxTTS.from_pretrained(device=device)

text = "Ezreal and Jinx teamed up with Ahri, Yasuo, and Teemo to take down the enemy's Nexus in an epic late-game pentakill."

# Original non-streaming generation
print("Generating audio (non-streaming)...")
wav = None
try:
    wav = model.generate(text)
    ta.save("test-1.wav", wav, model.sr)
    print(f"Saved non-streaming audio to test-1.wav")
except Exception as e:
    print(f"Error in non-streaming generation: {e}")
    wav = None

# Test streaming generation with real-time playback
print("\nGenerating audio (streaming with real-time playback)...")
streamed_chunks = []
chunk_count = 0

# Setup audio playback queue and thread
if AUDIO_AVAILABLE:
    audio_queue = queue.Queue()
    audio_thread = threading.Thread(target=audio_player_worker, args=(audio_queue, model.sr))
    audio_thread.daemon = True
    audio_thread.start()
    print("Real-time audio playback enabled!")
else:
    audio_queue = None

try:
    for audio_chunk, metrics in model.generate_stream(
        text=text,
        chunk_size=25,  # tokens per chunk
        exaggeration= 0.5,
        temperature=0.8,
        cfg_weight=0.5,
        print_metrics=True
    ):
        chunk_count += 1
        streamed_chunks.append(audio_chunk)
        
        # Queue audio for immediate playback
        if AUDIO_AVAILABLE and audio_queue:
            audio_queue.put(audio_chunk.clone())
        
        chunk_duration = audio_chunk.shape[-1] / model.sr
        print(f"Received chunk {chunk_count}, shape: {audio_chunk.shape}, duration: {chunk_duration:.3f}s")
        
        if chunk_count == 1:
            print("Audio playback started!")

except KeyboardInterrupt:
    print("\nPlayback interrupted by user")
except Exception as e:
    print(f"Error during streaming generation: {e}")

# Stop audio thread
if AUDIO_AVAILABLE and audio_queue:
    audio_queue.join()  # Wait for all audio to finish playing
    audio_queue.put(None)  # Sentinel to stop thread

# Concatenate all streaming chunks
if streamed_chunks:
    full_streamed_audio = torch.cat(streamed_chunks, dim=-1)
    ta.save("test-streaming.wav", full_streamed_audio, model.sr)
    print(f"\nSaved streaming audio to test-streaming.wav")
    print(f"Total streaming chunks: {len(streamed_chunks)}")
    print(f"Final audio shape: {full_streamed_audio.shape}")
    print(f"Final audio duration: {full_streamed_audio.shape[-1] / model.sr:.3f}s")
    
else:
    print("No audio chunks were generated!")

print("\n" + "="*60)
print("STREAMING DEMO COMPLETE!")