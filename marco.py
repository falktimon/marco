#!/usr/bin/env python3

import curses
import shutil
import os
import subprocess
import sys
from pathlib import Path

# Optional TOML parsing – fall back to a simple ``eval`` if the library is missing.
try:
    import toml
except ImportError:  # pragma: no cover
    toml = None


# ----------------------------------------------------------------------
# Configuration handling
# ----------------------------------------------------------------------
def load_config() -> dict:
    """Load configuration from ``~/.config/marco/marco.toml``, ``./marco.toml`` and ``./config.toml``.

    The local files (in the current working directory) override the user‑level
    configuration. Missing files are ignored.
    """
    default_cfg = {
        "colors": {
            "bg": "default",
            "fg": "white",
            "highlight_fg": "black",
            "highlight_bg": "cyan",
        },
        "padding": 2,
        "editor": None,  # optional explicit editor command
    }

    cfg: dict = default_cfg.copy()
    user_cfg_path = Path.home() / ".config" / "marco" / "marco.toml"
    local_cfg_path = Path.cwd() / "marco.toml"
    local_config_path = Path.cwd() / "config.toml"

    for path in (user_cfg_path, local_cfg_path, local_config_path):
        if not path.is_file():
            continue
        try:
            if toml:
                data = toml.load(path)
            else:
                data = eval(path.read_text(), {"__builtins__": {}})
            for k, v in data.items():
                # Merge dicts recursively; otherwise replace the value.
                if isinstance(v, dict):
                    if isinstance(cfg.get(k), dict):
                        cfg[k].update(v)  # type: ignore[arg-type]
                    else:
                        cfg[k] = v
                else:
                    cfg[k] = v
        except Exception:
            # Silently ignore malformed config files.
            pass
    return cfg


# ----------------------------------------------------------------------
# Colour handling
# ----------------------------------------------------------------------
_COLOR_NAME_MAP = {
    "black": curses.COLOR_BLACK,
    "red": curses.COLOR_RED,
    "green": curses.COLOR_GREEN,
    "yellow": curses.COLOR_YELLOW,
    "blue": curses.COLOR_BLUE,
    "magenta": curses.COLOR_MAGENTA,
    "cyan": curses.COLOR_CYAN,
    "white": curses.COLOR_WHITE,
}


def init_colors(cfg: dict) -> dict:
    """Initialise colour pairs based on the configuration.

    Returns a mapping with keys ``normal`` and ``highlight`` containing the
    colour‑pair numbers to be used with ``curses.color_pair``.
    """
    curses.start_color()
    curses.use_default_colors()
    fg = _COLOR_NAME_MAP.get(cfg["colors"].get("fg", "white"), curses.COLOR_WHITE)
    bg = _COLOR_NAME_MAP.get(cfg["colors"].get("bg", "default"), -1)
    curses.init_pair(1, fg, bg)

    h_fg = _COLOR_NAME_MAP.get(
        cfg["colors"].get("highlight_fg", "black"), curses.COLOR_BLACK
    )
    h_bg = _COLOR_NAME_MAP.get(
        cfg["colors"].get("highlight_bg", "cyan"), curses.COLOR_CYAN
    )
    curses.init_pair(2, h_fg, h_bg)

    return {"normal": curses.color_pair(1), "highlight": curses.color_pair(2)}


# ----------------------------------------------------------------------
# Core utilities
# ----------------------------------------------------------------------
def list_dir(path: str) -> list[str]:
    """Return a sorted list of entries in *path*.

    ``..`` is inserted unless *path* is the filesystem root.
    """
    try:
        entries = os.listdir(path)
    except PermissionError:
        entries = []
    entries.sort()
    if os.path.abspath(path) != os.path.abspath("/"):
        entries.insert(0, "..")
    return entries


