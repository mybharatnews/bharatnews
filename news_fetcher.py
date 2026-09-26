import datetime
import json
from gnews import GNews

def fetch_hindi_news():
    # ભારતના હિન્દી ન્યૂઝ માટે સેટિંગ
    google_news = GNews(language='hi', country='IN', period='1d', max_results=10)
    
    # બિઝનેસ/માર્કેટ સંબંધિત ન્યૂઝ શોધો
    news = google_news.get_news('શેર બજાર')
    
    news_list = []
    
    for article in news:
        news_list.append({
            "title": article['title'],
            "link": article['url'],
            "source": article['publisher']['title'],
            "date": datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
        })
    
    return news_list

if __name__ == "__main__":
    news = fetch_hindi_news()
    with open('news_data.json', 'w', encoding='utf-8') as f:
        json.dump(news, f, ensure_ascii=False, indent=4)
    print(f"{len(news)} હિન્દી ન્યૂઝ સેવ થયા!")
