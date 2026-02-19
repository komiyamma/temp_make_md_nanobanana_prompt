# 第11章：Googleログイン：`GoogleAuthProvider`で最短実装🌈

この章でやることはシンプル！
「Googleでログイン」ボタンを押したら、**ポップアップでGoogleログイン → アプリに戻ってログイン完了**まで一気に通します🙂👍
Firebase公式でも、Webはまず **`GoogleAuthProvider`＋`signInWithPopup()`**（または `signInWithRedirect()`）が基本手順として案内されています。([Firebase][1])

---

## ゴール🎯

![Google Login Popup Flow](./picture/firebase_login_ts_study_011_01_popup_flow.png)

* Googleボタンでログインできる✅
* 失敗時に「次に何をすればいいか」が分かるエラー表示ができる✅
* （おまけ）AIで「やさしい説明文」に言い換えできる✅🤖

---

## 1) 読む📚👀（5分）

* Firebase AuthでのGoogleログイン（Web）の基本手順（Provider作ってPopup/Redirect）([Firebase][1])
* ポップアップがダメな環境向けに、Redirectも用意できる（モバイルはRedirect推奨の記述もあり）([Firebase][1])

---

## 2) 手を動かす🛠️💨（メイン）

## 2-1. Console側の確認🔧（1分）

![Firebase Console Setup](./picture/firebase_login_ts_study_011_02_console_setup.png)

やることは1つだけ：**Authentication → Sign-in method → Google を有効化**。
ここがOFFだと、アプリ側が完璧でも `operation-not-allowed` で止まります😇（後で「つまずき救急箱」に出てきます）

---

## 2-2. Googleログイン関数を作る🧩（まずは“動く最短”）

![Google Auth Code Concept](./picture/firebase_login_ts_study_011_03_code_concept.png)

例：`src/features/auth/signInWithGoogle.ts`

```ts
import { GoogleAuthProvider, signInWithPopup } from "firebase/auth";
import { auth } from "@/lib/firebase"; // 第3章あたりで作った auth を想定

export async function signInWithGooglePopup() {
  const provider = new GoogleAuthProvider();

  // 追加でGoogle APIの権限が必要なら scope を足す（最初は不要でOK）
  // provider.addScope("https://www.googleapis.com/auth/contacts.readonly");

  const result = await signInWithPopup(auth, provider);
  return result.user; // displayName / email / photoURL などが取れる
}
```

`GoogleAuthProvider` を作って `signInWithPopup()` に渡す、これが基本の型です。([Firebase][1])

---

## 2-3. ログイン画面に「Googleでログイン」ボタンを付ける🧼🖱️

![Friendly Error UI](./picture/firebase_login_ts_study_011_04_friendly_error.png)

例：`src/pages/LoginPage.tsx`（構成は自由）

```tsx
import { useState } from "react";
import { signInWithGooglePopup } from "@/features/auth/signInWithGoogle";

type FriendlyError = { title: string; detail?: string };

function toFriendlyAuthError(code?: string): FriendlyError {
  switch (code) {
    case "auth/popup-blocked":
      return { title: "ポップアップがブロックされちゃった💦", detail: "ブラウザの設定でこのサイトのポップアップを許可して、もう一回！" };
    case "auth/popup-closed-by-user":
      return { title: "ログインが途中で閉じられたよ🙂", detail: "もう一度ボタンを押してやり直してね。" };
    case "auth/cancelled-popup-request":
      return { title: "連続クリックでキャンセルされたかも🌀", detail: "ボタン連打を防ぐ（disabled）で直るよ。" };
    case "auth/operation-not-allowed":
      return { title: "Googleログインが無効っぽい🥲", detail: "Firebase ConsoleでGoogleプロバイダがONか確認してね。" };
    case "auth/unauthorized-domain":
      return { title: "このドメインが許可されてないよ🚫", detail: "Authの「Authorized domains」に追加してね。" };
    case "auth/network-request-failed":
      return { title: "通信が不安定かも📶", detail: "Wi-Fi/プロキシ/VPNを見直して再トライ！" };
    default:
      return { title: "ログインに失敗したよ😵", detail: "少し待ってもう一度やってみてね。" };
  }
}

export default function LoginPage() {
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<FriendlyError | null>(null);

  const onGoogle = async () => {
    setErr(null);
    setLoading(true);
    try {
      const user = await signInWithGooglePopup();
      // ここで「ログインできた！」表示や、マイページへ遷移など
      console.log("Signed in:", user.uid, user.displayName, user.email);
    } catch (e: any) {
      const code = e?.code as string | undefined;
      setErr(toFriendlyAuthError(code));
      console.warn("Google sign-in failed:", e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 420, margin: "40px auto", padding: 16 }}>
      <h1>ログイン🔐</h1>

      <button
        onClick={onGoogle}
        disabled={loading}
        style={{ width: "100%", padding: 12, marginTop: 12 }}
      >
        {loading ? "ログイン中…⏳" : "Googleでログイン🌈"}
      </button>

      {err && (
        <div style={{ marginTop: 12, padding: 12, border: "1px solid #ddd" }}>
          <div style={{ fontWeight: 700 }}>{err.title}</div>
          {err.detail && <div style={{ marginTop: 6 }}>{err.detail}</div>}
        </div>
      )}
    </div>
  );
}
```

ポイントはこれだけ👇

* **連打防止（`disabled`）** → `cancelled-popup-request` が激減🧯
* **エラーはコードで分岐** → 人間向けの案内に変換🙂

---

## 3) つまずき救急箱🚑🧠（ここ超大事）

![Troubleshooting Trio](./picture/firebase_login_ts_study_011_05_troubleshooting.png)

