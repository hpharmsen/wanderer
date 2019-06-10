import pygame
import pygame.gfxdraw

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (12, 160, 12)
RED = (200, 0, 0)
BLUE = (0, 0, 128)
LIGHT_GRAY = (192, 192, 192)
GRAY = (128, 128, 128)
DARK_GRAY = (45, 45, 45)
YELLOW = (192, 192, 0)
LIGHT_BLUE = (100, 140, 255)
PINK = (255, 140, 140)
MIDDLE_GREEN = (91, 195, 66)
LIGHT_GREEN = (170, 230, 120)

TOP_LEFT = 0
TOP_RIGHT = 1


def draw_line(grid, cell_dimensions, fromcoo, tocoo, color, width):
    x, y, w, h = cell_dimensions
    pygame.draw.line(
        grid.screen,
        color,
        (x + w * fromcoo[0] // 100, y + h * fromcoo[1] // 100),
        (x + w * tocoo[0] // 100, y + h * tocoo[1] // 100),
        w * width // 100,
    )


def draw_circle(grid, cell_dimensions, pos, diameter, color=DARK_GRAY):
    x, y, w, h = cell_dimensions
    pygame.gfxdraw.aacircle(grid.screen, x + w * pos[0] // 100, y + h * pos[1] // 100, w * diameter // 200, color)
    pygame.gfxdraw.filled_circle(grid.screen, x + w * pos[0] // 100, y + h * pos[1] // 100, w * diameter // 200, color)


def draw_text(grid, cell_dimensions, text, pos, size, color):
    x, y, w, h = cell_dimensions
    font = pygame.font.Font(grid.font, h * size // 100)
    text = font.render(text, True, WHITE)
    text_rect = text.get_rect()
    text_rect.center = (x + w * pos[0] // 100, y + h * pos[1] // 100)
    grid.screen.blit(text, text_rect)


# Specific drawing routines


def draw_boulder(grid, cell_dimensions):
    draw_circle(grid, cell_dimensions, (50, 50), 80, color=(90, 48, 22))
    if 0:  # Draw cell positions in the boulders
        x, y, w, h = cell_dimensions
        if grid.sidebar_position == 1:
            x -= grid.sidebar_size
        if grid.sidebar_position == 2:
            y -= grid.sidebar_size

        cellx = int(x / (grid.cellwidth + grid.margin))
        celly = int(y / (grid.cellheight + grid.margin))
        draw_text(grid, cell_dimensions, f'{cellx},{celly}', (50, 50), 29, WHITE)


def draw_bomb(grid, cell_dimensions):
    draw_circle(grid, cell_dimensions, (50, 50), 70, BLACK)  # Bomb itself
    draw_circle(grid, cell_dimensions, (40, 40), 10, WHITE)  # White glow
    draw_line(grid, cell_dimensions, (50, 50), (85, 15), BLACK, 23)  # Fuse
    draw_line(grid, cell_dimensions, (80, 10), (90, 20), YELLOW, 23)  # Spark


def draw_down_line(grid, cell_dimensions):
    draw_line(grid, cell_dimensions, (0, 0), (100, 100), GREEN, 10)


def draw_up_line(grid, cell_dimensions):
    draw_line(grid, cell_dimensions, (0, 100), (100, 0), GREEN, 10)


def draw_money(grid, cell_dimensions):
    draw_circle(grid, cell_dimensions, (50, 60), 60, LIGHT_BLUE)  # Sack itself
    draw_line(grid, cell_dimensions, (40, 25), (60, 25), LIGHT_BLUE, 15)
    draw_text(grid, cell_dimensions, '$', (50, 60), 36, WHITE)


def draw_balloon(grid, cell_dimensions):
    draw_circle(grid, cell_dimensions, (50, 40), 60, PINK)  # Balloon itself
    draw_line(grid, cell_dimensions, (40, 75), (60, 75), PINK, 15)
    draw_line(grid, cell_dimensions, (48, 70), (53, 80), GRAY, 6)
    draw_line(grid, cell_dimensions, (53, 80), (48, 90), GRAY, 6)
    draw_line(grid, cell_dimensions, (48, 90), (53, 100), GRAY, 6)


def draw_hero(grid, cell_dimensions):
    draw_circle(grid, cell_dimensions, (50, 20), 30, RED)  # Head
    draw_circle(grid, cell_dimensions, (50, 50), 40, RED)  # Body
    draw_line(grid, cell_dimensions, (50, 20), (60, 95), RED, 15)
    draw_line(grid, cell_dimensions, (50, 20), (40, 95), RED, 15)


def draw_monster(grid, cell_dimensions):
    draw_circle(grid, cell_dimensions, (50, 50), 80, MIDDLE_GREEN)  # body
    draw_circle(grid, cell_dimensions, (30, 50), 10, BLACK)  # eye
    draw_circle(grid, cell_dimensions, (70, 50), 10, BLACK)  # eye
    draw_line(grid, cell_dimensions, (25, 10), (25, 30), DARK_GRAY, 10)  # horn
    draw_line(grid, cell_dimensions, (75, 10), (75, 30), DARK_GRAY, 10)  # horn
    draw_line(grid, cell_dimensions, (25, 70), (75, 70), DARK_GRAY, 8)  # Mouth
    draw_line(grid, cell_dimensions, (35, 70), (35, 80), WHITE, 10)  # talon
    draw_line(grid, cell_dimensions, (65, 70), (65, 80), WHITE, 10)  # talon


def draw_baby_monster(grid, cell_dimensions):
    draw_circle(grid, cell_dimensions, (50, 50), 70, LIGHT_GREEN)  # body
    draw_circle(grid, cell_dimensions, (30, 50), 10, BLACK)  # eye
    draw_circle(grid, cell_dimensions, (70, 50), 10, BLACK)  # eye
    draw_line(grid, cell_dimensions, (25, 70), (75, 70), DARK_GRAY, 8)  # Mouth
    draw_line(grid, cell_dimensions, (40, 70), (40, 80), WHITE, 10)  # talon
    draw_line(grid, cell_dimensions, (60, 70), (60, 80), WHITE, 10)  # talon


def draw_cage(grid, cell_dimensions):
    for x in range(10, 100, 20):
        draw_line(grid, cell_dimensions, (x, 5), (x, 95), GRAY, 8)
    draw_line(grid, cell_dimensions, (10, 5), (90, 5), DARK_GRAY, 8)
    draw_line(grid, cell_dimensions, (10, 95), (90, 95), DARK_GRAY, 8)


def full_screen_message(grid, color, message):
    play_area_dimensions = grid.cell_dimensions(0, 0, grid.width, grid.height)
    pygame.draw.rect(grid.screen, color, play_area_dimensions)
    draw_text(grid, play_area_dimensions, message, (50, 50), 12, WHITE)
    pygame.display.flip()


def blit_text(grid, text, font, color, coo, adjust):
    sx, sy, sw, sh = grid.get_sidebar_dimensions()
    x = sx + sw * coo[0] // 100
    y = sy + sh * coo[1] // 100
    rendered = font.render(text, True, color)
    text_rect = rendered.get_rect()
    if adjust == TOP_LEFT:
        text_rect.topleft = (x, y)
    elif adjust == TOP_RIGHT:
        text_rect.topright = (x, y)
    grid.screen.blit(rendered, text_rect)
    return text_rect


def sidebar_message(grid, coo, text):
    grid.clear_sidebar(DARK_GRAY)
    font = pygame.font.Font(grid.font, 18)
    blit_text(grid, text, font, WHITE, coo, TOP_LEFT)
    pygame.display.flip()


class LevelButton(pygame.sprite.Sprite):
    def __init__(self, grid, level, color):
        # Call the parent class (Sprite) constructor
        super().__init__()
        self.grid = grid
        self.level = level
        self.font = pygame.font.Font(pygame.font.get_default_font(), 12)
        self.color = color
        self.x = 48 + 1.7 * ((level - 1) % 30)
        self.y = 10 + ((level - 1) // 30) * 50

    def show(self):
        self.rect = blit_text(self.grid, str(self.level), self.font, self.color, (self.x, self.y), TOP_RIGHT)


def level_buttons(grid, curlevel):
    buttons = pygame.sprite.Group()
    for l in range(60):
        level = l + 1
        color = LIGHT_GRAY if level <= curlevel else GRAY
        button = LevelButton(grid, level, color)
        buttons.add(button)
    return buttons


def show_levels(grid, level):
    buttons = level_buttons(grid, level)
    font = pygame.font.Font(grid.font, 12)
    blit_text(grid, 'choose', font, GRAY, (46, 10), TOP_RIGHT)
    blit_text(grid, 'a level', font, GRAY, (46, 60), TOP_RIGHT)
    for button in buttons:
        button.show()
    pygame.display.flip()
    return buttons
