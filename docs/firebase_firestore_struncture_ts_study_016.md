# 第16章：`orderBy` の罠（存在しないフィールドは落ちる）🕳️

## この章でできるようになること🎯

* `orderBy("createdAt")` を付けたら結果が減る理由を説明できる🗣️
* 「一覧でソートするフィールド」は**必須フィールド**として設計できる🧱
* 既存データに “抜け” があっても、**埋め戻し（バックフィル）**で直せる🛠️
* ページングでも崩れない「安定ソート」を作れる📜✨

---

## 1) まず読む：`orderBy` は「並べ替え」だけじゃない⚠️

![Missing Field Exclusion](./picture/firebase_firestore_struncture_ts_study_016_01_missing_field_exclusion.png)

Firestore の `orderBy()` は、ただ並べ替えるだけ…に見えるけど、実は**そのフィールドが存在するドキュメントしか返さない**という性質があるよ😵‍💫
つまり「`createdAt` が無い投稿」は、他の条件に合っていても**検索結果から消える**！ ([Firebase][1])

✅ 公式の言い方だとこう：

* `orderBy()` は「そのフィールドの存在」でフィルタされる
* なので結果セットに「そのフィールドが無いドキュメント」は入らない ([Firebase][1])

---

## 2) 何が起きる？よくある事故パターン集💥

## パターンA：件数が急に減る😱

* `getDocs(collection("posts"))` → 100件
* `getDocs(query(collection("posts"), orderBy("createdAt","desc")))` → 10件

これ、**残り90件は `createdAt` が無い**だけ…が本当に多い🙃 ([Firebase][1])

---

## パターンB：ページングが壊れる📜💣

ページングはだいたい `orderBy + startAfter` で作るけど、
「ソートキーが無いドキュメント」が混ざってると **ページ境界が不安定**になりがち😇

---

## パターンC：同点が出て順番がフワる🌀

![Stable Sort](./picture/firebase_firestore_struncture_ts_study_016_02_stable_sort.png)

`createdAt` が同じ投稿が並んだ時、順序が不安定だと「次ページに同じの出た」「抜けた」が起きる。

Firestore は内部的に安定した順序付けのルールを持っていて、`__name__`（ドキュメントID）を最後に加える（または暗黙に足される）仕様があるよ📌 ([Google Cloud Documentation][2])
→ なので **“第2ソートキー” を明示**しておくと、ページングが強くなる💪✨

---

## 3) 手を動かす：わざと落とし穴に落ちてみよう🕳️😆

ここは体験がいちばん早い！
「フィールドが無いと、結果から消える」を目で見るよ👀✨

## 3-1. ダメなデータを作る（`createdAt` がある/ないを混ぜる）

```ts
import { getFirestore, collection, addDoc, serverTimestamp } from "firebase/firestore";

const db = getFirestore();

// createdAt あり✅
await addDoc(collection(db, "posts"), {
  title: "createdAt あり",
  createdAt: serverTimestamp(),
});

// createdAt なし❌（わざと）
await addDoc(collection(db, "posts"), {
  title: "createdAt なし",
});
```

## 3-2. `orderBy` なし → ありで件数比較

![Experiment Result](./picture/firebase_firestore_struncture_ts_study_016_03_experiment_result.png)

```ts
import { collection, getDocs, query, orderBy } from "firebase/firestore";

const postsRef = collection(db, "posts");

// orderByなし（全部出やすい）
const a = await getDocs(postsRef);
console.log("orderByなし:", a.size);

// orderByあり（createdAt無い投稿が消える）
const b = await getDocs(query(postsRef, orderBy("createdAt", "desc")));
console.log("orderByあり:", b.size);
```

✅ ここで **`orderByあり` の方が少なくなったら成功**🎉
（その差分が “createdAt が無いドキュメント” だよ）

---

## 4) 解決：設計で勝つ🧱✨（これが本題）

## 解決策①：ソートキーは「全ドキュメントに必ず入れる」✅

一覧で `orderBy("createdAt")` したいなら、`createdAt` は **全投稿に必須**。

* `createdAt`：作成時に必ず入れる
* `updatedAt`：更新時に必ず入れる
* 型は Timestamp で統一（文字列にしない）🧠

## 解決策②：作成時に “自動で埋める” を標準化する🛠️

![Standard Create Flow](./picture/firebase_firestore_struncture_ts_study_016_04_standard_create.png)

クライアント実装のブレで `createdAt` が抜けるのが事故の原因なので、**投稿作成関数を1個に固定**しよう（「どこからでも同じ道」🚪）

```ts
import { addDoc, collection, serverTimestamp } from "firebase/firestore";

type NewPost = {
  title: string;
  body: string;
};

export async function createPost(input: NewPost) {
  const doc = {
    ...input,
    createdAt: serverTimestamp(),
    updatedAt: serverTimestamp(),
  };

  return addDoc(collection(db, "posts"), doc);
}
```

---

## 5) さらに強く：安定ソート（ページング耐性UP）📜💪

「同じ createdAt が出た時」のために **第2キー**を足すのが定番だよ✨
Firestore は `__name__`（ドキュメントID）を安定化に使うルールがあるので、これを使うのが素直👍 ([Google Cloud Documentation][2])

```ts
import { query, collection, orderBy, limit, documentId } from "firebase/firestore";

const q = query(
  collection(db, "posts"),
  orderBy("createdAt", "desc"),
  orderBy(documentId(), "desc"), // 第2キー（安定化）
  limit(20)
);
```

---

