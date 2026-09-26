import feedparser
import datetime
import json
from deep_translator import GoogleTranslator

RSS_URL = "https://www.moneycontrol.com/rss/business.xml"

def fetch_and_translate_news():
    feed = feedparser.parse(RSS_URL)
    news_list = []
    
    for entry in feed.entries[:10]:
        title_en = entry.title
        link = entry.link
        
        # અંગ્રેજી ટાઈટલને હિન્દીમાં ટ્રાન્સલેટ કરો
        try:
            title_hi = GoogleTranslator(source='en', target='hi').translate(title_en)
        except Exception as e:
            title_hi = title_en  # એરર આવે તો અંગ્રેજી રાખો
        
        news_list.append({
            "title": title_hi,
            "original_title": title_en,
            "link": link,
            "source": "Moneycontrol",
            "date": datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
        })
    return news_list

if __name__ == "__main__":
    news = fetch_and_translate_news()
    with open('news_data.json', 'w', encoding='utf-8') as f:
        json.dump(news, f, ensure_ascii=False, indent=4)
    print(f"{len(news)} ન્યૂઝ સેવ થયા!")
