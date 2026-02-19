# 第20章：ミニ課題：ログイン必須ページ完成＋チェックリスト✅🚪

ここは“総仕上げ回”だよ〜！😄
いままで作ってきた **メールログイン＋Googleログイン**を、**「ログイン必須ページ（ガード付き）」として完成**させて、さらに **エラーがやさしい日本語**で出るように整えて、最後に **AI（Firebase AI Logic / Gemini）**でUXを一段よくします🤖✨

---

## 0) この章のゴール（完成形イメージ）🏁🧭

完成したらこうなる👇😊

* `/login`：メールログイン + Googleログイン（Popupメイン、Redirectも逃げ道）🌈
* `/signup`：メール登録✍️
* `/mypage`：ログイン必須（未ログインなら `/login` へ）🚧
* エラー表示が「次に何をすればいいか」わかる言葉になってる😇
* ログイン失敗時に「原因の説明💬」をGeminiに作ってもらえる（押すと出る）🤖✨（Firebase AI Logic）

---

## 1) “最終チェック用”の作るものリスト🧱📝

この章で揃える部品はこれ！

1. **ルート構成**（`/login` `/signup` `/mypage`）🧭
2. **Auth状態の一本化**（`AuthProvider` / `useAuth`）🦴
3. **ガード（RequireAuth）** 🚧
4. **Googleログイン：Popup + Redirect**（Popupがダメな環境の逃げ道）🌈
5. **getRedirectResultの回収**（Redirectで戻ってきたときの結果取得）🔁
6. **エラー翻訳テーブル**（Firebaseのエラーコード→やさしい表示）🗺️
7. **AIボタン**（Geminiが“原因説明”を生成）🤖📝

---

## 2) ルーティング（React Router）を“完成形”にする🧭✨

![Route Structure Map

**Labels to Render**:
- Public: "/login, /signup"
- Guard: "RequireAuth 🚧"
- Private: "/mypage 🔐"

**Visual Details**:
1. Core Concept: The final routing structure.
2. Metaphor: A map of the app. Public area is open. Private area is fenced off with a guard station.
3. Action: Guarding.
4. Layout: Map view.](./picture/firebase_login_ts_study_020_01_route_structure.png)


まずはルートを3つに固定しよう👍
（すでに第16章でやってたら「最終形に整える」感じでOK！）

* `/login` → ログインページ
* `/signup` → 登録ページ
* `/mypage` → ログイン必須ページ（ガード付き）

例（超ざっくり）👇

```tsx
// App.tsx（例）
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./auth/AuthProvider";
import { RequireAuth } from "./auth/RequireAuth";
import { LoginPage } from "./pages/LoginPage";
import { SignupPage } from "./pages/SignupPage";
import { MyPage } from "./pages/MyPage";

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<Navigate to="/mypage" replace />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<SignupPage />} />
          <Route
            path="/mypage"
            element={
              <RequireAuth>
                <MyPage />
              </RequireAuth>
            }
          />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
```

---

## 3) RequireAuth（ガード）を“事故らない形”にする🚧🛡️

![RequireAuth Logic Flow

**Labels to Render**:
- Check 1: "Loading? -> Spinner ⏳"
- Check 2: "User? -> Content ✅"
- Else: "Redirect -> Login 🔁"

**Visual Details**:
1. Core Concept: The decision logic of the auth guard.
2. Metaphor: A traffic control point. Stop for loading. Pass for user. Detour for guest.
3. Action: Directing traffic.
4. Layout: Flowchart.](./picture/firebase_login_ts_study_020_02_require_auth_logic.png)


ガードの鉄板はこれ👇

* `loading` の間はスピナー（ここ超大事！）⏳
* `user == null` なら `/login` に飛ばす（できれば“戻り先”も渡す）🔁
* `user != null` なら子コンポーネント表示🙆‍♂️

```tsx
// auth/RequireAuth.tsx（例）
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "./useAuth";

export function RequireAuth({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return <div style={{ padding: 24 }}>読み込み中…⏳</div>;
  }

  if (!user) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }

  return <>{children}</>;
}
```

---

## 4) Googleログイン：Popupメイン＋Redirectを“逃げ道”として用意🌈🚪

![Google Login Fallback

**Labels to Render**:
- Attempt: "Popup"
- Fail: "Blocked 🚫"
- Fallback: "Redirect 🚪"
- Success: "Login"

**Visual Details**:
1. Core Concept: Popup failing and falling back to Redirect.
2. Metaphor: A user trying a revolving door (Popup). It's stuck. They use the side door (Redirect) instead.
3. Action: Switching paths.
4. Layout: Process flow.](./picture/firebase_login_ts_study_020_03_google_login_flow.png)


