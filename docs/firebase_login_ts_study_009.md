# 第09章：エラー設計①：Firebaseエラーを人間の言葉に翻訳する😇

この章は、**「エラーが出たときにユーザーが次に何をすればいいか分かる」**ようにする回だよ💪✨
やることはシンプルで、**`auth/xxxx` みたいなエラーコードを、日本語の“やさしい文”に変換する辞書**を作ります📘

---

## この章のゴール🎯

* `catch (e)` で拾ったエラーから **`error.code` を見て**、表示する文言を決められる🙂
* **メール列挙保護（Email enumeration protection）**が有効でも破綻しないメッセージ設計にする🛡️
  （有効だと “ユーザー未登録” みたいな細かい情報が返らない/返しにくいことがあるよ、という話）([Firebase][1])
* 「フィールドの赤文字」「画面上部のエラー帯」「再試行できる案内」など、**UIの置き場所もルール化**できる✅

---

## 読む📚（5分でOK）

## 1) “メール列挙保護”でエラーが変わるのを知る🛡️

* メール列挙保護を有効にすると、**エラーが“より曖昧”になる**ことがあるよ（＝攻撃者がメール登録有無を推測しにくくする）([Firebase][1])
* 2023-09-15以降に作ったプロジェクトは、**デフォルトで有効**になっているケースがあるよ（`fetchSignInMethodsForEmail()` が無効化される、など）([Firebase][2])

## 2) エラーコードは “処理する前提” にする🧠

* 公式でも「エラー報告の挙動が変わるから、アプリ側が特定のエラーに依存しないでね」って趣旨が書かれてるよ([Firebase][1])

---

## まず決める：エラーの出し方ルール✨

おすすめの型はこれ👇（迷いが減るやつ！）

1. **入力ミス**（空欄・形式）🧾
   → フィールドの近くに赤文字（例：メール形式が変だよ）
2. **認証失敗系**（メール/パスワード違い等）🔐
   → 画面上部にまとめて1行（例：メールかパスワードが違うよ）
3. **設定ミス**（プロバイダ未有効・ドメイン未許可）🧯
   → ユーザーには「ログイン方法が使えないみたい🙏」、開発者には詳しいログ
4. **通信/一時障害**（ネットワーク・一時制限）🌐
   → 「回線を確認してね」「少し待って再試行してね」

ここで重要ポイント👇
**“ユーザー未登録”を言い当てる文言は、メール列挙保護と相性が悪い**ので、ログイン時は原則 **「メールかパスワードが違う」** に寄せるのが安全🙂🛡️([Firebase][1])

---

## 手を動かす🛠️：エラー翻訳ユーティリティを作る

## Step 1) まずは「Authっぽいエラーか？」判定関数を作る🔎

```ts
// src/lib/authError.ts

export type AuthErrorLike = {
  code?: unknown;
  message?: unknown;
};

export function isAuthErrorLike(e: unknown): e is AuthErrorLike {
  return typeof e === "object" && e !== null && "code" in e;
}

export function getAuthErrorCode(e: unknown): string | null {
  if (!isAuthErrorLike(e)) return null;
  return typeof e.code === "string" ? e.code : null;
}
```

---

## Step 2) “翻訳辞書” を作る📘✨

最初は「よくあるやつ」だけでOK！増やすのは後でいける🙂

```ts
// src/lib/authError.ts

const AUTH_MESSAGE_JA: Record<string, string> = {
  // ✅ 入力/登録系
  "auth/invalid-email": "メールアドレスの形がちょっと変かも！もう一回見てみて🙂",
  "auth/email-already-in-use": "そのメールアドレスは、すでに登録済みみたい！ログインを試してね🙂",
  "auth/weak-password": "パスワードが弱いかも！もう少し長くするか、文字を増やしてみてね🔑",

  // ✅ ログイン失敗（列挙保護があると“ぼかされる”ことがあるので統一寄せ）
  "auth/user-not-found": "メールかパスワードが違うよ🙂（どっちか確認してね）",
  "auth/wrong-password": "メールかパスワードが違うよ🙂（どっちか確認してね）",
  "auth/invalid-credential": "メールかパスワードが違うよ🙂（どっちか確認してね）",
  "auth/invalid-login-credentials": "メールかパスワードが違うよ🙂（どっちか確認してね）",

  // ✅ 状態/制限/通信
  "auth/user-disabled": "このアカウントは無効になっているみたい🙏 サポートに連絡してね。",
  "auth/too-many-requests": "試行回数が多いみたい！少し待ってからもう一回やってみてね⏳",
  "auth/network-request-failed": "通信が不安定かも！回線を確認して、もう一回やってみてね🌐",

  // ✅ Googleログイン（Popup系でよく出る）
  "auth/popup-blocked": "ポップアップがブロックされたみたい！ブラウザの設定を見てみてね🪟",
  "auth/popup-closed-by-user": "ポップアップを閉じちゃったみたい！もう一回押してみて🙂",
  "auth/cancelled-popup-request": "ログイン処理が重なっちゃったみたい！もう一回だけ試してね🙂",

  // ✅ 設定不足（開発中に出がち）
  "auth/operation-not-allowed": "このログイン方法がまだ有効になってないみたい🙏（設定を確認してね）",
  "auth/unauthorized-domain": "このドメインが許可されてないみたい🙏（Authorized domains を確認してね）",
};

export function toFriendlyAuthMessage(e: unknown): string {
  const code = getAuthErrorCode(e);
  if (code && AUTH_MESSAGE_JA[code]) return AUTH_MESSAGE_JA[code];

  // 最後の砦（ユーザー向け）
  return "うまくいかなかったみたい🙏 もう一回試すか、少し時間をおいてね。";
}
```

