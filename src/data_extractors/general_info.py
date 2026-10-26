import re
import urllib.request
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import (
    StaleElementReferenceException,
    TimeoutException,
)

from src.locators import ProfileLocators, AboutLocators
from config.conf import (
    X_URL, 
    DATA_DIR, 
    TIMEOUT_LONG, 
    TIMEOUT_MEDIUM, 
    TIMEOUT_SHORT,
    )

def open_profile(driver, username):
    """Navigate to x.com/<username>."""
    try:
        driver.get(f"{X_URL.rstrip('/')}/{username}")
    except TimeoutException:
        # The pageLoad timeout fired, but the page may still be usable;
        # the waits below decide.
        pass

def _wait_text(driver, locator):
    """Return (text, None), or (None, reason) if no text showed up in time."""
    wait = WebDriverWait(
        driver,
        timeout=TIMEOUT_SHORT,
        poll_frequency=0.5,
        ignored_exceptions=[StaleElementReferenceException],
    )
    try:
        # Reading the text inside the wait retries on stale elements automatically.
        text = wait.until(lambda d: d.find_element(*locator).text.strip() or False)
        return text, None
    except TimeoutException:
        return None, f"no text found within {TIMEOUT_SHORT}s"

def _wait_attr(driver, locator, attr):
    """Return (value, None), or (None, reason) if the attribute stayed empty."""
    wait = WebDriverWait(
        driver,
        timeout=TIMEOUT_SHORT,
        poll_frequency=0.5,
        ignored_exceptions=[StaleElementReferenceException],
    )
    try:
        value = wait.until(lambda d: d.find_element(*locator).get_attribute(attr) or False)
        return value, None
    except TimeoutException:
        return None, f"no '{attr}' found within {TIMEOUT_SHORT}s"

def _avatar_full_size(url):
    """Drop the size suffix (_200x200, _normal, ...) to get the original image."""
    return re.sub(r"_(mini|normal|bigger|\d+x\d+)(?=\.\w+$)", "", url)

def _banner_full_size(url):
    """Replace the trailing WxH (e.g. 1080x360) with the largest standard size."""
    return re.sub(r"/\d+x\d+$", "/1500x500", url)

def _download(url, dest_stem):
    """Download url to <dest_stem>.<ext> (ext from Content-Type). Return the path."""
    
    _CONTENT_TYPE_EXT = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
        "image/gif": ".gif",
    }

    dest_stem.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=TIMEOUT_MEDIUM) as resp:
        ext = _CONTENT_TYPE_EXT.get(resp.headers.get_content_type(), ".jpg")
        path = dest_stem.with_suffix(ext)
        path.write_bytes(resp.read())
    return path

def download_profile_media(driver, username):
    """Download the avatar and the banner into Data/<username>/.

    Call it while the profile page is open. Returns {"avatar": path, "banner": path};
    anything that failed is listed in result["missing"] with the reason.
    """

    result, missing = {}, {}
    folder = DATA_DIR / username.lower()

    jobs = {
        "avatar": (ProfileLocators.avatar_img(username), _avatar_full_size),
        "banner": (ProfileLocators.banner_img(username), _banner_full_size),
    }
    for key, (locator, upgrade) in jobs.items():
        url, reason = _wait_attr(driver, locator, "src")
        if url is None:
            missing[key] = reason
            continue
        try:
            result[key] = str(_download(upgrade(url), folder / key))
        except OSError as e:   # URLError/HTTPError are subclasses of OSError
            missing[key] = f"download failed: {e}"

    if missing:
        result["missing"] = missing
    return result

def extract_display_name(driver):
    """Return (name, None), or (None, reason). Emoji are kept, e.g. '🇮🇷 پـــای بــایـــت'."""
    
    # Walks the child nodes: text nodes give their text, emoji <img> nodes give their alt.
    _NAME_JS = """
    const walk = n => {
        if (n.nodeType === Node.TEXT_NODE) return n.textContent;
        if (n.nodeName === 'IMG') return n.alt || '';
        return Array.from(n.childNodes).map(walk).join('');
    };
    return walk(arguments[0]);
    """

    try:
        el = WebDriverWait(driver, TIMEOUT_SHORT).until(
            EC.presence_of_element_located(ProfileLocators.DISPLAY_NAME)
        )
        name = driver.execute_script(_NAME_JS, el).strip()
        return (name, None) if name else (None, "display name is empty")
    except TimeoutException:
        return None, f"no display name found within {TIMEOUT_SHORT}s"

def open_about(driver, username):
    """Navigate to x.com/<username>/about."""
    try:
        driver.get(f"{X_URL.rstrip('/')}/{username}/about")
    except TimeoutException:
        # The pageLoad timeout fired, but the page may still be usable;
        # the waits below decide.
        pass

