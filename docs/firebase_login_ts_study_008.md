# 第08章：フォームUX：バリデーション＆“読み込み中”の作法🧼

この章は「ログイン/サインアップは動くけど、なんか雑い…😇」を卒業して、**“気持ちいいフォーム”**に仕上げる回だよ〜！🎉
ポイントは **①入力チェック（バリデーション）** と **②送信中UI（ローディング/二重送信防止）** の2つ✅

ちなみに、`firebase` パッケージは npm 上で **12.9.0（2026-02-05時点）** が最新として表示されてるよ（ちょこちょこ更新されるのでここは要チェック）([npm][1])

---

## この章でできるようになること（ゴール）🏁✨

* 入力ミスをその場で気づける（空欄/形式/桁数）🧾
* 送信中は **ボタン無効＋スピナー** で「今やってる感」⏳
* **二重送信・連打** を確実に止める🛑
* エラー表示が「人間にやさしい」方向へ進む（次章へつながる）😇
* おまけ：AIで「ヒント文」生成してUXを底上げ🤖💬（Firebase AI Logic）

---

## 読む📚（重要な考え方だけ）

* 認証フォームでは、送信前に **パスワード要件などの検証**をしてから `createUserWithEmailAndPassword` に渡す流れが推奨されてるよ（公式がその発想で書いてる）([Firebase][2])
* さらにFirebase側には、短時間にサインアップが集中すると制限がかかる（IP制限的なやつ）ので、**無駄なリクエストを減らすUX**は普通に強い💪([Firebase][2])
* AIの文言生成は **Firebase AI Logic** でアプリから呼べる（Gemini/Imagen）([Firebase][3])

---

## 手を動かす🛠️（実装：バリデーション＋送信中UI）

ここでは「ログイン」と「サインアップ」で共通に使える形にするよ🙂
（すでに第5〜6章でページはある前提で、フォーム部分を強化するイメージ！）

---

## 1) バリデーション方針を決める🧠🧾

最低限これでOK👇

* **email**

  * 空はダメ
  * 形式が変ならダメ（`@` とかドメインとか）
* **password**

  * 空はダメ
  * 文字数は **最低6**（Firebase側で `weak-password` になりやすい）＋できれば自分ルールで8以上推奨🙂
* **confirmPassword（サインアップのみ）**

  * password と一致しないとダメ

「ガチガチにしすぎる」と初心者ユーザーが詰むので、最初は軽めでOK😇
（強いルールは後で足していこう🔥）

---

## 2) まずは“自前で”いく：小さく確実なフォームロジック🧩

## ✅ フォームに必要なstate

* `values`（email/password）
* `touched`（触ったかどうか：最初から赤文字だらけを避ける😇）
* `errors`（項目ごとのエラー文）
* `isSubmitting`（送信中フラグ：UXの心臓🫀）

## ✅ 例：フォーム用ユーティリティ（最小版）

```ts
// src/features/auth/validators.ts
export function validateEmail(email: string): string | null {
  const v = email.trim();
  if (!v) return "メールアドレスが空だよ🙂";
  // ゆるい判定でOK（厳密すぎると逆に事故る）
  const ok = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v);
  if (!ok) return "メールアドレスの形が変かも！例：name@example.com ✉️";
  return null;
}

export function validatePassword(password: string): string | null {
  const v = password;
  if (!v) return "パスワードが空だよ🙂";
  if (v.length < 8) return "パスワードは8文字以上が安心だよ🔒（最低6は欲しい！）";
  return null;
}

export function validateConfirmPassword(password: string, confirm: string): string | null {
  if (!confirm) return "確認用パスワードも入れてね🙂";
  if (password !== confirm) return "パスワードが一致してないよ😵";
  return null;
}
```

---

## 3) 送信中UI：二重送信を“確実に止める”🛑⏳

ポイントは2段構え👇

* **UIで止める**：ボタン `disabled` + 見た目も変える
* **ロジックでも止める**：`isSubmitting` のとき `return`（連打対策の保険🧯）

## ✅ ログインフォーム例（React）

