import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import youtube  # Import the youtube.py script
import requests

def get_coordinates(city_name):
    """Fetch latitude and longitude for a given city name."""
    url = f'https://nominatim.openstreetmap.org/search?city={city_name}&format=json'
    headers = {
        'User-Agent': 'stream/1.0'
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    if data:
        lat = data[0]['lat']
        lon = data[0]['lon']
        return lat, lon
    else:
        st.error("City not found!")
        return None, None

# Set up Streamlit page configuration
st.set_page_config(page_title="Social-guard", layout="wide", initial_sidebar_state="expanded")

# Sidebar for settings
# st.sidebar.title("Dashboard")

# Main dashboard layout
st.title("YouTube Channel Dashboard")

# YouTube Data Fetching Section
st.subheader("Fetch YouTube Video and Channel Data")
with st.form("video_fetch_form"):
    hashtag = st.text_input("Enter a hashtag to search for:")
    city = st.text_input("Enter a city name:")
    radius = st.text_input("Enter search radius (e.g., '50km'):", "50km")
    start_date = st.date_input("Start date", value=datetime(2023, 9, 16))
    end_date = st.date_input("End date", value=datetime(2024, 9, 15))
    max_results = st.number_input("Maximum results to fetch:", min_value=1, max_value=50, value=10)
    chart_type = st.selectbox("Select a chart type", ["Bar", "Line", "Area"])

    csv_filename = st.text_input("Enter the filename to save data:", "video_data.csv")
    submitted = st.form_submit_button("Fetch Data")

if submitted:
    try:
        # Convert dates to datetime objects
        start_date = datetime.combine(start_date, datetime.min.time())
        end_date = datetime.combine(end_date, datetime.max.time())

        # Fetch video data
        lat, lon = None, None
        if city:
            lat, lon = get_coordinates(city)
            if lat and lon:
                st.write(f"Coordinates for {city}: Latitude: {lat}, Longitude: {lon}")
            else:
                st.write("Could not retrieve coordinates.")

        st.write("Fetching video data, please wait...")
        youtube.video_info(hashtag, lat, lon, radius, max_results, start_date, end_date, csv_filename)
        st.success(f"Data fetched and saved to {csv_filename}.")

        # Load CSV data for display
        video_data = pd.read_csv(csv_filename)
        st.dataframe(video_data)

        # Show all channels summary
        st.subheader("All Channels Summary")
        channel_summary = video_data[['Channel Title', 'Channel URL', 'Subscriber Count', 'Total Views', 'Video Count']].drop_duplicates()

        # Display channel information in cards
        st.subheader("Channel Details")

        # CSS for card styling
        card_style = """
            <style>
            .card {
                border: 1px solid #e0e0e0;
                border-radius: 10px;
                padding: 15px;
                margin: 15px 0;
                background-color: #f9f9f9;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                transition: transform 0.2s ease, box-shadow 0.2s ease;
            }
            .card:hover {
                transform: scale(1.02);
                box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
            }
            .metric {
                font-size: 18px;
                font-weight: bold;
                margin: 5px 0;
            }
            </style>
        """
        st.markdown(card_style, unsafe_allow_html=True)

        for _, channel in channel_summary.iterrows():
            channel_card = f"""
            <div class="card">
                <h3>{channel['Channel Title']}</h3>
                <p><strong>Channel URL:</strong> <a href="{channel['Channel URL']}" target="_blank">Visit Channel</a></p>
                <p><strong>Social Blade:</strong> <a href="https://socialblade.com/youtube/channel/{channel['Channel URL'].split('/')[-1]}" target="_blank">View on Social Blade</a></p>
                <div style="display: flex; justify-content: space-between; margin-top: 10px;">
                    <div class="metric">Subscribers: {channel['Subscriber Count']}</div>
                    <div class="metric">Total Views: {channel['Total Views']}</div>
                    <div class="metric">Total Videos: {channel['Video Count']}</div>
                </div>
                <div style="margin-top: 10px;">
                    <strong>Videos by this Channel:</strong>
                    <ul>
            """
            # Add videos for this channel
            channel_videos = video_data[video_data['Channel Title'] == channel['Channel Title']]
            for _, video in channel_videos.iterrows():
                channel_card += f"<li><a href='{video['Video URL']}' target='_blank'>{video['Video Title']}</a></li>"
            # Display charts only when expanded
                # with st.expander("Show Metrics Chart"):
                #     metrics_data = channel_videos[['Published At', 'Views', 'Likes', 'Comments']]
                #     metrics_data['Published At'] = pd.to_datetime(metrics_data['Published At'])

                #     chart_title = f"{chart_type} Chart of Metrics Over Time"
                #     if chart_type == "Bar":
                #         fig = px.bar(metrics_data, x="Published At", y=["Views", "Likes", "Comments"],
                #                      labels={"value": "Count", "variable": "Metrics"},
                #                      title=chart_title)
                #     elif chart_type == "Line":
                #         fig = px.line(metrics_data, x="Published At", y=["Views", "Likes", "Comments"],
                #                       labels={"value": "Count", "variable": "Metrics"},
                #                       title=chart_title)
                #     else:
                #         fig = px.area(metrics_data, x="Published At", y=["Views", "Likes", "Comments"],
                #                       labels={"value": "Count", "variable": "Metrics"},
                #                       title=chart_title)

                #     st.plotly_chart(fig, use_container_width=True)
            channel_card += """
                    </ul>
                </div>
            </div>
            """
            st.markdown(channel_card, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"An error occurred: {e}")
