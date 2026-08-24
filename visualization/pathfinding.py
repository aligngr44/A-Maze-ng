from collections import deque
from config.read_file import Config

NORTH, EAST, SOUTH, WEST = 1, 2, 4, 8

DIRECTIONS = {
    "N": (NORTH, 0, -1),
    "E": (EAST, 1, 0),
    "S": (SOUTH, 0, 1),
    "W": (WEST, -1, 0),
}


def get_open_neighbors(grid, width, height, x, y):
    cell = grid[y][x]          # 1) bu hücrenin değerini al
    result = []             # 2) sonuçları biriktireceğin boş liste

    for direction, (bit, dx, dy) in DIRECTIONS.items():
        if not (cell & bit):                          # 3) bu yönün duvarı açık mı?
            nx, ny = dx + x, dy + y             # 4) komşunun koordinatını hesapla
            if 0 <= nx < width and 0 <= ny < height:      # 5) sınır içinde mi kontrolü
                result.append((direction, (nx, ny)))

    return result


def shortest_path(grid, width, height, entry, exit_):
    visited = {entry}
    queue = deque([entry])
    came_from = {}
    while queue:
        current = queue.popleft()

        if current == exit_:
            break

        for direction, neighbor in get_open_neighbors(grid, width, height, *current):
            if neighbor not in visited:
                visited.add(neighbor)
                came_from[neighbor] = (current, direction)
                queue.append(neighbor)

    # while bitti, şimdi path'i geriye doğru kuralım
    directions = []
    node = exit_
    while node != entry:
        prev, direction = came_from[node]
        directions.append(direction)
        node = prev

    directions.reverse()
    return "".join(directions)


def path_cells(entry: tuple[int, int], path: str) -> set[tuple[int, int]]:
    x, y = entry
    cells = {entry}

    for direction in path:
        _, dx, dy = DIRECTIONS[direction]
        x, y = x + dx, y + dy
        cells.add((x, y))

    return cells
