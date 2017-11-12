from sklearn.neighbors import NearestNeighbors
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

import os
import librosa
import warnings
from scipy import stats
import sys
import pandas as pd

import numpy as np
import MySQLdb
mysql_cn= MySQLdb.connect(host='localhost',
               user='root', passwd='#Phard',
               db='classy')

df_music = pd.read_sql('select * from features;', con=mysql_cn)
print 'loaded dataframe from MySQL.records:', len(df_music)
mysql_cn.close()

df_music = df_music.set_index('id')
filter_col = [col for col in df_music if (col.startswith('spectral')|
				col.startswith('chroma_cqt')|
				col.startswith('rmse')|
				col.startswith('mfcc'))]
df_music=df_music[filter_col]

def columns():
    feature_sizes = dict(chroma_cqt=12, mfcc=20, rmse=1,
                         spectral_centroid=1, spectral_bandwidth=1,
                         spectral_contrast=7, spectral_rolloff=1)
    moments = ('mean', 'std', 'skew', 'kurtosis', 'median', 'min', 'max')

    columns = []
    for name, size in feature_sizes.items():
        for moment in moments:
            it = ((name, moment, '{:02d}'.format(i+1)) for i in range(size))
            columns.extend(it)

    names = ('feature', 'statistics', 'number')
    columns = pd.MultiIndex.from_tuples(columns, names=names)

    # More efficient to slice if indexes are sorted.
    return columns.sort_values()
def audio_to_features(filepath):
    features = pd.Series(index=columns(), dtype=np.float32)
    # Catch warnings as exceptions (audioread leaks file descriptors).
    warnings.filterwarnings('error', module='librosa')
    def feature_stats(name, values):
        features[name, 'mean'] = np.mean(values, axis=1)
        features[name, 'std'] = np.std(values, axis=1)
        features[name, 'skew'] = stats.skew(values, axis=1)
        features[name, 'kurtosis'] = stats.kurtosis(values, axis=1)
        features[name, 'median'] = np.median(values, axis=1)
        features[name, 'min'] = np.min(values, axis=1)
        features[name, 'max'] = np.max(values, axis=1)


    path = os.getenv("PATH")
    if "/home/X88/miniconda2/bin" not in path:
        path += os.pathsep + "/home/X88/miniconda2/bin"
        os.environ["PATH"] = path

    x, sr = librosa.load(filepath, sr=None, mono=True)  # kaiser_fast
    cqt = np.abs(librosa.cqt(x, sr=sr, hop_length=512, bins_per_octave=12,
                                         n_bins=7*12, tuning=None))
    assert cqt.shape[0] == 7 * 12
    assert np.ceil(len(x)/512) <= cqt.shape[1] <= np.ceil(len(x)/512)+1

    f = librosa.feature.chroma_cqt(C=cqt, n_chroma=12, n_octaves=7)
    feature_stats('chroma_cqt', f)
    del cqt

    stft = np.abs(librosa.stft(x, n_fft=2048, hop_length=512))
    assert stft.shape[0] == 1 + 2048 // 2
    assert np.ceil(len(x)/512) <= stft.shape[1] <= np.ceil(len(x)/512)+1
    del x

    f = librosa.feature.rmse(S=stft)
    feature_stats('rmse', f)

    f = librosa.feature.spectral_centroid(S=stft)
    feature_stats('spectral_centroid', f)
    f = librosa.feature.spectral_bandwidth(S=stft)
    feature_stats('spectral_bandwidth', f)
    f = librosa.feature.spectral_contrast(S=stft, n_bands=6)
    feature_stats('spectral_contrast', f)
    f = librosa.feature.spectral_rolloff(S=stft)
    feature_stats('spectral_rolloff', f)

    mel = librosa.feature.melspectrogram(sr=sr, S=stft**2)
    del stft
    f = librosa.feature.mfcc(S=librosa.power_to_db(mel), n_mfcc=20)
    feature_stats('mfcc', f)

    features.index = ['_'.join(index_level).strip() for index_level in features.index.values]
    features = features.rename('f')
    return features

def train_model(df):
    index_safe = df.index.values
    df=df.dropna(axis=1, how='all')
    scaler = StandardScaler()
    df_std = scaler.fit_transform(df)

    pca = PCA(n_components=20)
    df_pca = pca.fit_transform(df_std)

    neigh = NearestNeighbors(n_neighbors=6, algorithm='auto')
    neigh.fit(df_pca)
    df_pca = pd.DataFrame(df_pca, index = index_safe)
    return (neigh, df_pca)

def return_similar_audio(df, argv):
    features = audio_to_features(argv)
    df = df.append(features)
    model = train_model(df)[0]
    df_pca = train_model(df)[1]
    query = df_pca.loc['f'].as_matrix()
    query = query.reshape(1, -1)
    neighbors = model.kneighbors(query, return_distance=False)
    index_neighbors = []
    for neighbor in neighbors:
        index_neighbors.append(df_pca.index.values[neighbor])
    return index_neighbors

def insert_to_db(argv):
    mysql_cn= MySQLdb.connect(host='localhost', 
               user='root', passwd='#Phard',
               db='classy')
    features = audio_to_features(argv)
    string_feat = features.to_string(index=False, header=False)
    string_feat = ",".join([str(item) for item in string_feat.split('\n')])
    command = 'insert into features values(UUID(), ' + string_feat + ");"
    pd.read_sql(command, con=mysql_cn)
    print "datapoint added to DB"
    mysql_cn.close()

def main(argv):
    insert_to_db(argv)
    return return_similar_audio(df_music, argv)
if __name__ == '__main__':
    main(sys.argv[1])
