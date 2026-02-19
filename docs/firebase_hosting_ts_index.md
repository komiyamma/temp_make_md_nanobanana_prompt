# 公開：Hosting / App Hosting＋CI/CDでリリース体験🌍🚢（20章アウトライン）

**ゴール🏁**：Reactアプリを「PRプレビュー → 本番反映」まで回して、“世に出す”流れを身につける✨
（2026-02-17時点の公式情報を反映しています📚）

---

![Deployment Pipeline Goal](./picture/firebase_hosting_ts_index_01_goal.png)

## このカテゴリで作る完成イメージ🎯

* Reactアプリを **Firebase Hosting** に公開して、URLで見れる🌐
* **GitHubのPRごとにプレビューURL** が自動で生える🔁（レビューが爆速）([Firebase][1])
* マージで **本番（live）へ自動デプロイ** 🤖([Firebase][1])
* 必要に応じて **Firebase App Hosting** を使い、SSR/フルスタック（Next.js/Angular等）も運用できる🧩([Firebase][2])
* キャッシュ・HTTPS・カスタムドメインまで最低限おさえる🛡️([Firebase][3])
* AIもガッツリ活用：コンソールAI支援／AI Logic／Genkit／MCPで “詰まり” を潰す🤖🧯([Firebase][4])

---

![Service Ecosystem](./picture/firebase_hosting_ts_index_02_ecosystem.png)

## 使う主要サービス🧩

* Firebase Hosting（静的配信＋SPAに強い）⚡
* Firebase App Hosting（動的Web/SSRをまとめて面倒見てくれる）🚀([Firebase][2])
* GitHub Actions（PRプレビュー＆自動デプロイ）🤖([Firebase][1])
* Firebase AI Logic（Gemini/Imagenをアプリに安全に組み込み）🤖([Firebase][5])
* Genkit（AI処理を“流れ”として作る）🧰([The Firebase Blog][6])
* Gemini in Firebase（コンソール上で詰まりを相談）🧯([Firebase][4])
* Firebase MCP server（Antigravity/Gemini CLI からFirebaseを操作しやすく）🧩([Firebase][7])
* Firebase Studio（Nixで環境を再現しやすい）🧰([Firebase][8])

---

## ✅ 20章アウトライン（読む→手を動かす→ミニ課題→チェック）📚✨

![Static Hosting Concept](./picture/firebase_hosting_ts_index_03_part_a.png)

## Part A：まず “公開できた！” を作る🚀

### 第1章：公開って何？HostingとApp Hostingの使い分け🌍

* 学ぶ：静的SPAはHosting、SSR/フルスタック寄りはApp Hostingが基本線🧠([Firebase][2])
* 手を動かす：自分のアプリが「SPA/SSR」どっちか仕分けする🧩
* ミニ課題：「今回はHostingにする理由」を一言で✍️
* チェック：どっちを選ぶべきか説明できる✅

### 第2章：最短で土台づくり（プロジェクト＆初期化）🧱

* 学ぶ：Hostingは `firebase.json` を中心に動く📄([Firebase][9])
* 手を動かす：Hosting有効化→ローカルから初期デプロイまでの流れを把握👣
* ミニ課題：「publicディレクトリは何？」を説明✍️([Firebase][9])
* チェック：初期化の意味が腹落ち✅

### 第3章：ReactをHostingへ“手動”デプロイしてみる🚀

* 学ぶ：まずは手動で出して全体像をつかむ🗺️
* 手を動かす：ビルド→デプロイ→公開URL確認🌐
* ミニ課題：公開URLを自分用メモに残す📝
* チェック：自分の操作で公開が更新できる✅

### 第4章：`firebase.json` 超入門（出すもの／無視するもの）🧾

* 学ぶ：`public` と `ignore` の役割、順番・設定の基本📌([Firebase][9])
* 手を動かす：ビルド成果物フォルダに合わせて `public` を調整🔧([Firebase][9])
* ミニ課題：なぜ `node_modules` は無視する？を一言で✍️
* チェック：設定ファイルが怖くなくなる✅

