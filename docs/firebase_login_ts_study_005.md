# 第05章：メール登録：サインアップ画面を作る✍️

この章は「メール＋パスワードでユーザーを作る」だけじゃなく、**“気持ちよく登録できる体験”**まで作ります🙂✨
（エラーが分かりやすい／二重送信しない／登録後に「ようこそ🎉」が出る、など！）

---

## 5-1 この章のゴール🎯

![Signup Screen Mockup](./picture/firebase_login_ts_study_005_01_ui_goal.png)

* ✅ サインアップ画面（メール・パスワード）を作る
* ✅ 登録成功・失敗を“人間の言葉”で出せる😇
* ✅ 登録後に「ようこそ🎉」を表示できる
* ✅ “パスワード方針（Password policy）”も意識できる🛡️ ([Google Cloud Documentation][1])

---

## 5-2 まず「読む」📚👀（ここだけ押さえればOK）

* メール/パスワードでユーザーを作る基本：`createUserWithEmailAndPassword` ([Firebase][2])
* ユーザーの表示名などを更新：`updateProfile` ([Firebase][3])
* パスワード方針（6〜30文字など）と、クライアント側での事前チェック：`validatePassword` ([Google Cloud Documentation][1])

---

## 5-3 手を動かす🛠️✨（サインアップ画面を完成させる）

> ここでは「React + TypeScript」前提で、**1ページで完結**する作りにします🙂
> ルーティングはあなたの構成（React Routerなど）に合わせて `SignupPage` を差し込めばOK！

---

## Step 0) コンソール側の確認🔧✅

* Authentication で **メール/パスワード**が有効になってることを確認
  （ここがOFFだと、実装が正しくても失敗します💦） ([Firebase][2])

---

## Step 1) エラーを“日本語に翻訳”する関数を作る🗺️😇

![Error Code Translation](./picture/firebase_login_ts_study_005_02_error_translation.png)

```ts
// src/features/auth/authErrorJa.ts
export function authErrorJa(code: string): string {
  switch (code) {
    case "auth/email-already-in-use":
      return "そのメールアドレスは、すでに使われています🙂";
    case "auth/invalid-email":
      return "メールアドレスの形式が変かも？もう一度チェックしてね📧";
    case "auth/weak-password":
      return "パスワードが弱いみたい💦 もう少し長くするか、文字の種類を増やしてみてね🔐";
    case "auth/network-request-failed":
      return "通信に失敗したっぽい…！Wi-Fiや回線を確認して、もう一回やってみてね📶";
    case "auth/too-many-requests":
      return "試行回数が多すぎるみたい😵 少し待ってから試してね⏳";
    default:
      return "登録に失敗しちゃった…💦 もう一度試してね（ダメなら時間をおいて再挑戦）";
  }
}
```

---

## Step 2) サインアップ画面（UI＋登録処理）を作る✍️🔑

![React Form State](./picture/firebase_login_ts_study_005_03_form_state.png)

ポイントはこれ👇

* 送信中はボタン無効＋文言変更（連打防止）⏳
* パスワード確認（confirm）で事故防止🧯
* 成功したら「ようこそ🎉」表示＋必要なら遷移🚀

