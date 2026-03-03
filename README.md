# `marco`: A minimal file browser for the terminal

[![asciicast](https://asciinema.org/a/tj6uL7OpnDYYuZou.svg)](https://asciinema.org/a/tj6uL7OpnDYYuZou)

- Currently under 170SLOC of Python (will never exceed 250SLOC)
- Editor integration similar to other file browsers
- Can execute common Bash commands for file management without leaving the terminal
- Configurable via a `.toml` file under `~/.config/marco`

## Installation

Under `linux`, clone the repository and run `make install`:

```bash
git clone https://github.com/falktimon/marco/tree/main && cd marco && make install
```

Some users might have to run `sudo make install`. Other operating systems have not been tested.
