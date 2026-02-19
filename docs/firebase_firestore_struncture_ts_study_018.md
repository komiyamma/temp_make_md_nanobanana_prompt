# 第18章：ページング設計（無限スクロールの作法）📜✨

この章では「記事一覧を無限スクロールにしたい！」を **壊れにくく・安く・速く** 実現するための “設計の型” を作ります😄🔥
Firestoreのページングは、基本 **`limit` + カーソル（`startAfter` など）** でやるのが王道です✅

---

## 1) まず結論：ページングの正解ルートはこれ！✅📌

**✅オフセット（n件スキップ）は避ける

![firebase_firestore_struncture_ts_study_018_01_offset_vs_cursor.png](./picture/firebase_firestore_struncture_ts_study_018_01_offset_vs_cursor.png)**
Firestoreは `offset` を使うと、**スキップした分も読み取り課金**されます💸（例：offset10で1件返っても11 reads）
なので **カーソル（cursors）を使う**のが推奨です✨ ([Firebase][1])

**✅実装は “この形” を基本にする**

* 並び順：`orderBy(createdAt desc)`（＋できれば第2キーも！）
* 取得数：`limit(PAGE_SIZE)`
* 次ページ：`startAfter(lastDoc)`（最後のドキュメントをカーソルにする）

`startAt()` は「その位置を含む」、`startAfter()` は「含まない」ので、重複防止の意味でも `startAfter()` が扱いやすいです🙂 ([Firebase][2])

---

## 2) “壊れない無限スクロール” のための設計チェックリスト🧠✅

### ✅(A) ソートキーは **変わらないもの** を使う📌

無限スクロールは「**前ページの続き**」を取ります。
だから途中で並び順が変わる（例：`likesCount` が増える）と、**重複・抜け**が起きやすいです😇💥

おすすめは👇

* `createdAt`（作成時刻）
* `publishedAt`（公開時刻）
* `id`（ドキュメントID）

### ✅(B) `orderBy()` したフィールドは **全ドキュメントに必ず入れる**🧱

`orderBy()` は **そのフィールドを持たないドキュメントを結果から除外**します⚠️
つまり `createdAt` が入ってない投稿が混ざると、一覧から消えて「え？ないんだけど？」になります😂

![firebase_firestore_struncture_ts_study_018_02_missing_field.png](./picture/firebase_firestore_struncture_ts_study_018_02_missing_field.png) ([Firebase][3])

> 対策：作成時に `createdAt` を必ず入れる（設計で勝つ🏆）

### ✅(C) “同じ値が並ぶ” 可能性があるなら第2キーを足す🎯

カーソルを「フィールド値」で作ると、**同じ値のドキュメントが複数あると曖昧**になって狙い通りにページングできないことがあります（公式ドキュメントでも注意されています） ([Firebase][2])

対策は2つ👇

![firebase_firestore_struncture_ts_study_018_03_tie_breaker.png](./picture/firebase_firestore_struncture_ts_study_018_03_tie_breaker.png)

1. **DocumentSnapshot（最後のドキュメント）をカーソルにする**（一番ラクで強い💪）
2. フィールド値カーソルを使うなら、**複数フィールドでカーソルを精密化**する（例：`createdAt` + `id`） ([Firebase][2])

---

## 3) 手を動かす：Firestoreの “ページ取得関数” を作ろう🛠️📄

ここでは「posts（記事）」を **新しい順** に20件ずつ読みます。
ポイントは👇

* **並び順を固定**（`createdAt desc`）
* **次ページは `startAfter(lastDoc)`**
* **lastDoc は QuerySnapshot の最後の doc**

> 公式でも「最後のドキュメントを取って、次クエリを startAfter で作る」流れが紹介されています📌

![firebase_firestore_struncture_ts_study_018_04_paging_flow.png](./picture/firebase_firestore_struncture_ts_study_018_04_paging_flow.png) ([Firebase][2])

