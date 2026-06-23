# cmux sidebar for Code Puppy

A tiny, zero-dependency [Code Puppy](https://github.com/mpfaffenberger/code_puppy)
plugin that turns the [cmux](https://cmux.io) sidebar into a **live dashboard**
of agent activity.

It runs entirely off the `cmux` CLI and **no-ops silently when you're not inside
cmux**, so it's safe to leave installed everywhere.

## What you get

**Three status pills** (color-coded, priority-sorted):

| Pill | Shows |
|---|---|
| `pup_task` | a **one-liner of the task** you asked for (your prompt) |
| `pup` | current activity with a **per-tool icon + color** and the actual target (file / command / pattern) |
| `pup_ctx` | **context-window usage %** -- green `<30%`, yellow `<65%`, red `>=65%` |

**A progress bar** that advances per tool call.

**Detailed log entries** showing what the agent is actually doing:

```
-> read_file README.md
-> grep plugin
-> agent_run_shell_command echo hello
   read_file done in 67ms
Complete - 15.9s - 3 tools - 241 tok - 45 tok/s - ctx 10%
```

**On completion**: a one-line **run summary** (duration, tool count, output
tokens, generation tok/s, context %), a **desktop notification**, and a
**screen flash** to grab your attention.

### Per-tool colors

| Tool kind | Icon | Color |
|---|---|---|
| read / list | eye / folder | blue |
| search (grep) | magnifyingglass | cyan |
| write (edit/create/replace) | pencil | orange |
| delete | trash | red |
| shell | terminal | purple |
| sub-agent | person.2 | green |

> Progress is an estimate (steps `+0.08` per tool call, caps at `0.9`, snaps to
> `1.0` on completion) -- the agent can't know the total tool count up front.
> Token / context metrics come from Code Puppy's own run-stats and
> context-indicator internals, imported defensively (skipped if your build
> doesn't expose them).

## Install

```bash
git clone https://github.com/12britz/code-puppy-cmux-sidebar.git
cd code-puppy-cmux-sidebar
./install.sh
```

That copies the plugin to `~/.code_puppy/plugins/cmux_sidebar/` (the Code Puppy
**user plugin** tier -- applies to every project, survives Code Puppy
auto-updates). Restart Code Puppy *inside a cmux pane* and run any task.

### Manual install

```bash
mkdir -p ~/.code_puppy/plugins
cp -R cmux_sidebar ~/.code_puppy/plugins/
```

## Uninstall

```bash
rm -rf ~/.code_puppy/plugins/cmux_sidebar
```

## Configuration

| Env var | Effect |
|---|---|
| `CMUX_SIDEBAR_DISABLED=1` | Turn the whole plugin off |
| `CMUX_SIDEBAR_QUIET=1` | Suppress per-tool log spam (keep pills + the end-of-run summary) |

## Requirements

- [Code Puppy](https://github.com/mpfaffenberger/code_puppy) (any version with
  the plugin/callbacks system).
- Running inside [cmux](https://cmux.io) with the `cmux` CLI on your `PATH`.

## How it works

Code Puppy's plugin loader auto-discovers `register_callbacks.py` in any plugin
directory and registers hooks via `code_puppy.callbacks.register_callback`. This
plugin is a single self-contained module (no sibling imports) so it loads
identically as a builtin, user, or project plugin, with a dedup guard so an
accidental double-load can't double-fire.

Hooks used: `startup`, `user_prompt_submit`, `agent_run_start`, `pre_tool_call`,
`post_tool_call`, `agent_run_end`, `agent_run_cancel`, `shutdown`.

## License

MIT -- see [LICENSE](LICENSE).