def _row_lines(driver, locator):
    """Return the text lines of a row on the about page, or None if the row is absent."""
    
    # Returns the text of the title line and the detail line of one row.
    _ROW_LINES_JS = """
    return Array.from(arguments[0].querySelectorAll('div[dir="ltr"]'))
                .map(d => d.innerText.trim());
    """
    
    rows = driver.find_elements(*locator)
    if not rows:
        return None
    return driver.execute_script(_ROW_LINES_JS, rows[0])

def extract_about_info(driver, username):
    """Return the info shown on x.com/<username>/about.

    Every value is exactly the text X displays (e.g. "Germany", "2 username changes").
    A row X does not show (e.g. an account that never changed its username) is left out.
    Fields that could not be read are listed in result["missing"] with the reason.
    """
    open_about(driver, username)

    info = {"username": username}

    # Wait until at least one row is there; all rows are rendered together.
    try:
        WebDriverWait(driver, TIMEOUT_LONG).until(
            EC.presence_of_element_located(AboutLocators.ROW)
        )
    except TimeoutException:
        info["missing"] = {"about": f"no info rows found within {TIMEOUT_LONG}s"}
        return info

    lines = _row_lines(driver, AboutLocators.row_by_icon(AboutLocators.ICON_ACCOUNT_BASED_IN))
    if lines and len(lines) > 1:
        info["account_based_in"] = lines[1]          # title is the fixed label

    lines = _row_lines(driver, AboutLocators.row_by_icon(AboutLocators.ICON_USERNAME_CHANGES))
    if lines:
        info["username_changes"] = lines[0]          # e.g. "2 username changes"
        if len(lines) > 1:
            info["username_last_change"] = lines[1]  # e.g. "Last on July 2025"

    lines = _row_lines(driver, AboutLocators.row_by_icon(AboutLocators.ICON_CONNECTED_VIA))
    if lines and len(lines) > 1:
        info["connected_via"] = lines[1]

    return info

def extract_profile_info(driver, username):
    """Return the public info shown on x.com/<username>.

    Every value is exactly the text X displays (e.g. "1,919 posts", "1.2K").
    "error" holds X's own message when the account page cannot be shown
    (e.g. the account does not exist); no other field is read then.
    Fields that could not be read are listed in result["missing"] with the reason.
    The claimed location is left out entirely when the account has none.
    "username" is the one we asked for, not one read from the page.
    """
    open_profile(driver, username)

    info = {"username": username}

    # Gate: wait for whichever shows up first, the profile header or X's empty-state
    # page. Anything else (suspended account, network problem) ends in the timeout
    # below instead of waiting for every field separately.
    try:
        WebDriverWait(driver, TIMEOUT_LONG).until(
            EC.any_of(
                EC.presence_of_element_located(ProfileLocators.HEADER_ITEMS),
                EC.presence_of_element_located(ProfileLocators.EMPTY_STATE),
            )
        )
    except TimeoutException:
        info["missing"] = {"profile": f"header not found within {TIMEOUT_LONG}s"}
        return info

    # No header means we are on the empty-state page: show X's message as it is.
    if not driver.find_elements(*ProfileLocators.HEADER_ITEMS):
        text, reason = _wait_text(driver, ProfileLocators.EMPTY_STATE_HEADER)
        info["error"] = text or reason
        return info

    fields = {
        "posts": ProfileLocators.POSTS,
        "following": ProfileLocators.following_count(username),
        "followers": ProfileLocators.followers_count(username),
        "joined": ProfileLocators.JOIN_DATE,
    }

    missing = {}
    for key, locator in fields.items():
        
        text, reason = _wait_text(driver, locator)
        if text is None:
            missing[key] = reason
        else:
            info[key] = text

    name, reason = extract_display_name(driver)
    if name is None:
        missing["name"] = reason
    else:
        info["name"] = name

    # Optional item: find_elements returns [] instead of waiting when it is absent.
    for el in driver.find_elements(*ProfileLocators.LOCATION):
        if el.text.strip():
            info["location"] = el.text.strip()
        
    media = download_profile_media(driver, username)
    info["avatar"] = media.get("avatar")
    info["banner"] = media.get("banner")
    missing.update(media.get("missing", {}))

    if missing:
        info["missing"] = missing
    return info

def extract_info(driver, username):
    """Return the profile info and the about info of an account in one dict."""
    info = extract_profile_info(driver, username)
    if "error" in info:
        return info   # no such account: the about page has nothing to read

    about = extract_about_info(driver, username)
    missing = {**info.pop("missing", {}), **about.pop("missing", {})}
    info.update(about)

    if missing:
        info["missing"] = missing
    return info