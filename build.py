#!/usr/bin/env python3
"""
主构建脚本 - 从 Notion 拉取数据并生成静态网站
"""
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import OUTPUT_DIR, IMAGES_DIR
from src.notion_client import NotionClient, extract_page_info
from src.image_handler import ImageHandler
from src.block_parser import BlockParser
from src.html_generator import HTMLGenerator


def clean_output():
    """清理输出目录"""
    import shutil
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(IMAGES_DIR, exist_ok=True)
    print(f"清理输出目录: {OUTPUT_DIR}")


def build():
    """执行构建"""
    print("=" * 50)
    print("开始构建 AI 使用技巧网站")
    print("=" * 50)

    # 1. 清理输出目录
    clean_output()

    # 2. 初始化组件
    notion = NotionClient()
    image_handler = ImageHandler()
    block_parser = BlockParser(notion, image_handler)
    html_generator = HTMLGenerator()

    # 3. 获取所有页面
    print("\n获取 Notion 数据库中的页面...")
    pages = notion.get_all_pages()
    print(f"找到 {len(pages)} 个页面")

    # 4. 处理每个页面
    articles = []
    for page in pages:
        page_info = extract_page_info(page)

        # 跳过无标题的页面
        if page_info["title"] == "无标题" or not page_info["title"].strip():
            print(f"跳过无标题页面: {page_info['id']}")
            continue

        print(f"\n处理页面: {page_info['title']}")

        # 获取页面内容
        blocks = notion.get_page_blocks(page_info["id"])
        print(f"  - 找到 {len(blocks)} 个内容块")

        # 解析块为 HTML
        content_html = block_parser.parse_blocks(blocks, page_info["id"])
        page_info["content"] = content_html

        articles.append(page_info)

        # 生成文章详情页
        html_generator.generate_article(page_info)

    # 5. 生成首页
    print(f"\n生成首页，共 {len(articles)} 篇文章")
    html_generator.generate_index(articles)

    print("\n" + "=" * 50)
    print("构建完成！")
    print(f"输出目录: {OUTPUT_DIR}")
    print("=" * 50)


if __name__ == "__main__":
    build()
