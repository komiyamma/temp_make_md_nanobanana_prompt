# 第01章：ゴールと完成イメージを固める 🗺️✨

この章は、**“作るもの”を先に1枚で決めて**、次章以降の実装で迷子にならないための準備です🙂
ここでやるのは **UIの完成形のイメージ固定** と **扱うデータ決め（Firestoreの下地）** だけ！🧱

---

## この章のゴール 🎯

* 管理画面っぽいアプリの完成イメージを、**3ページ以上**で説明できる📄✨
* 「一覧→詳細→保存」の流れを、**自分の言葉**で言える🗣️
* Firestoreで扱う予定のデータを **3つ（=コレクション3本）** 決める🗃️🗃️🗃️

---

## 1) まず“完成形”を脳内で固定する 🧠✨

管理画面UIは、だいたいこの“型”です👇

* **一覧**（テーブル）📋：たくさん並ぶ（検索・並び替え・ページングが乗る）
* **詳細**（フォーム）📝：1件を編集して保存
* **保存**（更新）💾：保存中・失敗・成功がちゃんと見える
* （後で）**画像**📷：Storageにアップ、URLを保存
* （後で）**AIボタン**🤖：文章を整形したり要約したり（安全に呼ぶ）

この型は、Firestoreに繋いだときもブレないので最強です💪🔥

![firebase_frontend_foundation_ts_study_001_01_standard_flow.png](./picture/firebase_frontend_foundation_ts_study_001_01_standard_flow.png)

---

## 2) 画面を“最低3ページ”に割る 🧭📄

この教材のチェックは「3ページ以上に割れてる？」でしたね✅
おすすめの3ページ構成はコレ👇（超王道で迷いません）

![firebase_frontend_foundation_ts_study_001_02_sitemap.png](./picture/firebase_frontend_foundation_ts_study_001_02_sitemap.png)

1. **/dashboard**：ダッシュボード（カードで概要）📊
2. **/items**：一覧（テーブル）📋
3. **/items/:id**：詳細（フォーム）📝

> 「設定ページ（/settings）」を追加すると、4ページになってさらに管理画面っぽくなります😆⚙️

---

## 3) 手を動かす：画面ラフを作る 🛠️🖊️

ここは凝らなくてOK！
紙でも、メモアプリでも、AntigravityのメモでもOKです🙂

**“それっぽい枠”**だけ先に描くと、実装が爆速になります🚀

![firebase_frontend_foundation_ts_study_001_03_wireframe.png](./picture/firebase_frontend_foundation_ts_study_001_03_wireframe.png)

```text
┌────────────────────────────────────────────┐
│  Header: タイトル / 検索 / ユーザー / ログアウト │  ← 上部バー
├───────────────┬────────────────────────────┤
│ Sidebar        │ Main                       │
│ - Dashboard    │  [KPIカード 3枚]           │
│ - Items        │  [一覧テーブル]            │
│ - Settings     │  [詳細フォーム]            │
│               │  [保存ボタン] [AI整形ボタン] │
└───────────────┴────────────────────────────┘
```

## ラフで決めるポイント（3つだけ）🧩

* **サイドバーのメニュー名**（3つ）📚
* **一覧テーブルの列**（3〜5列）📋
* **詳細フォームの入力項目**（3〜6項目）📝

---

## 4) ミニ課題：扱うデータ（コレクション）を3つ決める 🗃️🎯

ここが超大事です。
データが決まると「画面」「フォーム」「AIボタン」が一気に決まります🙂✨

## 迷ったらこの3パターンから選ぶ（おすすめ）🧠

![firebase_frontend_foundation_ts_study_001_04_data_patterns.png](./picture/firebase_frontend_foundation_ts_study_001_04_data_patterns.png)

## A. 記事管理（ブログCMS風）✍️

* `posts`（記事）
* `authors`（著者）
* `comments`（コメント）

## B. 問い合わせ/チケット管理（管理画面の王道）🎫✨

* `tickets`（問い合わせ）
* `customers`（顧客）
* `messages`（やり取り）

## C. 商品/在庫ミニ管理（業務っぽい）📦

* `items`（商品）
* `categories`（カテゴリ）
* `logs`（入出庫ログ）

> **AIを絡めやすいのはB（チケット管理）**です🤖✨
> 「問い合わせ文を丁寧語に整形」「要点だけ要約」「返信案の下書き」など、ボタン1発が自然に作れます🙂

---

## 5) “データ→画面”の対応を1枚にする 🧾✨（超重要）

次のテンプレを埋めてください。

![firebase_frontend_foundation_ts_study_001_05_data_ui_map.png](./picture/firebase_frontend_foundation_ts_study_001_05_data_ui_map.png)
これができたら、次章以降がスムーズすぎて感動します😆

```md
## ミニ仕様書（第1章の成果物）

## 1. アプリの名前（仮でOK）
- 例：Mini Support Dashboard

## 2. 3ページ構成
- /dashboard：何を表示する？（例：未対応件数、今日の件数…）
- /items（または /tickets）：一覧の列（例：タイトル、状態、更新日）
- /items/:id（または /tickets/:id）：詳細フォームの項目（例：タイトル、本文、状態）

## 3. コレクション3つ（Firestore想定）
- collection A：
  - 代表フィールド：例）title, status, updatedAt
- collection B：
  - 代表フィールド：例）name, email
- collection C：
  - 代表フィールド：例）ticketId, message, createdAt

## 4. AIボタン（第18章で実装する前提のネタ）
- ボタン名：
- 入力：
- AIにやらせること：
- 出力をどう扱う？（そのまま保存？確認して保存？）

## 5. 画像アップロード（第16章で実装する前提のネタ）
- 何の画像？（例：プロフィール画像、添付画像）
- どこに表示する？
```

