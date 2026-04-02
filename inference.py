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
    """Extract JSON from model output and parse into SupportAction."""
    text = text.strip()
    # Try to extract JSON block if model adds extra text
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        text = match.group(0)
    try:
        data = json.loads(text)
        return SupportAction(**data)
    except Exception:
        # Fallback — at minimum try to extract category
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

    print("\n" + "="*60)
    print("SupportOpsEnv — Baseline Inference Run")
    print(f"Model: {MODEL_NAME}")
    print("="*60)

    for step in range(MAX_STEPS):
        print(f"\n--- Task {step+1}: {obs.task_name} ({obs.instructions[:60]}...) ---")

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
            print(f"  Model request failed: {exc}. Using fallback.")
            response_text = '{"category":"general","priority":"P3","resolution_decision":"resolve"}'

        action = parse_action(response_text)
        print(f"  Action: category={action.category}, priority={action.priority}, "
              f"decision={action.resolution_decision}")

        obs, reward, done, info = env.step(action)
        scores.append(reward)
        print(f"  Reward: {reward:.4f} | Breakdown: {info['reward_breakdown']}")

        if done:
            break

    print("\n" + "="*60)
    print("RESULTS:")
    for i, s in enumerate(scores):
        task_name = ["ticket_triage", "draft_response", "full_resolution"][i]
        print(f"  Task {i+1} ({task_name}): {s:.4f}")
    print(f"  Average score: {sum(scores)/len(scores):.4f}")
    print("="*60)
    return scores


if __name__ == "__main__":
    run_episode()