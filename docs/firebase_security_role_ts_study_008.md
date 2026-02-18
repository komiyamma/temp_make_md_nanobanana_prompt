# 第8章：最小権限① “読む”の制御（get と list の感覚）📖🔒

この章はズバリ👇
**「1件だけ読める」と「一覧で読める」は別モノ**って体に覚えさせて、**“うっかり全公開😱”を最小権限で潰す**回です🛡️✨

---

## 0) 今日のゴール🎯✨

* `allow read` を雑に書かず、**`get` と `list` を分けて考えられる**🙂
* 「UIで一覧を隠したから安全」みたいな幻想を捨てて、**Rulesで止められる**🧯
* `list` を許す必要があるときに、**安全に許し方を設計できる**（制限＆クエリ整合）🔐

---

## 1) まず結論：`read` は `get` と `list` のセット📦

Firestoreの“読む”は大きく2種類👇

* `get`：**1件取得**（ドキュメントIDを指定して読む）
* `list`：**一覧取得**（コレクションの取得・クエリ・検索）

そして `allow read:` は基本的に **`get` と `list` の両方**を含みます。だから最小権限をやるなら、必要に応じて **`allow get:` と `allow list:` を分ける**のが王道です。([Firebase][1])

---

## 2) “listが怖い”理由：一度開けると吸い出しが速い🚨💨

たとえば「ログインしてたら読める」で `allow read: if request.auth != null` みたいにしていると…

* 攻撃者は自作スクリプトで **コレクションを片っ端からクエリ**できる
* 画面に一覧を出してなくても、**APIとしては開いてる**状態😇💥

つまり、**UIで隠す≠守る**です🙅‍♂️

---

## 3) 体験①：`get` だけ許可して、`list` を禁止してみる🧪

まずは“差”を体感しましょう🙂
例：`/posts/{postId}` に対して「1件はOK、一覧はNG」

```rules
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {

    match /posts/{postId} {
      // ✅ 1件取得はOK
      allow get: if true;

      // ❌ 一覧（クエリ）は禁止
      allow list: if false;
    }
  }
}
```

これで起きること👇

* ✅ `getDoc(doc(db, "posts", "abc"))` → 通る
* ❌ `getDocs(collection(db, "posts"))` → **Missing or insufficient permissions** になる

「一覧がダメ」って、こういうことか〜！が掴めます😆✨

---

## 4) React側で“getとlistの違い”を手で確認🖐️⚡

Firestore（Web SDK）だと、だいたいこう覚えるとラクです👇

* `getDoc(doc(...))` → **get**
* `getDocs(collection(...))` / `getDocs(query(...))` → **list**

サンプル（最低限）👇

```ts
import { getFirestore, doc, getDoc, collection, getDocs } from "firebase/firestore";

const db = getFirestore();

export async function tryGet(postId: string) {
  const snap = await getDoc(doc(db, "posts", postId));
  console.log("get:", snap.exists() ? snap.data() : "not found");
}

export async function tryList() {
  const snaps = await getDocs(collection(db, "posts"));
  console.log("list:", snaps.docs.map(d => d.id));
}
```

`tryGet()` は通るのに `tryList()` は落ちる、が見えたら勝ちです🏆✨

---

## 5) 体験②：`list` を「安全に」開ける3つの手札🃏🔐

アプリって、たいてい一覧が欲しいですよね🙂
だから次は「どう安全にlistを許すか」をやります！

## 手札A：公開データだけ一覧OK（`published == true`）🌍📣

「公開済みだけ読める」なら、listを許しても被害が小さいです。

ただし超重要👇
**Rulesはフィルタじゃない**ので、「読めないデータが混ざる可能性」があるクエリは **丸ごと失敗**します。([Firebase][2])

つまり、Rules側で `resource.data.published == true` を条件にしているなら、クエリ側も `where("published","==",true)` を入れて「絶対に公開しか返らない」形にする必要があります✅([Firebase][2])

---

## 手札B：取得件数を制限（`request.query.limit`）🧯📉

一覧OKでも「一気に1万件」はダメ！ってしたいですよね😇
Rulesでは **limitの有無/上限**をチェックできます。

公式ドキュメントでも `allow list: if request.query.limit <= 10;` のように書ける例が出ています。([Firebase][2])

---

## 手札C：「getは緩め」「listは厳しめ」に分ける👮‍♂️

典型例👇

* `get`：本人の下書きでも読める
* `list`：公開だけ、さらにlimit必須

まずはこの形がめちゃくちゃ安全に寄ります🛡️✨

---

## 6) “公開記事はlist OK、下書きはNG”の例（章タイトルのやつ！）📝🔒

想定データ（例）👇
`posts/{postId}` に

* `published: true/false`
* `authorUid: "..."`

Rules👇

```rules
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    function signedIn() { return request.auth != null; }
    function isOwner()  { return signedIn() && request.auth.uid == resource.data.authorUid; }
    function isPublic() { return resource.data.published == true; }

    match /posts/{postId} {

      // ✅ get：公開 or 本人ならOK（下書きも本人なら読める）
      allow get: if isPublic() || isOwner();

      // ✅ list：公開だけ + limit必須（例：20件まで）
      allow list: if request.query.limit <= 20 && isPublic();
    }
  }
}
```

ポイント解説🧠✨

* `get` は本人の下書きも読める（便利）
* `list` は公開だけ＆limit縛り（安全）
* これで「下書き一覧を出したい」なら、下書きは **別コレクションに分ける（第7章のuid設計）**のが自然です🙂

