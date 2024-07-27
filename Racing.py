import pygame
import sys
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = pygame.display.Info().current_w, pygame.display.Info().current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
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
PLAYER_SPEED = 3
BOT_SPEED = 2

# Track settings
LANE_WIDTH = 50
TRACK_RADIUS = 200
TRACK_CENTER = (WIDTH // 2, HEIGHT // 2)
NUM_LANES = 4

# Create players and bots
player = pygame.Rect(0, 0, PLAYER_SIZE, PLAYER_SIZE)
bot1 = pygame.Rect(0, 0, PLAYER_SIZE, PLAYER_SIZE)
bot2 = pygame.Rect(0, 0, PLAYER_SIZE, PLAYER_SIZE)
bot3 = pygame.Rect(0, 0, PLAYER_SIZE, PLAYER_SIZE)

# Finish line
finish_line = pygame.Rect(WIDTH - 50, 0, 50, HEIGHT)

# Fonts
font = pygame.font.Font(None, 74)
lap_font = pygame.font.Font(None, 36)

# Number of laps
NUM_LAPS = 3

def draw_objects():
    screen.fill(BLACK)

    # Draw lanes
    for i in range(NUM_LANES):
        lane_radius = TRACK_RADIUS + i * LANE_WIDTH
        pygame.draw.circle(screen, WHITE, TRACK_CENTER, lane_radius, 2)

    # Draw finish line
    pygame.draw.rect(screen, WHITE, finish_line)

    # Draw player and bots
    pygame.draw.rect(screen, RED, player)
    pygame.draw.rect(screen, GREEN, bot1)
    pygame.draw.rect(screen, BLUE, bot2)
    pygame.draw.rect(screen, YELLOW, bot3)

def update_position(entity, angle, lane_index):
    lane_radius = TRACK_RADIUS + lane_index * LANE_WIDTH
    x = TRACK_CENTER[0] + lane_radius * math.cos(angle)
    y = TRACK_CENTER[1] + lane_radius * math.sin(angle)
    entity.center = (x, y)

def display_winner(winner):
    text = font.render(f'{winner} wins!', True, WHITE)
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))
    pygame.display.flip()
    pygame.time.wait(3000)

def handle_player_input(player_lane_index, last_switch_time):
    current_time = pygame.time.get_ticks()
    if current_time - last_switch_time < 200:  # 200ms delay between switches
        return player_lane_index, False, last_switch_time

    keys = pygame.key.get_pressed()
    new_lane_index = player_lane_index
    lane_changed = False
    if keys[pygame.K_a]:
        new_lane_index = max(0, player_lane_index - 1)
        lane_changed = new_lane_index != player_lane_index
    if keys[pygame.K_d]:
        new_lane_index = min(NUM_LANES - 1, player_lane_index + 1)
        lane_changed = new_lane_index != player_lane_index

    if lane_changed:
        last_switch_time = current_time

    return new_lane_index, lane_changed, last_switch_time