---

## 6) AIを使って“仕様を一瞬で整える”🤖✨（おすすめ）

## Antigravityのエージェントに投げる例 🛸🧠

Antigravityは「エージェントを管理して計画→実装まで進める」思想の開発環境なので、**ラフ作りと相性がめちゃ良い**です🙂 ([Google Codelabs][1])

```text
あなたはプロダクトデザイナーです。
管理画面（ダッシュボード風）を作ります。

条件：
- 3ページ以上（dashboard / 一覧 / 詳細）
- 一覧はテーブル、詳細はフォーム
- 後でFirestoreと接続する
- 後でAIボタン（文章整形）と画像アップロードも入れる

やってほしいこと：
1) 画面構成（ページごとの目的）
2) 一覧テーブルの列案
3) 詳細フォーム項目案
4) Firestoreコレクション3つとフィールド案
を、初心者にも分かるように提案して
```

## Gemini CLIに投げるときのコツ 🧰🤖

Gemini CLIはターミナル内で動くAIエージェントで、ツール実行やMCP連携なども含めてタスクを進める前提です（`/tools` や `/mcp` みたいなコマンドもある）([Google Cloud Documentation][2])
なので「**テンプレ埋め**」みたいな作業を任せるのが楽です🙂

---

## 7) Firebase AIは“安全な呼び方”を先に意識する 🔐🤖

この教材では後でAIボタンを作りますが、考え方だけ先に👇

* ブラウザからAIを呼ぶなら、**Firebase AI Logic のクライアントSDK**が前提になる（JSもある）([Firebase][3])
* “キー直置きで叩く”みたいなのは事故りやすいのでやらない🙅‍♂️💥（この教材では安全側で組む）

![firebase_frontend_foundation_ts_study_001_06_safe_ai_call.png](./picture/firebase_frontend_foundation_ts_study_001_06_safe_ai_call.png)

---

## 8) チェック✅（1分でOK）

* [ ] ページが **3つ以上**ある？（/dashboard / 一覧 / 詳細）📄
* [ ] 一覧は **テーブル**、詳細は **フォーム**になってる？📋📝
* [ ] Firestore想定の **コレクションが3つ**決まった？🗃️
* [ ] AIボタンのネタが1つ決まった？（整形/要約/返信案など）🤖✨
* [ ] 「保存中/失敗/成功」を画面でどう見せるか、ちょっと想像できた？🔁✅❌

---

## 9) 参考：この教材で扱う“今のバージョン感”📌（ざっくり）

* React：npmの最新版として **19.2.4** が確認できます([npm][4])
* Tailwind：v4系の流れで、**v4.1 の公式記事**があります([tailwindcss.com][5])
* Node.js：**v24 が Active LTS**、v25 が Current です([Node.js][6])
* Functions（後の章）：Node.js **22 / 20（18はdeprecated）** の案内があります([Firebase][7])
* .NET（後の章）：**.NET 10 がLTS**としてサポート表に載っています([Microsoft][8])
* Python（後の章）：**Python 3.14.0（2025-10-07）** のリリースページがあります([Python.org][9])

---

## 次章へのつなぎ 🔥

第2章では、ここで決めた「3ページ構成」をそのまま土台にして、**雛形プロジェクトを作って起動**します⚡
なので次にやることはシンプル👇

1. さっきの「ミニ仕様書」を埋める🧾
2. ページ名（/dashboard / /items / /items/:id）を確定する🧭
3. 一覧の列とフォーム項目を確定する📋📝

もしよければ、あなたが選びたいアプリ案（A/B/C）を決め打ちして、**第1章のミニ仕様書をあなた用に“完成版”で埋めた例**もそのまま作りますよ🙂✨

[1]: https://codelabs.developers.google.com/getting-started-google-antigravity?utm_source=chatgpt.com "Getting Started with Google Antigravity"
[2]: https://docs.cloud.google.com/gemini/docs/codeassist/gemini-cli "Gemini CLI  |  Gemini for Google Cloud  |  Google Cloud Documentation"
[3]: https://firebase.google.com/docs/ai-logic?utm_source=chatgpt.com "Gemini API using Firebase AI Logic - Google"
[4]: https://www.npmjs.com/package/react?activeTab=versions&utm_source=chatgpt.com "react"
[5]: https://tailwindcss.com/blog/tailwindcss-v4-1?utm_source=chatgpt.com "Tailwind CSS v4.1: Text shadows, masks, and tons more"
[6]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
[7]: https://firebase.google.com/docs/functions/manage-functions?utm_source=chatgpt.com "Manage functions | Cloud Functions for Firebase - Google"
[8]: https://dotnet.microsoft.com/en-us/platform/support/policy?utm_source=chatgpt.com "The official .NET support policy | .NET"
[9]: https://www.python.org/downloads/release/python-3140/?utm_source=chatgpt.com "Python Release Python 3.14.0"
