from grid import BitpackedGrid
from heuristic import EuclideanDistanceHeuristic, Heuristic
from node import Node
from interval import Interval
from interval_projection import IntervalProjection
from constants import EPSILON
from typing import List

try:
    from sympy import Point2D
except ImportError as e:
    raise Exception('Unable to import SymPy, make sure you have it installed')


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
        file_name: str,
        prune: bool = True
    ):
        self._grid = BitpackedGrid(map_file=file_name)
        self._prune = prune
        self._successors = []
        self._heuristic = Heuristic()

    @property
    def heuristic(self) -> Heuristic:
        """Get heuristic for evaluating costs"""
        return self._heuristic

    @property
    def grid(self) -> BitpackedGrid:
        """Get current searching grid"""
        return self._grid
    
    def validate_instance(self, start: Node, target: Node) -> bool:
        """Validate start and target nodes when starting a new search instance"""
        self._start = start
        self._target = target
        self._tx, self._ty = self._target.root

        return self._grid.get_cell_is_traversable(int(start.root.x), int(start.root.y)) and \
               self._grid.get_cell_is_traversable(int(target.root.x), int(target.root.y))

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

    def next(self) -> Node:
        """Get next neighbor, if one exists, of the node being expanded"""
        csucc = None
        if self.has_next():
            csucc = self._successors[self._idx_succ]
            self._idx_succ += 1
        return csucc

    def has_next(self) -> bool:
        """Check whether or not the list of successors has been exhausted"""
        return self._idx_succ < len(self._successors)

    def step_cost(self) -> float:
        """Get Euclidean distance between the node that's being expanded and next neighbor"""
        assert self._cnode is not None and self._csucc is not None, \
            f'Node under expansion and/or next successor node are/is None. Got: {self._cnode} and {self._csucc}'

        return EuclideanDistanceHeuristic.distance(self._cnode.root.x, self._cnode.root.y, 
                                                   self._csucc.root.x, self._csucc.root.y)

    def generate_successors(self, node: Node, ret_val: List[Node]) -> None:
        """Generate flat and cone successors of a given node based on its Y coordinate.
        Project node's interval onto the next row
        """
        projection = IntervalProjection()

        if node.root.y == node.interval.row:
            projection.project(node, self._grid)
            self.flat_node_obs(node, ret_val, projection)

            projection.project_f2c(node, self._grid)
            self.flat_node_nobs(node, ret_val, projection)
        else:
            projection.project(node, self._grid)
            self.cone_node_obs(node, ret_val, projection)
            self.cone_node_nobs(node, ret_val, projection)

    def generate_start_successors(self, node: Node, ret_val: List[Node]) -> None:
        """Generate first successors of an off-grid node"""
        assert node.interval.left == node.interval.right and \
               node.interval.left == node.root.x and \
               node.interval.row == node.root.y, \
                f'Off-grid node\'s interval must contain only that node. Expected row == y; left == right == x'

        # certain successors will be ignored if the start is a double-corner
        start_dc = self._grid.get_point_is_double_corner(int(node.root.x), int(node.root.y))

        # certain start locations are ambiguous; we don't try to solve these
        if start_dc and not self._grid.get_cell_is_traversable(int(node.root.x), int(node.root.y)):
            return

        root_x, root_y = int(node.root.x), int(node.root.y)

        # generate flat observable successors left of the start point
        # NB: hacky implementation; we use a fake root for the projection
        projection = IntervalProjection()

        if not start_dc:
            projection.project(root_x, root_x, root_y,
                               root_x + 1, root_y, self._grid)
            
            self.generate_observable_flat__(projection, root_x, root_y, node, ret_val)

        # generate flat observable successors right of the start point
        # NB: hacky implementation; we use a fake root for the projection
        projection.project(root_x, root_x, root_y,
                           root_x - 1, root_y, self._grid)
        
        self.generate_observable_flat__(projection, root_x, root_y, node, ret_val)

        # generate conical observable successors below the start point
        max_left = self._grid.scan_cells_left(root_x, root_y) + 1
        max_right = self._grid.scan_cells_right(root_x, root_y)

        if max_left != root_x and not start_dc:
            self.split_interval_make_successors(max_left, root_x, root_y + 1,
                                                root_x, root_y, root_y + 1, node, ret_val)

        if max_right != root_x:
            self.split_interval_make_successors(root_x, max_right, root_y + 1,
                                                root_x, root_y, root_y + 1, node, ret_val)

        # generate conical observable successors above the start point
        max_left = self._grid.scan_cells_left(root_x - 1, root_y - 1) + 1
        max_right = self._grid.scan_cells_right(root_x, root_y - 1)

        if max_left != root_x and not start_dc:
            self.split_interval_make_successors(max_left, root_x, root_y - 1,
                                                root_x, root_y, root_y - 2, node, ret_val)

        if max_right != root_x:
            self.split_interval_make_successors(root_x, max_right, root_y - 1,
                                                root_x, root_y, root_y - 2, node, ret_val)

    def split_interval_make_successors(
        self,
        max_left: float,
        max_right: float,
        i_row: int,
        root_x: int,
        root_y: int,
        sterile_check_row: int,
        parent: Node,
        ret_val: List[Node]
    ) -> None:
        """After projecting the interval, split at each internal
        corner to generate new observable sucessors
        """
        if max_left == max_right:
            return

        succ_left = max_right
        succ_right = None
        num_successors = len(ret_val)
        target_node = self.contains_target(max_left, max_right, i_row)
        forced_succ = not self._prune or target_node

        successor = None
        while True:
            succ_right = succ_left
            succ_left = self._grid.scan_left(succ_right, i_row)

            if forced_succ or not self.sterile(succ_left, succ_right, sterile_check_row):
                successor = Node(parent=parent,
                                 interval=Interval(succ_left, succ_right, i_row),
                                 root=Point2D(root_x, root_y))
                
                successor.interval.left = max_left if succ_left < max_left else succ_left
                ret_val.append(successor)
            
            if succ_left != succ_right and succ_left > max_left:
                break

        if not forced_succ and len(ret_val) == (num_successors + 1) and \
           self.intermediate(successor.interval, root_x, root_y):
            del ret_val[-1]

            proj = IntervalProjection()
            proj.project_cone(successor.interval.left, successor.interval.right,
                              successor.interval.row, root_x, root_y, self._grid)

            if proj.valid and proj.observable:
                self.split_interval_make_successors(proj.left, proj.right, proj.row,
                                                    root_x, root_y, proj.sterile_check_row, parent, ret_val)

    def sterile(self, left: float, right: float, row: int) -> bool:
        """Check if non-discrete left and right points are adjacent to obstacle cells on row"""
        r = int(right - EPSILON)
        l = int(left + EPSILON)

        return not (self._grid.get_cell_is_traversable(l, row) and
                    self._grid.get_cell_is_traversable(r, row))

    def intermediate(self, interval: Interval, root_x: int, root_y: int) -> bool:
        """Return True if the interval has no adjacent successors.
        Intermediate nodes have intervals that are not taut; i.e.
        their endpoints are not adjacent to any location that cannot be
        directly observed from the root
        """
        row = interval.row
        left, right = interval.left, interval.right

        tmp_left = int(left)
        tmp_right = int(right)

        discrete_left = interval.discrete_left
        discrete_right = interval.discrete_right

        right_root = ((tmp_right - root_x) >> 31) == 1
        left_root = ((root_x - tmp_left) >> 31) == 1

        right_turning_point = False
        left_turning_point = False

        if root_y < row:
            left_turning_point: bool = discrete_left and \
                                       self._grid.get_point_is_corner(tmp_left, row) and \
                                       (not self._grid.get_cell_is_traversable(tmp_left - 1, row - 1) or left_root)

            right_turning_point: bool = discrete_right and \
                                        self._grid.get_point_is_corner(tmp_right, row) and \
                                        (not self._grid.get_cell_is_traversable(tmp_right, row - 1) or right_root)

        else:
            left_turning_point: bool = discrete_left and \
                                       self._grid.get_point_is_corner(tmp_left, row) and \
                                       (not self._grid.get_cell_is_traversable(tmp_left - 1, row) or left_root)

            right_turning_point: bool = discrete_right and \
                                        self._grid.get_point_is_corner(tmp_right, row) and \
                                        (not self._grid.get_cell_is_traversable(tmp_right, row) or right_root)

        return not ((discrete_left and left_turning_point) or (discrete_right and right_turning_point))

    def contains_target(self, left: float, right: float, row: int) -> bool:
        """Check if an given interval contains the target node"""
        return row == self._ty and self._tx >= left and self._tx <= right

    def cone_node_obs(self, node: Node, ret_val: List[Node], projection: IntervalProjection) -> None:
        """There is an inductive argument here: if the move is not valid
        the node should have been pruned. check this is always true
        """
        assert node.root.y != node.interval.row, \
            f'Node interval and root must not be on the same row. Got {node.root.y} and {node.interval.row}'

        self.generate_observable_cone__(projection, int(node.root.x), int(node.root.y), node, ret_val)

    def generate_observable_cone__(
            self,
            projection: IntervalProjection,
            root_x: int,
            root_y: int,
            parent: Node,
            ret_val: List[Node]
        ) -> None:
        """Generate observable cone successors by splitting the interval
        projection at each internal corner point
        """
        if not (projection.valid and projection.observable):
            return
        
        self.split_interval_make_successors(projection.left, projection.right,
                                            int(projection.row), root_x, root_y,
                                            projection.sterile_check_row, parent, ret_val)

    def cone_node_nobs(self, node: Node, ret_val: List[Node], projection: IntervalProjection) -> None:
        """There are two kinds of non-observable successors:
        (i) conical successors that are adjacent to an observable projection
        (ii) flat successors that are adjacent to the current interval
        (iii) conical successors that are not adjacent to any observable
        projection or the current interval (i.e the angle from the root
        to the interval is too low to observe any point from the next row)
        """
        if not projection.valid:
            return

        i_left, i_right = node.interval.left, node.interval.right
        i_row = int(node.interval.row)

        # non-observable successor type (iii)
        if not projection.observable:
            if node.root.x > i_right and \
               node.interval.discrete_right and \
               self._grid.get_point_is_corner(int(i_right), i_row):
                self.split_interval_make_successors(projection.max_left, i_right, projection.row,
                                                    int(i_right), i_row, projection.sterile_check_row,
                                                    node, ret_val)

            elif node.root.x < i_left and \
                 node.interval.discrete_left and \
                 self._grid.get_point_is_corner(int(i_left), i_row):
                  self.split_interval_make_successors(i_left, projection.max_right, projection.row,
                                                      int(i_left), i_row, projection.sterile_check_row,
                                                      node, ret_val)

            if node.interval.discrete_left and not \
               self._grid.get_cell_is_traversable(int(i_left - 1), projection.type_iii_check_row) and \
               self._grid.get_cell_is_traversable(int(i_left - 1), projection.check_vis_row):
                # non-observable successors to the left of the current interval
                projection.project_flat(i_left - self._grid.smallest_step_div2, i_left,
                                        int(i_left), int(i_row), self._grid)

                self.generate_observable_flat__(projection, int(i_left), i_row, node, ret_val)

            if node.interval.discrete_right and not \
               self._grid.get_cell_is_traversable(int(i_right), projection.type_iii_check_row) and \
               self._grid.get_cell_is_traversable(int(i_right), projection.check_vis_row):
                # non-observable successors to the right of the current interval
                projection.project_flat(i_right, i_right + self._grid.smallest_step_div2,
                                        int(i_right), int(i_row), self._grid)

                self.generate_observable_flat__(projection, int(i_right), i_row, node, ret_val)
            return

        # non-observable successors type (i) and (ii)
        flat_prj = IntervalProjection()
        corner_row = i_row - (int(node.root.y) - i_row) >> 31

        # non-observable successors to the left of the current interval
        if node.interval.discrete_left and self._grid.get_point_is_corner(int(i_left), i_row):
            # flat successors from the interval row
            if not self._grid.get_cell_is_traversable(int(i_left - 1), corner_row):
                flat_prj.project(i_left - EPSILON, i_right,
                                 int(i_row), int(i_left), int(i_row), self._grid)

                self.generate_observable_flat__(flat_prj, int(i_left), int(i_row), node, ret_val)

            # conical successors from the projected row
            self.split_interval_make_successors(projection.max_left, projection.left, projection.row,
                                                int(i_left), i_row, projection.sterile_check_row,
                                                node, ret_val)

        # non-observable successors to the right of the current interval
        if node.interval.discrete_right and self._grid.get_point_is_corner(int(i_right), i_row):
            # flat successors from the interval row
            if not self._grid.get_cell_is_traversable(int(i_right), corner_row):
                flat_prj.project(i_left, i_right + EPSILON,
                                 int(i_row), int(i_left), int(i_row), self._grid)

                self.generate_observable_flat__(flat_prj, int(i_right), i_row, node, ret_val)

            # conical successors from the projected row
            self.split_interval_make_successors(projection.right, projection.max_right, projection.row,
                                                int(i_right), i_row, projection.sterile_check_row,
                                                node, ret_val)

    def flat_node_obs(self, node: Node, ret_val: List[Node], projection: IntervalProjection) -> None:
        self.generate_observable_flat__(projection, int(node.root.x), int(node.root.y), node, ret_val)

    def generate_observable_flat__(
            self,
            projection: IntervalProjection,
            root_x: int,
            root_y: int,
            parent: Node,
            ret_val: List[Node]
        ) -> None:
        """Generate observable flat successors by splitting the interval
        projection at each internal corner point
        """
        assert projection.row == root_y, \
            f'Projection and root must be on the same row. Got {projection.row} and {root_y}'

        if not projection.valid:
            return

        goal_interval = self.contains_target(projection.left, projection.right, projection.row)

        if projection.intermediate and self._prune and not goal_interval:
            # ignore intermediate nodes and project further along the row
            projection.project(projection.left, projection.right, projection.row,
                               root_x, root_y, self._grid)

            # check if the projection contains the goal
            goal_interval = self.contains_target(projection.left, projection.right, projection.row)

        if not projection.dead_end or not self._prune or goal_interval:
            ret_val.append(
                Node(parent=parent,
                     interval=Interval(projection.left, projection.right, projection.row),
                     root=Point2D(root_x, root_y))
            )

    def flat_node_nobs(self, node: Node, ret_val: List[Node], projection: IntervalProjection) -> None:
        """Generate non-observable flat successors"""
        if not projection.valid:
            return

        # conical successors from the projected row
        new_root_y = node.interval.row
        if node.root.x <= node.interval.left:
            new_root_x = int(node.interval.right)
        else:
            new_root_x = int(node.interval.left)

        self.split_interval_make_successors(projection.left, projection.right, projection.row,
                                            new_root_x, new_root_y, projection.sterile_check_row,
                                            node, ret_val)
