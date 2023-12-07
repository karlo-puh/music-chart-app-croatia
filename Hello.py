# Copyright (c) Streamlit Inc. (2018-2022) Snowflake Inc. (2022)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import streamlit as st
from streamlit.logger import get_logger
from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import numpy as np
from fuzzywuzzy import fuzz


LOGGER = get_logger(__name__)


st.set_page_config(
    page_title="Overall",
    page_icon="👋",
)

st.write("# Welcome to Streamlit! 👋")

# Function to clean up track names
def clean_track_name(track_name):
    return re.sub(r'\s{2,}', ' - ', track_name)

# Check for billboard chart in the session state. If not in session state create the dataframe
if "billboard" not in st.session_state:
    data = []
    # Get HTML content from Billboard website
    response = requests.get('https://www.billboard.com/charts/croatia-songs-hotw/')
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the div that contains song data
    table = soup.find_all('div', class_='o-chart-results-list-row-container')

    # Loop through each row in the table
    for row in table:
        # Get chart number
        chart_position = int(row.find('span').text.strip())

        # Get rest of properties
        properties_ul = row.find('ul', class_='lrv-a-unstyle-list lrv-u-flex lrv-u-height-100p lrv-u-flex-direction-column@mobile-max')
        properties = properties_ul.find_all('li')

        # Using properties list items to get all the data
        track_name = clean_track_name(properties[0].text.strip())
        last_week = int(properties[3].text.strip().replace('-', '0'))
        peak_position = int(properties[4].text.strip())
        weeks_on_chart = int(properties[5].text.strip())
        
        data.append([track_name, chart_position, peak_position, weeks_on_chart])

    st.session_state['billboard'] = pd.DataFrame(data, columns=['track_name', 'chart_position', 'peak_position', 'weeks_on_chart'])




# Check for apple chart in the session state. If not in session state create the dataframe
if "apple" not in st.session_state:
    data = []

    # Get HTML content from Apple charts website
    response = requests.get('https://kworb.net/charts/apple_s/hr.html')
    response.encoding = response.apparent_encoding
    soup = BeautifulSoup(response.text, 'html.parser')

    # Get all table rows
    table = soup.find_all('tr')

    # Loop through table rows
    for row in table:
        # Skip header row
        if row.find_all('th'):
            continue

        # Find all table data
        properties = row.find_all('td')

        chart_position = int(properties[0].text.strip())
        last_week = properties[1].text.strip().replace('=', '0')
        track_name = properties[2].text.strip()

        data.append([track_name, chart_position, last_week])

    # Create dataframe
    st.session_state['apple'] = pd.DataFrame(data[0:25], columns=['track_name', 'chart_position', 'last_week'])


# Check for youtube chart in the session state. If not in session state create the dataframe
if "youtube" not in st.session_state:
    data = []

    response = requests.get('https://kworb.net/youtube/trending/hr.html')
    response.encoding = 'UTF-8'
    soup = BeautifulSoup(response.text, 'html.parser')

    table = soup.find('div', class_='music')
    table = table.find('tbody')
    table = table.find_all('tr')

    for row in table:
        properties = row.find_all('td')

        chart_position = int(properties[0].text.strip())
        last_week = properties[1].text.strip().replace('=', '0')
        track_name = properties[2].text.strip()

        data.append([track_name, chart_position, last_week])

    # Create dataframe
    st.session_state['youtube'] = pd.DataFrame(data[0:25], columns=['track_name', 'chart_position', 'last_week'])

    pattern = re.compile(r'\bfea\w*', re.IGNORECASE)
    st.session_state['youtube']['track_name'] = st.session_state['youtube']['track_name'].str.replace(r'\([^)]*\)', '').replace(pattern, '')

# Continue with the rest of your code...



# Check for deezer chart in the session state. If not in session state create the dataframe
if "deezer" not in st.session_state:
    data = []
    response = requests.get('https://kworb.net/charts/deezer/hr.html')
    response.encoding = 'UTF-8'
    soup = BeautifulSoup(response.text, 'html.parser')

    table = soup.find('tbody')
    table = table.find_all('tr')

    for row in table:
        properties = row.find_all('td')

        chart_position = int(properties[0].text.strip())
        last_week = properties[1].text.strip()
        track_name = properties[2].text.strip()

        data.append([track_name, chart_position, last_week])

    # Create dataframe
    st.session_state['deezer'] = pd.DataFrame(data[0:25], columns=['track_name', 'chart_position', 'last_week'])



# Check for extrafm chart in the session state. If not in session state create the dataframe
if "extrafm" not in st.session_state:
    song_dict = {}
    for i in range(0, 7):
        print(i)
        url = 'https://onlineradiobox.com/hr/extra936/playlist/'
        if i != 0:
            url += str(i)

        response = requests.get(url)
        response.encoding = 'UTF-8'
        soup = BeautifulSoup(response.text, 'html.parser')

        table = soup.find('table', class_='tablelist-schedule')
        table = soup.find('tbody')
        table = table.find_all('tr')

        for row in table:
            properties = row.find_all('td')
            song_and_artist = properties[1].text.strip()

            time = properties[0].text.strip()
            time = time.replace('Uživo', '1000')
            time = int(time.replace(':', ''))

            # Adjust for time zone difference of the scraper location
            time += 600

            # Drop songs from 12:00 AM to 6:00 AM or SW (probably commercials)
            if 0 <= time <= 600 or 'SW - ' in song_and_artist:
                continue

            if song_and_artist in song_dict.keys():
                song_dict[song_and_artist] += 1
            else:
                song_dict[song_and_artist] = 1

    sorted_songs = sorted(song_dict.items(), key=lambda x: x[1], reverse=True)

    # Create dataframe
    st.session_state['extrafm'] = pd.DataFrame(sorted_songs[0:50], columns=['track_name', 'times_played'])
