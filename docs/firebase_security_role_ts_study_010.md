# 第10章：入力検証① 必須フィールドと型（まず事故を止める）🧠🧱

この章は「**変なデータをDBに入れさせない**」がテーマだよ😊✨
Firestoreは“スキーマなし（何でも入る）”だから、**Rulesで最低限のスキーマを作る**のが超大事🔥 ([Firebase][1])

---

## 1) まずココだけ覚える！🎯（今日の武器🗡️）

**入力検証の基本セット**はこれ👇

1. ✅ **必須フィールドが揃ってる？** → `keys().hasAll([...])`
2. ✅ **余計なフィールドが紛れ込んでない？** → `keys().hasOnly([...])`（ホワイトリスト方式）
3. ✅ **型が合ってる？** → `is string / is int / is timestamp ...`

Firestoreはスキーマレスだから、これをやらないと
「title が配列だった😇」「isAdmin を勝手に付けられた😇」みたいな事故が起きがち💥 ([Firebase][1])

---

## 2) 例題：AIメモアプリの `aiNotes` を守る📝🤖

AI系（FirebaseのAI機能やGeminiなど）を絡めると、Firestoreには例えばこんなデータを入れたくなるよね👇

* `prompt`（ユーザーの入力）
* `answer`（AIの返答）
* `ownerUid`（持ち主）
* `createdAt`（作成日時）

ここで**入力検証を入れないと**、悪意ある人が👇みたいな“混入”を狙える😱

* `isAdmin: true` を勝手に書く
* `createdAt` に文字列を入れる（timestampじゃない）
* 必須フィールド無しで壊れたドキュメントを量産する

---

## 3) ルール実装（読む→手を動かす🧑‍💻✨）

## 3-1. ルールの考え方（超ざっくり）🧠

* **必須**：`keys().hasAll([...])` で「最低限これが無いとダメ！」
* **許可リスト**：`keys().hasOnly([...])` で「これ以外は一切ダメ！」

  * これが強い🔥（“新しいフィールド”はデフォで拒否できる） ([Firebase][1])
* **型**：`is` で型を固定（`string`, `int`, `timestamp` など） ([Firebase][1])

---

## 3-2. `firestore.rules` サンプル🛡️✨

```js
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {

    function isSignedIn() {
      return request.auth != null;
    }

    // ✅ 必須フィールド（最低限これが無いと拒否）
    function hasRequiredFields(d) {
      return d.keys().hasAll(['prompt', 'answer', 'ownerUid', 'createdAt']);
    }

    // ✅ 許可フィールド（これ以外の“余計なキー”が来たら拒否）
    function hasOnlyAllowedFields(d) {
      return d.keys().hasOnly([
        'prompt', 'answer', 'ownerUid', 'createdAt',
        'updatedAt', 'model'  // ← 任意（後で増やしたいならここに追加）
      ]);
    }

    // ✅ 型チェック（“っぽい”じゃなく、ちゃんと型で止める）
    function hasValidTypes(d) {
      return d.prompt is string
        && d.answer is string
        && d.ownerUid is string
        && d.createdAt is timestamp
        // optional: updatedAt（無ければOK、あればtimestamp）
        && (d.get('updatedAt', null) == null || d.get('updatedAt', null) is timestamp)
        // optional: model（無ければOK、あればstring）
        && (d.get('model', null) == null || d.get('model', null) is string);
    }

    // ✅ ちょいUX：空文字は拒否（最低限）
    function notEmptyStrings(d) {
      return d.prompt != "" && d.answer != "";
    }

    match /aiNotes/{noteId} {

      // 読みは一旦「本人だけ」にしておく（安全寄り）
      allow get, list: if isSignedIn() && resource.data.ownerUid == request.auth.uid;

      // 作成：本人のデータ + 必須 + 許可リスト + 型 + 空文字NG
      allow create: if isSignedIn()
        && request.resource.data.ownerUid == request.auth.uid
        && hasRequiredFields(request.resource.data)
        && hasOnlyAllowedFields(request.resource.data)
        && hasValidTypes(request.resource.data)
        && notEmptyStrings(request.resource.data);

      // 更新：基本は create と同じ検証を“もう一回”
      // （update は request.resource が「更新後の完成形」になるので、必須チェックも効く）
      allow update: if isSignedIn()
        && request.resource.data.ownerUid == request.auth.uid
        && hasRequiredFields(request.resource.data)
        && hasOnlyAllowedFields(request.resource.data)
        && hasValidTypes(request.resource.data)
        && notEmptyStrings(request.resource.data);

      // 削除：本人のみ（ここは第9章の復習）
      allow delete: if isSignedIn() && resource.data.ownerUid == request.auth.uid;
    }
  }
}
```

