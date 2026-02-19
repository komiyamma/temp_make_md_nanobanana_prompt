# 第14章：リアルタイム更新の気持ちよさを入れる ⚡👀（Firestore購読 onSnapshot 編）

この章では、Firestoreの「リアルタイム購読」をReactに入れて、**別タブで更新したら画面が勝手に追従する**“気持ちよさ”を作ります😆✨
Firestoreのリアルタイムは「スナップショットリスナー（snapshot listener）」で、**接続は長時間開きっぱなしになり、アプリが明示的に閉じるまで維持**されます。だからこそ「解除（cleanup）」が超重要です🧹🔥 ([Firebase][1])

---

## 1) まずイメージ：購読（subscribe）ってなに？📡

![Fetch vs Realtime Comparison](./picture/firebase_frontend_foundation_ts_study_014_01_fetch_vs_stream.png)

* **1回だけ取得**：必要な時に取りに行って終わり（例：設定画面の初期表示）
* **購読（onSnapshot）**：最初に現在のデータが届いて、その後も更新があるたびに届く📬✨
  最初のコールで、すぐ現在のスナップショットが来て、変更のたびに呼ばれます。([Google Cloud Documentation][2])

そして **onSnapshot は解除用の関数（unsubscribe）を返す**ので、これを呼ぶと止まります🛑 ([Firebase][3])

---

## 2) 実装のゴール 🎯

* ✅ 一覧ページ（例：Users）を **リアルタイムで自動更新**
* ✅ 画面を離れたら **購読解除**（メモリリーク回避）
* ✅ “更新された感”を出す（例：更新トースト/点滅など）✨
* ✅ ついでに「AI処理でFirestoreが更新されたらUIが勝手に追従」も体験できる🤖

---

## 3) いちばん大事：Reactでの正しい型 🧠🧹

![React Effect Lifecycle](./picture/firebase_frontend_foundation_ts_study_014_02_lifecycle_pattern.png)

## ✅ 基本パターン（useEffectで購読→returnで解除）

Firestore公式の例でも、Webは `onSnapshot(...)` が解除関数を返して、それを後で呼ぶ流れです。([Firebase][3])

ポイントはこれ👇

* `useEffect(() => { const unsub = onSnapshot(...); return () => unsub(); }, [依存])`
* **依存配列が変わるたびに再購読**になるので、`query(...)` を毎回作らない工夫が必要（後でやる！）

---

## 4) 手を動かす：Users一覧をリアルタイム購読にする 🛠️📋

ここでは “users コレクションを一覧表示” を例にします🙂

## 4-1. 型（TypeScript）を用意 🧩

```ts
export type UserRow = {
  id: string;
  displayName: string;
  role: "admin" | "editor" | "viewer";
  updatedAt?: Date; // Firestore TimestampをDateに変換して入れる想定
};
```

## 4-2. 「購読をまとめるhook」を作る（おすすめ）🪝✨

![Realtime Hook Structure](./picture/firebase_frontend_foundation_ts_study_014_03_hook_structure.png)

`useUsersRealtime.ts`（例）

```ts
import { useEffect, useMemo, useState } from "react";
import {
  collection,
  onSnapshot,
  orderBy,
  query,
  limit,
  type QuerySnapshot,
  type DocumentData,
} from "firebase/firestore";
import { db } from "../services/firebase"; // 第10章のfirebase.ts想定

type UserRow = {
  id: string;
  displayName: string;
  role: "admin" | "editor" | "viewer";
  updatedAt?: Date;
};

function mapUsersSnapshot(snapshot: QuerySnapshot<DocumentData>): UserRow[] {
  return snapshot.docs.map((d) => {
    const data = d.data();
    return {
      id: d.id,
      displayName: String(data.displayName ?? ""),
      role: (data.role ?? "viewer") as UserRow["role"],
      updatedAt: data.updatedAt?.toDate?.(),
    };
  });
}

export function useUsersRealtime() {
  const [data, setData] = useState<UserRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // ★超重要：queryをuseMemoで固定して、再レンダーで購読が張り直されないようにする
  const q = useMemo(() => {
    return query(
      collection(db, "users"),
      orderBy("updatedAt", "desc"),
      limit(50)
    );
  }, []);

  useEffect(() => {
    setLoading(true);
    setError(null);

    // onSnapshotは解除関数を返す（unsubscribe）
    const unsubscribe = onSnapshot(
      q,
      (snapshot) => {
        setData(mapUsersSnapshot(snapshot));
        setLoading(false);
      },
      (e) => {
        console.error(e);
        setError("読み込みに失敗しました（権限や通信を確認してね）🙏");
        setLoading(false);
      }
    );

    // ★cleanup：画面を離れたら購読解除
    return () => unsubscribe();
  }, [q]);

  return { data, loading, error };
}
```

* `onSnapshot(query, onNext, onError)` の形で **エラーも受け取れます**🧯 ([Firebase][3])
* `unsubscribe()` で止められます🛑 ([Firebase][3])

## 4-3. 画面で使う（UsersPage）🧑‍💻

