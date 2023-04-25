from math import sqrt
from vertex import Vertex
from node import Node
from typing import Optional


class EuclideanDistanceHeuristic:
    @classmethod
    def get_value(
            cls,
            n: Optional[Vertex],
            t: Optional[Vertex] = None
        ):
        if not n or not t:
            return 0
        return cls.distance(*n.position, *t.position)
    
    @classmethod
    def distance(cls, x1: int, y1: int, x2: int, y2: int) -> float:
        return sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


class Heuristic:
    """Anya heuristic differs from other heuristics due to the fact that
    Anya relies on intervals given those being composed of intermediate points.

    Anya only successfully terminates if the algorithm finds an interval that contains the target (or end) node.
    The target node must have an interval that only has its XY point, that means
    interval left == right == target.root.x; and interval row == target.root.y

    Example
    -------
    t = Node(root=(3, 4), interval=(3, 3, 4))

    Both current and target nodes must be on opposite sides of the interval or 
    both on the same row as the interval. If that condition is not met,
    target node is mirrored on the opposite side.

    Example
    -------
    n = Node(root=(2, 0), interval=(2, 4, 2))
    t = Node(root=(4, 1), interval=(4, 4, 1)) <--- mirrored to t' based on `n` interval

    t' = Node(root=(4, 3), interval=(4, 4, 3))
    """
    EPSILON = 1e-07

    def get_value(
            self,
            n: Node,
            t: Optional[Node] = None
        ) -> float:
        if not t:
            return 0
        
        assert t.root.y == t.interval.row and \
               t.root.x == t.interval.left and \
               t.root.x == t.interval.right
        
        i_row = n.interval.row
        i_left, i_right = n.interval.left, n.interval.right

        target_x, target_y = t.root
        root_x, root_y = n.root

        if root_y < i_row and target_y < i_row:
            target_y += 2 * (i_row - target_y)
        elif root_y > i_row and target_y > i_row:
            target_y -= 2 * (target_y - i_row)

        """project the interval endpoints onto the target row"""
        rise_root_to_i_row = abs(root_y - i_row)
        rise_i_row_to_target = abs(i_row - target_y)

        l_run = root_x - i_left
        r_run = i_right - root_x

        left_proj = i_left - rise_i_row_to_target * (l_run / rise_root_to_i_row)
        right_proj = i_right + rise_i_row_to_target * (r_run / rise_root_to_i_row)

        if (target_x + self.EPSILON) < left_proj:
            return EuclideanDistanceHeuristic.distance(root_x, root_y, i_left, i_row) + EuclideanDistanceHeuristic.distance(i_left, i_row, target_x, target_y)	

        if target_x > (right_proj + self.EPSILON):
            return EuclideanDistanceHeuristic.distance(root_x, root_y, i_right, i_row) + EuclideanDistanceHeuristic.distance(i_right, i_row, target_x, target_y)

        return EuclideanDistanceHeuristic.distance(root_x, root_y, target_x, target_y)