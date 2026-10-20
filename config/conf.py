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
SHOW_DISPLAY                = False          # False: virtual display (CLI: --display shows the real window)
WAIT_FOR_LOGIN              = True           # only used with --display
DETACH                      = False          # only used with --display
WINDOW_SIZE                 = (1920, 1080)   # keep in sync with the screen size in GroX.sh
LOGIN_CHECK_TIMEOUT         = 20             # seconds
MANUAL_LOGIN_TIMEOUT        = 300            # seconds

PROFILE_PATH                = str(os.getenv("PROFILE_PATH"))
DRIVER_EXECUTABLE_PATH      = str(os.getenv("DRIVER_EXECUTABLE_PATH"))
BROWSER_EXECUTABLE_PATH     = str(os.getenv("BROWSER_EXECUTABLE_PATH"))
VERSION_MAIN                = int(str(os.getenv("VERSION_MAIN")))