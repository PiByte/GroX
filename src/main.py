import sys
import signal
from src.parser import parse_args
from config.settings import build_config
from src.data_extractors.general_info import extract_info
from src.helpers import (
    print_box,
    create_driver,
    ensure_logged_in,
    release_driver,
    safe_quit,
    raise_interrupt,
)


def main():
    cfg = build_config(vars(parse_args()))   # defaults + this run's overrides
    print_box(cfg, "Current Config")

    signal.signal(signal.SIGTERM, raise_interrupt)

    driver = create_driver(cfg)
    
    try:
        if not ensure_logged_in(driver, cfg):
            return 1
        
        info = extract_info(driver, cfg.x_username)
        print_box(info, "General Info")
        
        if "error" in info:
            return 2
 
        return 0
    finally:
        if cfg.detach:
            release_driver(driver)   # keep the browser window open
        else:
            safe_quit(driver)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nInterrupted (Ctrl+C or SIGTERM): cleaned up, exiting.")
        sys.exit(130)   # 128 + SIGINT(2): the conventional exit code for Ctrl+C