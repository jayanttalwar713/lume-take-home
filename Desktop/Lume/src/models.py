from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class TrustTier(str, Enum):
    BLUE = "blue"
    RED = "red"
    GREY = "grey"


@dataclass
class UserContext:
    employee_id: str
    trust_tier: TrustTier
    department: Optional[str] = None
    role: Optional[str] = None
    is_manager: bool = False
    is_verified_manager: bool = False

    def __str__(self) -> str:
        tier_emoji = {"blue": "🔵", "red": "🔴", "grey": "⚫"}[self.trust_tier.value]
        return (
            f"{tier_emoji} {self.employee_id} | {self.department or 'unknown dept'} | "
            f"{'manager ' if self.is_manager else ''}{self.trust_tier.value}"
        )


@dataclass
class Message:
    role: str  # "user" or "assistant"
    content: str


@dataclass
class PolicySection:
    section_id: str
    title: str
    content: str
    score: float = 0.0


@dataclass
class ToolCall:
    tool_name: str
    inputs: dict
    raw_output: dict
    filtered_output: dict


@dataclass
class DecisionLog:
    log_id: str
    conversation_id: str
    turn_number: int
    user_message: str
    user_context: UserContext
    retrieved_sections: list[PolicySection]
    action: str  # "allow" | "deny" | "escalate" | "clarify" | "general"
    reasoning: str
    tool_calls: list[ToolCall]
    policy_sections_cited: list[str]
    response: str
    prompt_injection_detected: bool = False
