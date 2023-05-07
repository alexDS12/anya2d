from __future__ import annotations

from typing import TypeVar, Generic


T = TypeVar('T')


class FibonacciHeapNode(Generic[T]):
    """Implements a node of the Fibonacci heap. It holds the information necessary
    for maintaining the structure of the heap. It also holds the reference to the
    key value (which is used to determine the heap structure).
    This is a merely copy of Daniel Harabor's FibonacciHeapNode

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
        Indicate whether this node has had a child removed since this node was added to its parent (True) or not (False)

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

    @property
    def key(self) -> float:
        """Get key for this node"""
        return self.key

    @property
    def secondary_key(self) -> float:
        """Get secondary key for this node"""
        return self.secondary_key

    @property
    def data(self) -> T:
        """Get data for this node"""
        return self.data

    def __lt__(self, other: FibonacciHeapNode) -> bool:
        """Return True if this node has a lower priority than other node"""
        tmp_key = self.key * self.BIG_ONE + 0.5
        tmp_other = other.key * self.BIG_ONE + 0.5
        if tmp_key < tmp_other:
            return True

        if tmp_key == tmp_other:
            tmp_key = self.secondary_key * self.BIG_ONE + 0.5
            tmp_other = other.secondary_key * self.BIG_ONE + 0.5

            if tmp_key > tmp_other:
                return True
        return False

    def __repr__(self) -> str:
        """Representation of the node object"""
        return str(self.key)
