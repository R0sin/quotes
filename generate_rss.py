import json
import random
from datetime import datetime, timezone, timedelta
from xml.etree import ElementTree as ET
from xml.dom import minidom

# --- 配置区 ---
QUOTES_FILE = 'quotes.json'
RSS_FILE = 'rss.xml'
FEED_LINK = 'https://r0sin.github.io/quotes/' 
FEED_TITLE = '盗賊の極意'
FEED_DESCRIPTION = '每日一条精选书摘或语录'
# ---------------

def pretty_print_xml(elem):
    """返回一个美化格式的 XML 字符串。"""
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

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

    # Channel 元数据
    ET.SubElement(channel, 'title').text = FEED_TITLE
    ET.SubElement(channel, 'link').text = FEED_LINK
    ET.SubElement(channel, 'description').text = FEED_DESCRIPTION
    
    # 【修复】添加 lastBuildDate
    tz_utc_8 = timezone(timedelta(hours=8))
    now = datetime.now(tz_utc_8)
    ET.SubElement(channel, 'lastBuildDate').text = now.strftime('%a, %d %b %Y %H:%M:%S %z')
    
    atom_link = ET.SubElement(channel, 'atom:link', href=f"{FEED_LINK}{RSS_FILE}", rel="self", type="application/rss+xml")

    # 创建 Item
    item = ET.SubElement(channel, 'item')
    
    item_title = quote_author if quote_author else "一条新书摘"
    ET.SubElement(item, 'title').text = item_title

    # 【修复】为 item 添加 link 标签
    # 让它指向你的 RSS 源，或者如果有来源链接就指向来源
    item_link = quote_source if quote_source else FEED_LINK
    ET.SubElement(item, 'link').text = item_link
    
    # 创建美观的 HTML 描述
    description_html = f"<blockquote>{quote_text}</blockquote>"
    if quote_author:
        description_html += f"<p><em>— {quote_author}</em></p>"
    if quote_source:
        description_html += f'<p><a href="{quote_source}">来源</a></p>'
        
    # 【重大修复】使用 CDATA 包裹 HTML 内容
    # ElementTree 没有直接创建 CDATA 的好方法，我们通过一个技巧来实现
    description_node = ET.SubElement(item, 'description')
    description_node.text = f"<![CDATA[{description_html}]]>"

    ET.SubElement(item, 'pubDate').text = now.strftime('%a, %d %b %Y %H:%M:%S %z')
    
    # Guid 可以用发布时间+内容哈希来确保唯一性
    guid_text = f"{now.isoformat()}-{hash(quote_text)}"
    ET.SubElement(item, 'guid', isPermaLink='false').text = guid_text

    # 3. 写入文件
    # 使用一种能正确处理 CDATA 的方式写入文件
    xml_string = ET.tostring(rss, 'unicode')
    
    # ElementTree 会把 <![CDATA[...]]> 编码成 <![CDATA[...]]>
    # 我们需要把它替换回来，这是一个标准的处理技巧
    xml_string = xml_string.replace('<![CDATA[', '<![CDATA[').replace(']]>', ']]>')
    
    # 使用 minidom 美化格式 (可选，但推荐)
    md_parsed = minidom.parseString(xml_string.encode('utf-8'))
    pretty_xml_string = md_parsed.toprettyxml(indent="    ", encoding='utf-8').decode()

    # 写入最终文件，并包含 xml 声明
    with open(RSS_FILE, 'w', encoding='utf-8') as f:
        # minidom 会添加一个 xml 声明，但我们最好自己控制
        # f.write('<?xml version="1.0" encoding="UTF-8"?>\n') 
        # minidom 的 toprettyxml 已经包含了
        f.write(pretty_xml_string)

    print(f"RSS file '{RSS_FILE}' generated successfully with a quote from {quote_author or 'Unknown'}.")

if __name__ == '__main__':
    generate_rss()