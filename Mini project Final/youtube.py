import csv
from googleapiclient.discovery import build
from datetime import datetime

# Set up the API with your key
api_key = 'AIzaSyBP2RiFfqTZV-ofCOiIY-MMC68t4RcYbkc'
youtube = build('youtube', 'v3', developerKey=api_key)

def videoData(video_id):
    """Fetch video metadata including views, likes, dislikes, and comments."""
    try:
        # Get video statistics
        request = youtube.videos().list(
            part="statistics",
            id=video_id
        )
        response = request.execute()

        # Extract video statistics
        video_stats = response['items'][0]['statistics']
        views = int(video_stats.get('viewCount', 0))
        likes = int(video_stats.get('likeCount', 0))
        dislikes = int(video_stats.get('dislikeCount', 0))
        comment_count = int(video_stats.get('commentCount', 0))

        return views, likes, dislikes, comment_count

    except Exception as e:
        print(f"Error fetching statistics for video {video_id}: {e}")
        return None, None, None, None

def channelData(channel_id):
    """Fetch channel metadata including title, subscribers, total views, and video count."""
    try:
        request = youtube.channels().list(
            part="snippet,statistics",
            id=channel_id
        )
        response = request.execute()

        # Extract channel metadata
        channel_info = response['items'][0]
        channel_title = channel_info['snippet']['title']
        channel_id = channel_info['id']
        channel_description = channel_info['snippet']['description']
        subscriber_count = channel_info['statistics'].get('subscriberCount', 'N/A')
        total_views = channel_info['statistics'].get('viewCount', 'N/A')
        video_count = channel_info['statistics'].get('videoCount', 'N/A')

        return channel_title, channel_id, subscriber_count, total_views, video_count, channel_description

    except Exception as e:
        print(f"Error fetching metadata for channel {channel_id}: {e}")
        return None, None, None, None, None, None

def video_info(hashtag, latitude, longitude, radius='50km', max_results=10, start_date=None, end_date=None, csv_filename="video_data.csv"):
    try:
        # Search for videos using the hashtag and within the specified location
        request = youtube.search().list(
            part="snippet",
            q=hashtag,  # Search for the hashtag
            type="video",  # We want videos only
            location=f"{latitude},{longitude}",  # Location in latitude,longitude format
            locationRadius=radius,  # Radius to search within
            maxResults=max_results  # Limit the number of results
        )
        response = request.execute()

        #  thresholds 
        min_views = 0
        min_likes = 0
        min_comments = 0

        
        # total_videos = 0
        # filtered_videos = 0

        # Open CSV file in write mode, creating it if it doesn't exist
        with open(csv_filename, mode='w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'Video Title', 'Description', 'Video URL', 'Published At',
                'Channel Title', 'Channel ID', 'Channel Description', 'Subscriber Count',
                'Total Views', 'Video Count', 'Views', 'Likes', 'Dislikes', 'Comments'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # Write the header row if the file is empty (first write)
            csvfile.seek(0, 2)  
            if csvfile.tell() == 0:  
                writer.writeheader()

            # Loop through the results and display the video details
            for i, item in enumerate(response['items'], 1):
                video_title = item['snippet']['title']
                video_description = item['snippet']['description']
                video_id = item['id']['videoId']
                published_at = item['snippet']['publishedAt']
                channel_title = item['snippet']['channelTitle']
                channel_id = item['snippet']['channelId']

                # Convert the publishedAt to datetime
                published_datetime = datetime.strptime(published_at, '%Y-%m-%dT%H:%M:%SZ')

                # Filter by the date range if specified
                if start_date and end_date:
                    if not (start_date <= published_datetime <= end_date):
                        continue  # Skip if the video is not within the date range

                # Get video statistics (views, likes, dislikes, comments)
                views, likes, dislikes, comment_count = videoData(video_id)

                # Get channel metadata
                channel_title, channel_id, subscriber_count, total_views, video_count, channel_description = channelData(channel_id)

                # Skip videos with low engagement
                if views < min_views or likes < min_likes or comment_count < min_comments:
                    continue  # Skip if the engagement is below the threshold

                # Increment the counter for filtered videos
                # filtered_videos += 1

                # Write the video and channel details to the CSV file
                writer.writerow({
                    'Video Title': video_title,
                    'Description': video_description,
                    'Video URL': f'https://www.youtube.com/watch?v={video_id}',
                    'Published At': published_at,
                    'Channel Title': channel_title,
                    'Channel ID': channel_id,
                    'Channel Description': channel_description,
                    'Subscriber Count': subscriber_count,
                    'Total Views': total_views,
                    'Video Count': video_count,
                    'Views': views,
                    'Likes': likes,
                    'Dislikes': dislikes,
                    'Comments': comment_count
                })

                # Increment the total video count
                # total_videos += 1

                # Print video and channel details
                print(f"Video {i}:")
                print(f"Title: {video_title}")
                print(f"Description: {video_description}")
                print(f"Video URL: https://www.youtube.com/watch?v={video_id}")
                print(f"Published At: {published_at}")
                print(f"Channel: {channel_title}")
                print(f"Channel ID: {channel_id}")
                print(f"Channel Description: {channel_description}")
                print(f"Subscriber Count: {subscriber_count}")
                print(f"Total Views: {total_views}")
                print(f"Video Count: {video_count}")
                print(f"Views: {views}")
                print(f"Likes: {likes}")
                print(f"Dislikes: {dislikes}")
                print(f"Comments: {comment_count}")
                print("-" * 50)

        # Display the total number of videos uploaded in that area and time span
        # print(f"Total number of videos uploaded in the specified area and time span: {total_videos}")
        # print(f"Filtered videos with good engagement: {filtered_videos}")

    except Exception as e:
        print(f"Error: {e}")

# Example usage: Fetch videos for the hashtag '#technology' from a specific location and within a date range
if __name__ == "__main__":
    hashtag = input("Enter the hashtag to search for: ")
    latitude = float(input("Enter the latitude: "))
    longitude = float(input("Enter the longitude: "))
    radius = input("Enter the radius (e.g., '50km', '1000m'): ") or '50km'
    start_date = input("Enter the start date (YYYY-MM-DD): ")
    end_date = input("Enter the end date (YYYY-MM-DD): ")
    max_results = int(input("Enter the number of videos to fetch: "))

    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")

    video_info(hashtag, latitude, longitude, radius, max_results, start_date, end_date)
