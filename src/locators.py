from config.conf import X_URL
from urllib.parse import urlparse
from selenium.webdriver.common.by import By


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
    X_HOST = urlparse(X_URL).hostname   # extract "x.com" from "https://x.com" 
    """Return True if the URL belongs to x.com (not a blank or browser error page)."""
    host = urlparse(url).hostname or ""
    return host == X_HOST or host.endswith(f".{X_HOST}")