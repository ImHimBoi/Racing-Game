import pygame
import math
import sys
import time
from pygame.locals import *

def level1():
    pygame.init()
    WIDTH, HEIGHT = 1024, 768
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 75)
    win_font = pygame.font.Font(None, 50)
    small_font = pygame.font.Font(None, 36)
    win_condition = None
    win_text = font.render('', True, (0, 255, 0))
    loss_text = font.render('', True, (255, 0, 0))
    t0 = time.time()

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

    class AICarSprite(CarSprite):
        def __init__(self, image, position, waypoints):
            super().__init__(image, position)
            self.waypoints = waypoints
            self.current_waypoint = 0
            self.target_speed = self.MAX_FORWARD_SPEED * 0.75
            self.safe_distance = 150  # Increased safe distance
            self.rect = self.src_image.get_rect(center=position)
            self.exploded = False

        def update(self, deltat, player_car, center, inner_a, inner_b, outer_a, outer_b):
            if self.exploded:
                return

            if self.current_waypoint < len(self.waypoints):
                target_x, target_y = self.waypoints[self.current_waypoint]
                dx = target_x - self.position[0]
                dy = target_y - self.position[1]
                distance = math.hypot(dx, dy)

                if distance < 50:
                    self.current_waypoint = (self.current_waypoint + 1) % len(self.waypoints)
                else:
                    angle_to_target = math.degrees(math.atan2(-dy, dx))
                    angle_diff = (angle_to_target - self.direction + 180) % 360 - 180

                # Adjust steering based on track boundaries
                    cx, cy = center
                    x, y = self.position
                    distance_to_center = math.hypot(x - cx, y - cy)
                    angle_to_center = math.degrees(math.atan2(cy - y, cx - x))

                    if distance_to_center > (outer_a + outer_b) / 2 - self.safe_distance:
                        angle_diff = (angle_to_center - self.direction + 180) % 360 - 180
                    elif distance_to_center < (inner_a + inner_b) / 2 + self.safe_distance:
                        angle_diff = (angle_to_center + 180 - self.direction + 180) % 360 - 180

                    if abs(angle_diff) > 10:
                        self.k_right = -1 if angle_diff > 0 else 0
                        self.k_left = 1 if angle_diff < 0 else 0
                    else:
                        self.k_right = 0
                        self.k_left = 0

                    turn_sharpness = abs(angle_diff) / 180
                    self.target_speed = self.MAX_FORWARD_SPEED * (1 - turn_sharpness * 0.7)

                    self.k_up = 1 if self.speed < self.target_speed else 0
                    self.k_down = 1 if self.speed > self.target_speed else 0

                # Collision avoidance with player car
                player_x, player_y = player_car.position
                if math.hypot(player_x - self.position[0], player_y - self.position[1]) < 200:  # Increased avoidance distance
                    avoid_angle = math.degrees(math.atan2(self.position[1] - player_y, self.position[0] - player_x))
                    angle_diff = (avoid_angle - self.direction + 180) % 360 - 180
                    self.k_right = -1 if angle_diff > 0 else 0
                    self.k_left = 1 if angle_diff < 0 else 0
                    self.target_speed = self.MAX_FORWARD_SPEED * 0.5

            # Check if AI car is off the road
            x, y = self.position
            cx, cy = center
            car_width, car_height = self.rect.size

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

            if not on_track:
                self.image = pygame.image.load('images/collision.png')
                self.rect = self.image.get_rect(center=self.position)
                self.MAX_FORWARD_SPEED = 0
                self.MAX_REVERSE_SPEED = 0
                self.k_right = 0
                self.k_left = 0
                self.exploded = True  # Set exploded flag to True
                return

            super().update(deltat)
            self.rect = self.image.get_rect()
            self.rect.center = self.position


    def generate_waypoints(center, inner_a, inner_b, outer_a, outer_b, num_points=100):
        waypoints = []
        for i in range(num_points):
            angle = 2 * math.pi * i / num_points
            # Generate waypoints closer to the middle of the track
            x = center[0] + (inner_a * 1.2 + outer_a * 0.8) / 2 * math.cos(angle)
            y = center[1] + (inner_b * 1.2 + outer_b * 0.8) / 2 * math.sin(angle)
            waypoints.append((x, y))
        return waypoints

    center = (2000, 1000)
    inner_a, inner_b = 1600, 800
    outer_a, outer_b = 2200, 1100

    car_start_pos = (center[0] - 20, center[1] - (inner_b + outer_b) / 2 + 10)
    car = CarSprite('images/car.png', car_start_pos)
    car.direction = -90
    car_group = pygame.sprite.RenderPlain(car)

    waypoints = generate_waypoints(center, inner_a, inner_b, outer_a, outer_b, num_points=100)

    ai_car_start_pos = (center[0] + 20, center[1] - (inner_b + outer_b) / 2 + 10)
    ai_car = AICarSprite('images/ai_car.png', ai_car_start_pos, waypoints)
    ai_car.direction = -90
    ai_car_group = pygame.sprite.RenderPlain(ai_car)

    lap_start = False
    lap_complete = False
    start_angle = math.pi / 2
    current_angle = start_angle
    last_angle = start_angle
    clockwise = False

    def draw_oval(surface, color, rect, width=0):
        pygame.draw.ellipse(surface, color, rect, width)

    def point_inside_ellipse(x, y, cx, cy, a, b):
        return ((x - cx)**2 / a**2 + (y - cy)**2 / b**2) <= 1

    while 1:
        t1 = time.time()
        dt = t1 - t0
        deltat = clock.tick(30)

        for event in pygame.event.get():
            if not hasattr(event, 'key'): continue
            down = event.type == KEYDOWN 
            if win_condition == None: 
                if event.key == K_RIGHT: car.k_right = down * -5 
                elif event.key == K_LEFT: car.k_left = down * 5
                elif event.key == K_UP: car.k_up = down * 2
                elif event.key == K_DOWN: car.k_down = down * -2 
                elif event.key == K_ESCAPE: sys.exit(0)
            elif (win_condition == True or win_condition == False) and event.key == K_SPACE:
                level1()
                t0 = t1
            elif event.key == K_ESCAPE: sys.exit(0)    
    
        seconds = round((60 - dt), 2)
        if win_condition == None:
            timer_text = font.render(str(seconds), True, (255, 255, 0))
            if seconds <= 0:
                win_condition = False
                timer_text = font.render("Time!", True, (255, 0, 0))
                loss_text = win_font.render('Press Space to Retry', True, (255, 0, 0))
        
        screen.fill((0, 100, 0))
        car_group.update(deltat)
        ai_car_group.update(deltat, car, center, inner_a, inner_b, outer_a, outer_b)

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

        if not on_track:
            win_condition = False
            timer_text = font.render("Crash!", True, (255, 0, 0))
            car.image = pygame.image.load('images/collision.png')
            loss_text = win_font.render('Press Space to Retry', True, (255, 0, 0))
            car.MAX_FORWARD_SPEED = 0
            car.MAX_REVERSE_SPEED = 0
            car.k_right = 0
            car.k_left = 0

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

        if lap_start and current_angle < start_angle and last_angle > start_angle and not clockwise and race_completion > 95:
            lap_complete = True

        if lap_complete:
            win_condition = True
            timer_text = font.render("Lap Complete!", True, (0, 255, 0))
            win_text = win_font.render('Press Space to Restart', True, (0, 255, 0))

        if clockwise:
            race_completion = 0
        else:
            race_completion = ((start_angle - current_angle) % (2 * math.pi)) / (2 * math.pi) * 100
        completion_text = small_font.render(f'Race Completion: {race_completion:.1f}%', True, (255, 255, 255))

        offset_x = WIDTH // 2 - car.position[0]
        offset_y = HEIGHT // 2 - car.position[1]

        outer_rect = pygame.Rect(center[0] - outer_a + offset_x, center[1] - outer_b + offset_y, 2 * outer_a, 2 * outer_b)
        inner_rect = pygame.Rect(center[0] - inner_a + offset_x, center[1] - inner_b + offset_y, 2 * inner_a, 2 * inner_b)
        draw_oval(screen, (128, 128, 128), outer_rect)
        draw_oval(screen, (0, 100, 0), inner_rect)

        draw_oval(screen, (255, 255, 255), outer_rect, 2)
        draw_oval(screen, (255, 255, 255), inner_rect, 2)

        start_pos = (center[0] + offset_x, center[1] - outer_b + offset_y)
        end_pos = (center[0] + offset_x, center[1] - inner_b + offset_y)
        pygame.draw.line(screen, (255, 0, 0), start_pos, end_pos, 5)

        screen.blit(car.image, (WIDTH // 2 - car.image.get_width() // 2, HEIGHT // 2 - car.image.get_height() // 2))
        screen.blit(ai_car.image, (ai_car.rect.x + offset_x, ai_car.rect.y + offset_y))

        screen.blit(timer_text, (20, 60))
        screen.blit(win_text, (250, 700))
        screen.blit(loss_text, (250, 700))
        screen.blit(completion_text, (20, 120))

        if pygame.sprite.collide_rect(car, ai_car):
            win_condition = False
            timer_text = font.render("Collision!", True, (255, 0, 0))
            car.image = pygame.image.load('images/collision.png')
            ai_car.image = pygame.image.load('images/collision.png')
            loss_text = win_font.render('Press Space to Retry', True, (255, 0, 0))
            car.MAX_FORWARD_SPEED = 0
            car.MAX_REVERSE_SPEED = 0
            ai_car.MAX_FORWARD_SPEED = 0
            ai_car.MAX_REVERSE_SPEED = 0
            car.k_right = 0
            car.k_left = 0
            ai_car.k_right = 0
            ai_car.k_left = 0
        
        pygame.display.flip()

if __name__ == "__main__":
    level1()