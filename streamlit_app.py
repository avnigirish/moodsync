import requests
import streamlit as st

st.title("MoodSync+ 🎵")
st.write("Analyze your mood and get personalized recommendations!")

#mood input
mood = st.selectbox("How are you feeling?", ["happy", "sad", "energetic", "relaxed"])

if st.button("Get Playlists"):
    try:
        # Call FastAPI endpoint
        response = requests.get(f"http://127.0.0.1:8000/spotify-recommendations/?mood={mood}")
        data = response.json()

        if "error" in data:
            st.error(data["error"])
        else:
            # Display playlists
            st.subheader(f"Playlists for '{mood}' mood:")
            for playlist in data["playlists"]:
                st.image(playlist["image"], width=300)
                st.write(f"**{playlist['name']}**")
                st.write(f"*{playlist['description']}*")
                st.write(f"[Listen on Spotify]({playlist['url']})")
                st.write("---")

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")