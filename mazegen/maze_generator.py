"""Reusable maze generation module."""

import random
from collections import deque


class MazeGenerator:
    """Generate perfect and imperfect mazes using a bitmask grid."""

    Pattern_42 = [
        "0000000",
        "1000111",
        "1000001",
        "1110111",
        "0010100",
        "0010111",
        "0000000",
    ]

    def __init__(
        self,
        width: int,
        height: int,
        seed: int | None = None,
    ) -> None:
        """Initialize a maze with all cell walls closed."""
        self.width = width
        self.height = height
        self.random = random.Random(seed)
        self.blocked_cells: set[tuple[int, int]] = set()
        self.grid: list[list[int]] = []

        for _ in range(height):
            row = []

            for _ in range(width):
                row.append(15)

            self.grid.append(row)

    def remove_wall(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
    ) -> None:
        """Remove the shared wall between two adjacent cells."""
        if x2 == x1 + 1:
            self.grid[y1][x1] &= ~2
            self.grid[y2][x2] &= ~8

        elif x2 == x1 - 1:
            self.grid[y1][x1] &= ~8
            self.grid[y2][x2] &= ~2

        elif y2 == y1 + 1:
            self.grid[y1][x1] &= ~4
            self.grid[y2][x2] &= ~1

        elif y2 == y1 - 1:
            self.grid[y1][x1] &= ~1
            self.grid[y2][x2] &= ~4

    def get_neighbors(self, x: int, y: int) -> list[tuple[int, int]]:
        """Return all in-bounds neighboring cells."""
        neighbors = []

        if y > 0:
            neighbors.append((x, y - 1))

        if x < self.width - 1:
            neighbors.append((x + 1, y))

        if y < self.height - 1:
            neighbors.append((x, y + 1))

        if x > 0:
            neighbors.append((x - 1, y))

        return neighbors

    def create_42_pattern(self, start_x: int, start_y: int) -> None:
        """Add the blocked cells forming the 42 pattern."""
        for pattern_y, row in enumerate(self.Pattern_42):
            for pattern_x, value in enumerate(row):
                if value == "1":
                    x = start_x + pattern_x
                    y = start_y + pattern_y

                    if 0 <= x < self.width and 0 <= y < self.height:
                        self.blocked_cells.add((x, y))

    def place_42_pattern(self) -> None:
        """Place the 42 pattern in the center of the maze."""
        pattern_height = len(self.Pattern_42)
        pattern_width = len(self.Pattern_42[0])

        min_width = pattern_width + 4
        min_height = pattern_height + 4

        if self.width < min_width or self.height < min_height:
            print("Warning: maze is too small for the 42 pattern")
            return

        start_x = (self.width - pattern_width) // 2
        start_y = (self.height - pattern_height) // 2

        self.create_42_pattern(start_x, start_y)

    def get_unvisited_neighbors(
        self,
        x: int,
        y: int,
        visited: set[tuple[int, int]],
    ) -> list[tuple[int, int]]:
        """Return neighboring cells not yet visited or blocked."""
        neighbors = self.get_neighbors(x, y)
        unvisited = []

        for neighbor in neighbors:
            if (
                neighbor not in visited
                and neighbor not in self.blocked_cells
            ):
                unvisited.append(neighbor)

        return unvisited

    def generate_perfect(self) -> None:
        """Generate a perfect maze using iterative DFS backtracking."""
        self.place_42_pattern()

        start = (0, 0)
        visited = {start}
        stack = [start]

        while stack:
            x, y = stack[-1]

            unvisited = self.get_unvisited_neighbors(x, y, visited)

            if unvisited:
                next_x, next_y = self.random.choice(unvisited)

                self.remove_wall(x, y, next_x, next_y)

                visited.add((next_x, next_y))
                stack.append((next_x, next_y))

            else:
                stack.pop()

    def count_open_paths(self, x: int, y: int) -> int:
        """Return the number of open walls for a cell."""
        cell = self.grid[y][x]
        count = 0

        if not cell & 1:
            count += 1

        if not cell & 2:
            count += 1

        if not cell & 4:
            count += 1

        if not cell & 8:
            count += 1

        return count

    def find_dead_cell(self) -> list[tuple[int, int]]:
        """Return cells that have exactly one open path."""
        dead_cell = []

        for y in range(self.height):
            for x in range(self.width):
                if self.count_open_paths(x, y) == 1:
                    dead_cell.append((x, y))

        return dead_cell

    def get_closed_neighbors(
        self,
        x: int,
        y: int,
    ) -> list[tuple[int, int]]:
        """Return adjacent cells separated by a closed wall."""
        closed = []

        for nx, ny in self.get_neighbors(x, y):
            if (nx, ny) in self.blocked_cells:
                continue

            if nx == x + 1 and self.grid[y][x] & 2:
                closed.append((nx, ny))

            elif nx == x - 1 and self.grid[y][x] & 8:
                closed.append((nx, ny))

            elif ny == y + 1 and self.grid[y][x] & 4:
                closed.append((nx, ny))

            elif ny == y - 1 and self.grid[y][x] & 1:
                closed.append((nx, ny))

        return closed

    def creates_open_3x3(self) -> bool:
        """Check if there is a fully open 3x3 area."""
        for y in range(self.height - 2):
            for x in range(self.width - 2):

                horizontal_open = True
                vertical_open = True

                for row in range(y, y + 3):
                    for col in range(x, x + 2):
                        if self.grid[row][col] & 2:
                            horizontal_open = False

                for row in range(y, y + 2):
                    for col in range(x, x + 3):
                        if self.grid[row][col] & 4:
                            vertical_open = False

                if horizontal_open and vertical_open:
                    return True

        return False

    def generate_imperfect(self) -> None:
        """Generate an imperfect maze by adding loops to a perfect maze."""
        self.generate_perfect()

        dead_cells = self.find_dead_cell()

        for x, y in dead_cells:
            closed_neighbors = self.get_closed_neighbors(x, y)

            if closed_neighbors:
                nx, ny = self.random.choice(closed_neighbors)

                old_cell = self.grid[y][x]
                old_neighbor = self.grid[ny][nx]

                self.remove_wall(x, y, nx, ny)

                if self.creates_open_3x3():
                    self.grid[y][x] = old_cell
                    self.grid[ny][nx] = old_neighbor

    def write_grid(self, filename: str) -> None:
        """Write the maze grid to a file using hexadecimal wall values."""
        with open(filename, "w") as file:
            for row in self.grid:
                for cell in row:
                    file.write(format(cell, "X"))
                file.write("\n")

    def get_open_neighbors(
        self,
        x: int,
        y: int,
    ) -> list[tuple[int, int]]:
        """Return neighboring cells connected through an open wall."""
        open_neighbors = []

        for nx, ny in self.get_neighbors(x, y):
            if nx == x + 1 and not self.grid[y][x] & 2:
                open_neighbors.append((nx, ny))

            elif nx == x - 1 and not self.grid[y][x] & 8:
                open_neighbors.append((nx, ny))

            elif ny == y + 1 and not self.grid[y][x] & 4:
                open_neighbors.append((nx, ny))

            elif ny == y - 1 and not self.grid[y][x] & 1:
                open_neighbors.append((nx, ny))

        return open_neighbors

    def get_solution(
        self,
        start: tuple[int, int],
        exit_: tuple[int, int],
    ) -> list[tuple[int, int]]:
        """Return the shortest path between two cells using BFS."""
        start_x, start_y = start
        exit_x, exit_y = exit_

        if not (
            0 <= start_x < self.width
            and 0 <= start_y < self.height
            and 0 <= exit_x < self.width
            and 0 <= exit_y < self.height
        ):
            return []

        if start in self.blocked_cells or exit_ in self.blocked_cells:
            return []

        queue = deque([start])
        visited = {start}
        parent: dict[
            tuple[int, int],
            tuple[int, int] | None,
        ] = {start: None}

        while queue:
            x, y = queue.popleft()

            if (x, y) == exit_:
                break

            for neighbor in self.get_open_neighbors(x, y):
                if neighbor not in visited:
                    visited.add(neighbor)
                    parent[neighbor] = (x, y)
                    queue.append(neighbor)

        if exit_ not in parent:
            return []

        path = []
        current: tuple[int, int] | None = exit_

        while current is not None:
            path.append(current)
            current = parent[current]

        path.reverse()

        return path
