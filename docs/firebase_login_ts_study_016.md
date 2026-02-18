# 第16章：画面ガード：ログイン必須ページ（ルート保護）を作る🚧

この章では「URL直打ちでも守れる」ログイン必須ページを作ります🙂
**ポイントは3つ**だけ👇

* **まだログイン状態が分からない間（loading）**は待つ⏳
* **未ログイン（user=null）**ならログイン画面へ飛ばす🚪
* **ログイン済み**なら普通にページ表示✅

（React Router v7 でも、`Outlet` + `Navigate` + `useLocation` の組み合わせが超安定です）([React Router][1])

---

## 0) この章でできあがる動き（完成イメージ）🧠✨

たとえば **/mypage** を「ログイン必須」にすると…

1. 未ログインで /mypage を開く
2. ログイン画面へリダイレクト🚀（ついでに「元いたページ」を覚える）
3. ログイン成功🎉 → **元いた /mypage に戻る**🔁

---

## 1) まずは “認証の状態” を 2つ持つ（user と loading）🦴

前章までで作った **AuthProvider** がある前提でOKですが、最低限こういう形になっていれば勝ちです🙂
（ここが弱いと、ガードがチラついたり無限リダイレクトしがち💦）

**src/auth/AuthProvider.tsx**

```tsx
import { createContext, useContext, useEffect, useMemo, useState } from "react";
import type { User } from "firebase/auth";
import { onAuthStateChanged } from "firebase/auth";
import { auth } from "../firebase/firebaseApp"; // あなたの場所に合わせてね🙂

type AuthState = {
  user: User | null;
  loading: boolean;
};

const AuthContext = createContext<AuthState | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const unsub = onAuthStateChanged(auth, (u) => {
      setUser(u);
      setLoading(false);
    });
    return unsub;
  }, []);

  const value = useMemo(() => ({ user, loading }), [user, loading]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
```

---

## 2) “門番コンポーネント” を作る（ProtectedLayout）🚧👮

ここがこの章の主役です🔥
React Router v7 は **「ルートを守る専用の親ルート」**を作って、子ルートを `Outlet` で流すのが定番です。([React Router][1])

**src/routes/ProtectedLayout.tsx**

```tsx
import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../auth/AuthProvider";

export function ProtectedLayout() {
  const { user, loading } = useAuth();
  const location = useLocation();

  // ① まだ判定中なら待つ（ここ超重要！）
  if (loading) {
    return (
      <div style={{ padding: 24 }}>
        <div>ログイン状態を確認中…⏳</div>
      </div>
    );
  }

  // ② 未ログインならログインへ（「元いた場所」を state に保存）
  if (!user) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  // ③ ログイン済みなら、守りたいページたちを表示
  return <Outlet />;
}
```

* `useLocation()` で「今どこにいるか」を取れます([React Router][2])
* `Outlet` は「ここに子ルートを表示する穴」です([React Router][1])

---

## 3) ルーター設定で “ログイン必須ゾーン” を作る🗺️✨

`createBrowserRouter` の構成例です。
（React Router v7 は Node 20 以上が要件として明記されています）([React Router][3])

**src/AppRouter.tsx**

```tsx
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import { ProtectedLayout } from "./routes/ProtectedLayout";
import { RootLayout } from "./routes/RootLayout";
import { HomePage } from "./routes/HomePage";
import { LoginPage } from "./routes/LoginPage";
import { MyPage } from "./routes/MyPage";

const router = createBrowserRouter([
  {
    path: "/",
    element: <RootLayout />,
    children: [
      { index: true, element: <HomePage /> },
      { path: "login", element: <LoginPage /> },

      // 🔐 ここから下が「ログイン必須ゾーン」
      {
        element: <ProtectedLayout />,
        children: [
          { path: "mypage", element: <MyPage /> },
          // 例: { path: "settings", element: <SettingsPage /> },
        ],
      },
    ],
  },
]);

export function AppRouter() {
  return <RouterProvider router={router} />;
}
```

そして **AuthProvider を Router より上**に置きます👇

**src/App.tsx**

```tsx
import { AuthProvider } from "./auth/AuthProvider";
import { AppRouter } from "./AppRouter";

export default function App() {
  return (
    <AuthProvider>
      <AppRouter />
    </AuthProvider>
  );
}
```

---

## 4) ログイン成功したら “元いたページ” に戻す🔁🎉

`ProtectedLayout` が `state.from` を渡してるので、ログイン画面でそれを読んで戻ります🙂

**src/routes/LoginPage.tsx（戻り先だけ抜粋）**

```tsx
import type { Location } from "react-router-dom";
import { useLocation, useNavigate } from "react-router-dom";

type LocationState = { from?: Location };

export function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const state = location.state as LocationState | null;

  const fromPath = state?.from?.pathname ?? "/mypage";

  async function onLoginSuccess() {
    navigate(fromPath, { replace: true });
  }

  // ここでメール/Googleログインを実行して…
  // 成功したら onLoginSuccess() を呼ぶ
  return (
    <div style={{ padding: 24 }}>
      <h1>ログイン🔐</h1>
      {/* ログインUI */}
      <button onClick={onLoginSuccess}>（例）ログイン成功として戻る</button>
    </div>
  );
}
```

---

