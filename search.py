from expansion_policy import ExpansionPolicy
from node import Node
from fibonacci_heap import FibonacciHeap
from fibonacci_heap_node import FibonacciHeapNode
from path import Path
from constants import EPSILON
from ai import _load_model, predict
from typing import Dict, Optional


class SearchNode(FibonacciHeapNode):
    """This class holds various bits of data needed
    to drive the search

    Attributes
    ----------
    parent : SearchNode
        Parent node of current node
    search_id : int
        Tracks if the node has been added to open_list
    closed : bool
        Tracks if the node has been expanded

    """

    def __init__(self, vertex: Node):
        super().__init__(vertex)
        self.search_id = -1

    def reset_(self, search_id_counter: int) -> None:
        """Reset search node attrs"""
        self.parent = None
        self.search_id = search_id_counter
        self.closed = False
        super().reset()

    def __repr__(self) -> str:
        """Debug representation of the search node"""
        return f'({self.data.x}, {self.data.y})'


class Search:
    """An implementation of the Anya search algorithm.
    A new search always starts on an off-grid node which is only
    visible from the start node. The corresponding cost from 
    the off-grid node to start node is zero

    Attributes
    ----------
    _expander : ExpansionPolicy
        Policy to expand nodes and generate their successors
    _heuristic : Heuristic
        Heuristic to evaluate movement costs from a given node to another
    roots_ : Dict[int, self.SearchNode]
        Tracks if the node has been expanded. Helps to avoid root-level redundancy
    expanded : int
        Tracks how many nodes were expanded
    insertions : int
        Tracks how many nodes were inserted into the open list
    generated : int
        Tracks how many neighbors were generated during the search
    heap_ops : int
        Counts operations in the heap structure
    open : FibonacciHeap
        Priority queue where unexpanded search nodes are stored ordered by their f value
    mb_start : Node
        Start node
    mb_target : Node
        Target node
    mb_cost : float
        Cost between start and target nodes
    path_found : bool
        Flag indicating whether or not path was found
    model : Optional[Sequential]
        Trained DNN model to compute distance between nodes
    id_map : Optional[str]
        Map name to be used for DNN computations

    """

    search_id_counter = 0
    VERBOSE = False

    def __init__(
        self,
        expander: ExpansionPolicy,
        model_path: Optional[str] = None,
        id_map: Optional[str] = None
    ):
        self.roots_: Dict[int, SearchNode] = {}
        self.open = FibonacciHeap()
        self._heuristic = expander.heuristic
        self._expander = expander
        self.mb_start = None
        self.mb_target = None
        if model_path is not None:
            self.model = _load_model(model_path)
            self.id_map = id_map

    def init(self) -> None:
        """Initialize open, closed and counters for a new search"""
        Search.search_id_counter += 1
        self.expanded = 0
        self.insertions = 0
        self.generated = 0
        self.heap_ops = 0
        self.open.clear()
        self.roots_.clear()
        self.path_found = False

    def print_path(self, current: SearchNode) -> None:
        """Get path starting from the first search node that is a parent
        to the last node before target
        """
        if current.parent is not None:
            self.print_path(current.parent)
        print(f'{current.data.root}; g={current.secondary_key}')

    def search(self, start: Node, target: Node) -> Path:
        """Perform search from `start` to `target` if there's a solution.
        First compute path cost only and generate path going backwards on nodes
        """
        cost = self.search_costonly(start, target)
        # generate the path
        path = Path()
        if cost != -1:
            node = self.generate(target)
            while True:
                path = Path(node.data, path, node.secondary_key)
                if node.parent is None:
                    break
                node = node.parent
        return path

    def search_costonly(self, start: Node, target: Node) -> float:
        """Perform cost only search from `start` to `target` if one exists.
        Initialize start search node and insert into the priority queue
        where later on lowest f-value nodes will be expanded.
        Iterate over all successors queued and update their g-value
        based on Harabor's strategy to avoid root-level redundancies
        """
        self.init()
        cost = -1
        if not self._expander.validate_instance(start, target):
            return cost

        start_node = self.generate(start)
        start_node.reset_(Search.search_id_counter)

        if hasattr(self, 'model'):
            value = predict(self.model, self.id_map, *start.root, *target.root)
        else:
            value = self._heuristic.get_value(start, target)
        self.open.insert(start_node, value, 0)

        while not self.open.is_empty():
            current: SearchNode = self.open.remove_min()
            
            if self.VERBOSE:
                print(f'expanding (f={current.key}) {current}')

            self._expander.expand(current.data)
            self.expanded += 1
            self.heap_ops += 1

            if current.data.interval.contains(target.root):
                # found the goal
                cost = current.key
                self.path_found = True

                if self.VERBOSE:
                    self.print_path(current)
                break

            # unique id for the root of the parent node
            p_hash = self._expander.hash(current.data)

            # iterate over all neighbours
            while self._expander.has_next():
                succ = self._expander.next()
                neighbour = self.generate(succ)

                insert = True
                root_hash = self._expander.hash(succ)
                root_rep = self.roots_.get(root_hash, None)
                new_g_value = current.secondary_key + self._expander.step_cost()

                """Root level pruning:
                We prune a node if its g-value is larger than the best
                distance to its root point. In the case that the g-value
                is equal to the best known distance, we prune only if the
                node isn't a sibling of the node with the best distance or
                if the node with the best distance isn't the immediate parent
                """
                if root_rep is not None:
                    """Secondary key stores the g-value of the node
                    We check if the root has a g-value <= than current value.
                    If the value improves, the node is added to the open list
                    while updating its g-value in the root history.
                    If it doesn't, we discard the node
                    """
                    root_best_g = root_rep.secondary_key
                    insert = (new_g_value - root_best_g) <= EPSILON
                    eq = (new_g_value - root_best_g) >= -EPSILON
                    if insert and eq and root_rep.parent is not None:
                        p_rep_hash = self._expander.hash(root_rep.parent.data)
                        insert = (root_hash == p_hash) or (p_rep_hash == p_hash)

                if insert:
                    """Neighbor not found in the root history,
                    which means it must be inserted. Reset its 
                    search counter, add current node being expanded
                    as its parent and add to open and to root history
                    """
                    neighbour.reset_(Search.search_id_counter)
                    neighbour.parent = current
                    
                    if hasattr(self, 'model'):
                        value = predict(self.model, self.id_map,
                                        *neighbour.data.root, *target.root)
                    else:
                        value = self._heuristic.get_value(neighbour.data, target)

                    self.open.insert(
                        neighbour,
                        new_g_value + value,
                        new_g_value
                    )
                    self.roots_[root_hash] = neighbour

                    if self.VERBOSE:
                        print(f'\tinserting with f={neighbour.key} (g={new_g_value}) {neighbour}')

                    self.heap_ops += 1
                    self.insertions += 1

                else:
                    if self.VERBOSE:
                        print(f'\told rootg: {root_rep.secondary_key}')
                        print(f'\tNOT inserting with f={neighbour.key} (g={new_g_value}) {neighbour}')

        if self.VERBOSE:
            print('finishing search;')
        return cost

    def generate(self, v: Node) -> SearchNode:
        """Generate a new search node that acts as Fibonacci heap node under the hood"""
        retval = SearchNode(v)
        self.generated += 1
        return retval

    def run(self) -> None:
        """Initiate a new search based on current start and target nodes"""
        self.mb_cost = self.search_costonly(self.mb_start, self.mb_target)
