"""Quick check: is the generated maze a true perfect maze?

A perfect maze on N cells is a spanning tree, so it must have
exactly N - 1 open passages (no more, no less). More passages
means there's a loop somewhere; fewer means it's disconnected.

Usage:
    python3 verify_perfect.py config.txt
"""
import sys

from config.read_file import read_to_file, pars
from maze_generator import MazeGenerator

EAST = 2
SOUTH = 4


def count_open_passages(grid: list[list[int]], width: int, height: int) -> int:
    """Count open passages, each shared wall counted exactly once."""
    count = 0
    for y in range(height):
        for x in range(width):
            cell = grid[y][x]
            if x < width - 1 and not (cell & EAST):
                count += 1
            if y < height - 1 and not (cell & SOUTH):
                count += 1
    return count


def main() -> None:
    config_path = sys.argv[1]
    cfg = pars(read_to_file(config_path))

    maze = MazeGenerator(cfg.width, cfg.height)
    maze.generate_perfect()

    total_cells = cfg.width * cfg.height
    open_passages = count_open_passages(maze.grid, cfg.width, cfg.height)
    expected = total_cells - 1

    print(f"Hücre sayısı     : {total_cells}")
    print(f"Açık geçiş sayısı: {open_passages}")
    print(f"Beklenen (N-1)   : {expected}")
    print(f"Mükemmel mi?     : {open_passages == expected}")


if __name__ == "__main__":
    main()