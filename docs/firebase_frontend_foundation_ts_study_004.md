# 第04章：ルーティングでページ分割する 🧭✨（React Routerで「URL＝画面」を作る）

この章では、管理画面アプリを **「/dashboard」「/users」「/settings」** に分割して、**URL直打ち＆リロードでも崩れない** “ページ遷移の土台” を作ります🚀
（2026-02-16時点の最新ルート設計として、React Router **v7系（latest 7.13.0）** 前提で進めます）([reactrouter.com][1])

---

## 1) まずは超ざっくり理解 🧠💡

## SPAの「ルーティング」って何？🤔

ReactのSPAは基本 **1枚のHTML（index.html）** で動きます。
でもユーザーから見ると「ページがある」ようにしたいので…

* **URL（/users など）を見て**
* **表示するコンポーネント（画面）を切り替える**

これがルーティングです🧭✨
つまり **URL＝アプリの状態** です（どの画面を見てるか、どのユーザーを開いてるか、など）📌

---

## 2) 今日の推奨：React Router v7 の入れ方 🧰✨

React Router v7 のドキュメントでは、インストールは **`react-router`** を入れる形が基本になっています。([reactrouter.com][1])

PowerShell（またはターミナル）で👇

```bash
npm i react-router
```

> 以前の情報で `react-router-dom` を見かけることもあるけど、v7の公式ガイドは `react-router` を中心に書かれています🧭([reactrouter.com][1])

---

## 3) ハンズオン：3ページ（+404）を作る 🛠️🎉

## ゴール 🎯

* `/dashboard` `/users` `/settings` に行ける
* URL直打ちでも表示される
* 変なURLは 404 ページが出る

---

## Step A：ページ（画面）コンポーネントを作る 📄✨

`src/pages/` を作って、まずは“文字だけページ”を作ります🙂

**`src/pages/DashboardPage.tsx`**

```tsx
export function DashboardPage() {
  return (
    <div className="space-y-2">
      <h1 className="text-2xl font-bold">Dashboard 📊</h1>
      <p className="text-slate-700">ここが管理画面のトップだよ！</p>
    </div>
  );
}
```

**`src/pages/UsersPage.tsx`**

```tsx
import { Link } from "react-router";

const demoUsers = [
  { id: "u001", name: "Aさん" },
  { id: "u002", name: "Bさん" },
  { id: "u003", name: "Cさん" },
] as const;

export function UsersPage() {
  return (
    <div className="space-y-3">
      <h1 className="text-2xl font-bold">Users 👥</h1>

      <ul className="list-disc pl-5 text-slate-800">
        {demoUsers.map((u) => (
          <li key={u.id}>
            <Link className="underline" to={`/users/${u.id}`}>
              {u.name}（詳細へ）
            </Link>
          </li>
        ))}
      </ul>

      <p className="text-sm text-slate-600">
        ※ 今はダミー。後でFirestoreの一覧に置き換えるよ🗃️
      </p>
    </div>
  );
}
```

**`src/pages/SettingsPage.tsx`**

```tsx
export function SettingsPage() {
  return (
    <div className="space-y-2">
      <h1 className="text-2xl font-bold">Settings ⚙️</h1>
      <p className="text-slate-700">設定画面（後でログイン必須にする）</p>
    </div>
  );
}
```

**`src/pages/NotFoundPage.tsx`**

```tsx
import { Link } from "react-router";

export function NotFoundPage() {
  return (
    <div className="space-y-3">
      <h1 className="text-2xl font-bold">404 😵</h1>
      <p className="text-slate-700">そのページは見つからなかったよ…</p>
      <Link className="underline" to="/dashboard">
        Dashboardへ戻る
      </Link>
    </div>
  );
}
```

---

## Step B：レイアウト（共通枠）を作る 🧱✨

ここでは“ミニ版の共通枠”だけ作ります（本格レイアウトは次章でガッツリ！）💪
React Routerは **親（枠）＋子（ページ）** を **`Outlet`** で合成できます。([reactrouter.com][2])

**`src/layouts/AppShell.tsx`**

