# 第7章：参照の持ち方（id文字列 vs DocumentReference）🔗

この章は「投稿（post）やコメント（comment）が、作者（user）をどう指すか？」を**設計で迷わない**ようにする回です😄✨
参照の持ち方は、**UIの落ち方（退会ユーザー表示）**や、**Rulesの書きやすさ**や、**移行のしやすさ**に直結します⚠️

---

## 0) まずは超ざっくり結論🧠💡

![String ID vs Document Reference](./picture/firebase_firestore_struncture_ts_study_007_01_string_id_vs_ref_obj.png)

* **迷ったら `authorId: string`（UID文字列）**が最強にラクです💪✨
  → Rulesが書きやすい、データ移行が楽、参照切れ対応もシンプル😊
* **「参照を“型”として扱いたい / 間違いを減らしたい / 参照でwhereしたい」**なら `authorRef: DocumentReference` が便利です🔗✨
  → ただし、Rulesや移行で少しクセが出ます😇

Firestoreには**Reference型（参照型）**があり、参照は「プロジェクト/DB/ドキュメントへのパス」で表現されます。([Firebase][1])
そしてSDKの `DocumentReference` は「ドキュメントの場所を指すだけ」で、その先が存在する保証はありません（参照切れは普通に起きます）([Firebase][2])

---

## 読む📖：2つの参照パターンを “同じ例” で比べる🧩

題材：`posts/{postId}` に「作者」を持たせたい✍️

---

## A案：`authorId: string`（おすすめ🥇）

**保存する形（例）**

* `posts/{postId}`

  * `authorId: "uid_abc..."`
  * `authorName: "こみやんま"`（表示用スナップショット：任意）
  * `authorPhotoURL: "..."`（任意）

**メリット✅**

* Rulesが書きやすい（`request.auth.uid` と比較するだけ）🛡️
* 退会ユーザーでもUIが落ちにくい（`authorName` を残せる）🙂
* データのエクスポート/移行が分かりやすい📦✨

**デメリット⚠️**

* 作者の詳細を読むなら `doc(db,'users', authorId)` を組み立てる必要がある（慣れれば一瞬😄）

---

## B案：`authorRef: DocumentReference`（ハマると気持ちいい😎）

**保存する形（例）**

* `posts/{postId}`

  * `authorRef: /users/uid_abc...`（Reference型）([Firebase][1])

**メリット✅**

* コードで `getDoc(authorRef)` できて気持ちいい✨
* 「参照そのもの」を値として扱えるので、ミス（コレクション名のタイプミス等）が減りやすい🧯
* 参照一致で `where('authorRef','==', doc(...))` が書ける🔎

**デメリット⚠️**

* Rules側での比較がちょいクセ（後述）😇
* 参照は「場所」なので、移行（パス変更）時に更新が必要になることがある📦💥
* 参照切れは普通に起きる（参照先が消えてもフィールドは残る）([Firebase][2])

---

## 手を動かす🛠️：両方の書き方を “同じ操作” で実装する🔥

ここでは **投稿の作成 → 一覧取得 → 詳細で作者表示** をやります😄✨
（コードは最小で、コピペしやすくしてます📎）

---

## 1) `authorId: string` で投稿を作る✍️（まずこれでOK）

```ts
import { addDoc, collection, getDoc, doc, serverTimestamp } from "firebase/firestore";
import { db } from "./firebase"; // いつもの初期化済みdb

type PostCreateInput = {
  title: string;
  body: string;
  authorId: string;          // ← 参照はUID文字列
  authorName?: string;       // ← 表示用（任意）
  authorPhotoURL?: string;   // ← 表示用（任意）
};

export async function createPost(input: PostCreateInput) {
  const postsCol = collection(db, "posts");

  const newDoc = await addDoc(postsCol, {
    title: input.title,
    body: input.body,
    authorId: input.authorId,
    authorName: input.authorName ?? null,
    authorPhotoURL: input.authorPhotoURL ?? null,
    createdAt: serverTimestamp(),
    updatedAt: serverTimestamp(),
  });

  return newDoc.id;
}
```

