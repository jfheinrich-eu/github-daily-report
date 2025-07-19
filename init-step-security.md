# Anleitung für ein Python-Github-Action Repo
Hier ist eine Schritt-für-Schritt-Anleitung, um ein neues Python-Projekt github-daily-report von Anfang an mit GitHub Actions, StepSecurity und pre-commit.ci-lite abzusichern.

0. Requirements
```shell
sudo apk add --update github-cli
(gh auth status || gh auth login) && gh extension install https://github.com/nektos/gh-act
mkdir <repository directory>
git int <repository directory>
python -m pip install poetry
```
1. Repository anlegen 
```shell
cd <repository directory>
git branch -m main
gh repo create github-daily-report --public --source=. --remote=origin
git push -u origin main
```
2. Python Project initialisieren
```shell
poetry new <repository name>
cd <respository directory>
poetry self add poetry-export
poetry self add poethepoet[poetry_plugin]
poetry self add poetry-git-version-plugin
```
3. pre-commit konfigurieren
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.4.2
    hooks:
      - id: black
  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
  - repo: https://github.com/pycqa/flake8
    rev: 7.3.0
    hooks:
      - id: flake8
```


4. Install hooks
```shell
poetry install --all-groups --no-root
poetry run pre-commit install
git add .pre-commit-config.yaml
git commt -m "tests: Add pre-commit config"
```
5. GitHub Actions Workflow mit StepSecurity und pre-commit-ci-lite
6. 