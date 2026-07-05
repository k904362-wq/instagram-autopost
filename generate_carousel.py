"""
カルーセル画像生成モジュール
HTMLテンプレート3種 → Playwright → Imgur
複数枚のURLリストを返す
"""

import asyncio
import base64
import os
import requests
from pathlib import Path
from playwright.async_api import async_playwright

TEMPLATES_DIR = Path(__file__).parent / "templates"
COVER_TMPL    = TEMPLATES_DIR / "slide_cover.html"
POINT_TMPL    = TEMPLATES_DIR / "slide_point.html"
SUMMARY_TMPL  = TEMPLATES_DIR / "slide_summary.html"

IMGUR_CLIENT_ID = os.environ.get("IMGUR_CLIENT_ID", "546c25a59c58ad7")


# ============================================================
# 投稿タイプ別カルーセルコンテンツ（10枚構成）
# ============================================================
CAROUSEL_CONTENT = {

    "問いかけ": {
        "cover": {
            "slide_num": "01",
            "sub_label": "1人サロンオーナーへ",
            "main_title": "毎日投稿しているのに<br><span class='yellow'>予約が増えない</span><br>本当の理由",
            "content_box": "まず決めるべき\n1つのこと",
        },
        "points": [
            {
                "heading": "SNSを頑張るほど\n<span class='yellow'>疲弊</span>する矛盾",
                "body": "毎朝6時に投稿。\nストーリーも毎日上げてる。\n\nでも予約は月3〜5人のまま。\n\nこの状況、心当たりありませんか？",
                "hint": "頑張り方が間違っているだけ",
            },
            {
                "heading": "問題は<span class='yellow'>投稿の質</span>じゃない",
                "body": "「もっと上手い文章を書けば」\n「写真のクオリティを上げれば」\n\nそれが原因じゃない場合がほとんど。\n\n本当の原因は<span class='key'>「設計」</span>がないこと。",
                "hint": "質より設計が先",
            },
            {
                "heading": "<span class='yellow'>集客設計</span>とは何か",
                "body": "① ターゲットを1人に絞る\n② 投稿タイプを固定する\n③ LINEへの導線を明確にする\n\nこの3つが揃って初めて\nSNSが集客につながる。",
                "hint": "設計なしの投稿は穴の空いたバケツ",
            },
            {
                "heading": "やってはいけない\n<span class='yellow'>3つのNG</span>",
                "body": "❌ フォロワー数を目標にする\n❌ なんとなく毎日投稿する\n❌ 全員に向けて書く\n\nこのどれか1つでも当てはまる人は\n今すぐやめた方がいい。",
                "hint": "NGをやめるだけで変わる",
            },
            {
                "heading": "<span class='yellow'>AI</span>を使えば\n何が変わるか",
                "body": "投稿文を考える時間：ゼロ\n画像を作る手間：ゼロ\n投稿し忘れるリスク：ゼロ\n\nAIが24時間代わりに動き続ける。\nあなたは施術に集中できる。",
                "hint": "AI＝時間を買うツール",
            },
            {
                "heading": "設定は\n<span class='yellow'>たった1〜2時間</span>",
                "body": "難しい知識は不要。\nスマホがあればできる。\n\n最初の設定だけ済ませれば\nあとはAIが毎日動き続ける。\n\n一度作った仕組みは消えない。",
                "hint": "初期投資で永続的なリターン",
            },
            {
                "heading": "<span class='yellow'>月10人</span>の\n新規をとる仕組み",
                "body": "SNSで認知\n→ 固定投稿でLINEに誘導\n→ LINEで特典プレゼント\n→ 予約へ\n\nこのルートが設計されていれば\n投稿1本ごとに集客が動く。",
                "hint": "ルートを作れば流れる",
            },
            {
                "heading": "今すぐ\n<span class='yellow'>確認すること</span>",
                "body": "あなたのプロフィールを開いてください。\n\nLINEへの導線はありますか？\n固定投稿はありますか？\n\nここが集客の入り口です。",
                "hint": "プロフィールがLPになっているか",
            },
        ],
        "summary": {
            "main_message": "<span class='yellow'>保存</span>して、\n集客の仕組みを\n作るときに見返してください",
            "summary_body": "・投稿の質より「設計」が先\n・AIで投稿を自動化する\n・LINEへの導線を固定投稿に入れる\n\nこれだけで月10人集客が動き出す。",
        },
    },

    "炎上": {
        "cover": {
            "slide_num": "01",
            "sub_label": "怒られそうですが正直に言います",
            "main_title": "<span class='yellow'>毎日投稿</span>は\n集客に\nならない",
            "content_box": "9割のサロンオーナーが\n知らない事実",
        },
        "points": [
            {
                "heading": "<span class='yellow'>衝撃の事実</span>を\n言います",
                "body": "フォロワー2000人いる\nサロンオーナーが\n月の新規3人だった。\n\nフォロワー数と集客は\n別の話です。",
                "hint": "数字に騙されるな",
            },
            {
                "heading": "毎日投稿しても\n<span class='yellow'>予約が埋まらない</span>理由",
                "body": "投稿→見てもらう→終わり\n\nここで止まっている。\n\n本来はここから\n「LINE登録→特典受け取り→予約」\nという流れが必要。",
                "hint": "投稿はゴールじゃなくスタート",
            },
            {
                "heading": "<span class='yellow'>設計</span>のない投稿は\n穴の空いたバケツ",
                "body": "水を注ぎ続けても\n全部下に流れていく。\n\nどれだけ頑張って投稿しても\nLINEへの導線がなければ\n集客にはつながらない。",
                "hint": "バケツの穴を先に塞ぐ",
            },
            {
                "heading": "じゃあ何を\n<span class='yellow'>変えればいい</span>か",
                "body": "① 固定投稿にLINE誘導を入れる\n② 週2回、LINE誘導投稿をする\n③ AIで投稿を自動化する\n\nこの3つだけ。\nあとは仕組みが動く。",
                "hint": "変える順番が大事",
            },
            {
                "heading": "<span class='yellow'>AI</span>が代わりに\n投稿する時代",
                "body": "文章を考えるのはAI。\n画像を作るのもAI。\n投稿するのも自動。\n\nあなたがやることは\n最初の設定だけ。",
                "hint": "AIに任せられることは任せる",
            },
            {
                "heading": "<span class='yellow'>消耗</span>をやめて\n仕組みに切り替える",
                "body": "深夜に投稿文を考えていた。\n施術中も「今日何投稿しよう」と考えていた。\n\nそれは全部やめていい。\nAIが24時間動いてくれる。",
                "hint": "消耗は選択肢の一つに過ぎない",
            },
            {
                "heading": "設定は\n<span class='yellow'>1〜2時間</span>で完了",
                "body": "難しいことは何もない。\nスマホとAIがあればできる。\n\n設定が終われば\nあとは勝手に動き続ける。\n\n時間を買う感覚に近い。",
                "hint": "一度だけ頑張れば永続する",
            },
            {
                "heading": "今日から\n<span class='yellow'>変えられること</span>",
                "body": "プロフィールのリンク欄を確認する\n↓\nLINEへの誘導を入れる\n↓\nAI自動投稿を設定する\n\nこの順番でやれば必ず動く。",
                "hint": "できることから今日始める",
            },
        ],
        "summary": {
            "main_message": "<span class='yellow'>保存</span>して、\n今すぐプロフィールを\n見直してください",
            "summary_body": "・毎日投稿より「設計」が大事\n・LINEへの導線を先に作る\n・AIで投稿を自動化する\n\n仕組みを作った人だけが楽になる。",
        },
    },

    "パクリOK": {
        "cover": {
            "slide_num": "01",
            "sub_label": "そのまま使えます",
            "main_title": "AI自動集客の\n<span class='yellow'>全手順</span>\nまとめました",
            "content_box": "パクってください",
        },
        "points": [
            {
                "heading": "STEP 1\n<span class='yellow'>ターゲット</span>を1人に絞る",
                "body": "「誰に届けたいか」を\n具体的に1人イメージする。\n\n例：30代・子育て中・\n自分へのご褒美を求めている\n近所の主婦\n\n<span class='key'>1人に絞ると刺さる投稿になる。</span>",
                "hint": "全員に届けようとすると誰にも届かない",
            },
            {
                "heading": "STEP 2\n<span class='yellow'>投稿タイプ</span>を曜日で固定",
                "body": "月：問いかけ投稿\n火：本音投稿\n水：保存推奨投稿\n木：比較投稿\n金：体験談投稿\n\n曜日ごとにパターンを固定すると\nAIが迷わず生成できる。",
                "hint": "型があるから自動化できる",
            },
            {
                "heading": "STEP 3\n<span class='yellow'>固定投稿</span>をLPにする",
                "body": "プロフィールの固定投稿に\n「無料プレゼント告知」を入れる。\n\nここがLINE誘導の入り口。\nここを作ると\n毎投稿が集客につながる。",
                "hint": "固定投稿がすべての起点",
            },
            {
                "heading": "STEP 4\n<span class='yellow'>LINE特典</span>を用意する",
                "body": "プレゼントの中身は何でもOK。\n\n・施術メニューPDF\n・セルフケア動画\n・初回割引クーポン\n\nもらって嬉しいものを1つ用意する。",
                "hint": "特典がないと登録してもらえない",
            },
            {
                "heading": "STEP 5\n<span class='yellow'>AI投稿</span>を設定する",
                "body": "ClaudeなどのAIに\n自分のサロン情報を登録。\n\n投稿テンプレートを作らせる。\n\n予約投稿ツール（Buffer等）に\n自動送信を設定する。",
                "hint": "設定さえすれば動き続ける",
            },
            {
                "heading": "STEP 6\n週2回<span class='yellow'>LINE誘導</span>投稿",
                "body": "「無料プレゼント配布中」投稿を\n週に2回入れる。\n\nしつこく感じるかもしれないが\n実際は2〜3割の人しか\n最初の投稿を見ていない。",
                "hint": "繰り返しが大事",
            },
            {
                "heading": "STEP 7\n<span class='yellow'>数値</span>を見て改善する",
                "body": "1週間後にチェックする数値：\n\n・LINE登録数\n・いいね・保存が多い投稿\n・フォロワー増加数\n\nここを見て、次の投稿に活かす。",
                "hint": "データを見ない人は成長できない",
            },
            {
                "heading": "完成したら\n<span class='yellow'>勝手に動く</span>",
                "body": "設定完了後は：\n\nAIが毎日投稿を作り\n自動でInstagramに投稿され\nLINEに見込み客が流れてくる。\n\nあなたは施術に集中するだけ。",
                "hint": "仕組みは24時間365日働く",
            },
        ],
        "summary": {
            "main_message": "<span class='yellow'>保存</span>して、\n今日から1つずつ\n実践してください",
            "summary_body": "STEP1：ターゲットを1人に絞る\nSTEP2：曜日別投稿タイプを決める\nSTEP3：固定投稿をLPにする\nSTEP4：LINE特典を用意する\nSTEP5：AI自動投稿を設定する",
        },
    },

    "VS": {
        "cover": {
            "slide_num": "01",
            "sub_label": "差はここだけ",
            "main_title": "集客できる\nサロン<span class='yellow'> vs </span>\nできないサロン",
            "content_box": "あなたはどっち側か\n確認してください",
        },
        "points": [
            {
                "heading": "SNSの<span class='yellow'>目標設定</span>\nが違う",
                "body": "❌ できないサロン\nフォロワーを増やすことが目標\n\n✅ できるサロン\nLINE登録者を増やすことが目標\n\nSNSはLINEへの橋渡し。\n<span class='key'>ゴールを間違えると全部ズレる。</span>",
                "hint": "ゴールが違えば行動も違う",
            },
            {
                "heading": "投稿の<span class='yellow'>設計</span>が違う",
                "body": "❌ できないサロン\nなんとなく毎日投稿している\n\n✅ できるサロン\n曜日ごとに投稿タイプが決まっている\nLINE誘導が週2回入っている",
                "hint": "型がある人は迷わない",
            },
            {
                "heading": "<span class='yellow'>プロフィール</span>の\n使い方が違う",
                "body": "❌ できないサロン\nプロフィールが自己紹介で終わっている\n\n✅ できるサロン\nプロフィールのリンク欄にLINEがある\n固定投稿で無料プレゼントを告知している",
                "hint": "プロフィールがLPになっているか",
            },
            {
                "heading": "<span class='yellow'>時間の使い方</span>が違う",
                "body": "❌ できないサロン\n毎晩1〜2時間投稿文を考えている\n深夜に投稿している\n\n✅ できるサロン\nAIが自動で投稿を作り配信している\n施術に100%集中できている",
                "hint": "できる人は仕組みを作る",
            },
            {
                "heading": "<span class='yellow'>集客導線</span>が違う",
                "body": "❌ できないサロン\n投稿→見てもらって終わり\n\n✅ できるサロン\n投稿→固定投稿へ→LINE登録\n→特典受け取り→予約\n\nルートが設計されているかどうか。",
                "hint": "導線がなければ宝の持ち腐れ",
            },
            {
                "heading": "<span class='yellow'>メンタル</span>が違う",
                "body": "❌ できないサロン\n「いいねが少ない…」と落ち込む\n施術中も集客のことを考えてしまう\n\n✅ できるサロン\nAIが動いているので気にしない\n数値だけをたまに確認する",
                "hint": "仕組みがあると心に余裕が生まれる",
            },
            {
                "heading": "差が生まれる\n<span class='yellow'>本当の理由</span>",
                "body": "能力の差ではない。\nセンスの差でもない。\n\n「仕組みを作ったかどうか」\nただこれだけ。\n\n仕組みは誰でも作れる。",
                "hint": "スタートラインは同じ",
            },
            {
                "heading": "今日から\n<span class='yellow'>できること</span>",
                "body": "① プロフィールのリンク欄を確認する\n② 固定投稿にLINE誘導を入れる\n③ AI自動投稿の設定を始める\n\nこの順番でやれば\n1週間後には仕組みができている。",
                "hint": "小さく始めて大きく育てる",
            },
        ],
        "summary": {
            "main_message": "<span class='yellow'>保存</span>して\n「できるサロン」側に\n移行してください",
            "summary_body": "差はたった1つ。\n仕組みを作ったかどうかだけ。\n\nAI自動投稿 × LINE誘導設計\nこれだけで月10人集客が動く。",
        },
    },

    "Tier": {
        "cover": {
            "slide_num": "01",
            "sub_label": "正直に評価します",
            "main_title": "サロン集客\n<span class='yellow'>SNS運用</span>\nTier表",
            "content_box": "あなたは今どの位置か\n確認してください",
        },
        "points": [
            {
                "heading": "<span class='yellow'>Tier SS</span>\n予約が自動で埋まる",
                "body": "・AI自動投稿が24時間稼働中\n・LINE登録が毎週増えている\n・固定投稿がLPの役割を果たしている\n・施術に100%集中できている",
                "hint": "<span class='em'>仕組みが完成した状態</span>",
            },
            {
                "heading": "<span class='yellow'>Tier S</span>\n月10人以上の新規",
                "body": "・投稿タイプが曜日で固定されている\n・LINE誘導を週2回入れている\n・プロフィールにLINEリンクがある\n・数値を週1で確認している",
                "hint": "設計がきちんとある状態",
            },
            {
                "heading": "<span class='yellow'>Tier A</span>\n月5〜9人",
                "body": "・投稿の質は高い\n・フォロワーは増えている\n・でもLINEへの導線が弱い\n\nあと一歩で大きく変わる。",
                "hint": "導線を強化すれば突き抜ける",
            },
            {
                "heading": "<span class='yellow'>Tier B</span>\n月1〜4人",
                "body": "・毎日投稿できている\n・でも設計がない\n・フォロワー数を目標にしている\n\n頑張っているのに結果が出ない\n典型的なパターン。",
                "hint": "方向を変えるだけで一気に上がる",
            },
            {
                "heading": "<span class='yellow'>Tier C</span>\n新規ゼロ",
                "body": "・なんとなく投稿している\n・ターゲットが決まっていない\n・プロフィールが自己紹介で終わっている\n\n投稿の前にやることがある。",
                "hint": "土台から作り直す必要がある",
            },
            {
                "heading": "<span class='yellow'>Tier D</span>\n消耗している",
                "body": "・毎晩投稿文を考えている\n・いいねが少ないと落ち込む\n・それでも結果が出ていない\n\nやり方を根本から変えないと\nずっとこのまま。",
                "hint": "消耗は選択肢ではない",
            },
            {
                "heading": "Tier を上げる\n<span class='yellow'>最速ルート</span>",
                "body": "① AI自動投稿を設定する（2時間）\n② 固定投稿にLINE誘導を入れる（30分）\n③ 週2回LINE誘導投稿を入れる（自動）\n\nこれだけで\nTier B→Tier Sに上がれる。",
                "hint": "正しい順番でやれば最速で変わる",
            },
            {
                "heading": "今すぐ\n<span class='yellow'>自分のTier</span>を確認",
                "body": "プロフィールを開いて確認する：\n\n□ LINEへのリンクがある\n□ 固定投稿でプレゼント告知している\n□ 投稿タイプが曜日で決まっている\n\n全部YESならTier A以上。",
                "hint": "現状把握が最初の一歩",
            },
        ],
        "summary": {
            "main_message": "<span class='yellow'>保存</span>して、\n今のTierから\n1つ上を目指してください",
            "summary_body": "Tier SS：AI自動投稿 × LINE導線完備\nTier S：設計あり × 週2LINE誘導\nTier A：質は高いが導線が弱い\nTier B〜D：設計から見直しが必要",
        },
    },

    "実体験": {
        "cover": {
            "slide_num": "01",
            "sub_label": "実際に起きたことを話します",
            "main_title": "投稿0秒で\n<span class='yellow'>月10人</span>\n集客できた話",
            "content_box": "顔出しなし\n営業なし\nDMなし",
        },
        "points": [
            {
                "heading": "<span class='yellow'>3年前</span>\n毎日投稿していた",
                "body": "毎朝6時に起きて投稿文を考えた。\n写真も毎回撮り直した。\nハッシュタグも30個つけた。\n\n結果：月の新規は5人。\n\n頑張り方が間違っていた。",
                "hint": "努力の方向性が全てを決める",
            },
            {
                "heading": "変えたのは\n<span class='yellow'>投稿頻度</span>じゃない",
                "body": "「毎日じゃなくて週3でいい」\nそういう話でもなかった。\n\n変えたのは「設計」。\n\n誰に・何を・どこへ繋げるか\nこれを先に決めた。",
                "hint": "設計が先、行動が後",
            },
            {
                "heading": "まず<span class='yellow'>LINEの導線</span>を\n作った",
                "body": "プロフィールのリンク欄にLINEを入れた。\n固定投稿でプレゼントを告知した。\n\nたったこれだけで\n毎投稿がLINE登録につながるようになった。",
                "hint": "入口を作ると自然に流れ込む",
            },
            {
                "heading": "次に<span class='yellow'>AI</span>に\n投稿を任せた",
                "body": "自分のサロンの情報をAIに登録。\n投稿テンプレートを作ってもらった。\n自動投稿ツールに接続した。\n\n設定時間：約2時間。\nその後：投稿時間ゼロ。",
                "hint": "2時間で永続する仕組みができた",
            },
            {
                "heading": "1週間後に\n<span class='yellow'>変化</span>が起きた",
                "body": "LINE登録が週3〜5件来るようになった。\n\n投稿を頑張っていた時より\n多い。\n\n仕組みを作ってから\n初めて集客が「流れ込む」感覚になった。",
                "hint": "仕組みは時間差で効いてくる",
            },
            {
                "heading": "今は<span class='yellow'>施術</span>だけを\nやっている",
                "body": "投稿のことを考えるのは\n週1回の数値確認だけ。\n\nAIが24時間投稿し続け\nLINEに見込み客が流れてくる。\n\n施術に集中できるようになった。",
                "hint": "本業に集中できることが最大の価値",
            },
            {
                "heading": "誰でも\n<span class='yellow'>再現できる</span>",
                "body": "特別なスキルは不要。\nSNSの知識も不要。\n\n必要なのは：\n① 初期設定の2時間\n② LINE特典を1つ用意すること\n\nそれだけで仕組みができる。",
                "hint": "仕組みに特別な才能はいらない",
            },
            {
                "heading": "最初の<span class='yellow'>一歩</span>は\nこれだけ",
                "body": "プロフィールのリンク欄を確認する。\n\nLINEへの誘導がなければ\n今すぐ追加する。\n\nそれがすべての起点になる。",
                "hint": "小さな一歩が大きく変える",
            },
        ],
        "summary": {
            "main_message": "<span class='yellow'>保存</span>して、\n仕組みを作るときの\n参考にしてください",
            "summary_body": "①LINEの導線を先に作る\n②AIに投稿を任せる\n③施術に集中する\n\nこの順番で動けば\n必ず同じ結果が出る。",
        },
    },

    "LINE誘導": {
        "cover": {
            "slide_num": "01",
            "sub_label": "無料でお渡しします",
            "main_title": "<span class='yellow'>Threads</span>自動投稿\n初期設定\nマニュアル",
            "content_box": "プロフィールのリンクから\n受け取れます",
        },
        "points": [
            {
                "heading": "こんな人に\n<span class='yellow'>渡したい</span>",
                "body": "・AIで投稿を自動化したいが\n  やり方がわからない\n・毎日投稿に疲れている\n・集客の仕組みを作りたい\n\n1人でも当てはまれば受け取ってください。",
                "hint": "該当する人は全員もらってOK",
            },
            {
                "heading": "マニュアルの\n<span class='yellow'>中身</span>",
                "body": "① Threadsアカウント設定\n② AIへの情報登録方法\n③ 投稿テンプレートの作り方\n④ 自動投稿ツールの連携\n⑤ LINE誘導の設計方法\n\n全部入っています。",
                "hint": "ゼロから完成まで全手順を解説",
            },
            {
                "heading": "設定時間は\n<span class='yellow'>たった2時間</span>",
                "body": "マニュアル通りに進めれば\n<span class='key'>2時間で完成する。</span>\n\n難しい知識は不要。\nスマホがあればできる。\n\nパソコンなしでもOK。",
                "hint": "誰でも再現できる設計になっている",
            },
            {
                "heading": "完成後は\n<span class='yellow'>自動</span>で動く",
                "body": "設定が終われば：\n\n・AIが毎日投稿を作る\n・自動でThreadsに投稿される\n・LINEに見込み客が流れてくる\n\nあなたは何もしなくていい。",
                "hint": "一度作ればずっと動く",
            },
            {
                "heading": "実際に使った人の\n<span class='yellow'>変化</span>",
                "body": "「投稿時間がゼロになった」\n「LINE登録が週5件来るようになった」\n「施術に集中できるようになった」\n\n設定2時間で\nこれだけ変わる。",
                "hint": "仕組みは時間で回収できる",
            },
            {
                "heading": "<span class='yellow'>完全無料</span>で\n受け取れます",
                "body": "クレジットカード不要。\n購入手続き不要。\n\nLINEを追加するだけで\n自動的に届きます。\n\n今すぐ受け取れます。",
                "hint": "面倒な手続きは一切ない",
            },
            {
                "heading": "受け取り方は\n<span class='yellow'>3ステップ</span>",
                "body": "① プロフィールのリンクを開く\n② LINEを追加する\n③ マニュアルが自動で届く\n\n所要時間：30秒。",
                "hint": "今すぐできる",
            },
            {
                "heading": "今すぐ\n<span class='yellow'>プロフィール</span>へ",
                "body": "↑ 画面を上にスクロール\n→ @ai_jidou_salon のプロフィールへ\n→ リンク欄のLINEを追加\n→ マニュアルが届く\n\n2時間後には自動投稿が動いている。",
                "hint": "やるなら今が一番いいタイミング",
            },
        ],
        "summary": {
            "main_message": "<span class='yellow'>今すぐ</span>\nプロフィールへ\n行ってください",
            "summary_body": "「Threads自動投稿マニュアル」\n完全無料でお渡しします。\n\nプロフィールのリンクから\nLINE追加で自動受け取り。\n\n所要時間：30秒。",
        },
    },
}


