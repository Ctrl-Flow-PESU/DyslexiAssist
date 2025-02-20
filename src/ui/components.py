import pygame

class Slider:
    def __init__(self, x, y, width, min_val, max_val, initial_val, label):
        self.rect = pygame.Rect(x, y, width, 20)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.knob_radius = 12
        self.knob_x = x + int((initial_val - min_val) / (max_val - min_val) * width)
        self.label = label
        self.dragging = False
        self.hover = False

    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        self.hover = self.get_knob_rect().collidepoint(mouse_pos)
        
        if event.type == pygame.MOUSEBUTTONDOWN and self.hover:
            self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            rel_x = event.pos[0] - self.rect.x
            rel_x = max(0, min(rel_x, self.rect.width))
            self.knob_x = self.rect.x + rel_x
            self.value = self.min_val + (self.knob_x - self.rect.x) / self.rect.width * (self.max_val - self.min_val)

    def draw(self, screen, font):
        # Draw slider track with gradient
        gradient_rect = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(gradient_rect, (200, 220, 240, 255), gradient_rect.get_rect(), border_radius=10)
        screen.blit(gradient_rect, self.rect)
        
        # Draw active portion of slider
        active_width = self.knob_x - self.rect.x
        if active_width > 0:
            active_rect = pygame.Rect(self.rect.x, self.rect.y, active_width, self.rect.height)
            pygame.draw.rect(screen, (100, 149, 237), active_rect, border_radius=10)
        
        # Draw knob with shadow and hover effect
        shadow_color = (80, 80, 80, 100)
        knob_color = (65, 105, 225) if self.hover or self.dragging else (100, 149, 237)
        
        # Draw shadow
        pygame.draw.circle(screen, shadow_color, (self.knob_x + 2, self.rect.centery + 2), self.knob_radius)
        
        # Draw knob
        pygame.draw.circle(screen, knob_color, (self.knob_x, self.rect.centery), self.knob_radius)
        pygame.draw.circle(screen, (255, 255, 255), (self.knob_x, self.rect.centery), self.knob_radius - 2)
        
        # Draw label with value
        label_surface = font.render(f"{self.label}: {int(self.value)}", True, (0, 0, 0))
        shadow_surface = font.render(f"{self.label}: {int(self.value)}", True, (100, 100, 100))
        screen.blit(shadow_surface, (self.rect.x + 1, self.rect.y - 25))
        screen.blit(label_surface, (self.rect.x, self.rect.y - 26))

    def get_value(self):
        return self.value

    def get_knob_rect(self):
        return pygame.Rect(self.knob_x - self.knob_radius,
                         self.rect.centery - self.knob_radius,
                         self.knob_radius * 2, self.knob_radius * 2)

class TextBox:
    def __init__(self, x, y, width, height, font, text=''):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = pygame.Color('white')
        self.font = font
        self.text = text
        self.active = False
        self.hover = False
        self.padding = 10

    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        self.hover = self.rect.collidepoint(mouse_pos)
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = pygame.Color('dodgerblue2') if self.active else pygame.Color('white')
        
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                print(self.text)  # For debugging
                self.text = ''
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode

    def draw(self, screen):
        # Draw the text box
        pygame.draw.rect(screen, self.color, self.rect, 2)
        txt_surface = self.font.render(self.text, True, (0, 0, 0))
        screen.blit(txt_surface, (self.rect.x + self.padding, self.rect.y + self.padding))
        pygame.draw.rect(screen, self.color, self.rect, 2)

class LevelButton:
    def __init__(self, rect, text, font):
        self.rect = rect
        self.text = text
        self.font = font
        self.is_pressed = False
        self.hover = False

    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        self.hover = self.rect.collidepoint(mouse_pos)
        
        if event.type == pygame.MOUSEBUTTONDOWN and self.hover:
            self.is_pressed = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.is_pressed = False

    def draw(self, screen):
        # Colors
        base_color = (65, 105, 225) if self.is_pressed else (100, 149, 237) if self.hover else (173, 216, 230)
        
        # Draw shadow
        shadow_rect = self.rect.copy()
        shadow_rect.x += 2
        shadow_rect.y += 2
        pygame.draw.rect(screen, (100, 100, 100, 128), shadow_rect, border_radius=10)
        
        # Draw main button with gradient
        gradient_rect = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        pygame.draw.rect(gradient_rect, (*base_color, 255), gradient_rect.get_rect(), border_radius=10)
        screen.blit(gradient_rect, self.rect)
        
        # Draw text with shadow
        shadow_surface = self.font.render(self.text, True, (100, 100, 100))
        text_surface = self.font.render(self.text, True, (0, 0, 0))
        
        # Position text
        text_rect = text_surface.get_rect(center=self.rect.center)
        shadow_rect = shadow_surface.get_rect(center=(self.rect.centerx + 1, self.rect.centery + 1))
        
        # Draw text shadow and main text
        screen.blit(shadow_surface, shadow_rect)
        screen.blit(text_surface, text_rect)

def draw_button(screen, rect, text, font, button_color, text_color, border_radius=10, shadow_offset=2):
    """Draw a button with shadow, hover effect, and gradient. Button width adjusts to text length."""
    
    # Calculate required width for text
    text_surface = font.render(text, True, text_color)
    required_width = text_surface.get_width() + 40  # Padding
    
    # Create new rect centered on original but with calculated width
    new_rect = pygame.Rect(0, 0, required_width, rect.height)
    new_rect.center = rect.center
    
    # Draw shadow
    shadow_rect = new_rect.copy()
    shadow_rect.x += shadow_offset
    shadow_rect.y += shadow_offset
    pygame.draw.rect(screen, (100, 100, 100, 128), shadow_rect, border_radius=border_radius)
    
    # Draw main button with gradient effect
    gradient_rect = pygame.Surface(new_rect.size, pygame.SRCALPHA)
    pygame.draw.rect(gradient_rect, (*button_color, 255), gradient_rect.get_rect(), border_radius=border_radius)
    screen.blit(gradient_rect, new_rect)
    
    # Handle text with icons
    # Draw text shadow
    shadow_surface = font.render(text, True, (100, 100, 100))
    shadow_rect = shadow_surface.get_rect(center=(new_rect.centerx + shadow_offset, new_rect.centery + shadow_offset))
    screen.blit(shadow_surface, shadow_rect)
    
    # Draw main text
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=new_rect.center)
    screen.blit(text_surface, text_rect)

def wrap_text(text, font, max_width):
    words = text.split(' ')
    lines = []
    current_line = []
    current_width = 0
    for word in words:
        word_surface = font.render(word, True, (0, 0, 0))
        word_width = word_surface.get_width()
        if current_width + word_width <= max_width:
            current_line.append(word)
            current_width += word_width + font.size(' ')[0]
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
            current_width = word_width
    if current_line:
        lines.append(' '.join(current_line))
    return lines 