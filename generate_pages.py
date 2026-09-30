import json
import os
import re
from datetime import datetime

# ફોલ્ડર બનાવો
os.makedirs('news', exist_ok=True)

def clean_filename(text, index=0):
    """SEO ફ્રેન્ડલી ફાઈલ નામ બનાવો"""
    # હિન્દી અક્ષરો દૂર કરો
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    # ખાસ અક્ષરો દૂર કરો
    text = re.sub(r'[^\w\s-]', '', text)
    # સ્પેસને ડેશમાં બદલો
    text = re.sub(r'\s+', '-', text)
    text = re.sub(r'-+', '-', text)
    text = text.strip('-')
    
    # આજની તારીખ
    today = datetime.now().strftime('%Y%m%d')
    
    # જો નામ ટૂંકું હોય, તો index + date વાપરો
    if not text or len(text) < 10:
        text = f"market-news-{index}-{today}"
    else:
        text = f"market-news-{text}"
    
    return text[:60].lower()

def generate_article_page(news_item, index):
    """દરેક ન્યૂઝ માટે અલગ પેજ બનાવો"""
    
    title = news_item.get('title', '')
    summary = news_item.get('summary', '')
    link = news_item.get('link', '')
    source = news_item.get('source', '')
    date = news_item.get('date', '')
    
    full_article = f"""
    <p><strong>{summary}</strong></p>
    
    <p>આ સમાચાર {source} દ્વારા પ્રકાશિત કરવામાં આવ્યા છે. ભારતીય શેર બજારમાં આ સમાચારની ખૂબ અસર પડી શકે છે. રોકાણકારોએ આ સમાચારને ધ્યાનથી વાંચવા જોઈએ અને તેના આધારે પોતાના રોકાણના નિર્ણય લેવા જોઈએ.</p>
    
    <h2>શેર બજાર પર અસર</h2>
    <p>ભારતીય શેર બજારમાં આજે મોટી હલચલ જોવા મળી રહી છે. નિફ્ટી 50 અને સેન્સેક્સમાં ઉતાર-ચઢાવ જોવા મળી રહ્યો છે. આ સમાચારની અસર બેંકિંગ, IT, ઓટોમોબાઈલ અને ફાર્મા સેક્ટર પર પડી શકે છે.</p>
    
    <p>નિષ્ણાતોના મતે, આ સમાચાર ટૂંકા ગાળામાં બજારને અસર કરી શકે છે. પણ લાંબા ગાળે બજારના મૂળભૂત સિદ્ધાંતો જ મહત્વના છે. રોકાણકારોએ ગભરાવું નહીં જોઈએ અને ધીરજ રાખવી જોઈએ.</p>
    
    <h2>રોકાણકારો માટે સલાહ</h2>
    <p>શેર બજારમાં રોકાણ કરતી વખતે હંમેશા સંશોધન કરો. કોઈપણ સમાચારને આધારે તરત જ નિર્ણય ના લો. તમારા નાણાકીય સલાહકારની સલાહ લો. ડાઇવર્સિફિકેશન (વિવિધ ક્ષેત્રોમાં રોકાણ) એ સૌથી સારો રસ્તો છે.</p>
    
    <p>શેર બજારમાં જોખમ છે, પણ યોગ્ય સંશોધન અને ધીરજથી સારો વળતર મળી શકે છે. લાંબા ગાળાનું રોકાણ હંમેશા ફાયદાકારક સાબિત થાય છે.</p>
    
    <h2>વધુ માહિતી</h2>
    <p>આ સમાચાર વિશે વધુ માહિતી માટે, મૂળ સ્રોત પર જાઓ. ત્યાં તમને સંપૂર્ણ વિગતો મળશે. અમારી વેબસાઇટ પર રોજ નવા સમાચાર આવે છે, તેથી નિયમિત મુલાકાત લેતા રહો.</p>
    
    <p>અમારી વેબસાઇટ ભારતીય શેર બજાર, બિઝનેસ અને અર્થતંત્ર સંબંધિત તાજા સમાચાર પ્રદાન કરે છે. અમે Moneycontrol, Economic Times, Livemint જેવા વિશ્વસનીય સ્રોતોમાંથી સમાચાર લાવીએ છીએ અને તેને સરળ હિન્દીમાં રજૂ કરીએ છીએ.</p>
    """
    
    filename = clean_filename(title, index) + '.html'
    
    html_content = f"""<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - भारत न्यूज़</title>
    <meta name="description" content="{summary[:150]}">
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Devanagari:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Noto Sans Devanagari', Arial, sans-serif; 
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            color: #e0e0e0;
            padding: 30px 20px;
            line-height: 1.8;
        }}
        .container {{ max-width: 800px; margin: auto; background: rgba(255,255,255,0.07); padding: 30px; border-radius: 15px; }}
        h1 {{ color: #feca57; font-size: 26px; margin-bottom: 20px; line-height: 1.5; }}
        h2 {{ color: #ff6b6b; margin-top: 25px; margin-bottom: 15px; font-size: 20px; }}
        p {{ color: #b0b0b0; margin-bottom: 15px; font-size: 16px; }}
        a {{ color: #48dbfb; }}
        .source-box {{
            background: rgba(255,255,255,0.05);
            padding: 15px;
            border-radius: 10px;
            margin: 20px 0;
            border-left: 4px solid #feca57;
        }}
        .back-btn {{
            display: inline-block;
            background: linear-gradient(90deg, #ff6b6b, #ee5a6f);
            color: white;
            padding: 12px 25px;
            text-decoration: none;
            border-radius: 8px;
            margin-top: 20px;
            font-weight: 600;
        }}
        .back-btn:hover {{ background: linear-gradient(90deg, #feca57, #ff9f43); }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        
        <div class="source-box">
            📰 स्रोत: {source} | 🕐 {date}
        </div>
        
        {full_article}
        
        <div class="source-box">
            <strong>मूल स्रोत:</strong> <a href="{link}" target="_blank">पूरी न्यूज़ यहाँ पढ़ें →</a>
        </div>
        
        <a href="../index.html" class="back-btn">← होम पेज पर जाएं</a>
    </div>
</body>
</html>"""
    
    with open(f'news/{filename}', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return filename

def main():
    if not os.path.exists('news_data.json'):
        print("❌ news_data.json મળી નથી!")
        return
    
    with open('news_data.json', 'r', encoding='utf-8') as f:
        news_list = json.load(f)
    
    print(f"📰 કુલ {len(news_list)} ન્યૂઝ મળ્યા")
    
    generated = []
    for i, news in enumerate(news_list[:30]):
        try:
            filename = generate_article_page(news, i)
            generated.append(filename)
            print(f"✅ [{i+1}] {filename}")
        except Exception as e:
            print(f"❌ [{i+1}] એરર: {e}")
    
    print(f"\n🎉 કુલ {len(generated)} પેજ બન્યા!")
    
    # news_index.json બનાવો
    with open('news_index.json', 'w', encoding='utf-8') as f:
        json.dump(generated, f, ensure_ascii=False, indent=4)
    
    # ═══════════════════════════════════════
    # sitemap.xml બનાવો (ઓટોમેટિક)
    # ═══════════════════════════════════════
    sitemap_urls = [
        "https://mybharatnews.github.io/bharatnews/",
        "https://mybharatnews.github.io/bharatnews/about.html",
        "https://mybharatnews.github.io/bharatnews/contact.html",
        "https://mybharatnews.github.io/bharatnews/privacy.html",
    ]
    
    for filename in generated:
        sitemap_urls.append(f"https://mybharatnews.github.io/bharatnews/news/{filename}")
    
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    
    for url in sitemap_urls:
        sitemap += f'    <url>\n'
        sitemap += f'        <loc>{url}</loc>\n'
        sitemap += f'        <changefreq>daily</changefreq>\n'
        sitemap += f'        <priority>0.8</priority>\n'
        sitemap += f'    </url>\n'
    
    sitemap += '</urlset>'
    
    with open('sitemap.xml', 'w', encoding='utf-8') as f:
        f.write(sitemap)
    
    print(f"\n📄 sitemap.xml બન્યું ({len(sitemap_urls)} URLs)")

if __name__ == "__main__":
    main()
