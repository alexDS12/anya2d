import traceback
from re import split
from experiment import Experiment
from fileinput import input
from typing import List


class ExperimentLoader:
    def load_experiments(self, map_file: str) -> List[Experiment]:
        exp_list = []

        try:
            with input(map_file, mode='r') as file:
                _, exp_line = [next(file).strip() for _ in range(2)]

                experiment_counter = 0
                while exp_line is not None:
                    exp_tokens = split('\s{1,}', exp_line)
                    if len(exp_tokens) != 9:
                        exp_line = next(file).strip()
                        continue
                    experiment_counter += 1

                    try:                        
                        exp = Experiment(
                            title       = f'Experiment #{experiment_counter}',
                            map_file    = exp_tokens[1],
                            x_size      = int(exp_tokens[2]),
                            y_size      = int(exp_tokens[3]),
                            start_x     = int(exp_tokens[4]),
                            start_y     = int(exp_tokens[5]),
                            end_x       = int(exp_tokens[6]),
                            end_y       = int(exp_tokens[7]),
                            upper_bound = float(exp_tokens[8])
                        )
                    except Exception as e:
                        print(traceback.format_exc())
                        exp_line = next(file).strip()
                        continue
                    
                    exp_list.append(exp)
                    
                    try:
                        exp_line = next(file).strip()
                    except StopIteration as e:
                        # reached EOF
                        break
            return exp_list
        except Exception as e:
            raise Exception(traceback.format_exc())
