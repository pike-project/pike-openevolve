"""
Evaluator for the function minimization example
"""

import time
import traceback
from openevolve.evaluation_result import EvaluationResult
import requests
import os
import json
from pathlib import Path
from time import sleep

curr_dir = Path(os.path.realpath(os.path.dirname(__file__)))


def evaluate(program_path):
    """
    Evaluate the program

    Args:
        program_path: Path to the program file

    Returns:
        Dictionary of metrics
    """

    try:
        # read the program file and send it to the evaluator

        with open(curr_dir / "eval_config.json") as f:
            eval_config = json.load(f)

        eval_port = eval_config["port"]
        base_url = f"http://localhost:{eval_port}"

        level = eval_config["level"]
        task = eval_config["task"]

        with open(program_path) as f:
            code = f.read()

        submit_path = "/submit"
        submit_params = {
            "code": code,
            "level": level,
            "task": task
        }

        res = requests.post(f"{base_url}{submit_path}", json=submit_params)
        res.raise_for_status()

        eval_id = res.text

        poll_path = "/poll"
        poll_params = {"id": eval_id}

        poll_timeout = 3600
        poll_start = time.time()
        while True:
            if time.time() - poll_start > poll_timeout:
                return EvaluationResult(
                    metrics={
                        "combined_score": 0.0,
                        "error": "Poll timeout",
                    },
                    artifacts={}
                )
            res = requests.get(f"{base_url}{poll_path}", params=poll_params)
            res.raise_for_status()
            data = res.json()
            if data is not None:
                break

            sleep(1)

        artifacts = data

        try:
            runtime = data["results"]["eval_results"]["runtime"]
        except Exception as e:
            return EvaluationResult(
                metrics={
                    "combined_score": 0.0,
                    "error": "Eval failed",
                },
                artifacts=artifacts
            )

        return EvaluationResult(
            metrics={
                "combined_score": 1 / runtime,
                "runtime": runtime,
            },
            artifacts=artifacts
        )
    except Exception as e:
        print(f"Evaluation failed completely: {str(e)}")
        print(traceback.format_exc())
        
        # Create error artifacts
        error_artifacts = {
            "error_type": type(e).__name__,
            "error_message": str(e),
            "full_traceback": traceback.format_exc(),
            "suggestion": "Check for syntax errors or missing imports in the generated code"
        }
        
        return EvaluationResult(
            metrics={
                "value_score": 0.0,
                "distance_score": 0.0,
                "reliability_score": 0.0,
                "combined_score": 0.0,
                "error": str(e),
            },
            artifacts=error_artifacts
        )
