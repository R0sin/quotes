import json
import random
from datetime import datetime, timezone, timedelta
from xml.etree import ElementTree as ET
from xml.dom import minidom

# --- 配置区 ---
QUOTES_FILE = 'quotes.json'
RSS_FILE = 'rss.xml'
FEED_LINK = 'https://r0sin.github.io/quotes/'
# 【重要】Channel 标题必须是静态的、不变的
FEED_TITLE = '盗賊の極意'
FEED_DESCRIPTION = '每日一条精选书摘或语录'
GENERATOR = 'R0sin/Quotes-RSS-Generator' # 生成器名称
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
    # 【修复】添加了 dc 命名空间，提高兼容性
    rss = ET.Element('rss', version='2.0', attrib={
        'xmlns:atom': 'http://www.w3.org/2005/Atom',
        'xmlns:dc': 'http://purl.org/dc/elements/1.1/'
    })
    channel = ET.SubElement(rss, 'channel')

    # Channel 元数据（全部使用静态信息）
    ET.SubElement(channel, 'title').text = FEED_TITLE
    ET.SubElement(channel, 'link').text = FEED_LINK
    ET.SubElement(channel, 'description').text = FEED_DESCRIPTION
    ET.SubElement(channel, 'generator').text = GENERATOR # 【修复】添加 generator
    
    tz_utc_8 = timezone(timedelta(hours=8))
    now = datetime.now(tz_utc_8)
    ET.SubElement(channel, 'lastBuildDate').text = now.strftime('%a, %d %b %Y %H:%M:%S %z')
    
    atom_link = ET.SubElement(channel, 'atom:link', href=f"{FEED_LINK}{RSS_FILE}", rel="self", type="application/rss+xml")

    # 创建 Item
    item = ET.SubElement(channel, 'item')
    
    # 【布局最终方案】Item 的标题是“作者”
    item_title_text = quote_author if quote_author else "无名氏"
    item_title_node = ET.SubElement(item, 'title')
    item_title_node.text = f"<![CDATA[{item_title_text}]]>"
    
    # 【可选但推荐】使用 dc:creator 标签明确指定作者
    ET.SubElement(item, 'dc:creator').text = item_title_text
    
    item_link = quote_source if quote_source else FEED_LINK
    ET.SubElement(item, 'link').text = item_link
    
    # 【布局最终方案】Item 的描述是“书摘句子”
    description_html = f"<blockquote>{quote_text}</blockquote>"
    if quote_source:
        description_html += f'<p><a href="{quote_source}">来源</a></p>'
        
    description_node = ET.SubElement(item, 'description')
    description_node.text = f"<![CDATA[{description_html}]]>"

    ET.SubElement(item, 'pubDate').text = now.strftime('%a, %d %b %Y %H:%M:%S %z')
    
    guid_text = f"{now.isoformat()}-{hash(quote_text)}"
    ET.SubElement(item, 'guid', isPermaLink='false').text = guid_text

    # 3. 写入文件
    xml_string = ET.tostring(rss, 'unicode')
    xml_string = xml_string.replace('<![CDATA[', '<![CDATA[').replace(']]>', ']]>')
    md_parsed = minidom.parseString(xml_string.encode('utf-8'))
    pretty_xml_string = md_parsed.toprettyxml(indent="    ", encoding='utf-8').decode()

    with open(RSS_FILE, 'w', encoding='utf-8') as f:
        f.write(pretty_xml_string)

    print(f"RSS file '{RSS_FILE}' generated successfully with classic layout.")

if __name__ == '__main__':
    generate_rss()