```tsx
import { NavLink, Outlet } from "react-router";

const navItems = [
  { to: "/dashboard", label: "Dashboard" },
  { to: "/users", label: "Users" },
  { to: "/settings", label: "Settings" },
] as const;

export function AppShell() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b bg-white">
        <div className="mx-auto flex max-w-5xl items-center gap-4 p-4">
          <div className="text-lg font-semibold">My Admin 🧩</div>

          <nav className="flex gap-2">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  [
                    "rounded px-3 py-1 text-sm",
                    isActive
                      ? "bg-slate-900 text-white"
                      : "text-slate-700 hover:bg-slate-100",
                  ].join(" ")
                }
              >
                {item.label}
              </NavLink>
            ))}
          </nav>
        </div>
      </header>

      <main className="mx-auto max-w-5xl p-4">
        <Outlet />
      </main>
    </div>
  );
}
```

---

## Step C：ルーター定義（URL ↔ 画面）を作る 🧭

React Router v7（Data Mode）では `createBrowserRouter` でルートをオブジェクトとして定義できます。([reactrouter.com][3])
さらに、**pathなしの親ルート**を使うと「URLを増やさずに枠だけ作る（Layout Route）」ができます。([reactrouter.com][3])

**`src/router.tsx`**

```tsx
import { createBrowserRouter } from "react-router";

import { AppShell } from "./layouts/AppShell";
import { DashboardPage } from "./pages/DashboardPage";
import { UsersPage } from "./pages/UsersPage";
import { SettingsPage } from "./pages/SettingsPage";
import { NotFoundPage } from "./pages/NotFoundPage";
import { UserDetailPage } from "./pages/UserDetailPage";

export const router = createBrowserRouter([
  {
    Component: AppShell,
    children: [
      { index: true, Component: DashboardPage },      // "/" はDashboard
      { path: "dashboard", Component: DashboardPage },// "/dashboard" もDashboard
      { path: "users", Component: UsersPage },        // "/users"
      { path: "users/:userId", Component: UserDetailPage }, // "/users/u001" みたいなやつ
      { path: "settings", Component: SettingsPage },  // "/settings"
      { path: "*", Component: NotFoundPage },         // それ以外は404
    ],
  },
]);
```

> `:userId` のような **動的セグメント**は、URLから値を取り出す王道パターンです🧩（後でFirestoreの「詳細ページ」と相性バツグン！）([reactrouter.com][3])

---

## Step D：User詳細ページ（動的ルートの練習）🧑‍💻✨

**`src/pages/UserDetailPage.tsx`**

```tsx
import { Link, useParams } from "react-router";

export function UserDetailPage() {
  const { userId } = useParams();

  return (
    <div className="space-y-3">
      <h1 className="text-2xl font-bold">User Detail 🪪</h1>
      <p className="text-slate-700">
        userId: <span className="font-mono">{userId}</span>
      </p>

      <Link className="underline" to="/users">
        Usersへ戻る
      </Link>
    </div>
  );
}
```

---

## Step E：`main.tsx` を RouterProvider に差し替える 🔁

公式のData Modeでは、`RouterProvider` を使ってルーターをアプリに渡します。([reactrouter.com][4])

**`src/main.tsx`（例）**

```tsx
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { RouterProvider } from "react-router/dom";
import { router } from "./router";
import "./index.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>
);
```

---

## 4) 動作チェック（URL直打ちミッション）✅🧪

開発サーバー起動👇

```bash
npm run dev
```

ブラウザでこれを順に試してね👇😆

* `http://localhost:5173/dashboard`
* `http://localhost:5173/users`
* `http://localhost:5173/users/u001`
* `http://localhost:5173/settings`

そして最大のチェック💥
**それぞれのページで F5（リロード）しても表示が崩れない？** ✅

---

## 5) つまづきポイント集 🧯😵‍💫

## ❌ ルートは切り替わるのに「中身が出ない」

👉 たいてい **`<Outlet />` を置き忘れ**です。
親（AppShell）が枠で、子（各ページ）が中身。子はOutletに出ます🧩([reactrouter.com][2])

## ❌ `<a href="/users">` で遷移すると画面が“全部リロード”される

👉 React Routerでは **`Link` / `NavLink`** を使うのが基本！🚀
（SPA体験が一気に“それっぽく”なるよ）

