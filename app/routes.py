from app import app
from flask import render_template, request, send_from_directory
from .route_handlers import *

import os
from werkzeug.utils import secure_filename
import deezer


def allowed_file(filename):
    if not "." in filename:
        return False
    
    ext = filename.rsplit(".", 1)[1]

    if ext.upper() in app.config["ALLOWED_EXTENSIONS"]:
        return True
    else:
        return False


@app.route('/song/download')
def download_song():
    # Doesn't need a check of existing.
    return send_from_directory(directory=app.config['UPLOAD_FOLDER'], filename=request.args.get('song'))


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/akinator')
def akinator():
    return render_template('akinator.html')

@app.route('/game')
def game():
    return render_template('game.html')


@app.route('/song/recognize_by_text', methods=['POST'])
def recognize_song_by_text():
    data = request.form["lyric"]
    if data is not None:
        dry_data = recognize_song_by_text_handler(data)
        if dry_data[0] == 'Not found':
            return render_template('akinator.html', is_send=True, is_found=False)
        
        track = dry_data[0]["result"][0]["full_title"].replace("\xa0", " ")
        result = {"track": track}
        client = deezer.Client()
        advanced_client = client.advanced_search(result)
        if advanced_client:
            url_song = advanced_client[0].asdict()["preview"]
            title = advanced_client[0].asdict()["title"]
            artist = advanced_client[0].asdict()["artist"]["name"]
            link = advanced_client[0].asdict()["link"]
            return render_template('akinator.html', is_send=True, is_found=True, result=url_song, title=title, author=artist, url=link)
        return render_template('akinator.html', is_send=True, is_found=False)
    return jsonify(msg='Invalid data', result=False), 400


@app.route('/song/recognize_by_voice', methods=['GET', 'POST'])
def recognize_song_by_voice():
    # if request.files.get("voice"):
    # print('request', request.files)
    voice = request.files["voice"]
    if voice.filename == "":
        print("File must have a filename")
        return jsonify(msg="File must have a filename", result=False), 200

    if not allowed_file(voice.filename):
        return jsonify(msg="Invalid file format", result=False), 200
    else:
        filename = secure_filename(voice.filename)
        voice.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        result = recognize_song_by_voice_handler(filename)
        os.remove(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        return result
    # return jsonify(msg='Invalid request'), 400


@app.route('/song/recognize_by_track', methods=['POST'])
def recognize_song_by_track():
    if request.files.get("track"):
        track = request.files["track"]
        print(track)

        if track.filename == "":
            print("Image must have a filename")
            return jsonify(msg="Image must have a filename", result=False), 200

        if not allowed_file(track.filename):
            return jsonify(msg="Invalid file format", result=False), 200
        else:
            filename = secure_filename(track.filename)
            track.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            result = recognize_song_by_sound_handler(filename)
            print('recognize by track api:', result)
            os.remove(os.path.join(app.config["UPLOAD_FOLDER"], filename))

            if result[0]["status"] == "error":
                return render_template('akinator.html', is_send=True, is_found=False)
            else:
                title = result[0]["result"]["title"]
                artist = result[0]["result"]["artist"]
                link = result[0]["result"]["deezer"]["link"]
                url_song = result[0]["result"]["deezer"]["preview"]
                return render_template('akinator.html', is_send=True, is_found=True, result=url_song, title=title, autor=artist, url=link)
            
            return result
    return jsonify(msg='Invalid request'), 400
