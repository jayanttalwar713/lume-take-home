"""
Evaluation runner — processes all test scenarios through the policy agent
and produces a structured results report.

Pass --judge to also run the LLM-as-judge on each scenario.
Pass --from-id N to resume from scenario N (skips earlier ones).
"""
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent import PolicyAgent
from src.models import Message
from evaluation.scenarios import ALL_SCENARIOS, PROVIDED_SCENARIOS, GENERATED_SCENARIOS


RESULT_FILE = Path(__file__).parent.parent / "logs" / "eval_results.json"

# ANSI colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"


def action_match(expected: str, actual: str) -> bool:
    """
    Flexible action matching.
    - 'deny' and 'escalate' are both acceptable for clearly prohibited actions.
    - 'allow' requires exact match.
    """
    if expected == actual:
        return True
    # escalate implies deny for prohibited actions
    if expected in ("deny", "escalate") and actual in ("deny", "escalate"):
        return True
    return False


def run_scenario(agent: PolicyAgent, scenario: dict, verbose: bool = False, judge=None) -> dict:
    msg = scenario["message"]
    ctx = scenario["user_context"]

    print(f"\n{'─'*60}")
    tier_sym = {"blue": "🔵", "red": "🔴", "grey": "⚫"}[ctx.trust_tier.value]
    print(f"[{scenario['id']:02d}] {tier_sym} {BOLD}{scenario['name']}{RESET}")
    print(f"  User: {ctx.employee_id} ({ctx.department}) | Tier: {ctx.trust_tier.value}")
    print(f"  Message: {msg[:100]}")

    start = time.time()
    history = scenario.get("history", [])

    # Retry loop — handles provider rate limits automatically
    max_retries = 4
    for attempt in range(max_retries):
        try:
            response, log_id = agent.chat(
                msg, ctx, history=history, conversation_id=f"eval-{scenario['id']}"
            )
            break  # success
        except Exception as e:
            err_str = str(e)
            # Check for rate limit and parse the suggested wait time
            if "429" in err_str or "rate_limit" in err_str.lower():
                match = re.search(r"try again in (\d+)m([\d.]+)s", err_str)
                wait = (int(match.group(1)) * 60 + float(match.group(2)) + 5) if match else 65
                if attempt < max_retries - 1:
                    print(f"  {YELLOW}Rate limited. Waiting {wait:.0f}s then retrying...{RESET}")
                    time.sleep(wait)
                    continue
            # Non-rate-limit error or out of retries
            elapsed = round((time.time() - start) * 1000)
            print(f"  {RED}ERROR: {e}{RESET}")
            return {
                "id": scenario["id"],
                "category": scenario["category"],
                "name": scenario["name"],
                "pass": False,
                "error": str(e),
            }
    else:
        # All retries exhausted
        return {
            "id": scenario["id"],
            "category": scenario["category"],
            "name": scenario["name"],
            "pass": False,
            "error": "Max retries exceeded (rate limit)",
        }

    try:
        elapsed = round((time.time() - start) * 1000)

        # Parse footer from response
        actual_action, cited_sections = agent._parse_footer(response)
        expected_action = scenario["expected_action"]
        match = action_match(expected_action, actual_action)

        status = f"{GREEN}PASS{RESET}" if match else f"{RED}FAIL{RESET}"
        print(f"  Expected: {expected_action} | Got: {actual_action} → {status}")
        print(f"  Cited sections: {cited_sections}")
        if verbose:
            print(f"\n  Response:\n  {response[:400]}\n")

        result = {
            "id": scenario["id"],
            "category": scenario["category"],
            "name": scenario["name"],
            "pass": match,
            "expected_action": expected_action,
            "actual_action": actual_action,
            "cited_sections": cited_sections,
            "response_preview": response[:300],
            "elapsed_ms": elapsed,
            "log_id": log_id,
        }

        # Optional LLM-as-judge
        if judge is not None:
            judge_result = judge.evaluate(scenario, response, actual_action, cited_sections)
            result["judge"] = judge_result
            judge_sym = f"{GREEN}✓{RESET}" if judge_result["pass"] else f"{RED}✗{RESET}"
            print(f"  Judge: {judge_sym} — {judge_result['reasoning']}")
            if judge_result.get("data_leaked"):
                print(f"  {RED}⚠ JUDGE: Potential data leak detected{RESET}")
    except Exception as e:
        print(f"  {RED}ERROR: {e}{RESET}")
        result = {
            "id": scenario["id"],
            "category": scenario["category"],
            "name": scenario["name"],
            "pass": False,
            "error": str(e),
        }

    return result


