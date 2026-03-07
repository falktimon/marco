# `marco`: A minimal file browser for the terminal

[![asciicast](https://asciinema.org/a/tj6uL7OpnDYYuZou.svg)](https://asciinema.org/a/tj6uL7OpnDYYuZou)

A lightweight file explorer written in Python with curses.

## Features

- **Navigation**: `j/k` or arrow keys to move, `h/l` to go up/down directories, Enter to open files
- **Selection**: Press `Space` to select files (marked with `[*]`)
- **Clipboard**: `c` to copy, `x` to cut, `p` to paste selected files
- **Copy in same directory**: Creates duplicates with `_copy` suffix
- **Shell commands**: Press `:` to run shell commands in current directory
- **Editor integration**: Opens files in `$EDITOR` or `vi`
- **Customizable colors**: Set foreground/background/highlight colors
- **Keybindings**: All navigation and action keys are configurable

## Installation

### Via curl (recommended)

```bash
curl -sSL https://raw.githubusercontent.com/falktimon/marco/main/install.sh | sh
```

### Manual installation

```bash
git clone https://github.com/falktimon/marco.git && cd marco && make install
```

Some systems may require `sudo make install`.

## Configuration

Create `~/.config/marco/marco.toml` or `./marco.toml`:

```toml
[colors]
bg = "default"         # Terminal background
fg = "white"
highlight_fg = "black"
highlight_bg = "cyan"

padding = 2
editor = null          # Use $EDITOR or vi

[keybindings]
select = " "
copy = "c"
cut = "x"
paste = "p"
page_up = "u"
page_down = "d"
quit = "q"
```

## Keybindings

| Key     | Action                        |
|---------|-------------------------------|
| `j`/`↓` | Move down                     |
| `k`/`↑` | Move up                       |
| `u`     | Scroll up half a page         |
| `d`     | Scroll down half a page       |
| `h`     | Go to parent directory        |
| `l`/`→` | Open directory / edit file    |
| `Space` | Toggle selection              |
| `c`     | Copy selected files           |
| `x`     | Cut selected files            |
| `p`     | Paste files                   |
| `:`     | Run shell command            |
| `q`/`Esc`| Quit                         |

## Uninstall

```bash
sudo rm /usr/local/bin/marco
```