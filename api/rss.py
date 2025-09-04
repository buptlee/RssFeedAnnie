from http.server import BaseHTTPRequestHandler
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, tostring

def fetch_latest(username, nitter_url="https://nitter.net"):
    url = f"{nitter_url}/{username}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    items = []
    for tweet in soup.select(".timeline-item"):
        content = tweet.select_one(".tweet-content")
        if not content:
            continue
        text = content.get_text(" ", strip=True)
        link_tag = tweet.select_one("a.tweet-link")
        link = f"https://x.com{link_tag['href']}" if link_tag else ""
        time_tag = tweet.select_one("span.tweet-date > a")
        pub_date = time_tag["title"] if time_tag else datetime.utcnow().isoformat()
        items.append((text, link, pub_date))
    return items

def build_rss(username, items):
    rss = Element("rss", version="2.0")
    channel = SubElement(rss, "channel")
    SubElement(channel, "title").text = f"{username} latest posts"
    SubElement(channel, "link").text = f"https://x.com/{username}"
    SubElement(channel, "description").text = f"RSS feed for {username}'s X posts"
    
    for text, link, pub_date in items:
        item = SubElement(channel, "item")
        SubElement(item, "title").text = text[:50] + "..."
        SubElement(item, "link").text = link
        SubElement(item, "description").text = text
        SubElement(item, "pubDate").text = pub_date
    
    return tostring(rss, encoding="utf-8")

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        from urllib.parse import parse_qs, urlparse
        query = parse_qs(urlparse(self.path).query)
        username = query.get("username", ["elonmusk"])[0]
        posts = fetch_latest(username)
        rss_feed = build_rss(username, posts)
        self.send_response(200)
        self.send_header("Content-type", "application/rss+xml")
        self.end_headers()
        self.wfile.write(rss_feed)
