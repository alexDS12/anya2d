from __future__ import annotations

from enum import Enum, auto
from edge import Edge
from grid_position import GridPosition
from typing import Optional, Set, Hashable

try:
    from sympy import Point2D
except ImportError as e:
    raise Exception('Unable to import SymPy, make sure you have it installed')


class Vertex:
    """Representation of a vertex.
    All vertices associated with a given cell are called discrete points of the grid.

    Attributes
    ----------
    _id : int
        Vertex identification
    _position : Point2D
        Discrete XY position of the vertex
    _grid_position : GridPosition
        Vertex's discrete XY position in the grid
    _incoming_edges : Set[Edge]
        Edges that end at current vertex
    _outgoing_edges : Set[Edge]
        Edges that start at current vertex
    cell_directions : Enum
        All possible directions from a cell
    vertex_directions : Enum
        All possible vertex directions

    """
    def __init__(
            self,
            id: int,
            position: Point2D,
            grid_position: GridPosition
        ):
        self._id = id
        self._position = position
        self._grid_position = grid_position
        self._incoming_edges = set()
        self._outgoing_edges = set()
        self.cell_directions = CellDirections()
        self.vertex_directions = VertexDirections()

    @property
    def id(self) -> int:
        """Get vertex identification"""
        return self._id

    @property
    def position(self) -> Point2D:
        """Get vertex XY position"""
        return self._position
    
    @property
    def grid_position(self) -> GridPosition:
        """Get vertex position in the grid"""
        return self._grid_position
    
    @property
    def incoming_edges(self) -> Set[Edge]:
        """Get edges coming to current vertex"""
        return self._incoming_edges
    
    @property
    def outgoing_edges(self) -> Set[Edge]:
        """Get edges going from current vertex"""
        return self._outgoing_edges
    
    @property
    def touching_edges(self) -> Set[Edge]:
        """Union between incoming and outgoing edges"""
        return self._incoming_edges | self._outgoing_edges

    def add_incoming_edge(self, edge: Edge) -> None:
        self._incoming_edges.add(edge)

    def remove_incoming_edge(self, edge: Edge) -> None:
        self._incoming_edges.discard(edge)

    def add_outgoing_edge(self, edge: Edge) -> None:
        self._outgoing_edges.add(edge)

    def remove_outgoing_edge(self, edge: Edge) -> None:
        self._outgoing_edges.discard(edge)

    def get_outgoing_to(self, target: Vertex) -> Optional[Edge]:
        """Get outgoing edge to given target vertex"""
        if not target:
            return None
        
        for edge in self._outgoing_edges:
            if edge.end == target:
                return edge
        return None

    def get_incoming_from(self, start: Vertex) -> Optional[Edge]:
        """Get incoming edge from a given start vertex"""
        if not start:
            return None
        
        for edge in self._incoming_edges:
            if edge.start == start:
                return edge
        return None
    
    def get_outgoing_neighbors(self) -> Set[Vertex]:
        """Get all neighbors' vertices of current vertex"""
        return {edge.end for edge in self._outgoing_edges}
    
    def __hash__(self) -> Hashable:
        return hash((self._id, self._position))

    def __eq__(self, other_vertex: Vertex) -> bool:
        """Check if two vertices have same id"""
        if not isinstance(other_vertex, type(self)):
            return False
        return self._id == other_vertex.id
    
    def __repr__(self) -> str:
        """Debug representation of the vertex"""
        return f'Vertex(id: {self._id}, grid position: {self._grid_position})'

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