from __future__ import annotations


class GridPosition:
    def __init__(
        self,
        x: int = 0,
        y: int = 0
    ):
        self.x = x
        self.y = y

    def __hash__(self) -> int:
        return 31 * self.x + self.y

    def __eq__(self, gp: GridPosition) -> bool:
        """Check if two grid positions are identical"""
        if self is gp:
            return True
        elif not isinstance(gp, type(self)):
            return False
        return self.x == gp.x and self.y == gp.y

    def __repr__(self) -> str:
        """Debug representation of the grid position"""
        return f'[{self.x}, {self.y}]'
