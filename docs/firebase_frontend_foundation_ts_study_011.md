# 第11章：認証状態で画面を切り替える 🔐🚧（ログイン監視 → ガード → ログアウト）

この章は「**ログインしてる人だけ管理画面を見れる**」を、React側で“ちゃんと気持ちよく”作る回です😆✨
（リロードしてもログインが保たれて、未ログインなら `/login` に飛ぶやつ！）

※バージョン感の確認：Reactの最新は `19.2.4`（npm上でLatest）です🧠✨ ([npm][1])
Nodeは `v24` が Active LTS（2026-02-09更新）になっています🟢 ([nodejs.org][2])

---

## この章でできるようになること 🎯✨

* ログイン状態を **アプリ全体で監視**できる（`onAuthStateChanged`）👀 ([Firebase][3])
* 認証の初期化が終わるまで **チラつかない**（`ready` フラグ）🌀
* 未ログインなら **自動で `/login` に飛ばす**（ルートガード）🚧
* ヘッダーに **ログアウトボタン**を付ける🚪
* 「ログイン保持」の仕組み（永続/タブのみ/メモリ）を理解して選べる🧠 ([Firebase][4])

---

## まず超重要：認証は“最初の数瞬”だけ不確定 😵‍💫

Firebase Authは、ページ読み込み直後に `currentUser` がすぐ取れない瞬間があります。
だから「**最初に1回、Authの状態確定イベントを待つ**」のが正解です✅

そのために使うのが **`onAuthStateChanged`**。ログイン/ログアウト/初期化完了のタイミングで呼ばれます📣 ([Firebase][3])

---

## ハンズオン：実装の全体像 🧩✨

やることはシンプルに3つだけ👇

1. `AuthProvider`：ログイン状態を監視して、全コンポーネントに配る📦
2. `ProtectedRoute`：未ログインなら `/login` に送る🚧
3. `Header`：ログアウトボタンを置く🚪

（第10章で作った `firebase.ts` から `auth` を import できる前提で進めます🔌🔥）

---

## Step 1：AuthProvider を作る（“配給所”）📦👑

📁 `src/auth/AuthProvider.tsx`

```tsx
import React, { createContext, useContext, useEffect, useMemo, useState } from "react";
import type { User } from "firebase/auth";
import { onAuthStateChanged } from "firebase/auth";
import { auth } from "../firebase"; // 第10章の firebase.ts から auth を export してる想定

type AuthState = {
  user: User | null;
  ready: boolean;          // ★これが超大事：初期化完了した？
  isAuthed: boolean;
};

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    // 認証状態を監視：最初の1回も必ず呼ばれる
    const unsubscribe = onAuthStateChanged(auth, (u) => {
      setUser(u ?? null);
      setReady(true);
    });
    return unsubscribe;
  }, []);

  const value = useMemo<AuthState>(() => {
    return { user, ready, isAuthed: !!user };
  }, [user, ready]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
```

ポイントはここ👇😆

* `ready === false` の間は「ログインしてない」と決めつけない！🛑
* `onAuthStateChanged` が **初期化完了の合図**になる📣 ([Firebase][3])

---

## Step 2：ルートガード（ProtectedRoute）を作る 🚧🛡️

📁 `src/routes/ProtectedRoute.tsx`

```tsx
import React from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../auth/AuthProvider";

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { ready, isAuthed } = useAuth();
  const location = useLocation();

  // ① 認証の初期化待ち：ここでスピナー等を出す（チラつき防止）
  if (!ready) {
    return (
      <div className="p-6">
        <div className="animate-pulse">読み込み中…⏳</div>
      </div>
    );
  }

  // ② 未ログインなら /login へ（元いた場所は state に保存）
  if (!isAuthed) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  // ③ OKなら表示
  return <>{children}</>;
}
```

ここで「**ready を待ってから** login 判定する」のが勝ち筋です🏆✨
これが無いと、リロード直後に一瞬 `/login` に飛ぶ “チラつき” が出がちです😵‍💫

---

## Step 3：ルーティングにガードを組み込む 🧭✨

例：`/dashboard` を守る（React Router v7でも基本は同じノリでOK🙆‍♂️）

📁 `src/main.tsx`（ざっくり例）

