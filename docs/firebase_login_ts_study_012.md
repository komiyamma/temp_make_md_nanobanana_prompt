# 第12章：Popup/Redirectの使い分け：詰まりどころ回避の知恵🧠

この章では、**Googleログインを「Popup基本＋Redirectも備える」**にして、環境差で詰まらない構成にします😌🌈
（特に最近は、ブラウザの**Cookie/ストレージ制限**が強くなってきてるので、ここを押さえると安心度が跳ねます🛡️）

---

## 0) この章のゴール🎯✨

* **Popup** と **Redirect** の違いが、ふんわりじゃなく判断できる🙂📌
* クリック1つで **Popupを試してダメならRedirectへ**…みたいな“強い導線”が作れる💪🚪
* Redirect時に必須の **戻り処理（getRedirectResult）** を実装できる🔁✅

---

## 1) Popup と Redirect、なにが違うの？🤔🪟➡️

![Popup vs Redirect](./picture/firebase_login_ts_study_012_01_popup_vs_redirect.png)

## Popup（signInWithPopup）🪟

* 画面はそのまま、別ウィンドウでログイン → 戻ってくる✨
* **WindowsのPCブラウザ**だと成功率が高い👍
* ただし、**ポップアップブロック**されることがある😇（企業PC設定とか、ブラウザ設定とか）

## Redirect（signInWithRedirect）➡️

* 今のページからログインページへ移動 → 終わったら戻ってくる🔁
* **モバイルや、ポップアップが厳しい環境**で強い💪
* ただし注意：Firebase AuthのRedirectは内部で **cross-origin iframe** を使う都合があり、**第三者ストレージ（3rd-party storage）をブロックするブラウザ**だとハマることがある⚠️ ([Firebase][5])
* そして **2024-06-24以降、Chrome(M115+)でも“対策オプションの実装が必要”** という扱いになっています（Firefox 109+ / Safari 16.1+ はそれ以前から要対策）📅⚠️ ([Firebase][5])

---

## 2) 迷ったらこの方針でOK🙆‍♂️🧭

![Fallback Strategy](./picture/firebase_login_ts_study_012_02_fallback_strategy.png)

* **基本はPopup**（PCならこれが一番ラク）🪟✨
* **Popupが無理なときだけRedirectへ**（逃げ道として用意）➡️🛟
* Redirectを“ちゃんと動かす”には、Firebase公式の **Option 1〜5 のどれか**を入れる必要がある🧰 ([Firebase][5])

  * Firebase Hosting を `firebaseapp.com` サブドメインで使ってるなら **影響なし**（対策不要）🆗 ([Firebase][5])
  * Hostingの **カスタムドメイン** や `web.app` サブドメインなら **Option 1 推奨**🧩 ([Firebase][5])
  * Firebase以外でホストするなら **Option 2〜5** を検討🧠 ([Firebase][5])

---

## 3) 手を動かす①：Popup→ダメならRedirect の関数を作る🛠️😎

ここがこの章のコアです🔥
UI側は「Googleでログイン」ボタンを押すだけでOKにします🎛️✨

## 3-1) Firebase初期化（例）🧱

```ts
// src/lib/firebase.ts
import { initializeApp } from "firebase/app";
import { getAuth, GoogleAuthProvider } from "firebase/auth";

const firebaseConfig = {
  // Viteなら import.meta.env から読んでOK（ここは省略）
};

export const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const googleProvider = new GoogleAuthProvider();
```

---

## 3-2) “賢いGoogleログイン”関数を作る🪄

![Smart Login Logic](./picture/firebase_login_ts_study_012_03_smart_login.png)

```ts
// src/features/auth/signInWithGoogleSmart.ts
import { FirebaseError } from "firebase/app";
import { signInWithPopup, signInWithRedirect } from "firebase/auth";
import { auth, googleProvider } from "@/lib/firebase";

type SmartSignInResult =
  | { kind: "signed-in" }
  | { kind: "redirecting" };

export async function signInWithGoogleSmart(): Promise<SmartSignInResult> {
  try {
    // ✅ 重要：signInWithPopup は「ボタンクリック」などユーザー操作の中で呼ぶ
    await signInWithPopup(auth, googleProvider);
    return { kind: "signed-in" };
  } catch (err) {
    // Popupがブロック/閉じられた系なら Redirectへ逃がす
    if (isPopupTrouble(err)) {
      await signInWithRedirect(auth, googleProvider);
      // ここで画面遷移が起きる（戻り処理は後で getRedirectResult で拾う）
      return { kind: "redirecting" };
    }
    throw err;
  }
}

function isPopupTrouble(err: unknown): boolean {
  if (!(err instanceof FirebaseError)) return false;

  // よくある「Popupが使えない」系
  return [
    "auth/popup-blocked",
    "auth/popup-closed-by-user",
    "auth/cancelled-popup-request",
  ].includes(err.code);
}
```

