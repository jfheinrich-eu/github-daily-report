FROM docker.io/jfheinrich/github-daily-report:latest

ENV PATH="/opt/git/bin:${PATH}"
ENV LD_LIBRARY_PATH="/opt/git/lib"
ENV PYTHONPATH=/app

WORKDIR /app
ENTRYPOINT ["python", "-m", "daily_report.main"]