```tsx
import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./auth/AuthProvider";
import { ProtectedRoute } from "./routes/ProtectedRoute";

import { LoginPage } from "./pages/LoginPage";
import { DashboardPage } from "./pages/DashboardPage";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            }
          />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  </React.StrictMode>
);
```

---

## Step 4：LoginPage を作る（ログイン後に元のページへ戻す）🔐↩️

ここは“最低限の形”でOKです🙂✨
Firebaseのメール/パスワードログインは `signInWithEmailAndPassword` でできます📌 ([Firebase][3])

📁 `src/pages/LoginPage.tsx`

```tsx
import React, { useState } from "react";
import { signInWithEmailAndPassword, setPersistence, browserLocalPersistence, browserSessionPersistence } from "firebase/auth";
import { useLocation, useNavigate } from "react-router-dom";
import { auth } from "../firebase";

type LocationState = { from?: { pathname?: string } };

export function LoginPage() {
  const nav = useNavigate();
  const location = useLocation();
  const from = (location.state as LocationState | null)?.from?.pathname ?? "/dashboard";

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [remember, setRemember] = useState(true); // ✅「ログイン保持」っぽい
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // remember=true: ブラウザ再起動後も保持（local）
      // remember=false: タブを閉じたら消える（session）
      await setPersistence(auth, remember ? browserLocalPersistence : browserSessionPersistence);
      // Webのデフォルトは local（必要なら上で上書き） :contentReference[oaicite:7]{index=7}

      await signInWithEmailAndPassword(auth, email, password); // :contentReference[oaicite:8]{index=8}
      nav(from, { replace: true });
    } catch (e: any) {
      setError(e?.code ?? "ログインに失敗しました😢");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen grid place-items-center p-6">
      <form onSubmit={onSubmit} className="w-full max-w-sm space-y-4 rounded-xl border p-6">
        <h1 className="text-xl font-bold">ログイン 🔐</h1>

        <label className="block space-y-1">
          <div className="text-sm">メール</div>
          <input className="w-full rounded border p-2" value={email} onChange={(e) => setEmail(e.target.value)} />
        </label>

        <label className="block space-y-1">
          <div className="text-sm">パスワード</div>
          <input className="w-full rounded border p-2" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
        </label>

        <label className="flex items-center gap-2 text-sm">
          <input type="checkbox" checked={remember} onChange={(e) => setRemember(e.target.checked)} />
          ログイン状態を保持する（おすすめ）✨
        </label>

        {error && <div className="text-sm text-red-600">エラー：{error}</div>}

        <button disabled={loading} className="w-full rounded bg-black px-3 py-2 text-white disabled:opacity-50">
          {loading ? "ログイン中…⏳" : "ログイン"}
        </button>
      </form>
    </div>
  );
}
```

## 「保持（Persistence）」の超ざっくり 🧠

* `local`：ブラウザ閉じても残る（共有PCだと危険な場合あり⚠️）
* `session`：そのタブ/ウィンドウだけ（閉じたら消える）
* `none`：リロードでも消える（ほぼデバッグ用）
  これらは公式で整理されています📌 ([Firebase][4])

---

## Step 5：ヘッダーにログアウトボタンを付ける 🚪✨

📁 `src/components/AppHeader.tsx`

```tsx
import React from "react";
import { signOut } from "firebase/auth";
import { auth } from "../firebase";
import { useAuth } from "../auth/AuthProvider";

export function AppHeader() {
  const { user } = useAuth();

  return (
    <header className="flex items-center justify-between border-b p-3">
      <div className="font-bold">管理画面 📊</div>

      <div className="flex items-center gap-3">
        <div className="text-sm opacity-80">{user?.email ?? "ゲスト"}</div>

        <button
          className="rounded border px-3 py-1"
          onClick={() => signOut(auth)} // signOut は公式APIにあります :contentReference[oaicite:10]{index=10}
        >
          ログアウト 🚪
        </button>
      </div>
    </header>
  );
}
```

---

## ✅ 動作チェック（ここまでで完成）🎉

* `/dashboard` を直打ち → 未ログインなら `/login` に行く？🚧
* ログイン成功 → `/dashboard` に戻る？↩️
* リロード → ログインが保持される？（remember=true のとき）🔄
* ログアウト → すぐ `/login` に戻る？🚪

---

