import streamlit as st
from streamlit.logger import get_logger
from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import numpy as np
from fuzzywuzzy import fuzz


LOGGER = get_logger(__name__)


# Set page configuration
st.set_page_config(
    page_title="Chars Overall",
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


st.write("# Welcome to Streamlit! 👋")

# Function to clean up track names
def clean_track_name(track_name):
    return re.sub(r'\s{2,}', ' - ', track_name)

def convert_balkan_characters(input_string):
    replace_dict = {
        'ć': 'c',
        'č': 'c',
        'ž': 'z',
        'š': 's',
        'đ': 'd',
    }
    
    result_string = input_string
    for old, new in replace_dict.items():
        result_string = result_string.replace(old, new)
    return result_string

# Function for fuzzy matching
def fuzzy_match(song1, song2):
    return fuzz.token_set_ratio(convert_balkan_characters(song1.lower()), convert_balkan_characters(song2.lower()))

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
        last_week = properties[1].text.strip().replace('=', '0')
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

        #Check if there is actual data before extracting
    
        if table:
            table = table.find('tbody')
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

                
                pattern = re.compile(r'\bfea\w*', re.IGNORECASE)
                song_and_artist = re.sub(r'\([^)]*\)', '', song_and_artist)
                song_and_artist = re.sub(pattern, '', song_and_artist).strip()

                if song_and_artist in song_dict.keys():
                    song_dict[song_and_artist] += 1
                else:
                    song_dict[song_and_artist] = 1

    sorted_songs = sorted(song_dict.items(), key=lambda x: x[1], reverse=True)

    # Create dataframe
    st.session_state['extrafm'] = pd.DataFrame(sorted_songs, columns=['track_name', 'times_played'])






st.session_state['billboard']['source'] = 'billboard'
st.session_state['deezer']['source'] = 'deezer'
st.session_state['apple']['source'] = 'apple'
st.session_state['youtube']['source'] = 'youtube'

one_dataframe = pd.concat([st.session_state['billboard'][['track_name','chart_position','source']], 
                           st.session_state['deezer'][['track_name','chart_position','source']], 
                           st.session_state['apple'][['track_name','chart_position','source']],
                           st.session_state['youtube'][['track_name','chart_position','source']]],
                           ignore_index=True)


#Cleaning song titles
pattern = re.compile(r'\bfea\w*', re.IGNORECASE)
one_dataframe['track_name'] = one_dataframe['track_name'].str.replace(r'\([^)]*\)', '', regex=True).replace(pattern, '', regex=True)
one_dataframe['normalized_chart_position'] = abs(((one_dataframe['chart_position'] - 1) / 24) -1)

# Fuzzy Matching and Avoiding Duplicates
unique_tracks = []
matching_threshold = 90  # Adjust this threshold based on your data and requirements

aggregated_scores = {}
matched_songs = {}

# Iterate over each row in the DataFrame
for index, row in one_dataframe.iterrows():
    track = row['track_name']
    matched = False

    for unique_track in aggregated_scores.keys():
        if fuzzy_match(track, unique_track) > matching_threshold:
            # Match found, aggregate the score and add to the list of matched songs
            aggregated_scores[unique_track] += row['normalized_chart_position']
            matched_songs[unique_track].append(track)
            matched = True
            break

    if not matched:
        # If no match found, create a new entry in the dictionaries
        aggregated_scores[track] = row['normalized_chart_position']
        matched_songs[track] = [track]

# Convert the dictionaries to a new DataFrame
result_df = pd.DataFrame({
    'unique_track': list(aggregated_scores.keys()),
    'chart_position_sum': list(aggregated_scores.values()),
    'matched_songs': list(matched_songs.values())
})

result_df = result_df.sort_values(by='chart_position_sum', ascending=False).reset_index(drop=True)
result_df['extrafm'] = np.nan

for result_index, result_row in result_df.iterrows():
    for index, row in one_dataframe.iterrows():
        if row['track_name'] in result_row['matched_songs']:
            result_df.at[result_index, row['source']] = row['chart_position']

            #Add 0.2 score for billboard position
            if row['source'] == 'billboard':
                result_df.at[result_index, 'chart_position_sum'] += 0.2

    for index, row in st.session_state['extrafm'].iterrows():
        if fuzzy_match(row['track_name'], result_row['unique_track']) > 90:
            result_df.at[result_index, 'extrafm'] = row['times_played']
            result_df.at[result_index, 'chart_position_sum'] += ((row['times_played'])/(st.session_state['extrafm']['times_played'].max()) / 2)


result_df['extrafm'].fillna(0, inplace = True)
result_df.fillna(np.inf, inplace = True)


st.dataframe(result_df[['unique_track','chart_position_sum','billboard','deezer','apple','youtube', 'extrafm','matched_songs']].sort_values(by = 'chart_position_sum', ascending = False).reset_index(drop = True),
    width = 1500,
    height= 600,
    hide_index=False,
    column_config={
        "unique_track": st.column_config.Column(
            "Track Name"
        ),
        "chart_position_sum": st.column_config.Column(
            "Calculated score"
        ),
        "matched_songs": st.column_config.Column(
            "Matched Song Names"
        ),
        "billboard": st.column_config.Column(
            "Billboard"
        ),
        "deezer": st.column_config.Column(
            "Deezer"
        ),
        "apple": st.column_config.Column(
            "Apple"
        ),
        "youtube": st.column_config.Column(
            "Youtube"
        ),
        "extrafm": st.column_config.ProgressColumn(
            "ExtraFM Times Played",
            format="%d",
            min_value=0,
            max_value=int(st.session_state['extrafm'].times_played.max())
        )
    }
)


