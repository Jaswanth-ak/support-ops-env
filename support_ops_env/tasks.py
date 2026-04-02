from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Task:
    name: str
    difficulty: str
    ticket_id: str
    ticket_subject: str
    ticket_body: str
    correct_category: str
    correct_priority: str
    knowledge_base: List[str]
    correct_decision: Optional[str]
    sla_hours: float
    customer_history: List[str]
    instructions: str


TASKS: List[Task] = [

    # ── TASK 1: Easy — Ticket Triage ────────────────────────────────────────
    Task(
        name="ticket_triage",
        difficulty="easy",
        ticket_id="TKT-001",
        ticket_subject="Cannot login to my account",
        ticket_body=(
            "Hi, I've been trying to log into my account for the past 2 hours "
            "but keep getting 'Invalid credentials'. I've tried resetting my "
            "password twice but still can't get in. My email is user@example.com. "
            "Please help urgently as I need to access my files for a meeting today."
        ),
        correct_category="account",
        correct_priority="P2",
        knowledge_base=[
            "Account lockouts occur after 5 failed login attempts.",
            "Password reset links expire after 30 minutes.",
            "Contact account team to manually unlock: accounts@support.com"
        ],
        correct_decision="resolve",
        sla_hours=4.0,
        customer_history=["Customer since 2021", "2 previous tickets resolved"],
        instructions=(
            "TASK 1 (Easy) — Ticket Triage.\n"
            "Your job: classify this ticket.\n"
            "Set 'category' to one of: billing / technical / account / shipping / general\n"
            "Set 'priority' to one of: P1 (critical) / P2 (high) / P3 (medium) / P4 (low)\n"
            "Do NOT write a response yet. Only classify."
        )
    ),

    # ── TASK 2: Medium — Draft Response ─────────────────────────────────────
    Task(
        name="draft_response",
        difficulty="medium",
        ticket_id="TKT-002",
        ticket_subject="Charged twice for my subscription",
        ticket_body=(
            "Hello, I was charged $49.99 twice this month on March 3rd and March 5th. "
            "My bank statement shows two charges from your company. "
            "Order ID: ORD-88421. I need a refund for the duplicate charge immediately. "
            "This is very frustrating."
        ),
        correct_category="billing",
        correct_priority="P2",
        knowledge_base=[
            "Duplicate charges happen when payment gateway times out and retries.",
            "Refund SLA: 3-5 business days back to original payment method.",
            "To issue refund: verify order ID, confirm duplicate in billing system, "
            "then process via billing portal. Refund confirmation email is auto-sent.",
            "Compensation policy: offer 1 month free on billing errors over $20."
        ],
        correct_decision="resolve",
        sla_hours=8.0,
        customer_history=[
            "Customer since 2020",
            "Premium subscriber",
            "No previous billing issues"
        ],
        instructions=(
            "TASK 2 (Medium) — Draft a Resolution Response.\n"
            "The customer was double-charged. Use the knowledge base hints to write "
            "a professional, empathetic support response.\n"
            "Set 'response_text' with your full reply to the customer.\n"
            "Your response MUST: acknowledge the problem, explain the cause, "
            "state the refund timeline, and offer compensation per policy.\n"
            "Also set 'category' = billing, 'priority' = P2, "
            "'resolution_decision' = resolve."
        )
    ),

    # ── TASK 3: Hard — Full Resolution Cycle ────────────────────────────────
    Task(
        name="full_resolution",
        difficulty="hard",
        ticket_id="TKT-003",
        ticket_subject="Data export failing - critical for compliance audit",
        ticket_body=(
            "We are a business customer (Enterprise plan, Account: ENT-5521). "
            "Our data export function has been broken for 3 days. "
            "We get error code ERR-5091 when exporting any dataset over 10k rows. "
            "This is BLOCKING our compliance audit which is due in 48 hours. "
            "We have already tried: clearing cache, different browsers, API export. "
            "All fail with ERR-5091. Previous ticket TKT-998 from last week was "
            "marked resolved but the issue is NOT resolved."
        ),
        correct_category="technical",
        correct_priority="P1",
        knowledge_base=[
            "ERR-5091: Known intermittent bug in export service for datasets >10k rows.",
            "Fix: Engineering team must deploy hotfix. ETA unknown but tracked in JIRA-4421.",
            "Enterprise SLA: P1 issues must be escalated to Tier-2 within 2 hours.",
            "For re-opened tickets, escalation is mandatory — do NOT mark resolve.",
            "Escalation message must reference original ticket ID and include error code.",
            "Business impact statement required in all P1 escalations.",
        ],
        correct_decision="escalate",
        sla_hours=2.0,
        customer_history=[
            "Enterprise customer since 2019",
            "Annual contract value: $120k",
            "Previous ticket TKT-998 incorrectly closed",
            "3 escalations in past year - all resolved"
        ],
        instructions=(
            "TASK 3 (Hard) — Full Resolution Cycle with SLA Pressure.\n"
            "This is a P1 enterprise issue with a 2-hour SLA and a compliance deadline.\n"
            "Previous ticket was incorrectly closed. Do NOT resolve — this MUST be escalated.\n"
            "Set 'resolution_decision' to: resolve / escalate / request_info\n"
            "Set 'response_text' with your message to the customer.\n"
            "Set 'category' = technical, 'priority' = P1.\n"
            "Escalation message must mention: error code, original ticket ID, "
            "business impact, and SLA urgency."
        )
    ),
]