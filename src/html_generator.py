"""HTML 生成器"""
import os
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
import sys
sys.path.insert(0, '..')
from config import OUTPUT_DIR, SITE_TITLE, SITE_DESCRIPTION


class HTMLGenerator:
    """HTML 生成器"""

    def __init__(self, templates_dir: str = "templates", output_dir: str = OUTPUT_DIR):
        self.output_dir = output_dir
        self.env = Environment(loader=FileSystemLoader(templates_dir))
        self.year = datetime.now().year

    def format_date(self, date_str: str) -> str:
        """格式化日期显示"""
        if not date_str:
            return "未知日期"

        try:
            # 处理 ISO 格式日期
            if "T" in date_str:
                dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            else:
                dt = datetime.strptime(date_str, "%Y-%m-%d")
            return dt.strftime("%Y年%m月%d日")
        except:
            return date_str

    def generate_index(self, articles: list):
        """生成首页"""
        # 准备文章数据
        for article in articles:
            date = article.get("date") or article.get("created_time")
            article["date_display"] = self.format_date(date)

        # 按日期倒序排序
        articles.sort(
            key=lambda x: x.get("date") or x.get("created_time") or "",
            reverse=True
        )

        # 读取基础模板
        base_template = self.env.get_template("base.html")

        # 生成文章列表 HTML
        list_html = self._generate_list_html(articles)

        # 渲染页面
        html = base_template.render(
            title="首页",
            site_title=SITE_TITLE,
            site_description=SITE_DESCRIPTION,
            description=SITE_DESCRIPTION,
            content=list_html,
            year=self.year
        )

        # 写入文件
        os.makedirs(self.output_dir, exist_ok=True)
        output_path = os.path.join(self.output_dir, "index.html")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)

        print(f"生成首页: {output_path}")

    def _generate_list_html(self, articles: list) -> str:
        """生成文章列表 HTML"""
        html = '''
<div class="sort-controls">
    <span>排序：</span>
    <button class="sort-btn active" data-sort="desc">最新优先</button>
    <button class="sort-btn" data-sort="asc">最早优先</button>
</div>

<div class="article-list" id="article-list">
'''
        for article in articles:
            date = article.get("date") or article.get("created_time") or ""
            cover_image = article.get("cover_image", "")
            preview_text = article.get("preview_text", "")

            # 封面图 HTML
            if cover_image:
                cover_html = f'<div class="article-cover"><img src="{cover_image}" alt="{article["title"]}" loading="lazy"></div>'
            else:
                cover_html = ''

            # 预览文本 HTML
            preview_html = f'<p class="article-preview">{preview_text}</p>' if preview_text else ''

            html += f'''
    <article class="article-item" data-date="{date}">
        {cover_html}
        <div class="article-content-wrap">
            <a href="{article['id']}.html">
                <h2 class="article-title">{article['title']}</h2>
            </a>
            {preview_html}
            <div class="article-meta">
                <time>{article['date_display']}</time>
            </div>
        </div>
    </article>
'''
        html += '''
</div>

<style>
    .sort-controls {
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .sort-btn {
        padding: 6px 12px;
        border: 1px solid var(--border-color);
        background: var(--bg-color);
        color: var(--text-color);
        border-radius: 4px;
        cursor: pointer;
        font-size: 0.9em;
    }

    .sort-btn.active {
        background: var(--text-color);
        color: var(--bg-color);
    }

    .article-list {
        display: flex;
        flex-direction: column;
        gap: 24px;
    }

    .article-item {
        display: flex;
        gap: 16px;
        padding-bottom: 24px;
        border-bottom: 1px solid var(--border-color);
    }

    .article-item:last-child {
        border-bottom: none;
    }

    .article-cover {
        flex-shrink: 0;
        width: 160px;
        height: 100px;
        overflow: hidden;
        border-radius: 6px;
    }

    .article-cover img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }

    .article-content-wrap {
        flex: 1;
        min-width: 0;
    }

    .article-title {
        font-size: 1.2em;
        margin: 0 0 8px 0;
        line-height: 1.4;
    }

    .article-preview {
        color: var(--text-secondary);
        font-size: 0.9em;
        margin: 0 0 8px 0;
        line-height: 1.5;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }

    .article-meta {
        color: var(--text-secondary);
        font-size: 0.85em;
        display: flex;
        gap: 12px;
    }

    @media (max-width: 600px) {
        .article-item {
            flex-direction: column;
        }

        .article-cover {
            width: 100%;
            height: 180px;
        }
    }
</style>

<script>
    document.addEventListener('DOMContentLoaded', function() {
        const list = document.getElementById('article-list');
        const buttons = document.querySelectorAll('.sort-btn');

        buttons.forEach(btn => {
            btn.addEventListener('click', function() {
                buttons.forEach(b => b.classList.remove('active'));
                this.classList.add('active');

                const sort = this.dataset.sort;
                const items = Array.from(list.querySelectorAll('.article-item'));

                items.sort((a, b) => {
                    const dateA = new Date(a.dataset.date);
                    const dateB = new Date(b.dataset.date);
                    return sort === 'desc' ? dateB - dateA : dateA - dateB;
                });

                items.forEach(item => list.appendChild(item));
            });
        });
    });
</script>
'''
        return html

    def generate_article(self, article: dict):
        """生成文章详情页"""
        date = article.get("date") or article.get("created_time")
        article["date_display"] = self.format_date(date)

        # 读取基础模板
        base_template = self.env.get_template("base.html")

        # 生成文章内容 HTML
        article_html = self._generate_article_html(article)

        # 渲染页面
        html = base_template.render(
            title=article["title"],
            site_title=SITE_TITLE,
            site_description=SITE_DESCRIPTION,
            description=f'{article["title"]} - {SITE_DESCRIPTION}',
            content=article_html,
            year=self.year
        )

        # 写入文件
        os.makedirs(self.output_dir, exist_ok=True)
        output_path = os.path.join(self.output_dir, f"{article['id']}.html")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)

        print(f"生成文章: {output_path}")

    def _generate_article_html(self, article: dict) -> str:
        """生成文章内容 HTML"""
        return f'''
<article class="article">
    <header class="article-header">
        <h1>{article['title']}</h1>
        <div class="article-meta">
            <time>{article['date_display']}</time>
        </div>
    </header>

    <div class="article-content">
        {article.get('content', '')}
    </div>

    <nav class="article-nav">
        <a href="index.html">&larr; 返回列表</a>
    </nav>
</article>

<style>
    .article-header {{
        margin-bottom: 32px;
    }}

    .article-header h1 {{
        margin-top: 0;
        font-size: 1.8em;
    }}

    .article-meta {{
        color: var(--text-secondary);
    }}

    .article-content {{
        margin-bottom: 40px;
    }}

    .article-nav {{
        padding-top: 20px;
        border-top: 1px solid var(--border-color);
    }}
</style>
'''
