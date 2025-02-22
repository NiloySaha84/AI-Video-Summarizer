import speech_recognition as sr
import os
from flask import flash
from werkzeug.utils import secure_filename
import ffmpeg
from yt_dlp import YoutubeDL
from youtube_transcript_api import YouTubeTranscriptApi



UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def yt_audioExtractor(videoLink=None):
    link = videoLink
    with YoutubeDL() as video:
            info_dict = video.extract_info(link, download=False)
            video_id = info_dict.get("id")
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            transcript_text = "\n".join([entry["text"] for entry in transcript])
            return transcript_text
    

def extract_audio(video_path, audio_path):
    try:
        (
            ffmpeg
            .input(video_path)
            .output(audio_path, format='wav', acodec='pcm_s16le', ac=1, ar='16k')  # Set PCM format, mono, 16 kHz
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
        print(f"Audio extraction successful. Output file: {audio_path}")
        return audio_path
    except ffmpeg.Error as e:
        print("FFmpeg error:", e.stderr.decode('utf8'))
        return None

def preprocess(videoLink=None, file=None):
    if videoLink:
        return yt_audioExtractor(videoLink=videoLink)
    elif file:
        filename = secure_filename(file.filename)
        video_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(video_path)
    
        ext = os.path.splitext(video_path)[1].lower()
        if ext in ['.mov', '.m4v', '.mp4']:  # You can add more extensions as needed.
            converted_path = os.path.join(UPLOAD_FOLDER, "converted_video.mp4")
            new_video_path = convert_video(video_path, converted_path)
            if new_video_path:
                video_path = new_video_path
            else:
                flash("Video conversion failed", "error")
                return "Conversion Failed"
        
        audio_path = os.path.join(UPLOAD_FOLDER, "audio.wav")
        if extract_audio(video_path, audio_path):
            return transcribe_audio(audio_path)
        else:
            flash("Audio extraction failed", "error")
            return "Audio extraction failed"

        

def transcribe_audio(audio_path):
    r = sr.Recognizer()
    try:
        with sr.AudioFile(audio_path) as source:
            r.adjust_for_ambient_noise(source)
            raw_audio = r.record(source)
        transcribed_audio = r.recognize_google(raw_audio)
        return transcribed_audio
    except sr.UnknownValueError:
        return "Google Web Speech API could not understand the audio"
    except sr.RequestError as e:
        return f"Could not request results from Google Web Speech API; {e}"

def convert_video(input_path, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)  

    try:
        (
            ffmpeg
            .input(input_path)
            .output(output_path, format='mp4', vcodec='libx264', acodec='aac', pix_fmt='yuv420p')
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
        print(f"Conversion successful. Output file: {output_path}")

        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            return output_path
        else:
            print("Conversion failed: Output file is empty.")
            return None

    except ffmpeg.Error as e:
        print("FFmpeg error:", e.stderr.decode('utf8'))
        return None