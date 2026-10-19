################ file: conf.py

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / "grox.env")

X_URL      = "https://x.com"
X_HOME_URL = "https://x.com/home"
X_USERNAME = "XPiByte"      # without the @

PAGE_LOAD_STRATEGY          = "normal"
ACCEPT_INSECURE_CERTS       = False
STRICT_FILE_INTERACTABILITY = True
WAIT_FOR_LOGIN              = True
DETACH                      = False
LOGIN_CHECK_TIMEOUT         = 20    # Seconds
MANUAL_LOGIN_TIMEOUT        = 300   # seconds

PROFILE_PATH                = str(os.getenv("PROFILE_PATH"))
DRIVER_EXECUTABLE_PATH      = str(os.getenv("DRIVER_EXECUTABLE_PATH"))
BROWSER_EXECUTABLE_PATH     = str(os.getenv("BROWSER_EXECUTABLE_PATH"))
VERSION_MAIN                = int(str(os.getenv("VERSION_MAIN")))
