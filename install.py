"""Script to install all dependencies listed in requirements.txt using launch utilities (WebUI)."""

import os

import launch


def main() -> None:
    """Install all packages from requirements.txt using pip."""
    req_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "requirements.txt")
    if not os.path.exists(req_file):
        raise FileNotFoundError(f"requirements.txt not found at {req_file}")
    launch.run_pip(f"install -r {req_file}", f"requirements from {req_file}")


if __name__ == "__main__":
    main()
