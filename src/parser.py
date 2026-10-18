import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="grox")

    # Rules: default=None (so we can tell "not passed" from "passed"),
    # and dest must match a field name of Config.

    parser.add_argument(
        "--page-load", dest="page_load_strategy",
        choices=["normal", "eager"], default=None,
        help="normal: wait for full load | eager: return at DOMContentLoaded (faster)",
    )
    parser.add_argument(
        "--login-timeout", dest="login_check_timeout",
        type=int, default=None,
        help="seconds to wait when detecting the login state",
    )
    parser.add_argument(
        "--username", dest="x_username", default=None,
        help="X username to use for this run",
    )
    parser.add_argument(
        "--insecure-certs", dest="accept_insecure_certs",
        action=argparse.BooleanOptionalAction, default=None,
        help="accept insecure TLS certificates for this run",
    )
    return parser.parse_args()
