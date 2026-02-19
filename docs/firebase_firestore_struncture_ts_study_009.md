# 第9章：ホットスポットと書き込み衝突（地味に重要）🔥

この章のゴールはシンプルです👇
**「アクセスが増えても、1点集中で詰まらないFirestore設計」にできる**ようになること！💪✨

---

## まず結論：Firestoreで“詰まりやすい”のはこの2種類😵

### ① 1つのドキュメントに書き込みが集中（ドキュメント・ホットスポット）🔥

たとえば…👇

* `posts/{postId}` に `likesCount++` を**全員が同時に**やる
* `posts/{postId}` に `commentsCount++` を**毎回**やる
* `stats/today` みたいな「今日の集計」ドキュメントを**全員が更新**する

Firestoreの書き込みは、**ドキュメント本体 + インデックス**を“まとめて”更新します。だから、1点集中が起きると待ちが発生しやすいんですね😇 ([Firebase][1])

![Document vs Collection Hotspot](./picture/firebase_firestore_struncture_ts_study_009_01_hotspot_types.png)

### ② 連番っぽい値でインデックスがホット（コレクション・ホットスポット）🔥

たとえば…👇

* `createdAt`（増え続けるタイムスタンプ）を **indexed** のままにして
* 1つのコレクションに対して大量追加（ログ、IoT、イベントなど）

このパターンは、**“連続するインデックス値”が原因で、コレクションの書き込みが 500 writes/sec に制限**され得ます⚠️ ([Firebase][2])

---

## 「書き込み衝突」って何が起きるの？🤔

ありがちな症状はこんな感じ👇

* たまに書き込みが失敗する（リトライが必要）
* レイテンシが急に悪化する
* トランザクションが衝突して弾かれる（同じ場所を同時更新）

公式のエラー説明でも、**hot-spot がスケールを邪魔するから、個別ドキュメントへの書き込みレートを下げよう**って話が出てきます。 ([Google Cloud Documentation][3])

---

## 事故りやすい設計トップ3（まず避けたい）💥

## 1) `likesCount` / `commentsCount` を親ドキュメントに直書き

「見た目ラク」なんだけど、人気記事ほど**1点集中**で詰まりがち😇

![Direct Write Bottleneck](./picture/firebase_firestore_struncture_ts_study_009_02_direct_write_bottleneck.png)

## 2) `stats/today` に全イベントを集めて `increment`

「全体集計」を1枚にまとめるのは、ホットスポット製造機🔥

## 3) 連番IDや、単純なタイムスタンプで大量追加

自分で `2026-02-16-000001` みたいなIDを振ると、**書き込みが偏りやすい**です。自動IDのほうが安全寄り。 ([Firebase][2])

---

## 対策カタログ（初心者でも選びやすく！）🧰✨

## 対策A：みんなが同じドキュメントを更新しない（分散する）🧩

**「いいね」や「既読」みたいな“ユーザーごとの状態”**は、こうします👇

* ✅ `posts/{postId}/likes/{uid}` に保存（ユーザーごとに別ドキュメント）

![Subcollection for Likes](./picture/firebase_firestore_struncture_ts_study_009_03_subcollection_likes.png)
* ✅ `posts/{postId}/reads/{uid}` に保存

こうすると、人気投稿でも**書き込み先が散らばる**ので衝突しにくいです👏

---

## 対策B：どうしてもカウントが必要なら「分散カウンタ」🧱

「1つの数字に書き込みが集中する」のが問題なので、**カウンタをシャード（分割）**します。

Firestore公式の定番解がこれ👇
分散カウンタは、シャード数に応じてスループットが伸びます。 ([Firebase][4])

![Sharded Counter Concept](./picture/firebase_firestore_struncture_ts_study_009_04_sharded_counter.png)

---

## 対策C：大量追加で 500 writes/sec 制限に近づくなら「シャーディングされたタイムスタンプ」⏱️🧱

ログやイベントを1コレクションに大量追加するなら、公式に「シャーディングされたタイムスタンプ」解法があります。 ([Firebase][5])

---

## 手を動かす（ハンズオン）🛠️😄

## ハンズオン1：いいねを「衝突しにくい形」で保存する👍✨

**狙い：** `likesCount++` をやめて、**ユーザーごとに別ドキュメント**へ。

## データ構造（おすすめ）

* `posts/{postId}`
* `posts/{postId}/likes/{uid}`  ← ここがポイント！

## React/TypeScript例（トグル：いいね付ける/外す）

```ts
import { doc, setDoc, deleteDoc, serverTimestamp } from "firebase/firestore";
import { db } from "./firebase"; // 既に初期化済み想定

export async function likePost(postId: string, uid: string) {
  const likeRef = doc(db, "posts", postId, "likes", uid);
  await setDoc(likeRef, { createdAt: serverTimestamp() }, { merge: true });
}

export async function unlikePost(postId: string, uid: string) {
  const likeRef = doc(db, "posts", postId, "likes", uid);
  await deleteDoc(likeRef);
}
```

✅ これで「人気記事に全員が同時に `posts/{postId}` を更新する」構図が消えます🎉
（カウントの出し方は後の章で “集計クエリ” や “サーバー側集計” として育てればOK！🌱）

---

## ハンズオン2：分散カウンタの“雰囲気”だけ掴む（ミニ実装）🧱

**狙い：** 1ドキュメント更新を避けて、ランダムなシャードへ `increment` する。

## 例：構造

