from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity


app = Flask(__name__)

df = pd.read_csv('data/spotify_data.csv', index_col=0)
df['track_name'] = df['track_name'].str.lower()
df['artist_name'] = df['artist_name'].str.lower()

@app.route("/")
def index():
    return render_template("index.html")


@app.route('/search')
def search():
    query = request.args.get('query')
    if not query:
        return jsonify([])
    query = query.lower()
    title_results = df[(df['track_name'].str.contains(query, na=False))]
    artist_results = df[(df['artist_name'].str.contains(query, na=False))]
    # print(query)
    # print(artist_results)
    results = pd.concat([title_results, artist_results]).drop_duplicates()
    results = results.sort_values('popularity', ascending=False)
    if results.empty:
        return jsonify([])
    if len(results) > 10:
        results = results.head(10)
        return jsonify(results.to_dict(orient='records'))
    else:
        return jsonify(results.to_dict(orient='records'))


@app.route('/recommend', methods=['POST'])
def recommend():
    playlist = request.json['playlist']
    print("\n\n\n", playlist, "\n\n\n")
    filtered_songs = df[df['track_id'].isin(playlist)]
    recommendations = get_recommendations(filtered_songs)
    return jsonify(recommendations.to_dict(orient='records'))


def get_recommendations(playlist):
    print("\n\n\n\n")
    print(playlist)
    print("\n\n\n\n")
    df = pd.read_csv('data/spotify_data.csv', index_col=0)
    songs_already_in_playlist = df[df['track_id'].isin(playlist['track_id'])]
    df = df.drop(songs_already_in_playlist.index)
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(df[numeric_cols])
    kmeans = KMeans(n_clusters=10, random_state=42)
    clusters = kmeans.fit_predict(scaled_data)
    df['cluster'] = clusters
    
    playlist_vector = create_playlist_vector(playlist, scaler, kmeans)
    
    songs_in_cluster = df[df['cluster'] == playlist_vector[-1]]
    songs_in_cluster = songs_in_cluster.drop('cluster', axis=1)
    numerical_songs = songs_in_cluster.select_dtypes(include=[np.number])
    scaled_songs = scaler.transform(numerical_songs)
    
    similarities = cosine_similarity([playlist_vector[:-1]], scaled_songs)
    
    top_indices = similarities.argsort()[0][-5:][::-1]
    top_songs = songs_in_cluster.iloc[top_indices]
    
    return top_songs
    
    # return df.sample(5)


def create_playlist_vector(playlist, scaler, kmeans):
    numerical_playlist = playlist.select_dtypes(include=[np.number])
    scaled_playlist = scaler.transform(numerical_playlist)
    playlist_vector = scaled_playlist.mean(axis=0)
    playlist_cluster = kmeans.predict([playlist_vector])[0]
    playlist_vector = np.append(playlist_vector, playlist_cluster)
    return playlist_vector

if __name__ == "__main__":
    
    app.run(debug=True)

