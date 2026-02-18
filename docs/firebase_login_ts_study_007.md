# 第07章：メール運用：確認メール・パスワードリセットを足す📨

この章でやることはシンプルだよ🙂
**「登録したメールが本物か確認する」**＋**「パスワード忘れを救う」**の2本立て！
ここが入ると、アプリが一気に“ちゃんとしてる感”出る✨

---

## 7-0) 今日作るもの（完成イメージ）🧩✨

* ✅ サインアップ直後に **確認メール** を送る📩
* ✅ ログイン後、未確認なら **警告バナー** を出す⚠️

  * 「再送」ボタン🔁
  * 「確認した！」ボタン（状態更新）🔄
* ✅ ログイン画面に **パスワードリセット導線** を追加🔑

  * メール入力 → リセットメール送信📨

（確認メール送信 / リセットメール送信 は Firebase Auth の定番メソッドで実装するよ）([Firebase][1])

---

## 7-1) まず知っておく話（なぜ必要？）🧠

## ✅ 確認メール（Email Verification）があると何がうれしい？✨

* メール打ち間違いのまま登録して、二度とログインできない事故を減らせる🙂
* 「そのメールの持ち主本人だよね？」を最低限チェックできる🔐
* 大事な機能（設定変更・課金・管理画面など）を **“確認済みだけOK”** にできる🚧

Firebase 側は「確認フローを完了した」などの条件でメールを verified とみなすよ、という整理もあるよ([Firebase][2])

## ✅ そして超重要：`emailVerified` は勝手に更新されない😇

ユーザーが別タブ/別端末で確認リンク踏んでも、**いま開いてる画面の `user` は古いまま**になりがち。
だから「確認した！」ボタンで **reload（再取得）** して更新するのが気持ちいい👍
（「ユーザー情報は reload して更新できる」という考え方が公式にもあるよ）([Firebase][2])

---

## 7-2) 実装①：サインアップ直後に確認メールを送る📩✨

サインアップ（`createUserWithEmailAndPassword`）が成功した直後に、確認メールを送るよ。

```ts
// signup.ts（例）
import { auth } from "./firebase";
import {
  createUserWithEmailAndPassword,
  sendEmailVerification,
} from "firebase/auth";

export async function signupWithEmail(email: string, password: string) {
  const cred = await createUserWithEmailAndPassword(auth, email, password);

  // ✅ 登録直後に確認メールを送る
  await sendEmailVerification(cred.user);

  return cred.user;
}
```

`sendEmailVerification()` は「確認メール送る」ための公式手段だよ([Firebase][1])

## よくあるUX（おすすめ）🙂✨

* 送った直後に「送信したよ！受信箱見てね📩（迷惑メールも！）」を出す
* そのままマイページへ行かせてもOKだけど、未確認ならバナーを出して導線を残すのが親切🙆‍♂️

---

## 7-3) 実装②：未確認ユーザーに“やさしい警告バナー”を出す⚠️📌

ログイン後、`user.emailVerified === false` のときだけ表示する小コンポーネントを作るよ。

ポイントは2つ👇

1. **再送**（resend）🔁
2. **確認した！**（reloadして状態更新）🔄

```tsx
// EmailVerificationBanner.tsx（例）
import { useState } from "react";
import { auth } from "./firebase";
import { sendEmailVerification } from "firebase/auth";

export function EmailVerificationBanner() {
  const user = auth.currentUser;
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);

  if (!user) return null;
  if (user.emailVerified) return null;

  const resend = async () => {
    setBusy(true);
    setMsg(null);
    try {
      await sendEmailVerification(user);
      setMsg("確認メールを再送したよ📩 受信箱をチェックしてね🙂");
    } catch (e: any) {
      setMsg("うまく送れなかったかも🥲 しばらく待ってから再挑戦してね！");
    } finally {
      setBusy(false);
    }
  };

  const refreshStatus = async () => {
    setBusy(true);
    setMsg(null);
    try {
      await user.reload(); // ✅ 別タブで確認した反映を取りにいく
      if (user.emailVerified) {
        setMsg("確認できたよ🎉 ありがとう！");
      } else {
        setMsg("まだ未確認みたい🙏 メールのリンクを開いたか確認してね📩");
      }
    } finally {
      setBusy(false);
    }
  };

  return (
    <div style={{ padding: 12, border: "1px solid #ddd", borderRadius: 8 }}>
      <div>⚠️ メールアドレスが未確認だよ！</div>
      <div style={{ marginTop: 8, display: "flex", gap: 8 }}>
        <button onClick={resend} disabled={busy}>再送する🔁</button>
        <button onClick={refreshStatus} disabled={busy}>確認した！🔄</button>
      </div>
      {msg && <div style={{ marginTop: 8 }}>{msg}</div>}
    </div>
  );
}
```

