from __future__ import annotations

from constants import PADDING_, BITS_PER_WORD, LOG2_BITS_PER_WORD, INDEX_MASK
from fileinput import input

try:
    from numpy import zeros, ndarray, uint
except ImportError as e:
    raise Exception('Unable to import NumPy, make sure you have it installed')


class BitpackedGrid:
    """A grid consists of width x height square cells.
    A bitpacked representation is used to improve time and space efficiency.
    This is merely a copy of the original bitpacked grid used by Daniel Harabor.

    Attributes
    ----------
    _map_height_original : int
        Original dimension of the grid
    _map_width_original : int
        Original dimension of the grid
    _map_height : int
        Padded dimension of the grid, one row added before first row and one after last row
    _map_width : int
        Padded dimension of the grid
    _map_size : int
        Map size in words based on padded dimensions
    _map_width_in_words : int
        Map width in words for convenience
    _map_cells : ndarray[int]
        Flat array representing map grid cells
    _visible : ndarray[int]
        Array indicating which cell grids are visible and which are not
    _corner : ndarray[int]
        Array indicating which cell grids are corners and which are not
    _double_corner : ndarray[int]
        Array indicating which cell grids are double corners and which are not
    smallest_step : float
        Smallest distance between two adjacent points
    smallest_step_div2 : float
        Ditto; for convenience

    """

    def __init__(self, **kwargs):
        map_file = kwargs.get('map_file')
        width = kwargs.get('width', 0)
        height = kwargs.get('height', 0)

        if map_file:
            self.load(map_file)
        elif width > 0 and height > 0:
            self.init(width, height)
        else:
            raise Exception('Either map or graph file must be provided or width and height must be greater than 0')

    def init(self, width: int, height: int) -> None:
        """Initialize map attributes based on grid dimensions"""
        self._map_height_original = height
        self._map_width_original = width
        self._map_width_in_words = ((width >> LOG2_BITS_PER_WORD) + 1)
        self._map_width = self._map_width_in_words << LOG2_BITS_PER_WORD
        self._map_height = height + 2 * PADDING_

        self._map_size = ((self._map_height * self._map_width) >> LOG2_BITS_PER_WORD)
        self._map_cells = zeros(self._map_size, dtype=uint)
        self._visible = zeros(self._map_size, dtype=uint)
        self._corner = zeros(self._map_size, dtype=uint)
        self._double_corner = zeros(self._map_size, dtype=uint)

        self.smallest_step = min(1 / float(self._map_width), 1 / float(self._map_height))
        self.smallest_step_div2 = self.smallest_step / 2.0

    @property
    def map_width(self) -> int:
        """Get padded dimensions of the grid"""
        return self._map_width
    
    @property
    def map_height(self) -> int:
        """Get padded dimensions of the grid"""
        return self._map_height
    
    @property
    def num_cells(self) -> int:
        """Get number of cells of the grid"""
        return self._map_height * self._map_width
    
    @property
    def map_height_original(self) -> int:
        """Get original map height"""
        return self._map_height_original
    
    @property
    def map_width_original(self) -> int:
        """Get original map width"""
        return self._map_width_original

    def get_point_is_visible(self, x: int, y: int) -> bool:
        """Return True/False indicating the point (x, y)
        has at least one adjacent unblocked cell
        """
        return self.get_bit_value(x, y, self._visible)

    def get_point_is_corner(self, x: int, y: int) -> bool:
        """Return True/False indicating the point (x, y)
        has three adjacent unblocked cells and one blocked
        or exactly two diagonal adjacent blocked cells
        """
        return self.get_bit_value(x, y, self._corner)

    def get_point_is_double_corner(self, x: int, y: int) -> bool:
        """Return True/False indicating the point (x, y)
        has exactly two diagonal adjacent blocked cells
        """
        return self.get_bit_value(x, y, self._double_corner)

    def get_cell_is_traversable(self, cx: int, cy: int) -> bool:
        """Return True if cell is unblocked or False otherwise"""
        return self.get_bit_value(cx, cy, self._map_cells)

    def set_point_is_visible(self, x: int, y: int, value: bool) -> None:
        """Set point as visible (True) or not (False)"""
        self.set_bit_value(x, y, value, self._visible)

    def set_point_is_corner(self, x: int, y: int, value: bool) -> None:
        """Set point as corner (True) or not (False)"""
        self.set_bit_value(x, y, value, self._corner)

    def set_point_is_double_corner(self, x: int, y: int, value: bool) -> None:
        """Set point as double corner (True) or not (False)"""
        self.set_bit_value(x, y, value, self._double_corner)

    def get_point_is_discrete(self, x: float, y: int) -> bool:
        """Return True indicating a given point is discrete or False otherwise"""
        return abs(int(x + self.smallest_step_div2) - x) < self.smallest_step

    def set_cell_is_traversable(self, cx: int, cy: int, value: bool) -> None:
        """Set cell as unblocked or blocked along with,
        for each of the four points (NW, NE, SW, SE) of the cell,
        update their corresponding adjacent points as visible, corner
        and/or double corner
        """
        self.set_bit_value(cx, cy, value, self._map_cells)
        self.update_point(cx, cy)
        self.update_point(cx + 1, cy)
        self.update_point(cx, cy + 1)
        self.update_point(cx + 1, cy + 1)		

    def update_point(self, px: int, py: int) -> None:
        """Set point as visible, corner or double corner
        by analyzing its surrounding four adjacent cells.
        Each cell is found by its north-west discrete point.
        A point can be:
        - visible: has at least one adjacent unblocked cell
        - corner: has three adjacent unblocked cells and one blocked
        or exactly two diagonal adjacent blocked cells
        - double corner: has exactly two diagonal adjacent blocked cells
        """
        cell_nw = self.get_cell_is_traversable(px - 1, py - 1)
        cell_ne = self.get_cell_is_traversable(px, py - 1)
        cell_sw = self.get_cell_is_traversable(px - 1, py)
        cell_se = self.get_cell_is_traversable(px, py)

        corner = ((not cell_nw or not cell_se) and cell_sw and cell_ne) or \
                 ((not cell_ne or not cell_sw) and cell_nw and cell_se)

        double_corner = ((not cell_nw and not cell_se) and cell_sw and cell_ne) ^ \
                        ((not cell_sw and not cell_ne) and cell_nw and cell_se)

        visible = cell_nw or cell_ne or cell_sw or cell_se

        self.set_point_is_corner(px, py, corner)
        self.set_point_is_double_corner(px, py, double_corner)
        self.set_point_is_visible(px, py, visible)

    def set_bit_value(
        self,
        x: int,
        y: int,
        value: bool,
        elts: ndarray[uint]
    ) -> None:
        """Set cell value based on corresponding map word index"""
        map_id = self.get_map_id(x, y)
        word_index = map_id >> LOG2_BITS_PER_WORD
        mask = (1 << ((map_id & INDEX_MASK)))
        tmp = elts[word_index]
        elts[word_index] = (tmp | mask) if value else (tmp & ~mask)

    def get_bit_value(
        self,
        x: int,
        y: int,
        elts: ndarray[uint]
    ) -> bool:
        """Get cell value based on corresponding map word index"""
        map_id = self.get_map_id(x, y)
        word_index = map_id >> LOG2_BITS_PER_WORD		
        mask = 1 << ((map_id & INDEX_MASK))
        return (elts[word_index] & mask) != 0

    def get_map_id(self, x: int, y: int) -> int:
        """Get cell index on padded dimensions map"""
        return (y + PADDING_)* self._map_width + (x + PADDING_)

    def scan_cells_right(self, x: int, y: int) -> int:
        """Scan cells to the right starting at `p` (x, y)
        and heading in the negative x direction.
        Return `x` of the first obstacle reached by traveling
        right from `p`
        """
        tile_id = self.get_map_id(x, y)
        t_index = tile_id >> LOG2_BITS_PER_WORD

        # ignore obstacles in bit positions < (i.e. to the left of) the starting cell
        # (NB: big endian order means the leftmost cell is in the lowest bit)
        obstacles = ~self._map_cells[t_index]
        start_bit_index = tile_id & INDEX_MASK
        mask = ~((1 << start_bit_index) - 1)
        obstacles &= mask

        stop_pos = 0
        start_index = t_index
        while True:
            if obstacles != 0:
                stop_pos = BitpackedGrid.get_number_trailing_zeros(obstacles)
                break

            t_index += 1
            obstacles = ~self._map_cells[t_index]

        retval = ((t_index - start_index) * BITS_PER_WORD)
        retval += (stop_pos - start_bit_index)
        return x + retval

    def scan_cells_left(self, x: int, y: int) -> int:
        """Scan cells to the left starting at p (x, y)
        and heading in the negative x direction.
        Return `x` of the first obstacle reached by traveling
        left from `p`
        """         	
        tile_id = self.get_map_id(x, y)
        t_index = tile_id >> LOG2_BITS_PER_WORD

        # scan adjacent cells from the current row and the row above
        obstacles = ~self._map_cells[t_index]

        # ignore cells in bit positions > (i.e. to the right of) the starting cell
        # (NB: big endian order means the rightmost cell is in the highest bit)
        start_bit_index = tile_id & INDEX_MASK
        opposite_index = (BITS_PER_WORD - (start_bit_index + 1))
        mask = (1 << start_bit_index)
        mask = (mask | (mask - 1))
        obstacles &= mask

        stop_pos = 0
        start_index = t_index
        while True:
            if obstacles != 0:
                stop_pos = BitpackedGrid.get_number_leading_zeros(obstacles)
                break

            t_index -= 1
            obstacles = ~self._map_cells[t_index]

        retval = ((start_index - t_index) * BITS_PER_WORD)
        retval += (stop_pos - opposite_index)
        return x - retval
    
    def scan_right(self, x: float, row: int) -> int:
        """Scan right along the lattice from (x, row)
        Return next discrete point that is a corner or which
        is the last traversable point before an obstacle
        """
        left_of_x = int(x + self.smallest_step_div2)
        tile_id = self.get_map_id(left_of_x, row)
        t_index = tile_id >> LOG2_BITS_PER_WORD
        ta_index = t_index - self._map_width_in_words

        # scan adjacent cells from the current row and the row above
        cells = self._map_cells[t_index]
        cells_above = self._map_cells[ta_index]

        obstacles = ~cells & ~cells_above
        corners = self._corner[t_index]

        # ignore corners in bit positions <= (i.e. to the left of) the starting cell
        # (NB: big endian order means the leftmost cell is in the lowest bit)
        start_bit_index = tile_id & INDEX_MASK
        mask = (1 << start_bit_index)
        corners &= ~(mask | (mask-1))
        # ignore obstacles in bit positions < (i.e. strictly left of) the starting cell    	
        # Because we scan cells (and not corners) we cannot ignore the current location. 
        # To do so might result in intervals that pass through obstacles 
        # (e.g. current location is a double corner)
        obstacles &= ~(mask-1)

        stop_pos = 0
        start_index = t_index
        while True:
            value = corners | obstacles
            if value != 0:
                # Each point (x, y) is associated with the top-left 
                # corner of tile (x, y). When traveling right (cf. left)
                # we need to stop exactly at the position of the first 
                # (corner or obstacle) bit. 
                stop_pos = BitpackedGrid.get_number_trailing_zeros(value)
                break

            t_index += 1
            ta_index += 1
            corners = self._corner[t_index]
            obstacles = ~self._map_cells[t_index] & ~self._map_cells[ta_index]

        retval = left_of_x + ((t_index - start_index) * BITS_PER_WORD + stop_pos)
        retval -= start_bit_index
        return retval

    def scan_left(self, x: float, row: int) -> int:
        """Scan left along the lattice from (x, row)
        Return next discrete point that is a corner or which
        is the last traversable point before an obstacle
        """
        # early return if the next discrete point 
        # left of x is a corner
        left_of_x = int(x)
        if (x - left_of_x) >= self.smallest_step and self.get_point_is_corner(left_of_x, row):
            return left_of_x

        tile_id = self.get_map_id(left_of_x, row)
        t_index = tile_id >> LOG2_BITS_PER_WORD
        ta_index = t_index - self._map_width_in_words

        # scan adjacent cells from the current row and the row above
        cells = self._map_cells[t_index]
        cells_above = self._map_cells[ta_index]

        obstacles = ~cells & ~cells_above
        corners = self._corner[t_index]

        # ignore cells in bit positions >= (i.e. to the right of) the starting cell
        # (NB: big endian order means the rightmost cell is in the highest bit)
        # Because we scan cells (and not just corners) we can safely ignore
        # the current position. The traversability of its associated cell has
        # no impact on deciding whether we can travel left, away from the cell.
        start_bit_index = tile_id & INDEX_MASK
        mask = (1 << start_bit_index) - 1
        corners &= mask
        obstacles &= mask

        stop_pos = 0
        start_index = t_index
        while True:
            value = corners | obstacles
            if value != 0:
                # Each point (x, y) is associated with the top-left 
                # corner of tile (x, y). When counting zeroes to figure
                # out how far we can travel we end up stopping one 
                # position before the first set bit. This approach prevents
                # us from traveling through an obstacle (we stop right before)
                # but in in the case of corner tiles, we need to stop exactly 
                # at the position of the set bit. Hence, +1 below.
                stop_pos = min(
                    BitpackedGrid.get_number_leading_zeros(corners) + 1, 
                    BitpackedGrid.get_number_leading_zeros(obstacles)
                )
                break

            t_index -= 1
            ta_index -= 1
            corners = self._corner[t_index]
            obstacles = ~self._map_cells[t_index] & ~self._map_cells[ta_index]

        retval = left_of_x - ((start_index - t_index) * BITS_PER_WORD + stop_pos)
        retval += (BITS_PER_WORD - start_bit_index)
        return retval

    def load(self, map_file: str) -> None:
        """Load map file and initialize traversable and non-traversable cells"""
        print(f'Loading map: {map_file}')
        
        try:
            with input(map_file, mode='r') as file:
                map_type, *dims, map_token = [next(file).strip() for _ in range(4)]

                if map_token != 'map':
                    raise Exception(f'Could not load map; unrecognized format: {map_token}')
                if map_token == 'octile':
                    raise Exception(f'Could not load map; only octile types are supported; got: {map_type}')
                
                dims = dict([dim.split() for dim in dims])
                try:
                    dims['width'] = int(dims['width'])
                    dims['height'] = int(dims['height'])
                except Exception as e:
                    raise Exception(f'Could not load map; invalid height/width: {e}')
                
                self.init(**dims)
                for y in range(dims['height']):
                    map_line = next(file)
                    for x in range(dims['width']):
                        self.set_cell_is_traversable(x, y, map_line[x] == '.')
            print('Map loaded')
        except Exception as e:
            raise Exception(f'Unexpected exception while loading map file: {e}')
        
    def get_num_traversable_cells(self) -> int:
        """Return the number of map cells that are not blocked.
        Although this value does not represent all possible paths
        since there may be problems without solution
        e.g. cells surrounded by obstacles
        """
        valid = 0
        for x in range(self._map_width_original):
            for y in range(self._map_height_original):
                if self.get_cell_is_traversable(x, y):
                    valid += 1
        return valid

    @staticmethod
    def get_number_trailing_zeros(value: int) -> int:
        """Return the number of zero bits following righmost one-bit
        in the binary representation.
        If value is zero a.k.a. no one-bits, return 32
        """
        if value == 0:
            return 32
        return len(s := bin(value)) - len(s.rstrip('0'))

    @staticmethod
    def get_number_leading_zeros(value: int) -> int:
        """Return the number of zero bits following leftmost one-bit
        in the 32 bits representation.
        If value is zero a.k.a. no one-bits, return 32
        """
        if value == 0:
            return 32
        return len(s := f'{value:032b}') - len(s.lstrip('0'))
