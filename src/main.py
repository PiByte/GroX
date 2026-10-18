################ file: main.py
from parser import parse_args
from config.settings import build_config
from src.helpers import (
    print_config,
    create_driver,
    detect_login_state,
)

def main():
    cfg = build_config(vars(parse_args()))   # defaults + this run's overrides
    print_config(cfg)

    driver = create_driver(cfg)
    try:
        state = detect_login_state(driver, cfg)
        if state != "logged_in":
            print(f"Login state: {state}. Run once WITHOUT xvfb-run to log in manually.")
            return
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
