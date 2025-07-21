"""Unit tests for the DailyReporter class and environment validation."""

import builtins
import os
import smtplib
from unittest.mock import MagicMock, patch

import pytest

from daily_report.daily_reporter import DailyReporter
from daily_report.env_check import EnvCheckError
from tests.conftest import selective_open, selective_open_github_output_path, valid_env


@patch("daily_report.daily_reporter.check_env_vars")
@patch("daily_report.daily_reporter.Github")
@patch("daily_report.daily_reporter.OpenAI")
# @patch("daily_report.daily_reporter.open")
def test_run_sends_email(
    # mock_open: MagicMock,
    mock_openai: MagicMock,
    mock_github: MagicMock,
    mock_check_env_vars: MagicMock,
    github_output_path: str,  # pylint: disable=redefined-outer-name
) -> None:
    """Test that DailyReporter.run sends an email and writes the report file."""
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

    # mock_open.return_value.__enter__.return_value = MagicMock()

    with (
        patch("builtins.print"),
        patch("sys.exit", side_effect=SystemExit) as mock_exit,
    ):
        with pytest.raises(SystemExit):
            with patch("daily_report.daily_reporter.smtplib.SMTP"):
                reporter = DailyReporter()
                reporter.run()
        mock_exit.assert_called_once()
        with open(github_output_path, encoding="utf-8") as f:
            content = f.read()
            assert "report" in content


@patch("daily_report.daily_reporter.check_env_vars")
@patch("daily_report.daily_reporter.Github")
@patch("daily_report.daily_reporter.OpenAI")
def test_analyze_commits_with_gpt_empty(
    mock_openai: MagicMock,  # pylint: disable=unused-argument
    mock_github: MagicMock,  # pylint: disable=unused-argument
    mock_check_env_vars: MagicMock,  # pylint: disable=unused-argument
    github_output_path: str,  # pylint: disable=unused-argument,redefined-outer-name
) -> None:
    """Test analyze_commits_with_gpt returns correct message for empty commit list."""
    env = valid_env()
    for k, v in env.items():
        os.environ[k] = v
    mock_check_env_vars.return_value = env
    reporter = DailyReporter()
    result = reporter.analyze_commits_with_gpt([])
    assert "No commits" in result


@patch("daily_report.daily_reporter.check_env_vars")
@patch("daily_report.daily_reporter.Github")
@patch("daily_report.daily_reporter.OpenAI")
def test_analyze_commits_with_gpt_empty_response(
    mock_openai: MagicMock,
    mock_github: MagicMock,  # pylint: disable=unused-argument
    mock_check_env_vars: MagicMock,  # pylint: disable=unused-argument
    github_output_path: str,  # pylint: disable=unused-argument,redefined-outer-name
) -> None:
    """Test analyze_commits_with_gpt returns correct message for empty GPT response."""
    env = valid_env()
    for k, v in env.items():
        os.environ[k] = v
    mock_check_env_vars.return_value = env
    mock_openai.return_value.chat.completions.create.return_value.choices = [
        MagicMock(message=MagicMock(content=None))
    ]
    reporter = DailyReporter()
    commits: list[dict[str, str]] = [
        {"sha": "abc", "message": "msg", "author": "a", "url": "", "date": ""}
    ]
    result = reporter.analyze_commits_with_gpt(commits)
    assert "No summary generated" in result


@patch("daily_report.daily_reporter.check_env_vars")
@patch("daily_report.daily_reporter.Github")
@patch("daily_report.daily_reporter.OpenAI")
def test_send_email_password_missing(
    mock_openai: MagicMock,  # pylint: disable=unused-argument
    mock_github: MagicMock,  # pylint: disable=unused-argument
    mock_check_env_vars: MagicMock,  # pylint: disable=unused-argument
    github_output_path: str,  # pylint: disable=unused-argument,redefined-outer-name
) -> None:
    """Test send_email raises ValueError if EMAIL_PASSWORD is missing."""
    env = valid_env()
    env["EMAIL_PASSWORD"] = ""
    for k, v in env.items():
        os.environ[k] = v
    mock_check_env_vars.return_value = env
    reporter = DailyReporter()
    with patch("daily_report.daily_reporter.smtplib.SMTP"):
        with pytest.raises(ValueError):
            reporter.send_email("subject", "body")


@patch("daily_report.daily_reporter.check_env_vars")
@patch("daily_report.daily_reporter.Github")
@patch("daily_report.daily_reporter.OpenAI")
def test_collect_commits(
    mock_openai: MagicMock,  # pylint: disable=unused-argument
    mock_github: MagicMock,
    mock_check_env_vars: MagicMock,  # pylint: disable=unused-argument
    github_output_path: str,  # pylint: disable=unused-argument, disable=redefined-outer-name
) -> None:
    """Test collect_commits returns a list of commit dictionaries."""
    env = valid_env()
    for k, v in env.items():
        os.environ[k] = v
    mock_check_env_vars.return_value = env

    mock_commit = MagicMock()
    mock_commit.commit.message = "test"
    mock_commit.commit.author.name = "author"
    mock_commit.html_url = "http://example.com"
    mock_commit.sha = "sha"
    mock_commit.commit.author.date = "2024-01-01"
    mock_repo = MagicMock()
    mock_repo.get_commits.return_value = [mock_commit]
    mock_github.return_value.get_repo.return_value = mock_repo

    reporter = DailyReporter()
    commits = reporter.collect_commits()
    assert isinstance(commits, list)
    assert commits[0]["message"] == "test"


