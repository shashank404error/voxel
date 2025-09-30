import os
import argparse
from pydub import AudioSegment

# python preprocess_audio.py --input raw_audio/neelesh_sir_final.wav --output audio_data --clip_length 15 --overlap 1

def split_and_normalize(audio_path, out_dir, clip_length=15_000, overlap=1_000):
    """
    Splits an audio file into smaller clips and normalizes loudness.
    
    Args:
        audio_path (str): Path to the input audio file.
        out_dir (str): Directory to save processed clips.
        clip_length (int): Length of each clip in milliseconds (default 15s).
        overlap (int): Overlap between clips in ms (default 1s).
    """
    os.makedirs(out_dir, exist_ok=True)
    audio = AudioSegment.from_file(audio_path)

    # normalize loudness to -20 dBFS (you can tweak this)
    change_in_dBFS = -20.0 - audio.dBFS
    audio = audio.apply_gain(change_in_dBFS)

    total_len = len(audio)
    counter = 0

    for start in range(0, total_len, clip_length - overlap):
        end = min(start + clip_length, total_len)
        clip = audio[start:end]

        # skip clips shorter than 5 sec (to avoid useless fragments)
        if len(clip) < 5_000:
            continue

        out_path = os.path.join(out_dir, f"clip_{counter:04d}.wav")
        clip.export(out_path, format="wav")
        print(f"Saved {out_path} ({len(clip)/1000:.2f}s)")
        counter += 1

    print(f"\n✅ Done! Extracted {counter} clips into {out_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to input audio file (mp3/wav/etc.)")
    parser.add_argument("--output", required=True, help="Directory to save processed clips")
    parser.add_argument("--clip_length", type=int, default=15, help="Clip length in seconds")
    parser.add_argument("--overlap", type=int, default=1, help="Overlap between clips in seconds")
    args = parser.parse_args()

    split_and_normalize(
        args.input,
        args.output,
        clip_length=args.clip_length * 1000,
        overlap=args.overlap * 1000
    )
