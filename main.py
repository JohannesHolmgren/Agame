from random import randint, choice

import pygame
from pygame.locals import *

pygame.init()


class Player(pygame.sprite.Sprite):

    class Attack(pygame.sprite.Sprite):
        def __init__(self, radius, pos):
            super().__init__()
            self.image = pygame.Surface((radius, radius))
            self.image.fill((255, 255, 255))
            self.rect = self.image.get_rect()
            self.rect.center = pos

        def draw(self, win):
            pygame.draw.circle(win, (255, 255, 255), self.rect.center, 150)

    def __init__(self):
        super().__init__()
        self.radius = 20
        self.image = pygame.Surface([self.radius * 2, self.radius * 2])
        pygame.draw.circle(self.image, (255, 0, 0), (self.radius, self.radius),
                           self.radius)        # Draw player as circle
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.attack_range = 150
        self.attack_sprite = None
        self.safe_margin = 50
        self.color = (255, 0, 0)
        self.charged_color = (0, 255, 0)
        self.new_game()

    def draw(self, win):
        win.blit(self.image, self.rect.topleft)

    def move(self):
        (pos_x, pos_y) = pygame.mouse.get_pos()
        self.rect.centerx += (pos_x - self.rect.centerx) / 10
        self.rect.centery += (pos_y - self.rect.centery) / 10

    def update(self, enemies, fruits):
        keys = pygame.key.get_pressed()
        # Move
        self.move()
        # Attack
        self.attack_sprite = None
        if keys[K_SPACE]:
            if self.charge >= 1:
                self.attack(enemies)
                self.charge = 0
                pygame.draw.circle(
                    self.image, self.color, (self.radius, self.radius), self.radius)
        # Fruits
        collected_fruits = pygame.sprite.spritecollide(
            self, fruits, dokill=False)  # Not using circle collision
        for fruit in collected_fruits:
            fruit.kill()
            self.charge += 1
            pygame.draw.circle(self.image, self.charged_color,
                               (self.radius, self.radius), self.radius)
        # Enemies
        hurt = pygame.sprite.spritecollideany(self, enemies)
        if hurt:
            return True
        else:
            return False

    def attack(self, enemies):
        self.attack_sprite = self.Attack(self.attack_range, self.rect.center)
        damaged = pygame.sprite.spritecollide(
            self.attack_sprite,
            enemies,
            dokill=False)        # Not using circle collision
        for enemy in damaged:
            enemy.health -= 1
        self.score += self.get_points(damaged)

    def get_points(self, damaged):
        """ Calculated the number of points for killed enemies,
            including combos etc.
        """
        total_points = len(damaged)
        if len(damaged) > 2:
            total_points += 1
        elif len(damaged) > 3:
            total_points += 2
        elif len(damaged) > 4:
            total_points += 4
        return total_points

    def new_game(self):
        """ Resets necessary attributes for every game """
        self.rect.center = (int(win_x / 2), int(win_y / 2))
        self.score = 0
        self.charge = 0
        pygame.draw.circle(self.image, self.color,
                           (self.radius, self.radius), self.radius)


class Fruit(pygame.sprite.Sprite):

    fruits = pygame.sprite.Group()
    spawn_rate = 120
    spawn_counter = 1

    def __init__(self):
        super().__init__()
        self.radius = 5
        self.image = pygame.Surface([self.radius * 2, self.radius * 2])
        pygame.draw.circle(self.image, (0, 255, 0),
                           (self.radius, self.radius), self.radius)
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.center = [randint(0, win_x), randint(0, win_y)]

    def draw(self, win):
        win.blit(self.image, self.rect.topleft)

    @classmethod
    def spawn_controller(cls):
        cls.spawn_counter += 1
        if cls.spawn_counter % cls.spawn_rate == 0:
            cls.fruits.add(Fruit())

    @classmethod
    def new_game(cls):
        cls.fruits.empty()
        for _ in range(10):
            cls.fruits.add(Fruit())