```tsx
import { useUsersRealtime } from "../hooks/useUsersRealtime";

export function UsersPage() {
  const { data, loading, error } = useUsersRealtime();

  if (loading) return <div className="p-4">読み込み中...⏳</div>;
  if (error) return <div className="p-4 text-red-600">{error}</div>;

  return (
    <div className="p-4">
      <h1 className="text-xl font-bold mb-3">Users 👥</h1>

      {data.length === 0 ? (
        <div className="opacity-70">0件です🙂</div>
      ) : (
        <div className="space-y-2">
          {data.map((u) => (
            <div key={u.id} className="rounded-xl border p-3">
              <div className="font-semibold">{u.displayName}</div>
              <div className="text-sm opacity-70">
                role: {u.role} / updated: {u.updatedAt?.toLocaleString() ?? "-"}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

---

## 5) ミニ課題：別タブ更新で「勝手に変わる」を体験 🎯⚡

![Multi-tab Synchronization](./picture/firebase_frontend_foundation_ts_study_014_04_multitab_sync.png)

1. ブラウザで **同じアプリを2タブ**開く🪟🪟
2. 片方でユーザーを更新（またはFirebaseコンソールで編集）✍️
3. もう片方が **自動で更新される**のを確認👀✨

「おお〜！」ってなるやつです😆

---

## 6) さらに気持ちよく：差分（docChanges）で“追加/変更/削除”を演出 🎉

![docChanges Events](./picture/firebase_frontend_foundation_ts_study_014_05_doc_changes.png)

Firestoreの例では、`snapshot.docChanges()` で **added / modified / removed** が取れます。([Firebase][3])

たとえば👇

* added → 「新しいユーザーが追加されました✨」
* modified → 「更新されました🔁」
* removed → 「削除されました🗑️」

※初心者のうちは、まずは「全部描き直し（setData(全部))」でOK！
慣れてきたら差分演出に挑戦すると楽しいです😄

---

## 7) つまずきポイント集 🧨（ここ超大事）

## ❌ 1) 購読解除し忘れ（メモリリーク）😱

![Memory Leak Ghost](./picture/firebase_frontend_foundation_ts_study_014_06_memory_leak.png)

リアルタイム接続は長く維持されるので、解除しないと裏で生き続けがちです。([Firebase][1])
→ `useEffect` の `return () => unsubscribe()` を必ず書く🧹 ([Firebase][3])

## ❌ 2) queryを毎回作って再購読ループ🔁

`query(collection(...))` をコンポーネント内で毎回作ると、依存が変わって購読が張り直されがち💦
→ `useMemo` で固定する✅

## ❌ 3) でかすぎる購読（全件購読）で重い＆コスト怖い💸

Firestoreの課金は **読み書き・インデックス読み・保存容量・帯域**などで計算されます。([Firebase][4])
さらに、リアルタイムは内部的に“取得＋listen維持”の性質があって、読み取りの扱いも理解しておくのが安全です🧠 ([Firebase][1])
→ `where` / `orderBy` / `limit` で狭くする✅（第15章のページングにもつながる！）

---

## 8) ちょい上級：オフライン/キャッシュっぽい挙動を見たい（metadata）🧊📶

`includeMetadataChanges: true` を渡すと、メタデータ変化も拾えます。([Firebase][3])
たとえば「キャッシュ由来なのか？」みたいな表示を作る入口になります🙂

（最初は深追いしなくてOK！“そういう仕組みがある”を知っておくと強い💪）

---

## 9) AIとのつながり（この章の裏テーマ）🤖✨

![AI Realtime Update Flow](./picture/firebase_frontend_foundation_ts_study_014_07_ai_realtime.png)

これ、めちゃ相性いいです👇

* ボタン押す
* Functions / FirebaseのAI系で文章整形 or 分類
* 結果がFirestoreに書き込まれる
* **この章のリアルタイム購読でUIが勝手に更新される**⚡

つまり「AI処理の結果を待って、リロード無しで画面が追従」できるわけです。体験として強い🔥

---

## 10) チェック✅（章のゴール達成？）

* ✅ 別タブで更新したら一覧が勝手に変わる
* ✅ 画面移動で購読解除できてる（useEffect cleanup）
* ✅ エラー時に“無言”にならずメッセージが出る
* ✅ `limit` を付けて購読範囲を絞れた（次章の布石📜）

---

## おまけ：Geminiに手伝わせるなら（例）🛸💻

* 「Firestoreのusers用に、`useUsersRealtime` をもっと汎用hookにしたい。Queryを受け取って型安全に返す案を出して」
* 「docChangesを使って、added/modified/removedでトーストを出す最小実装を作って」

出てきたコードは、**依存配列・unsubscribe・limit** の3点だけは必ず目視チェックしてね👀✅（ここが事故りやすい！）

---

次の第15章は、この購読を「ページング/無限スクロール」に拡張して、**速い＆安い＆気持ちいい**一覧にしていきます📜🔥

[1]: https://firebase.google.com/docs/firestore/enterprise/real-time-queries-at-scale "Understand real-time listen queries at scale  |  Firestore  |  Firebase"
[2]: https://docs.cloud.google.com/firestore/native/docs/query-data/listen "Get real-time updates  |  Firestore in Native mode  |  Google Cloud Documentation"
[3]: https://firebase.google.com/docs/firestore/query-data/listen "Get realtime updates with Cloud Firestore  |  Firebase"
[4]: https://firebase.google.com/docs/firestore/pricing "Understand Cloud Firestore billing  |  Firebase"
