from config.conf import X_URL
from urllib.parse import urlparse
from selenium.webdriver.common.by import By


_UPPER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
_LOWER = _UPPER.lower()

class XLocators:
    # Present only in the logged-in app shell (data-testid is language-independent).
        LOGGED_IN = [
            (By.CSS_SELECTOR, '[data-testid="SideNav_AccountSwitcher_Button"]'),
        ]
        # Icons of the login buttons on the logged-out landing page (weak signal).
        LOGGED_OUT = [
            (By.CSS_SELECTOR, 'svg[data-icon="icon-logo-apple"]'),
            (By.CSS_SELECTOR, 'svg[data-icon="icon-logo-google"]'),
            (By.CSS_SELECTOR, 'svg[data-icon="icon-phone-stroke"]'),
        ]
        AUTH_COOKIE = "auth_token"


class ProfileLocators:
    """Locators for a profile page (x.com/<username>).

    Anchored on data-testid / href only: the CSS classes are auto-generated and change often.
    """

    # Wait for this container, then read the optional items below with find_elements.
    HEADER_ITEMS = (By.XPATH, "//*[@data-testid='UserProfileHeader_Items']")
    # Optional: absent when the account has not set a location.
    LOCATION = (By.XPATH, "//*[@data-testid='UserLocation']")
    # Text looks like "Joined May 2025" (month and year only, language of the UI).
    JOIN_DATE = (By.XPATH, "//*[@data-testid='UserJoinDate']")
    # It has no stable attribute, so it is anchored on structure inside primaryColumn:
    POSTS = (By.XPATH,"//*[@data-testid='primaryColumn']//h2[@role='heading']/following-sibling::div[1]",)
    # Shown instead of the profile when the account does not exist.
    EMPTY_STATE = (By.XPATH, "//*[@data-testid='emptyState']")
    # Its message exactly as X displays it, e.g. "This account doesn’t exist".
    EMPTY_STATE_HEADER = (By.XPATH, "//*[@data-testid='empty_state_header_text']")
    # Display name block: contains the name and the @handle.
    # The first dir=ltr div inside it holds the display name (text + emoji images).
    DISPLAY_NAME = (By.XPATH, "(//*[@data-testid='UserName']//div[@dir='ltr'])[1]")

    @staticmethod
    def following_count(username):
        return (By.XPATH, f"//a[{_href_is(username, 'following')}]/span[1]/span")

    @staticmethod
    def followers_count(username):
        # X links followers to /verified_followers; plain /followers does not exist in the DOM.
        return (By.XPATH, f"//a[{_href_is(username, 'verified_followers')}]/span[1]/span")

    @staticmethod
    def avatar_img(username):
        # When no profile chosed, the account has X's default.
        return (By.XPATH, f"//a[{_href_is(username, 'photo')}]//img")

    @staticmethod
    def banner_img(username):
        # Optional: absent when the account has no banner.
        return (By.XPATH, f"//a[{_href_is(username, 'header_photo')}]//img")

class AboutLocators:
    """Locators for the about page (x.com/<username>/about).

    Every row is a data-testid="pivot" tab with an icon, a title line and a detail line.
    The texts are in the UI language and the CSS classes change often, so a row is found
    by the beginning of its icon path (language independent).
    """

    # Any row: used to know the page has loaded.
    ROW = (By.CSS_SELECTOR, '[data-testid="pivot"]')

    # Beginning of the "d" attribute of each row's icon.
    ICON_ACCOUNT_BASED_IN = "M12 7c-1.93"       # location pin
    ICON_USERNAME_CHANGES = "M12 3.786c-4.556"  # "@" sign
    ICON_CONNECTED_VIA = "M12.25 2C6.59"        # globe

    @staticmethod
    def row_by_icon(icon_prefix):
        return (By.CSS_SELECTOR, f'[data-testid="pivot"]:has(path[d^="{icon_prefix}"])')

def any_displayed(driver, locators):
    """Return True if at least one locator in the group is displayed on the page."""
    return any(
        el.is_displayed()
        for by, value in locators
        for el in driver.find_elements(by, value)
    )

def any_present(driver, locators):
    """Return True if at least one locator in the group exists in the DOM (visible or not)."""
    return any(driver.find_elements(by, value) for by, value in locators)

def is_on_x(url):
    """Return True if the URL belongs to x.com (not a blank or browser error page)."""
    x_host = urlparse(X_URL).hostname   # extract "x.com" from "https://x.com" 
    host = urlparse(url).hostname or ""
    return host == x_host or host.endswith(f".{x_host}")

def _href_is(username, suffix):
    """XPath predicate: @href equals /<username>/<suffix>, ignoring letter case.

    X usernames only contain letters, digits and underscore, so they are safe inside an XPath string.
    """
    target = f"/{username}/{suffix}".lower()
    return f"translate(@href, '{_UPPER}', '{_LOWER}')='{target}'"

