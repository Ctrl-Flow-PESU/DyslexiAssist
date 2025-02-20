import speech_recognition as sr

def get_voice_input():
    """
    Gets voice input from the microphone and converts it to text.
    Returns the recognized text in lowercase or None if recognition fails.
    """
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for voice command...")
        try:
            # Adjust for ambient noise
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
        except sr.WaitTimeoutError:
            print("Error: Listening timed out. Please try again.")
            return None
        
    try:
        recognized_text = recognizer.recognize_google(audio)
        print("Recognized:", recognized_text)
        return recognized_text.lower()
    except sr.UnknownValueError:
        print("Error: Could not understand audio")
        return None
    except sr.RequestError as e:
        print(f"Error with speech recognition service: {str(e)}")
        return None
    except Exception as e:
        print(f"Error recognizing voice: {str(e)}")
        return None

def get_level_from_voice(voice_command):
    """
    Extracts the level number from a voice command.
    Returns the level as a string (e.g. "Level 1") or None if no level is found.
    
    Args:
        voice_command (str): The voice command to parse
        
    Returns:
        str|None: The detected level or None if no level found
    """
    if not voice_command:
        return None
        
    voice_command = voice_command.lower()
    
    # Check for various ways to say level numbers
    if any(word in voice_command for word in ["one", "1", "first"]):
        return "Level 1"
    elif any(word in voice_command for word in ["two", "2", "second"]):
        return "Level 2" 
    elif any(word in voice_command for word in ["three", "3", "third"]):
        return "Level 3"
        
    # Check for just numbers
    if "level" in voice_command:
        for num in ["1", "2", "3"]:
            if num in voice_command:
                return f"Level {num}"
                
    return None

def get_command_from_voice(voice_command):
    """
    Extracts command actions from voice input.
    Returns the command type or None if no command is recognized.
    
    Args:
        voice_command (str): The voice command to parse
        
    Returns:
        str|None: The detected command or None if no command found
    """
    if not voice_command:
        return None
        
    voice_command = voice_command.lower()
    
    # Map common command phrases
    command_map = {
        "start": ["start", "begin", "go"],
        "stop": ["stop", "end", "finish"],
        "replay": ["replay", "repeat", "again"],
        "back": ["back", "return", "previous"],
        "help": ["help", "assist", "support"]
    }
    
    for command, phrases in command_map.items():
        if any(phrase in voice_command for phrase in phrases):
            return command
            
    return None 