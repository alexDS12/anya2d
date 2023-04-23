import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from node import Node
from interval import Interval

try:
    from sympy import Point2D
except ImportError as e:
    raise Exception('Unable to import SymPy, make sure you have it installed')


class TestNode(unittest.TestCase):
  def test_different_nodes(self):
    # same X, same Z, different interval, different Y
    self.assertTrue(
        Node(
            root = Point2D(1, 2),
            interval = Interval(1, 10, 0)
        )
        !=
        Node(
            root = Point2D(1, 5),
            interval = Interval(1, 1, 1)
        ),
        '1st assert did not pass'
    )

    # same X, same interval, different Y, different Z
    self.assertTrue(
        Node(
            root = Point2D(1, 2),
            interval = Interval(1, 10, 2)
        )
        !=
        Node(
            root = Point2D(1, 5),
            interval = Interval(1, 10, 2)
        ),
        '2nd assert did not pass'
    )

    # same Y, same Z, different X, different interval
    self.assertTrue(
        Node(
            root = Point2D(6, 5),
            interval = Interval(1, 10, 1)
        )
        !=
        Node(
            root = Point2D(1, 5),
            interval = Interval(1, 1, 1)
        ),
        '3rd assert did not pass'
    )

    # same interval, same Y, different X, different Z
    self.assertTrue(
        Node(
            root = Point2D(6, 5),
            interval = Interval(9, 12, 0)
        )
        !=
        Node(
            root = Point2D(1, 5),
            interval = Interval(9, 12, 0)
        ),
        '4th assert did not pass'
    )

  def test_same_nodes(self):
    self.assertTrue(
        Node(
            root = Point2D(3, 3),
            interval = Interval(2, 8, 5)
        )
        ==
        Node(
            root = Point2D(3, 3),
            interval = Interval(2, 8, 5)
        ),
        '1st assert did not pass'
    )

  def test_g_with_parents(self):
    n1 = Node(
        root = Point2D(1, 2),
        interval = Interval(1, 9, 1)
    )
    n1.g = 20
    
    n2 = Node(
        root = Point2D(3, 2),
        interval = Interval(2, 4, 2),
        parent = n1
    )

    self.assertTrue(
        abs(n2.g - 22) < 1e-07, # 20 + sqrt(2²)
        '1st assert did not pass'
    )

if __name__ == '__main__':
    unittest.main(argv=[''], verbosity=2, exit=False)