## 5) よくあるハマりどころ（ここだけ見れば事故が減る）🧯😵‍💫

## A) “一瞬ログイン画面に飛ぶ” チラつき問題👻

原因：`loading` を見ずに `user==null` で即リダイレクトしてる
対策：**必ず loading を先に処理**（この章の実装はOK👍）

## B) 無限リダイレクト♾️

原因：ログイン画面まで守ってしまってる（/login も Protected の子に入れてる）
対策：/login は **保護ゾーンの外**に置く✅

## C) ログイン後に戻れない🤔

原因：`Navigate` で `state` を渡してない / ログイン側で `state.from` を読んでない
対策：この章の `state={{ from: location }}` と `navigate(fromPath)` をセットで✅

## D) “ログイン画面をリロードしたら戻り先が消えた”🔄

`location.state` は **ページを丸ごとリロードすると消えやすい**です。
より強くするなら「next をクエリに入れる」方式が安定します💪（特に `signInWithRedirect()` みたいに画面遷移が絡むとき）

---

## 6) ミニ課題：マイページにユーザー情報を表示👤✨

**src/routes/MyPage.tsx（例）**

```tsx
import { useAuth } from "../auth/AuthProvider";

export function MyPage() {
  const { user } = useAuth();

  return (
    <div style={{ padding: 24 }}>
      <h1>マイページ👤</h1>
      <p>displayName: {user?.displayName ?? "（未設定）"}</p>
      <p>email: {user?.email ?? "（なし）"}</p>
      <p>uid: {user?.uid}</p>
    </div>
  );
}
```

---

## 7) AIでUX強化（この章の“おまけ”🤖💬）

ログインが必要な理由って、ユーザーにとっては「なんで？」になりがちです🙂
そこで **Firebase AI Logic** を使って、やさしい説明文をその場で生成しちゃいます✨
（Web だと `firebase/ai` から `getAI` / `getGenerativeModel` を使う形が公式に載っています）([Firebase][4])

たとえばログイン画面に「なぜログインが必要？」ボタン👇

```tsx
import { initializeApp } from "firebase/app";
import { getAI, getGenerativeModel, GoogleAIBackend } from "firebase/ai";

const firebaseApp = initializeApp({ /* いつもの config */ });
const ai = getAI(firebaseApp, { backend: new GoogleAIBackend() });
const model = getGenerativeModel(ai, { model: "gemini-2.5-flash" });

export async function generateWhyLoginText(pageName: string) {
  const prompt = `ユーザー向けに日本語で、やさしく短く説明して。
「${pageName}」は個人データを扱うのでログインが必要、という感じ。
絵文字も少し入れて🙂`;
  const result = await model.generateContent(prompt);
  return result.response.text();
}
```

※ ちなみに公式ガイド内で **Gemini 2.0 Flash/Flash-Lite が 2026-03-31 にリタイア予定**と明記されているので、学習段階でも新しめモデル名を使うのが安心です🧠([Firebase][4])

---

## 8) Antigravity / Gemini CLI をここでどう使う？🚀🧑‍💻

## Antigravity（エージェントで“門番実装”を一気に作る）🛰️

「ProtectedLayout と Router 構成を作って、/login は保護しないで」みたいなミッション設計がやりやすいです。([Google Codelabs][5])

おすすめ指示（コピペ用）👇

* 「React Router v7 で ProtectedLayout（Outlet/Navigate/useLocation）を作成して」
* 「ログイン成功後に元URLへ戻る実装（state.from）も入れて」
* 「無限リダイレクトのテスト観点も箇条書きで出して」

## Gemini CLI（プロジェクト全体を点検🔎）🧰

Gemini CLI はターミナルから“コード理解→修正提案”までやれる設計です。([Google Cloud Documentation][6])

おすすめの使い方👇

* 「/login が ProtectedLayout 配下に入ってないかチェックして」
* 「loading 判定が抜けてチラつく箇所がないか探して」
* 「保護したいルート一覧を抽出して、ルーター設定案を提案して」

---

## 9) 最終チェック✅🧪

* 未ログインで /mypage を開く → /login へ飛ぶ🚪
* ログイン成功 → /mypage に戻る🔁
* リロードしても、ログイン済みなら /mypage が開く♻️
* ログアウト後に /mypage を開く → また /login へ🚧

---

必要なら次のメッセージで、**「next クエリ方式（リロードしても戻り先が消えない版）」**まで仕上げた“決定版ガード”も書けます🙂✨

[1]: https://reactrouter.com/api/components/Outlet?utm_source=chatgpt.com "Outlet"
[2]: https://reactrouter.com/api/hooks/useLocation?utm_source=chatgpt.com "useLocation"
[3]: https://reactrouter.com/upgrading/v6?utm_source=chatgpt.com "Upgrading from v6"
[4]: https://firebase.google.com/docs/ai-logic/get-started "Get started with the Gemini API using the Firebase AI Logic SDKs  |  Firebase AI Logic"
[5]: https://codelabs.developers.google.com/getting-started-google-antigravity?utm_source=chatgpt.com "Getting Started with Google Antigravity"
[6]: https://docs.cloud.google.com/gemini/docs/codeassist/gemini-cli?utm_source=chatgpt.com "Gemini CLI | Gemini for Google Cloud"
