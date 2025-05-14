import pygame
import random
import os
import json

pygame.init()
pygame.mixer.init()

# Размеры
CELL = 30
COLS, ROWS = 10, 20
WIDTH, HEIGHT = COLS * CELL, ROWS * CELL

# Цвета
BLACK = (0, 0, 0)
GRAY = (50, 50, 50)
WHITE = (255, 255, 255)
GHOST = (150, 150, 150)
COLORS = [
    (0, 255, 255), (0, 0, 255), (255, 165, 0),
    (255, 255, 0), (0, 255, 0), (128, 0, 128), (255, 0, 0)
]
SHAPES = [
    [[1, 1, 1, 1]],
    [[1, 0, 0], [1, 1, 1]],
    [[0, 0, 1], [1, 1, 1]],
    [[1, 1], [1, 1]],
    [[0, 1, 1], [1, 1, 0]],
    [[0, 1, 0], [1, 1, 1]],
    [[1, 1, 0], [0, 1, 1]]
]

font = pygame.font.SysFont("Arial", 20)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tetris")

SAVE_FILE = "savegame.json"
HIGHSCORE_FILE = "highscore.txt"

class Tetromino:
    def __init__(self):
        self.type = random.randint(0, len(SHAPES) - 1)
        self.shape = SHAPES[self.type]
        self.color = COLORS[self.type]
        self.x = COLS // 2 - len(self.shape[0]) // 2
        self.y = 0

    def rotate(self):
        prev = self.shape
        self.shape = [list(row)[::-1] for row in zip(*self.shape)]
        if self.collide():
            self.shape = prev

    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        if self.collide():
            self.x -= dx
            self.y -= dy
            return False
        return True

    def collide(self):
        for i, row in enumerate(self.shape):
            for j, cell in enumerate(row):
                if cell:
                    xi, yi = self.x + j, self.y + i
                    if xi < 0 or xi >= COLS or yi >= ROWS or (yi >= 0 and grid[yi][xi]):
                        return True
        return False

    def drop_y(self):
        orig = self.y
        while not self.collide():
            self.y += 1
        self.y -= 1
        y = self.y
        self.y = orig
        return y

    def place(self):
        for i, row in enumerate(self.shape):
            for j, cell in enumerate(row):
                if cell and self.y + i >= 0:
                    grid[self.y + i][self.x + j] = self.color

def draw_grid():
    for y in range(ROWS):
        for x in range(COLS):
            if grid[y][x]:
                pygame.draw.rect(screen, grid[y][x], (x*CELL, y*CELL, CELL, CELL))
            pygame.draw.rect(screen, GRAY, (x*CELL, y*CELL, CELL, CELL), 1)

def draw_ghost(tetromino):
    ghost_y = tetromino.drop_y()
    for i, row in enumerate(tetromino.shape):
        for j, cell in enumerate(row):
            if cell:
                pygame.draw.rect(screen, GHOST, ((tetromino.x + j)*CELL, (ghost_y + i)*CELL, CELL, CELL), 1)

def clear_rows():
    global grid
    cleared = 0
    new_grid = [row for row in grid if any(cell == 0 for cell in row)]
    cleared = ROWS - len(new_grid)
    for _ in range(cleared):
        new_grid.insert(0, [0] * COLS)
    grid = new_grid
    return cleared

def draw_text(text, y, size=30):
    font = pygame.font.SysFont("Arial", size)
    surf = font.render(text, True, WHITE)
    rect = surf.get_rect(center=(WIDTH//2, y))
    screen.blit(surf, rect)

def save_game():
    with open(SAVE_FILE, "w") as f:
        json.dump({"grid": grid, "score": score, "level": level}, f)

def load_game():
    global grid, score, level
    with open(SAVE_FILE) as f:
        data = json.load(f)
        grid = data["grid"]
        score = data["score"]
        level = data["level"]

def load_highscore():
    try:
        with open(HIGHSCORE_FILE) as f:
            return int(f.read())
    except:
        return 0

def save_highscore(new_score):
    high = load_highscore()
    if new_score > high:
        with open(HIGHSCORE_FILE, "w") as f:
            f.write(str(new_score))

def game_loop():
    global grid, score, level
    grid = [[0] * COLS for _ in range(ROWS)]
    clock = pygame.time.Clock()
    current = Tetromino()
    fall_time = 0
    fall_speed = 500
    score = 0
    level = 1
    running, paused = True, False

    if os.path.exists(SAVE_FILE):
        load_game()

    while running:
        dt = clock.tick(60)
        fall_time += dt
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                save_game()
                return
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_LEFT: current.move(-1, 0)
                elif e.key == pygame.K_RIGHT: current.move(1, 0)
                elif e.key == pygame.K_DOWN: current.move(0, 1)
                elif e.key == pygame.K_UP: current.rotate()
                elif e.key == pygame.K_SPACE:
                    while current.move(0, 1): pass
                    fall_time = fall_speed + 1
                elif e.key == pygame.K_p:
                    paused = not paused

        if paused:
            screen.fill(BLACK)
            draw_text("PAUSED", HEIGHT//2)
            pygame.display.flip()
            continue

        if fall_time > fall_speed:
            if not current.move(0, 1):
                current.place()
                cleared = clear_rows()
                if cleared:
                    score += cleared * 100
                    level = score // 500 + 1
                    fall_speed = max(100, 500 - level * 25)
                current = Tetromino()
                if current.collide():
                    save_highscore(score)
                    save_game()
                    return
            fall_time = 0

        screen.fill(BLACK)
        draw_grid()
        draw_ghost(current)
        for i, row in enumerate(current.shape):
            for j, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(screen, current.color, ((current.x + j)*CELL, (current.y + i)*CELL, CELL, CELL))

        screen.blit(font.render(f"Score: {score}", True, WHITE), (10, 10))
        screen.blit(font.render(f"Level: {level}", True, WHITE), (10, 30))
        screen.blit(font.render(f"Highscore: {load_highscore()}", True, WHITE), (10, 50))
        pygame.display.flip()

def menu():
    while True:
        screen.fill(BLACK)
        draw_text("TETRIS", HEIGHT // 3, 40)
        draw_text("1. Play", HEIGHT // 2)
        draw_text("2. Exit", HEIGHT // 2 + 40)
        draw_text("P - Pause, SPACE - Drop", HEIGHT - 30, 18)
        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_1:
                    game_loop()
                elif e.key == pygame.K_2:
                    return

if __name__ == "__main__":
    menu()
    pygame.quit()
