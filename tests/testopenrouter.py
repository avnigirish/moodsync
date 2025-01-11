from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from os import getenv
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

# Constants
API_KEY = getenv("OPENROUTER_API_KEY")
BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

# Initialize FastAPI app
app = FastAPI()

# Request payload model
class OpenRouterRequest(BaseModel):
    prompt: str


@app.post("/test-openrouter/")
async def test_openrouter(request: OpenRouterRequest):
    if not API_KEY:
        raise HTTPException(status_code=500, detail="API Key is not configured. Check your environment variables.")

    # Prepare payload
    payload = {
        "model": "meta-llama/llama-3.2-1b-instruct:free",
        "messages": [
            {"role": "user", "content": request.prompt},
        ],
    }

    # Headers
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    # POST request to OpenRouter API
    try:
        response = requests.post(BASE_URL, headers=headers, json=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()

        # Extract response content
        response_content = data.get("choices", [{}])[0].get("message", {}).get("content", "No content received.")
        return {
            "input_prompt": request.prompt,
            "model": "meta-llama/llama-3.2-1b-instruct:free",
            "response": response_content,
        }

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error connecting to OpenRouter API: {str(e)}")


