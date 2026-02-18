# 第07章：状態の3点セットを覚える 🔁😵‍💫（loading / error / data）

この章のゴールはシンプルです🙂
**「画面が沈黙しない」**＝**読み込み中 / 失敗 / 成功（データあり）**を必ず出せるようにします✨
（ついでに **0件** のときの表示も入れて、UIが完成形に近づきます📊）

---

## 読む📖：3点セットがないと何が起きる？😇

ありがちな事故👇

* 通信中なのに… **何も変わらない**（ユーザー「固まった？」）🧊
* 失敗したのに… **何も出ない**（ユーザー「押せてない？」）🫥
* データ0件なのに… **空白**（ユーザー「バグ？」）🫨

なので、画面はこの4状態を最低限持つのが強いです💪

1. **loading**：待ってね⏳
2. **error**：ごめん、失敗した🙏（＋リトライ🔁）
3. **data**：表示できた🎉
4. **empty**：0件です🙂（※dataの中の分岐）

この考え方は、Firestoreでも、Functionsでも、AI呼び出しでも全部同じです🧠✨
Firestoreのリアルタイム購読でも、**エラーコールバックを渡して失敗を拾える**ので「沈黙防止」に直結します📡💥 ([Firebase][1])

---

## 手を動かす🛠️：まず“状態”を型で固定しよう（TSの勝ち🏆）

## 1) `AsyncState<T>`（状態の型）を作る📦

```ts
// src/types/asyncState.ts
export type AsyncStatus = "idle" | "loading" | "success" | "error";

export type AsyncState<T> =
  | { status: "idle"; data?: undefined; error?: undefined }
  | { status: "loading"; data?: T; error?: undefined } // 前のdataを残してもOK
  | { status: "success"; data: T; error?: undefined }
  | { status: "error"; data?: T; error: Error };
```

ポイント💡

* `loading` のとき **前のdataを残せる**ようにしておくと、更新中でも画面がチカチカしません✨

---

## 2) “三兄弟”を管理する `useAsync` フックを作る🔁

```ts
// src/hooks/useAsync.ts
import { useCallback, useRef, useState } from "react";
import type { AsyncState } from "../types/asyncState";

export function useAsync<T>() {
  const [state, setState] = useState<AsyncState<T>>({ status: "idle" });
  const runIdRef = useRef(0);

  const run = useCallback(async (promiseFactory: () => Promise<T>) => {
    const runId = ++runIdRef.current;

    // 既存dataを残して "loading" にする（更新中スピナー向け✨）
    setState((prev) => ({ status: "loading", data: prev.data }));

    try {
      const data = await promiseFactory();
      if (runId !== runIdRef.current) return; // 古いリクエストは捨てる🗑️
      setState({ status: "success", data });
      return data;
    } catch (e) {
      if (runId !== runIdRef.current) return;
      const error = e instanceof Error ? e : new Error(String(e));
      setState((prev) => ({ status: "error", data: prev.data, error }));
      throw error;
    }
  }, []);

  const reset = useCallback(() => setState({ status: "idle" }), []);

  return { state, run, reset };
}
```

これで **どの非同期処理でも** `loading / error / data` を同じ書き方で扱えます🎯

---

## 手を動かす🛠️：表示部品を3つ作る（Spinner / Error / Empty）🧩

## 3) `Spinner`（読み込み中⏳）

```tsx
// src/components/Spinner.tsx
export function Spinner({ label = "読み込み中…" }: { label?: string }) {
  return (
    <div className="flex items-center gap-2 text-sm text-zinc-600">
      <div className="h-4 w-4 animate-spin rounded-full border-2 border-zinc-300 border-t-transparent" />
      <span>{label}</span>
    </div>
  );
}
```

## 4) `ErrorPanel`（失敗😵＋リトライ🔁）

```tsx
// src/components/ErrorPanel.tsx
export function ErrorPanel({
  title = "失敗しちゃった…🙏",
  error,
  onRetry,
}: {
  title?: string;
  error: Error;
  onRetry?: () => void;
}) {
  return (
    <div className="rounded-xl border border-red-200 bg-red-50 p-4">
      <p className="font-semibold text-red-800">{title}</p>
      <p className="mt-1 break-words text-sm text-red-700">{error.message}</p>

      {onRetry && (
        <button
          onClick={onRetry}
          className="mt-3 rounded-lg bg-red-600 px-3 py-2 text-sm font-semibold text-white hover:opacity-90 disabled:opacity-50"
        >
          もう一回やる🔁
        </button>
      )}
    </div>
  );
}
```

