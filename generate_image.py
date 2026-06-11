"""
HTMLテンプレート → スクリーンショット → Imgur アップロード
投稿タイプごとに画像を生成してURLを返す
"""

import asyncio
import base64
import os
import re
import requests
from pathlib import Path
from playwright.async_api import async_playwright

TEMPLATE_PATH = Path(__file__).parent / "templates" / "post_template.html"

# 投稿タイプ別タグ表示名
TAG_LABELS = {
    "炎上":    "本音",
    "パクリOK": "保存推奨",
    "VS":      "比較",
    "Tier":    "Tier表",
    "実体験":  "実体験",
    "問いかけ": "質問",
    "LINE誘導": "プレゼント",
}

# 投稿タイプ別アクセントカラー
TAG_COLORS = {
    "炎上":    "linear-gradient(135deg, #ef4444, #dc2626)",
    "パクリOK": "linear-gradient(135deg, #10b981, #059669)",
    "VS":      "linear-gradient(135deg, #6366f1, #8b5cf6)",
    "Tier":    "linear-gradient(135deg, #f59e0b, #d97706)",
    "実体験":  "linear-gradient(135deg, #3b82f6, #2563eb)",
    "問いかけ": "linear-gradient(135deg, #8b5cf6, #7c3aed)",
    "LINE誘導": "linear-gradient(135deg, #06b6d4, #0891b2)",
}


def build_html(post_type: str, text: str) -> str:
    """テンプレートHTMLにテキストを埋め込む"""
    html = TEMPLATE_PATH.read_text(encoding="utf-8")

    tag   = TAG_LABELS.get(post_type, post_type)
    color = TAG_COLORS.get(post_type, "linear-gradient(135deg, #6366f1, #8b5cf6)")

    # ハッシュタグ以降を除いてメイン本文を抽出
    lines = text.strip().split("\n")
    body_lines = []
    for line in lines:
        if line.startswith("#"):
            break
        # CTAも除く（画像内のフッターに表示済み）
        if "自動投稿マニュアル" in line or "プロフィールのリンク" in line or line.strip() == "↓":
            continue
        body_lines.append(line)

    body = "\n".join(body_lines).strip()

    # HTMLエスケープ
    body_escaped = (body
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("✅", '<span class="good">✅</span>')
        .replace("❌", '<span class="bad">❌</span>')
    )

    html = html.replace("{{ tag }}", tag)
    html = html.replace("{{ body }}", body_escaped)
    html = html.replace(
        "linear-gradient(135deg, #6366f1, #8b5cf6);",
        f"{color};",
        1  # tagのbackgroundのみ
    )
    return html


async def screenshot_html(html: str, output_path: str):
    """HTMLを1080×1350のPNG画像にレンダリング"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1080, "height": 1350})
        await page.set_content(html, wait_until="networkidle")
        await page.screenshot(path=output_path, full_page=False)
        await browser.close()


def upload_to_imgur(image_path: str) -> str:
    """ImgurのAnonymous APIに画像をアップロードしてURLを返す"""
    client_id = os.environ.get("IMGUR_CLIENT_ID", "546c25a59c58ad7")  # Imgur公開デモID

    with open(image_path, "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")

    response = requests.post(
        "https://api.imgur.com/3/image",
        headers={"Authorization": f"Client-ID {client_id}"},
        data={"image": data, "type": "base64"}
    )
    result = response.json()

    if result.get("success"):
        url = result["data"]["link"]
        print(f"Imgur アップロード成功: {url}")
        return url
    else:
        raise Exception(f"Imgur アップロード失敗: {result}")


def generate_image(post_type: str, text: str) -> str:
    """
    投稿タイプとテキストから画像を生成してURLを返す
    メインスクリプトから呼び出す
    """
    html = build_html(post_type, text)

    tmp_path = f"/tmp/instagram_post_{post_type}.png"
    asyncio.run(screenshot_html(html, tmp_path))

    url = upload_to_imgur(tmp_path)
    return url


if __name__ == "__main__":
    # テスト実行
    test_text = """伸びるサロン vs 消耗するサロン

❌ 消耗するサロン
・集客をSNSの気合いに頼ってる
・毎月集客に不安を感じてる

✅ 伸びるサロン
・AIが24時間集客を代わりにやってる
・施術に100%集中できる

差は能力じゃない。
仕組みがあるかどうかだけ。

#1人サロン #AI集客"""

    print("画像生成中...")
    url = generate_image("VS", test_text)
    print(f"完成URL: {url}")
