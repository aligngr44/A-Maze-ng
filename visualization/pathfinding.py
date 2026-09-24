"""Shortest-path finding over the maze grid (BFS from entry to exit)."""

from collections import deque

NORTH, EAST, SOUTH, WEST = 1, 2, 4, 8

DIRECTIONS = {
    "N": (NORTH, 0, -1),
    "E": (EAST, 1, 0),
    "S": (SOUTH, 0, 1),
    "W": (WEST, -1, 0),
}


def get_open_neighbors(
    grid: list[list[int]], width: int, height: int, x: int, y: int
) -> list[tuple[str, tuple[int, int]]]:
    """Return (direction, coordinates) for each open, in-bounds neighbor."""
    cell = grid[y][x]
    result = []

    for direction, (bit, dx, dy) in DIRECTIONS.items():
        if not (cell & bit):
            nx, ny = dx + x, dy + y
            if 0 <= nx < width and 0 <= ny < height:
                result.append((direction, (nx, ny)))

    return result


def shortest_path(
    grid: list[list[int]],
    width: int,
    height: int,
    entry: tuple[int, int],
    exit_: tuple[int, int],
) -> str:
    """Return the shortest entry-to-exit path as N/E/S/W letters."""
    visited = {entry}
    queue = deque([entry])
    came_from: dict[tuple[int, int], tuple[tuple[int, int], str]] = {}
    while queue:
        current = queue.popleft()

        if current == exit_:
            break

        neighbors = get_open_neighbors(grid, width, height, *current)
        for direction, neighbor in neighbors:
            if neighbor not in visited:
                visited.add(neighbor)
                came_from[neighbor] = (current, direction)
                queue.append(neighbor)

    directions = []
    node = exit_
    while node != entry:
        prev, direction = came_from[node]
        directions.append(direction)
        node = prev

    directions.reverse()
    return "".join(directions)


def path_cells(entry: tuple[int, int], path: str) -> set[tuple[int, int]]:
    """Return every grid cell visited while walking path from entry."""
    x, y = entry
    cells = {entry}

    for direction in path:
        _, dx, dy = DIRECTIONS[direction]
        x, y = x + dx, y + dy
        cells.add((x, y))

    return cells
