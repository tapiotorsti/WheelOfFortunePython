import pygame
import pygame_gui
import math
import random
import pygame.gfxdraw

# Initialize Pygame
pygame.init()

# Screen dimensions and setup
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Wheel of Fortune")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
TEAM_COLORS = [
    (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 165, 0),
    (128, 0, 128), (0, 255, 255), (192, 192, 192), (128, 128, 0), (255, 105, 180)
]

# Fonts
font = pygame.font.SysFont("Arial", 16)

# Pygame GUI manager
manager = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT))

# Create buttons and text input box
spin_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((650, 50), (100, 50)),
                                           text="Spin",
                                           manager=manager)
add_name_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((650, 120), (100, 50)),
                                               text="Add Name",
                                               manager=manager)
clear_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((650, 190), (100, 50)),
                                            text="Clear",
                                            manager=manager)
name_input = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((650, 260), (100, 30)),
                                                  manager=manager)

# Function to draw a wheel
def draw_wheel(surface, x, y, radius, participants, colors, rotation_angle):
    num_segments = len(participants)
    if num_segments == 0:
        return
    
    angle_step = 2 * math.pi / num_segments
    for i in range(num_segments):
        # Calculate the angles for the segment
        start_angle = i * angle_step + rotation_angle
        end_angle = start_angle + angle_step
        color = colors[i % len(colors)]
        
        # Generate points for a filled arc
        points = [(x, y)]
        for angle in range(int(math.degrees(start_angle)), int(math.degrees(end_angle)) + 1):
            rad = math.radians(angle)
            points.append((x + radius * math.cos(rad), y + radius * math.sin(rad)))
        
        # Draw the filled arc
        pygame.gfxdraw.filled_polygon(surface, points, color)
        pygame.gfxdraw.aapolygon(surface, points, color)  # Anti-aliasing for smooth edges
        
        # Add text to the segment
        mid_angle = (start_angle + end_angle) / 2
        text_x = x + (radius * 0.7) * math.cos(mid_angle)
        text_y = y + (radius * 0.7) * math.sin(mid_angle)
        text = font.render(participants[i], True, WHITE)
        surface.blit(text, (text_x - text.get_width() // 2, text_y - text.get_height() // 2))

# Function to draw the arrow
def draw_arrow(surface, x, y, size):
    """Draws a stationary black arrow pointing downward above the wheel."""
    points = [
        (x, y + size),  # Tip of the arrow (downward)
        (x - size // 2, y - size),  # Left base of the arrow
        (x + size // 2, y - size)   # Right base of the arrow
    ]
    pygame.draw.polygon(surface, BLACK, points)

# Function to convert angle to index
def get_selected_segment(rotation_angle, participants):
    num_segments = len(participants)
    angle_step = 360 / num_segments
    adjusted_angle = (-math.degrees(rotation_angle) - 90) % 360  # Adjust for top position
    selected_index = int((adjusted_angle) // angle_step)
    return selected_index % num_segments

# Initial data
participants = []
rotation_angle = 0
spinning = False
spin_speed = 0
stop_segment = None

# Main loop
running = True
clock = pygame.time.Clock()

while running:
    time_delta = clock.tick(60) / 1000.0
    screen.fill(WHITE)
    
    # Draw the wheel
    if participants:
        draw_wheel(screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, 150, participants, TEAM_COLORS, rotation_angle)
    
    # Draw the arrow
    draw_arrow(screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 160, 20)
    
    # Handle Pygame events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Process GUI events
        manager.process_events(event)

        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == spin_button and participants and not spinning:
                    # Start spinning
                    spinning = True
                    spin_speed = random.uniform(10, 20)
                    stop_segment = None  # Reset stop segment
                elif event.ui_element == add_name_button:
                    # Add name from input box
                    name = name_input.get_text()
                    if name.strip():
                        participants.append(name.strip())
                        name_input.set_text("")  # Clear input box
                elif event.ui_element == clear_button:
                    # Clear all participants
                    participants.clear()
                    spinning = False
    
    # Spin logic
    if spinning:
        rotation_angle += math.radians(spin_speed)
        spin_speed *= 0.98  # Decelerate
        if spin_speed < 0.1:  # Stop when speed is low enough
            spinning = False
            stop_segment = get_selected_segment(rotation_angle, participants)
            if stop_segment is not None:
                # Remove the stopped participant
                print(f"Removing: {participants[stop_segment]}")
                participants.pop(stop_segment)
    
    # Update GUI elements
    manager.update(time_delta)
    manager.draw_ui(screen)
    
    # Update display
    pygame.display.flip()

pygame.quit()