```ts
import {
  collection,
  documentId,
  getDocs,
  limit,
  orderBy,
  query,
  startAfter,
  QueryDocumentSnapshot,
  DocumentData,
  Timestamp,
} from "firebase/firestore";
import { db } from "./firebase"; // 既に作ってある想定

export type Post = {
  id: string;
  title: string;
  body: string;
  createdAt: Timestamp;
  authorId: string;
};

const PAGE_SIZE = 20;

// 1ページ取得（cursor が null なら最初のページ）
export async function fetchPostsPage(cursor: QueryDocumentSnapshot<DocumentData> | null) {
  const postsRef = collection(db, "posts");

  // 安定ソート：createdAt + docId（同値対策の第2キー）
  const base = [
    orderBy("createdAt", "desc"),
    orderBy(documentId(), "desc"),
    limit(PAGE_SIZE),
  ] as const;

  const q = cursor
    ? query(postsRef, ...base, startAfter(cursor))
    : query(postsRef, ...base);

  const snap = await getDocs(q);

  const posts: Post[] = snap.docs.map((d) => {
    const data = d.data() as Omit<Post, "id">;
    return { id: d.id, ...data };
  });

  const nextCursor = snap.docs.length > 0 ? snap.docs[snap.docs.length - 1] : null;

  // hasMore は “今回PAGE_SIZE取れたか” でざっくり判定（初心者向けでOK）
  const hasMore = snap.docs.length === PAGE_SIZE;

  return { posts, nextCursor, hasMore };
}
```

**なぜ `orderBy(documentId())` を足した？🤔**
`createdAt` が同じ投稿があり得るからです（同値でページ境界が曖昧になるのを避けたい）✨
「フィールド値カーソルは同値があると期待通りにならない」という注意は公式にもあります📌 ([Firebase][2])

---

## 4) React：無限スクロール用の Hook を作る🪝⚡

![firebase_firestore_struncture_ts_study_018_05_hook_state.png](./picture/firebase_firestore_struncture_ts_study_018_05_hook_state.png)

やりたいことはシンプル👇

* 画面表示で最初のページを読み込む
* 下まで来たら次ページを読む
* ローディング中は二重読み込みしない

```tsx
import { useCallback, useEffect, useRef, useState } from "react";
import type { Post } from "./fetchPostsPage";
import { fetchPostsPage } from "./fetchPostsPage";
import type { QueryDocumentSnapshot, DocumentData } from "firebase/firestore";

export function useInfinitePosts() {
  const [items, setItems] = useState<Post[]>([]);
  const [hasMore, setHasMore] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const cursorRef = useRef<QueryDocumentSnapshot<DocumentData> | null>(null);

  const loadMore = useCallback(async () => {
    if (loading || !hasMore) return;

    setLoading(true);
    setError(null);
    try {
      const { posts, nextCursor, hasMore: more } = await fetchPostsPage(cursorRef.current);

      // 超初歩の重複対策：idでユニークにする（安全側）
      setItems((prev) => {
        const map = new Map(prev.map((p) => [p.id, p]));
        for (const p of posts) map.set(p.id, p);
        return Array.from(map.values());
      });

      cursorRef.current = nextCursor;
      setHasMore(more);
    } catch (e: any) {
      setError(e?.message ?? "読み込みに失敗しました");
    } finally {
      setLoading(false);
    }
  }, [loading, hasMore]);

  // 初回ロード
  useEffect(() => {
    loadMore();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return { items, hasMore, loading, error, loadMore };
}
```

---

## 5) IntersectionObserverで “下に来たら読む” 👀👇

![firebase_firestore_struncture_ts_study_018_06_sentinel_trigger.png](./picture/firebase_firestore_struncture_ts_study_018_06_sentinel_trigger.png)

```tsx
import { useEffect, useRef } from "react";
import { useInfinitePosts } from "./useInfinitePosts";

export function PostsInfiniteList() {
  const { items, hasMore, loading, error, loadMore } = useInfinitePosts();
  const sentinelRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!sentinelRef.current) return;

    const el = sentinelRef.current;
    const obs = new IntersectionObserver(
      (entries) => {
        if (entries[0]?.isIntersecting) {
          loadMore();
        }
      },
      { rootMargin: "300px" } // ちょい早めに読む（体験が良くなる✨）
    );

    obs.observe(el);
    return () => obs.disconnect();
  }, [loadMore]);

  return (
    <div>
      <h2>記事一覧</h2>

      {items.map((p) => (
        <article key={p.id} style={{ borderBottom: "1px solid #ddd", padding: 8 }}>
          <h3>{p.title}</h3>
          <p>{p.body}</p>
        </article>
      ))}

      {error && <p style={{ color: "crimson" }}>⚠️ {error}</p>}
      {loading && <p>読み込み中…⏳</p>}
      {!hasMore && <p>ここまで！🎉</p>}

      {/* これが “監視ターゲット” */}
      <div ref={sentinelRef} style={{ height: 1 }} />
    </div>
  );
}
```

---

## 6) “あるある事故” と対策集💥🧯

### 事故①：途中で並び順が変わって、重複・抜ける😵

* 例：`likesCount desc` で並べてたら、スクロール中に誰かが「いいね」→順位が変わる
* 対策：

  * ページングは **安定キー（createdAtなど）** を使う
  * 人気順にしたいなら **ランキング専用コレクション** を作って “固定された並び” を読む（第13章の発想）🥇

