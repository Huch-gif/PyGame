import pygame
import random
import os

# Инициализация Pygame
pygame.init()

# Константы экрана
WIDTH, HEIGHT = 800, 600
FPS = 60

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)

# Путь к ресурсам
ASSETS_DIR = "assets"

# Настройки игрока
PLAYER_SIZE = (64, 64)
PLAYER_SPEED = 4
ANIMATION_SPEED = 150  # мс между кадрами

# Настройки врагов
ENEMY_SIZE = (40, 40)
ENEMY_SPEED_BASE = 1.5
SPAWN_RATE_BASE = 90

# Создание экрана
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Игра на выживание")

clock = pygame.time.Clock()

# Загрузка изображений
def load_image(path):
    try:
        image = pygame.image.load(path).convert_alpha()
        return image
    except FileNotFoundError:
        print(f"Файл {path} не найден.")
        return None

# Загрузка анимаций
def load_animation(folder, prefix, count, size):
    animation = []
    for i in range(count):
        path = os.path.join(ASSETS_DIR, folder, f"{prefix}_{i}.png")
        img = load_image(path)
        if img:
            animation.append(pygame.transform.scale(img, size))
    return animation or [pygame.Surface(size)]

# Функция воспроизведения звука
def load_sound(path):
    try:
        return pygame.mixer.Sound(path)
    except Exception as e:
        print(f"Ошибка загрузки звука {path}: {e}")
        return None

# Анимированный игрок
class AnimatedPlayer:
    def __init__(self):
        self.direction = 'down'
        self.animations = {
            'idle': load_animation('player', 'idle', 1, PLAYER_SIZE),
            'up': load_animation('player', 'walk_up', 2, PLAYER_SIZE),
            'down': load_animation('player', 'walk_down', 2, PLAYER_SIZE),
            'left': load_animation('player', 'walk_left', 2, PLAYER_SIZE),
            'right': load_animation('player', 'walk_right', 2, PLAYER_SIZE)
        }
        self.current_animation = self.animations['down']
        self.frame_index = 0
        self.image = self.current_animation[self.frame_index]
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.last_update = pygame.time.get_ticks()

    def update_direction(self, dx, dy):
        if dx < 0:
            self.direction = 'left'
        elif dx > 0:
            self.direction = 'right'
        elif dy < 0:
            self.direction = 'up'
        elif dy > 0:
            self.direction = 'down'

    def animate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > ANIMATION_SPEED:
            self.last_update = now
            self.frame_index = (self.frame_index + 1) % len(self.current_animation)
            self.image = self.current_animation[self.frame_index]

    def move(self, dx, dy):
        self.update_direction(dx, dy)
        self.rect.x += dx * PLAYER_SPEED
        self.rect.y += dy * PLAYER_SPEED
        self.rect.clamp_ip(screen.get_rect())

        # Выбор анимации
        if dx != 0 or dy != 0:
            self.current_animation = self.animations[self.direction]
        else:
            self.current_animation = self.animations['idle']

        self.animate()

    def draw(self):
        screen.blit(self.image, self.rect.topleft)

# Класс врага
class Enemy:
    def __init__(self, speed):
        self.animations = {
            'walk': load_animation('enemy', 'walk', 2, ENEMY_SIZE)
        }
        self.current_animation = self.animations['walk']
        self.frame_index = 0
        self.image = self.current_animation[self.frame_index]
        self.rect = self.image.get_rect()
        self.speed = speed
        self.last_update = pygame.time.get_ticks()

        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top':
            self.rect.x = random.randint(0, WIDTH - ENEMY_SIZE[0])
            self.rect.y = -ENEMY_SIZE[1]
            self.direction = [random.uniform(-1, 1), 1]
        elif side == 'bottom':
            self.rect.x = random.randint(0, WIDTH - ENEMY_SIZE[0])
            self.rect.y = HEIGHT + ENEMY_SIZE[1]
            self.direction = [random.uniform(-1, 1), -1]
        elif side == 'left':
            self.rect.x = -ENEMY_SIZE[0]
            self.rect.y = random.randint(0, HEIGHT - ENEMY_SIZE[1])
            self.direction = [1, random.uniform(-1, 1)]
        else:
            self.rect.x = WIDTH + ENEMY_SIZE[0]
            self.rect.y = random.randint(0, HEIGHT - ENEMY_SIZE[1])
            self.direction = [-1, random.uniform(-1, 1)]

        length = (self.direction[0]**2 + self.direction[1]**2)**0.5
        self.direction = [d / length * speed for d in self.direction]

    def animate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > ANIMATION_SPEED:
            self.last_update = now
            self.frame_index = (self.frame_index + 1) % len(self.current_animation)
            self.image = self.current_animation[self.frame_index]

    def move(self):
        self.rect.x += self.direction[0]
        self.rect.y += self.direction[1]
        self.animate()

    def draw(self):
        screen.blit(self.image, self.rect.topleft)

