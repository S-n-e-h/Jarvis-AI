from Frontend.GUI import (
    GraphicalUserInterface,
    SetAssistantStatus,
    ShowTextToScreen,
    TempDirectoryPath,
    SetMicrophoneStatus,
    AnswerModifier,
    QueryModifier,
    GetMicrophoneStatus,
    GetAssistantStatus
)
from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import realtime_search_engine
from Backend.Automation import Automation
from Backend.SpeechToText import SpeechRecognition
from Backend.Chatbot import ChatBot
from Backend.TextToSpeech import TextToSpeech
from dotenv import dotenv_values
from asyncio import run
from time import sleep
import threading
import json
import os

env_vars = dotenv_values(".env")
Username = env_vars.get("USERNAME", "User")
Assistantname = env_vars.get("ASSISTANT_NAME", "Assistant")
DefaultMessage = f"""{Username} : Hello {Assistantname}, How are you?
{Assistantname} : Welcome {Username}. I am doing well. How may I help you?"""

Functions = ["open", "close", "play", "system", "content", "google search", "youtube search"]

def ShowDefaultChatIfNoChats():
    try:
        with open('Data/ChatLog.json', "r", encoding='utf-8') as file:
            if len(file.read()) < 5:
                open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8').close()
                with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as resp_file:
                    resp_file.write(DefaultMessage)
    except FileNotFoundError:
        os.makedirs('Data', exist_ok=True)
        with open('Data/ChatLog.json', 'w', encoding='utf-8') as file:
            json.dump([], file)
        ShowDefaultChatIfNoChats()

def ReadChatLogJson():
    with open('Data/ChatLog.json', 'r', encoding='utf-8') as file:
        return json.load(file)

def ChatLogIntegration():
    json_data = ReadChatLogJson()
    formatted_chatlog = ""
    for entry in json_data:
        role = Username if entry["role"] == "user" else Assistantname
        formatted_chatlog += f"{role}: {entry['content']}\n"

    with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
        file.write(AnswerModifier(formatted_chatlog))

def ShowChatsOnGUI():
    try:
        with open(TempDirectoryPath('Database.data'), "r", encoding='utf-8') as file:
            data = file.read()
        if data.strip():
            with open(TempDirectoryPath('Responses.data'), "w", encoding='utf-8') as file:
                file.write(data)
    except FileNotFoundError:
        pass

def InitialExecution():
    SetMicrophoneStatus("False")
    ShowTextToScreen("")
    ShowDefaultChatIfNoChats()
    ChatLogIntegration()
    ShowChatsOnGUI()

InitialExecution()

def MainExecution():
    TaskExecution = False
    SetAssistantStatus("Listening ... ")
    Query = SpeechRecognition()
    ShowTextToScreen(f"{Username} : {Query}")
    SetAssistantStatus("Thinking ... ")
    Decision = FirstLayerDMM(Query)

    print(f"\nDecision : {Decision}\n")

    G = any(i.startswith("general") for i in Decision)
    R = any(i.startswith("realtime") for i in Decision)

    merged_query = " and ".join(" ".join(i.split()[1:]) for i in Decision if i.startswith(("general", "realtime")))

    for query in Decision:
        if not TaskExecution and any(query.startswith(func) for func in Functions):
            run(Automation(Decision))
            TaskExecution = True

    if R:
        SetAssistantStatus("Searching ... ")
        Answer = realtime_search_engine(QueryModifier(merged_query))
        ShowTextToScreen(f"{Assistantname} : {Answer}")
        TextToSpeech(Answer)
        return

    for query in Decision:
        if query.startswith("general "):
            SetAssistantStatus("Thinking ... ")
            final_query = query.replace("general ", "")
            Answer = ChatBot(QueryModifier(final_query))
            ShowTextToScreen(f"{Assistantname} : {Answer}")
            TextToSpeech(Answer)
            return

        elif query.startswith("realtime "):
            SetAssistantStatus("Searching ... ")
            final_query = query.replace("realtime ", "")
            Answer = realtime_search_engine(QueryModifier(final_query))
            ShowTextToScreen(f"{Assistantname} : {Answer}")
            TextToSpeech(Answer)
            return

        elif "exit" in query:
            Answer = ChatBot(QueryModifier("Okay, Bye!"))
            ShowTextToScreen(f"{Assistantname} : {Answer}")
            TextToSpeech(Answer)
            os._exit(0)

def FirstThread():
    while True:
        if GetMicrophoneStatus() == "True":
            MainExecution()
        elif "Available" not in GetAssistantStatus():
            SetAssistantStatus("Available ... ")
        sleep(0.1)

def SecondThread():
    print("Launching GUI...")
    try:
        GraphicalUserInterface()
        print("GUI launched successfully.")
    except Exception as e:
        print(f"[ERROR] GUI launch failed: {e}")

if __name__ == "__main__":
    threading.Thread(target=FirstThread, daemon=True).start()
    SecondThread()