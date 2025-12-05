import serial
import pygame
import math
import sys
from collections import deque

# Configuration
SERIAL_PORT = 'COM5'  # Change to your Arduino port
BAUD_RATE = 9600
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 700
MAX_RANGE = 400  # Max distance in cm

# Colors
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BRIGHT_GREEN = (0, 255, 100)
DARK_GREEN = (0, 80, 0)
RED = (255, 50, 50)
ORANGE = (255, 150, 0)
YELLOW = (255, 255, 0)
GRAY = (30, 30, 30)
BLUE = (0, 150, 255)

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Arduino Radar - Enhanced")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 28)
small_font = pygame.font.Font(None, 20)

# Radar parameters
center_x = SCREEN_WIDTH // 2
center_y = SCREEN_HEIGHT - 80
radar_radius = min(center_x - 50, center_y - 100)

# Store detections with timestamp for fading
detections = deque(maxlen=180)
sweep_trail = deque(maxlen=20)  # Trail effect for sweep line

# Particle effect for detections
particles = []


class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.life = 255
        self.vx = (pygame.time.get_ticks() % 10 - 5) / 10
        self.vy = (pygame.time.get_ticks() % 10 - 5) / 10

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 8

    def draw(self, screen):
        if self.life > 0:
            color = (255, int(self.life), 0)
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), 2)


try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print(f"Connected to {SERIAL_PORT}")
except Exception as e:
    print(f"Error: Could not open serial port {SERIAL_PORT}")
    print(f"Details: {e}")
    sys.exit(1)


