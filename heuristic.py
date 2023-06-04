from math import nan
from functools import cache
from node import Node
from vertex import Vertex
from constants import EPSILON
from typing import Optional


class EuclideanDistanceHeuristic:
    """A heuristic for computing Euclidean distances in the plane."""
    def get_value(
        self,
        n: Optional[Vertex],
        t: Optional[Vertex] = None
    ) -> float:
        if n is None or t is None:
            return 0
        return self.h(*n.position, *t.position)

    def h(self, x1: float, y1: float, x2: float, y2: float) -> float:
        return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5


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

    @cache
    def get_value(
        self,
        n: Node,
        t: Optional[Node] = None
    ) -> float:
        """Calculate heuristic between `n` and `t`.
        The target node must have an interval that only has its XY point, that means
        interval left == right == target.root.x; and interval row == target.root.y
        """
        if t is None:
            return 0

        assert (t.root.y == t.interval.row and
                t.root.x == t.interval.left and
                t.root.x == t.interval.right)

        irow = int(n.interval.row)
        ileft = float(n.interval.left)
        iright = float(n.interval.right)
        targetx = float(t.root.x)
        targety = float(t.root.y)
        rootx = float(n.root.x)
        rooty = float(n.root.y)

        if rooty < irow and targety < irow:
            targety += 2 * (irow - targety)
        elif rooty > irow and targety > irow:
            targety -= 2 * (targety - irow)

        # project the interval endpoints onto the target row
        rise_root_to_irow = abs(rooty - irow)
        rise_irow_to_target = abs(irow - targety)
        lrun = rootx - ileft
        rrun = iright - rootx
        left_proj = ileft - rise_irow_to_target * (lrun / rise_root_to_irow) if rise_root_to_irow != 0.0 else nan
        right_proj = iright + rise_irow_to_target * (rrun / rise_root_to_irow) if rise_root_to_irow != 0.0 else nan
        
        if (targetx + EPSILON) < left_proj:
            return self._h.h(rootx, rooty, ileft, irow) + self._h.h(ileft, irow, targetx, targety)

        if targetx > (right_proj + EPSILON):
            return self._h.h(rootx, rooty, iright, irow) + self._h.h(iright, irow, targetx, targety)

        return self._h.h(rootx, rooty, targetx, targety)
