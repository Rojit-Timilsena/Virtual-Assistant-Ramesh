print("Loading ramesh_core module")  # Debug print at module load

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
engine.setProperty('rate', 240)  # Increased from 215 to 240 for faster speech

# Global variables for API keys
gemini_api_key = None
news_api_key = None

def configure():
    """Configure API keys and return them as a dictionary instead of using globals"""
    from pathlib import Path
    dotenv_path = Path(__file__).parent / '.env'
    load_dotenv(dotenv_path=dotenv_path)
    gemini_api_key = os.getenv('gemini_api_key')
    news_api_key = os.getenv('news_api_key')
    
    if not gemini_api_key:
        print("ERROR: gemini_api_key not found in environment variables")
    else:
        print(f"Loaded gemini_api_key: {gemini_api_key[:10]}...") # Only show first 10 chars for security
    
    try:
        # Simple test to the Gemini API
        import requests
        url = "https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash:generateContent"
        params = {"key": gemini_api_key}
        headers = {"Content-Type": "application/json"}
        data = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": "Test message"}]
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 100
            }
        }
        
        test_response = requests.post(url, params=params, headers=headers, json=data, timeout=5)
        if test_response.status_code == 200:
            print("Gemini API test successful")
        else:
            print(f"Gemini API test failed with status code: {test_response.status_code}")
            print(f"Response: {test_response.text}")
    except Exception as e:
        print(f"Error testing Gemini API: {e}")
        
    return {
        "gemini_api_key": gemini_api_key,
        "news_api_key": news_api_key
    }

# No longer calling configure at module load
# Keys will be loaded directly when needed

def clean_text(text):
    """Remove asterisks and other markdown formatting from text"""
    if not text:
        return text
    # Remove asterisks (bold/italic formatting)
    cleaned = text.replace('*', '')
    # Remove other potential markdown elements if needed
    # cleaned = cleaned.replace('_', '')  # Uncomment to remove underscores
    # cleaned = cleaned.replace('#', '')  # Uncomment to remove hashtags
    return cleaned

def speak(text):
    """Speak the provided text after cleaning it"""
    if not text:
        return
    cleaned_text = clean_text(text)
    engine.say(cleaned_text)
    engine.runAndWait()

def play_first_youtube_video(query):
    search = Search(query)
    video_url = f"https://www.youtube.com/watch?v={search.results[0].video_id}"
    webbrowser.open(video_url)