## ❌ デプロイ後に「直URL」や「リロード」で404になる（超ある）😭

これは**静的ホスティングあるある**です。
解決は「どのURLで来ても index.html を返す」設定にします。

Firebase Hostingなら、`firebase.json` に **rewrite** を入れるのが王道です👇([Firebase][5])

```json
{
  "hosting": {
    "public": "dist",
    "rewrites": [{ "source": "**", "destination": "/index.html" }]
  }
}
```

> これで `/users` 直アクセスでも、まずindex.htmlが返ってきて、そこからReact Routerが正しい画面に切り替えます🧠✨

---

## 6) AI活用（開発を爆速にするコツ）🤖⚡

## 🧩 ルーティングはAIに“設計表”を作らせると早い

例：Gemini（エージェント/CLI）にこう頼むと便利👇

* 「/dashboard /users /settings の3ページ構成の管理画面で、`createBrowserRouter` 使って最小実装して」
* 「Layout Route + Outlet で共通ヘッダー付きにして」
* 「/users/:userId の詳細も追加して」

React Routerの基本構造（Layout Route / Outlet / 動的セグメント）は公式ガイドに載ってるので、AIに参照させるとブレにくいです📚([reactrouter.com][3])

## 🛸 Firebase側もAI連携が進んでる（Gemini CLI / MCP など）

Firebaseには **Gemini CLI拡張** や **MCPサーバー** の公式ドキュメントが用意されています。([Firebase][6])
さらにプロンプト集（Prompt catalog）も公式で整備されていて、更新も新しめです（Last updated 2026-02-05）。([Firebase][7])

> この章では“ルーティング作業の補助”として使うだけでOK🙆‍♂️
> 本格的にFirebase AI（AI Logic）を繋ぐのは後半章でやるよ🤖✨

---

## 7) Firebase AI Logic と「安全にAIを呼ぶ」考え方（予告）🔐🤖

今はまだ繋がないけど、後でAIボタンを付けるときに超大事な話👇
**クライアントからAIを呼ぶ時は「キーを守る」「悪用を防ぐ」**が必須です🧯

Firebase AI Logic は、クライアントSDKからAIを呼ぶときの仕組み（プロキシ的な立ち位置）を説明しています。([Firebase][8])
ルーティングができてると、たとえば `/users/:userId` の詳細画面に **「AIでプロフィール文を整形」ボタン**みたいなのを自然に置けます😆✨

---

## 8) ミニ課題 🎯✨

## ミニ課題A（必須）✅

* `/dashboard` `/users` `/settings` を **URL直打ち**
* それぞれ **リロード**
* **404にならず表示できる**ことを確認！

## ミニ課題B（おかわり）🍚

* `/users/:userId` を追加したので
  `Users` から `u001` などへ遷移して、**URLの値が画面に出る**のを確認👀✨

---

## 9) チェックリスト ✅📌

* [ ] `createBrowserRouter` で routes を定義できた
* [ ] `AppShell` に `<Outlet />` があり、ページが表示される
* [ ] `Link / NavLink` で遷移して、画面がリロードされない
* [ ] `/users/u001` みたいな動的URLで値が取れる
* [ ] （将来）Firebase Hosting の rewrite を入れる意味がわかった

---

次の第5章では、ここで作った `AppShell` を **左サイドバー＋上部バーの“管理画面っぽい骨格”** に進化させます🧱📊✨

[1]: https://reactrouter.com/start/declarative/installation "Installation  | React Router"
[2]: https://reactrouter.com/start/declarative/routing "Routing  | React Router"
[3]: https://reactrouter.com/start/data/routing "Routing  | React Router"
[4]: https://reactrouter.com/start/data/installation "Installation  | React Router"
[5]: https://firebase.google.com/docs/hosting/full-config "Configure Hosting behavior  |  Firebase Hosting"
[6]: https://firebase.google.com/docs/ai-assistance/gcli-extension "Firebase extension for the Gemini CLI  |  Develop with AI assistance"
[7]: https://firebase.google.com/docs/ai-assistance/prompt-catalog "AI prompt catalog for Firebase  |  Develop with AI assistance"
[8]: https://firebase.google.com/docs/ai-logic "Gemini API using Firebase AI Logic  |  Firebase AI Logic"
