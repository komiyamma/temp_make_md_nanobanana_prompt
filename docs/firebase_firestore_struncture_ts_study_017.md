# 第17章：複数範囲クエリと制約（2026の重要ポイント）📏✨

この章のゴールは「検索フィルタを増やしたくなった時に、**その組み合わせがFirestoreで行けるか/行けないか**を即判断できる」状態になることだよ😄🔎
（そして、無理なら**保存の形を変える**発想に切り替えられるようになる💡）

---

## 読む：複数範囲クエリって何？どう使う？🧠📚

## 1) “範囲/不等号フィルタ”ってどれ？👀

Firestoreで「範囲っぽい」やつはだいたいこの仲間👇

* `>`, `>=`, `<`, `<=`（いわゆる範囲）
* `!=`（一致しない）
* `not-in`（このリスト以外）
* （文脈によっては `in` / `array-contains-any` / `or` も “分岐” が増えて重くなりやすい仲間）

Firestoreの制約は、ざっくり言うと **「インデックスで高速にできる形しか許さない」** から来てるよ🗂️⚡

---

## 2) 2026の激アツ変更：複数フィールドで範囲ができるようになった🔥

![Multiple Range Query](./picture/firebase_firestore_struncture_ts_study_017_01_multi_range_query.png)

昔は「範囲（不等号）は1フィールドだけ」って縛りが強かったけど、今は **複数フィールドに対して範囲/不等号を組み合わせられる** ように整理されてるよ📈
公式の “複数範囲” ガイドも更新されていて、例としてこんな形が載ってる👇（`salary` と `experience` の両方で範囲）([Firebase][1])

ポイントは **範囲をかけたフィールドを `orderBy` にも入れる** こと！🧷

---

## 3) ただし重要：`orderBy` の順番が “コスト” を左右する💸

![OrderBy Cost](./picture/firebase_firestore_struncture_ts_study_017_02_orderby_cost.png)

複数範囲クエリでは、どの複合インデックスが使われるかが超重要で、`orderBy` の並べ方で **スキャンするインデックス件数** が増減するよ😵‍💫
公式でも「より絞れる（＝選択性が高い）条件のフィールドを先に `orderBy` に置く」と効率が良い、って説明されてる([Firebase][1])

> 迷ったら：
> **“絞り込みが強い方（結果が少なくなる方）を先に orderBy”** → コスト下がりやすい💡([Firebase][1])

---

## 4) “複数範囲” とは別に、昔からの制約も普通に残ってる⚠️

![Constraint Map](./picture/firebase_firestore_struncture_ts_study_017_03_constraint_map.png)

ここ、検索UIを作る時にめちゃ踏みがち🥹

* `not-in` は **`in` / `array-contains-any` / `or` と同じクエリで併用できない**([Firebase][2])
* `not-in` と `!=` を **同時に使えない**([Firebase][2])
* `not-in` または `!=` は **1クエリにつき1回だけ**（Standard edition の制約）([Firebase][2])
* `OR` 系（`or` / `in` / `array-contains-any`）は内部で展開されて、**最大30個の分岐**まで（固定）([Firebase][2])
* 不等号を使うと、そのフィールドは **“存在するドキュメントだけ” が対象になりがち**（`orderBy` も同様で、フィールド無しは結果から外れる）([Firebase][2])

さらに、複数範囲クエリ側にも追加制約があるよ👇

* 範囲/不等号フィールドは **最大10個まで**（高コスト化防止）([Firebase][1])
* 「ドキュメントID（`__name__`）に等価条件だけ」＋「他フィールドに範囲/不等号」は **サポートされない**([Firebase][1])

---

## 手を動かす：検索フィルタUIを想定して、許される組み合わせを作る🧩🛠️

ここからは「記事一覧（posts）」でよくある検索を作る想定でいくよ😄📰

## ステップ1：まず “やりたいフィルタ” を書き出す📝

例👇

* `status == "published"`（等価）
* `authorId == 自分`（等価）
* `createdAt` を `from〜to`（範囲）
* `likesCount >= 10`（範囲）
* `tag` を含む（配列系：`array-contains`）

---

## ステップ2：分類する（これができると勝ち🏆）

![Filter Classification](./picture/firebase_firestore_struncture_ts_study_017_04_filter_classification.png)

* 等価：`==`
* 範囲/不等号：`> >= < <= != not-in`
* OR系：`or / in / array-contains-any`
* 配列：`array-contains`（これも癖ある）

この分類ができると「**あ、ここで詰まりそう**」が事前に見える👀✨

---

## ステップ3：複数範囲クエリを “正しい型” で書く✍️（TypeScript）

![Query Execution](./picture/firebase_firestore_struncture_ts_study_017_05_query_execution.png)

例として「作成日レンジ」＋「いいね数レンジ」の2軸フィルタをやるよ📅❤️

* まず **where で範囲**
* 次に **範囲をかけたフィールドを orderBy に入れる**
* `orderBy` の順は **より絞れる方を先** が基本（コスト意識）([Firebase][1])

```ts
import {
  collection,
  query,
  where,
  orderBy,
  limit,
  getDocs,
  Timestamp,
} from "firebase/firestore";
import { db } from "./firebase";

// 例：UIから来た値
const from = Timestamp.fromDate(new Date("2026-02-01"));
const to   = Timestamp.fromDate(new Date("2026-02-16"));
const minLikes = 10;

const postsRef = collection(db, "posts");

// createdAt と likesCount の “複数範囲”
// ✅ 範囲をかけたフィールドを orderBy に入れるのがコツ
const q = query(
  postsRef,
  where("createdAt", ">=", from),
  where("createdAt", "<=", to),
  where("likesCount", ">=", minLikes),

  // どっちが絞れる？で順番を考える（例：likesCount>=10 の方が絞れるなら先）
  orderBy("likesCount", "desc"),
  orderBy("createdAt", "desc"),

  limit(20)
);

const snap = await getDocs(q);
const posts = snap.docs.map(d => ({ id: d.id, ...d.data() }));
```

