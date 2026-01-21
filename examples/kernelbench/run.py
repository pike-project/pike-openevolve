import os
import asyncio
import shutil
import json
import yaml
from pathlib import Path
from datetime import datetime
from openevolve import OpenEvolve
import argparse

curr_dir = Path(os.path.realpath(os.path.dirname(__file__)))

async def run_task(pike_dir: Path, run_dir: Path, level: str, task: int, eval_port: int, base_config_path: Path, max_fix_attempts: int):
    level_dir = pike_dir / "KernelBench" / f"level{level}"

    task_filename = None

    for filename in os.listdir(level_dir):
        if not filename.endswith(".py"):
            continue

        file_task = int(filename.split("_")[0])

        if task == file_task:
            task_filename = filename
            break

    if task_filename is None:
        print(f"Warning: task not found, skipping - {task}")
        return
        # raise Exception(f"Task not found: {task}")
    
    task_path = level_dir / task_filename

    with open(task_path) as f:
        task_code = f.read()

    tasks_dir = run_dir / "tasks"
    evolve_dir = tasks_dir / f"task{task}"
    os.makedirs(evolve_dir, exist_ok=True)

    config_path = evolve_dir / "config.yaml"

    with open(base_config_path, "r") as f:
        config = yaml.safe_load(f)

    config["max_fix_attempts"] = max_fix_attempts

    with open(config_path, "w") as f:
        yaml.safe_dump(config, f, sort_keys=False)

    # when we grab a task to run from KernelBench, must wrap it with EVOLVE blocks!
    init_program = evolve_dir / "initial_program.py"

    with open(init_program, "w") as f:
        f.write("# EVOLVE-BLOCK-START\n")
        f.write(task_code)
        f.write("\n# EVOLVE-BLOCK-END\n")

    # must have the evaluator read from a file to determine which task number we are dealing with
    base_eval_file = curr_dir / "evaluator.py"
    eval_file = evolve_dir / "evaluator.py"
    shutil.copy(base_eval_file, eval_file)

    eval_config_path = evolve_dir / "eval_config.json"

    eval_config = {
        "level": level,
        "task": task,
        "port": eval_port,
    }

    with open(eval_config_path, "w") as f:
        json.dump(eval_config, f)

    # create a new run directory (based on current yyyy-mm-dd-... and place each individual task run in here)
    output_dir = evolve_dir / "output"

    runner = OpenEvolve(init_program, eval_file, config_path=config_path, output_dir=output_dir)

    await runner.run()

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pike-dir", type=str, required=True, help="Path to the root of your local PIKE directory")
    parser.add_argument("--level", type=str, required=True, help="KernelBench level")
    parser.add_argument("--task-start", type=int, required=True, help="Task range start, inclusive")
    parser.add_argument("--task-end", type=int, required=True, help="Task range end, inclusive")
    parser.add_argument("--eval-port", type=int, required=False, default=8000, help="Port where evaluation server is running")
    parser.add_argument("--run-dir", type=str, required=False, help="Directory for run results output")
    parser.add_argument("--max-fix-attempts", type=int, required=False, default=0, help="Error Fixing Agent max attempts allowed")
    args = parser.parse_args()

    level_str = args.level
    task_start = args.task_start
    task_end = args.task_end

    pike_dir = Path(args.pike_dir)

    if args.run_dir is None:
        timestamp_str = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        run_dir = curr_dir / "openevolve_output_runs" / timestamp_str
    else:
        run_dir = Path(args.run_dir)

    os.makedirs(run_dir, exist_ok=True)

    base_config_path = curr_dir / "config.yaml"

    for task in range(task_start, task_end + 1):
        await run_task(pike_dir, run_dir, level_str, task, args.eval_port, base_config_path, args.max_fix_attempts)

if __name__ == "__main__":
    asyncio.run(main())