## 5) `EmptyState`（0件🙂）

```tsx
// src/components/EmptyState.tsx
export function EmptyState({
  message = "0件です🙂",
  hint = "条件を変えるか、追加してみてね✨",
}: {
  message?: string;
  hint?: string;
}) {
  return (
    <div className="rounded-xl border border-zinc-200 bg-white p-6 text-center">
      <p className="text-base font-semibold">{message}</p>
      <p className="mt-2 text-sm text-zinc-600">{hint}</p>
    </div>
  );
}
```

---

## 手を動かす🛠️：デモページで4状態を全部出す（超重要）🎮✨

「Users一覧ページ」みたいな画面で、**わざと成功/0件/失敗を切り替えて**学びます🙂

```tsx
// src/pages/UsersPage.tsx
import { useEffect, useMemo, useState } from "react";
import { useAsync } from "../hooks/useAsync";
import { Spinner } from "../components/Spinner";
import { ErrorPanel } from "../components/ErrorPanel";
import { EmptyState } from "../components/EmptyState";

type UserRow = {
  id: string;
  name: string;
  role: "admin" | "member";
  updatedAt: string;
};

export function UsersPage() {
  const [mode, setMode] = useState<"ok" | "empty" | "error">("ok");
  const { state, run } = useAsync<UserRow[]>();

  const fetchUsers = useMemo(() => {
    return async () => {
      await new Promise((r) => setTimeout(r, 700)); // 擬似通信📡

      if (mode === "error") throw new Error("通信に失敗しました（デモ）📵");
      if (mode === "empty") return [];

      return [
        { id: "u1", name: "Alice", role: "admin", updatedAt: "2026-02-16" },
        { id: "u2", name: "Bob", role: "member", updatedAt: "2026-02-16" },
      ];
    };
  }, [mode]);

  useEffect(() => {
    run(fetchUsers);
  }, [run, fetchUsers]);

  // ① 初回ロード（dataがまだ無い loading）
  if (state.status === "loading" && !state.data) {
    return <Spinner label="ユーザー一覧を読み込み中…" />;
  }

  // ② 初回でコケた（dataが無い error）
  if (state.status === "error" && !state.data) {
    return <ErrorPanel error={state.error} onRetry={() => run(fetchUsers)} />;
  }

  // ③ dataがある（success か、更新中/エラーでも前dataが残ってる）
  const users =
    state.status === "success" ? state.data : state.data ?? [];

  return (
    <div className="space-y-4">
      {/* デモ用：状態切替ボタン */}
      <div className="flex flex-wrap gap-2">
        <button
          className="rounded-lg border px-3 py-2 text-sm hover:bg-zinc-50"
          onClick={() => setMode("ok")}
        >
          成功🎉
        </button>
        <button
          className="rounded-lg border px-3 py-2 text-sm hover:bg-zinc-50"
          onClick={() => setMode("empty")}
        >
          0件🙂
        </button>
        <button
          className="rounded-lg border px-3 py-2 text-sm hover:bg-zinc-50"
          onClick={() => setMode("error")}
        >
          失敗💥
        </button>
      </div>

      {/* ④ 更新中は “画面は維持” しつつ小さく表示 */}
      {state.status === "loading" && users.length > 0 && (
        <Spinner label="更新中…" />
      )}

      {/* ⑤ dataありでも error のときは “上に注意” を出す（沈黙しない） */}
      {state.status === "error" && users.length > 0 && (
        <ErrorPanel
          title="更新に失敗…（表示は前のまま）😵"
          error={state.error}
          onRetry={() => run(fetchUsers)}
        />
      )}

      {/* ⑥ empty */}
      {users.length === 0 ? (
        <EmptyState message="ユーザーがいません🙂" hint="まずは追加してみよう✨" />
      ) : (
        <div className="rounded-xl border bg-white p-4">
          <p className="mb-3 text-sm font-semibold">ユーザー一覧📋</p>
          <ul className="space-y-2">
            {users.map((u) => (
              <li key={u.id} className="flex items-center justify-between">
                <span className="font-medium">{u.name}</span>
                <span className="text-xs text-zinc-600">
                  {u.role} / {u.updatedAt}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
```

