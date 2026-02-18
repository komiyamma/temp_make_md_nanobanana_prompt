# 第9章：最小権限② “書く”の制御（create / update / delete を分ける）✍️🧯

この章のテーマはズバリ👇
**「書き込み権限を “まとめて許可” しないで、事故を未然に止める」** です😎🛡️

---

## 1) まず、ここだけ覚えればOKな結論✨

Firestore の “書く” は3種類あります👇

* **create**：新規作成🆕
* **update**：更新✏️
* **delete**：削除🗑️

そして…
**allow write** は、上の **3つ全部を許す** のと同じです⚠️（＝めちゃ雑になりがち） ([Stack Overflow][1])

なので基本方針はこう👇
✅ **create / update / delete を別々に書く**
✅ **delete は特に厳しくする（最悪 “管理者のみ”）**
✅ **update は “変更できる項目” を絞る（勝手にrole追加とかを防ぐ）**

---

## 2) なぜ「分ける」だけで一気に安全になるの？😳🔒

理由は2つあります👇

## 理由A：操作ごとに“危険の種類”が違う💣

* **create**：変なデータを作られる（スパム・巨大データ・型崩れ）😵
* **update**：権限フィールドを書き換えられる（role / isAdmin など）😱
* **delete**：データ消滅（復旧が地獄）😭🔥

## 理由B：見えるデータが違う（＝検査できる範囲が違う）🔍

* **resource.data**：今DBにある “元データ”
* **request.resource.data**：これから書き込まれる “新データ”

特に重要👇
**delete では request.resource.data が使えない** ので、create/update と同じ検証を書けません⚠️
だから “一括で allow write” すると、検証が崩れやすいです😵‍💫 ([Zenn][2])

---

## 3) 今日のハンズオン：投稿（posts）で体験しよう📌✨

## サンプルのドキュメント構造（例）

`posts/{postId}` に、こんな形で保存する想定👇

* `uid`：作成者のuid👤
* `title`：タイトル📝
* `body`：本文📄
* `status`：`draft` / `public`（下書き/公開）🔒🌍
* `updatedAt`：更新日時🕒（今回は必須にしないでOK）

---

## 4) ルール実装（create / update / delete を分ける）🧩🔐

ポイントはこの3つです👇
✅ **create：本人のuidで作るだけ許可**
✅ **update：本人の投稿だけ更新OK ＋ “変えていい項目” を限定**
✅ **delete：管理者のみ**（この章のゴール🎯）

```ts
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {

    function signedIn() {
      return request.auth != null;
    }

    // 管理者フラグ（あとで Custom Claims 章でちゃんと作る前提の形）
    function isAdmin() {
      return signedIn() && request.auth.token.admin == true;
    }

    function creatingOwnDoc() {
      return signedIn() && request.resource.data.uid == request.auth.uid;
    }

    function owningExistingDoc() {
      return signedIn() && resource.data.uid == request.auth.uid;
    }

    match /posts/{postId} {

      // ✅ create：新規作成だけ許可
      allow create: if creatingOwnDoc()
        // “変な項目を勝手に追加” を防ぐ（最小権限の超重要テク）
        && request.resource.data.keys().hasOnly(['uid','title','body','status','updatedAt'])
        // 入力の型チェック（最低限）
        && request.resource.data.title is string
        && request.resource.data.title.size() >= 1
        && request.resource.data.title.size() <= 60
        && request.resource.data.body is string
        && request.resource.data.body.size() <= 5000
        && request.resource.data.status in ['draft','public'];

      // ✅ update：既存更新だけ許可（本人のみ）
      allow update: if owningExistingDoc()
        // uid は絶対に変更させない（なりすまし防止）
        && request.resource.data.uid == resource.data.uid
        // 更新で触っていいキーを限定（権限昇格防止）
        && request.resource.data.diff(resource.data).affectedKeys()
              .hasOnly(['title','body','status','updatedAt']);

      // ✅ delete：管理者のみ（事故が一番ヤバいので強めに）
      allow delete: if isAdmin();

      // ※読み取りは第8章でやってるので、ここでは省略でもOK
    }
  }
}
```

* `keys().hasOnly([...])` は「余計なフィールドを混ぜて送ってくる攻撃」を止める超強力なやつです🛡️✨ ([Firebase][3])
* `diff(...).affectedKeys()` は「どのフィールドが変わったか」を見て、更新範囲を縛れます👍（Rules機能の改善で使いやすくなった流れがあります） ([The Firebase Blog][4])

---

## 5) 手を動かす（3分で “違い” を体感）🧑‍💻⚡

## ① create だけOKを体験🆕

* 自分の `uid` で作る → ✅通る
* 別の `uid` で作る（なりすまし） → ❌落ちる

## ② update の “変更できる項目だけ” を体験✏️

* `title` を変更 → ✅通る
* `uid` を変更しようとする → ❌落ちる
* `role: "admin"` とか勝手に足す → ❌落ちる（keys/diffで止まる）

## ③ delete が “管理者のみ” を体験🗑️

* 一般ユーザーで delete → ❌落ちる
* 管理者で delete → ✅通る（※ admin クレームが付いてる想定）

---

## 6) ルールをテストで固める（ここが一番大事）🧪🧯

Firestore のルールは **エミュレータ + 単体テスト** で安全に確認できます✅ ([Firebase][5])
テスト用ライブラリは **@firebase/rules-unit-testing** が公式ルートです🧰 ([Firebase][6])

例：**「一般ユーザーはdeleteできない」「adminだけdeleteできる」** をテストで固定👇

