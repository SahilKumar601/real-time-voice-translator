from moviepy.editor import VideoFileClip
import tempfile

def extract_audio(video_path):
    """Extracts audio from video and saves it to a temporary file."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as audio_file:
        video = VideoFileClip(video_path)
        video.audio.write_audiofile(audio_file.name)
        return audio_file.name