```tsx
// src/features/auth/SignupPage.tsx
import { useMemo, useState } from "react";
import { createUserWithEmailAndPassword, updateProfile } from "firebase/auth";
import { auth } from "../firebase"; // あなたの auth export に合わせてね
import { authErrorJa } from "./authErrorJa";

type FormState = {
  email: string;
  password: string;
  confirm: string;
  displayName: string;
};

export function SignupPage() {
  const [form, setForm] = useState<FormState>({
    email: "",
    password: "",
    confirm: "",
    displayName: "",
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string>("");
  const [error, setError] = useState<string>("");

  const canSubmit = useMemo(() => {
    if (!form.email.trim()) return false;
    if (form.password.length < 6) return false; // デフォルト最小は6文字（後で方針強化も可）🛡️
    if (form.password !== form.confirm) return false;
    return true;
  }, [form]);

  const onChange =
    (key: keyof FormState) => (e: React.ChangeEvent<HTMLInputElement>) => {
      setForm((p) => ({ ...p, [key]: e.target.value }));
    };

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setMessage("");

    if (!canSubmit) {
      setError("入力をもう一度チェックしてね🙂（メール・パスワード・確認用パスワード）");
      return;
    }

    setLoading(true);
    try {
      // 1) アカウント作成（成功すると userCredential.user が返る）🔐
      //    新規作成後、そのユーザーでサインイン状態になります🙆‍♂️
      const userCredential = await createUserWithEmailAndPassword(
        auth,
        form.email.trim(),
        form.password
      );

      // 2) ついでに表示名（ニックネーム）も付けると気持ちいい👤✨
      if (form.displayName.trim()) {
        await updateProfile(userCredential.user, {
          displayName: form.displayName.trim(),
        });
      }

      // 3) 成功メッセージ🎉
      const name = form.displayName.trim() || "ユーザー";
      setMessage(`ようこそ ${name} さん🎉 登録できたよ！`);

      // 4) ここでマイページへ遷移してもOK（あなたのルーティングに合わせてね）
      // navigate("/me");
    } catch (err: any) {
      const code = typeof err?.code === "string" ? err.code : "";
      setError(authErrorJa(code));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-md p-4">
      <h1 className="text-2xl font-bold">サインアップ✍️</h1>
      <p className="mt-2 text-sm opacity-80">
        メールとパスワードで登録するよ🙂🔐
      </p>

      <form className="mt-4 space-y-3" onSubmit={onSubmit}>
        <div>
          <label className="text-sm font-medium">ニックネーム（任意）</label>
          <input
            className="mt-1 w-full rounded border p-2"
            value={form.displayName}
            onChange={onChange("displayName")}
            placeholder="例：こみやんま"
            autoComplete="nickname"
          />
        </div>

        <div>
          <label className="text-sm font-medium">メールアドレス</label>
          <input
            className="mt-1 w-full rounded border p-2"
            value={form.email}
            onChange={onChange("email")}
            placeholder="you@example.com"
            autoComplete="email"
            inputMode="email"
          />
        </div>

        <div>
          <label className="text-sm font-medium">パスワード（6文字以上）</label>
          <input
            className="mt-1 w-full rounded border p-2"
            type="password"
            value={form.password}
            onChange={onChange("password")}
            autoComplete="new-password"
          />
        </div>

        <div>
          <label className="text-sm font-medium">パスワード（確認）</label>
          <input
            className="mt-1 w-full rounded border p-2"
            type="password"
            value={form.confirm}
            onChange={onChange("confirm")}
            autoComplete="new-password"
          />
          {form.password && form.confirm && form.password !== form.confirm && (
            <p className="mt-1 text-sm text-red-600">
              パスワードが一致してないよ💦
            </p>
          )}
        </div>

        <button
          className="w-full rounded bg-black px-4 py-2 text-white disabled:opacity-50"
          disabled={loading || !canSubmit}
        >
          {loading ? "登録中…⏳" : "登録する🎉"}
        </button>

        {message && (
          <div className="rounded border border-green-300 bg-green-50 p-3 text-sm">
            {message}
          </div>
        )}
        {error && (
          <div className="rounded border border-red-300 bg-red-50 p-3 text-sm">
            {error}
          </div>
        )}
      </form>
    </div>
  );
}
```

* `createUserWithEmailAndPassword()` はメール/パスワードでユーザーを作り、成功するとユーザー情報（`userCredential.user`）が返ります。([Firebase][2])
* `updateProfile()` で `displayName` などを更新できます。([Firebase][3])

---

## 5-4 「パスワード方針」を1段強くする🛡️🔥（おすすめ）

![Password Policy Enforcement](./picture/firebase_login_ts_study_005_04_password_policy.png)

Firebase/Identity Platform には **Password policy** があり、

* 最小長（6〜30、デフォルト6）
* 大文字/小文字/数字/記号必須
  みたいなルールを強制できます。([Google Cloud Documentation][1])

そしてクライアント側で、送信前に方針チェックもできます（`validatePassword`）。([Google Cloud Documentation][1])

「方針を設定したいけど、ユーザーに優しく案内したい」って時に超便利🙂✨

