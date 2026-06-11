"""
Instagram 自動投稿スクリプト
@ai_jidou_salon / 鷹村｜SNS投稿0秒で月10人集客
Buffer GraphQL API 経由で投稿
"""

import os
import requests
import random
from datetime import datetime
import pytz

# ============================================================
# 設定
# ============================================================
BUFFER_API_KEY    = os.environ.get("BUFFER_API_KEY")
BUFFER_CHANNEL_ID = "6a28fd4b8f1d11f9b26e7ae1"  # @ai_jidou_salon
BUFFER_API_URL    = "https://api.buffer.com/graphql"

JST = pytz.timezone("Asia/Tokyo")

# ============================================================
# 投稿タイプ別画像URL
# ============================================================
IMAGE_URLS = {
    "炎上":    "https://raw.githubusercontent.com/k904362-wq/instagram-images/main/ChatGPT%20Image%202026%E5%B9%B46%E6%9C%8811%E6%97%A5%2010_00_57.png",
    "パクリOK": "https://raw.githubusercontent.com/k904362-wq/instagram-images/main/ChatGPT%20Image%202026%E5%B9%B46%E6%9C%8811%E6%97%A5%2010_02_16.png",
    "VS":      "https://raw.githubusercontent.com/k904362-wq/instagram-images/main/ChatGPT%20Image%202026%E5%B9%B46%E6%9C%8811%E6%97%A5%2010_03_17.png",
    "Tier":    "https://raw.githubusercontent.com/k904362-wq/instagram-images/main/ChatGPT%20Image%202026%E5%B9%B46%E6%9C%8811%E6%97%A5%2010_03_58.png",
    "実体験":  "https://raw.githubusercontent.com/k904362-wq/instagram-images/main/ChatGPT%20Image%202026%E5%B9%B46%E6%9C%8811%E6%97%A5%2010_04_58.png",
    "問いかけ": "https://raw.githubusercontent.com/k904362-wq/instagram-images/main/ChatGPT%20Image%202026%E5%B9%B46%E6%9C%8811%E6%97%A5%2010_05_47.png",
    "LINE誘導": "https://raw.githubusercontent.com/k904362-wq/instagram-images/main/ChatGPT%20Image%202026%E5%B9%B46%E6%9C%8811%E6%97%A5%2010_08_49.png",
}

# ============================================================
# 投稿テンプレート
# ============================================================
CTA = """
↓「Threads自動投稿マニュアル」無料配布中
プロフィールのリンクから受け取れます"""

POST_TEMPLATES = {

    "炎上": [
        """怒られそうですが正直に言います。

SNSを毎日頑張っているサロンオーナーの9割が、集客できない本当の理由を知りません。

問題は投稿の質じゃない。
設計がないだけです。
{cta}

#サロン集客 #AI集客 #自動投稿 #1人サロン""",

        """炎上覚悟で言います。

「毎日投稿すれば集客できる」は嘘です。

正確には、
設計なしに毎日投稿しても予約は埋まりません。

変えるべきは頻度じゃなく、仕組みです。
{cta}

#サロン集客 #AI自動投稿 #集客の仕組み""",

        """サロンオーナーが知らない事実を言います。

フォロワー1000人いても、月の新規が3人という人がいます。

原因は投稿の質じゃない。
LINEへの導線がないだけです。
{cta}

#サロン経営 #SNS集客 #LINE集客""",
    ],

    "パクリOK": [
        """そのまま使えます。パクってください。

AIで24時間自動集客が回る
サロン向け初期設定の全手順をまとめました。

スルーする理由、ある？
{cta}

#AI集客 #サロン集客 #自動投稿 #保存推奨""",

        """丸パクリOKです。

集客できているサロンが必ずやっている
SNS設計の4つのポイント↓

① ターゲットを1人に絞る
② 投稿タイプを曜日で固定する
③ 固定投稿をLPとして使う
④ LINE誘導を週2回入れる

後で見返せるように保存推奨。
{cta}

#サロン集客 #SNS運用 #保存""",

        """コピペOKです。

AIで投稿を自動化したいサロンオーナーが
最初にやるべきこと3つ↓

① Claudeに自分のサロンの強みを教える
② 投稿タイプ別にテンプレートを作らせる
③ 予約投稿ツールで自動化する

これだけで投稿時間がゼロになります。
{cta}

#AI活用 #サロン経営 #時短""",
    ],

    "VS": [
        """集客できるSNS vs できないSNS

❌ できないSNS
・毎日なんとなく投稿してる
・フォロワー増やすのが目標
・手書きで頑張ってる

✅ できるSNS
・AIで24時間自動投稿が回る
・LINEへの導線が設計されてる
・ターゲットが1人に絞られてる

差は仕組みがあるかどうかだけ。
{cta}

#サロン集客 #AI自動投稿 #SNS運用""",

        """伸びるサロン vs 消耗するサロン

❌ 消耗するサロン
・集客をSNSの気合いに頼ってる
・毎月集客に不安を感じてる
・施術中も投稿のことを考えてる

✅ 伸びるサロン
・AIが24時間集客を代わりにやってる
・施術に100%集中できる

差は能力じゃない。
仕組みがあるかどうかだけ。
{cta}

#1人サロン #AI集客 #サロン経営""",
    ],

    "Tier": [
        """集客SNS Tier表

【Tier S】予約が自動で埋まる
・AIで自動投稿が24時間稼働
・LINEへの導線が固定投稿にある

【Tier A】月10人以上
・投稿タイプを曜日で設計
・LINE誘導を週2回入れてる

【Tier D】頑張って0人
・毎日なんとなく投稿
・フォロワー数が目標

あなたは今どのTier？
{cta}

#サロン集客 #SNS運用 #AI活用""",

        """サロンSNS Tier表

【絶対NG】
・ハッシュタグ20個つける
・キャンペーン依存

【まあ大丈夫】
・毎日投稿できない日がある
・文章が上手く書けない

集客できない本当の理由は
投稿の質でも頻度でもない。

「導線設計がないこと」です。
{cta}

#サロン経営 #集客 #SNS""",
    ],

    "実体験": [
        """3年前、毎日投稿していたのに
月の新規は5人だった。

変えたのは投稿頻度じゃなく、設計だった。

今は週数回の投稿で、
AIが24時間集客を代わりにやってくれている。

消耗をやめて、仕組みにシフトした結果です。
{cta}

#サロン集客 #AI自動化 #1人サロン""",

        """深夜2時に投稿文を考えていた時期があった。

今は違う。

AIが投稿を作り、自動で配信し、
LINEに見込み客を流してくれている。

施術に集中できるようになったのは、
仕組みを作ってからです。
{cta}

#AI集客 #サロン経営 #自動化""",

        """「顔出しなし・営業なし・DM送付なし」で
集客できるようになった話をします。

変えたのはたった一つ。

AIに自分のサロンの強みを覚えさせて、
24時間投稿し続ける仕組みを作ったこと。

設定時間は最初の1〜2時間だけ。
あとはAIが動き続けます。
{cta}

#サロン集客 #AI活用 #自動投稿""",
    ],

    "問いかけ": [
        """毎日SNS投稿を頑張っているのに、
全く集客につながっていない。

こんな経験、ありますか？
{cta}

#サロン集客 #SNS運用 #1人サロン""",

        """サロン集客に、もうAI使ってますか？

使っている人と使っていない人で、
1年後に圧倒的な差が出ます。
{cta}

#AI集客 #サロン経営 #自動投稿""",

        """1人でサロンを回しながら、
集客まで全部自分でやっている。

それ、限界じゃないですか？
{cta}

#1人サロン #サロン集客 #AI活用""",

        """投稿を頑張っているのに予約が増えない。

その原因、「投稿の質」だと思っていませんか？

たぶん違います。
{cta}

#サロン集客 #SNS #集客""",
    ],

    "LINE誘導": [
        """Threads投稿を自動化して集客したいサロンオーナーに
「Threads自動投稿マニュアル」を無料でお渡しします。

設定時間1〜2時間で
AIが24時間投稿し続ける仕組みが完成します。

プロフィールのリンクから受け取れます↓

#サロン集客 #Threads自動投稿 #LINE #無料プレゼント""",

        """AIでThreads自動投稿を始めたいサロンオーナー、います？

初期設定の全手順をPDFにまとめました。
無料でお渡しします。

プロフィールのリンクから受け取れます↓

#AI集客 #サロン経営 #自動化 #無料""",
    ],
}