## 6) 既に欠けてるデータはどうする？（埋め戻し戦略）🩹🧹

![Backfill Strategy](./picture/firebase_firestore_struncture_ts_study_016_05_backfill_strategy.png)

## 現実あるある😇

昔作った投稿に `createdAt` が無い！
→ このままじゃ `orderBy("createdAt")` で永遠に表示されない… ([Firebase][1])

## 対策の考え方（おすすめ順）✨

1. **今後の作成分は絶対に欠けない**ように固定（まず再発防止）🧱
2. 既存分は、どこかで一回だけ **バックフィル**（埋め戻し）🛠️

## バックフィルの最小方針（超シンプル）

* `createdAt` が無いドキュメントに対して

  * 可能なら「本来の作成日時」を復元
  * 無理なら「暫定で今の時刻」でもいい（ただし並びが変になるのは理解して使う）

※ バックフィルの方法はいくつかあるけど、章のゴールは「**`orderBy` が安定する形にする**」なので、まずは方針が決まればOKだよ👌

---

## 7) AIでこの章が爆速になる🤖⚡（Firebase AI Logic / Genkit / Antigravity / Gemini CLI）

## 7-1. “設計レビュー” をAIに投げる（Firebase AI Logic）🧠

![AI Design Review](./picture/firebase_firestore_struncture_ts_study_016_06_ai_review.png)

Firebase AI Logic はアプリから Gemini/Imagen を使える導線で、モデルや運用の更新も速い領域だよ🚀 ([Firebase][3])
だからこそ、**データ設計のレビュー**にAIを使うと相性がいい✅

例：AIに投げる質問（コピペ用）📎

* 「posts を `orderBy(createdAt)` で一覧表示する。createdAt/updatedAt を必須にする設計で、抜けが起きない実装パターンを提案して。ページングも壊れない第2キーも含めて」

---

## 7-2. “作業の自動化” は Antigravity が強い🏗️🤖

Google の Antigravity は「エージェントが計画→実装→検証」まで回す思想の開発環境として説明されてるよ🛰️ ([Google Codelabs][4])

使い方イメージ：

* エージェントに「プロジェクト内の `addDoc(posts)` を全部探して、createdAt/updatedAt を必ず入れるようにリファクタして」
* さらに「クエリ一覧（orderByしてる所）を列挙して、ソートキーが欠けた時の影響もコメントして」

---

## 7-3. “ターミナルで一気に整備” は Gemini CLI🧑‍💻⚡

Gemini CLI はターミナルで動く AI エージェントとして公式に案内されてるよ（Code Assist との関係や、CLI自体がオープンソースである点など） ([Google for Developers][5])

例（コピペ用）📎

* 「Firestore の posts コレクションで createdAt が無いドキュメントが出ないように、作成関数を共通化して。さらに orderBy(createdAt) のクエリを全部見つけて安定ソート（第2キー）を足して」

---

## 7-4. Genkit で “AI処理→保存” を作る時こそ createdAt 必須🧾🤖

![Genkit Logging](./picture/firebase_firestore_struncture_ts_study_016_07_genkit_log.png)

Genkit は Firebase チーム側の OSS フレームワークとして案内されてて、Functions から呼び出す導線も用意されてるよ。 ([Firebase][6])
AI出力を Firestore に保存するなら、

* `aiLogs/{logId}` に `createdAt` を必須
* 「いつ、どのモデルで、どのアクションをしたか」を残す

みたいにしておくと、**あとで監査・課金・調査がラク**になるよ〜🔍✨ ([Firebase][3])

---

## 8) ミニ課題🎒（10〜20分）

## お題：投稿一覧を「必ず最新順」で安定表示する📜✨

やることは3つだけ👇

1. 投稿作成を必ず `createPost()` 経由にする🚪
2. `createdAt` / `updatedAt` を必ず入れる🧱
3. 一覧クエリを **安定ソート**にする（第2キー追加）🧷

---

## 9) チェック✅（ここまでできたら勝ち！）

* `orderBy()` で結果が減る理由を「フィールドの存在」で説明できる？ ([Firebase][1])
* 一覧に使うソートキーを「必須フィールド」として設計できた？🧱
* `createdAt` を “作成時に自動で埋める” 実装に統一できた？🛠️
* 第2キーで安定ソートまでできた？📜 ([Google Cloud Documentation][2])

---

次の第17章（複数範囲クエリと制約📏）に行くと、「UIでやりたい検索が、Firestoreの制約で無理」って状況が出てくるんだけど…
その時に今日の学び（**“クエリが無理なら保存形を変える”**）がめちゃ効くよ😄🔥

[1]: https://firebase.google.com/docs/firestore/query-data/order-limit-data?utm_source=chatgpt.com "Order and limit data with Cloud Firestore - Firebase - Google"
[2]: https://docs.cloud.google.com/firestore/docs/reference/rest/v1beta1/StructuredQuery?utm_source=chatgpt.com "StructuredQuery | Firestore"
[3]: https://firebase.google.com/docs/ai-logic?utm_source=chatgpt.com "Gemini API using Firebase AI Logic - Google"
[4]: https://codelabs.developers.google.com/getting-started-google-antigravity?utm_source=chatgpt.com "Getting Started with Google Antigravity"
[5]: https://developers.google.com/gemini-code-assist/docs/gemini-cli?utm_source=chatgpt.com "Gemini CLI | Gemini Code Assist"
[6]: https://firebase.google.com/codelabs/ai-genkit-rag?utm_source=chatgpt.com "Build gen AI features powered by your data with Genkit"