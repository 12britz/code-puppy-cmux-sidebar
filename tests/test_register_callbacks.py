"""Tests for the cmux_sidebar plugin (v2).

Exercise gating, command construction, arg-summary extraction, and the
context-color buckets without needing a real cmux instance. ``code_puppy``
must be importable (provides ``register_callback``); cmux is mocked.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

PLUGIN = (
    Path(__file__).resolve().parent.parent / "cmux_sidebar" / "register_callbacks.py"
)


@pytest.fixture()
def mod(monkeypatch):
    """Load the plugin module fresh with a clean in_cmux cache."""
    spec = importlib.util.spec_from_file_location("cmux_sidebar_test", PLUGIN)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.in_cmux.cache_clear()
    return module


def _capture(mod, monkeypatch):
    calls: list = []
    monkeypatch.setattr(mod.subprocess, "Popen", lambda args, **k: calls.append(args))
    return calls


def test_no_op_outside_cmux(mod, monkeypatch):
    monkeypatch.delenv("CMUX_WORKSPACE_ID", raising=False)
    mod.in_cmux.cache_clear()
    assert mod.in_cmux() is False
    calls = _capture(mod, monkeypatch)
    mod._status("k", "v", "sparkle", "#fff")
    mod._log("nope")
    assert calls == []


def test_disabled_env_wins(mod, monkeypatch):
    monkeypatch.setenv("CMUX_WORKSPACE_ID", "ws")
    monkeypatch.setenv("CMUX_SIDEBAR_DISABLED", "1")
    monkeypatch.setattr(mod.shutil, "which", lambda _: "/usr/bin/cmux")
    mod.in_cmux.cache_clear()
    assert mod.in_cmux() is False


def test_runs_inside_cmux(mod, monkeypatch):
    monkeypatch.setenv("CMUX_WORKSPACE_ID", "ws-123")
    monkeypatch.delenv("CMUX_SIDEBAR_DISABLED", raising=False)
    monkeypatch.setattr(mod.shutil, "which", lambda _: "/usr/bin/cmux")
    mod.in_cmux.cache_clear()
    assert mod.in_cmux() is True
    calls = _capture(mod, monkeypatch)
    mod._progress(0.5, label="half")
    assert calls and calls[0][0] == "cmux"
    assert "set-progress" in calls[0] and "0.50" in calls[0]


def test_progress_clamped(mod, monkeypatch):
    monkeypatch.setenv("CMUX_WORKSPACE_ID", "ws")
    monkeypatch.setattr(mod.shutil, "which", lambda _: "/usr/bin/cmux")
    mod.in_cmux.cache_clear()
    calls = _capture(mod, monkeypatch)
    mod._progress(5.0)
    assert "1.00" in calls[0]


def test_arg_summary_basename(mod):
    # file_path tools show just the basename
    assert mod._arg_summary("edit_file", {"file_path": "/a/b/c/foo.py"}) == "foo.py"
    # shell tools show the command
    assert mod._arg_summary("run_shell_command", {"command": "ls -la"}) == "ls -la"
    # grep shows the pattern
    assert mod._arg_summary("grep", {"search_string": "needle"}) == "needle"
    # unknown args -> empty
    assert mod._arg_summary("read_file", {}) == ""


def test_arg_summary_truncates(mod):
    long = "x" * 200
    out = mod._arg_summary("run_shell_command", {"command": long})
    assert len(out) <= 44 and out.endswith("\u2026")


def test_ctx_color_buckets(mod):
    assert mod._ctx_color(10) == mod.CTX_GREEN
    assert mod._ctx_color(50) == mod.CTX_YELLOW
    assert mod._ctx_color(90) == mod.CTX_RED


def test_human_tokens(mod):
    assert mod._human_tokens(500) == "500"
    assert mod._human_tokens(1500) == "1.5k"


def test_handlers_never_raise(mod, monkeypatch):
    monkeypatch.delenv("CMUX_WORKSPACE_ID", raising=False)
    mod.in_cmux.cache_clear()
    mod._on_startup()
    mod._on_agent_run_start("B", "some-model")
    mod._on_pre_tool_call("edit_file", {"file_path": "/x/y.py"})
    mod._on_post_tool_call("edit_file", {}, None, 12.0)
    mod._on_agent_run_end("B", "some-model", success=True)
    mod._on_agent_run_cancel("group-1")
    mod._on_shutdown()