## ✅ 1) ポップアップが出ない（`auth/popup-blocked`）

* ブラウザがポップアップをブロックしてる可能性大
  → **サイトごと許可**して再トライ💡

## ✅ 2) `auth/unauthorized-domain`

* 本番URLやプレビューURLを使ったときに出やすい
  → Firebase Consoleの **Authorized domains** を確認👀
  （独自ドメイン運用やauth handler周りの話にも繋がるやつ！）([Firebase][2])

## ✅ 3) モバイル/一部環境でポップアップが不安定

Firebase公式でも **モバイルはRedirectが推奨**と書かれています。([Firebase][1])
次章（第12章）で「Popup/Redirectの使い分け」をちゃんと固めよう🙂

---

## 4) ミニ課題🎒✨（10分）

1. Googleログイン成功後に、マイページで

   * `displayName`
   * `email`
   * `photoURL`
     を表示👤📸
2. ログイン画面に「ログインできないとき」リンクを作って、

   * ポップアップ許可
   * 通信確認
     を案内するテキストを書く📝

---

## 5) チェック✅✅✅

* [ ] Googleボタン → ポップアップ → ログイン完了まで通った
* [ ] ボタン連打しても壊れない（`disabled`が効いてる）
* [ ] 失敗時に、ユーザーが次にやることが表示される
* [ ] `console.log` に `uid` と `email` が出てる

---

## 6) AIでUX強化🤖📝（Firebase AI Logic：やさしい文言に言い換え）

![AI Logic Integration](./picture/firebase_login_ts_study_011_06_ai_logic.png)

「エラー表示はできた。でももっと優しくしたい…」ってときに、**Firebase AI Logic** で“言い換え文”を作らせるのが便利です✨
Web向けSDKは `firebase/ai` を使って `getAI()` → `getGenerativeModel()` → `generateContent()` という流れが公式の手順です。([Firebase][3])

例：エラーコードだけを渡して、短い案内文を作る（※パスワード等は渡さない！）🔒

```ts
import { firebaseApp } from "@/lib/firebase";
import { getAI, getGenerativeModel, GoogleAIBackend } from "firebase/ai";

const ai = getAI(firebaseApp, { backend: new GoogleAIBackend() });
const model = getGenerativeModel(ai, { model: "gemini-2.5-flash" });

export async function explainAuthErrorWithAI(code: string) {
  const prompt =
    `あなたはWebアプリの案内係です。次の認証エラーコードを、` +
    `日本語でやさしく、短く、次の行動が分かるように説明して。\n` +
    `エラーコード: ${code}\n` +
    `条件: 80文字以内、絵文字は1〜2個。`;

  const result = await model.generateContent(prompt);
  return result.response.text();
}
```

これを `toFriendlyAuthError()` のデフォルト分岐で呼ぶと、**“とりあえず意味が伝わる文”**が即席で作れます🙂✨
（AI LogicのWeb向けコード例には `gemini-2.5-flash` などモデル指定も載っています）([Firebase][3])

---

## 7) Antigravity / Gemini CLI の使いどころ🚀🔎

* **Antigravity**：アプリの「Googleログイン実装」を“ミッション化”して、必要ファイル（LoginPage、エラー変換、ボタンUI）をまとめて作らせるのが強いです。([Firebase][4])
* **Gemini CLI**：ターミナルでリポジトリ全体を見ながら、バグ修正・機能追加・テスト改善まで“ReAct＋MCP”で進められる、って位置づけ（Cloud Shellなら追加セットアップなしで使える記述もあり）。([Google Cloud Documentation][5])

おすすめ依頼文（そのまま投げてOK）👇

* 「Googleログインの例外処理が足りないところ、エラーコード観点で洗い出して」🔎
* 「`auth/unauthorized-domain` が出たときの案内を、初心者向けに整えて」📝
* 「ボタン連打で挙動が崩れないように、状態管理を最小変更で直して」🧯

---

## 8) 補足：Googleログイン周辺は“仕様の波”がある🌊（知っておくだけでOK）

![Browser Spec Wave](./picture/firebase_login_ts_study_011_07_browser_wave.png)

Google側のサインイン（特に「Google Sign-In platform library」系）では **FedCM** への移行が進んでいて、ガイドにはタイムラインや影響点が整理されています。([Google for Developers][6])
Firebase Authのこの章のやり方（Provider＋Popup）は別ルートだけど、**ブラウザの制限や挙動変化は今後も起きやすい**ので、動作確認は“たまに”でいいからやっておくと安心です🙂👍

---

次の第12章では、この章で作ったGoogleログインをベースに、**Popup/Redirectの分岐**を“詰まらない形”に仕上げます🧠🚧

[1]: https://firebase.google.com/docs/auth/web/google-signin "Authenticate Using Google with JavaScript  |  Firebase Authentication"
[2]: https://firebase.google.com/docs/auth/web/google-signin?utm_source=chatgpt.com "Authenticate Using Google with JavaScript - Firebase"
[3]: https://firebase.google.com/docs/ai-logic/get-started "Get started with the Gemini API using the Firebase AI Logic SDKs  |  Firebase AI Logic"
[4]: https://firebase.google.com/docs/auth/web/redirect-best-practices "Best practices for using signInWithRedirect on browsers that block third-party storage access  |  Firebase"
[5]: https://docs.cloud.google.com/gemini/docs/codeassist/gemini-cli "Gemini CLI  |  Gemini for Google Cloud  |  Google Cloud Documentation"
[6]: https://developers.google.com/identity/sign-in/web/gsi-with-fedcm?utm_source=chatgpt.com "Google Sign-in with FedCM APIs | Web guides"
