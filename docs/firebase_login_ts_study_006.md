# 第06章：メールログイン：ログイン/ログアウトを通す🚪

この章でやることはシンプル👇
**「メール＋パスワードでログイン」→「ログアウト」→「UIが切り替わる」** を、ちゃんと“気持ちよく”通します🙂🌈
（Firebase公式のメールログイン手順と、`signOut`/エラー仕様も最新更新（2026-02-05）を踏まえて作っています）([Firebase][1])

---

## ゴール🎯

![Authentication Cycle](./picture/firebase_login_ts_study_006_01_cycle.png)

* ログインフォームから **メールログイン**できる✅
* ログアウトで **ログイン前UIに戻る**✅
* 失敗時に **ユーザーに優しいエラーメッセージ**を出せる✅
* （おまけ）AIで「失敗理由の説明」をやさしく生成できる🤖📝([Firebase][2])

---

## まず読む📚（超短くでOK）

* メール/パスワードでログインする基本は `signInWithEmailAndPassword` ([Firebase][1])
* ログアウトは `signOut` ([Firebase][1])
* 近年は **メール列挙（存在チェック）対策**の影響で、ログイン失敗が “まとめて同じエラー” になりがち（後で解説）([Zenn][3])

---

## 手を動かす🛠️：ログイン画面を作る（React + TypeScript）

## 1) 便利な「エラー翻訳」関数を用意😇🗺️

![Friendly Error Logic](./picture/firebase_login_ts_study_006_02_error_logic.png)

ログイン失敗は、基本 **「メールかパスワードが違う」** に寄せるのが安全です（理由は後述）。([Zenn][3])

```tsx
// src/features/auth/authErrorMessage.ts
export function toFriendlyAuthMessage(code: string): string {
  // まずは「ユーザー行動につながる」文にするのがコツ🙂
  switch (code) {
    case "auth/invalid-email":
      return "メールアドレスの形が変かも！もう一度チェックしてね🧐";
    case "auth/missing-password":
      return "パスワードが空っぽだよ！入力してね🔑";
    case "auth/user-disabled":
      return "このアカウントは無効になっているみたい…管理者に連絡してね🙏";
    case "auth/too-many-requests":
      return "試行回数が多いみたい💦 ちょっと時間をおいて再チャレンジしてね⏳";
    case "auth/network-request-failed":
      return "通信に失敗したよ📡 Wi-Fiや回線を確認してもう一度！";
    // 重要：列挙保護などで「全部これ」になりやすい
    case "auth/invalid-credential":
    default:
      return "メールアドレスかパスワードが違うみたい😵 もう一度試してね！";
  }
}
```

> ✅ポイント：**存在する/しない** を言い当てるメッセージ（「このメールは未登録です」など）は、セキュリティ的に避けがちです。最近は仕様としても “まとめて同じ失敗” になりやすいです。([Zenn][3])

---

## 2) ログインページ本体を実装✍️🚀

![Login Screen UI](./picture/firebase_login_ts_study_006_03_login_ui.png)

`signInWithEmailAndPassword(auth, email, password)` を呼ぶだけ！([Firebase][1])

```tsx
// src/features/auth/LoginPage.tsx
import { useMemo, useState } from "react";
import { signInWithEmailAndPassword } from "firebase/auth";
import { auth } from "../../lib/firebase"; // 既に作ってある想定（getAuthしたやつ）
import { toFriendlyAuthMessage } from "./authErrorMessage";

type Props = {
  onSuccess?: () => void; // ログイン成功後に画面遷移したい時用（任意）
};

export function LoginPage({ onSuccess }: Props) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [submitting, setSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const canSubmit = useMemo(() => {
    return email.trim().length > 0 && password.length > 0 && !submitting;
  }, [email, password, submitting]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setErrorMsg(null);
    setSubmitting(true);

    try {
      await signInWithEmailAndPassword(auth, email.trim(), password);
      onSuccess?.();
    } catch (err: any) {
      const code = typeof err?.code === "string" ? err.code : "unknown";
      setErrorMsg(toFriendlyAuthMessage(code));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div style={{ maxWidth: 420, margin: "40px auto", padding: 16 }}>
      <h1>ログイン🔐</h1>

      <form onSubmit={handleSubmit}>
        <label>
          メールアドレス📧
          <input
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            type="email"
            autoComplete="email"
            placeholder="you@example.com"
            style={{ width: "100%", padding: 10, marginTop: 6, marginBottom: 12 }}
          />
        </label>

        <label>
          パスワード🔑
          <input
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            type="password"
            autoComplete="current-password"
            placeholder="********"
            style={{ width: "100%", padding: 10, marginTop: 6, marginBottom: 12 }}
          />
        </label>

        <button disabled={!canSubmit} style={{ width: "100%", padding: 10 }}>
          {submitting ? "ログイン中…⏳" : "ログイン🚪"}
        </button>

        {errorMsg && (
          <p style={{ marginTop: 12 }}>
            ❗ {errorMsg}
          </p>
        )}
      </form>
    </div>
  );
}
```

---

## 3) ログアウトボタンを作る👋🚪

`signOut(auth)` でOK！([Firebase][1])

```tsx
// src/features/auth/LogoutButton.tsx
import { signOut } from "firebase/auth";
import { auth } from "../../lib/firebase";

export function LogoutButton() {
  async function handleLogout() {
    await signOut(auth);
  }

  return (
    <button onClick={handleLogout}>
      ログアウト🚪
    </button>
  );
}
```

---

## 4) いちばん簡単な「UI切り替え」例🔁

