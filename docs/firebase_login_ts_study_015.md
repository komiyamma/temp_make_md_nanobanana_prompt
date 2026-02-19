# 第15章：セッション保持：Persistence（local/session/none）を選べるようにする💾

この章は「ログインが消える/残りすぎる」問題を、ちゃんとコントロールできるようになる回だよ🙂✨
**“どの端末で、どれくらいログイン状態を残す？”** を選べるようにして、認証の完成度をグッと上げよう💪

---

## 読む📚👀（まずはイメージ）

![Persistence Types](./picture/firebase_login_ts_study_015_01_persistence_types.png)

Webアプリの認証は、基本的に「ブラウザを閉じてもログイン状態を残す（＝便利）」がデフォルト。だけど、共有PCとかだと危ないよね😇
そこで **Persistence（保持方式）** を選べるようにする、って話！ ([Firebase][1])

保持方式は3つ👇 ([Firebase][1])

* **local（LOCAL）**：ブラウザを閉じても残る💾（明示的にログアウトしない限り残る）
* **session（SESSION）**：そのタブ/ウィンドウを閉じたら消える🧼
* **none（NONE）**：メモリだけ（リロードで消える）🫥

そして重要ポイント：
**何も指定しなければ、ブラウザでは default = local** になるよ🧠 ([Firebase][1])

---

## 手を動かす🛠️✨（やることはシンプル）

目標はこれ👇
✅ ログイン画面に「保持のしかた」を付ける
✅ ログイン処理の直前で `setPersistence()` を呼ぶ
✅ 事故りやすい罠（タブ・初期化・redirect）を避ける

---

## 1) 保持方式の“選択肢”を作る🧩🎛️

まず、保持方式をまとめるユーティリティを用意しよう（TypeScript）👇

```ts
// authPersistence.ts
import type { Auth } from "firebase/auth";
import {
  setPersistence,
  browserLocalPersistence,
  browserSessionPersistence,
  inMemoryPersistence,
} from "firebase/auth";

export type PersistenceMode = "local" | "session" | "none";

export async function applyPersistence(auth: Auth, mode: PersistenceMode) {
  switch (mode) {
    case "session":
      return setPersistence(auth, browserSessionPersistence);
    case "none":
      return setPersistence(auth, inMemoryPersistence);
    case "local":
    default:
      return setPersistence(auth, browserLocalPersistence);
  }
}
```

`setPersistence()` は「今のセッション」と「これからのサインイン」に効くし、**ストレージ間のコピーが終わるまで Promise が解決しない**よ🧠✨（だから `await` 推奨） ([Firebase][1])

---

## 2) ログイン直前に `applyPersistence()` → ログイン実行🚪🔐

![Implementation Flow](./picture/firebase_login_ts_study_015_02_flow_diagram.png)

## メールログイン版📧

```ts
import { signInWithEmailAndPassword } from "firebase/auth";
import { auth } from "./firebase"; // 既に作ってある想定
import { applyPersistence, type PersistenceMode } from "./authPersistence";

export async function loginWithEmail(
  email: string,
  password: string,
  mode: PersistenceMode
) {
  await applyPersistence(auth, mode);
  return signInWithEmailAndPassword(auth, email, password);
}
```

## Googleログイン（Popup）版🌈

```ts
import { GoogleAuthProvider, signInWithPopup } from "firebase/auth";
import { auth } from "./firebase";
import { applyPersistence, type PersistenceMode } from "./authPersistence";

export async function loginWithGooglePopup(mode: PersistenceMode) {
  await applyPersistence(auth, mode);
  const provider = new GoogleAuthProvider();
  return signInWithPopup(auth, provider);
}
```

---

## 3) ログイン画面に「保持のしかた（Remember me）」を追加🖥️🧷

![Login UI with Persistence](./picture/firebase_login_ts_study_015_03_login_ui.png)

ログイン画面でこういうラジオを出すのが分かりやすい🙂✨
（選んだ値は `localStorage` に保存して、次回も同じ選択にする）

```tsx
import { useEffect, useState } from "react";
import type { PersistenceMode } from "./authPersistence";
import { loginWithEmail, loginWithGooglePopup } from "./loginActions";

const KEY = "auth:persistence";

function loadMode(): PersistenceMode {
  const v = localStorage.getItem(KEY);
  if (v === "local" || v === "session" || v === "none") return v;
  return "local";
}

export function LoginForm() {
  const [mode, setMode] = useState<PersistenceMode>("local");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  useEffect(() => {
    setMode(loadMode());
  }, []);

  function updateMode(m: PersistenceMode) {
    setMode(m);
    localStorage.setItem(KEY, m);
  }

  return (
    <div>
      <h2>ログイン🔐</h2>

      <fieldset>
        <legend>ログイン状態の保持💾</legend>

        <label>
          <input
            type="radio"
            name="persist"
            checked={mode === "local"}
            onChange={() => updateMode("local")}
          />
          このPCではログインを維持（おすすめ）
        </label>

        <label>
          <input
            type="radio"
            name="persist"
            checked={mode === "session"}
            onChange={() => updateMode("session")}
          />
          共有PCモード（閉じたら消える）
        </label>

        <label>
          <input
            type="radio"
            name="persist"
            checked={mode === "none"}
            onChange={() => updateMode("none")}
          />
          超安全モード（リロードで消える）
        </label>
      </fieldset>

      <button onClick={() => loginWithEmail(email, password, mode)}>
        メールでログイン📧
      </button>

      <button onClick={() => loginWithGooglePopup(mode)}>
        Googleでログイン🌈
      </button>
    </div>
  );
}
```

