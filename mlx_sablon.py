import math
import random

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
BACKGROUND = 0xFF11121A   # neredeyse siyah ama tam siyah değil, koyu lacivert/antrasit
WALL_COLOR_OPTIONS = [
    0xFF3FE0B0,  # nane yeşili / turkuaz (varsayılan)
    0xFFFFA94D,  # amber / turuncu
    0xFF64B5F6,  # açık mavi
    0xFFFF6EC7,  # pembe
]
ENTRY_COLOR = 0xFF3DFF7A  # giriş (canlı yeşil)
EXIT_COLOR = 0xFFFF4D6D   # çıkış (mercan/pembe-kırmızı)
PATH_COLOR = 0xFFB388FF   # yol (lavanta/mor) — duvar renginden net ayrışsın

WIN_WIDTH = 500
WIN_HEIGHT = 500
UI_BAR_HEIGHT = 20   # altta yazı için ayrılan şerit; labirent bunun üstüne çizilir
LINE_THICKNESS = 3  # kalın duvar hissi için; cell_size küçükse otomatik küçültülür

LEGEND_TEXT = "R: regen   P: path   C: color   ESC: quit"
LEGEND_COLOR = 0xFFAAAAAA  # gri, arkaplandan hafif ayrışsın

# Tuş kodları (X11 keysym'leri; küçük harfler ASCII koduyla aynıdır)
KEY_ESC = 65307
KEY_R = 114  # re-generate
KEY_P = 112  # show/hide path
KEY_C = 99   # rotate wall colours


def run_mlx_view(maze: MazeGenerator, cfg: Config, path: str) -> None:
    """Generated mazeyi MLX penceresinde çizer, klavye kısayollarıyla etkileşim sağlar.

    Args:
        maze: Hücre duvar verisini (maze.grid) barındıran MazeGenerator örneği
            (başlangıç mazesi; R tuşuyla yenisiyle değiştirilir).
        cfg: entry/exit/width/height/perfect bilgilerini içeren config.
        path: shortest_path'ten dönen N/E/S/W harflerinden oluşan başlangıç dizgisi.

    Klavye kısayolları:
        R   -> yeni bir maze üret ve göster
        P   -> en kısa yolu göster/gizle
        C   -> duvar rengini değiştir (WALL_COLOR_OPTIONS içinde döner)
        ESC -> çık
    """
    _mlx = mlx.Mlx()
    mlx_ptr = _mlx.mlx_init()

    maze_area_height = WIN_HEIGHT - UI_BAR_HEIGHT
    cell_size = min(WIN_WIDTH // cfg.width, maze_area_height // cfg.height)
    # Hücre çok küçükse (kalabalık maze) kalın çizgi hücreyi boğar; kalınlığı sınırla.
    thickness = max(1, min(LINE_THICKNESS, cell_size // 4))
    win_ptr = _mlx.mlx_new_window(mlx_ptr, WIN_WIDTH, WIN_HEIGHT, "A-Maze-Ing")

    # --- Değişebilir durum (tuşlarla güncellenecek) ---
    state = {
        "maze": maze,
        "path": path,
        "show_path": True,
        "color_index": 0,
        "needs_redraw": True,
    }

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
        wall_color = WALL_COLOR_OPTIONS[state["color_index"]]
        current_maze = state["maze"]
        for y in range(cfg.height):
            for x in range(cfg.width):
                cell = current_maze.grid[y][x]
                px = x * cell_size
                py = y * cell_size

                if cell & NORTH:
                    draw_line(px, py, px + cell_size, py, wall_color, thickness)

                if cell & WEST:
                    draw_line(px, py, px, py + cell_size, wall_color, thickness)

                if x == cfg.width - 1 and cell & EAST:
                    draw_line(px + cell_size, py, px + cell_size, py + cell_size, wall_color, thickness)

                if y == cfg.height - 1 and cell & SOUTH:
                    draw_line(px, py + cell_size, px + cell_size, py + cell_size, wall_color, thickness)

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

        for direction in state["path"]:
            dx, dy = PATH_DIRECTIONS[direction]
            x += dx
            y += dy
            nx = x * cell_size + cell_size // 2
            ny = y * cell_size + cell_size // 2

            draw_line(cx, cy, nx, ny, PATH_COLOR, max(1, thickness - 1))

            cx, cy = nx, ny

    def draw_legend() -> None:
        # Alt şeritte kontrol tuşlarını yazdırır. mlx_string_put(mlx, win, x, y, color, str)
        # Not: wrapper'ında fonksiyon adı farklıysa (örn. mlx_put_string), burayı ona göre değiştir.
        text_y = WIN_HEIGHT - UI_BAR_HEIGHT + 14
        _mlx.mlx_string_put(mlx_ptr, win_ptr, 8, text_y, LEGEND_COLOR, LEGEND_TEXT)

    def redraw() -> None:
        fill_background()
        draw_maze()
        if state["show_path"]:
            draw_path()
        fill_dot(*cfg.entry, ENTRY_COLOR)
        fill_dot(*cfg.exit, EXIT_COLOR)
        draw_legend()

    def render(param: object) -> int:
        # Ağır işlemi (arkaplan + tüm duvarları yeniden çizmek) sadece bir
        # şey değiştiğinde yap; her frame'de tekrar çizmek gereksiz maliyet.
        if state["needs_redraw"]:
            redraw()
            state["needs_redraw"] = False
        return 0

    def regenerate_maze() -> None:
        new_seed = random.randint(0, 1_000_000)
        new_maze = MazeGenerator(cfg.width, cfg.height, new_seed)
        if cfg.perfect:
            new_maze.generate_perfect()
        else:
            new_maze.generate_imperfect()
        state["maze"] = new_maze
        state["path"] = shortest_path(new_maze.grid, cfg.width, cfg.height, cfg.entry, cfg.exit)
        state["needs_redraw"] = True

    def toggle_path() -> None:
        state["show_path"] = not state["show_path"]
        state["needs_redraw"] = True

    def rotate_wall_color() -> None:
        state["color_index"] = (state["color_index"] + 1) % len(WALL_COLOR_OPTIONS)
        state["needs_redraw"] = True

    def on_key(keycode: int, param: object) -> int:
        if keycode == KEY_ESC:
            _mlx.mlx_loop_exit(mlx_ptr)
        elif keycode == KEY_R:
            regenerate_maze()
        elif keycode == KEY_P:
            toggle_path()
        elif keycode == KEY_C:
            rotate_wall_color()
        return 0

    _mlx.mlx_key_hook(win_ptr, on_key, 0)
    _mlx.mlx_loop_hook(mlx_ptr, render, None)
    _mlx.mlx_loop(mlx_ptr)