from __future__ import annotations

import json
import os
import re
import threading
import time
import traceback
from collections.abc import Mapping
from dataclasses import dataclass
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlparse

from src.bootstrap import App
from src.layers.eventbus_09 import event_types
from src.shared.types import RunTask


RESULT_SPLIT_MARKER = "## Result"
_run_buffers: dict[str, dict[str, Any]] = {}
_active_run_id: str | None = None
_run_lock = threading.Lock()


@dataclass
class WebuiConfig:
    host: str = "127.0.0.1"
    port: int = 8765
    static_dir: Path | None = None


def run_webui_server(app: App, config: WebuiConfig | None = None) -> None:
    resolved = config or WebuiConfig()
    static_dir = resolved.static_dir or _default_static_dir()
    static_dir = static_dir.resolve()

    if not static_dir.is_dir():
        raise FileNotFoundError(f"webui directory not found: {static_dir}")

    handler_cls = _build_handler(app, static_dir)
    server = ThreadingHTTPServer((resolved.host, resolved.port), handler_cls)
    print(f"  WebUI: http://{resolved.host}:{resolved.port}")
    print(f"  Static: {static_dir}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def _default_static_dir() -> Path:
    return Path(__file__).resolve().parent.parent.parent / "webui"


def _build_handler(app: App, static_dir: Path) -> type[SimpleHTTPRequestHandler]:
    task_lock = threading.Lock()

    class WebuiHandler(SimpleHTTPRequestHandler):
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            super().__init__(*args, directory=str(static_dir), **kwargs)

        def do_OPTIONS(self) -> None:  # noqa: N802
            self.send_response(HTTPStatus.NO_CONTENT)
            self._send_common_headers("application/json; charset=utf-8")
            self.end_headers()

        def do_GET(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            if parsed.path.startswith("/api/chat/think/"):
                run_id = parsed.path[len("/api/chat/think/"):]
                buffer = _run_buffers.get(run_id)
                if buffer is None:
                    self._write_json(HTTPStatus.NOT_FOUND, {"error": "run_id not found"})
                    return
                self._write_json(HTTPStatus.OK, buffer)
                return
            super().do_GET()

        def do_POST(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            if parsed.path == "/api/chat":
                self._handle_chat()
                return
            if parsed.path == "/api/history/clear":
                self._handle_history_clear()
                return
            self._write_json(HTTPStatus.NOT_FOUND, {"error": "Unknown endpoint"})

        def end_headers(self) -> None:
            self.send_header("Cache-Control", "no-store")
            super().end_headers()

        def log_message(self, format: str, *args: Any) -> None:
            return

        def _handle_chat(self) -> None:
            payload = self._read_json_body()
            if payload is None:
                return

            question = str(payload.get("question", "")).strip()
            history = _coerce_history(payload.get("history"))

            if not question:
                self._write_json(HTTPStatus.BAD_REQUEST, {"error": "question is required"})
                return

            history = _dedupe_current_question(question, history)

            try:
                result = _start_web_task_background(app, question, history)
                if result is None:
                    self._write_json(HTTPStatus.TOO_MANY_REQUESTS, {
                        "error": "A task is already running",
                    })
                    return
                self._write_json(HTTPStatus.OK, result)
            except Exception as e:
                traceback.print_exc()
                self._write_json(HTTPStatus.INTERNAL_SERVER_ERROR, {
                    "error": f"{type(e).__name__}: {e}",
                })

        def _handle_history_clear(self) -> None:
            with task_lock:
                app.memory.clear_session()
            self._write_json(HTTPStatus.OK, {"ok": True})

        def _read_json_body(self) -> dict[str, Any] | None:
            try:
                raw_len = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                self._write_json(HTTPStatus.BAD_REQUEST, {"error": "Invalid Content-Length"})
                return None

            try:
                raw = self.rfile.read(raw_len).decode("utf-8")
                data = json.loads(raw or "{}")
            except (UnicodeDecodeError, json.JSONDecodeError):
                self._write_json(HTTPStatus.BAD_REQUEST, {"error": "Invalid JSON body"})
                return None

            if not isinstance(data, dict):
                self._write_json(HTTPStatus.BAD_REQUEST, {"error": "JSON body must be an object"})
                return None

            return data

        def _write_json(self, status: HTTPStatus, payload: Mapping[str, Any]) -> None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self._send_common_headers("application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _send_common_headers(self, content_type: str) -> None:
            self.send_header("Content-Type", content_type)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")

    return WebuiHandler


def _run_web_task(
    app: App,
    question: str,
    history: list[dict[str, str]],
) -> dict[str, Any]:
    task = RunTask(id=os.urandom(4).hex(), user_message=question)
    report_text = app.harness.run(task, conversation_history=history)
    answer = _extract_result(report_text)
    app.memory.add_conversation_turn(question, answer)

    run_finished = app.eventbus.get_history("run.finished")
    latest_run = run_finished[-1].payload if run_finished else {}
    return {
        "answer": answer,
        "run_id": latest_run.get("run_id", task.id),
        "steps": latest_run.get("steps", 0),
        "tool_summary": latest_run.get("tool_summary", {}),
        "duration_ms": int(latest_run.get("duration_ms", 0)),
        "token_usage": latest_run.get("token_usage", {}),
    }


def _start_web_task_background(
    app: App,
    question: str,
    history: list[dict[str, str]],
) -> dict[str, Any] | None:
    """Start the agent in a background thread. Returns run info or None if busy."""
    global _active_run_id

    with _run_lock:
        if _active_run_id is not None:
            return None  # one task at a time

        task = RunTask(id=os.urandom(4).hex(), user_message=question)
        run_id = task.id
        _active_run_id = run_id

    buffer: dict[str, Any] = {
        "thinking": "",
        "tools": [],
        "answer": "",
        "status": "running",
        "run_id": run_id,
    }
    _run_buffers[run_id] = buffer

    def _run() -> None:
        global _active_run_id
        unsubs: list[Callable[[], Any]] = []
        try:
            unsubs.append(app.eventbus.subscribe(
                event_types.AGENT_REASONING_CHUNK,
                lambda e: _on_reasoning_chunk(e, run_id),
            ))
            unsubs.append(app.eventbus.subscribe(
                event_types.AGENT_ANSWER_CHUNK,
                lambda e: _on_answer_chunk(e, run_id),
            ))
            unsubs.append(app.eventbus.subscribe(
                event_types.TOOL_CALL_REQUESTED,
                lambda e: _on_tool_call(e, run_id),
            ))

            start_time = time.time()
            report_text = app.harness.run(task, conversation_history=history)
            answer = _extract_result(report_text)
            app.memory.add_conversation_turn(question, answer)

            run_finished = app.eventbus.get_history(event_types.RUN_FINISHED)
            latest_run = run_finished[-1].payload if run_finished else {}
            buffer.update({
                "answer": answer,
                "status": "completed",
                "duration_ms": int((time.time() - start_time) * 1000),
                "steps": latest_run.get("steps", 0),
                "tool_summary": latest_run.get("tool_summary", {}),
                "token_usage": latest_run.get("token_usage", {}),
            })
        except Exception as e:
            traceback.print_exc()
            buffer["status"] = "error"
            buffer["error"] = f"{type(e).__name__}: {e}"
        finally:
            _active_run_id = None
            for unsub in unsubs:
                unsub()

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()
    return {"run_id": run_id, "status": "started"}


def _on_reasoning_chunk(event: Any, run_id: str) -> None:
    buffer = _run_buffers.get(run_id)
    if buffer is None:
        return
    chunk = event.payload.get("chunk", "")
    if chunk:
        buffer["thinking"] += chunk


def _on_answer_chunk(event: Any, run_id: str) -> None:
    buffer = _run_buffers.get(run_id)
    if buffer is None:
        return
    chunk = event.payload.get("chunk", "")
    if chunk:
        buffer["thinking"] += chunk


def _on_tool_call(event: Any, run_id: str) -> None:
    buffer = _run_buffers.get(run_id)
    if buffer is None:
        return
    tool = event.payload.get("tool_name", "")
    args = event.payload.get("arguments", {})
    brief = tool
    for key in ("file_path", "url", "path", "command"):
        val = args.get(key, "")
        if val:
            brief += f"  {str(val)[:60]}"
            break
    buffer["thinking"] += f"\n—— {brief}\n"


def _coerce_history(value: Any) -> list[dict[str, str]]:
    if not isinstance(value, list):
        return []

    history: list[dict[str, str]] = []

    for item in value:
        if not isinstance(item, Mapping):
            continue
        question = str(item.get("question", "")).strip()
        answer = str(item.get("answer", "")).strip()
        if question:
            history.append({"role": "user", "content": question})
        if answer:
            history.append({"role": "assistant", "content": answer})

    return history[-40:]


def _dedupe_current_question(
    question: str,
    history: list[dict[str, str]],
) -> list[dict[str, str]]:
    """Drop a trailing duplicate user message from optimistic UI history."""
    if history and history[-1] == {"role": "user", "content": question}:
        return history[:-1]
    return history


def _extract_result(report: str) -> str:
    if RESULT_SPLIT_MARKER not in report:
        return report.strip()

    result = report.split(RESULT_SPLIT_MARKER, 1)[1].strip()
    result = re.split(r"\n##\s+", result, maxsplit=1)[0].strip()
    return result
