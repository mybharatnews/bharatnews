import feedparser
import urllib.parse
import datetime
import json

RSS_URL = "https://www.moneycontrol.com/rss/business.xml"

def fetch_news():
    feed = feedparser.parse(RSS_URL)
    news_list = []
    
    for entry in feed.entries[:10]: # હવે 10 ન્યૂઝ લઈએ
        title = entry.title
        link = entry.link
        # હિન્દીમાં ટ્રાન્સલેટ કરવા માટે Google Translate ની લિંક
        hindi_link = f"https://translate.google.com/translate?sl=auto&tl=hi&u={urllib.parse.quote(link)}"
        
        news_list.append({
            "title": title,
            "hindi_link": hindi_link,
            "source": "Moneycontrol",
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        })
    return news_list

if __name__ == "__main__":
    news = fetch_news()
    # આ ડેટાને JSON ફાઈલમાં સેવ કરો, જેથી વેબસાઈટ વાંચી શકે
    with open('news_data.json', 'w', encoding='utf-8') as f:
        json.dump(news, f, ensure_ascii=False, indent=4)
    print(f"{len(news)} ન્યૂઝ સેવ થયા!")
