import os
from pathlib import Path
from openevolve import OpenEvolve

curr_dir = Path(os.path.realpath(os.path.dirname(__file__)))

# TODO: when we grab a task to run from KernelBench, must wrap it with EVOLVE blocks!
init_program = curr_dir / "initial_program.py"
# TODO: must have the evaluator read from a file to determine which task number we are dealing with
eval_file = curr_dir / "evaluator.py"
config_path = curr_dir / "config.yaml"
# create a new run directory (based on current yyyy-mm-dd-... and place each individual task run in here)
output_dir = curr_dir / "openevolve_output_level_0_task_5_trial_2"

runner = OpenEvolve(init_program, eval_file, config_path=config_path, output_dir=output_dir)

runner.run()
