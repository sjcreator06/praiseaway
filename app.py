from flask import Flask, render_template, request, jsonify
from pyshorteners import Shortener
import lyricsgenius as lg
import csv
import base64

access_token = "LC2defTjjGgEM09GFXIhStvjR9d_YnZ3WArkc_yoW3aA1ewUgCbJGVk8k2BYuveo"
app = Flask(__name__, template_folder='templates')

# Define routes
@app.route("/")
def index():
    return render_template("index.html")

# Recieves the Data when we click on song text with "-"
@app.route('/receive_data', methods=['POST'])
def receive_data():
    global song_and_artist
    data = request.get_json()
    
    
    print("Received data from JavaScript:", data)

    song_and_artist = data.get('songAndArtist')
    
    
    if song_and_artist:
        song_name, artist_name = map(str.strip, song_and_artist.split('-', 1))

        genius = lg.Genius("LC2defTjjGgEM09GFXIhStvjR9d_YnZ3WArkc_yoW3aA1ewUgCbJGVk8k2BYuveo")
        if artist_name:
            artist = genius.search_artist(artist_name, max_songs=1, sort="title")
            if artist:
                song = artist.song(song_name)
                if song:
                    encoded_lyrics = base64.b64encode(song.lyrics.encode()).decode()
                    return jsonify({'lyrics': encoded_lyrics})

        else:
            song = genius.search_song(song_name)
            if song:
                encoded_lyrics = base64.b64encode(song.lyrics.encode()).decode()
                return jsonify({'lyrics': encoded_lyrics})

    return jsonify({'error': 'Failed to retrieve lyrics'})

# Search Function using Artist and Song Name
@app.route("/lyrics", methods=["POST"])
def process_form():
    songInput = request.form.get("searchInput")
    
    
    if "-" in songInput:
        songartistSeparated = songInput.split(" - ")
        songName = songartistSeparated[0].title()
        ArtistName = songartistSeparated[1].title()

    else:
        songName = songInput
    
    with open('Artists.csv') as csvfile:
        genius = lg.Genius(access_token)
        
        # Artist Database
        artistsCSV = csv.reader(csvfile, delimiter='\n')
        artistsDatabase = []
        
        for row in artistsCSV:
            artistsDatabase.append(row)
        
        flattenedArtistsDatabase = []

        for sublist in artistsDatabase:
            for artist in sublist:
                flattenedArtistsDatabase.append(artist)
        
        # Initializing song name and artist as key value pairs
        data = []
        artistNames = []
        songTitles = []
        
        
        songDict = genius.search_songs(songName)
        songResults = songDict["hits"]
        
        for hit in songResults:
            song_info = hit["result"]
            artistName = song_info.get("primary_artist").get("name")
            songTitle = song_info.get("title")
            data.append({artistName + " , " + songTitle})   
            artistNames.append(artistName)
            songTitles.append(songTitle)
        
        
        # New Search Method (Song Name)
        secularArtistNames = []
        christianArtistNames = []
        artistSongforHTML = []

        for artist in artistNames:
            if artist in flattenedArtistsDatabase:
                christianArtistNames.append(artist)
            elif artist not in flattenedArtistsDatabase:
                secularArtistNames.append(artist)
       
                
        for name in christianArtistNames:
            artistSongforHTML.append(songInput + " - " + name)
            print(songInput + " - " + name)

        # Output Test Code
        print("Secular: " + str(secularArtistNames))
        print("Christian: " + str(christianArtistNames))


        if "-" in songInput and ArtistName in christianArtistNames:
            genius = lg.Genius(access_token)
            artist = genius.search_artist(ArtistName, max_songs=1, sort="title")
            song = artist.song(songName)
            
            encoded_lyrics = base64.b64encode(song.lyrics.encode()).decode()
            decoded_lyrics = base64.b64decode(encoded_lyrics.encode()).decode()
            
            return render_template("lyrics.html", content=decoded_lyrics, Song=songName+ " - " + ArtistName)
        
        elif "-" not in songInput and christianArtistNames != []:
            return render_template("songsList.html", songList = artistSongforHTML, Song=songName)
        else:
            return render_template("404.html")
        
        
@app.route("/lyrics")
def lyrics():
    lyrics_data = request.args.get('lyrics')
    decoded_lyrics = base64.b64decode(lyrics_data).decode() if lyrics_data else "Lyrics not available"
    return render_template("lyrics.html", content=decoded_lyrics, Song=song_and_artist)

@app.route("/loading")
def loading():
    return render_template("loading.html")

"""# Define routes
@app.route("/")
def index():
    return render_template("index.html")"""


# Shortens Setlist URL
@app.route('/URL_Data', methods=['POST'])
def receive_datas():
    global setlistURL
    data = request.get_json()
    setlistURL = data.get('setlistURL')
    url_shortner = Shortener()
    shortURL = format(url_shortner.tinyurl.short(setlistURL))
    print(shortURL)
    return jsonify({'shortenedURL': shortURL})
    




#if __name__ == "__main__":
    #app.run(debug=True, port=8002)
