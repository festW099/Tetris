import pygame
import random
import os
import json

pygame.init()
pygame.mixer.init()

CELL = 30
COLS, ROWS = 10, 20
SIDE_PANEL = 200
WIDTH, HEIGHT = COLS * CELL + SIDE_PANEL, ROWS * CELL

BLACK = (10, 10, 10)
WHITE = (255, 255, 255)
GHOST = (100, 100, 100)
BUTTON_COLOR = (30, 30, 30)
BUTTON_HOVER = (70, 70, 70)
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

grid = [[0] * COLS for _ in range(ROWS)]
score = 0
level = 1
paused = False

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

def clear_rows():
    global grid
    cleared = 0
    new_grid = [row for row in grid if any(cell == 0 for cell in row)]
    cleared = ROWS - len(new_grid)
    for _ in range(cleared):
        new_grid.insert(0, [0] * COLS)
    grid = new_grid
    return cleared

def draw_text(text, x, y, size=30):
    font = pygame.font.SysFont("Arial", size)
    surf = font.render(text, True, WHITE)
    screen.blit(surf, (x, y))

def draw_button(text, x, y, w, h, mouse_pos):
    rect = pygame.Rect(x, y, w, h)
    color = BUTTON_HOVER if rect.collidepoint(mouse_pos) else BUTTON_COLOR
    pygame.draw.rect(screen, color, rect, border_radius=8)
    pygame.draw.rect(screen, WHITE, rect, 2, border_radius=8)
    label = font.render(text, True, WHITE)
    label_rect = label.get_rect(center=rect.center)
    screen.blit(label, label_rect)
    return rect

def draw_ghost(tetromino):
    ghost_y = tetromino.drop_y()
    for i, row in enumerate(tetromino.shape):
        for j, cell in enumerate(row):
            if cell:
                pygame.draw.rect(screen, GHOST, ((tetromino.x + j)*CELL, (ghost_y + i)*CELL, CELL, CELL), 1)

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
    global grid, score, level, paused
    clock = pygame.time.Clock()
    current = Tetromino()
    fall_time = 0
    fall_speed = 500
    score = 0
    level = 1

    running = True
    while running:
        dt = clock.tick(60)
        fall_time += dt
        mouse_pos = pygame.mouse.get_pos()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return
            elif e.type == pygame.MOUSEBUTTONDOWN:
                if pause_btn.collidepoint(mouse_pos):
                    paused = not paused
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    return
                if not paused:
                    if e.key == pygame.K_LEFT: current.move(-1, 0)
                    elif e.key == pygame.K_RIGHT: current.move(1, 0)
                    elif e.key == pygame.K_DOWN: current.move(0, 1)
                    elif e.key == pygame.K_UP: current.rotate()
                    elif e.key == pygame.K_SPACE:
                        while current.move(0, 1): pass
                        fall_time = fall_speed + 1

        if not paused and fall_time > fall_speed:
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
                    return
            fall_time = 0

        screen.fill(BLACK)
        for y in range(ROWS):
            for x in range(COLS):
                if grid[y][x]:
                    pygame.draw.rect(screen, grid[y][x], (x*CELL, y*CELL, CELL, CELL), border_radius=5)

        draw_ghost(current)
        for i, row in enumerate(current.shape):
            for j, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(screen, current.color, ((current.x + j)*CELL, (current.y + i)*CELL, CELL, CELL), border_radius=5)

        panel_x = COLS * CELL + 20
        draw_text(f"Score: {score}", panel_x, 40)
        draw_text(f"Level: {level}", panel_x, 80)
        draw_text(f"Highscore: {load_highscore()}", panel_x, 120)

        pause_btn = draw_button("Pause" if not paused else "Resume", panel_x, 160, 120, 40, mouse_pos)
        pygame.display.flip()

def menu():
    while True:
        screen.fill(BLACK)
        mouse_pos = pygame.mouse.get_pos()
        play_btn = draw_button("Play", WIDTH//2 - 60, HEIGHT//2, 120, 40, mouse_pos)
        quit_btn = draw_button("Quit", WIDTH//2 - 60, HEIGHT//2 + 60, 120, 40, mouse_pos)
        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return
            elif e.type == pygame.MOUSEBUTTONDOWN:
                if play_btn.collidepoint(mouse_pos):
                    game_loop()
                elif quit_btn.collidepoint(mouse_pos):
                    return

if __name__ == "__main__":
    menu()
    pygame.quit()
