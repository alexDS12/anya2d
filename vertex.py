from __future__ import annotations

from enum import Enum, auto
from edge import Edge
from grid_position import GridPosition
from point import Point2D
from typing import Optional, Set


class Vertex:
    """Representation of a vertex.
    All vertices associated with a given cell are called discrete points of the grid.

    Attributes
    ----------
    id : int
        Vertex identification
    position : Point2D
        Discrete XY position of the vertex
    grid_position : GridPosition
        Vertex's discrete XY position in the grid
    incoming_edges : Set[Edge]
        Edges that end at current vertex
    outgoing_edges : Set[Edge]
        Edges that start at current vertex
    cell_directions : Enum
        All possible directions from a cell
    vertex_directions : Enum
        All possible vertex directions

    """

    def __init__(self, id: int, position: Point2D, grid_position: GridPosition):
        self.id = id
        self.position = position
        self.grid_position = grid_position
        self.incoming_edges = set()
        self.outgoing_edges = set()
    
    @property
    def touching_edges(self) -> Set[Edge]:
        """Get union of incoming and outgoing edges"""
        return self.incoming_edges | self.outgoing_edges
    
    def add_outgoing_edge(self, e: Edge) -> None:
        self.outgoing_edges.add(e)

    def add_incoming_edge(self, e: Edge) -> None:
        self.incoming_edges.add(e)

    def remove_incoming_edge(self, e: Edge) -> None:
        self.incoming_edges.discard(e)

    def remove_outgoing_edge(self, e: Edge) -> None:
        self.outgoing_edges.discard(e)

    def get_outgoing_neighbors(self) -> Set[Vertex]:
        """Get all neighbors' vertices of current vertex"""
        return {e.end for e in self.outgoing_edges}
    
    def get_outgoing_to(self, target: Optional[Vertex]) -> Optional[Edge]:
        """Get outgoing edge to given target vertex"""
        if target is None:
            return None
        
        for e in self.outgoing_edges:
            if e.end == target:
                return e
        return None

    def get_incoming_from(self, start: Vertex) -> Optional[Edge]:
        """Get incoming edge from a given start vertex"""
        for e in self.incoming_edges:
            if e.start == start:
                return e
        return None

    def __eq__(self, v: Vertex) -> bool:
       """Check if two vertices have same id"""
       return self.id == v.id

    def __repr__(self) -> str:
        """Debug representation of the vertex"""
        return f'Vertex(id: {self.id}, pos: {self.position}, grid position: {self.grid_position})'


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
