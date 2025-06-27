import json
import random
from datetime import datetime, timezone, timedelta
from xml.etree import ElementTree as ET
from xml.dom import minidom

# --- 配置区 ---
QUOTES_FILE = 'quotes.json'
RSS_FILE = 'rss.xml'
FEED_LINK = 'https://r0sin.github.io/quotes/'
# 这个 FEED_TITLE 将作为作者为空时的备用标题
FALLBACK_FEED_TITLE = '盗賊の極意'
FEED_DESCRIPTION = '每日一条精选书摘或语录'
# ---------------

def generate_rss():
    # 1. 读取并随机选择一条书摘
    with open(QUOTES_FILE, 'r', encoding='utf-8') as f:
        quotes = json.load(f)
    
    quote = random.choice(quotes)
    quote_text = quote.get('text', '')
    quote_author = quote.get('author', '')
    quote_source = quote.get('source', '')

    # 2. 构建 RSS XML 结构
    rss = ET.Element('rss', version='2.0', attrib={'xmlns:atom': 'http://www.w3.org/2005/Atom'})
    channel = ET.SubElement(rss, 'channel')

    # --- 以下是实现您新想法的核心修改区域 ---

    # 【重大修改】将 Channel 的标题设置为“作者”
    # 如果作者名存在，就用作者名；否则，使用备用标题。
    channel_title = quote_author if quote_author else FALLBACK_FEED_TITLE
    ET.SubElement(channel, 'title').text = channel_title
    
    ET.SubElement(channel, 'link').text = FEED_LINK
    ET.SubElement(channel, 'description').text = FEED_DESCRIPTION
    
    tz_utc_8 = timezone(timedelta(hours=8))
    now = datetime.now(tz_utc_8)
    ET.SubElement(channel, 'lastBuildDate').text = now.strftime('%a, %d %b %Y %H:%M:%S %z')
    
    atom_link = ET.SubElement(channel, 'atom:link', href=f"{FEED_LINK}{RSS_FILE}", rel="self", type="application/rss+xml")

    # 创建 Item
    item = ET.SubElement(item, 'item')
    
    # 【修改2】将 Item 的标题设置为“书摘内容”
    ET.SubElement(item, 'title').text = quote_text
    
    item_link = quote_source if quote_source else FEED_LINK
    ET.SubElement(item, 'link').text = item_link
    
    # 【修改3】Item 的描述可以设为来源，或留空
    description_html = ""
    if quote_source:
        description_html = f'<p>来源: <a href="{quote_source}">{quote_source}</a></p>'
    else:
        # 如果没有来源，可以不显示任何内容，或者给一个占位符
        description_html = "<p><em>——每日箴言</em></p>"
        
    description_node = ET.SubElement(item, 'description')
    description_node.text = f"<![CDATA[{description_html}]]>"

    ET.SubElement(item, 'pubDate').text = now.strftime('%a, %d %b %Y %H:%M:%S %z')
    
    guid_text = f"{now.isoformat()}-{hash(quote_text)}"
    ET.SubElement(item, 'guid', isPermaLink='false').text = guid_text

    # --- 核心修改区域结束 ---
    
    # 3. 写入文件
    xml_string = ET.tostring(rss, 'unicode')
    xml_string = xml_string.replace('<![CDATA[', '<![CDATA[').replace(']]>', ']]>')
    md_parsed = minidom.parseString(xml_string.encode('utf-8'))
    pretty_xml_string = md_parsed.toprettyxml(indent="    ", encoding='utf-8').decode()

    with open(RSS_FILE, 'w', encoding='utf-8') as f:
        f.write(pretty_xml_string)

    print(f"RSS file '{RSS_FILE}' generated successfully. Channel title is now '{channel_title}'.")

if __name__ == '__main__':
    generate_rss()