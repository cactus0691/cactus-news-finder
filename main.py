import os
import requests
import feedparser
from transformers import pipeline
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Read token from env (Railway variable)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise RuntimeError("Set TELEGRAM_BOT_TOKEN in Railway → Variables.")

# Light, fast summarizer
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌵 Cactus News Finder here!\n"
        "Type any topic or company (e.g., Infosys, AI, layoffs, cricket) and I’ll fetch recent news."
    )

def search_feed(query: str, limit: int = 5):
    import urllib.parse
    url = (
        "https://news.google.com/rss/search?"
        f"q={urllib.parse.quote(query)}&hl=en-IN&gl=IN&ceid=IN:en"
    )
    feed = feedparser.parse(url)
    return feed.entries[:limit]

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = (update.message.text or "").strip()
    if not query:
        await update.message.reply_text("Type a keyword, e.g., Infosys or AI.")
        return

    await update.message.reply_text(f"🔍 Searching: {query}")
    entries = search_feed(query, 5)
    if not entries:
        await update.message.reply_text(f"⚠️ No recent news for “{query}”. Try another term.")
        return

    for e in entries:
        title = getattr(e, "title", "")
        desc = getattr(e, "summary", "")
        combined = (title + ". " + desc).replace("\n", " ")[:600]
        try:
            out = summarizer(combined, max_length=48, min_length=16, do_sample=False)
            summary = out[0]["summary_text"].strip()
        except Exception:
            summary = (combined[:140] + "…") if len(combined) > 140 else combined

        msg = f"🗞️ {title}\n\n✨ {summary}\n\n🔗 {getattr(e, 'link', '')}"
        await update.message.reply_text(msg, disable_web_page_preview=True)

def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.run_polling()  # no webhook needed on Railway

if __name__ == "__main__":
    main()

