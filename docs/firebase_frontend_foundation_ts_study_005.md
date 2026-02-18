# 第05章：管理画面レイアウトの基本 🧱📊

この章で作るのは「どのページでも共通で使う“枠”」です🧩✨
サイドバー＋ヘッダー＋メイン領域が固定されて、ページ中身だけが切り替わる“管理画面の型”を作ります😆

> ちなみに今の最新版は、React **19.2.4**、React Router **7.13.0**、Node **v24 (Active LTS)**、Tailwind **v4.1系**あたりが「2026年の安定ど真ん中」です🧠✨ ([NPM][1])

---

## 5-0 まず「レイアウトの勝ち筋」3つだけ覚える 🏆

1. **枠を先に固定**（サイドバー幅・ヘッダー高さ・余白）📐
2. **スクロールする場所は1つだけ**（メインだけスクロール）🌀
3. **中身（ページ）は Outlet で差し替え**（枠は同じ）🔁

ここまでできると、Firestore一覧もフォームもAIボタンも「枠に乗せるだけ」になります🚀
（Firebase AI Logic のUIボタンも、この枠に自然に置けます🤖✨） ([Firebase][2])

---

## 5-1 手を動かす：AppShell（枠）を作る 🛠️🧱

## ① フォルダを作る（Windows）📁

```powershell
mkdir src\layouts
mkdir src\components\layout
```

## ② AppShell を作る（枠の本体）🧱

`src/layouts/AppShell.tsx`

```tsx
import { useState } from "react";
import { Outlet } from "react-router-dom";
import { Sidebar } from "../components/layout/Sidebar";
import { Topbar } from "../components/layout/Topbar";

export function AppShell() {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <div className="h-screen bg-zinc-50 text-zinc-900">
      {/* アクセシビリティ：キーボードで本文に飛べるやつ */}
      <a
        href="#main"
        className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-50 rounded bg-white px-3 py-2 shadow"
      >
        本文へスキップ
      </a>

      <div className="flex h-full">
        {/* Sidebar（PC） */}
        <div className="hidden md:block w-64 shrink-0 border-r bg-white">
          <Sidebar onNavigate={() => {}} />
        </div>

        {/* Sidebar（スマホ：オーバーレイ） */}
        {mobileOpen && (
          <div className="fixed inset-0 z-40 md:hidden">
            <button
              className="absolute inset-0 bg-black/30"
              aria-label="閉じる"
              onClick={() => setMobileOpen(false)}
            />
            <div className="relative z-50 h-full w-64 bg-white shadow-lg">
              <Sidebar onNavigate={() => setMobileOpen(false)} />
            </div>
          </div>
        )}

        {/* 右側：ヘッダー＋メイン */}
        <div className="flex min-w-0 flex-1 flex-col">
          <Topbar onOpenMenu={() => setMobileOpen(true)} />

          {/* ここだけスクロールさせるのがコツ */}
          <main id="main" className="min-w-0 flex-1 overflow-y-auto p-4">
            <Outlet />
          </main>
        </div>
      </div>
    </div>
  );
}
```

**ポイント**👇😺

* `h-screen` で“画面全体”を固定✨
* `main` にだけ `overflow-y-auto` → スクロールが迷子にならない🌀
* `Outlet` が「ページ差し替え口」🔁

---

## 5-2 手を動かす：Sidebar を作る 🧭📚

`src/components/layout/Sidebar.tsx`

```tsx
import { NavLink } from "react-router-dom";

const items = [
  { to: "/dashboard", label: "Dashboard" },
  { to: "/users", label: "Users" },
  { to: "/settings", label: "Settings" },
] as const;

type Props = {
  onNavigate: () => void;
};

export function Sidebar({ onNavigate }: Props) {
  return (
    <aside className="h-full p-3">
      <div className="px-2 py-3 text-lg font-semibold">My Admin</div>

      <nav className="mt-2 space-y-1">
        {items.map((it) => (
          <NavLink
            key={it.to}
            to={it.to}
            onClick={onNavigate}
            className={({ isActive }) =>
              [
                "block rounded px-3 py-2 text-sm",
                isActive
                  ? "bg-zinc-900 text-white"
                  : "text-zinc-700 hover:bg-zinc-100 hover:text-zinc-900",
              ].join(" ")
            }
            end
          >
            {it.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
```

**ここが管理画面っぽくなるツボ**😆✨

* `NavLink` の `isActive` で「今どこ？」が一発で分かる🚩
* `w-64`（=16rem）くらいが“それっぽい”📐

> React Router の最新版（7.13.0）系でOKです🧭✨ ([NPM][3])

---

## 5-3 手を動かす：Topbar（上部バー）を作る 🧢✨

`src/components/layout/Topbar.tsx`

```tsx
type Props = {
  onOpenMenu: () => void;
};

export function Topbar({ onOpenMenu }: Props) {
  return (
    <header className="sticky top-0 z-30 border-b bg-white/80 backdrop-blur">
      <div className="flex h-14 items-center gap-2 px-4">
        <button
          type="button"
          className="md:hidden rounded px-2 py-1 hover:bg-zinc-100"
          onClick={onOpenMenu}
          aria-label="メニューを開く"
        >
          ☰
        </button>

        <div className="font-semibold">管理画面</div>

        <div className="ml-auto flex items-center gap-2">
          {/* ここが“拡張ポイント”🌱：後でログアウトやAI機能を置く */}
          <button className="rounded border px-3 py-1 text-sm hover:bg-zinc-50">
            🤖 AI
          </button>
          <div className="h-8 w-8 rounded-full bg-zinc-200" aria-label="ユーザー" />
        </div>
      </div>
    </header>
  );
}
```

