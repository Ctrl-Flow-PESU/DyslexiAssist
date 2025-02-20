def analyze_text(input_text, target_text):
    input_words = len(input_text.split())
    target_words = len(target_text.split())
    word_count_diff = abs(input_words - target_words)
    accuracy = 1 - (word_count_diff / max(target_words, 1))
    accuracy = max(0, min(1, accuracy))
    
    if accuracy >= 0.9:
        return "Excellent work! Your response closely matches the target length."
    elif accuracy >= 0.7:
        return "Good job! Your response length is reasonably close to the target."
    else:
        return f"Keep practicing! Your response had {input_words} words while the target had {target_words} words." 