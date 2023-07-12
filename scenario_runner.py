import os
from traceback import format_exc
from argparse import ArgumentParser
from experiment_loader import ExperimentLoader
from experiment import Experiment
from search import Search
from expansion_policy import ExpansionPolicy
from bitpacked_grid_expansion_policy import BitpackedGridExpansionPolicy
from micro_benchmark import MicroBenchmark
from node import Node
from interval import Interval
from astar import AStar
from typing import List, Iterator, Tuple, Optional


class ScenarioRunner:
    MAP_DIR = 'maps'
    RESULT_DIR = 'results'
    EXP_HEADER = 'exp;path_found;alg;wallt_micro;runt_micro;'+ \
        'expanded;generated;heapops;start;target;gridcost;realcost;map'
    
    def __init__(
        self,
        scenario_file_path: str,
        verbose: bool
    ):
        self.scenario = scenario_file_path
        self.verbose = verbose
    
    def run(self, alg_name: str, model_path: Optional[str]) -> None:
        """Load experiments, run respective algorithm and
        save experiment results in an external file
        """
        try:
            exp_loader = ExperimentLoader()
            experiments = exp_loader.load_experiments(f'{self.MAP_DIR}/{self.scenario}')
            if len(experiments) == 0:
                print('No experiments to run; finishing.')
                return
            
            map_file = experiments[0].map_file
            file_path = ScenarioRunner.get_file_path(alg_name, map_file, model_path)
            with open(file_path, 'w') as run_file:
                print(f'{ScenarioRunner.EXP_HEADER}', file=run_file)
                
                for exp_line in eval(f'self.run_{alg_name}(experiments, map_file, model_path)'):
                    print(exp_line, file=run_file)
        except Exception as e:
            raise Exception(f'Issue while trying to run {alg_name}:\n{e}')

    def run_anya(
        self,
        experiments: List[Experiment],
        map_file: str,
        model_path: Optional[str]
    ) -> Iterator[Tuple[str]]:
        print(f'Running Anya for {self.scenario}')
        
        try:
            anya = Search(ExpansionPolicy(f'{self.MAP_DIR}/{map_file}'),
                          model_path=model_path,
                          id_map=map_file.replace('.map', '') if model_path is not None else None)

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
                   f'{exp.upper_bound};{cost};{exp.map_file}')

    def run_astar(
        self,
        experiments: List[Experiment],
        map_file: str,
        model_path: Optional[str]
    ) -> Iterator[str]:
        print(f'Running A-star for {self.scenario}')

        try:
            astar = AStar(BitpackedGridExpansionPolicy(f'{self.MAP_DIR}/{map_file}'),
                          model_path=model_path,
                          id_map=map_file.replace('.map', '') if model_path is not None else None)

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
    def get_file_path(alg: str, map_file: str, model_path: Optional[str]) -> str:
        """Save results to a determined path within <RESULT_DIR>.
        If computing paths without a model, the final path should be within root folder of <RESULT_DIR>.
        On the other hand, if using a model, the real path should consider the first two levels
        of `model_path`, that is <RESULT_DIR>/<MODEL_PATH>/<ALG>_<MAP_FILE>.txt
        e.g.
        Computing path using ANYA on London_0_512.map
        model_path is <ai.MODEL_DIR>/anya_dnn/20230628_150610/final_model.h5
        f_path should be <RESULT_DIR>/anya_dnn/20230628_150610/anya_London_0_512.txt
        """
        f_name = f"{alg}_{map_file.replace('.map', '.txt')}"

        if model_path is not None:
            path = ScenarioRunner.create_dirs_if_missing(model_path)
            f_path = f'{path}\\{f_name}'
        else:
            f_path = f'{ScenarioRunner.RESULT_DIR}\\{f_name}'
        return f_path
    
    @staticmethod
    def create_dirs_if_missing(model_path: str) -> str:
        path = os.path.abspath(model_path).split('\\')[-3:-1]
        path = '{}\\{}\\{}'.format(ScenarioRunner.RESULT_DIR, *path)
        if not os.path.exists(path):
            os.makedirs(path)
        return path


def main():
    parser = ArgumentParser()
    parser.add_argument('-scen', '--scenario',
                        required=True,
                        help='Map scenario to run experiments')
    
    parser.add_argument('-v', '--verbose',
                        action='store_true', 
                        help='Verbose output')

    parser.add_argument('-alg', '--algorithm',
                        type=lambda arg: arg.lower(),
                        choices=['anya', 'astar'],
                        required=True,
                        help='Possible algorithms: anya, astar (case-insensitive)')
    
    parser.add_argument('-m_path', '--model_path',
                        help='Path for trained model for the algorithm to compute paths')
    
    args = parser.parse_args()
    runner = ScenarioRunner(args.scenario, args.verbose)
    runner.run(args.algorithm, args.model_path)


if __name__ == '__main__':
    main()
