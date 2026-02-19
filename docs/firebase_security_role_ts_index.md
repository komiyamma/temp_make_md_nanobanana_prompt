# セキュリティ：Rulesでロール制御（守りの中心）🛡️🔥 21章アウトライン教材

このパートのゴールはシンプルです👇
**「うっかり公開😱」を“仕組み”で潰して、安心して開発できる状態にする**ことです✅✨

---

## まず全体像（この21章でできるようになること）🗺️

* Firestore Security Rules を「APIの門番🚪」として理解する
* **一般ユーザー / 管理者**をキレイに分離して守る👮‍♂️👩‍💻
* **最小権限（読める/書ける）**を設計できる🔐
* **入力検証（必須・型・文字数など）**をRulesでやれる🧠
* Emulatorで **ルールをテストしてから**安全に出す🧪🧯 ([Firebase][1])
* AI（Gemini CLI / Antigravity など）で **ルール＆テスト作成を加速**しつつ、人間レビューで堅くする🤖🧑‍⚖️ ([Firebase][2])

---

## 20章構成（各章 10〜20分想定）📚⏱️

> 各章は「読む→手を動かす→ミニ課題→チェック」で進みます🙂✨
> （章タイトルだけじゃなく、**中身のアウトライン**も入れてあります！）

---

## 第1章：なぜRulesが必要？「公開しちゃった😱」事故の構造を知る💥

![Rules as Gatekeeper

**Labels to Render**:
- User: "Request"
- Gate: "Security Rules 🛡️"
- Castle: "Firestore 🏰"
- Action: "Allow / Deny"

**Visual Details**:
1. Core Concept: Rules acting as the entry guard.
2. Metaphor: A medieval castle gate with a guard checking a scroll (Request).
3. Action: Guarding.
4. Layout: Gatekeeper scene.](./picture/firebase_security_role_ts_index_01_rules_concept.png)


* 読む📖：DBは“置き場”で、Rulesは“入口の審査”🚪
* 手を動かす🧑‍💻：わざと危ないルール例を見て「何がヤバいか」言語化
* ミニ課題🎯：「このルールだと誰が何できちゃう？」を3つ書く
* チェック✅：事故パターンを“説明できる”状態になった？

---

## 第2章：Firestoreのアクセス経路を整理（Rulesが効く/効かない）🧭

![Access Path Logic

**Labels to Render**:
- Client: "Rules Apply ✅"
- Server: "Rules Bypass ⚠️"
- Admin SDK: "God Mode 👑"

**Visual Details**:
1. Core Concept: Different rules for different paths.
2. Metaphor: A secure front door (Client) vs a VIP back entrance (Server).
3. Action: Entering.
4. Layout: Comparison.](./picture/firebase_security_role_ts_index_02_access_path.png)


* 読む📖：Web/モバイルSDKのリクエストはRulesで判定される
* 注意⚠️：**サーバー用ライブラリ（Admin/Server SDK等）はRulesをバイパス**する（別でIAM等が必要） ([Firebase][3])
* 手を動かす🧑‍💻：同じ“読む/書く”でも「クライアント」と「サーバー」で意味が違う図を作る
* ミニ課題🎯：自分のアプリで「サーバー側でやる処理」を1つ決める
* チェック✅：Rulesが守る範囲を間違えてない？

---

## 第3章：Rulesの管理とデプロイの基本（Console vs CLI）🧰

![Rules Deployment Flow

**Labels to Render**:
- Local: "firestore.rules 📄"
- Tool: "Firebase CLI ⚙️"
- Cloud: "Deploy (Overwrite) ☁️"
- Console: "Old Rules 🗑️"

**Visual Details**:
1. Core Concept: Local file overwriting cloud settings.
2. Metaphor: Uploading a new blueprint that replaces the old one instantly.
3. Action: Overwriting.
4. Layout: Left-to-right flow.](./picture/firebase_security_role_ts_index_03_deployment_flow.png)


