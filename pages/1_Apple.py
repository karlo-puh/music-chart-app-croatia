from urllib.error import URLError
import altair as alt
import pandas as pd
import streamlit as st
from streamlit.hello.utils import show_code



# Set page configuration
st.set_page_config(
    page_title="Apple Charts",
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
st.markdown("# Apple Charts")
st.sidebar.header("Apple Charts")
st.write("""Data scraped from Weekly Croatian [Apple Chart](https://kworb.net/charts/apple_s/hr.html)""")

# DataFrame customization
st.dataframe(
    st.session_state['apple'][['chart_position', 'track_name', 'last_week']],
    width = 1200,
    height= 600,
    hide_index=True,
    column_config={
        "chart_position": st.column_config.Column(
            "Chart Position",
            width = "small"
        ),
        "track_name": st.column_config.Column(
            "Track Title",
            width = "large"
            ),
        "last_week": st.column_config.Column(
            "Last Week",
            width = "small"
        )
    },
)
