from __future__ import annotations

from interval import Interval
from typing import Optional

try:
    from sympy import Point2D, N
except ImportError as e:
    raise Exception('Unable to import SymPy, make sure you have it installed')


class Node:
    """Search node representation.
    A search node is a tuple (interval, root) where interval does not contain the root.

    Attributes
    ----------
    _root -- three dimensional point in a space
    _interval -- tuple of continuous and visible points from a discrete row of the grid
    _parent -- parent node of current node
    _f -- calculated total cost for node
    _g -- distance between current and start nodes based on parent's distance and Euclidian distance between parent and current nodes

    """
    def __init__(
            self, 
            root: Point2D,
            interval: Interval,
            parent: Optional[Node] = None
        ):
        self._root = root
        self._interval = interval
        self._parent = parent

        self._f = 0
        self._g = 0 if self._parent is None else self._parent.g + N(self._parent.root.distance(self._root))

    @property
    def root(self) -> Point2D:
        """Get or set XY node root"""
        return self._root
    
    @root.setter
    def root(self, root: Point2D) -> None:
        self._root = root

    @property
    def interval(self) -> Interval:
        """Get or set node interval"""
        return self._interval

    @interval.setter
    def interval(self, interval: Interval) -> None:
        self._interval = interval

    @property
    def parent(self) -> Optional[Node]:
        """Get or set parent node of current node"""
        return self._parent

    @parent.setter
    def parent(self, parent: Optional[Node]) -> None:
        self._parent = parent

    @property
    def f(self) -> float:
        """Get or set total cost for node"""
        return self._f

    @f.setter
    def f(self, f: float) -> None:
        self._f = f

    @property
    def g(self) -> float:
        """Get or set distance between current node and start node"""
        return self._g

    @g.setter
    def g(self, g: float) -> None:
        self._g = g

    def __eq__(self, other_node: Node) -> bool:
        """Check if two nodes are identical, same interval and XY root"""
        if not isinstance(other_node, type(self)):
            return False
        return self._interval == other_node.interval and self._root.equals(other_node.root)
    
    def __repr__(self) -> str:
        """Debug representation of the node"""
        return f'Node(root: {self._root}, interval: {self._interval}, f: {self._f}, g: {self._g}, parent: {self._parent})'