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
NEWS_SITEMAP_DAYS = 2   # Google News: છેલ્લા 2 દિવસ

# ફોલ્ડર બનાવો
os.makedirs('news', exist_ok=True)


# ═══════════════════════════════════════════════════════
# ═══ Escape Helpers ═══
# ═══════════════════════════════════════════════════════
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
            .replace('"', '&quot;')
            .replace("'", '&#39;'))


def escape_js(text):
    """JavaScript string માટે escape કરો (XSS-safe)"""
    return (str(text)
            .replace('\\', '\\\\')
            .replace('</', '<\\/')      # ✅ script tag break અટકાવો
            .replace("'", "\\'")
            .replace('"', '\\"')
            .replace('\n', '\\n')
            .replace('\r', ''))


# ═══════════════════════════════════════════════════════
# ═══ Date Helpers ═══
# ═══════════════════════════════════════════════════════
def parse_date_ist(date_str):
    """Date string → IST-aware datetime (fallback: now)"""
    for fmt in ['%d-%m-%Y %H:%M', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M']:
        try:
            return datetime.strptime(date_str.strip(), fmt).replace(tzinfo=IST)
        except:
            continue
    return datetime.now(IST)


def parse_date_to_iso(date_str):
    """Date string → ISO 8601 (schema.org માટે)"""
    return parse_date_ist(date_str).isoformat()


# ═══════════════════════════════════════════════════════
# ═══ Stable Slug (hash-based) ═══
# ═══════════════════════════════════════════════════════
def make_slug(news_item):
    """
    ✅ Stable hash-based filename
    એક જ news હંમેશા એક જ URL પર રહેશે
    """
    key = (news_item.get('link', '') + '|' + news_item.get('title', '')).encode('utf-8')
    h = hashlib.sha1(key).hexdigest()[:12]
    return f"market-news-{h}"


# ═══════════════════════════════════════════════════════
# ═══ Structured Data (JSON-LD) ═══
# ═══════════════════════════════════════════════════════
def generate_structured_data(title, summary, page_url, date_iso, source):
    """NewsArticle Structured Data — json.dumps() થી safe"""
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
    <!-- 🎯 Copy & Go Button -->
    <div class="copy-go-section">
        <h3>📤 Post to Facebook Page</h3>
        <p style="color: #b0b0b0; font-size: 14px; margin-bottom: 15px;">
            1 click → Caption copy + Facebook page open
        </p>
        <button onclick="copyAndGoToFacebook()" class="copy-go-btn">
            📘 Facebook પર પોસ્ટ કરો (Copy & Go)
        </button>
        <div id="copy-status" style="margin-top: 10px; font-size: 14px;"></div>
    </div>

    <script>
    function copyAndGoToFacebook() {{
        const title = "{js_title}";
        const url = "{js_url}";

        const caption = "📰 " + title + "\\n\\n" +
            "🔗 पूरी खबर: " + url + "\\n\\n" +
            "📊 Bharat News Hindi\\n" +
            "🌐 {js_site}\\n" +
            "💬 WhatsApp: {js_wa}\\n" +
            "📢 Telegram: {js_tg}\\n\\n" +
            "#ShareMarket #Nifty #Sensex #Business #India";

        function onCopyDone() {{
            document.getElementById('copy-status').innerHTML =
                '<span style="color: #25d366;">✅ Caption copy થઈ ગયું! Facebook પર paste કરો.</span>';
            setTimeout(function() {{
                window.open("{js_fb}", '_blank');
            }}, 500);
        }}

        if (navigator.clipboard && navigator.clipboard.writeText) {{
            navigator.clipboard.writeText(caption).then(onCopyDone).catch(function() {{
                fallbackCopy(caption);
            }});
        }} else {{
            fallbackCopy(caption);
        }}

        function fallbackCopy(text) {{
            const ta = document.createElement('textarea');
            ta.value = text;
            document.body.appendChild(ta);
            ta.select();
            try {{ document.execCommand('copy'); }} catch(e) {{}}
            document.body.removeChild(ta);
            onCopyDone();
        }}
    }}
    </script>
    '''


# ═══════════════════════════════════════════════════════
# ═══ Social Share Buttons ═══
# ═══════════════════════════════════════════════════════
def generate_share_buttons(page_url, title):
    import urllib.parse
    encoded_url = urllib.parse.quote(page_url)
    encoded_title = urllib.parse.quote(title[:100])

    return f'''
    <div class="share-section">
        <h3>📤 Share this news</h3>
        <div class="share-buttons">
            <a href="https://api.whatsapp.com/send?text={encoded_title}%20{encoded_url}"
               target="_blank" rel="noopener" class="share-btn whatsapp">💬 WhatsApp</a>
            <a href="https://t.me/share/url?url={encoded_url}&text={encoded_title}"
               target="_blank" rel="noopener" class="share-btn telegram">📢 Telegram</a>
            <a href="https://twitter.com/intent/tweet?url={encoded_url}&text={encoded_title}"
               target="_blank" rel="noopener" class="share-btn twitter">🐦 Twitter</a>
            <a href="{FACEBOOK_PAGE}" target="_blank" rel="noopener" class="share-btn facebook">📘 Facebook Page</a>
        </div>
    </div>
    '''


# ═══════════════════════════════════════════════════════
# ═══ Social Follow Buttons ═══
# ═══════════════════════════════════════════════════════
def generate_social_follow():
    return f'''
    <div class="social-follow">
        <h3>📱 Follow us for daily updates</h3>
        <div class="follow-buttons">
            <a href="{WHATSAPP_CHANNEL}" target="_blank" rel="noopener" class="follow-btn whatsapp-follow">💬 WhatsApp Channel</a>
            <a href="{TELEGRAM_CHANNEL}" target="_blank" rel="noopener" class="follow-btn telegram-follow">📢 Telegram Channel</a>
            <a href="{FACEBOOK_PAGE}" target="_blank" rel="noopener" class="follow-btn facebook-follow">📘 Facebook Page</a>
        </div>
    </div>
    '''


# ═══════════════════════════════════════════════════════
# ═══ Related News ═══
# ═══════════════════════════════════════════════════════
def generate_related_news(current_index, all_news):
    total = len(all_news)
    if total <= 1:
        return ""

    related = []
    for offset in [1, 2, 3, -1, -2]:
        idx = (current_index + offset) % total
        if idx == current_index:
            continue
        if len(related) >= 5:
            break
        item = all_news[idx]
        rel_title = item.get('title', '')[:80]
        rel_file = make_slug(item) + '.html'
        related.append((rel_file, rel_title))

    if not related:
        return ""

    html = '<div class="related-news"><h3>📚 આ પણ વાંચો</h3><ul>'
    for rel_file, rel_title in related:
        html += f'<li><a href="{rel_file}">{escape_html(rel_title)}</a></li>'
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

    title_esc = escape_html(title)
    summary_esc = escape_html(summary[:150])
    summary_full_esc = escape_html(summary)      # ✅ XSS fix
    source_esc = escape_html(source)
    date_esc = escape_html(date)
    link_esc = escape_html(link)

    structured_data = generate_structured_data(title, summary, page_url, date_iso, source)
    related_news = generate_related_news(index, all_news)
    share_buttons = generate_share_buttons(page_url, title)
    social_follow = generate_social_follow()
    copy_go_button = generate_copy_go_button(title, page_url)

    full_article = f"""
    <p><strong>{summary_full_esc}</strong></p>

    <p>આ સમાચાર {source_esc} દ્વારા પ્રકાશિત કરવામાં આવ્યા છે. ભારતીય શેર બજારમાં આ સમાચારની ખૂબ અસર પડી શકે છે. રોકાણકારોએ આ સમાચારને ધ્યાનથી વાંચવા જોઈએ અને તેના આધારે પોતાના રોકાણના નિર્ણય લેવા જોઈએ.</p>

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

    <meta property="og:title" content="{title_esc}">
    <meta property="og:description" content="{summary_esc}">
    <meta property="og:url" content="{page_url}">
    <meta property="og:type" content="article">
    <meta property="og:site_name" content="{SITE_NAME}">
    <meta property="og:locale" content="hi_IN">

    <meta name="twitter:card" content="summary">
    <meta name="twitter:title" content="{title_esc}">
    <meta name="twitter:description" content="{summary_esc}">

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
        .copy-go-section {{ margin: 30px 0; padding: 25px; background: linear-gradient(135deg, rgba(24, 119, 242, 0.15), rgba(24, 119, 242, 0.05)); border-radius: 12px; border-left: 4px solid #1877f2; text-align: center; }}
        .copy-go-section h3 {{ margin-top: 0; color: #1877f2; }}
        .copy-go-btn {{ background: #1877f2; color: white; padding: 15px 30px; border: none; border-radius: 10px; font-weight: 700; font-size: 16px; cursor: pointer; transition: all 0.3s; font-family: inherit; }}
        .copy-go-btn:hover {{ background: #0d5bbf; transform: translateY(-2px); box-shadow: 0 5px 20px rgba(24, 119, 242, 0.4); }}
        .copy-go-btn:active {{ transform: translateY(0); }}
        .share-section {{ margin: 30px 0; padding: 20px; background: rgba(254, 202, 87, 0.08); border-radius: 12px; border-left: 4px solid #feca57; }}
        .share-section h3 {{ margin-top: 0; color: #feca57; }}
        .share-buttons {{ display: flex; gap: 10px; flex-wrap: wrap; margin-top: 15px; }}
        .share-btn {{ display: inline-block; padding: 10px 18px; border-radius: 8px; text-decoration: none; color: white; font-weight: 600; font-size: 14px; transition: transform 0.2s, box-shadow 0.2s; }}
        .share-btn:hover {{ transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.3); }}
        .share-btn.whatsapp {{ background: #25d366; }}
        .share-btn.telegram {{ background: #0088cc; }}
        .share-btn.twitter {{ background: #1da1f2; }}
        .share-btn.facebook {{ background: #1877f2; }}
        .social-follow {{ margin: 30px 0; padding: 20px; background: rgba(72, 219, 251, 0.08); border-radius: 12px; border-left: 4px solid #48dbfb; }}
        .social-follow h3 {{ margin-top: 0; color: #48dbfb; }}
        .follow-buttons {{ display: flex; gap: 10px; flex-wrap: wrap; margin-top: 15px; }}
        .follow-btn {{ display: inline-block; padding: 12px 20px; border-radius: 8px; text-decoration: none; color: white; font-weight: 600; font-size: 14px; transition: transform 0.2s, box-shadow 0.2s; }}
        .follow-btn:hover {{ transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.3); }}
        .follow-btn.whatsapp-follow {{ background: #25d366; }}
        .follow-btn.telegram-follow {{ background: #0088cc; }}
        .follow-btn.facebook-follow {{ background: #1877f2; }}
        .related-news {{ margin-top: 30px; padding: 20px; background: rgba(72, 219, 251, 0.08); border-radius: 12px; border-left: 4px solid #48dbfb; }}
        .related-news h3 {{ margin-top: 0; }}
        .related-news ul {{ list-style: none; padding-left: 0; }}
        .related-news li {{ margin-bottom: 12px; padding-left: 20px; position: relative; }}
        .related-news li::before {{ content: "▸"; position: absolute; left: 0; color: #48dbfb; }}
        .related-news a {{ color: #e0e0e0; text-decoration: none; transition: color 0.3s; }}
        .related-news a:hover {{ color: #feca57; }}
        @media (max-width: 600px) {{
            .share-buttons, .follow-buttons {{ flex-direction: column; }}
            .share-btn, .follow-btn {{ width: 100%; text-align: center; }}
            .copy-go-btn {{ width: 100%; padding: 15px 20px; font-size: 15px; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title_esc}</h1>
        <div class="source-box">📰 स्रोत: {source_esc} | 🕐 {date_esc}</div>

        {full_article}

        <div class="source-box"><strong>मूल स्रोत:</strong> <a href="{link_esc}" target="_blank" rel="noopener nofollow">पूरी न्यूज़ यहाँ पढ़ें →</a></div>

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
# ═══ Index Page ═══
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
    <meta name="description" content="भारतीय शेयर बाजार, बिजनेस और अर्थव्यवस्था की ताज़ा हिंदी अपडेट्स. Nifty 50, Sensex, IPO, Stock Market News.">
    <meta name="keywords" content="share market, stock market, hindi news, business, sensex, nifty, भारत न्यूज़">
    <link rel="canonical" href="{SITE_URL}/">
    <meta property="og:title" content="{SITE_NAME}">
    <meta property="og:description" content="भारतीय शेयर बाजार की ताज़ा हिंदी अपडेट्स">
    <meta property="og:url" content="{SITE_URL}/">
    <meta property="og:type" content="website">
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
        .social-links a {{ padding: 10px 18px; border-radius: 8px; text-decoration: none; color: white; font-weight: 600; font-size: 14px; transition: transform 0.2s; }}
        .social-links a:hover {{ transform: translateY(-2px); }}
        .social-links .wa {{ background: #25d366; }}
        .social-links .tg {{ background: #0088cc; }}
        .social-links .fb {{ background: #1877f2; }}
        .news-card {{ background: rgba(255,255,255,0.07); padding: 25px; border-radius: 12px; margin-bottom: 20px; transition: transform 0.2s; }}
        .news-card:hover {{ transform: translateY(-3px); }}
        .news-card h2 {{ font-size: 20px; margin-bottom: 10px; line-height: 1.4; }}
        .news-card h2 a {{ color: #feca57; text-decoration: none; }}
        .news-card h2 a:hover {{ color: #ff9f43; }}
        .news-meta {{ color: #48dbfb; font-size: 13px; margin-bottom: 12px; }}
        .news-card p {{ color: #b0b0b0; font-size: 15px; margin-bottom: 12px; }}
        .read-more {{ display: inline-block; color: #ff6b6b; text-decoration: none; font-weight: 600; font-size: 14px; }}
        .read-more:hover {{ color: #feca57; }}
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
                <a href="{WHATSAPP_CHANNEL}" target="_blank" rel="noopener" class="wa">💬 WhatsApp</a>
                <a href="{TELEGRAM_CHANNEL}" target="_blank" rel="noopener" class="tg">📢 Telegram</a>
                <a href="{FACEBOOK_PAGE}" target="_blank" rel="noopener" class="fb">📘 Facebook</a>
            </div>
        </header>

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
# ═══ Sitemap (main) ═══
# ═══════════════════════════════════════════════════════
def generate_sitemap(generated_files):
    today = datetime.now(IST).strftime('%Y-%m-%d')

    urls = [f"{SITE_URL}/"]
    for filename in generated_files:
        urls.append(f"{SITE_URL}/news/{filename}")

    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

    for url in urls:
        if url == f"{SITE_URL}/":
            priority, changefreq = '1.0', 'hourly'
        else:
            priority, changefreq = '0.8', 'daily'

        sitemap += '    <url>\n'
        sitemap += f'        <loc>{escape_xml(url)}</loc>\n'
        sitemap += f'        <lastmod>{today}</lastmod>\n'
        sitemap += f'        <changefreq>{changefreq}</changefreq>\n'
        sitemap += f'        <priority>{priority}</priority>\n'
        sitemap += '    </url>\n'

    sitemap += '</urlset>'

    with open('sitemap.xml', 'w', encoding='utf-8') as f:
        f.write(sitemap)

    print(f"📄 sitemap.xml બન્યું ({len(urls)} URLs)")


# ═══════════════════════════════════════════════════════
# ═══ Google News Sitemap ═══
# ═══════════════════════════════════════════════════════
def generate_news_sitemap(news_list, generated_files):
    cutoff = datetime.now(IST) - timedelta(days=NEWS_SITEMAP_DAYS)
    today = datetime.now(IST).strftime('%Y-%m-%d')

    news_sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n'
    news_sitemap += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
    news_sitemap += '    xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">\n'

    count = 0
    for i, news in enumerate(news_list[:MAX_NEWS_SITEMAP]):
        if i >= len(generated_files):
            continue
        filename = generated_files[i]
        if not filename:
            continue

        # ✅ 2 દિવસથી જૂનું skip
        dt = parse_date_ist(news.get('date', ''))
        if dt < cutoff:
            continue

        title = escape_xml(news.get('title', '')[:110])     # ✅ 110 char limit
        page_url = f"{SITE_URL}/news/{filename}"
        pub_date = dt.isoformat()

        news_sitemap += '  <url>\n'
        news_sitemap += f'    <loc>{escape_xml(page_url)}</loc>\n'
        news_sitemap += f'    <lastmod>{today}</lastmod>\n'
        news_sitemap += '    <news:news>\n'
        news_sitemap += '      <news:publication>\n'
        news_sitemap += f'        <news:name>{escape_xml(SITE_NAME)}</news:name>\n'
        news_sitemap += '        <news:language>hi</news:language>\n'
        news_sitemap += '      </news:publication>\n'
        news_sitemap += f'      <news:publication_date>{pub_date}</news:publication_date>\n'
        news_sitemap += f'      <news:title>{title}</news:title>\n'
        news_sitemap += '    </news:news>\n'
        news_sitemap += '  </url>\n'
        count += 1

    news_sitemap += '</urlset>'

    with open('news-sitemap.xml', 'w', encoding='utf-8') as f:
        f.write(news_sitemap)

    print(f"📰 news-sitemap.xml બન્યું ({count} URLs)")


# ═══════════════════════════════════════════════════════
# ═══ Sitemap Index ═══
# ═══════════════════════════════════════════════════════
def generate_sitemap_index():
    today = datetime.now(IST).strftime('%Y-%m-%d')

    idx = '<?xml version="1.0" encoding="UTF-8"?>\n'
    idx += '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

    for name in ['sitemap.xml', 'news-sitemap.xml']:
        idx += '  <sitemap>\n'
        idx += f'    <loc>{SITE_URL}/{name}</loc>\n'
        idx += f'    <lastmod>{today}</lastmod>\n'
        idx += '  </sitemap>\n'

    idx += '</sitemapindex>'

    with open('sitemap_index.xml', 'w', encoding='utf-8') as f:
        f.write(idx)

    print("🗂️ sitemap_index.xml બન્યું")


# ═══════════════════════════════════════════════════════
# ═══ robots.txt ═══
# ═══════════════════════════════════════════════════════
def generate_robots():
    robots = f"""User-agent: *
Allow: /
Disallow: /news_index.json
Disallow: /news_data.json

User-agent: Googlebot-News
Allow: /

Sitemap: {SITE_URL}/sitemap.xml
Sitemap: {SITE_URL}/news-sitemap.xml
"""
    with open('robots.txt', 'w', encoding='utf-8') as f:
        f.write(robots)

    print("🤖 robots.txt બન્યું")


# ═══════════════════════════════════════════════════════
# ═══ RSS Feed ═══
# ═══════════════════════════════════════════════════════
def generate_rss(news_list, generated_files):
    now = email.utils.format_datetime(datetime.now(IST))

    rss_items = ""
    for news, filename in zip(news_list, generated_files):
        title = escape_xml(news.get('title', ''))
        summary = escape_xml(news.get('summary', ''))
        source = escape_xml(news.get('source', ''))
        link_original = escape_xml(news.get('link', ''))

        # ✅ દરેક item ની પોતાની pubDate
        pub_date = email.utils.format_datetime(parse_date_ist(news.get('date', '')))

        page_url = f"{SITE_URL}/news/{filename}"

        rss_items += f"""    <item>
      <title>{title}</title>
      <link>{escape_xml(page_url)}</link>
      <description>{escape_xml(summary[:300])}</description>
      <pubDate>{pub_date}</pubDate>
      <guid isPermaLink="true">{escape_xml(page_url)}</guid>
      <source url="{link_original}">{source}</source>
    </item>
"""

    rss = '<?xml version="1.0" encoding="UTF-8"?>\n'
    rss += '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">\n'
    rss += '  <channel>\n'
    rss += f'    <title>{escape_xml(SITE_NAME)} - શેર બજારની તાજી હિન્દી અપડેટ્સ</title>\n'
    rss += f'    <link>{SITE_URL}/</link>\n'
    rss += '    <description>શેર બજાર, બિઝનેસ અને અર્થતંત્રની તાજી હિન્દી અપડેટ્સ</description>\n'
    rss += '    <language>hi-in</language>\n'
    rss += f'    <copyright>© 2026 {escape_xml(SITE_NAME)}</copyright>\n'
    rss += f'    <lastBuildDate>{now}</lastBuildDate>\n'
    rss += f'    <pubDate>{now}</pubDate>\n'
    rss += '    <ttl>60</ttl>\n'
    rss += f'    <atom:link href="{SITE_URL}/rss.xml" rel="self" type="application/rss+xml"/>\n'
    rss += rss_items
    rss += '  </channel>\n'
    rss += '</rss>'

    with open('rss.xml', 'w', encoding='utf-8') as f:
        f.write(rss)

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

    top_news = news_list[:MAX_NEWS]     # ✅ એક વાર બનાવો

    # ✅ જૂની બધી HTML files સાફ કરો
    if os.path.exists('news'):
        old_files = glob.glob('news/*.html')
        for f in old_files:
            os.remove(f)
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

    # news_index.json
    with open('news_index.json', 'w', encoding='utf-8') as f:
        json.dump(generated, f, ensure_ascii=False, indent=4)

    # ═══ બધા ફાઇલો ═══
    generate_index_page(top_news, generated)
    generate_sitemap(generated)
    generate_news_sitemap(top_news, generated)
    generate_sitemap_index()
    generate_robots()
    generate_rss(top_news, generated)

    print("\n✅ બધું તૈયાર! 🎉")


if __name__ == "__main__":
    main()
