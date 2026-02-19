# 第13章：Rules関数化（読みやすさ＝安全性）🧩✨

この章のゴールはこれ👇
**「Rulesのコピペ地獄😵」を卒業して、読みやすく・直しやすく・事故りにくい🛡️ルールにする**ことです✨
Rulesは条件（true/false）で守る世界なので、**読みやすさ＝安全性**に直結します✅ ([Firebase][1])

![Comparison of messy vs clean code structure.](./picture/firebase_security_role_ts_study_013_01_messy_vs_clean.png)

---

## 1) 読む📖：なんで“関数化”が安全につながるの？🤔🔐

## コピペが増えると起きる事故💥

たとえば「ログイン必須」の条件を10か所にコピペすると…

* 1か所だけ修正漏れ → **そこが穴になる**😱
![Security risk from copy-paste errors.](./picture/firebase_security_role_ts_study_013_02_copy_paste_leak.png)
* 似てるけど微妙に違う条件が混ざる → **挙動が読めなくなる**🌀
* 後から見返して怖い → **触れなくなる（最悪）**🧟‍♂️

だから、**同じ意味の条件は1か所に集める**のが強いです💪✨

---

## 2) 重要ルール📌：関数の書き方（Rules v2の基本）🧠✨

Rulesファイルは先頭で **`rules_version = '2';`** を使うのが基本です✅ ([Google Cloud Documentation][2])

そして関数はこんな制約があります👇（地味だけど超大事！）

* `let` でローカル変数を作れる（最大10個）🧺
* **最後は必ず `return`** で終わる📤
* 関数は呼び出しできるけど **再帰は不可**🙅
* **呼び出しの深さ（スタック）は最大20**🧱 ([Firebase][3])

つまり、関数は「小さく」「浅く」「質問っぽい名前（is～ / can～）」が安全です🙂✨

![Constraints of Firestore Rules functions.](./picture/firebase_security_role_ts_study_013_03_function_constraints.png)

---

## 3) 手を動かす🧑‍💻：コピペRulesを“関数化Rules”へリファクタリング🛠️✨

ここでは「AIチャット履歴（=AI機能の材料🧠💬）」を Firestore に保存する想定でいきます！
（例：`chats/{chatId}` と `chats/{chatId}/messages/{msgId}`）

---

## Step 0：まず“コピペ地獄”の例を見る😵

```js
// firestore.rules（例：悪い感じ😵）
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {

    match /chats/{chatId} {
      allow read: if request.auth != null;
      allow create: if request.auth != null
        && request.resource.data.ownerUid == request.auth.uid;

      allow update: if request.auth != null
        && resource.data.ownerUid == request.auth.uid
        && request.resource.data.ownerUid == resource.data.ownerUid;

      allow delete: if request.auth != null
        && resource.data.ownerUid == request.auth.uid;
    }

    match /chats/{chatId}/messages/{msgId} {
      allow read: if request.auth != null; // ← もう同じの出てる😵
      allow create: if request.auth != null
        && request.resource.data.senderUid == request.auth.uid;
    }
  }
}
```

この状態だと「ログイン必須」や「オーナー判定」が散らばって、修正漏れが起きやすいです💥

---

## Step 1：よく使う“共通関数”を作る🧩✨

ポイント：**上のほう（共通スコープ）にまとめる**と読みやすいです📚

```js
// firestore.rules（関数化の土台✨）
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {

    // ✅ 1) まずは「超よく使う3点セット」
    function isSignedIn() {
      return request.auth != null;
    }

    function uid() {
      return request.auth.uid;
    }

    function isOwner(ownerUid) {
      return isSignedIn() && ownerUid == uid();
    }

    // ✅ 2) 「更新で触っていいフィールドだけ許可」も関数化できる
    //    affectedKeys() は「変更があったフィールド一覧」
    function onlyTheseFieldsCanChange(allowed) {
      return request.resource.data.diff(resource.data).affectedKeys().hasOnly(allowed);
    }

    // ここから match が続く...
  }
}
```

* `isSignedIn()` / `uid()` / `isOwner()` があるだけで、Rulesの可読性が一気に上がります📈✨
![Building a strong foundation with common functions.](./picture/firebase_security_role_ts_study_013_04_function_building_blocks.png)
* `hasOnly()` で「触っていいフィールドだけ」を縛れるのが超強いです🛡️（禁止リストより安全になりがち） ([Google Cloud Documentation][4])
* `let` を使いたくなったら「式が長すぎる時だけ」にすると読みやすいです🙂（制限もあるので） ([Firebase][3])

