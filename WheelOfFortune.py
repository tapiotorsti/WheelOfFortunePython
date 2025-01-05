import pygame
import pygame_gui
import math
import random
import pygame.gfxdraw

# Initialize Pygame
pygame.init()

# Screen dimensions and setup
SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Wheel of Fortune - F1 Teams")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
HIGHLIGHT_COLOR = (0, 255, 255, 128)  # Highlight with transparency

# Hex color codes for each team (Primary, Secondary, and Tertiary colors)
TEAM_COLORS = {
    "Red Bull": ("#1E41FF", "#FFDD00", "#FFFFFF"),  # Blue, Yellow, White
    "Ferrari": ("#DC0000", "#FFFFFF", "#000000"),   # Red, White, Black
    "Mercedes": ("#00D2BE", "#FFFFFF", "#000000"),  # Cyan, White, Black
    "McLaren": ("#FF8700", "#000000", "#FFFFFF"),   # Orange, Black, White
    "Aston Martin": ("#006F62", "#FFFFFF", "#000000"),  # Green, White, Black
    "Alpine": ("#0090FF", "#FF0000", "#FFFFFF"),    # Blue, Red, White
    "Haas": ("#FFFFFF", "#000000", "#FF0000"),      # White, Black, Red
    "AlphaTauri": ("#4E5DAB", "#FFFFFF", "#FFDD00"),  # Dark Blue, White, Yellow
    "Alfa Romeo": ("#900000", "#FFFFFF", "#000000"), # Dark Red, White, Black
    "Williams": ("#005AFF", "#FFFFFF", "#FFDD00")   # Bright Blue, White, Yellow
}

TEAM_NAMES = list(TEAM_COLORS.keys())

# Fonts
font = pygame.font.SysFont("Arial", 16)

# Pygame GUI manager
manager = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT))

# Create buttons and text input box
add_name_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1000, 120), (150, 50)),
                                               text="Add Name",
                                               manager=manager)
spin_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1000, 190), (150, 50)),
                                           text="Spin Wheel",
                                           manager=manager)
zoom_in_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1000, 260), (150, 50)),
                                              text="Zoom In",
                                              manager=manager)
zoom_out_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1000, 330), (150, 50)),
                                               text="Zoom Out",
                                               manager=manager)
name_input = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((1000, 470), (150, 30)),
                                                  manager=manager)

# Helper function to convert hex to RGB
def hex_to_rgb(hex_color):
    """Convert a hex color code (#RRGGBB) to an RGB tuple."""
    hex_color = hex_color.lstrip('#')  # Remove '#' if present
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

# Helper function to determine if a color is bright
def is_bright_color(color):
    """Determine if a color is bright based on its RGB components."""
    r, g, b = color
    brightness = (r * 0.299 + g * 0.587 + b * 0.114)  # Perceived brightness formula
    return brightness > 186  # Threshold for brightness

