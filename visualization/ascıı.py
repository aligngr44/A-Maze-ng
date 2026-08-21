from config.read_file import Config


def display_ascii(grid: list[list[int]], cfg: Config) -> str:
    line: list[str] = []
    lines.append("+" + "+".join("--" for _ in range(cfg.width)) + "+")
    for y in range(cfg.height):
        row_mid = "|"
        row_bottom = "+"
        for x in range(cfg.width):
            cell = grid[x][y]
            