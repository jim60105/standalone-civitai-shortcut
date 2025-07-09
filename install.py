"""Script to install all dependencies listed in requirements.txt using launch utilities (WebUI)."""

import os
import re

import launch


def parse_requirements(file_path: str) -> list[str]:
    """Parse requirements.txt and return a list of requirement strings."""
    requirements: list[str] = []
    with open(file_path, encoding="utf-8") as req_file:
        for line in req_file:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            requirements.append(line)
    return requirements


def get_package_name(requirement: str) -> str:
    """Extract the package name from a requirement specifier."""
    # Split off version specifiers and extras
    name = re.split(r"[<>=\[\]]", requirement, 1)[0]
    return name.strip()


def main() -> None:
    """Install missing packages from requirements.txt."""
    req_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "requirements.txt")

    reqs = parse_requirements(req_file)
    for req in reqs:
        pkg = get_package_name(req)
        if not launch.is_installed(pkg):
            launch.run_pip(f"install {req}", f"requirements dependency {req}")


if __name__ == "__main__":
    main()
