#!/usr/bin/env python3
"""Convenience wrapper for the evaluation suite."""
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from evaluation.runner import run_all
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--subset", choices=["all", "provided", "generated"], default="all")
    parser.add_argument("--id", type=int, help="Run single scenario by ID")
    parser.add_argument("--judge", action="store_true", help="Enable LLM-as-judge evaluation")
    parser.add_argument("--from-id", type=int, default=0, help="Resume from scenario ID")
    args = parser.parse_args()

    if args.id:
        from evaluation.scenarios import ALL_SCENARIOS
        from src.agent import PolicyAgent
        from evaluation.runner import run_scenario
        scenario = next((s for s in ALL_SCENARIOS if s["id"] == args.id), None)
        if not scenario:
            print(f"Scenario {args.id} not found.")
        else:
            agent = PolicyAgent(verbose=True)
            judge = None
            if args.judge:
                from evaluation.judge import PolicyJudge
                judge = PolicyJudge()
            result = run_scenario(agent, scenario, verbose=True, judge=judge)
            print(f"\nFull response:\n{result.get('response_preview', '')}")
    else:
        run_all(verbose=args.verbose, subset=args.subset, use_judge=args.judge, from_id=args.from_id)
