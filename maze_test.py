from maze_generator import MazeGenerator


def count_edges(maze: MazeGenerator) -> int:
    edges = 0

    for y in range(maze.height):
        for x in range(maze.width):
            if (x, y) in maze.blocked_cells:
                continue

            if x + 1 < maze.width:
                if not maze.grid[y][x] & 2:
                    edges += 1

            if y + 1 < maze.height:
                if not maze.grid[y][x] & 4:
                    edges += 1

    return edges


def count_active_cells(maze: MazeGenerator) -> int:
    return maze.width * maze.height - len(maze.blocked_cells)


def count_loops(maze: MazeGenerator) -> int:
    nodes = count_active_cells(maze)
    edges = count_edges(maze)

    return edges - nodes + 1


for seed in range(100):
    maze = MazeGenerator(25, 20, seed)
    maze.generate_imperfect()

    loops = count_loops(maze)

    if loops < 2:
        print(f"IMPERFECT FAIL seed={seed}, loops={loops}")