from flask import Blueprint, render_template, request, flash
from .preprocessing import preprocess, transcribe_audio
from .summarize import summarize

views = Blueprint('views', __name__)
@views.route('/', methods=['GET', 'POST'])
def home():
    transcription = ""
    if request.method == 'POST':
        videoLink = request.form.get('videoLink')
        file = request.files.get('file')
        if bool(videoLink) ^ bool(file): 
            if videoLink:
                if videoLink.startswith(('http://', 'https://')):
                    flash("Video link provided successfully!", "success")
                    transcription = summarize(preprocess(videoLink=videoLink))
                else:
                    flash("Invalid video link format.", "error")
            elif file:
                if file.filename:
                    flash("File uploaded successfully!", "success")
                    transcription = summarize(preprocess(file=file))
                else:
                    flash("No file selected.", "error")
        else:
            flash("Please provide either a video link or upload a file, not both.", "error")
    return render_template("home.html", transcription=transcription)