from grid import BitpackedGrid
from heuristic import HackyHeuristic
from point import Point2D
from constants import ROOT_TWO
from typing import Optional


class BitpackedGridExpansionPolicy:
    def __init__(self, file_name: str):
        self._grid = BitpackedGrid(map_file=file_name)
        self._neis = [None] * 8
        self._step_costs = [None] * 8
        self._h = HackyHeuristic()

        self._pool = [None] * self._grid.num_cells
        for y in range(self._grid.map_height):
            for x in range(self._grid.map_width):
                self._pool[self.compute_id(x, y)] = Point2D(x, y)

    @property
    def heuristic(self) -> HackyHeuristic:
        """Get heuristic used for this policy instance"""
        return self._h

    def validate_instance(self, start: Point2D, target: Point2D) -> bool:
        """Validate start and target points when starting a new search instance"""
        self._s = start
        self._t = target
        self._h.target = target
        return (self._grid.get_cell_is_traversable(*self._s) and 
                self._grid.get_cell_is_traversable(*self._t))

    def expand_start_is_valid_double_corner(self, v: Point2D) -> None:
        se = self._grid.get_cell_is_traversable(v.x, v.y)
        sw = self._grid.get_cell_is_traversable(v.x - 1, v.y)
        nw = self._grid.get_cell_is_traversable(v.x - 1, v.y - 1)
        ne = self._grid.get_cell_is_traversable(v.x, v.y - 1)

        # add diagonals
        if se:
            self._step_costs[self._num_neis] = ROOT_TWO
            self._neis[self._num_neis] = self._pool[self.compute_id(v.x + 1, v.y + 1)]
            self._num_neis += 1

        # add cardinals  (east and south only)
        if ne or se:
            self._step_costs[self._num_neis] = 1.0
            self._neis[self._num_neis] = self._pool[self.compute_id(v.x + 1, v.y)]
            self._num_neis += 1

        if se or sw:
            self._step_costs[self._num_neis] = 1.0
            self._neis[self._num_neis] = self._pool[self.compute_id(v.x, v.y + 1)]
            self._num_neis += 1

    def expand(self, v: Point2D) -> None:
        """Expand all neighbors of a point"""
        self._num_neis = 0
        self._index = 0
        
        if self._grid.get_point_is_double_corner(v.x, v.y):
            if v.x == self._s.x and v.y == self._s.y:
                self.expand_start_is_valid_double_corner(v)
            return

        se = self._grid.get_cell_is_traversable(v.x, v.y)
        sw = self._grid.get_cell_is_traversable(v.x - 1, v.y)
        nw = self._grid.get_cell_is_traversable(v.x - 1, v.y - 1)
        ne = self._grid.get_cell_is_traversable(v.x, v.y - 1)

        # add diagonals
        if ne:
            self._step_costs[self._num_neis] = ROOT_TWO
            self._neis[self._num_neis] = self._pool[self.compute_id(v.x + 1, v.y - 1)]
            self._num_neis += 1

        if se:
            self._step_costs[self._num_neis] = ROOT_TWO
            self._neis[self._num_neis] = self._pool[self.compute_id(v.x + 1, v.y + 1)]
            self._num_neis += 1

        if nw:
            self._step_costs[self._num_neis] = ROOT_TWO
            self._neis[self._num_neis] = self._pool[self.compute_id(v.x - 1, v.y - 1)]
            self._num_neis += 1

        if sw:
            self._step_costs[self._num_neis] = ROOT_TWO
            self._neis[self._num_neis] = self._pool[self.compute_id(v.x - 1, v.y + 1)]
            self._num_neis += 1

        # add cardinals
        if ne or se:
            self._step_costs[self._num_neis] = 1.0
            self._neis[self._num_neis] = self._pool[self.compute_id(v.x + 1, v.y)]
            self._num_neis += 1

        if nw or sw:
            self._step_costs[self._num_neis] = 1.0
            self._neis[self._num_neis] = self._pool[self.compute_id(v.x - 1, v.y)]
            self._num_neis += 1

        if ne or nw:
            self._step_costs[self._num_neis] = 1.0
            self._neis[self._num_neis] = self._pool[self.compute_id(v.x, v.y - 1)]
            self._num_neis += 1

        if se or sw:
            self._step_costs[self._num_neis] = 1.0
            self._neis[self._num_neis] = self._pool[self.compute_id(v.x, v.y + 1)]
            self._num_neis += 1

    def next(self) -> Optional[Point2D]:
        """Get next neighbor, if one exists, of the point being expanded"""
        if self._index < self._num_neis:
            self._stepcost = self._step_costs[self._index]
            n = self._neis[self._index]
            self._index += 1
            return n
        self._stepcost = 0
        return None

    def has_next(self) -> bool:
        """Check whether or not there are still neighbors to visit"""
        return self._index < self._num_neis

    def step_cost(self) -> float:
        return self._stepcost

    def get_grid_vertex(self, x: int, y: int) -> Optional[Point2D]:
        if x < self._grid.map_width and y < self._grid.map_height:
            return self._pool[self.compute_id(x, y)]
        return None

    def compute_id(self, x: int, y: int) -> int:
        return y * self._grid.map_width + x

    def hash(self, v: Point2D) -> int:
        return self.compute_id(v.x, v.y)