---

## つまずきポイント集😵‍💫➡️🙂（ここ超大事）

## A) “起動時に毎回 setPersistence(local)” はやりがち事故💥

![Init Overwrite Trap](./picture/firebase_login_ts_study_015_04_init_trap.png)

`local` がデフォルトだからといって、アプリ起動のたびに **明示的に `setPersistence(browserLocalPersistence)` を呼ぶ**と、状況によっては **既存の local セッションが消える**報告があるよ😇 ([GitHub][2])

おすすめ運用ルール👇

* ✅ **ログイン直前にだけ** `setPersistence()`
* ✅ 起動時は `onAuthStateChanged` で復元されるのを待つ（前章の背骨）
* ⚠️ “毎回initで固定” は避ける（特に複数タブで痛い） ([GitHub][2])

## B) タブ挙動：local は“同期”、session/none は“別人”になれる🧠🪟

![Tab Synchronization](./picture/firebase_login_ts_study_015_05_tab_behavior.png)

Firebase公式が期待挙動をはっきり書いてる👇 ([Firebase][1])

* session/none：タブごとに別ユーザーでログインできる（お互い見えない）
* local：タブ間で同期される
* local→session/none に切り替えると、**他タブがログアウト**され得る

だから「共有PCモード（session）」は、**“そのタブだけ”で完結するログイン**にしたい時に強い👍

## C) Redirect を使う時の注意（上書き問題）🔁🧠

![Redirect Persistence Risk](./picture/firebase_login_ts_study_015_06_redirect_risk.png)

`signInWithRedirect()` は **“呼んだ時点の persistence を保持して、OAuth完了時に適用”**する挙動が基本。
でも、**戻ってきたページで `setPersistence()` を呼ぶと、保持してた設定を上書きする**こともあるよ⚠️ ([Firebase][1])

👉 ルール：Redirect 使うなら **「どのページで persistence を決めるか」**を固定しよう🙂

---

## ミニ課題🎯🧪

**「共有PCモード」**をちょい親切にしよう✨

* `mode === "session"` のときだけ、ログイン画面に注意バナーを表示

  * 例：「このモードはウィンドウを閉じるとログインが消えるよ🧼」
* さらに余裕あれば：ログイン後のマイページにも、現在のモードを表示🪪

---

## チェック✅✅✅（自分で動作確認）

次のテストをやれば、Persistence の理解が一気に固まるよ💪

* local：ログイン → ブラウザ終了 → 再起動 → まだログイン中✅
* session：ログイン → タブ閉じる → 開き直し → ログアウト状態✅
* none：ログイン → F5（リロード） → ログアウト状態✅
* 追加：local でログイン中に別タブを開いた時、状態が同期される✅ ([Firebase][1])

---

## AIでUX強化🤖💬（迷った人を助けるボタン）

![AI Persistence Advisor](./picture/firebase_login_ts_study_015_07_ai_helper.png)

ここで Firebase の **AI Logic（Gemini）** を混ぜると、体験がやさしくなる☺️✨
例：「どれ選べばいい？」ボタンを押すと、状況に合わせて提案してくれる👍 ([Firebase][3])

```ts
// aiSuggest.ts（イメージ）
import { getAI, getGenerativeModel, GoogleAIBackend } from "firebase/ai";
import { app } from "./firebaseApp";

const ai = getAI(app, { backend: new GoogleAIBackend() });
const model = getGenerativeModel(ai, { model: "gemini-2.5-flash" });

export async function suggestPersistence(sharedPc: boolean) {
  const prompt = `
あなたはWebアプリの先生です。
ログイン状態の保持方式を、初心者にもわかる言葉でおすすめして。
前提：sharedPc=${sharedPc}
候補：local/session/none
最後に「おすすめ：○○」を1行で出して。
  `.trim();

  const res = await model.generateContent(prompt);
  return res.response.text();
}
```

---

## 開発AIの使いどころ🧠⚡（この章と相性よすぎ）

* **Antigravity**：ログイン画面に「保持のしかた」を足すUIを丸ごと作らせる（Mission形式で）🚀 ([Google Codelabs][4])
* **Gemini CLI**：リポジトリ全体を見て、「setPersistence を init で呼んでない？」「redirect戻りで上書きしてない？」をレビューさせる🔎
  （CLIはMCPやツール連携も想定されてるよ） ([Google Cloud Documentation][5])

---

ここまでできたら、**ログインが“勝手に消える/残りすぎる”問題がほぼ消える**はず🙂💪
次の章（ルートガード）に行くと、さらに「アプリとして完成」って感じになるよ🚧✨

[1]: https://firebase.google.com/docs/auth/web/auth-state-persistence "Authentication State Persistence  |  Firebase"
[2]: https://github.com/firebase/firebase-js-sdk/issues/9319 "auth.setPersistence(browserLocalPersistence) is not idempotent: wipes previous browser local storage · Issue #9319 · firebase/firebase-js-sdk · GitHub"
[3]: https://firebase.google.com/docs/ai-logic/generate-text "Generate text using the Gemini API  |  Firebase AI Logic"
[4]: https://codelabs.developers.google.com/getting-started-google-antigravity?utm_source=chatgpt.com "Getting Started with Google Antigravity"
[5]: https://docs.cloud.google.com/gemini/docs/codeassist/gemini-cli?utm_source=chatgpt.com "Gemini CLI | Gemini for Google Cloud"
