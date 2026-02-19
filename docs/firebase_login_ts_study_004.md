# 第04章：ログイン状態の監視：`onAuthStateChanged`で背骨を通す🦴

この章は、**「アプリ起動 → ログイン済みかどうかが確定 → 画面が正しく切り替わる」**という“背骨”を通す回です🙂
ここができると、次の章（ログイン実装）も、その後の「ログイン必須ページ🚧」もスイスイ進みます！

> ちなみに本日時点（2026-02-16）で、`firebase`（Web/JS SDK）の最新リリースは **v12.9.0（2026-02-05公開）** が見えています📌 ([Firebase][1])

---

## 1) まずイメージ：ログイン状態は「3つの状態」になる🧠🧊🔥

![Three Authentication States](./picture/firebase_login_ts_study_004_01_three_states.png)

アプリ起動直後、認証状態はこうなりがち👇

1. **まだ分からない**（初期化中）⏳ ← ここが超重要！
2. **ログイン中**（`user` がいる）👤
3. **ログアウト中**（`user` が `null`）🚪

ここで、②③だけ見てると事故ります💥
**初期化が終わる前**に「ログアウト扱いの画面」を出してしまい、**チラつき**が起きるからです😵‍💫

そこで **`onAuthStateChanged`** を使って、**「確定してから表示」**にします✨
公式でも「`currentUser` がまだ `null` のことがあるから、オブザーバ（監視）を置くのがオススメ」と明確に書かれています🧷 ([Firebase][2])

---

## 2) 「監視」の正体：`onAuthStateChanged` は何をしてくれる？👀

![Auth Monitor Flow](./picture/firebase_login_ts_study_004_02_monitor_flow.png)

`onAuthStateChanged(auth, callback)` は、

* ログイン状態が確定したら `callback(user)` を呼ぶ✅
* その後もログイン/ログアウトで呼び続ける🔁
* 解除用の **unsubscribe関数** を返す🧹

さらに大事ポイント👇
リダイレクトログイン（後の章でやる `signInWithRedirect`）でも、**`getRedirectResult()` が解決してから通知**されるので、変な中間状態を避けやすいです🛡️ ([Firebase][2])

---

## 3) 実装方針：`AuthProvider`（React Context）で全画面共通の“背骨”にする🦴🧩

![AuthProvider Backbone](./picture/firebase_login_ts_study_004_03_provider_bone.png)

この章で作るものはこれ👇

* `AuthProvider`：アプリ全体を包むコンポーネント
* `useAuth()`：どこからでも `user / loading` を取るフック
* `AuthGate`：表示の分岐（loading中はスピナー、確定したら中身）

イメージ図🗺️

```text
<App>
  <AuthProvider>
    loading: true  →  (onAuthStateChanged で確定)  → loading: false
    user: null / User
    └─ 画面を切り替える
  </AuthProvider>
</App>
```

---

## 4) 手を動かす：`AuthProvider` を作る🛠️✨

> 前章までで `firebase/app` と `firebase/auth` を初期化して `auth` を export 済み、という前提で進めるね🙂
> （まだなら、先に `getAuth()` まで通しておこう！）

## 4-1. `AuthProvider.tsx`（監視して state を持つ）🧱

```tsx
// src/features/auth/AuthProvider.tsx
import React, { createContext, useContext, useEffect, useMemo, useState } from "react";
import { onAuthStateChanged, type User } from "firebase/auth";
import { auth } from "@/lib/firebase"; // あなたのプロジェクトの配置に合わせてね🙂

type AuthState = {
  user: User | null;
  loading: boolean;
};

const AuthContext = createContext<AuthState | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // ✅ 監視開始
    const unsubscribe = onAuthStateChanged(auth, (nextUser) => {
      setUser(nextUser);
      setLoading(false); // ← 「確定した！」の合図
    });

    // ✅ 監視解除（メモリリーク＆二重購読防止）
    return () => unsubscribe();
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

## ✅ ここが“背骨”ポイント

* `loading` を **最初 true** にする
* `onAuthStateChanged` が来た瞬間に **false** にする
* `unsubscribe()` を必ず返す（Reactの開発モードだと特に重要！）🧹

---

## 4-2. `App` の一番外側で `AuthProvider` を使う🌍

```tsx
// src/main.tsx もしくは src/App.tsx（プロジェクト構成による）
import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import { AuthProvider } from "@/features/auth/AuthProvider";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <AuthProvider>
      <App />
    </AuthProvider>
  </React.StrictMode>
);
```

---

## 5) 表示を切り替える：`AuthGate` を作ってチラつきを消す✨🪄

![AuthGate Switch](./picture/firebase_login_ts_study_004_04_auth_gate.png)

```tsx
// src/features/auth/AuthGate.tsx
import React from "react";
import { useAuth } from "@/features/auth/AuthProvider";

