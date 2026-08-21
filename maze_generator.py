import random


class MazeGenerator:
    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height

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


    def get_unvisited_neighbors(self,x: int, y: int, visited: set[tuple[int, int]]) -> list[tuple[int, int]]:
        neighbors = self.get_neighbors(x,y)
        unvisited = []

        for neighbor in neighbors:
            if neighbor not in visited:
                unvisited.append(neighbor)

        return unvisited

    
    def generate_perfect(self) -> None:
        start = (0,0)

        visited = {start}
        stack = [start]

        while stack:
            x,y = stack[-1]

            unvisited = self.get_unvisited_neighbors(x,y, visited)

            if unvisited:
                next_x, next_y = random.choice(unvisited)

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
            if nx == x + 1 and self.grid[y][x] & 2:
                closed.append((nx, ny))
            
            elif nx == x - 1 and self.grid[y][x] & 8:
                closed.append((nx, ny))
            
            elif ny == ny + 1 and self.grid[y][x] & 4:
                closed.append((nx, ny))
            
            elif ny == ny - 1 and self.grid[y][x] & 1:
                closed.append((nx, ny))
            
        return closed
    

    def generate_imperfect(self) -> None:
        self.generate_perfect()

        dead_cells = self.find_dead_cell()

        for x, y in dead_cells:
            closed_neigbors = self.get_closed_neighbors(x, y)

            if closed_neigbors:
                nx, ny = random.choice(closed_neigbors)
                self.remove_wall(x, y, nx, ny)


if __name__ == "__main__":

    maze = MazeGenerator(8,6)
    # maze.remove_wall(3,1,2,1)
    # visited = {(1, 0), (0, 1)}

    # print(maze.get_unvisited_neighbors(1, 1, visited ))
    maze.generate_perfect()
    for row in maze.grid:
        print(row)