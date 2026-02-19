# 第12章：分散カウンタ（シャーディング）で“書き込み集計”を守る🧱🔥

この章は「いいね数👍」「閲覧数👀」「投票数🗳️」みたいな**カウンタ系**を、アクセス増えても壊れにくくするための“定番の守り方”を身につけます😊✨
（題材：記事 `posts` の **likesCount**）

---

## まず、なにが困るの？（カウンタ直書きの事故）💥

たとえば、記事ドキュメントにこうやって持つのは自然👇

* `posts/{postId}` の中に `likesCount: 123`

でも、いいねが押されるたびに

* `posts/{postId}.likesCount += 1`

をやると…人気記事ほど**1つのドキュメントに書き込みが集中**して詰まりやすいです🔥
Firestoreは「単一ドキュメントをどれくらいの速度で更新できるか」は**ワークロード次第**で、負荷テストで把握してね、というスタンスです（固定の安全値は状況で変わるよ、という話）([Firebase][1])

さらに、限界を超えると `RESOURCE_EXHAUSTED` みたいなエラー（クォータ/書き込みランプアップ制限など）が出ることがあります😵‍💫([Google Cloud Documentation][2])

![Bottleneck Funnel](./picture/firebase_firestore_struncture_ts_study_012_01_bottleneck_funnel.png)

---

## 分散カウンタの発想（1個をN個に割る）🧩✨

そこで登場するのが、Firebase の公式パターン **Distributed counters（分散カウンタ）**です🥇([Firebase][3])

考え方は超シンプル👇

* カウンタを **1個のドキュメント**で持つのをやめる
* 小さなカウンタ（**shard**）を **N個**に分けて持つ
* 合計値は「N個の合計」にする

公式ドキュメントでも「shard数に比例して書き込み耐性が増える」ことが説明されています([Firebase][3])

![Shard Shattering Concept](./picture/firebase_firestore_struncture_ts_study_012_02_shard_shattering.png)

**設計イメージ🧠**

* `posts/{postId}/counters/likes` … カウンタの“箱”
* `posts/{postId}/counters/likes/shards/{shardId}` … 分割カウンタ（N個）

---

## 手を動かす①：データ構造を作る（likesカウンタ）🛠️

まずは「likes用の分散カウンタ」を作ります。
**最初は shard=10 でOK**（学習も分かりやすい）😊

```ts
// パス例（イメージ）
// posts/{postId}/counters/likes/shards/{shardId}
//
// shardId は "0"〜"9" とか文字列でOK
// 各 shard ドキュメントの中身は { count: number } だけでOK
```

---

## 手を動かす②：shardを初期化する（最初に10個作る）🧱

```ts
import { collection, doc, writeBatch, setDoc } from "firebase/firestore";
import type { Firestore } from "firebase/firestore";

export async function initLikeCounter(db: Firestore, postId: string, numShards = 10) {
  const shardsCol = collection(db, "posts", postId, "counters", "likes", "shards");
  const batch = writeBatch(db);

  for (let i = 0; i < numShards; i++) {
    const shardRef = doc(shardsCol, String(i));
    batch.set(shardRef, { count: 0 }, { merge: true });
  }

  await batch.commit();
}
```

ポイント😊

* `merge: true` にしておくと「すでにあっても壊しにくい」👍

---

## 手を動かす③：いいねを +1 する（ランダム shard に書く）🎯👍

書き込みが集中しないように、**毎回ランダムな shard を選んで** `count` を増やします。

```ts
import { collection, doc, setDoc, increment } from "firebase/firestore";
import type { Firestore } from "firebase/firestore";

export async function incrementLike(db: Firestore, postId: string, numShards = 10) {
  const shardsCol = collection(db, "posts", postId, "counters", "likes", "shards");
  const shardId = Math.floor(Math.random() * numShards);
  const shardRef = doc(shardsCol, String(shardId));

  // increment() は衝突に強い原子的更新（同時押しでもズレにくい）
  await setDoc(shardRef, { count: increment(1) }, { merge: true });
}
```

![Random Shard Selection](./picture/firebase_firestore_struncture_ts_study_012_03_roulette_selection.png)

---

## 手を動かす④：合計値を読む（全 shard を読んで合計）📚➕📚

分散した分、読むときは合計が必要です（ここがトレードオフ⚖️）。

```ts
import { collection, getDocs } from "firebase/firestore";
import type { Firestore } from "firebase/firestore";

export async function getLikesCount(db: Firestore, postId: string) {
  const shardsCol = collection(db, "posts", postId, "counters", "likes", "shards");
  const snap = await getDocs(shardsCol);

  let total = 0;
  snap.forEach((d) => {
    const data = d.data() as { count?: number };
    total += data.count ?? 0;
  });

  return total;
}
```

![Read Cost Trade-off](./picture/firebase_firestore_struncture_ts_study_012_04_read_cost_effort.png)

---

## ここが重要：分散カウンタの“向き不向き”⚖️🧠

**向いてる✅**

* いいね👍・閲覧👀など、**書き込みが多い**カウンタ
* “多少の遅延”が許される表示（たとえば詳細ページで表示）

