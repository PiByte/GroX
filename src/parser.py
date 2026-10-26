import argparse


def build_parser():
    parser = argparse.ArgumentParser(prog="./GroX.bash", description="Grow your X account.")

    # Rules: default=None (so we can tell "not passed" from "passed"),
    # and dest must match a field name of Config.

    parser.add_argument(
        "--display", dest="show_display",
        action="store_true", default=None,
        help="show the real browser window (needed to log in by hand); without it the "
             "browser runs in a virtual display and --wait-login / --detach have no effect",
    )
    parser.add_argument(
        "--page-load", dest="page_load_strategy",
        choices=["normal", "eager"], default=None,
        help="normal: wait for full load | eager: return at DOMContentLoaded (faster)",
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
    parser.add_argument(
        "--wait-login", dest="wait_for_login",
        action=argparse.BooleanOptionalAction, default=None,
        help="wait for a manual login when logged out (needs --display); "
             "--no-wait-login exits instead",
    )
    parser.add_argument(
        "--detach", dest="detach",
        action=argparse.BooleanOptionalAction, default=None,
        help="keep the browser window open after the script finishes; the profile stays "
             "locked until you close it (needs --display)",
    )
    return parser


def parse_args():
    return build_parser().parse_args()