# ============================================================
# HTML生成関数
# ============================================================

def build_cover(content: dict, total: int) -> str:
    html = COVER_TMPL.read_text(encoding="utf-8")
    html = html.replace("{{ slide_num }}", content["slide_num"])
    html = html.replace("{{ sub_label }}", content["sub_label"])
    html = html.replace("{{ main_title }}", content["main_title"])
    html = html.replace("{{ content_box }}", content["content_box"])
    html = html.replace("{{ total }}", str(total))
    return html


def build_point(content: dict, slide_num: int, total: int) -> str:
    html = POINT_TMPL.read_text(encoding="utf-8")
    html = html.replace("{{ slide_num }}", str(slide_num))
    html = html.replace("{{ slide_num_pad }}", f"{slide_num:02d}")
    html = html.replace("{{ total }}", str(total))

    # 見出し: \n → <br>
    heading_html = content["heading"].replace("\n", "<br>")
    html = html.replace("{{ heading }}", heading_html)

    # 本文: 行数カウントしてフォントサイズを自動調整
    body_text = content["body"]
    line_count = len(body_text.split("\n"))

    if line_count <= 5:
        body_font_size = "28px"
        body_line_height = "1.75"
        gap_height = "0.5em"   # \n\n の空白行の高さ
    elif line_count <= 7:
        body_font_size = "25px"
        body_line_height = "1.65"
        gap_height = "0.35em"
    else:
        body_font_size = "22px"
        body_line_height = "1.55"
        gap_height = "0.25em"

    # \n\n（空白行）→ 小さいgap div、\n → <br>
    body_html = body_text.replace(
        "\n\n",
        f'<div style="height:{gap_height}"></div>'
    ).replace("\n", "<br>")

    html = html.replace("{{ body }}", body_html)
    html = html.replace("{{ body_font_size }}", body_font_size)
    html = html.replace("{{ body_line_height }}", body_line_height)
    html = html.replace("{{ hint }}", content["hint"])
    return html


