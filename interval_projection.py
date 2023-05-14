from grid import BitpackedGrid
from node import Node

# hacky implementation; we infer float and int as Number for method overload
from numbers import Number

try:
    from multipledispatch import dispatch
except ImportError as e:
    raise Exception('Unable to import multipledispatch, make sure you have it installed')


class IntervalProjection:
    """Project intervals from one location on the grid onto another. There are two types of projections:
    - Flat projections 
    - Conical projections

    Attributes
    ----------
    left : float
        leftmost point of the projected interval
    right : float 
        rightmost point of the projected interval
    max_left : float
        furthest visible left point of the projection
    max_right : float
        furthest visible right point of the projection
    row : int
        Y axis denotating which row the interval is projected to
    valid : bool
        A projection is valid if it is possible to move the endpoints of the interval to the adjacent row (up or down) without intersecting an obstacle
    observable : bool
        A projection is observable if the projected left endpoint is strictly smaller than the projected right endpoint. NB: a projection can be valid but non-observable
    sterile_check_row : int
        Check if successors of a projection are sterile. Only used for conical projection
    check_vis_row : int
        Check visibility of row. Only used for conical projection
    type_iii_check_row : int
        Only used when generating type iii non-observable conical successors
    deadend : bool
        Node that can't be projected any further. Only used for flat projection
    intermediate : bool
        Node that doesn't hug any walls. Only used for flat projection

    """

    def __init__(self):
        self.valid = False

    @dispatch(Node, BitpackedGrid)
    def project(self, node: Node, grid: BitpackedGrid) -> None:
        """Wrapper for projecting node on the grid"""
        self.project(node.interval.left, node.interval.right, 
                     int(node.interval.row), int(node.root.x), int(node.root.y), grid)

    @dispatch(Number, Number, int, int, int, BitpackedGrid)
    def project(
        self,
        ileft: Number,
        iright: Number,
        irow: int,
        rootx: int,
        rooty: int,
        grid: BitpackedGrid
    ) -> None:
        """Project the interval associated with the node.
        The type of projection is determined by the Y coordinate of the root
        """
        self.observable = False
        self.valid = False
        
        if rooty == irow:
            self.project_flat(ileft, iright, rootx, rooty, grid)
        else:
            self.project_cone(ileft, iright, irow, rootx, rooty, grid)

    def project_cone(
        self,
        ileft: float,
        iright: float,
        irow: int,
        rootx: int,
        rooty: int,
        grid: BitpackedGrid
    ) -> None:
        """Cone projection based on node and interval row.
        Project down if node is below interval.
        If node is above interval, project up
        """
        if rooty < irow:
            self.check_vis_row = irow
            self.sterile_check_row = self.row = irow + 1
            self.type_iii_check_row = irow - 1
        else:
            assert rooty > irow, \
                f'Node Y axis must be greater than interval\'s row to project up. Got {rooty} and {irow}'
            
            self.sterile_check_row = irow - 2
            self.row = self.check_vis_row = irow - 1
            self.type_iii_check_row = irow

        self.valid = (grid.get_cell_is_traversable(int(ileft + grid.smallest_step_div2), self.check_vis_row) and 
                      grid.get_cell_is_traversable(int(iright - grid.smallest_step_div2), self.check_vis_row))

        if not self.valid:
            return

        # interpolate the endpoints of the new interval onto the next row.
        rise = abs(irow - rooty)
        lrun = rootx - ileft
        rrun = iright - rootx 	    	

        # clip the interval if visibility from the root is obstructed.
        # NB: +1 because we convert from tile coordinates to point coords
        self.max_left = grid.scan_cells_left(int(ileft), self.check_vis_row) + 1
        self.left = max(ileft - lrun/rise, self.max_left)   	

        self.max_right = grid.scan_cells_right(int(iright), self.check_vis_row)
        self.right = min(iright + rrun/rise, self.max_right)

        self.observable = self.left < self.right

        # sanity checking; sometimes an interval cannot be projected 
        # all the way to the next row without first hitting an obstacle.
        # in these cases we need to reposition the endpoints appropriately
        if self.left >= self.max_right:
            self.left = (self.right
                         if grid.get_cell_is_traversable(int(ileft - grid.smallest_step_div2), self.check_vis_row)
                         else self.max_left)

        if self.right <= self.max_left:
            self.right = (self.left
                          if grid.get_cell_is_traversable(int(iright), self.check_vis_row)
                          else self.max_right)

    def project_flat(
        self, 
        ileft: float,
        iright: float,
        rootx: int,
        rooty: int,
        grid: BitpackedGrid
    ) -> None:
        """Flat projection based on node X and interval's left/right.
        If node is on interval's left or is exactly left, project the interval
        to the right; left of projection is current interval's right, whereas
        right of projection will be the lattice before next obstacle or
        corner on the same row as the root.
        If node is on interval's right, do the opposite by scanning to the left
        """
        if rootx <= ileft:
            self.left = iright
            self.right = grid.scan_right(self.left, rooty)
            self.deadend = not (grid.get_cell_is_traversable(int(self.right), rooty) and 
                                grid.get_cell_is_traversable(int(self.right), rooty - 1))	
        else:
            self.right = ileft
            self.left = grid.scan_left(self.right, rooty)
            self.deadend = not (grid.get_cell_is_traversable(int(self.left - grid.smallest_step_div2), rooty) and 
                                grid.get_cell_is_traversable(int(self.left - grid.smallest_step_div2), rooty - 1))

        self.intermediate = (grid.get_cell_is_traversable(int(self.left), rooty) and 
                             grid.get_cell_is_traversable(int(self.left), rooty - 1))

        self.row = rooty
        self.valid = self.left != self.right

    @dispatch(Node, BitpackedGrid)
    def project_f2c(self, node: Node, grid: BitpackedGrid) -> None:
        """Wrapper for projecting flat node"""
        assert node.interval.row == node.root.y, \
            f'Node interval and root must be on the same row. Got {node.interval.row} and {node.root.y}'
        
        self.project_f2c(node.interval.left, node.interval.right, 
                         int(node.interval.row), int(node.root.x), int(node.root.y), grid)

    @dispatch(Number, Number, int, int, int, BitpackedGrid)
    def project_f2c(
        self,
        ileft: Number,
        iright: Number,
        irow: int,
        rootx: int,
        rooty: int,
        grid: BitpackedGrid
    ) -> None:
        """Project through a flat node and onto an adjacent grid row"""
        # look to the right for successors
        # recall that each point (x, y) corresponds to the
        # top-left corner of a tile at location (x, y)
        if rootx <= ileft:
            # can we make a valid turn? valid means 
            # (i) the path bends around a corner; 
            # (ii) we do not step through any obstacles or through 
            # double-corner points.
            can_step = grid.get_cell_is_traversable(int(iright), irow) and \
                       grid.get_cell_is_traversable(int(iright), irow - 1)

            if not can_step:
                self.valid = False
                self.observable = False
                return
            
            # if the tile below is free, we must be going up
            # else we round the corner and go down			
            if not grid.get_cell_is_traversable(int(iright - 1), irow):
                # going down
                self.sterile_check_row = self.row = irow + 1
                self.check_vis_row = irow
            else:
             	# going up
                self.row = self.check_vis_row = irow - 1
                self.sterile_check_row = irow - 2
            
            self.left = self.max_left = iright
            self.right = self.max_right = grid.scan_cells_right(int(self.left), self.check_vis_row)

        else:
            # look to the left for successors
            assert rootx >= iright, \
                f'Node X axis must be greater than interval\'s right to find left successors. Got {rootx} and {iright}'
            
            can_step = grid.get_cell_is_traversable(int(ileft - 1), irow) and \
                       grid.get_cell_is_traversable(int(ileft - 1), irow - 1)
            
            if not can_step:
                self.valid = False
                self.observable = False
                return
            
            # if the tiles below are free, we must be going up
            # else we round the corner and go down		
            if not grid.get_cell_is_traversable(int(ileft), irow):
             	# going down
                self.check_vis_row = irow
                self.sterile_check_row = self.row = irow + 1
            
            else:
             	# going up
                self.row = self.check_vis_row = irow - 1
                self.sterile_check_row = irow - 2	
            
            self.right = self.max_right = ileft
            self.left = self.max_left = grid.scan_cells_left(int(self.right - 1), self.check_vis_row) + 1

        self.valid = True
        self.observable = False