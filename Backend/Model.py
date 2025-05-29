import time
import cohere
from rich import print
from dotenv import dotenv_values

env = dotenv_values(".env")
CohereAPIkey = "vkuiXGxLccUSw2o0HXiZQMRRkrQcbg5eHS4ajpiX"

co = cohere.Client(api_key=CohereAPIkey)

funcs = [
    "exit", "general", "realtime", "open", "close", "play", "system",
    "content", "google search", "youtube search", "reminder",
    "linkedin search", "instagram search"
]

preamble = """
You are a Decision-Making Model. Your job is to classify the user's query into one or more of the following types:

- general
- realtime
- open
- close
- play
- system
- content
- google search
- youtube search
- reminder
- linkedin search
- instagram search
- exit

Do not answer the query. Only classify it.

Use the following formats:

- general (query)  
  → For questions that don’t need real-time data.  
  → Examples: "What is AI?", "Explain gravity."

- realtime (query)  
  → For queries that need live updates.  
  → Examples: "Weather in Delhi", "Today's cricket score"

- open (app or site)  
  → When the user wants to open something.  
  → Examples: "Open YouTube", "Launch Instagram"

- close (app)  
  → When the user wants to close something.  
  → Examples: "Close Spotify", "Exit Chrome"

- play (song)  
  → When the user wants to play music.  
  → Examples: "Play Shape of You", "Play a Hindi song"

- system (command)  
  → For system actions.  
  → Examples: "Shutdown", "Mute", "Increase brightness"

- content (topic)  
  → When the user wants to create something.  
  → Examples: "Write a story", "Generate Python code"

- google search (query)  
  → For Google searches.  
  → Examples: "Search best laptops on Google"

- youtube search (query)  
  → For YouTube searches.  
  → Examples: "Search music videos on YouTube"

- reminder (task)  
  → When the user wants to set a reminder.  
  → Examples: "Remind me to take meds at 8", "Set reminder"

- linkedin search (query)  
  → For LinkedIn searches.  
  → Examples: "Search software jobs on LinkedIn"

- instagram search (query)  
  → For Instagram searches.  
  → Examples: "Search Virat Kohli on Instagram"

- exit  
  → If the user wants to stop.  
  → Examples: "Bye", "Exit", "Goodnight"

If the user gives multiple tasks, respond with each:
→ Example: "open Chrome, close Spotify"

If unsure, classify as:
→ general (query)
"""

ChatHistory = [
    {"role": "USER", "message": "how are you?"},
    {"role": "CHATBOT", "message": "general how are you?"},
    {"role": "USER", "message": "do you like pizza?"},
    {"role": "CHATBOT", "message": "general do you like pizza?"},
    {"role": "USER", "message": "open chrome and tell me about mahatma gandhi."},
    {"role": "CHATBOT", "message": "open chrome, general tell me about mahatma gandhi."},
    {"role": "USER", "message": "open chrome and firefox"},
    {"role": "CHATBOT", "message": "open chrome, open firefox"},
    {"role": "USER", "message": "what is today's date and by the way remind me that i have a dancing performance on what is today's date"},
    {"role": "CHATBOT", "message": "general what is today's date, reminder 11:00pm 5th aug dancing performance"},
    {"role": "USER", "message": "chat with me."},
    {"role": "CHATBOT", "message": "general chat with me."}
]

def FirstLayerDMM(prompt: str = "test"):
    # Append current user message
    full_history = ChatHistory + [{"role": "user", "message": prompt}]

    stream = co.chat_stream(
        model='command-r-plus',
        message=prompt,
        chat_history=full_history,
        temperature=0.7,
        prompt_truncation='OFF',
        connectors=[],
        preamble=preamble,
    )

    response = ""
    for event in stream:
        if event.event_type == "text-generation":
            response += event.text

    # Normalize and split
    candidates = [part.strip() for part in response.replace("\n", ",").split(",")]
    filtered = [task for task in candidates if any(task.lower().startswith(f) for f in funcs)]
    return filtered or [f"general ({prompt})"]

if __name__ == "__main__":
    while True:
        user_input = input(">>> ")
        output = FirstLayerDMM(user_input)
        print(output)
