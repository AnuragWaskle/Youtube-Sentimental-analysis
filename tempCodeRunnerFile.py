from flask import Flask, request, jsonify, render_template
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from flask_cors import CORS
import sentimental_analyzer
import matplotlib.pyplot as plt
import io
import base64
import symspellpy 
from symspellpy.symspellpy import SymSpell, Verbosity
import words  # Import your words.py file

app = Flask(__name__)
CORS(app)

# Replace with YouTube API key
api_key = "AIzaSyBd8oa2qjhZZrDSg9TXHTmCj-ek_gd9Ce0"

# Initialize SymSpell
sym_spell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)

# Using vader_lexicon from words.py
vader_lexicon = words.vader_lexicon  # Make sure this is the correct name of the dictionary

# Load vader_lexicon into SymSpell
for word, count in vader_lexicon.items():
    sym_spell.create_dictionary_entry(word, count)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/comments", methods=["POST"])
def get_comments():
    data = request.get_json()
    query = data.get("query", "")

    if not query:
        return jsonify({"error": "No search term provided"}), 400

    try:
        youtube = build('youtube', 'v3', developerKey=api_key)

        # Search for videos based on the query
        search_response = youtube.search().list(
            q=query,
            part="id",
            type="video",
            maxResults=5
        ).execute()

        # Get video IDs from search results
        video_ids = [item['id']['videoId'] for item in search_response.get('items', [])]
        print("Video IDs found:", video_ids)  # Log the video IDs to check if the search is working

        # Fetch comments from the videos
        comments = []
        for video_id in video_ids:
            try:
                response = youtube.commentThreads().list(
                    videoId=video_id,
                    part="snippet",
                    maxResults=10
                ).execute()

                # Log the response to check if comments are returned
                print(f"Comments for video {video_id}:", response)

                for item in response.get('items', []):
                    comment = item['snippet']['topLevelComment']['snippet'].get('textDisplay')
                    if comment:
                        comments.append(comment)

            except HttpError as e:
                print(f"An error occurred while fetching comments for video {video_id}: {e}")
                continue

        if not comments:
            return jsonify({"message": "No comments found for the given query."}), 404

        # Perform spelling correction and sentiment analysis
        sentiments = []
        sentiment_counts = {"Positive": 0, "Neutral": 0, "Negative": 0}
        for comment in comments:
            # Correct spelling while keeping the original comment
            corrected_comment = sym_spell.lookup_compound(comment, max_edit_distance=2)[0].term
            sentiment_score = sentimental_analyzer.analyze_polarity(corrected_comment)

            # Determine sentiment label
            if sentiment_score >= 0.05:
                sentiment = "Positive"
            elif sentiment_score <= -0.05:
                sentiment = "Negative"
            else:
                sentiment = "Neutral"
            sentiment_counts[sentiment] += 1

            sentiments.append({
                "original_comment": comment,
                "corrected_comment": corrected_comment,
                "sentiment": sentiment,
                "scores": sentiment_score
            })

        # Generate sentiment pie chart
        plt.figure(figsize=(6, 6))
        plt.pie(sentiment_counts.values(), labels=sentiment_counts.keys(), autopct='%1.1f%%', colors=['green', 'orange', 'red'])
        plt.title('Sentiment Analysis Summary')
        plt.tight_layout()

        # Save the chart as a base64 string
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        chart_base64 = base64.b64encode(img.read()).decode('utf-8')
        plt.close()

        accuracy = sum(sentiment_counts.values())  # Calculate total number of comments
        accurate_sentiment_percentage = (sentiment_counts["Positive"] / accuracy) * 100 if accuracy else 0

        return jsonify({
            "sentiments": sentiments,
            "summary": sentiment_counts,
            "chart": chart_base64,
            "accuracy": f"Accuracy of Positive Sentiment: {accurate_sentiment_percentage:.2f}%"
        })

    except HttpError as e:
        print(f"An error occurred while connecting to YouTube: {e}")
        return jsonify({"error": f"An error occurred while connecting to YouTube: {e}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
