import sys

import config
from config.read_file import Config
from maze_generator import MazeGenerator
from visualization.pathfinding import shortest_path
from visualization import print_pixel_grid, build_pixel_grid, wall_color


def generate_maze(cfg: Config, seed: int | None) -> MazeGenerator:
    """Create a maze, generate it per cfg.perfect, and validate entry/exit.

    Raises ValueError if the maze is invalid (e.g. entry/exit blocked
    by the "42" pattern) — never returns an unvalidated maze.
    """
    maze = MazeGenerator(cfg.width, cfg.height, seed)

    if cfg.perfect:
        maze.generate_perfect()
    else:
        maze.generate_imperfect()

    config.validate.check_entry_exit_not_blocked(cfg.entry, cfg.exit, maze.blocked_cells)

    return maze


def run_menu(maze: MazeGenerator, cfg: Config) -> None:
    show_path = False
    color_index = 0
    seed = cfg.seed


    while True:
        path = shortest_path(maze.grid, cfg.width, cfg.height, cfg.entry, cfg.exit)
        pixels = build_pixel_grid(maze.grid, cfg, maze.blocked_cells)
        print_pixel_grid(pixels, cfg, color_index, path if show_path else None)

        print("=== A-Maze-ing ===")
        print("1. Re-generate a new maze")
        print("2. Show / Hide the shortest path")
        print("3. Rotate the wall colours")
        print("4. Quit")

        try:
            choice = input("Choice? (1-4): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            return

        if choice == "1":
            seed = None if seed is None else seed + 1
            try:
                maze = generate_maze(cfg, seed)
            except ValueError as error:
                print(f"Error: could not generate a valid maze ({error}). Keeping the current one.")
        elif choice == "2":
            show_path = not show_path
        elif choice == "3":
            color_index += 1
        elif choice == "4":
            return
        else:
            print("Invalid choice.")


def main() -> None:

    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt")
        return
    try:
        raw_config = config.read_to_file(sys.argv[1])
        cfg = config.pars(raw_config)

        config.validate_config(cfg)

        maze = generate_maze(cfg, cfg.seed)
        maze.write_grid(cfg.output_file)

        path = shortest_path(maze.grid, cfg.width, cfg.height, cfg.entry, cfg.exit)

        with open(cfg.output_file, "a") as file:
            file.write("\n")
            file.write(f"{cfg.entry[0]},{cfg.entry[1]}\n")
            file.write(f"{cfg.exit[0]},{cfg.exit[1]}\n")
            file.write(f"{path}\n")

        run_menu(maze, cfg)

    except ValueError as Error:
        print(f"Error: {Error}")


if __name__ == "__main__":
    main()