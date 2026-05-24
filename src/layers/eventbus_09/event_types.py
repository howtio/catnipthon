from __future__ import annotations

# Run lifecycle
RUN_STARTED = "run.started"
RUN_FINISHED = "run.finished"
RUN_HEARTBEAT = "run.heartbeat"

# Agent loop
AGENT_STEP_FINISHED = "agent.step.finished"
AGENT_PLAN_GENERATED = "agent.plan.generated"
AGENT_REASONING_SUMMARY = "agent.reasoning.summary"
AGENT_REASONING_CHUNK = "agent.reasoning.chunk"
AGENT_ANSWER_PRODUCED = "agent.answer.produced"

# Tool calls
TOOL_CALL_REQUESTED = "tool.call.requested"
TOOL_CALL_RESULT = "tool.call.result"
TOOL_CALL_FAILED = "tool.call.failed"

# Worker / Queue
QUEUE_HEARTBEAT = "queue.heartbeat"
WORKER_HEARTBEAT = "worker.heartbeat"

# LLM
LLM_USAGE = "llm.usage"

# Prompt
PROMPT_COMPOSED = "prompt.composed"