* 読む📖：Rulesは「ローカルで管理→デプロイ」が安全
* 超重要⚠️：CLIデプロイは **Consoleの既存ルールを上書き**する（運用事故ポイント） ([Firebase][4])
* 手を動かす🧑‍💻：ルールをファイル管理する場所と流れを整理
* ミニ課題🎯：「編集はローカルが正」ルール運用メモを作る
* チェック✅：チームでも事故りにくい運用になってる？

---

## 第4章：Rules言語の基本①（match / allow の読み方）🧩

* 読む📖：matchが対象、allowが許可条件🙂
* 手を動かす🧑‍💻：最小のルールを書いて“拒否される感覚”を体験
* ミニ課題🎯：コレクション1つに「読みだけOK」を付ける
* チェック✅：allow の条件式が読める？

---

## 第5章：Rules言語の基本②（request / resource / 変更差分）🔍

* 読む📖：request（リクエスト内容）と resource（既存データ）
* 手を動かす🧑‍💻：「create / update / delete」で見える情報が変わるのを確認
* ミニ課題🎯：更新時だけ禁止するルールを1つ作る
* チェック✅：createとupdateを混ぜて事故らない？

---

## 第6章：認証チェックの基本（ログインしてない人を入れない）🔐

* 読む📖：「ログイン済み」の判定はここから
* 手を動かす🧑‍💻：特定コレクションを「ログイン必須」にする
* ミニ課題🎯：未ログイン時の画面UXも一言で決める🙂
* チェック✅：未ログインが1文字も読めない状態？

---

## 第7章：ユーザー別データ設計（uid基準の王道）👤📁

![User Data Isolation

**Labels to Render**:
- User A: "See A Only 👀"
- User B: "See B Only 👀"
- Pattern: "users/{uid}"

**Visual Details**:
1. Core Concept: Each user can only access their own data.
2. Metaphor: Private lockers. User A's key only opens Locker A. Locker B is locked.
3. Action: Isolating.
4. Layout: Side-by-side lockers.](./picture/firebase_security_role_ts_index_04_user_isolation.png)


* 読む📖：王道は「users/{uid}/…」構造
* 手を動かす🧑‍💻：自分専用ドキュメントだけ読める/書けるルール
* ミニ課題🎯：プロフィールを「本人だけ更新OK」にする
* チェック✅：他人のuidを指定しても弾ける？

---

## 第8章：最小権限① “読む”の制御（get と list の感覚）📖🔒

* 読む📖：「1件取得(get)」と「一覧(list)」は別物
* 手を動かす🧑‍💻：getだけ許可 / listは禁止 を作って違いを体感
* ミニ課題🎯：公開記事はlist OK、下書きはNG みたいな設計を考える
* チェック✅：一覧が“全部ダダ漏れ”になってない？

---

## 第9章：最小権限② “書く”の制御（create/update/deleteを分ける）✍️🧯

![Granular Write Control

**Labels to Render**:
- Create: "Allow ✅"
- Update: "Deny 🚫"
- Delete: "Admin Only 👑"

**Visual Details**:
1. Core Concept: Splitting write permissions.
2. Metaphor: A control panel with separate switches for 'Create', 'Update', and 'Delete'.
3. Action: Controlling.
4. Layout: Control panel.](./picture/firebase_security_role_ts_index_05_write_control.png)


* 読む📖：書き込みは危険度が高いので分解がコツ
* 手を動かす🧑‍💻：createだけOK / updateは禁止 などを作る
* ミニ課題🎯：「削除だけは管理者のみ」ルールにする
* チェック✅：一般ユーザーが消せない？

---

## 第10章：入力検証① 必須フィールドと型（まず事故を止める）🧠🧱

* 読む📖：Rulesでも「必須」「型っぽい検証」ができる
* 手を動かす🧑‍💻：必須項目が欠けたら拒否、を入れる
* ミニ課題🎯：タイトル必須＋空文字NG
* チェック✅：変な形のデータを弾ける？

---

## 第11章：入力検証② 文字数・パターン（ユーザー入力の地雷💣）🔤

