from __future__ import annotations

# hacky implementation; we infer float and int as Number for method overload
from numbers import Number
from typing import Callable, Iterable, Tuple

try:
    from multipledispatch import dispatch
except ImportError as e:
    raise Exception('Unable to import multipledispatch, make sure you have it installed')


class Point2D:
    def __init__(self, x: float, y: float):
        self.set_location(x, y)

    @property
    def x(self) -> float:
        """Get or set X axis coordinate"""
        return self._x
    
    @x.setter
    def x(self, x: float) -> None:
        self._x = x
    
    @property
    def y(self) -> float:
        """Get or set Y axis coordinate"""
        return self._y
    
    @y.setter
    def y(self, y: float) -> None:
        self._y = y
    
    def set_location(self, x: float, y: float) -> None:
        """Combine X and Y setters within class"""
        self._x = x
        self._y = y

    @dispatch(object)
    def distance(self, p: Point2D) -> Callable[[float, float], float]:
        """Return euclidean distance between this point and `p`"""
        if not isinstance(p, Point2D):
            raise Exception('Object is not Point2D')
        return self.distance(p.x, p.y)
    
    @dispatch(Number, Number)
    def distance(self, px: Number, py: Number) -> float:
        """Return euclidean distance between these coordinates and `px` and `py`"""
        return ((self._x - px) ** 2 + (self._y - py) ** 2) ** 0.5
        
    def __eq__(self, p: Point2D) -> bool:
        """Check if two points have the same coordinates"""
        return self._x == p.x and self._y == p.y
    
    def __iter__(self) -> Iterable[Tuple[float]]:
        """Hacky implementation so `(x, y)` coordinate can be unpacked"""
        return iter((self._x, self._y))
    
    def __hash__(self) -> int:
        """Hash attrs to compare against other points"""
        return hash((self._x, self._y))

    def __repr__(self) -> str:
        """Debug representation of Point2D"""
        return f'({self._x}, {self._y})'
