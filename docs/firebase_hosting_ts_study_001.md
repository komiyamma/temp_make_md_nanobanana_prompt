# 第01章：公開って何？HostingとApp Hostingの使い分け🌍

## この章でできるようになること🎯

* 「公開＝URLで見れる状態にする」って何が起きてるか、ざっくり説明できる📣
* 自分のアプリが **Hosting向き** か **App Hosting向き** か判断できる✅
* その判断を、AI（Gemini / Antigravity / Gemini CLI）にも“根拠付き”で手伝わせられる🤖🧠

---

## 1) そもそも「公開」って何？🌐

![Public Hosting Concept](./picture/firebase_hosting_ts_study_001_01_public_concept.png)

超ざっくり言うと👇

* あなたのアプリ（HTML / CSS / JavaScript / 画像など）を **世界中から取りに来れる場所に置く**
* みんながブラウザでアクセスすると、**速く・安全に** 届くようにする（CDN / HTTPS / キャッシュ）⚡🔒
* 更新したら「新しい版」に差し替える（デプロイ）🔁

**Firebase Hosting** は、コマンド1発で **グローバルCDNに配信**して、**SSLも自動**で、速く安全に公開できるのが売りです⚡🔒([Firebase][1])

---

## 2) まず結論：迷ったらこの基準でOK🧭

## ✅ Hosting が向いてる（基本、ReactのSPAはこっち）⚡

![Hosting for SPA](./picture/firebase_hosting_ts_study_001_02_hosting_use_case.png)

* いわゆる **SPA（シングルページアプリ）**：Vite + React Router みたいなやつ🧩
* ビルドすると **静的ファイル（HTML/CSS/JS）がフォルダに出る**
* 公開後も、基本は「ファイルを配る」だけで成立する📦

Firebase Hosting は **静的・SPAに最適化**されていて、ルーティングのrewriteやヘッダー設定なども柔軟です🧠([Firebase][1])

---

## ✅ App Hosting が向いてる（SSR/フルスタック寄り）🚀

![App Hosting for SSR](./picture/firebase_hosting_ts_study_001_03_app_hosting_use_case.png)

* **SSR（サーバーサイドレンダリング）**が必要（アクセスのたびにHTMLをサーバーで組み立てる）🧠
* Next.js / Angular で “フルスタック” をやりたい（サーバー処理も同居）🧩
* GitHub連携や運用も “最初から一体化” した形で持ちたい🤝

App Hosting は **Angular / Next.js 向けに本番利用（GA）**として提供されています✅([The Firebase Blog][2])
しかも、App Hosting で動くNodeアプリは **Cloud Run上で動く**前提で、**Node.js 20 以上**がサポート範囲です🟩([Firebase][3])

---

## 3) Hosting と App Hosting を「一枚で」比較🧾✨

![Hosting vs App Hosting](./picture/firebase_hosting_ts_study_001_04_comparison.png)

| ざっくり観点      | Hosting ⚡                          | App Hosting 🚀                 |
| ----------- | ---------------------------------- | ------------------------------ |
| 得意          | 静的サイト / SPA                        | SSR / フルスタック（Next.js/Angular等） |
| 配信          | CDNでファイル配信が中心                      | CDN + サーバー実行（Cloud Runベース）     |
| “サーバーで動く処理” | 基本は別枠（Functions/Cloud Runなどと組み合わせ） | まとめて面倒見やすい                     |
| 学習の最初の一歩    | とにかく最短で公開できる🧨                     | SSR前提ならむしろ近道🏎️                |

補足：Firebase Hosting でも動的要素は **Functions / Cloud Run と組み合わせ**て作れます（ただし章が進んでからが楽）🧩([Firebase][1])

---

## 4) 仕分けの超シンプル診断（これだけで8割当たる）🎯

![Selection Flowchart](./picture/firebase_hosting_ts_study_001_05_decision_tree.png)

## Q1：ビルドした成果物は「ただのファイル」？📦

* **Yes** → Hosting でOKな確率高い✅
* **No / よく分からない** → 次へ➡️

## Q2：アクセスごとにサーバーでHTML作る（SSR）必要？🧠

* **Yes** → App Hosting（まずこれ）🚀
* **No** → Hosting でOK⚡

## Q3：今のコードに「サーバー側の入口」がある？🚪

目印の例👇（見つかったらSSR/サーバー寄りの匂い）

* Next.js の SSRっぽい仕組み（サーバーで動くロジックがある）
* APIルートやサーバー処理が同居している
* “実行時にサーバーが必要” な機能が前提

さらに現実的な注意：Firebase Hosting の “フレームワーク統合（Next.js等）” はプレビュー扱いで、フルスタックなら **App Hosting推奨**と明記されています🧩([Firebase][4])

---

## 5) 「コスト/課金」の超入門（怖がらない版）💰😌

![Hosting Cost](./picture/firebase_hosting_ts_study_001_08_cost.png)


* Hosting は無料枠もあり、まず公開して試すには十分な範囲があります🧪
  例：Hosting の無料枠に **ストレージ10GB、転送量360MB/日** などが載っています📦([Firebase][5])
* SSRやサーバー処理が絡むと、課金設定が必要になる場面が増えます（特にSSR）🧾
  公式の“HostingでSSRする系”の案内でも、SSRするなら課金が必要になり得る趣旨が書かれています🧠([Firebase][6])

