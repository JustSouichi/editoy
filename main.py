from pydub import AudioSegment
from pydub.silence import split_on_silence
from tqdm import tqdm
import os

def remove_silence_and_save_chunks_in_named_dir(audio_path, base_output_dir="videos/out"):
    # Load the audio file
    audio = AudioSegment.from_mp3(audio_path)

    # Split audio on silence
    chunks = split_on_silence(
        audio,
        # Use a silence threshold of -40 dBFS. Adjust this value based on your needs.
        min_silence_len=500,  # Minimum length of silence in ms to consider it as silence
        silence_thresh=-40    # Silence threshold in dBFS
    )

    # Get the base filename without the path and extension
    base_filename = os.path.basename(os.path.splitext(audio_path)[0])

    # Create a directory for this file within the base output directory
    chunks_dir = os.path.join(base_output_dir, base_filename)
    os.makedirs(chunks_dir, exist_ok=True)

    # Save each chunk as a separate file in the new directory
    for i, chunk in enumerate(tqdm(chunks, desc="Saving chunks")):
        chunk_filename = os.path.join(chunks_dir, f"{i+1}.mp3")
        chunk.export(chunk_filename, format="mp3")
        print(f"Chunk saved as {chunk_filename}")

# Example usage
audio_path = input("Insert url file audio: ")  # Prompt the user to enter the audio file path
remove_silence_and_save_chunks_in_named_dir(audio_path)