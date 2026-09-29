import feedparser
import datetime
import json
import time
import re
import os
import requests
from deep_translator import MyMemoryTranslator

# ═══════════════════════════════════════
# RSS ફીડ ગ્રુપ (સમય પ્રમાણે, અલગ સ્રોત)
# ═══════════════════════════════════════
RSS_SCHEDULE = {
    "06:30": [
        "https://www.moneycontrol.com/rss/business.xml",
        "https://www.livemint.com/rss/news",
        "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
    ],
    "09:30": [
        "https://www.moneycontrol.com/rss/marketreports.xml",
        "https://www.livemint.com/rss/markets",
        "https://www.zeebiz.com/rss/markets.xml",
    ],
    "12:30": [
        "https://www.moneycontrol.com/rss/results.xml",
        "https://www.livemint.com/rss/companies",
        "https://economictimes.indiatimes.com/industry/rssfeeds/13352306.cms",
    ],
    "15:30": [
        "https://www.moneycontrol.com/rss/economy.xml",
        "https://www.livemint.com/rss/industry",
        "https://economictimes.indiatimes.com/economy/rssfeeds/1373380680.cms",
    ],
    "18:30": [
        "https://www.moneycontrol.com/rss/latestnews.xml",
        "https://www.livemint.com/rss/money",
        "https://www.zeebiz.com/rss/business.xml",
    ],
    "21:30": [
        "https://www.moneycontrol.com/rss/iponews.xml",
        "https://www.livemint.com/rss/technology",
        "https://economictimes.indiatimes.com/tech/rssfeeds/13357270.cms",
    ],
}

TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

SENT_FILE = 'sent_news.json'
NEWS_FILE = 'news_data.json'


def clean_html(text):
    """HTML ટેગ્સ સાફ કરો"""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text).strip()


def load_sent_news():
    """પહેલેથી મોકલેલા ન્યૂઝની લિસ્ટ લોડ કરો"""
    if os.path.exists(SENT_FILE):
        with open(SENT_FILE, 'r', encoding='utf-8') as f:
            return set(json.load(f))
    return set()


def save_sent_news(sent_set):
    """મોકલેલા ન્યૂઝની લિસ્ટ સેવ કરો (ફક્ત 500)"""
    sent_list = list(sent_set)[-500:]
    with open(SENT_FILE, 'w', encoding='utf-8') as f:
        json.dump(sent_list, f, ensure_ascii=False, indent=4)


