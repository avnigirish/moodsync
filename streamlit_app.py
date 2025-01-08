import requests
import streamlit as st

st.title("MoodSync+ 🎵💪💬")
st.write("Analyze your mood, get exercise recommendations, and chat with our AI assistant!")

# Sidebar for navigation
with st.sidebar:
    st.header("Navigation")
    page = st.radio("Go to:", ["Spotify Recommendations", "Exercise Suggestions", "Chatbot"])

# Spotify Recommendations Page
if page == "Spotify Recommendations":
    st.subheader("Spotify Recommendations 🎵")
    mood = st.selectbox("How are you feeling?", ["happy", "sad", "energetic", "relaxed"])

    if st.button("Get Playlists"):
        try:
            # Call FastAPI endpoint
            response = requests.get(f"http://127.0.0.1:8000/spotify-recommendations/?mood={mood}")
            data = response.json()

            if "error" in data:
                st.error(data["error"])
            else:
                st.subheader(f"Playlists for '{mood}' mood:")
                for playlist in data["playlists"]:
                    st.write(f"**{playlist['name']}**")
                    st.write(f"[Listen on Spotify]({playlist['url']})")
                    st.write("---")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# Exercise Suggestions Page
elif page == "Exercise Suggestions":
    st.subheader("Exercise Recommendations 💪")
    exercise_goal = st.selectbox(
        "What is your fitness goal?",
        ["Lose weight", "Build muscle", "Increase flexibility", "General fitness"]
    )

    if st.button("Get Exercises"):
        try:
            # Call FastAPI endpoint
            response = requests.get(f"http://127.0.0.1:8000/exercise-recommendations/?goal={exercise_goal}")
            data = response.json()

            if "error" in data:
                st.error(data["error"])
            else:
                st.subheader(f"Exercises for '{exercise_goal}':")
                for exercise in data["exercises"]:
                    st.write(f"**{exercise['name']}**: {exercise['description']}")
                    st.write("---")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# Chatbot Page
elif page == "Chatbot":
    st.subheader("MoodSync+ Chatbot 💬")
    st.write("Chat with our AI assistant!")

    user_message = st.text_input("You:", placeholder="Ask me anything...")

    if st.button("Send"):
        try:
            response = requests.post(
                "http://127.0.0.1:8000/chat/",
                json={"message": user_message}
            )
            data = response.json()

            if "error" in data:
                st.error(data["error"])
            else:
                st.write("**You:**", user_message)
                st.write("**AI:**", data["bot_response"])

                # Display Spotify recommendations from the chatbot, if available
                if data.get("spotify_recommendations"):
                    st.subheader("Spotify Recommendations:")
                    for playlist in data["spotify_recommendations"]:
                        st.write(f"**{playlist['name']}**")
                        st.write(f"[Listen on Spotify]({playlist['url']})")
                        st.write("---")

                # Display exercise recommendations from the chatbot, if available
                if data.get("exercise_recommendations"):
                    st.subheader("Exercise Suggestions:")
                    for exercise in data["exercise_recommendations"]:
                        st.write(f"**{exercise['name']}**: {exercise['description']}")
                        st.write("---")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
