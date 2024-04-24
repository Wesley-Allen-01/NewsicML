function searchSongs() {
    const searchInput = document.getElementById('searchInput').value;
    fetch(`/search?query=${encodeURIComponent(searchInput)}`)
        .then(response => response.json())
        .then(data => {
            displaySearchResults(data);
        })
        .catch(error => console.error('Error:', error));
}

function displaySearchResults(results) {
    const resultsContainer = document.getElementById('searchResults');
    resultsContainer.innerHTML = ''; // Clear previous results

    if (results.length === 0) {
        resultsContainer.innerHTML = 'No results found';
        return;
    }

    results.forEach(song => {
        let songElement = document.createElement('div');
        let addButton = document.createElement('button');
        
        songElement.innerHTML = `${song.track_name} by ${song.artist_name}`;
        songElement.dataset.trackId = song.track_id;
        
        addButton.innerHTML = 'Add to playlist';
        addButton.onclick = () => addSongToPlaylist(song);

        songElement.appendChild(addButton);
        resultsContainer.appendChild(songElement);
    });
}


function addSongToPlaylist(song) {
    const playlist = document.getElementById('playlist');
    let songElement = document.createElement('div');
    songElement.id = song.track_id;
    songElement.innerHTML = `${song.track_name} by ${song.artist_name}`;
    playlist.appendChild(songElement);
}


function getRecommendations() {
    console.log('heyhey');
    let playlistSongs = Array.from(document.getElementById('playlist').children);
    let trackIds = playlistSongs.map(song => song.id);
    const recommendationsContainer = document.getElementById('recommendations');
    recommendationsContainer.innerHTML = 'Loading...';
    fetch('/recommend', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ playlist: trackIds})
    })
    .then(response => response.json())
    .then(recommendations => {
        displayRecommendations(recommendations);
    })
    .catch(error => console.error('Error:', error));
}

function displayRecommendations(recommendations) {
    const recommendationsContainer = document.getElementById('recommendations');
    recommendationsContainer.innerHTML = ''; // Clear previous recommendations

    recommendations.forEach(song => {
        let songElement = document.createElement('div');
        songElement.innerHTML = `${song.track_name} by ${song.artist_name}`;
        recommendationsContainer.appendChild(songElement);
    });
}