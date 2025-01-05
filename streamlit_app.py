import requests
import streamlit as st

st.title("MoodSync+")
st.write("Analyze your mood and get personalized recommendations!")

#mood input
mood = st.text_input("How are you feeling today?")

if st.button('Analyze'):
    #send a request to FastAPI endpoint
    response = requests.post(
        "http://127.0.0.1:8000/analyze_mood/", json={"mood": mood}
    )
    if response.status_code == 200:
        result = response.json()
        st.write(f"Mood: {result['mood']}")
        st.write(f"Recommendation: {result['recommendation']}")
    else:
        st.write("Error: Unable to analyze mood")