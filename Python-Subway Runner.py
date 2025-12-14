import pygame
import random
import os

pygame.init()

# ---------------- WINDOW ----------------
WIDTH, HEIGHT = 600, 700
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Subway Runner")

FPS = 60
clock = pygame.time.Clock()

# ---------------- CONSTANTS ----------------
LANES = [150, 300, 450]
GROUND = 580

PLAYER_W, PLAYER_H = 50, 80
COIN_SIZE = 25

GRAVITY = 1
JUMP_VEL = -18

MAGNET_DURATION = 300
SHIELD_DURATION = 300

DAY_COLOR = (200, 200, 200)
NIGHT_COLOR = (40, 40, 60)

WHITE = (255,255,255)
BLACK = (0,0,0)
BLUE = (0,120,255)
RED = (200,0,0)
YELLOW = (255,215,0)
GREEN = (0,200,0)

FONT_BIG = pygame.font.SysFont("arial", 50)
FONT_SMALL = pygame.font.SysFont("arial", 30)

HIGHSCORE_FILE = "highscore.txt"

# ---------------- HIGH SCORE ----------------
def load_highscore():
    if os.path.exists(HIGHSCORE_FILE):
        return int(open(HIGHSCORE_FILE).read())
    return 0

def save_highscore(score):
    open(HIGHSCORE_FILE, "w").write(str(score))

