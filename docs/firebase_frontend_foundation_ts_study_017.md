# 第17章：Functionsを呼ぶUIを作る ⚙️📨

この章では「フロントからボタン1発でサーバー処理（Functions）を呼んで、その結果をUIに気持ちよく返す」体験を作ります😆✨
やることはシンプルで、でも実戦力が一気に上がる章です🔥

---

## この章でできるようになること ✅✨

* ボタン → Functions呼び出し → 結果表示（成功/失敗/実行中）を作れる🧠
* 「Callable Functions（推奨）」で CORS 地獄を回避できる🌈
* 失敗時もユーザーに優しいエラーメッセージ設計ができる😇
* Emulator でローカル検証できる🧪
* 次章（AIボタン🤖）にそのまま繋がる土台ができる🏗️

---

## 1) まず結論：UIから呼ぶなら「Callable」が最強 🥇✨

Functionsの呼び方は大きく2つあります👇

## A. Callable Functions（おすすめ）☎️✨

* フロントは `httpsCallable()` で呼ぶだけ
* 認証情報（ログイン情報）も自動で付いてくる
* 返り値やエラーが「アプリ向け」に整っている
* **CallableはデフォルトでCORSが全許可**（必要なら制限もできる）🧩 ([Firebase][1])

## B. HTTP Functions（fetchで叩く）🌐

* `fetch()` で叩ける自由さはある
* でも CORS、認証トークン検証、レスポンス整形…やることが増える😵‍💫
  この教材では「まず勝てる形」を優先して **Callable** でいきます💪✨

---

## 2) 最小のCallable Functionを用意する（サーバー側）🛠️

UIから呼ぶには、呼び先の関数が必要なので、まず“超ミニ”を作ります🙂
（後でここをAI呼び出しに差し替えるだけで、AIボタンが完成します🤖✨）

## 2-1) Functionsのランタイム感（2026）📌

* Cloud Functions for Firebase は **Node.js 22 / 20** が現行サポートの中心（18は非推奨扱い）⚙️ ([Firebase][1])
* Pythonでも書けます（ランタイム例：3.10〜3.13 など）🐍 ([Firebase][2])

> ※UI側は「Callableを呼ぶ」だけなので、サーバーがNodeでもPythonでも基本同じ気持ちです🙂

## 2-2) 関数例：テキスト整形（formatText）🧽✨

```ts
// functions/src/index.ts
import { onCall, HttpsError } from "firebase-functions/v2/https";
import { setGlobalOptions } from "firebase-functions/v2";

// 日本（東京）寄りにすると体感が良いことが多い🗼✨
setGlobalOptions({ region: "asia-northeast1" });

// 入力: { text: string }
// 出力: { text: string }
export const formatText = onCall(async (request) => {
  const text = request.data?.text;

  // ① 入力チェック
  if (typeof text !== "string" || text.trim().length === 0) {
    throw new HttpsError("invalid-argument", "文章が空っぽです🥲", {
      hint: "text に文字列を入れてね",
    });
  }

  // ② 認証チェック（ログイン必須にしたい場合）
  if (!request.auth) {
    throw new HttpsError("unauthenticated", "ログインが必要です🔐");
  }

  // ③ ここが“サーバー処理”（いまは整形だけ）
  const cleaned = text
    .replace(/\r\n/g, "\n")
    .replace(/[ \t]+/g, " ")
    .replace(/\n{3,}/g, "\n\n")
    .trim();

  return { text: cleaned };
});
```

* `request.auth` が取れるのがCallableの超うれしい点です🔐 ([Firebase][1])
* エラーは `HttpsError` を投げると、クライアントに「コード＋メッセージ＋詳細」が届くようになります✨ ([Firebase][1])

> 💡CORSを制限したい場合は `onCall({ cors: [...] }, handler)` も可能です（Callableはデフォルト全許可）。([Firebase][1])

---

## 3) React側：Functions呼び出しを “services化” して綺麗にする 🧼📦

UIコードに `httpsCallable` を直書きすると散らかりがちなので、ここで “接続口” を1箇所に集めます✨

## 3-1) SDKの目安（Web）

Functionsの公式ガイド例では `firebase@12.9.0` が示されています📦 ([Firebase][1])

## 3-2) `src/services/functions.ts` を作る 🔌

