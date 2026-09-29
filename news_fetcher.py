import feedparser
import datetime
import json
import time
import re
import os
import sys
import requests
from deep_translator import MyMemoryTranslator

# ═══════════════════════════════════════
# RSS ફીડ ગ્રુપ (સમય પ્રમાણે)
# ═══════════════════════════════════════
RSS_GROUPS = {
    "15min": [
        "https://www.moneycontrol.com/rss/latestnews.xml",
        "https://www.moneycontrol.com/rss/marketreports.xml",
    ],
    "30min": [
        "https://www.moneycontrol.com/rss/business.xml",
        "https://www.moneycontrol.com/rss/economy.xml",
    ],
    "60min": [
        "https://www.moneycontrol.com/rss/results.xml",
        "https://www.moneycontrol.com/rss/iponews.xml",
    ],
}

TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

SENT_FILE = 'sent_news.json'
NEWS_FILE = 'news_data.json'

def clean_html(text):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text).strip()

def load_sent_news():
    if os.path.exists(SENT_FILE):
        with open(SENT_FILE, 'r', encoding='utf-8') as f:
            return set(json.load(f))
    return set()

def save_sent_news(sent_set):
    sent_list = list(sent_set)[-500:]
    with open(SENT_FILE, 'w', encoding='utf-8') as f:
        json.dump(sent_list, f, ensure_ascii=False, indent=4)

def load_existing_news():
    if os.path.exists(NEWS_FILE):
        with open(NEWS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def send_to_telegram(title, link, summary):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Telegram credentials નથી")
        return False
    
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
            return True
        else:
            print(f"❌ Telegram એરર: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Telegram એરર: {e}")
        return False

def get_rss_urls():
    """સમય પ્રમાણે RSS ફીડ પસંદ કરો"""
    now = datetime.datetime.now()
    minute = now.minute
    hour = now.hour
    
    urls = []
    
    # દર 15 મિનિટે (0, 15, 30, 45)
    if minute % 15 == 0:
        urls.extend(RSS_GROUPS["15min"])
        print("📡 15-મિનિટ ગ્રુપ ચેક થઈ રહ્યું છે...")
    
    # દર 30 મિનિટે (0, 30)
    if minute % 30 == 0:
        urls.extend(RSS_GROUPS["30min"])
        print("📡 30-મિનિટ ગ્રુપ ચેક થઈ રહ્યું છે...")
    
    # દર 60 મિનિટે (0)
    if minute == 0:
        urls.extend(RSS_GROUPS["60min"])
        print("📡 60-મિનિટ ગ્રુપ ચેક થઈ રહ્યું છે...")
    
    # જો કોઈ ગ્રુપ ના મળે, તો ડિફોલ્ટ
    if not urls:
        urls = RSS_GROUPS["30min"]
        print("📡 ડિફોલ્ટ ગ્રુપ ચેક થઈ રહ્યું છે...")
    
    return urls

def fetch_and_translate_news():
    rss_urls = get_rss_urls()
    
    # બધા RSS ફીડમાંથી ન્યૂઝ લાવો
    all_entries = []
    for url in rss_urls:
        try:
            feed = feedparser.parse(url)
            all_entries.extend(feed.entries)
            print(f"   └─ {url.split('/')[-1]}: {len(feed.entries)} ન્યૂઝ")
        except Exception as e:
            print(f"   └─ ❌ RSS એરર: {e}")
    
    print(f"\n📊 કુલ {len(all_entries)} ન્યૂઝ મળ્યા")
    
    # ડુપ્લિકેટ દૂર કરો
    seen_links = set()
    unique_entries = []
    for entry in all_entries:
        if entry.link not in seen_links:
            seen_links.add(entry.link)
            unique_entries.append(entry)
    
    print(f"🔍 ડુપ્લિકેટ દૂર કર્યા પછી: {len(unique_entries)} યુનિક ન્યૂઝ\n")
    
    # પહેલેથી મોકલેલા ન્યૂઝ
    sent_news = load_sent_news()
    
    # જૂના ન્યૂઝ લોડ કરો (વેબસાઇટ માટે)
    existing_news = load_existing_news()
    
    new_news = []
    sent_count = 0
    max_telegram = 5
    
    for entry in unique_entries[:15]:
        title_en = entry.title
        link = entry.link
        summary_en = clean_html(entry.get('summary', entry.get('description', '')))
        summary_en = summary_en[:300]
        
        # જો પહેલેથી મોકલ્યું હોય, તો છોડી દો
        if link in sent_news:
            continue
        
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
            "date": datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
        }
        new_news.append(news_item)
        
        # Telegram પર ફક્ત 5 નવા ન્યૂઝ મોકલો
        if sent_count < max_telegram:
            success = send_to_telegram(title_hi, link, summary_hi)
            if success:
                sent_news.add(link)
                sent_count += 1
            time.sleep(2)
    
    # જૂના + નવા ન્યૂઝ ભેગા કરો (ફક્ત 20 રાખો)
    all_news = new_news + existing_news
    all_news = all_news[:20]
    
    # મોકલેલા ન્યૂઝ સેવ કરો
    save_sent_news(sent_news)
    
    print(f"\n📝 નવા ન્યૂઝ: {len(new_news)}")
    print(f"📚 વેબસાઇટ પર કુલ: {len(all_news)}")
    
    return all_news

if __name__ == "__main__":
    news = fetch_and_translate_news()
    with open(NEWS_FILE, 'w', encoding='utf-8') as f:
        json.dump(news, f, ensure_ascii=False, indent=4)
    print(f"\n🎉 કુલ {len(news)} ન્યૂઝ સેવ થયા!")