class Enemy(pygame.sprite.Sprite):

    speed = 1                       # Self-explanatory
    level = 1                       # Controls spawn_rate
    enemies = pygame.sprite.Group()  # Group containing all enemies
    enemy_spawn_rate = 60           # Frames between enemy spawn
    enemy_spawn_counter = 1         # Counter for next spawn

    def __init__(self, player):
        super().__init__()
        self.radius = 10
        self.image = pygame.Surface((self.radius * 2, self.radius * 2))
        pygame.draw.circle(self.image, (0, 255, 255),
                           (self.radius, self.radius), self.radius)
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.center = self.get_start_pos()
        """self.rect.centerx = choice(
            list(range(0, player.rect.x - player.safe_margin)) +
            list(range(player.rect.x + player.safe_margin, win_x)))
        self.rect.centery = choice(
            list(range(0, player.rect.y - player.safe_margin)) +
            list(range(player.rect.y + player.safe_margin, win_y)))
        # self.rect.center = [randint(0, win_x), randint(0, win_y)]
        """
        self.health = 1
        self.enemies.add(self)

    def get_start_pos(self):
        if choice([True, False]):
            # True - spawn on vertical sides (just outside)
            x_pos = choice([-self.radius, win_x + self.radius])
            y_pos = randint(-self.radius, win_y + self.radius)
        else:
            # False - spawn on horizontal sides
            x_pos = randint(-self.radius, win_x + self.radius)
            y_pos = choice([-self.radius, win_y + self.radius])
        return (x_pos, y_pos)

    def draw(self, win):
        win.blit(self.image, self.rect.topleft)

    def update(self, player):
        if self.health <= 0:
            self.kill()
        self.move(player)

    def move(self, player):
        (player_x, player_y) = player.rect.center
        dir_x = (lambda x: -1 if x < 0 else 1)(player_x - self.rect.centerx)
        self.rect.centerx += Enemy.speed * dir_x
        dir_y = (lambda x: -1 if x < 0 else 1)(player_y - self.rect.centery)
        self.rect.centery += Enemy.speed * dir_y

    @classmethod
    def increase_spawn_rate(cls, player):
        if player.score // (cls.level * 10) > 0:
            cls.level += 1
            cls.enemy_spawn_rate = int(cls.get_spawn_rate(cls.level))
            print(cls.enemy_spawn_rate)
        # if not 60 - cls.level * 5 <= 0:
        #     cls.enemy_spawn_rate = 60 - cls.level * 5

    @classmethod
    def get_spawn_rate(cls, level):
        """ How many frames between enemy spawns.

            Start with per 60 frames, then reduce as a
            negative parabola:
                f(x) = -0.3x^2+60
        """
        def f1(x): return -0.3 * x**2 + 60
        def f2(x): return 40 - x
        spawn_rate = f1(level) if level < 10 else f2(level)
        return spawn_rate

    @classmethod
    def spawn_controller(cls, player):
        cls.increase_spawn_rate(player)
        cls.enemy_spawn_counter += 1
        if cls.enemy_spawn_counter % cls.enemy_spawn_rate == 0:
            cls.enemies.add(Enemy(player=player))

    @classmethod
    def new_game(cls):
        cls.level = 1
        cls.enemy_spawn_rate = 60
        cls.enemies.empty()


# Window
win_x, win_y = 800, 600
win = pygame.display.set_mode([win_x, win_y])
pygame.display.set_caption("Game")

# Clock
clock = pygame.time.Clock()
FPS = 60

# UI
font = pygame.font.SysFont("text", 50, bold=True)
# attackBar = pygame.Surface([win_x - 100, 30])
# attackBar.fill((80, 255, 80))

# Player
player = Player()

# Fruits
Fruit.new_game()

# drawing


def redrawGameWindow(win, UI):
    win.fill((0, 0, 0))
    Fruit.fruits.draw(win)
    Enemy.enemies.draw(win)
    player.draw(win)
    for surf, pos in UI.items():
        win.blit(surf, pos)
    pygame.display.update()

# update everything


def updateGameWindow(enemies, fruits):
    game_over = player.update(Enemy.enemies, fruits)
    Enemy.enemies.update(player)
    return game_over


def updateUI(win):
    """ returns a dict of surfaces and pos with the UI """
    score_text = f"Score: {player.score}"
    score = font.render(score_text, False, (255, 255, 255))
    level_text = f"Level: {Enemy.level}"
    level = font.render(level_text, False, (255, 255, 255))

    """ if player.charge >= 1:
        attackBar.fill((0, 255, 80))
    else:
        attackBar.fill((80, 80, 80))
    """
    return {
        score: (0, 0),
        # attackBar: (50, win_y - 40),
        level: (win_x - level.get_width() - 10, 0)}


# Window loop
RUNNING_WINDOW = True
while RUNNING_WINDOW:

    # Game loop
    RUNNING = True
    while RUNNING:
        # For handling exiting
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                RUNNING = False
                RUNNING_WINDOW = False
        # Handle fruits- and enemy spawn
        Fruit.spawn_controller()
        Enemy.spawn_controller(player)
        # Handle UI and Drawing
        UI = updateUI(win)
        redrawGameWindow(win, UI)
        # Update window and check if game over
        game_over = updateGameWindow(Enemy.enemies, Fruit.fruits)
        if game_over:
            RUNNING = False
        # FPS
        clock.tick(FPS)

    if RUNNING_WINDOW:
        # Prepare for game-over text and play again loop
        text = f"GAME OVER --- SCORE: {player.score}"
        gameover = font.render(text, False, (255, 255, 255))
        play_again_text = "PLAY AGAIN? [Y]/[N]"
        play_again = font.render(play_again_text, False, (255, 255, 255))
        GAME_OVER = True
    else:
        # If window closed it shouldn't do anything of below
        GAME_OVER = False

    while GAME_OVER:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                GAME_OVER = False
                RUNNING_WINDOW = False
        win.blit(gameover, (int((win_x - gameover.get_width()) / 2),
                 int((win_y - gameover.get_height()) / 2)))
        win.blit(play_again,
                 ((int((win_x - play_again.get_width()) / 2)),
                  int((win_y - play_again.get_height()) / 2 + 50)))
        keys = pygame.key.get_pressed()
        if keys[K_y]:
            GAME_OVER = False
        elif keys[K_n]:
            GAME_OVER = False
            RUNNING_WINDOW = False
        pygame.display.update()

    if RUNNING_WINDOW:
        player.new_game()
        Enemy.new_game()
        Fruit.new_game()

pygame.quit()