```ts
// src/services/functions.ts
import { app } from "../firebase"; // 第10章で作った初期化ファイル想定
import { getFunctions, httpsCallable, connectFunctionsEmulator } from "firebase/functions";

const functions = getFunctions(app);

// Emulatorにつなぐ（開発中だけ）
if (import.meta.env.DEV) {
  // Functions Emulatorは通常 5001
  connectFunctionsEmulator(functions, "127.0.0.1", 5001);
  // ↑ connectFunctionsEmulator の公式例 :contentReference[oaicite:7]{index=7}
}

type FormatTextInput = { text: string };
type FormatTextOutput = { text: string };

export async function callFormatText(input: FormatTextInput): Promise<FormatTextOutput> {
  const fn = httpsCallable<FormatTextInput, FormatTextOutput>(functions, "formatText");
  const res = await fn(input);
  return res.data;
}
```

* `httpsCallable(functions, "関数名")` が基本形です☎️ ([Firebase][1])
* エラー時は `error.code / error.message / error.details` が取れます（UI側で丁寧に表示できる！）😇 ([Firebase][3])

---

## 4) UI：ボタン → 実行中 → 成功 → 失敗 を気持ちよく作る 🎮✨

例として「文章を貼って整形ボタンを押す」と、整形結果が返ってくる画面を作ります📝✨

```tsx
// src/pages/TextTools.tsx
import { useState } from "react";
import { callFormatText } from "../services/functions";

function friendlyMessage(code?: string) {
  // code は "functions/invalid-argument" みたいな形で来ることがあります
  // （サンプルでは前方一致で雑に処理）
  if (!code) return "うまくいきませんでした🥲 もう一度試してね";

  if (code.includes("unauthenticated")) return "ログインが必要です🔐";
  if (code.includes("permission-denied")) return "権限が足りないみたい🥲";
  if (code.includes("invalid-argument")) return "入力内容を確認してね📝";
  if (code.includes("resource-exhausted")) return "混み合ってるよ💦 少し待って再挑戦してね";
  return "サーバー側でエラーが起きたかも🥲";
}

export default function TextTools() {
  const [text, setText] = useState("");
  const [result, setResult] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string>("");

  const onClick = async () => {
    setLoading(true);
    setErrorMsg("");
    try {
      const out = await callFormatText({ text });
      setResult(out.text);
    } catch (e: any) {
      // Functions error: code/message/details が取れることが多い
      // :contentReference[oaicite:10]{index=10}
      setErrorMsg(friendlyMessage(e?.code));
      console.error("functions error", e?.code, e?.message, e?.details);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 space-y-4">
      <h1 className="text-xl font-bold">テキスト整形ツール🧽✨</h1>

      <textarea
        className="w-full border rounded p-3 min-h-[160px]"
        placeholder="ここに文章を貼ってね📝"
        value={text}
        onChange={(e) => setText(e.target.value)}
      />

      <button
        className="px-4 py-2 rounded bg-black text-white disabled:opacity-50"
        onClick={onClick}
        disabled={loading || text.trim().length === 0}
      >
        {loading ? "整形中…⏳" : "Functionsで整形する⚙️"}
      </button>

      {errorMsg && (
        <div className="border rounded p-3 bg-red-50">
          <p className="font-bold">エラー🥲</p>
          <p>{errorMsg}</p>
        </div>
      )}

      <div className="space-y-2">
        <h2 className="font-bold">結果✨</h2>
        <textarea className="w-full border rounded p-3 min-h-[160px]" value={result} readOnly />
      </div>
    </div>
  );
}
```

ポイントはこれだけです👇

* `loading` の間はボタン無効化＆文言変更⏳
* `errorMsg` は “人間向け” にする（コードをそのまま見せない）😇
* `services/functions.ts` に集約して、UIは呼ぶだけ🧼

---

## 5) Emulatorでローカル検証する 🧪✨（超重要！）

本番デプロイ前にローカルで叩けると、安心感が段違いです😆

* フロント側は `connectFunctionsEmulator(functions, "127.0.0.1", 5001)` を使います🔌 ([Firebase][2])
* Callableの作法やエラー設計は公式ガイドにまとまってます📚 ([Firebase][1])

> Emulatorで「ログ」「投げたHttpsError」「返り値」を見ながら直すのが最速です🏎️💨

