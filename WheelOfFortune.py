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
RED = (255, 0, 0)
GREY_OVERLAY = (50, 50, 50, 150)
HIGHLIGHT_COLOR = (0, 255, 255, 128)

# Hex color codes for each team (Primary, Secondary)
TEAM_COLORS = {
    "Red Bull": ("#00192D", "#EC1B3E"),
    "Ferrari": ("#ED1C24", "#000000"),
    "Mercedes": ("#00B5AE", "#000000"),
    "McLaren": ("#FF8000", "#000000"),
    "Aston Martin": ("#035950", "#000000"),
    "Alpine": ("#FD74DB", "#032179"),
    "Haas": ("#EC1B3E", "#C3C3C3"),
    "RB": ("#1535CE", "#C3C3C3"),
    "Kick": ("#0BE60C", "#000000"),
    "Williams": ("#00A2E0", "#031E43")
}

TEAM_NAMES = list(TEAM_COLORS.keys())

# Load team logos and store them in a dictionary
TEAM_LOGOS = {
    "Red Bull": pygame.image.load("team_logos/red-bull-racing-logo.png"),
    "Ferrari": pygame.image.load("team_logos/ferrari-logo.png"),
    "Mercedes": pygame.image.load("team_logos/mercedes-logo.png"),
    "McLaren": pygame.image.load("team_logos/mclaren-logo.png"),
    "Aston Martin": pygame.image.load("team_logos/aston-martin-logo.png"),
    "Alpine": pygame.image.load("team_logos/alpine-logo.png"),
    "Haas": pygame.image.load("team_logos/haas-logo.png"),
    "RB": pygame.image.load("team_logos/rb-logo.png"),
    "Kick": pygame.image.load("team_logos/kick-sauber-logo.png"),
    "Williams": pygame.image.load("team_logos/williams-logo.png")
}

# Scale logos to fit the inner circle (e.g., 60x60)
for team in TEAM_LOGOS:
    TEAM_LOGOS[team] = pygame.transform.scale(TEAM_LOGOS[team], (60, 60))

# Load F1 car pointer image
arrow_image = pygame.image.load("icon/image.png")
arrow_image = pygame.transform.scale(arrow_image, (80, 40))

# Fonts
font = pygame.font.SysFont("Arial", 16)

# Pygame GUI manager
manager = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT))

# Buttons
BUTTON_X = 1050
BUTTON_Y_START = 120
BUTTON_SPACING = 80

add_name_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((BUTTON_X, BUTTON_Y_START), (150, 50)),
    text="Add Name",
    manager=manager
)

spin_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((BUTTON_X, BUTTON_Y_START + BUTTON_SPACING), (150, 50)),
    text="Spin Wheel",
    manager=manager
)

zoom_in_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((BUTTON_X, BUTTON_Y_START + 2 * BUTTON_SPACING), (150, 50)),
    text="Zoom In",
    manager=manager
)

zoom_out_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((BUTTON_X, BUTTON_Y_START + 3 * BUTTON_SPACING), (150, 50)),
    text="Zoom Out",
    manager=manager
)

delete_segment_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((BUTTON_X, BUTTON_Y_START + 4 * BUTTON_SPACING), (150, 50)),
    text="Delete Segment",
    manager=manager
)

name_input = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect((BUTTON_X, BUTTON_Y_START + 5 * BUTTON_SPACING), (150, 30)),
    manager=manager
)

# Helper function to convert hex to RGB
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

# Draw the F1 car pointer
def draw_arrow(surface, draw_x, draw_y, draw_radius):
    arrow_offset = draw_radius + 10
    arrow_x = draw_x - arrow_offset
    arrow_y = draw_y
    arrow_rect = arrow_image.get_rect(center=(arrow_x, arrow_y))
    surface.blit(arrow_image, arrow_rect)

