import json
import os
import re
import glob
import hashlib
import email.utils
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# ═══════════════════════════════════════════════════════
# ═══ Site Information ═══
# ═══════════════════════════════════════════════════════
SITE_NAME = "भारत न्यूज़"
SITE_URL = "https://mybharatnews.github.io/bharatnews"
SITE_LANG = "hi"

WHATSAPP_CHANNEL = "https://whatsapp.com/channel/0029VbD6VLP6buMSzAGWNE3V"
TELEGRAM_CHANNEL = "https://t.me/indianews_official"
FACEBOOK_PAGE = "https://www.facebook.com/profile.php?id=61595205934642"

IST = ZoneInfo("Asia/Kolkata")
MAX_NEWS = 30
MAX_NEWS_SITEMAP = 10
NEWS_SITEMAP_DAYS = 7   # Google News: છેલ્લા 7 દિવસ

# ફોલ્ડર બનાવો
os.makedirs('news', exist_ok=True)


# ═══════════════════════════════════════════════════════
# ═══ Escape Helpers ═══
# ═══════════════════════════════════════════════════════
def escape_xml(text):
    return (str(text)
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
            .replace("'", '&apos;'))

def escape_html(text):
    return (str(text)
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
            .replace("'", '&#39;'))

def escape_js(text):
    return (str(text)
            .replace('\\', '\\\\')
            .replace('</', '<\\/')
            .replace("'", "\\'")
            .replace('"', '\\"')
            .replace('\n', '\\n')
            .replace('\r', ''))


