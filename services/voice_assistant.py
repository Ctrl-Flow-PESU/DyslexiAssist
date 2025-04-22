import speech_recognition as sr
import pyttsx3
import threading
from queue import Queue
import time

class VoiceAssistant:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.recognizer = sr.Recognizer()
        self.is_listening = False
        self.command_queue = Queue()
        self.speaking = False
        self.commands = {
            "menu": {"main menu", "go back", "home"},
            "reading_test": {"reading test", "start reading", "practice reading"},
            "dictation": {"dictation test", "start dictation", "practice writing", "dictation"},
            "contrast": {"contrast test", "change colors", "test contrast", "contrast"},
            "help": {"help", "what can you do", "commands"},
            "read_aloud": {"read aloud", "read this", "read text"},
            "scroll": {"scroll down", "scroll up"},
            "click": {"click", "select", "choose"},
            "open_text_file": {"text file", "open text", "open file"}
        }

    def start_listening(self):
        """Start listening for voice commands in a separate thread"""
        self.is_listening = True
        threading.Thread(target=self._listen_loop, daemon=True).start()

    def stop_listening(self):
        """Stop listening for voice commands"""
        self.is_listening = False

    def speak(self, text):
        """Speak the given text"""
        if self.speaking:
            return
        
        def speak_thread():
            self.speaking = True
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            finally:
                self.speaking = False

        threading.Thread(target=speak_thread, daemon=True).start()

    def _listen_loop(self):
        """Continuous listening loop for voice commands"""
        while self.is_listening:
            if self.speaking:
                time.sleep(0.1)
                continue
                
            try:
                with sr.Microphone() as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    print("Listening...")  # Debug print
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                    
                    try:
                        text = self.recognizer.recognize_google(audio).lower()
                        print(f"Recognized: {text}")  # Debug print
                        self._process_command(text)
                    except sr.UnknownValueError:
                        pass  # Ignore unrecognized speech
                    except sr.RequestError as e:
                        print(f"Could not request results; {e}")
                        
            except sr.WaitTimeoutError:
                continue
            except Exception as e:
                print(f"Error in voice recognition: {e}")
                time.sleep(1)  # Prevent rapid retries on error

    def _process_command(self, text):
        """Process the recognized voice command"""
        if not text:
            return
            
        print(f"Processing text: {text}")  # Debug print
        command = None
        
        # Check each command category
        for cmd_type, phrases in self.commands.items():
            if any(phrase in text for phrase in phrases):
                command = cmd_type
                print(f"Matched command: {cmd_type}")  # Debug print
                break

        if command:
            try:
                self.command_queue.put_nowait(command)
                print(f"Command queued: {command}")  # Debug print
            except Exception as e:
                print(f"Error queuing command: {e}")

    def get_command(self):
        """Get the next command from the queue if available"""
        try:
            if not self.command_queue.empty():
                return self.command_queue.get_nowait()
        except Exception as e:
            print(f"Error getting command: {e}")
        return None

    def provide_help(self):
        """Speak available commands and their descriptions"""
        help_text = """
        Available commands:
        Say 'main menu' to return to the main menu
        Say 'reading test' to start a reading exercise
        Say 'dictation test' to practice writing
        Say 'contrast test' to adjust colors
        Say 'read aloud' to have text read to you
        Say 'scroll up' or 'scroll down' to navigate
        Say 'help' to hear these commands again
        """
        self.speak(help_text)