---

## Step 2：allow を “英文っぽく” 読める形にする📖✨

次に、**match内のallow条件を短く**していきます👇

```js
// firestore.rules（関数化後の完成イメージ✨）
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {

    function isSignedIn() { return request.auth != null; }
    function uid() { return request.auth.uid; }
    function isOwner(ownerUid) { return isSignedIn() && ownerUid == uid(); }

    function onlyTheseFieldsCanChange(allowed) {
      return request.resource.data.diff(resource.data).affectedKeys().hasOnly(allowed);
    }

    // ✅ chats（AIチャットの部屋）
    match /chats/{chatId} {

      // 読めるのは：ログイン済み かつ オーナーだけ
      allow read: if isOwner(resource.data.ownerUid);

      // 作れるのは：自分のownerUidで作るときだけ
      allow create: if isSignedIn()
        && request.resource.data.ownerUid == uid();

      // 更新できるのは：オーナーだけ + 変更できるのは title だけ
      allow update: if isOwner(resource.data.ownerUid)
        && onlyTheseFieldsCanChange(['title']);

      // 削除できるのは：オーナーだけ
      allow delete: if isOwner(resource.data.ownerUid);
    }

    // ✅ messages（AIへの質問/回答ログ）
    match /chats/{chatId}/messages/{msgId} {

      // まず親chatのownerを参照して判定（チャットの持ち主だけ読める）
      allow read: if isSignedIn()
        && get(/databases/$(database)/documents/chats/$(chatId)).data.ownerUid == uid();

      // 送信できるのは：自分がsenderUidのときだけ
      allow create: if isSignedIn()
        && request.resource.data.senderUid == uid();
    }
  }
}
```

✅ ここが気持ちいいポイント😍

* `allow read: if isOwner(...)` みたいに **一瞬で意味が読める**
![Code that reads like natural language.](./picture/firebase_security_role_ts_study_013_05_readable_rules.png)
* 条件を直すとき、**直す場所が少ない**（＝穴が減る）🛡️✨
* AIが生成したRulesも、関数があるとレビューしやすい👀✅

> ※ `get()` など「別ドキュメント参照」は便利だけど、使いすぎると複雑になりやすいので、**必要最小限**にするのがコツです🙂
> （Rulesは「条件で守る」仕組み） ([Firebase][1])

---

## 4) AIで加速🤖⚡（でも“最終責任”は人間🧑‍⚖️✅）

## 4-1. Gemini CLI / Firebase拡張で「叩き台」を作る🧰

![AI assisting with security rules.](./picture/firebase_security_role_ts_study_013_06_ai_assistant.png)

Firebaseの **AI prompt（Write security rules）** は、Gemini CLI の Firebase拡張から **Rulesとテストの下書き**を作る用途で提供されています。
コードを解析してスキーマやアクセスを推測し、最小権限ベースで草案を作り、攻撃っぽい試行で弱点を探す設計になっています🧠🛡️ ([Firebase][5])

さらに、Gemini CLI の Firebase拡張は **Firebase MCP server** をセットアップして使う流れが公式で案内されています。 ([Firebase][6])

---

## 4-2. Antigravity側でもFirebase MCPが使える🧩✨

AntigravityのAgent画面から **MCP Servers → Firebase を入れる**流れが公式に案内されています。
つまり「プロジェクト状況を見ながらRulesを相談→修正」みたいな体験がしやすいです🤝🤖 ([The Firebase Blog][7])

---

## 4-3. すぐ使える“AI指示テンプレ”3つ📋✨

以下をそのまま投げると強いです💪（※最後に必ず自分の目で確認👀✅）

1. **関数化して可読性UP**

* 「このFirestore Rulesを、`isSignedIn / uid / isOwner / onlyTheseFieldsCanChange` を使って関数化してください。allow条件は短く、意図が読める形にして。」

2. **攻撃者視点チェック**

* 「このRulesに対して、想定できる攻撃（権限昇格・他人のデータ参照・想定外フィールド注入）を列挙し、それぞれ防げているか確認して。」

