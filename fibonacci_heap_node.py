from __future__ import annotations

from typing import TypeVar

T = TypeVar('T')


class FibonacciHeapNode:
    """Implements a node of the Fibonacci heap. 
    It holds the information necessary for maintaining 
    the structure of the heap. It also holds the reference to the
    key value (which is used to determine the heap structure).
    Translated Python version of Nathan Fiedler's FibonacciHeapNode

    Attributes
    ----------
    data : T
        Generic type node data
    parent : FibonacciHeapNode
        Parent node
    child : FibonacciHeapNode
        First child node
    right : FibonacciHeapNode
        Right sibling node
    left : FibonacciHeapNode
        Left sibling node
    key : float
        Key value for this node
    secondary_key : float
        Ditto
    degree : int
        Number of children of this node (doesn't count grandchildren)
    mark : bool
        Indicate whether this node has had a child removed since this
        node was added to its parent (True) or not (False)

    """

    BIG_ONE = 100000
    EPSILON = 1 / BIG_ONE

    def __init__(self, data: T):
        self.data = data
        self.reset()

    def reset(self) -> None:
        self.parent = None
        self.child = None
        self.right = self
        self.left = self
        self.key = 0
        self.secondary_key = 0
        self.degree = 0
        self.mark = False

    @staticmethod
    def less_than(
        pk_a: float,
        sk_a: float,
        pk_b: float,
        sk_b: float
    ) -> bool:
        tmp_key = int(pk_a * FibonacciHeapNode.BIG_ONE + 0.5)
        tmp_other = int(pk_b * FibonacciHeapNode.BIG_ONE + 0.5)
        if tmp_key < tmp_other:
            return True

        # tie-break in favour of nodes with higher
        # secondaryKey values
        if tmp_key == tmp_other:
            tmp_key = int(sk_a * FibonacciHeapNode.BIG_ONE + 0.5)
            tmp_other = int(sk_b * FibonacciHeapNode.BIG_ONE + 0.5)
            if tmp_key > tmp_other:
                return True
        return False

    def __lt__(self, other: FibonacciHeapNode) -> bool:
        """Return True if this node has a lower priority than other"""
        return FibonacciHeapNode.less_than(self.key, self.secondary_key,
                                           other.key, other.secondary_key)

    def __repr__(self) -> str:
        return str(self.key)
