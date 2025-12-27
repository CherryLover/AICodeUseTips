"""图片下载处理模块"""
import os
import hashlib
import requests
from urllib.parse import urlparse
from typing import Optional
import sys
sys.path.insert(0, '..')
from config import IMAGES_DIR


def get_image_extension(url: str, content_type: Optional[str] = None) -> str:
    """从 URL 或 Content-Type 获取图片扩展名"""
    # 优先从 Content-Type 获取
    if content_type:
        type_map = {
            "image/jpeg": ".jpg",
            "image/png": ".png",
            "image/gif": ".gif",
            "image/webp": ".webp",
            "image/svg+xml": ".svg"
        }
        for mime, ext in type_map.items():
            if mime in content_type:
                return ext

    # 从 URL 路径获取
    parsed = urlparse(url)
    path = parsed.path.lower()
    for ext in [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"]:
        if path.endswith(ext):
            return ext if ext != ".jpeg" else ".jpg"

    return ".png"  # 默认


def generate_image_filename(url: str, page_id: str, index: int) -> str:
    """生成图片文件名"""
    # 使用 URL 的 hash 确保唯一性
    url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
    return f"{page_id[:8]}_{index}_{url_hash}"


def download_image(url: str, save_path: str) -> bool:
    """下载图片到本地"""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        # 获取扩展名
        content_type = response.headers.get("Content-Type", "")
        ext = get_image_extension(url, content_type)

        # 确保路径包含扩展名
        if not save_path.endswith(ext):
            save_path = save_path + ext

        # 确保目录存在
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        with open(save_path, "wb") as f:
            f.write(response.content)

        return True
    except Exception as e:
        print(f"下载图片失败: {url}, 错误: {e}")
        return False


class ImageHandler:
    """图片处理器"""

    def __init__(self, images_dir: str = IMAGES_DIR):
        self.images_dir = images_dir
        self.downloaded_images = {}  # url -> local_path

    def process_image(self, url: str, page_id: str, index: int) -> Optional[str]:
        """处理图片：下载并返回本地路径"""
        if not url:
            return None

        # 检查是否已下载
        if url in self.downloaded_images:
            return self.downloaded_images[url]

        # 生成文件名
        filename = generate_image_filename(url, page_id, index)

        # 先下载获取真实扩展名
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            content_type = response.headers.get("Content-Type", "")
            ext = get_image_extension(url, content_type)

            save_path = os.path.join(self.images_dir, filename + ext)
            os.makedirs(self.images_dir, exist_ok=True)

            with open(save_path, "wb") as f:
                f.write(response.content)

            # 返回相对路径（用于 HTML）
            relative_path = f"images/{filename}{ext}"
            self.downloaded_images[url] = relative_path
            return relative_path

        except Exception as e:
            print(f"处理图片失败: {url}, 错误: {e}")
            return None

    def get_local_path(self, url: str) -> Optional[str]:
        """获取已下载图片的本地路径"""
        return self.downloaded_images.get(url)
