from dotenv import load_dotenv
import speech_recognition as sr
import webbrowser
import pyttsx3
from pytube import Search
import requests
import google.generativeai as genai
import os
import pyautogui

recognizer = sr.Recognizer()
engine = pyttsx3.init()
engine.setProperty('rate', 215)

# Global variables for API keys
gemini_api_key = None
news_api_key = None

def configure():
    global gemini_api_key, news_api_key
    load_dotenv()
    gemini_api_key = os.getenv('gemini_api_key')
    news_api_key = os.getenv('news_api_key')
    genai.configure(api_key=gemini_api_key)


def speak(text):
    engine.say(text)
    engine.runAndWait()

def play_first_youtube_video(query):
    search = Search(query)
    video_url = f"https://www.youtube.com/watch?v={search.results[0].video_id}"
    webbrowser.open(video_url)

def processCommand(c):
    if "open google" in c.lower():
        webbrowser.open("https://www.google.com/")
    elif "open youtube" in c.lower():
        webbrowser.open("https://www.youtube.com/")
    elif "open facebook" in c.lower():
        webbrowser.open("https://www.facebook.com/")
    elif "open linkedin" in c.lower():
        webbrowser.open("https://www.linkedin.com/")
    elif "open amazon" in c.lower():
        webbrowser.open("https://www.amazon.com/")
    elif "open nepali online shopping site" in c.lower():
        webbrowser.open("https://www.daraz.com.np/")
    elif "open chess.com" in c.lower():
        webbrowser.open("https://www.chess.com/")
    elif "shut up" in c.lower():
        speak("Huss dai sorry")

    elif "play" in c.lower():
        search_query = c.lower().split("play", 1)[1].strip()
        if search_query:
            speak(f"Playing {search_query} on YouTube")
            play_first_youtube_video(search_query)
        else:
            print("Error catching that")

    elif "news" in c.lower():
        try:
            # Fetch international news
            r = requests.get(f"https://newsapi.org/v2/top-headlines?apiKey={news_api_key}&language=en")  # Specify language as English
            r.raise_for_status()  # Check for HTTP errors
            
            data = r.json()  # Parse JSON response
            articles = data.get('articles', [])  # Safely get articles
            
            if articles:  # Check if there are articles
                for i, article in enumerate(articles, 1):
                    print(f"{i}. {article['title']}")
                    speak(f"{i}. {article['title']}")
            else:
                speak("No news articles found.")
        except requests.exceptions.HTTPError:
            speak("An error occurred while fetching news.")
        except requests.exceptions.ConnectionError:
            speak("Connection error occurred. Please check your internet.")
        except requests.exceptions.Timeout:
            speak("Request timed out. Please try again later.")
        except requests.exceptions.RequestException:
            speak("An error occurred with your request.")
        except Exception:
            speak("An unexpected error occurred.")

    elif "pause" in c.lower() or "continue" in c.lower():
        pyautogui.press('space')

    # Let Gemini handle the request
    else:
        try:
            speak(f"Processing the answer for {c}")
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(c)
            print(response.text)
            speak(response.text)
        except Exception as e:
            speak(f"Failed to fetch data: {e}")

if __name__ == "__main__":
    configure()
    speak("Initializing Ramesh...")
    while True:
        # Listen for the wake command
        print("recognizing")

        # recognize speech using Google Speech Recognition
        try:
            with sr.Microphone() as source:
                print("Listening...")
                audio = recognizer.listen(source, timeout=4)
            
            command = recognizer.recognize_google(audio)
            if "ramesh" in command.lower():
                speak("Haw jur")
                # Listen for command
                with sr.Microphone() as source:
                    print("Ramesh Active")
                    audio = recognizer.listen(source)
                    command = recognizer.recognize_google(audio)
                    processCommand(command)

        except Exception as e:
            print("Error: {}".format(e))