# ============================================================
# 曜日別投稿タイプ（週1投稿・7種類を順番に）
# 0=月, 1=火, 2=水, 3=木, 4=金, 5=土, 6=日
# ============================================================
WEEKDAY_TYPE = {
    0: "問いかけ",
    1: "炎上",
    2: "パクリOK",
    3: "VS",
    4: "Tier",
    5: "実体験",
    6: "LINE誘導",
}

# ============================================================
# Buffer GraphQL投稿
# ============================================================

MUTATION = """
mutation CreatePost($input: CreatePostInput!) {
    createPost(input: $input) {
        ... on PostActionSuccess {
            post {
                id
                status
            }
        }
    }
}
"""

def post_to_buffer(text: str, image_url: str):
    """Buffer GraphQL APIで投稿"""
    variables = {
        "input": {
            "channelId": BUFFER_CHANNEL_ID,
            "text": text,
            "schedulingType": "automatic",
            "mode": "shareNow",
            "assets": [{"image": {"url": image_url}}]
        }
    }

    response = requests.post(
        BUFFER_API_URL,
        json={"query": MUTATION, "variables": variables},
        headers={
            "Authorization": f"Bearer {BUFFER_API_KEY}",
            "Content-Type": "application/json"
        }
    )
    return response.json()


def get_post_content():
    """今日の投稿タイプ・テキスト・画像URLを返す"""
    now = datetime.now(JST)
    weekday = now.weekday()
    today_str = now.strftime("%Y-%m-%d")

    post_type = WEEKDAY_TYPE.get(weekday, "問いかけ")
    templates  = POST_TEMPLATES[post_type]
    image_url  = IMAGE_URLS[post_type]

    # 日付をシードにして毎日違うテンプレートを選択
    random.seed(hash(today_str) % (2**32))
    template = random.choice(templates)
    # LINE誘導タイプはCTA不要（本文にすでに含まれている）
    text = template.format(cta=CTA) if "{cta}" in template else template

    print(f"[{today_str}] 曜日: {['月','火','水','木','金','土','日'][weekday]} / タイプ: {post_type}")
    return post_type, text, image_url


def main():
    now = datetime.now(JST)
    print(f"=== Instagram自動投稿開始 {now.strftime('%Y-%m-%d %H:%M')} JST ===")

    if not BUFFER_API_KEY:
        print("ERROR: BUFFER_API_KEY が設定されていません")
        return

    post_type, text, image_url = get_post_content()

    print(f"投稿タイプ: {post_type}")
    print(f"画像URL: {image_url}")
    print(f"投稿内容:\n{text}\n")

    result = post_to_buffer(text, image_url)

    if "errors" in result:
        print(f"ERROR: {result['errors']}")
    else:
        create_post = result.get("data", {}).get("createPost", {})
        post_id = create_post.get("post", {}).get("id", "不明")
        status  = create_post.get("post", {}).get("status", "")
        print(f"SUCCESS: Instagram投稿完了 (ID: {post_id}, status: {status})")


if __name__ == "__main__":
    main()