# Функция отрисовки текста
def draw_text(text, size, color, x, y):
    font = pygame.font.SysFont(None, size)
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))

# Меню старта
def start_screen():
    screen.fill(WHITE)
    draw_text("Добро пожаловать!", 60, BLACK, WIDTH//2 - 200, HEIGHT//2 - 100)
    draw_text("Управляйте игроком стрелками", 30, BLACK, WIDTH//2 - 200, HEIGHT//2)
    draw_text("Не касайтесь врагов!", 30, BLACK, WIDTH//2 - 150, HEIGHT//2 + 40)
    draw_text("Нажмите ПРОБЕЛ чтобы начать", 30, BLACK, WIDTH//2 - 170, HEIGHT//2 + 100)
    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            waiting = False
    return True

# Меню паузы
def pause_menu():
    screen.fill(GRAY)
    draw_text("ПАУЗА", 60, BLACK, WIDTH // 2 - 100, HEIGHT // 2 - 100)
    draw_text("1. Продолжить (P)", 30, BLACK, WIDTH // 2 - 130, HEIGHT // 2 - 20)
    draw_text("2. Перезапустить (R)", 30, BLACK, WIDTH // 2 - 140, HEIGHT // 2 + 30)
    draw_text("3. Выйти (ESC)", 30, BLACK, WIDTH // 2 - 120, HEIGHT // 2 + 80)
    pygame.display.flip()
    paused = True
    while paused:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
        keys = pygame.key.get_pressed()
        if keys[pygame.K_p]:  # Продолжить
            paused = False
            return "continue"
        if keys[pygame.K_r]:  # Перезапустить
            paused = False
            return "restart"
        if keys[pygame.K_ESCAPE]:  # Выйти
            paused = False
            return "quit"

# Основной игровой цикл
def game_loop():
    hit_sound = load_sound(os.path.join(ASSETS_DIR, "hit.wav"))
    try:
        pygame.mixer.music.load(os.path.join(ASSETS_DIR, "background.mp3"))
        pygame.mixer.music.play(-1)
    except Exception as e:
        print("Ошибка музыки:", e)

    player = AnimatedPlayer()
    enemies = []
    frame_count = 0
    enemy_spawn_rate = SPAWN_RATE_BASE
    enemy_speed = ENEMY_SPEED_BASE
    start_time = pygame.time.get_ticks()
    running = True
    game_over = False

    while running:
        clock.tick(FPS)
        screen.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

        keys = pygame.key.get_pressed()
        if keys[pygame.K_p]:
            action = pause_menu()
            if action == "continue":
                pass
            elif action == "restart":
                return "restart"
            elif action == "quit":
                return "quit"

        if not game_over:
            dx = dy = 0
            if keys[pygame.K_LEFT]:
                dx = -1
            elif keys[pygame.K_RIGHT]:
                dx = 1
            if keys[pygame.K_UP]:
                dy = -1
            elif keys[pygame.K_DOWN]:
                dy = 1

            player.move(dx, dy)

            time_survived = (pygame.time.get_ticks() - start_time) // 1000
            if time_survived % 5 == 0 and time_survived > 0:
                enemy_speed = ENEMY_SPEED_BASE + time_survived / 10
                enemy_spawn_rate = max(SPAWN_RATE_BASE - time_survived, 30)

            frame_count += 1
            if frame_count >= enemy_spawn_rate:
                frame_count = 0
                enemies.append(Enemy(enemy_speed))

            for enemy in enemies:
                enemy.move()
                enemy.draw()
                if player.rect.colliderect(enemy.rect):
                    if hit_sound:
                        hit_sound.play()
                    game_over = True

            player.draw()
            draw_text(f"Время: {time_survived} сек", 30, BLACK, 10, 10)

        else:
            time_survived = (pygame.time.get_ticks() - start_time) // 1000
            draw_text("Вы проиграли!", 60, BLACK, WIDTH // 2 - 200, HEIGHT // 2 - 50)
            draw_text(f"Вы продержались: {time_survived} сек", 30, BLACK, WIDTH // 2 - 180, HEIGHT // 2 + 20)
            draw_text("Нажмите ПРОБЕЛ чтобы перезапустить или ESC чтобы выйти", 25, BLACK,
                      WIDTH // 2 - 300, HEIGHT // 2 + 60)

            if keys[pygame.K_SPACE]:
                return "restart"
            if keys[pygame.K_ESCAPE]:
                return "quit"

        pygame.display.flip()

# Запуск игры
if __name__ == "__main__":
    while True:
        if not start_screen():
            break
        result = game_loop()
        if result == "quit":
            break