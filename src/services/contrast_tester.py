import time
import random
import pygame

class ContrastTester:
    def __init__(self, window_width, window_height):
        self.window_width = window_width
        self.window_height = window_height
        self.test_started = False
        self.test_complete = False
        
        # Research-based color combinations for dyslexia
        self.dyslexic_friendly_colors = [
            {
                "bg": (255, 248, 229),  # Cream/Off-white (recommended by BDA)
                "text": (0, 0, 0),      # Black
                "name": "Cream & Black"
            },
            {
                "bg": (204, 232, 207),  # Soft Mint Green
                "text": (0, 0, 0),      # Black
                "name": "Mint & Black"
            },
            {
                "bg": (203, 225, 241),  # Light Blue
                "text": (0, 0, 0),      # Black
                "name": "Light Blue & Black"
            },
            {
                "bg": (44, 44, 44),     # Dark Gray
                "text": (255, 248, 229), # Cream
                "name": "Dark Mode"
            },
            {
                "bg": (250, 226, 197),  # Peach
                "text": (0, 0, 0),      # Black
                "name": "Peach & Black"
            },
            {
                "bg": (235, 235, 235),  # Light Gray
                "text": (68, 68, 68),   # Dark Gray
                "name": "Gray Scale"
            }
        ]
        
        # Initialize test parameters
        self.current_index = 0
        self.results = []
        self.test_texts = [
            "Reading should be comfortable for your eyes.",
            "Focus on the clarity of these letters.",
            "Does this combination reduce visual stress?",
            "Are the words stable or do they move?",
            "Can you distinguish letters easily?"
        ]
        self.current_text = self.test_texts[0]
        self.best_contrast = None
        self.reading_start_time = None
        
        # Sort combinations by contrast ratio
        self._sort_combinations_by_contrast()
        self.current_feedback_provided = False
    
    def calculate_contrast_ratio(self, bg_color, text_color):
        """
        Calculate WCAG contrast ratio between background and text colors
        Returns a ratio where 1:1 is no contrast and 21:1 is maximum contrast
        """
        def get_luminance(rgb):
            # Convert to sRGB values
            srgb = [x / 255.0 for x in rgb]
            # Convert to linear RGB
            rgb_linear = []
            for val in srgb:
                if val <= 0.03928:
                    rgb_linear.append(val / 12.92)
                else:
                    rgb_linear.append(((val + 0.055) / 1.055) ** 2.4)
            # Calculate luminance
            return 0.2126 * rgb_linear[0] + 0.7152 * rgb_linear[1] + 0.0722 * rgb_linear[2]

        l1 = get_luminance(bg_color)
        l2 = get_luminance(text_color)
        
        # Calculate contrast ratio
        if l1 > l2:
            return (l1 + 0.05) / (l2 + 0.05)
        return (l2 + 0.05) / (l1 + 0.05)
    
    def _sort_combinations_by_contrast(self):
        """Sort color combinations by their contrast ratio"""
        for combo in self.dyslexic_friendly_colors:
            combo['contrast_ratio'] = self.calculate_contrast_ratio(combo['bg'], combo['text'])
        
        # Sort by contrast ratio (aiming for 7:1 ratio as per WCAG AAA)
        self.dyslexic_friendly_colors.sort(
            key=lambda x: abs(x['contrast_ratio'] - 7.0)
        )
    
    def start_test(self):
        """Initialize the contrast test"""
        self.test_started = True
        self.current_index = 0
        self.results = []
        self.reading_start_time = time.time()
        random.shuffle(self.test_texts)  # Randomize test texts
        self.current_text = self.test_texts[0]
    
    def get_current_contrast(self):
        """Get current background and text colors"""
        current = self.dyslexic_friendly_colors[self.current_index]
        return current["bg"], current["text"], current["name"]
    
    def record_feedback(self, rating):
        """
        Record user feedback with multiple factors:
        - Subjective comfort (1-3)
        - Reading time
        - Contrast ratio
        """
        reading_time = time.time() - self.reading_start_time
        current = self.dyslexic_friendly_colors[self.current_index]
        
        feedback = {
            "contrast": current,
            "comfort_rating": rating,
            "contrast_ratio": current['contrast_ratio'],
            "reading_time": reading_time
        }
        
        # Calculate reading speed (words per minute)
        words = len(self.current_text.split())
        wpm = (words / reading_time) * 60
        
        feedback['total_score'] = (
            (rating * 0.4) +  # 40% weight to comfort
            (min(current['contrast_ratio'] / 7.0, 1.0) * 0.4) +  # 40% weight to optimal contrast
            (min(wpm / 200.0, 1.0) * 0.2)  # 20% weight to reading speed
        )
        
        self.results.append(feedback)
        self.reading_start_time = time.time()  # Reset timer for next test
        self.current_feedback_provided = True
        # Change test text for next combination
        if self.current_index + 1 < len(self.test_texts):
            self.current_text = self.test_texts[self.current_index + 1]
    
    def next_contrast(self):
        """Move to next contrast combination"""
        self.current_feedback_provided = False
        self.current_index += 1
        if self.current_index >= len(self.dyslexic_friendly_colors):
            self._calculate_best_contrast()
            return False
        return True
    
    def feedback_provided(self):
        """Check if feedback has been provided for the current contrast combination"""
        return self.current_feedback_provided

    def _calculate_best_contrast(self):
        """
        Calculate best contrast using multiple factors:
        - WCAG guidelines (7:1 ratio for AAA level)
        - User comfort ratings
        - Reading speed
        """
        if not self.results:
            # Default to research-backed combination
            self.best_contrast = (self.dyslexic_friendly_colors[0]['bg'], 
                                self.dyslexic_friendly_colors[0]['text'])
            return
            
        # Weight different factors
        for result in self.results:
            # Calculate reading speed (words per minute)
            words = len(self.current_text.split())
            wpm = (words / result['reading_time']) * 60
            
            result['total_score'] = (
                (result['comfort_rating'] * 0.4) +  # 40% weight to comfort
                (min(result['contrast_ratio'] / 7.0, 1.0) * 0.4) +  # 40% weight to optimal contrast
                (min(wpm / 200.0, 1.0) * 0.2)  # 20% weight to reading speed
            )
        
        # Get best result
        self.best_result = max(self.results, key=lambda x: x['total_score'])
        self.best_contrast = (self.best_result['contrast']['bg'], 
                            self.best_result['contrast']['text'])
        self.test_complete = True
        
    def get_results_summary(self):
        """Get a summary of the test results"""
        if not self.test_complete:
            return "Test not completed"
        
        return {
            "best_combination": self.best_result['contrast']['name'],
            "contrast_ratio": round(self.best_result['contrast_ratio'], 2),
            "comfort_rating": self.best_result['comfort_rating'],
            "recommendations": [
                "Use this color combination for reading materials",
                "Consider adjusting text size and spacing",
                "Take regular breaks to reduce visual stress"
            ]
        }