3. **テスト観点の洗い出し**

* 「このRulesに必要なテストケースを、`未ログイン / 本人 / 他人 / 管理者（将来）` の観点で一覧化して。通るべき✅/弾くべき❌をセットで。」

---

## 5) ミニ課題🎯：owner判定を“3か所以上”で使ってみよう🙂✨

次のどれかを選んでOKです👇

* 課題A：`isOwner()` を `chats` と `messages` の両方で使う（すでに例に近い）💬
* 課題B：`onlyTheseFieldsCanChange(['title'])` を `profile` 更新にも適用してみる👤
* 課題C：`isSignedIn()` のコピペを全部消して、関数呼び出しに置き換える🧹✨

---

## 6) チェック✅：この章を終えたらクリアしてたいリスト📝✨

* [ ] `request.auth != null` のコピペが減った🧹
* [ ] `isOwner()` で「本人だけ」を表現できる👤🔒
* [ ] allow条件が短くて、**英語の文みたいに読める**📖✨
* [ ] 更新時は「触っていいフィールドだけ」縛れてる🛡️ ([Google Cloud Documentation][4])
* [ ] 関数が深くなりすぎてない（スタック最大20）🧱 ([Firebase][3])

---

## 7) 次章へのつながり🚪✨（ロール設計がラクになる）

次の第14章で「admin / user みたいなロール」を考えるんだけど、ここで関数化しておくと…

* `function isAdmin() { ... }` を1個足すだけで
* いろんな `allow` に「管理者だけOK👑」を安全に入れられます

ここ、めっちゃ気持ちいいです😆🔥

---

## おまけ：サーバー側（Custom Claims付与）で使う言語の目安🧾✨

ロール付与はサーバー側（Admin SDK）でやるのが基本なので、バージョン目安だけ置いときます👇

* Admin SDK（Node.js）：**Node 18+** が前提（18未満は対象外） ([Firebase][8])
* Admin SDK（.NET）：**.NET 8+ 推奨**（6/7はdeprecated） ([Firebase][9])
* Admin SDK（Python）：**Python 3.10+ 推奨**（3.9はdeprecated） ([Firebase][10])
* Cloud Functions/CLI：**Node 20/22 がフルサポート**（18はdeprecated扱い） ([Firebase][11])

---

必要なら、この第13章のRulesをベースにして、次の第14章（ロール設計）へスムーズにつながる「isAdmin() の仮置き版」まで含めたテンプレも作るよ👑🛡️✨

[1]: https://firebase.google.com/docs/firestore/security/rules-conditions?utm_source=chatgpt.com "Writing conditions for Cloud Firestore Security Rules - Firebase"
[2]: https://docs.cloud.google.com/firestore/native/docs/security/rules-structure?utm_source=chatgpt.com "Structure security rules | Firestore in Native mode"
[3]: https://firebase.google.com/docs/rules/rules-language?utm_source=chatgpt.com "Security Rules language - Firebase - Google"
[4]: https://docs.cloud.google.com/firestore/native/docs/security/rules-fields?hl=ja&utm_source=chatgpt.com "特定のフィールドへのアクセスを制御する | Firestore in Native ..."
[5]: https://firebase.google.com/docs/ai-assistance/prompt-catalog/write-security-rules?utm_source=chatgpt.com "AI Prompt: Write Firebase Security Rules"
[6]: https://firebase.google.com/docs/ai-assistance/gcli-extension?utm_source=chatgpt.com "Firebase extension for the Gemini CLI"
[7]: https://firebase.blog/posts/2025/11/firebase-mcp-and-antigravity/?utm_source=chatgpt.com "Antigravity and Firebase MCP accelerate app development"
[8]: https://firebase.google.com/docs/admin/setup?utm_source=chatgpt.com "Add the Firebase Admin SDK to your server - Google"
[9]: https://firebase.google.com/support/release-notes/admin/dotnet?utm_source=chatgpt.com "Firebase Admin .NET SDK Release Notes"
[10]: https://firebase.google.com/support/release-notes/admin/python?utm_source=chatgpt.com "Firebase Admin Python SDK Release Notes - Google"
[11]: https://firebase.google.com/docs/functions/get-started?utm_source=chatgpt.com "Get started: write, test, and deploy your first functions - Firebase"