✅ポイント

* `authorName` みたいな**表示用スナップショット**を入れておくと、後でUIが超強くなります💪✨
* 退会/削除で `users/{uid}` が消えても「投稿一覧」は普通に描画できるようになります🙂

---

## 2) 投稿詳細で「作者ドキュメント」を読む（必要なときだけ）👤

![Broken Reference Handling](./picture/firebase_firestore_struncture_ts_study_007_02_broken_reference.png)

```ts
import { getDoc, doc } from "firebase/firestore";
import { db } from "./firebase";

export async function getAuthorById(authorId: string) {
  const userRef = doc(db, "users", authorId);
  const snap = await getDoc(userRef);

  // 参照切れ（退会など）でも落とさない😇
  if (!snap.exists()) {
    return { displayName: "退会ユーザー", photoURL: null };
  }

  const data = snap.data() as { displayName?: string; photoURL?: string };
  return {
    displayName: data.displayName ?? "名無し",
    photoURL: data.photoURL ?? null,
  };
}
```

---

## 3) `authorRef: DocumentReference` で投稿を作る🔗（B案）

```ts
import { addDoc, collection, doc, serverTimestamp, DocumentReference } from "firebase/firestore";
import { db } from "./firebase";

export async function createPostWithRef(params: {
  title: string;
  body: string;
  authorId: string;
}) {
  const authorRef = doc(db, "users", params.authorId) as DocumentReference;

  const postsCol = collection(db, "posts");
  const newDoc = await addDoc(postsCol, {
    title: params.title,
    body: params.body,
    authorRef,                 // ← 参照型をそのまま保存
    createdAt: serverTimestamp(),
    updatedAt: serverTimestamp(),
  });

  return newDoc.id;
}
```

✅ここで大事：
`DocumentReference` は「場所」を指すだけです。参照先が無い可能性は常にあるので、UIは必ず保険をかけます🧯([Firebase][2])

---

## 4) 投稿詳細で `authorRef` を使って作者を読む👀

```ts
import { getDoc, DocumentReference } from "firebase/firestore";

export async function getAuthorByRef(authorRef: DocumentReference) {
  const snap = await getDoc(authorRef);

  if (!snap.exists()) {
    return { displayName: "退会ユーザー", photoURL: null };
  }

  const data = snap.data() as { displayName?: string; photoURL?: string };
  return {
    displayName: data.displayName ?? "名無し",
    photoURL: data.photoURL ?? null,
  };
}
```

---

## 退会ユーザー（参照切れ）を “仕様にする” 🧱✨

参照切れは「バグ」じゃなくて**仕様として起きる**ので、先に決めちゃうのが勝ちです😄

おすすめの落とし所👇

* 投稿/コメントには **表示用スナップショット（`authorName` など）**を入れる
* 作者が消えても一覧は描画できる
* 詳細で作者が必要なら `users/{uid}` を読みに行く（無ければ “退会ユーザー”）

このやり方だと、読み回数（コスト）も減りやすいです💰✨

---

## Rules目線🛡️：`authorId` がラクな理由（超重要）🔥

![Security Rules Comparison](./picture/firebase_firestore_struncture_ts_study_007_03_rules_comparison.png)

## ✅ `authorId: string` なら Rules が一瞬

```js
service cloud.firestore {
  match /databases/{database}/documents {
    match /posts/{postId} {
      allow create: if request.auth != null
        && request.resource.data.authorId == request.auth.uid;

      allow update, delete: if request.auth != null
        && resource.data.authorId == request.auth.uid;

      allow read: if true;
    }
  }
}
```

---

## 🔗 `authorRef` でやる場合の考え方

Security Rules の型チェックでは `path` が使えます。([Firebase][3])
FirestoreのReference型は「パスで表現される」ので([Firebase][1])、Rules側では **“パスとして比較する” 発想**が分かりやすいです🙂（※ここは実装時にエミュレータで必ず確認してね✅）