この章では「怖いからやめる」じゃなくて、**“どっちを選ぶと課金や運用が自然か”** の判断材料にします😎👍

---

## 6) AIで「仕分け」を爆速にする🤖⚡（ここが2026っぽい）

![AI Decision Helper](./picture/firebase_hosting_ts_study_001_06_ai_helper.png)

## 6-1) Gemini in Firebase で相談する🧯

Firebaseコンソールの中で、詰まりを自然言語で聞ける枠が用意されています🗨️✨([Firebase][7])

おすすめの聞き方（コピペOK）👇

* 「このアプリはReactのSPAです。HostingとApp Hostingどっちが自然？理由も3つ」
* 「SSRが必要になる条件を、初心者向けに例で説明して」
* 「PRごとにプレビューURLを出す前提で、最初に選ぶべき公開方式は？」

## 6-2) Antigravity / Gemini CLI で“リポジトリを見せて”判断させる🕵️‍♂️

Firebaseの **MCP server** を使うと、AI開発ツール（Antigravity / Gemini CLI など）からFirebase操作や調査がしやすくなります🧩([Firebase][8])

さらに Gemini CLI には **Firebase拡張**もあり、入れるとMCP serverや文脈ファイル込みで効きやすい、という流れが案内されています🧠([Firebase][8])

**おすすめ依頼テンプレ（Gemini CLI / Antigravityどっちでも）**👇

* 「このリポジトリを見て、SPAかSSRか判定して。根拠ファイル名も挙げて」
* 「Hostingで出す場合に必要な設定（rewrite等）が出そうか、先にチェックして」
* 「App Hostingを選ぶなら、Nodeの要件（20+など）に当たってるか確認して」([Firebase][3])

---

## 7) 手を動かす🛠️：自分のアプリを“仕分け”してみよう

![Build Folder Check](./picture/firebase_hosting_ts_study_001_07_build_check.png)

ここは **今あるReactアプリ**（または作成予定のサンプル）を対象にやります📁✨

## Step 1：自分のアプリを一言で説明してみる✍️

例：

* 「ReactのSPA。ログインあり。SSRはいらない」
* 「Next.jsでSEO重視。記事ページはSSRしたい」

## Step 2：ビルド結果が“ファイルの塊”か見る👀

Windowsでプロジェクトフォルダを開いて、ビルドして成果物フォルダができるか確認します。
（フォルダ名はツールで違うけど、**“成果物フォルダが出る”**ならSPA寄りの可能性大📦）

コマンド例（必要なら）👇

```text
npm run build
```

※ ここで「成果物フォルダができた」「静的ファイルが並ぶ」が見えれば、かなりHosting寄りです⚡

## Step 3：SSRが必要か、要件でチェック✅

* SEOで「初回HTMLが重要」？（ニュース/ブログ/商品一覧など）📰
* ログイン後のアプリ中心で、検索に載せる必要ほぼない？🔐
* “アクセスのたびにサーバー計算が必要” な画面が多い？🧮

ここまでで、**選ぶべき土台**がほぼ決まります😎

---

## 8) ミニ課題🎒：「今回はHostingにする理由」を一言で！

![Assignment Note](./picture/firebase_hosting_ts_study_001_09_assignment.png)


例👇

* 「ReactのSPAで、ビルド成果物をCDN配信できるから」⚡
* 「SSRが必要で、Next.jsを本番で安心運用したいから」🚀

---

## 9) チェック✅（合格ライン）

![Final Check](./picture/firebase_hosting_ts_study_001_10_check.png)


* 「Hostingは何が得意？」を一言で言える⚡
* 「App Hostingが向くのはどんな時？」を一言で言える🚀
* 自分のアプリを **Hosting / App Hosting** どっちにするか、理由つきで決められる🧠

---

## 10) 次章へのつなぎ🔗

第2章では、選んだ土台（主にHosting側）を最短で初期化して、**“公開の土台”**を作ります🧱✨
（ここまでの仕分けが正しいほど、次からの作業がスムーズになります😆）

必要なら、あなたの現在の構成（Reactの種類：Vite？Next.js？）を想定して、**「このパターンなら第1章の結論はこう」**って具体例も3パターン作って続けますよ📚🔥

[1]: https://firebase.google.com/docs/hosting "Firebase Hosting"
[2]: https://firebase.blog/posts/2025/04/apphosting-general-availability/ "Deploy Angular & Next.js apps with App Hosting, now GA!"
[3]: https://firebase.google.com/docs/app-hosting/frameworks-tooling "Frameworks and tooling for App Hosting  |  Firebase App Hosting"
[4]: https://firebase.google.com/docs/hosting/frameworks/nextjs "Integrate Next.js  |  Firebase Hosting"
[5]: https://firebase.google.com/pricing "Firebase Pricing"
[6]: https://firebase.google.com/docs/hosting/frameworks/frameworks-overview "Integrate web frameworks with Hosting  |  Firebase Hosting"
[7]: https://firebase.google.com/docs/ai-assistance/gemini-in-firebase/set-up-gemini?utm_source=chatgpt.com "Set up Gemini in Firebase - Google"
[8]: https://firebase.google.com/docs/ai-assistance/mcp-server "Firebase MCP server  |  Develop with AI assistance"
