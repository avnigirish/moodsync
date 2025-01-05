from fastapi import FastAPI
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials

app = FastAPI()

#Configure Spotify API
spotify = Spotify(auth_manager=SpotifyClientCredentials(
    client_id = "f524fa5d6eec4cfcb4c05f8469a612c0",
    cleint_secret = "22cec1f60c3649ed984e5930b5869502"
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

        query = mood_queries(mood.lower(), "mood booster")
        results = spotify.search(q=query, type="playlist", limit=3)

        #Extract playlist data
        playlists = [
            {
                "name": playlist["name"],
                "description": playlist["description"],
                "url": playlist["external_urls"]["spotify"]
            }
            for playlist in results["playlists"]["items"]
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