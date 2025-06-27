import json
import random
from datetime import datetime, timezone, timedelta
import xml.etree.ElementTree as ET

# --- 配置区 ---
QUOTES_FILE = 'quotes.json'
RSS_FILE = 'rss.xml'
FEED_LINK = 'https://r0sin.github.io/quotes/'
# 静态、不变的 Channel 标题
FEED_TITLE = '盗賊の極意'
FEED_DESCRIPTION = '每日一条精选书摘或语录'
GENERATOR = 'R0sin/Quotes-RSS-Generator' # 保持这个，是好习惯
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
    # 【修复】移除所有不必要的命名空间，只保留最基本的
    rss = ET.Element('rss', version='2.0', attrib={
        'xmlns:atom': 'http://www.w3.org/2005/Atom'
    })
    channel = ET.SubElement(rss, 'channel')

    # Channel 元数据 - 保持极简和静态
    ET.SubElement(channel, 'title').text = FEED_TITLE
    ET.SubElement(channel, 'link').text = FEED_LINK
    ET.SubElement(channel, 'description').text = FEED_DESCRIPTION
    ET.SubElement(channel, 'generator').text = GENERATOR
    
    tz_utc_8 = timezone(timedelta(hours=8))
    now = datetime.now(tz_utc_8)
    ET.SubElement(channel, 'lastBuildDate').text = now.strftime('%a, %d %b %Y %H:%M:%S %z')
    
    atom_link = ET.SubElement(channel, 'atom:link', href=f"{FEED_LINK}{RSS_FILE}", rel="self", type="application/rss+xml")

    # 创建 Item
    item = ET.SubElement(channel, 'item')
    
    # 【重大修复】Item Title: 直接使用文本，不加 CDATA
    item_title_text = quote_author if quote_author else "无名氏"
    ET.SubElement(item, 'title').text = item_title_text
    
    # 【重大修复】创建唯一的、永久的链接和GUID
    # 使用内容的哈希值作为唯一标识符，确保每个 item 的链接都不同
    item_id = str(abs(hash(quote_text)))
    item_permalink = f"{FEED_LINK}#{item_id}" # 使用 #hash 的形式创建页面内锚点链接

    ET.SubElement(item, 'link').text = item_permalink
    ET.SubElement(item, 'pubDate').text = now.strftime('%a, %d %b %Y %H:%M:%S %z')
    
    # 【重大修复】GUID 与 Link 保持一致，这是最稳妥的做法
    ET.SubElement(item, 'guid').text = item_permalink
    
    # 【重大修复】Item Description: 直接使用HTML字符串，不加 CDATA
    # ElementTree 会自动处理特殊字符的转义 (e.g., < to <)
    description_html = f"<blockquote>{quote_text}</blockquote>"
    if quote_source:
        description_html += f'<p><a href="{quote_source}">来源</a></p>'
    ET.SubElement(item, 'description').text = description_html

    # 3. 写入文件
    # 使用 ElementTree 自带的 indent 功能美化输出，更简单可靠
    tree = ET.ElementTree(rss)
    ET.indent(tree, space="  ", level=0)
    tree.write(RSS_FILE, encoding='utf-8', xml_declaration=True)

    print(f"RSS file '{RSS_FILE}' generated successfully with barebones compatible format.")

if __name__ == '__main__':
    generate_rss()