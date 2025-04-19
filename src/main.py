import pygame
import sys
import os
import speech_recognition as sr  # Import the speech recognition library
import pyttsx3  # Import the text-to-speech library
import json
import google.generativeai as genai
from services.voice_assistant import VoiceAssistant

from ui.components import Slider, TextBox, draw_button
from ui.text_utils import wrap_text
from services.text_reader import TextReader
from services.image_recognition import detect_document
from assistant import DyslexiaAssistant
from services.contrast_tester import ContrastTester
import tkinter as tk
from tkinter import filedialog
import threading

# Define colors as global variables
BACKGROUND_COLOR = (245, 245, 220)  # Beige
BUTTON_COLOR = (135, 206, 250)      # Light sky blue
DARK_BUTTON_COLOR = (70, 130, 180)  # Steel blue
BACK_BUTTON_COLOR = (100, 149, 237) # Cornflower blue
TEXT_COLOR = (0, 0, 0)              # Black
WHITE = (255, 255, 255)             # White
VOICE_INDICATOR_COLOR = (0, 255, 0)  # Green

genai.configure(api_key="AIzaSyCtuJn4GVM2Ysfu9aUJiRnffVGEOet1Zjc")  # Replace with your API key
model = genai.GenerativeModel('gemini-2.0-flash')  # Changed from gemini-2.0-flash

def dictate_text_to_student(text, speed):
    """
    Uses Gemini API to process the text for better pronunciation and then uses TTS to read it. Any other APIs can be used, Gemini was found to give more accurate
    solutions in this situation.
    """
    try:        
        engine = TextReader
        engine.read_text(text, speed)

    except Exception as e:
        print(f"Error in Gemini text processing: {e}")
        # Fallback to basic TTS if AI fails
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()

def check_accuracy(user_input, expected_text):
    """
    Checks the accuracy of user input against expected text, including spelling and grammar using Google's Gemini API.
    Returns a tuple of (is_correct, feedback_message)
    """
    # Basic exact match check
    if user_input.strip().lower() == expected_text.strip().lower():
        return True, "Perfect match! Well done!"
    
    # Construct prompt for analysis
    prompt = f"""You are a JSON-only response API. Analyze these texts and respond with ONLY valid JSON:
    Expected text: "{expected_text}"
    User input: "{user_input}"
    
    Format: {{"is_correct": boolean, "feedback": "analysis of spelling, grammar, and word differences"}}"""
    
    # Get AI analysis
    response = model.generate_content(prompt)
    response_text = response.text.strip()
    
    # Clean the response to ensure it's valid JSON
    response_text = response_text.replace("```json", "").replace("```", "").strip()
    
    try:
        result = json.loads(response_text)
        return result["is_correct"], result["feedback"]
    except json.JSONDecodeError:
        return False, f"Comparison failed. Expected: '{expected_text}', Got: '{user_input}'"

def upload_image():
    # Use tkinter for file dialog
    
    # Create and hide root window
    root = tk.Tk()
    root.withdraw()
    
    # Open file dialog for image selection
    file_path = filedialog.askopenfilename(
        title="Select Image File",
        filetypes=[
            ("Image files", "*.png *.jpg *.jpeg *.bmp"),
            ("All files", "*.*")
        ]
    )
    
    # Initialize selected flag
    selected = False if not file_path else True
    if selected:
        return file_path
    return False

def open_text_file():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if file_path:
        return file_path
    return None

