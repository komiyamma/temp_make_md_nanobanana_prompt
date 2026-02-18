# 第15章：ページングと無限スクロールの入口 📜🧠

（Firestore の `limit` + `startAfter` で「さらに読み込む」を作るよ！✨）

---

## この章でできるようになること ✅

* Firestore の一覧を **少しずつ取得（ページング）**できるようになる 📄➡️📄
* 「**さらに読み込む**」ボタンで、**重複なし**＆**二重クリック事故なし**に追加表示できる 🔁🛡️
* 余力で「**無限スクロール**」にもできる 🌊✨

Firestore のページングは、公式的にも **“カーソル（cursor）＋ limit”** が基本です。([Firebase][1])
そして `offset` を使うと、**飛ばした分も読み取り課金**になるので避けたい…！というのも重要ポイントです💸😇([Firebase][2])

---

## まず「ページングの考え方」💡

## 1) offset じゃなく cursor（カーソル）を使う理由 🧾➡️🎯

* SQLの `OFFSET 100` みたいに “100件飛ばして次” は、Firestore だとコスト面で不利になりがち😵‍💫
* **カーソル方式**は「前回の最後のドキュメント（`DocumentSnapshot`）を覚えて、次はそこから先を取る」感じ✨

  * 公式サンプルもまさにこれ：**`lastVisible` を `startAfter(lastVisible)` に渡す**([Firebase][1])
* `offset` は **スキップした分も読み取り**として数えられやすいので、できるだけ cursor が推奨💸([Firebase][2])

---

## 実装パート：まずは「さらに読み込む」ボタン版 🔘📥

ここでは「users 一覧」を例にします（他のコレクションでも同じだよ🙂）。

## 0) 先に“並び順”を決めよう（超重要）🧭

ページングは **順番が命**です⚠️

* 例：`updatedAt`（更新日時）で新しい順
* ただし、`orderBy()` は **そのフィールドが存在するドキュメントだけ**返す点に注意！
  → `updatedAt` が入ってない古いドキュメントがあると、一覧から消えます👻([Firebase][3])

💡おすすめ：

* **全ドキュメントに `updatedAt` を必ず入れる**（作成時・更新時にセット）
* “同点”（同じ `updatedAt`）で順序がブレないように、**第2キーに `documentId()`** を足す（安定する）✨

---

## 1) ページング用の hook を作る 🪝✨

ポイントは3つ👇

1. `lastVisible`（最後のスナップショット）を覚える
2. `loading` 中は追加取得させない（二重クリック防止）
3. `Set` で **ID重複をガード**（安全第一🛡️）

```ts
// src/hooks/useUsersPaging.ts
import { useCallback, useRef, useState } from "react";
import {
  collection,
  documentId,
  getDocs,
  limit,
  orderBy,
  query,
  startAfter,
  type DocumentSnapshot,
  type QueryDocumentSnapshot,
} from "firebase/firestore";

import { db } from "../lib/firebase"; // あなたの firebase.ts の場所に合わせてね🙂

export type UserRow = {
  id: string;
  displayName?: string;
  role?: string;
  updatedAt?: any; // Timestamp想定（表示の章で整えるでもOK）
};

const PAGE_SIZE = 25;

export function useUsersPaging() {
  const [items, setItems] = useState<UserRow[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasMore, setHasMore] = useState(true);

  const lastRef = useRef<DocumentSnapshot | null>(null);
  const seenIdsRef = useRef<Set<string>>(new Set());

  const loadMore = useCallback(async () => {
    if (loading || !hasMore) return; // 二重クリック＆終端ガード🛑
    setLoading(true);
    setError(null);

    try {
      const base = [
        orderBy("updatedAt", "desc"),
        orderBy(documentId(), "desc"),
        limit(PAGE_SIZE),
      ] as const;

      const q = lastRef.current
        ? query(collection(db, "users"), ...base, startAfter(lastRef.current))
        : query(collection(db, "users"), ...base);

      const snap = await getDocs(q);

      // 0件なら終わり🏁
      if (snap.empty) {
        setHasMore(false);
        return;
      }

      const docs = snap.docs;
      const lastVisible = docs[docs.length - 1];
      lastRef.current = lastVisible;

      // 追加分を作る（重複IDは捨てる🧹）
      const nextItems: UserRow[] = [];
      for (const d of docs as QueryDocumentSnapshot[]) {
        if (seenIdsRef.current.has(d.id)) continue;
        seenIdsRef.current.add(d.id);
        nextItems.push({ id: d.id, ...(d.data() as Omit<UserRow, "id">) });
      }

      setItems((prev) => [...prev, ...nextItems]);

      // 「今回がPAGE_SIZE未満」なら次はない可能性が高い📉
      if (docs.length < PAGE_SIZE) {
        setHasMore(false);
      }
    } catch (e: any) {
      setError(e?.message ?? "読み込みに失敗しました");
    } finally {
      setLoading(false);
    }
  }, [hasMore, loading]);

  const reset = useCallback(() => {
    setItems([]);
    setError(null);
    setHasMore(true);
    lastRef.current = null;
    seenIdsRef.current = new Set();
  }, []);

  return { items, loading, error, hasMore, loadMore, reset };
}
```

