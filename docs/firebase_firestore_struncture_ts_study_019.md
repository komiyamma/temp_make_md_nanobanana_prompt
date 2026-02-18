# 第19章：TypeScriptで型安全CRUD　DTO・Converter・ガード🧱✨

この章のゴールはシンプルです👇😄
**「Firestoreに保存する形」と「UIで使う形」を分けて、読み書きの事故を減らす**こと！
そして、読み出しのたびに「えーい！as で型アサーション！」を卒業します🎓✨

なお、Firebase JS SDK は **12.8.0（2026-01-14）** まで公式リリースノートで確認できます。([Firebase][1])
Firestore の Converter まわりも公式APIに載ってるので、そこに寄せた実装をします💪([Firebase][2])

---

## 読む📚✨　なんで DTO と Converter が必要なの？

Firestore は **DB側でスキーマ（型）を強制しません**。なので「昔のアプリが書いた古い形のデータ」や「Converter無しの別クライアントが書いたデータ」が混ざる可能性があります😇
公式も「変換時に “復旧するか / エラーにするか” を決めてね」と言っています。([Firebase][2])

そこで登場するのがこの3点セット👇

* **DTO（DbModel）**：Firestore に保存する “生の形” 🧱
* **UIモデル（AppModel）**：React が気持ちよく使える形 💖
* **Converter（withConverter）**：読み書き時に自動で変換してくれる橋🌉

  * Converter は「AppModel ↔ DbModel」を自動変換するための仕組みとして定義されています。([Firebase][2])

---

## 手を動かす🖐️🔥　DTO・Converter・CRUD を作る

ここでは例として「posts」と「comments」を想定します📝
（あなたのロードマップの「日報/記事/コメント」の “記事/コメント” にそのまま対応できます👌）

## 0) Firebase を入れる📦

Firebase のWebセットアップは npm 前提の手順が公式にあります。([Firebase][3])

```bash
npm install firebase
```

---

## 1) 型を2つに分ける🧩　UI用と保存用

ポイントはここ👇😄
Firestore は Timestamp を返すけど、UI は Date の方が扱いやすい！みたいなズレを吸収します。

* **UI用（AppModel）**：Date を使う
* **保存用（DbModel / DTO）**：Timestamp を使う

```ts
// src/features/posts/types.ts
import type { Timestamp, FieldValue } from "firebase/firestore";

// UIで使う形（Reactが嬉しい）
export type Post = {
  id: string;
  title: string;
  body: string;
  authorId: string;
  authorName: string;
  createdAt: Date;
  updatedAt: Date;
  commentCount: number;
};

// Firestoreに保存する形（DTO）
export type PostDTO = {
  title: string;
  body: string;
  authorId: string;
  authorName: string;
  createdAt: Timestamp;
  updatedAt: Timestamp;
  commentCount: number;
};

// 書き込み時だけ許したい形（serverTimestamp など）
export type PostWrite = Omit<Post, "id" | "createdAt" | "updatedAt"> & {
  createdAt: Date | FieldValue;
  updatedAt: Date | FieldValue;
};
```

---

## 2) ガードを書く🛡️　Firestoreは型を保証しないので最後は自分で守る

「Converter があるから安全！」…と言いたいけど、**DBに変なデータが入ってたら終わり**です😇
だから **fromFirestore の中で検査**します。

```ts
// src/features/posts/guards.ts
import { Timestamp } from "firebase/firestore";
import type { PostDTO } from "./types";

function isNonEmptyString(v: unknown): v is string {
  return typeof v === "string" && v.trim().length > 0;
}

function isNumber(v: unknown): v is number {
  return typeof v === "number" && Number.isFinite(v);
}

function isTimestamp(v: unknown): v is Timestamp {
  return v instanceof Timestamp;
}

export function assertPostDTO(data: any): asserts data is PostDTO {
  if (!data || typeof data !== "object") throw new Error("PostDTO: not an object");

  if (!isNonEmptyString(data.title)) throw new Error("PostDTO.title invalid");
  if (!isNonEmptyString(data.body)) throw new Error("PostDTO.body invalid");
  if (!isNonEmptyString(data.authorId)) throw new Error("PostDTO.authorId invalid");
  if (!isNonEmptyString(data.authorName)) throw new Error("PostDTO.authorName invalid");

  if (!isTimestamp(data.createdAt)) throw new Error("PostDTO.createdAt invalid");
  if (!isTimestamp(data.updatedAt)) throw new Error("PostDTO.updatedAt invalid");

  if (!isNumber(data.commentCount)) throw new Error("PostDTO.commentCount invalid");
}
```

