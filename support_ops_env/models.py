from pydantic import BaseModel, Field
from typing import Optional, List


# ── Action ──────────────────────────────────────────────────────────────────
class SupportAction(BaseModel):
    category: Optional[str] = Field(
        None,
        description="Ticket category: billing/technical/account/shipping/general"
    )
    priority: Optional[str] = Field(
        None,
        description="Priority level: P1/P2/P3/P4"
    )
    response_text: Optional[str] = Field(
        None,
        description="The drafted response to send to the customer"
    )
    resolution_decision: Optional[str] = Field(
        None,
        description="Decision: resolve/escalate/request_info"
    )


# ── Observation ──────────────────────────────────────────────────────────────
class SupportObservation(BaseModel):
    ticket_id: str
    ticket_subject: str
    ticket_body: str
    customer_history: List[str] = Field(default_factory=list)
    knowledge_base_hints: List[str] = Field(default_factory=list)
    sla_hours_remaining: Optional[float] = None
    previous_responses: List[str] = Field(default_factory=list)
    task_name: str
    step_number: int
    instructions: str


# ── Reward ───────────────────────────────────────────────────────────────────
class SupportReward(BaseModel):
    total: float = Field(description="Total reward 0.0 to 1.0")
    category_score: float = 0.0
    priority_score: float = 0.0
    response_score: float = 0.0
    resolution_score: float = 0.0
    penalty: float = 0.0
    breakdown: str = ""