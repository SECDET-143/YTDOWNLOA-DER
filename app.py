from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for
from typing import Any
import os
import threading
import yt_dlp

app = Flask(__name__)
DOWNLOAD_FOLDER = os.path.join(os.getcwd(), 'FUN PROJ', 'YT_DOWNLOAD', 'downloads')
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

download_status = {}

def download_video(url, format_choice, download_id):
    ydl_opts: dict[str, Any] = {}
    if format_choice == 'mp3':
        ydl_opts = {
            'format': 'bestaudio/best',
            'extractaudio': True,
            'audioformat': 'mp3',
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'noplaylist': False,
            'max_downloads': 100,
            'retries': 10,
            'fragment_retries': 10,
            'skip_unavailable_fragments': True,
            'merge_output_format': 'mp3',
            'no_warnings': True,
            'progress_hooks': [lambda d: progress_hook(d, download_id)],
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
            'postprocessor_args': ['-metadata', 'title=%(title)s'],
        }
    else:
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
            'noplaylist': False,
            'max_downloads': 100,
            'retries': 10,
            'fragment_retries': 10,
            'skip_unavailable_fragments': True,
            'progress_hooks': [lambda d: progress_hook(d, download_id)],
        }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        title = info_dict.get('title', 'Unknown Title')
        download_status[download_id]['title'] = title

def progress_hook(d, download_id):
    if d['status'] == 'downloading':
        total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
        if total_bytes:
            percent = d['downloaded_bytes'] / total_bytes * 100
            download_status[download_id]['status'] = 'downloading'
            download_status[download_id]['progress'] = percent
    elif d['status'] == 'finished':
        download_status[download_id]['status'] = 'finished'
        download_status[download_id]['progress'] = 100

@app.route('/')
def splash():
    # Redirect to splash screen, then after delay redirect to home
    return render_template('splash.html')

@app.route('/home')
def index():
    return render_template('index.html')

@app.route('/start_download', methods=['POST'])
def start_download():
    url = request.form.get('url')
    format_choice = request.form.get('format')
    download_id = str(len(download_status) + 1)
    download_status[download_id] = {'status': 'starting', 'progress': 0}

    thread = threading.Thread(target=download_video, args=(url, format_choice, download_id))
    thread.start()

    return jsonify({'download_id': download_id})

@app.route('/progress/<download_id>')
def progress(download_id):
    status = download_status.get(download_id, {'status': 'unknown', 'progress': 0})
    return jsonify(status)

@app.route('/downloads/<filename>')
def download_file(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
    