* `sendEmailVerification()` はそのまま再送にも使えるよ([Firebase][1])
* `reload` の発想（別端末/別タブの変更を取り込む）は公式でも説明があるよ([Firebase][2])

> 💡 注意：`auth.currentUser` は「ログイン中のユーザー」だけ。ログアウト状態で再送はできないよ🙂

---

## 7-4) 実装③：パスワードリセット（忘れた人の救済）🔑🛟

ログイン画面に「パスワードを忘れた？」リンクを置いて、メール入力→送信の流れを作るよ📨

```tsx
// ForgotPassword.tsx（例）
import { useState } from "react";
import { auth } from "./firebase";
import { sendPasswordResetEmail } from "firebase/auth";

export function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);

  const submit = async () => {
    setBusy(true);
    setMsg(null);

    try {
      await sendPasswordResetEmail(auth, email);

      // ✅ セキュリティ的に「存在した/しない」を言いすぎないのが無難🙂
      setMsg("もし登録済みのメールなら、リセット用メールを送ったよ📩");
    } catch (e: any) {
      // ここも詳細を出しすぎないのが無難（アカウント列挙対策）
      setMsg("送信できなかったかも🥲 メール形式や入力を確認してね！");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div style={{ padding: 12, border: "1px solid #ddd", borderRadius: 8 }}>
      <div>🔑 パスワードリセット</div>
      <input
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="メールアドレス"
        style={{ marginTop: 8, width: "100%" }}
      />
      <button onClick={submit} disabled={busy} style={{ marginTop: 8 }}>
        リセットメールを送る📨
      </button>
      {msg && <div style={{ marginTop: 8 }}>{msg}</div>}
    </div>
  );
}
```

`sendPasswordResetEmail()` も公式の定番メソッドだよ([Firebase][1])

---

## 7-5) メールのリンク先（continue URL）と「Authorized domains」罠🧨

## ✅ “リンクを踏んだあと、アプリに戻ってきてほしい”問題

確認メールやリセットメールは、デフォルトの処理ページ（Firebase の用意したページ）を経由して進むけど、
**最後に自分のアプリへ戻すURL（continue URL）** を設定できるよ。
このあたりは「メールアクションに state / continue URL を渡す」系の公式ガイドにまとまってる([Firebase][3])

## ✅ そして初心者が一番ハマる：Authorized domains に `localhost` が無い😇

2025年4月28日以降に作った Firebase プロジェクトは、**`localhost` が最初から許可されない**仕様になった、って公式に明記があるよ。([Firebase][3])
なので開発中にメールリンクの挙動がおかしいときは、Console の **Authentication → Settings → Authorized domains** に

* `localhost`
* 本番ドメイン（例：`example.com`）
  を入れてね👍([Firebase][3])

> ✅ 「メールリンクが開くけど、最後に戻ってこない」「エラーになる」系の多くがここ！

---

## 7-6) Consoleでできる“メールの見た目”調整（テンプレ）✉️🎨

Firebase Console の「Email Templates」から、

* 送信者名
* 件名
* 本文（テンプレ範囲）
* アクションURL（リンク先の扱い）
  などを調整できるよ。([Google ヘルプ][4])

「確認メールが味気ない…🥲」ってときは、ここを整えるだけで一気に印象良くなる✨

---

## 7-7) Firebase AI LogicでUXを“やさしく言い換え”する🤖💬

ここは“実装の必須”じゃないけど、体験がかなり良くなるやつ！
**確認メール/リセットメール周りって、ユーザーが不安になりがち**なんだよね😇
そこで、画面の説明文やエラーメッセージを **Gemini に「やさしく短く」整えてもらう**✨

Firebase AI Logic（Web）では、こんな感じで `firebase/ai` を使ってモデルを作れるよ([Firebase][5])

```ts
// ai.ts（例）
import { initializeApp } from "firebase/app";
import { getAI, getGenerativeModel, GoogleAIBackend } from "firebase/ai";

const firebaseApp = initializeApp({ /* ... */ });

// Gemini Developer API backend
const ai = getAI(firebaseApp, { backend: new GoogleAIBackend() });

// 例：軽めで速いモデル
export const model = getGenerativeModel(ai, { model: "gemini-2.5-flash" });
```

