from maze_generator import MazeGenerator


def print_maze(maze: MazeGenerator) -> None:
    for y in range(maze.height):
        top = ""
        middle = ""

        for x in range(maze.width):
            cell = maze.grid[y][x]

            top += "+"

            if cell & 1:
                top += "---"
            else:
                top += "   "

            if cell & 8:
                middle += "|"
            else:
                middle += " "

            middle += "   "

        top += "+"

        if maze.grid[y][maze.width - 1] & 2:
            middle += "|"
        else:
            middle += " "

        print(top)
        print(middle)

    bottom = ""

    for x in range(maze.width):
        bottom += "+"

        if maze.grid[maze.height - 1][x] & 4:
            bottom += "---"
        else:
            bottom += "   "

    bottom += "+"

    print(bottom)


maze = MazeGenerator(30, 10)

maze.generate_imperfect()

print_maze(maze)