from traceback import format_exc
from argparse import ArgumentParser
from experiment_loader import ExperimentLoader
from search import Search
from expansion_policy import ExpansionPolicy
from micro_benchmark import MicroBenchmark
from node import Node
from interval import Interval


class ScenarioRunner:
    MAP_DIR = 'maps'
    RESULT_DIR = 'results'
    VERBOSE = False
    EXP_HEADER = 'exp;path_found;alg;wallt_micro;runt_micro;'+ \
        'expanded;generated;heapops;start;target;gridcost;realcost;map'

    @staticmethod
    def run_anya(scenario_file_path: str) -> None:
        if ScenarioRunner.VERBOSE:
            print(f'Running Anya for {scenario_file_path}')
    
        exp_loader = ExperimentLoader()

        try:
            experiments = exp_loader.load_experiments(f'{ScenarioRunner.MAP_DIR}/{scenario_file_path}')
            if len(experiments) == 0:
                print('No experiments to run; finishing.')
                return

            map_file = experiments[0].map_file
            anya = Search(ExpansionPolicy(f'{ScenarioRunner.MAP_DIR}/{map_file}'))
            if ScenarioRunner.VERBOSE:
                anya.VERBOSE = ScenarioRunner.VERBOSE
        except Exception as e:
            print(format_exc())
            return

        exp_runner = MicroBenchmark(anya)
        res_file = open(f"{ScenarioRunner.RESULT_DIR}/{map_file.replace('.map', '.txt')}", 'w')
        
        print(ScenarioRunner.EXP_HEADER)
        print(ScenarioRunner.EXP_HEADER, file=res_file)

        start = Node.from_points(Interval(0, 0, 0), 0, 0)
        target = Node.from_points(Interval(0, 0, 0), 0, 0)

        anya.mb_start_ = start
        anya.mb_target_ = target

        for exp in experiments:            
            start.root.set_location(exp.start_x, exp.start_y)
            start.interval.init(exp.start_x, exp.start_x, exp.start_y)
            
            target.root.set_location(exp.end_x, exp.end_y)
            target.interval.init(exp.end_x, exp.end_x, exp.end_y)
                    
            wallt_micro = exp_runner.benchmark(1)
            cost = anya.mb_cost_
            duration = exp_runner.avg_time + 0.5

            res_exp = (
                f'{exp.title};{anya.path_found};AnyaSearch;{wallt_micro};{duration};'
                f'{anya.expanded};{anya.generated};{anya.heap_ops};'
                f'({exp.start_x},{exp.start_y});({exp.end_x},{exp.end_y});'
                f'{exp.upper_bound};{cost};{exp.map_file}'
            )
            print(res_exp, file=res_file)
            print(res_exp)
        res_file.close()


def main():
    parser = ArgumentParser()
    parser.add_argument('-scen', '--scenario', 
                        help='Map scenario to run experiments', required=True)
    
    parser.add_argument('-v', '--verbose', action='store_true', 
                        help='Verbose output')
    
    args = parser.parse_args()
    if args.verbose:
        ScenarioRunner.VERBOSE = True
    ScenarioRunner.run_anya(args.scenario)


if __name__ == '__main__':
    main()
