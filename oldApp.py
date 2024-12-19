import os
import requests
import pandas as pd
import streamlit as st
from streamlit_extras.let_it_rain import rain

# Spotify API Configuration
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_URL = "https://api.spotify.com/v1/me/top/"

CLIENT_ID = '55ae96424a324fdc94a7c741218818d1'
CLIENT_SECRET = 'bad2752d4c4d451da8b3dab0ca76481d'
REDIRECT_URI = 'http://localhost:8501'
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
            "Popularity": track["popularity"]  # Popularity score for uniqueness
        } for track in data.get("items", [])
    ]
    return tracks

def format_top_artists(data):
    """Format top artists data for display."""
    artists = [
        {
            "Name": artist["name"],
            "Image URL": artist["images"][0]["url"] if artist.get("images") else None,
            "Popularity": artist["popularity"]  # Popularity score for uniqueness
        } for artist in data.get("items", [])
    ]
    return artists

# Function to add animation
def example():
    rain(
        emoji="🎈",
        font_size=54,
        falling_speed=5,
        animation_length=4,
    )

# Function to calculate uniqueness based on popularity
def calculate_uniqueness(data):
    """Calculate uniqueness based on popularity score and return the top 10 unique items."""
    # Sort items based on popularity score in ascending order (most unique comes first)
    unique_items = sorted(data, key=lambda x: x.get('Popularity', 0))
    return unique_items[:10]

# Streamlit app
st.title("Welcome to Spotify (Re)Wrapped")

# Check if access token is already in session state
if "access_token" not in st.session_state:
    st.session_state["access_token"] = None

# Check for authentication status and URL params
auth_code = st.query_params.get("code")

if auth_code and st.session_state["access_token"] is None:
    try:
        tokens = get_access_token(auth_code)
        st.session_state["access_token"] = tokens.get("access_token")
        st.success("Authentication successful!")
    except Exception as e:
        st.error(f"An error occurred: {e}")

# If not authenticated, show the authentication link
if st.session_state["access_token"] is None:
    st.write("1. Click the link below to authenticate with Spotify.")
    auth_url = get_auth_url()
    st.markdown(f"[Authenticate with Spotify]({auth_url})", unsafe_allow_html=True)