## なぜPopupだけじゃダメ？🤔

PopupはPCで体験が良いけど、**環境によってはブロック**されることがある😵‍💫
だから「PopupがダメならRedirectボタンを出す」が優しい✨

しかも Redirect は、近年のブラウザ事情で **追加の対策が必要**になることがあるよ。Firebase公式も「本番で全ブラウザで意図どおり動かすには、案内されてる選択肢のどれかを必ず実装してね」と明言してる。さらに **2024-06-24以降、Chrome M115+ でも必須**になったよ（Firefox/Safariはもっと前から必須）。([Firebase][1])

## 実装方針（おすすめ）👍

* Googleログインボタン（Popup）
* Popupがブロックされたっぽいエラーなら「Redirectでログイン」ボタンを表示
* Redirectで戻ってきたら `getRedirectResult()` を回収する🔁（後でやる）

---

## 5) Loginページ（メール＋Google＋エラー表示）を完成させる🔑🌈😇

![Login Page Wireframe

**Labels to Render**:
- Title: "Login"
- Input: "Email/Pass"
- Button: "Google (Popup)"
- Link: "Use Redirect"

**Visual Details**:
1. Core Concept: The layout of the login page with fallback options.
2. Metaphor: A clean UI wireframe showing the hierarchy of buttons.
3. Action: Displaying UI.
4. Layout: Wireframe.](./picture/firebase_login_ts_study_020_04_login_page_ui.png)


ポイントはこの3つ！

1. メールログイン（成功したら “元のページ”へ戻す）🔁
2. Googleログイン（まずPopup）🌈
3. エラーは“翻訳して表示”😇（AIボタンは次で追加）

例👇（必要なところだけ抜粋）

```tsx
// pages/LoginPage.tsx（例）
import { useLocation, useNavigate, Link } from "react-router-dom";
import { useState } from "react";
import { useAuth } from "../auth/useAuth";
import { toFriendlyAuthMessage } from "../lib/authErrors";

export function LoginPage() {
  const nav = useNavigate();
  const loc = useLocation();
  const from = (loc.state as any)?.from ?? "/mypage";

  const { loginWithEmail, loginWithGooglePopup, loginWithGoogleRedirect } = useAuth();

  const [email, setEmail] = useState("");
  const [pw, setPw] = useState("");
  const [err, setErr] = useState<string | null>(null);
  const [showRedirect, setShowRedirect] = useState(false);
  const [busy, setBusy] = useState(false);

  async function onEmailLogin() {
    setBusy(true); setErr(null);
    try {
      await loginWithEmail(email, pw);
      nav(from, { replace: true });
    } catch (e: any) {
      setErr(toFriendlyAuthMessage(e));
    } finally {
      setBusy(false);
    }
  }

  async function onGooglePopup() {
    setBusy(true); setErr(null); setShowRedirect(false);
    try {
      await loginWithGooglePopup();
      nav(from, { replace: true });
    } catch (e: any) {
      const msg = toFriendlyAuthMessage(e);
      setErr(msg);

      // Popup系の失敗なら「Redirectでやり直す」導線を出す（例）
      const code = e?.code as string | undefined;
      if (code?.includes("popup") || code === "auth/operation-not-supported-in-this-environment") {
        setShowRedirect(true);
      }
    } finally {
      setBusy(false);
    }
  }

  async function onGoogleRedirect() {
    setBusy(true); setErr(null);
    try {
      await loginWithGoogleRedirect();
      // ここで画面が遷移する（戻ってきたら getRedirectResult で回収）
    } catch (e: any) {
      setErr(toFriendlyAuthMessage(e));
      setBusy(false);
    }
  }

  return (
    <div style={{ padding: 24, maxWidth: 480 }}>
      <h1>ログイン🔐</h1>

      <div style={{ marginTop: 12 }}>
        <input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="メール" />
      </div>
      <div style={{ marginTop: 8 }}>
        <input value={pw} onChange={(e) => setPw(e.target.value)} placeholder="パスワード" type="password" />
      </div>

      <button disabled={busy} onClick={onEmailLogin} style={{ marginTop: 12 }}>
        メールでログイン🔑
      </button>

      <hr style={{ margin: "16px 0" }} />

      <button disabled={busy} onClick={onGooglePopup}>
        Googleでログイン🌈
      </button>

      {showRedirect && (
        <div style={{ marginTop: 8 }}>
          <button disabled={busy} onClick={onGoogleRedirect}>
            Popupが無理そう → Redirectでログイン🚪
          </button>
        </div>
      )}

      {err && <div style={{ marginTop: 12, color: "crimson" }}>{err}</div>}

      <div style={{ marginTop: 16 }}>
        <Link to="/signup">新規登録はこちら✍️</Link>
      </div>
    </div>
  );
}
```

