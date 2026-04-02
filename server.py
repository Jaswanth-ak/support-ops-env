from fastapi import FastAPI, HTTPException
from support_ops_env.env import SupportOpsEnv
from support_ops_env.models import SupportAction, SupportObservation
from typing import Any, Dict

app = FastAPI(title="SupportOpsEnv", version="1.0.0")
env = SupportOpsEnv()


@app.post("/reset")
def reset() -> Dict[str, Any]:
    obs = env.reset()
    return obs.model_dump()


@app.post("/step")
def step(action: SupportAction) -> Dict[str, Any]:
    try:
        obs, reward, done, info = env.step(action)
        return {
            "observation": obs.model_dump(),
            "reward": reward,
            "done": done,
            "info": info,
        }
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/state")
def state() -> Dict[str, Any]:
    return env.state()


@app.get("/health")
def health():
    return {"status": "ok"}