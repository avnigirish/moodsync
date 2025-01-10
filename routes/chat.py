from pydantic import BaseModel
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def root():
    return {"message": "Chat module is working!"}

# Define the request model for chat
class ChatRequest(BaseModel):
    message: str

# Process the user's message to detect mood (could expand with NLP)
def detect_mood(user_message: str):
    mood_keywords = {
        "happy": ["happy", "excited", "joyful"],
        "sad": ["sad", "down", "depressed"],
        "energetic": ["energetic", "hyped", "active"],
        "relaxed": ["relaxed", "calm", "peaceful"]
    }

    for mood, keywords in mood_keywords.items():
        if any(keyword in user_message.lower() for keyword in keywords):
            return mood
    return None

# Generate chatbot response based on detected mood
def generate_response(user_message: str, mood: str):
    if mood == "happy":
        return "I'm so glad you're feeling happy! Want to dance to some tunes or try a fun workout?"
    elif mood == "sad":
        return "I'm here for you. How about some calming music or gentle yoga?"
    elif mood == "energetic":
        return "You're full of energy! How about a HIIT workout or a lively playlist?"
    elif mood == "relaxed":
        return "That's great. Maybe some chill acoustic music or a slow-paced yoga session?"
    else:
        return "I'm here to help with music, workouts, or anything you'd like to share!"

# Fetch Spotify recommendations or workout routines (placeholder for integration)
def fetch_recommendations(mood: str):
    # Example stub; replace with real Spotify and workout logic
    return {
        "spotify": [{"name": "Mood Booster", "url": "https://spotify.com/moodbooster"}],
        "routine": "A general full-body workout routine."
    }