🔥ここで使っているページングの考え方は公式と同じで、**「最初は `limit`、次は `startAfter(lastVisible)`」**です。([Firebase][1])

---

## 2) 画面に「さらに読み込む」ボタンを置く 🧱🎽

Tailwind でそれっぽく✨（押せない時は薄く＆カーソル変える）

```tsx
// src/pages/UsersPage.tsx
import { useEffect } from "react";
import { useUsersPaging } from "../hooks/useUsersPaging";

export default function UsersPage() {
  const { items, loading, error, hasMore, loadMore, reset } = useUsersPaging();

  // 初回ロード
  useEffect(() => {
    loadMore();
  }, [loadMore]);

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold">Users</h1>

        <button
          onClick={() => {
            reset();
            loadMore();
          }}
          className="px-3 py-2 rounded-lg border text-sm hover:bg-gray-50"
        >
          🔄 最初から読み直す
        </button>
      </div>

      {error && (
        <div className="p-3 rounded-lg bg-red-50 border border-red-200 text-red-700">
          ❌ {error}
        </div>
      )}

      <div className="rounded-xl border overflow-hidden">
        <div className="grid grid-cols-3 bg-gray-50 text-sm font-semibold">
          <div className="p-3">名前</div>
          <div className="p-3">権限</div>
          <div className="p-3">ID</div>
        </div>

        {items.map((u) => (
          <div key={u.id} className="grid grid-cols-3 border-t text-sm">
            <div className="p-3">{u.displayName ?? "（未設定）"}</div>
            <div className="p-3">{u.role ?? "-"}</div>
            <div className="p-3 font-mono text-xs text-gray-600">{u.id}</div>
          </div>
        ))}

        {!loading && items.length === 0 && (
          <div className="p-6 text-gray-600">📭 0件です</div>
        )}
      </div>

      <div className="flex justify-center">
        <button
          onClick={loadMore}
          disabled={loading || !hasMore}
          className={[
            "px-4 py-2 rounded-xl font-semibold",
            "border shadow-sm",
            loading || !hasMore
              ? "opacity-50 cursor-not-allowed"
              : "hover:bg-gray-50",
          ].join(" ")}
        >
          {loading ? "⏳ 読み込み中..." : hasMore ? "📥 さらに読み込む" : "🏁 ここまで"}
        </button>
      </div>
    </div>
  );
}
```

---

## 3) 無限スクロール版（入口だけ）🌊✨

「一番下に見えない“当たり判定”を置いて、見えたら loadMore」方式だよ👀
IntersectionObserver はブラウザ標準なので追加ライブラリいらない👍

```tsx
// src/hooks/useInfiniteScroll.ts
import { useEffect } from "react";

export function useInfiniteScroll(params: {
  enabled: boolean;
  loading: boolean;
  onLoadMore: () => void;
  sentinel: React.RefObject<HTMLDivElement | null>;
}) {
  const { enabled, loading, onLoadMore, sentinel } = params;

  useEffect(() => {
    if (!enabled) return;
    if (!sentinel.current) return;

    const el = sentinel.current;

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0]?.isIntersecting && !loading) {
          onLoadMore();
        }
      },
      {
        // 少し早めに読み込む（体感が良い）✨
        rootMargin: "200px",
      }
    );

    observer.observe(el);
    return () => observer.disconnect();
  }, [enabled, loading, onLoadMore, sentinel]);
}
```

UsersPage 側にこう足す👇

```tsx
import { useRef } from "react";
import { useInfiniteScroll } from "../hooks/useInfiniteScroll";

const sentinelRef = useRef<HTMLDivElement | null>(null);

useInfiniteScroll({
  enabled: hasMore,
  loading,
  onLoadMore: loadMore,
  sentinel: sentinelRef,
});

// JSXの一番下に置く
<div ref={sentinelRef} className="h-10" />
```