---

## 6) Redirectで戻ってきた結果を“必ず回収”する🔁✅

![Redirect Result Retrieval

**Labels to Render**:
- App Start: "Init"
- Check: "getRedirectResult()"
- Result: "User Found"
- Action: "Set User"

**Visual Details**:
1. Core Concept: Retrieving the user after a redirect.
2. Metaphor: A baggage claim. The user arrives (App Start) and picks up their luggage (User Data) from the carousel (Redirect Result).
3. Action: Retrieving.
4. Layout: Timeline.](./picture/firebase_login_ts_study_020_05_redirect_result.png)


Redirectログインは、戻ってきたあとに **`getRedirectResult()` で結果を受け取る**のがセットだよね😊
Firebase公式のベストプラクティスでも `signInWithRedirect()` と `getRedirectResult()` の組み合わせが例示されてるよ。([Firebase][1])

これを `AuthProvider` の初期化で一回だけ実行して、エラーも表示できるようにしよう。

```tsx
// auth/AuthProvider.tsx（例：要点だけ）
import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { onAuthStateChanged, getRedirectResult, GoogleAuthProvider, signInWithRedirect, signInWithPopup, signInWithEmailAndPassword, signOut, User } from "firebase/auth";
import { auth } from "../lib/firebase";
import { toFriendlyAuthMessage } from "../lib/authErrors";

type AuthCtx = {
  user: User | null;
  loading: boolean;
  lastAuthError: string | null;
  loginWithEmail: (email: string, pw: string) => Promise<void>;
  loginWithGooglePopup: () => Promise<void>;
  loginWithGoogleRedirect: () => Promise<void>;
  logout: () => Promise<void>;
};

const Ctx = createContext<AuthCtx | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [lastAuthError, setLastAuthError] = useState<string | null>(null);

  useEffect(() => {
    let alive = true;

    async function boot() {
      // ① Redirect結果の回収（戻ってきた直後だけ意味がある）
      try {
        await getRedirectResult(auth);
      } catch (e: any) {
        if (alive) setLastAuthError(toFriendlyAuthMessage(e));
      }

      // ② 通常のログイン状態監視
      const unsub = onAuthStateChanged(auth, (u) => {
        if (!alive) return;
        setUser(u);
        setLoading(false);
      });

      return () => unsub();
    }

    const cleanupPromise = boot();
    return () => {
      alive = false;
      cleanupPromise.then((fn) => fn?.());
    };
  }, []);

  const value = useMemo<AuthCtx>(() => ({
    user,
    loading,
    lastAuthError,
    loginWithEmail: async (email, pw) => { await signInWithEmailAndPassword(auth, email, pw); },
    loginWithGooglePopup: async () => { await signInWithPopup(auth, new GoogleAuthProvider()); },
    loginWithGoogleRedirect: async () => { await signInWithRedirect(auth, new GoogleAuthProvider()); },
    logout: async () => { await signOut(auth); },
  }), [user, loading, lastAuthError]);

  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export function useAuth() {
  const v = useContext(Ctx);
  if (!v) throw new Error("AuthProviderが必要です");
  return v;
}
```

> Redirectログインを本番で“全ブラウザ安定”させたいときは、Firebase公式の **Option 1〜5**のどれかをちゃんと入れるのが大事だよ。
> とくに **2024-06-24以降はChromeでも必須**になってる点は、今から作るアプリでも避けて通れないやつ😵‍💫([Firebase][1])

---

## 7) エラー翻訳（“人間の言葉”にする）😇🗺️

Firebase Authのエラーは、コードのままだと冷たい…🥶
だから「よくあるやつだけでも翻訳表」を作ると、体験が一気に良くなる✨

```ts
// lib/authErrors.ts（例）
export function toFriendlyAuthMessage(e: any): string {
  const code = (e?.code as string | undefined) ?? "unknown";
  switch (code) {
    case "auth/invalid-email":
      return "メールアドレスの形がちょっと変かも…📧💦 もう一回確認してね！";
    case "auth/user-not-found":
      return "そのメールのユーザーが見つからなかったよ👀 登録がまだなら新規登録へ！";
    case "auth/wrong-password":
      return "パスワードが違うみたい…🔑💦 入力ミスがないか見てみてね！";
    case "auth/too-many-requests":
      return "試行回数が多いので、少し時間をおいてから試してね⏳";
    case "auth/popup-blocked":
      return "Popupがブロックされたみたい😵 ブラウザ設定を確認するか、Redirectで試してね🚪";
    case "auth/popup-closed-by-user":
      return "Popupを閉じたみたい！もう一回やってみよう😊";
    default:
      return `ログインでエラーが起きたよ😢（${code}）`;
  }
}
```

