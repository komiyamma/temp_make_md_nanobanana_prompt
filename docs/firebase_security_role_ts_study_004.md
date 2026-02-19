# 第4章：Rules言語の基本①（match / allow の読み方）🧩🛡️

この章は、Rulesを“読める＆書ける”ようになるための最初の山場です⛰️✨
ポイントはシンプル👇
**「どの道（パス）に」「どの操作（読む/書く）を」「どんな条件で」通すか**を、Rulesの文で表せるようになることです🙂

---

## 1) この章のゴール 🎯✨

* **match** が「対象の道（ドキュメントのパス）」だとわかる🚪
* **allow** が「通す操作（読む/書く）と条件」だとわかる✅
* まずは **“最小ルール”** を書いて、拒否される感覚を体で覚える😈→😇
* 「読みだけOK」を **コレクション1つ** に付けられる📖🔒

---

## 2) まずこの3つだけ覚えよう 🧠🔑

![Firebase Security Rules Structure](./picture/firebase_security_role_ts_study_004_01_rule_structure.png)

## ✅ ルールは “道（path）× 操作（method）× 条件（if）”

Rulesの基本形はこう👇（Firestore版の骨組み）
Firestoreは最初に **service** と **/databases/{database}/documents** で土台を作ります。([Firebase][1])

---

## ✅ match は「ドキュメントを指す」

![Match Targets Document](./picture/firebase_security_role_ts_study_004_02_match_document.png)

match は **コレクションじゃなくて “ドキュメントのパス” を狙う**のが基本です。
たとえば `/cities/{city}` は “citiesの中の1ドキュメント” を指す、って感じ。([Firebase][2])

---

## ✅ allow は「1つでもtrueがあれば勝ち」⚠️

![Allow Rule OR Logic](./picture/firebase_security_role_ts_study_004_03_allow_logic_or.png)

同じドキュメントが複数の match に当たることがあります。
その場合、**どれか1つでも allow 条件が true なら許可**されます（ゆるいルールが勝ちやすい）😱([Firebase][2])

---

## 3) match の読み方：パスの書き方を“日本語化”する 🗺️🙂

## (1) 単一ワイルドカード `{id}`

![Wildcard Variable Capture](./picture/firebase_security_role_ts_study_004_04_wildcard_variable.png)

`{city}` みたいな `{}` は「なんでも1区切りぶん入るよ」って意味です。
そして、その値は **変数** として if の中で使えます（例：city には "SF" とかが入る）。([Firebase][2])

---

## (2) サブコレは “自動では守られない” 🧨

![Subcollection Rules Independence](./picture/firebase_security_role_ts_study_004_05_subcollection_independence.png)

親の match を書いても、**子（サブコレ）には効きません**。
サブコレはサブコレで **明示的に match を書く**必要があります。([Firebase][2])

---

## (3) 再帰ワイルドカード `{path=**}` は強い（強すぎる）💥

![Recursive Wildcard Scope](./picture/firebase_security_role_ts_study_004_06_recursive_wildcard.png)

`{document=**}` みたいなやつは「下の階層ぜんぶ」をまとめてマッチします。
便利だけど、**うっかり allow を緩くすると全階層が開通**しがちなので注意⚠️
しかも Rules には “version 1/2” があり、再帰ワイルドカードの挙動が変わります。今は **rules_version = '2'** を明示しておくのが無難です。([Firebase][2])

---

## 4) allow の読み方：操作（method）をちゃんと区別する ✍️📖

![Read/Write Operation Granularity](./picture/firebase_security_role_ts_study_004_07_read_write_granularity.png)

allow は「何を許可するか」を書きます。
ざっくり便利メソッドはこの2つ👇

* **read**：読む系ぜんぶ（get + list）
* **write**：書く系ぜんぶ（create + update + delete）

さらに細かくも書けます👇

* get / list / create / update / delete ([Firebase][3])

> ここでのコツ：最初は read / write で理解して、慣れてきたら get/list と create/update/delete に分けると安全性が上がります🛡️✨([Firebase][3])

---

## 5) ハンズオン 🧑‍💻🔥（読む→手を動かす）

ここでは、わざと **拒否** を体験してから、**読みだけOK** にします😎

## 手順A：Rulesファイルを作る（まず全拒否）🙅‍♂️

プロジェクト直下で Firestore を初期化（Rulesファイルを作る）します👇([Firebase][4])

```bash
firebase init firestore
```

生成された rules（例：firestore.rules）を、まずは **全拒否** に👇（超大事：deny by default）

```js
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {

    // ✅ まずは全部拒否（安全の出発点）
    match /{document=**} {
      allow read, write: if false;
    }
  }
}
```

---

## 手順B：拒否される感覚を味わう 😈➡️😇

