from flask import Flask, render_template, request, jsonify
import os
from groq import Groq
import json
import platform
import subprocess
from pathlib import Path
from pywhatkit import search, playonyt

# Constants
GROQ_API_KEY = "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"
DATA_PATH = Path("data/ChatLog.json")
FRONTEND_PATH = Path("frontend")

# Ensure the Data folder exists and the ChatLog.json file
if not DATA_PATH.parent.exists():
    os.makedirs(DATA_PATH.parent)  # Create the 'data' directory if it doesn't exist
if not DATA_PATH.exists():
    with open(DATA_PATH, "w") as f:
        f.write("[]")  # Initial empty JSON content

client = Groq(api_key=GROQ_API_KEY)

# Flask app setup
app = Flask(__name__, static_folder='static', template_folder='frontend')


@app.route('/')
def index():
    # Serve the index.html from the frontend folder
    return render_template('index.html')


@app.route('/google_search', methods=['POST'])
def google_search():
    query = request.form['query']
    answer = perform_google_search(query)
    return jsonify({"answer": answer})


@app.route('/generate_content', methods=['POST'])
def generate_content():
    topic = request.form['topic']
    content = generate_content_ai(topic)
    return jsonify({"content": content})


# Perform Google Search using pywhatkit (Can be enhanced with real APIs)
def perform_google_search(query):
    search(query)
    return f"Search for '{query}' initiated."


# Generate Content using Groq API
def generate_content_ai(topic):
    messages = [{"role": "system", "content": f"Create content about {topic}"}]
    completion = client.chat.completions.create(
        model="mixtral-8x7b-32768",
        messages=messages,
        max_tokens=2048,
        temperature=0.7,
        top_p=1,
        stream=True,
    )

    answer = ""
    for chunk in completion:
        if chunk.choices[0].delta.content:
            answer += chunk.choices[0].delta.content

    return answer


# Helper functions for opening and closing apps (platform dependent)
def open_app(app_name):
    if platform.system() == "Windows":
        subprocess.Popen(['start', app_name], shell=True)
    elif platform.system() == "Darwin":  # macOS
        subprocess.Popen(["open", "-a", app_name])
    else:
        return "Unsupported OS"


def close_app(app_name):
    if platform.system() == "Windows":
        subprocess.Popen(['taskkill', '/f', '/im', app_name])
    elif platform.system() == "Darwin":  # macOS
        subprocess.Popen(["pkill", app_name])
    else:
        return "Unsupported OS"


# Starting the Flask app
if __name__ == '__main__':
    app.run(debug=True)