### 第5章：SPAルーティング（リロードで404になる問題）🔁

* 学ぶ：rewrite/redirectの違いと優先順位🧠([Firebase][9])
* 手を動かす：SPA向けのrewritesを入れて、リロードでも画面が出るようにする🛠️
* ミニ課題：`/about` を直叩きして確認👀
* チェック：SPA公開でハマりやすい罠を回避✅

---

![CI/CD Robot](./picture/firebase_hosting_ts_index_04_part_b.png)

## Part B：CI/CDで “PRプレビュー→本番” を回す🤖🔁

### 第6章：Preview Channel入門（プレビューURLを作る）🔎

* 学ぶ：プレビューは“チャンネル”として作れて、期限も持てる⏳([Firebase][10])
* 手を動かす：プレビュー用チャンネルを作ってURLで確認🌐([Firebase][10])
* ミニ課題：チャンネル命名ルール案を作る（例：`pr-123`）🏷️
* チェック：プレビューの役割が言語化できる✅

### 第7章：GitHub連携（PRごとに自動プレビュー）🤝

* 学ぶ：PRごとにプレビューURL作成＆更新、PRコメントもできる🧠([Firebase][1])
* 手を動かす：公式手順でGitHub Actionsをセットアップ🛠️([Firebase][11])
* ミニ課題：PRを1本投げてプレビューURLが出るのを確認👀
* チェック：レビューがURLワンクリックになる✅

### 第8章：本番（live）自動デプロイ（マージで反映）🚢

* 学ぶ：プレビューと本番は“流れ”でセットにするのが強い🧠([Firebase][1])
* 手を動かす：main（またはmaster）マージでliveに自動デプロイ🤖
* ミニ課題：デプロイ前後で表示差分をスクショ比較📸
* チェック：PR→マージ→本番の一連が回る✅

### 第9章：CI/CDの秘密の箱（Secrets・権限・事故防止）🧰🔐

* 学ぶ：GitHub連携はサービスアカウント＆Secretsが要💡([Firebase][11])
* 手を動かす：Secretsがどこにあり、何を入れているか把握する🗝️
* ミニ課題：「漏れたらヤバいもの／別にOKなもの」を仕分け✍️
* チェック：鍵の扱いが怖くなくなる✅

### 第10章：失敗しても焦らない（ログの見方＆典型エラー）🧯

* 学ぶ：CIの失敗は“原因の場所”を切り分ければ勝ち🏆
* 手を動かす：Actionsログ→Hostingデプロイ結果→差分確認の順で追う🔎
* ミニ課題：わざと失敗（ビルド壊す等）→直して復帰🛠️
* チェック：トラブル対応の型ができる✅

---

![Quality Shield](./picture/firebase_hosting_ts_index_05_part_c.png)

## Part C：公開品質を上げる（HTTPS・キャッシュ・ドメイン）🌐🛡️

### 第11章：HTTPSとカスタムドメイン（“ちゃんとしたサイト感”）🔒

* 学ぶ：カスタムドメイン設定とSSL証明書の流れ（DNS→証明書）🧠([Firebase][12])
* 手を動かす：DNSレコードを理解し、設定手順をなぞる🧩([Firebase][12])
* ミニ課題：`www` と apex を揃える方針を決める🔁([Firebase][12])
* チェック：公開URLが“自分のドメイン”になる✅

### 第12章：キャッシュ基礎（速くするけど壊さない）⚡🧠

* 学ぶ：`Cache-Control` と `max-age/s-maxage` の考え方📌([Firebase][3])
* 手を動かす：静的ファイルのキャッシュ方針を決める🛠️
* ミニ課題：「どれを長期キャッシュして良い？」を3つ挙げる✍️
* チェック：更新したのに反映されない事故が減る✅

### 第13章：Hostingのルール整理（redirect/rewritesの設計）🗺️