```tsx
// src/features/auth/LoginForm.tsx
import { useMemo, useState } from "react";
import { signInWithEmailAndPassword } from "firebase/auth";
import { auth } from "@/lib/firebase";
import { validateEmail, validatePassword } from "./validators";

type Values = { email: string; password: string; };

export function LoginForm() {
  const [values, setValues] = useState<Values>({ email: "", password: "" });
  const [touched, setTouched] = useState<{ email: boolean; password: boolean; }>({ email: false, password: false });
  const [fieldErrors, setFieldErrors] = useState<{ email?: string; password?: string; }>({});
  const [formError, setFormError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const computedErrors = useMemo(() => {
    const e: typeof fieldErrors = {};
    const emailErr = validateEmail(values.email);
    const passErr = validatePassword(values.password);
    if (emailErr) e.email = emailErr;
    if (passErr) e.password = passErr;
    return e;
  }, [values.email, values.password]);

  const canSubmit = Object.keys(computedErrors).length === 0 && !isSubmitting;

  function onChange<K extends keyof Values>(key: K, v: Values[K]) {
    setValues((p) => ({ ...p, [key]: v }));
    // 入力中に“優しく”消していく（体験が良い🙂）
    setFieldErrors((p) => ({ ...p, [key]: undefined }));
    setFormError(null);
  }

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();

    // 連打対策（ロジック側の保険🧯）
    if (isSubmitting) return;

    // 送信前に全部touchedにして、エラーを見せる
    setTouched({ email: true, password: true });

    const next = computedErrors;
    if (Object.keys(next).length > 0) {
      setFieldErrors(next);
      return;
    }

    setIsSubmitting(true);
    setFormError(null);

    try {
      await signInWithEmailAndPassword(auth, values.email.trim(), values.password);
      // 成功したら遷移する/閉じるなど（この章では省略🙂）
    } catch (err: any) {
      // 第9章で“翻訳”を本格化するけど、ここは最低限でOK
      setFormError("ログインできなかったよ😵 メール/パスワードを確認してね！");
      // デバッグ用に code を出したい場合は console に
      console.log("login error:", err?.code, err?.message);
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form onSubmit={onSubmit} className="space-y-3" aria-busy={isSubmitting}>
      <div>
        <label className="block text-sm font-medium">メールアドレス📧</label>
        <input
          type="email"
          autoComplete="email"
          value={values.email}
          onChange={(e) => onChange("email", e.target.value)}
          onBlur={() => setTouched((p) => ({ ...p, email: true }))}
          className="w-full rounded border px-3 py-2"
          placeholder="name@example.com"
        />
        {(touched.email && (fieldErrors.email ?? computedErrors.email)) && (
          <p className="mt-1 text-sm text-red-600" role="alert">
            {fieldErrors.email ?? computedErrors.email}
          </p>
        )}
      </div>

      <div>
        <label className="block text-sm font-medium">パスワード🔑</label>
        <input
          type="password"
          autoComplete="current-password"
          value={values.password}
          onChange={(e) => onChange("password", e.target.value)}
          onBlur={() => setTouched((p) => ({ ...p, password: true }))}
          className="w-full rounded border px-3 py-2"
          placeholder="8文字以上がおすすめ"
        />
        {(touched.password && (fieldErrors.password ?? computedErrors.password)) && (
          <p className="mt-1 text-sm text-red-600" role="alert">
            {fieldErrors.password ?? computedErrors.password}
          </p>
        )}
      </div>

      {formError && (
        <div className="rounded border border-red-200 bg-red-50 px-3 py-2 text-sm" role="status" aria-live="polite">
          {formError}
        </div>
      )}

      <button
        type="submit"
        disabled={!canSubmit}
        className="w-full rounded bg-black px-3 py-2 text-white disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isSubmitting ? "ログイン中…⏳" : "ログイン🚪"}
      </button>
    </form>
  );
}
```

✅ これで「未入力で送信」「連打」「送信中の不安」あたりが全部消えるよ🎉

---

## 4) サインアップフォームにも同じ作法を入れる✍️🎉

サインアップは「confirmPassword」だけ追加でOK🙂
コツは、**登録ボタン押した瞬間に “全部touch” にして、どこが悪いか一気に見せる**こと！

* confirm不一致は最優先で教える😵
* 成功したら「ようこそ🎉」→（第7章の確認メール導線へ）📨

---

## つまずきポイント集（あるある）🪤😇

* **送信中にボタンだけ無効**にして安心しちゃう
  → JS側でも `if (isSubmitting) return;` を必ず入れる🧯
* `finally` を書き忘れて **永久にスピナー**になる
  → `try/catch/finally` をテンプレ化して体に覚えさせる💪
* エラーを「英語のまま」出しちゃう
  → 第9章で“翻訳辞書”を作るけど、この章では一旦「やさしい固定文」でもOK😇

---

## おまけ：AIで“フォームのヒント文”を自動生成🤖💬✨

