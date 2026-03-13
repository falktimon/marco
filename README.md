# marco

A minimal terminal file explorer.

## Installation

```bash
curl -sSL https://raw.githubusercontent.com/falktimon/marco/main/install.sh | sh
```

Or manually:

```bash
git clone https://github.com/falktimon/marco.git
cd marco
make install  # may require sudo
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
| `:`     | Run shell command             |
| `q`/`Esc`| Quit                         |

## Features

**Selection & Clipboard** - Select files with `Space`, then copy (`c`) or cut (`x`) and paste (`p`) elsewhere. Copying in the same directory creates duplicates with `_copy` suffix.

**Shell Commands** - Press `:` to run any shell command in the current directory. Output is displayed in the terminal.

**Half-page Navigation** - Use `u`/`d` to jump multiple entries at once.

## Configuration

Create `~/.config/marco/marco.toml`:

```toml
[colors]
bg = "default"
fg = "white"
highlight_fg = "black"
highlight_bg = "cyan"

padding = 2
editor = null  # uses $EDITOR, $VISUAL, or vi

[keybindings]
select = " "
copy = "c"
cut = "x"
paste = "p"
page_up = "u"
page_down = "d"
quit = "q"
```

