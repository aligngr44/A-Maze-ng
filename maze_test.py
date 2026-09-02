from maze_generator import MazeGenerator


# def count_edges(maze: MazeGenerator) -> int:
#     edges = 0

#     for y in range(maze.height):
#         for x in range(maze.width):
#             if (x, y) in maze.blocked_cells:
#                 continue

#             if x + 1 < maze.width:
#                 if not maze.grid[y][x] & 2:
#                     edges += 1

#             if y + 1 < maze.height:
#                 if not maze.grid[y][x] & 4:
#                     edges += 1

#     return edges


# def count_active_cells(maze: MazeGenerator) -> int:
#     return maze.width * maze.height - len(maze.blocked_cells)


# def count_loops(maze: MazeGenerator) -> int:
#     nodes = count_active_cells(maze)
#     edges = count_edges(maze)

#     return edges - nodes + 1


# for seed in range(100):
#     maze = MazeGenerator(25, 20, seed)
#     maze.generate_imperfect()

#     loops = count_loops(maze)

#     if loops < 2:
#         print(f"IMPERFECT FAIL seed={seed}, loops={loops}")


from maze_generator import MazeGenerator


def get_open_neighbors(
    maze: MazeGenerator,
    x: int,
    y: int
) -> list[tuple[int, int]]:
    open_neighbors = []

    for nx, ny in maze.get_neighbors(x, y):
        if nx == x + 1 and not maze.grid[y][x] & 2:
            open_neighbors.append((nx, ny))

        elif nx == x - 1 and not maze.grid[y][x] & 8:
            open_neighbors.append((nx, ny))

        elif ny == y + 1 and not maze.grid[y][x] & 4:
            open_neighbors.append((nx, ny))

        elif ny == y - 1 and not maze.grid[y][x] & 1:
            open_neighbors.append((nx, ny))

    return open_neighbors


def check_full_connectivity(maze: MazeGenerator) -> None:
    start = (0, 0)

    if start in maze.blocked_cells:
        raise ValueError("Start cell is blocked")

    reachable = {start}
    stack = [start]

    while stack:
        x, y = stack.pop()

        for neighbor in get_open_neighbors(maze, x, y):
            if (
                neighbor not in reachable
                and neighbor not in maze.blocked_cells
            ):
                reachable.add(neighbor)
                stack.append(neighbor)

    all_cells = set()

    for y in range(maze.height):
        for x in range(maze.width):
            if (x, y) not in maze.blocked_cells:
                all_cells.add((x, y))

    if reachable != all_cells:
        unreachable = all_cells - reachable
        raise ValueError(
            f"Maze is not fully connected. "
            f"Unreachable cells: {unreachable}"
        )









maze = MazeGenerator(25, 20, 42)
maze.generate_imperfect()

try:
    check_full_connectivity(maze)
    print("Connectivity OK")
except ValueError as error:
    print(error)