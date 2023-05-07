from __future__ import annotations

from math import log, sqrt, floor
from collections import deque
from io import StringIO
from fibonacci_heap_node import FibonacciHeapNode
from typing import TypeVar, Generic, Optional


T = TypeVar('T')


class FibonacciHeap(Generic[T]):
    """This class implements a Fibonacci heap data structure. Much of the code in
    this class is based on the algorithms in the "Introduction to Algorithms" by
    Cormen, Leiserson, and Rivest in Chapter 21. The amortized running time of
    most of these methods is O(1), making it a very fast data structure. Several
    have an actual running time of O(1). removeMin() and delete() have O(log n)
    amortized running times because they do the heap consolidation. If you
    attempt to store nodes in this heap with key values of -Infinity
    the delete() operation may fail to remove the correct element.
    This is a merely copy of Daniel Harabor's FibonacciHeap

    Attributes
    ----------
    _min_node : T
        Points to the minimum node in the heap
    _n_nodes : int
        Number of nodes in the heap

    """

    ONE_OVER_LOG_PHI = 1.0 / log((1.0 + sqrt(5.0)) / 2.0)

    def __init__(self):
        self.clear()

    def is_empty(self) -> bool:
        """Tests if the Fibonacci heap is empty or not. Returns True if the heap is
        empty, False otherwise.
        """
        return self._min_node is None

    def clear(self) -> None:
        """Removes all elements from this heap."""
        self._min_node: FibonacciHeapNode = None
        self._n_nodes: int = 0

    @property
    def min_node(self) -> FibonacciHeapNode:
        """Returns the smallest element in the heap. This smallest element is the
        one with the minimum key value.
        """
        return self._min_node

    @min_node.setter
    def min_node(self, min_node: FibonacciHeapNode) -> None:
        self._min_node = min_node

    @property
    def n_nodes(self) -> int:
        """Returns the size of the heap which is measured in the number of elements
        contained in the heap.
        """
        return self._n_nodes

    @n_nodes.setter
    def n_nodes(self, n_nodes: int) -> None:
        self._n_nodes = n_nodes

    def decrease_key(
        self,
        x: FibonacciHeapNode,
        k: float,
        new_secondary_key: Optional[float] = None
    ) -> None:
        """Decreases the key value for a heap node, given the new value to take on.
        The structure of the heap may be changed and will not be consolidated
        """
        if new_secondary_key is not None:
            x.secondary_key = new_secondary_key
            self.decrease_key(x, k)
        else:
            tmp_k = k * FibonacciHeapNode.BIG_ONE + 0.5
            tmp_x = x.key * FibonacciHeapNode.BIG_ONE + 0.5
            if tmp_k > tmp_x:
                raise Exception('decreaseKey() got larger key value')

            x.key = k
            y: FibonacciHeapNode = x.parent
            if y is not None and x < y:
                self.cut(x, y)
                self.cascading_cut(y)

            if x < self._min_node:
                self._min_node = x

    def delete(self, x: FibonacciHeapNode) -> None:
        """Deletes a node from the heap given the reference to the node. The trees
        in the heap will be consolidated, if necessary. This operation may fail
        to remove the correct element if there are nodes with key value -Infinity
        """
        self.decrease_key(x, float('-Inf'))

        # remove the smallest, which decreases n also
        self.remove_min()

    def insert(
        self,
        node: FibonacciHeapNode,
        k: float,
        new_secondary_key: Optional[float] = None
    ) -> None:
        """Inserts a new data element into the heap. No heap consolidation is
        performed at this time, the new node is simply inserted into the root
        list of this heap
        """
        if new_secondary_key is not None:
            node.secondary_key = new_secondary_key
            self.insert(node, k)
        else:
            node.key = k

            # concatenate node into min list
            if self._min_node is not None:
                node.left = self._min_node
                node.right = self._min_node.right
                self._min_node.right = node
                node.right.left = node
                if node < self._min_node:
                    self._min_node = node
            else:
                self._min_node = node
            self._n_nodes += 1

    def remove_min(self) -> FibonacciHeapNode:
        z = self._min_node

        if z is not None:
            num_kids = z.degree
            x: FibonacciHeapNode = z.child
            temp_right: FibonacciHeapNode = None

            # for each child of z do...
            while num_kids > 0:
                temp_right = x.right

                # remove x from child list
                x.left.right = x.right
                x.right.left = x.left

                # add x to root list of heap
                x.left = self._min_node
                x.right = self._min_node.right
                self._min_node.right = x
                x.right.left = x

                # set parent[x] to null
                x.parent = None
                x = temp_right
                num_kids -= 1

            # remove z from root list of heap
            z.left.right = z.right
            z.right.left = z.left

            if z == z.right:
                self._min_node = None
            else:
                self._min_node = z.right
                self.consolidate()

            # decrement size of heap
            self._n_nodes -= 1
        return z

    @staticmethod
    def union(h1: FibonacciHeap, h2: FibonacciHeap) -> FibonacciHeap:
        """Joins two Fibonacci heaps into a new one. No heap consolidation is
        performed at this time. The two root lists are simply joined together.
        """
        h = FibonacciHeap()

        if h1 is not None and h2 is not None:
            h.min_node = h1.min_node

            if h.min_node is not None:
                if h2.min_node is not None:
                    h.min_node.right.left = h2.min_node.left
                    h2.min_node.left.right = h.min_node.right
                    h.min_node.right = h2.min_node
                    h2.min_node.left = h.min_node

                    if h2.min_node < h1.min_node:
                        h.min_node = h2.min_node
            else:
                h.min_node = h2.min_node

            h.n_nodes = h1.n_nodes + h2.n_nodes
        return h

    def cascading_cut(self, y: FibonacciHeapNode) -> None:
        """Performs a cascading cut operation. This cuts y from its parent and then
        does the same for its parent, and so on up the tree.
        """
        z: FibonacciHeapNode = y.parent

        # if there's a parent...
        if z is not None:
            # if y is unmarked, set it marked
            if not y.mark:
                y.mark = True
            else:
                # it's marked, cut it from parent
                self.cut(y, z)

                # cut its parent as well
                self.cascading_cut(z)

    def consolidate(self) -> None:
        array_size = int(floor(log(self._n_nodes) * self.ONE_OVER_LOG_PHI)) + 1

        # Initialize degree array
        array = [None] * array_size

        # Find the number of root nodes
        num_roots = 0
        x = self._min_node

        if x is not None:
            num_roots += 1
            x = x.right

            while x is not self._min_node:
                num_roots += 1
                x = x.right

        # For each node in root list do...
        while num_roots > 0:
            # Access this node's degree..
            d = x.degree
            next: FibonacciHeapNode = x.right

            # ..and see if there's another of the same degree.
            while True:
                try:
                    y: FibonacciHeapNode = array[d]
                except IndexError:
                    break  # Nope.

                # There is, make one of the nodes a child of the other.
                # Do this based on the key value.
                if y < x:
                    x, y = y, x

                # y disappears from root list.
                self.link(y, x)

                # We've handled this degree, go to next one.
                array[d] = None
                d += 1

            # Save this node for later when we might encounter another
            # of the same degree.
            array[d] = x

            # Move forward through list.
            x = next
            num_roots -= 1

        # Set min to null (effectively losing the root list) and
        # reconstruct the root list from the array entries in array[].
        self._min_node = None

        for i in range(array_size):
            try:
                y: FibonacciHeapNode = array[i]
            except IndexError:
                continue  # if y does not exist

            # We've got a live one, add it to root list.
            if self._min_node is not None:
                # First remove node from root list.
                y.left.right = y.right
                y.right.left = y.left

                # Now add to root list, again.
                y.left = self._min_node
                y.right = self._min_node.right
                self._min_node.right = y
                y.right.left = y

                # Check if this is a new min.
                if y < self._min_node:
                    self._min_node = y
            else:
                self._min_node = y

    def cut(self, x: FibonacciHeapNode, y: FibonacciHeapNode) -> None:
        """The reverse of the link operation: removes x from the child list of y.
        This method assumes that min is non-null.
        """
        # remove x from childlist of y and decrement degree[y]
        x.left.right = x.right
        x.right.left = x.left
        y.degree -= 1

        # reset y.child if necessary
        if y.child == x:
            y.child = x.right

        if y.degree == 0:
            y.child = None

        # add x to root list of heap
        x.left = self._min_node
        x.right = self._min_node.right
        self._min_node.right = x
        x.right.left = x

        # set parent[x] to nil
        x.parent = None

        # set mark[x] to false
        x.mark = False

    def link(self, y: FibonacciHeapNode, x: FibonacciHeapNode) -> None:
        """Make node y a child of node x."""
        # remove y from root list of heap
        y.left.right = y.right
        y.right.left = y.left

        # make y a child of x
        y.parent = x

        if x.child is None:
            x.child = y
            y.right = y
            y.left = y
        else:
            y.left = x.child
            y.right = x.child.right
            x.child.right = y
            y.right.left = y

        # increase degree[x]
        x.degree += 1

        # set mark[y] false
        y.mark = False

    def __repr__(self) -> str:
        """Creates a String representation of this Fibonacci heap."""
        if self._min_node is None:
            return 'FibonacciHeap=[]'
        
        # create a new stack and put root on it
        stack = deque()
        stack.append(self._min_node)

        with StringIO() as buf:
            buf.append('FibonacciHeap=[')

            # do a simple breadth-first traversal on the tree
            while len(stack) > 0:
                curr: FibonacciHeapNode = stack.pop()
                buf.append(curr)
                buf.append(', ')

                if curr.child is not None:
                    stack.append(curr.child)

                start: FibonacciHeapNode = curr
                curr = curr.right

                while curr != start:
                    buf.append(curr)
                    buf.append(', ')

                    if curr.child is not None:
                        stack.append(curr.child)

                    curr = curr.right
            
            buf.append(']')
            out = buf.getvalue()
        return out