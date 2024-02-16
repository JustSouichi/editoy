from pydub import AudioSegment
from pydub.silence import split_on_silence
import os, random, shutil
from moviepy.editor import VideoFileClip

def find_video_with_minimum_length(min_length_sec, search_dir):
    suitable_videos = []
    for file in os.listdir(search_dir):
        if file.endswith(".mp4"):
            video_path = os.path.join(search_dir, file)
            try:
                with VideoFileClip(video_path) as video:
                    if video.duration >= min_length_sec:
                        suitable_videos.append(file)
            except Exception as e:
                print(f"Error processing video {video_path}: {e}")
    return random.choice(suitable_videos) if suitable_videos else None

def remove_silence_and_select_video_for_first_chunk(audio_path, audio_output_dir="videos/out", video_search_dir="videos/hooks"):
    audio = AudioSegment.from_mp3(audio_path)
    chunks = split_on_silence(audio, min_silence_len=500, silence_thresh=-40)

    if not chunks:
        print("No audio chunks found.")
        return

    base_filename = os.path.basename(os.path.splitext(audio_path)[0])
    chunks_dir = os.path.join(audio_output_dir, base_filename)
    os.makedirs(chunks_dir, exist_ok=True)

    # Process only the first chunk
    chunk = chunks[0]
    chunk_filename = os.path.join(chunks_dir, "1.mp3")
    chunk.export(chunk_filename, format="mp3")

    min_length_sec = len(chunk) / 1000.0  # Duration of the chunk in seconds
    video_name = find_video_with_minimum_length(min_length_sec, video_search_dir)
    if video_name:
        video_path = os.path.join(video_search_dir, video_name)
        # Copy the selected video into the output directory
        output_video_path = os.path.join(chunks_dir, video_name)
        shutil.copy(video_path, output_video_path)
        print(f"First chunk saved as {chunk_filename}, matched with video: {video_name}")
    else:
        print(f"First chunk saved as {chunk_filename}, no suitable video found.")

# Simulating the input
audio_path = input("insert url audio: ")  # Assuming 'test.mp3' is the file you want to process
remove_silence_and_select_video_for_first_chunk(audio_path)
