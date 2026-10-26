#!/usr/bin/env bash
# Run grox. By default the browser runs in a virtual display (no visible window).
# Usage: ./GroX.bash [--display] [grox options...]
#   --display   show the real browser window (manual login, development, --detach)
# Every argument is passed to grox unchanged; this script only looks at them.
set -euo pipefail
cd "$(dirname "$0")"          # always run from the project root

PYTHON=Xvenv/bin/python3

# Does the caller want the real display? (--help needs no virtual display either.)
use_real_display=0
for arg in "$@"; do
    case "$arg" in
        --display|-h|--help) use_real_display=1 ;;
    esac
done

if [[ $use_real_display -eq 1 ]]; then
    exec "$PYTHON" -m src.main "$@"
fi

# Virtual display. Keep the screen size in sync with WINDOW_SIZE in config/conf.py.
exec xvfb-run -a -s "-screen 0 1920x1080x24" "$PYTHON" -m src.main "$@"