* 何かしらの読み取り・書き込みをすると、**Permission denied** 的な拒否になります（それが正解！）✅
* ルール確認には、Firebase Console の **Rulesシミュレータ** が使えます（エディタ上のルールに対してシミュレートします）。([Firebase][4])

---

## 手順C：コレクション1つだけ「読みOK」にする📖✅

たとえば `publicPosts` は誰でも読める、でも書けない（＝読みだけOK）にしてみます👇

```js
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {

    // ① 全部拒否（ベース）
    match /{document=**} {
      allow read, write: if false;
    }

    // ② publicPosts だけは “読む” を許可
    match /publicPosts/{postId} {
      allow read: if true;
    }
  }
}
```

ここで超重要👇
**「①で拒否してても、②でtrueなら読める」**（＝どれか1つtrueで勝ち）なので、ルール追加は “開通工事” だと思って慎重に！🚧😱([Firebase][2])

---

## 手順D：デプロイ（反映）🚀

CLIでデプロイすると反映できます👇([Firebase][4])

```bash
firebase deploy --only firestore
```

※ CLI デプロイは **Console側の既存ルールを上書き**するので、Consoleで直したときはローカル側も合わせてね⚠️🧯([Firebase][5])

---

## 6) ミニ課題 🎯✨（10分）

## 課題A：もう1コレクション作って「読みだけOK」🚪📖

* `publicProfiles/{uid}` を “読むだけOK” にしてみよう🙂

  * ヒント：`match /publicProfiles/{uid} { allow read: if true; }`

## 課題B：サブコレに効かないのを体感する 🧨

* `publicPosts/{postId}/comments/{commentId}` を作って、
  **comments は読めない**ことを確認👉（親の match では守れない）
* できたら comments 用の match を追加して、読めるようにしてみよう！

---

## 7) チェック ✅（できた？）

* [ ] match は「ドキュメントの道」を指してると説明できる？([Firebase][2])
* [ ] allow は「操作＋条件」で、1つでもtrueがあれば通るのを理解した？([Firebase][2])
* [ ] サブコレは別 match が必要だとわかった？([Firebase][2])
* [ ] 全拒否→必要な場所だけ開ける流れで書けた？🛡️✨

---

## 8) AI活用 🤖💨（Rules学習の最短ルート）

## ✅ Antigravity + Firebase MCP で「Rulesの読み書き」を加速⚡

Antigravity には Firebase MCP を追加して、プロジェクトの状況を見ながら相談できる流れが紹介されています。([The Firebase Blog][6])
そこで、こう聞くのが強いです👇

* 「`publicPosts` は誰でも読める、書けない。`comments` はログインユーザーだけ読める…みたいな設計で、match/allow を最小で書いて」
* 「“どれか1つtrueで勝つ” ルール衝突が起きないように、危ないパターンも指摘して」

---

## ✅ Gemini CLI（Firebase拡張）で“叩き台”を出させる🧱

Firebaseの Gemini CLI 拡張は、**Rulesとテスト生成**を助ける目的で用意されていて、MCPサーバーと連携して動くことが明記されています。([Firebase][7])

おすすめ運用👇

1. AIに **最小権限** で叩き台を作らせる
2. 人間がこの章の観点でレビュー（match/allow/衝突/サブコレ）🧑‍⚖️
3. Consoleシミュレータ or Emulator で確認🧪（本格テストは後章で！）([Firebase][4])

※ AIプロンプトカタログ自体も更新され続けてます（2026-02-05更新のページが案内あり）。([Firebase][8])

---

## 9) 次章予告 👀✨

次は **request / resource** が登場します！
「今送ってきたデータ」と「元からあるデータ」を比べられるようになって、**“更新だけ禁止”** みたいな制御ができるようになります🔍🛡️

[1]: https://firebase.google.com/docs/firestore/security/rules-structure "Structuring Cloud Firestore Security Rules  |  Firebase"
[2]: https://firebase.google.com/docs/rules/rules-behavior "How Security Rules work  |  Firebase Security Rules"
[3]: https://firebase.google.com/docs/rules/rules-language "Security Rules language  |  Firebase Security Rules"
[4]: https://firebase.google.com/docs/firestore/security/get-started "Get started with Cloud Firestore Security Rules  |  Firebase"
[5]: https://firebase.google.com/docs/rules/manage-deploy?utm_source=chatgpt.com "Manage and deploy Firebase Security Rules - Google"
[6]: https://firebase.blog/posts/2025/11/firebase-mcp-and-antigravity/?utm_source=chatgpt.com "Antigravity and Firebase MCP accelerate app development"
[7]: https://firebase.google.com/docs/ai-assistance/prompt-catalog/write-security-rules?utm_source=chatgpt.com "AI Prompt: Write Firebase Security Rules"
[8]: https://firebase.google.com/docs/ai-assistance/prompt-catalog?utm_source=chatgpt.com "AI prompt catalog for Firebase | Develop with AI assistance"
