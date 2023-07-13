from traceback import format_exc
from argparse import ArgumentParser
from search import Search
from expansion_policy import ExpansionPolicy
from micro_benchmark import MicroBenchmark
from node import Node
from interval import Interval
from random import randint
from collections import defaultdict
from typing import Tuple


class RandomRunner:
    MAP_DIR = 'maps'
    RESULT_DIR = 'results/random'
    RUN_HEADER = 'id_map;start;target;path_cost;bench_time;run_time;expanded;generated;heapops'

    def run_anya(self, map_file: str) -> None:
        print(f'Running Anya for {map_file}')

        try:
            expander = ExpansionPolicy(f'{self.MAP_DIR}/{map_file}')
            grid = expander.grid
            anya = Search(expander)
        except Exception as e:
            raise Exception(format_exc())

        exp_runner = MicroBenchmark(anya)
        start = Node.from_points(Interval(0, 0, 0), 0, 0)
        target = Node.from_points(Interval(0, 0, 0), 0, 0)

        anya.mb_start = start
        anya.mb_target = target

        max_width = grid.map_width_original
        max_height = grid.map_height_original

        point_history = defaultdict(set)
        
        with open(RandomRunner.get_file_path('anya', map_file), 'w') as run_file:
            print(f'{RandomRunner.RUN_HEADER}', file=run_file)

            while True:
                start_point = self.randomize_point(max_width, max_height)
                while not grid.get_cell_is_traversable(*start_point):
                    start_point = self.randomize_point(max_width, max_height)

                target_point = self.randomize_point(max_width, max_height)
                while (start_point == target_point or 
                    not grid.get_cell_is_traversable(*target_point)):
                    target_point = self.randomize_point(max_width, max_height)

                if (start_point not in point_history or 
                    target_point not in point_history[start_point]):
                    # add start -> target and target -> start to history (same cost going backwards)
                    point_history[start_point].add(target_point)
                    point_history[target_point].add(start_point)

                    start.root.set_location(*start_point)
                    start.interval.init(start_point[0], *start_point)
                    
                    target.root.set_location(*target_point)
                    target.interval.init(target_point[0], *target_point)
                            
                    wallt_micro = exp_runner.benchmark(1)
                    cost = anya.mb_cost
                    path_found = anya.path_found
                    duration = exp_runner.avg_time + 0.5

                    if path_found:
                        print((f'{map_file.replace(".map", "")};'
                               f'{start_point};{target_point};{cost};{wallt_micro};'
                               f'{duration};{anya.expanded};{anya.generated};{anya.heap_ops}'), file=run_file)
     
    def randomize_point(self, max_width: int, max_height: int) -> Tuple[int, int]:
        return randint(0, max_width), randint(0, max_height)
    
    @staticmethod
    def get_file_path(alg: str, map_file: str) -> str:
        return f"{RandomRunner.RESULT_DIR}/{alg}_{map_file.replace('.map', '.csv')}"


def main():
    parser = ArgumentParser()
    parser.add_argument('-map_file', '--map_file', 
                        help='Map file to compute random paths', required=True)

    parser.add_argument('-alg', '--algorithm',
                        type=lambda arg: arg.lower(),
                        choices=['anya', 'astar'],
                        required=True,
                        help='Possible algorithms: anya, astar (case-insensitive)')
    
    args = parser.parse_args()
    runner = RandomRunner()
    try:
        eval(f'runner.run_{args.algorithm}(args.map_file)')
    except Exception as e:
        raise Exception(f'Issue while trying to run {args.algorithm}:\n{e}')


if __name__ == '__main__':
    main()
