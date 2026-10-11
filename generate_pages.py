import json
import os
import re
import email.utils
from datetime import datetime

# ફોલ્ડર બનાવો
os.makedirs('news', exist_ok=True)

# ═══ Site Information ═══
SITE_NAME = "भारत न्यूज़"
SITE_URL = "https://mybharatnews.github.io/bharatnews"
SITE_LANG = "hi"

def clean_filename(text, index=0):
    """SEO ફ્રેન્ડલી ફાઈલ નામ બનાવો"""
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'\s+', '-', text)
    text = re.sub(r'-+', '-', text)
    text = text.strip('-')
    
    today = datetime.now().strftime('%Y%m%d')
    
    if not text or len(text) < 10:
        text = f"market-news-{index}-{today}"
    else:
        text = f"market-news-{text}"
    
    return text[:60].lower()

def escape_xml(text):
    """XML માટે special characters escape કરો"""
    return (str(text)
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
            .replace("'", '&apos;'))

def escape_html(text):
    """HTML માટે special characters escape કરો"""
    return (str(text)
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;'))

def parse_date_to_iso(date_str):
    """Date string ને ISO format માં બદલો (schema.org માટે)"""
    try:
        # Try different formats
        for fmt in ['%d-%m-%Y %H:%M', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M']:
            try:
                dt = datetime.strptime(date_str.strip(), fmt)
                return dt.strftime('%Y-%m-%dT%H:%M:%S+05:30')
            except:
                continue
    except:
        pass
    return datetime.now().strftime('%Y-%m-%dT%H:%M:%S+05:30')

def generate_structured_data(title, summary, page_url, date_iso, source):
    """NewsArticle Structured Data (JSON-LD) બનાવો"""
    # JSON escape
    title_esc = title.replace('"', '\\"').replace('\\', '\\\\')
    summary_esc = summary[:160].replace('"', '\\"').replace('\\', '\\\\')
    source_esc = source.replace('"', '\\"').replace('\\', '\\\\')
    
    return f'''<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "NewsArticle",
  "headline": "{title_esc}",
  "description": "{summary_esc}",
  "datePublished": "{date_iso}",
  "dateModified": "{date_iso}",
  "author": {{
    "@type": "Organization",
    "name": "{SITE_NAME}"
  }},
  "publisher": {{
    "@type": "Organization",
    "name": "{SITE_NAME}",
    "logo": {{
      "@type": "ImageObject",
      "url": "{SITE_URL}/icon.png"
    }}
  }},
  "mainEntityOfPage": {{
    "@type": "WebPage",
    "@id": "{page_url}"
  }},
  "articleSection": "Business",
  "inLanguage": "hi-IN",
  "isAccessibleForFree": true,
  "sourceOrganization": {{
    "@type": "Organization",
    "name": "{source_esc}"
  }}
}}
</script>'''

def generate_related_news(current_index, all_news, current_filename):
    """સંબંધિત 5 ન્યૂઝની લિંક બનાવો (Internal Linking)"""
    related = []
    total = len(all_news)
    
    # Next 3 + Previous 2 (circular)
    offsets = [1, 2, 3, -1, -2]
    
    for offset in offsets:
        idx = (current_index + offset) % total
        if idx == current_index:
            continue
        if len(related) >= 5:
            break
        
        news_item = all_news[idx]
        rel_title = news_item.get('title', '')[:80]
        rel_filename = clean_filename(news_item.get('title', ''), idx) + '.html'
        related.append((rel_filename, rel_title))
    
    if not related:
        return ""
    
    html = '<div class="related-news">'
    html += '<h3>📚 આ પણ વાંચો</h3>'
    html += '<ul>'
    for rel_file, rel_title in related:
        html += f'<li><a href="{rel_file}">{escape_html(rel_title)}</a></li>'
    html += '</ul>'
    html += '</div>'
    
    return html

def generate_article_page(news_item, index, all_news):
    """દરેક ન્યૂઝ માટે અલગ પેજ બનાવો"""
    
    title = news_item.get('title', '')
    summary = news_item.get('summary', '')
    link = news_item.get('link', '')
    source = news_item.get('source', '')
    date = news_item.get('date', '')
    
    filename = clean_filename(title, index) + '.html'
    page_url = f"{SITE_URL}/news/{filename}"
    
    # ISO date for schema
    date_iso = parse_date_to_iso(date)
    
    # Escape HTML
    title_esc = escape_html(title)
    summary_esc = escape_html(summary[:150])
    
    # Structured Data
    structured_data = generate_structured_data(title, summary, page_url, date_iso, source)
    
    # Related News (Internal Linking)
    related_news = generate_related_news(index, all_news, filename)
    
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
    
    html_content = f"""<!DOCTYPE html>
<html lang="{SITE_LANG}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title_esc} - {SITE_NAME}</title>
    <meta name="description" content="{summary_esc}">
    <meta name="keywords" content="share market, stock market, hindi news, business, sensex, nifty, भारत न्यूज़">
    <meta name="author" content="{SITE_NAME}">
    <meta name="robots" content="index, follow, max-image-preview:large">
    <link rel="canonical" href="{page_url}">
    
    <!-- Open Graph -->
    <meta property="og:title" content="{title_esc}">
    <meta property="og:description" content="{summary_esc}">
    <meta property="og:url" content="{page_url}">
    <meta property="og:type" content="article">
    <meta property="og:site_name" content="{SITE_NAME}">
    <meta property="og:locale" content="hi_IN">
    
    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary">
    <meta name="twitter:title" content="{title_esc}">
    <meta name="twitter:description" content="{summary_esc}">
    
    <!-- Structured Data (Google News Rich Results) -->
    {structured_data}
    
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Devanagari:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Noto Sans Devanagari', Arial, sans-serif; background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); color: #e0e0e0; padding: 30px 20px; line-height: 1.8; }}
        .container {{ max-width: 800px; margin: auto; background: rgba(255,255,255,0.07); padding: 30px; border-radius: 15px; }}
        h1 {{ color: #feca57; font-size: 26px; margin-bottom: 20px; line-height: 1.5; }}
        h2 {{ color: #ff6b6b; margin-top: 25px; margin-bottom: 15px; font-size: 20px; }}
        h3 {{ color: #48dbfb; margin-top: 20px; margin-bottom: 12px; font-size: 18px; }}
        p {{ color: #b0b0b0; margin-bottom: 15px; font-size: 16px; }}
        a {{ color: #48dbfb; }}
        .source-box {{ background: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px; margin: 20px 0; border-left: 4px solid #feca57; }}
        .back-btn {{ display: inline-block; background: linear-gradient(90deg, #ff6b6b, #ee5a6f); color: white; padding: 12px 25px; text-decoration: none; border-radius: 8px; margin-top: 20px; font-weight: 600; }}
        .back-btn:hover {{ background: linear-gradient(90deg, #feca57, #ff9f43); }}
        
        /* Related News Styles */
        .related-news {{ margin-top: 30px; padding: 20px; background: rgba(72, 219, 251, 0.08); border-radius: 12px; border-left: 4px solid #48dbfb; }}
        .related-news h3 {{ margin-top: 0; }}
        .related-news ul {{ list-style: none; padding-left: 0; }}
        .related-news li {{ margin-bottom: 12px; padding-left: 20px; position: relative; }}
        .related-news li::before {{ content: "▸"; position: absolute; left: 0; color: #48dbfb; }}
        .related-news a {{ color: #e0e0e0; text-decoration: none; transition: color 0.3s; }}
        .related-news a:hover {{ color: #feca57; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title_esc}</h1>
        <div class="source-box">📰 स्रोत: {source} | 🕐 {date}</div>
        {full_article}
        <div class="source-box"><strong>मूल स्रोत:</strong> <a href="{link}" target="_blank" rel="noopener nofollow">पूरी न्यूज़ यहाँ पढ़ें →</a></div>
        
        {related_news}
        
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
            filename = generate_article_page(news, i, news_list[:30])
            generated.append(filename)
            print(f"✅ [{i+1}] {filename}")
        except Exception as e:
            print(f"❌ [{i+1}] એરર: {e}")
    
    print(f"\n🎉 કુલ {len(generated)} પેજ બન્યા!")
    
    with open('news_index.json', 'w', encoding='utf-8') as f:
        json.dump(generated, f, ensure_ascii=False, indent=4)
    
    # ═══ sitemap.xml ═══
    sitemap_urls = [
        f"{SITE_URL}/",
        f"{SITE_URL}/about.html",
        f"{SITE_URL}/contact.html",
        f"{SITE_URL}/privacy.html",
    ]
    for filename in generated:
        sitemap_urls.append(f"{SITE_URL}/news/{filename}")
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    
    for url in sitemap_urls:
        if url.endswith('/bharatnews/'):
            priority, changefreq = '1.0', 'hourly'
        elif 'about' in url or 'contact' in url:
            priority, changefreq = '0.7', 'weekly'
        elif 'privacy' in url:
            priority, changefreq = '0.5', 'monthly'
        else:
            priority, changefreq = '0.8', 'daily'
        
        sitemap += f'    <url>\n'
        sitemap += f'        <loc>{url}</loc>\n'
        sitemap += f'        <lastmod>{today}</lastmod>\n'
        sitemap += f'        <changefreq>{changefreq}</changefreq>\n'
        sitemap += f'        <priority>{priority}</priority>\n'
        sitemap += f'    </url>\n'
    
    sitemap += '</urlset>'
    
    with open('sitemap.xml', 'w', encoding='utf-8') as f:
        f.write(sitemap)
    
    print(f"\n📄 sitemap.xml બન્યું ({len(sitemap_urls)} URLs)")
    
    # ═══ rss.xml ═══
    now = email.utils.formatdate(localtime=True)
    
    rss_items = ""
    for i, news in enumerate(news_list[:30]):
        title = escape_xml(news.get('title', ''))
        summary = escape_xml(news.get('summary', ''))
        source = escape_xml(news.get('source', ''))
        link_original = news.get('link', '')
        
        filename = generated[i] if i < len(generated) else ''
        page_url = f"{SITE_URL}/news/{filename}"
        
        rss_items += f"""    <item>
      <title>{title}</title>
      <link>{page_url}</link>
      <description>{summary[:300]}</description>
      <pubDate>{now}</pubDate>
      <guid>{page_url}</guid>
      <source url="{escape_xml(link_original)}">{source}</source>
    </item>
"""
    
    rss = '<?xml version="1.0" encoding="UTF-8"?>\n'
    rss += '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">\n'
    rss += '  <channel>\n'
    rss += f'    <title>{SITE_NAME} - શેર બજારની તાજી હિન્દી અપડેટ્સ</title>\n'
    rss += f'    <link>{SITE_URL}/</link>\n'
    rss += '    <description>શેર બજાર, બિઝનેસ અને અર્થતંત્રની તાજી હિન્દી અપડેટ્સ</description>\n'
    rss += '    <language>hi-in</language>\n'
    rss += f'    <copyright>© 2026 {SITE_NAME}</copyright>\n'
    rss += f'    <lastBuildDate>{now}</lastBuildDate>\n'
    rss += f'    <pubDate>{now}</pubDate>\n'
    rss += '    <ttl>60</ttl>\n'
    rss += f'    <atom:link href="{SITE_URL}/rss.xml" rel="self" type="application/rss+xml"/>\n'
    rss += rss_items
    rss += '  </channel>\n'
    rss += '</rss>'
    
    with open('rss.xml', 'w', encoding='utf-8') as f:
        f.write(rss)
    
    print(f"\n📡 rss.xml બન્યું ({len(generated)} items)")

if __name__ == "__main__":
    main()
