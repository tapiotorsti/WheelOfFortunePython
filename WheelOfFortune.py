import pygame
import pygame_gui
import math
import random
import pygame.gfxdraw
import json

# Initialize Pygame
pygame.init()

# Screen dimensions and setup
SCREEN_WIDTH, SCREEN_HEIGHT = 1550, 800
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
    "Alpine": ("#032179", "#FD74DB"),
    "Haas": ("#EC1B3E", "#C3C3C3"),
    "RB": ("#1535CE", "#C3C3C3"),
    "Kick": ("#0BE60C", "#000000"),
    "Williams": ("#00A2E0", "#031E43")
}

TEAM_NAMES = list(TEAM_COLORS.keys())

# File to save and load progress
SAVE_FILE = "wheel_progress.json"

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
    "Kick": pygame.image.load("team_logos/kick-logo.png"),
    "Williams": pygame.image.load("team_logos/williams-logo.png")
}

# Define individual logo sizes (width, height)
TEAM_LOGO_SIZES = {
    "Red Bull": (380, 350),
    "Ferrari": (330, 230),
    "Mercedes": (330, 250),
    "McLaren": (300, 300),
    "Aston Martin": (350, 350),
    "Alpine": (60, 60), 
    "Haas": (330, 260),
    "RB": (200, 200),
    "Kick": (330, 250),
    "Williams": (180, 180)
}


# Scale logos with individual sizes
for team in TEAM_LOGOS:
    width, height = TEAM_LOGO_SIZES.get(team, (60, 60)) 
    TEAM_LOGOS[team] = pygame.transform.scale(TEAM_LOGOS[team], (width, height))


# Load F1 car pointer image
arrow_image = pygame.image.load("icon/image.png")
arrow_image = pygame.transform.scale(arrow_image, (80, 40))

# Fonts
font = pygame.font.SysFont("Arial", 16)

# Pygame GUI manager
manager = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT), "theme.json")

# Buttons
BUTTON_X = 1150  # Move buttons further to the right
BUTTON_Y_START = 50  # Slightly higher start position
BUTTON_SPACING = 100  # Increased spacing between buttons


name_input = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect((BUTTON_X, BUTTON_Y_START + 1 * BUTTON_SPACING), (150, 30)),
    manager=manager
)

add_name_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((BUTTON_X, BUTTON_Y_START), (150, 50)),
    text="Lisää kilpailija",
    manager=manager
)

spin_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((BUTTON_X, BUTTON_Y_START + 3 * BUTTON_SPACING), (150, 50)),
    text="Pyöräytä",
    manager=manager
)

zoom_in_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((BUTTON_X, BUTTON_Y_START + 4 * BUTTON_SPACING), (150, 50)),
    text="Suurenna",
    manager=manager
)

delete_name_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((BUTTON_X, BUTTON_Y_START + 2 * BUTTON_SPACING), (150, 50)),
    text="Poista kilpailija",
    manager=manager
)


zoom_out_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((BUTTON_X, BUTTON_Y_START + 5 * BUTTON_SPACING), (150, 50)),
    text="Loitonna",
    manager=manager
)

delete_segment_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((BUTTON_X, BUTTON_Y_START + 6 * BUTTON_SPACING), (150, 50)),
    text="Poista voittaja",
    manager=manager
)

participants_list = pygame_gui.elements.UISelectionList(
    relative_rect=pygame.Rect((BUTTON_X + 190, BUTTON_Y_START), (250, 500)),  # Adjust width and height
    item_list=[],
    manager=manager,
    allow_multi_select=True
)




# Helper function to convert hex to RGB
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

# Save progress to a JSON file
def save_progress(wheels):
    data = []
    for wheel in wheels:
        data.append({
            "team_name": wheel.team_name,
            "participants": wheel.participants
        })
    with open(SAVE_FILE, "w") as file:
        json.dump(data, file, indent=4)
    print("[DEBUG] Progress saved to", SAVE_FILE)

# Load progress from a JSON file
def load_progress(wheels):
    try:
        with open(SAVE_FILE, "r") as file:
            data = json.load(file)
        
        for saved_wheel in data:
            for wheel in wheels:
                if wheel.team_name == saved_wheel["team_name"]:
                    wheel.participants = saved_wheel["participants"]
                    wheel.segment_colors = [wheel.secondary_color] * len(wheel.participants)
        print("[DEBUG] Progress loaded from", SAVE_FILE)

    except FileNotFoundError:
        print("[DEBUG] Save file not found, starting fresh.")

