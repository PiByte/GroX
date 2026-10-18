################ file: conf.py

import os
from pathlib import Path
from dotenv import load_dotenv

# SET ENVIRONMENTAL VARIABLES

# BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(Path(__file__).parent / "grox.env")

X_URL = str(os.getenv("X_URL"))
X_HOME_URL = str(os.getenv("X_HOME_URL"))
X_USERNAME = str(os.getenv("X_USERNAME"))

PROFILE_PATH = str(os.getenv("PROFILE_PATH"))
DRIVER_EXECUTABLE_PATH = str(os.getenv("DRIVER_EXECUTABLE_PATH"))
BROWSER_EXECUTABLE_PATH = str(os.getenv("BROWSER_EXECUTABLE_PATH"))

VERSION_MAIN = int(str(os.getenv("VERSION_MAIN")))

PAGE_LOAD_STRATEGY = "normal"

ACCEPT_INSECURE_CERTS = False
STRICT_FILE_INTERACTABILITY = True
LOGIN_CHECK_TIMEOUT = 20 # Seconds

# UNSTABLE! - You may have problems working with it.
# # Setting the detach parameter to True will keep the browser open after the
# # process has ended so long as the quit command is not sent to the driver.
# DETACH = False