### 事故②：`orderBy(createdAt)` なのに一部の投稿が出ない😇

* 原因：`createdAt` が無いドキュメントは結果から除外されるため
* 対策：作成時に必ず埋める（設計で勝つ）
  ([Firebase][3])

### 事故③：同じ `createdAt` が続いてページ境界が曖昧🤔

* 対策：

  * **DocumentSnapshot をカーソルにする**（`startAfter(lastDoc)`）
  * もしくは **第2キー** を足して曖昧さを潰す（`createdAt + id` など）
    ([Firebase][2])

### 事故④：offsetでページングしてたらコストが爆増💸

* 対策：カーソルを使う（公式が「可能なら offsets より cursors」推し）
  ([Firebase][1])

---

## 7) AIも絡めて強くする🤖⚡（Gemini / Antigravity / Firebase AI）

### ✅Gemini CLI：コードと設計レビューが速い🧠💨

Gemini CLI は、ターミナル/grep/ファイル操作/ウェブ検索などを組み合わせて進められる前提があり、VS Codeのエージェントモードとも関係があります📌 ([Google for Developers][4])

### ✅Antigravity：エージェントに “実装→差分→検証” まで任せやすい🧰✨

Googleの Antigravity は、会話を追えるInboxや、ファイル生成・差分レビュー・ブラウザ操作のサブエージェントなどの概念が整理されています📌 ([Google Codelabs][5])

### ✅Firebase AI Logic：無限スクロールと相性が良いけど “レート制限” に注意⚠️

無限スクロールで「各投稿をAIで要約」みたいにすると、スクロールだけでリクエストが増えます📈
Firebase AI Logic 側には “per user” のレート制限があり

![firebase_firestore_struncture_ts_study_018_07_ai_guard.png](./picture/firebase_firestore_struncture_ts_study_018_07_ai_guard.png)、**デフォルトが 100 RPM** と明記されています（必要に応じて調整推奨）([Firebase][6])

> 対策アイデア💡
>
> * 要約は「表示された時だけ」＆「一度作ったらFirestoreにキャッシュ」
> * 連続スクロール中はまとめて実行（デバウンス）
> * 監査ログ（aiLogs）に残してコスト追跡（第20章の発想）🧾

---

## 8) ミニ課題（やると強くなる🔥）📝

**ミニ課題A：無限スクロール完成🎯**

* 新しい順に20件ずつ読み込む
* 最後まで行ったら「ここまで！」表示🎉

**ミニ課題B：検索条件を足して壊れないか確認🔎**

* 例：`where("authorId","==",uid)` を追加
* ページングが同じように動くか確認（必要ならインデックス作成）

**ミニ課題C：AI要約を “1投稿につき1回だけ” 生成して保存🤖🧠**

* 表示時に要約が無ければ生成 → `posts/{id}` に `summary` 保存
* 連続スクロールでレート制限に当たりにくい工夫を入れる（デバウンス）
  ([Firebase][6])

---

## 9) チェック（この章の合格ライン✅）

* [ ] `limit + startAfter` でページングできた
* [ ] ソートキーが安定していて、途中で並びが崩れにくい
* [ ] `createdAt` が無いドキュメントが混ざる事故を潰せた（`orderBy` の性質を理解）([Firebase][3])
* [ ] 同値（同じ createdAt）対策として第2キー or DocumentSnapshotカーソルを使えた([Firebase][2])
* [ ] offsetのコスト罠を説明できる（cursors推しの理由）([Firebase][1])

---

おつかれ！ここまでできると、Firestoreの一覧画面はもう怖くないです😄💪✨
次の第19章（型安全CRUD）に進むと、今作ったページングが **型で守られて気持ちよく** なりますよ〜🧱🔥

[1]: https://firebase.google.com/docs/firestore/pricing "Understand Cloud Firestore billing  |  Firebase"
[2]: https://firebase.google.com/docs/firestore/query-data/query-cursors "Paginate data with query cursors  |  Firestore  |  Firebase"
[3]: https://firebase.google.com/docs/firestore/query-data/order-limit-data "Order and limit data with Cloud Firestore  |  Firebase"
[4]: https://developers.google.com/gemini-code-assist/docs/gemini-cli "Gemini CLI  |  Gemini Code Assist  |  Google for Developers"
[5]: https://codelabs.developers.google.com/getting-started-google-antigravity "Getting Started with Google Antigravity  |  Google Codelabs"
[6]: https://firebase.google.com/docs/ai-logic/quotas "Rate limits and quotas  |  Firebase AI Logic"
