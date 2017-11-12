from __future__ import unicode_literals
import youtube_dl
import os
import datetime
import shutil

from flask import current_app

def get_youtube_song(url):
    output_dir = current_app.config['UPLOAD_FOLDER'] 

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_dir + '/%(title)sssss.mp3', 
        'progress_hooks': [on_finish],
        'postprocessors': [ {
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


def on_finish(progress_args):
    if progress_args['status'] != 'finished':
        print('nope')
        os.mkdir('nope')
        return
    print("got youtubes")
    os.mkdir('gotit')
    return 

