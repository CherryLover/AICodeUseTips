"""配置文件"""
import os

# Notion API 配置（从环境变量读取）
NOTION_TOKEN = os.getenv("NOTION_TOKEN", "")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID", "")

# API 版本
NOTION_VERSION = "2022-06-28"

# 输出目录
OUTPUT_DIR = "output"
IMAGES_DIR = f"{OUTPUT_DIR}/images"

# 网站配置
SITE_TITLE = "AI 使用技巧"
SITE_DESCRIPTION = "记录日常使用 AI 的小技巧和经验"