公式も「Firestore はスキーマを強制しないので、変換時にどう扱うか決めてね」と明記しています。([Firebase][2])
ここでは “壊れてたら落とす” を選びました（最初はこれが一番気づけて安全）💥

---

## 3) Converter を作る🌉✨　withConverter の本体

Converter の型定義（toFirestore / fromFirestore）は公式に載っています。([Firebase][2])
また、**merge を使うなら PartialWithFieldValue を扱える形にしてね** という注意も公式にあります。([Firebase][2])

```ts
// src/features/posts/converter.ts
import {
  Timestamp,
  serverTimestamp,
  type FirestoreDataConverter,
  type QueryDocumentSnapshot,
  type SnapshotOptions,
  type WithFieldValue,
  type PartialWithFieldValue,
} from "firebase/firestore";

import type { Post, PostDTO, PostWrite } from "./types";
import { assertPostDTO } from "./guards";

function omitUndefined<T extends Record<string, any>>(obj: T): T {
  return Object.fromEntries(Object.entries(obj).filter(([, v]) => v !== undefined)) as T;
}

function toDbTimestamp(v: unknown): any {
  // Date → Timestamp
  if (v instanceof Date) return Timestamp.fromDate(v);
  // serverTimestamp() など FieldValue はそのまま通す
  return v;
}

export const postConverter: FirestoreDataConverter<Post, PostDTO> = {
  toFirestore(model: WithFieldValue<Post> | PartialWithFieldValue<Post>) {
    const m: any = model;

    // 重要：undefined を Firestore に投げない（投げるとエラーになりがち）
    return omitUndefined({
      title: m.title,
      body: m.body,
      authorId: m.authorId,
      authorName: m.authorName,
      createdAt: toDbTimestamp(m.createdAt),
      updatedAt: toDbTimestamp(m.updatedAt),
      commentCount: m.commentCount,
    }) as any;
  },

  fromFirestore(snapshot: QueryDocumentSnapshot, options?: SnapshotOptions): Post {
    const data = snapshot.data(options);

    // ここで “壊れてたら即発見” 💥
    assertPostDTO(data);

    return {
      id: snapshot.id,
      title: data.title,
      body: data.body,
      authorId: data.authorId,
      authorName: data.authorName,
      createdAt: data.createdAt.toDate(),
      updatedAt: data.updatedAt.toDate(),
      commentCount: data.commentCount,
    };
  },
};

// 作成時に使う便利ヘルパ（UIからはこれだけ触ればOKにする）
export function buildNewPostWrite(input: {
  title: string;
  body: string;
  authorId: string;
  authorName: string;
}): PostWrite {
  return {
    title: input.title,
    body: input.body,
    authorId: input.authorId,
    authorName: input.authorName,
    createdAt: serverTimestamp(),
    updatedAt: serverTimestamp(),
    commentCount: 0,
  };
}
```

---

## 4) 型安全 CRUD を “関数” に閉じ込める📦✨

React コンポーネントが Firestore の細かい事情を知り始めると、すぐ散らかります😵
なので **Repository（読み書き関数）に寄せます**。

