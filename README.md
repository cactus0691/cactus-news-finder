# 🌵 Cactus News Finder
A free Telegram bot that summarizes the latest news on any topic you type (e.g., Infosys, AI, layoffs, cricket).

## Setup
1. Deploy on Render (Free).
2. Add environment variable `TELEGRAM_BOT_TOKEN` with your BotFather token.
3. Start command: `gunicorn app:app`.

## Usage
- Open the bot on Telegram, type any keyword.
- Bot fetches latest Google News headlines, summarizes, and replies with links.
