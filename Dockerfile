FROM python:3.11-slim

    # no print buffering
ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    # chromium driver
    CHROME_BIN=/usr/bin/chromium \
    # headless
    DISPLAY=:99 

RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium \
    chromium-driver \
    ca-certificates \
    wget \
    # clean up apt cache
    && rm -rf /var/lib/apt/lists/*

# root not recommended, use a non-root user instead
RUN useradd --create-home --shell /bin/bash appuser
WORKDIR /home/appuser/app
COPY --chown=appuser:appuser . /home/appuser/app

USER appuser

RUN pip install --no-cache-dir -r requirements.txt

# expose logs
VOLUME ["/home/appuser/app/logs"]

# run forest run
CMD ["python", "main.py"]