@patch("daily_report.daily_reporter.check_env_vars")
def test_init_env_error(
    mock_check_env_vars: MagicMock,
    github_output_path: str,  # pylint: disable=unused-argument,redefined-outer-name
) -> None:
    """Test that DailyReporter exits if environment validation fails."""
    mock_check_env_vars.side_effect = EnvCheckError("fail")
    with (
        patch("builtins.print"),
        patch("sys.exit", side_effect=SystemExit) as mock_exit,
    ):
        with pytest.raises(SystemExit):
            DailyReporter()
        mock_exit.assert_called_once()


@patch("daily_report.daily_reporter.check_env_vars")
@patch("daily_report.daily_reporter.Github")
@patch("daily_report.daily_reporter.OpenAI")
def test_run_exception_handling(
    mock_openai: MagicMock,
    mock_github: MagicMock,
    mock_check_env_vars: MagicMock,
    github_output_path: str,  # pylint: disable=redefined-outer-name
) -> None:
    """Test that DailyReporter.run handles exceptions and sets report_status=failure."""
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

    with (
        patch("builtins.open", side_effect=selective_open),
        patch("builtins.print"),
        patch("sys.exit", side_effect=SystemExit) as mock_exit,
        patch("daily_report.daily_reporter.smtplib.SMTP"),
    ):
        with pytest.raises(SystemExit):
            reporter = DailyReporter()
            reporter.run()
        mock_exit.assert_called_once()

    # Now use the original open for reading the output file
    with builtins.open(github_output_path, encoding="utf-8") as f:
        content = f.read()
        assert "report_status=failure" in content


def test_sanitize_filename() -> None:
    """Test the _sanitize_filename static method."""
    assert DailyReporter.sanitize_filename("test file.md") == "test_file.md"
    assert DailyReporter.sanitize_filename("äöüß.md") == "____.md"
    assert DailyReporter.sanitize_filename("report:2024.md") == "report_2024.md"
    assert DailyReporter.sanitize_filename("report.md") == "report.md"


@patch("daily_report.daily_reporter.check_env_vars")
@patch("daily_report.daily_reporter.Github")
@patch("daily_report.daily_reporter.OpenAI")
def test_run_smtp_exception(
    mock_openai: MagicMock,
    mock_github: MagicMock,
    mock_check_env_vars: MagicMock,
    github_output_path: str,  # pylint: disable=redefined-outer-name
) -> None:
    """Test that DailyReporter.run handles SMTPException and sets report_status=failure."""
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

    with (
        patch("builtins.print"),
        patch("sys.exit", side_effect=SystemExit),
        patch(
            "daily_report.daily_reporter.smtplib.SMTP",
            side_effect=smtplib.SMTPException("SMTP error"),
        ),
    ):
        with pytest.raises(SystemExit):
            reporter = DailyReporter()
            reporter.run()

    with open(github_output_path, encoding="utf-8") as f:
        content = f.read()
        assert "report_status=failure" in content


@patch("daily_report.daily_reporter.check_env_vars")
@patch("daily_report.daily_reporter.Github")
@patch("daily_report.daily_reporter.OpenAI")
def test_run_github_output_oserror(
    mock_openai: MagicMock,
    mock_github: MagicMock,
    mock_check_env_vars: MagicMock,
    github_output_path: str,  # pylint: disable=redefined-outer-name
) -> None:
    """Test that DailyReporter.run handles OSError when writing to GITHUB_OUTPUT."""
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

    with (
        patch("builtins.open", side_effect=selective_open_github_output_path),
        patch("builtins.print"),
        patch("sys.exit", side_effect=SystemExit),
        patch("daily_report.daily_reporter.smtplib.SMTP"),
    ):
        with pytest.raises(SystemExit):
            reporter = DailyReporter()
            reporter.run()
    # No assertion needed, test passes if SystemExit is raised due to OSError


@patch("daily_report.daily_reporter.check_env_vars")
@patch("daily_report.daily_reporter.Github")
@patch("daily_report.daily_reporter.OpenAI")
def test_run_status_success(
    mock_openai: MagicMock,
    mock_github: MagicMock,
    mock_check_env_vars: MagicMock,
    github_output_path: str,  # pylint: disable=redefined-outer-name
) -> None:
    """Test that DailyReporter.run sets report_status=success on successful run."""
    env = valid_env()
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

    with (
        patch("builtins.print"),
        patch("sys.exit", side_effect=SystemExit),
        patch("daily_report.daily_reporter.smtplib.SMTP"),
    ):
        with pytest.raises(SystemExit):
            reporter = DailyReporter()
            reporter.run()

    with open(github_output_path, encoding="utf-8") as f:
        content = f.read()
        assert "report_status=success" in content