export function AuthGate({
  signedIn,
  signedOut,
}: {
  signedIn: React.ReactNode;
  signedOut: React.ReactNode;
}) {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div style={{ padding: 24 }}>
        <div>認証状態を確認中…⏳</div>
      </div>
    );
  }

  return <>{user ? signedIn : signedOut}</>;
}
```

`App.tsx` で使うとこう👇

```tsx
// src/App.tsx
import React from "react";
import { AuthGate } from "@/features/auth/AuthGate";

function SignedOut() {
  return <div>ログイン画面（次章で作るよ）🔑🙂</div>;
}

function SignedIn() {
  return <div>ログイン済み！マイページへようこそ🎉</div>;
}

export default function App() {
  return <AuthGate signedIn={<SignedIn />} signedOut={<SignedOut />} />;
}
```

---

## 6) ここで一回「永続化」の感覚だけ掴む💾🧠

![Persistence Types](./picture/firebase_login_ts_study_004_05_persistence.png)

「リロードしてもログインが残る」って、魔法じゃなくて **永続化（persistence）** の話です✨
Webではデフォルトが **`local`**（ブラウザが対応していれば）になっていて、タブを閉じても残ります。 ([Firebase][3])

* `local`：閉じても残る（個人PC向け）🏠
* `session`：そのタブ/ウィンドウだけ（共有PC向け）🧑‍🤝‍🧑
* `none`：メモリだけ（更新で消える）🫥

この3つが公式に整理されています📘 ([Firebase][3])

※ persistence を切り替える実装は後の章でもいいけど、**「ログインが残る/残らないは設計できる」**だけ覚えておけばOK🙂

---

## 7) AI を絡める：ログイン状態の説明文を “その場で” やさしくする🤖💬✨

![AI Logic Helper](./picture/firebase_login_ts_study_004_06_ai_helper.png)

ここはミニおまけ！
**Firebase AI Logic** は、アプリから **Gemini** を呼んで文章生成などをしやすくする導線です🧠✨ ([Firebase][4])

たとえば「今の状態をやさしく説明する」ボタンを作ると、初心者向けUXが一気に上がります🙂🌈

> 公式の Get started では `getAI()` → `getGenerativeModel()` の形で使う例が載っています📌 ([Firebase][4])

（実装は後のAI章で深掘りしてもいいけど、雰囲気だけ👇）

```ts
// 例：AIに「ログイン状態の説明文」を作らせる（雰囲気コード）
/*
import { getAI, getGenerativeModel, GoogleAIBackend } from "firebase/ai";
import { app } from "@/lib/firebase";

const ai = getAI(app, { backend: new GoogleAIBackend() });
const model = getGenerativeModel(ai, { model: "gemini-2.0-flash" });

export async function makeAuthHintText(isSignedIn: boolean) {
  const prompt = isSignedIn
    ? "ユーザーに『ログイン済み』をやさしく短く伝えて。絵文字も少し。"
    : "ユーザーに『ログアウト中』をやさしく短く伝えて。次に何をすればいいかも。絵文字も少し。";

  const result = await model.generateContent(prompt);
  return result.response.text();
}
*/
```

---

## 8) Antigravity / Gemini CLI をこの章でどう使う？🚀🔍

![Antigravity Mission Control](./picture/firebase_login_ts_study_004_07_antigravity.png)

## ✅ Google Antigravity（エージェント開発環境）での使い方🛰️

Antigravityは「エージェントが計画→実装→検証まで回す」開発プラットフォーム、という位置づけで紹介されています。ミッション管理（Mission Control）も特徴として説明されています🧭 ([Google Codelabs][5])

**この章で投げるミッション例**👇（コピペでOK）

* 「`AuthProvider` を作って。`user/loading` を持って、`onAuthStateChanged` で更新して。購読解除も忘れずに」🦴
* 「`AuthGate` を作って。`loading` 中はスピナー、確定後に `user` で分岐して」🚦
* 「“チラつき”が起きないか、UIの遷移をチェックして改善案も出して」🧪

## ✅ Gemini CLI（ターミナルAI）での使い方⌨️🤖

Gemini CLI は **`npm install -g @google/gemini-cli`** で入れられる（stable）と公式ドキュメントに書かれています📌 ([Gemini CLI][6])
また、codelabでも **Node 20+** を先に入れる流れで説明されています🧱 ([Google Codelabs][7])

**この章での使い方（超実用）**👇

* 「`onAuthStateChanged` が二重購読になってない？（StrictMode含む）コード見てチェックして」🔎
* 「`loading` が true のままになる経路ない？（return漏れ・例外）探して」🧯
* 「`AuthProvider` の責務を増やしすぎてない？ 分割案出して」✂️

---

## 9) よくあるつまずき集 🧨➡️🩹

## Q1. リロード直後にログアウト画面が一瞬出る😵

👉 `loading` を見てない可能性大！
`onAuthStateChanged` が来る前は「未確定」なので、**loading中は何も判定しない**のがコツです⏳

## Q2. 開発中だけログが2回出る🤔

👉 Reactの開発モード（StrictMode）で effect が意図的に2回動くことがあります。
でも `unsubscribe()` を入れていれば、**本番で致命傷にはなりにくい**です🙂（入れてなかったら入れよう🧹）

## Q3. `auth.currentUser` が `null` で焦る😱

👉 公式でも「初期化が終わってないと `null` がありえる」ので、**監視（observer）を推奨**しています📘 ([Firebase][2])

---

## 10) ミニ課題 🎮✅

## ミニ課題A：デバッグ表示パネルを作る🪪🔧

* ログイン中なら `uid / email / providerId` を表示
* ログアウト中なら「ログアウト中🚪」と表示

## ミニ課題B：AIで“状態説明”ボタンを付ける🤖💬

* 「いま何が起きてる？」ボタンを押す
* AIが短文で説明（例：「認証状態を確認できたよ！次はログインしてね🔑🙂」）

---

## 11) この章のチェックリスト ✅✅✅

* [ ] `AuthProvider` がアプリの最上流にある🌊
* [ ] `user` と `loading` を Context で配れる🧩
* [ ] `loading` 中にログアウト扱いにしない（チラつき防止）✨
* [ ] `onAuthStateChanged` の解除（unsubscribe）が入ってる🧹
* [ ] リロードしてもログイン状態が復元される雰囲気がある💾 ([Firebase][3])

---

次の第5章からは、いよいよ **メール＋パスワードのサインアップ画面✍️🔑** を作って、「ログインできた！」の成功体験を取りに行くよ〜🎉

[1]: https://firebase.google.com/support/release-notes/js "Firebase JavaScript SDK Release Notes"
[2]: https://firebase.google.com/docs/auth/web/manage-users?hl=ja "Firebase でユーザーを管理する"
[3]: https://firebase.google.com/docs/auth/web/auth-state-persistence "Authentication State Persistence  |  Firebase"
[4]: https://firebase.google.com/docs/ai-logic/get-started "Get started with the Gemini API using the Firebase AI Logic SDKs  |  Firebase AI Logic"
[5]: https://codelabs.developers.google.com/getting-started-google-antigravity?utm_source=chatgpt.com "Getting Started with Google Antigravity"
[6]: https://geminicli.com/docs/get-started/installation/?utm_source=chatgpt.com "Gemini CLI installation, execution, and releases"
[7]: https://codelabs.developers.google.com/gemini-cli-hands-on?utm_source=chatgpt.com "Hands-on with Gemini CLI"
