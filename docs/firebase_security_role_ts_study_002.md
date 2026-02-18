# 第2章：Firestoreのアクセス経路を整理（Rulesが効く/効かない）🧭🛡️

この章はひとことで言うと…👇
**「Rulesが守ってくれる“入口”と、守ってくれない“裏口”を見分けられるようになる」** 回です😎✨
ここが曖昧だと、がんばってRules書いても「え、守れてないじゃん😱」が起きます。

---

## 1) まず結論：Rulesが効くのは “クライアント経路” 🧑‍💻✅

**Firestore Security Rulesは、主にWeb/モバイルなどのクライアントSDKからのアクセスを判定する「門番🚪」**です。

でも…
**サーバー向けライブラリ（server client libraries / Admin SDK的なやつ）はRulesをバイパスします**⚠️
その場合は **Google Cloud側の認証（ADC）＋ IAM** で守ります。([Firebase][1])

---

## 2) 入口の地図🗺️：Firestoreへ行く“3つの道”🚦

イメージはこれ👇（この図を頭に入れるだけで事故が激減します🧯）

* **A: クライアントの道（Rulesが効く）✅**
  React（Web）/ iOS / Android など → Firebase SDK → Firestore
  → **Rulesで「通す/通さない」**が決まる🛡️

* **B: サーバーの道（Rulesが効かない）❌**
  Cloud Functions / Cloud Run / 自前サーバー → **サーバー用ライブラリ** → Firestore
  → **Rulesはスキップ**、代わりに **IAM** が守る🧱([Firebase][1])

* **C: REST / RPC APIの道（Rulesが効かない扱いで考える）❌**
  サービスアカウント等でREST/RPC → Firestore
  → **IAMを必ず設計**（ここもRules前提で考えると危険）([Firebase][1])

---

## 3) ここが超大事💥：「同じ“読む/書く”でも意味が違う」🧠

## クライアントの「読む/書く」📲

* ユーザーの端末は信用できない前提（改造できる😈）
* だから **Rulesで最小権限**にする（守りの中心🛡️）

## サーバーの「読む/書く」🖥️

* サーバーは「信頼できる実行環境」前提（でも流出すると終わる😱）
* だから守り方が別物👇

  * サービスアカウント（権限）＝ **IAMで絞る**🔐
  * 受け取ったユーザーIDトークン等＝ **サーバー側で検証**✅
  * 「管理者だけOK」な処理＝ **サーバーに寄せる**👑

---

## 4) ひと目で分かる表📋✨（これが“事故防止の答え”）

| 経路         | 例                      | 何で認証してる？            | Rules | 代わりに必要な守り                 |
| ---------- | ---------------------- | ------------------- | ----- | ------------------------- |
| クライアントSDK  | ReactからFirestore直読み    | Firebase Auth（ユーザー） | ✅効く   | Rules（最小権限）＋App Check（後で） |
| サーバー用ライブラリ | Functions/Runで集計して書き込み | ADC/サービスアカウント       | ❌効かない | IAM（権限最小）＋サーバー検証          |
| REST/RPC   | バッチ・別システム連携            | OAuth/サービスアカウント     | ❌効かない | IAM（権限最小）＋監査ログ等           |

> 「サーバー用ライブラリはRulesをバイパス」「REST/RPCはIAMを設定してね」って公式が明言してます。([Firebase][1])

---

## 5) 手を動かす🧑‍💻✨：あなたのアプリの“アクセス経路マップ”を作る

ここはコードより **整理が勝ち** です✍️😊
次のテンプレをコピって、あなたのアプリを当てはめて埋めてください👇

* 画面A：〇〇一覧を見る

  * Firestoreアクセス：**クライアント** / **サーバー** どっち？
  * 誰の権限：未ログイン / 一般 / 管理者
  * 守り：Rulesで？ IAMで？ 両方？

* 画面B：投稿する

  * Firestoreアクセス：クライアント or サーバー
  * 「危ない項目」（例：role/isAdmin/priceなど）を書けない設計になってる？🧨

* 管理画面：ユーザーBAN、全件CSV、集計など

  * Firestoreアクセス：ほぼ確実に **サーバー**（推奨）👑
  * 守り：IAM最小＋サーバー検証（Rulesじゃない！）🛡️

---

## 6) ミニ課題🎯：サーバー側でやる処理を1つ決める（10分）⏱️

次のどれか1つでOK！👇（迷ったら①が鉄板😋）

