from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from deep_translator import GoogleTranslator
import os

# Initialize translator
translator = GoogleTranslator()

# Set input language
InputLanguage = "en"

# HTML code for speech recognition
HtmlCode = '''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;

        function startRecognition() {
            recognition = new webkitSpeechRecognition() || new SpeechRecognition();
            recognition.lang = '';
            recognition.continuous = true;

            recognition.onresult = function(event) {
                const transcript = event.results[event.results.length - 1][0].transcript;
                output.textContent += transcript;
            };

            recognition.onend = function() {
                recognition.start();
            };
            recognition.start();
        }

        function stopRecognition() {
            recognition.stop();
            output.innerHTML = "";
        }
    </script>
</body>
</html>'''

# Set language correctly in JavaScript
HtmlCode = HtmlCode.replace("recognition.lang = '';", f"recognition.lang = '{InputLanguage}';")

# Create Data folder if it doesn't exist
os.makedirs("Data", exist_ok=True)

# Write HTML file
with open(r"Data\Voice.html", "w", encoding="utf-8") as f:
    f.write(HtmlCode)

# Construct file path
current_dir = os.getcwd()
Link = f"file:///{current_dir.replace(os.sep, '/')}/Data/Voice.html"

# Set Chrome options
chrome_options = Options()
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.142.86 Safari/537.36"
chrome_options.add_argument(f'user-agent={user_agent}')
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--use-fake-device-for-media-stream")
# Do NOT use headless mode for speech recognition
# chrome_options.add_argument("--headless=new")

# Setup ChromeDriver
service = Service(r"C:\Users\omlap\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe")
driver = webdriver.Chrome(service=service, options=chrome_options)

# Temp directory for assistant status
TempDirPath = os.path.join(current_dir, "Frontend", "Files")
os.makedirs(TempDirPath, exist_ok=True)

def SetAssistantStatus(Status):
    with open(os.path.join(TempDirPath, 'Status.data'), "w", encoding="utf-8") as f:
        f.write(Status)

def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = ["how", "what", "who", "when", "why", "which", "whose", "whom", "can you", "what's", "where's", "how's"]
    if any(word in new_query for word in query_words):
        if new_query[-1] not in ['.', '?', '!']:
            new_query += "?"
    return new_query.capitalize()

def UniversalTranslator(Text):
    try:
        result = translator.translate(Text, src='auto', dest='en')
        return result.text.lower()
    except Exception as e:
        return Text.lower()

def SpeechRecognition():
    driver.get(Link)

    # Wait for the start button to appear
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "start")))

    # Click start
    driver.find_element(By.ID, "start").click()

    while True:
        try:
            Text = driver.find_element(By.ID, "output").text
            if Text:
                # Stop recognition
                driver.find_element(By.ID, "end").click()

                # Translate if needed
                if InputLanguage.lower() == "en":
                    return QueryModifier(Text)
                else:
                    SetAssistantStatus("Translating ... ")
                    return QueryModifier(UniversalTranslator(Text))
        except Exception:
            pass

if __name__ == "__main__":
    while True:
        query = SpeechRecognition()
        if query:
            print("Recognized and modified query:", query)
        else:
            print("No input recognized, retrying...")
