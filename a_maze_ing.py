import sys

import config
from maze_generator import MazeGenerator
from visualization.mlx_view import run_mlx_view
from visualization.pathfinding import shortest_path
from visualization import print_pixel_grid, build_pixel_grid, path_pixels

def main() -> None:

    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt")
        return
    try:
        raw_config = config.read_to_file(sys.argv[1])
        cfg = config.pars(raw_config)

        config.validate_config(cfg)

        maze = MazeGenerator(cfg.width, cfg.height, cfg.seed)

        if cfg.perfect:
            maze.generate_perfect()
        else:
            maze.generate_imperfect()

        path = shortest_path(maze.grid, cfg.width, cfg.height, cfg.entry, cfg.exit)

        maze.write_grid(cfg.output_file)

        with open(cfg.output_file, "a") as file:
            file.write("\n")
            file.write(f"Entry: {cfg.entry[0]},{cfg.entry[1]}\n")
            file.write(f"Exit: {cfg.exit[0]},{cfg.exit[1]}\n")
            file.write(f"Path: {path}\n")


        x = build_pixel_grid(maze.grid, cfg)
        print(print_pixel_grid(x, cfg, None))

    except ValueError as Error:
        print(f"Error: {Error}")


if __name__ == "__main__":
    main()