def draw_back_button(screen, button_font, button_width, button_height):
    """Draw a consistent back button for all states"""
    back_button = pygame.Rect(50, 30, button_width//4, button_height//2)
    
    # Check if mouse is hovering over the button
    mouse_pos = pygame.mouse.get_pos()
    is_hovered = back_button.collidepoint(mouse_pos)
    
    # Use darker color when hovered
    button_color = (80, 129, 217) if is_hovered else BACK_BUTTON_COLOR  # Darker shade when hovered
    text_color = WHITE
    
    draw_button(screen, back_button, "Back", button_font, 
                button_color, text_color, border_radius=5)
    return back_button  # Return the rect for click detection

def generate_dictation_text():
    """Generate a new random text for dictation test"""
    try:        
        prompt = """Generate a single short 1 line text suitable for testing dyslexic person's listening and writing ability. 
        The text should be simple, clear, and use common words. Don't include any special characters or numbers or anything else, just the text."""
        
        response = model.generate_content(prompt)
        return response.text if response.text else "The cat sat on the mat. It was a sunny day. The birds flew in the sky."
    except Exception as e:
        print(f"Error generating dictation text: {e}")
        return "The cat sat on the mat. It was a sunny day. The birds flew in the sky."

def generate_reading_texts():
        try:            
            reading_texts = {}
            
            # Generate texts for each level
            for level in range(1, 4):
                prompt = f"""Generate a small reading passage (maximum 6 lines) for level {level} dyslexic readers.
                Level 1 should be very simple sentences.
                Level 2 should be medium difficulty with compound sentences.
                Level 3 should be more complex sentences.
                Keep the text natural and engaging.
                Return ONLY the text passage(No, formatting required, just the text.). Generate only level {level} text."""
                
                response = model.generate_content(prompt)
                reading_texts[f"Level {level}"] = [{"text": response.text.strip()}]
                
            return reading_texts
        except Exception as e:
            print(f"Error generating reading texts: {e}")
            # Fallback texts if generation fails
            return {
                "Level 1": [{"text": "The cat sat on the mat. It was a sunny day. The birds flew in the sky."}],
                "Level 2": [{"text": "Sarah loved to read books. She would visit the library on weekends. Her favorite books were about adventures."}], 
                "Level 3": [{"text": "The quick brown fox jumps over the lazy dog. A skilled reader can understand complex sentences."}]
            }

reading_texts = generate_reading_texts()        
voice_assistant = VoiceAssistant()
voice_assistant.start_listening()
voice_assistant.speak("Welcome to Dyslexia Assistant. Say 'help' for available commands.")

def main():
    global BACKGROUND_COLOR, TEXT_COLOR
    pygame.init()
    
    # Add scroll_y initialization here
    scroll_y = 0  # Initialize scroll position
    
    # Get the display info to set appropriate window size
    display_info = pygame.display.Info()
    # Use 80% of screen height and maintain 16:9 aspect ratio
    window_height = int(display_info.current_h * 0.8)
    window_width = int(window_height * 16/9)
    
    # Ensure minimum size
    window_width = max(1280, window_width)
    window_height = max(720, window_height)
    
    # Center the window on screen
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    
    screen = pygame.display.set_mode((window_width, window_height))
    pygame.display.set_caption("Dyslexia Assistant")
    clock = pygame.time.Clock()

    # Adjust UI component positions based on new window size
    slider_width = int(window_width * 0.15)  # 15% of window width
    voice_speed_slider = Slider(int(window_width * 0.05), window_height - 60, slider_width, 10, 200, 150, "Voice Speed")
    text_size_slider = Slider(int(window_width * 0.25), window_height - 60, slider_width, 18, 36, 18, "Text Size")

    # Update menu layout calculations
    menu_start_y = int(window_height * 0.15)  # Start menu 15% from top
    menu_spacing = int(window_height * 0.25)  # Increase space between menu items
    button_width = int(window_width * 0.5)     # Buttons take 50% of width
    button_height = int(window_height * 0.12)   # Button height proportional to window

    # Create UI components
    slider_font = pygame.font.SysFont("Arial", 18)
    textbox_font = pygame.font.SysFont("Arial", int(text_size_slider.get_value()))
    text_box = TextBox(100, 500, window_width - 200, 100, textbox_font)

    # Initialize services
    reader = TextReader()
    assistant = DyslexiaAssistant("AIzaSyA1VgJaj0VW6E9tV5cITXGxmBRUPDLEddc")

    # Initialize services
    reader = TextReader()
    assistant = DyslexiaAssistant("AIzaSyA1VgJaj0VW6E9tV5cITXGxmBRUPDLEddc")

    # Application state and options
    state = "menu"
    main_options = [
        {"name": "Reading Test", "suboptions": [
            "Level 1",
            "Level 2",
            "Level 3"
        ]},
        {"name":"Reading Tools",
        "suboptions":[
            "Contrast Test",
            "Open Text File"
        ]},
        {"name": "Writing Tools", "suboptions": [
            "Dictation Test",
            "Notes Proofreading"
        ]}
    ]

    # Menu state tracking
    active_menu = None
    
    # UI spacing and dimensions
    PADDING = int(window_height * 0.02)  # 2% of window height
    TITLE_MARGIN = int(window_height * 0.08)  # 8% from top
    MENU_START = int(window_height * 0.2)  # 20% from top
    MENU_SPACING = int(window_height * 0.25)  # Increased spacing between items
    SUBMENU_SPACING = int(window_height * 0.02)  # 2% spacing for submenu
    
    # Button dimensions
    MAIN_BUTTON_WIDTH = int(window_width * 0.6)  # 60% of window width
    MAIN_BUTTON_HEIGHT = int(window_height * 0.1)  # 10% of window height
    SUB_BUTTON_HEIGHT = int(window_height * 0.06)  # 6% of window height

    # Initialize state variables
    correction_result = None
    textbox_font = pygame.font.SysFont("Arial", int(text_size_slider.get_value()))
    text_box = TextBox(100, 500, window_width - 200, 100, textbox_font)

    # Reading test content
    # Generate reading texts using Gemini
            
    # reading_texts = generate_reading_texts()

    # Add contrast tester
    contrast_tester = ContrastTester(window_width, window_height)

    # Game loop
    while True:
        # Update font sizes based on slider
        base_size = int(text_size_slider.get_value())
        try:
            dyslexic_font_path = r".\opendyslexic-0.91.12\opendyslexic-0.91.12\compiled\OpenDyslexic-Regular.otf"
            title_font = pygame.font.Font(dyslexic_font_path, base_size + 16)
            button_font = pygame.font.Font(dyslexic_font_path, base_size + 8)
            text_font = pygame.font.Font(dyslexic_font_path, base_size)
        except Exception:
            title_font = pygame.font.SysFont("Arial", base_size + 16)
            button_font = pygame.font.SysFont("Arial", base_size + 8)
            text_font = pygame.font.SysFont("Arial", base_size)

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                voice_assistant.stop_listening()
                pygame.quit()
                sys.exit()

            voice_speed_slider.handle_event(event)
            text_size_slider.handle_event(event)
            
            if state == "dictation_test":
                text_box.handle_event(event)

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                
                if state != "menu":
                    # Handle back button for all states except menu
                    back_button = draw_back_button(screen, button_font, button_width, button_height)
                    if back_button.collidepoint(mouse_pos):
                        state = "menu"
                        active_menu = None
                        if hasattr(text_box, 'expected_text'):
                            delattr(text_box, 'expected_text')  # Clear the stored text when leaving
                        continue

                if state == "menu":
                    # Handle main menu clicks
                    for i, option in enumerate(main_options):
                        main_rect = pygame.Rect(
                            (window_width - MAIN_BUTTON_WIDTH) // 2,
                            MENU_START + (i * MENU_SPACING),
                            MAIN_BUTTON_WIDTH,
                            MAIN_BUTTON_HEIGHT
                        )
                        
                        if main_rect.collidepoint(mouse_pos):
                            active_menu = i if active_menu != i else None
                            break
                    
                    # Handle submenu clicks
                    if active_menu is not None:
                        option = main_options[active_menu]
                        sub_width = MAIN_BUTTON_WIDTH // len(option['suboptions'])
                        sub_y = MENU_START + (active_menu * MENU_SPACING) + MAIN_BUTTON_HEIGHT + SUBMENU_SPACING
                        x = (window_width - MAIN_BUTTON_WIDTH) // 2
                        
                        for j, suboption in enumerate(option['suboptions']):
                            sub_rect = pygame.Rect(
                                x + (j * sub_width),
                                sub_y,
                                sub_width - PADDING,
                                SUB_BUTTON_HEIGHT
                            )
                            
                            if sub_rect.collidepoint(mouse_pos):
                                state = suboption.lower().replace(" ", "_")
                                if suboption == "Open Text File":
                                    state = "open_text_file"
                                break

                elif state in ["level_1", "level_2", "level_3"]:
                    # Handle read aloud button click
                    read_button = pygame.Rect(
                        (window_width - button_width)//2,
                        container_rect.bottom + 20,
                        button_width//2,
                        button_height//2
                    )
                    
                    if read_button.collidepoint(mouse_pos):
                        level_num = state.split("_")[1]
                        current_text = reading_texts[f"Level {level_num}"][0]
                        reader.read_text(current_text["text"], rate=int(voice_speed_slider.get_value()))

                elif state == "dictation_test":
                    # Generate new text when entering the state
                    if not hasattr(text_box, 'expected_text'):
                        text_box.expected_text = generate_dictation_text()
                        text_box.show_results = False
                        text_box.text = ""  # Clear previous input

                    # Draw title
                    title_text = title_font.render("Dictation Test", True, TEXT_COLOR)
                    title_rect = title_text.get_rect(center=(window_width//2, TITLE_MARGIN))
                    screen.blit(title_text, title_rect)
                    
                    # Move buttons higher up
                    button_y = int(window_height * 0.2)
                    button_width = 120
                    button_spacing = 40
                    total_width = (button_width * 2) + button_spacing
                    start_x = window_width // 2 - (total_width // 2)
                    
                    # Create button rectangles
                    dictate_button = pygame.Rect(start_x, button_y, button_width, button_height//2)
                    check_button = pygame.Rect(start_x + button_width + button_spacing, button_y, button_width, button_height//2)
                    
                    # Draw buttons
                    draw_button(screen, dictate_button, "Dictate", button_font, 
                                DARK_BUTTON_COLOR, WHITE, border_radius=5)
                    draw_button(screen, check_button, "Check", button_font, 
                                DARK_BUTTON_COLOR, WHITE, border_radius=5)
                    
                    # Handle button clicks in a way that doesn't interfere with typing
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if dictate_button.collidepoint(event.pos):
                            # Use text-to-speech in a non-blocking way
                            threading.Thread(target=reader.read_text, 
                                           args=(text_box.expected_text, int(voice_speed_slider.get_value()))).start()
                        elif check_button.collidepoint(event.pos):
                            # Check accuracy when check button is clicked
                            is_correct, feedback = check_accuracy(text_box.text, text_box.expected_text)
                            text_box.show_results = True
                            text_box.result_text = feedback
                    
                    # Move text box higher (position it closer to the buttons)
                    text_box_y = button_y + button_height//2 + 20  # 20px gap after buttons
                    text_box.rect.y = text_box_y
                    text_box.draw(screen)

                elif state == "notes_proofreading":
                    upload_button = pygame.Rect((window_width - button_width)//2, menu_start_y + menu_spacing, 
                                             button_width//2, button_height//2)
                    draw_button(screen, upload_button, "Upload Image", button_font, DARK_BUTTON_COLOR, WHITE)
                    if upload_button.collidepoint(mouse_pos):
                        file_path = upload_image()
                        if file_path:
                            try:
                                extracted_text = detect_document(file_path)
                                if extracted_text:
                                    correction_result = assistant.process_text(extracted_text)
                                    text_box.text = correction_result["final_correction"]
                            except Exception as e:
                                print(f"Error processing image: {e}")

                elif state == "open_text_file":
                    screen.fill(BACKGROUND_COLOR)

                    # Draw title
                    title_text = title_font.render("Open Text File", True, TEXT_COLOR)
                    title_rect = title_text.get_rect(center=(window_width//2, TITLE_MARGIN))
                    screen.blit(title_text, title_rect)

                    # Add "Open File" button
                    open_file_button = pygame.Rect(window_width//2 - 100, window_height//2 - 25, 200, 50)
                    draw_button(screen, open_file_button, "Open File", button_font, 
                                DARK_BUTTON_COLOR, WHITE, border_radius=5)

                    # Handle button click
                    if event.type == pygame.MOUSEBUTTONDOWN and open_file_button.collidepoint(event.pos):
                        file_path = open_text_file()
                        if file_path:
                            with open(file_path, 'r', encoding='utf-8') as file:
                                opened_text = file.read()
                            state = "display_text"
                            scroll_y = 0  # Reset scroll position

                    # If text is already opened, display it
                    if 'opened_text' in locals():
                        state = "display_text"
                        scroll_y = 0  # Reset scroll position

                elif state == "display_text":
                    screen.fill(BACKGROUND_COLOR)

                    # Draw title
                    title_text = title_font.render("Opened Text", True, TEXT_COLOR)
                    title_rect = title_text.get_rect(center=(window_width//2, TITLE_MARGIN))
                    screen.blit(title_text, title_rect)

                    # Calculate text area dimensions
                    text_area_width = int(window_width * 0.8)
                    text_area_height = int(window_height * 0.6)

                    # Wrap and display text
                    wrapped_lines = wrap_text(opened_text, text_font, text_area_width)
                    line_height = int(text_font.get_height() * 1.5)

                    # Create scrollable text container
                    text_container = pygame.Surface((text_area_width, len(wrapped_lines) * line_height))
                    text_container.fill(BACKGROUND_COLOR)

                    for i, line in enumerate(wrapped_lines):
                        text_surface = text_font.render(line, True, TEXT_COLOR)
                        text_rect = text_surface.get_rect(x=0, y=i * line_height)
                        text_container.blit(text_surface, text_rect)

                    # Display text with scrolling
                    container_rect = pygame.Rect((window_width - text_area_width) // 2, TITLE_MARGIN + 50, 
                                                text_area_width, text_area_height)
                    screen.blit(text_container, container_rect, 
                                (0, scroll_y, text_area_width, text_area_height))

                    # Draw scroll bar
                    scroll_bar_height = min(text_area_height, 
                                            text_area_height * (text_area_height / text_container.get_height()))
                    scroll_bar_pos = (scroll_y / (text_container.get_height() - text_area_height)) * (text_area_height - scroll_bar_height)
                    scroll_bar_rect = pygame.Rect(container_rect.right + 10, container_rect.top + scroll_bar_pos, 
                                                10, scroll_bar_height)
                    pygame.draw.rect(screen, DARK_BUTTON_COLOR, scroll_bar_rect)

                    # Handle scrolling
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 4:  # Scroll up
                            scroll_y = max(scroll_y - 30, 0)
                        elif event.button == 5:  # Scroll down
                            scroll_y = min(scroll_y + 30, text_container.get_height() - text_area_height)

                elif state == "contrast_test":
                    # Center everything
                    center_x = window_width // 2
                    center_y = window_height // 2
                    
                    if not contrast_tester.test_started:
                        # Draw title and instructions
                        title_text = title_font.render("Contrast Test", True, TEXT_COLOR)
                        title_rect = title_text.get_rect(center=(window_width//2, TITLE_MARGIN))
                        screen.blit(title_text, title_rect)
                        
                        # Draw instructions
                        instructions = [
                            "This test will help determine the best text contrast for you.",
                            "You will be shown different color combinations.",
                            "Rate each combination based on:",
                            "- Reading comfort",
                            "- Text clarity",
                            "- Visual stress reduction"
                        ]
                        
                        for i, line in enumerate(instructions):
                            instr_surface = text_font.render(line, True, TEXT_COLOR)
                            instr_rect = instr_surface.get_rect(center=(center_x, center_y - 100 + (i * 30)))
                            screen.blit(instr_surface, instr_rect)
                        
                        # Draw start button
                        start_button = pygame.Rect(center_x - 100, center_y + 100, 200, 50)
                        draw_button(screen, start_button, "Start Test", button_font, 
                                  DARK_BUTTON_COLOR, WHITE, border_radius=5)
                        
                        if event.type == pygame.MOUSEBUTTONDOWN and start_button.collidepoint(mouse_pos):
                            contrast_tester.start_test()
                    
                    elif not contrast_tester.test_complete:
                        # Get current contrast and fill background
                        bg_color, text_color, combo_name = contrast_tester.get_current_contrast()
                        screen.fill(bg_color)  # No need for Color object
                        
                        # Draw combination name
                        combo_surface = text_font.render(f"Testing: {combo_name}", True, text_color)
                        combo_rect = combo_surface.get_rect(center=(center_x, 50))
                        screen.blit(combo_surface, combo_rect)
                        
                        # Draw test text
                        text_surface = text_font.render(contrast_tester.current_text, True, text_color)
                        text_rect = text_surface.get_rect(center=(center_x, center_y - 100))
                        screen.blit(text_surface, text_rect)
                        
                        # Update the button spacing and positioning in the contrast test section
                        button_y = center_y + 50
                        button_width = 120
                        button_spacing = 80  # Increased from 40 to 80 pixels
                        total_width = (button_width * 3) + (button_spacing * 2)
                        start_x = center_x - (total_width // 2)

                        # Create rating buttons with increased spacing
                        difficult_button = pygame.Rect(start_x, button_y, button_width, 40)
                        neutral_button = pygame.Rect(start_x + button_width + button_spacing, button_y, button_width, 40)
                        easy_button = pygame.Rect(start_x + (button_width + button_spacing) * 2, button_y, button_width, 40)
                        
                        # Draw rating buttons with contrast-appropriate colors
                        buttons = [
                            (difficult_button, "Difficult", 1),
                            (neutral_button, "Neutral", 2),
                            (easy_button, "Easy", 3)
                        ]
                        
                        # Handle button clicks
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            mouse_pos = pygame.mouse.get_pos()
                            for button, _, rating in buttons:
                                if button.collidepoint(mouse_pos):
                                    contrast_tester.record_feedback(rating)
                                    if contrast_tester.feedback_provided():
                                        if not contrast_tester.next_contrast():
                                            contrast_tester.test_complete = True
                                    else:
                                        # Ensure the screen updates to the next contrast
                                        bg_color, text_color, combo_name = contrast_tester.get_current_contrast()
                                        screen.fill(bg_color)
                                        pygame.display.flip()
                        
                        # Draw buttons
                        for button, text, _ in buttons:
                            draw_button(screen, button, text, button_font, 
                                      text_color, bg_color, 
                                      border_radius=5)
                    
                    else:
                        # Show results
                        results = contrast_tester.get_results_summary()
                        screen.fill(BACKGROUND_COLOR)
                        
                        # Draw results title
                        title_surface = title_font.render("Test Results", True, TEXT_COLOR)
                        title_rect = title_surface.get_rect(center=(center_x, 50))
                        screen.blit(title_surface, title_rect)
                        
                        # Draw best combination info
                        results_text = [
                            f"Best Color Combination: {results['best_combination']}",
                            f"Contrast Ratio: {results['contrast_ratio']}",
                            f"Comfort Rating: {results['comfort_rating']}/3",
                            "",
                            "Recommendations:"
                        ] + results['recommendations']
                        
                        for i, line in enumerate(results_text):
                            result_surface = text_font.render(line, True, TEXT_COLOR)
                            result_rect = result_surface.get_rect(x=window_width//4, y=150 + (i * 30))
                            screen.blit(result_surface, result_rect)
                        
                        # Draw "Apply Settings" and "Back to Menu" buttons
                        button_y = window_height - 100
                        button_width = 200
                        button_spacing = 100  # Increased spacing between buttons
                        apply_button = pygame.Rect(center_x - (button_width + button_spacing), button_y, button_width, 50)
                        menu_button = pygame.Rect(center_x + button_spacing, button_y, button_width, 50)
                        
                        draw_button(screen, apply_button, "Apply Settings", button_font,
                                  DARK_BUTTON_COLOR, WHITE, border_radius=5)
                        draw_button(screen, menu_button, "Back to Menu", button_font,
                                  BACK_BUTTON_COLOR, WHITE, border_radius=5)
                        
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            if apply_button.collidepoint(mouse_pos):
                                # Apply the best contrast settings
                                BACKGROUND_COLOR = contrast_tester.best_contrast[0]
                                TEXT_COLOR = contrast_tester.best_contrast[1]
                                state = "menu"
                            elif menu_button.collidepoint(mouse_pos):
                                state = "menu"

        # Process voice commands
        try:
            voice_command = voice_assistant.get_command()
            if voice_command:
                print(f"Processing command: {voice_command}")  # Debug print
                if voice_command == "menu":
                    state = "menu"
                    active_menu = None
                    voice_assistant.speak("Returning to main menu")
                elif voice_command == "reading_test":
                    state = "level_1"
                    voice_assistant.speak("Starting reading test")
                elif voice_command == "dictation":
                    state = "dictation_test"
                    voice_assistant.speak("Starting dictation test")
                elif voice_command == "contrast":
                    state = "contrast_test"
                    voice_assistant.speak("Starting contrast test")
                elif voice_command == "help":
                    voice_assistant.provide_help()
                elif voice_command == "open_text_file":
                    opened_file = open(open_text_file())
                    opened_text = opened_file.read()
                    state = "display_text"
                    voice_assistant.speak("Opening text file")
                elif voice_command == "read_aloud" and state in ["level_1", "level_2", "level_3"]:
                    level_num = state.split("_")[1]
                    current_text = reading_texts[f"Level {level_num}"][0]
                    voice_assistant.speak(current_text["text"])
        except Exception as e:
            print(f"Error processing voice command: {e}")

        # Draw screen
        screen.fill(BACKGROUND_COLOR)
        
        # Draw common UI elements
        voice_speed_slider.draw(screen, slider_font)
        text_size_slider.draw(screen, slider_font)

        if state != "menu":
            # Draw back button for all non-menu states
            back_button = draw_back_button(screen, button_font, button_width, button_height)
            
            # Handle back button clicks
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.collidepoint(event.pos):
                    state = "menu"
                    active_menu = None
                    if hasattr(text_box, 'expected_text'):
                        delattr(text_box, 'expected_text')  # Clear the stored text when leaving
                    continue

        # Draw state-specific content
        if state == "menu":
            # Draw title
            title_text = title_font.render("Dyslexia Assistant", True, TEXT_COLOR)
            title_rect = title_text.get_rect(center=(window_width//2, TITLE_MARGIN))
            screen.blit(title_text, title_rect)

            # Draw main menu options
            for i, option in enumerate(main_options):
                x = (window_width - MAIN_BUTTON_WIDTH) // 2
                y = MENU_START + (i * MENU_SPACING)
                main_rect = pygame.Rect(x, y, MAIN_BUTTON_WIDTH, MAIN_BUTTON_HEIGHT)
                
                is_hovered = main_rect.collidepoint(pygame.mouse.get_pos())
                is_active = active_menu == i
                
                
                # Draw button text
                text = option['name']
                draw_button(screen, main_rect, text, button_font, 
                          TEXT_COLOR, WHITE, border_radius=15)

                if is_active or is_hovered:
                    sub_y = y + MAIN_BUTTON_HEIGHT + SUBMENU_SPACING
                    sub_width = MAIN_BUTTON_WIDTH // len(option['suboptions'])
                    
                    for j, suboption in enumerate(option['suboptions']):
                        sub_rect = pygame.Rect(x + (j * sub_width), sub_y,
                                             sub_width - PADDING, SUB_BUTTON_HEIGHT)
                        
                        is_sub_hovered = sub_rect.collidepoint(pygame.mouse.get_pos())
                        sub_color = DARK_BUTTON_COLOR if is_sub_hovered else BUTTON_COLOR
                        
                        draw_button(screen, sub_rect, suboption, text_font,
                                  sub_color, WHITE if is_sub_hovered else TEXT_COLOR,
                                  border_radius=10)

        else:
            # Draw back button for all non-menu states
            back_button = draw_back_button(screen, button_font, button_width, button_height)

            if state in ["level_1", "level_2", "level_3"]:
                # Get the level number from the state
                level_num = state.split("_")[1]
                current_text = reading_texts[f"Level {level_num}"][0]
                
                # Draw title
                title_text = title_font.render(f"Level {level_num} Reading", True, TEXT_COLOR)
                title_rect = title_text.get_rect(center=(window_width//2, TITLE_MARGIN))
                screen.blit(title_text, title_rect)
                
                # Calculate text area dimensions
                text_area_width = int(window_width * 0.8)  # Use 80% of window width
                text_area_height = int(window_height * 0.5)  # Use 50% of window height
                
                # Draw text with proper positioning and line spacing
                wrapped_lines = wrap_text(current_text["text"], text_font, text_area_width)
                line_height = int(text_font.get_height() * 1.5)  # Increase line spacing
                
                # Create text container
                text_container = pygame.Surface((text_area_width, len(wrapped_lines) * line_height))
                text_container.fill(BACKGROUND_COLOR)
                
                # Draw lines onto container with proper spacing
                for i, line in enumerate(wrapped_lines):
                    text_surface = text_font.render(line, True, TEXT_COLOR)
                    text_rect = text_surface.get_rect(center=(text_container.get_width()//2, i * line_height + line_height//2))
                    text_container.blit(text_surface, text_rect)
                
                # Position container in center of screen
                container_rect = text_container.get_rect(center=(window_width//2, window_height//2))
                screen.blit(text_container, container_rect)
                
                # Draw read aloud button below the text
                read_button = pygame.Rect(
                    (window_width - button_width)//2,
                    container_rect.bottom + 20,  # Position below text container
                    button_width//2,
                    button_height//2
                )
                draw_button(screen, read_button, "Read Aloud", button_font, 
                          DARK_BUTTON_COLOR, WHITE, border_radius=5)

            elif state == "dictation_test":
                # Generate new text when entering the state
                if not hasattr(text_box, 'expected_text'):
                    text_box.expected_text = generate_dictation_text()
                    text_box.show_results = False
                    text_box.text = ""  # Clear previous input

                # Draw title
                title_text = title_font.render("Dictation Test", True, TEXT_COLOR)
                title_rect = title_text.get_rect(center=(window_width//2, TITLE_MARGIN))
                screen.blit(title_text, title_rect)
                
                # Move buttons higher up
                button_y = int(window_height * 0.2)
                button_width = 120
                button_spacing = 40
                total_width = (button_width * 2) + button_spacing
                start_x = window_width // 2 - (total_width // 2)
                
                # Create button rectangles
                dictate_button = pygame.Rect(start_x, button_y, button_width, button_height//2)
                check_button = pygame.Rect(start_x + button_width + button_spacing, button_y, button_width, button_height//2)
                
                # Draw buttons
                draw_button(screen, dictate_button, "Dictate", button_font, 
                          DARK_BUTTON_COLOR, WHITE, border_radius=5)
                draw_button(screen, check_button, "Check", button_font, 
                          DARK_BUTTON_COLOR, WHITE, border_radius=5)
                
                # Handle button clicks in a way that doesn't interfere with typing
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if dictate_button.collidepoint(event.pos):
                        # Use text-to-speech in a non-blocking way
                        threading.Thread(target=reader.read_text, 
                                       args=(text_box.expected_text, int(voice_speed_slider.get_value()))).start()
                    elif check_button.collidepoint(event.pos):
                        # Check accuracy when check button is clicked
                        is_correct, feedback = check_accuracy(text_box.text, text_box.expected_text)
                        text_box.show_results = True
                        text_box.result_text = feedback
                
                # Move text box higher (position it closer to the buttons)
                text_box_y = button_y + button_height//2 + 20  # 20px gap after buttons
                text_box.rect.y = text_box_y
                text_box.draw(screen)
                
                # Draw results if they exist
                if hasattr(text_box, 'show_results') and text_box.show_results:
                    feedback_start_y = text_box.rect.bottom + 20
                    
                    expected_label = text_font.render("Expected Text:", True, TEXT_COLOR)
                    screen.blit(expected_label, (window_width//4, feedback_start_y))
                    
                    wrapped_expected = wrap_text(text_box.expected_text, text_font, window_width//2)
                    for i, line in enumerate(wrapped_expected):
                        expected_surface = text_font.render(line, True, DARK_BUTTON_COLOR)
                        expected_rect = expected_surface.get_rect(
                            x=window_width//4,
                            y=feedback_start_y + 30 + (i * 25)  # Reduced line spacing
                        )
                        screen.blit(expected_surface, expected_rect)
                    
                    # Draw feedback closer to expected text
                    if hasattr(text_box, 'result_text'):
                        feedback_y = feedback_start_y + (len(wrapped_expected) * 25) + 40
                        feedback_label = text_font.render("Analysis:", True, TEXT_COLOR)
                        screen.blit(feedback_label, (window_width//4, feedback_y))
                        
                        wrapped_feedback = wrap_text(text_box.result_text, text_font, window_width//2)
                        for i, line in enumerate(wrapped_feedback):
                            result_surface = text_font.render(line, True, TEXT_COLOR)
                            result_rect = result_surface.get_rect(
                                x=window_width//4,
                                y=feedback_y + 30 + (i * 25)  # Reduced line spacing
                            )
                            screen.blit(result_surface, result_rect)

            elif state == "contrast_test":
                # Center everything
                center_x = window_width // 2
                center_y = window_height // 2
                
                if not contrast_tester.test_started:
                    # Draw title and instructions
                    title_text = title_font.render("Contrast Test", True, TEXT_COLOR)
                    title_rect = title_text.get_rect(center=(window_width//2, TITLE_MARGIN))
                    screen.blit(title_text, title_rect)
                    
                    # Draw instructions
                    instructions = [
                        "This test will help determine the best text contrast for you.",
                        "You will be shown different color combinations.",
                        "Rate each combination based on:",
                        "- Reading comfort",
                        "- Text clarity",
                        "- Visual stress reduction"
                    ]
                    
                    for i, line in enumerate(instructions):
                        instr_surface = text_font.render(line, True, TEXT_COLOR)
                        instr_rect = instr_surface.get_rect(center=(center_x, center_y - 100 + (i * 30)))
                        screen.blit(instr_surface, instr_rect)
                    
                    # Draw start button
                    start_button = pygame.Rect(center_x - 100, center_y + 100, 200, 50)
                    draw_button(screen, start_button, "Start Test", button_font, 
                              DARK_BUTTON_COLOR, WHITE, border_radius=5)
                    
                    if event.type == pygame.MOUSEBUTTONDOWN and start_button.collidepoint(mouse_pos):
                        contrast_tester.start_test()
                
                elif not contrast_tester.test_complete:
                    # Get current contrast and fill background
                    bg_color, text_color, combo_name = contrast_tester.get_current_contrast()
                    screen.fill(bg_color)  # No need for Color object
                    
                    # Draw combination name
                    combo_surface = text_font.render(f"Testing: {combo_name}", True, text_color)
                    combo_rect = combo_surface.get_rect(center=(center_x, 50))
                    screen.blit(combo_surface, combo_rect)
                    
                    # Draw test text
                    text_surface = text_font.render(contrast_tester.current_text, True, text_color)
                    text_rect = text_surface.get_rect(center=(center_x, center_y - 100))
                    screen.blit(text_surface, text_rect)
                    
                    # Update the button spacing and positioning in the contrast test section
                    button_y = center_y + 50
                    button_width = 120
                    button_spacing = 80  # Increased from 40 to 80 pixels
                    total_width = (button_width * 3) + (button_spacing * 2)
                    start_x = center_x - (total_width // 2)

                    # Create rating buttons with increased spacing
                    difficult_button = pygame.Rect(start_x, button_y, button_width, 40)
                    neutral_button = pygame.Rect(start_x + button_width + button_spacing, button_y, button_width, 40)
                    easy_button = pygame.Rect(start_x + (button_width + button_spacing) * 2, button_y, button_width, 40)
                    
                    # Draw rating buttons with contrast-appropriate colors
                    buttons = [
                        (difficult_button, "Difficult", 1),
                        (neutral_button, "Neutral", 2),
                        (easy_button, "Easy", 3)
                    ]
                    
                    # Draw buttons
                    for button, text, _ in buttons:
                        draw_button(screen, button, text, button_font, 
                                    text_color, bg_color, 
                                    border_radius=5)
            
                else:
                    # Show results
                    results = contrast_tester.get_results_summary()
                    screen.fill(BACKGROUND_COLOR)
                    
                    # Draw results title
                    title_surface = title_font.render("Test Results", True, TEXT_COLOR)
                    title_rect = title_surface.get_rect(center=(center_x, 50))
                    screen.blit(title_surface, title_rect)
                    
                    # Draw best combination info
                    results_text = [
                        f"Best Color Combination: {results['best_combination']}",
                        f"Contrast Ratio: {results['contrast_ratio']}",
                        f"Comfort Rating: {results['comfort_rating']}/3",
                        "",
                        "Recommendations:"
                    ] + results['recommendations']
                    
                    for i, line in enumerate(results_text):
                        result_surface = text_font.render(line, True, TEXT_COLOR)
                        result_rect = result_surface.get_rect(x=window_width//4, y=150 + (i * 30))
                        screen.blit(result_surface, result_rect)
                    
                    # Draw "Apply Settings" and "Back to Menu" buttons
                    button_y = window_height - 100
                    button_width = 200
                    button_spacing = 100  # Increased spacing between buttons
                    apply_button = pygame.Rect(center_x - (button_width + button_spacing), button_y, button_width, 50)
                    menu_button = pygame.Rect(center_x + button_spacing, button_y, button_width, 50)
                    
                    draw_button(screen, apply_button, "Apply Settings", button_font,
                              DARK_BUTTON_COLOR, WHITE, border_radius=5)
                    draw_button(screen, menu_button, "Back to Menu", button_font,
                              BACK_BUTTON_COLOR, WHITE, border_radius=5)
                    
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if apply_button.collidepoint(mouse_pos):
                            # Apply the best contrast settings
                            BACKGROUND_COLOR = contrast_tester.best_contrast[0]
                            TEXT_COLOR = contrast_tester.best_contrast[1]
                            state = "menu"
                        elif menu_button.collidepoint(mouse_pos):
                            state = "menu"
            elif state == "notes_proofreading":
                upload_button = pygame.Rect((window_width - button_width)//2, menu_start_y + menu_spacing, 
                                             button_width//2, button_height//2)
                draw_button(screen, upload_button, "Upload Image", button_font, DARK_BUTTON_COLOR, WHITE)
            elif state == "open_text_file":
                # Draw title
                title_text = title_font.render("Open Text File", True, TEXT_COLOR)
                title_rect = title_text.get_rect(center=(window_width//2, TITLE_MARGIN))
                screen.blit(title_text, title_rect)

                # Add "Open File" button
                open_file_button = pygame.Rect(window_width//2 - 100, window_height//2 - 25, 200, 50)
                draw_button(screen, open_file_button, "Open File", button_font, 
                            DARK_BUTTON_COLOR, WHITE, border_radius=5)
            elif state == "display_text":
                # Draw title
                title_text = title_font.render("Opened Text", True, TEXT_COLOR)
                title_rect = title_text.get_rect(center=(window_width//2, TITLE_MARGIN))
                screen.blit(title_text, title_rect)

                # Calculate text area dimensions
                text_area_width = int(window_width * 0.8)
                text_area_height = int(window_height * 0.6)

                # Wrap and display text
                wrapped_lines = wrap_text(opened_text, text_font, text_area_width)
                line_height = int(text_font.get_height() * 1.5)

                # Create scrollable text container
                text_container = pygame.Surface((text_area_width, len(wrapped_lines) * line_height))
                text_container.fill(BACKGROUND_COLOR)

                for i, line in enumerate(wrapped_lines):
                    text_surface = text_font.render(line, True, TEXT_COLOR)
                    text_rect = text_surface.get_rect(x=0, y=i * line_height)
                    text_container.blit(text_surface, text_rect)

                # Display text with scrolling
                container_rect = pygame.Rect((window_width - text_area_width) // 2, TITLE_MARGIN + 50, 
                                            text_area_width, text_area_height)
                screen.blit(text_container, container_rect, 
                            (0, scroll_y, text_area_width, text_area_height))

                # Draw scroll bar
                scroll_bar_height = min(text_area_height, 
                                        text_area_height * (text_area_height / text_container.get_height()))
                scroll_bar_pos = (scroll_y / (text_container.get_height() - text_area_height)) * (text_area_height - scroll_bar_height)
                scroll_bar_rect = pygame.Rect(container_rect.right + 10, container_rect.top + scroll_bar_pos, 
                                            10, scroll_bar_height)
                pygame.draw.rect(screen, DARK_BUTTON_COLOR, scroll_bar_rect)
        # Draw voice command indicator
        if voice_assistant.is_listening:
            indicator_radius = 10
            pygame.draw.circle(screen, VOICE_INDICATOR_COLOR, 
                              (window_width - 20, 20), indicator_radius)
        clock.tick(60)
        pygame.display.flip()

if __name__ == "__main__":
    main()
