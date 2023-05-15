from grid import BitpackedGrid
from heuristic import Heuristic, EuclideanDistanceHeuristic
from node import Node
from interval_projection import IntervalProjection
from interval import Interval
from constants import EPSILON
from typing import List, Optional


class ExpansionPolicy:
    """Policy to expand nodes and generate their successors.
    A new search always starts on an off-grid node.

    Attributes
    ----------
    _grid : BitpackedGrid
        Grid graph represented as bitpacked
    _prune : bool = True
        Indicates whether or not pruning nodes without successors should be applied; defaults to True
    _successors : List[Node]
        List of successors of the node currently being expanded
    _heuristic : Heuristic
        Heuristic to evaluate movement costs from a given node to another
    _euclidean : Heuristic
        Heuristic to calculate distance between points
    _start : Node
        Start node when starting a new search
    _target : Node
        Target node to finish the search
    _tx : float
        Target node X axis coordinate
    _ty : float
        Target node Y axis coordinate
    _csucc : Node
        Next successor node of the node currently being expanded, if one exists
    _idx_succ : int
        Next successor helper
    _cnode : Node
        Current node that is being expanded

    """
	
    def __init__(
        self,
        map_file: str,
        prune: bool = True
    ):
        self._grid = BitpackedGrid(map_file=map_file)
        self._prune = prune
        self._successors = []
        self._heuristic = Heuristic()
        self._euclidean = EuclideanDistanceHeuristic()

    @property
    def heuristic(self) -> Heuristic:
        """Get heuristic for evaluating costs"""
        return self._heuristic
    
    @property
    def grid(self) -> BitpackedGrid:
        """Get current searching grid"""
        return self._grid

    def expand(self, vertex: Node) -> None:
        """Expand all neighbors of a node"""
        self._cnode = vertex
        self._csucc = None
        self._idx_succ = 0
        self._successors.clear()

        if vertex == self._start:
            self.generate_start_successors(self._cnode, self._successors)
        else:
            self.generate_successors(self._cnode, self._successors)

    def next(self) -> Optional[Node]:
        """Get next neighbor, if one exists, of the node being expanded"""
        self._csucc = None
        if self._idx_succ < len(self._successors):
            self._csucc = self._successors[self._idx_succ]
            self._idx_succ += 1
        return self._csucc

    def has_next(self) -> bool:
        """Check whether or not the list of successors has been exhausted"""
        return self._idx_succ < len(self._successors)

    def step_cost(self) -> float:
        """Get Euclidean distance between the node that's being expanded and next neighbor"""
        assert self._cnode is not None and self._csucc is not None, \
            f'Node under expansion and/or next successor node are/is None. Got: {self._cnode} and {self._csucc}'
        
        return self._euclidean.h(self._cnode.root.x, self._cnode.root.y, 
                                 self._csucc.root.x, self._csucc.root.y)

    def validate_instance(self, start: Node, target: Node) -> bool:
        """Validate start and target nodes when starting a new search instance"""
        self._start = start
        self._target = target
        self._tx = self._target.root.x
        self._ty = self._target.root.y

        return (self._grid.get_cell_is_traversable(int(start.root.x), int(start.root.y)) and 
                self._grid.get_cell_is_traversable(int(target.root.x), int(target.root.y)))

    def generate_successors(self, node: Node, retval: List[Node]) -> None:
        """Generate flat and cone successors of a given node based on its Y coordinate.
        Project node's interval onto the next row
        """
        projection = IntervalProjection()

        if node.root.y == node.interval.row:
            projection.project(node, self._grid)
            self.flat_node_obs(node, retval, projection)    	
            
            projection.project_f2c(node, self._grid)
            self.flat_node_nobs(node, retval, projection)
        else:
            projection.project(node, self._grid)
            self.cone_node_obs(node, retval, projection)
            self.cone_node_nobs(node, retval, projection)

    def generate_start_successors(self, node: Node, retval: List[Node]) -> None:
        """Generate first successors of an off-grid node"""
        assert (node.interval.left == node.interval.right and
                node.interval.left == node.root.x and
                node.interval.row == node.root.y), \
                    f'Off-grid node\'s interval must contain only that node. Expected row == y; left == right == x'

        # certain successors will be ignored if the start is a double-corner
        start_dc = self._grid.get_point_is_double_corner(int(node.root.x), int(node.root.y))

        # certain start locations are ambiguous; we don't try to solve these
        if start_dc and not self._grid.get_cell_is_traversable(int(node.root.x), int(node.root.y)):
            return

        rootx = int(node.root.x)
        rooty = int(node.root.y)
            
        # generate flat observable successors left of the start point
        # NB: hacky implementation; we use a fake root for the projection
        projection = IntervalProjection()
        if not start_dc:
            projection.project(rootx, rootx, rooty,
                               rootx + 1, rooty, self._grid)
            self.generate_observable_flat__(projection, rootx, rooty, node, retval)

        # generate flat observable successors right of the start point
        # NB: hacky implementation; we use a fake root for the projection
        projection.project(rootx, rootx, rooty,
                           rootx - 1, rooty, self._grid)
        self.generate_observable_flat__(projection, rootx, rooty, node, retval)

        # generate conical observable successors below the start point 
        max_left = self._grid.scan_cells_left(rootx, rooty) + 1
        max_right = self._grid.scan_cells_right(rootx, rooty)
        if max_left != rootx and not start_dc:
            self.split_interval_make_successors(max_left, rootx, rooty + 1,
                                                rootx, rooty, rooty + 1, node, retval)
 	
        if max_right != rootx:
            self.split_interval_make_successors(rootx, max_right, rooty + 1,
                                                rootx, rooty, rooty + 1, node, retval)

        # generate conical observable successors above the start point
        max_left = self._grid.scan_cells_left(rootx - 1, rooty - 1) + 1
        max_right = self._grid.scan_cells_right(rootx, rooty - 1)
        if max_left != rootx and not start_dc:
            self.split_interval_make_successors(max_left, rootx, rooty - 1,
                                                rootx, rooty, rooty - 2, node, retval) 	

        if max_right != rootx:
            self.split_interval_make_successors(rootx, max_right, rooty - 1,
                                                rootx, rooty, rooty - 2, node, retval)

    def split_interval_make_successors(
        self,
        max_left: float,
        max_right: float,
        irow: int,
        rootx: int,
        rooty: int,
        sterile_check_row: int,
        parent: Node,
        retval: List[Node]
    ) -> None:
        """After projecting the interval, split at each internal
        corner to generate new observable sucessors
        """
        if max_left == max_right:
            return

        succ_left = max_right
        num_successors = len(retval)
        target_node = self.contains_target(max_left, max_right, irow)
        forced_succ = not self._prune or target_node

        successor = None
        while True:
            succ_right = succ_left
            succ_left = self._grid.scan_left(succ_right, irow)
            if forced_succ or not self.sterile(succ_left, succ_right, sterile_check_row):
                successor = Node.from_points(
                    Interval(succ_left, succ_right, irow), rootx, rooty, parent
                )
                
                successor.interval.left = max_left if succ_left < max_left else succ_left
                retval.append(successor)

            if not (succ_left != succ_right and succ_left > max_left):
                break

        if (not forced_succ and len(retval) == (num_successors + 1) and
            self.intermediate(successor.interval, rootx, rooty)):
            del retval[-1]

            proj = IntervalProjection()
            proj.project_cone(successor.interval.left, successor.interval.right, 
                              successor.interval.row, rootx, rooty, self._grid)
            if proj.valid and proj.observable:
                self.split_interval_make_successors(proj.left, proj.right, proj.row,
                                                    rootx, rooty, proj.sterile_check_row, parent, retval)

    def sterile(self, left: float, right: float, row: int) -> bool:
        """Check if non-discrete left and right points are adjacent to obstacle cells on row"""
        r = int(right - EPSILON)
        l = int(left + EPSILON)
        return not ((self._grid.get_cell_is_traversable(l, row) and
                     self._grid.get_cell_is_traversable(r, row)))

    def intermediate(self, interval: Interval, rootx: int, rooty: int) -> bool:
        """Return True if the interval has no adjacent successors.
        Intermediate nodes have intervals that are not taut; i.e.
        their endpoints are not adjacent to any location that cannot be
        directly observed from the root
        """
        left = interval.left
        right = interval.right
        row = interval.row

        tmp_left = int(left)
        tmp_right = int(right)
        
        discrete_left = interval.discrete_left
        discrete_right = interval.discrete_right

        rightroot = ((tmp_right - rootx) >> 31) == 1
        leftroot = ((rootx - tmp_left) >> 31) == 1
        
        right_turning_point = False
        left_turning_point = False
        
        if rooty < row:
            left_turning_point = discrete_left and \
                                 self._grid.get_point_is_corner(tmp_left, row) and \
                                 (not self._grid.get_cell_is_traversable(tmp_left - 1, row - 1) or leftroot)

            right_turning_point = discrete_right and \
                                  self._grid.get_point_is_corner(tmp_right, row) and \
                                  (not self._grid.get_cell_is_traversable(tmp_right, row - 1) or rightroot)				       	
        else:
            left_turning_point = discrete_left and \
                                 self._grid.get_point_is_corner(tmp_left, row) and \
                                 (not self._grid.get_cell_is_traversable(tmp_left - 1, row) or leftroot)

            right_turning_point = discrete_right and \
                                  self._grid.get_point_is_corner(tmp_right, row) and \
                                  (not self._grid.get_cell_is_traversable(tmp_right, row) or rightroot)
                
        return not ((discrete_left and left_turning_point) or (discrete_right and right_turning_point))

    def contains_target(self, left: float, right: float, row: int) -> bool:
        """Check if an given interval contains the target node"""
        return row == self._ty and self._tx >= (left - EPSILON) and self._tx <= (right + EPSILON)

    def cone_node_obs(self, node: Node, retval: List[Node], projection: IntervalProjection) -> None:
        """There is an inductive argument here: if the move is not valid
        the node should have been pruned. check this is always true
        """
        assert node.root.y != node.interval.row, \
            f'Node interval and root must not be on the same row. Got {node.root.y} and {node.interval.row}'

        root = node.root
        self.generate_observable_cone__(projection, int(root.x), int(root.y), node, retval)

    def generate_observable_cone__(
        self,
        projection: IntervalProjection,
        rootx: int,
        rooty: int,
        parent: Node,
        retval: List[Node]
    ) -> None:
        """Generate observable cone successors by splitting the interval
        projection at each internal corner point
        """
        if not (projection.valid and projection.observable):
            return
        self.split_interval_make_successors(projection.left, projection.right,
                                            int(projection.row), rootx, rooty,
                                            projection.sterile_check_row, parent, retval)

    def cone_node_nobs(self, node: Node, retval: List[Node], projection: IntervalProjection) -> None:
        """There are two kinds of non-observable successors:
        (i) conical successors that are adjacent to an observable projection
        (ii) flat successors that are adjacent to the current interval
        (iii) conical successors that are not adjacent to any observable
        projection or the current interval (i.e the angle from the root
        to the interval is too low to observe any point from the next row)
        """
        if not projection.valid:
            return

        ileft = node.interval.left
        iright = node.interval.right
        irow = int(node.interval.row)

        # non-observable successor type (iii)
        if not projection.observable:
            if (node.root.x > iright and node.interval.discrete_right and 
                self._grid.get_point_is_corner(int(iright), irow)):
                
                self.split_interval_make_successors(projection.max_left, iright, projection.row,
                                                    int(iright), irow, projection.sterile_check_row,
                                                    node, retval)

            elif (node.root.x < ileft and node.interval.discrete_left and 
                  self._grid.get_point_is_corner(int(ileft), irow)):
                self.split_interval_make_successors(ileft, projection.max_right, projection.row,
                                                    int(ileft), irow, projection.sterile_check_row,
                                                    node, retval)

            if (node.interval.discrete_left and 
                not self._grid.get_cell_is_traversable(int(ileft - 1), projection.type_iii_check_row) and 
                self._grid.get_cell_is_traversable(int(ileft - 1), projection.check_vis_row)):
                # non-observable successors to the left of the current interval
                projection.project_flat(ileft - self._grid.smallest_step_div2, ileft, 
                                        int(ileft), int(irow), self._grid)
                
                self.generate_observable_flat__(projection, int(ileft), irow, node, retval)  	

            if (node.interval.discrete_right and 
                not self._grid.get_cell_is_traversable(int(iright), projection.type_iii_check_row) and 
                self._grid.get_cell_is_traversable(int(iright), projection.check_vis_row)):
                # non-observable successors to the right of the current interval
                projection.project_flat(iright, iright + self._grid.smallest_step_div2, 
                                        int(iright), int(irow), self._grid) # NB: dummy root
                
                self.generate_observable_flat__(projection, int(iright), irow, node, retval) 	   		
            return

        # non-observable successors type (i) and (ii)
        flatprj = IntervalProjection() 	
        corner_row = irow - ((int(node.root.y) - irow) >> 31)

        # non-observable successors to the left of the current interval
        if node.interval.discrete_left and self._grid.get_point_is_corner(int(ileft), irow):
            # flat successors from the interval row
            if not self._grid.get_cell_is_traversable(int(ileft - 1), corner_row):
                flatprj.project(ileft - EPSILON, iright, 
                                int(irow), int(ileft), int(irow), self._grid)
                
                self.generate_observable_flat__(flatprj, int(ileft), irow, node, retval) 	    				

            # conical successors from the projected row
            self.split_interval_make_successors(projection.max_left, projection.left, projection.row, 
                                                int(ileft), irow, projection.sterile_check_row,
                                                node, retval)

        # non-observable successors to the right of the current interval
        if node.interval.discrete_right and self._grid.get_point_is_corner(int(iright), irow):
            # flat successors from the interval row
            if not self._grid.get_cell_is_traversable(int(iright), corner_row):			
                flatprj.project(ileft, iright + EPSILON, 
                                int(irow), int(ileft), int(irow), self._grid)

                self.generate_observable_flat__(flatprj, int(iright), irow, node, retval)
            
            # conical successors from the projected row
            self.split_interval_make_successors(projection.right, projection.max_right, projection.row, 
                                                int(iright), irow, projection.sterile_check_row, node, retval)

    def flat_node_obs(self, node: Node, retval: List[Node], projection: IntervalProjection) -> None:
        root = node.root
        self.generate_observable_flat__(projection, int(root.x), int(root.y), node, retval)

    def generate_observable_flat__(
        self,
        projection: IntervalProjection,
        rootx: int,
        rooty: int,
        parent: Node,
        retval: List[Node]
    ) -> None:
        """Generate observable flat successors by splitting the interval
        projection at each internal corner point
        """
        assert projection.row == rooty, \
            f'Projection and root must be on the same row. Got {projection.row} and {rooty}'
        
        if not projection.valid:
            return

        goal_interval = self.contains_target(projection.left, projection.right, projection.row)
        if projection.intermediate and self._prune and not goal_interval:
            # ignore intermediate nodes and project further along the row
            projection.project(projection.left, projection.right, projection.row,
                               rootx, rooty, self._grid)
            
            # check if the projection contains the goal
            goal_interval = self.contains_target(projection.left, projection.right, projection.row)

        if not projection.deadend or not self._prune or goal_interval:
            retval.append(
                Node.from_points(
                    Interval(projection.left, projection.right, projection.row), 
                    rootx,
                    rooty,
                    parent
                )
            )

    def flat_node_nobs(self, node: Node, retval: List[Node], projection: IntervalProjection) -> None:
        """Generate non-observable flat successors"""
        if not projection.valid: 
            return
        
        # conical successors from the projected row
        new_rooty = node.interval.row
        if node.root.x <= node.interval.left:
            new_rootx = int(node.interval.right)
        else:
            new_rootx = int(node.interval.left)

        self.split_interval_make_successors(projection.left, projection.right, projection.row,
                                            new_rootx, new_rooty, projection.sterile_check_row,
                                            node, retval)

    def hash(self, n: Node) -> int:
        """Hash node based on map attrs"""
        return int(n.root.y) * self._grid.map_width + int(n.root.x)
