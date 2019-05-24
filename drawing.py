import pygame

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (12, 192, 12)
RED = (255, 0, 0)
BLUE = (0, 0, 128)
LIGHTGRAY = (192, 192, 192)
GRAY = (128, 128, 128)
DARKGRAY = (45, 45, 45)
YELLOW = (192, 192, 0)
LIGHTBLUE = (100, 140, 255)


def draw_ground(grid, cell_dimensions, color=GRAY):
    return pygame.draw.rect(grid.screen, color, cell_dimensions)


def draw_line(grid, cell_dimensions, fromcoo, tocoo, color, width):
    x, y, w, h = cell_dimensions
    pygame.draw.line(
        grid.screen,
        color,
        (x + w * fromcoo[0] // 100, y + h * fromcoo[1] // 100),
        (x + w * tocoo[0] // 100, y + h * tocoo[1] // 100),
        w * width // 100,
    )


def draw_circle(grid, cell_dimensions, pos, diameter, color=DARKGRAY):
    x, y, w, h = cell_dimensions
    pygame.draw.circle(grid.screen, color, (x + w * pos[0] // 100, y + h * pos[1] // 100), w * diameter // 200)


def draw_text(grid, cell_dimensions, text, pos, size, color):
    x, y, w, h = cell_dimensions
    font = pygame.font.Font(grid.itemfont, h * size // 100)
    text = font.render(text, True, WHITE)
    text_rect = text.get_rect()
    text_rect.center = (x + w * pos[0] // 100, y + h * pos[1] // 100)
    grid.screen.blit(text, text_rect)


# Specific drawing routines


def draw_boulder(grid, cell_dimensions):
    draw_ground(grid, cell_dimensions, LIGHTGRAY)
    draw_circle(grid, cell_dimensions, (50, 50), 80, color=(90, 48, 22))
    x, y, w, h = cell_dimensions
    cellx = int(x / (grid.cellwidth + grid.margin))
    celly = int(y / (grid.cellheight + grid.margin))
    draw_text(grid, cell_dimensions, f'{cellx},{celly}', (50, 50), 29, WHITE)


def draw_bomb(grid, cell_dimensions):
    draw_ground(grid, cell_dimensions, LIGHTGRAY)
    draw_circle(grid, cell_dimensions, (50, 50), 70, BLACK)  # Bomb itself
    draw_circle(grid, cell_dimensions, (40, 40), 10, WHITE)  # White glow
    draw_line(grid, cell_dimensions, (50, 50), (85, 15), BLACK, 23)  # Fuse
    draw_line(grid, cell_dimensions, (80, 10), (90, 20), YELLOW, 23)  # Spark


def draw_down_line(grid, cell_dimensions):
    draw_ground(grid, cell_dimensions, LIGHTGRAY)
    draw_line(grid, cell_dimensions, (0, 0), (100, 100), GREEN, 10)


def draw_up_line(grid, cell_dimensions):
    draw_ground(grid, cell_dimensions, LIGHTGRAY)
    draw_line(grid, cell_dimensions, (0, 100), (100, 0), GREEN, 10)


def draw_money(grid, cell_dimensions):
    draw_ground(grid, cell_dimensions, LIGHTGRAY)
    draw_circle(grid, cell_dimensions, (50, 60), 60, LIGHTBLUE)  # Sack itself
    draw_line(grid, cell_dimensions, (40, 25), (60, 25), LIGHTBLUE, 15)
    draw_text(grid, cell_dimensions, '$', (50, 60), 36, WHITE)
