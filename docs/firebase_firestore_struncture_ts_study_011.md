# 第11章：Aggregation Queries（Count / Sum / Avg）で“その場集計”📊

この章は「一覧で *“全◯件”* を出したい」「合計いいね数だけ知りたい」「平均だけほしい」みたいな **“件数・合計・平均だけ取る”** 技を、Firestoreでスマートにやる回です😄✨
Firestoreは **集計結果だけ** を返してくれるので、全部のドキュメントを読んで数えるより **速くて安くなりやすい** です💰⚡ ([Firebase][1])

---

## 1) まず結論：集計クエリは何ができる？🤔

Firebase の Cloud Firestore には、次の“読み取り時集計（read-time）”があります👇 ([Firebase][1])

* `count()`：件数（何件ヒットした？）
* `sum()`：合計（いいね数の合計、課金額の合計など）
* `average()`：平均（平均いいね、平均スコアなど）

ポイントはこれ👇
**「集計をサーバー側で計算して、結果だけ返す」** ので、転送量も読み取りコストも節約しやすい、ということです📉✨ ([Firebase][1])

---

## 2) “使いどころ”はここ！✅（日報/記事/コメントの例つき）

あなたの題材（日報/記事/コメント3階層）で超よくあるのはこのへん👇

* 記事一覧：タイトルの横に **「コメント(12)」** を出したい💬
* 検索結果：フィルタ後に **「全 1,234 件」** を出したい🔎
* ダッシュボード：今週の **合計いいね数** / **平均いいね数** を出したい📈

こういう「数字だけ欲しい」場面で、Aggregation Queries が刺さります🎯 ([Firebase][1])

---

## 3) 超重要な注意点（ここで事故が減る）🧯

## A. “リアルタイム購読”できない 😭

集計結果を `onSnapshot` みたいに **購読してリアルタイム更新**…は **できません**。
リアルタイムに数字が動いてほしいなら、次章の「書き込み時集計（Write-time）」系（分散カウンタ等）に寄せます💡 ([Firebase][2])

## B. “キャッシュ前提”にも向かない 🧊

集計クエリは **クライアント側キャッシュに載せたい** みたいな用途とも相性がよくないです。
「毎回サクッと取りに行く」か、「書き込み時に集計を保存」するかを選びます🙂 ([Firebase][2])

## C. `sum()` / `average()` は“数値以外を無視”する⚠️

* `sum()` と `average()` は **数値じゃない値を無視** します（nullや文字列が混ざるとズレる）
* `count()` は **数値かどうか関係なく** ドキュメント数を数えます

なので、**`count()` と `average()` を同時に出すと「母数が違う」** みたいなズレが起きがちです😇
対策は簡単で、**集計したいフィールドは必ず数値で入れる（初期値0）** に寄せるのが安全です✅ ([Firebase][3])

## D. 複数フィールドの集計を同時にすると“対象ドキュメントが絞られる”ことがある🧩

別フィールドの集計を同時に組むと、**両方のフィールドを持つドキュメントだけ** が対象になるケースがあります。
「なんか合計が小さい…」ってときはここを疑うと早いです👀 ([Firebase][3])

---

## 4) 読む：料金イメージ（めちゃ大事）💰

Aggregation Queries は、ざっくり言うと **スキャンした“インデックスエントリ”量** に応じて課金されます。
目安として **0〜1000件ぶんのインデックス読み取りで “1 read”**、1500件なら“2 read”みたいな感じです📚 ([Firebase][4])

たとえば👇

* 条件に一致するのが約 12,000 件 → **だいたい 12 read 相当**（※インデックス読みの話）
  みたいな感覚になります。
  「全部ドキュメントを読むより、かなり軽くなりやすい」方向性ですね✨ ([Firebase][4])

---

## 5) 手を動かす：`count()` を実装して「コメント数」を出す💬

## 5-1. コメント数を数える（サブコレ想定）

```
import { getFirestore } from "firebase/firestore";
import { collection, getCountFromServer } from "firebase/firestore";

const db = getFirestore();

export async function fetchCommentCount(postId: string) {
  const commentsRef = collection(db, "posts", postId, "comments");
  const snap = await getCountFromServer(commentsRef);
  return snap.data().count; // number
}
```

`getCountFromServer()` の形は公式サンプルと同じです👍 ([Firebase][1])

## 5-2. Reactで表示する（最小形）

React で「記事カードの右上にコメント数」みたいに出すなら、こんな感じ👇

