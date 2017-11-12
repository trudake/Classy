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
        'postprocessors': [ {
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    fpath = os.path.join(mydir, os.listdir(mydir)[0])
    f = file(fpath)
    fn = os.path.basename(fpath)
    nf = file(os.path.join(output_dir, fn))
    os.rename(fpath, os.path.join(output_dir, fn))

    shutil.rmtree(mydir)

    return nf