---

## 8) 伸ばし（AI）：失敗理由の説明をGeminiに作らせる💬🤖✨

![AI Error Explanation Flow

**Labels to Render**:
- Error: "Login Failed ❌"
- Click: "Ask AI 🤖"
- AI: "Gemini"
- Explanation: "Check your caps lock! 💡"

**Visual Details**:
1. Core Concept: User requesting help from AI for an error.
2. Metaphor: A user showing a broken part to a robot mechanic, who gives a clear diagnosis.
3. Action: Diagnosing.
4. Layout: Interaction sequence.](./picture/firebase_login_ts_study_020_06_ai_error_flow.png)


ここからが“今っぽい強化”🔥
ログインに失敗したとき、ただエラーを出すだけじゃなくて、

* 「何が起きたか」
* 「ユーザーが次に何をすればいいか」

を **Geminiが短くやさしく説明**してくれるボタンを付けよう😊

## Firebase AI Logic（Web）の最小セット🧩

Firebase公式のWeb例では、`firebase/ai` から `getAI`, `getGenerativeModel`, `GoogleAIBackend` を使うよ。([Firebase][2])
また、**Gemini 2.0 Flash 系が 2026-03-31 に退役予定**なので、今からなら `gemini-2.5-...` 系を選ぶのが安全だよ（例：`gemini-2.5-flash` / `gemini-2.5-flash-lite`）。([Firebase][2])

## 8-1) `lib/ai.ts` を作る（AIの窓口）🚪🤖

```ts
// lib/ai.ts（例）
import { firebaseApp } from "./firebase";
import { getAI, getGenerativeModel, GoogleAIBackend } from "firebase/ai";

const ai = getAI(firebaseApp, { backend: new GoogleAIBackend() });
const model = getGenerativeModel(ai, { model: "gemini-2.5-flash" });

export async function explainAuthErrorWithAI(params: {
  errorCode: string;
  situation: "login" | "signup";
}): Promise<string> {
  // 個人情報は送らない（メール・パスワード・UIDなどは入れない）🙅‍♂️
  const prompt =
    `あなたはWebアプリのサポート担当です。` +
    `ユーザーに向けて、次を日本語でやさしく説明して。` +
    `\n- 起きたこと（1文）` +
    `\n- どうすれば直るか（2〜3個の箇条書き）` +
    `\n- 不安を煽らないトーン` +
    `\n\n状況: ${params.situation}` +
    `\nFirebase Auth errorCode: ${params.errorCode}`;

  const result = await model.generateContent(prompt);
  // SDKの返し方は環境で差があるので「とにかくテキストを返す」形に寄せる
  const text = (result as any)?.response?.text?.() ?? (result as any)?.text ?? "";
  return String(text || "うまく説明を作れなかった…ごめんね🥲");
}
```

> Firebase AI Logic の導入フローでは、コンソール側でプロバイダ（Gemini Developer API 推奨）を選んで、必要APIやキーを準備する流れになってるよ。キーをアプリに直書きしない注意も書かれてる。([Firebase][2])
> それと、開発が本気になってきたら **App Checkを早めに入れるのが推奨**だよ🛡️([Firebase][2])

## 8-2) Login画面に「原因を説明して💬」ボタンを付ける✨

```tsx
// LoginPage.tsx のどこか（例）
import { explainAuthErrorWithAI } from "../lib/ai";

const [aiHelp, setAiHelp] = useState<string | null>(null);
const [aiBusy, setAiBusy] = useState(false);
const [lastErrorCode, setLastErrorCode] = useState<string | null>(null);

// catch(e) の中で
// setLastErrorCode(e?.code ?? "unknown");

async function onAskAI() {
  if (!lastErrorCode) return;
  setAiBusy(true);
  try {
    const text = await explainAuthErrorWithAI({ errorCode: lastErrorCode, situation: "login" });
    setAiHelp(text);
  } finally {
    setAiBusy(false);
  }
}
```

表示部分👇

