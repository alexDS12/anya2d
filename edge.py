from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # hack to avoid circular import for type hint
    from vertex import Vertex


class Edge:
    """Representation of an edge.
    An edge is an open interval of continuous/intermediate points and 
    is limited by two discrete points that are represented by two vertices.

    Attributes
    ----------
    id : int
        Edge identification
    start : Vertex
        Discrete XY pair of coordinates that represents a vertex where an edge starts 
    end : Vertex
        Discrete XY pair of coordinates that represents a vertex where an edge ends
    weight : float
        Total cost of the current edge

    """

    def __init__(
        self,
        id: int,
        start: Vertex,
        end: Vertex,
        weight: float
    ):
        self.id = id
        self.start = start
        self.end = end
        self.weight = weight

    def __eq__(self, e: Edge) -> bool:
        """Check if two edges have same id"""
        return self.id == e.id
    
    def __repr__(self) -> str:
        """Debug representation of the edge"""
        return f'Edge(\n\tid: {self.id}, \n\tvertex start: {self.start}, \n\tvertex end: {self.end}, \n\tweight: {self.weight}\n)'
