from selenium.webdriver.common.by import By


class XLocators:
    LOGGED_IN = [
        (By.CSS_SELECTOR, '[data-testid="SideNav_AccountSwitcher_Button"]'),
        (By.CSS_SELECTOR, '[data-testid="AppTabBar_Home_Link"]'),
    ]
    LOGGED_OUT = [
        (By.CSS_SELECTOR, '[data-testid="loginButton"]'),
        (By.CSS_SELECTOR, '[data-testid="signupButton"]'),
        (By.CSS_SELECTOR, 'input[autocomplete="username"]'),
    ]
    LOGIN_URL_HINTS = ("/login", "/i/flow/login")


def any_displayed(driver, locators):
    """Return True if at least one locator in the group is displayed on the page."""
    return any(
        el.is_displayed()
        for by, value in locators
        for el in driver.find_elements(by, value)
    )