def run_all(scenarios=None, verbose: bool = False, subset: str = "all", use_judge: bool = False, from_id: int = 0) -> list[dict]:
    if scenarios is None:
        if subset == "provided":
            scenarios = PROVIDED_SCENARIOS
        elif subset == "generated":
            scenarios = GENERATED_SCENARIOS
        else:
            scenarios = ALL_SCENARIOS

    if from_id:
        scenarios = [s for s in scenarios if s["id"] >= from_id]

    agent = PolicyAgent(verbose=verbose)
    judge = None
    if use_judge:
        from evaluation.judge import PolicyJudge
        judge = PolicyJudge()

    results = []

    print(f"\n{BOLD}{'='*60}")
    print(f"Gaggia IT Helpdesk Agent — Evaluation Suite")
    print(f"Model: {agent.model}")
    print(f"Scenarios: {len(scenarios)}")
    if use_judge:
        print(f"LLM-as-judge: enabled ({judge.model})")
    print(f"{'='*60}{RESET}")

    for scenario in scenarios:
        result = run_scenario(agent, scenario, verbose=verbose, judge=judge)
        results.append(result)

    # Summary
    total = len(results)
    passed = sum(1 for r in results if r.get("pass"))
    errors = sum(1 for r in results if "error" in r)

    print(f"\n{BOLD}{'='*60}")
    print(f"RESULTS: {GREEN}{passed}/{total} passed{RESET}")
    if errors:
        print(f"  {RED}{errors} errors{RESET}")

    # By category
    categories = sorted(set(r["category"] for r in results))
    for cat in categories:
        cat_results = [r for r in results if r["category"] == cat]
        cat_pass = sum(1 for r in cat_results if r.get("pass"))
        print(f"  {cat}: {cat_pass}/{len(cat_results)}")

    # Judge summary
    judge_results = [r for r in results if "judge" in r]
    if judge_results:
        judge_pass = sum(1 for r in judge_results if r["judge"].get("pass"))
        leaks = sum(1 for r in judge_results if r["judge"].get("data_leaked"))
        print(f"\nLLM-as-judge: {GREEN}{judge_pass}/{len(judge_results)} passed{RESET}")
        if leaks:
            print(f"  {RED}⚠ {leaks} potential data leak(s) detected{RESET}")

    print(f"{'='*60}{RESET}\n")

    # Save results
    RESULT_FILE.parent.mkdir(exist_ok=True)
    with open(RESULT_FILE, "w") as f:
        json.dump(
            {
                "summary": {
                    "total": total,
                    "passed": passed,
                    "failed": total - passed - errors,
                    "errors": errors,
                    "pass_rate": round(passed / total * 100, 1) if total else 0,
                },
                "by_category": {
                    cat: {
                        "passed": sum(1 for r in results if r["category"] == cat and r.get("pass")),
                        "total": sum(1 for r in results if r["category"] == cat),
                    }
                    for cat in categories
                },
                "results": results,
            },
            f,
            indent=2,
        )
    print(f"Full results saved to: {RESULT_FILE}")
    return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--subset", choices=["all", "provided", "generated"], default="all")
    parser.add_argument("--id", type=int, help="Run a single scenario by ID")
    parser.add_argument("--judge", action="store_true", help="Enable LLM-as-judge evaluation")
    parser.add_argument("--from-id", type=int, default=0, help="Resume from scenario ID (skip earlier ones)")
    args = parser.parse_args()

    if args.id:
        scenario = next((s for s in ALL_SCENARIOS if s["id"] == args.id), None)
        if not scenario:
            print(f"Scenario {args.id} not found.")
            sys.exit(1)
        agent = PolicyAgent(verbose=True)
        judge = None
        if args.judge:
            from evaluation.judge import PolicyJudge
            judge = PolicyJudge()
        run_scenario(agent, scenario, verbose=True, judge=judge)
    else:
        run_all(verbose=args.verbose, subset=args.subset, use_judge=args.judge, from_id=args.from_id)
