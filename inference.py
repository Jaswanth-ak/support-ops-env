"""
inference.py — SupportOpsEnv Baseline Inference Script
=======================================================
MANDATORY env vars:
    API_BASE_URL   The API endpoint for the LLM
    MODEL_NAME     The model identifier
    HF_TOKEN       Your Hugging Face / API key
"""

import os
import json
import re
from openai import OpenAI
from support_ops_env.env import SupportOpsEnv
from support_ops_env.models import SupportAction

API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
API_KEY      = os.getenv("HF_TOKEN") or os.getenv("API_KEY", "")
MODEL_NAME   = os.getenv("MODEL_NAME", "meta-llama/Llama-3.3-70B-Instruct")

MAX_STEPS    = 3
TEMPERATURE  = 0.2
MAX_TOKENS   = 512

client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

SYSTEM_PROMPT = """You are an expert customer support agent.
You will receive a support ticket and instructions.
Respond ONLY with a valid JSON object matching this schema:
{
  "category": "billing|technical|account|shipping|general",
  "priority": "P1|P2|P3|P4",
  "response_text": "your response to customer (if needed)",
  "resolution_decision": "resolve|escalate|request_info"
}
No extra text. No markdown. Only the JSON object."""


def parse_action(text: str) -> SupportAction:
    text = text.strip()
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        text = match.group(0)
    try:
        data = json.loads(text)
        return SupportAction(**data)
    except Exception:
        return SupportAction(
            category="general",
            priority="P3",
            response_text=text[:300],
            resolution_decision="resolve"
        )


def run_episode() -> list:
    env = SupportOpsEnv()
    obs = env.reset()
    scores = []
    task_names = ["ticket_triage", "draft_response", "full_resolution"]

    # [START] log — required format
    print(json.dumps({
        "type": "[START]",
        "model": MODEL_NAME,
        "environment": "SupportOpsEnv",
        "tasks": task_names,
        "total_tasks": 3
    }))

    for step in range(MAX_STEPS):
        user_content = f"""TICKET ID: {obs.ticket_id}
SUBJECT: {obs.ticket_subject}

TICKET:
{obs.ticket_body}

CUSTOMER HISTORY: {', '.join(obs.customer_history)}

KNOWLEDGE BASE:
{chr(10).join(f'- {h}' for h in obs.knowledge_base_hints)}

SLA HOURS REMAINING: {obs.sla_hours_remaining}

INSTRUCTIONS:
{obs.instructions}"""

        try:
            completion = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user",   "content": user_content},
                ],
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS,
                stream=False,
            )
            response_text = completion.choices[0].message.content or ""
        except Exception as exc:
            print(f"Model request failed: {exc}. Using fallback.")
            response_text = '{"category":"general","priority":"P3","resolution_decision":"resolve"}'

        action = parse_action(response_text)
        obs_next, reward, done, info = env.step(action)
        scores.append(reward)

        # [STEP] log — required format
        print(json.dumps({
            "type": "[STEP]",
            "step": step + 1,
            "task": task_names[step],
            "difficulty": info["difficulty"],
            "action": {
                "category": action.category,
                "priority": action.priority,
                "resolution_decision": action.resolution_decision,
                "response_text": (action.response_text or "")[:100]
            },
            "reward": round(reward, 4),
            "reward_breakdown": info["reward_breakdown"],
            "done": done
        }))

        obs = obs_next
        if done:
            break

    avg = round(sum(scores) / len(scores), 4)

    # [END] log — required format
    print(json.dumps({
        "type": "[END]",
        "tasks_completed": len(scores),
        "scores": {
            "ticket_triage":   round(scores[0], 4) if len(scores) > 0 else 0,
            "draft_response":  round(scores[1], 4) if len(scores) > 1 else 0,
            "full_resolution": round(scores[2], 4) if len(scores) > 2 else 0,
        },
        "average_score": avg,
        "model": MODEL_NAME
    }))

    return scores


if __name__ == "__main__":
    run_episode()