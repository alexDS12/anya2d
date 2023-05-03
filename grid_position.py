from __future__ import annotations


class GridPosition:
    def __init__(
        self,
        x: int = 0,
        y: int = 0
    ):
        self._x = x
        self._y = y

    @property
    def x(self) -> int:
        """Get or set X position in the grid"""
        return self._x

    @x.setter
    def x(self, x: int) -> None:
        self._x = x

    @property
    def y(self) -> int:
        """Get or set Y position in the grid"""
        return self._y

    @y.setter
    def y(self, y: int) -> None:
        self._y = y

    def __eq__(self, other_position: GridPosition) -> bool:
        """Check if two grid positions are identical"""
        if not isinstance(other_position, type(self)):
            return False
        elif other_position is self:
            return True
        return self._x == other_position.x and self._y == other_position.y

    def __repr__(self) -> str:
        """Debug representation of the grid position"""
        return f'[{self._x}, {self._y}]'
