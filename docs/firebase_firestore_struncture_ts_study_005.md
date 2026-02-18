# 第5章：サブコレの落とし穴（削除・移動・集計）💥🧩🗑️

サブコレ（例：`posts/{postId}/comments/{commentId}`）って、設計が気持ちよく整理できて最高なんだけど…
運用フェーズで **「え、そうなの！？」** となりがちな地雷が3つあります👇💣

1. **削除がややこしい**（親を消しても子が残る）
2. **移動がめんどい**（コピー→切替→削除、が基本）
3. **集計がズレやすい**（件数/いいね等が「削除とセット」で崩れる）

この章は、それを **先に踏んでおく章**です😄✨

---

## 1) 読む📚：サブコレの「落とし穴3兄弟」👨‍👩‍👧‍👦💥

## 落とし穴①：親ドキュメントを消しても、サブコレは消えない😇

アプリのコードで `deleteDoc(postRef)` しても、**サブコレのドキュメントは自動で消えません**。
つまり「記事は消えたのにコメントだけ残る（孤児化）」が起きます。([Google Cloud Documentation][1])

> ただし、**コンソール上での削除**は “ネストしたデータ（サブコレ等）も含めて削除” になる挙動が案内されています。
> 「コンソールでは消えたのに、コードだと残る」って混乱しやすいポイントなので、ここは分けて覚えるのが大事です🧠⚡([Firebase][2])

---

## 落とし穴②：削除は「一撃で全部」にならない（途中で止まることもある）🫠

サブコレ含む “ツリー削除” は、裏では大量のドキュメントを順番に消す処理になりがちで、**途中で失敗して半分だけ消える**こともあります。([Google Cloud Documentation][1])

だから設計段階で👇を決めておくと、未来の自分が助かります🫶

* 「ユーザー操作の削除」は **論理削除（ゴミ箱）** にする？🗑️
* 「管理者操作だけ」物理削除（完全消去）を許す？👮‍♂️
* 監査ログ（誰が何を消した）を残す？🧾

---

## 落とし穴③：移動（＝構造変更）は“コピー＆切替”が基本🚚📦

Firestoreの構造を後で変えたくなったら、基本は👇
**新しい場所へコピー → 読み取りを並行運用 → 切替 → 古い方を削除**。([Firebase][3])

「コレクション名を変更」とか「ここからここへ移動」を一発でやるイメージは持たない方が安全です😄

---

## 2) 手を動かす🛠️：わざと“孤児コメント”を作って、対策を決める😈➡️😇

ここからは「記事 / コメント」でいきます📝✨

## Step A：まず“事故”を体験する💥

1. `posts/{postId}` を1件作る
2. `posts/{postId}/comments` にコメントを2〜3件作る
3. アプリコードで「記事だけ削除」を実行（`deleteDoc`）
4. コンソールで **コメントが残ってないか** を見てみる👀

この「残ってるじゃん！」が落とし穴①です🧨([Google Cloud Documentation][1])

---

## Step B：削除方針を3択から選ぶ🎛️🗑️

## 方針1：論理削除（ゴミ箱）🗑️（いちばん事故りにくい）

記事を物理削除せず、`isDeleted: true` と `deletedAt` を付けて隠します。
**コメントも同じ方針**にしておくと、親が消えた/残ったに振り回されにくいです😄

```ts
import { doc, updateDoc, serverTimestamp } from "firebase/firestore";
import { db } from "./firebase";

// 記事を「ゴミ箱へ」🗑️（物理削除しない）
export async function trashPost(postId: string) {
  await updateDoc(doc(db, "posts", postId), {
    isDeleted: true,
    deletedAt: serverTimestamp(),
  });
}
```

ポイント💡

* 一覧クエリは `where("isDeleted", "==", false)` を基本にする
* “復元”もできる（`isDeleted=false`）✨

---

## 方針2：論理削除＋TTLで「○日後に自動で完全削除」⏳🧹

ゴミ箱に入れた記事に `expireAt` を入れて、**TTLポリシーで自動削除**させます。
TTLは「その時刻を過ぎたら即消える」じゃなく、**だいたい24時間以内に削除**みたいな動きです⏱️([Firebase][4])

超重要⚠️
TTLで親ドキュメントが消えても、**サブコレが自動で消えるわけではありません**。
つまり「TTLで記事だけ消える → コメントが孤児化」は普通に起こりえます。([Firebase][4])

なので実務では👇どれかにします👍

* `comments` にもTTL（`expireAt`）を付けて同じく掃除🧹
* あるいは後述の「サーバー側の再帰削除」でツリーごと消す👮‍♂️

---

## 方針3：物理削除（ツリーごと完全消去）🔥

「管理者だけが実行できる」前提で、ツリー削除を用意するのが王道です👮‍♂️

公式の代表例として、**Callable Functionsから Firebase CLI の `firestore:delete` を使って再帰削除する**解決策が紹介されています。([Google Cloud Documentation][1])
このやり方だと、指定パス配下を探索して消すので、状況によっては「孤児ドキュメントを見つけて削除」もありえます。([Google Cloud Documentation][1])

ただし⚠️

* **削除はアトミックじゃない**（途中まで消えて止まる可能性あり）([Google Cloud Documentation][1])
* Callableは **デフォルトで安全じゃない**ので、必ず権限チェックが必要([Google Cloud Documentation][1])

（この章では「そういう設計が必要」まで理解できればOK👌 実装は第20章寄りの話です⚙️）

