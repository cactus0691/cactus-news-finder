from flask import Flask, request
import feedparser, requests
from transformers import pipeline

app = Flask(__name__)
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
TELEGRAM_BOT_TOKEN = "${TELEGRAM_BOT_TOKEN}"
BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if 'message' in data and 'text' in data['message']:
        chat_id = data['message']['chat']['id']
        query = data['message']['text']
        send_news(chat_id, query)
    return "ok"

def send_news(chat_id, query):
    url = f"https://news.google.com/rss/search?q={query}"
    feed = feedparser.parse(url)
    results = []
    for entry in feed.entries[:3]:
        text = entry.title + ". " + entry.summary
        try:
            summary = summarizer(text, max_length=40, min_length=10, do_sample=False)[0]['summary_text']
        except:
            summary = entry.title
        results.append(f"• {summary}
{entry.link}")
    message = "

".join(results) if results else "No news found."
    requests.post(f"{BASE_URL}/sendMessage", json={"chat_id": chat_id, "text": message})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