![Input Validation

**Labels to Render**:
- Input: "Title (Empty)"
- Rule: "title.size() > 0"
- Result: "Reject 🛑"

**Visual Details**:
1. Core Concept: Validating data before saving.
2. Metaphor: A shape sorter. A square block (Bad Data) trying to fit in a round hole (Rule). It doesn't fit.
3. Action: Rejecting.
4. Layout: Input check.](./picture/firebase_security_role_ts_index_06_input_validation.png)


* 読む📖：長すぎ・短すぎ・怪しい文字列への備え
* 手を動かす🧑‍💻：文字数上限をRulesで固定
* ミニ課題🎯：表示名「1〜20文字」にする
* チェック✅：想定外の長文を弾ける？

---

## 第12章：入力検証③ “書いていい項目だけ許す”（権限昇格を防ぐ）🛡️

* 読む📖：いちばん大事！「role」みたいな危険フィールドは書かせない
* 手を動かす🧑‍💻：許可キー以外が来たら拒否する
* ミニ課題🎯：「isAdmin」的な項目を一般ユーザーが書けないように
* チェック✅：クライアント改造されても大丈夫？

---

## 第13章：Rules関数化（読みやすさ＝安全性）🧩✨

* 読む📖：同じ条件のコピペは事故のもと😵
* 手を動かす🧑‍💻：共通関数（isSignedIn / isOwner など）を作る
* ミニ課題🎯：owner判定を関数にして3箇所で使う
* チェック✅：あとで読んでも怖くない？

---

## 第14章：ロール設計の基本（管理者/一般ユーザーをどう分ける？）👮‍♂️👩‍💻

* 読む📖：ロールは「増やしすぎない」「意味を固定」
* 手を動かす🧑‍💻：role設計表（admin/editor/user）を作る
* ミニ課題🎯：管理画面の操作を「3分類」してみる
* チェック✅：ロールの責務が説明できる？

---

## 第15章：Custom Claims入門（ロールを“トークンに埋める”）🎫🔐

* 読む📖：カスタムクレームは **IDトークン経由で扱う** ([Firebase][5])
* 手を動かす🧑‍💻：管理者にだけ「admin=true」を付ける流れを理解
* ミニ課題🎯：付与後に「トークン更新が必要」な点をメモ📝
* チェック✅：「UIで隠す」だけに頼らない意識になってる？

---

## 第16章：Custom Claims × RulesでRBAC（王道パターン）👑🛡️

* 読む📖：Rules内で「request.auth.token」の情報を使って分岐
* 手を動かす🧑‍💻：adminだけ読めるコレクションを作る
* ミニ課題🎯：一般ユーザーは「自分の分だけ」、adminは「全部」
* チェック✅：ロールで読める世界がちゃんと分かれてる？

---

## 第17章：Firestore内ロール管理パターン（やるなら注意点もセット）⚠️📦

* 読む📖：rolesドキュメント参照は便利だけど、設計ミスると危ない
* 手を動かす🧑‍💻：「role docはadminのみ書ける」制約を入れる
* ミニ課題🎯：roleの保存場所を「どこが一番安全か」比較
* チェック✅：権限データをユーザーが書けない？

---

## 第18章：よくある事故パターン集（教材で先に踏む😂💥）

* 事故例💥

  * allow read, write を雑に許可
  * list を許して丸見え
  * ルール関数のコピペ地獄
  * 「サーバー側はRules関係ない」誤解 ([Firebase][3])
* 手を動かす🧑‍💻：事故ルールを“安全ルールに直す”
* ミニ課題🎯：事故を1個選んで「再発防止メモ」作る
* チェック✅：事故を見つけたら即ツッコめる？

---

## 第19章：テストが本体！EmulatorでRules単体テスト🧪🧯

![Emulator Testing

**Labels to Render**:
- Test 1: "Admin (Pass) ✅"
- Test 2: "User (Pass) ✅"
- Test 3: "Guest (Fail) 🛑"
- Tool: "Emulator 🧪"

**Visual Details**:
1. Core Concept: Testing different scenarios locally.
2. Metaphor: A crash test dummy running through three different walls.
3. Action: Testing.
4. Layout: Three tracks.](./picture/firebase_security_role_ts_index_07_emulator_testing.png)


