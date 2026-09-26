import feedparser
import urllib.parse
import datetime

# અહીં Moneycontrol ના RSS ફીડની લિંક છે
RSS_URL = "https://www.moneycontrol.com/rss/business.xml"

def fetch_news():
    feed = feedparser.parse(RSS_URL)
    news_list = []
    
    # ફક્ત છેલ્લા 5 ન્યૂઝ લઈએ
    for entry in feed.entries[:5]:
        title = entry.title
        link = entry.link
        # Google Translate ની ફ્રી લિંક વાપરીને હિન્દીમાં કન્વર્ટ કરીએ
        # (આ ઓટોમેટિક થશે, તમારે કંઈ કરવાનું નથી)
        hindi_title = f"https://translate.google.com/translate?sl=auto&tl=hi&u={urllib.parse.quote(link)}"
        
        news_list.append({
            "title": title,
            "hindi_link": hindi_title,
            "source": "Moneycontrol",
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        })
    return news_list

if __name__ == "__main__":
    news = fetch_news()
    # આ ફક્ત ટેસ્ટ માટે છે, અસલી વેબસાઈટ માટે આગળનું સ્ટેપ જુઓ
    for n in news:
        print(f"શીર્ષક: {n['title']}")
        print(f"સ્રોત: {n['source']} | લિંક: {n['hindi_link']}")
        print("---")