# Wheel class with delayed segment deletion
class Wheel:
    def __init__(self, x, y, radius, team_name, primary_color, secondary_color, tertiary_color):
        self.x = x
        self.y = y
        self.radius = radius
        self.team_name = team_name
        self.primary_color = primary_color
        self.secondary_color = secondary_color
        self.tertiary_color = tertiary_color
        self.participants = []
        self.segment_colors = []  # Store precomputed segment colors
        self.rotation_angle = 0
        self.spinning = False
        self.spin_speed = 0
        self.selected = False  # To track if this wheel is selected
        self.stopped_segment = None  # Track the last stopped segment

    def is_clicked(self, mouse_pos):
        """Check if the wheel is clicked based on the mouse position."""
        distance = math.sqrt((mouse_pos[0] - self.x) ** 2 + (mouse_pos[1] - self.y) ** 2)
        return distance <= self.radius

    def compute_segment_colors(self):
        """Compute colors for each segment, ensuring no two adjacent segments are the same."""
        self.segment_colors = []
        color_pool = [self.primary_color, self.secondary_color, self.tertiary_color]
        
        for i in range(len(self.participants)):
            if i == 0:
                # First segment gets any color
                self.segment_colors.append(random.choice(color_pool))
            else:
                # Exclude the previous segment's color
                previous_color = self.segment_colors[-1]
                available_colors = [color for color in color_pool if color != previous_color]
                self.segment_colors.append(random.choice(available_colors))

    def add_participant(self, name):
        """Add a participant and recompute segment colors."""
        self.participants.append(name)
        self.compute_segment_colors()

    def remove_participant(self, index):
        """Remove a participant and recompute segment colors."""
        if 0 <= index < len(self.participants):
            self.participants.pop(index)
            self.compute_segment_colors()

    def delete_stopped_segment(self):
        """Delete the segment where the wheel stopped."""
        if self.stopped_segment is not None:
            self.remove_participant(self.stopped_segment)
            self.stopped_segment = None  # Reset the stopped segment

    def spin(self):
        """Start spinning the wheel."""
        if not self.spinning:
            self.spinning = True
            self.spin_speed = random.uniform(10, 20)
            self.stopped_segment = None  # Reset stopped segment when spinning starts

    def update(self):
        """Update the spinning logic."""
        if self.spinning:
            self.rotation_angle += math.radians(self.spin_speed)
            self.spin_speed *= 0.98  # Decelerate
            if self.spin_speed < 0.1:
                self.spinning = False
                self.stopped_segment = self.get_selected_segment()
                if self.stopped_segment is not None:
                    print(f"Selected segment: {self.participants[self.stopped_segment]}")

    def get_selected_segment(self):
        """Get the segment where the wheel stops."""
        num_segments = len(self.participants)
        if num_segments == 0:
            return None
        angle_step = 360 / num_segments
        adjusted_angle = (-math.degrees(self.rotation_angle) - 90) % 360  # Adjust for top position
        selected_index = int(adjusted_angle // angle_step)
        return selected_index % num_segments

    def draw(self, surface, zoomed=False):
        """Draw the wheel, optionally zoomed in."""
        draw_radius = self.radius * 2 if zoomed else self.radius
        draw_x, draw_y = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2) if zoomed else (self.x, self.y)

        # Validate segment colors
        if len(self.segment_colors) != len(self.participants):
            self.compute_segment_colors()

        # Draw the wheel background if no participants
        if len(self.participants) == 0:
            pygame.draw.circle(surface, self.primary_color, (draw_x, draw_y), draw_radius)
            pygame.draw.circle(surface, BLACK, (draw_x, draw_y), draw_radius, 3)  # Border
        else:
            num_segments = len(self.participants)
            angle_step = 2 * math.pi / num_segments

            for i in range(num_segments):
                color = self.segment_colors[i]  # Use the precomputed color

                # Calculate the angles for the segment
                start_angle = i * angle_step + self.rotation_angle
                end_angle = start_angle + angle_step

                # Generate points for a filled arc
                points = [(draw_x, draw_y)]
                for angle in range(int(math.degrees(start_angle)), int(math.degrees(end_angle)) + 1):
                    rad = math.radians(angle)
                    points.append((draw_x + draw_radius * math.cos(rad), draw_y + draw_radius * math.sin(rad)))

                # Draw the filled arc
                pygame.gfxdraw.filled_polygon(surface, points, color)
                pygame.gfxdraw.aapolygon(surface, points, color)  # Anti-aliasing for smooth edges

                # Draw the black border
                pygame.draw.polygon(surface, BLACK, points, width=2)

                # Determine text color (white or black based on brightness)
                text_color = BLACK if is_bright_color(color) else WHITE

                # Add text to the segment
                mid_angle = (start_angle + end_angle) / 2
                text_x = draw_x + (draw_radius * 0.7) * math.cos(mid_angle)
                text_y = draw_y + (draw_radius * 0.7) * math.sin(mid_angle)
                text = font.render(self.participants[i], True, text_color)
                surface.blit(text, (text_x - text.get_width() // 2, text_y - text.get_height() // 2))

        # Highlight the wheel if selected
        if self.selected and not zoomed:
            pygame.draw.circle(surface, HIGHLIGHT_COLOR, (draw_x, draw_y), draw_radius + 5, 5)

        # Draw the team name
        team_text = font.render(self.team_name, True, BLACK)
        surface.blit(team_text, (draw_x - team_text.get_width() // 2, draw_y + draw_radius + 10))

        # Draw the black arrow
        self.draw_arrow(surface, draw_x, draw_y, draw_radius)

    def draw_arrow(self, surface, draw_x, draw_y, draw_radius):
        """Draw a black arrow pointing downward at the top of the wheel."""
        arrow_size = 15
        arrow_points = [
            (draw_x, draw_y - draw_radius + arrow_size),  # Tip of the arrow (downward)
            (draw_x - arrow_size // 2, draw_y - draw_radius),  # Left base of the arrow
            (draw_x + arrow_size // 2, draw_y - draw_radius)   # Right base of the arrow
        ]
        pygame.draw.polygon(surface, BLACK, arrow_points)

# Create wheels dynamically
wheels = []
columns = 4  # Number of wheels per row
spacing_x = 250  # Horizontal spacing between wheels
spacing_y = 250  # Vertical spacing between wheels
x_positions = [150 + i * spacing_x for i in range(columns)]
y_positions = [150 + j * spacing_y for j in range((len(TEAM_NAMES) + columns - 1) // columns)]

for i, team_name in enumerate(TEAM_NAMES):
    x = x_positions[i % columns]  # Determine x position
    y = y_positions[i // columns]  # Determine y position
    primary_color = hex_to_rgb(TEAM_COLORS[team_name][0])
    secondary_color = hex_to_rgb(TEAM_COLORS[team_name][1])
    tertiary_color = hex_to_rgb(TEAM_COLORS[team_name][2])
    wheels.append(Wheel(x, y, 100, team_name, primary_color, secondary_color, tertiary_color))

# Main loop
running = True
clock = pygame.time.Clock()
selected_wheel = wheels[0]
selected_wheel.selected = True  # Mark the first wheel as selected
zoomed_in = False
delete_button = None  # Dynamically created delete button

while running:
    time_delta = clock.tick(60) / 1000.0
    screen.fill(WHITE)
    
    # Draw non-selected wheels first
    for wheel in wheels:
        if not wheel.selected or not zoomed_in:
            wheel.draw(screen)
        wheel.update()
    
    # Draw the selected wheel last (on top)
    if zoomed_in:
        selected_wheel.draw(screen, zoomed=True)

    # Handle Pygame events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button
            mouse_pos = event.pos
            for wheel in wheels:
                if wheel.is_clicked(mouse_pos):
                    # Remove the delete button if switching wheels
                    if delete_button:
                        delete_button.kill()
                        delete_button = None

                    selected_wheel.selected = False  # Deselect the current wheel
                    selected_wheel = wheel  # Update the selected wheel
                    selected_wheel.selected = True  # Highlight the new selection
        # Process GUI events
        manager.process_events(event)

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == add_name_button:
                # Add name to the selected wheel
                name = name_input.get_text()
                if name.strip():
                    selected_wheel.add_participant(name.strip())
                    name_input.set_text("")  # Clear input box
            elif event.ui_element == spin_button:
                # Spin the selected wheel
                selected_wheel.spin()

                # Remove any existing delete button
                if delete_button:
                    delete_button.kill()

            elif event.ui_element == zoom_in_button:
                # Zoom in on the selected wheel
                zoomed_in = True
            elif event.ui_element == zoom_out_button:
                # Zoom out to show all wheels
                zoomed_in = False
            elif delete_button and event.ui_element == delete_button:
                # Delete the stopped segment
                selected_wheel.delete_stopped_segment()
                delete_button.kill()  # Remove the delete button
                delete_button = None

    # Check if a wheel has stopped spinning and create the delete button
    if not selected_wheel.spinning and selected_wheel.stopped_segment is not None and delete_button is None:
        delete_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((selected_wheel.x + selected_wheel.radius + 20, selected_wheel.y - 25), (120, 40)),
            text="Delete Segment",
            manager=manager
        )

    # Update GUI elements
    manager.update(time_delta)
    manager.draw_ui(screen)
    
    # Update display
    pygame.display.flip()

pygame.quit()