# ═══════════════════════════════════════════════════════
# ═══ Date Helpers ═══
# ═══════════════════════════════════════════════════════
def parse_date_ist(date_str):
    for fmt in ['%d-%m-%Y %H:%M', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M']:
        try:
            return datetime.strptime(date_str.strip(), fmt).replace(tzinfo=IST)
        except:
            continue
    return datetime.now(IST)

def parse_date_to_iso(date_str):
    return parse_date_ist(date_str).isoformat()


# ═══════════════════════════════════════════════════════
# ═══ Stable Slug ═══
# ═══════════════════════════════════════════════════════
def make_slug(news_item):
    key = (news_item.get('link', '') + '|' + news_item.get('title', '')).encode('utf-8')
    h = hashlib.sha1(key).hexdigest()[:12]
    return f"market-news-{h}"


# ═══════════════════════════════════════════════════════
# ═══ Structured Data ═══
# ═══════════════════════════════════════════════════════
def generate_structured_data(title, summary, page_url, date_iso, source):
    data = {
        "@context": "https://schema.org",
        "@type": "NewsArticle",
        "headline": title[:110],
        "description": summary[:160],
        "datePublished": date_iso,
        "dateModified": date_iso,
        "author": {"@type": "Organization", "name": SITE_NAME},
        "publisher": {"@type": "Organization", "name": SITE_NAME},
        "mainEntityOfPage": {"@type": "WebPage", "@id": page_url},
        "articleSection": "Business",
        "inLanguage": "hi-IN",
        "isAccessibleForFree": True,
        "sourceOrganization": {"@type": "Organization", "name": source},
    }
    return ('<script type="application/ld+json">\n'
            + json.dumps(data, ensure_ascii=False, indent=2)
            + '\n</script>')


# ═══════════════════════════════════════════════════════
# ═══ Copy & Go Button ═══
# ═══════════════════════════════════════════════════════
def generate_copy_go_button(title, page_url):
    js_title = escape_js(title)
    js_url = escape_js(page_url)
    js_fb = escape_js(FACEBOOK_PAGE)
    js_wa = escape_js(WHATSAPP_CHANNEL)
    js_tg = escape_js(TELEGRAM_CHANNEL)
    js_site = escape_js(SITE_URL + "/")

    return f'''
    <div class="copy-go-section">
        <h3>📤 Post to Facebook Page</h3>
        <button onclick="copyAndGoToFacebook()" class="copy-go-btn">📘 Facebook પર પોસ્ટ કરો (Copy & Go)</button>
        <div id="copy-status" style="margin-top: 10px; font-size: 14px;"></div>
    </div>
    <script>
    function copyAndGoToFacebook() {{
        const caption = "📰 " + "{js_title}" + "\\n\\n🔗 पूरी खबर: " + "{js_url}" + "\\n\\n📊 Bharat News Hindi\\n🌐 {js_site}\\n💬 WhatsApp: {js_wa}\\n📢 Telegram: {js_tg}\\n\\n#ShareMarket #Nifty #Sensex";
        function onDone() {{
            document.getElementById('copy-status').innerHTML = '<span style="color: #25d366;">✅ Caption copy થઈ ગયું!</span>';
            setTimeout(function() {{ window.open("{js_fb}", '_blank'); }}, 500);
        }}
        if (navigator.clipboard) {{ navigator.clipboard.writeText(caption).then(onDone); }}
        else {{ const t=document.createElement('textarea'); t.value=caption; document.body.appendChild(t); t.select(); document.execCommand('copy'); document.body.removeChild(t); onDone(); }}
    }}
    </script>
    '''


# ═══════════════════════════════════════════════════════
# ═══ Social Share & Follow ═══
# ═══════════════════════════════════════════════════════
def generate_share_buttons(page_url, title):
    import urllib.parse
    e_url = urllib.parse.quote(page_url)
    e_title = urllib.parse.quote(title[:100])
    return f'''
    <div class="share-section">
        <h3>📤 Share this news</h3>
        <div class="share-buttons">
            <a href="https://api.whatsapp.com/send?text={e_title}%20{e_url}" target="_blank" class="share-btn whatsapp">💬 WhatsApp</a>
            <a href="https://t.me/share/url?url={e_url}&text={e_title}" target="_blank" class="share-btn telegram">📢 Telegram</a>
            <a href="{FACEBOOK_PAGE}" target="_blank" class="share-btn facebook">📘 Facebook Page</a>
        </div>
    </div>
    '''

def generate_social_follow():
    return f'''
    <div class="social-follow">
        <h3>📱 Follow us for daily updates</h3>
        <div class="follow-buttons">
            <a href="{WHATSAPP_CHANNEL}" target="_blank" class="follow-btn whatsapp-follow">💬 WhatsApp</a>
            <a href="{TELEGRAM_CHANNEL}" target="_blank" class="follow-btn telegram-follow">📢 Telegram</a>
            <a href="{FACEBOOK_PAGE}" target="_blank" class="follow-btn facebook-follow">📘 Facebook</a>
        </div>
    </div>
    '''


# ═══════════════════════════════════════════════════════
# ═══ Related News ═══
# ═══════════════════════════════════════════════════════
def generate_related_news(current_index, all_news):
    total = len(all_news)
    if total <= 1: return ""
    related = []
    for offset in [1, 2, 3, -1, -2]:
        idx = (current_index + offset) % total
        if idx == current_index: continue
        if len(related) >= 5: break
        item = all_news[idx]
        related.append((make_slug(item) + '.html', item.get('title', '')[:80]))
    if not related: return ""
    html = '<div class="related-news"><h3>📚 આ પણ વાંચો</h3><ul>'
    for f, t in related: html += f'<li><a href="{f}">{escape_html(t)}</a></li>'
    html += '</ul></div>'
    return html


# ═══════════════════════════════════════════════════════
# ═══ Article Page ═══
# ═══════════════════════════════════════════════════════
def generate_article_page(news_item, index, all_news):
    title = news_item.get('title', '')
    summary = news_item.get('summary', '')
    link = news_item.get('link', '')
    source = news_item.get('source', '')
    date = news_item.get('date', '')

    filename = make_slug(news_item) + '.html'
    page_url = f"{SITE_URL}/news/{filename}"

    date_iso = parse_date_to_iso(date)
    
    # Escape
    t_esc = escape_html(title)
    s_esc = escape_html(summary[:150])
    sf_esc = escape_html(summary)
    src_esc = escape_html(source)
    dt_esc = escape_html(date)
    lnk_esc = escape_html(link)

    structured_data = generate_structured_data(title, summary, page_url, date_iso, source)
    related_news = generate_related_news(index, all_news)
    share_buttons = generate_share_buttons(page_url, title)
    social_follow = generate_social_follow()
    copy_go_button = generate_copy_go_button(title, page_url)

    full_article = f"""
    <p><strong>{sf_esc}</strong></p>
    <p>આ સમાચાર {src_esc} દ્વારા પ્રકાશિત કરવામાં આવ્યા છે. ભારતીય શેર બજારમાં આ સમાચારની ખૂબ અસર પડી શકે છે.</p>
    <h2>શેર બજાર પર અસર</h2>
    <p>ભારતીય શેર બજારમાં આજે મોટી હલચલ જોવા મળી રહી છે. નિફ્ટી 50 અને સેન્સેક્સમાં ઉતાર-ચઢાવ જોવા મળી રહ્યો છે.</p>
    <p>નિષ્ણાતોના મતે, આ સમાચાર ટૂંકા ગાળામાં બજારને અસર કરી શકે છે. પણ લાંબા ગાળે બજારના મૂળભૂત સિદ્ધાંતો જ મહત્વના છે.</p>
    <h2>રોકાણકારો માટે સલાહ</h2>
    <p>શેર બજારમાં રોકાણ કરતી વખતે હંમેશા સંશોધન કરો. કોઈપણ સમાચારને આધારે તરત જ નિર્ણય ના લો.</p>
    """

    html_content = f"""<!DOCTYPE html>
<html lang="{SITE_LANG}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{t_esc} - {SITE_NAME}</title>
    <meta name="description" content="{s_esc}">
    <link rel="canonical" href="{page_url}">
    <meta property="og:title" content="{t_esc}">
    <meta property="og:description" content="{s_esc}">
    <meta property="og:url" content="{page_url}">
    <meta property="og:type" content="article">
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
        
        .copy-go-section {{ margin: 30px 0; padding: 25px; background: rgba(24, 119, 242, 0.15); border-radius: 12px; border-left: 4px solid #1877f2; text-align: center; }}
        .copy-go-btn {{ background: #1877f2; color: white; padding: 15px 30px; border: none; border-radius: 10px; font-weight: 700; cursor: pointer; }}
        
        .share-section, .social-follow, .related-news {{ margin: 30px 0; padding: 20px; background: rgba(72, 219, 251, 0.08); border-radius: 12px; border-left: 4px solid #48dbfb; }}
        .share-buttons, .follow-buttons {{ display: flex; gap: 10px; flex-wrap: wrap; margin-top: 15px; }}
        .share-btn, .follow-btn {{ padding: 10px 18px; border-radius: 8px; text-decoration: none; color: white; font-weight: 600; }}
        .whatsapp {{ background: #25d366; }} .telegram {{ background: #0088cc; }} .facebook {{ background: #1877f2; }}
        
        .related-news ul {{ list-style: none; padding-left: 0; }}
        .related-news li {{ margin-bottom: 12px; padding-left: 20px; position: relative; }}
        .related-news li::before {{ content: "▸"; position: absolute; left: 0; color: #48dbfb; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{t_esc}</h1>
        <div class="source-box">📰 स्रोत: {src_esc} | 🕐 {dt_esc}</div>
        {full_article}
        <div class="source-box"><strong>मूल स्रोत:</strong> <a href="{lnk_esc}" target="_blank" rel="nofollow">पूरी न्यूज़ यहाँ पढ़ें →</a></div>
        {copy_go_button}
        {share_buttons}
        {social_follow}
        {related_news}
        <a href="../index.html" class="back-btn">← होम पेज पर जाएं</a>
    </div>
</body>
</html>"""

    with open(f'news/{filename}', 'w', encoding='utf-8') as f:
        f.write(html_content)
    return filename


# ═══════════════════════════════════════════════════════
# ═══ Index Page (Home Page) ═══
# ═══════════════════════════════════════════════════════
def generate_index_page(news_list, generated_files):
    news_cards = ""
    for news, filename in zip(news_list, generated_files):
        title = escape_html(news.get('title', ''))
        summary = escape_html(news.get('summary', '')[:150])
        source = escape_html(news.get('source', ''))
        date = escape_html(news.get('date', ''))
        news_cards += f'''
        <article class="news-card">
            <h2><a href="news/{filename}">{title}</a></h2>
            <div class="news-meta">📰 {source} | 🕐 {date}</div>
            <p>{summary}...</p>
            <a href="news/{filename}" class="read-more">पूरी खबर पढ़ें →</a>
        </article>
        '''

    html_content = f"""<!DOCTYPE html>
<html lang="{SITE_LANG}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{SITE_NAME} - भारतीय शेयर बाजार की ताज़ा हिंदी अपडेट्स</title>
    <link rel="canonical" href="{SITE_URL}/">
    <link rel="alternate" type="application/rss+xml" title="RSS Feed" href="{SITE_URL}/rss.xml">
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Devanagari:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Noto Sans Devanagari', Arial, sans-serif; background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); color: #e0e0e0; padding: 20px; line-height: 1.7; }}
        .container {{ max-width: 900px; margin: auto; }}
        header {{ text-align: center; padding: 40px 20px; background: rgba(255,255,255,0.05); border-radius: 15px; margin-bottom: 30px; }}
        header h1 {{ color: #feca57; font-size: 32px; margin-bottom: 10px; }}
        header p {{ color: #b0b0b0; font-size: 16px; }}
        .social-links {{ display: flex; gap: 10px; justify-content: center; flex-wrap: wrap; margin-top: 20px; }}
        .social-links a {{ padding: 10px 18px; border-radius: 8px; text-decoration: none; color: white; font-weight: 600; font-size: 14px; }}
        .social-links .wa {{ background: #25d366; }} .social-links .tg {{ background: #0088cc; }} .social-links .fb {{ background: #1877f2; }}
        
        /* 👇 એપ ડાઉનલોડ બેનર નો CSS 👇 */
        .app-download-banner {{
            background: linear-gradient(135deg, #1e130c, #9a8478);
            border-radius: 15px;
            padding: 25px 20px;
            margin-bottom: 30px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        }}
        .app-text h3 {{ color: #feca57; font-size: 22px; margin-bottom: 8px; }}
        .app-text p {{ color: #e0e0e0; font-size: 15px; margin-bottom: 20px; }}
        .app-buttons {{ display: flex; justify-content: center; gap: 15px; flex-wrap: wrap; }}
        .btn-online, .btn-download {{
            display: inline-block; padding: 12px 25px; text-decoration: none;
            border-radius: 8px; font-weight: bold; font-size: 16px; color: white;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .btn-online {{ background: #00c853; box-shadow: 0 4px 10px rgba(0, 200, 83, 0.3); }}
        .btn-online:hover {{ background: #00e676; transform: translateY(-3px); }}
        .btn-download {{ background: #1877f2; box-shadow: 0 4px 10px rgba(24, 119, 242, 0.3); }}
        .btn-download:hover {{ background: #0d5bbf; transform: translateY(-3px); }}
        /* 👆 એપ બેનર CSS પૂરો 👆 */

        .news-card {{ background: rgba(255,255,255,0.07); padding: 25px; border-radius: 12px; margin-bottom: 20px; }}
        .news-card h2 {{ font-size: 20px; margin-bottom: 10px; line-height: 1.4; }}
        .news-card h2 a {{ color: #feca57; text-decoration: none; }}
        .news-meta {{ color: #48dbfb; font-size: 13px; margin-bottom: 12px; }}
        .news-card p {{ color: #b0b0b0; font-size: 15px; margin-bottom: 12px; }}
        .read-more {{ display: inline-block; color: #ff6b6b; text-decoration: none; font-weight: 600; font-size: 14px; }}
        footer {{ text-align: center; padding: 30px 20px; color: #666; font-size: 13px; }}
        footer a {{ color: #48dbfb; text-decoration: none; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📊 {SITE_NAME}</h1>
            <p>भारतीय शेयर बाजार और बिजनेस की ताज़ा हिंदी अपडेट्स</p>
            <div class="social-links">
                <a href="{WHATSAPP_CHANNEL}" target="_blank" class="wa">💬 WhatsApp</a>
                <a href="{TELEGRAM_CHANNEL}" target="_blank" class="tg">📢 Telegram</a>
                <a href="{FACEBOOK_PAGE}" target="_blank" class="fb">📘 Facebook</a>
            </div>
        </header>

        <!-- 👇 અહીં એપ ડાઉનલોડ બેનર શરૂ થાય છે 👇 -->
        <div class="app-download-banner">
            <div class="app-text">
                <h3>📱 Dravy's English Learning App</h3>
                <p>ધોરણ 7 ના વિદ્યાર્થીઓ માટે અંગ્રેજી શીખવા માટેની શ્રેષ્ઠ એપ.</p>
            </div>
            <div class="app-buttons">
                <!-- ઓનલાઇન ઓપન બટન -->
                <a href="https://mybharatnews.github.io/kids-activity-app/" target="_blank" class="btn-online">
                    🌐 ઓનલાઇન ખોલો
                </a>
                <!-- ડાઉનલોડ બટન -->
                <a href="https://mybharatnews.github.io/kids-activity-app/" download class="btn-download">
                    ⬇️ ઓફલાઇન ડાઉનલોડ કરો
                </a>
            </div>
        </div>
        <!-- 👆 એપ બેનર પૂરો થયો 👆 -->

        {news_cards}

        <footer>
            <p>© 2026 {SITE_NAME}</p>
            <p>📡 <a href="rss.xml">RSS Feed</a> | 🗺️ <a href="sitemap.xml">Sitemap</a></p>
        </footer>
    </div>
</body>
</html>"""
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    print("🏠 index.html બન્યું")


# ═══════════════════════════════════════════════════════
# ═══ Sitemaps & Feeds ═══
# ═══════════════════════════════════════════════════════
def generate_sitemap(generated_files):
    today = datetime.now(IST).strftime('%Y-%m-%d')
    urls = [f"{SITE_URL}/"] + [f"{SITE_URL}/news/{f}" for f in generated_files]
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for url in urls:
        sitemap += f'    <url>\n        <loc>{escape_xml(url)}</loc>\n        <lastmod>{today}</lastmod>\n        <changefreq>daily</changefreq>\n        <priority>{"1.0" if url == SITE_URL+"/" else "0.8"}</priority>\n    </url>\n'
    sitemap += '</urlset>'
    with open('sitemap.xml', 'w', encoding='utf-8') as f: f.write(sitemap)
    print(f"📄 sitemap.xml બન્યું ({len(urls)} URLs)")

def generate_news_sitemap(news_list, generated_files):
    cutoff = datetime.now(IST) - timedelta(days=NEWS_SITEMAP_DAYS)
    today = datetime.now(IST).strftime('%Y-%m-%d')
    eligible = []
    for i, news in enumerate(news_list):
        if i >= len(generated_files): break
        dt = parse_date_ist(news.get('date', ''))
        if dt < cutoff or dt > datetime.now(IST) + timedelta(hours=1): continue
        eligible.append((news, generated_files[i], dt))
    eligible = eligible[:1000]

    news_sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">\n'
    for news, filename, dt in eligible:
        title = escape_xml(news.get('title', '')[:110])
        page_url = f"{SITE_URL}/news/{filename}"
        news_sitemap += f'''  <url>
    <loc>{escape_xml(page_url)}</loc>
    <lastmod>{today}</lastmod>
    <news:news>
      <news:publication><news:name>{escape_xml(SITE_NAME)}</news:name><news:language>hi</news:language></news:publication>
      <news:publication_date>{dt.isoformat()}</news:publication_date>
      <news:title>{title}</news:title>
      <news:keywords>share market, stock market, sensex, nifty, business</news:keywords>
    </news:news>
  </url>\n'''
    news_sitemap += '</urlset>'
    with open('news-sitemap.xml', 'w', encoding='utf-8') as f: f.write(news_sitemap)
    print(f"📰 news-sitemap.xml બન્યું ({len(eligible)} URLs)")

def generate_sitemap_index():
    today = datetime.now(IST).strftime('%Y-%m-%d')
    idx = '<?xml version="1.0" encoding="UTF-8"?>\n<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for name in ['sitemap.xml', 'news-sitemap.xml']:
        idx += f'  <sitemap>\n    <loc>{SITE_URL}/{name}</loc>\n    <lastmod>{today}</lastmod>\n  </sitemap>\n'
    idx += '</sitemapindex>'
    with open('sitemap_index.xml', 'w', encoding='utf-8') as f: f.write(idx)
    print("🗂️ sitemap_index.xml બન્યું")

def generate_robots():
    robots = f"User-agent: *\nAllow: /\nDisallow: /news_index.json\nDisallow: /news_data.json\n\nUser-agent: Googlebot-News\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\nSitemap: {SITE_URL}/news-sitemap.xml\n"
    with open('robots.txt', 'w', encoding='utf-8') as f: f.write(robots)
    print("🤖 robots.txt બન્યું")

def generate_rss(news_list, generated_files):
    now = email.utils.format_datetime(datetime.now(IST))
    rss_items = ""
    for news, filename in zip(news_list, generated_files):
        page_url = f"{SITE_URL}/news/{filename}"
        pub_date = email.utils.format_datetime(parse_date_ist(news.get('date', '')))
        rss_items += f'''    <item>
      <title>{escape_xml(news.get('title', ''))}</title>
      <link>{escape_xml(page_url)}</link>
      <description>{escape_xml(news.get('summary', '')[:300])}</description>
      <pubDate>{pub_date}</pubDate>
      <guid>{escape_xml(page_url)}</guid>
    </item>\n'''
    rss = f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>{escape_xml(SITE_NAME)} - શેર બજારની તાજી હિન્દી અપડેટ્સ</title>
    <link>{SITE_URL}/</link>
    <description>શેર બજાર, બિઝનેસ અને અર્થતંત્રની તાજી હિન્દી અપડેટ્સ</description>
    <language>hi-in</language>
    <lastBuildDate>{now}</lastBuildDate>
    <atom:link href="{SITE_URL}/rss.xml" rel="self" type="application/rss+xml"/>
{rss_items}  </channel>
</rss>'''
    with open('rss.xml', 'w', encoding='utf-8') as f: f.write(rss)
    print(f"📡 rss.xml બન્યું ({len(generated_files)} items)")


# ═══════════════════════════════════════════════════════
# ═══ Main ═══
# ═══════════════════════════════════════════════════════
def main():
    if not os.path.exists('news_data.json'):
        print("❌ news_data.json મળી નથી!")
        return

    with open('news_data.json', 'r', encoding='utf-8') as f:
        news_list = json.load(f)

    print(f"📰 કુલ {len(news_list)} ન્યૂઝ મળ્યા")
    top_news = news_list[:MAX_NEWS]

    if os.path.exists('news'):
        old_files = glob.glob('news/*.html')
        for f in old_files: os.remove(f)
        print(f"🧹 {len(old_files)} જૂની files સાફ કરી")

    generated = []
    for i, news in enumerate(top_news):
        try:
            filename = generate_article_page(news, i, top_news)
            generated.append(filename)
            print(f"✅ [{i+1}] {filename}")
        except Exception as e:
            print(f"❌ [{i+1}] એરર: {e}")

    print(f"\n🎉 કુલ {len(generated)} પેજ બન્યા!")

    with open('news_index.json', 'w', encoding='utf-8') as f:
        json.dump(generated, f, ensure_ascii=False, indent=4)

    generate_index_page(top_news, generated)
    generate_sitemap(generated)
    generate_news_sitemap(top_news, generated)
    generate_sitemap_index()
    generate_robots()
    generate_rss(top_news, generated)

    print("\n✅ બધું તૈયાર! 🎉")

if __name__ == "__main__":
    main()
