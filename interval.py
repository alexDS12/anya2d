from __future__ import annotations

try:
    from sympy import Point2D
except ImportError as e:
    raise Exception('Unable to import SymPy, make sure you have it installed')


class Interval:
    """An interval is a set of continuous and visible points from any discrete row in the grid.

    Attributes
    ----------
    _left : float
        leftmost point of the interval
    _right : float
        rightmost point of the interval
    _row : int
        Y axis denotating which row the interval is projected to

    """
    DOUBLE_INEQUALITY_THRESHOLD = 1e-07
    EPSILON = 1e-07

    def __init__(
            self,
            left: float,
            right: float,
            row: int
        ):
        self._left = left
        self._right = right
        self._row = row
        self.discrete_left = False
        self.discrete_right = False

    @property
    def left(self) -> float:
        return self._left

    @left.setter
    def left(self, left: float) -> None:
        self._left = left

        self.discrete_left = abs(int(left + self.EPSILON) - left) < self.EPSILON
        if self.discrete_left:
            self._left = int(self._left + self.EPSILON)
    
    @property
    def right(self) -> float:
        return self._right

    @right.setter
    def right(self, right: float) -> None:
        self._right = right

        self.discrete_right = abs(int(right + self.EPSILON) - right) < self.EPSILON
        if self.discrete_right:
            self._right = int(self._right + self.EPSILON)

    @property
    def row(self) -> int:
        return self._row

    @row.setter
    def row(self, row: int) -> None:
        self._row = row

    def range_size(self) -> float:
        return self._right - self._left
    
    def covers(self, other_interval: Interval) -> bool:
        """Check if intervals are identical or if interval covers other interval"""
        if self == other_interval:
            return True

        return self._left <= other_interval.left and \
               self._right >= other_interval.right and \
               self._row == other_interval.row
    
    def contains(self, point_position: Point2D) -> bool:
        """Check if a point is in the interval. row_num is Y whereas left and right control X"""
        return self._row == int(point_position.y) and \
               self._left <= point_position.x + self.EPSILON and \
               self._right + self.EPSILON >= point_position.x
    
    def __eq__(self, other_interval: Interval) -> bool:
        """Check if all attributes from two intervals are the same"""
        if not isinstance(other_interval, type(self)):
            return False
        
        return abs(other_interval.left - self._left) < self.DOUBLE_INEQUALITY_THRESHOLD and \
               abs(other_interval.right - self._right) < self.DOUBLE_INEQUALITY_THRESHOLD and \
               self._row == other_interval.row
        
    def __repr__(self) -> str:
        """Debug representation of the interval"""
        return f'Interval(left: {self._left}, right: {self._right}, row: {self._row})'