* `postCounters/{postId}/shards/{shardId}`

## 書き込み（ランダムシャードに +1）

```ts
import { doc, increment, setDoc, updateDoc } from "firebase/firestore";
import { db } from "./firebase";

const SHARDS = 10;

export async function incrementLikeDistributed(postId: string) {
  const shardId = Math.floor(Math.random() * SHARDS).toString();
  const shardRef = doc(db, "postCounters", postId, "shards", shardId);

  // shardが無ければ作る（初回だけ）
  await setDoc(shardRef, { count: 0 }, { merge: true });

  // ランダムシャードに加算（書き込み先が分散）
  await updateDoc(shardRef, { count: increment(1) });
}
```

⚠️ 注意：合計値は「シャードを全部読んで足す」必要があります（コスト感や最適化は後の章で！）
でもこの章では「**1点集中を散らす**」感覚が掴めれば勝ちです😄✨

---

## AIも絡める（設計レビューを爆速化）🤖⚡

## 1) Antigravityで「ホットスポット検査官」をやらせる🕵️‍♂️

Antigravityは“エージェントが計画→実行→検証”まで寄せていく思想の開発環境です。 ([Google Codelabs][6])

**依頼例（コピペ用）📎**

* 「このFirestore設計（posts/likes/comments/stats）を見て、ホットスポット候補を列挙して。特に“同じドキュメントへの書き込み集中”と“連番インデックスの500 writes/sec制限”をチェックして、回避案を3パターン出して」

---

## 2) Gemini CLIで“衝突しにくい書き方”へ自動リファクタ🔧

Gemini CLIはターミナルから使えるAIエージェントで、開発フローに組み込みやすいです。 ([Google for Developers][7])

**依頼例（コピペ用）📎**

* 「likesCount++ をやめて、`posts/{postId}/likes/{uid}` 方式に書き換えて。UI側は“自分がいいね済みか”を効率よく判定できるようにして」

---

## 3) Firebase AI Logicを使うときも“ログのホットスポット”に注意🧨

AI結果を保存するとき、うっかり👇みたいにすると危険です。

* ❌ `aiStats/today` に毎回 `increment`（集中しがち）

![AI Log Strategy](./picture/firebase_firestore_struncture_ts_study_009_05_ai_log_strategy.png)

代わりに👇がおすすめ！

* ✅ `aiLogs/{autoId}` に **追記型（append-only）**で保存

  * `{ userId, model, promptHash, createdAt, action }` みたいな感じ

さらに、AI系は**レート制限**も重要です。Firebase AI Logicは**デフォルトで「1ユーザーあたり 100 RPM」**の制限があり、調整もできます。 ([Firebase][8])
本番チェックリストでも、クォータ確認やレート制限設定が推されています。 ([Firebase][9])

---

## ミニ課題（3つ挙げて対策メモ）📝🔥

次のテンプレで、**“集中しそうな更新”を3つ**書き出してみてください👇

1. 集中しそうな更新：`（例：posts/{postId}.likesCount）`

   * なぜ集中？：`（例：人気記事に全員が押す）`
   * 対策案A：`（例：likes/{uid}）`
   * 対策案B：`（例：分散カウンタ）`

✅ **チェック**：

* 「同じドキュメントを全員で更新してない？」
* 「連番（ID/インデックス）で偏ってない？」
* 「ログ/集計が1点に集まってない？」

---

## まとめ（この章で身につけたこと）🎉

* ホットスポットは **“1点集中”** が原因になりやすい🔥 ([Firebase][2])
* 対策の基本は **「書き込み先を分散」**（ユーザー別ドキュメント / シャード）🧩🧱
* 大量追加なら **500 writes/sec 制限（連番インデックス）**も意識！ ([Firebase][2])
* AI連携でも「ログ設計」と「レート制限」はホットスポット回避に直結🤖⚡ ([Firebase][8])

---

次の章（第10章）は「集計の全体像（いつ計算する？いつ保存する？）」に入るので、今日の“分散する発想”がそのまま効いてきますよ〜！🧠✨

[1]: https://firebase.google.com/docs/firestore/understand-reads-writes-scale?utm_source=chatgpt.com "Understand reads and writes at scale | Firestore - Firebase"
[2]: https://firebase.google.com/docs/firestore/best-practices?utm_source=chatgpt.com "Best practices for Cloud Firestore - Firebase - Google"
[3]: https://docs.cloud.google.com/firestore/native/docs/understand-error-codes?utm_source=chatgpt.com "Understand error codes | Firestore in Native mode"
[4]: https://firebase.google.com/docs/firestore/solutions/counters?utm_source=chatgpt.com "Distributed counters | Firestore | Firebase"
[5]: https://firebase.google.com/docs/firestore/solutions/shard-timestamp?utm_source=chatgpt.com "Sharded timestamps | Firestore - Firebase"
[6]: https://codelabs.developers.google.com/getting-started-google-antigravity?utm_source=chatgpt.com "Getting Started with Google Antigravity"
[7]: https://developers.google.com/gemini-code-assist/docs/gemini-cli?utm_source=chatgpt.com "Gemini CLI | Gemini Code Assist"
[8]: https://firebase.google.com/docs/ai-logic/quotas?utm_source=chatgpt.com "Rate limits and quotas | Firebase AI Logic - Google"
[9]: https://firebase.google.com/docs/ai-logic/production-checklist?utm_source=chatgpt.com "Production checklist for using Firebase AI Logic - Google"
