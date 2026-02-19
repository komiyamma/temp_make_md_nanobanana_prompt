# 第19章：AIで開発を加速する 🛸💻🤖✨（Antigravity / Gemini CLI / Firebase AIも総動員！）

この章は「**AIに“作業を任せる”→人間が“判断する”**」の型を作る回です🙂✨
1回ここを体験すると、以後の章ぜんぶが速くなります🚀💨

---

## 1) この章でできるようになること 🎯✨

* UI部品（ボタン・カード・テーブル周り）を **AIに量産させる** 🧱🧩
* 既存コードの **リファクタ案 → 差分レビュー → 適用** を “流れ作業” にする 🧼🔁
* テストの叩き台（最低限）を作って、**壊してない自信**を得る 🧪✅
* Firebase AI（AI Logic）に入れる **プロンプトや入出力仕様を整える** 🧠📦

---

## 2) まず「AIに任せる範囲」を決めるコツ 🧭🤝

AIって万能そうに見えるけど、得意・不得意がハッキリしてます😇

## AIに任せると爆速になるやつ ⚡

* 雛形づくり（UIコンポーネント、hook、型、テストの骨組み）🧱
* “こういう時どう書く？” の提案（状態管理、分割、命名）🧠
* エラーの原因候補の列挙＆切り分け手順 🧯
* ドキュメントの要点まとめ（公式仕様の読み取り）📚

## 人間が絶対に握るやつ（ここ重要）🧨

* 仕様の最終判断（何をどう見せるか）👀
* セキュリティ（権限・認可・秘密情報）🔐
* 差分レビュー（どのファイルに何を足したか）🧾
* “運用しやすさ”（将来メンテできるか）🛠️

---

## 3) 今回使う3つの“加速エンジン” 🚀🧰

![AI Development Tools Triad](./picture/firebase_frontend_foundation_ts_study_019_01_ai_tools_triad.png)

## A. Google Antigravity：ミッションで「まとめて作らせる」🎮🤖

![Antigravity Workflow](./picture/firebase_frontend_foundation_ts_study_019_02_antigravity_flow.png)

Antigravityは、エージェントを管理する **Mission Control** を持っていて、計画→実装→検証までをまとめて進めやすい設計です。ブラウザで調べ物しながら作業もできます。([Google Codelabs][1])
（Windows向けも用意されています。([Google Codelabs][1])）
※ Google 製のエージェント系開発環境です。

## B. Gemini CLI：ターミナルで「差分作業＆自動化」⌨️🧠

![Gemini CLI ReAct Loop](./picture/firebase_frontend_foundation_ts_study_019_03_gemini_cli_loop.png)

Gemini CLIは、ターミナルから使える **オープンソースAIエージェント**で、ReActループ（考える→実行→検証）で作業します。MCPサーバーにも対応しています。([Google Cloud Documentation][2])
Cloud Shellでは追加セットアップ無しでも使える案内があります。([Google Cloud Documentation][2])

## C. Firebase Studio：環境をNixで固定して「再現性で勝つ」🧊📦

Firebase Studioは、Nixでワークスペース環境を定義できて、同じ環境をみんなで再現しやすいのが強みです。([Firebase][3])

---

## 4) ハンズオン：AIで“UI部品量産 → リファクタ → テスト”を通す 🏃‍♂️💨

ここからは、あなたの管理画面アプリを想定して進めます📊✨
（例：Users一覧ページ、詳細フォーム、画像アップロード、AI整形ボタン…など）

---

## Step 0：AI作業の前に「安全ベルト」を締める 🧷✅

最低これだけやると、AI作業が怖くなくなります🙂

* `git status` がクリーンか確認（未コミットが多いと事故りやすい）🧹
* `npm test` / `npm run build` が通る状態にしておく 🔧✅
* 1回のAI依頼は **“小さく”**（1コンポーネント、1リファクタ、1テスト）📦

---

## Step 1：Antigravityに「UI部品を3つまとめて」作らせる 🧱🤖✨

![UI Component Factory](./picture/firebase_frontend_foundation_ts_study_019_04_component_factory.png)

