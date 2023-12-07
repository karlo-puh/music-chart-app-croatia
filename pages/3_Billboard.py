from urllib.error import URLError

import altair as alt
import pandas as pd

import streamlit as st
from streamlit.hello.utils import show_code


st.set_page_config(page_title="Billboard Charts", page_icon="📊")

st.markdown("# Billboard Charts")
st.sidebar.header("Billboard Charts")
st.write(
    """Data scraped from Weekly Croatian [Billboard Charts](https://www.billboard.com/charts/croatia-songs-hotw/)"""
)


st.dataframe(
    st.session_state['billboard'],
    column_config={
        "chart_position": "Chart Position",
        "track_name": "Track Title",
        "peak_position": "Peak position",
        "weeks_on_chart": st.column_config.ProgressColumn(
            "Weeks on chart",
            help="The number of consecutive weeks song was on the charts",
            format = "%d",
            min_value= 0,
            max_value= int(st.session_state['billboard'].weeks_on_chart.max())
        )
    },
    hide_index=True,
)