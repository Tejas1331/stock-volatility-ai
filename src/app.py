from flask import Flask, jsonify
from dotenv import load_dotenv
import os
from google import genai

# Load environment variables
load_dotenv()

# Create Gemini client
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

app = Flask(__name__)

@app.route("/")
def home():
    return "Flask + Gemini (uv) is running 🚀"

@app.route("/ask", methods=["GET"])
def ask_gemini():
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="How are you?"
    )
    return jsonify({"response": response.text})

if __name__ == "__main__":
    app.run(debug=True)
