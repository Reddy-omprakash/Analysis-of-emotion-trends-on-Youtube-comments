from flask import Flask, render_template, request
import re
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import googleapiclient.discovery

# Initialize NLTK's VADER sentiment analyzer
nltk.download('vader_lexicon')
sid = SentimentIntensityAnalyzer()

# Initialize Flask application
app = Flask(__name__)

# YouTube API setup
api_service_name = "youtube"
api_version = "v3"
DEVELOPER_KEY = "AIzaSyDcYWzjg9tcKyjCHaHfqjCAqVuMrjPQWhg"
youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey=DEVELOPER_KEY)

# Function to analyze sentiment of YouTube comments
def analyze_sentiment(video_id):
    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=100
    )
    response = request.execute()
    comments_sentiments = []
    for item in response['items']:
        comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
        scores = sid.polarity_scores(comment)
        sentiment = "Positive" if scores['compound'] > 0 else "Negative" if scores['compound'] < 0 else "Neutral"
        comments_sentiments.append({'comment': comment, 'sentiment': sentiment})
    return comments_sentiments

# Function to extract video ID from YouTube link
def extract_video_id(youtube_link):
    video_id_match = re.search(r"(?<=v=)[\w-]+", youtube_link)
    if video_id_match:
        return video_id_match.group(0)
    else:
        return None

# Route to handle the form submission and display results
# @app.route('/', methods=['GET', 'POST'])
# def index():
#     if request.method == 'POST':
#         youtube_link = request.form['youtube_link']
#         video_id = extract_video_id(youtube_link)
#         if video_id:
#             comments_sentiments = analyze_sentiment(video_id)
#             return render_template('results.html', comments_sentiments=comments_sentiments)
#         else:
#             return "Invalid YouTube link. Please provide a valid link."
#     return render_template('index.html')

# Route to handle the form submission and display results
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        youtube_link = request.form['youtube_link']
        video_id = extract_video_id(youtube_link)
        if video_id:
            comments_sentiments = analyze_sentiment(video_id)
            positive_count = sum(1 for comment_sentiment in comments_sentiments if comment_sentiment['sentiment'] == 'Positive')
            negative_count = sum(1 for comment_sentiment in comments_sentiments if comment_sentiment['sentiment'] == 'Negative')
            neutral_count = sum(1 for comment_sentiment in comments_sentiments if comment_sentiment['sentiment'] == 'Neutral')
            return render_template('results.html', comments_sentiments=comments_sentiments, positive_count=positive_count, negative_count=negative_count, neutral_count=neutral_count)
        else:
            return "Invalid YouTube link. Please provide a valid link."
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
