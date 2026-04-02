import re
from support_ops_env.models import SupportAction, SupportReward
from support_ops_env.tasks import Task


def grade_task1_triage(action: SupportAction, task: Task) -> SupportReward:
    """Easy: category + priority classification. Fully deterministic."""
    cat_score = 0.0
    pri_score = 0.0
    penalty = 0.0

    if action.category and action.category.lower().strip() == task.correct_category:
        cat_score = 0.6
    elif action.category:
        # Partial: at least tried to classify
        cat_score = 0.1

    if action.priority and action.priority.upper().strip() == task.correct_priority:
        pri_score = 0.4
    elif action.priority and action.priority.upper() in ["P1", "P2"]:
        # Adjacent priority is worth something
        pri_score = 0.15

    total = round(min(cat_score + pri_score - penalty, 1.0), 4)
    breakdown = (
        f"category={cat_score:.2f} priority={pri_score:.2f} penalty={penalty:.2f}"
    )
    return SupportReward(
        total=total,
        category_score=cat_score,
        priority_score=pri_score,
        penalty=penalty,
        breakdown=breakdown
    )


def grade_task2_response(action: SupportAction, task: Task) -> SupportReward:
    """Medium: rubric-based response grader. Deterministic keyword scoring."""
    cat_score = 0.0
    pri_score = 0.0
    resp_score = 0.0
    penalty = 0.0

    # Category + priority
    if action.category and action.category.lower().strip() == task.correct_category:
        cat_score = 0.1
    if action.priority and action.priority.upper().strip() == task.correct_priority:
        pri_score = 0.1

    # Response quality rubric (keyword-based, deterministic)
    resp = (action.response_text or "").lower()

    # 1. Acknowledges the problem
    ack_words = ["apologize", "sorry", "understand", "i see", "frustrating",
                 "inconvenience", "acknowledge"]
    ack = 0.2 if any(w in resp for w in ack_words) else 0.0

    # 2. Mentions refund timeline
    timeline_words = ["3-5", "3 to 5", "business day", "working day", "refund"]
    timeline = 0.2 if any(w in resp for w in timeline_words) else 0.0

    # 3. Mentions compensation / free month
    comp_words = ["free month", "1 month", "one month", "compensat", "credit"]
    comp = 0.1 if any(w in resp for w in comp_words) else 0.0

    # 4. References order ID
    order_ref = 0.1 if "ord-88421" in resp or "88421" in resp else 0.0

    # 5. Not too short (less than 50 chars = useless)
    length_ok = 0.1 if len(action.response_text or "") >= 80 else 0.0

    # 6. Wrong resolution decision penalty
    if action.resolution_decision and action.resolution_decision.lower() == "escalate":
        penalty += 0.3  # billing duplicate should NOT be escalated

    resp_score = round(ack + timeline + comp + order_ref + length_ok, 4)
    total = round(min(cat_score + pri_score + resp_score - penalty, 1.0), 4)

    breakdown = (
        f"category={cat_score:.2f} priority={pri_score:.2f} "
        f"ack={ack:.2f} timeline={timeline:.2f} comp={comp:.2f} "
        f"order_ref={order_ref:.2f} length={length_ok:.2f} penalty={penalty:.2f}"
    )
    return SupportReward(
        total=max(total, 0.0),
        category_score=cat_score,
        priority_score=pri_score,
        response_score=resp_score,
        penalty=penalty,
        breakdown=breakdown
    )


def grade_task3_escalation(action: SupportAction, task: Task) -> SupportReward:
    """Hard: escalation decision + message quality. Fully deterministic."""
    resolution_score = 0.0
    resp_score = 0.0
    penalty = 0.0

    # Core decision (most important)
    decision = (action.resolution_decision or "").lower().strip()
    if decision == "escalate":
        resolution_score = 0.4
    elif decision == "request_info":
        resolution_score = 0.1  # partial — at least didn't wrongly resolve
    elif decision == "resolve":
        penalty += 0.4  # wrong — this must be escalated per policy

    # Category + priority
    cat_ok = (action.category or "").lower().strip() == "technical"
    pri_ok = (action.priority or "").upper().strip() == "P1"
    if cat_ok:
        resp_score += 0.05
    if pri_ok:
        resp_score += 0.1

    # Response message quality
    resp = (action.response_text or "").lower()

    # Must mention error code
    err_code = 0.1 if "err-5091" in resp or "5091" in resp else 0.0

    # Must reference previous ticket
    prev_ticket = 0.1 if "tkt-998" in resp or "998" in resp else 0.0

    # Must convey urgency / SLA awareness
    urgency_words = ["urgent", "immediately", "priority", "sla", "escalat",
                     "48 hour", "compliance", "audit", "critical"]
    urgency = 0.1 if any(w in resp for w in urgency_words) else 0.0

    # Must acknowledge business impact
    impact_words = ["enterprise", "business", "audit", "compliance",
                    "blocking", "critical", "contract"]
    impact = 0.1 if any(w in resp for w in impact_words) else 0.0

    resp_score += err_code + prev_ticket + urgency + impact

    total = round(min(resolution_score + resp_score - penalty, 1.0), 4)
    breakdown = (
        f"decision={resolution_score:.2f} cat={cat_ok} pri={pri_ok} "
        f"err_code={err_code:.2f} prev_ticket={prev_ticket:.2f} "
        f"urgency={urgency:.2f} impact={impact:.2f} penalty={penalty:.2f}"
    )
    return SupportReward(
        total=max(total, 0.0),
        resolution_score=resolution_score,
        response_score=resp_score,
        penalty=penalty,
        breakdown=breakdown
    )


GRADERS = {
    "ticket_triage":    grade_task1_triage,
    "draft_response":   grade_task2_response,
    "full_resolution":  grade_task3_escalation,
}