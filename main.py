from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def index():
    return {"message": "Hello, FastAPI World!"}

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