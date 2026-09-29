import feedparser
import datetime
import json
import time
import re
import os
import requests
from deep_translator import MyMemoryTranslator

RSS_URL = "https://www.moneycontrol.com/rss/business.xml"

# Telegram Settings (GitHub Secrets માંથી આવશે)
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

def clean_html(text):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text).strip()

def send_to_telegram(title, link, summary):
    """Telegram ચેનલ પર ન્યૂઝ મોકલો"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Telegram credentials નથી")
        return
    
    message = f"""📰 *{title}*

{summary[:200]}...

🔗 [પૂરી ન્યૂઝ વાંચો]({link})

📌 સ્રોત: Moneycontrol"""
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown',
        'disable_web_page_preview': False
    }
    
    try:
        response = requests.post(url, data=payload, timeout=10)
        if response.status_code == 200:
            print(f"✅ Telegram પર મોકલ્યું: {title[:30]}...")
        else:
            print(f"❌ Telegram એરર: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Telegram એરર: {e}")

def fetch_and_translate_news():
    feed = feedparser.parse(RSS_URL)
    news_list = []
    
    print(f"કુલ {len(feed.entries)} ન્યૂઝ મળ્યા RSS માંથી")
    
    for entry in feed.entries[:5]:
        title_en = entry.title
        link = entry.link
        summary_en = clean_html(entry.get('summary', entry.get('description', '')))
        summary_en = summary_en[:300]
        
        try:
            title_hi = MyMemoryTranslator(source='en-GB', target='hi-IN').translate(title_en)
            time.sleep(1.5)
            
            if summary_en:
                summary_hi = MyMemoryTranslator(source='en-GB', target='hi-IN').translate(summary_en)
                time.sleep(1.5)
            else:
                summary_hi = ""
            
            print(f"✅ ટ્રાન્સલેટ: {title_hi[:50]}...")
        except Exception as e:
            print(f"❌ ટ્રાન્સલેશન એરર: {e}")
            title_hi = title_en
            summary_hi = summary_en
        
        news_item = {
            "title": title_hi,
            "summary": summary_hi,
            "link": link,
            "source": "Moneycontrol",
            "date": datetime.datetime.now().strftime("%d-%m-%Y %H:%M"),
            "id": link.split('/')[-1][:20]  # યુનિક ID
        }
        news_list.append(news_item)
        
        # Telegram પર મોકલો
        send_to_telegram(title_hi, link, summary_hi)
        time.sleep(2)
    
    return news_list

if __name__ == "__main__":
    news = fetch_and_translate_news()
    with open('news_data.json', 'w', encoding='utf-8') as f:
        json.dump(news, f, ensure_ascii=False, indent=4)
    print(f"🎉 કુલ {len(news)} ન્યૂઝ સેવ થયા!")
