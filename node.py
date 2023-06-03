from __future__ import annotations

from interval import Interval
from point import Point2D
from typing import Optional


class Node:
    """Search node representation.
    A search node is a tuple (interval, root) where interval does not contain the root.
    Moreover, a search node and its parents represent a single path between the points
    from the root to the current node

    Attributes
    ----------
    _root : Point2D
        Two dimensional point in a space
    _interval : Interval
        Tuple of continuous and visible points from a discrete row of the grid
    _parent : Optional[Node]
        Parent node of current node
    f : float
        Calculated total cost for node
    g : float
        Distance between current and start nodes based on parent's distance and 
        Euclidean distance between parent and current nodes

    """

    def __init__(
        self,
        interval: Interval,
        root: Point2D,
        parent: Optional[Node] = None
    ):
        self._interval = interval
        self._root = root
        self._parent = parent

        self.f = 0
        self.g = (0 if self._parent is None
                  else self._parent.g + self._parent.root.distance(self._root))
    
    @classmethod
    def from_points(
        cls,
        interval: Interval,
        rootx: int,
        rooty: int, 
        parent: Optional[Node] = None
    ) -> Node:
        """Create node based on raw points"""
        return cls(interval, Point2D(rootx, rooty), parent)

    @property
    def parent(self) -> Optional[Node]:
        """Get or set parent node of current node, a parent can be None"""
        return self._parent

    @parent.setter
    def parent(self, parent: Optional[Node]) -> None:
        self._parent = parent

    @property
    def interval(self) -> Interval:
        """Get or set node interval"""
        return self._interval

    @interval.setter
    def interval(self, interval: Interval) -> None:
        self._interval = interval

    @property
    def root(self) -> Point2D:
        """Get or set XY node root"""
        return self._root

    @root.setter
    def root(self, root: Point2D) -> None:
        self._root = root

    def __eq__(self, n: Node) -> bool:
        """Check if two nodes are identical, same interval and XY root"""
        if not isinstance(n, type(self)):
            return False

        if not n.interval == self._interval:
            return False
        return self._root == n.root

    def __hash__(self) -> int:
        """Hash node attrs so nodes can be compared between themselves"""
        return super().__hash__()

    def __repr__(self) -> str:
        """Debug representation of the node"""
        return f'root: {self._root}, {self._interval}'
