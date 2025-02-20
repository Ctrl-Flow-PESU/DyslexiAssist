def wrap_text(text, font, max_width):
    """Wrap text to fit within a given width."""
    lines = []
    words = text.split(' ')
    current_line = []
    current_width = 0

    for word in words:
        if '\n' in word:
            parts = word.split('\n')
            for i, part in enumerate(parts):
                if i > 0:
                    lines.append(' '.join(current_line))
                    current_line = []
                    current_width = 0
                current_line.append(part)
                current_width += font.size(part)[0]
        else:
            word_width = font.size(word)[0]
            if current_width + word_width <= max_width:
                current_line.append(word)
                current_width += word_width + font.size(' ')[0]
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
                current_width = word_width + font.size(' ')[0]

    if current_line:
        lines.append(' '.join(current_line))

    return lines