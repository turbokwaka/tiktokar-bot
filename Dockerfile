FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        wget \
        gnupg \
        unzip \
        ffmpeg \
        libglib2.0-0 \
        libnss3 \
        libgconf-2-4 \
        libfontconfig1 \
        libxss1 \
        libasound2 \
        libatk-bridge2.0-0 \
        libgtk-3-0 \
        fonts-liberation \
        libu2f-udev \
        xdg-utils \
        libgbm1 \
        libx11-xcb1 \
    && rm -rf /var/lib/apt/lists/*

RUN wget -O chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt-get update && \
    apt-get install -y ./chrome.deb && \
    rm chrome.deb

COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt
COPY . .

CMD ["python", "bot.py"]
