import pygame
import math
import sys
import time
import random
from pygame.locals import *

def read_personal_best(filename):
    try:
        with open(filename, 'r') as file:
            return float(file.read().strip())
    except FileNotFoundError:
        return float('inf')
    except ValueError:
        return float('inf')

def write_personal_best(filename, time):
    with open(filename, 'w') as file:
        file.write(str(time))

def level1():
    pygame.init()
    WIDTH, HEIGHT = 1024, 768
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 75)
    win_font = pygame.font.Font(None, 50)
    small_font = pygame.font.Font(None, 36)
    stopwatch_start_time = time.time()
    car_crashed = False
    laps_completed = 0
    win_text = font.render('', True, (0, 255, 0))
    loss_text = font.render('', True, (255, 0, 0))
    personal_best_file = 'personal_best.txt'

    # Read the personal best time from the file
    personal_best_time = read_personal_best(personal_best_file)

    class CarSprite(pygame.sprite.Sprite):
        MAX_FORWARD_SPEED = 10
        MAX_REVERSE_SPEED = 10
        ACCELERATION = 2
        TURN_SPEED = 5

        def __init__(self, image, position):
            pygame.sprite.Sprite.__init__(self)
            self.src_image = pygame.image.load(image)
            self.position = position
            self.speed = 0
            self.direction = 0
            self.k_left = self.k_right = self.k_down = self.k_up = 0

        def update(self, deltat):
            self.speed += (self.k_up + self.k_down)
            if self.speed > self.MAX_FORWARD_SPEED:
                self.speed = self.MAX_FORWARD_SPEED
            if self.speed < -self.MAX_REVERSE_SPEED:
                self.speed = -self.MAX_REVERSE_SPEED
            self.direction += (self.k_right + self.k_left)
            x, y = self.position
            rad = self.direction * math.pi / 180
            x += -self.speed * math.sin(rad)
            y += -self.speed * math.cos(rad)
            self.position = (x, y)
            self.image = pygame.transform.rotate(self.src_image, self.direction)
            self.rect = self.image.get_rect()
            self.rect.center = self.position

    class ObstacleSprite(pygame.sprite.Sprite):
        def __init__(self, image, position):
            pygame.sprite.Sprite.__init__(self)
            self.src_image = pygame.image.load(image)
            self.image = self.src_image
            self.rect = self.image.get_rect()
            self.rect.center = position
            # Adjust hitbox (bounding box) to be smaller than the obstacle image
            self.hitbox = pygame.Rect(self.rect.centerx - 10, self.rect.centery - 10, 20, 20)  # Smaller hitbox

        def update(self):
            # Sync hitbox with image position
            self.hitbox.center = self.rect.center

    center = (2000, 1000)
    inner_a, inner_b = 1600, 800
    outer_a, outer_b = 2200, 1100

    car_start_pos = (center[0] - 20, center[1] - (inner_b + outer_b) / 2 + 10)
    car = CarSprite('images/car.png', car_start_pos)
    car.direction = -90
    car_group = pygame.sprite.RenderPlain(car)

    # Generate a dense population of obstacles
    obstacles = pygame.sprite.Group()
    num_obstacles = 100  # Increased number of obstacles for more density
    for _ in range(num_obstacles):
        angle = random.uniform(0, 2 * math.pi)
        radius_a = random.uniform(inner_a, outer_a)  # Randomize horizontal distance
        radius_b = random.uniform(inner_b, outer_b)  # Randomize vertical distance
        x = center[0] + radius_a * math.cos(angle)
        y = center[1] + radius_b * math.sin(angle)
        obstacle = ObstacleSprite('images/trophy.png', (x, y))
        obstacles.add(obstacle)

    lap_start = False
    start_angle = math.pi / 2
    current_angle = start_angle
    last_angle = start_angle
    clockwise = False

    def draw_oval(surface, color, rect, width=0):
        pygame.draw.ellipse(surface, color, rect, width)

    def point_inside_ellipse(x, y, cx, cy, a, b):
        return ((x - cx) ** 2 / a ** 2 + (y - cy) ** 2 / b ** 2) <= 1

    while True:
        t1 = time.time()
        deltat = clock.tick(30)

        for event in pygame.event.get():
            if not hasattr(event, 'key'): continue
            down = event.type == KEYDOWN
            if not car_crashed:
                if event.key == K_RIGHT:
                    car.k_right = down * -5
                elif event.key == K_LEFT:
                    car.k_left = down * 5
                elif event.key == K_UP:
                    car.k_up = down * 2
                elif event.key == K_DOWN:
                    car.k_down = down * -2
                elif event.key == K_ESCAPE:
                    sys.exit(0)
            elif car_crashed and event.key == K_SPACE:
                level1()
                return  # Exit current loop to restart the level
            elif event.key == K_ESCAPE:
                sys.exit(0)

        # Stopwatch
        stopwatch_time = time.time() - stopwatch_start_time
        stopwatch_text = font.render(f'Time: {int(stopwatch_time // 60):02}:{int(stopwatch_time % 60):02}', True, (255, 255, 0))

        screen.fill((0, 100, 0))
        car_group.update(deltat)

        # Update obstacle hitboxes
        for obstacle in obstacles:
            obstacle.update()

        x, y = car.position
        cx, cy = center
        car_width, car_height = car.rect.size

        corners = [
            (x - car_width / 2, y - car_height / 2),
            (x + car_width / 2, y - car_height / 2),
            (x - car_width / 2, y + car_height / 2),
            (x + car_width / 2, y + car_height / 2)
        ]

        on_track = all(
            point_inside_ellipse(corner[0], corner[1], cx, cy, outer_a, outer_b) and
            not point_inside_ellipse(corner[0], corner[1], cx, cy, inner_a, inner_b)
            for corner in corners
        )

        # Check for collisions with smaller hitboxes
        if not on_track or any(obstacle.hitbox.colliderect(car.rect) for obstacle in obstacles):
            if not car_crashed:  # Crash only once
                car_crashed = True
                car.image = pygame.image.load('images/collision.png')
                car.MAX_FORWARD_SPEED = 0
                car.MAX_REVERSE_SPEED = 0
                car.k_right = 0
                car.k_left = 0
                loss_text = win_font.render('Press Space to Restart', True, (255, 0, 0))

                # Check and update personal best time
                if stopwatch_time < personal_best_time:
                    write_personal_best(personal_best_file, stopwatch_time)
                    personal_best_time = stopwatch_time

        if car_crashed:
            screen.blit(loss_text, (250, 700))
            # Display personal best time
            personal_best_text = small_font.render(f'Personal Best: {int(personal_best_time // 60):02}:{int(personal_best_time % 60):02}', True, (255, 255, 255))
            screen.blit(personal_best_text, (20, 160))
        else:
            # Calculate and display race completion
            last_angle = current_angle
            current_angle = math.atan2(center[1] - y, x - center[0])
            if current_angle < 0:
                current_angle += 2 * math.pi

            angle_diff = (current_angle - last_angle + math.pi) % (2 * math.pi) - math.pi
            if angle_diff > 0:
                clockwise = True
            elif angle_diff < 0:
                clockwise = False

            if not lap_start and car.speed != 0:
                lap_start = True

            if lap_start and current_angle < start_angle and last_angle > start_angle and not clockwise:
                laps_completed += 1
                lap_start = False

            completion_text = small_font.render(f'Laps Completed: {laps_completed}', True, (255, 255, 255))

            offset_x = WIDTH // 2 - car.position[0]
            offset_y = HEIGHT // 2 - car.position[1]

            outer_rect = pygame.Rect(center[0] - outer_a + offset_x, center[1] - outer_b + offset_y, 2 * outer_a,
                                     2 * outer_b)
            inner_rect = pygame.Rect(center[0] - inner_a + offset_x, center[1] - inner_b + offset_y, 2 * inner_a,
                                     2 * inner_b)
            draw_oval(screen, (128, 128, 128), outer_rect)
            draw_oval(screen, (0, 100, 0), inner_rect)

            draw_oval(screen, (255, 255, 255), outer_rect, 2)
            draw_oval(screen, (255, 255, 255), inner_rect, 2)

            start_pos = (center[0] + offset_x, center[1] - outer_b + offset_y)
            end_pos = (center[0] + offset_x, center[1] - inner_b + offset_y)
            pygame.draw.line(screen, (255, 0, 0), start_pos, end_pos, 5)

            screen.blit(car.image, (WIDTH // 2 - car.image.get_width() // 2, HEIGHT // 2 - car.image.get_height() // 2))

            # Draw obstacles
            for obstacle in obstacles:
                screen.blit(obstacle.image, (obstacle.rect.x + offset_x, obstacle.rect.y + offset_y))

            screen.blit(stopwatch_text, (20, 60))
            screen.blit(completion_text, (20, 120))

        pygame.display.flip()

if __name__ == "__main__":
    level1()
