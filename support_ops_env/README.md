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

A real-world customer support operations environment for training AI agents.

## Tasks
- Task 1 (Easy): Ticket triage — classify category and priority
- Task 2 (Medium): Draft a resolution response using knowledge base
- Task 3 (Hard): Full escalation cycle with SLA pressure

## API Endpoints
- POST /reset — start new episode
- POST /step — send agent action
- GET /state — current environment state

## Baseline Scores
- Task 1: 0.75
- Task 2: 0.90
- Task 3: 0.95
- Average: 0.87