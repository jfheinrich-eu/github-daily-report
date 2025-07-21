"""Unit test for verifying GitHub Actions output file integration in DailyReporter."""

import os
from unittest.mock import MagicMock, patch

import pytest

from daily_report.daily_reporter import DailyReporter
from tests.conftest import valid_env


@patch("daily_report.daily_reporter.check_env_vars")
@patch("daily_report.daily_reporter.Github")
@patch("daily_report.daily_reporter.OpenAI")
@patch("daily_report.daily_reporter.smtplib.SMTP")
def test_github_output_written(
    mock_smtp: MagicMock,  # pylint: disable=unused-argument
    mock_openai: MagicMock,
    mock_github: MagicMock,
    mock_check_env_vars: MagicMock,
    github_output_path: str,  # pylint: disable=redefined-outer-name
) -> None:
    """Test that the GitHub Actions output file is written with the report content."""
    env = valid_env(github_output_path=github_output_path)
    for k, v in env.items():
        os.environ[k] = v
    mock_check_env_vars.return_value = env

    mock_repo = MagicMock()
    mock_commit = MagicMock()
    mock_commit.commit.message = "test"
    mock_commit.commit.author.name = "author"
    mock_commit.html_url = "http://example.com"
    mock_commit.sha = "sha"
    mock_commit.commit.author.date = "2024-01-01"
    mock_repo.get_commits.return_value = [mock_commit]
    mock_github.return_value.get_repo.return_value = mock_repo

    mock_openai.return_value.chat.completions.create.return_value.choices = [
        MagicMock(message=MagicMock(content="Test-Report"))
    ]

    reporter = DailyReporter()
    with pytest.raises(SystemExit):
        reporter.run()
    with open(github_output_path, encoding="utf-8") as tmpfile:
        # Check if the report content is written to the GITHUB_OUTPUT file
        tmpfile.seek(0)
        content = tmpfile.read()
        assert "Test-Report" in content


@patch("daily_report.daily_reporter.check_env_vars")
@patch("daily_report.daily_reporter.Github")
@patch("daily_report.daily_reporter.OpenAI")
@patch("daily_report.daily_reporter.smtplib.SMTP")
def test_multiline_github_output(
    mock_smtp: MagicMock,  # pylint: disable=unused-argument
    mock_openai: MagicMock,
    mock_github: MagicMock,
    mock_check_env_vars: MagicMock,
    github_output_path: str,  # pylint: disable=redefined-outer-name
) -> None:
    """Test that DailyReporter.run writes multi-line output to GITHUB_OUTPUT."""
    env = valid_env(github_output_path=github_output_path)
    for k, v in env.items():
        os.environ[k] = v
    mock_check_env_vars.return_value = env

    mock_repo = MagicMock()
    mock_commit = MagicMock()
    mock_commit.commit.message = "fix: bug"
    mock_commit.commit.author.name = "dev"
    mock_commit.html_url = "http://example.com"
    mock_commit.sha = "abc1234"
    mock_commit.commit.author.date = "2024-01-01"
    mock_repo.get_commits.return_value = [mock_commit]
    mock_github.return_value.get_repo.return_value = mock_repo

    mock_openai.return_value.chat.completions.create.return_value.choices = [
        MagicMock(message=MagicMock(content="Test-Report"))
    ]

    reporter = DailyReporter()
    with pytest.raises(SystemExit):
        reporter.run()

    # Check multi-line output format in GITHUB_OUTPUT
    with open(github_output_path, encoding="utf-8") as f:
        content = f.read()
        assert "report<<EOF" in content
        assert "Test-Report" in content
        assert "\nEOF" in content