def run_shell_command(stdscr: curses.window, cwd: str) -> None:
    """Prompt for a command, execute it in *cwd*, and display the output."""
    curses.echo()
    stdscr.addstr(curses.LINES - 1, 0, ":")
    stdscr.clrtoeol()
    cmd = stdscr.getstr(curses.LINES - 1, 1).decode("utf-8")
    curses.noecho()
    if not cmd.strip():
        return
    proc = subprocess.Popen(
        cmd,
        shell=True,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    out, _ = proc.communicate()
    stdscr.clear()
    stdscr.addstr(0, 0, f"$ {cmd}\n")
    lines = out.splitlines()
    for idx, line in enumerate(lines[: curses.LINES - 2]):
        stdscr.addstr(idx + 1, 0, line)
    stdscr.addstr(curses.LINES - 1, 0, "Press any key to continue...")
    stdscr.getch()


def open_in_editor(path: str, editor_cmd: str | None) -> None:
    """Open *path* with the configured editor.

    Resolution order:
        1. ``editor_cmd`` from the config file
        2. ``EDITOR`` environment variable
        3. ``VISUAL`` environment variable
        4. Fallback to ``vi``
    The curses UI is temporarily suspended while the editor runs and then
    restored using ``curses.def_prog_mode`` / ``curses.reset_prog_mode``.
    """
    editor = editor_cmd or os.getenv("EDITOR") or os.getenv("VISUAL") or "vi"
    curses.def_prog_mode()
    curses.endwin()
    try:
        subprocess.call([editor, path])
    finally:
        curses.reset_prog_mode()
        curses.curs_set(0)


# ----------------------------------------------------------------------
# Main UI loop
# ----------------------------------------------------------------------
def main(stdscr: curses.window) -> None:
    """Main UI loop for the Marco file explorer."""
    cfg = load_config()
    # Load optional keybindings from config
    keybindings = cfg.get("keybindings", {})
    SPACE_KEY = ord(keybindings.get("select", " "))
    COPY_KEY = ord(keybindings.get("copy", "c"))
    CUT_KEY = ord(keybindings.get("cut", "x"))
    PASTE_KEY = ord(keybindings.get("paste", "p"))
    QUIT_KEY = ord(keybindings.get("quit", "q"))
    colors = init_colors(cfg)
    padding = cfg.get("padding", 2)
    editor_cfg = cfg.get("editor")

    curses.curs_set(0)  # Hide cursor
    cwd = os.getcwd()
    selection = 0
    # Set of selected entries (absolute paths) per directory
    selected: dict[str, set[str]] = {}
    # Clipboard for copy/cut operations
    clipboard: dict = {"paths": [], "mode": None}

    # Persistent per‑directory selection state
    dir_selection: dict[str, int] = {}

    # Set background for the whole window
    stdscr.bkgd(" ", colors["normal"])
    while True:
        stdscr.clear()
        # Draw current directory on the top‑right with the normal colour pair.
        height, width = stdscr.getmaxyx()
        dir_str = cwd
        if len(dir_str) + padding > width:
            dir_display = dir_str[-(width - padding - 1) :]
        else:
            dir_display = dir_str
        start_x = max(padding, width - len(dir_display) - padding)
        stdscr.addstr(0, start_x, dir_display, colors["normal"])

        entries = list_dir(cwd)
        max_rows = curses.LINES - 2
        start = max(0, selection - max_rows + 1)
        visible = entries[start : start + max_rows]

        # Draw entries with selection and cursor indicators
        selected_set = selected.get(cwd, set())
        for idx, entry in enumerate(visible):
            real_idx = start + idx
            entry_path = os.path.abspath(os.path.join(cwd, entry))
            is_selected = entry_path in selected_set
            cursor = "> " if real_idx == selection else "  "
            marker = "[*] " if is_selected else "    "
            line = f"{cursor}{marker}{entry}"
            attr = colors["highlight"] if real_idx == selection else colors["normal"]
            stdscr.addstr(idx + 1, padding, line, attr)

        stdscr.refresh()
        key = stdscr.getch()

        if key in (QUIT_KEY, 27):  # q or ESC
            break
        elif key in (ord("j"), curses.KEY_DOWN):
            if selection < len(entries) - 1:
                selection += 1
        elif key in (ord("k"), curses.KEY_UP):
            if selection > 0:
                selection -= 1
        elif key in (ord("l"), curses.KEY_RIGHT, 10, 13):  # ENTER or l
            chosen = entries[selection]
            chosen_path = os.path.abspath(os.path.join(cwd, chosen))
            if os.path.isdir(chosen_path):
                # Save current selection for the directory we are leaving
                dir_selection[cwd] = selection
                cwd = chosen_path
                selection = dir_selection.get(cwd, 0)
            else:
                open_in_editor(chosen_path, editor_cfg)
        elif key == ord("h"):
            parent = os.path.abspath(os.path.join(cwd, ".."))
            if parent != cwd:
                dir_selection[cwd] = selection
                cwd = parent
                selection = dir_selection.get(cwd, 0)
        elif key == ord(":"):
            run_shell_command(stdscr, cwd)
        elif key == SPACE_KEY:
            # Toggle selection of the highlighted entry
            entry_path = os.path.abspath(os.path.join(cwd, entries[selection]))
            sel_set = selected.setdefault(cwd, set())
            if entry_path in sel_set:
                sel_set.remove(entry_path)
            else:
                sel_set.add(entry_path)
        elif key == COPY_KEY:
            # Copy selected entries to clipboard
            sel_set = selected.get(cwd, set())
            if sel_set:
                clipboard["paths"] = list(sel_set)
                clipboard["mode"] = "copy"
                continue
        elif key == CUT_KEY:
            # Cut selected entries to clipboard
            sel_set = selected.get(cwd, set())
            if sel_set:
                clipboard["paths"] = list(sel_set)
                clipboard["mode"] = "cut"
                continue
        elif key == PASTE_KEY:
            # Paste entries from clipboard into current directory
            if clipboard["paths"]:
                for src in clipboard["paths"]:
                    base = os.path.basename(src)
                    dst = os.path.join(cwd, base)
                    # Skip if source and destination are the same
                    if os.path.abspath(src) == os.path.abspath(dst):
                        continue
                    try:
                        if os.path.isdir(src):
                            if clipboard["mode"] == "copy":
                                shutil.copytree(src, dst, dirs_exist_ok=True)
                            else:
                                shutil.move(src, dst)
                                src_dir = os.path.abspath(os.path.dirname(src))
                                sel_set_src = selected.get(src_dir)
                                if sel_set_src and src in sel_set_src:
                                    sel_set_src.discard(src)
                        else:
                            if clipboard["mode"] == "copy":
                                shutil.copy2(src, dst)
                            else:
                                shutil.move(src, dst)
                                src_dir = os.path.abspath(os.path.dirname(src))
                                sel_set_src = selected.get(src_dir)
                                if sel_set_src and src in sel_set_src:
                                    sel_set_src.discard(src)
                    except Exception:
                        pass
                # After paste, clear clipboard for cut mode
                if clipboard["mode"] == "cut":
                    clipboard["paths"] = []
                    clipboard["mode"] = None
                continue
        # other keys are ignored


if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        sys.exit(0)
