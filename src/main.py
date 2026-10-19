################ file: main.py
import os
from src.parser import parse_args
from config.settings import build_config
from src.helpers import (
    print_config,
    create_driver,
    ensure_logged_in,
)   

def main():
    cfg = build_config(vars(parse_args()))   # defaults + this run's overrides
    print_config(cfg)

    driver = create_driver(cfg)

    try:
        if not ensure_logged_in(driver, cfg):
            return

    finally:
        if cfg.detach:
            os._exit(0)
        else:
            driver.quit()

if __name__ == "__main__":
    main()
