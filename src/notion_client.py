"""Notion API 客户端"""
import requests
from typing import Optional
import sys
sys.path.insert(0, '..')
from config import NOTION_TOKEN, NOTION_DATABASE_ID, NOTION_VERSION


class NotionClient:
    """Notion API 客户端"""

    BASE_URL = "https://api.notion.com/v1"

    def __init__(self, token: str = NOTION_TOKEN):
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Notion-Version": NOTION_VERSION,
            "Content-Type": "application/json"
        }

    def query_database(self, database_id: str = NOTION_DATABASE_ID,
                       start_cursor: Optional[str] = None) -> dict:
        """查询数据库，获取所有页面"""
        url = f"{self.BASE_URL}/databases/{database_id}/query"
        payload = {}
        if start_cursor:
            payload["start_cursor"] = start_cursor

        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()

    def get_all_pages(self, database_id: str = NOTION_DATABASE_ID) -> list:
        """获取数据库中的所有页面（处理分页）"""
        all_pages = []
        start_cursor = None

        while True:
            result = self.query_database(database_id, start_cursor)
            all_pages.extend(result.get("results", []))

            if not result.get("has_more"):
                break
            start_cursor = result.get("next_cursor")

        return all_pages

    def get_page_blocks(self, page_id: str) -> list:
        """获取页面的所有块内容"""
        all_blocks = []
        start_cursor = None

        while True:
            url = f"{self.BASE_URL}/blocks/{page_id}/children"
            params = {}
            if start_cursor:
                params["start_cursor"] = start_cursor

            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            result = response.json()

            all_blocks.extend(result.get("results", []))

            if not result.get("has_more"):
                break
            start_cursor = result.get("next_cursor")

        return all_blocks

    def get_block_children(self, block_id: str) -> list:
        """获取块的子块（用于嵌套内容如 toggle、callout 等）"""
        return self.get_page_blocks(block_id)


def parse_rich_text(rich_text_list: list) -> str:
    """解析 Notion rich_text 为纯文本"""
    text = ""
    for item in rich_text_list:
        text += item.get("plain_text", "")
    return text


def parse_rich_text_to_html(rich_text_list: list) -> str:
    """解析 Notion rich_text 为 HTML（保留格式）"""
    html = ""
    for item in rich_text_list:
        content = item.get("plain_text", "")
        annotations = item.get("annotations", {})
        href = item.get("href")

        # 转义 HTML 特殊字符
        content = content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        # 应用格式
        if annotations.get("code"):
            content = f"<code>{content}</code>"
        if annotations.get("bold"):
            content = f"<strong>{content}</strong>"
        if annotations.get("italic"):
            content = f"<em>{content}</em>"
        if annotations.get("strikethrough"):
            content = f"<del>{content}</del>"
        if annotations.get("underline"):
            content = f"<u>{content}</u>"
        if href:
            content = f'<a href="{href}" target="_blank">{content}</a>'

        html += content
    return html


def extract_page_info(page: dict) -> dict:
    """从页面对象中提取关键信息"""
    properties = page.get("properties", {})

    # 获取标题
    title_prop = properties.get("分享标题", {})
    title_list = title_prop.get("title", [])
    title = parse_rich_text(title_list) if title_list else "无标题"

    # 获取日期
    date_prop = properties.get("分享时间", {})
    date_obj = date_prop.get("date")
    date = date_obj.get("start") if date_obj else None

    # 获取是否有图片
    has_image = properties.get("是否有图片", {}).get("checkbox", False)

    return {
        "id": page.get("id"),
        "title": title,
        "date": date,
        "has_image": has_image,
        "created_time": page.get("created_time"),
        "last_edited_time": page.get("last_edited_time"),
        "url": page.get("url")
    }