* 学ぶ：ルールは“上から順”で効く（優先順位が命）🧠([Firebase][9])
* 手を動かす：`/old` → `/new` リダイレクトを入れて確認🔁
* ミニ課題：将来のURL設計メモを作る📝
* チェック：URL変更に強くなる✅

### 第14章：複数環境（staging/prod）を運用できる形にする🏗️

* 学ぶ：本番と検証を分けると、心が平和🕊️
* 手を動かす：Firebaseプロジェクト（またはHosting site/target）を環境で分ける方針を作る📌
* ミニ課題：ブランチ戦略（例：main=prod / develop=staging）を決める🌿
* チェック：うっかり本番デプロイを減らせる✅

---

![App Hosting Dynamic](./picture/firebase_hosting_ts_index_06_part_d.png)

## Part D：App Hostingで“動的Web”も運用する🧩🚀

### 第15章：App Hosting入門（何がラク？）✨

* 学ぶ：App Hostingは動的Webの開発・デプロイをまとめて簡略化、GitHub統合も強い🧠([Firebase][2])
* 手を動かす：HostingとApp Hostingの差を自分の言葉で整理📝
* ミニ課題：自分のアプリが「SSR必要？」を判定✍️
* チェック：選択ミスしにくくなる✅

### 第16章：App Hostingを動かす（GitHub接続〜初回デプロイ）🔌

* 学ぶ：App HostingはGitHub連携で継続デプロイしやすい🤖([Firebase][2])
* 手を動かす：App Hostingバックエンド作成→デプロイ確認👀
* ミニ課題：初回デプロイの手順をメモ化🧾
* チェック：SSR系でも“出せる”✅

### 第17章：`apphosting.yaml` で環境変数・VPCなどを扱う🧩

* 学ぶ：App Hostingは `apphosting.yaml` で設定を管理できる📄([Firebase][13])
* 手を動かす：環境変数の置き場所（ビルド時/実行時）を整理して設定🛠️([Firebase][13])
* ミニ課題：本番/検証で値が違う変数を3つ考える🔁
* チェック：設定がコードから分離できる✅

### 第18章：ロールアウト制御（勝手に出ないようにする）🧯

* 学ぶ：App Hostingは自動ロールアウトを止める/再開できる（状況で使い分け）🧠([The Firebase Blog][14])
* 手を動かす：自動デプロイON/OFFの判断基準を作る⚖️
* ミニ課題：「止めたいタイミング」を2つ挙げる✍️
* チェック：運用の安心感が増える✅

---

![AI Ops Team](./picture/firebase_hosting_ts_index_07_part_e.png)

## Part E：AIで“リリース体験”を実務っぽくする🤖🔥

### 第19章：サーバー処理の選択肢（Functions/Cloud Run）🧠⚙️

* 学ぶ：

  * Functions（Firebase側）はNode中心で選びやすい（Node 22/20、18は非推奨扱い）🟩([Firebase][15])
  * 画像処理や別言語が必要なら Cloud Run functions 側に逃がすのも手（.NET 8 / Python 3.13 などが“対応枠”）🐍🟦([Google Cloud Documentation][16])
* 手を動かす：どの処理をどこに置くか、ざっくり設計図を描く🗺️
* ミニ課題：「Hosting/App Hostingだけで足りない処理」を2つ挙げる✍️
* チェック：バックエンドの置き場で迷いにくくなる✅

### 第20章：AI合体（リリース手順書・自動チェック・最終完成）🏁✨

* 学ぶ：

  * **Firebase AI Logic** でGemini/Imagenを安全に呼べる（クライアント直でも/サーバー経由でも）🤖([Firebase][5])
  * **Genkit** で「リリース前チェック」みたいなフローを作って、作業を型にできる🧰([Firebase][17])
  * **Gemini in Firebase** でコンソール上の詰まりを相談して最短で直す🧯([Firebase][4])
  * **Firebase MCP server** を入れると、Antigravity/Gemini CLIからFirebase操作・調査がやりやすい🧩([Firebase][7])
  * **Firebase Studio** はNixで環境を固定できて学習が崩れにくい🧰([Firebase][8])
