from traceback import format_exc
from argparse import ArgumentParser
from io import StringIO
from experiment_loader import ExperimentLoader
from experiment import Experiment
from search import Search
from expansion_policy import ExpansionPolicy
from bitpacked_grid_expansion_policy import BitpackedGridExpansionPolicy
from micro_benchmark import MicroBenchmark
from node import Node
from interval import Interval
from astar import AStar
from typing import TextIO, List, Iterator, Tuple


class ScenarioRunner:
    MAP_DIR = 'maps'
    RESULT_DIR = 'results'
    EXP_HEADER = 'exp;path_found;alg;wallt_micro;runt_micro;'+ \
        'expanded;generated;heapops;start;target;gridcost;realcost;map'
    
    def __init__(
        self,
        scenario_file_path: str,
        verbose: bool,
        save_output: bool
    ):
        self.scenario = scenario_file_path
        self.verbose = verbose
        self.save = save_output
    
    def run(self, alg_name: str) -> None:
        """Load experiments, run respective algorithm and
        save experiment results in a stream and save output to
        an external file if `save` is True
        """
        try:
            exp_loader = ExperimentLoader()
            experiments = exp_loader.load_experiments(f'{self.MAP_DIR}/{self.scenario}')
            if len(experiments) == 0:
                print('No experiments to run; finishing.')
                return
            
            num_exps = len(experiments)
            map_file = experiments[0].map_file
            res_stream = StringIO()
            res_stream.write(f'{ScenarioRunner.EXP_HEADER}\n')
            
            for i, exp_line in enumerate(eval(f'self.run_{alg_name}(experiments, map_file)'), start=1):
                res_stream.write(f'{exp_line}\n')
                if i % 500 == 0:
                    print(f'Computed {i}/{num_exps} experiments') 

            print(res_stream.getvalue())
            if self.save:
                ScenarioRunner.save_result(res_stream, map_file, alg_name)
        except Exception as e:
            raise Exception(f'Issue while trying to run {alg_name}:\n{e}')

    def run_anya(self, experiments: List[Experiment], map_file: str) -> Iterator[Tuple[str]]:
        print(f'Running Anya for {self.scenario}')
        
        try:
            anya = Search(ExpansionPolicy(f'{self.MAP_DIR}/{map_file}'))
            if self.verbose:
                anya.VERBOSE = True
        except Exception as e:
            raise Exception(format_exc())

        exp_runner = MicroBenchmark(anya)
        start = Node.from_points(Interval(0, 0, 0), 0, 0)
        target = Node.from_points(Interval(0, 0, 0), 0, 0)

        anya.mb_start = start
        anya.mb_target = target

        for exp in experiments:
            start.root.set_location(exp.start_x, exp.start_y)
            start.interval.init(exp.start_x, exp.start_x, exp.start_y)
            
            target.root.set_location(exp.end_x, exp.end_y)
            target.interval.init(exp.end_x, exp.end_x, exp.end_y)
                    
            wallt_micro = exp_runner.benchmark(1)
            cost = anya.mb_cost
            duration = exp_runner.avg_time + 0.5

            yield (f'{exp.title};{anya.path_found};AnyaSearch;{wallt_micro};{duration};'
                   f'{anya.expanded};{anya.generated};{anya.heap_ops};'
                   f'({exp.start_x},{exp.start_y});({exp.end_x},{exp.end_y});'
                   f'{exp.title};{exp.upper_bound};{cost};{exp.map_file}')

    def run_astar(self, experiments: List[Experiment], map_file: str) -> Iterator[str]:
        print(f'Running A-star for {self.scenario}')

        try:
            astar = AStar(BitpackedGridExpansionPolicy(f'{self.MAP_DIR}/{map_file}'))
            if self.verbose:
                astar.VERBOSE = True
        except Exception as e:
            raise Exception(format_exc())
        
        exp_runner = MicroBenchmark(astar)
        
        for exp in experiments:
            astar.mb_start = astar.expander.get_grid_vertex(exp.start_x, exp.start_y)
            astar.mb_target = astar.expander.get_grid_vertex(exp.end_x, exp.end_y)
            
            wallt_micro = exp_runner.benchmark(1)
            cost = astar.mb_cost
            duration = exp_runner.avg_time + 0.5

            yield (f'{exp.title};{astar.path_found};AStar;{wallt_micro};{duration};'
                   f'{astar.expanded};{astar.generated};{astar.heap_ops};'
                   f'({exp.start_x},{exp.start_y});({exp.end_x},{exp.end_y});'
                   f'{exp.upper_bound};{cost};{exp.map_file}')

    @staticmethod
    def save_result(stream: TextIO, map_file: str, alg: str) -> None:
        f_name = ScenarioRunner.get_output_f_name(map_file, alg)
        print(f'Saving experiments to {f_name}')
        
        stream.seek(0)
        with open(f_name, 'w') as f:
            print(stream.getvalue(), file=f)
    
    @staticmethod
    def get_output_f_name(map_file: str, alg: str) -> str:
        return f"{ScenarioRunner.RESULT_DIR}/{alg}_{map_file.replace('.map', '.txt')}"


def main():
    parser = ArgumentParser()
    parser.add_argument('-scen', '--scenario',
                        required=True,
                        help='Map scenario to run experiments')
    
    parser.add_argument('-v', '--verbose',
                        action='store_true', 
                        help='Verbose output')
    
    parser.add_argument('--save',
                        action='store_true',
                        help='Save output to an external file')

    parser.add_argument('-alg', '--algorithm',
                        type=lambda arg: arg.lower(),
                        choices=['anya', 'astar'],
                        required=True,
                        help='Possible algorithms: anya, astar (case-insensitive)')
    
    args = parser.parse_args()
    runner = ScenarioRunner(args.scenario, args.verbose, args.save)
    runner.run(args.algorithm)


if __name__ == '__main__':
    main()
