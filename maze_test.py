"""Automated tests for MazeGenerator, config parsing, and pathfinding.

Run with: pytest
"""

from pathlib import Path

import pytest

from config.read_file import Config, pars, read_to_file
from config.validate import check_entry_exit_not_blocked, validate_config
from mazegen import MazeGenerator
from visualization.pathfinding import shortest_path

NORTH, EAST, SOUTH, WEST = 1, 2, 4, 8


def open_neighbors(
    maze: MazeGenerator, x: int, y: int
) -> list[tuple[int, int]]:
    """Return neighbors of (x, y) reachable through an open wall."""
    neighbors = []
    for nx, ny in maze.get_neighbors(x, y):
        if nx == x + 1 and not maze.grid[y][x] & EAST:
            neighbors.append((nx, ny))
        elif nx == x - 1 and not maze.grid[y][x] & WEST:
            neighbors.append((nx, ny))
        elif ny == y + 1 and not maze.grid[y][x] & SOUTH:
            neighbors.append((nx, ny))
        elif ny == y - 1 and not maze.grid[y][x] & NORTH:
            neighbors.append((nx, ny))
    return neighbors


def reachable_cells(
    maze: MazeGenerator, start: tuple[int, int]
) -> set[tuple[int, int]]:
    """Flood-fill from start over open walls; return every reachable cell."""
    reached = {start}
    stack = [start]
    while stack:
        x, y = stack.pop()
        for neighbor in open_neighbors(maze, x, y):
            if neighbor not in reached:
                reached.add(neighbor)
                stack.append(neighbor)
    return reached


def non_blocked_cells(maze: MazeGenerator) -> set[tuple[int, int]]:
    """Return every grid cell that is not part of the '42' pattern."""
    return {
        (x, y)
        for y in range(maze.height)
        for x in range(maze.width)
        if (x, y) not in maze.blocked_cells
    }


def count_open_edges(maze: MazeGenerator) -> int:
    """Count open walls between non-blocked cells, each edge once."""
    edges = 0
    for y in range(maze.height):
        for x in range(maze.width):
            if (x, y) in maze.blocked_cells:
                continue
            if x + 1 < maze.width and not maze.grid[y][x] & EAST:
                edges += 1
            if y + 1 < maze.height and not maze.grid[y][x] & SOUTH:
                edges += 1
    return edges


# --- Wall coherence ---------------------------------------------------------


def test_walls_are_coherent_between_neighbours() -> None:
    """A wall closed on one side must be closed on the neighbour's side."""
    maze = MazeGenerator(20, 15, seed=1)
    maze.generate_imperfect()
    for y in range(maze.height):
        for x in range(maze.width):
            if x + 1 < maze.width:
                east_closed = bool(maze.grid[y][x] & EAST)
                west_closed = bool(maze.grid[y][x + 1] & WEST)
                assert east_closed == west_closed
            if y + 1 < maze.height:
                south_closed = bool(maze.grid[y][x] & SOUTH)
                north_closed = bool(maze.grid[y + 1][x] & NORTH)
                assert south_closed == north_closed


# --- PERFECT=True: exactly one path, no loops -------------------------------


def test_generate_perfect_has_exactly_one_path() -> None:
    """PERFECT mode must build a spanning tree: connected, zero loops."""
    maze = MazeGenerator(15, 12, seed=7)
    maze.generate_perfect()
    cells = non_blocked_cells(maze)
    assert reachable_cells(maze, (0, 0)) == cells
    assert count_open_edges(maze) == len(cells) - 1


# --- PERFECT=False (default): Pac-Man-ready board ---------------------------


def test_generate_imperfect_is_fully_connected() -> None:
    """The default board must stay fully connected (winnable everywhere)."""
    maze = MazeGenerator(25, 20, seed=3)
    maze.generate_imperfect()
    assert reachable_cells(maze, (0, 0)) == non_blocked_cells(maze)


def test_generate_imperfect_has_at_least_two_independent_loops() -> None:
    """A chased player needs at least two independent routes."""
    maze = MazeGenerator(25, 20, seed=3)
    maze.generate_imperfect()
    cells = non_blocked_cells(maze)
    loops = count_open_edges(maze) - (len(cells) - 1)
    assert loops >= 2


def test_generate_imperfect_dead_ends_stay_rare() -> None:
    """The subject tolerates "a couple" of real dead-ends by default."""
    maze = MazeGenerator(25, 20, seed=3)
    maze.generate_imperfect()
    real_dead_ends = [
        cell
        for cell in maze.find_dead_cell()
        if cell not in maze.blocked_cells
    ]
    assert len(real_dead_ends) <= 2