目的：コピペ地獄をなくす🔥
おすすめの量産セットはこれ👇

* `EmptyState`（0件表示）🫙
* `LoadingOverlay`（読み込み中）⏳
* `ConfirmDialog`（削除など危険操作）⚠️

## ✅ Antigravity “ミッション文”テンプレ（そのまま貼ってOK）📝

```text
目的：
管理画面アプリに共通UI部品を追加したい。EmptyState / LoadingOverlay / ConfirmDialog を実装して。

制約：
- TypeScript + React の既存構成に合わせる
- Tailwind v4系のクラスで見た目を整える
- propsは型安全に（any禁止）
- アクセシビリティ（ボタンのラベル、dialogのフォーカス）も意識

成果物：
- components/common/EmptyState.tsx
- components/common/LoadingOverlay.tsx
- components/common/ConfirmDialog.tsx
- 使い方例を pages/users/UserListPage.tsx に1箇所だけ入れて
- 既存のUIルール（角丸/余白/色）を壊さない

最後に：
- どんな差分を入れたか要約して
- 動作確認手順（画面で何を見ればOKか）を書いて
```

Antigravityは “指示→エージェントが動く” 体験が中心なので、**成果物と差分要約**を必ず出させるのがコツです🧠✨([Google Codelabs][4])

---

## Step 2：Gemini CLIで「リファクタ案→差分確認→適用」まで回す 🔁🧼🧠

![Safe Refactoring Flow](./picture/firebase_frontend_foundation_ts_study_019_05_refactor_flow.png)

目的：第7章でやった `loading / error / data` の三兄弟を、ページごとにバラバラにしない😵‍💫➡️統一🙂✨

## ✅ 例：Firestore一覧取得をカスタムhookに寄せる

* いま：`UserListPage.tsx` に取得処理がベタ書き
* これから：`hooks/useUsers.ts` に寄せる

## Gemini CLIに投げる“依頼文”テンプレ 🧾

```text
次の方針でリファクタして：
- UserListPage.tsx の Firestore取得処理を hooks/useUsers.ts に移動
- return は { data, loading, error, refresh } に統一
- loading/error/empty の表示は共通部品（LoadingOverlay / EmptyState）を使う
- 変更は最小限、UIの見た目は維持
- まず差分案を提示して、OKなら適用
最後に：npm test と npm run build の実行手順を書いて
```

Gemini CLIは、ターミナルやファイル操作などの “道具” を使いながら作業する設計（ReAct）で、MCPサーバーも扱えます。([Google Cloud Documentation][2])
なので「**差分を先に出して**」がめちゃ効きます💡

## 🧠（一旦ここだけ覚えればOK）“AI差分運用”の鉄則3つ

1. **提案→差分→適用** の順にする（いきなり全書き換え禁止）🛑
2. 変更ファイル数を絞る（多いとレビュー破綻）📉
3. 通ったらすぐ小さくコミット（戻れるのが正義）🧷

---

## Step 3：テストの叩き台をAIに作らせて“壊してない自信”を手に入れる 🧪✅✨

テストって最初むずいんだけど、AIに “型” を作らせると楽になります🙂
おすすめはこの順👇

* **純関数**（utils）→ テスト簡単🍬
* **hook** → 少し難しいけど効果大🧠
* **UI** → 慣れてからでOK👍

## テスト依頼テンプレ（hook向け）🧪

```text
hooks/useUsers.ts に対して、最低限の単体テストを追加したい。
- 正常系：dataが返るとき loading=false になる
- 異常系：例外時に error が入る
Firestore部分はモックでOK。
テストフレームワークは既存プロジェクトの方針に合わせて提案して。
```

---

## Step 4：Firebase AI（AI Logic）で“プロンプトを仕様化”しておく 🧠📐🤖

![Structured Prompt Specification](./picture/firebase_frontend_foundation_ts_study_019_06_prompt_spec.png)

第18章でAIボタンを作ってるので、この章ではさらに一歩進めて **AI出力の形を固定**します✨
Firebase AI Logicは、アプリからGemini/Imagenモデルにアクセスするための仕組みを提供しています。([Firebase][5])

## ここでやると強いこと 💪