---

## 3-3) ボタンにつなぐ（React）🖱️🌈

```tsx
// src/components/GoogleSignInButton.tsx
import { useState } from "react";
import { signInWithGoogleSmart } from "@/features/auth/signInWithGoogleSmart";

export function GoogleSignInButton() {
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);

  return (
    <div>
      <button
        disabled={busy}
        onClick={async () => {
          setBusy(true);
          setMsg(null);
          try {
            const r = await signInWithGoogleSmart();
            if (r.kind === "redirecting") {
              setMsg("ポップアップが難しそうだから、画面移動でログインするね🙂➡️");
            }
          } catch (e) {
            setMsg("ログイン失敗…🥲（次の章でエラー翻訳を強化するよ）");
          } finally {
            setBusy(false);
          }
        }}
      >
        {busy ? "ログイン中…⏳" : "Googleでログイン🌈"}
      </button>

      {msg && <p style={{ marginTop: 8 }}>{msg}</p>}
    </div>
  );
}
```

---

## 4) 手を動かす②：Redirectの“戻り処理”を入れる🔁✅

![Redirect Return Handling](./picture/firebase_login_ts_study_012_04_redirect_return.png)

Redirectは **戻ってきたあと** に結果を拾わないと「なんか起きたけど分からん😇」になりがちです。

## 4-1) AuthProvider（または起動時のどこか）で getRedirectResult を呼ぶ🧠

ポイント：Firebase JS SDKは、Redirect利用時に **onAuthStateChanged が getRedirectResult の解決を待つ**挙動になっています（Observerが二重発火しにくい）🧯 ([Firebase][6])
それでも、**エラー表示やログのために getRedirectResult を自分でも呼ぶ**のが実務ではラクです🙂

```tsx
// src/features/auth/AuthProvider.tsx（例）
import { createContext, useEffect, useState } from "react";
import { FirebaseError } from "firebase/app";
import { auth } from "@/lib/firebase";
import { onAuthStateChanged, getRedirectResult, User } from "firebase/auth";

export const AuthContext = createContext<{
  user: User | null;
  loading: boolean;
  authError: string | null;
}>({ user: null, loading: true, authError: null });

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [authError, setAuthError] = useState<string | null>(null);

  useEffect(() => {
    const unsub = onAuthStateChanged(auth, (u) => {
      setUser(u);
      setLoading(false);
    });

    // Redirect戻りの結果を拾う（無ければ null で終わる）
    (async () => {
      try {
        await getRedirectResult(auth);
      } catch (e) {
        const msg =
          e instanceof FirebaseError ? `${e.code}` : "redirect error";
        setAuthError(`Redirectログインでエラー😵: ${msg}`);
      }
    })();

    return () => unsub();
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading, authError }}>
      {children}
    </AuthContext.Provider>
  );
}
```

---

## 5) Redirectが動かない系の“現代の罠”🕳️🧨

![Redirect Cookie Trap](./picture/firebase_login_ts_study_012_05_cookie_trap.png)

## 5-1) ブラウザのストレージ制限でRedirectが詰まることがある🍪🚫

Firebase公式が「redirect sign-in をスムーズにするため cross-origin iframe を使うが、第三者ストレージをブロックするブラウザでは動かない」と明記しています⚠️ ([Firebase][5])

さらに重要：
**2024-06-24以降、Chrome M115+ でも“Option実装が必須”**扱いです📅⚠️ ([Firebase][5])

なので対策方針はこう👇

* `firebaseapp.com` サブドメインの Hosting で運用してる → **そのままでOK**🆗 ([Firebase][5])
* Hostingのカスタムドメイン / `web.app` → **Option 1 推奨**🧩 ([Firebase][5])
* Firebase以外でホスト → **Option 2〜5** を検討（難しめだけど、回避策はある）🧰 ([Firebase][5])

この章の結論としては、**まずPopupを基本にして、Redirectは“ちゃんと対策できる前提で”逃げ道にする**のが事故りにくいです🙂🛡️

---

## 6) AIでUXを一段やさしくする🤖💬✨（Firebase AI Logic）

「ポップアップがブロックされた」「Redirectで詰まった」みたいな時に、ユーザーへ出す文言を **やさしく説明**できると神です😇✨

Firebase AI LogicのWeb例では、`firebase/ai` から `getAI` / `getGenerativeModel` を使う形が載っています📌 ([Firebase][7])
あと、**Gemini 2.0 Flash/Flash-Lite が 2026-03-31 に廃止予定**なので、モデル名は新しめに寄せるのが安全です🧯 ([Firebase][7])

