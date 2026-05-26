import streamlit as st
import re

def extract_youtube_id(url):
    """Extract the YouTube video ID from a URL."""
    if not url:
        return None
    regex = r'(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})'
    match = re.search(regex, url)
    return match.group(1) if match else None

def render_video_player(url):
    """Renders a YouTube video player given a URL."""
    video_id = extract_youtube_id(url)
    if video_id:
        iframe_html = f'<iframe width="100%" height="400" src="https://www.youtube.com/embed/{video_id}?rel=0" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>'
        st.markdown(iframe_html, unsafe_allow_html=True)
    else:
        st.error("Invalid YouTube URL provided.")