```tsx
{lastErrorCode && (
  <div style={{ marginTop: 8 }}>
    <button disabled={aiBusy} onClick={onAskAI}>
      原因をやさしく説明して💬🤖
    </button>
  </div>
)}

{aiHelp && (
  <div style={{ marginTop: 8, whiteSpace: "pre-wrap", background: "#f6f6f6", padding: 12 }}>
    {aiHelp}
  </div>
)}
```

---

## 9) Antigravity / Gemini CLI で“仕上げの品質チェック”をやる🔎🤖🛠️

## Antigravity（エージェント）に投げるミッション例🛰️

Antigravityは「複数エージェントをミッションコントロールで動かす」系の開発体験を狙ったものだよ。([Google Codelabs][3])
この章の相性、めっちゃ良い🙂

* ミッションA：`RequireAuth` の分岐漏れ（loading/user null）チェック🚧
* ミッションB：Authエラーコード一覧の“不足”を洗い出して候補追加🗺️
* ミッションC：`getRedirectResult` の呼び出し位置が安全かレビュー🔁
* ミッションD：UI文言（説明、ボタン、補足文）を統一して整える🧼✨

## Gemini CLIで「抜け・漏れ」点検🧪

Gemini CLI はターミナルで使えるオープンソースのAIエージェントで、ReActループやMCPなども触れられる設計になってるよ。([Google Cloud Documentation][4])

やること例👇（イメージ）

* 「未ログインで `/mypage` 直打ちしたときの挙動」をレビュー
* 「Popupが失敗したときの導線」が自然かレビュー
* 「エラーメッセージが責めてないか」レビュー😇

---

## 10) 最終チェックリスト（この章の合格ライン）✅✅✅

![Chapter Completion Checklist

**Labels to Render**:
- Item 1: "Routes OK 🧭"
- Item 2: "Guard OK 🚧"
- Item 3: "Redirect OK 🔁"
- Item 4: "AI OK 🤖"

**Visual Details**:
1. Core Concept: Verifying all completed tasks.
2. Metaphor: A golden clipboard with all items checked off.
3. Action: Verification.
4. Layout: Checklist view.](./picture/firebase_login_ts_study_020_07_checklist.png)


ここ、チェックが全部つけば勝ち！🎉

* [ ] `/mypage` を未ログインで開く → `/login` に飛ぶ🚧
* [ ] ログイン成功 → 元のページ（`from`）に戻る🔁
* [ ] リロードしてもログイン状態が方針どおり維持される（local/sessionなど）🔄
* [ ] ログアウト → ログイン前UIに戻る🚪
* [ ] Googleログイン：Popupが成功する🌈
* [ ] Popupが失敗する環境でも Redirect導線で詰まらない🚪
* [ ] Redirectで戻ってきたあと `getRedirectResult()` が回収されてる🔁
* [ ] エラー文が「次に何すればいいか」になってる😇
* [ ] AIボタンが押せて、説明文が出る💬🤖

> Redirectの本番安定化は、Firebase公式の “Option 1〜5” のどれを採るかが超重要だよ（ホスティング形態で分岐するやつ）。([Firebase][1])

---

## 11) ミニ問題（理解チェック）📝🙂

1. `RequireAuth` で `loading` 中に即リダイレクトしちゃうと何が起きる？⏳
2. Redirectログインで “戻ってきた結果” を受け取る関数はどれ？🔁
3. Popupがブロックされたとき、ユーザーに用意すべき導線は？🚪
4. AIに送っていい情報・ダメな情報の例を1つずつ言える？🙅‍♂️✅

---

## 次に進むなら…🔜🔥

この“認証の背骨”ができたら、次の章（Firestore）で **`users/{uid}` を中心にデータを持つ**設計が一気に気持ちよくなるよ🦴➡️📚

「今のコード構成（ファイル一覧）を貼る」か、「今どこまで動いてるか（Popup/Redirect/AI）」を教えてくれたら、あなたの状態に合わせて“最短で合格”に寄せる調整案も出せるよ😄✨

[1]: https://firebase.google.com/docs/auth/web/redirect-best-practices "Best practices for using signInWithRedirect on browsers that block third-party storage access  |  Firebase"
[2]: https://firebase.google.com/docs/ai-logic/get-started "Get started with the Gemini API using the Firebase AI Logic SDKs  |  Firebase AI Logic"
[3]: https://codelabs.developers.google.com/getting-started-google-antigravity?utm_source=chatgpt.com "Getting Started with Google Antigravity"
[4]: https://docs.cloud.google.com/gemini/docs/codeassist/gemini-cli?utm_source=chatgpt.com "Gemini CLI | Gemini for Google Cloud"
