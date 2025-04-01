# Telegram Media Downloader Bot for Cobalt

## Overview
This project is a simple Telegram bot that serves as an interface for the Cobalt app. Send the bot a video link, and it will instruct Cobalt (running on a specified port, typically `9000`) to download the video. Remember, the port is set during the Cobalt app setup.

> **Note:** The Cobalt package can be [downloaded](https://github.com/imputnet/cobalt/pkgs/container/cobalt) from GitHub.

## Features
- **Simple Interface:** Download videos by sending a link via Telegram.
- **Dockerized:** Easily deploy using Docker and Docker Compose.

## Requirements
- Create your Telegram bot using [BotFather](https://core.telegram.org/bots#6-botfather).
- Cobalt package (ensure you specify the port during setup).
- Docker & Docker Compose

## Setup

### Environment Variables
Before running the bot, set:
- `TOKEN`: Your Telegram bot token (obtained from BotFather).
- `URL`: The Cobalt service endpoint with the specified port (e.g., `http://<your_global_ip>:9000`).

### Docker Compose Configuration
Create a `docker-compose.yml` file with the following content:

```yaml
version: '3'
services:
  bot:
    build: .
    environment:
      - TOKEN=your_telegram_bot_token
      - URL=http://your_global_ip:9000
```

### Running the App
1. Update `TOKEN` and `URL` in the configuration.
2. Build and run with:
   ```bash
   docker-compose up --build
   ```
3. The bot will start polling Telegram and instruct Cobalt (running on the specified port) to download videos from the provided links.

## Troubleshooting
- Ensure `TOKEN` and `URL` are correctly set.
- Verify Docker and Docker Compose are installed.
- Confirm that your global IP and the specified port (default `9000`) are accessible.