* プロンプトを「日本語でふわっと」→「入力/出力のルールあり」にする📏
* 例：日報整形なら

  * 入力：自由文
  * 出力：`title / summary / bullets / actionItems` みたいな形に寄せる📦

## “プロンプト仕様”テンプレ（例：日報整形）📝

```text
あなたは文章編集アシスタントです。
入力：日本語の作業メモ（雑でOK）
出力：次のJSON形式で返してください
- title: 15〜30文字
- summary: 80〜140文字
- bullets: 箇条書き5個まで
- actionItems: 次やること3個まで
制約：誇張しない。数字や固有名詞は入力にあるものだけ使う。
```

これをやると、UI側が作りやすくなって「AI結果を確認して反映」が安定します🙂✅

---

## 5) “AIがクラウド側のコードを出してきた時”のバージョン注意 ⚙️📌

![Runtime Version Safety](./picture/firebase_frontend_foundation_ts_study_019_07_version_safety.png)

AIが「Functionsも直しといたよ！」ってノリで書いてくることがあるんですが…そこで事故ります😇💥
最低限ここだけ見ておくと安全です👇

* Cloud Functions for Firebase のNodeランタイムは **Node.js 22 / 20**、**18はdeprecated** の案内です。([Firebase][6])
* Node.jsのリリース状況として、**v24がActive LTS、v25がCurrent** になっています（2026-02-09更新）。([nodejs.org][7])
* .NETは **.NET 10がLTS**（2026-02-10時点で 10.0.3）。([Microsoft][8]) ※ Microsoft
* Pythonは **3.14系が安定版として提供**され、3.14.3や3.13.12が配布されています（2026-02-03付近）。([Python.org][9])

---

## 6) ミニ課題 🎯🔥（30〜45分）

次のどれか1つやればOKです😆✨

1. **Users一覧ページ**に、`EmptyState / LoadingOverlay / ConfirmDialog` をちゃんと組み込む🧩
2. Firestore取得を `useUsers()` に寄せて、`loading/error/data` を統一する🔁
3. AI整形ボタンの出力を **JSON形式に寄せるプロンプト仕様**を作って、UIに反映する📦🤖

---

## 7) チェック✅（ここ通ったら勝ち🏆）

* 変更は小さく、差分が追える🧾✅
* `npm run build` が通る🔧✅
* ローディング/エラー/0件が全部“無言”にならない😇✅
* AIの提案をそのまま採用せず、命名・責務・安全性を見直せた👀✅
* AI出力（文章整形など）が“確認して反映”になっている🧠✅

---

必要なら、この第19章のハンズオンを「あなたの今のフォルダ構成（components/pages/hooks/services）」に合わせて、**具体的なファイル名で“作業指示書”形式**にして出します📋✨
（例：`pages/users/UserListPage.tsx` を起点に、どこへ何を移すかまで全部書くやつ😆）

[1]: https://codelabs.developers.google.com/getting-started-google-antigravity "Getting Started with Google Antigravity  |  Google Codelabs"
[2]: https://docs.cloud.google.com/gemini/docs/codeassist/gemini-cli "Gemini CLI  |  Gemini for Google Cloud  |  Google Cloud Documentation"
[3]: https://firebase.google.com/docs/studio/get-started-workspace?utm_source=chatgpt.com "About Firebase Studio workspaces - Google"
[4]: https://codelabs.developers.google.com/building-with-google-antigravity "Building with Google Antigravity  |  Google Codelabs"
[5]: https://firebase.google.com/docs/ai-logic?utm_source=chatgpt.com "Gemini API using Firebase AI Logic - Google"
[6]: https://firebase.google.com/docs/functions/manage-functions?utm_source=chatgpt.com "Manage functions - Cloud Functions for Firebase"
[7]: https://nodejs.org/ja/about/previous-releases?utm_source=chatgpt.com "Node.js リリース"
[8]: https://dotnet.microsoft.com/en-us/platform/support/policy?utm_source=chatgpt.com "The official .NET support policy | .NET"
[9]: https://www.python.org/downloads/source/?utm_source=chatgpt.com "Python Source Releases"
