<p align="center">
 <img height=70px src="https://raw.githubusercontent.com/jfheinrich-eu/github-daily-report/main/assets/daily-report-logo.png" alt="Daily Report">
</p>

# jfheinrich/github-daily-report Docker Image

## Overview

This image provides a minimal Python 3.12 environment based on Alpine Linux, bundled with a custom-built version of Git (v2.50.0) and the Github Action jfheinrich-eu/github-daily-report. It is designed for use from the Github action.

---

## Features

- **Python 3.12** based on Alpine Linux for a small footprint
- **Git 2.50.0** built from source and installed to `/opt/git`
- **jfheinrich-eu/github-daily-report v1**
- Multi-stage build for a clean and minimal final image
- Environment variables set for Git binaries and libraries

---

## Usage

Use in a Github workflow, optional with report upload as artifact:

```yaml
- name: Run Daily Report
  id: daily_report
  uses: jfheinrich-eu/github-daily-report@63196a129709dfe696458e3bea5b9cf893b3e611  # v1.1.4
  with:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    REPO_NAME: "owner/repo"
    EMAIL_SENDER: "sender@example.com"
    EMAIL_USER: "sender@example.com"
    EMAIL_RECEIVER: "receiver@example.com"
    EMAIL_PASSWORD: ${{ secrets.EMAIL_PASSWORD }}
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
    SMTP_SERVER: "smtp.example.com"
    SMTP_PORT: "587"
- name: Create report file with date
  id: create_report_file
  if: ${{ steps.daily_report.outputs.report_status == 'success' }}
  run: |
    echo "Creating report file with date..."
    REPORT_NAME="daily-report-$(date +'%Y-%m-%d').md"
    report_file_name="${REPORT_NAME}""
    echo "${{ steps.daily_report.outputs.report }}" >> "$report_file_name"
    echo "Report file created: $report_file_name"
    echo "report_file_created=success" >> $GITHUB_OUTPUT
    echo "report_file_name=$report_file_name" >> $GITHUB_OUTPUT
- name: Upload Daily Report
  if: ${{ steps.daily_report.outputs.report_status == 'success' }} && ${{ steps.create_report_file.outputs.report_file_created == 'success' }}
  uses: actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02 # v4.6.2
  with:
    name: daily-report
    path: ${{ steps.create_report_file.outputs.report_file_name }}

```

---

## Environment Variables

- `PATH` includes `/opt/git/bin` so the custom Git is used by default.
- `LD_LIBRARY_PATH` includes `/opt/git/lib` for Git dependencies.

---

## License

This image is provided as-is under the MIT License.
Git is licensed under the GNU General Public License v2.0.
Python is licensed under the Python Software Foundation License.

---

## Maintainer

Joerg Heinrich
[joerg@jfheinrich.eu](mailto:joerg@jfheinrich.eu)

---

## Notes

- The image is intended for use in CI/CD and automation scenarios.
- For production workloads, review and adjust the image to your security and compliance