この “型” は、公式の複数範囲の説明（範囲に使ったフィールドを `orderBy` に入れる）と同じ方向性だよ([Firebase][1])

---

## ステップ4：インデックス最適化の考え方（地味に差が出る）🧠⚙️

![Query Explain](./picture/firebase_firestore_struncture_ts_study_017_06_query_explain.png)

複数範囲クエリは **複合インデックス**が絡みやすい。
しかも `orderBy` の順が悪いと、結果は同じでも **大量のインデックスを読んで捨てる** みたいなことが起きる😇

公式の最適化ガイドだと、

* `Query Explain` で実行計画（どのインデックス使ったか、何件スキャンしたか）を見て改善できる([Firebase][3])
* `orderBy` を “より選択性の高い制約から先に” で効率が上がる([Firebase][3])

って流れが紹介されてるよ📉✨

（補足：`Query Explain` の実行例はサーバーSDK側（Nodeなど）で紹介されてる([Firebase][3])）

---

## ミニ課題：この検索、Firestoreだけでいける？🤔🧪

次の6つを **A:そのまま行けそう / B:設計工夫が必要 / C:そのままは無理寄り** で仕分けしてみてね👇✨

1. `status == "published"` AND `createdAt from〜to`
2. `createdAt from〜to` AND `likesCount from〜to`（2軸レンジ）
3. `tags array-contains "firebase"` AND `tags array-contains "react"`（配列2本）
4. `category in ["tech","life"]` AND `tag array-contains "firebase"`
5. `authorId != "u123"` AND `authorId not-in ["u777","u888"]`
6. `(status=="published" OR status=="scheduled")` AND `createdAt >= from`

---

## 解答の目安（チラ見OK👀）

* 1：A（普通に定番）
* 2：A（複数範囲OK！ただし `orderBy` とインデックス意識）([Firebase][1])
* 3：C（`array-contains` は ORグループ内で数や組み合わせ制約が強い。設計変更しがち）([Firebase][2])
* 4：B（OR展開（DNF）や制約に引っかかる可能性。分岐数や組み合わせに注意）([Firebase][2])
* 5：C（`not-in` と `!=` の併用NG）([Firebase][2])
* 6：B（ORは最大30分岐、展開で重くなる。要注意）([Firebase][2])

---

## チェック：ここまでできたらOK✅🎉

* 「このフィルタは等価 / 範囲 / OR / 配列」って分類できる😄
* 複数範囲をやる時、**範囲に使ったフィールドを `orderBy` に入れる**のが自然に出る🧷([Firebase][1])
* `not-in` / `!=` / `in` / `array-contains-any` / `or` の “併用制約” を知ってる⚠️([Firebase][2])
* `orderBy` は “フィールドが無いドキュメントは落ちる” を覚えてて、必須フィールド設計に意識が向く🧱([Firebase][4])

---

## AIで設計レビュー＆実装を爆速にする🤖⚡

![AI Query Validator](./picture/firebase_firestore_struncture_ts_study_017_07_ai_validator.png)

「検索の組み合わせで詰まる前に、AIに“ルールチェック”させる」のが強いよ🧠✨
（エージェント型の開発環境やCLIエージェントが、設計レビューと相性良い）([Google Codelabs][5])

## Gemini CLI に投げる依頼例（コピペ用📎）

```text
Firestore の posts 検索を作りたい。
フィルタ候補：
- status == "published"
- createdAt from-to
- likesCount min-max
- tags (array-contains)
この組み合わせで「できる/できない」を分類して、
できない場合の代案（検索用フィールド案）を3つ提案して。
さらに、複数範囲クエリが必要なケースは orderBy の並びと、
必要になりそうな複合インデックスの方向性も書いて。
```

## Firebaseの生成AI機能を絡める時の“事故防止”メモ🛡️

生成AIをアプリに入れると「コスト爆発（Denial-of-Wallet）」が怖いから、**App Check + レート制限**をセットで意識すると安心だよ😇
Firebase側はAI機能に **ユーザー単位のレート制限（デフォルト100 RPM）**などの考え方が整理されてる([Firebase][6])

---

次の第18章（ページング設計📜）に行くと、この章の「orderByの選び方」がそのまま “無限スクロールの安定性” に直結してくるよ🔥

[1]: https://firebase.google.com/docs/firestore/query-data/multiple-range-fields "Query with range and inequality filters on multiple fields overview  |  Firestore  |  Firebase"
[2]: https://firebase.google.com/docs/firestore/query-data/queries "Perform simple and compound queries in Cloud Firestore  |  Firebase"
[3]: https://firebase.google.com/docs/firestore/query-data/multiple-range-optimize-indexes "Optimize queries with range and inequality filters on multiple fields  |  Firestore  |  Firebase"
[4]: https://firebase.google.com/docs/firestore/query-data/order-limit-data "Order and limit data with Cloud Firestore  |  Firebase"
[5]: https://codelabs.developers.google.com/getting-started-google-antigravity?utm_source=chatgpt.com "Getting Started with Google Antigravity"
[6]: https://firebase.google.com/docs/ai-logic/quotas?utm_source=chatgpt.com "Rate limits and quotas | Firebase AI Logic - Google"