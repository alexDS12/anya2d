from __future__ import annotations

from typing import Optional, Set, Hashable, TYPE_CHECKING

if TYPE_CHECKING:  # hack to avoid circular import for type hint
    from vertex import Vertex


class Edge:
    """Representation of an edge.
    An edge is an open interval of continuous/intermediate points and 
    is limited by two discrete points that are represented by two vertices.

    Attributes
    ----------
    _id : int
        Edge identification
    _start : Vertex
        Discrete XY pair of coordinates that represents a vertex where an edge starts 
    _end : Vertex
        Discrete XY pair of coordinates that represents a vertex where an edge ends
    _weight : float
        Total cost of the current edge

    """

    def __init__(
        self,
        id: int,
        start: Vertex,
        end: Vertex,
        weight: float
    ):
        self._id = id
        self._start = start
        self._end = end
        self._weight = weight

    @property
    def id(self) -> int:
        """Get edge identification"""
        return self._id

    @property
    def start(self) -> Vertex:
        """Get start vertex of current edge"""
        return self._start

    @property
    def end(self) -> Vertex:
        """Get end vertex of current edge"""
        return self._end

    @property
    def weight(self) -> float:
        """Get edge's weight/cost"""
        return self._weight

    def __hash__(self) -> Hashable:
        return hash((self._id, self._start, self._end, self._weight))

    def __eq__(self, other_edge: Edge) -> bool:
        """Check if two edges have same id"""
        return self._id == other_edge.id

    def __repr__(self) -> str:
        """Debug representation of the edge"""
        return f'Edge(\n\tid: {self._id}, \n\tvertex start: {self._start}, \n\tvertex end: {self._end}, \n\tweight: {self._weight}\n)'