* 読む📖：Emulator SuiteでRulesをローカル検証できる ([Firebase][1])
* 手を動かす🧑‍💻：

  * 「通るべきテスト✅」と「弾くべきテスト❌」を作る
  * v9のテストライブラリ推奨の流れを確認 ([Firebase][1])
* ミニ課題🎯：admin/user/未ログインの3者テストを作る
* チェック✅：デプロイ前に“自信”が持てる？

---

## 第20章：AIでRules作成を加速（でも必ず人間レビュー）🤖✅

* 読む📖：

  * Gemini CLI のFirebase拡張で **Rules＋テストの叩き台**を作れる（自動更新ではない） ([Firebase][2])
  * GitHubの拡張（生成＋テスト）もあるが、**AI生成は信用せず必ずレビュー** ([GitHub][6])
  * Antigravity＋Firebase MCPで、プロジェクト状態を見ながら設計・修正の相談がしやすい ([The Firebase Blog][7])
* 手を動かす🧑‍💻：AIに「やらせる範囲」と「人が決める範囲」を線引き
* ミニ課題🎯：AIが作ったRulesに「レビュー観点チェックリスト」を当てる📝
* チェック✅：AIを使っても安全性が下がらない運用になった？

---

## 第21章：ミニ総合課題（このカテゴリの完成品）🧑‍💼✨

**「管理画面だけ見えるコレクション」を作る**（例：adminOnlyLogs / adminNotes など）

* 一般ユーザー：存在すら見えない🙈
* 管理者：読み書きOK👑
* Emulatorテスト：3者（admin/user/未ログイン）で全部確認🧪
* デプロイ：ローカル管理→CLIで反映（上書き注意）🧯 ([Firebase][4])

---

## 2026年2月時点の“バージョン目安”メモ（アウトライン内で使う）🧾✨

* Functions（Node.jsランタイム）

  * **Node.js 20 / 22 がサポート**、18はdeprecated扱い ([Firebase][8])
* Admin SDK（カスタムクレーム付与など、サーバー側で使う想定）

  * Node.js：Node 18以上が推奨方向（16はdeprecated） ([Firebase][9])
  * .NET：**.NET 8以上推奨**（6/7はdeprecated） ([GitHub][10])
  * Python：**Python 3.10以上推奨**（3.9はdeprecated） ([Firebase][11])

---

[1]: https://firebase.google.com/docs/rules/unit-tests?hl=ja&utm_source=chatgpt.com "単体テストを作成する | Firebase Security Rules - Google"
[2]: https://firebase.google.com/docs/ai-assistance/prompt-catalog/write-security-rules?utm_source=chatgpt.com "AI Prompt: Write Firebase Security Rules"
[3]: https://firebase.google.com/docs/firestore/security/test-rules-emulator?utm_source=chatgpt.com "Test your Cloud Firestore Security Rules - Firebase - Google"
[4]: https://firebase.google.com/docs/rules/manage-deploy?utm_source=chatgpt.com "Manage and deploy Firebase Security Rules - Google"
[5]: https://firebase.google.com/docs/auth/admin/custom-claims?utm_source=chatgpt.com "Control Access with Custom Claims and Security Rules"
[6]: https://github.com/firebase/snippets-rules?utm_source=chatgpt.com "Snippets for security rules on firebase.google.com"
[7]: https://firebase.blog/posts/2025/11/firebase-mcp-and-antigravity/?utm_source=chatgpt.com "Antigravity and Firebase MCP accelerate app development"
[8]: https://firebase.google.com/docs/functions/manage-functions?utm_source=chatgpt.com "Manage functions | Cloud Functions for Firebase - Google"
[9]: https://firebase.google.com/support/release-notes/admin/node?utm_source=chatgpt.com "Firebase Admin Node.js SDK Release Notes - Google"
[10]: https://github.com/firebase/firebase-admin-dotnet?utm_source=chatgpt.com "Firebase Admin .NET SDK"
[11]: https://firebase.google.com/support/release-notes/admin/python?utm_source=chatgpt.com "Firebase Admin Python SDK Release Notes - Google"
