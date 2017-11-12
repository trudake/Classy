from flask import *
from werkzeug.utils import secure_filename
import os

from dao import *
from train import *
from youtube import *

app = Flask(__name__, static_url_path='/static')

app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'uploads')


@app.route('/classy')
def home():
    term=request.args.get('search', None)
    print term
    #if term is None:
    #    term="Beethoven"
    results = get_song_search_results(term)
    numsongs = get_num_songs()
    return render_template('classy.html', results=results, term=term, numsongs=numsongs)

@app.route('/classy/recommend')
def recommend():
    song_id = request.args.get('id', None)
    title = get_song_title(song_id)
    results = get_song_recommendations(song_id)
    numsongs = get_num_songs()
    return render_template('recommend.html', results=results, title=title, numsongs=numsongs)

@app.route('/classy/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        song_id = train_new_file(file)
        return redirect(url_for('recommend', id=song_id))

@app.route('/classy/youtube', methods=['GET'])
def youtube():
    url = request.args.get('url', None)
    get_youtube_song(url)
    song_id = 1865
    return redirect(url_for('recommend', id=song_id))

@app.route('/<name>')
def hello_name(name):
    upload_folder = os.path.join(app.root_path, 'uploads')
    return "Hello {} {}!".format(name, upload_folder)

def allowed_file(filename):
    return True

if __name__ == '__main__':
    app.run()
