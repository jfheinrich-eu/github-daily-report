# jfheinrich/github-daily-report Image


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

Use in a Github workflow:

```yaml
- name: Run Daily Report
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