```ts
// src/features/posts/repository.ts
import {
  collection,
  doc,
  getDoc,
  getDocs,
  query,
  orderBy,
  limit,
  setDoc,
  deleteDoc,
  type Firestore,
} from "firebase/firestore";

import type { Post } from "./types";
import { postConverter, buildNewPostWrite } from "./converter";

export function postsCollection(db: Firestore) {
  return collection(db, "posts").withConverter(postConverter);
}

export async function createPost(db: Firestore, input: {
  title: string;
  body: string;
  authorId: string;
  authorName: string;
}): Promise<string> {
  const col = postsCollection(db);
  const ref = doc(col); // 自動ID
  await setDoc(ref, buildNewPostWrite(input) as any);
  return ref.id;
}

export async function getPost(db: Firestore, postId: string): Promise<Post | null> {
  const ref = doc(postsCollection(db), postId);
  const snap = await getDoc(ref);
  return snap.exists() ? (snap.data() as Post) : null;
}

export async function listLatestPosts(db: Firestore, n = 20): Promise<Post[]> {
  const q = query(postsCollection(db), orderBy("createdAt", "desc"), limit(n));
  const snaps = await getDocs(q);
  return snaps.docs.map((d) => d.data());
}

export async function updatePostTitle(db: Firestore, postId: string, title: string): Promise<void> {
  // ✅ updateDoc は Converter を使ってくれません（重要）ので、
  // setDoc(merge:true) で更新するのが安全寄り
  const ref = doc(postsCollection(db), postId);
  await setDoc(ref, { title, updatedAt: new Date() } as any, { merge: true });
}

export async function deletePost(db: Firestore, postId: string): Promise<void> {
  const ref = doc(postsCollection(db), postId);
  await deleteDoc(ref);
}
```

---

## 超重要⚠️　updateDoc の罠に注意

公式の例でもハッキリ書かれてます👇
**Converter は setDoc / addDoc / getDoc では使われるけど、updateDoc の書き込みでは使われません**。([Firebase][2])

つまり、こういう事故が起きます😱

* UIモデルの「Date」をそのまま updateDoc で投げる
* 本当は DTO の「Timestamp」であるべき
* 変なデータが混ざる
* 次回読み込みでガードが爆発💥（でもこれは早期発見できて良い！）

なのでこの章では、更新は基本👇でいきます😊

* **更新は setDoc + merge:true** を第一候補にする✨([Firebase][2])

---

## React 側での使い方イメージ⚛️✨

「型がついてる」気持ちよさを味わうところです😆

```tsx
// src/features/posts/PostList.tsx
import { useEffect, useState } from "react";
import type { Firestore } from "firebase/firestore";
import type { Post } from "./types";
import { listLatestPosts } from "./repository";

export function PostList({ db }: { db: Firestore }) {
  const [posts, setPosts] = useState<Post[]>([]);

  useEffect(() => {
    (async () => {
      const data = await listLatestPosts(db, 20);
      setPosts(data);
    })();
  }, [db]);

  return (
    <div>
      <h2>最新記事📰</h2>
      {posts.map((p) => (
        <div key={p.id} style={{ borderBottom: "1px solid #ddd", padding: 8 }}>
          <div style={{ fontWeight: 700 }}>{p.title}</div>
          <div>by {p.authorName} 👤</div>
          <div>{p.createdAt.toLocaleString()}</div>
          <div>コメント {p.commentCount} 💬</div>
        </div>
      ))}
    </div>
  );
}
```

---

## AI でこの章を “倍速” にする🤖⚡

## 1) Antigravity で設計レビューを回す🧠🛠️

Antigravity は「エージェントが計画→実行→検証」を回す “Mission Control” 的な思想が公式Codelabにあります。([Google Codelabs][4])
ここでやると強いのは👇

* DTO と UI モデルの **差分レビュー**
* Converter の **漏れフィールド検出**
* ガードの **チェック項目の提案**

依頼文の例（そのまま貼れるやつ）👇📎

* 「Post/PostDTO/Converter/Guard を見て、事故りやすい点と修正案を出して。特に updateDoc の混入リスクもチェックして」

---

## 2) Gemini CLI に雛形を作らせる🧱✨