---

## 5-5 AIでUXをちょい上げ🤖✨（Firebase AI Logic を軽く混ぜる）

![AI UX Helper](./picture/firebase_login_ts_study_005_05_ai_ux.png)

ここは“やりすぎ注意”なんだけど、**登録フォームの説明文**とか**エラーの補足**って、地味に大事なんだよね🙂
そこで **Firebase AI Logic** を使って、例えば👇を作ると気持ちいいです✨

* 「安全なパスワードの作り方」をワンクリックで説明💡
* `auth/weak-password` の時に、やさしい言い換え文を生成📝

Firebase AI Logic は Gemini/Imagen をアプリから扱えるようにする仕組みです。([Firebase][4])
※モデル周りは更新が速いので、ドキュメントの “Models” も一度目を通すのがおすすめ（特にモデル名や移行情報）。([Firebase][4])

> ⚠️ パスワードそのものをAIに送らないでね！
> 送るのは「エラーコード」や「一般的な説明の依頼」くらいが安全🙆‍♂️

---

## 5-6 Gemini CLI / Antigravity で爆速にする🚀🤝

![Rapid Development with AI](./picture/firebase_login_ts_study_005_06_gemini_workflow.png)

## Gemini CLI で「叩き台」を一気に作る🧠⚡

Gemini CLI は Node.js が必要で、インストール手順が用意されています。([GitHub][5])
（プロジェクト全体を見て、`SignupPage` を生成→あなたが微調整、が速い！）

たとえば依頼文はこんな感じ👇（コピペOK）

```text
React+TypeScript のアプリに SignupPage を追加したい。
要件：email/password/confirm/displayName、二重送信防止、成功時「ようこそ🎉」表示、
失敗時は Firebase Auth のエラーコードを日本語で表示する関数を用意。
Tailwindのクラスで最低限整える。
```

## Antigravity で「ページ丸ごと組み立て」🧱🤖

UI・フォーム・エラーハンドリングの“型”を作るのが得意なので、
「SignupPage と authErrorJa を生成して、既存ルーティングに組み込む」みたいに丸投げ→レビューが楽です🙂✨
（Firebase周辺のAI支援やプロンプト集も整備されています）

---

## 5-7 ミニ課題🎒✅（3つだけ！）

1. 🎉 登録成功時に「ようこそ〜」を表示
2. 👤 `displayName` を保存（`updateProfile`）
3. 🔁 ログイン画面に「新規登録はこちら」リンクを付ける（導線づくり）

---

## 5-8 チェックリスト✅🧾

* [ ] Console の Authentication にユーザーが増えた👀
* [ ] パスワード不一致で登録できない（ちゃんと止まる）🧯
* [ ] 送信中にボタンが無効化される（連打しても増えない）⏳
* [ ] `auth/email-already-in-use` が分かりやすく出る🙂
* [ ] 「ようこそ🎉」が出る✨

---

## 5-9 よくある詰まりポイント🪤（先に潰す！）

* **短時間に作りまくって弾かれる**：新規登録は過剰な作成を防ぐ制限がかかることがあります（テスト時は落ち着いて🙂）([Firebase][2])
* **`auth/operation-not-allowed`**：メール/パスワードが有効化されてない可能性大（Step0へ🔁）([Firebase][2])

---

次の章（第6章）は、このサインアップで作ったアカウントで **ログイン/ログアウトを通して“認証の背骨”を完成**させます🚪🦴✨

[1]: https://docs.cloud.google.com/identity-platform/docs/password-policy "Enable, disable, and use password policies  |  Identity Platform  |  Google Cloud Documentation"
[2]: https://firebase.google.com/docs/auth/web/password-auth "Authenticate with Firebase using Password-Based Accounts using Javascript"
[3]: https://firebase.google.com/docs/auth/web/manage-users "Manage Users in Firebase"
[4]: https://firebase.google.com/docs/ai-logic/get-started "Get started with the Gemini API using the Firebase AI Logic SDKs  |  Firebase AI Logic"
[5]: https://raw.githubusercontent.com/google-gemini/gemini-cli/refs/heads/main/docs/get-started/installation.md "raw.githubusercontent.com"
