from typing import Any, Dict, Tuple
from support_ops_env.models import SupportAction, SupportObservation, SupportReward
from support_ops_env.tasks import TASKS, Task
from support_ops_env.graders import GRADERS


class SupportOpsEnv:
    """
    SupportOpsEnv — OpenEnv-compliant customer support operations environment.
    Simulates real enterprise support workflows: triage, response drafting,
    and full escalation cycle.
    """

    MAX_STEPS = 3  # One step per task is the natural episode length

    def __init__(self):
        self._task_index: int = 0
        self._current_task: Task = TASKS[0]
        self._step_count: int = 0
        self._done: bool = False
        self._last_reward: float = 0.0
        self._last_breakdown: str = ""

    # ── reset ────────────────────────────────────────────────────────────────
    def reset(self) -> SupportObservation:
        """Start a fresh episode from Task 1."""
        self._task_index = 0
        self._current_task = TASKS[0]
        self._step_count = 0
        self._done = False
        self._last_reward = 0.0
        self._last_breakdown = ""
        return self._make_observation()

    # ── step ─────────────────────────────────────────────────────────────────
    def step(
        self, action: SupportAction
    ) -> Tuple[SupportObservation, float, bool, Dict[str, Any]]:
        """
        Process one agent action and return (observation, reward, done, info).
        Each step corresponds to one task. After all 3 tasks, episode is done.
        """
        if self._done:
            raise RuntimeError("Episode is done. Call reset() to start a new one.")

        task = self._current_task
        grader = GRADERS[task.name]
        reward_obj: SupportReward = grader(action, task)

        self._last_reward = reward_obj.total
        self._last_breakdown = reward_obj.breakdown
        self._step_count += 1

        # Advance to next task or finish episode
        self._task_index += 1
        if self._task_index >= len(TASKS):
            self._done = True
        else:
            self._current_task = TASKS[self._task_index]

        obs = self._make_observation() if not self._done else self._terminal_observation()

        info = {
            "task_name": task.name,
            "difficulty": task.difficulty,
            "reward_breakdown": reward_obj.breakdown,
            "reward_detail": reward_obj.model_dump(),
        }

        return obs, reward_obj.total, self._done, info

    # ── state ────────────────────────────────────────────────────────────────
    def state(self) -> Dict[str, Any]:
        """Return current environment state (for OpenEnv compliance)."""
        return {
            "task_index": self._task_index,
            "current_task": self._current_task.name if not self._done else "done",
            "step_count": self._step_count,
            "done": self._done,
            "last_reward": self._last_reward,
            "last_breakdown": self._last_breakdown,
            "total_tasks": len(TASKS),
        }

    # ── helpers ──────────────────────────────────────────────────────────────
    def _make_observation(self) -> SupportObservation:
        t = self._current_task
        return SupportObservation(
            ticket_id=t.ticket_id,
            ticket_subject=t.ticket_subject,
            ticket_body=t.ticket_body,
            customer_history=t.customer_history,
            knowledge_base_hints=t.knowledge_base,
            sla_hours_remaining=t.sla_hours,
            previous_responses=[],
            task_name=t.name,
            step_number=self._step_count,
            instructions=t.instructions,
        )

    def _terminal_observation(self) -> SupportObservation:
        return SupportObservation(
            ticket_id="DONE",
            ticket_subject="Episode complete",
            ticket_body="All 3 tasks completed.",
            task_name="done",
            step_number=self._step_count,
            instructions="Episode finished. Call reset() to start again.",
        )