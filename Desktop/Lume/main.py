#!/usr/bin/env python3
"""
Interactive CLI for the Gaggia IT Helpdesk Policy Agent.

Usage:
    python main.py --tier blue --emp EMP-2011 --dept Engineering
    python main.py  (prompted for context)
"""
import argparse
import sys
from pathlib import Path

# Load env from .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from src.agent import PolicyAgent
from src.models import TrustTier, UserContext, Message


BANNER = """
╔═══════════════════════════════════════════════════════════════╗
║         Gaggia Inc. IT Helpdesk — Policy Agent v1.0          ║
║   Type 'exit' to quit | 'log' to view last decision log       ║
╚═══════════════════════════════════════════════════════════════╝
"""

TIER_MAP = {"blue": TrustTier.BLUE, "red": TrustTier.RED, "grey": TrustTier.GREY}


def get_user_context_interactive() -> UserContext:
    print("\nSet up your user context:")
    emp_id = input("  Employee ID (e.g., EMP-2011): ").strip() or "EMP-2011"
    tier_raw = input("  Trust tier (blue/red/grey) [blue]: ").strip().lower() or "blue"
    tier = TIER_MAP.get(tier_raw, TrustTier.BLUE)
    dept = input("  Department [Engineering]: ").strip() or "Engineering"
    is_mgr = input("  Are you a verified manager? (y/n) [n]: ").strip().lower() == "y"
    return UserContext(
        employee_id=emp_id,
        trust_tier=tier,
        department=dept,
        is_manager=is_mgr,
        is_verified_manager=is_mgr,
    )


def main():
    parser = argparse.ArgumentParser(description="Gaggia IT Helpdesk Policy Agent")
    parser.add_argument("--tier", choices=["blue", "red", "grey"], default=None)
    parser.add_argument("--emp", default=None, help="Employee ID")
    parser.add_argument("--dept", default=None, help="Department")
    parser.add_argument("--manager", action="store_true", help="Mark as verified manager")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    print(BANNER)

    if args.tier and args.emp:
        user_context = UserContext(
            employee_id=args.emp,
            trust_tier=TIER_MAP[args.tier],
            department=args.dept or "Unknown",
            is_manager=args.manager,
            is_verified_manager=args.manager,
        )
    else:
        user_context = get_user_context_interactive()

    print(f"\nSession started as: {user_context}")

    try:
        agent = PolicyAgent(verbose=args.verbose)
    except EnvironmentError as e:
        print(f"\nError: {e}")
        print("Set ANTHROPIC_API_KEY in your .env file or environment.")
        sys.exit(1)

    history: list[Message] = []
    import uuid
    conv_id = str(uuid.uuid4())[:8]

    print("\nReady. Ask your IT question:\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit", "bye"):
            print("Goodbye.")
            break
        if user_input.lower() == "log":
            logs = agent.logger.read_session_logs()
            if logs:
                agent.logger.print_summary(logs[-1])
            else:
                print("No logs yet.")
            continue

        response, log_id = agent.chat(
            user_input, user_context, history=history, conversation_id=conv_id
        )

        print(f"\nAgent: {response}\n")

        # Update history for multi-turn awareness
        history.append(Message(role="user", content=user_input))
        history.append(Message(role="assistant", content=response))


if __name__ == "__main__":
    main()
