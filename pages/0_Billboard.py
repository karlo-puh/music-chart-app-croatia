from urllib.error import URLError
import altair as alt
import pandas as pd
import streamlit as st
from streamlit.hello.utils import show_code



# Set page configuration
st.set_page_config(
    page_title="Billboard Charts",
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
st.markdown("# Billboard Charts")
st.sidebar.header("Billboard Charts")
st.write("""Data scraped from Weekly Croatian [Billboard Chart](https://www.billboard.com/charts/croatia-songs-hotw/)""")

# DataFrame customization
st.dataframe(
    st.session_state['billboard'][['chart_position', 'track_name', 'peak_position', 'weeks_on_chart']],
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
        "peak_position": st.column_config.Column(
            "Peak position",
            width = "small"
        ),
        "weeks_on_chart": st.column_config.ProgressColumn(
            "Weeks on chart",
            help="The number of consecutive weeks song was on the charts",
            width= "medium",
            format="%d",
            min_value=0,
            max_value=int(st.session_state['billboard'].weeks_on_chart.max())
        )
    },
)
