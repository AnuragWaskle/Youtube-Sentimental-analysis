from words import vader_lexicon

def analyze_polarity(string):
    score = 0

    for i in string.split():
        score += vader_lexicon.get(i.lower(), 0)

    return score

if __name__ == "__main__":
    comment = "I had a sandwich for lunch today."
    score = analyze_polarity(comment)
    if score <= -0.05:
        print("The sentiment of the string is negative")
    elif score >= 0.05:
        print("The sentiment of the string is positive")
    else:
        print("Neutral")