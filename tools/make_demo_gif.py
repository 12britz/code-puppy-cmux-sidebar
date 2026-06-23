#!/usr/bin/env python3
"""Generate an illustrative animated GIF of the cmux_sidebar dashboard.

Not a screen capture -- a faithful rendering of the pills / progress / log
states the plugin produces, so the PR/README can show the feature at a glance.
"""

from __future__ import annotations

from PIL import Image, ImageDraw, ImageFont

W, H = 380, 500
BG = (24, 24, 37)
PANEL = (33, 33, 50)
TEXT = (220, 222, 233)
MUTED = (140, 144, 165)
DOTBG = (45, 46, 66)

SF = "/System/Library/Fonts/SFNS.ttf"
MONO = "/System/Library/Fonts/Menlo.ttc"
f_title = ImageFont.truetype(SF, 15)
f_pill = ImageFont.truetype(SF, 14)
f_log = ImageFont.truetype(MONO, 11)
f_small = ImageFont.truetype(SF, 11)

LVL_COLOR = {
    "info": MUTED,
    "progress": (86, 204, 242),
    "success": (76, 175, 80),
    "warning": (242, 201, 76),
    "error": (235, 87, 87),
}


def _hex(c: str):
    c = c.lstrip("#")
    return tuple(int(c[i : i + 2], 16) for i in (0, 2, 4))


def pill(d, x, y, w, label, color, value):
    d.rounded_rectangle([x, y, x + w, y + 30], radius=15, fill=PANEL)
    d.ellipse([x + 9, y + 10, x + 21, y + 22], fill=_hex(color))
    txt = f"{value}"
    d.text((x + 30, y + 8), txt, font=f_pill, fill=TEXT)
    return y + 38


def frame(pills, progress, plabel, logs, flash=False):
    img = Image.new("RGB", (W, H), BG if not flash else (40, 50, 44))
    d = ImageDraw.Draw(img)
    d.text((18, 14), "cmux", font=f_title, fill=TEXT)
    d.text((58, 16), "sidebar", font=f_small, fill=MUTED)
    d.line([0, 40, W, 40], fill=(50, 51, 72))

    y = 56
    for label, color, value in pills:
        y = pill(d, 16, y, W - 32, label, color, value)

    # progress bar
    y += 6
    d.text((18, y), plabel, font=f_small, fill=MUTED)
    y += 18
    d.rounded_rectangle([16, y, W - 16, y + 10], radius=5, fill=DOTBG)
    if progress > 0:
        d.rounded_rectangle(
            [16, y, 16 + int((W - 32) * progress), y + 10], radius=5, fill=(124, 77, 255)
        )
    y += 26

    d.line([0, y, W, y], fill=(50, 51, 72))
    y += 10
    d.text((18, y), "LOG", font=f_small, fill=MUTED)
    y += 18
    for lvl, msg in logs[-9:]:
        d.text((18, y), msg, font=f_log, fill=LVL_COLOR.get(lvl, MUTED))
        y += 16
    return img


# brand colors
TASK, SAY = "#4F8EF7", "#00BFA5"
PURPLE, BLUE, CYAN, ORANGE, PURP2, GREEN, RED, GREY = (
    "#7C4DFF", "#2D9CDB", "#56CCF2", "#F2994A", "#9B51E0",
    "#4CAF50", "#EB5757", "#9E9E9E",
)

TASK_V = "Add auth + tests to the app"
frames = []
logs = []


def add(pills, prog, plabel, dur, flash=False, hold=1):
    for _ in range(hold):
        frames.append((frame(pills, prog, plabel, logs, flash), dur))


# 1 idle
add([("act", GREY, "ready")], 0, "", 900)
# 2 task arrives
logs.append(("info", "Task: Add auth + tests to the app"))
add([("task", TASK, TASK_V), ("act", PURPLE, "thinking")], 0.05, "claude-4-8", 900)
# 3 read
logs.append(("progress", "-> read_file main.py"))
add([("task", TASK, TASK_V), ("say", SAY, "Let me read the entry point"),
     ("act", BLUE, "read_file: main.py"), ("ctx", GREEN, "ctx 8%")], 0.13, "read_file (#1)", 900)
# 4 grep
logs.append(("progress", "-> grep FastAPI"))
add([("task", TASK, TASK_V), ("say", SAY, "looking for the app object"),
     ("act", CYAN, "grep: FastAPI"), ("ctx", GREEN, "ctx 14%")], 0.21, "grep (#2)", 900)
# 5 create
logs.append(("progress", "-> create_file auth.py"))
add([("task", TASK, TASK_V), ("say", SAY, "writing the auth module now"),
     ("act", ORANGE, "create_file: auth.py"), ("ctx", "#F2C94C", "ctx 41%")], 0.29, "create_file (#3)", 1000)
# 6 shell
logs.append(("progress", "-> agent_run_shell_command pytest -q"))
add([("task", TASK, TASK_V), ("say", SAY, "running the test suite"),
     ("act", PURP2, "shell: pytest -q"), ("ctx", "#F2C94C", "ctx 58%")], 0.37, "shell (#4)", 1000)
# 7 subagent
logs.append(("progress", "-> [retriever] read_file index.json"))
add([("task", TASK, TASK_V), ("say", SAY, "delegating to a sub-agent"),
     ("act", GREEN, "[retriever] read_file"), ("ctx", RED, "ctx 71%")], 0.45, "read_file (#5)", 1000)
# 8 done + flash
logs.append(("success", "Complete - 18.4s - 5 tools - 1.2k tok - 63 tok/s"))
logs.append(("info", "Tools: 2 read - 1 search - 1 edit - 1 shell"))
logs.append(("info", "Files: auth.py"))
add([("task", TASK, TASK_V), ("act", GREEN, "done"), ("ctx", RED, "ctx 71%")],
    1.0, "Complete", 700, flash=True)
add([("task", TASK, TASK_V), ("act", GREEN, "done"), ("ctx", RED, "ctx 71%")],
    1.0, "Complete", 1600)

imgs = [f for f, _ in frames]
durs = [d for _, d in frames]
out = "assets/demo.gif"
imgs[0].save(out, save_all=True, append_images=imgs[1:], duration=durs, loop=0, optimize=True)
print("wrote", out, "frames:", len(imgs))