---

## つまずきポイント集 🧯😵‍💫（ここ超大事）

## ✅ 1) 同じデータが重複したり、抜けたりする

* `startAfter(フィールド値)` 方式だと、同値が多いと事故ることがある（公式サンプルにも注意書きあり）😇([Firebase][1])
* なのでこの章では **`startAfter(lastVisibleDocumentSnapshot)`** を使ってます（安全✨）([Firebase][1])
* さらに念押しで **ID重複を Set で弾く** 🛡️（UIの安全装置）

## ✅ 2) `orderBy("updatedAt")` にしたら一部のドキュメントが消えた

* `orderBy()` は「そのフィールドが存在するドキュメントだけ」返す仕様です👻([Firebase][3])
  → **全ドキュメントに updatedAt を入れる**のが正攻法🙆‍♂️

## ✅ 3) offset でやりたくなる

* Firestore は cursor が基本で、`offset` は **スキップ分も読み取り課金**になりやすいです💸([Firebase][2])
  → “一覧は cursor” を癖にすると、運用が楽になります🙂

## ✅ 4) 複雑な条件（where + orderBy）で「インデックスが必要」エラー

* Firestore が「この組み合わせはインデックス作ってね」と教えてくれるやつ🧠
* エラー文に作成リンクが出るので、それに従えばOK（怖くない！）

---

## ミニ課題 🎯✨

## 課題A：ページサイズを変えられるようにする 🧮

* 25 / 50 / 100 をセレクトで選べるようにしてみよう🙂
* 変更したら `reset()` → `loadMore()` で読み直し！

## 課題B：一覧は軽く、詳細でAIを呼ぶ 🤖🧠

一覧で全件にAI処理をかけるとコスト爆発しがち💥

* 一覧：`displayName` / `role` / `updatedAt` だけ
* 詳細：開いた時に「プロフィール文章を要約」ボタンを出す

  * Gemini/Imagen をアプリから扱うなら、Firebase の **AI Logic** が入口になります🧩([Firebase][4])

---

## AIで“実装の品質”を上げる小ワザ 🛸🔧

## 1) Google の Gemini CLI に「事故パターン」を洗い出してもらう 🧠

Gemini CLI はドキュメントでも案内されている開発支援の入口です。([Google Cloud Documentation][5])
たとえばこんな観点を投げると強い👇

* 「二重クリックで二重ロードしない？」
* 「0件のとき lastVisible が undefined にならない？」
* 「同値の updatedAt が多いとき抜けない？」

## 2) Google の Antigravity に“ページングhookのリファクタ案”を出してもらう 🧩

Antigravity は “エージェント前提の開発プラットフォーム”として紹介されています。([Google Codelabs][6])
→ 「useUsersPaging を汎用化して `usePagedCollection<T>` にして！」みたいな依頼が相性いいです🙂✨

---

## チェック ✅（この章のゴール）

* [ ] 1回目は `limit()` で取れてる？([Firebase][1])
* [ ] 2回目以降は `startAfter(lastVisible)` になってる？([Firebase][1])
* [ ] 連打しても二重取得しない？🔒
* [ ] 取得順が安定して、重複表示しない？🧊
* [ ] `orderBy` のフィールドが欠けてて消える件を理解した？([Firebase][3])

---

必要なら次の一手として、**「検索条件（where）つきページング」**や、**「リアルタイム購読（onSnapshot）とページングの両立」**も続けて作れますよ😆🔥

[1]: https://firebase.google.com/docs/firestore/query-data/query-cursors "Paginate data with query cursors  |  Firestore  |  Firebase"
[2]: https://firebase.google.com/docs/firestore/pricing?utm_source=chatgpt.com "Understand Cloud Firestore billing - Firebase - Google"
[3]: https://firebase.google.com/docs/firestore/query-data/order-limit-data "Order and limit data with Cloud Firestore  |  Firebase"
[4]: https://firebase.google.com/docs/ai-logic?utm_source=chatgpt.com "Gemini API using Firebase AI Logic - Google"
[5]: https://docs.cloud.google.com/gemini/docs/codeassist/gemini-cli?utm_source=chatgpt.com "Gemini CLI | Gemini for Google Cloud"
[6]: https://codelabs.developers.google.com/getting-started-google-antigravity?utm_source=chatgpt.com "Getting Started with Google Antigravity"
