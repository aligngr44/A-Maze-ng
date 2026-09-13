import random

class MazeGenerator:
    def __init__(
        self,
        width: int,
        height: int,
        seed: int | None = None,
    ) -> None:
        self.width = width
        self.height = height
        self.random = random.Random(seed)
        self.blocked_cells: set[tuple[int, int]] = set()
        self.grid = []

        for _ in range(height):
            row = []

            for _ in range(width):
                row.append(15)

            self.grid.append(row)

    def remove_wall(self, x1: int, y1: int, x2: int, y2: int) -> None:
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

    Pattern_42 = [
    "0000000",
    "1000111",
    "1000001",
    "1110111",
    "0010100",
    "0010111",
    "0000000",
    ]


    def create_42_pattern(self, start_x: int, start_y: int) -> None:
        for pattern_y, row in enumerate(self.Pattern_42):
            for pattern_x, value in enumerate(row):
                if value == "1":
                    x = start_x + pattern_x
                    y = start_y + pattern_y

                    if 0 <= x < self.width and 0 <= y < self.height:
                        self.blocked_cells.add((x,y))


    def place_42_pattern(self) -> None:
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


    def get_unvisited_neighbors(self,x: int, y: int, visited: set[tuple[int, int]]) -> list[tuple[int, int]]:
        neighbors = self.get_neighbors(x,y)
        unvisited = []

        for neighbor in neighbors:
            if neighbor not in visited and neighbor not in self.blocked_cells:
                unvisited.append(neighbor)

        return unvisited

    
    def generate_perfect(self) -> None:
        self.place_42_pattern()
        start = (0,0)

        visited = {start}
        stack = [start]

        while stack:
            x,y = stack[-1]

            unvisited = self.get_unvisited_neighbors(x,y, visited)

            if unvisited:
                next_x, next_y = self.random.choice(unvisited)

                self.remove_wall(x, y, next_x, next_y)
                
                visited.add((next_x, next_y))
                stack.append((next_x, next_y))

            else:
                stack.pop()


    def count_open_paths(self, x: int, y: int) -> int:
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
        dead_cell = []

        for y in range(self.height):
            for x in range(self.width):
                if self.count_open_paths(x, y) == 1:
                    dead_cell.append((x, y))
        
        return dead_cell


    def get_closed_neighbors(self, x: int, y: int) -> list[tuple[int, int]]: 
        closed = []

        for nx, ny in self.get_neighbors(x, y):
            if (nx, ny) in self.blocked_cells:
                continue

            elif nx == x + 1 and self.grid[y][x] & 2:
                closed.append((nx, ny))
            
            elif nx == x - 1 and self.grid[y][x] & 8:
                closed.append((nx, ny))
            
            elif ny == y + 1 and self.grid[y][x] & 4:
                closed.append((nx, ny))
            
            elif ny == y - 1 and self.grid[y][x] & 1:
                closed.append((nx, ny))
            
        return closed
    

    def generate_imperfect(self) -> None:
        self.generate_perfect()

        dead_cells = self.find_dead_cell()

        for x, y in dead_cells:
            closed_neigbors = self.get_closed_neighbors(x, y)

            if closed_neigbors:
                nx, ny = self.random.choice(closed_neigbors)
                self.remove_wall(x, y, nx, ny)



    def write_grid(self, filename: str) -> None:
        with open(filename, "w") as file:
            for row in self.grid:
                for cell in row:
                    file.write(format(cell, "X"))
                file.write("\n")

