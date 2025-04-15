# Telegram Media Downloader Bot

## Overview
This project is a simple Telegram bot that serves as an interface for the Cobalt-tools app. Send the bot a video link, and it will send a video file back.

## Requirements
- Create your Telegram bot using [BotFather](https://t.me/BotFather).
- Docker & Docker Compose

## Setup

### Environment Variables
Before running the bot, set:
- `TOKEN`: Your Telegram bot token (obtained from BotFather).
- `ADMIN_CHAT_ID`: Chat ID of admin, that will receive error logs (optional).

### Running the App
1. Update `TOKEN` and `ADMIN_CHAT_ID` in the docker-compose.yml .
2. Build and run with:
   ```bash
   sudo docker compose up -d
   ```

## Troubleshooting
- Ensure `TOKEN` is correctly set.
- Verify docker daemon is running.
