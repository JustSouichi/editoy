from pydub import AudioSegment
from pydub.silence import split_on_silence
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips
import os, random, datetime

def find_video_with_minimum_length(min_length_sec, search_dir, used_videos):
    suitable_videos = []
    for file in os.listdir(search_dir):
        if file.endswith(".mp4") and file not in used_videos:
            video_path = os.path.join(search_dir, file)
            try:
                with VideoFileClip(video_path) as video:
                    if video.duration >= min_length_sec:
                        suitable_videos.append(file)
            except Exception as e:
                print(f"Error processing video {video_path}: {e}")
    if suitable_videos:
        selected_video = random.choice(suitable_videos)
        used_videos.add(selected_video)  # Mark this video as used
        return selected_video
    else:
        return None

def trim_resize_and_replace_audio(video_path, audio_path, output_path, audio_length, target_resolution=(1080, 1920)):
    video_clip = VideoFileClip(video_path).subclip(0, audio_length).resize(newsize=target_resolution)
    audio_clip = AudioFileClip(audio_path).subclip(0, audio_length)
    final_clip = video_clip.set_audio(audio_clip)
    final_clip.write_videofile(output_path, codec='libx264', audio_codec='aac', temp_audiofile='temp-audio.m4a', remove_temp=True)
    video_clip.close()
    audio_clip.close()
    final_clip.close()

def process_audio_and_video(audio_path, audio_output_dir="videos/out", initial_video_search_dir="videos/hooks", subsequent_video_search_dir="videos/viral", target_resolution=(1080, 1920)):
    audio = AudioSegment.from_mp3(audio_path)
    chunks = split_on_silence(audio, min_silence_len=500, silence_thresh=-40)

    if not chunks:
        print("No audio chunks found.")
        return

    base_filename = os.path.basename(os.path.splitext(audio_path)[0])
    chunks_dir = os.path.join(audio_output_dir, base_filename)
    os.makedirs(chunks_dir, exist_ok=True)

    used_videos = set()
    video_clip_paths = []

    for i, chunk in enumerate(chunks):
        chunk_filename = os.path.join(chunks_dir, f"{i+1}.mp3")
        chunk.export(chunk_filename, format="mp3")
        audio_length = len(chunk) / 1000.0

        search_dir = initial_video_search_dir if i == 0 else subsequent_video_search_dir
        video_name = find_video_with_minimum_length(audio_length, search_dir, used_videos)

        if video_name:
            video_path = os.path.join(search_dir, video_name)
            output_video_path = os.path.join(chunks_dir, f"video_{i+1}.mp4")
            trim_resize_and_replace_audio(video_path, chunk_filename, output_video_path, audio_length, target_resolution)
            video_clip_paths.append(output_video_path)
            print(f"Chunk {i+1} saved as {chunk_filename}, paired with resized and audio-replaced video: {video_name}.")
        else:
            print(f"Chunk {i+1} saved as {chunk_filename}, no suitable video found in {search_dir} not already used.")

    # Concatenate all video clips into a final video
    final_clips = [VideoFileClip(path) for path in video_clip_paths]
    final_video = concatenate_videoclips(final_clips, method="compose")
    
    # Format the final video name with the current day and hour
    current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    final_video_name = f"final_video_{base_filename}_{current_time}.mp4"
    final_video_path = os.path.join(chunks_dir, final_video_name)
    
    final_video.write_videofile(final_video_path, codec="libx264", audio_codec='aac')
    final_video.close()
    print(f"Final video saved as {final_video_path}")

# Example usage
if __name__ == "__main__":
    audio_path = input("Insert file path for audio: ")  # Prompt for the audio file path
    audio_path = "audio/" + audio_path
    process_audio_and_video(audio_path)
