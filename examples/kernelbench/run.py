import os
import asyncio
import shutil
import json
from pathlib import Path
from datetime import datetime
from openevolve import OpenEvolve

curr_dir = Path(os.path.realpath(os.path.dirname(__file__)))

async def run_task(run_dir: Path, level: str, task: int, eval_file: Path, config_path: Path):
    kernel_bench_dir = Path("/pscratch/sd/k/kir/llm/KernelBench")
    level_dir = kernel_bench_dir / "KernelBench" / f"level{level}"

    task_filename = None

    for filename in os.listdir(level_dir):
        if not filename.endswith(".py"):
            continue

        file_task = int(filename.split("_")[0])

        if task == file_task:
            task_filename = filename
            break

    if task_filename is None:
        raise Exception(f"Task not found: {task}")
    
    task_path = level_dir / task_filename

    with open(task_path) as f:
        task_code = f.read()

    evolve_dir = run_dir / f"task{task}"
    os.makedirs(evolve_dir, exist_ok=True)

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
    }

    with open(eval_config_path, "w") as f:
        json.dump(eval_config, f)

    # create a new run directory (based on current yyyy-mm-dd-... and place each individual task run in here)
    output_dir = evolve_dir / "output"

    runner = OpenEvolve(init_program, eval_file, config_path=config_path, output_dir=output_dir)

    await runner.run()

async def main():
    level_str = "0"

    timestamp_str = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    run_dir = "openevolve_output_runs" / timestamp_str
    os.makedirs(run_dir, exist_ok=True)

    base_config_path = curr_dir / "config.yaml"
    config_path = run_dir / "config.yaml"
    shutil.copy(base_config_path, config_path)

    for task in range(1, 3):
        await run_task(run_dir, level_str, task, config_path)

if __name__ == "__main__":
    asyncio.run(main())
