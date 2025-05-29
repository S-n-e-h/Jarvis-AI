import platform
import subprocess
import requests
import webbrowser
import os
import keyboard
import asyncio
from pywhatkit import search, playonyt
from rich import print
from groq import Groq
from Backend.TextToSpeech import TextToSpeech
try:
    from AppOpener import close, open as appopen
except ImportError:
    appopen = None
    close = None

useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64 x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36'


client = Groq(api_key='')

SystemChatBot = [{"role": "system", "content": "Hello I am Shark, You're a content writer. You have to write letter"}]
messages = []

# Google search
def GoogleSearch(Topic):
    search(Topic)
    TextToSpeech("Searching in google")
    return True

# Open Notepad / TextEditor
def OpenNotepad(File):
    TextToSpeech("Opening Notepad")
    if platform.system() == "Windows":
        subprocess.Popen(['notepad.exe', File])
    elif platform.system() == "Darwin":
        subprocess.Popen(['open', '-e', File])
    else:
        print("[red]Editor launch not supported on this OS[/red]")

# Write content using Groq
def Content(Topic):
    def ContentWriteAI(prompt):
        messages.append({"role": "user", "content": prompt})
        completion = client.chat.completions.create(
            model="llama3-70b-8192",  # or another supported mode
            messages=SystemChatBot + messages,
            max_tokens=2048,
            temperature=0.7,
            top_p=1,
            stream=True,
        )

        Answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content

        Answer = Answer.replace("</s>", "")
        messages.append({"role": "user", "content": Answer})
        TextToSpeech("Content is written")
        return Answer

    Topic = Topic.replace("Content ", "")
    ContentByAI = ContentWriteAI(Topic)
    filename = rf"Data/{Topic.lower().replace(' ', '')}.txt"

    os.makedirs("../Data", exist_ok=True)

    with open(filename, "w", encoding="utf-8") as f:
        f.write(ContentByAI)

    OpenNotepad(filename)
    return True

def YoutubeSearch(Topic):
    Url4Search = f"https://www.youtube.com/results?search_query={Topic}"
    try:
        webbrowser.get(using='windows-default').open(Url4Search)
        TextToSpeech(f"Searched for {Topic}")
    except webbrowser.Error as e:
        print(f"[red]Failed to open browser: {e}[/red]")
    return True

# Play YouTube
def PlayYoutube(query):
    playonyt(query)
    return True

def PlaySpotify(query):
    try:
        # Open Spotify search in the browser
        search_url = f"https://open.spotify.com/search/{query.replace(' ', '%20')}"
        webbrowser.open(search_url)
        print(f"[green]Opened Spotify search for: {query}[/green]")
        TextToSpeech(f"searching {query} in Spotify")
        return True
    except Exception as e:
        print(f"[red]Error opening Spotify: {e}[/red]")
        return False

def OpenApp(app_name, sess=requests.session()):
    os_type = platform.system()

    if os_type == "Windows":
        known_apps = {
            "spotify": r"C:\Users\omlap\AppData\Roaming\Spotify\Spotify.exe",
            "chrome": r"C:\Users\Public\Desktop\Google Chrome.lnk",
            "notepad": "notepad.exe"
        }

        try:
            path = known_apps.get(app_name.lower(), app_name)
            os.startfile(path)
            print(f"[green]Opened {app_name}[/green]")
            TextToSpeech(f"Opened {app_name}")
            return True
        except Exception as e:
            print(f"[red]Failed to open {app_name}: {e}[/red]")
            return False

    elif os_type == "Darwin":
        try:
            subprocess.Popen(["open", "-a", app_name])
            return True
        except Exception as e:
            print(f"[red]Failed to open app on macOS: {e}[/red]")
            return False

    else:
        print(f"[yellow]Unsupported OS: {os_type}[/yellow]")
        return False

# Close App (cross-platform)
def CloseApp(app_name):
    os_type = platform.system()
    if os_type == "Windows" and close:
        try:
            close(app_name, match_closest=True, output=True, throw_error=True)
            return True
        except Exception as e:
            print(f"[red]Error closing app: {e}[/red]")
            return False
    elif os_type == "Darwin":
        try:
            subprocess.call(["pkill", "-f", app_name])
            return True
        except Exception as e:
            print(f"[red]Failed to close app on macOS: {e}[/red]")
            return False
    else:
        print(f"[yellow]Unsupported OS: {os_type}[/yellow]")
        return False

# System volume control (Windows only)
def System(command):
    if platform.system() != "Windows":
        print("[yellow]System volume control not supported on this OS[/yellow]")
        return False

    def mute():
        keyboard.press_and_release("volume mute")
        TextToSpeech("Volume muted")
    def unmute():
        keyboard.press_and_release("volume unmute")
        TextToSpeech("Volume unmuted")
    def volume_up():
        keyboard.press_and_release("volume up")
        TextToSpeech("Volume increased")
    def volume_down():
        keyboard.press_and_release("volume down")
        TextToSpeech("Volume decreased")

    actions = {
        "mute": mute,
        "unmute": unmute,
        "volume up": volume_up,
        "volume down": volume_down
    }

    action = actions.get(command)
    if action:
        action()
        return True
    else:
        print("[red]Invalid system command[/red]")
        return False

# Command handler
async def TranslateAndExecute(commands: list[str]):
    funcs = []
    for cmd in commands:
        cmd = cmd.strip().lower()
        if not cmd:
            continue  # Skip blank lines

        if cmd.startswith("open "):
            funcs.append(asyncio.to_thread(OpenApp, cmd.removeprefix("open ")))
        elif cmd.startswith("close "):
            funcs.append(asyncio.to_thread(CloseApp, cmd.removeprefix("close ")))
        elif cmd.startswith("play "):
            funcs.append(asyncio.to_thread(PlayYoutube, cmd.removeprefix("play ")))
        elif cmd.startswith("content "):
            funcs.append(asyncio.to_thread(Content, cmd.removeprefix("content ")))
        elif cmd.startswith("system "):
            funcs.append(asyncio.to_thread(System, cmd.removeprefix("system ")))
        elif cmd.startswith("google search "):
            funcs.append(asyncio.to_thread(GoogleSearch, cmd.removeprefix("google search ")))
        elif cmd.startswith("spotify "):
            funcs.append(asyncio.to_thread(PlaySpotify, cmd.removeprefix("spotify ")))
        elif cmd.startswith("youtube search "):
            funcs.append(asyncio.to_thread(YoutubeSearch, cmd.removeprefix("youtube search ")))
        else:
            print(f"[red]Unknown command: {cmd}[/red]")

    results = await asyncio.gather(*funcs)
    for result in results:
        yield result

# Run automation
async def Automation(commands: list[str]):
    async for _ in TranslateAndExecute(commands):
        pass
    return True

# New perform_task function
async def perform_task(command):
    if isinstance(command, str):
        commands = command.split("\n")
        await Automation(commands)
    else:
        print("[red]Command is not a string[/red]")

if __name__ == "__main__":
    # Example commands
    commands = """
    system volume down
    """
    asyncio.run(perform_task(commands))