---

## 3) 集計の落とし穴📊：コメント数がズレる“あるある”😵

サブコレでコメントを持つと、**コメント数**はだいたい欲しくなりますよね？😄

## 典型パターンA：`posts` に `commentCount` を持つ（速いけどズレやすい）⚡

* コメント追加→ `commentCount+1`
* コメント削除→ `commentCount-1`
* でも…「論理削除」「TTL」「途中で削除失敗」などが混ざると、ズレやすい😇

## 典型パターンB：Aggregation queryでその場カウント（ズレないけど都度コスト）🔎

Firestoreには **count/sum/avg** の集計クエリがあります。([Firebase][5])
論理削除してるなら「生きてるコメントだけ数える」みたいに設計できて、ズレにくいです👍

例（コメントに `postId` を持たせて、コレクショングループで数える案）👇

```ts
import { collectionGroup, getCountFromServer, query, where } from "firebase/firestore";
import { db } from "./firebase";

export async function countAliveComments(postId: string) {
  const q = query(
    collectionGroup(db, "comments"),
    where("postId", "==", postId),
    where("isDeleted", "==", false),
  );
  const snap = await getCountFromServer(q);
  return snap.data().count;
}
```

---

## 4) ミニ課題🎯：記事削除時、コメントをどう扱う？（設計を文章で決める）📝✨

次の3つを、あなたのアプリ方針として決めてみてください👇😄

1. 記事削除は

   * A. ゴミ箱（論理削除）🗑️
   * B. 即完全削除🔥
   * C. ゴミ箱→30日後に完全削除⏳

2. コメントは

   * A. 記事と同じ方針にする
   * B. コメントだけ先に消す（or 先に隠す）
   * C. “監査用”に残す（表示はしない）

3. 集計（コメント数）は

   * A. `commentCount` を持つ（サーバー側で更新）
   * B. その場カウント（Aggregation）
   * C. 両方（普段はキャッシュ、ズレ修正は集計で）

書けたら勝ちです🏆✨

---

## 5) チェック✅（この章のゴール達成ライン）

* 親を消してもサブコレは消えない、を腹で理解した😄([Google Cloud Documentation][1])
* TTLは便利だけど「即時じゃない」「サブコレは消さない」を理解した⏳([Firebase][4])
* 構造変更（移動）は「コピー→並行→切替→削除」が基本だと分かった🚚([Firebase][3])
* 削除と集計はセットで設計する、と思えるようになった📊

---

## 6) AIブースト🤖⚡（Antigravity / Gemini CLI で一気に固める）

## Antigravityの使いどころ🧠🛰️

Antigravityは「エージェントが計画→実行→検証まで回す」思想の開発環境で、ブラウズや安全設定（ポリシー）も含めて扱えます。([Google Codelabs][6])
この章だと「削除方針の比較表」「失敗ケース洗い出し」「実装の危険箇所レビュー」に強いです💪

## Gemini CLIの使いどころ⌨️🤖

Gemini CLIはターミナル中心で、最近は拡張の入れ方や設定がわかりやすく案内されています（例：v0.28.0+ の拡張設定ファイル）。

## コピペ依頼例📎

* 「`posts/{postId}/comments/{commentId}` の設計で、削除方針を3案（論理削除/TTL/再帰削除）比較して。メリデメ、事故パターン、集計への影響も書いて」
* 「論理削除にした時のクエリ一覧と必要なインデックス候補（第2キー含む）を出して」
* 「“途中で削除が止まる”前提で、UIに出すべき状態（削除中/失敗/再試行）を提案して」

## Firebase AI Logic もここに直結するよ🔐🤖

生成AIを絡めると「リクエスト乱発」「コスト」「不正アクセス」が現実問題になります😇
Firebase AI Logicは **ユーザー単位のレート制限（デフォルト例：100 RPM）** があり、調整も可能です。([Firebase][7])
さらに **App Check 連携**で、正規アプリ以外からの呼び出しを弾く設計にもできます。([Firebase][8])

---

次の章（第6章：正規化 vs 非正規化⚖️）に入ると、「表示のための複製」と「削除時の整合性」がガッツリ繋がってきて、めちゃくちゃ面白くなりますよ😄🔥

[1]: https://docs.cloud.google.com/firestore/native/docs/solutions/delete-collections?hl=ja "呼び出し可能な Cloud Functions の関数を使用してデータを削除する  |  Firestore in Native mode  |  Google Cloud Documentation"
[2]: https://firebase.google.com/docs/firestore/manage-data/delete-data "Delete data from Cloud Firestore  |  Firebase"
[3]: https://firebase.google.com/docs/firestore/best-practices "Best practices for Cloud Firestore  |  Firebase"
[4]: https://firebase.google.com/docs/firestore/ttl "Manage data retention with TTL policies  |  Firestore  |  Firebase"
[5]: https://firebase.google.com/docs/firestore/query-data/aggregation-queries?hl=ja&utm_source=chatgpt.com "集計クエリでデータを要約する | Firestore - Firebase - Google"
[6]: https://codelabs.developers.google.com/getting-started-google-antigravity "Getting Started with Google Antigravity  |  Google Codelabs"
[7]: https://firebase.google.com/docs/ai-logic?utm_source=chatgpt.com "Gemini API using Firebase AI Logic - Google"
[8]: https://firebase.google.com/docs/ai-logic/app-check?utm_source=chatgpt.com "Implement Firebase App Check to protect APIs from ... - Google"
