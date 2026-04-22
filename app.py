from flask import Flask, render_template, request, jsonify
from groq import Groq
import os
from dotenv import load_dotenv
from database import collection

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Debug: check API key
api_key = os.getenv("GROQ_API_KEY")
print("Loaded API KEY:", api_key)

# Initialize Groq client safely
client = Groq(api_key=api_key)


def analyze_sentiment(text):
    try:
        prompt = f"""
        Analyze the sentiment of the following text and respond ONLY in one word:
        Positive, Negative, or Neutral.

        Text: "{text}"
        """

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}]
        )

        result = response.choices[0].message.content.strip()

        # Clean response (extra safety)
        if "positive" in result.lower():
            return "Positive"
        elif "negative" in result.lower():
            return "Negative"
        else:
            return "Neutral"

    except Exception as e:
        print("Groq API Error:", e)
        return "Error"


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        data = request.json
        text = data.get("text")

        if not text:
            return jsonify({"sentiment": "No text provided"})

        sentiment = analyze_sentiment(text)

        # Save only if valid
        if sentiment != "Error":
            collection.insert_one({
                "text": text,
                "sentiment": sentiment
            })

        return jsonify({"sentiment": sentiment})

    except Exception as e:
        print("Server Error:", e)
        return jsonify({"sentiment": "Server Error"})


@app.route("/stats")
def stats():
    try:
        total = collection.count_documents({})
        positive = collection.count_documents({"sentiment": "Positive"})
        negative = collection.count_documents({"sentiment": "Negative"})
        neutral = collection.count_documents({"sentiment": "Neutral"})

        return jsonify({
            "total": total,
            "positive": positive,
            "negative": negative,
            "neutral": neutral
        })

    except Exception as e:
        print("Stats Error:", e)
        return jsonify({"total": 0, "positive": 0, "negative": 0, "neutral": 0})


if __name__ == "__main__":
    app.run(debug=True)