else:
    st.markdown("**Choose an option:**")

    # Create columns for buttons (side by side)
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        top_tracks_button = st.button("My Top Tracks 🎶")
    with col2:
        top_artists_button = st.button("My Top Artists 🎤")
    with col3:
        top_uniqueness_button = st.button("How Niche Am I? ✨")  # New button for uniqueness
    with col4:
        future_button2 = st.button("Get AI Analyzed 📂")

    top_tracks_data, top_artists_data = None, None

    if top_tracks_button:
        example()  # Run animation when top tracks button is clicked
        top_tracks_data = get_top_items(st.session_state["access_token"], item_type="tracks")
    if top_artists_button:
        example()  # Run animation when top artists button is clicked
        top_artists_data = get_top_items(st.session_state["access_token"], item_type="artists")

    # Display top tracks and artists side by side if both are selected
    if top_tracks_data and top_artists_data:
        col1, col2 = st.columns(2)

        with col1:
            st.write("Your Top Tracks:")
            tracks = format_top_tracks(top_tracks_data)

            # Display each track's album image, track name, and artist name
            for idx, track in enumerate(tracks, start=1):
                col1, col2 = st.columns([1, 4])  # Adjust columns ratio for image and text
                
                with col1:
                    if track["Album Image URL"]:
                        st.image(track["Album Image URL"], caption=track["Album Name"], use_container_width=True, width=100)  # Image scaled to 1/3 size
                    else:
                        st.write(f"Image not available")
                
                with col2:
                    st.markdown(f"**{idx}. {track['Name']}** by {track['Artist']}", unsafe_allow_html=True)  # Bold and larger number

        with col2:
            st.write("Your Top Artists:")
            artists = format_top_artists(top_artists_data)

            # Display each artist's image and name in a numbered list
            for idx, artist in enumerate(artists, start=1):
                col1, col2 = st.columns([1, 4])  # Adjust columns ratio for image and text
                
                with col1:
                    if artist["Image URL"]:
                        st.image(artist["Image URL"], caption=artist["Name"], use_container_width=True, width=100)  # Image scaled to 1/3 size
                    else:
                        st.write(f"Image not available")
                
                with col2:
                    st.markdown(f"**{idx}. {artist['Name']}**", unsafe_allow_html=True)  # Bold and larger number

    elif top_tracks_data:
        st.write("Your Top Tracks:")
        tracks = format_top_tracks(top_tracks_data)

        # Display each track's album image, track name, and artist name
        for idx, track in enumerate(tracks, start=1):
            col1, col2 = st.columns([1, 4])  # Adjust columns ratio for image and text

            with col1:
                if track["Album Image URL"]:
                    st.image(track["Album Image URL"], caption=track["Album Name"], use_container_width=True, width=100)  # Image scaled to 1/3 size
                else:
                    st.write(f"Image not available")
            
            with col2:
                st.markdown(f"**{idx}. {track['Name']}** by {track['Artist']}", unsafe_allow_html=True)  # Bold and larger number

    elif top_artists_data:
        st.write("Your Top Artists:")
        artists = format_top_artists(top_artists_data)

        # Display each artist's image and name in a numbered list
        for idx, artist in enumerate(artists, start=1):
            col1, col2 = st.columns([1, 4])  # Adjust columns ratio for image and text

            with col1:
                if artist["Image URL"]:
                    st.image(artist["Image URL"], caption=artist["Name"], use_container_width=True, width=100)  # Image scaled to 1/3 size
                else:
                    st.write(f"Image not available")
            
            with col2:
                st.markdown(f"**{idx}. {artist['Name']}**", unsafe_allow_html=True)  # Bold and larger number

        # New functionality for uniqueness button
        # New functionality for uniqueness button
        if top_uniqueness_button:
            example()  # Run animation when uniqueness button is clicked
            
            # Fetch top tracks and artists data for uniqueness calculation
            top_tracks_data = get_top_items(st.session_state["access_token"], item_type="tracks")
            top_artists_data = get_top_items(st.session_state["access_token"], item_type="artists")
            
            # Calculate average popularity for tracks and artists
            if top_tracks_data and top_artists_data:
                tracks = format_top_tracks(top_tracks_data)
                artists = format_top_artists(top_artists_data)
                
                # Compute average popularity for tracks and artists
                avg_track_popularity = sum(track["Popularity"] for track in tracks) / len(tracks)
                avg_artist_popularity = sum(artist["Popularity"] for artist in artists) / len(artists)
                
                # Display header
                st.header("How Niche is Your Music Taste?")
                
                # Create two columns for composite scores
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Average Track Popularity")
                    st.markdown(f"<h1 style='text-align: center; color: green;'>{avg_track_popularity:.2f}</h1>", unsafe_allow_html=True)
                
                with col2:
                    st.subheader("Average Artist Popularity")
                    st.markdown(f"<h1 style='text-align: center; color: blue;'>{avg_artist_popularity:.2f}</h1>", unsafe_allow_html=True)
                
                # Provide some context for the scores
                st.write("""
                - **Lower scores** indicate a more niche music taste.
                - **Higher scores** mean your music taste aligns with popular trends.
                """)
            else:
                st.warning("Unable to calculate niche scores. Please try again.")

        # Get the top 10 unique artists based on popularity (sorted by lowest popularity)
        if top_artists_data:
            artists = format_top_artists(top_artists_data)
            unique_artists = calculate_uniqueness(artists)
            st.write("Your Top 10 Unique Artists:")
            for idx, artist in enumerate(unique_artists, start=1):
                col1, col2 = st.columns([1, 4])  # Adjust columns ratio for image and text
                with col1:
                    if artist["Image URL"]:
                        st.image(artist["Image URL"], caption=artist["Name"], use_container_width=True, width=100)  # Image scaled
            
