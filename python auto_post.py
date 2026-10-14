# auto_post.py
import pyperclip
import webbrowser
import time

def create_post_caption(title, url):
    caption = f"""📰 {title}

🔗 पूरी खबर: {url}

📊 Bharat News Hindi
🌐 https://mybharatnews.github.io/bharatnews/
💬 WhatsApp: https://whatsapp.com/channel/0029VbD6VLP6buMSzAGWNE3V
📢 Telegram: https://t.me/indianews_official

#ShareMarket #Nifty #Sensex"""
    
    pyperclip.copy(caption)
    print("✅ Caption copied to clipboard!")
    print("📋 Paste in Facebook (Ctrl+V)")
    
    # Open Facebook
    webbrowser.open("https://www.facebook.com/profile.php?id=61595205934642")
    time.sleep(2)
    print("📘 Facebook opened — paste caption!")

# Use
title = "India tightens Mauritius tax treaty rules"
url = "https://mybharatnews.github.io/bharatnews/"
create_post_caption(title, url)
