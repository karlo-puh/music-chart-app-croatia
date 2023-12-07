from urllib.error import URLError
import altair as alt
import pandas as pd
import streamlit as st
from streamlit.hello.utils import show_code



# Set page configuration
st.set_page_config(
    page_title="Extra FM Most Played Songs",
    page_icon="📊",
    layout="wide",  # You can adjust the layout
)

# Add background color
st.markdown(
    """
    <style>
        body {
            background-color: #f4f4f4;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Main content
st.markdown("# Extra FM  Charts")
st.sidebar.header("Extra FM  Charts")
st.write("""Data from [Extra FM Playlist](https://onlineradiobox.com/hr/extra936/playlist/) last 7 days.""")

# DataFrame customization
st.dataframe(
    st.session_state['extrafm'][['track_name', 'times_played']],
    width = 1200,
    height= 600,
    hide_index=False,
    column_config={
        "times_played": st.column_config.ProgressColumn(
            "Number of plays",
            help="Last 7 days not counting between 00:00 and 06:00",
            width= "medium",
            format="%d",
            min_value=0,
            max_value=int(st.session_state['extrafm'].times_played.max())
        ),
        "track_name": st.column_config.Column(
            "Track Title",
            width = "large"
            ),
    },
)
