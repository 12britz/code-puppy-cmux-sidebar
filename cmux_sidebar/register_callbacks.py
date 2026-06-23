"""cmux sidebar reporter for Code Puppy.

A self-contained Code Puppy plugin that mirrors live agent activity into the
cmux terminal sidebar: status pills, a progress bar, log entries, and a
desktop notification on completion.

Self-contained on purpose: everything lives in this single module with no
sibling imports, so it works identically whether dropped in as a builtin,
user (~/.code_puppy/plugins/), or project (<repo>/.code_puppy/plugins/) plugin.

No-ops cleanly when not running inside cmux.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from functools import lru_cache

from code_puppy.callbacks import register_callback

# --------------------------------------------------------------------------- #
# cmux CLI wrapper (crash-proof, fire-and-forget)
# --------------------------------------------------------------------------- #
STATUS_KEY = "puppy"
LOG_SOURCE = "code-puppy"

COLOR_THINKING = "#7C4DFF"
COLOR_TOOL = "#2D9CDB"
COLOR_DONE = "#4CAF50"
COLOR_ERROR = "#EB5757"
COLOR_IDLE = "#9E9E9E"


@lru_cache(maxsize=1)
def in_cmux() -> bool:
    """True only when we're inside cmux and the CLI is callable."""
    return bool(os.environ.get("CMUX_WORKSPACE_ID")) and shutil.which("cmux") is not None


def _run(args: list[str]) -> None:
    """Fire a cmux command and forget it. Never blocks, never raises."""
    if not in_cmux():
        return
    try:
        subprocess.Popen(
            ["cmux", *args],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
        )
    except Exception:
        pass  # cosmetic feature: swallow everything


def _set_status(value: str, icon: str, color: str) -> None:
    _run(["set-status", STATUS_KEY, value, "--icon", icon, "--color", color])


def _log(message: str, level: str = "info") -> None:
    _run(["log", "--level", level, "--source", LOG_SOURCE, "--", message])


def _set_progress(value: float, label: str = "") -> None:
    value = max(0.0, min(1.0, value))
    args = ["set-progress", f"{value:.2f}"]
    if label:
        args += ["--label", label]
    _run(args)


def _clear_progress() -> None:
    _run(["clear-progress"])


def _notify(title: str, body: str, subtitle: str = "") -> None:
    args = ["notify", "--title", title, "--body", body]
    if subtitle:
        args += ["--subtitle", subtitle]
    _run(args)


# --------------------------------------------------------------------------- #
# Lifecycle -> sidebar mapping
# --------------------------------------------------------------------------- #
_TOOL_STEP = 0.08
_TOOL_CAP = 0.9
_state: dict[str, int] = {"tool_count": 0}


def _on_startup() -> None:
    if in_cmux():
        _set_status("ready", "sparkle", COLOR_IDLE)


def _on_agent_run_start(agent_name: str, model_name: str, session_id=None) -> None:
    _state["tool_count"] = 0
    _set_status("thinking...", "sparkle", COLOR_THINKING)
    _set_progress(0.05, label=f"{agent_name} - {model_name}")
    _log(f"Run started ({agent_name} / {model_name})", "info")


def _on_pre_tool_call(tool_name: str, tool_args: dict, context=None) -> None:
    _state["tool_count"] += 1
    count = _state["tool_count"]
    progress = min(0.05 + count * _TOOL_STEP, _TOOL_CAP)
    _set_status(tool_name, "hammer", COLOR_TOOL)
    _set_progress(progress, label=f"{tool_name} (#{count})")
    _log(f"-> {tool_name}", "progress")


def _on_post_tool_call(
    tool_name: str, tool_args: dict, result=None, duration_ms: float = 0.0, context=None
) -> None:
    _log(f"   {tool_name} done in {duration_ms:.0f}ms", "info")


def _on_agent_run_end(
    agent_name: str,
    model_name: str,
    session_id=None,
    success: bool = True,
    error=None,
    response_text=None,
    metadata=None,
) -> None:
    tools = _state.get("tool_count", 0)
    if success:
        _set_progress(1.0, label="Complete")
        _set_status("done", "checkmark", COLOR_DONE)
        _log(f"Run complete ({tools} tool calls)", "success")
        _notify("Code Puppy", f"Task complete - {tools} tool call(s).", agent_name)
    else:
        _set_status("error", "xmark", COLOR_ERROR)
        _log(f"Run failed: {error}", "error")
        _notify("Code Puppy", f"Run failed: {error}", agent_name)
    _clear_progress()


def _on_agent_run_cancel(group_id: str) -> None:
    _set_status("cancelled", "xmark", COLOR_ERROR)
    _log("Run cancelled", "warning")
    _clear_progress()


def register() -> None:
    """Register all sidebar callbacks. Runs at import time (plugin loader)."""
    register_callback("startup", _on_startup)
    register_callback("agent_run_start", _on_agent_run_start)
    register_callback("pre_tool_call", _on_pre_tool_call)
    register_callback("post_tool_call", _on_post_tool_call)
    register_callback("agent_run_end", _on_agent_run_end)
    register_callback("agent_run_cancel", _on_agent_run_cancel)


register()
