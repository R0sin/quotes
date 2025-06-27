import json
import random
from datetime import datetime, timezone, timedelta
import xml.etree.ElementTree as ET

# --- 配置区 ---
QUOTES_FILE = 'quotes.json'
RSS_FILE = 'rss.xml'
FEED_TITLE = '盗賊の極意'
FEED_LINK = 'https://R0sin.github.io/quotes/' # 替换成你的 GitHub Pages 地址
FEED_DESCRIPTION = '盗賊の極意'
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
    # 使用 ElementTree 构建 XML
    rss = ET.Element('rss', version='2.0', attrib={'xmlns:atom': 'http://www.w3.org/2005/Atom'})
    channel = ET.SubElement(rss, 'channel')

    # Channel 元数据
    ET.SubElement(channel, 'title').text = FEED_TITLE
    ET.SubElement(channel, 'link').text = FEED_LINK
    ET.SubElement(channel, 'description').text = FEED_DESCRIPTION
    
    # Atom link for self-reference
    atom_link = ET.SubElement(channel, 'atom:link', href=f"{FEED_LINK}{RSS_FILE}", rel="self", type="application/rss+xml")

    # 创建 Item (即那条书摘)
    item = ET.SubElement(channel, 'item')
    
    # 使用作者作为标题，如果作者为空则使用通用标题
    item_title = quote_author if quote_author else "Unknown"
    ET.SubElement(item, 'title').text = item_title
    
    # 创建美观的 HTML 描述
    description_html = f"<blockquote>{quote_text}</blockquote>"
    if quote_author:
        description_html += f"<p><em>— {quote_author}</em></p>"
    if quote_source:
        description_html += f'<p><a href="{quote_source}">来源</a></p>'
        
    ET.SubElement(item, 'description').text = description_html

    # pubDate 使用当前时间 (UTC+8)
    tz_utc_8 = timezone(timedelta(hours=8))
    pub_date = datetime.now(tz_utc_8).strftime('%a, %d %b %Y %H:%M:%S %z')
    ET.SubElement(item, 'pubDate').text = pub_date

    # Guid 是每条 item 的唯一标识符，可以用书摘内容做哈希或者直接用发布时间
    ET.SubElement(item, 'guid', isPermaLink='false').text = str(hash(quote_text))

    # 3. 写入文件
    tree = ET.ElementTree(rss)
    ET.indent(tree, space="\t", level=0) # 美化输出的 XML
    tree.write(RSS_FILE, encoding='utf-8', xml_declaration=True)

    print(f"RSS file '{RSS_FILE}' generated successfully with a quote from {quote_author or 'Unknown'}.")

if __name__ == '__main__':
    generate_rss()