# ---------------- PLAYER ----------------
class Player:
    def __init__(self):
        self.lane = 1
        self.x = LANES[self.lane]
        self.y = GROUND - PLAYER_H
        self.vel_y = 0
        self.jumping = False

        self.magnet = False
        self.magnet_timer = 0
        self.shield = False
        self.shield_timer = 0

    def move(self, d):
        self.lane = max(0, min(2, self.lane + d))

    def jump(self):
        if not self.jumping:
            self.jumping = True
            self.vel_y = JUMP_VEL

    def update(self):
        self.x += (LANES[self.lane] - self.x) * 0.2

        if self.jumping:
            self.y += self.vel_y
            self.vel_y += GRAVITY
            if self.y >= GROUND - PLAYER_H:
                self.y = GROUND - PLAYER_H
                self.jumping = False

        if self.magnet:
            self.magnet_timer -= 1
            if self.magnet_timer <= 0:
                self.magnet = False

        if self.shield:
            self.shield_timer -= 1
            if self.shield_timer <= 0:
                self.shield = False

    def rect(self):
        return pygame.Rect(self.x - 25, self.y, PLAYER_W, PLAYER_H)

    def draw(self):
        body_x = int(self.x)
        body_y = int(self.y)

        # Body
        pygame.draw.ellipse(WIN, (30,144,255),
                            (body_x - 20, body_y + 25, 40, 45))

        # Head
        pygame.draw.circle(WIN, (80,200,255),
                           (body_x, body_y + 15), 18)

        # Eyes
        pygame.draw.circle(WIN, BLACK, (body_x - 6, body_y + 13), 3)
        pygame.draw.circle(WIN, BLACK, (body_x + 6, body_y + 13), 3)

        # Legs animation
        leg_offset = (pygame.time.get_ticks() // 120) % 2 * 6
        pygame.draw.line(WIN, BLACK,
                         (body_x - 10, body_y + 70),
                         (body_x - 10, body_y + 80 + leg_offset), 4)
        pygame.draw.line(WIN, BLACK,
                         (body_x + 10, body_y + 70),
                         (body_x + 10, body_y + 80 - leg_offset), 4)

        # Shield
        if self.shield:
            pygame.draw.circle(WIN, GREEN, (body_x, body_y + 45), 45, 3)

        # Magnet
        if self.magnet:
            pygame.draw.arc(
                WIN, WHITE,
                (body_x - 30, body_y - 5, 60, 60),
                3.14, 0, 4
            )

# ---------------- OBSTACLE ----------------
class Obstacle:
    def __init__(self):
        self.x = random.choice(LANES)
        self.y = -80

    def update(self, speed):
        self.y += speed

    def rect(self):
        return pygame.Rect(self.x - 25, self.y, 50, 80)

    def draw(self):
        pygame.draw.rect(WIN, RED, self.rect(), border_radius=8)

# ---------------- COIN ----------------
class Coin:
    def __init__(self):
        self.x = random.choice(LANES)
        self.y = -20

    def update(self, speed):
        self.y += speed

    def rect(self):
        return pygame.Rect(self.x - COIN_SIZE//2,
                           self.y - COIN_SIZE//2,
                           COIN_SIZE, COIN_SIZE)

    def draw(self):
        pygame.draw.circle(WIN, YELLOW,
                           (int(self.x), int(self.y)), COIN_SIZE//2)

# ---------------- POWERUP ----------------
class PowerUp:
    def __init__(self, kind):
        self.kind = kind
        self.x = random.choice(LANES)
        self.y = -40

    def update(self, speed):
        self.y += speed

    def rect(self):
        return pygame.Rect(self.x - 20, self.y, 40, 40)

    def draw(self):
        color = GREEN if self.kind == "shield" else WHITE
        pygame.draw.rect(WIN, color, self.rect(), border_radius=6)

# ---------------- GAME LOOP ----------------
def game_loop():
    player = Player()
    obstacles, coins, powerups = [], [], []

    score = 0
    speed = 7
    paused = False

    spawn_obs = spawn_coin = spawn_power = 0
    day_timer = 0
    is_day = True

    highscore = load_highscore()

    while True:
        clock.tick(FPS)
        day_timer += 1

        if day_timer >= FPS * 30:
            is_day = not is_day
            day_timer = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = not paused

                if not paused:
                    if event.key == pygame.K_LEFT:
                        player.move(-1)
                    if event.key == pygame.K_RIGHT:
                        player.move(1)
                    if event.key == pygame.K_UP:
                        player.jump()

        if paused:
            WIN.blit(FONT_BIG.render("PAUSED", True, WHITE),
                     (WIDTH//2 - 100, HEIGHT//2))
            pygame.display.update()
            continue

        spawn_obs += 1
        spawn_coin += 1
        spawn_power += 1

        if spawn_obs > 70:
            obstacles.append(Obstacle())
            spawn_obs = 0

        if spawn_coin > 50:
            coins.append(Coin())
            spawn_coin = 0

        if spawn_power > 400:
            powerups.append(PowerUp(random.choice(["magnet","shield"])))
            spawn_power = 0

        player.update()

        for obs in obstacles[:]:
            obs.update(speed)
            if obs.rect().colliderect(player.rect()):
                if player.shield:
                    player.shield = False
                    obstacles.remove(obs)
                else:
                    if score > highscore:
                        save_highscore(score)
                    return "game_over"
            elif obs.y > HEIGHT:
                obstacles.remove(obs)

        for coin in coins[:]:
            if player.magnet and abs(coin.x - player.x) < 150:
                coin.x += (player.x - coin.x) * 0.15
                coin.y += (player.y - coin.y) * 0.15

            coin.update(speed)

            if coin.rect().colliderect(player.rect()):
                score += 1
                coins.remove(coin)
            elif coin.y > HEIGHT:
                coins.remove(coin)

        for p in powerups[:]:
            p.update(speed)
            if p.rect().colliderect(player.rect()):
                if p.kind == "magnet":
                    player.magnet = True
                    player.magnet_timer = MAGNET_DURATION
                else:
                    player.shield = True
                    player.shield_timer = SHIELD_DURATION
                powerups.remove(p)
            elif p.y > HEIGHT:
                powerups.remove(p)

        speed += 0.002

        WIN.fill(DAY_COLOR if is_day else NIGHT_COLOR)

        player.draw()
        for obs in obstacles:
            obs.draw()
        for coin in coins:
            coin.draw()
        for p in powerups:
            p.draw()

        WIN.blit(FONT_SMALL.render(f"Score: {score}", True, BLACK), (20,20))
        WIN.blit(FONT_SMALL.render(f"High: {highscore}", True, BLACK), (20,50))

        pygame.display.update()

# ---------------- GAME OVER ----------------
def game_over_screen():
    while True:
        WIN.fill(BLACK)
        WIN.blit(FONT_BIG.render("GAME OVER", True, WHITE), (160,250))
        WIN.blit(FONT_SMALL.render("Press R to Restart", True, WHITE), (180,320))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                return "restart"

# ---------------- MAIN ----------------
def main():
    while True:
        result = game_loop()

        if result == "game_over":
            result = game_over_screen()

        if result == "restart":
            continue
        if result == "quit":
            break

    pygame.quit()

if __name__ == "__main__":
    main()