ここまでできたら、**Firestore接続（第12章〜）がめちゃ楽**になります🗃️✨

---

## 追加で強くなる📌：保存ボタンの “pending” をReact 19で気持ちよくする🧠✨

「保存」みたいな操作は、`useTransition` で **ボタンdisabled + pending表示**がきれいに作れます🔁
React 19では、**Transitionの中でasyncを扱う**方向が強化されています ([react.dev][2])

```tsx
import { useState, useTransition } from "react";
import { ErrorPanel } from "../components/ErrorPanel";

async function saveProfile(): Promise<void> {
  await new Promise((r) => setTimeout(r, 800));
  // throw new Error("保存に失敗しました😵"); // デモ用
}

export function SaveButtonDemo() {
  const [isPending, startTransition] = useTransition();
  const [err, setErr] = useState<Error | null>(null);

  const onSave = () => {
    setErr(null);
    startTransition(async () => {
      try {
        await saveProfile();
      } catch (e) {
        setErr(e instanceof Error ? e : new Error(String(e)));
      }
    });
  };

  return (
    <div className="space-y-3">
      <button
        onClick={onSave}
        disabled={isPending}
        className="rounded-lg bg-zinc-900 px-4 py-2 text-sm font-semibold text-white disabled:opacity-50"
      >
        {isPending ? "保存中…" : "保存する💾"}
      </button>

      {err && <ErrorPanel error={err} onRetry={onSave} />}
    </div>
  );
}
```

---

## AIも同じ3点セットで扱う🤖✨（エラー文を“人間語”にする）

AI呼び出しって、やることは結局これです👇
**loading（生成中） / error（生成失敗） / data（生成結果）** ✅

FirebaseのAI機能は **Web向けSDK**もあり、`firebase/ai` から `getAI` → `getGenerativeModel` → `generateContent` の流れで呼べます ([Firebase][3])
また、**キーをアプリに埋め込まない**ための仕組みや **App Check推奨**なども整理されています ([Firebase][4])

## 例：エラーをAIで“やさしく説明”ボタン（オプション）🧑‍🏫✨

```ts
// src/lib/aiModel.ts
import { initializeApp } from "firebase/app";
import { getAI, getGenerativeModel, GoogleAIBackend } from "firebase/ai";

const firebaseConfig = {
  // ...
};

const app = initializeApp(firebaseConfig);
const ai = getAI(app, { backend: new GoogleAIBackend() });

// 迷ったらまずは軽いモデルから✨（例）
export const model = getGenerativeModel(ai, { model: "gemini-2.5-flash" });
```

※モデルには入れ替わりがあるので、古いモデル指定でエラーになっても「沈黙しない」設計が大事です⚠️（例：一部モデルのretire告知）([Firebase][3])

```tsx
// src/components/AiExplainErrorButton.tsx
import { useAsync } from "../hooks/useAsync";
import { model } from "../lib/aiModel";
import { Spinner } from "./Spinner";
import { ErrorPanel } from "./ErrorPanel";

export function AiExplainErrorButton({ message }: { message: string }) {
  const { state, run } = useAsync<string>();

  const onClick = async () => {
    await run(async () => {
      const prompt =
        `次のエラーメッセージを、初心者にわかる日本語で短く説明して。` +
        `\n\nエラー:\n${message}\n\n出力は1〜2文。`;
      const result = await model.generateContent(prompt);
      return result.response.text();
    });
  };

  return (
    <div className="space-y-2">
      <button
        onClick={onClick}
        className="rounded-lg border px-3 py-2 text-sm hover:bg-zinc-50"
      >
        AIでわかりやすくする🤖
      </button>

      {state.status === "loading" && <Spinner label="AIが説明を作成中…" />}
      {state.status === "error" && (
        <ErrorPanel title="AIの説明生成に失敗😵" error={state.error} />
      )}
      {state.status === "success" && (
        <div className="rounded-xl border bg-white p-3 text-sm">
          {state.data}
        </div>
      )}
    </div>
  );
}
```

