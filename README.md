# cmux sidebar for Code Puppy 

A tiny, zero-dependency [Code Puppy](https://github.com/mpfaffenberger/code_puppy)
plugin that mirrors live agent activity into the [cmux](https://cmux.io) terminal
sidebar — **status pills, a progress bar, log entries, and a desktop
notification** when a run finishes.

It runs entirely off the `cmux` CLI and **no-ops silently when you're not inside
cmux**, so it's safe to leave installed everywhere.

## What you'll see

| Moment | Sidebar reaction |
|---|---|
| App boot | grey `ready` pill |
| Run starts | purple `thinking...` pill + progress kickoff + log line |
| Each tool call | blue pill with the tool name + progress bump + `→ tool` log |
| Tool finishes | `tool done in Nms` log |
| Run completes | green `done` pill, completion log, **desktop notification**, progress reset |
| Failure / cancel | red pill + error/warning log + notify |

> Progress is an estimate (steps `+0.08` per tool call, caps at `0.9`, snaps to
> `1.0` on completion) — the agent can't know the total tool count up front.

## Install

```bash
git clone https://github.com/12britz/code-puppy-cmux-sidebar.git
cd code-puppy-cmux-sidebar
./install.sh
```

That copies the plugin to `~/.code_puppy/plugins/cmux_sidebar/` (the Code Puppy
**user plugin** tier — applies to every project). Restart Code Puppy *inside a
cmux pane* and run any task.

### Manual install

```bash
mkdir -p ~/.code_puppy/plugins
cp -R cmux_sidebar ~/.code_puppy/plugins/
```

## Uninstall

```bash
rm -rf ~/.code_puppy/plugins/cmux_sidebar
```

## Requirements

- [Code Puppy](https://github.com/mpfaffenberger/code_puppy) (any version with
  the plugin/callbacks system).
- Running inside [cmux](https://cmux.io) with the `cmux` CLI on your `PATH`.

## How it works

Code Puppy's plugin loader auto-discovers `register_callbacks.py` in any plugin
directory and registers hooks via `code_puppy.callbacks.register_callback`. This
plugin is a single self-contained module (no sibling imports) so it loads
identically as a builtin, user, or project plugin.

Hooks used: `startup`, `agent_run_start`, `pre_tool_call`, `post_tool_call`,
`agent_run_end`, `agent_run_cancel`.

## License

MIT — see [LICENSE](LICENSE).