![Conditional UI Switching](./picture/firebase_login_ts_study_006_04_app_switch.png)

（ルーターやガードは後の章で本格的にやるとして、まずは最短で成功体験🙂）

```tsx
// src/App.tsx
import { useEffect, useState } from "react";
import { onAuthStateChanged, User } from "firebase/auth";
import { auth } from "./lib/firebase";
import { LoginPage } from "./features/auth/LoginPage";
import { LogoutButton } from "./features/auth/LogoutButton";

export default function App() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    return onAuthStateChanged(auth, (u) => {
      setUser(u);
      setLoading(false);
    });
  }, []);

  if (loading) return <p>起動中…⏳</p>;

  if (!user) {
    return <LoginPage />;
  }

  return (
    <div style={{ padding: 16 }}>
      <h1>ログインできた🎉</h1>
      <p>こんにちは！ {user.email ?? "（メール不明）"} 👤</p>
      <LogoutButton />
    </div>
  );
}
```

---

## つまずき対策🧯（ここ超大事）

## ✅ ログイン失敗が「全部同じ」に見えるのはバグじゃない

![Email Enumeration Protection](./picture/firebase_login_ts_study_006_05_security_mask.png)

最近の設定/仕様では、**メールアドレスが存在するかどうかを推測されないように**、ログイン失敗が “まとめて同じ扱い” になることがあります。
そのため、アプリ側は「未登録です！」みたいに断定しないほうが安全です。([Zenn][3])

## ✅ たまに出るエラーたち

* 通信系：`auth/network-request-failed` → 回線チェック📡
* 連打系：`auth/too-many-requests` → ちょい待ち⏳
* だいたいこれ：`auth/invalid-credential` → 「メールかパスワードが違う」😵([Firebase][4])

---

## AIでUX強化🤖✨：失敗理由を“やさしく説明”ボタンにする

![AI Error Explanation](./picture/firebase_login_ts_study_006_06_ai_assist.png)

ログイン失敗時に、ボタン1つで「何を確認すればいいか」を生成すると親切です🙂
Firebase AI Logic の Web例は `firebase/ai` を使う形が公式です。([Firebase][2])

```ts
// src/lib/ai.ts（例）
import { getAI, getGenerativeModel, GoogleAIBackend } from "firebase/ai";
import { firebaseApp } from "./firebaseApp"; // initializeApp したものをexportしてる想定

const ai = getAI(firebaseApp, { backend: new GoogleAIBackend() });
export const model = getGenerativeModel(ai, { model: "gemini-2.5-flash" }); 
```

```tsx
// LoginPage のエラー表示の下に置くイメージ（例）
import { model } from "../../lib/ai";

async function explainWithAI(errorMessage: string) {
  const prompt =
    "ログインに失敗したユーザーに、やさしい口調で原因候補と確認手順を3つだけ教えて。"
    + " 余計な専門用語はなし。"
    + " 失敗メッセージ: " + errorMessage;

  const result = await model.generateContent(prompt);
  return result.response.text();
}
```

> ⚠️モデル名は今後も更新されます。Firebase AI Logic 側で特定モデルの廃止予定も告知されているので、古いモデル名を固定しないのがコツです。([Firebase][2])

---

## Antigravity / Gemini CLI を“第6章の相棒”にする🧠🛠️

![Gemini CLI Ecosystem](./picture/firebase_login_ts_study_006_07_cli_tools.png)

## ✅ Gemini CLI 側に Firebase の道具箱（MCP）を追加

Firebase公式は、Gemini CLI に **Firebase拡張を入れる方法**を推しています。([Firebase][5])

```bash
gemini extensions install https://github.com/gemini-cli-extensions/firebase/
```

## ✅ Antigravity 側も Firebase MCP server を入れられる

Antigravity の画面から Firebase をインストールすると、内部的に `firebase-tools@latest mcp` を使う設定が入ります。([Firebase][5])

---

## ミニ課題🎒✅

1. ログイン成功後に「ようこそ🎉」を表示して、3秒後に自動で消す⏲️
2. ログイン失敗時に「AIにコツを聞く🤖」ボタンを付ける（押したら短い説明文が出る）📝
3. ログアウト後に「またね👋」を出す（出したらログインフォームへ）🔁

---

## チェックリスト✅✅✅

* [ ] メール＋パスワードでログインできる
* [ ] ログアウトで UI がログイン前に戻る
* [ ] 失敗時に “次の行動” が分かるメッセージが出る
* [ ] （できたら）AI説明で UX がさらにやさしくなる🤖✨

---

次の章（第7章）は、**確認メール**と**パスワードリセット**で「運用できる認証」に育てていきます📨🔁
必要なら、この第6章のコードを「React Router の画面遷移版」に組み直した完成形もそのまま出せるよ🙂

[1]: https://firebase.google.com/docs/auth/web/password-auth "Authenticate with Firebase using Password-Based Accounts using Javascript"
[2]: https://firebase.google.com/docs/ai-logic/get-started "Get started with the Gemini API using the Firebase AI Logic SDKs  |  Firebase AI Logic"
[3]: https://zenn.dev/junsei_tanaka/articles/684f9d3c1e5432?utm_source=chatgpt.com "[Firebase Auth] user-not-foundを拾いたいのに、invalid- ..."
[4]: https://firebase.google.com/docs/reference/js/auth "auth package  |  Firebase JavaScript API reference"
[5]: https://firebase.google.com/docs/ai-assistance/mcp-server "Firebase MCP server  |  Develop with AI assistance"
