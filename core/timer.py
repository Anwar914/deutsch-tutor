"""Pure timer arithmetic; wall-clock passage is not proof of active learning."""

import time

DURATIONS = (900, 900, 600, 300)


def elapsed(timer: dict, now: float | None = None) -> float:
    """Return elapsed seconds, including the current unpaused segment."""
    now = time.time() if now is None else now
    start = timer.get("started")
    return timer.get("elapsed", 0.0) + (max(0.0, now - start) if start is not None else 0.0)


def pause(timer: dict, now: float | None = None) -> None:
    """Freeze a timer in place."""
    timer["elapsed"] = elapsed(timer, now)
    timer["started"] = None


def resume(timer: dict, now: float | None = None) -> None:
    """Resume without resetting accumulated time."""
    if timer.get("started") is None:
        timer["started"] = time.time() if now is None else now
