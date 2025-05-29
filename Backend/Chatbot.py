import os
import datetime
from json import load, dump, JSONDecodeError
from groq import Groq

Username = "Shark"
Assistantname = "Jarvis"
GroqAPIKey = ""

client = Groq(api_key=GroqAPIKey)

SystemPrompt = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Reply in only English, even if the question is in Hindi, reply in English.***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""

SystemChatBot = [{"role": "system", "content": SystemPrompt}]
chatlog_path = r"../Data/ChatLog.json"
os.makedirs(os.path.dirname(chatlog_path), exist_ok=True)
# Load or initialize messages
try:
    if not os.path.exists(chatlog_path) or os.path.getsize(chatlog_path) == 0:
        raise FileNotFoundError
    with open(chatlog_path, 'r') as file:
        messages = load(file)
except (FileNotFoundError, JSONDecodeError):
    messages = SystemChatBot.copy()
    with open(chatlog_path, 'w') as file:
        dump(messages, file, indent=4)

def RealtimeInformation():
    now = datetime.datetime.now()
    return (
        f"Please use this real-time information if needed,\n"
        f"Day: {now.strftime('%A')}\n"
        f"Date: {now.strftime('%d')}\n"
        f"Month: {now.strftime('%B')}\n"
        f"Year: {now.strftime('%Y')}\n"
        f"Time: {now.strftime('%H')} hours\n"
        f"{now.strftime('%M')} Minutes\n"
        f"{now.strftime('%S')} Seconds\n"
    )

def AnswerModifier(answer):
    return '\n'.join([line for line in answer.split('\n') if line.strip()])

def ChatBot(query):
    try:
        # Reload messages to keep session synced
        with open(chatlog_path, 'r') as file:
            messages = load(file)

        messages.append({"role": "user", "content": query})

        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=SystemChatBot + [{"role": "system", "content": RealtimeInformation()}] + messages,
            max_tokens=1024,
            temperature=0.7,
            top_p=1,
            stream=True
        )

        answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                answer += chunk.choices[0].delta.content

        answer = answer.replace("</s>", " ")
        messages.append({"role": "system", "content": answer})

        with open(chatlog_path, 'w') as file:
            dump(messages, file, indent=4)

        return AnswerModifier(answer)
    except Exception as e:
        print("Error:", e)
        return "An error occurred. Please check the logs."

if __name__ == "__main__":
    while True:
        user_input = input("Enter your question: ")
        print(ChatBot(user_input))
