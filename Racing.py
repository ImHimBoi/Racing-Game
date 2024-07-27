import pygame
import sys
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Four-Lane Racing Game')

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)

# Player settings
PLAYER_SIZE = 20
PLAYER1_SPEED = 3
PLAYER2_SPEED = 3
BOT_SPEED = 2
ACCELERATION = 0.1

# Track settings
LANE_WIDTH = 50
TRACK_RADIUS = 200
TRACK_CENTER = (WIDTH // 2, HEIGHT // 2)
NUM_LANES = 4

# Create players and bots
player1 = pygame.Rect(0, 0, PLAYER_SIZE, PLAYER_SIZE)
player2 = pygame.Rect(0, 0, PLAYER_SIZE, PLAYER_SIZE)
bot1 = pygame.Rect(0, 0, PLAYER_SIZE, PLAYER_SIZE)
bot2 = pygame.Rect(0, 0, PLAYER_SIZE, PLAYER_SIZE)

# Finish line
finish_line = pygame.Rect(WIDTH - 50, 0, 50, HEIGHT)

# Fonts
font = pygame.font.Font(None, 74)

def draw_objects():
    screen.fill(BLACK)

    # Draw lanes
    for i in range(NUM_LANES):
        lane_radius = TRACK_RADIUS + i * LANE_WIDTH
        pygame.draw.circle(screen, WHITE, TRACK_CENTER, lane_radius, 2)

    # Draw finish line
    pygame.draw.rect(screen, WHITE, finish_line)

    # Draw players
    pygame.draw.rect(screen, RED, player1)
    pygame.draw.rect(screen, BLUE, player2)
    pygame.draw.rect(screen, GREEN, bot1)
    pygame.draw.rect(screen, YELLOW, bot2)

def update_player_position(player, angle, speed, lane_index):
    lane_radius = TRACK_RADIUS + lane_index * LANE_WIDTH
    x = TRACK_CENTER[0] + lane_radius * math.cos(angle)
    y = TRACK_CENTER[1] + lane_radius * math.sin(angle)
    player.center = (x, y)

def update_bot_position(bot, angle, speed, lane_index):
    lane_radius = TRACK_RADIUS + lane_index * LANE_WIDTH
    x = TRACK_CENTER[0] + lane_radius * math.cos(angle)
    y = TRACK_CENTER[1] + lane_radius * math.sin(angle)
    bot.center = (x, y)

def display_winner(winner):
    text = font.render(f'{winner} wins!', True, WHITE)
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))
    pygame.display.flip()
    pygame.time.wait(3000)

def main():
    clock = pygame.time.Clock()
    game_state = 'MENU'
    countdown_start_time = None
    countdown_seconds = 3

    player1_angle = -math.pi / 2
    player2_angle = -math.pi / 2
    bot1_angle = 0
    bot2_angle = math.pi / 2
    bot1_lane_index = 0
    bot2_lane_index = 1
    player1_lane_index = 2
    player2_lane_index = 3
    player1_speed = 0
    player2_speed = 0
    bot1_speed = BOT_SPEED
    bot2_speed = BOT_SPEED

    # Initial positions
    update_player_position(player1, player1_angle, player1_speed, player1_lane_index)
    update_player_position(player2, player2_angle, player2_speed, player2_lane_index)
    update_bot_position(bot1, bot1_angle, bot1_speed, bot1_lane_index)
    update_bot_position(bot2, bot2_angle, bot2_speed, bot2_lane_index)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and game_state == 'MENU':
                    game_state = 'COUNTDOWN'
                    countdown_start_time = pygame.time.get_ticks()

        if game_state == 'MENU':
            screen.fill(BLACK)
            text = font.render('Press SPACE to Start', True, WHITE)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))
            pygame.display.flip()

        elif game_state == 'COUNTDOWN':
            current_time = pygame.time.get_ticks()
            elapsed_time = (current_time - countdown_start_time) / 1000

            if elapsed_time > countdown_seconds:
                game_state = 'RACING'
            else:
                countdown_text = font.render(str(countdown_seconds - int(elapsed_time)), True, WHITE)
                screen.fill(BLACK)
                screen.blit(countdown_text, (WIDTH // 2 - countdown_text.get_width() // 2, HEIGHT // 2 - countdown_text.get_height() // 2))
                pygame.display.flip()

        elif game_state == 'RACING':
            keys = pygame.key.get_pressed()

            # Player 1 controls (WASD)
            if keys[pygame.K_w]:
                player1_speed = min(PLAYER1_SPEED, player1_speed + ACCELERATION)
            if keys[pygame.K_s]:
                player1_speed = max(0, player1_speed - ACCELERATION)
            if keys[pygame.K_a]:
                player1_angle -= player1_speed / (TRACK_RADIUS + player1_lane_index * LANE_WIDTH)
            if keys[pygame.K_d]:
                player1_angle += player1_speed / (TRACK_RADIUS + player1_lane_index * LANE_WIDTH)

            # Player 2 controls (Arrow keys)
            if keys[pygame.K_UP]:
                player2_speed = min(PLAYER2_SPEED, player2_speed + ACCELERATION)
            if keys[pygame.K_DOWN]:
                player2_speed = max(0, player2_speed - ACCELERATION)
            if keys[pygame.K_LEFT]:
                player2_angle -= player2_speed / (TRACK_RADIUS + player2_lane_index * LANE_WIDTH)
            if keys[pygame.K_RIGHT]:
                player2_angle += player2_speed / (TRACK_RADIUS + player2_lane_index * LANE_WIDTH)

            # Update bot positions and switch lanes
            bot1_angle += bot1_speed / (TRACK_RADIUS + bot1_lane_index * LANE_WIDTH)
            bot2_angle -= bot2_speed / (TRACK_RADIUS + bot2_lane_index * LANE_WIDTH)
            if bot1_angle % (2 * math.pi) > math.pi:
                bot1_lane_index = (bot1_lane_index + 1) % NUM_LANES
            if bot2_angle % (2 * math.pi) < -math.pi:
                bot2_lane_index = (bot2_lane_index + 1) % NUM_LANES

            # Update positions
            update_player_position(player1, player1_angle, player1_speed, player1_lane_index)
            update_player_position(player2, player2_angle, player2_speed, player2_lane_index)
            update_bot_position(bot1, bot1_angle, bot1_speed, bot1_lane_index)
            update_bot_position(bot2, bot2_angle, bot2_speed, bot2_lane_index)

            # Check for winners
            if player1.right >= finish_line.left:
                display_winner('Player 1')
                game_state = 'MENU'
                player1_angle = -math.pi / 2
                player2_angle = -math.pi / 2
                bot1_angle = 0
                bot2_angle = math.pi / 2
                player1_lane_index = 2
                player2_lane_index = 3
                bot1_lane_index = 0
                bot2_lane_index = 1
                player1_speed = 0
                player2_speed = 0
            elif player2.right >= finish_line.left:
                display_winner('Player 2')
                game_state = 'MENU'
                player1_angle = -math.pi / 2
                player2_angle = -math.pi / 2
                bot1_angle = 0
                bot2_angle = math.pi / 2
                player1_lane_index = 2
                player2_lane_index = 3
                bot1_lane_index = 0
                bot2_lane_index = 1
                player1_speed = 0
                player2_speed = 0

            draw_objects()
            pygame.display.flip()

        clock.tick(60)

if __name__ == '__main__':
    main()