* 手を動かす：

  * “PRプレビュー→本番反映” の手順書（Runbook）をAIに下書きさせて、自分用に整える🧾🤖
  * PRテンプレに「確認項目（キャッシュ/ドメイン/動作）」を追加✅
* ミニ課題：手順書に「ロールバック方法」「緊急停止のやり方」を1行ずつ追加🧯
* チェック：もう“それっぽい運用”で出せる😎🚢

---

## 章の流れのイメージ（超ざっくり）🗺️

![Chapter Flow Map](./picture/firebase_hosting_ts_index_08_chapter_flow.png)


* **前半（1〜5）**：まず公開できる
* **中盤（6〜10）**：PRプレビュー＆自動デプロイでチーム開発っぽく
* **後半（11〜18）**：品質（ドメイン・HTTPS・キャッシュ）＋App Hosting運用
* **ラスト（19〜20）**：Functions/Cloud RunとAIで“実務モード”へ🔥

---

次は、この20章のうち **第1章から本文教材化**（読む→手を動かす→ミニ課題→チェックを“文章として”展開）していけます📚✨
どこから本文にする？（おすすめは **第6〜第8章**：PRプレビューが動くと一気に楽しくなるよ😆）

[1]: https://firebase.google.com/docs/hosting/github-integration?utm_source=chatgpt.com "Deploy to live & preview channels via GitHub pull requests"
[2]: https://firebase.google.com/docs/app-hosting?utm_source=chatgpt.com "Firebase App Hosting"
[3]: https://firebase.google.com/docs/hosting/manage-cache?utm_source=chatgpt.com "Manage cache behavior | Firebase Hosting"
[4]: https://firebase.google.com/docs/ai-assistance/gemini-in-firebase?utm_source=chatgpt.com "Gemini in Firebase - Google"
[5]: https://firebase.google.com/docs/ai-logic?utm_source=chatgpt.com "Gemini API using Firebase AI Logic - Google"
[6]: https://firebase.blog/posts/2024/05/introducing-genkit/?utm_source=chatgpt.com "Introducing Firebase Genkit"
[7]: https://firebase.google.com/docs/ai-assistance/mcp-server?utm_source=chatgpt.com "Firebase MCP server | Develop with AI assistance - Google"
[8]: https://firebase.google.com/docs/studio?utm_source=chatgpt.com "Firebase Studio - Google"
[9]: https://firebase.google.com/docs/hosting/full-config?utm_source=chatgpt.com "Configure Hosting behavior - Firebase"
[10]: https://firebase.google.com/docs/hosting/test-preview-deploy?utm_source=chatgpt.com "Test your web app locally, share changes with ... - Firebase"
[11]: https://firebase.google.com/docs/hosting/github-integration?hl=ja&utm_source=chatgpt.com "GitHub pull リクエストによるライブチャネルとプレビュー ..."
[12]: https://firebase.google.com/docs/hosting/custom-domain?utm_source=chatgpt.com "Connect a custom domain | Firebase Hosting - Google"
[13]: https://firebase.google.com/docs/app-hosting/configure?utm_source=chatgpt.com "Configure and manage App Hosting backends - Firebase"
[14]: https://firebase.blog/posts/2024/09/app-hosting-environments/?utm_source=chatgpt.com "Firebase App Hosting: Environments & deployment settings"
[15]: https://firebase.google.com/docs/functions/manage-functions?utm_source=chatgpt.com "Manage functions | Cloud Functions for Firebase - Google"
[16]: https://docs.cloud.google.com/functions/docs/release-notes?utm_source=chatgpt.com "Cloud Run functions (formerly known as Cloud Functions ..."
[17]: https://firebase.google.com/docs/functions/oncallgenkit?utm_source=chatgpt.com "Invoke Genkit flows from your App | Cloud Functions for Firebase"
