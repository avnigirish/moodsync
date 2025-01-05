from fastapi import FastAPI
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials

app = FastAPI()

#Configure Spotify API
spotify = Spotify(auth_manager=SpotifyClientCredentials(
    client_id = "f524fa5d6eec4cfcb4c05f8469a612c0",
    client_secret = "22cec1f60c3649ed984e5930b5869502"
))

@app.get("/")
def index():
    return {"message": "Welcome to MoodSync+"}

@app.get("/spotify-recommendations/")
def get_spotify_recommendations(mood: str):
    try:
        #Map moods to Spotify seach queries
        mood_queries = {
            "happy": "happy vibes",
            "sad": "calm and relaxing",
            "energetic": "workout beats",
            "relaxed": "chill acoustic"
        }

        query = mood_queries.get(mood.lower(), "mood booster")
        results = spotify.search(q=query, type="playlist", limit=3)

        # Check if results and playlists exist
        playlists_data = results.get("playlists", {}).get("items", [])
        valid_playlists = [playlist for playlist in playlists_data if playlist]  # Filter out None

        if not valid_playlists:
            return {"error": "No playlists found for the given mood"}

        #Extract playlist data
        playlists = [
            {
                "name": playlist.get("name", "Unknown Playlist"),
                "description": playlist.get("description", "No description available"),
                "url": playlist["external_urls"]["spotify"],
                "image": playlist["images"][0]["url"] if playlist.get("images") else None,
                "owner": playlist["owner"]["display_name"]
            }
            for playlist in valid_playlists
        ]

        return {"mood": mood, "playlists": playlists}
    except Exception as e:
        return {"error": str(e)}
        

#Analyze mood
@app.post("/analyze_mood/")
async def analyze_mood(data: dict):
    mood = data.get("mood")
    #mock analysis
    if mood == "happy":
        recommendation = "Keep up the good vibes!"
    else:
        recommendation = "Here are some tips to improve your mood."
    return {"mood": mood, "recommendation": recommendation}