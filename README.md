# YouTube Comment Sentiment Analysis System  

## Introduction  
This project analyzes sentiments of YouTube comments using Natural Language Processing (NLP) techniques. It extracts comments from YouTube videos via the YouTube Data API, corrects spelling errors using SymSpell, and classifies comments into positive, neutral, or negative sentiments.  

---

## Features  
- **YouTube Comment Extraction**: Fetch comments from any public YouTube video.  
- **Spelling Correction**: Corrects spelling errors for accurate sentiment analysis.  
- **Sentiment Analysis**: Categorizes comments into positive, neutral, and negative sentiments.  
- **Visualization**: Displays sentiment distribution in pie charts.  

---

## Technologies Used  
- **Programming Language**: Python  
- **Framework**: Flask  
- **Libraries**:  
  - SymSpell for spelling corrections  
  - Matplotlib for visualizations  
  - Google API client for YouTube comment extraction  

---

## Installation and Setup  

### Prerequisites  
- **Python 3.7 or above** installed on your system  
- A **YouTube Data API key** (Follow the [YouTube API Documentation](https://developers.google.com/youtube/registering_an_application) to generate an API key)  

---

### Step-by-Step Procedure  

1. **Clone the Repository**  
   Open a terminal and clone this repository:  
   ```bash
   git clone https://github.com/YourUsername/YouTube-Comment-Sentiment-Analysis.git
   cd YouTube-Comment-Sentiment-Analysis



Create a Virtual Environment (Optional but Recommended)
Set up a virtual environment to isolate dependencies:

bash
Copy code
python -m venv venv
source venv/bin/activate    # For Linux/macOS  
venv\Scripts\activate       # For Windows  
Install Dependencies
Install the required Python libraries using requirements.txt:

bash
Copy code
pip install -r requirements.txt
Add Your YouTube Data API Key
Open the app.py file in any text editor and replace the placeholder api_key with your YouTube API key:

python
Copy code
api_key = "YOUR_YOUTUBE_API_KEY"
Run the Application
Start the Flask application:

bash
Copy code
python app.py
