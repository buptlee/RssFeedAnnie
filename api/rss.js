import fetch from "node-fetch";
import * as cheerio from "cheerio";

export default async function handler(req, res) {
  const { username = "elonmusk" } = req.query;
  const url = `https://nitter.net/${username}`;
  
  const response = await fetch(url);
  const html = await response.text();
  const $ = cheerio.load(html);

  const items = [];
  $(".timeline-item").each((_, el) => {
    const content = $(el).find(".tweet-content").text().trim();
    const link = "https://x.com" + $(el).find("a.tweet-link").attr("href");
    const date = $(el).find("span.tweet-date > a").attr("title") || new Date().toISOString();

    if (content) {
      items.push({ content, link, date });
    }
  });

  // Build RSS XML
  let rss = `<?xml version="1.0" encoding="UTF-8" ?>\n<rss version="2.0">\n<channel>\n`;
  rss += `<title>${username} latest posts</title>\n`;
  rss += `<link>https://x.com/${username}</link>\n`;
  rss += `<description>RSS feed for ${username}'s X posts</description>\n`;

  items.forEach(item => {
    rss += `<item>\n`;
    rss += `<title>${item.content.substring(0, 50)}...</title>\n`;
    rss += `<link>${item.link}</link>\n`;
    rss += `<description>${item.content}</description>\n`;
    rss += `<pubDate>${item.date}</pubDate>\n`;
    rss += `</item>\n`;
  });

  rss += `</channel>\n</rss>`;

  res.setHeader("Content-Type", "application/rss+xml");
  res.status(200).send(rss);
}
