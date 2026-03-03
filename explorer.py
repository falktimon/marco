#!/usr/bin/env python3

import curses
import os
import subprocess
import sys

# Simple ncurses file explorer with Vim-like navigation.
# - h: go up one directory (if not root)
# - l or ENTER: enter selected directory
# - j/k: move selection down/up
# - : : prompt for a shell command to execute in the current directory
# - q: quit

def list_dir(path):
    try:
        entries = os.listdir(path)
    except PermissionError:
        entries = []
    entries.sort()
    # Prepend parent directory entry
    if os.path.abspath(path) != os.path.abspath('/'):
        entries.insert(0, '..')
    return entries

def run_shell_command(stdscr, cwd):
    curses.echo()
    stdscr.addstr(curses.LINES - 1, 0, ":")
    stdscr.clrtoeol()
    cmd = stdscr.getstr(curses.LINES - 1, 1).decode('utf-8')
    curses.noecho()
    if not cmd.strip():
        return
    # Execute the command and capture output
    proc = subprocess.Popen(cmd, shell=True, cwd=cwd,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True)
    out, _ = proc.communicate()
    # Show output in a simple pager-like view
    stdscr.clear()
    stdscr.addstr(0, 0, f"$ {cmd}\n")
    lines = out.splitlines()
    for idx, line in enumerate(lines[:curses.LINES - 2]):
        stdscr.addstr(idx + 1, 0, line)
    stdscr.addstr(curses.LINES - 1, 0, "Press any key to continue...")
    stdscr.getch()

def main(stdscr):
    curses.curs_set(0)  # Hide cursor
    cwd = os.getcwd()
    selection = 0
    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, f"Current directory: {cwd}")
        entries = list_dir(cwd)
        for idx, entry in enumerate(entries):
            prefix = "> " if idx == selection else "  "
            stdscr.addstr(idx + 1, 0, f"{prefix}{entry}")
        stdscr.refresh()
        key = stdscr.getch()
        if key in (ord('q'), 27):  # q or ESC to quit
            break
        elif key in (ord('j'), curses.KEY_DOWN):
            if selection < len(entries) - 1:
                selection += 1
        elif key in (ord('k'), curses.KEY_UP):
            if selection > 0:
                selection -= 1
        elif key in (ord('l'), curses.KEY_RIGHT, 10, 13):  # ENTER or l
            chosen = entries[selection]
            new_path = os.path.abspath(os.path.join(cwd, chosen))
            if os.path.isdir(new_path):
                cwd = new_path
                selection = 0
        elif key == ord('h'):
            # Go to parent directory
            parent = os.path.abspath(os.path.join(cwd, '..'))
            if parent != cwd:
                cwd = parent
                selection = 0
        elif key == ord(':'):
            run_shell_command(stdscr, cwd)
        # Ignore other keys

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        sys.exit(0)