```ts
import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { initializeTestEnvironment, assertFails, assertSucceeds } from "@firebase/rules-unit-testing";

const projectId = "demo-rules-ch9";

let testEnv;

test("setup", async () => {
  testEnv = await initializeTestEnvironment({
    projectId,
    firestore: {
      rules: readFileSync("firestore.rules", "utf8"),
    },
  });
});

test("user can create own post", async () => {
  const alice = testEnv.authenticatedContext("alice").firestore();
  await assertSucceeds(
    alice.collection("posts").doc("p1").set({
      uid: "alice",
      title: "hello",
      body: "body",
      status: "draft",
      updatedAt: null,
    })
  );
});

test("user cannot delete (admin only)", async () => {
  // seed（ルール無視で事前データを作る）
  await testEnv.withSecurityRulesDisabled(async (ctx) => {
    await ctx.firestore().collection("posts").doc("p_del").set({
      uid: "alice",
      title: "to delete",
      body: "x",
      status: "draft",
      updatedAt: null,
    });
  });

  const alice = testEnv.authenticatedContext("alice").firestore();
  await assertFails(alice.collection("posts").doc("p_del").delete());
});

test("admin can delete", async () => {
  const admin = testEnv.authenticatedContext("root", { admin: true }).firestore();
  await assertSucceeds(admin.collection("posts").doc("p_del").delete());
});
```

こういうテストがあると👇
「うっかりルール変更で delete が開く事故😱」を **CIでも防げる** ようになります🧯✨

---

## 7) AIで爆速に叩き台を作る（でも最後は人間チェック）🤖✅

## Antigravity / Gemini CLI でできること🧠✨

* Firebase の **MCP サーバー**を使うと、AIが Firebase 作業を手伝えるようになります（Antigravity / Gemini CLI / Firebase Studio など） ([Firebase][7])
* **Gemini CLI の Firebase 拡張**には、Security Rules とテストの生成・検証を助けるプロンプトが用意されています🧰 ([Firebase][8])
* ただし現時点では、少なくともこの “Write security rules” 系は **Firestore と Cloud Storage 向け**が中心で、Realtime Database には未対応の制約があります⚠️ ([Firebase][8])
* プロンプトカタログ自体も更新されています（2026-02-05更新のページが見えています）📚✨ ([Firebase][9])

## AIに投げる指示のテンプレ（例）📝🤖

* コレクション：posts
* フィールド：uid/title/body/status/updatedAt
* ルール：create=本人のみ、update=本人のみ＋変更キー限定、delete=adminのみ
* “攻撃シミュレーション”：uid差し替え、role追加、巨大文字列、delete乱用
* 生成物：`firestore.rules` とテスト（成功✅/失敗❌の両方）

👉 AIが作ったら、**必ず** この章のチェックリスト（次）で人間レビューしてね🙆‍♂️✨

---

## 8) ミニ課題🎯（10分）

次の3つを満たすように、ルールを微調整してみてください👇

1. **create**：`status` は作成時は必ず `draft` に固定（public を作れない）🔒
2. **update**：`status` を `draft→public` にするのはOK、`public→draft` はNG（例）🔁
3. **delete**：一般ユーザーは絶対NG、adminだけOK👑

---

## 9) チェック✅（ここまでできたら勝ち！🏁✨）

* ✅ create で “他人uid” を弾けた？
* ✅ update で “uid変更” を弾けた？
* ✅ update で “余計なフィールド追加” を弾けた？
* ✅ delete は admin だけ通った？
* ✅ エミュレータのテストで ✅/❌ が固定できた？ ([Firebase][5])

---

## おまけ：サーバー側で削除する設計もアリだよ🧠🧰

「管理者UI（クライアント）から delete」じゃなくて、**サーバー（Functions等）で削除**に寄せる手もあります👍
ただしサーバー用ライブラリは **Rulesをバイパス**するので、IAMやサーバー側の認可が別途必要です⚠️ ([Firebase][5])
（Functions を使うなら Node.js は 20/22 が主力、18は deprecated 扱いの流れです） ([Firebase][10])

---

次は第10章（入力検証：必須フィールドと型）で、**create/update の安全度をさらに上げる**やつに入れます🧱🧠✨

[1]: https://stackoverflow.com/questions/59061664/difference-between-allow-write-and-allow-create-update-in-firebase-database-rule?utm_source=chatgpt.com "Difference between allow write and allow create update in ..."
[2]: https://zenn.dev/go5go69/articles/0ec1fcf74a8d36?utm_source=chatgpt.com "Firestoreのセキュリティルールでフィールドの値を利用する ..."
[3]: https://firebase.google.com/docs/firestore/security/rules-fields?utm_source=chatgpt.com "Control access to specific fields | Firestore - Firebase - Google"
[4]: https://firebase.blog/posts/2020/06/new-firestore-security-rules-features/?utm_source=chatgpt.com "New improvements to Firestore Security Rules"
[5]: https://firebase.google.com/docs/firestore/security/test-rules-emulator?utm_source=chatgpt.com "Test your Cloud Firestore Security Rules - Firebase - Google"
[6]: https://firebase.google.com/docs/reference/emulator-suite/rules-unit-testing/rules-unit-testing?utm_source=chatgpt.com "rules-unit-testing package - Firebase"
[7]: https://firebase.google.com/docs/ai-assistance/mcp-server?utm_source=chatgpt.com "Firebase MCP server | Develop with AI assistance - Google"
[8]: https://firebase.google.com/docs/ai-assistance/prompt-catalog/write-security-rules?utm_source=chatgpt.com "AI Prompt: Write Firebase Security Rules"
[9]: https://firebase.google.com/docs/ai-assistance/prompt-catalog?utm_source=chatgpt.com "AI prompt catalog for Firebase | Develop with AI assistance"
[10]: https://firebase.google.com/docs/functions/manage-functions?utm_source=chatgpt.com "Manage functions | Cloud Functions for Firebase - Google"