さらに、Webでは **Chromeデスクトップ向けにオンデバイス推論とクラウドのハイブリッド**も触れられるので、失敗時や待ち時間の設計がより大事になります🧠✨ ([Firebase][4])

---

## Antigravity / Gemini CLIで、この章を“爆速で固める”🚀🛠️

* Antigravityは **エージェントをまとめて動かす Mission Control** みたいな開発体験が中心です ([Google Codelabs][5])
* Gemini CLIは **ターミナル上のオープンソースAIエージェント**で、ReActループやMCP連携にも触れられます ([Google Cloud Documentation][6])
  codelabもあります ([Google Codelabs][7])

## 今日のおすすめ指示（そのまま投げてOK）💬✨

* 「`useAsync` をテストしやすい形にして（副作用分離）🧪」
* 「UsersPageの状態分岐を読みやすくリファクタして（早期return整理）🧹」
* 「“前のdataを残す更新中表示”のUIをもっと良くして（スケルトン等）🦴」

---

## 余力：TanStack Query（React Query）を使うなら👀✨

将来「Firestore + キャッシュ + 再取得」を強くしたくなったら選択肢になります。
v5では **loading→pending** などの名称変更があるので、そこだけ注意です🧠 ([tanstack.com][8])
Suspense連携もあります ([tanstack.com][9])

---

## ミニ課題🎯（5〜10分）

1. UsersPageに **「更新」ボタン**を追加して、押したら再取得🔁
2. `loading` 中はボタンを無効化🧊
3. `error` のときは **リトライ**で復帰できるようにする🔁✨
4. `empty` のときは「0件です🙂」が必ず出るようにする

---

## チェック✅（ここまでできたら合格🎉）

* [ ] 初回ロードで **必ず** Spinner が出る⏳
* [ ] 失敗時に **必ず** ErrorPanel が出る😵
* [ ] 0件時に **必ず** EmptyState が出る🙂
* [ ] 更新中は **前の表示を保ったまま** “更新中…” が出る✨
* [ ] リトライで復帰できる🔁

---

## よくあるつまづきポイント🧯

* **失敗したのに画面が無言** → `catch` で state を `error` にしてない😵
* **リトライしても直らない** → `error` を消してない / 同じ関数を呼んでない🔁
* **古いリクエストが勝って表示が戻る** → 競合（race）対策がない（この章の `runId` が効く）🧠
* **リアルタイム購読で放置** → `onSnapshot` は unsubscribe を `useEffect` のreturnで返す（＋errorコールバックで沈黙防止）📡 ([Firebase][1])

---

次の第8章は「フォーム入力とバリデーション」なので、今作った **loading/errorの型**がそのまま効きます📝✨
（入力→保存→保存中→失敗→復帰、が超きれいに作れるようになります🎉）

[1]: https://firebase.google.com/docs/firestore/query-data/listen?utm_source=chatgpt.com "Get realtime updates with Cloud Firestore - Firebase - Google"
[2]: https://react.dev/blog/2024/12/05/react-19?utm_source=chatgpt.com "React v19"
[3]: https://firebase.google.com/docs/ai-logic/get-started "Get started with the Gemini API using the Firebase AI Logic SDKs  |  Firebase AI Logic"
[4]: https://firebase.google.com/docs/ai-logic "Gemini API using Firebase AI Logic  |  Firebase AI Logic"
[5]: https://codelabs.developers.google.com/getting-started-google-antigravity?utm_source=chatgpt.com "Getting Started with Google Antigravity"
[6]: https://docs.cloud.google.com/gemini/docs/codeassist/gemini-cli?utm_source=chatgpt.com "Gemini CLI | Gemini for Google Cloud"
[7]: https://codelabs.developers.google.com/gemini-cli-hands-on?utm_source=chatgpt.com "Hands-on with Gemini CLI"
[8]: https://tanstack.com/query/v5/docs/react/guides/migrating-to-v5?utm_source=chatgpt.com "Migrating to TanStack Query v5"
[9]: https://tanstack.com/query/v5/docs/react/guides/suspense?utm_source=chatgpt.com "Suspense | TanStack Query React Docs"
