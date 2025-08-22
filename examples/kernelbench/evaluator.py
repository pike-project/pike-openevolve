"""
Evaluator for the function minimization example
"""

import importlib.util
import numpy as np
import time
import concurrent.futures
import traceback
import signal
import random
from openevolve.evaluation_result import EvaluationResult


def run_with_timeout(func, args=(), kwargs={}, timeout_seconds=5):
    """
    Run a function with a timeout using concurrent.futures

    Args:
        func: Function to run
        args: Arguments to pass to the function
        kwargs: Keyword arguments to pass to the function
        timeout_seconds: Timeout in seconds

    Returns:
        Result of the function or raises TimeoutError
    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(func, *args, **kwargs)
        try:
            result = future.result(timeout=timeout_seconds)
            return result
        except concurrent.futures.TimeoutError:
            raise TimeoutError(f"Function timed out after {timeout_seconds} seconds")


def evaluate(program_path):
    """
    Evaluate the program

    Args:
        program_path: Path to the program file

    Returns:
        Dictionary of metrics
    """

    try:
        # TODO: read the program file and set it to the evaluator

        success_count = 1

        # If all trials failed, return zero scores
        if success_count == 0:
            error_artifacts = {
                # "error_type": "AllTrialsFailed",
                # "error_message": f"All {num_trials} trials failed - common issues: timeouts, crashes, or invalid return values",
                # "suggestion": "Check for infinite loops, ensure function returns (x, y) or (x, y, value), and verify algorithm terminates within time limit"
            }
            
            return EvaluationResult(
                metrics={
                    "value_score": 0.0,
                    "distance_score": 0.0,
                    "reliability_score": 0.0,
                    "combined_score": 0.0,
                    "error": "All trials failed",
                },
                artifacts=error_artifacts
            )

        # Add artifacts for successful runs
        artifacts = {
            # "convergence_info": f"Converged in {num_trials} trials with {success_count} successes",
            # "best_position": f"Final position: x={x_values[-1]:.4f}, y={y_values[-1]:.4f}" if x_values else "No successful trials",
            # "average_distance_to_global": f"{avg_distance:.4f}",
            # "search_efficiency": f"Success rate: {reliability_score:.2%}"
        }

        return EvaluationResult(
            metrics={
                # "value_score": value_score,
                # "distance_score": distance_score,
                # "reliability_score": reliability_score,
                # "combined_score": combined_score,
                "combined_score": random.random()
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
