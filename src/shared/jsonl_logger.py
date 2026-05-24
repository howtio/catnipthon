from __future__ import annotations

import json
import time
from pathlib import Path

from src.layers.eventbus_09 import EventBusLayerApi, event_types
from src.layers.eventbus_09.types import Event

_ALL_EVENTS = [
    event_types.RUN_STARTED,
    event_types.RUN_FINISHED,
    event_types.RUN_HEARTBEAT,
    event_types.AGENT_STEP_FINISHED,
    event_types.AGENT_PLAN_GENERATED,
    event_types.AGENT_REASONING_SUMMARY,
    event_types.AGENT_REASONING_CHUNK,
    event_types.AGENT_ANSWER_PRODUCED,
    event_types.TOOL_CALL_REQUESTED,
    event_types.TOOL_CALL_RESULT,
    event_types.TOOL_CALL_FAILED,
    event_types.WORKER_HEARTBEAT,
    event_types.QUEUE_HEARTBEAT,
    event_types.LLM_USAGE,
    event_types.PROMPT_COMPOSED,
]


def attach_jsonl_logger(
    eventbus: EventBusLayerApi,
    log_path: str | None = None,
) -> Path:
    """Subscribe to all EventBus events and write them to a JSONL file.

    Returns the path to the log file.
    """
    logs_dir = Path(__file__).resolve().parent.parent.parent / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_path_obj = Path(log_path) if log_path else logs_dir / "catnip.jsonl"

    def _on_event(event: Event) -> None:
        record = {
            "timestamp": time.time(),
            "type": event.type,
            "payload": event.payload,
        }
        with open(log_path_obj, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    for evt_type in _ALL_EVENTS:
        eventbus.subscribe(evt_type, _on_event)

    return log_path_obj
