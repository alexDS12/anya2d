from __future__ import annotations

from vertex import Vertex
from typing import Optional


class Path:
    """Describes a path in a graph in terms of its constituent vertices
    and their associated cumulative cost. i.e. the cost to step from 
    the start vertex to the current vertex, i

    Attributes
    ----------
    _vertex : Optional[Vertex]
        Start node vertex
    _next : Optional[Path]
        Points to the next path in the graph
    _prev : Optional[Path]
        Points to the previous path in the graph
    _path_cost : Optional[float]
        Cost between two vertices that compose the path

    """

    def __init__(
        self,
        vertex: Optional[Vertex] = None,
        next: Optional[Path] = None,
        path_cost: Optional[float] = None
    ):
        if not vertex and not next and not path_cost:
            pass # when initializing a new search, there are no attributes for the first node

        self._vertex = vertex
        self._path_cost = path_cost
        self._next = next
        if next is not None:
            self._next.prev = self

    @property
    def path_cost(self) -> float:
        return self._path_cost

    @property
    def next(self) -> Optional[Path]:
        return self._next

    @property
    def prev(self) -> Optional[Path]:
        return self._prev
    
    @prev.setter
    def prev(self, prev: Path) -> None:
        self._prev = prev

    @property
    def vertex(self) -> Optional[Vertex]:
        return self._vertex
