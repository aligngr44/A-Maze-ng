"""Expose the public interface of the mazegen package."""

from .maze_generator import MazeGenerator

__all__: list[str] = [
    "MazeGenerator",
]
