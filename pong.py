import pygame
import random

# Constants for the window width and height values
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 720

# RGB values for colors used in the game
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_SPEED_UP = (0, 255, 255)    # Light blue for speed-up gate
COLOR_SLOW_DOWN = (255, 0, 255)   # Magenta for slow-down gate

# Paddle speed and other game parameters
PADDLE_SPEED = 0.8
WINNING_SCORE = 3  # First to 3 points wins
GATE_WIDTH = 5
GATE_HEIGHT = 100
SPEED_UP_FACTOR = 1.3
SLOW_DOWN_FACTOR = 0.7
MAX_GATES = 2
GATE_SPAWN_INTERVAL = 3000  # Time in milliseconds

def main():
    # Game setup
    pygame.init()
    pygame.mixer.init()  # Initialize the mixer for sound
    
    # Load sound effects
    paddle_hit_sfx = pygame.mixer.Sound('sounds/paddle_hit.wav')
    score_sfx = pygame.mixer.Sound('sounds/score.wav')
    speed_up_sfx = pygame.mixer.Sound('sounds/speed_up.wav')
    slow_down_sfx = pygame.mixer.Sound('sounds/slow_down.wav')
    
    # Load and play background music
    pygame.mixer.music.load('sounds/background_music.mp3')
    pygame.mixer.music.set_volume(0.15)
    pygame.mixer.music.play(-1)  # Loop indefinitely
    
    # Create the game window
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Pong Plus')

    # Create the clock object to manage time
    clock = pygame.time.Clock()
    
    # Game state variables
    started = False
    game_over = False
    score_1 = 0
    score_2 = 0

    # Paddles
    paddle_1_rect = pygame.Rect(30, SCREEN_HEIGHT // 2 - 50, 7, 100)
    paddle_2_rect = pygame.Rect(SCREEN_WIDTH - 50, SCREEN_HEIGHT // 2 - 50, 7, 100)
    paddle_1_move = 0
    paddle_2_move = 0

    # Ball
    ball_rect = pygame.Rect(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, 25, 25)
    ball_accel_x = random.choice([0.3, -0.3])
    ball_accel_y = random.choice([0.3, -0.3])

    # Font for displaying text
    font = pygame.font.SysFont('Consolas', 30)

    # Gate variables
    gates = []  # List to store active gates
    last_gate_spawn_time = pygame.time.get_ticks()  # Time since the last gate spawned

    # Game loop
    while True:
        screen.fill(COLOR_BLACK)
        
        # Display the scoreboard
        score_text = font.render(f"{score_1}  |  {score_2}", True, COLOR_WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 50))
        screen.blit(score_text, score_rect)

        # Display start or win message
        if not started or game_over:
            message = 'Press Space to Start' if not game_over else f"Player {'1' if score_1 == WINNING_SCORE else '2'} Wins! Press Space to Restart"
            text = font.render(message, True, COLOR_WHITE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(text, text_rect)
            pygame.display.flip()
            clock.tick(60)

            # Wait for space to start or restart
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if game_over:
                            # Reset the game
                            score_1 = 0
                            score_2 = 0
                            game_over = False
                        started = True
                        gates.clear()  # Clear gates on new game start
            continue

        # Delta time for consistent speed
        delta_time = clock.tick(60)

        # Event handling for exiting the game
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

        # Real-time key check for paddle movement
        keys = pygame.key.get_pressed()
        paddle_1_move = -PADDLE_SPEED if keys[pygame.K_w] else PADDLE_SPEED if keys[pygame.K_s] else 0
        paddle_2_move = -PADDLE_SPEED if keys[pygame.K_UP] else PADDLE_SPEED if keys[pygame.K_DOWN] else 0

        # Move paddles
        paddle_1_rect.top += paddle_1_move * delta_time
        paddle_2_rect.top += paddle_2_move * delta_time
        paddle_1_rect.top = max(0, min(paddle_1_rect.top, SCREEN_HEIGHT - paddle_1_rect.height))
        paddle_2_rect.top = max(0, min(paddle_2_rect.top, SCREEN_HEIGHT - paddle_2_rect.height))

        # Ball collision with top/bottom screen edges
        if ball_rect.top <= 0 or ball_rect.bottom >= SCREEN_HEIGHT:
            ball_accel_y *= -1  # Reverse direction

        # Ball collision with paddles
        if paddle_1_rect.colliderect(ball_rect) and ball_accel_x < 0:
            pygame.mixer.Sound.play(paddle_hit_sfx)
            ball_accel_x *= -1.1  # Reverse and increase speed
            ball_accel_y *= 1.1
            ball_rect.left = paddle_1_rect.right + 5  # Reposition to avoid re-triggering

        if paddle_2_rect.colliderect(ball_rect) and ball_accel_x > 0:
            pygame.mixer.Sound.play(paddle_hit_sfx)
            ball_accel_x *= -1.1  # Reverse and increase speed
            ball_accel_y *= 1.1
            ball_rect.right = paddle_2_rect.left - 5  # Reposition to avoid re-triggering

        # Ball out of bounds - score and reset position
        if ball_rect.left <= 0:  # Player 2 scores
            pygame.mixer.Sound.play(score_sfx)
            score_2 += 1
            started = False
            paddle_1_move = 0
            paddle_2_move = 0
            gates.clear()  # Clear gates on new round
            if score_2 == WINNING_SCORE:
                game_over = True
                pygame.mixer.music.stop()  # Stop background music on game over
            ball_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            ball_accel_x = random.choice([0.3, -0.3])
            ball_accel_y = random.choice([0.3, -0.3])

        elif ball_rect.right >= SCREEN_WIDTH:  # Player 1 scores
            pygame.mixer.Sound.play(score_sfx)
            score_1 += 1
            started = False
            paddle_1_move = 0
            paddle_2_move = 0
            gates.clear()  # Clear gates on new round
            if score_1 == WINNING_SCORE:
                game_over = True
                pygame.mixer.music.stop()  # Stop background music on game over
            ball_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            ball_accel_x = random.choice([0.3, -0.3])
            ball_accel_y = random.choice([0.3, -0.3])

        # Spawn gates periodically
        current_time = pygame.time.get_ticks()
        if len(gates) < MAX_GATES and current_time - last_gate_spawn_time > GATE_SPAWN_INTERVAL:
            x_pos = random.randint(100, SCREEN_WIDTH - 100)
            y_pos = random.randint(50, SCREEN_HEIGHT - 50)
            gate_type = random.choice(['speed_up', 'slow_down'])
            color = COLOR_SPEED_UP if gate_type == 'speed_up' else COLOR_SLOW_DOWN
            gate_rect = pygame.Rect(x_pos, y_pos, GATE_WIDTH, GATE_HEIGHT)
            gates.append({'rect': gate_rect, 'type': gate_type, 'color': color})
            last_gate_spawn_time = current_time

        # Check for ball collision with gates
        for gate in gates[:]:  # Iterate over a copy to allow safe removal
            if gate['rect'].colliderect(ball_rect):
                if gate['type'] == 'speed_up':
                    pygame.mixer.Sound.play(speed_up_sfx)
                    ball_accel_x *= SPEED_UP_FACTOR
                    ball_accel_y *= SPEED_UP_FACTOR
                else:
                    pygame.mixer.Sound.play(slow_down_sfx)
                    ball_accel_x *= SLOW_DOWN_FACTOR
                    ball_accel_y *= SLOW_DOWN_FACTOR
                gates.remove(gate)

        # Move the ball
        if started:
            ball_rect.left += ball_accel_x * delta_time
            ball_rect.top += ball_accel_y * delta_time

        # Draw everything
        pygame.draw.rect(screen, COLOR_WHITE, paddle_1_rect)
        pygame.draw.rect(screen, COLOR_WHITE, paddle_2_rect)
        pygame.draw.ellipse(screen, COLOR_WHITE, ball_rect)

        for gate in gates:
            pygame.draw.rect(screen, gate['color'], gate['rect'])

        pygame.display.flip()

if __name__ == '__main__':
    main()