def load_existing_news():
    """જૂના ન્યૂઝ લોડ કરો"""
    if os.path.exists(NEWS_FILE):
        with open(NEWS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def get_source_name(url):
    """URL માંથી સ્રોતનું નામ કાઢો"""
    try:
        domain = url.split('/')[2].replace('www.', '')
        if 'moneycontrol' in domain:
            return 'Moneycontrol'
        elif 'livemint' in domain:
            return 'Livemint'
        elif 'economictimes' in domain:
            return 'Economic Times'
        elif 'zeebiz' in domain:
            return 'Zee Business'
        else:
            return domain
    except:
        return 'Bharat News'


def send_to_telegram(title, link, summary, source):
    """Telegram ચેનલ પર ન્યૂઝ મોકલો"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Telegram credentials નથી")
        return False

    message = f"""📰 *{title}*

{summary[:200]}...

🔗 [પૂરી ન્યૂઝ વાંચો]({link})

📌 સ્રોત: {source}"""

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


def get_rss_urls_for_now():
    """હાલના સમય પ્રમાણે RSS ફીડ પસંદ કરો"""
    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M")

    schedule_times = sorted(RSS_SCHEDULE.keys())

    # ચોક્કસ સમય મેળ ખાય છે કે નહીં
    if current_time in RSS_SCHEDULE:
        print(f"📡 {current_time} સ્લોટ ચેક થઈ રહ્યો છે...")
        return RSS_SCHEDULE[current_time]

    # જો ચોક્કસ સમય ના મળે, તો સૌથી નજીકનો સમય લો
    current_minutes = now.hour * 60 + now.minute

    closest_slot = None
    min_diff = 999

    for time_str in schedule_times:
        h, m = map(int, time_str.split(':'))
        slot_minutes = h * 60 + m
        diff = abs(current_minutes - slot_minutes)

        if diff < min_diff and diff <= 60:
            min_diff = diff
            closest_slot = time_str

    if closest_slot:
        print(f"📡 {closest_slot} સ્લોટ (નજીકનો) ચેક થઈ રહ્યો છે...")
        return RSS_SCHEDULE[closest_slot]

    # જો કોઈ સ્લોટ ના મળે, તો બધા ફીડ ચેક કરો
    print("📡 બધા RSS ફીડ ચેક થઈ રહ્યા છે...")
    all_urls = []
    for urls in RSS_SCHEDULE.values():
        all_urls.extend(urls)
    return list(set(all_urls))


def fetch_and_translate_news():
    rss_urls = get_rss_urls_for_now()

    all_entries = []
    for url in rss_urls:
        try:
            feed = feedparser.parse(url)
            # દરેક RSS માંથી ફક્ત 4 ન્યૂઝ લો
            entries_from_feed = feed.entries[:4]
            all_entries.extend(entries_from_feed)
            print(f"   └─ {url.split('/')[-1][:40]}: {len(entries_from_feed)} ન્યૂઝ")
        except Exception as e:
            print(f"   └─ ❌ RSS એરર: {e}")

    print(f"\n📊 કુલ {len(all_entries)} ન્યૂઝ મળ્યા (દરેક સ્રોતમાંથી 4)")
    # ડુપ્લિકેટ દૂર કરો
    seen_links = set()
    unique_entries = []
    for entry in all_entries:
        if entry.link not in seen_links:
            seen_links.add(entry.link)
            unique_entries.append(entry)

    print(f"🔍 ડુપ્લિકેટ દૂર કર્યા પછી: {len(unique_entries)} યુનિક ન્યૂઝ\n")

    sent_news = load_sent_news()
    existing_news = load_existing_news()

    new_news = []
    sent_count = 0
    max_telegram = 8

    for entry in unique_entries[:30]:
        title_en = entry.title
        link = entry.link
        summary_en = clean_html(entry.get('summary', entry.get('description', '')))
        summary_en = summary_en[:300]

        # જો પહેલેથી મોકલ્યું હોય, તો છોડી દો
        if link in sent_news:
            continue

        # સ્રોતનું નામ
        source_name = get_source_name(link)

        try:
            title_hi = MyMemoryTranslator(source='en-GB', target='hi-IN').translate(title_en)
            time.sleep(1.5)

            if summary_en:
                summary_hi = MyMemoryTranslator(source='en-GB', target='hi-IN').translate(summary_en)
                time.sleep(1.5)
            else:
                summary_hi = ""

            print(f"✅ [{source_name}] {title_hi[:45]}...")
        except Exception as e:
            print(f"❌ ટ્રાન્સલેશન એરર: {e}")
            title_hi = title_en
            summary_hi = summary_en

        news_item = {
            "title": title_hi,
            "summary": summary_hi,
            "link": link,
            "source": source_name,
            "date": datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
        }
        new_news.append(news_item)

        # Telegram પર ફક્ત 8 નવા ન્યૂઝ
        if sent_count < max_telegram:
            success = send_to_telegram(title_hi, link, summary_hi, source_name)
            if success:
                sent_news.add(link)
                sent_count += 1
            time.sleep(2)

        # વેબસાઇટ માટે 25 ન્યૂઝ પૂરતા
        if len(new_news) >= 25:
            break

    # જૂના + નવા ન્યૂઝ (ફક્ત 30 રાખો)
    all_news = new_news + existing_news
    all_news = all_news[:30]

    save_sent_news(sent_news)

    print(f"\n📝 નવા ન્યૂઝ: {len(new_news)}")
    print(f"📚 વેબસાઇટ પર કુલ: {len(all_news)}")

    return all_news


if __name__ == "__main__":
    news = fetch_and_translate_news()
    with open(NEWS_FILE, 'w', encoding='utf-8') as f:
        json.dump(news, f, ensure_ascii=False, indent=4)
    print(f"\n🎉 કુલ {len(news)} ન્યૂઝ સેવ થયા!")
