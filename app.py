from flask import Flask, render_template, request, jsonify, json
from pyshorteners import Shortener
import lyricsgenius as lg
import csv
import base64
from github import Github, Auth

app = Flask(__name__, template_folder='templates')

access_token = "LC2defTjjGgEM09GFXIhStvjR9d_YnZ3WArkc_yoW3aA1ewUgCbJGVk8k2BYuveo"
gh_access_token = "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"
auth = Auth.Token(gh_access_token)
g = Github(auth=auth)
repo = g.get_repo("sjcreator06/Praiseaway-Database")


# Fetching Github Repo Data
contents = repo.get_contents("")

gitContentPaths = []
gitArtists = []
gitSongs = []

while contents:
    file_content = contents.pop(0)
    if file_content.type == "dir":
        contents.extend(repo.get_contents(file_content.path))
    else:
        gitContentPaths.append(str(file_content))

i=0
for content in range(len(gitContentPaths)):
    trimmedContent = gitContentPaths[i].replace('ContentFile(path="Artists/',"")
    SlashIndex = trimmedContent.find("/")
    endIndex = trimmedContent.find('"',SlashIndex+1)
    gitartist = trimmedContent[:SlashIndex]
    gitsong = trimmedContent[SlashIndex+1:endIndex]
    gitArtists.append(gitartist)
    gitSongs.append(gitsong)
    i += 1

gitArtists = list(set(gitArtists))   
gitSongs = list(set(gitSongs))  


# Key Lists Initialization
secularArtistNames = []
christianArtistNames = []
artistSongforHTML = []
christianTemporaryArtistNames = []   
christianSongIndex = []
christianSongTitles = []

# Define routes
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/setchoice")
def setchoice():
    return render_template("setchoice.html")

# Recieves the Data when we click on song text with "-"
@app.route('/receive_data', methods=['POST'])
def receive_data():
    global song_and_artist
    data = request.get_json()
    
    print("Received data from JavaScript:", data)

    song_and_artist = data.get('songAndArtist')
    print(song_and_artist)
     
    if "amp;" in song_and_artist:
        song_and_artist = song_and_artist.replace("amp;","&")


    if song_and_artist:
        song_name, artist_name = map(str.strip, song_and_artist.split('-', 1))

        genius = lg.Genius(access_token)
        if artist_name:
            artist = genius.search_artist(artist_name, max_songs=1, sort="title")
            if artist:
                song = artist.song(song_name)
                print(song_name)
                if song_name not in gitSongs:
                    return jsonify({'lyrics': song.lyrics})
                
                else:
                    contents = repo.get_contents("Artists/" + artist_name+ "/" + song_name)
                    print("Artists/" + artist_name+ "/" + song_name)
                    lyrics = contents.decoded_content.decode()
                    g.close()
                    return jsonify({'lyrics': lyrics})

        else:
            song = genius.search_song(song_name)
            if song:
                return jsonify({'lyrics': song.lyrics})

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
        
        
        for name in artistNames:
            christianTemporaryArtistNames.append(name)
            if name in flattenedArtistsDatabase:
                index = christianTemporaryArtistNames.index(name)
                christianSongIndex.append(index)
                christianTemporaryArtistNames[index] = ""
                
    
        for artist in artistNames:
            if artist in flattenedArtistsDatabase:
                christianArtistNames.append(artist)
        
            elif artist not in flattenedArtistsDatabase:
                secularArtistNames.append(artist)
        
        for index in christianSongIndex:
            christianSongTitles.append(songTitles[index])
              
        i = 0   
        for name in christianArtistNames:    
            artistSongforHTML.append(christianSongTitles[i] + " - " + name)
            print(songTitles[i] + " - " + name)
            i += 1
            
        # Output Test Code
        print("Secular Artists: " + str(secularArtistNames))
        print("Christian Artists: " + str(christianArtistNames))
        print("Christian Songs: " + str(christianSongTitles))
    
        if "-" in songInput and ArtistName in christianArtistNames:
            genius = lg.Genius(access_token)
            artist = genius.search_artist(ArtistName, max_songs=1, sort="title")
            song = artist.song(songName)
            return render_template("lyrics.html", content=song.lyrics, Song=songName+ " - " + ArtistName)
        
        elif "-" in songInput and songName in gitSongs and songName not in christianSongTitles and ArtistName in gitArtists:
            contents = repo.get_contents("Artists/" + ArtistName+ "/" + songName)
            lyrics = contents.decoded_content.decode()
            g.close()
            return render_template("lyrics.html", content=lyrics, Song=songName+ " - " + ArtistName)
        
        elif "-" in songInput and songName not in gitSongs and songName not in christianSongTitles and ArtistName not in gitArtists:
            return render_template("404.html")
                
        elif "-" not in songInput and christianArtistNames != []: 
            return render_template("songsList.html", songList = artistSongforHTML, Song=songName)
        
        else:
            return render_template("404.html")
        
        
@app.route("/lyrics")
def lyrics():
    lyrics_data = request.args.get('lyrics')
    if lyrics_data:
        return render_template("lyrics.html", content=lyrics_data, Song=song_and_artist)
    else:
        print("Lyrics not available")
        return render_template("404.html")
        
    
        

@app.route("/loading")
def loading():
    return render_template("loading.html")


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
    #app.run(debug=True, host='192.168.0.28')  # host='192.168.0.28'
