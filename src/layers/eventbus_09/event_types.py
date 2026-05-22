# Event type constants for the full catnip-agent event schema.

RUN_STARTED = "run.started"
RUN_FINISHED = "run.finished"
RUN_HEARTBEAT = "run.heartbeat"
PROMPT_COMPOSED = "prompt.composed"

AGENT_STEP_FINISHED = "agent.step.finished"
AGENT_PLAN_GENERATED = "agent.plan.generated"
AGENT_REASONING_SUMMARY = "agent.reasoning.summary"
AGENT_ANSWER_PRODUCED = "agent.answer.produced"

TOOL_CALL_REQUESTED = "tool.call.requested"
TOOL_CALL_RESULT = "tool.call.result"
TOOL_CALL_FAILED = "tool.call.failed"

WORKER_HEARTBEAT = "worker.heartbeat"