Gemini CLI はターミナルで動くAIエージェントで、ReAct ループで作業を進める説明があります。([Google Cloud Documentation][5])
生成させると美味しいのは👇

* Converter の雛形
* omitUndefined などの小物関数
* ガードのパターン（必須・型・範囲）

---

## 3) Firebase AI Logic と Firestore をつなぐ時の注意🧯

Firebase AI Logic はアプリ向けの仕組みで、Firestore など Firebase の他サービスとも組み合わせられることが公式に説明されています。([Firebase][6])
ただし本番を考えるなら👇は必ず意識😄

* **デフォルトのユーザー別レート制限**（例：100 RPM / user）([Firebase][7])
* **App Check で不正クライアントをブロック**（AI Logic は App Check と連携できる）([Firebase][8])

この章の型安全CRUDと相性がいいのは、AIの出力を Firestore に保存するとき👇

* 「AIログ」「要約」「タグ」みたいな **構造化データ**を DTO で固定して、Converter + ガードで守る🛡️✨

---

## 4) Genkit で “構造化出力” を取る発想📦✨

Genkit はスキーマを定義して、LLM から **構造化データを返させる**流れが紹介されています。([Firebase][9])
これを Firestore に保存するなら、まさに DTO/Converter/ガードの出番です😆

---

## ミニ課題📝🔥　AI 由来のデータを型安全に保存してみよう

## お題🎯

記事（Post）に「AI要約」を付けたい！✨

* UIでは「summaryText: string」だけ欲しい
* DBには「summaryText / model / createdAt」を保存したい
* 変な形が入ったらガードで落とす

## やること✅

1. Post に UI用フィールド（summaryText）を追加
2. PostDTO に保存用フィールド（summaryText, summaryModel, summaryCreatedAt）を追加
3. Converter に変換を追加
4. ガードにチェックを追加
5. AI Logic または Genkit で生成した summary を保存（まずはダミー文字列でもOK😄）

---

## チェック✅✨　この章を終えたら勝ち！

* DTO と UI モデルの “ズレ” を **意図して設計**できる😄
* Converter の fromFirestore で **ガードしてる**（事故が即発見できる）🛡️
* updateDoc の罠を避けて **setDoc + merge** で更新できる⚠️([Firebase][2])
* React 側が Firestore の都合を知らずに **型だけで気持ちよく描画**できる💖
* AI の出力も DTO に落として **保存の事故を減らせる**🤖✨([Firebase][7])

---

次の第20章（整合性をサーバー側で守る）に進むと、この章で作った DTO/Converter/ガードがそのまま “堅牢な土台” になりますよ〜😄⚙️

[1]: https://firebase.google.com/support/release-notes/js?utm_source=chatgpt.com "Firebase JavaScript SDK Release Notes - Google"
[2]: https://firebase.google.com/docs/reference/js/firestore_.firestoredataconverter "FirestoreDataConverter interface  |  Firebase JavaScript API reference"
[3]: https://firebase.google.com/docs/web/setup?utm_source=chatgpt.com "Add Firebase to your JavaScript project"
[4]: https://codelabs.developers.google.com/getting-started-google-antigravity?utm_source=chatgpt.com "Getting Started with Google Antigravity"
[5]: https://docs.cloud.google.com/gemini/docs/codeassist/gemini-cli?utm_source=chatgpt.com "Gemini CLI | Gemini for Google Cloud"
[6]: https://firebase.google.com/docs/ai-logic?utm_source=chatgpt.com "Gemini API using Firebase AI Logic - Google"
[7]: https://firebase.google.com/docs/ai-logic/quotas?utm_source=chatgpt.com "Rate limits and quotas | Firebase AI Logic - Google"
[8]: https://firebase.google.com/docs/ai-logic/app-check?utm_source=chatgpt.com "Implement Firebase App Check to protect APIs from ... - Google"
[9]: https://firebase.google.com/codelabs/ai-genkit-rag?utm_source=chatgpt.com "Build gen AI features powered by your data with Genkit"