補足🔍：

* Popup系エラーや `unauthorized-domain` などは、公式のJavaScript API referenceにも “auth/xxxx” として載ってるよ([Firebase][3])
* メール列挙保護を有効にすると、ログイン失敗時に `INVALID_LOGIN_CREDENTIALS` のような形で返る例があるよ（Identity Platform側の例）([Google Cloud Documentation][4])

---

## Step 3) ログイン画面で使う（catchして表示）🚪

例：`setUiError(...)` でバナー表示する感じ。

```tsx
// src/pages/LoginPage.tsx
import { useState } from "react";
import { signInWithEmailAndPassword } from "firebase/auth";
import { auth } from "../lib/firebase";
import { toFriendlyAuthMessage } from "../lib/authError";

export function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [uiError, setUiError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setUiError(null);
    setBusy(true);

    try {
      await signInWithEmailAndPassword(auth, email, password);
      // 成功したら遷移 or close
    } catch (err) {
      // 開発者向けログ（本番では出し方を調整）
      console.error("login failed:", err);

      // ユーザー向けメッセージ
      setUiError(toFriendlyAuthMessage(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div>
      <h1>ログイン🔐</h1>

      {uiError && (
        <div role="alert" style={{ padding: 12, border: "1px solid #ccc" }}>
          {uiError}
        </div>
      )}

      <form onSubmit={onSubmit}>
        <div>
          <label>
            メール📧
            <input value={email} onChange={(e) => setEmail(e.target.value)} />
          </label>
        </div>

        <div>
          <label>
            パスワード🔑
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </label>
        </div>

        <button disabled={busy}>
          {busy ? "ログイン中…⏳" : "ログインする🚪"}
        </button>
      </form>
    </div>
  );
}
```

---

## ミニ課題🎒：エラーを“わざと出して”確認する🧪

次のケースを試して、**表示が期待通りか**チェックしよう🙂

* メールを `aaa` みたいにして送信 → `auth/invalid-email` 想定📧
* パスワード短すぎで登録 → `auth/weak-password` 想定🔑
* 間違ったパスワードでログイン → **「メールかパスワードが違う」** で統一されるか🔐
* ネット切ってログイン → `auth/network-request-failed` 想定🌐
* GoogleログインPopupを手動で閉じる → `auth/popup-closed-by-user` 想定🪟([Firebase][3])

---

## チェック問題✅（3つだけ！）

1. `catch(err)` の `err` から、ユーザー向け表示に使う “キー” は何だった？🔑
2. メール列挙保護が有効だと、ログイン失敗時の文言はどう寄せるのが安全？🛡️([Firebase][1])
3. Popup系エラー（blocked/closed）は、ユーザーに何を案内すると親切？🪟([Firebase][3])

---

## 🤖AIちょい足し（この章でもう使えるやつ）

## Google の Antigravity：辞書の叩き台を作らせる🧠

* 「`auth/invalid-email` とかの文言を“やさしい日本語”で10案」みたいに作らせて、**一番しっくりくるのを採用**すると速いよ🚀([Google Codelabs][5])

## GitHub リポジトリで Gemini CLI：抜け漏れ検査🔎

* 「`catch` のたびに `toFriendlyAuthMessage` が使われてる？」
* 「UIに生の `error.message` 出してない？」
  みたいなレビューが得意✨([Google for Developers][6])

## Firebase AI Logic：文言を“状況に合わせて”言い換え（任意）💬

* 章10で本格的にやるけど、この章の段階でも
  「このエラー文、もっと短くして」
  「中学生にも分かる言い方にして」
  みたいな**言い換え**に使えるよ🙂
  ちなみに最近はAI Logic側で “thinking” の調整やデフォルトモデル変更なども動きがあるから、触るときはモデル設定も意識すると安心🧠([Firebase][7])

---

## おまけ：今日時点の“最新版メモ”📝

* `firebase` npm の最新は **12.9.0**（2026-02-05公開）だよ([npm][8])

---

次の第10章は、いま作った「翻訳」をさらに気持ちよくして、**説明文や補足をAIに作らせてUXを底上げ**していく感じになるよ🤖✨

[1]: https://firebase.google.com/docs/auth/web/password-auth "Authenticate with Firebase using Password-Based Accounts using Javascript"
[2]: https://firebase.google.com/docs/auth/web/email-link-auth "Authenticate with Firebase Using Email Link in JavaScript"
[3]: https://firebase.google.com/docs/reference/js/v8/firebase.auth.Auth?utm_source=chatgpt.com "Auth | JavaScript SDK | Firebase JavaScript API reference"
[4]: https://docs.cloud.google.com/identity-platform/docs/admin/email-enumeration-protection "Enable or disable email enumeration protection  |  Identity Platform  |  Google Cloud Documentation"
[5]: https://codelabs.developers.google.com/getting-started-google-antigravity?utm_source=chatgpt.com "Getting Started with Google Antigravity"
[6]: https://developers.google.com/gemini-code-assist/docs/gemini-cli?utm_source=chatgpt.com "Gemini CLI | Gemini Code Assist"
[7]: https://firebase.google.com/support/release-notes/js?utm_source=chatgpt.com "Firebase JavaScript SDK Release Notes - Google"
[8]: https://www.npmjs.com/package/firebase?utm_source=chatgpt.com "firebase"
