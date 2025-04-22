import pyttsx3
import threading

class TextReader:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", 150)
        self.is_paused = False
        self.current_text = ""
        self.current_position = 0
        self.lock = threading.Lock()

    def read_text(self, text, rate=150):
        self.engine.setProperty('rate', rate)
        self.engine.say(text)
        self.engine.runAndWait()

    def pause(self):
        self.engine.stop()

    def resume(self):
        with self.lock:
            if self.is_paused:
                self.is_paused = False
                self._speak_from_position() 

    def _speak_from_position(self):
        """
        Internal method to handle speech from the current position.
        """
        with self.lock:
            text_to_speak = self.current_text[self.current_position:]
            self.engine.say(text_to_speak)
            self.engine.runAndWait() 