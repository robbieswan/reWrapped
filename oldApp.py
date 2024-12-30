import os
import requests
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# Spotify API Configuration
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_URL = "https://api.spotify.com/v1/me/top/"

CLIENT_ID = '55ae96424a324fdc94a7c741218818d1'
CLIENT_SECRET = 'bad2752d4c4d451da8b3dab0ca76481d'
REDIRECT_URI = 'https://rewrapped.streamlit.app/'
SCOPES = "user-top-read"

def get_auth_url():
    """Generate the Spotify authorization URL."""
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPES
    }
    return f"{SPOTIFY_AUTH_URL}?" + "&".join([f"{k}={v}" for k, v in params.items()])

def get_access_token(auth_code):
    """Exchange authorization code for an access token."""
    payload = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    response = requests.post(SPOTIFY_TOKEN_URL, data=payload)
    response.raise_for_status()
    return response.json()

def get_top_items(token, item_type="tracks", time_range="long_term", limit=20):
    """Fetch top tracks or artists for the user."""
    headers = {
        "Authorization": f"Bearer {token}"
    }
    params = {
        "time_range": time_range,
        "limit": limit
    }
    response = requests.get(f"{SPOTIFY_API_URL}{item_type}", headers=headers, params=params)
    response.raise_for_status()
    return response.json()

def format_top_tracks(data):
    """Format top tracks data for display."""
    tracks = [
        {
            "Name": track["name"],
            "Artist": ", ".join([artist["name"] for artist in track["artists"]]),
            "Album Name": track["album"]["name"],
            "Album Image URL": track["album"]["images"][0]["url"] if track["album"].get("images") else None,
            "Track Preview URL": track["preview_url"],
            "Popularity": track["popularity"],
            "Track URL": track["external_urls"]["spotify"]  # Spotify URL for embedding
        } for track in data.get("items", [])
    ]
    return tracks

def format_top_artists(data):
    """Format top artists data for display."""
    artists = [
        {
            "Name": artist["name"],
            "Image URL": artist["images"][0]["url"] if artist.get("images") else None,
            "Popularity": artist["popularity"],
            "Spotify URL": artist["external_urls"].get("spotify")  # Spotify URL for embedding
        } for artist in data.get("items", [])
    ]
    return artists

def calculate_uniqueness(data):
    """Calculate uniqueness based on popularity score and return the top 10 unique items."""
    unique_items = sorted(data, key=lambda x: x.get('Popularity', 0))
    return unique_items[:10]

# Streamlit app
st.title("Welcome to Spotify (Re)Wrapped")

st.markdown("""<style>
    div.stButton > button {
        background-color: #f0f0f5;
        color: black;
        font-size: 16px;
        height: 3em;
        width: 12em;
        border-radius: 10px;
        margin: 5px;
    }
    div.stButton > button:focus {
        background-color: #4CAF50;
        color: white;
    }
</style>""", unsafe_allow_html=True)

if "access_token" not in st.session_state:
    st.session_state["access_token"] = None

auth_code = st.query_params.get("code")

if auth_code and st.session_state["access_token"] is None:
    try:
        tokens = get_access_token(auth_code)
        st.session_state["access_token"] = tokens.get("access_token")
        st.success("Authentication successful!")
    except Exception as e:
        st.error(f"An error occurred: {e}")

if st.session_state["access_token"] is None:
    st.write("1. Click the link below to authenticate with Spotify.")
    auth_url = get_auth_url()
    st.markdown(f"[Authenticate with Spotify]({auth_url})", unsafe_allow_html=True)
else:
    st.markdown("**Choose a time range:**")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Short Term (4 weeks)", key="short_term"):
            time_range = "short_term"
    with col2:
        if st.button("Medium Term (6 months)", key="medium_term"):
            time_range = "medium_term"
    with col3:
        if st.button("Long Term (~1 year)", key="long_term"):
            time_range = "long_term"

    st.markdown("---")  # Separator

    st.markdown("**Choose an option:**")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("My Top Tracks 🎶", key="top_tracks"):
            selected_option = "tracks"
    with col2:
        if st.button("My Top Artists 🎤", key="top_artists"):
            selected_option = "artists"

    top_tracks_data, top_artists_data = None, None

    if selected_option == "tracks":
        top_tracks_data = get_top_items(
            st.session_state["access_token"], item_type="tracks", time_range=time_range
        )
    if selected_option == "artists":
        top_artists_data = get_top_items(
            st.session_state["access_token"], item_type="artists", time_range=time_range
        )

    if top_tracks_data:
        st.write("Your Top Tracks:")
        tracks = format_top_tracks(top_tracks_data)

        for idx, track in enumerate(tracks, start=1):
            col1, col2 = st.columns([1, 4])

            with col1:
                if track["Album Image URL"]:
                    st.image(track["Album Image URL"], caption=track["Album Name"], use_container_width=True, width=100)
                else:
                    st.write("Image not available")

            with col2:
                embed_url = track['Track URL'].replace("open.spotify.com", "embed.spotify.com")
                st.markdown(f"**{idx}. {track['Name']}** by {track['Artist']}", unsafe_allow_html=True)
                components.iframe(embed_url, width=400, height=152, scrolling=False)

    if top_artists_data:
        st.write("Your Top Artists:")
        artists = format_top_artists(top_artists_data)

        for idx, artist in enumerate(artists, start=1):
            col1, col2 = st.columns([1, 4])

            with col1:
                if artist["Image URL"]:
                    st.image(artist["Image URL"], caption=artist["Name"], use_container_width=True, width=100)
                else:
                    st.write("Image not available")

            with col2:
                embed_url = artist['Spotify URL'].replace("open.spotify.com", "embed.spotify.com")
                st.markdown(f"**{idx}. {artist['Name']}**", unsafe_allow_html=True)
                components.iframe(embed_url, width=400, height=152, scrolling=False)
