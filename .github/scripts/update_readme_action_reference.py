"""This script updates the `README.md` file to reference the latest tag of the GitHub Action.
It finds the line that uses the action and replaces it with the latest tag and SHA.
It assumes the action is referenced in the format `uses: jfheinrich-eu/github-daily-report@<tag>`.
The script is intended to be run in a GitHub Actions workflow or locally in a repository where the action is defined.
"""

import re
import subprocess
from pathlib import Path

README = Path("README.md")
ACTION = "jfheinrich-eu/github-daily-report"


def get_latest_tag() -> str:
    """Get the latest tag from the git repository."""
    # Use git describe to get the latest tag, which is the most recent annotated tag
    # The --abbrev=0 option gives the tag name without the commit hash
    # If there are no tags, this will raise an error, which we can handle if needed
    try:
        tag = (
            subprocess.check_output(["git", "describe", "--tags", "--abbrev=0"])
            .decode()
            .strip()
        )
    except subprocess.CalledProcessError:
        print("No tags found in the repository.")
        raise RuntimeError(
            "Cannot determine the latest tag. Please create a tag first."
        )
    tag = (
        subprocess.check_output(["git", "describe", "--tags", "--abbrev=0"])
        .decode()
        .strip()
    )
    return tag


def get_tag_sha(tag: str) -> str:
    """Get the SHA of the given tag."""
    # Use git rev-list to get the commit SHA for the given tag
    # This will return the SHA of the commit that the tag points to
    try:
        sha = subprocess.check_output(["git", "rev-list", "-n", "1", tag])
    except subprocess.CalledProcessError:
        print(f"Tag '{tag}' not found in the repository.")
        raise RuntimeError(
            f"Cannot find SHA for tag '{tag}'. Please check the tag name."
        )
    # Decode the output and strip any extra whitespace
    sha = subprocess.check_output(["git", "rev-list", "-n", "1", tag]).decode().strip()
    return sha


def main():
    """Main function to update the README.md with the latest action tag."""
    # Get the latest tag and its SHA
    tag = get_latest_tag()
    sha = get_tag_sha(tag)
    new_line = f"  uses: {ACTION}@{sha}  # {tag}\n"

    content = README.read_text().splitlines(keepends=True)
    pattern = re.compile(rf"\s*uses:\s*{re.escape(ACTION)}@.*")
    changed = False
    for i, line in enumerate(content):
        if pattern.match(line):
            content[i] = new_line
            changed = True
            break
    if changed:
        README.write_text("".join(content))
        print(f"README.md updated to {new_line.strip()}")
    else:
        print("No matching line found in README.md.")


if __name__ == "__main__":
    # Ensure the script is run in a git repository
    if not Path(".git").exists():
        raise RuntimeError("This script must be run in a git repository.")
    main()