# Delete participant from JSON
def delete_participant_from_json(wheel_name, participant):
    """Delete a participant from the JSON file."""
    try:
        with open(SAVE_FILE, "r") as file:
            data = json.load(file)
        
        # Find the relevant wheel and remove the participant
        for wheel_data in data:
            if wheel_data["team_name"] == wheel_name:
                if participant in wheel_data["participants"]:
                    wheel_data["participants"].remove(participant)
                    break

        # Save the updated data back to the file
        with open(SAVE_FILE, "w") as file:
            json.dump(data, file, indent=4)
        print(f"[DEBUG] Deleted participant '{participant}' from wheel '{wheel_name}' in JSON.")

    except (FileNotFoundError, KeyError, ValueError):
        print(f"[ERROR] Failed to delete participant '{participant}' from JSON.")

# Update participants list box
def update_participants_list(selected_wheel):
    participants_list.set_item_list(selected_wheel.participants)
    print(f"[DEBUG] Updated participants list: {selected_wheel.participants}")  # Logs updated list


# Draw the F1 car pointer
def draw_arrow(surface, draw_x, draw_y, draw_radius):
    arrow_offset = draw_radius + 35
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
            
                # Draw thick lines between segments
                line_color = self.secondary_color
                thickness = 3  # Adjust thickness here
            
                # Calculate line coordinates for the segment boundary
                line_x_start = draw_x + int(inner_radius * math.cos(start_angle))
                line_y_start = draw_y + int(inner_radius * math.sin(start_angle))
                line_x_end = draw_x + int(draw_radius * math.cos(start_angle))
                line_y_end = draw_y + int(draw_radius * math.sin(start_angle))
            
                pygame.draw.line(surface, line_color, (line_x_start, line_y_start), (line_x_end, line_y_end), thickness)


                mid_angle = (start_angle + end_angle) / 2
                text_x = draw_x + int((draw_radius * 0.55) * math.cos(mid_angle))
                text_y = draw_y + int((draw_radius * 0.55) * math.sin(mid_angle))

                text_surface = font.render(participant, True, WHITE)
                text_rect = text_surface.get_rect(center=(text_x, text_y))
                surface.blit(text_surface, text_rect)

        if self.team_name in TEAM_LOGOS:
            logo = TEAM_LOGOS[self.team_name]
            logo_width, logo_height = TEAM_LOGO_SIZES.get(self.team_name, (60, 60))
            logo_rect = logo.get_rect(center=(draw_x, draw_y))
            screen.blit(logo, logo_rect)

        if self.selected and not zoomed:
            pygame.draw.circle(surface, HIGHLIGHT_COLOR, (draw_x, draw_y), draw_radius + 5, 5)

        draw_arrow(surface, draw_x, draw_y, draw_radius)

    def spin(self):
        if not self.spinning:
            self.spinning = True
            self.spin_speed = random.uniform(5, 100)

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
                    adjusted_angle = (normalized_angle + 195) % 360
                    stopped_index = int(adjusted_angle // angle_per_segment) % num_segments
                    self.stopped_segment = self.participants[stopped_index]
                    print(f"[DEBUG] Wheel stopped at segment: {self.stopped_segment} (Index: {stopped_index})")

    def is_clicked(self, mouse_x, mouse_y):
        return math.sqrt((mouse_x - self.x)**2 + (mouse_y - self.y)**2) <= self.radius

# Create wheels dynamically
wheels = []
columns = 4  # Reduce the number of columns to allow more space per wheel
spacing_x = 280  # Increased from 250 for wider horizontal gaps
spacing_y = 250  # Increased from 250 for wider vertical gaps

x_positions = [200 + i * spacing_x for i in range(columns)]
y_positions = [150 + j * spacing_y for j in range((len(TEAM_NAMES) + columns - 1) // columns)]


for i, team_name in enumerate(TEAM_NAMES):
    x = x_positions[i % columns]
    y = y_positions[i // columns]
    primary_color = hex_to_rgb(TEAM_COLORS[team_name][0])
    secondary_color = hex_to_rgb(TEAM_COLORS[team_name][1])
    wheels.append(Wheel(x, y, 100, team_name, primary_color, secondary_color))

# Load progress at startup
load_progress(wheels)
update_participants_list(wheels[0])

# Main loop
running = True
clock = pygame.time.Clock()
selected_wheel = wheels[0]
selected_wheel.selected = True
zoomed_in = False

while running:
    # Limit the frame rate
    time_delta = clock.tick(60) / 1000.0

    # Clear the screen
    screen.fill(WHITE)

    # Zoomed-in wheel rendering
    # Zoomed-in wheel rendering
    if zoomed_in:
        # Draw grey overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill(GREY_OVERLAY)
        screen.blit(overlay, (0, 0))

        # Render other wheels with transparency
        for wheel in wheels:
            if wheel != selected_wheel:
                surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                wheel.draw(surface)
                surface.set_alpha(50)
                screen.blit(surface, (0, 0))

        # Calculate the drawing coordinates for the zoomed-in wheel
        draw_x, draw_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        draw_radius = selected_wheel.radius * 2

        # Draw white background circle under the zoomed-in wheel
        pygame.gfxdraw.filled_circle(screen, draw_x, draw_y, draw_radius + 80, WHITE)

        # Update and draw the zoomed-in wheel
        selected_wheel.update_spin()
        selected_wheel.draw(screen, zoomed=True)

    else:
        # Render all wheels
        for wheel in wheels:
            wheel.update_spin()
            wheel.draw(screen)

    # Event Handling
    for event in pygame.event.get():
        # Debug: Print all events

        # Quit Event
        if event.type == pygame.QUIT:
            save_progress(wheels)
            running = False

        # Mouse Click for Wheel Selection
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_x, mouse_y = event.pos
            for wheel in wheels:
                if wheel.is_clicked(mouse_x, mouse_y):
                    selected_wheel.selected = False
                    selected_wheel = wheel
                    selected_wheel.selected = True
                    update_participants_list(selected_wheel)
                    break

        # Button Pressed Event
        elif event.type == pygame_gui.UI_BUTTON_PRESSED:
            print(f"[DEBUG] Button pressed: {event.ui_element.text}")
            if event.ui_element == add_name_button:
                new_name = name_input.get_text()
                if new_name.strip():
                    selected_wheel.participants.append(new_name)
                    selected_wheel.segment_colors.append(selected_wheel.secondary_color)
                    name_input.set_text("")
                    save_progress(wheels)
                    update_participants_list(selected_wheel)
            elif event.ui_element == spin_button:
                selected_wheel.spin()
            elif event.ui_element == zoom_in_button:
                zoomed_in = True
            elif event.ui_element == zoom_out_button:
                zoomed_in = False
            elif event.ui_element == delete_segment_button:
                if selected_wheel.stopped_segment:
                    stopped_segment = selected_wheel.stopped_segment
                    print(f"[DEBUG] Deleting stopped segment: {stopped_segment}")
                    stopped_index = selected_wheel.participants.index(stopped_segment)
                    del selected_wheel.participants[stopped_index]
                    del selected_wheel.segment_colors[stopped_index]
                    selected_wheel.stopped_segment = None
                    delete_participant_from_json(selected_wheel.team_name, stopped_segment)
                    update_participants_list(selected_wheel)
                else:
                    print("[DEBUG] No stopped segment to delete.")
            elif event.ui_element == delete_name_button:
                selected_items = participants_list.get_multi_selection()
                print(f"[DEBUG] Selected items to delete: {selected_items}")  # Debug selected items

                for item in selected_items:
                    if item in selected_wheel.participants:
                        # Remove the segment color first
                        index = selected_wheel.participants.index(item)  # Get the index before removing
                        selected_wheel.segment_colors.pop(index)  # Remove the corresponding color

                        # Remove the participant
                        selected_wheel.participants.remove(item)  # Remove from wheel's participants list

                        # Remove from JSON
                        delete_participant_from_json(selected_wheel.team_name, item)
                        print(f"[DEBUG] Deleted participant: {item}")

                # Update the displayed list
                update_participants_list(selected_wheel)


        # Selection Events
        elif event.type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION:
            print(f"[DEBUG] Selected item: {event.text}")
        elif event.type == pygame_gui.UI_SELECTION_LIST_DROPPED_SELECTION:
            print(f"[DEBUG] Deselected item: {event.text}")
        elif event.type == pygame_gui.UI_SELECTION_LIST_DOUBLE_CLICKED_SELECTION:
            print(f"[DEBUG] Double-clicked item: {event.text}")

        # Ensure pygame_gui processes all events
        manager.process_events(event)

    # Update and draw the UI
    manager.update(time_delta)
    manager.draw_ui(screen)

    # Update the display
    pygame.display.flip()

# Quit pygame
pygame.quit()



#myenv\Scripts\activate