---

## 7) “Rulesはフィルタじゃない”をもう一段だけ深掘り🧠💥

Firestoreはクエリを評価するとき、**結果に出そうな集合（potential result set）**に対してRulesチェックします。
だから「たまたま今は全部自分の投稿だけ」でも、クエリが“他人の投稿を含む可能性”がある形だと **失敗**します。([Firebase][2])

この性質のおかげで、設計がちゃんとしてれば **“一覧ダダ漏れ”をクエリ段階で止められる**んですよね🙂🛡️

---

## 8) Emulatorでテスト（ここで“安心”を作る）🧪✅

Rulesは「書いた気になる」のが一番危ないです😱
なのでEmulator + 単体テストで固めましょう！

Firebaseは**Rules単体テスト用ライブラリ**を配布していて、v9系のテスト方式をおすすめしています。([Firebase][3])

イメージ（擬似）👇

```ts
import { initializeTestEnvironment, assertSucceeds, assertFails } from "@firebase/rules-unit-testing";
import { doc, getDoc, collection, getDocs, query, where, limit } from "firebase/firestore";

test("getはOK / listは公開だけOK", async () => {
  // userEnv / db を作って…

  // ✅ 公開postはget OK
  await assertSucceeds(getDoc(doc(db, "posts", "public1")));

  // ✅ 公開一覧は where+limit があるならOK
  await assertSucceeds(getDocs(query(collection(db, "posts"), where("published","==",true), limit(20))));

  // ❌ 下書き一覧は落ちる（公開縛りを満たさない）
  await assertFails(getDocs(query(collection(db, "posts"), where("published","==",false), limit(20))));
});
```

---

## 9) AI活用：Rules＆テストの叩き台を爆速で作る🤖⚡

## 使いどころ🎯

* 「このコレクション構造で、get/listを最小権限にしたRules案ちょうだい」
* 「通るべき✅/落ちるべき❌ テストケースを列挙して」
* 「“一覧で漏れるパターン”を攻撃者視点で洗い出して」

FirebaseのAIプロンプト（Security Rules用）は、**最小権限を狙ってRulesとテストの下書きを作る**ことを目的にしていて、コード解析＆“攻撃シミュレーション”的な反復で穴を探す設計になっています。([Firebase][4])

また、Gemini CLIのFirebase拡張は **Firebase MCPサーバーをセットアップして、事前プロンプト（slash command）を使える**ようにする説明があります。([Firebase][5])

そして Antigravity 側でも Firebase MCP を追加して使う流れが紹介されています。([The Firebase Blog][6])

## 注意⚠️（ここ大事）

* **Admin SDKなどサーバー経由はRulesが呼ばれない**ので、そこは別の認可が必要です（AIプロンプト側の注意にも明記）。([Firebase][4])
* Firebaseコンソール内のGeminiは、この用途（Rules生成）に向いてない旨も書かれています（だからCLI/エージェントを使うのが自然）。([Firebase][4])
  → つまり **AIで作る＝終わりじゃなくて、テストで固める＝終わり**です🧑‍⚖️✅

---

## 10) ミニ課題🎯📝（10分）

次の仕様を満たす設計＆Rules案を作ってください🙂✨

## お題：記事アプリ📰

* 公開記事：誰でも一覧OK（ただし **最大20件**）
* 下書き：本人だけ **1件表示はOK**（URL直打ちでもOK）
* 下書き：本人でも **一覧はNG**（ここがポイント！）

できたら、次も追加🔥

* 「公開一覧は `published==true` が必須」になるように、クエリとRulesをセットで揃える

---

## 11) チェック✅✅（自分採点）

* [ ] `allow read` を雑に使ってない？（get/listに分けた？）([Firebase][1])
* [ ] 一覧（list）に **limit縛り**を入れた？([Firebase][2])
* [ ] 「Rulesはフィルタじゃない」を理解して、クエリ側も条件を揃えた？([Firebase][2])
* [ ] Emulatorのテストで「通る✅/落ちる❌」を自動化した？([Firebase][3])
* [ ] AIの提案を“信じず”、テストとレビューで固めた？🤖🧑‍⚖️([Firebase][4])

---

次の第9章は「書く（create/update/delete）を分ける」なので、今回のget/listの感覚がそのまま効いてきます✍️🧯
必要なら、この第8章のサンプルをベースに **“公開一覧＋本人下書き（別コレクション）”の完成形**も作って渡せますよ🙂✨

[1]: https://firebase.google.com/docs/firestore/security/rules-structure "Structuring Cloud Firestore Security Rules  |  Firebase"
[2]: https://firebase.google.com/docs/firestore/security/rules-query "Securely query data  |  Firestore  |  Firebase"
[3]: https://firebase.google.com/docs/rules/unit-tests?hl=ja "単体テストを作成する  |  Firebase Security Rules"
[4]: https://firebase.google.com/docs/ai-assistance/prompt-catalog/write-security-rules "AI Prompt: Write Firebase Security Rules  |  Develop with AI assistance"
[5]: https://firebase.google.com/docs/ai-assistance/gcli-extension "Firebase extension for the Gemini CLI  |  Develop with AI assistance"
[6]: https://firebase.blog/posts/2025/11/firebase-mcp-and-antigravity/ "Antigravity and Firebase MCP accelerate app development"