1. **管理者だけが使う「全件集計」**（例：日別PV、投稿数）📊
2. **危ない更新**（例：課金状態、権限フラグ）💳
3. **AI実行**（例：文章要約、分類、モデレーション）🤖

**理由：AI系は特に「キーや権限」をクライアントに置くと事故りやすい**ので、サーバーに寄せるのが安全側です🔐✨

---

## 7) AIで爆速チェック🤖💨（Gemini CLI / Antigravity活用）

## 7-1. “アクセス経路の棚卸し”をAIにやらせる🧹

**Gemini CLIのFirebase拡張**は、ソースコードを見て **Firestoreのスキーマやアクセスパターンを推定しつつ、最小権限でRulesとテスト案を作る**方向の仕組みが用意されています。([Firebase][2])
（ただし、AI生成は**必ず人間レビュー**ね🧑‍⚖️✅）

使い方（イメージ）👇

* 「このリポジトリのFirestoreアクセス箇所を全部洗い出して、
  **Rulesで守れるアクセス / 守れないアクセス（サーバー/IAM）** に分類して」
* 「管理画面っぽい処理を検出して、**サーバー寄せ候補**を提案して」
* 「“listが危ない”箇所がないか攻撃者目線でレビューして」😈🛡️

## 7-2. Gemini CLIって何者？🧰

Gemini CLIは「ターミナルで動くAIエージェント」で、MCPサーバー等の仕組みも扱える、という位置付けの教材が出ています。([Google Codelabs][3])
なので「プロジェクトの状態を見ながら相談→修正案→テスト案」みたいな流れが作りやすいです😊✨

---

## 8) この章の“落とし穴あるある”😂💥（先に踏んでおこう）

* 「Rules書いたから、サーバーも守られてるよね？」→ **NO**🙅‍♂️
  サーバー用ライブラリはRulesをバイパスします([Firebase][1])
* 「管理画面をフロントで隠したからOK」→ **NO**🙅‍♀️
  UIは飾り！守りは **Rules/IAM/検証** でやる🛡️
* 「REST叩くからRulesで…」→ **IAMを前提に設計**🧱([Firebase][1])

---

## 9) バージョン目安メモ🧾✨（この章の範囲で必要なぶんだけ）

* Cloud Functions（Node.jsランタイム）
  **Node.js 20 / 22 をフルサポート**、Node.js 18は早期にdeprecated扱いになっています。([Firebase][4])
* Admin SDK（サーバーでロール付与や管理処理をやる側）

  * Python：**3.10+推奨**（3.9はdeprecated）([Firebase][5])
  * .NET：**.NET 8+推奨**（6/7はdeprecated）([Firebase][6])
  * Node.js：Admin SDKの前提として **Node 18+** が示されています([Firebase][7])（ただしFunctionsは20/22に寄せるのが安心）

---

## 10) チェック✅（3分でセルフ採点）

* [ ] 自分のアプリのFirestoreアクセスを **クライアント/サーバー/REST** に分類できた
* [ ] 「Rulesが効く範囲」と「効かない範囲」を説明できる
* [ ] 管理者処理は **サーバー寄せ＋IAM** が基本、と腹落ちした
* [ ] “同じread/writeでも意味が違う”が分かった
* [ ] AI機能は **サーバーで実行** する方が安全、がイメージできた🤖🔐

---

次の第3章では、この知識を土台にして **Rulesを「ローカルで管理→安全にデプロイ」**する流れに入ります🧰✨（Console直編集の事故も防げます🧯）

[1]: https://firebase.google.com/docs/firestore/security/get-started?utm_source=chatgpt.com "Get started with Cloud Firestore Security Rules - Firebase"
[2]: https://firebase.google.com/docs/ai-assistance/prompt-catalog/write-security-rules?utm_source=chatgpt.com "AI Prompt: Write Firebase Security Rules"
[3]: https://codelabs.developers.google.com/gemini-cli-hands-on?utm_source=chatgpt.com "Hands-on with Gemini CLI"
[4]: https://firebase.google.com/docs/functions/get-started?utm_source=chatgpt.com "Get started: write, test, and deploy your first functions - Firebase"
[5]: https://firebase.google.com/support/release-notes/admin/python?utm_source=chatgpt.com "Firebase Admin Python SDK Release Notes - Google"
[6]: https://firebase.google.com/support/release-notes/admin/dotnet?utm_source=chatgpt.com "Firebase Admin .NET SDK Release Notes"
[7]: https://firebase.google.com/docs/admin/setup?utm_source=chatgpt.com "Add the Firebase Admin SDK to your server - Google"
