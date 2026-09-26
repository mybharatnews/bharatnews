import feedparser
import datetime
import json
from deep_translator import GoogleTranslator

RSS_URL = "https://www.moneycontrol.com/rss/business.xml"

def fetch_and_translate_news():
    feed = feedparser.parse(RSS_URL)
    news_list = []
    
    print(f"કુલ {len(feed.entries)} ન્યૂઝ મળ્યા RSS માંથી")
    
    for entry in feed.entries[:10]:
        title_en = entry.title
        link = entry.link
        
        try:
            title_hi = GoogleTranslator(source='en', target='hi').translate(title_en)
            print(f"✅ ટ્રાન્સલેટ: {title_hi[:50]}...")
        except Exception as e:
            print(f"❌ ટ્રાન્સલેશન એરર: {e}")
            title_hi = title_en
        
        news_list.append({
            "title": title_hi,
            "link": link,
            "source": "Moneycontrol",
            "date": datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
        })
    
    return news_list

if __name__ == "__main__":
    news = fetch_and_translate_news()
    with open('news_data.json', 'w', encoding='utf-8') as f:
        json.dump(news, f, ensure_ascii=False, indent=4)
    print(f"🎉 કુલ {len(news)} ન્યૂઝ સેવ થયા!")
