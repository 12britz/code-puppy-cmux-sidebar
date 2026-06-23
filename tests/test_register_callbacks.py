"""Tests for the cmux_sidebar plugin.

These exercise the gating and command-construction logic without needing a
real cmux instance. ``code_puppy`` must be importable (it provides
``register_callback``); everything cmux-related is mocked.
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


def test_no_op_outside_cmux(mod, monkeypatch):
    monkeypatch.delenv("CMUX_WORKSPACE_ID", raising=False)
    mod.in_cmux.cache_clear()
    assert mod.in_cmux() is False

    calls = []
    monkeypatch.setattr(mod.subprocess, "Popen", lambda *a, **k: calls.append(a))
    mod._set_status("hello", "sparkle", "#fff")
    mod._log("nope")
    assert calls == []  # nothing fired when not in cmux


def test_runs_inside_cmux(mod, monkeypatch):
    monkeypatch.setenv("CMUX_WORKSPACE_ID", "ws-123")
    monkeypatch.setattr(mod.shutil, "which", lambda _: "/usr/bin/cmux")
    mod.in_cmux.cache_clear()
    assert mod.in_cmux() is True

    calls = []
    monkeypatch.setattr(mod.subprocess, "Popen", lambda args, **k: calls.append(args))
    mod._set_progress(0.5, label="half")
    assert calls and calls[0][0] == "cmux"
    assert "set-progress" in calls[0]
    assert "0.50" in calls[0]


def test_handlers_never_raise(mod, monkeypatch):
    monkeypatch.delenv("CMUX_WORKSPACE_ID", raising=False)
    mod.in_cmux.cache_clear()
    # Full lifecycle should be safe even when cmux is absent.
    mod._on_startup()
    mod._on_agent_run_start("B", "some-model")
    mod._on_pre_tool_call("grep", {})
    mod._on_post_tool_call("grep", {}, None, 12.0)
    mod._on_agent_run_end("B", "some-model", success=True)
    mod._on_agent_run_cancel("group-1")


def test_progress_clamped(mod, monkeypatch):
    monkeypatch.setenv("CMUX_WORKSPACE_ID", "ws-123")
    monkeypatch.setattr(mod.shutil, "which", lambda _: "/usr/bin/cmux")
    mod.in_cmux.cache_clear()
    calls = []
    monkeypatch.setattr(mod.subprocess, "Popen", lambda args, **k: calls.append(args))
    mod._set_progress(5.0)  # over 1.0
    assert "1.00" in calls[0]
