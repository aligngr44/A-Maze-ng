import sys

from config.read_file import read_to_file, pars
from maze_generator import MazeGenerator
from visualization.ascii import display_ascii


def main() -> None:
    config_path = sys.argv[1]

    raw_config = read_to_file(config_path)
    cfg = pars(raw_config)

    maze = MazeGenerator(cfg.width, cfg.height)
    if cfg.perfect:
        maze.generate_perfect()
    else:
        maze.generate_imperfect()   # Bilal'in eklediği fonksiyon, henüz test etmedik
    try:
        with open(cfg.output_file, "w") as f:
            f.write(display_ascii(maze.grid, cfg))
    except Exception as e:
        print(e)
    print(display_ascii(maze.grid, cfg))


if __name__ == "__main__":
    main()