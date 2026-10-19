from dataclasses import dataclass, replace
from typing import Any
from config import conf


@dataclass(frozen=True)
class Config:
    """Immutable runtime config. Defaults come from conf.py."""
    x_url: str = conf.X_URL
    x_home_url: str = conf.X_HOME_URL
    x_username: str = conf.X_USERNAME
    profile_path: str = conf.PROFILE_PATH
    driver_executable_path: str = conf.DRIVER_EXECUTABLE_PATH
    browser_executable_path: str = conf.BROWSER_EXECUTABLE_PATH
    version_main: int = conf.VERSION_MAIN
    page_load_strategy: str = conf.PAGE_LOAD_STRATEGY
    accept_insecure_certs: bool = conf.ACCEPT_INSECURE_CERTS
    strict_file_interactability: bool = conf.STRICT_FILE_INTERACTABILITY
    login_check_timeout: int = conf.LOGIN_CHECK_TIMEOUT
    detach: bool = conf.DETACH
    wait_for_login: bool = conf.WAIT_FOR_LOGIN
    manual_login_timeout: int = conf.MANUAL_LOGIN_TIMEOUT


def build_config(overrides: dict[str, Any]) -> Config:
    """Return the default config with the given overrides applied.

    Keys whose value is None are ignored (None means "the user did not pass it").
    """
    changes = {key: value for key, value in overrides.items() if value is not None}
    return replace(Config(), **changes)