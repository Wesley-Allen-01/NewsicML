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
    resultsContainer.innerHTML = ''; 

    if (results.length === 0) {
        resultsContainer.innerHTML = 'No results found';
        return;
    }


    let table = document.createElement('table');
    table.classList.add('table'); 


    let headerRow = document.createElement('tr');
    let titleHeader = document.createElement('th');
    let artistHeader = document.createElement('th');
    let addToPlaylistHeader = document.createElement('th');

    titleHeader.textContent = 'Title';
    artistHeader.textContent = 'Artist';
    addToPlaylistHeader.textContent = 'Add to Playlist';

    headerRow.appendChild(titleHeader);
    headerRow.appendChild(artistHeader);
    headerRow.appendChild(addToPlaylistHeader);
    table.appendChild(headerRow);


    let tbody = document.createElement('tbody');


    results.forEach(song => {
        let row = document.createElement('tr');
        row.id = song.track_id + 'search_row';
        
        let titleCell = document.createElement('td');
        titleCell.textContent = song.track_name;

        let artistCell = document.createElement('td');
        artistCell.textContent = song.artist_name;
        
        const isInPlaylist = document.getElementById(song.track_id) !== null;

        let addToPlaylistCell = document.createElement('td');
        let addButton = document.createElement('button');
        addButton.textContent = 'Add to playlist';
        addButton.classList.add('btn', 'btn-primary'); 
        addButton.onclick = () => addSongToPlaylist(song);

        addButton.disabled = isInPlaylist;

        addToPlaylistCell.appendChild(addButton);

        row.appendChild(titleCell);
        row.appendChild(artistCell);
        row.appendChild(addToPlaylistCell);

        tbody.appendChild(row);
    });

    table.appendChild(tbody);
    resultsContainer.appendChild(table);
}




function addSongToPlaylist(song) {
    const playlist = document.getElementById('playlistBody');

    if (document.getElementById(song.track_id)) {
        alert('This song is already in the playlist!');
        return; 
    }

    let row = document.createElement('tr');
    row.id = song.track_id;

    let titleCell = document.createElement('td');
    titleCell.textContent = song.track_name;

    let artistCell = document.createElement('td');
    artistCell.textContent = song.artist_name;

    let removeCell = document.createElement('td');
    let removeButton = document.createElement('button');
    removeButton.textContent = 'Remove';
    removeButton.classList.add('btn', 'btn-danger');
    removeButton.onclick = () => removeSongFromPlaylist(song);
    removeCell.appendChild(removeButton);

    row.appendChild(titleCell);
    row.appendChild(artistCell);
    row.appendChild(removeCell);


    playlist.appendChild(row);



    let searchResults = document.getElementById('searchResults');
    let songRow = searchResults.querySelector(`tr[id="${song.track_id + 'search_row'}"]`);
    songRow.querySelector('button').disabled = true;
    songRow.querySelector('button').textContent = 'Added';
}

function removeSongFromPlaylist(song) {
    let playlist = document.getElementById('playlistBody');
    let songRow = playlist.querySelector(`tr[id="${song.track_id + 'playlist_row'}"]`);
    playlist.removeChild(songRow);

    let searchResults = document.getElementById('searchResults');
    let songRowSearch = searchResults.querySelector(`tr[id="${song.track_id + 'search_row'}"]`);
    songRowSearch.querySelector('button').disabled = false;
    songRowSearch.querySelector('button').textContent = 'Add to playlist';
}


function getRecommendations() {
    console.log('heyhey');
    let playlistSongs = Array.from(document.getElementById('playlistBody').children);
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
    recommendationsContainer.innerHTML = ''; 

    recommendations.forEach(song => {
        let songElement = document.createElement('div');
        songElement.innerHTML = `${song.track_name} by ${song.artist_name}`;
        recommendationsContainer.appendChild(songElement);
    });
}