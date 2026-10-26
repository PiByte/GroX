from typing import Any
from collections.abc import Mapping
import undetected_chromedriver as uc
from dataclasses import asdict, is_dataclass
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import (
    TimeoutException,
    StaleElementReferenceException,
)

from src.locators import (
    XLocators,
    any_displayed,
    any_present,
    is_on_x,
)


def create_driver(cfg):
    options = uc.ChromeOptions()

    options.platform_name = 'any'
    options.page_load_strategy = cfg.page_load_strategy
    # Strategy  Ready State   Notes
    # --------|-------------|---------------------------------------------------------------------------
    # normal    complete      Used by default, waits for all resources to download
    # --------|-------------|---------------------------------------------------------------------------
    # eager     interactive   DOM access is ready, but other resources like images may still be loading
    # --------|-------------|---------------------------------------------------------------------------
    # none      Any           Does not block WebDriver at all

    options.unhandled_prompt_behavior = 'dismiss and notify'

    # WE DO NOT NEED PROXY YET.
    # options.proxy = Proxy({ 'proxyType': ProxyType.MANUAL, 'httpProxy' : 'http.proxy:1234'})

    options.accept_insecure_certs = cfg.accept_insecure_certs
    options.strict_file_interactability = cfg.strict_file_interactability
    options.timeouts = {
    'pageLoad': cfg.timeout_long * 1000,    # Maximum time to wait for a page to load. W3C timeouts are milliseconds, config values are seconds.
    'script': cfg.timeout_medium * 1000,    # Maximum time to wait for an asynchronous JavaScript script to finish.
    'implicit': 0,                          # Must stay 0: we use explicit waits only (mixing both causes unpredictable delays).
    }

    width, height = cfg.window_size
    options.add_argument("--start-maximized")                # real display: fill the screen
    options.add_argument(f"--window-size={width},{height}")  # virtual display has no window manager, so maximize does nothing there

    if not cfg.show_display:
        # Chrome 140+ may pick Wayland by itself and ignore the virtual X11 display.
        options.add_argument("--ozone-platform=x11")

    # Persistent profile so login/cookies survive between runs (no need to log in every time)
    options.add_argument(f"--user-data-dir={cfg.profile_path}")
    options.add_argument("--profile-directory=Default")

    # Skip background component updates that slow down startup
    # options.add_argument("--disable-component-update")
    # options.add_argument("--disable-features=OptimizationHints,PrivacySandboxSettings4")
    # options.add_argument("--disable-background-networking")

    driver = uc.Chrome(
        options=options,
        driver_executable_path=cfg.driver_executable_path,
        browser_executable_path=cfg.browser_executable_path,
        version_main=cfg.version_main,
    )
    return driver

def safe_quit(driver):
    """Close the browser, ignoring errors if it is already gone (e.g. it also received Ctrl+C)."""
    try:
        driver.quit()
    except Exception:
        pass

def release_driver(driver):
    """Leave the browser window open when this program exits (--detach).

    undetected_chromedriver closes the browser in Chrome.__del__ (it calls self.quit()),
    so merely not calling driver.quit() is not enough. Replacing quit() on this instance
    turns that call into a no-op. __del__ still stops chromedriver, which Chrome does not need.
    """
    driver.quit = lambda: None
    
def raise_interrupt(signum, frame):
    """Turn SIGTERM (kill, systemd stop) into KeyboardInterrupt so the cleanup below runs."""
    raise KeyboardInterrupt

def detect_login_state(driver, cfg, navigate=True):
    """Return (state, reason). state: 'logged_in' | 'logged_out' | 'unknown'."""

    # navigate=False: never reload the page while the user is trying to log in.
    if navigate:
        try:
            driver.get(cfg.x_home_url)
        except TimeoutException:
            # The pageLoad timeout fired, but the page may still be usable;
            # let the wait below decide.
            pass

    def probe(d):
        # Blank/error page or unexpected redirect: conclude nothing.
        if not is_on_x(d.current_url):
            return False

        # No session cookie means we cannot be logged in.
        if d.get_cookie(XLocators.AUTH_COOKIE) is None:
            return "logged_out", "no auth_token cookie"

        # Logged-in UI is visible.
        if any_displayed(d, XLocators.LOGGED_IN):
            return "logged_in", "cookie and logged-in UI"

        # Logged-out UI is present.
        if any_present(d, XLocators.LOGGED_OUT):
            return "logged_out", "cookie but logged-out UI"

        return False

    wait = WebDriverWait(
        driver=driver,
        timeout=cfg.timeout_long,
        poll_frequency=0.5,
        ignored_exceptions=[StaleElementReferenceException],
    )

    try:
        return wait.until(probe, message="login state undetermined")
    except TimeoutException:
        return "unknown", f"timeout (last url: {driver.current_url})"

def ensure_logged_in(driver, cfg):
    """Return True once we are logged in; guide the user through a manual login if needed."""

    state, reason = detect_login_state(driver, cfg)
    print_box({"state": state, "reason": reason}, "Login State")

    if state == "logged_in":
        return True

    if state == "unknown":
        return False  # logging in by hand would not fix e.g. a network problem

    if not cfg.wait_for_login:
        if cfg.show_display:
            print("Not logged in (--no-wait-login is set).")
        else:
            print("Not logged in. Log in once by hand with: ./GroX.bash --display --wait-login")
        return False

    print(f"Please log in by hand in the browser window (waiting up to {cfg.manual_login_timeout}s)...")
    wait = WebDriverWait(driver, cfg.manual_login_timeout, poll_frequency=2)
    try:
        # navigate=False: never reload the page while the user is trying to log in.
        wait.until(lambda d: detect_login_state(d, cfg, navigate=False)[0] == "logged_in")
    except TimeoutException:
        print("Timed out waiting for the manual login.")
        return False

    print("Login detected.")
    return True

def print_box(data: Any, title: str | None = None) -> None:
    """Print a dict or a dataclass instance as a titled box.

    Raises TypeError for anything else.
    """

    BOX_WIDTH = 77

    if is_dataclass(data) and not isinstance(data, type):
        data = asdict(data)
    elif not isinstance(data, Mapping):
        raise TypeError(
            f"Cannot print {type(data).__name__}: expected a dict or a dataclass instance"
        )

    if title is None:
        header = f"".center(BOX_WIDTH, "═")
    else:
        header = f" {title} ".ljust(BOX_WIDTH, "═")
    print(f"\n╔══{header}")
    for key, value in data.items():
        print(f"║ {str(key):<30} : {value}")
    print(f"╚══{'═' * BOX_WIDTH}\n")