## ちょい上級：React Router v7 の loader / middleware で“入口で弾く” 🧠🚧

「画面が表示されてから弾く」より、**最初から弾く**ほうがキレイなこともあります✨
React Router v7 には `redirect()` があり、loader内で `throw redirect("/login")` できます📌 ([api.reactrouter.com][5])

さらに middleware で認証チェックの例も載っています🛡️ ([reactrouter.com][6])

> ただし、Firebase Auth は初期化待ちが絡むので、SPAだと「Auth ready を待つ」仕組み（Promise化）が必要になります。
> ここは“やりたくなったら”でOK🙆‍♂️（今は ProtectedRoute 方式で十分強いです💪）

---

## AIも絡める（軽くでOK！）🤖✨

## 1) UI実装を一気に作る（Antigravity / Gemini CLI）🛸💻

* Antigravityは「エージェントが計画→実装→検証」まで進めるIDE系の仕組みとして整理されています📌 ([Google Codelabs][7])
* 例えば、こう依頼すると速いです👇

  * 「AuthProvider / ProtectedRoute / LoginPage を作って。readyフラグでチラつき防止も入れて」
  * 出力された差分をレビューして採用✅

Gemini CLI は “コード生成→差分確認→適用” の流れで使える公式ドキュメントがあります📌 ([Firebase][8])

## 2) Firebase AI Logic を“ログイン後の機能”に繋げる🤖🔌

この章のゴールは認証UIだけど、次の章（Firestore等）へ繋げるために、
「ログイン後の画面でAIボタンを使える状態にする」導線はここで作れます✨

Firebase AI Logic は「アプリから直接 Gemini/Imagen を呼ぶ」入り口のガイドがあります📌 ([Firebase][9])
（※やるなら **ログイン後画面にだけAI UIを出す** のが自然で安全です🔐✨）

---

## よくある詰まりポイント集 😵‍💫🧯

* **リロード直後に一瞬ログアウト扱いになる**
  → `ready` が無いのが原因！`ready=false` の間はスピナーにする✅

* **別タブでもログイン状態が共有される/されない**
  → `local` は同一オリジンでタブ同期されます（挙動も公式に説明あり）🧠 ([Firebase][4])
  → `session` は基本タブ単位になるので「共有したくない」用途に便利✨

* **エラーコードが英語でつらい**
  → まずは `error.code` を画面に出して原因特定→後で辞書化でOK🙂
  → AIで文言整形もできるけど、最初は辞書で十分👍

---

## ミニ課題 🎯🔥

1. `/settings` も ProtectedRoute で保護してみよう🔐
2. ログイン画面に「ログイン後は元のページに戻る」ことを表示しよう↩️
3. remember をOFFにして、タブを閉じたらログアウトになるのを確認しよう🧪

---

## まとめ 🏁✨（この章で“背骨”が完成！）

* `onAuthStateChanged` で「Authの確定」を待つのが基本📣 ([Firebase][3])
* `ready` を持つと **チラつきが消える**✨
* `ProtectedRoute` で管理画面を守れる🚧
* `setPersistence` で「保持する/しない」をユーザーに選ばせられる🧠 ([Firebase][4])

次（第12章）で Firestore の一覧をテーブルに出すとき、**“ログインしてる人だけデータを見る”**が自然に繋がりますよ😆🗃️✨

[1]: https://www.npmjs.com/package/react?utm_source=chatgpt.com "react"
[2]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
[3]: https://firebase.google.com/docs/auth/web/start "Get Started with Firebase Authentication on Websites"
[4]: https://firebase.google.com/docs/auth/web/auth-state-persistence "Authentication State Persistence  |  Firebase"
[5]: https://api.reactrouter.com/v7/variables/react-router.redirect.html "redirect | React Router API Reference"
[6]: https://reactrouter.com/how-to/middleware "Middleware  | React Router"
[7]: https://codelabs.developers.google.com/getting-started-google-antigravity?utm_source=chatgpt.com "Getting Started with Google Antigravity"
[8]: https://firebase.google.com/docs/auth/web/manage-users?utm_source=chatgpt.com "Manage Users in Firebase - Google"
[9]: https://firebase.google.com/docs/ai-logic/get-started?utm_source=chatgpt.com "Get started with the Gemini API using the Firebase AI Logic ..."