def test_generate_imperfect_corners_and_centre_are_open() -> None:
    """The four corners and the centre must stay open for Pac-Man."""
    maze = MazeGenerator(25, 20, seed=3)
    maze.generate_imperfect()
    corners = {
        (0, 0),
        (maze.width - 1, 0),
        (0, maze.height - 1),
        (maze.width - 1, maze.height - 1),
    }
    centre = (maze.width // 2, maze.height // 2)
    for cell in corners | {centre}:
        assert cell not in maze.blocked_cells


# --- "42" pattern ------------------------------------------------------------


def test_42_pattern_is_placed_when_maze_is_large_enough() -> None:
    """A maze large enough for the pattern must contain blocked cells."""
    maze = MazeGenerator(25, 20, seed=3)
    maze.generate_perfect()
    assert len(maze.blocked_cells) > 0


def test_42_pattern_skipped_when_maze_too_small(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A maze too small for the pattern must warn instead of crashing."""
    maze = MazeGenerator(5, 5, seed=3)
    maze.generate_perfect()
    assert maze.blocked_cells == set()
    assert "too small" in capsys.readouterr().out


# --- Output file format ------------------------------------------------------


def test_write_grid_uses_one_hex_digit_per_cell(tmp_path: Path) -> None:
    """write_grid: one uppercase hex digit per cell, one row per line."""
    maze = MazeGenerator(4, 3, seed=2)
    maze.generate_perfect()
    output = tmp_path / "maze.txt"
    maze.write_grid(str(output))
    lines = output.read_text().splitlines()
    assert len(lines) == 3
    for line in lines:
        assert len(line) == 4
        assert all(ch in "0123456789ABCDEF" for ch in line)


# --- Config parsing & validation ---------------------------------------------


def test_read_to_file_ignores_comments_and_blank_lines(
    tmp_path: Path,
) -> None:
    """Comment (#) and blank lines must be skipped when reading."""
    config_file = tmp_path / "config.txt"
    config_file.write_text("# comment\nWIDTH=10\n\nHEIGHT=8\n")
    raw = read_to_file(str(config_file))
    assert raw == {"WIDTH": "10", "HEIGHT": "8"}


def test_read_to_file_rejects_malformed_line(tmp_path: Path) -> None:
    """A line without exactly one '=' must raise, not crash."""
    config_file = tmp_path / "config.txt"
    config_file.write_text("NOT_A_KEY_VALUE_LINE\n")
    with pytest.raises(ValueError):
        read_to_file(str(config_file))


def test_pars_requires_mandatory_keys() -> None:
    """Missing a mandatory key must raise ValueError, not KeyError."""
    with pytest.raises(ValueError):
        pars({"WIDTH": "10"})


def test_pars_builds_config() -> None:
    """A complete raw config dict must parse into the expected Config."""
    raw = {
        "WIDTH": "10",
        "HEIGHT": "8",
        "ENTRY": "0,0",
        "EXIT": "9,7",
        "OUTPUT_FILE": "maze.txt",
        "PERFECT": "True",
    }
    cfg = pars(raw)
    assert cfg == Config(
        width=10,
        height=8,
        entry=(0, 0),
        exit=(9, 7),
        output_file="maze.txt",
        perfect=True,
        seed=None,
    )


def test_validate_config_rejects_entry_equals_exit() -> None:
    """ENTRY and EXIT must not be the same cell."""
    cfg = Config(10, 8, (0, 0), (0, 0), "maze.txt", True, None)
    with pytest.raises(ValueError):
        validate_config(cfg)


def test_validate_config_rejects_out_of_bounds_exit() -> None:
    """EXIT must lie within the grid bounds."""
    cfg = Config(10, 8, (0, 0), (10, 8), "maze.txt", True, None)
    with pytest.raises(ValueError):
        validate_config(cfg)


def test_check_entry_exit_not_blocked_raises_when_blocked() -> None:
    """Entry/exit overlapping the '42' pattern must be rejected."""
    with pytest.raises(ValueError):
        check_entry_exit_not_blocked((0, 0), (1, 1), blocked_cells={(1, 1)})


# --- Pathfinding ---------------------------------------------------------


def test_shortest_path_matches_bfs_distance() -> None:
    """Walking the returned path from entry must land exactly on exit_."""
    maze = MazeGenerator(10, 8, seed=5)
    maze.generate_imperfect()
    entry, exit_ = (0, 0), (9, 7)
    path = shortest_path(maze.grid, maze.width, maze.height, entry, exit_)

    x, y = entry
    steps = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}
    for direction in path:
        dx, dy = steps[direction]
        x, y = x + dx, y + dy
    assert (x, y) == exit_
