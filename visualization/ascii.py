from config.read_file import Config

NORTH = 1
EAST = 2
SOUTH = 4
WEST = 8


def display_ascii(grid: list[list[int]], cfg: Config) -> str:
    line: list[str] = []
    line.append("+" + "+".join("--" for _ in range(cfg.width)) + "+")
    for y in range(cfg.height):
        row_mid = "|"
        row_bottom = "+"
        for x in range(cfg.width):
            cell = grid[y][x]
            ch = " "
            east_wall = "|" if cell & EAST else " "
            row_mid += ch + " " + east_wall

            south_wall = "--" if cell & SOUTH else "  "
            row_bottom += south_wall + "+"

        line.append(row_mid)
        line.append(row_bottom)

    return "\n".join(line)