---

## 6) つまづきポイント集（ここで詰まりやすい）🧯

## ① 「CORSで死ぬ」😵‍💫

* Callableなら基本回避できます（デフォルト全許可）
* 逆に、Callableでも制限したいなら `cors` オプションで絞れます🧩 ([Firebase][1])

## ② 「エラーが INTERNAL しか返ってこない」🧊

* それ、たぶん `HttpsError` 以外を投げてるやつです🥲
* `HttpsError(code, message, details)` にして、UIは `error.code/message/details` を元に表示しましょう✨ ([Firebase][1])

## ③ 「ログインしてるのに unauthenticated」🔐

* フロントがAuth状態を確立する前に押してることが多いです
* UI側で「ログイン完了後にボタンを出す」「未ログインは押せない」がおすすめ🙂

---

## 7) AIへ繋げる布石：次章（AIボタン🤖）が超ラクになる話 🚀

この章で作った「ボタン→Functions→結果表示」の器は、AIにもそのまま使えます✨

* GenkitのFlowをCallableとして公開する `onCallGenkit` という仕組みも用意されています🧠 ([Firebase][4])
* AI側では「function calling（ツール呼び出し）」の考え方も出てきます（モデルが“必要なら関数を使う”設計）🛠️ ([Firebase][5])
* AIを本番で出すなら **App Check** などの守りが大事です🛡️ ([Firebase][6])

---

## 8) Antigravity / Gemini CLIで爆速にするコツ ⚡🤖

* Googleの「Antigravity」は “エージェント開発プラットフォーム” として紹介されています🛸 ([Google Codelabs][7])
* Gemini CLI はターミナルで使えるOSSのAIエージェントとして案内されています⌨️🤖 ([Google Cloud Documentation][8])

## 使いどころ（おすすめ）🎯

* `services/functions.ts` の雛形生成
* エラーコード→ユーザー向け文言のマップ案
* UIの `loading/error/data` の整理案

## 例プロンプト（コピペ用）📋✨

* 「Reactで、Callable Functionsを叩く `useCallableAction()` フックを作って。状態は loading/error/data。TypeScriptで」
* 「Functions v2 onCallで、入力バリデーションして HttpsError を返す例を最小で」
* 「UIのエラー表示を“ユーザー向け”に改善して。技術用語なしで」

---

## ミニ課題🎯✨

「formatText」を少しだけ実戦寄りにしてみよう🔥

1. 入力に `mode: "light" | "strong"` を追加
2. strong のときは「敬語っぽく整形」みたいなルールを追加（AIじゃなくてOK！）
3. UIに mode 切替（2ボタン）を付ける

---

## チェック✅✨（できたら勝ち！）

* ボタン押下で `loading` 表示になる⏳
* 成功したら結果が表示される✨
* 失敗したら「人間向け」のメッセージが出る😇
* `HttpsError` の code をUI側で分岐できてる🧠 ([Firebase][1])
* Emulatorにつないでローカルで叩ける🔌 ([Firebase][2])

---

次章（第18章）は、この“器”に **AI整形ボタン🤖✨** を差し込んで完成させます🔥

[1]: https://firebase.google.com/docs/functions/callable "Call functions from your app  |  Cloud Functions for Firebase"
[2]: https://firebase.google.com/docs/emulator-suite/connect_functions "Connect your app to the Cloud Functions Emulator  |  Firebase Local Emulator Suite"
[3]: https://firebase.google.com/docs/functions/manage-functions "Manage functions  |  Cloud Functions for Firebase"
[4]: https://firebase.google.com/docs/functions/oncallgenkit "Invoke Genkit flows from your App  |  Cloud Functions for Firebase"
[5]: https://firebase.google.com/docs/ai-logic/function-calling "Function calling using the Gemini API  |  Firebase AI Logic"
[6]: https://firebase.google.com/docs/ai-logic/production-checklist "Production checklist for using Firebase AI Logic  |  Firebase AI Logic"
[7]: https://codelabs.developers.google.com/getting-started-google-antigravity "Getting Started with Google Antigravity  |  Google Codelabs"
[8]: https://docs.cloud.google.com/gemini/docs/codeassist/gemini-cli "Gemini CLI  |  Gemini for Google Cloud  |  Google Cloud Documentation"
