from sys import maxsize
from time import time_ns
from search import Search


class MicroBenchmark:
    def __init__(self, runnable: Search):
        self.runnable = runnable
        self.avg_time = -1
        self.max_time = -1
        self.min_time = maxsize

    def benchmark(self, reps: int) -> float:
        """Run an experiment and record some statistics. 
        Experiments are run repeatedly until the recorded time
        """
        if reps <= 0:
            return 0

        wall_start = time_ns()

        start = time_ns()
        for _ in range(reps):
            self.runnable.run()

        total_time = time_ns() - start
        self.avg_time = (total_time / 1000.0) / reps  # in microsecs

        # rerun the experiment if the total time is below the
        # guaranteed resolution of the timer (1 millisecond)
        if (total_time / 1000000) == 0:
            self.benchmark(reps * 2)

        return ((time_ns() - wall_start) / 1000) + 0.5

    def run(self, valid_iteration: bool) -> None:
        start = time_ns()
        self.runnable.run()
        time = (time_ns() - start) / 1000  # converting to microseconds

        if not valid_iteration:
            return

        self.avg_time += time

        if self.max_time < time:
            self.max_time = time

        if self.min_time > time:
            self.min_time = time
