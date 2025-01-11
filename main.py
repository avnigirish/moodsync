from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import requests
from sqlalchemy.orm import Session
from database import SessionLocal, Base, engine
from models import ChatLog, MoodLog
from routes import auth, chat
from dotenv import load_dotenv
import os
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from schemas import MoodLogCreate
from datetime import datetime
from transformers import pipeline

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Create database tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(chat.router, prefix="/chat", tags=["Chatbot"])

# Constants
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
PRIMARY_MODEL = "meta-llama/llama-3.2-1b-instruct:free"

HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
}

# Spotify API setup
spotify = Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET
))

# Hugging Face emotion analysis model
emotion_analyzer = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Request model for the /chat/ endpoint
class ChatRequest(BaseModel):
    message: str

# Analyzes the user's mood based on the input message using a Hugging Face model
def analyze_user_mood(user_message: str):
    try:
        results = emotion_analyzer(user_message, top_k=None)
        sorted_results = sorted(results, key=lambda x: x["score"], reverse=True)
        mood_array = [result["label"].lower() for result in sorted_results]
        return mood_array
    except Exception as e:
        print(f"Error analyzing user mood: {e}")
        return []

# Fetch Spotify recommendations based on the mood array
def fetch_spotify_recommendations(moods):
    try:
        recommendations = []
        for mood in moods:
            query = f"{mood} playlist"
            results = spotify.search(q=query, type="playlist", limit=3)
            
            # Log the search results for debugging
            print(f"Spotify search results for mood '{mood}': {results}")

            # Check for playlists and filter out None values
            if results and "playlists" in results:
                playlists = [playlist for playlist in results["playlists"]["items"] if playlist]
                
                # Proceed only if we have valid playlists
                if playlists:
                    playlist = playlists[0]
                    recommendations.append({
                        "mood": mood,
                        "name": playlist["name"],
                        "url": playlist["external_urls"]["spotify"]
                    })
                else:
                    recommendations.append({
                        "mood": mood,
                        "name": "Mood Booster Playlist",  # Default playlist
                        "url": "https://spotify.com"  # Placeholder link
                    })
            else:
                recommendations.append({
                    "mood": mood,
                    "name": "Mood Booster Playlist",  # Default playlist
                    "url": "https://spotify.com"  # Placeholder link
                })

        return recommendations
    except Exception as e:
        print(f"Error fetching Spotify recommendations: {e}")
        return []


# Generate exercise routines
def generate_exercise_routines(mood):
    routines = {
        "happy": "30-minute dance cardio or a fun Zumba session.",
        "sad": "A 20-minute yoga session or a calming walk.",
        "energetic": "A 45-minute HIIT workout or strength training.",
        "relaxed": "Gentle stretching or a slow-paced yoga flow."
    }
    return routines.get(mood.lower(), "A balanced workout routine.")

@app.post("/chat/")
async def chat_endpoint(chat_request: ChatRequest, db: Session = Depends(get_db)):
    try:
        user_id = 1  # You should retrieve the actual logged-in user ID here.
        user_message = chat_request.message
        if not user_message:
            raise HTTPException(status_code=400, detail="Message is required")

        mood_array = analyze_user_mood(user_message)

        spotify_recommendations = fetch_spotify_recommendations(mood_array)
        exercise_routines = [generate_exercise_routines(mood) for mood in mood_array]

        prompt = (
            f"User's mood(s): {', '.join(mood_array) or 'not specified'}\n"
            f"Spotify recommendations: {', '.join([p['name'] for p in spotify_recommendations])}\n"
            f"Suggested exercise routines: {', '.join(exercise_routines)}\n"
            f"User's message: {user_message}\n"
            f"Provide a personalized response."
        )

        payload = {
            "model": PRIMARY_MODEL,
            "messages": [
                {"role": "system", "content": "You are an AI assistant providing personalized recommendations."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 500,
        }

        response = requests.post(OPENROUTER_BASE_URL, json=payload, headers=HEADERS)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail=f"OpenRouter API error: {response.text}")

        response_data = response.json()
        bot_response = response_data["choices"][0]["message"]["content"]

        chat_log = ChatLog(user_message=user_message, bot_response=bot_response)
        db.add(chat_log)

        mood_log = MoodLog(user_id=user_id, mood=','.join(mood_array), timestamp=datetime.utcnow())
        db.add(mood_log)

        db.commit()

        return {
            "user_id": user_id, 
            "user_message": user_message,
            "mood_array": mood_array,
            "bot_response": bot_response,
            "spotify_recommendations": spotify_recommendations,
            "exercise_routines": exercise_routines,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