さらに、Rules内で別ドキュメントを読む `get()` / `exists()` は **1リクエストあたり最大10回**という制限があるので、参照チェックを増やしすぎないのも大事です⚠️([Firebase][4])

---

## AIで加速🤖⚡：設計レビュー＆事故潰しを自動化する

## 1) Antigravityで “2案比較→採用→実装” を一気に進める🛰️

Antigravityはエージェントが計画して作業を進めるIDE（Mission Control的な発想）です🧠✨([Google Codelabs][5])
第7章みたいな「設計の分岐」は相性バツグンです😄

**投げる指示例（そのままコピペOK）📎**

* 「`authorId`案と`authorRef`案を、Rulesの書きやすさ・移行・参照切れ対応・読み回数コストで比較して、今回の“日報/記事/コメント”に最適な案を決めて。決めた案で型とCRUD関数も生成して」

---

## 2) Gemini CLIで “ターミナルから設計・実装・テスト” 🔧

Gemini CLIはターミナルで動くAIエージェントで、ReActループで作業を進めます🧠🛠️([Google for Developers][6])

**投げる指示例📎**

* 「`posts` と `comments` の参照設計（author）を見直したい。参照切れ時にUIが落ちない仕様、Rulesの条件例、Firestoreの読み回数最小化まで含めて提案して」

---

## 3) Firebase AI Logicで “AI機能の乱用＆コスト事故” を防ぐ🧯💰

Firebase AI LogicはクライアントSDK＋ゲートウェイでAIを扱える仕組みで([Firebase][7])、**デフォルトで per-user のレート制限（例：100 RPM）**があり、調整も推奨されています⚙️([Firebase][8])

第7章の参照設計とどう関係あるの？🤔
→ **AIが生成した投稿/コメント**をFirestoreに保存するなら、

* 「誰が生成したか（user参照）」
* 「モデル名や監査ログ」
  を残す場面が出ます。ここで参照設計が効きます🧾✨

---

## ミニ課題🎯（15〜25分くらい）

1. `posts` の参照方式を **A（authorId）** か **B（authorRef）** で決める🔗
2. 投稿詳細画面で、作者が消えてても落ちないようにする😇

   * “退会ユーザー” 表示にフォールバック
3. 余裕があれば：投稿一覧では `authorName`（スナップショット）で表示して、作者ドキュメントの追加読み込みを減らす💰✨

---

## チェック✅

* [ ] 参照は「JOIN」じゃなく「場所」だと説明できる🔗
* [ ] 参照切れ（退会/削除）でUIが落ちない🙂
* [ ] Rulesがシンプルに書ける（または `path` 比較の方針が立ってる）🛡️([Firebase][3])
* [ ] `get()/exists()` を増やしすぎない意識がある（最大10回）⚠️([Firebase][4])

---

次の第8章は「一覧に強い設計（並べ替えから逆算）」📜で、**参照の持ち方が“一覧の速さ”にも効く**話に入っていきます😄⚡

[1]: https://firebase.google.com/docs/firestore/manage-data/data-types "Supported data types  |  Firestore  |  Firebase"
[2]: https://firebase.google.com/docs/reference/js/v8/firebase.firestore.DocumentReference "DocumentReference | JavaScript SDK  |  Firebase JavaScript API reference"
[3]: https://firebase.google.com/docs/firestore/security/rules-fields "Control access to specific fields  |  Firestore  |  Firebase"
[4]: https://firebase.google.com/docs/firestore/security/rules-conditions "Writing conditions for Cloud Firestore Security Rules  |  Firebase"
[5]: https://codelabs.developers.google.com/getting-started-google-antigravity "Getting Started with Google Antigravity  |  Google Codelabs"
[6]: https://developers.google.com/gemini-code-assist/docs/gemini-cli "Gemini CLI  |  Gemini Code Assist  |  Google for Developers"
[7]: https://firebase.google.com/docs/ai-logic "Gemini API using Firebase AI Logic  |  Firebase AI Logic"
[8]: https://firebase.google.com/docs/ai-logic/quotas "Rate limits and quotas  |  Firebase AI Logic"