ポイント解説😊👇

* `keys().hasAll([...])` で必須項目を強制できるよ ✅ ([Firebase][1])
* `keys().hasOnly([...])` は「許可リスト」方式なので強い🔥（**余計なフィールドをデフォ拒否**） ([Firebase][1])
* 型チェックは `is` を使う（`string`, `int`, `timestamp` など） ([Firebase][1])
* **optional フィールド**は `d.foo` って直に触ると「無い時にエラー→即拒否」になりがち。`get('foo', default)` が安全✅ ([Firebase][1])
* `update` のとき `request.resource` は「更新後のドキュメント状態」になるよ（だから必須チェックも効く） ([Firebase][2])

---

## 4) 手を動かす（3分でOK）🧪✨

## ✅ 試したい“ダメ入力”3連発💣

1. 必須不足（`createdAt` なし）
   → ❌ 作成できない

2. 型ミス（`createdAt: "2026-02-16"` みたいに文字列）
   → ❌ 作成できない（timestampじゃない）

3. 余計なフィールド混入（`isAdmin: true`）
   → ❌ 作成できない（`hasOnly`で止まる🔥）

---

## 5) ミニ課題🎯（章のゴールに直結✨）

次の条件を満たすように、上のルールを微調整してね😊🛠️

* `prompt` は必須＆空文字NG ✅
* `answer` は必須＆空文字NG ✅
* `model` は任意（無くてOK、あればstring） ✅
* 余計なフィールドは全部拒否 ✅

---

## 6) チェック✅（できたら勝ち！🏆）

* [ ] 必須フィールドが欠けると弾ける？😎
* [ ] 型がおかしいと弾ける？😎（`timestamp` が超重要）
* [ ] `isAdmin` みたいな“混入フィールド”を止められる？😎
* [ ] optional は `get()` を使って安全に書けた？😊 ([Firebase][1])

---

## 7) AIで加速するやり方（ただし“最後は人間が責任”🤖🧑‍⚖️）

## 7-1. Gemini CLIで「Rules＋テストの叩き台」を作る🚀

Firebase公式の流れだと👇こういう感じで、**Rulesとテスト雛形まで**出してくれるよ✨ ([Firebase][3])

```bash
gemini extensions install https://github.com/gemini-cli-extensions/firebase
gemini
/firestore:generate_security_rules
```

* `firestore.rules` と、テスト用の `security_rules_test_firestore` を生成してくれる（Node.jsプロジェクト） ([Firebase][3])
* しかも “攻撃シミュレーション”で脆弱っぽい所を探そうとしてくれるのが面白い😆🛡️ ([Firebase][3])
* ただし **自動追従で更新はされない**（作ったら終わり、毎回見直しが必要）⚠️ ([Firebase][3])
* そして重要：Firebaseコンソール内の **Gemini in Firebase はRules生成に未対応**（現時点）⚠️ ([Firebase][3])

## 7-2. Antigravity × Firebase MCP で“会話しながら整える”🧠✨

Firebase MCP server は **Antigravity に追加できる**ってFirebase公式Blogで紹介されてるよ📌
メニューからMCP servers→Firebase→install、みたいな流れ（記事に手順あり） ([The Firebase Blog][4])

ここでおすすめの頼み方（例）👇

* 「`aiNotes` の必須フィールドと型のRules関数を作って」
* 「`hasOnly` で余計なフィールド混入を止めたい。安全な書き方にして」
* 「“弾くべきテストケース”を3つ作って」

---

## 8) 最後に：Rulesだけに頼り切らないのもコツ😉

Rulesは“最後の砦🛡️”だけど、**アプリ側でも入力チェック**しておくと
UXも良くなるし、無駄なリクエストも減って気持ちいいよ😊✨
（Firestoreのガイドでも、入力チェックをRules条件として書く流れが紹介されてるよ） ([Firebase][2])

---

次の第11章は「文字数・パターン（地雷💣）」へ進むけど、
この第10章の **必須＋型＋許可リスト**ができた時点で、もう“守りの骨格”は完成だよ🦴🔥

[1]: https://firebase.google.com/docs/firestore/security/rules-fields "Control access to specific fields  |  Firestore  |  Firebase"
[2]: https://firebase.google.com/docs/rules/data-validation "Data validation  |  Firebase Security Rules"
[3]: https://firebase.google.com/docs/ai-assistance/prompt-catalog/write-security-rules "AI Prompt: Write Firebase Security Rules  |  Develop with AI assistance"
[4]: https://firebase.blog/posts/2025/11/firebase-mcp-and-antigravity/ "Antigravity and Firebase MCP accelerate app development"
