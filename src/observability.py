# observability.py - Minimal structured logging and per-request trace collection
import contextlib
import json
import re
import time
import uuid
from contextvars import ContextVar
from pathlib import Path


_trace_id: ContextVar[str | None] = ContextVar("_trace_id", default=None)
_events: ContextVar[list | None] = ContextVar("_events", default=None)
_span_stack: ContextVar[tuple] = ContextVar("_span_stack", default=())


def new_trace() -> str:
    """Start a new trace for the current request. Returns the trace_id."""
    trace_id = uuid.uuid4().hex[:12]
    _trace_id.set(trace_id)
    _events.set([])
    _span_stack.set(())
    return trace_id


def current_trace_id() -> str | None:
    return _trace_id.get()


def log_event(stage: str, **fields) -> None:
    """Append a structured event to the current trace."""
    events = _events.get()
    if events is None:
        return
    stack = _span_stack.get()
    fields.setdefault("parent_id", stack[-1] if stack else None)
    events.append({
        "trace_id": _trace_id.get(),
        "stage": stage,
        "ts": time.time(),
        **fields,
    })


@contextlib.contextmanager
def span(stage: str, **fields):
    """Time a block and emit one structured event at its end, linked to its parent span."""
    stack = _span_stack.get()
    parent_id = stack[-1] if stack else None
    span_id = uuid.uuid4().hex[:8]
    token = _span_stack.set(stack + (span_id,))
    start = time.perf_counter()
    err = None
    try:
        yield
    except BaseException as e:
        err = repr(e)
        raise
    finally:
        elapsed_ms = (time.perf_counter() - start) * 1000
        _span_stack.reset(token)
        extra = {"latency_ms": round(elapsed_ms, 1), "span_id": span_id, "parent_id": parent_id}
        if err is not None:
            extra["error"] = err
        log_event(stage, **fields, **extra)


def trace_events() -> list[dict]:
    """Return the accumulated events for the current trace."""
    return list(_events.get() or [])


def print_trace() -> None:
    """Pretty-print the current trace, one event per line, JSON-encoded."""
    for event in trace_events():
        print(json.dumps(event))


def write_trace(directory: str, label: str = "") -> Path | None:
    """Write the current trace (summary + events) as JSON. Returns the file path."""
    trace_id = _trace_id.get()
    if trace_id is None:
        return None
    out_dir = Path(directory)
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    safe_label = re.sub(r"[^A-Za-z0-9._-]", "_", label)
    name = "-".join(part for part in (stamp, safe_label, trace_id) if part)
    path = out_dir / f"{name}.json"
    payload = {"summary": trace_summary(), "events": trace_events()}
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    return path


def trace_summary() -> dict:
    """Aggregate per-stage latencies and token usage into a flat summary.

    Repeated stages report `count` and summed latency. The total only counts
    top-level spans so nested spans are not double-counted.
    """
    summary: dict = {"trace_id": _trace_id.get(), "stages": {}}
    total_ms = 0.0
    prompt_tokens = 0
    completion_tokens = 0
    for event in trace_events():
        stage = event["stage"]
        fields = {
            k: v for k, v in event.items()
            if k not in ("trace_id", "stage", "ts", "span_id", "parent_id")
        }
        previous = summary["stages"].get(stage)
        if previous is not None:
            fields["count"] = previous.get("count", 1) + 1
            if "latency_ms" in fields:
                fields["latency_ms"] = round(
                    fields["latency_ms"] + previous.get("latency_ms", 0), 1
                )
        summary["stages"][stage] = fields
        if event.get("parent_id") is None:
            total_ms += event.get("latency_ms", 0)
        prompt_tokens += event.get("prompt_tokens") or 0
        completion_tokens += event.get("completion_tokens") or 0
    summary["total_latency_ms"] = round(total_ms, 1)
    if prompt_tokens or completion_tokens:
        summary["prompt_tokens"] = prompt_tokens
        summary["completion_tokens"] = completion_tokens
    return summary
