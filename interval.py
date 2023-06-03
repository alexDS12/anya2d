from __future__ import annotations

from point import Point2D
from constants import DOUBLE_INEQUALITY_THRESHOLD, EPSILON


class Interval:
    """An interval is a set of continuous and visible points from any discrete row in the grid.
    Any row of the grid can be divided into maximally continuous sets of traversable and non-traversable points.
    An interval can be split repeatedly until all corner points are end points of intervals.

    Attributes
    ----------
    _left : float
        leftmost point of the interval
    _right : float
        rightmost point of the interval
    _row : int
        Y axis denotating which row the interval is projected to
    discrete_left : bool
        Indicates whether or not left point is discrete
    discrete_right : bool
        Indicates whether or not right point is discrete
    
    """

    def __init__(self, left: float, right: float, row: int):
        self.init(left, right, row)

    def init(self, left: float, right: float, row: int) -> None:
        """Use property setters to assign _left, _right and _row"""
        self.left = left
        self.right = right
        self.row = row

    @property
    def left(self) -> float:
        """Get or set left point of interval and whether it's discrete"""
        return self._left

    @left.setter
    def left(self, left: float) -> None:
        self._left = left

        self.discrete_left = abs(int(left + EPSILON) - left) < EPSILON
        if self.discrete_left:
            self._left = int(self._left + EPSILON)

    @property
    def right(self) -> float:
        """Get or set right point of interval and whether it's discrete"""
        return self._right

    @right.setter
    def right(self, right: float) -> None:
        self._right = right

        self.discrete_right = abs(int(right + EPSILON) - right) < EPSILON
        if self.discrete_right:
            self._right = int(self._right + EPSILON)

    @property
    def row(self) -> int:
        """Get or set row of interval"""
        return self._row

    @row.setter
    def row(self, row: int) -> None:
        self._row = row

    def range_size(self) -> float:
        """Get interval size"""
        return self._right - self._left

    def covers(self, i: Interval) -> bool:
        """Check if intervals are identical or if this interval covers interval `i`"""
        if self == i:
            return True

        return self._left <= i.left and self._right >= i.right and self._row == i.row

    def contains(self, p: Point2D) -> bool:
        """Check if a point is in the interval. 
        row is Y whereas left and right control X
        """
        return (int(p.y) == self._row and 
                (p.x + EPSILON) >= self._left and 
                p.x <= (self._right + EPSILON))

    def __eq__(self, i: Interval) -> bool:
        """Check if all attributes from two intervals are the same"""
        if not isinstance(i, type(self)):
            return False

        return abs(i.left - self._left) < DOUBLE_INEQUALITY_THRESHOLD and \
               abs(i.right - self._right) < DOUBLE_INEQUALITY_THRESHOLD and \
               i.row == self._row

    def __hash__(self) -> int:
        """Hash interval attrs so intervals can be compared"""
        return hash((self._left, self._right, self._row))

    def __repr__(self) -> str:
        """Debug representation of the interval"""
        return f'Interval({self._left}, {self._right}, {self._row})'
