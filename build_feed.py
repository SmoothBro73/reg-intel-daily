"""Rebuild feed.xml from episodes.json. Run after adding episodes/<date>.mp3 and its entry."""
import json, os, email.utils, datetime
from xml.sax.saxutils import escape
BASE = "https://smoothbro73.github.io/reg-intel-daily"
eps = sorted(json.load(open("episodes.json")), key=lambda e: e["date"], reverse=True)
items = []
for e in eps:
    path = f"episodes/{e['date']}.mp3"
    size = os.path.getsize(path)
    dt = datetime.datetime.fromisoformat(e["pubdate"])
    d = int(e.get("duration_seconds", 0))
    items.append(f"""    <item>
      <title>{escape(e['title'])}</title>
      <description>{escape(e['description'])}</description>
      <pubDate>{email.utils.format_datetime(dt)}</pubDate>
      <guid isPermaLink="false">reg-intel-daily-{e['date']}</guid>
      <enclosure url="{BASE}/{path}" length="{size}" type="audio/mpeg"/>
      <itunes:duration>{d//60}:{d%60:02d}</itunes:duration>
      <itunes:explicit>false</itunes:explicit>
    </item>""")
feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd">
  <channel>
    <title>Reg Intel Daily</title>
    <link>{BASE}/</link>
    <language>en-us</language>
    <description>A weekday briefing on financial regulatory developments that matter to RBC.</description>
    <itunes:author>Reg Intel Daily</itunes:author>
    <itunes:image href="{BASE}/cover.jpg"/>
    <itunes:category text="Business"/>
    <itunes:explicit>false</itunes:explicit>
    <itunes:block>Yes</itunes:block>
{chr(10).join(items)}
  </channel>
</rss>
"""
open("feed.xml", "w").write(feed)
print("feed.xml rebuilt with", len(items), "episode(s)")