## ✅ 例：未確認バナーの説明文をAIに作らせる🙂✨

（UIに表示する短文だけ生成する。メール本文そのものをAIに作らせるのは後回しでもOK👍）

```ts
import { model } from "./ai";

export async function buildFriendlyHint(kind: "verify" | "reset") {
  const prompt =
    kind === "verify"
      ? "メール確認が必要な理由を、やさしい日本語で60文字以内で説明して。絵文字も1つ。"
      : "パスワードリセット手順を、やさしい日本語で60文字以内で説明して。絵文字も1つ。";

  const res = await model.generateContent(prompt);
  return res.response.text();
}
```

## ✅ 2026年の注意：モデル名の“引退”がある⚠️

Firebase AI Logic 側で **Gemini 2.0 Flash / Flash-Lite が 2026-03-31 に retire** 予定、という注意が公式に出てるよ。
だから今から作るなら `gemini-2.5-flash(-lite)` 系を選ぶのが安全🙆‍♂️([Firebase][6])

---

## 7-8) Antigravity / Gemini CLI の使いどころ（時短ハック）🚀🛠️

* **Antigravity**：
  「未確認バナーを作って」「ForgotPasswordコンポーネントを追加して」みたいに、UI単位のミッションにすると速い🏎️([Google Codelabs][7])
* **Gemini CLI**：
  「送信後のメッセージが不親切」「例外握りつぶしてる」みたいな **レビュー** に強い🔎([Google Cloud Documentation][8])

---

## 7-9) つまずき集（ここだけ見ればだいたい助かる）🧯😇

* 📩 **メールが届かない**
  → 迷惑メール、プロモーション、受信拒否、送信元ドメイン設定を確認。テンプレも見直す([Google ヘルプ][4])
* 🌐 **ローカルでリンクが変 / 戻ってこない**
  → Authorized domains に `localhost` を入れる（新規プロジェクトは最初から入ってない）([Firebase][3])
* 🔁 **確認リンク踏んだのにバナーが消えない**
  → `reload()` で状態更新ボタンを用意する（別端末の変更を取り込む）([Firebase][2])
* 🧱 **`too-many-requests` っぽい（送れない）**
  → 連打しないUI（ボタン無効化、クールダウン）を入れる⏳

---

## 7-10) ミニ課題（10〜20分）🎯🔥

## ミニ課題A：未確認ユーザーの“ガード”🚧

* 未確認なら、保護ページに入る前に
  「メール確認してね🙂」画面を出す（入れない or 注意）
* 「確認した！」で reload → OKなら通す✅

## ミニ課題B：ログイン画面に“忘れた”導線🔑

* 「パスワードを忘れた？」を押す
* メール入力 → 送信
* 成功/失敗メッセージをやさしく表示🙂

---

## 7-11) できたかチェック✅✨（自己採点）

* [ ] サインアップ直後に確認メールが送られる📩([Firebase][1])
* [ ] 未確認のときだけバナーが出る⚠️
* [ ] 「再送」「確認した！」（reload）で体験が途切れない🔁🔄([Firebase][2])
* [ ] パスワードリセットが送れる📨([Firebase][1])
* [ ] `localhost` が Authorized domains に入ってる（必要なら）🧨([Firebase][3])
* [ ] AIで説明文が“人間っぽく”なってる🤖✨([Firebase][5])

---

次の章（フォームUXやエラー翻訳）に進むと、ここで作った導線がもっと気持ちよくなるよ😇✨

[1]: https://firebase.google.com/docs/auth/web/manage-users "Manage Users in Firebase"
[2]: https://firebase.google.com/docs/auth/users "Users in Firebase Projects  |  Firebase Authentication"
[3]: https://firebase.google.com/docs/auth/web/passing-state-in-email-actions "Passing State in Email Actions  |  Firebase"
[4]: https://support.google.com/firebase/answer/7000714?hl=en "Customize account management emails and SMS messages - Firebase Help"
[5]: https://firebase.google.com/docs/ai-logic/get-started "Get started with the Gemini API using the Firebase AI Logic SDKs  |  Firebase AI Logic"
[6]: https://firebase.google.com/docs/ai-logic/production-checklist "Production checklist for using Firebase AI Logic  |  Firebase AI Logic"
[7]: https://codelabs.developers.google.com/getting-started-google-antigravity?utm_source=chatgpt.com "Getting Started with Google Antigravity"
[8]: https://docs.cloud.google.com/gemini/docs/codeassist/gemini-cli?utm_source=chatgpt.com "Gemini CLI | Gemini for Google Cloud"
