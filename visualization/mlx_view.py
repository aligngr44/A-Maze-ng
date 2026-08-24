import math

import mlx
from config.read_file import Config
from maze_generator import MazeGenerator
from visualization.pathfinding import shortest_path

NORTH = 1
EAST = 2
SOUTH = 4
WEST = 8

PATH_DIRECTIONS = {
    "N": (0, -1),
    "E": (1, 0),
    "S": (0, 1),
    "W": (-1, 0),
}

# --- Renk paleti (PDF'teki koyu arkaplan + canlı duvar rengi mantığı) ---
BACKGROUND = 0xFF1A0F1F  # neredeyse siyah ama tam siyah değil, koyu lacivert/antrasit
WALL_COLOR = 0xFFFF8C42  # nane yeşili / turkuaz duvarlar
ENTRY_COLOR = 0xFF39FF14  # giriş (canlı yeşil)
EXIT_COLOR = 0xFFFF2D75   # çıkış (mercan/pembe-kırmızı)
PATH_COLOR = 0xFFD400FF   # yol (lavanta/mor) — duvar renginden net ayrışsın

WIN_WIDTH = 500
WIN_HEIGHT = 500
LINE_THICKNESS = 5  # kalın duvar hissi için; cell_size küçükse otomatik küçültülür


def run_mlx_view(maze: MazeGenerator, cfg: Config, path: str) -> None:
    """Generated mazeyi MLX penceresinde çizer ve olay döngüsünü başlatır.

    Args:
        maze: Hücre duvar verisini (maze.grid) barındıran MazeGenerator örneği.
        cfg: entry/exit/width/height bilgilerini içeren config.
        path: shortest_path'ten dönen N/E/S/W harflerinden oluşan dizgi.
    """
    _mlx = mlx.Mlx()
    mlx_ptr = _mlx.mlx_init()

    cell_size = min(WIN_WIDTH // cfg.width, WIN_HEIGHT // cfg.height)
    # Hücre çok küçükse (kalabalık maze) kalın çizgi hücreyi boğar; kalınlığı sınırla.
    thickness = max(1, min(LINE_THICKNESS, cell_size // 4))
    win_ptr = _mlx.mlx_new_window(mlx_ptr, WIN_WIDTH, WIN_HEIGHT, "A-Maze-Ing")

    def put_pixel_safe(x: int, y: int, color: int) -> None:
        # Kalınlık için kaydırılan pikseller pencere dışına taşabilir, koru.
        if 0 <= x < WIN_WIDTH and 0 <= y < WIN_HEIGHT:
            _mlx.mlx_pixel_put(mlx_ptr, win_ptr, x, y, color)

    def fill_background() -> None:
        for y in range(WIN_HEIGHT):
            for x in range(WIN_WIDTH):
                _mlx.mlx_pixel_put(mlx_ptr, win_ptr, x, y, BACKGROUND)

    def draw_line(x1: int, y1: int, x2: int, y2: int, color: int, width: int = 1) -> None:
        half = width // 2
        if x1 == x2:  # dikey çizgi -> kalınlığı yatayda genişlet
            y_start, y_end = min(y1, y2), max(y1, y2)
            for y in range(y_start, y_end + 1):
                for offset in range(-half, half + 1):
                    put_pixel_safe(x1 + offset, y, color)
        else:  # yatay çizgi -> kalınlığı dikeyde genişlet
            x_start, x_end = min(x1, x2), max(x1, x2)
            for x in range(x_start, x_end + 1):
                for offset in range(-half, half + 1):
                    put_pixel_safe(x, y1 + offset, color)

    def draw_maze() -> None:
        for y in range(cfg.height):
            for x in range(cfg.width):
                cell = maze.grid[y][x]
                px = x * cell_size
                py = y * cell_size

                if cell & NORTH:
                    draw_line(px, py, px + cell_size, py, WALL_COLOR, thickness)

                if cell & WEST:
                    draw_line(px, py, px, py + cell_size, WALL_COLOR, thickness)

                if x == cfg.width - 1 and cell & EAST:
                    draw_line(px + cell_size, py, px + cell_size, py + cell_size, WALL_COLOR, thickness)

                if y == cfg.height - 1 and cell & SOUTH:
                    draw_line(px, py + cell_size, px + cell_size, py + cell_size, WALL_COLOR, thickness)

    def fill_dot(cell_x: int, cell_y: int, color: int) -> None:
        center_x = cell_x * cell_size + cell_size // 2
        center_y = cell_y * cell_size + cell_size // 2
        radius = cell_size // 2 - 2  # hücreden biraz küçük, duvara değmesin

        for y in range(center_y - radius, center_y + radius + 1):
            for x in range(center_x - radius, center_x + radius + 1):
                distance = math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
                if distance <= radius:
                    put_pixel_safe(x, y, color)

    def draw_path() -> None:
        x, y = cfg.entry
        cx = x * cell_size + cell_size // 2
        cy = y * cell_size + cell_size // 2

        for direction in path:
            dx, dy = PATH_DIRECTIONS[direction]
            x += dx
            y += dy
            nx = x * cell_size + cell_size // 2
            ny = y * cell_size + cell_size // 2

            draw_line(cx, cy, nx, ny, PATH_COLOR, max(1, thickness - 1))

            cx, cy = nx, ny

    def render(param: object) -> int:
        draw_maze()
        draw_path()
        fill_dot(*cfg.entry, ENTRY_COLOR)
        fill_dot(*cfg.exit, EXIT_COLOR)
        return 0

    def on_key(keycode: int, param: object) -> int:
        if keycode == 65307:  # ESC
            _mlx.mlx_loop_exit(mlx_ptr)
        return 0

    # Arkaplanı bir kez doldur (her frame'de tekrar boyamak gereksiz maliyet
    # olur, çünkü render() zaten sürekli çağrılıyor).
    fill_background()

    _mlx.mlx_key_hook(win_ptr, on_key, 0)
    _mlx.mlx_loop_hook(mlx_ptr, render, None)
    _mlx.mlx_loop(mlx_ptr)