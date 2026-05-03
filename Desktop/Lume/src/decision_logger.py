"""
Decision logging for the Gaggia IT Helpdesk Agent.

Every request produces a JSON log entry capturing:
- Request context (user, trust tier, message)
- Policy sections retrieved and their relevance scores
- Action decision and reasoning
- Tool calls made (inputs + filtered outputs)
- Policy sections cited
- Whether prompt injection was detected
- Final response text
"""
import json
import uuid
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from .models import DecisionLog, UserContext, PolicySection, ToolCall


class DecisionLogger:
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self._session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._log_file = self.log_dir / f"session_{self._session_id}.jsonl"
        self._pending: dict[str, dict] = {}

    def start_request(
        self,
        conversation_id: str,
        turn_number: int,
        user_message: str,
        user_context: UserContext,
    ) -> str:
        log_id = str(uuid.uuid4())[:8]
        self._pending[log_id] = {
            "log_id": log_id,
            "conversation_id": conversation_id,
            "turn_number": turn_number,
            "timestamp": datetime.utcnow().isoformat(),
            "user_message": user_message,
            "user": {
                "employee_id": user_context.employee_id,
                "trust_tier": user_context.trust_tier.value,
                "department": user_context.department,
                "role": user_context.role,
                "is_manager": user_context.is_manager,
            },
            "retrieved_sections": [],
            "action": None,
            "reasoning": None,
            "tool_calls": [],
            "policy_sections_cited": [],
            "response": None,
            "prompt_injection_detected": False,
            "elapsed_ms": None,
            "token_usage": {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0},
            "_start_time": time.time(),
        }
        return log_id

    def log_retrieved_sections(
        self, log_id: str, sections: list[PolicySection]
    ):
        entry = self._pending.get(log_id, {})
        entry["retrieved_sections"] = [
            {
                "section_id": s.section_id,
                "title": s.title,
                "score": round(s.score, 4),
                "content_preview": s.content[:200],
            }
            for s in sections
        ]

    def log_tool_call(
        self,
        log_id: str,
        tool_name: str,
        inputs: dict,
        raw_output: dict,
        filtered_output: dict,
    ):
        entry = self._pending.get(log_id, {})
        # Redact the temp password from logs for security hygiene
        safe_raw = dict(raw_output)
        if "temp_password" in safe_raw:
            safe_raw["temp_password"] = "***REDACTED***"
        entry["tool_calls"].append(
            {
                "tool_name": tool_name,
                "inputs": inputs,
                "raw_output": safe_raw,
                "filtered_output": filtered_output,
            }
        )

    def log_prompt_injection(self, log_id: str):
        entry = self._pending.get(log_id, {})
        entry["prompt_injection_detected"] = True

    def log_token_usage(self, log_id: str, input_tokens: int, output_tokens: int):
        entry = self._pending.get(log_id, {})
        usage = entry.setdefault("token_usage", {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0})
        usage["input_tokens"] += input_tokens
        usage["output_tokens"] += output_tokens
        usage["total_tokens"] += input_tokens + output_tokens

    def finalize(
        self,
        log_id: str,
        action: str,
        reasoning: str,
        policy_sections_cited: list[str],
        response: str,
    ):
        entry = self._pending.get(log_id)
        if not entry:
            return

        entry["action"] = action
        entry["reasoning"] = reasoning
        entry["policy_sections_cited"] = policy_sections_cited
        entry["response"] = response
        entry["elapsed_ms"] = round((time.time() - entry.pop("_start_time")) * 1000)

        with open(self._log_file, "a") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        del self._pending[log_id]

    def read_session_logs(self) -> list[dict]:
        if not self._log_file.exists():
            return []
        logs = []
        with open(self._log_file) as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        logs.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
        return logs

    def print_summary(self, log_entry: dict, use_color: bool = True):
        """Pretty-print a single log entry to stdout."""
        tier_colors = {"blue": "\033[94m", "red": "\033[91m", "grey": "\033[90m"}
        action_colors = {
            "allow": "\033[92m",
            "deny": "\033[91m",
            "escalate": "\033[93m",
            "clarify": "\033[93m",
            "general": "\033[96m",
        }
        reset = "\033[0m" if use_color else ""

        tier = log_entry["user"]["trust_tier"]
        action = log_entry.get("action", "unknown")
        tc = tier_colors.get(tier, "") if use_color else ""
        ac = action_colors.get(action, "") if use_color else ""

        print(f"\n{'='*70}")
        print(f"[{log_entry['log_id']}] Turn {log_entry['turn_number']} | "
              f"{tc}{tier.upper()}{reset} | {ac}{action.upper()}{reset}")
        print(f"User: {log_entry['user']['employee_id']} ({log_entry['user']['department']})")
        print(f"Message: {log_entry['user_message'][:120]}")
        if log_entry.get("prompt_injection_detected"):
            print(f"\033[91m⚠ PROMPT INJECTION DETECTED{reset}")
        print(f"\nRetrieved sections: {[s['section_id'] for s in log_entry['retrieved_sections']]}")
        print(f"Tools called: {[t['tool_name'] for t in log_entry['tool_calls']]}")
        print(f"Sections cited: {log_entry.get('policy_sections_cited', [])}")
        print(f"Elapsed: {log_entry.get('elapsed_ms')}ms")
