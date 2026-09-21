# Agent Flight Recorder — Architecture

## Purpose

Agent Flight Recorder is a small educational prototype that demonstrates an important agent-observability problem:

> A final answer can be correct while the underlying tool behavior is suspicious.

The prototype records tool interactions and evaluates the resulting execution trace after the agent finishes.

## System Architecture

```mermaid
flowchart TD
    U[User Request] --> UI[Streamlit Interface]
    UI --> A[Agent / Orchestrator]

    A --> S[search_customers]
    A --> R[read_customer]
    A --> W[update_customer]

    S --> D[(Synthetic Customer Data)]
    R --> D
    W --> D

    S --> T[Telemetry Logger]
    R --> T
    W --> T

    T --> J[(session.jsonl)]

    J --> X[Anomaly Detector]
    P[policies.json] --> X

    X --> N[NORMAL]
    X --> V[REVIEW]

    A --> O[Final Answer]
    O --> UI
    X --> UI