from serpapi import GoogleSearch
from groq import Groq
from json import load, dump
import datetime
from pathlib import Path

# Constants
USERNAME = "Shark"
ASSISTANT_NAME = "Jarvis"
GROQ_API_KEY = "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"
DATA_PATH = Path("../Data/ChatLog.json")
SERPAPI_API_KEY = "4e815eb31c988c1987696c1b979eeea3243fede45772781101c5b866ff40cd74"  # Replace with your SerpApi key

# Ensure the Data folder and ChatLog.json exist
DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
if not DATA_PATH.exists():
    with open(DATA_PATH, "w") as f:
        dump([], f)

client = Groq(api_key=GROQ_API_KEY)
SYSTEM_MESSAGE = ""

# Initial system chat
SystemChatBot = [
    {"role": "system", "content": SYSTEM_MESSAGE},
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello, how can I help you?"}
]


def google_search(query):
    try:
        # Use SerpApi to fetch results
        params = {
            "q": query,
            "api_key": SERPAPI_API_KEY,
            "num": 5  # Limit results to 5
        }

        search = GoogleSearch(params)
        results = search.get_dict()

        # Check if we received results
        if 'organic_results' in results:
            answer = f"The search results for '{query}' are:\n[start]\n"
            for result in results['organic_results']:
                answer += f"Title: {result.get('title', 'N/A')}\n"
                answer += f"Description: {result.get('snippet', 'N/A')}\n"
                answer += f"Link: {result.get('link', 'N/A')}\n\n"
            answer += "[end]"
            return answer
        else:
            return "No search results found."

    except Exception as e:
        return f"Google search failed: {str(e)}"


def answer_modifier(answer):
    lines = answer.split("\n")
    non_empty_lines = [line.strip() for line in lines if line.strip()]
    return '\n'.join(non_empty_lines)


def get_datetime_info():
    now = datetime.datetime.now()
    return (
        "Use this real-time information if needed:\n"
        f"Day: {now.strftime('%A')}\n"
        f"Date: {now.strftime('%d')}\n"
        f"Month: {now.strftime('%B')}\n"
        f"Year: {now.strftime('%Y')}\n"
        f"Time: {now.strftime('%H')} hours, {now.strftime('%M')} minutes, {now.strftime('%S')} seconds.\n"
    )


def realtime_search_engine(prompt):
    global SystemChatBot

    try:
        with open(DATA_PATH, "r") as f:
            messages = load(f)
    except Exception:
        messages = []

    messages.append({"role": "user", "content": prompt})

    # Get real-time search results from SerpApi
    SystemChatBot.append({"role": "system", "content": google_search(prompt)})

    completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=SystemChatBot + [{"role": "system", "content": get_datetime_info()}] + messages,
        temperature=0.7,
        max_tokens=2048,
        top_p=1,
        stream=True,
    )

    answer = ""
    for chunk in completion:
        if chunk.choices[0].delta.content:
            answer += chunk.choices[0].delta.content

    answer = answer.replace("</s>", " ")
    messages.append({"role": "system", "content": answer})

    with open(DATA_PATH, 'w') as f:
        dump(messages, f, indent=4)

    SystemChatBot.pop()
    return answer_modifier(answer)


if __name__ == "__main__":
    while True:
        user_input = input("Enter your query: ")
        print(realtime_search_engine(prompt=user_input))
