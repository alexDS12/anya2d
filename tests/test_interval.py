import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from interval import Interval

try:
    from sympy import Point2D
except ImportError as e:
    raise Exception('Unable to import SymPy, make sure you have it installed')


class TestInterval(unittest.TestCase):
  def test_same_intervals(self):
    self.assertTrue(
        Interval(left=1, right=1, row=0) == Interval(left=1, right=1, row=0),
        '1st assert did not pass'
    )

    self.assertTrue(
        Interval(left=5, right=15, row=13) == Interval(left=5, right=15, row=13),
        '2nd assert did not pass'
    )

  def test_different_intervals(self):
    # same left and right, different row
    self.assertTrue(
        Interval(left=1, right=1, row=0) != Interval(left=1, right=1, row=3),
        '1st assert did not pass'
    )
    # different left and right, same row
    self.assertTrue(
        Interval(left=1, right=3, row=0) != Interval(left=4, right=7, row=0),
        '2nd assert did not pass'
    )
    # same left, different right and row
    self.assertTrue(
        Interval(left=1, right=2, row=1) != Interval(left=1, right=5, row=0),
        '3rd assert did not pass'
    )
    # different left, same right and row
    self.assertTrue(
        Interval(left=3, right=2, row=1) != Interval(left=1, right=2, row=1),
        '4th assert did not pass'
    )

  def test_covers_interval(self):
    # (1, 8, 0) covers (2, 5, 0)
    self.assertTrue(
        Interval(left=1, right=8, row=0).covers(Interval(left=2, right=5, row=0)),
        '1st assert did not pass'
    )
    # (1, 3, 5) == (1, 3, 5)
    self.assertTrue(
        Interval(left=1, right=3, row=5).covers(Interval(left=1, right=3, row=5)),
        '2nd assert did not pass'
    )
    # (1, 8, 0) does not cover (2, 5, 2), diff rows
    self.assertFalse(
        Interval(left=1, right=8, row=0).covers(Interval(left=2, right=5, row=2)),
        '3rd assert did not pass'
    )
    # (1, 3, 5) does not cover (1, 3, 1), same left and right but diff row
    self.assertFalse(
        Interval(left=1, right=3, row=5).covers(Interval(left=1, right=3, row=1)),
        '4th assert did not pass'
    )
    # (4, 8, 0) does not cover (2, 5, 0), bigger left
    self.assertFalse(
        Interval(left=4, right=8, row=0).covers(Interval(left=2, right=5, row=0)),
        '5th assert did not pass'
    )
    # (4, 8, 9) does not cover (5, 10, 9), smaller right
    self.assertFalse(
        Interval(left=4, right=8, row=9).covers(Interval(left=5, right=10, row=9)),
        '6th assert did not pass'
    )

  def test_interval_contains_point(self):
    self.assertTrue(
        Interval(left=1, right=5, row=0).contains(Point2D(1, 0)),
        '1st assert did not pass'
    )

    self.assertTrue(
        Interval(left=3.5, right=7, row=5).contains(Point2D(4, 5)),
        '2nd assert did not pass'
    )

    self.assertFalse(
        Interval(left=3.5, right=7, row=0).contains(Point2D(4, 5)),
        '3rd assert did not pass'
    )

    self.assertFalse(
        Interval(left=5, right=7, row=5).contains(Point2D(2, 5)),
        '4th assert did not pass'
    )

    self.assertFalse(
        Interval(left=5, right=7, row=1).contains(Point2D(8, 1)),
        '5th assert did not pass'
    )

    self.assertFalse(
        Interval(left=2, right=7, row=1).contains(Point2D(7.000001, 1)),
        '6th assert did not pass'
    )

    self.assertTrue(
        Interval(left=2, right=7, row=1).contains(Point2D(7.0000000001, 1)),
        '7th assert did not pass'
    )

if __name__ == '__main__':
    unittest.main(argv=[''], verbosity=2, exit=False)