**sticky + blur** で「上に張り付く管理画面感」が出ます🧊✨
ここに後で👇を“足すだけ”で強くなります🔥

* ログアウト🔐
* Firestoreの検索フォーム🔎
* 文章整形・要約の **Firebase AI Logic** ボタン🤖✨ ([Firebase][2])

---

## 5-4 ルーティング側を「枠＋中身」にする 🔁🧭

第4章で Router を作っている前提で、**AppShell を親にして children にページ**を入れます。

例：`src/router.tsx`（名前は何でもOK）

```tsx
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import { AppShell } from "./layouts/AppShell";
import { DashboardPage } from "./pages/DashboardPage";
import { UsersPage } from "./pages/UsersPage";
import { SettingsPage } from "./pages/SettingsPage";

const router = createBrowserRouter([
  {
    element: <AppShell />,
    children: [
      { path: "/", element: <DashboardPage /> },
      { path: "/dashboard", element: <DashboardPage /> },
      { path: "/users", element: <UsersPage /> },
      { path: "/settings", element: <SettingsPage /> },
    ],
  },
]);

export function AppRouter() {
  return <RouterProvider router={router} />;
}
```

> React Router v7 ではパッケージ整理の話もありますが、Webアプリならまずは `react-router-dom` でOKです🧭✨ ([reactrouter.com][4])

---

## 5-5 ミニ課題 🎯✨（10〜15分）

## お題：サイドバーに「メニュー3つ＋1つだけNEWバッジ」🏷️

* `Settings` の右に `NEW` を出してみよう😆
* ついでに `Topbar` の右側に「通知🔔」っぽい丸を足してみよう

ヒント👇

* `inline-flex items-center gap-2`
* `text-xs rounded-full px-2 py-0.5 bg-zinc-900 text-white`

---

## 5-6 チェック ✅✅✅

* [ ] **どのページでも** サイドバーとヘッダーが同じ見た目？🧱
* [ ] スクロールは **メインだけ** になってる？🌀
* [ ] `NavLink` で “今いる場所” が一瞬で分かる？🚩
* [ ] 画面幅を狭くしたら、メニューが ☰ で開ける？📱

---

## 5-7 つまずきポイント集 🧯😵‍💫

## 🧨「メインがスクロールしない」

だいたい **高さが固定されてない** か、**スクロールが body 側に行ってる** パターンです。
✅ `AppShell` の外側が `h-screen`、`main` が `flex-1 overflow-y-auto` になってるか確認👍

## 🧨「横幅がはみ出す（横スクロールが出る）」

✅ `min-w-0` を “右側の列” と `main` に入れると直ることが多いです📏✨
（この章のコードはそれを入れてます😺）

## 🧨「リロードで404（Hosting時）」

これはデプロイ章で直しますが、SPAは設定が必要なことがあります🌍🛠️
（Hosting / App Hosting どちらでも回避策があります） ([Firebase][5])

---

## 5-8 AIでレイアウト作りを爆速にする 🤖🛸

## ✅ Antigravity の「ミッション」例（そのまま貼れる）🧠

Antigravity は “エージェント前提” の開発プラットフォームで、計画→実装→検証まで回せる思想です🛰️ ([Google Codelabs][6])
ミッション例👇（やってほしいことを箇条書きにするのがコツ！）

* AppShell を作る（サイドバー＋トップバー＋Outlet）
* スマホは ☰ でサイドバー開閉
* main だけスクロール
* NavLink の active 表示

## ✅ Gemini CLI に「レビュー係」をやらせる 🧑‍⚖️🤖

Gemini CLI はターミナルから使えるオープンソースAIエージェントで、調査やコード改善も得意です🧰✨ ([Google Cloud Documentation][7])
おすすめの頼み方👇

* 「アクセシビリティ観点で直すところある？」
* 「Tailwindクラス長いから読みやすく整理して」
* 「`overflow` 周りのバグ起きそう？」

（AIが出した差分は、必ず目で見てから取り込むのが正解です👀✅）

---

## 5-9 次章へのつながり 🔗✨

この“枠”ができたので、次は **コンポーネント分割ルール** を決めて、UIを増やしても破綻しない構造にします📦😆
第6章で「components/pages/hooks/services」の型を固めると、Firestore一覧もフォームもAI機能もスルッと入りますよ〜🔥

[1]: https://www.npmjs.com/package/react?utm_source=chatgpt.com "react"
[2]: https://firebase.google.com/docs/ai-logic?utm_source=chatgpt.com "Gemini API using Firebase AI Logic - Google"
[3]: https://www.npmjs.com/package/react-router-dom?utm_source=chatgpt.com "react-router-dom"
[4]: https://reactrouter.com/upgrading/v6?utm_source=chatgpt.com "Upgrading from v6"
[5]: https://firebase.google.com/docs/app-hosting?utm_source=chatgpt.com "Firebase App Hosting"
[6]: https://codelabs.developers.google.com/getting-started-google-antigravity "Getting Started with Google Antigravity  |  Google Codelabs"
[7]: https://docs.cloud.google.com/gemini/docs/codeassist/gemini-cli "Gemini CLI  |  Gemini for Google Cloud  |  Google Cloud Documentation"