def build_summary(content: dict, slide_num: int, total: int) -> str:
    html = SUMMARY_TMPL.read_text(encoding="utf-8")
    html = html.replace("{{ slide_num }}", str(slide_num))
    html = html.replace("{{ total }}", str(total))
    html = html.replace("{{ main_message }}", content["main_message"])
    html = html.replace("{{ summary_body }}", content["summary_body"])
    return html


# ============================================================
# Playwright スクリーンショット
# ============================================================

async def screenshot_html(html: str, output_path: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1080, "height": 1350})
        await page.set_content(html, wait_until="networkidle")
        await page.wait_for_timeout(1000)  # フォント描画待ち
        await page.screenshot(path=output_path, full_page=False)
        await browser.close()


# ============================================================
# Imgur アップロード
# ============================================================

def upload_to_imgur(image_path: str) -> str:
    with open(image_path, "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")
    response = requests.post(
        "https://api.imgur.com/3/image",
        headers={"Authorization": f"Client-ID {IMGUR_CLIENT_ID}"},
        data={"image": data, "type": "base64"}
    )
    result = response.json()
    if result.get("success"):
        url = result["data"]["link"]
        print(f"  ✓ Imgur: {url}")
        return url
    else:
        raise Exception(f"Imgur失敗: {result}")