**注意ポイント⚠️**

* 合計を出すには shard 数だけ読みが必要 → shard=10なら「読むのに10ドキュメント」📚📚📚…
* 記事一覧で 20件表示 × shard10 = **200 reads** になりがち😇
  → 一覧は「近い値（キャッシュ）」を使う/詳細で正確に出す、みたいな設計が現実的です👌

---

## shard数の決め方（最初は少なく→必要なら増やす）📈✨

「何個にすべき？」は、公式にもある通り **負荷テストしながら調整**が王道です([Firebase][1])
分散カウンタ自体は「shard数に比例して耐性アップ」なので、増やすのは理にかなってます([Firebase][3])

おすすめの考え方👇

* まず **10** でスタート🎬
* 人気が出て、書き込みが混み始めたら **20 / 50** に増やす📈
* 増やすときは「shards のドキュメントを追加」するだけ🧱

（運用では `numShards` をどこかに保存して、アプリ側がそれを見てランダム範囲を決める形が多いです👀）

---

## セキュリティ注意：クライアントでカウンタ更新させるとズルされる😈⚠️

ここ、超大事です🔥
もし「ボタン押した人が `incrementLike()` を直接呼べる」設計にすると…

* 悪い人が連打・自動化して好き放題増やせる😇

なので実運用でよくある安全形は👇

1. クライアントは `likes/{uid}` みたいな「1ユーザー1いいね」の証拠ドキュメントだけ作る
2. サーバー側（後の章の Functions など）が、その作成/削除をトリガーにして分散カウンタを更新する
   → これで「ズル」と「衝突」を両方ケアできます🛡️✨

![Tamper Prevention Strategy](./picture/firebase_firestore_struncture_ts_study_012_05_tamper_prevention.png)

---

## 近道：分散カウンタ拡張機能（Extensions）を使う手もある🚀

「自分で実装するより、まず動くのを入れたい！」なら
**Distributed Counter** の拡張機能が用意されています👍([extensions.dev][4])

---

## AIで爆速にする（Antigravity / Gemini CLI / Firebase AI Logic）🤖⚡

* Google の **Antigravity** はエージェントが計画→実装まで進める“Mission Control”っぽい思想の開発環境、という説明がされています([Google Codelabs][5])
* **Gemini CLI** はターミナルからAIエージェント的に作業でき、Cloud Shell だと追加セットアップなしで使える旨が書かれています([Google for Developers][6])
* **Firebase AI Logic** はアプリから Gemini / Imagen を扱える公式導線です([Firebase][7])

コピペで使える依頼例👇（設計レビューに強い💪）

```text
Firestoreで posts/{postId} の likesCount を分散カウンタで設計したい。
- shards の配置パス案
- shard数の初期値と増やし方
- 一覧表示のreads爆発を避けるUI/キャッシュ案
- クライアント改ざん対策（安全な更新フロー）
を、初心者向けに箇条書きで提案して。
```

---

## ミニ課題🎒✨（やると一気に腹落ちする）

1. `initLikeCounter()` を記事作成時に1回だけ呼べるようにする🧱
2. Likeボタン押下で `incrementLike()` を呼ぶ（まずは学習用に直呼びでOK）👍
3. 詳細ページで `getLikesCount()` を呼んで表示する📄✨
4. おまけ：一覧ページでは「前回読んだ値を state に保持して、詳細を開いた時だけ正確に再取得」する（reads節約）💰

---

## チェック✅（この章のゴール）

* 「カウンタ直書きは人気コンテンツで詰まりやすい」が言える🔥
* 「分散カウンタ＝shards に分けて書き込み分散」が説明できる🧱
* shard の **書き込みは速くなる代わりに、読むのは shard 数ぶん増える**と理解できる⚖️
* 「クライアントが直接カウンタ更新は危険（ズルされる）」が言える🛡️

次の章（ランキング🥇）に行くと、この“集計の持ち方”がさらに効いてきますよ〜！🚀

[1]: https://firebase.google.com/docs/firestore/best-practices?utm_source=chatgpt.com "Best practices for Cloud Firestore - Firebase - Google"
[2]: https://docs.cloud.google.com/firestore/native/docs/understand-error-codes?utm_source=chatgpt.com "Understand error codes | Firestore in Native mode"
[3]: https://firebase.google.com/docs/firestore/solutions/counters?utm_source=chatgpt.com "Distributed counters | Firestore - Firebase - Google"
[4]: https://extensions.dev/extensions/firebase/firestore-counter?utm_source=chatgpt.com "Distributed Counter"
[5]: https://codelabs.developers.google.com/getting-started-google-antigravity?utm_source=chatgpt.com "Getting Started with Google Antigravity"
[6]: https://developers.google.com/gemini-code-assist/docs/gemini-cli?utm_source=chatgpt.com "Gemini CLI | Gemini Code Assist"
[7]: https://firebase.google.com/docs/ai-logic?utm_source=chatgpt.com "Gemini API using Firebase AI Logic - Google"
