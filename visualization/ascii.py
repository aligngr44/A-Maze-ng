from config.read_file import Config
from visualization.pathfinding import DIRECTIONS

NORTH = 1
EAST = 2
SOUTH = 4
WEST = 8


RESET = "\033[0m"


def fg(r: int, g: int, b: int) -> str:
    return f"\033[38;2;{r};{g};{b}m"


def bg(r: int, g: int, b: int) -> str:
    return f"\033[48;2;{r};{g};{b}m"


def path_pixels(entry: tuple[int, int], path: str) -> set[tuple[int, int]]:
    x, y = 2 * entry[0] + 1, 2 * entry[1] + 1
    pixels = {(x, y)}

    for direction in path:
        _, dx, dy = DIRECTIONS[direction]
        x, y = x + dx, y + dy
        pixels.add((x, y))
        x, y = x + dx, y + dy
        pixels.add((x, y))

    return pixels


def build_pixel_grid(
    grid: list[list[int]],
    cfg: Config,
    blocked_cells: set[tuple[int, int]] | None = None,
) -> list[list[str]]:
    pw = 2 * cfg.width + 1
    ph = 2 * cfg.height + 1
    pixels = [["wall" for _ in range(pw)] for _ in range(ph)]
    blocked_cells = blocked_cells or set()

    for y in range(cfg.height):
        for x in range(cfg.width):
            cell = grid[y][x]
            px, py = 2 * x + 1, 2 * y + 1
            pixels[py][px] = "pattern" if (x, y) in blocked_cells else "floor"

            if not (cell & NORTH):
                pixels[py - 1][px] = "floor"
            if not (cell & SOUTH):
                pixels[py + 1][px] = "floor"
            if not (cell & EAST):
                pixels[py][px + 1] = "floor"
            if not (cell & WEST):
                pixels[py][px - 1] = "floor"

    return pixels


def hex_to_rgb(color: int) -> tuple[int, int, int]:
    r = (color >> 16) & 0xFF
    g = (color >> 8) & 0xFF
    b = color & 0xFF
    return (r, g, b)

FLOOR_BG = bg(*hex_to_rgb(0x000000))    # BACKGROUND
WALL_BG = bg(*hex_to_rgb(0xB185DB))     # WALL_COLOR
ENTRY_BG = bg(*hex_to_rgb(0xFFD23F))    # ENTRY_COLOR
EXIT_BG = bg(*hex_to_rgb(0xFF3333))     # EXIT_COLOR
PATH_BG = bg(*hex_to_rgb(0xAAAAAA))     # PATH_COLOR (bir sonraki adımda kullanacağız)
PATTERN_BG = bg(*hex_to_rgb(0xFFFFFF))   # "42" deseni rengi (subject örneğindeki gri)


def print_pixel_grid(pixels: list[list[str]], cfg: Config, path: str | None = None) -> str:
    entry_px = (2 * cfg.entry[0] + 1, 2 * cfg.entry[1] + 1)
    exit_px = (2 * cfg.exit[0] + 1, 2 * cfg.exit[1] + 1)
    solved = path_pixels(cfg.entry, path) if path else set()

    for py, row in enumerate(pixels):
        line = ""
        for px, kind in enumerate(row):
            if (px, py) == entry_px:
                color = ENTRY_BG
            elif (px, py) == exit_px:
                color = EXIT_BG
            elif (px, py) in solved:
                color = PATH_BG
            elif kind == "wall":
                color = WALL_BG
            elif kind == "pattern":
                color = PATTERN_BG
            else:
                color = FLOOR_BG
            line += color + "  " + RESET
        print(line)
