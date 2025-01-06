from fastapi import FastAPI
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from database import Base, engine, SessionLocal
from models import MoodLog

app = FastAPI()

#Configure Spotify API
spotify = Spotify(auth_manager=SpotifyClientCredentials(
    client_id = "f524fa5d6eec4cfcb4c05f8469a612c0",
    client_secret = "22cec1f60c3649ed984e5930b5869502"
))

Base.metadata.create_all(bind=engine)

@app.get("/")
def index():
    return {"message": "Welcome to MoodSync+"}

@app.get("/spotify-recommendations/")
def get_spotify_recommendations(mood: str):
    try:
        # Spotify API logic
        mood_queries = {
            "happy": "happy vibes",
            "sad": "calm and relaxing",
            "energetic": "workout beats",
            "relaxed": "chill acoustic"
        }

        query = mood_queries.get(mood.lower(), "mood booster")
        results = spotify.search(q=query, type="playlist", limit=3)

        playlists_data = results.get("playlists", {}).get("items", [])
        valid_playlists = [playlist for playlist in playlists_data if playlist]

        if not valid_playlists:
            return {"error": "No playlists found for the given mood"}

        # Extract the first playlist for logging
        selected_playlist = valid_playlists[0]
        playlist_name = selected_playlist.get("name", "Unknown Playlist")
        playlist_url = selected_playlist["external_urls"]["spotify"]

        # Exercise recommendations
        exercises = {
            "happy": "Jogging for 10 minutes",
            "sad": "Gentle yoga poses",
            "energetic": "HIIT workout",
            "relaxed": "Meditation"
        }
        exercise = exercises.get(mood.lower(), "Take a short walk")

        # Save to the database
        db = SessionLocal()
        mood_log = MoodLog(mood=mood, playlist=playlist_name, exercise=exercise)
        db.add(mood_log)
        db.commit()
        db.refresh(mood_log)

        # Return recommendations
        return {
            "mood": mood,
            "playlists": [{"name": playlist_name, "url": playlist_url}],
            "exercise": exercise
        }

    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}

        

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