# ============================================================
# メイン: カルーセル全枚数を生成してURLリストを返す
# ============================================================

def generate_carousel(post_type: str) -> list:
    """
    投稿タイプに応じたカルーセル画像を生成し、ImgurのURLリストを返す
    """
    content = CAROUSEL_CONTENT.get(post_type)
    if not content:
        raise ValueError(f"未定義の投稿タイプ: {post_type}")

    points = content["points"]
    total = 1 + len(points) + 1  # 表紙 + POINT + まとめ

    urls = []
    tmp_dir = "/tmp/carousel"
    os.makedirs(tmp_dir, exist_ok=True)

    # スライド1: 表紙
    print(f"[1/{total}] 表紙を生成中...")
    cover_html = build_cover(content["cover"], total)
    cover_path = f"{tmp_dir}/slide_01_cover.png"
    asyncio.run(screenshot_html(cover_html, cover_path))
    urls.append(upload_to_imgur(cover_path))

    # スライド2〜N-1: POINT
    for i, point in enumerate(points, start=2):
        print(f"[{i}/{total}] POINT {i-1:02d} を生成中...")
        point_html = build_point(point, i, total)
        point_path = f"{tmp_dir}/slide_{i:02d}_point.png"
        asyncio.run(screenshot_html(point_html, point_path))
        urls.append(upload_to_imgur(point_path))

    # 最終スライド: まとめ
    final_num = total
    print(f"[{final_num}/{total}] まとめを生成中...")
    summary_html = build_summary(content["summary"], final_num, total)
    summary_path = f"{tmp_dir}/slide_{final_num:02d}_summary.png"
    asyncio.run(screenshot_html(summary_html, summary_path))
    urls.append(upload_to_imgur(summary_path))

    print(f"\n✅ カルーセル生成完了: {len(urls)}枚")
    return urls


# ============================================================
# テスト実行
# ============================================================

if __name__ == "__main__":
    import sys
    post_type = sys.argv[1] if len(sys.argv) > 1 else "VS"
    print(f"=== テスト: {post_type} ({len(CAROUSEL_CONTENT[post_type]['points'])+2}枚) ===")
    urls = generate_carousel(post_type)
    print("\n--- 生成URL一覧 ---")
    for i, url in enumerate(urls, 1):
        print(f"  スライド{i}: {url}")