def draw_radar_background():
    """Draw fancy radar background with glow effect"""
    # Draw outer glow
    for i in range(5, 0, -1):
        glow_color = (0, 40 - i * 5, 0)
        pygame.draw.circle(screen, glow_color, (center_x, center_y), radar_radius + i * 3, 2)

    # Draw range circles with labels
    for i in range(1, 5):
        radius = (radar_radius // 4) * i
        alpha = 100 - i * 15
        pygame.draw.circle(screen, DARK_GREEN, (center_x, center_y), radius, 1)

        # Range label with shadow
        distance_label = f"{(MAX_RANGE // 4) * i}cm"
        label = small_font.render(distance_label, True, BRIGHT_GREEN)
        shadow = small_font.render(distance_label, True, (0, 50, 0))
        screen.blit(shadow, (center_x + 6, center_y - radius + 1))
        screen.blit(label, (center_x + 5, center_y - radius))

    # Draw angle lines
    for angle in range(0, 181, 15):
        rad = math.radians(angle)
        end_x = center_x + radar_radius * math.cos(math.pi - rad)
        end_y = center_y - radar_radius * math.sin(math.pi - rad)

        # Thicker lines at major angles
        thickness = 2 if angle % 30 == 0 else 1
        color = DARK_GREEN if angle % 30 == 0 else GRAY
        pygame.draw.line(screen, color, (center_x, center_y), (end_x, end_y), thickness)

    # Draw angle labels at major angles
    for angle in range(0, 181, 30):
        rad = math.radians(angle)
        label_dist = radar_radius + 30
        label_x = center_x + label_dist * math.cos(math.pi - rad)
        label_y = center_y - label_dist * math.sin(math.pi - rad)
        label = font.render(f"{angle}°", True, BRIGHT_GREEN)
        shadow = font.render(f"{angle}°", True, (0, 50, 0))
        screen.blit(shadow, (label_x - 14, label_y - 9))
        screen.blit(label, (label_x - 15, label_y - 10))

    # Draw center dot
    pygame.draw.circle(screen, BRIGHT_GREEN, (center_x, center_y), 5)
    pygame.draw.circle(screen, GREEN, (center_x, center_y), 3)


def draw_sweep_line(angle):
    """Draw sweep line with trailing effect"""
    rad = math.radians(angle)
    end_x = center_x + radar_radius * math.cos(math.pi - rad)
    end_y = center_y - radar_radius * math.sin(math.pi - rad)

    # Add current position to trail
    sweep_trail.append((end_x, end_y))

    # Draw fading trail
    trail_len = len(sweep_trail)
    for i, (x, y) in enumerate(sweep_trail):
        alpha = int(255 * (i / trail_len))
        color = (0, alpha, 0)
        thickness = max(1, int(3 * (i / trail_len)))
        pygame.draw.line(screen, color, (center_x, center_y), (x, y), thickness)

    # Draw main sweep line with glow
    pygame.draw.line(screen, BRIGHT_GREEN, (center_x, center_y), (end_x, end_y), 3)
    pygame.draw.line(screen, (150, 255, 150), (center_x, center_y), (end_x, end_y), 1)


def draw_detections():
    """Draw detections with fading effect"""
    current_time = pygame.time.get_ticks()

    for i, (angle, distance, timestamp) in enumerate(detections):
        if distance >= MAX_RANGE or distance <= 0:
            continue

        # Calculate fade based on age
        age = current_time - timestamp
        fade_duration = 3000  # 3 seconds
        alpha = max(0, 255 - int(255 * (age / fade_duration)))

        if alpha > 0:
            # Convert polar to cartesian
            rad = math.radians(angle)
            scale = radar_radius / MAX_RANGE
            x = center_x + distance * scale * math.cos(math.pi - rad)
            y = center_y - distance * scale * math.sin(math.pi - rad)

            # Color gradient based on distance
            if distance < 100:
                color = (255, int(alpha * 0.3), 0)  # Close - red/orange
            elif distance < 200:
                color = (255, int(alpha * 0.7), 0)  # Medium - orange/yellow
            else:
                color = (int(alpha * 0.5), alpha, 0)  # Far - yellow/green

            # Draw detection with glow
            size = max(2, int(6 * (alpha / 255)))
            pygame.draw.circle(screen, color, (int(x), int(y)), size + 2)
            pygame.draw.circle(screen, (255, 255, 255), (int(x), int(y)), size)


def draw_ui():
    """Draw UI elements"""
    # Draw semi-transparent panel
    panel = pygame.Surface((280, 120))
    panel.set_alpha(200)
    panel.fill((10, 10, 10))
    screen.blit(panel, (10, 10))

    # Get latest detection info
    if detections:
        angle, distance, _ = detections[-1]

        # Angle info
        angle_text = font.render(f"Angle: {angle}°", True, BRIGHT_GREEN)
        screen.blit(angle_text, (20, 20))

        # Distance info with color coding
        if distance < MAX_RANGE and distance > 0:
            if distance < 100:
                dist_color = RED
                status = "CLOSE"
            elif distance < 200:
                dist_color = ORANGE
                status = "MEDIUM"
            else:
                dist_color = YELLOW
                status = "FAR"

            dist_text = font.render(f"Distance: {distance}cm", True, dist_color)
            status_text = small_font.render(f"[{status}]", True, dist_color)
        else:
            dist_text = font.render("Distance: OUT OF RANGE", True, GRAY)
            status_text = small_font.render("[---]", True, GRAY)

        screen.blit(dist_text, (20, 55))
        screen.blit(status_text, (20, 85))

    # Instructions
    instruction = small_font.render("Press ESC to exit", True, DARK_GREEN)
    screen.blit(instruction, (SCREEN_WIDTH - 150, SCREEN_HEIGHT - 30))


# Main loop
running = True
current_angle = 0
last_detection_pos = None

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    # Read data from Arduino
    try:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').strip()
            if ',' in line:
                parts = line.split(',')
                angle = int(parts[0])
                distance = int(parts[1])
                current_angle = angle
                timestamp = pygame.time.get_ticks()

                # Add detection with timestamp
                detections.append((angle, distance, timestamp))

                # Create particles for close detections
                if distance < 150 and distance > 0:
                    rad = math.radians(angle)
                    scale = radar_radius / MAX_RANGE
                    x = center_x + distance * scale * math.cos(math.pi - rad)
                    y = center_y - distance * scale * math.sin(math.pi - rad)

                    # Add particles
                    for _ in range(3):
                        particles.append(Particle(x, y))

    except Exception as e:
        print(f"Error reading serial: {e}")

    # Update particles
    particles = [p for p in particles if p.life > 0]
    for particle in particles:
        particle.update()

    # Draw everything
    screen.fill(BLACK)
    draw_radar_background()
    draw_detections()

    # Draw particles
    for particle in particles:
        particle.draw(screen)

    draw_sweep_line(current_angle)
    draw_ui()

    # Draw title
    title = font.render("RADAR SCANNER", True, BRIGHT_GREEN)
    title_shadow = font.render("RADAR SCANNER", True, (0, 80, 0))
    screen.blit(title_shadow, (SCREEN_WIDTH // 2 - 90, 11))
    screen.blit(title, (SCREEN_WIDTH // 2 - 91, 10))

    pygame.display.flip()
    clock.tick(60)

# Cleanup
ser.close()
pygame.quit()
print("Radar closed")