from fastapi import FastAPI, Request, HTTPException, Depends
from pydantic import BaseModel
import requests
from sqlalchemy.orm import Session
from database import SessionLocal, Base, engine
from models import ChatLog
from routes import auth, chat
from dotenv import load_dotenv
import os
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials

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

# Headers for OpenRouter API
HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
}

# Spotify API setup
spotify = Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET
))

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

# Fetch Spotify recommendations based on mood
def fetch_spotify_recommendations(mood: str):
    try:
        mood_queries = {
            "happy": "happy vibes",
            "sad": "calm and relaxing",
            "energetic": "workout beats",
            "relaxed": "chill acoustic"
        }
        query = mood_queries.get(mood.lower(), "mood booster")
        
        # Log the query for debugging
        print(f"Fetching Spotify playlists with query: {query}")
        
        results = spotify.search(q=query, type="playlist", limit=3)
        playlists = results.get("playlists", {}).get("items", [])
        
        if not playlists:
            # Fallback recommendation
            return [{"name": "Discover Weekly", "url": "https://spotify.com/discoverweekly"}]
        
        return [
            {"name": playlist["name"], "url": playlist["external_urls"]["spotify"]}
            for playlist in playlists
        ]
    except Exception as e:
        print(f"Error fetching Spotify recommendations: {e}")
        return []


# Generate exercise routines based on mood
def generate_exercise_routines(mood: str):
    routines = {
        "happy": "30-minute dance cardio or a fun Zumba session.",
        "sad": "A 20-minute yoga session or a calming walk.",
        "energetic": "A 45-minute HIIT workout or strength training.",
        "relaxed": "Gentle stretching or a slow-paced yoga flow."
    }
    return routines.get(mood.lower(), "A general full-body workout routine.")

@app.post("/chat/")
async def chat_endpoint(chat_request: ChatRequest, db: Session = Depends(get_db)):
    try:
        user_message = chat_request.message
        if not user_message:
            raise HTTPException(status_code=400, detail="Message is required")

        # Detect mood from the user's message
        mood_keywords = ["happy", "sad", "energetic", "relaxed"]
        detected_mood = next((mood for mood in mood_keywords if mood in user_message.lower()), None)

        # Fetch Spotify recommendations and exercise routines
        spotify_recommendations = fetch_spotify_recommendations(detected_mood) if detected_mood else []
        exercise_routine = generate_exercise_routines(detected_mood) if detected_mood else "A balanced workout routine."

        # Construct prompt for OpenRouter API
        prompt = (
            f"User's mood: {detected_mood or 'not specified'}\n"
            f"Spotify recommendations: {', '.join([p['name'] for p in spotify_recommendations])}\n"
            f"Suggested exercise routine: {exercise_routine}\n"
            f"User's message: {user_message}\n"
            f"Provide a personalized response considering the user's mood, Spotify playlists, and exercise routine."
        )
        
        payload = {
            "model": PRIMARY_MODEL,
            "messages": [
                {"role": "system", "content": "You are an AI assistant providing personalized recommendations based on mood."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 500,
        }

        # Send request to OpenRouter API
        response = requests.post(OPENROUTER_BASE_URL, json=payload, headers=HEADERS)

        # Check if the API call was successful
        if response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail=f"OpenRouter API error: {response.text}"
            )

        # Safely extract the chatbot's response
        response_data = response.json()
        if not response_data or "choices" not in response_data or not response_data["choices"]:
            raise HTTPException(
                status_code=500,
                detail="OpenRouter API returned an invalid response"
            )

        bot_response = response_data["choices"][0]["message"]["content"]

        # Save chat log to database
        chat_log = ChatLog(user_message=user_message, bot_response=bot_response)
        db.add(chat_log)
        db.commit()

        # Return the response
        return {
            "user_message": user_message,
            "bot_response": bot_response,
            "spotify_recommendations": spotify_recommendations,
            "exercise_routine": exercise_routine,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.get("/")
def read_root():
    return {"message": "Welcome to MoodSync+"}
