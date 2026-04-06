---
title: SupportOpsEnv
emoji: 🎧
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
tags:
  - openenv
---
# SupportOpsEnv

A real-world customer support operations environment for training AI agents using the OpenEnv framework.

## What is this?

SupportOpsEnv simulates an enterprise customer support operations center. AI agents learn to triage tickets, draft responses, and manage escalations — tasks that every company needs automated.

## Tasks

| Task | Difficulty | Description |
|------|-----------|-------------|
| ticket_triage | Easy | Classify ticket category and priority |
| draft_response | Medium | Draft a resolution response using knowledge base |
| full_resolution | Hard | Full escalation cycle with SLA pressure |

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| /reset | POST | Start a new episode |
| /step | POST | Send agent action, get reward |
| /state | GET | Current environment state |
| /health | GET | Health check |

## Action Space
```json
{
  "category": "billing | technical | account | shipping | general",
  "priority": "P1 | P2 | P3 | P4",
  "response_text": "string",
  "resolution_decision": "resolve | escalate | request_info"
}
```

## Reward Function

- Category correct: +0.60
- Priority correct: +0.40
- Response quality: +0.30
- Resolution decision: +0.40
- Wrong escalation penalty: -0.30
- SLA miss penalty: -0.10

## Baseline Scores

| Task | Score |
|------|-------|
| ticket_triage | 0.75 |
| draft_response | 0.90 |
| full_resolution | 0.95 |
| **Average** | **0.87** |

## Setup
```bash
docker build -t support-ops-env .
docker run -p 7860:7860 support-ops-env
```

## Environment Variables