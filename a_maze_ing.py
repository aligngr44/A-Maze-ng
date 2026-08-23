import sys
import config
from maze_generator import MazeGenerator


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
        
        maze.write_grid(cfg.output_file)

    except ValueError as Error:
        print(f"Error: {Error}")


if __name__ == "__main__":
    main()