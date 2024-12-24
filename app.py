from flask import Flask, request, jsonify, render_template
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from flask_cors import CORS
import sentimental_analyzer
import matplotlib.pyplot as plt
import io
import base64
from symspellpy import SymSpell, Verbosity


app = Flask(__name__)
CORS(app)  # Enables CORS to allow frontend requests from a different origin

# Replace with your YouTube API key
api_key = "AIzaSyDLz-nobHvc8ao-GM5-pgHDiFHKKen6BMk"

# Initialize SymSpell
sym_spell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)

# Load the dictionary for SymSpell (replace with the path to your dictionary or lexicon)
def load_symspell_dictionary():
    dictionary_path = "Lexicon.txt"  # Adjust this path accordingly
    if not sym_spell.load_dictionary(dictionary_path, term_index=0, count_index=1, encoding="utf-8"):
        print("Error loading dictionary")
    else:
        print("Dictionary loaded successfully")

load_symspell_dictionary()

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

        # Fetch comments from the videos
        comments = []
        for video_id in video_ids:
            try:
                response = youtube.commentThreads().list(
                    videoId=video_id,
                    part="snippet",
                    maxResults=10
                ).execute()

                for item in response.get('items', []):
                    comment = item['snippet']['topLevelComment']['snippet'].get('textDisplay')
                    if comment:
                        comments.append(comment)
            except HttpError as e:
                print(f"An error occurred while fetching comments: {e}")
                continue

        # Correct spelling in comments using SymSpell
        corrected_comments = [correct_spelling(comment) for comment in comments]

        # Perform sentiment analysis on corrected comments
        sentiments = []
        sentiment_counts = {"Positive": 0, "Neutral": 0, "Negative": 0}
        for comment in corrected_comments:
            sentiment_score = sentimental_analyzer.analyze_polarity(comment)
            # Determine sentiment label
            if sentiment_score >= 0.05:
                sentiment = "Positive"
            elif sentiment_score <= -0.05:
                sentiment = "Negative"
            else:
                sentiment = "Neutral"
            sentiment_counts[sentiment] += 1
            sentiments.append({"comment": comment, "sentiment": sentiment, "scores": sentiment_score})

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
        return jsonify({"error": f"An error occurred while connecting to YouTube: {e}"}), 500

# Function to correct spelling in a comment using SymSpell
def correct_spelling(comment):
    words = comment.split()  # Split the comment into words
    corrected_words = []

    for word in words:
        # Correct the word using symspell
        suggestions = sym_spell.lookup(word, Verbosity.TOP, max_edit_distance=2)
        corrected_word = suggestions[0].term if suggestions else word
        corrected_words.append(corrected_word)

    return " ".join(corrected_words)

if __name__ == "__main__":
    app.run(debug=True)
