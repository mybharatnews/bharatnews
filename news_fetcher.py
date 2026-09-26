import feedparser
import datetime
import json
import time
import re
from deep_translator import MyMemoryTranslator

RSS_URL = "https://www.moneycontrol.com/rss/business.xml"

def clean_html(text):
    """HTML ટેગ્સ સાફ કરો"""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text).strip()

def fetch_and_translate_news():
    feed = feedparser.parse(RSS_URL)
    news_list = []
    
    print(f"કુલ {len(feed.entries)} ન્યૂઝ મળ્યા RSS માંથી")
    
    # છેલ્લા 8 ન્યૂઝ લઈએ
    for entry in feed.entries[:8]:
        title_en = entry.title
        link = entry.link
        
        # RSS માંથી સારાંશ (Description) લો
        summary_en = entry.get('summary', entry.get('description', ''))
        summary_en = clean_html(summary_en)
        summary_en = summary_en[:250]  # 250 અક્ષરો સુધી
        
        try:
            # ટાઇટલ ટ્રાન્સલેટ કરો
            title_hi = MyMemoryTranslator(source='en-GB', target='hi-IN').translate(title_en)
            time.sleep(1.5)
            
            # સારાંશ ટ્રાન્સલેટ કરો
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
        
        news_list.append({
            "title": title_hi,
            "summary": summary_hi,
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