## 6-1) “エラー説明をAIに作らせる”関数（例）📝

![AI Trouble Explainer](./picture/firebase_login_ts_study_012_06_ai_explainer.png)

```ts
// src/features/ai/explainAuthTrouble.ts
import { getAI, getGenerativeModel, GoogleAIBackend } from "firebase/ai";
import { app } from "@/lib/firebase";

const ai = getAI(app, { backend: new GoogleAIBackend() });

// ✅ 例：軽量でUI向き（モデルは運用で差し替えしやすくするのが吉）
const model = getGenerativeModel(ai, { model: "gemini-2.5-flash-lite" });

export async function explainAuthTrouble(params: {
  code?: string;
  situation: string;
}): Promise<string> {
  const prompt = [
    "あなたはWebアプリのサポート係です。",
    "次の状況を、初心者にも分かるように、短く、次の行動が分かる文章で説明して。",
    "・難しい用語は避ける",
    "・3行以内",
    "",
    `状況: ${params.situation}`,
    params.code ? `エラーコード: ${params.code}` : "",
  ].join("\n");

  const result = await model.generateContent(prompt);
  return result.response.text() ?? "うまく説明できなかった…🥲";
}
```

※本番だと、モデル名をアプリに埋め打ちせず **Remote Configで切り替え**できるようにするのが推奨されています📌 ([Firebase][7])

---

## 7) Antigravity / Gemini CLI で“詰まりどころ”を潰す🧑‍💻🧠🚀

![Antigravity Smart Login Mission](./picture/firebase_login_ts_study_012_07_antigravity_mission.png)

* **Google Antigravity**は「agentic IDE」として、調査→実装→テスト生成まで流れで支援する、という説明があります🤖🛠️ ([Google Codelabs][8])

  * 例プロンプト：

    * 「Googleログインを Popup→失敗ならRedirect にして。戻り処理も入れて。エラーは人間向け文にして」🙂✨

* **Gemini CLI**はターミナルで使えるエージェントで、MCPや組み込みツールで修正・調査もできる、という位置づけです🔎🧰 ([Google for Developers][9])

  * 例：

    * 「redirect が発生してるのに getRedirectResult が呼ばれてない箇所ある？」
    * 「auth/popup-blocked を握りつぶしてない？」

---

## 8) ミニ課題🎒✅

1. ログインボタンを押す
2. Popupが成功したら「ログインできた🎉」
3. Popupが失敗したら Redirect に切り替わる（文言も出す）➡️
4. 戻ってきたら getRedirectResult を通して、エラー時は画面に表示😵‍💫

---

## 9) チェック✅🧾

* [ ] `signInWithPopup` は **クリックイベント内**で呼んでる？（これ大事🧠）
* [ ] Popup失敗時に **Redirectへ逃げる**導線がある？🛟
* [ ] `getRedirectResult` を起動時に呼んで、**戻り結果/エラー**を拾えてる？🔁
* [ ] Redirectを本番で使うなら、**Option対策**が必要だと理解できた？（Chrome M115+ は 2024-06-24 以降必須）📅⚠️ ([Firebase][5])
* [ ] AIで「次に何をすればいいか」を短く案内できる？🤖💬 ([Firebase][7])

---

次の章（Cookie制限時代のベストプラクティス）に行くと、Redirect周りの“現代の地雷”をさらに安全に踏み抜けるようになります🛡️🔥

[1]: https://chatgpt.com/c/69923c5e-4bc0-83a9-b83f-d835daf39f10 "第8章 フォームUX"
[2]: https://chatgpt.com/c/6992318f-e864-83ab-87f3-6654dd668356 "第6章 メールログイン"
[3]: https://chatgpt.com/c/69922be6-e828-83a6-8729-e3646a3857e2 "ログイン状態監視実装"
[4]: https://chatgpt.com/c/69923989-d28c-83aa-840b-3b2b98c6eeb8 "第7章 メール運用"
[5]: https://firebase.google.com/docs/auth/web/redirect-best-practices "Best practices for using signInWithRedirect on browsers that block third-party storage access  |  Firebase"
[6]: https://firebase.google.com/support/release-notes/js "Firebase JavaScript SDK Release Notes"
[7]: https://firebase.google.com/docs/ai-logic/get-started "Get started with the Gemini API using the Firebase AI Logic SDKs  |  Firebase AI Logic"
[8]: https://codelabs.developers.google.com/building-with-google-antigravity "Building with Google Antigravity  |  Google Codelabs"
[9]: https://developers.google.com/gemini-code-assist/docs/gemini-cli?hl=ja "Gemini CLI  |  Gemini Code Assist  |  Google for Developers"