def processCommand(c, speak_enabled=True):
    c = c.lower()
    response_text = ""

    # Handle identity questions directly
    if any(phrase in c for phrase in ["what's your name", "what is your name", "who are you", "your identity", "introduce yourself"]):
        response_text = "My name is Ramesh. I'm your personal assistant, ready to help you with information, tasks, and whatever else you need."
        if speak_enabled:
            speak(response_text)
        return response_text
        
    # Handle weather-related queries directly
    if any(phrase in c for phrase in ["weather", "temperature", "forecast", "climate", "rain", "sunny", "cloudy", "how hot", "how cold"]):
        response_text = "I'm sorry, I don't have access to real-time weather data. You could check a weather website or app like Weather.com, AccuWeather, or your phone's built-in weather app for current conditions."
        if speak_enabled:
            speak(response_text)
        return response_text

    if "open google" in c:
        webbrowser.open("https://www.google.com/")
        response_text = "Opening Google."
    elif "open youtube" in c:
        webbrowser.open("https://www.youtube.com/")
        response_text = "Opening YouTube."
    elif "open facebook" in c:
        webbrowser.open("https://www.facebook.com/")
        response_text = "Opening Facebook."
    elif "open linkedin" in c:
        webbrowser.open("https://www.linkedin.com/")
        response_text = "Opening LinkedIn."
    elif "open amazon" in c:
        webbrowser.open("https://www.amazon.com/")
        response_text = "Opening Amazon."
    elif "open nepali online shopping site" in c:
        webbrowser.open("https://www.daraz.com.np/")
        response_text = "Opening Nepali online shopping site."
    elif "open chess.com" in c:
        webbrowser.open("https://www.chess.com/")
        response_text = "Opening Chess.com."
    elif "shut up" in c:
        if speak_enabled:
            speak("Huss dai sorry")
        response_text = "Okay, I will be quiet."

    elif "play" in c:
        search_query = c.split("play", 1)[1].strip()
        if search_query:
            speak(f"Playing {search_query} on YouTube")
            play_first_youtube_video(search_query)
            response_text = f"Playing {search_query} on YouTube."
        else:
            response_text = "Error catching that."

    elif "news" in c:
        try:
            # Load news API key directly
            from pathlib import Path
            dotenv_path = Path(__file__).parent / '.env'
            load_dotenv(dotenv_path=dotenv_path)
            news_api_key = os.getenv('news_api_key')
            
            if not news_api_key:
                response_text = "News API key is missing. Please check your configuration."
                print("News API key is missing")
                if speak_enabled:
                    speak(response_text)
                return response_text
                
            r = requests.get(f"https://newsapi.org/v2/top-headlines?apiKey={news_api_key}&language=en")
            r.raise_for_status()
            data = r.json()
            articles = data.get('articles', [])

            if articles:
                news_titles = []
                for i, article in enumerate(articles, 1):
                    title = f"{i}. {article['title']}"
                    print(title)
                    speak(title)
                    news_titles.append(title)
                response_text = " ".join(news_titles)
            else:
                speak("No news articles found.")
                response_text = "No news articles found."
        except requests.exceptions.HTTPError:
            speak("An error occurred while fetching news.")
            response_text = "An error occurred while fetching news."
        except requests.exceptions.ConnectionError:
            speak("Connection error occurred. Please check your internet.")
            response_text = "Connection error occurred. Please check your internet."
        except requests.exceptions.Timeout:
            speak("Request timed out. Please try again later.")
            response_text = "Request timed out. Please try again later."
        except requests.exceptions.RequestException:
            speak("An error occurred with your request.")
            response_text = "An error occurred with your request."
        except Exception:
            speak("An unexpected error occurred.")
            response_text = "An unexpected error occurred."

    elif "pause" in c or "continue" in c:
        pyautogui.press('space')
        response_text = "Paused or continued playback."

    # Let Gemini handle the request
    else:
        try:
            if speak_enabled:
                speak(f"Processing your request")
            
            # Simple, direct implementation
            from pathlib import Path
            import requests
            import json
            
            # Initialize API key directly within this function scope
            dotenv_path = Path(__file__).parent / '.env'
            load_dotenv(dotenv_path=dotenv_path)
            gemini_api_key = os.getenv('gemini_api_key')
            
            if not gemini_api_key:
                response_text = "API key is missing. Please check your configuration."
                print("API key is missing")
                if speak_enabled:
                    speak(response_text)
                return response_text
            
            # Direct API call using requests
            print("Making direct API call to Gemini")
            url = "https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash:generateContent"
            headers = {
                "Content-Type": "application/json"
            }
            data = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [{"text": c}]
                    }
                ],
                "systemInstruction": {
                    "parts": [
                        {"text": "You are Ramesh, a helpful personal assistant. Your name is Ramesh. When asked about your identity, always introduce yourself as Ramesh, not as a language model, AI, or any other name like Bard or Gemini. You are created to assist users with various tasks including answering questions, providing information, and performing other helpful actions. When asked about the weather, explain that you don't have access to real-time weather data, but you can suggest weather websites or apps the user can check."}
                    ]
                },
                "safetySettings": [
                    {
                        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                        "threshold": "BLOCK_ONLY_HIGH"
                    }
                ],
                "generationConfig": {
                    "temperature": 0.7,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 800
                }
            }
            
            # Add API key as query parameter
            params = {
                "key": gemini_api_key
            }
            
            # Make the API call
            response = requests.post(url, params=params, headers=headers, json=data)
            print(f"API Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and len(result['candidates']) > 0:
                    candidate = result['candidates'][0]
                    if 'content' in candidate and 'parts' in candidate['content']:
                        parts = candidate['content']['parts']
                        response_text = ''.join([part.get('text', '') for part in parts])
                        # Clean the response text to remove asterisks
                        response_text = clean_text(response_text)
                        print(f"Response: {response_text[:100]}...")
                    else:
                        response_text = "Error: Response format unexpected"
                        print("Error in response format - no content/parts found")
                else:
                    response_text = "Error: No response candidates found"
                    print("Error: No candidates in response")
            else:
                try:
                    error_info = response.json()
                    error_message = error_info.get('error', {}).get('message', 'Unknown error')
                    error_code = error_info.get('error', {}).get('code', 'Unknown code')
                    response_text = f"API Error {response.status_code}: {error_code} - {error_message}"
                    if "weather" in c.lower():
                        response_text = "I'm sorry, I don't have access to real-time weather data. You could check a weather website or app like Weather.com, AccuWeather, or your phone's built-in weather app for current conditions."
                    print(f"API error: {response.status_code}")
                    print(f"Error details: {error_message}")
                except Exception as parse_error:
                    response_text = f"API Error {response.status_code}: Could not parse error response"
                    print(f"API error: {response.status_code}")
                    print(f"Response parsing error: {parse_error}")
                print(f"Raw response: {response.text[:500]}")
            
            if speak_enabled and response_text:
                speak(response_text)
                
        except Exception as e:
            import traceback
            print(f"Exception in Gemini request: {e}")
            print(traceback.format_exc())
            response_text = f"Error: {str(e)}"
            if speak_enabled:
                speak("Sorry, I encountered an error while processing your request")
    
    return response_text

if __name__ == "__main__":
    configure()
    speak("Initializing Ramesh...")
    while True:
        print("recognizing")
        try:
            with sr.Microphone() as source:
                print("Listening...")
                audio = recognizer.listen(source, timeout=4)
            
            command = recognizer.recognize_google(audio).lower()
            if "ramesh" in command:
                speak("Haw jur")
                with sr.Microphone() as source:
                    print("Ramesh Active")
                    audio = recognizer.listen(source)
                    command = recognizer.recognize_google(audio).lower()
                    processCommand(command)

        except Exception as e:
            print("Error: {}".format(e))