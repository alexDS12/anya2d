from math import nan
from node import Node
from vertex import Vertex
from constants import EPSILON, ROOT_TWO
from point import Point2D
from typing import Optional

# hacky implementation; we infer float and int as Number for method overload
from numbers import Number

try:
    from multipledispatch import dispatch
except ImportError as e:
    raise Exception('Unable to import multipledispatch, make sure you have it installed')


class EuclideanDistanceHeuristic:
    """A heuristic for computing Euclidean distances in the plane."""

    @dispatch(Vertex)
    def get_value(self, n: Vertex) -> float:
        return 0
    
    @dispatch(Vertex, Vertex)
    def get_value(
        self,
        n: Optional[Vertex],
        t: Optional[Vertex]
    ) -> float:
        if n is None or t is None:
            return 0
        return self.h(*n.position, *t.position)

    def h(self, x1: float, y1: float, x2: float, y2: float) -> float:
        return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5


class OctileDistanceHeuristic:
    def __init__(self, t: Vertex):
        self.target = t

    @dispatch(Vertex)
    def get_value(self, s: Vertex) -> float:
        if self.target is None:
            return 0
        return self.get_value(s, self.target)

    @dispatch(Vertex, Vertex)
    def get_value(self, s: Vertex, t: Vertex) -> float:
        if s is None:
            return 0
        return self.get_value(int(s.position.x), int(s.position.y),
                              int(t.position.x), int(t.position.y))

    @dispatch(Number, Number, Number, Number)
    def get_value(
        self,
        x1: Number,
        y1: Number,
        x2: Number,
        y2: Number
    ) -> float:
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return int(abs(dx - dy)) + min(dx, dy) * ROOT_TWO


class HackyHeuristic:
    def __init__(self):
        self.h = OctileDistanceHeuristic(None)
        self.target: Optional[Point2D] = None

    @dispatch(Point2D)
    def get_value(self, n: Point2D) -> float:
        if self.target is None:
            return 0
        return self.h.get_value(*n, *self.target)

    @dispatch(Point2D, Point2D)
    def get_value(self, n: Point2D, t: Point2D) -> float:
        return self.h.get_value(*n, *t)


class Heuristic:
    """Anya heuristic differs from other heuristics due to the fact that
    Anya relies on intervals given those being composed of intermediate points.

    Anya only successfully terminates if the algorithm finds an interval that contains 
    the target (or end) node.

    Both current and target nodes must be on opposite sides of the interval or 
    both on the same row as the interval. If that condition is not met,
    target node is mirrored on the opposite side.

    Attributes
    ----------
    _h : EuclideanDistanceHeuristic
        Heuristic to compute Euclidean distance between nodes

    Examples
    -------
    t = Node(root=(3, 4), interval=(3, 3, 4))

    Mirror target node:

    n = Node(root=(2, 0), interval=(2, 4, 2))
    t = Node(root=(4, 1), interval=(4, 4, 1)) <--- mirrored to t' based on interval of `n`

    t' = Node(root=(4, 3), interval=(4, 4, 3))

    """

    def __init__(self):
        self._h = EuclideanDistanceHeuristic()

    @dispatch(Node)
    def get_value(self, n: Node) -> float:
        return 0
    
    @dispatch(Node, Node)
    def get_value(
        self,
        n: Node,
        t: Node
    ) -> float:
        """Calculate heuristic between `n` and `t`.
        The target node must have an interval that only has its XY point, that means
        interval left == right == target.root.x; and interval row == target.root.y
        """
        assert (t.root.y == t.interval.row and
                t.root.x == t.interval.left and
                t.root.x == t.interval.right)

        irow = n.interval.row
        ileft = n.interval.left
        iright = n.interval.right
        targetx = t.root.x
        targety = t.root.y
        rootx = n.root.x
        rooty = n.root.y

        if rooty < irow and targety < irow:
            targety += 2 * (irow - targety)
        elif rooty > irow and targety > irow:
            targety -= 2 * (targety - irow)

        # project the interval endpoints onto the target row
        rise_root_to_irow = abs(n.root.y - n.interval.row)
        rise_irow_to_target = abs(n.interval.row - t.root.y)
        lrun = n.root.x - n.interval.left
        rrun = n.interval.right - n.root.x
        left_proj = n.interval.left - rise_irow_to_target * (lrun / rise_root_to_irow) if rise_root_to_irow != 0.0 else nan
        right_proj = n.interval.right + rise_irow_to_target * (rrun / rise_root_to_irow) if rise_root_to_irow != 0.0 else nan
        
        if (t.root.x + EPSILON) < left_proj:
            return self._h.h(rootx, rooty, ileft, irow) + self._h.h(ileft, irow, targetx, targety)

        if t.root.x > (right_proj + EPSILON):
            return self._h.h(rootx, rooty, iright, irow) + self._h.h(iright, irow, targetx, targety)

        return self._h.h(rootx, rooty, targetx, targety)
