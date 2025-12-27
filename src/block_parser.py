"""Notion Block 解析器 - 将 Notion 块转换为 HTML"""
from typing import Optional
from .notion_client import parse_rich_text_to_html
from .image_handler import ImageHandler


class BlockParser:
    """Notion Block 解析器"""

    def __init__(self, notion_client, image_handler: ImageHandler):
        self.notion_client = notion_client
        self.image_handler = image_handler
        self.image_index = 0

    def parse_blocks(self, blocks: list, page_id: str) -> str:
        """解析块列表为 HTML"""
        self.image_index = 0
        html_parts = []

        for block in blocks:
            html = self.parse_block(block, page_id)
            if html:
                html_parts.append(html)

        return "\n".join(html_parts)

    def parse_block(self, block: dict, page_id: str) -> Optional[str]:
        """解析单个块为 HTML"""
        block_type = block.get("type")
        block_id = block.get("id")

        parser_map = {
            "paragraph": self._parse_paragraph,
            "heading_1": self._parse_heading_1,
            "heading_2": self._parse_heading_2,
            "heading_3": self._parse_heading_3,
            "bulleted_list_item": self._parse_bulleted_list_item,
            "numbered_list_item": self._parse_numbered_list_item,
            "code": self._parse_code,
            "image": self._parse_image,
            "quote": self._parse_quote,
            "callout": self._parse_callout,
            "divider": self._parse_divider,
            "toggle": self._parse_toggle,
            "to_do": self._parse_todo,
            "bookmark": self._parse_bookmark,
            "embed": self._parse_embed,
            "video": self._parse_video,
        }

        parser = parser_map.get(block_type)
        if parser:
            return parser(block, page_id)

        # 未知类型，返回空
        return None

    def _get_rich_text_html(self, block: dict, block_type: str) -> str:
        """获取块的富文本 HTML"""
        block_data = block.get(block_type, {})
        rich_text = block_data.get("rich_text", [])
        return parse_rich_text_to_html(rich_text)

    def _parse_paragraph(self, block: dict, page_id: str) -> str:
        content = self._get_rich_text_html(block, "paragraph")
        if not content:
            return "<p>&nbsp;</p>"
        return f"<p>{content}</p>"

    def _parse_heading_1(self, block: dict, page_id: str) -> str:
        content = self._get_rich_text_html(block, "heading_1")
        return f"<h1>{content}</h1>"

    def _parse_heading_2(self, block: dict, page_id: str) -> str:
        content = self._get_rich_text_html(block, "heading_2")
        return f"<h2>{content}</h2>"

    def _parse_heading_3(self, block: dict, page_id: str) -> str:
        content = self._get_rich_text_html(block, "heading_3")
        return f"<h3>{content}</h3>"

    def _parse_bulleted_list_item(self, block: dict, page_id: str) -> str:
        content = self._get_rich_text_html(block, "bulleted_list_item")
        # 处理子块
        children_html = self._parse_children(block, page_id)
        if children_html:
            return f"<li>{content}<ul>{children_html}</ul></li>"
        return f"<li>{content}</li>"

    def _parse_numbered_list_item(self, block: dict, page_id: str) -> str:
        content = self._get_rich_text_html(block, "numbered_list_item")
        children_html = self._parse_children(block, page_id)
        if children_html:
            return f"<li>{content}<ol>{children_html}</ol></li>"
        return f"<li>{content}</li>"

    def _parse_code(self, block: dict, page_id: str) -> str:
        code_data = block.get("code", {})
        rich_text = code_data.get("rich_text", [])
        language = code_data.get("language", "")

        # 获取代码内容
        code_content = ""
        for item in rich_text:
            code_content += item.get("plain_text", "")

        # 转义 HTML
        code_content = code_content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        return f'<pre><code class="language-{language}">{code_content}</code></pre>'

    def _parse_image(self, block: dict, page_id: str) -> str:
        image_data = block.get("image", {})
        image_type = image_data.get("type")

        # 获取图片 URL
        if image_type == "file":
            url = image_data.get("file", {}).get("url")
        elif image_type == "external":
            url = image_data.get("external", {}).get("url")
        else:
            return ""

        if not url:
            return ""

        # 下载图片并获取本地路径
        self.image_index += 1
        local_path = self.image_handler.process_image(url, page_id, self.image_index)

        if local_path:
            # 获取图片说明
            caption = parse_rich_text_to_html(image_data.get("caption", []))
            caption_html = f"<figcaption>{caption}</figcaption>" if caption else ""
            return f'<figure><img src="{local_path}" alt="{caption or "图片"}" loading="lazy">{caption_html}</figure>'
        else:
            return f'<p>[图片加载失败]</p>'

    def _parse_quote(self, block: dict, page_id: str) -> str:
        content = self._get_rich_text_html(block, "quote")
        return f"<blockquote>{content}</blockquote>"

    def _parse_callout(self, block: dict, page_id: str) -> str:
        callout_data = block.get("callout", {})
        content = parse_rich_text_to_html(callout_data.get("rich_text", []))

        # 获取图标
        icon_data = callout_data.get("icon", {})
        icon = ""
        if icon_data.get("type") == "emoji":
            icon = icon_data.get("emoji", "")

        return f'<div class="callout"><span class="callout-icon">{icon}</span><div class="callout-content">{content}</div></div>'

    def _parse_divider(self, block: dict, page_id: str) -> str:
        return "<hr>"

    def _parse_toggle(self, block: dict, page_id: str) -> str:
        content = self._get_rich_text_html(block, "toggle")
        children_html = self._parse_children(block, page_id)
        return f'<details><summary>{content}</summary><div class="toggle-content">{children_html}</div></details>'

    def _parse_todo(self, block: dict, page_id: str) -> str:
        todo_data = block.get("to_do", {})
        content = parse_rich_text_to_html(todo_data.get("rich_text", []))
        checked = todo_data.get("checked", False)
        checked_attr = "checked" if checked else ""
        checked_class = "todo-checked" if checked else ""
        return f'<div class="todo-item {checked_class}"><input type="checkbox" {checked_attr} disabled><span>{content}</span></div>'

    def _parse_bookmark(self, block: dict, page_id: str) -> str:
        bookmark_data = block.get("bookmark", {})
        url = bookmark_data.get("url", "")
        caption = parse_rich_text_to_html(bookmark_data.get("caption", []))
        display = caption if caption else url
        return f'<div class="bookmark"><a href="{url}" target="_blank">{display}</a></div>'

    def _parse_embed(self, block: dict, page_id: str) -> str:
        embed_data = block.get("embed", {})
        url = embed_data.get("url", "")
        return f'<div class="embed"><a href="{url}" target="_blank">{url}</a></div>'

    def _parse_video(self, block: dict, page_id: str) -> str:
        video_data = block.get("video", {})
        video_type = video_data.get("type")

        if video_type == "external":
            url = video_data.get("external", {}).get("url", "")
            # YouTube 等外部视频
            return f'<div class="video"><a href="{url}" target="_blank">视频链接: {url}</a></div>'
        elif video_type == "file":
            url = video_data.get("file", {}).get("url", "")
            return f'<video controls><source src="{url}"></video>'

        return ""

    def _parse_children(self, block: dict, page_id: str) -> str:
        """解析块的子块"""
        if not block.get("has_children"):
            return ""

        block_id = block.get("id")
        children = self.notion_client.get_block_children(block_id)

        if not children:
            return ""

        html_parts = []
        for child in children:
            html = self.parse_block(child, page_id)
            if html:
                html_parts.append(html)

        return "\n".join(html_parts)
