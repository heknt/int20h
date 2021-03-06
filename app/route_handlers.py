import requests
from config import API_REC_TOKEN
from flask import jsonify


def recognize_song_by_text_handler(text):
    if text is not None:
        data = {
                'q': text,
                'api_token': API_REC_TOKEN
        }

        result = requests.post("https://api.audd.io/findLyrics/", data=data).json()
        if result['result']:
            return result, 200
        else:
            return "Not found", 200
    else:
        return jsonify(msg='Invalid data', result=False), 400


def recognize_song_by_voice_handler(filename):
    if filename is not None:
        data = {
            'url': f'https://int20h.herokuapp.com/song/download?song={filename}',
            'api_token': API_REC_TOKEN
        }
        return requests.post("https://api.audd.io/recognizeWithOffset/", data=data).json(), 200
    else:
        return jsonify(msg='Invalid data', result=False), 400


def recognize_song_by_sound_handler(filename):
    if filename is not None:
        data = {
                'url': f'https://int20h.herokuapp.com/song/download?song={filename}',
                'return': 'timecode,apple_music,deezer,spotify',
                'api_token': API_REC_TOKEN
        }
        return requests.post('https://api.audd.io/', data=data).json(), 200
    else:
        return jsonify(msg='Invalid data', result=False), 400