# Wheel class
class Wheel:
    def __init__(self, x, y, radius, team_name, primary_color, secondary_color):
        self.x = x
        self.y = y
        self.radius = radius
        self.team_name = team_name
        self.primary_color = primary_color
        self.secondary_color = secondary_color
        self.participants = []
        self.segment_colors = []
        self.rotation_angle = 0
        self.spinning = False
        self.spin_speed = 0
        self.stopped_segment = None
        self.selected = False

    def draw(self, surface, zoomed=False):
        draw_radius = self.radius * 2 if zoomed else self.radius
        draw_x, draw_y = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2) if zoomed else (self.x, self.y)

        pygame.gfxdraw.filled_circle(surface, draw_x, draw_y, draw_radius, self.primary_color)
        inner_radius = draw_radius * 0.3
        pygame.gfxdraw.filled_circle(surface, draw_x, draw_y, int(inner_radius), self.secondary_color)

        if self.participants:
            num_segments = len(self.participants)
            angle_per_segment = 360 / num_segments
            default_offset = -angle_per_segment / 2

            for i, participant in enumerate(self.participants):
                start_angle = math.radians(i * angle_per_segment + self.rotation_angle + default_offset)
                end_angle = math.radians((i + 1) * angle_per_segment + self.rotation_angle + default_offset)

                segment_color = self.segment_colors[i]
                pygame.gfxdraw.pie(surface, draw_x, draw_y, draw_radius,
                                   int(math.degrees(start_angle)),
                                   int(math.degrees(end_angle)),
                                   segment_color)

                mid_angle = (start_angle + end_angle) / 2
                text_x = draw_x + int((draw_radius * 0.55) * math.cos(mid_angle))
                text_y = draw_y + int((draw_radius * 0.55) * math.sin(mid_angle))

                text_surface = font.render(participant, True, WHITE)
                text_rect = text_surface.get_rect(center=(text_x, text_y))
                surface.blit(text_surface, text_rect)

        if self.team_name in TEAM_LOGOS:
            logo = TEAM_LOGOS[self.team_name]
            logo_rect = logo.get_rect(center=(draw_x, draw_y))
            surface.blit(logo, logo_rect)

        if self.selected and not zoomed:
            pygame.draw.circle(surface, HIGHLIGHT_COLOR, (draw_x, draw_y), draw_radius + 5, 5)

        draw_arrow(surface, draw_x, draw_y, draw_radius)

    def spin(self):
        if not self.spinning:
            self.spinning = True
            self.spin_speed = random.uniform(5, 10)

    def update_spin(self):
        if self.spinning:
            self.rotation_angle += self.spin_speed
            self.spin_speed *= 0.98
            if self.spin_speed < 0.1:
                self.spinning = False
                self.spin_speed = 0
                num_segments = len(self.participants)
                if num_segments > 0:
                    normalized_angle = (360 - (self.rotation_angle % 360)) % 360
                    angle_per_segment = 360 / num_segments
                    adjusted_angle = (normalized_angle + 270) % 360  # Adjust for 9 o'clock
                    stopped_index = int(adjusted_angle // angle_per_segment) % num_segments
                    self.stopped_segment = self.participants[stopped_index]
                    print(f"[DEBUG] Wheel stopped at segment: {self.stopped_segment} (Index: {stopped_index})")

    def is_clicked(self, mouse_x, mouse_y):
        return math.sqrt((mouse_x - self.x)**2 + (mouse_y - self.y)**2) <= self.radius

# Create wheels dynamically
wheels = []
columns = 4
spacing_x = 250
spacing_y = 250
x_positions = [150 + i * spacing_x for i in range(columns)]
y_positions = [150 + j * spacing_y for j in range((len(TEAM_NAMES) + columns - 1) // columns)]

for i, team_name in enumerate(TEAM_NAMES):
    x = x_positions[i % columns]
    y = y_positions[i // columns]
    primary_color = hex_to_rgb(TEAM_COLORS[team_name][0])
    secondary_color = hex_to_rgb(TEAM_COLORS[team_name][1])
    wheels.append(Wheel(x, y, 100, team_name, primary_color, secondary_color))

# Main loop
running = True
clock = pygame.time.Clock()
selected_wheel = wheels[0]
selected_wheel.selected = True
zoomed_in = False

while running:
    time_delta = clock.tick(60) / 1000.0
    screen.fill(WHITE)

    if zoomed_in:
        # Draw grey background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill(GREY_OVERLAY)
        screen.blit(overlay, (0, 0))

        # Draw other wheels with reduced opacity
        for wheel in wheels:
            if wheel != selected_wheel:
                surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                wheel.draw(surface)
                surface.set_alpha(50)
                screen.blit(surface, (0, 0))

        selected_wheel.update_spin()
        selected_wheel.draw(screen, zoomed=True)
    else:
        for wheel in wheels:
            wheel.update_spin()
            wheel.draw(screen)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button
            mouse_x, mouse_y = event.pos
            for wheel in wheels:
                if wheel.is_clicked(mouse_x, mouse_y):
                    selected_wheel.selected = False
                    selected_wheel = wheel
                    selected_wheel.selected = True
                    break
        elif event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == add_name_button:
                new_name = name_input.get_text()
                if new_name.strip():
                    selected_wheel.participants.append(new_name)
                    selected_wheel.segment_colors.append(selected_wheel.secondary_color)
                    name_input.set_text("")
            elif event.ui_element == spin_button:
                selected_wheel.spin()
            elif event.ui_element == zoom_in_button:
                zoomed_in = True
            elif event.ui_element == zoom_out_button:
                zoomed_in = False
            elif event.ui_element == delete_segment_button:
                if selected_wheel.stopped_segment:
                    print(f"[DEBUG] Deleting stopped segment: {selected_wheel.stopped_segment}")
                    stopped_index = selected_wheel.participants.index(selected_wheel.stopped_segment)
                    del selected_wheel.participants[stopped_index]
                    del selected_wheel.segment_colors[stopped_index]
                    selected_wheel.stopped_segment = None
                else:
                    print("[DEBUG] No stopped segment to delete.")

    manager.process_events(event)
    manager.update(time_delta)
    manager.draw_ui(screen)
    pygame.display.flip()

pygame.quit()


#myenv\Scripts\activate