def main():
    clock = pygame.time.Clock()
    game_state = 'MENU'
    countdown_start_time = None
    countdown_seconds = 3

    player_angle = -math.pi / 2
    bot1_angle = -math.pi / 2
    bot2_angle = -math.pi / 2
    bot3_angle = -math.pi / 2
    player_lane_index = 1  # Start in the second lane (0-indexed)
    bot1_lane_index = 0
    bot2_lane_index = 2
    bot3_lane_index = 3
    player_speed = PLAYER_SPEED
    bot_speed = BOT_SPEED

    player_lap_count = 0
    bot1_lap_count = 0
    bot2_lap_count = 0
    bot3_lap_count = 0

    # Initial positions
    update_position(player, player_angle, player_lane_index)
    update_position(bot1, bot1_angle, bot1_lane_index)
    update_position(bot2, bot2_angle, bot2_lane_index)
    update_position(bot3, bot3_angle, bot3_lane_index)

    bot1_switch_timer = pygame.time.get_ticks()
    bot2_switch_timer = pygame.time.get_ticks()
    bot3_switch_timer = pygame.time.get_ticks()
    last_switch_time = 0

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
            # Handle player lane switching
            new_player_lane_index, lane_changed, last_switch_time = handle_player_input(player_lane_index, last_switch_time)
            if lane_changed:
                player_lane_index = new_player_lane_index
                update_position(player, player_angle, player_lane_index)

            # Update bot positions and switch lanes
            current_time = pygame.time.get_ticks()
            if current_time - bot1_switch_timer > 3000:  # Switch every 3 seconds
                bot1_lane_index = (bot1_lane_index + 1) % NUM_LANES
                bot1_switch_timer = current_time
            if current_time - bot2_switch_timer > 4000:  # Switch every 4 seconds
                bot2_lane_index = (bot2_lane_index + 1) % NUM_LANES
                bot2_switch_timer = current_time
            if current_time - bot3_switch_timer > 5000:  # Switch every 5 seconds
                bot3_lane_index = (bot3_lane_index + 1) % NUM_LANES
                bot3_switch_timer = current_time

            # Move bots in a clockwise direction
            bot1_angle += bot_speed / (TRACK_RADIUS + bot1_lane_index * LANE_WIDTH)
            bot2_angle += bot_speed / (TRACK_RADIUS + bot2_lane_index * LANE_WIDTH)
            bot3_angle += bot_speed / (TRACK_RADIUS + bot3_lane_index * LANE_WIDTH)

            # Move player in a clockwise direction
            player_angle += player_speed / (TRACK_RADIUS + player_lane_index * LANE_WIDTH)

            # Update positions
            update_position(player, player_angle, player_lane_index)
            update_position(bot1, bot1_angle, bot1_lane_index)
            update_position(bot2, bot2_angle, bot2_lane_index)
            update_position(bot3, bot3_angle, bot3_lane_index)

            # Check for lap completion and winners
            if player.right >= finish_line.left:
                player_lap_count += 1
                if player_lap_count >= NUM_LAPS:
                    display_winner('Player')
                    game_state = 'MENU'
                    player_lap_count = 0
                    bot1_lap_count = 0
                    bot2_lap_count = 0
                    bot3_lap_count = 0
                player_angle = -math.pi / 2
            if bot1.right >= finish_line.left:
                bot1_lap_count += 1
                if bot1_lap_count >= NUM_LAPS:
                    display_winner('Bot 1')
                    game_state = 'MENU'
                    player_lap_count = 0
                    bot1_lap_count = 0
                    bot2_lap_count = 0
                    bot3_lap_count = 0
                bot1_angle = -math.pi / 2
            if bot2.right >= finish_line.left:
                bot2_lap_count += 1
                if bot2_lap_count >= NUM_LAPS:
                    display_winner('Bot 2')
                    game_state = 'MENU'
                    player_lap_count = 0
                    bot1_lap_count = 0
                    bot2_lap_count = 0
                    bot3_lap_count = 0
                bot2_angle = -math.pi / 2
            if bot3.right >= finish_line.left:
                bot3_lap_count += 1
                if bot3_lap_count >= NUM_LAPS:
                    display_winner('Bot 3')
                    game_state = 'MENU'
                    player_lap_count = 0
                    bot1_lap_count = 0
                    bot2_lap_count = 0
                    bot3_lap_count = 0
                bot3_angle = -math.pi / 2

            draw_objects()

            # Display lap counts
            player_lap_text = lap_font.render(f'Player Laps: {player_lap_count}/{NUM_LAPS}', True, RED)
            bot1_lap_text = lap_font.render(f'Bot 1 Laps: {bot1_lap_count}/{NUM_LAPS}', True, GREEN)
            bot2_lap_text = lap_font.render(f'Bot 2 Laps: {bot2_lap_count}/{NUM_LAPS}', True, BLUE)
            bot3_lap_text = lap_font.render(f'Bot 3 Laps: {bot3_lap_count}/{NUM_LAPS}', True, YELLOW)
            screen.blit(player_lap_text, (10, 10))
            screen.blit(bot1_lap_text, (10, 50))
            screen.blit(bot2_lap_text, (10, 90))
            screen.blit(bot3_lap_text, (10, 130))

            pygame.display.flip()

        clock.tick(60)

if __name__ == '__main__':
    main()
