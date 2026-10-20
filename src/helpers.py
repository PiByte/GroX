import undetected_chromedriver as uc
from dataclasses import asdict
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
        'pageLoad': 15000,  # Maximum time to wait for a page to load.
        'script': 10000,    # Maximum time to wait for an asynchronous JavaScript script to finish.
        'implicit': 0,      # Must stay 0: we use explicit waits only (mixing both causes unpredictable delays).
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
        timeout=cfg.login_check_timeout,
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
    print(f"Login state: {state} ({reason})")

    if state == "logged_in":
        return True

    if state == "unknown":
        return False  # logging in by hand would not fix e.g. a network problem

    if not cfg.wait_for_login:
        if cfg.show_display:
            print("Not logged in (--no-wait-login is set).")
        else:
            print("Not logged in. Log in once by hand with: ./GroX.sh --display --wait-login")
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

def print_config(cfg):
    print("\n╔════════════════════════════════════ CURRENT CONFIG ════════════════════════════════════╗")
    for key, value in asdict(cfg).items():
        print(f"║ {key:<30} : {value}")
    print("╚════════════════════════════════════════════════════════════════════════════════════════╝\n")


# -------- 0. EXTRACT GENERAL DATA --------
# def extract_profile_stats(driver, username):
#     """
#     Extract profile-level stats that X already displays on the profile page
#     (post count, following count, followers count) - pure reading of what's
#     shown, no computation.
#     """

#     driver.get(f"https://x.com/{username}")

#     stats = {"posts": None, "following": None, "followers": None}

#     # Posts count usually appears near the top as "<number> posts"
#     try:
#         posts_el = driver.find_element(By.XPATH, '//span[contains(text(), "posts")]')
#         stats["posts"] = posts_el.text
#     except Exception:
#         pass

#     # Following count link: href ends with /following
#     try:
#         following_el = driver.find_element(By.XPATH, f'//a[@href="/{username}/following"]')
#         stats["following"] = following_el.text
#     except Exception:
#         pass

#     # Followers count link: href ends with /followers or /verified_followers
#     try:
#         followers_el = driver.find_element(By.XPATH, f'//a[@href="/{username}/followers"]')
#         stats["followers"] = followers_el.text
#     except Exception:
#         try:
#             followers_el = driver.find_element(By.XPATH, f'//a[@href="/{username}/verified_followers"]')
#             stats["followers"] = followers_el.text
#         except Exception:
#             pass

#     print("\n=== Profile Stats (as shown by X) ===")
#     print(f"Posts:     {stats['posts']}")
#     print(f"Following: {stats['following']}")
#     print(f"Followers: {stats['followers']}")
#     print("======================================\n")

#     return stats

# def extract_about_this_account(driver, username):
#     """
#     Navigates directly to x.com/<username>/about, which is the same panel
#     normally triggered by hovering "Joined <date>" on the profile - avoids
#     simulating an unreliable hover interaction in Selenium. Pure text
#     extraction of what's already displayed, no computation.
#     """
#     about_data = {
#         "joined": None,
#         "account_based_in": None,
#         "username_changes": None,
#         "last_username_change": None,
#         "connected_via": None,
#         "raw_lines": [],
#     }

#     try:
#         driver.get(f"https://x.com/{username}/about")
#         time.sleep(2)

#         # Content might render as a dialog overlay OR as a plain section on
#         # the page depending on how X serves this URL - try dialog first,
#         # fall back to the main content area.
#         container = None
#         try:
#             container = WebDriverWait(driver, 4).until(
#                 EC.presence_of_element_located((By.CSS_SELECTOR, '[role="dialog"]'))
#             )
#         except TimeoutException:
#             container = driver.find_element(By.CSS_SELECTOR, '[data-testid="primaryColumn"]')

#         lines = [l.strip() for l in container.text.split("\n") if l.strip()]
#         about_data["raw_lines"] = lines

#         for i, line in enumerate(lines):
#             if line.lower().startswith("joined"):
#                 about_data["joined"] = line.replace("Joined", "").strip()

#             elif "account based in" in line.lower():
#                 about_data["account_based_in"] = line.split(" in ", 1)[-1].strip()

#             elif re.search(r"\d+ username changes?", line, re.IGNORECASE):
#                 about_data["username_changes"] = line.strip()
#                 if i + 1 < len(lines) and lines[i + 1].lower().startswith("last on"):
#                     about_data["last_username_change"] = lines[i + 1].replace("Last on", "").strip()

#             elif line.lower().startswith("connected via"):
#                 about_data["connected_via"] = line.replace("Connected via", "").strip()

#     except Exception as e:
#         print(f"Could not extract 'About this account' info: {e}")

#     print("\n=== About This Account ===")
#     print(f"Joined:                {about_data['joined']}")
#     print(f"Account based in:      {about_data['account_based_in']}")
#     print(f"Username changes:      {about_data['username_changes']}")
#     print(f"Last username change:  {about_data['last_username_change']}")
#     print(f"Connected via:         {about_data['connected_via']}")
#     print("===========================\n")

#     return about_data
