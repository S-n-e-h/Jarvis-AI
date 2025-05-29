import pygame
import random

# Import pygame library for handling audio playback
# Import random for generating random choices
import asyncio
import edge_tts # Import edge_tts for text-to-speech functionality
import os # Import os for file path handling
from dotenv import dotenv_values # Import dotenv for reading environment variables from a .env file

# Load environment variables from a .env file
env_vars = dotenv_values(".env")
AssistantVoice = "en-US-GuyNeural"
 # Get the AssistantVoice from the environment variables

# Asynchronous function to convert text to an audio file
async def TextToAudioFile(text) -> None:
    file_path = r"Data\speech.mp3" # Define the path where the speech file will be saved

    if os.path.exists(file_path): # Check if the file already exists
        os. remove(file_path) # If it exists, remove it to avoid overwriting errors

    # Create the communicate object to generate speech
    communicate = edge_tts. Communicate(text, AssistantVoice, pitch='+5Hz', rate='+13%' )
    await communicate.save(r'Data\speech.mp3')
# Function to manage Text-to-Speech (TTS) functionality
import pygame
import asyncio

def TTS(Text, func=lambda r=None: True):
    try:
        # Run your async function to generate speech file
        asyncio.run(TextToAudioFile(Text))
        
        # Initialize pygame once
        pygame.init()
        pygame.mixer.init()

        # Load and play the speech audio
        pygame.mixer.music.load(r"Data\speech.mp3")
        pygame.mixer.music.play()

        # Wait while audio is playing and func() returns True
        clock = pygame.time.Clock()
        while pygame.mixer.music.get_busy():
            if func() == False:
                break
            clock.tick(10)  # limit to 10 FPS

        return True  # Played successfully or interrupted by func()

    except Exception as e:
        print(f"Error in TTS: {e}")
        return False

    finally:
        try:
            func(False)  # signal end of TTS
            pygame.mixer.music.stop()
            pygame.mixer.quit()
        except Exception as e:
            print(f"Error in finally block: {e}")

def TextToSpeech(Text, func=lambda r=None: True):
    Data = str(Text). split(".") # Split the text by periods into a list of sentences

    # List of predefined responses for cases where the text is too long
    responses = [
        "The rest of the result has been printed to the chat screen, kindly check it out sir.",
        "The rest of the text is now on the chat screen, sir, please check it.",
        "You can see the rest of the text on the chat screen, sir.",
        "The remaining part of the text is now on the chat screen, sir.",
        "Sir, you'll find more text on the chat screen for you to see.",
        "The rest of the answer is now on the chat screen, sir.",
        "Sir, please look at the chat screen, the rest of the answer is there.",
        "You'll find the complete answer on the chat screen, sir.",
        "The next part of the text is on the chat screen, sir.",
        "Sir, please check the chat screen for more information.",
        "There's more text on the chat screen for you, sir.",
        "Sir, take a look at the chat screen for additional text.",
        "You'll find more to read on the chat screen, sir.",
        "Sir, check the chat screen for the rest of the text.",
        "The chat screen has the rest of the text, sir.",
        "There's more to see on the chat screen, sir, please look.",
        "Sir, the chat screen holds the continuation of the text.",
        "You'll find the complete answer on the chat screen, kindly check it out sir.",
        "Please review the chat screen for the rest of the text, sir.",
        "Sir, look at the chat screen for the complete answer."
    ]
    # If the text is very long (more than 4 sentences and 250 characters), add a response message
    if len(Data) > 4 and len(Text) >= 250:
        TTS(" ".join(Text.split(".")[0:2]) + ". " + random.choice(responses), func)

    # Otherwise, just play the whole text
    else:
        TTS(Text, func)
# if __name__ == "__main__":
#     while True:
#     # Prompt user for input and pass it to TextToSpeech function
#         TextToSpeech(input("Enter the text: "))
