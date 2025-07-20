"""pytest fixtures and utility functions for testing."""

import builtins
import os
import tempfile
from collections.abc import Generator
from typing import Any

import pytest

# Patch open to raise OSError only when writing the report file
original_open = builtins.open


@pytest.fixture
def github_output_path() -> Generator[str, None, None]:
    """Creates a temporary file for GITHUB_OUTPUT and cleans it up after the test."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmpfile:
        os.environ["GITHUB_OUTPUT"] = tmpfile.name
        yield tmpfile.name  # Type: str
    # Cleanup after test
    if os.path.exists(tmpfile.name):
        os.remove(tmpfile.name)
    os.environ.pop("GITHUB_OUTPUT", None)


@pytest.fixture(autouse=True)
def cleanup_report_file() -> None:
    """Remove the report file if it exists."""
    if "DAILY_REPORT_FILENAME" in os.environ:
        filename = os.environ.get("DAILY_REPORT_FILENAME")
        if filename is not None:
            filename = filename.strip()
            if os.path.exists(filename):
                os.remove(filename)


def valid_env(
    github_output_path: str | None = None,  # pylint: disable=redefined-outer-name
) -> dict[str, str]:
    """Return a valid environment variable dictionary for testing."""
    fake_env = {
        "GITHUB_TOKEN": "token",
        "REPO_NAME": "owner/repo",
        "EMAIL_SENDER": "sender@example.com",
        "EMAIL_USER": "sender@example.com",
        "EMAIL_RECEIVER": "receiver@example.com",
        "EMAIL_PASSWORD": "pw",
        "OPENAI_API_KEY": "sk-xxx",
        "SMTP_SERVER": "smtp.example.com",
        "SMTP_PORT": "587",
    }
    if github_output_path is not None:
        fake_env["GITHUB_OUTPUT"] = github_output_path
    return fake_env


def patched_open(
    file: str, *args: object, mode: str = "r", **kwargs: object
) -> Generator[str, None, None]:
    """Open function that raises OSError only for the report file."""
    # Only raise OSError when trying to write the report file
    report_filename = os.environ.get("DAILY_REPORT_FILENAME")
    if report_filename and file == report_filename and "w" in mode:
        raise OSError("Simulated write error for report file")
    return original_open(file, mode, *args, **kwargs)  # type: ignore


def selective_open_github_output_path(file: str, *args: Any, **kwargs: Any) -> Any:
    """Open function that raises OSError only for GITHUB_OUTPUT, but only once."""
    # Use an environment variable as a flag to track if OSError was already raised
    if file == os.environ.get("GITHUB_OUTPUT"):
        if not os.environ.get("OSERROR_RAISED"):
            os.environ["OSERROR_RAISED"] = "1"
            raise OSError("Disk error")
    return original_open(file, *args, **kwargs)  # type: ignore


def selective_open(file: str, *args: Any, **kwargs: Any) -> Any:
    """Open function that raises OSError for specific files."""
    # Use the original open function for all other files
    # Ensure correct types for open arguments
    mode = kwargs.get("mode", args[0] if args else "r")
    if not isinstance(mode, str):
        mode = str(mode)
    buffering = kwargs.get("buffering", args[1] if len(args) > 1 else -1)
    if not isinstance(buffering, int):
        try:
            buffering = int(buffering)
        except (ValueError, TypeError):
            buffering = -1
    kwargs["mode"] = mode
    kwargs["buffering"] = buffering
    # Simulate error only for the report file, not for GITHUB_OUTPUT
    if file.endswith(".md") and "GITHUB_OUTPUT" not in file:
        raise OSError("Disk error")
    return original_open(file, **kwargs)  # type: ignore
