from __future__ import annotations

from enum import Enum, auto
from point import Point2D


class Vertex:
    """Representation of a vertex.
    All vertices associated with a given cell are called discrete points of the grid.

    Attributes
    ----------
    id : int
        Vertex identification
    position : Point2D
        Discrete XY position of the vertex
    cell_directions : Enum
        All possible directions from a cell
    vertex_directions : Enum
        All possible vertex directions

    """

    def __init__(self, id: int, position: Point2D):
        self.id = id
        self.position = position

    def __eq__(self, v: Vertex) -> bool:
       """Check if two vertices have same id"""
       return self.id == v.id
    
    def __hash__(self) -> int:
        """Hash vertex attrs so vertices can be compared between themselves"""
        return super().__hash__()

    def __repr__(self) -> str:
        """Debug representation of the vertex"""
        return f'Vertex(id: {self.id}, pos: {self.position}'


class CellDirections(Enum):
    CD_LEFTDOWN = auto()
    CD_LEFTUP = auto()
    CD_RIGHTDOWN = auto()
    CD_RIGHTUP = auto()


class VertexDirections(Enum):
    VD_LEFT = auto()
    VD_RIGHT = auto()
    VD_DOWN = auto()
    VD_UP = auto()
