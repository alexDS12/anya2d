from bitpacked_grid_expansion_policy import BitpackedGridExpansionPolicy
from point import Point2D
from fibonacci_heap import FibonacciHeap
from search import SearchNode
from path import Path
from constants import EPSILON
from ai import _load_model, predict
from typing import Dict, Optional


class AStar:
    """ An implementation of the A* search algorithm.
    Acts like the Anya search under the hood

    """
    
    search_id_counter = 0
    VERBOSE = False
        
    def __init__(
        self,
        expander: BitpackedGridExpansionPolicy, 
        model_path: Optional[str], 
        id_map: Optional[str]
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

    @property
    def expander(self) -> BitpackedGridExpansionPolicy:
        """Get expansion policy used for this search"""
        return self._expander

    def init(self) -> None:
        AStar.search_id_counter += 1
        self.expanded = 0
        self.insertions = 0
        self.generated = 0
        self.heap_ops = 0
        self.open.clear()
        self.roots_.clear()
        self.path_found = False

    def print_path(self, current: SearchNode) -> None:
        if current.parent is not None:
            self.print_path(current.parent)
        print(f'{current.data}; g={current.secondary_key}')

    def search(self, start: Point2D, target: Point2D) -> Path:
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

    def search_costonly(self, start: Point2D, target: Point2D) -> float:
        self.init()
        cost = -1
        if not self._expander.validate_instance(start, target):
            return cost
        
        start_node = self.generate(start)
        start_node.reset_(AStar.search_id_counter)

        if hasattr(self, 'model'):
            value = predict(self.model, self.id_map, *start, *target)
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

            if current.data == target:
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
                n = self._expander.next()
                neighbour = self.generate(n)

                insert = True
                root_hash = self._expander.hash(n)
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
                    neighbour.reset_(AStar.search_id_counter)
                    neighbour.parent = current

                    if hasattr(self, 'model'):
                        value = predict(self.model, self.id_map,
                                        *neighbour.data, *target)
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
    
    def generate(self, v: Point2D) -> SearchNode:
        retval = SearchNode(v)
        self.generated += 1
        return retval
    
    def run(self) -> None:
        self.mb_cost = self.search_costonly(self.mb_start, self.mb_target)