Firebase AI Logic は、アプリからGeminiを呼べる仕組みだよ（公式）([Firebase][3])
しかも `firebase/ai` で **Webからの初期化例**が出てる（Firebase公式ブログのコード）([The Firebase Blog][4])

## 方針（超大事）🔐

* **パスワードそのものはAIに送らない**（安全第一🛡️）
* 送るのは「長さ」や「一致してない」みたいな**状態だけ**🙂

## ✅ 例：AIに“やさしい改善ヒント”を作らせる（ボタン押した時だけ）

```ts
// 例：src/features/auth/aiHints.ts
import { getAI, GoogleAIBackend, getGenerativeModel } from "firebase/ai";
import { app } from "@/lib/firebaseApp"; // initializeAppしたやつ

const ai = getAI(app, { backend: new GoogleAIBackend() });
const model = getGenerativeModel(ai, {
  // ここは最小例（細かい設定は後でOK）
  inCloudParams: { model: "gemini-2.5-flash-lite" },
});

export async function buildSignupHint(params: {
  emailOk: boolean;
  passwordLength: number;
  confirmMatch: boolean;
}) {
  const prompt =
`あなたは超やさしい先生です🙂
サインアップフォームで困ってる人に、短いヒントを日本語で3つください。
条件：
- 絵文字を少し入れる
- 叱らない
- セキュリティに配慮（パスワードそのものは聞かない）

状態：
- emailOk: ${params.emailOk}
- passwordLength: ${params.passwordLength}
- confirmMatch: ${params.confirmMatch}
`;

  const res = await model.generateContent(prompt);
  return res.response.text();
}
```

これを「🤖ヒント」ボタンに繋げると、ユーザー体験が一段やさしくなるよ😊
（AI Logic はクライアントから呼べる仕組みとして整理されてる）([Firebase][5])

---

## Antigravity / Gemini CLI の使いどころ🚀🧠

* Antigravity：フォームUIの叩き台（コンポーネント分割＋状態設計）を作らせるのに向いてる✨
* Gemini CLI：リポジトリ全体を見せて「二重送信になりうる箇所」「`finally` 漏れ」みたいな**レビュー**に使うのが強い🔎
  Gemini CLI は Cloud Shell だと追加セットアップ無しで使える案内があるよ([Google Cloud Documentation][6])
  （個人向けのGemini Code Assistの概要も公式にある）([Google for Developers][7])

※ここは“道具”なので、まずは本章のフォームを完成させるのが最優先ね💪🙂

---

## ミニ課題🎯（10〜20分でできる）

1. ログインフォームに以下を追加🧼

* 送信中はボタンが「ログイン中…⏳」になる
* 送信中は入力欄も編集不可にする（任意）
* エリアにエラーメッセージが出る（固定文でOK）

2. サインアップフォームに以下を追加✍️

* confirmPasswordの不一致を表示😵
* 不一致のとき登録ボタンを押しても送らない🛑

3. おまけ（できたら神）🤖

* 「ヒント」ボタンで、AIが改善ポイントを3つ出す（パスワード本文は送らない！）🔐✨

---

## チェック✅（できたらクリア！）

* 空欄のまま送信できない🙂
* 形式が変なメールは、その場で気づける📧
* 送信中は連打しても **1回しか飛ばない**🛑
* 送信中が視覚的に分かる（⏳が出る）
* 失敗しても「次に何をすればいいか」分かる😇（第9章でさらに強化！）

---

次の第9章は、今ちょっと雑にしてる `err.code` を **人間の言葉に翻訳する回**だよ🗺️😇
この第8章がしっかりしてると、エラー設計がめちゃくちゃ作りやすくなる🔥

[1]: https://www.npmjs.com/package/firebase?utm_source=chatgpt.com "firebase"
[2]: https://firebase.google.com/docs/auth/web/password-auth?hl=ja "JavaScript でパスワード ベースのアカウントを使用して Firebase 認証を行う"
[3]: https://firebase.google.com/docs/ai-logic?utm_source=chatgpt.com "Gemini API using Firebase AI Logic - Google"
[4]: https://firebase.blog/posts/2025/10/adding-ai-powered-reviews "AI in action: Adding AI-powered reviews"
[5]: https://firebase.google.com/docs/ai-logic/get-started?utm_source=chatgpt.com "Get started with the Gemini API using the Firebase AI Logic ..."
[6]: https://docs.cloud.google.com/gemini/docs/codeassist/gemini-cli?utm_source=chatgpt.com "Gemini CLI | Gemini for Google Cloud"
[7]: https://developers.google.com/gemini-code-assist/docs/overview?utm_source=chatgpt.com "Gemini Code Assist overview"