```
import { useEffect, useState } from "react";
import { fetchCommentCount } from "./fetchCommentCount";

export function useCommentCount(postId: string) {
  const [count, setCount] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    (async () => {
      try {
        setError(null);
        setCount(null);
        const n = await fetchCommentCount(postId);
        if (!cancelled) setCount(n);
      } catch (e) {
        if (!cancelled) setError("コメント数の取得に失敗しました💦");
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [postId]);

  return { count, error };
}
```

UI側は👇みたいなノリでOKです😄

* `count === null` → “…” 表示
* `count !== null` → `コメント(${count})` 表示

---

## 6) 手を動かす：`sum()` / `average()` で「合計いいね」「平均いいね」を出す📈

例えば `posts` に `likesCount: number` が入っているとして👇
（※入ってないなら、まず **0で必ず入れる** のが安全でしたね✅）

```
import { getFirestore } from "firebase/firestore";
import {
  collection, query, where,
  getAggregateFromServer, sum, average, count,
} from "firebase/firestore";

const db = getFirestore();

export async function fetchPostLikeStats() {
  const postsRef = collection(db, "posts");
  const q = query(postsRef, where("status", "==", "published"));

  const snap = await getAggregateFromServer(q, {
    postCount: count(),
    totalLikes: sum("likesCount"),
    avgLikes: average("likesCount"),
  });

  const data = snap.data();
  return {
    postCount: data.postCount,
    totalLikes: data.totalLikes,
    avgLikes: data.avgLikes,
  };
}
```

`getAggregateFromServer()` に `{ 名前: sum("field") }` みたいに渡すのが基本形です✨ ([Firebase][1])

---

## 7) ミニ課題🎒（10〜20分）

## お題：記事一覧に「コメント数」と「合計件数」を足す🧩

**やること**👇

1. 記事一覧（`posts`）を表示
2. 各記事カードに `コメント(◯)` を表示（`posts/{id}/comments` を `count()`）💬
3. 一覧上部に `全◯件` を表示（`posts` を `count()`）🔎

**できたら追加**👇（余力ある人向け✨）

* “公開済みだけ”にフィルタして `count()`
* “公開済みの平均いいね”を `average("likesCount")` で表示📈

---

## 8) チェック✅（ここまでできたら勝ち）

* [ ] 「**集計は count/sum/average**」が言える ([Firebase][1])
* [ ] 「集計は **結果だけ返るから軽くなりやすい**」が腹落ちしてる ([Firebase][1])
* [ ] 「課金は **インデックスエントリ基準（1000ごとに1 read目安）**」の感覚がある ([Firebase][4])
* [ ] 「集計は **リアルタイム購読できない** → 必要なら書き込み時集計」までつながる ([Firebase][2])
* [ ] `sum/average` は **数値以外を無視** するので、フィールド設計で事故を防げる ([Firebase][3])

---

## 9) AIで爆速にするコツ🤖⚡（Antigravity / Gemini CLI もOK）

Google Antigravity や Gemini CLI を使うなら、この章は **「実装の雛形を一気に作らせる」** が最強です😄

ちなみに、Firebase AI Logic を使うと、アプリから **Gemini系モデル** を呼ぶ導線も作りやすいです（App Checkなどと組み合わせやすい思想）🤖🔐 ([Firebase][5])
（※この章では“設計・実装補助”としてAIを使うイメージでOK！）

## コピペ用プロンプト例📎

* **① 集計設計レビュー**

  * 「posts/commentsの画面要件はこれ。`count/sum/average` で実現できるもの／できないものを仕分けして、次章の分散カウンタに回すべき項目も教えて」
* **② 実装雛形ジェネレート（TS/React）**

  * 「`useCommentCount(postId)` と `fetchPostLikeStats()` を、エラーハンドリング・ローディング状態込みで最小実装して」
* **③ 数値フィールド事故チェック**

  * 「`sum/average` でズレが起きるケース（null/欠損/文字列混入）を洗い出して、Firestore保存ルール（0埋め）を提案して」

---

次の第12章では、ここで出た弱点（**リアルタイム集計したい・超頻繁更新がある**）を、分散カウンタでガッチリ守ります🧱🔥

[1]: https://firebase.google.com/docs/firestore/query-data/aggregation-queries?hl=ja "集計クエリでデータを要約する  |  Firestore  |  Firebase"
[2]: https://firebase.google.com/docs/firestore/solutions/aggregation "Write-time aggregations  |  Firestore  |  Firebase"
[3]: https://firebase.google.com/docs/firestore/query-data/aggregation-queries?utm_source=chatgpt.com "Summarize data with aggregation queries | Firestore - Firebase"
[4]: https://firebase.google.com/docs/firestore/pricing "Understand Cloud Firestore billing  |  Firebase"
[5]: https://firebase.google.com/docs/ai-logic?utm_source=chatgpt.com "Gemini API using Firebase AI Logic - Google"
