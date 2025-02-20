import requests
import google.generativeai as genai
import threading
import pyttsx3

class DyslexiaAssistant:
    def __init__(self, api_key: str):
        self.gemini_api_key = api_key
        genai.configure(api_key=self.gemini_api_key)
        try:
            self.model = genai.GenerativeModel('gemini-pro')
        except Exception as e:
            print(f"Warning: Gemini model initialization failed: {e}")
            self.model = None
        try:
            self.tts_engine = pyttsx3.init()
        except Exception as e:
            print(f"Warning: Text-to-speech initialization failed: {e}")
            self.tts_engine = None

    def correct_with_languagetool(self, text: str):
        url = "https://api.languagetool.org/v2/check"
        params = {"text": text, "language": "en-US"}
        try:
            response = requests.post(url, data=params, timeout=10)
            response.raise_for_status()
            result = response.json()
            corrected_text = text
            errors = []
            matches = result.get("matches", [])
            matches.sort(key=lambda m: m.get("offset", 0), reverse=True)
            for match in matches:
                offset = match.get("offset", 0)
                length = match.get("length", 0)
                original_word = corrected_text[offset:offset + length]
                suggestions = [s.get("value", "") for s in match.get("replacements", [])]
                if suggestions:
                    best_suggestion = suggestions[0]
                    corrected_text = (corrected_text[:offset] +
                                    best_suggestion +
                                    corrected_text[offset + length:])
                    errors.append((original_word, best_suggestion))
            return errors, corrected_text
        except requests.exceptions.RequestException as e:
            print(f"LanguageTool API error: {e}")
            return [], text

    def correct_with_gemini(self, text: str):
        prompt = f"""
        Please correct the following text, focusing on spelling errors, phonetic mistakes, 
        letter reversals, and missing letters while preserving the original meaning:

        "{text}"

        Provide only the corrected text without any additional comments.
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Gemini API error: {e}")
            return text

    def process_text(self, text: str):
        errors, lt_corrected = self.correct_with_languagetool(text)
        gemini_corrected = self.correct_with_gemini(lt_corrected)
        results = {
            "original_text": text,
            "detected_errors": errors,
            "languagetool_correction": lt_corrected,
            "final_correction": gemini_corrected
        }
        return results

    def text_to_speech(self, text: str, rate=150, blocking=True):
        if self.tts_engine:
            self.tts_engine.setProperty("rate", rate)
            if blocking:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            else:
                threading.Thread(target=self._speak, args=(text, rate)).start()

    def _speak(self, text, rate):
        self.tts_engine.setProperty("rate", rate)
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()