# 第10章：AIでUX強化：説明文やエラーメッセージをGeminiに作らせる🤖📝

この章では「認証のロジックは堅く💎、言い回しはやさしく😊」をテーマに、**Firebase Authentication のエラー文**や**補足テキスト**を **Gemini で“いい感じの日本語”に整える**仕組みを作ります✨
（AIは“判断”じゃなくて“文章づくり”に使うのがコツだよ👍）

---

## できあがりイメージ👀✨

* ログイン/サインアップでエラーが出た😵
  → いつもの日本語メッセージ（第9章）に加えて
  → **「AIでやさしく説明💬」**ボタンが出る
* 押すと…

  * ✅ 何が起きたか（やさしい言葉）
  * ✅ 次に何をすればいいか（具体的な手順）
    を短く返してくれる✨

この章の主役は **Firebase AI Logic**（アプリからGeminiを安全寄りに呼べる仕組み）だよ🧠✨ ([Firebase][1])

---

## まず大事な考え方3つ🧠🧯

1. **AIに“正解判定”をさせない**🙅‍♂️
   認証の成否、UI遷移、エラー分岐は**コードで決め打ち**。
   AIは「説明の文章」を作るだけ✍️✨

2. **送る情報は最小限**🔒

* 送ってOK：`error.code`、画面（login/signup）、入力の“種類”（メール/パスワード）
* 送っちゃダメ：パスワード、確認コード、個人情報ドバドバ（メール全文など）🙅‍♀️

3. **本番はApp Checkもセット**🛡️
   Firebase AI Logic は **App Check で不正クライアント対策**ができるし、**ユーザー単位のレート制限**もある（調整可能）ので、“ちゃんと運用する前提”が作りやすい👍 ([Firebase][1])

---

## 手順①：Firebase AI Logic をプロジェクトで有効化🔧🤖

コンソール側で「AI Logic のセットアップ」を進めると、**Gemini API Provider**（Gemini Developer API / Vertex AI Gemini API）を選ぶ流れになるよ🌈
最初は **Gemini Developer API** 推奨、と公式が案内してる（必要になったらVertex側にも切替できる）📌 ([Firebase][2])

そして超重要⚠️
**コンソールが作った Gemini API key をアプリのコードに直書きしない**こと！🙅‍♂️
（直書き不要で使えるのが “Firebase AI Logic のおいしい所”） ([Firebase][2])

---

## 手順②：Web(React/TS)で Firebase AI Logic を初期化する🧩✨

> 既に `firebase/app` と `firebase/auth` を初期化している前提で、**AIの分だけ追加**していくよ👍

## 1) 依存関係📦

```powershell
npm install firebase
```

## 2) `src/lib/firebase.ts`（例）にAIを追加🤖

```ts
// src/lib/firebase.ts
import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";

// ★AI Logic（Gemini）を使うためのimport
import { getAI, getGenerativeModel, GoogleAIBackend } from "firebase/ai";

const firebaseConfig = {
  // ...（既存のやつ）
};

export const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);

// ★Gemini Developer API backend を使う
const ai = getAI(app, { backend: new GoogleAIBackend() });

// ★まずは速くて使いやすいモデル例（公式サンプルでも登場）
export const geminiModel = getGenerativeModel(ai, { model: "gemini-2.5-flash" });
```

この `getAI / getGenerativeModel / GoogleAIBackend` の形が、Web向けの公式サンプルに載ってるやつだよ📚 ([Firebase][2])

> ちなみに：**Gemini 2.0 Flash / Flash-Lite は 2026-03-31 にretire予定**って注意書きがあるので、今から作るなら新しめモデル名を使うのが安全寄り👍（例：`gemini-2.5-flash-lite` など） ([Firebase][1])

---

## 手順③：AIに「やさしい説明文」を作らせる関数を作る💬✨

`src/lib/ai/geminiUx.ts` みたいなのを作るイメージでいくね🧱

```ts
// src/lib/ai/geminiUx.ts
import type { AuthError } from "firebase/auth";
import { geminiModel } from "../firebase";

type Scene = "login" | "signup" | "reset";

const FALLBACK_MAP: Record<string, string> = {
  "auth/invalid-email": "メールアドレスの形式が正しくないみたい😵",
  "auth/user-not-found": "このメールアドレスのユーザーが見つからないよ😢",
  "auth/wrong-password": "パスワードが違うみたい…もう一回確認してね🔑",
  "auth/weak-password": "パスワードが弱いよ💦 もう少し強くしよう！",
  "auth/email-already-in-use": "そのメールはもう使われているよ📩",
};

function fallbackMessage(code: string): string {
  return FALLBACK_MAP[code] ?? "うまくいかなかったよ😵 もう一度試してね。";
}

export async function aiExplainAuthError(params: {
  error: unknown;
  scene: Scene;
}): Promise<string> {
  const err = params.error as Partial<AuthError> | undefined;
  const code = typeof err?.code === "string" ? err.code : "unknown";
  const base = fallbackMessage(code);

  // ✅ AIに渡す情報は最小限（個人情報/パスワードは渡さない）
  const prompt = [
    "あなたは日本語のUIライターです。",
    "Firebase Authentication のエラーを、初心者にもやさしく説明してください。",
    "次に何をすればいいかも、具体的に短く提案してください。",
    "",
    "ルール:",
    "- 120〜220文字くらい",
    "- 絵文字を少し入れる",
    "- 断定しすぎない（“〜かも”を使う）",
    "- 個人情報に触れない",
    "",
    `画面: ${params.scene}`,
    `エラーコード: ${code}`,
    `既存の短い説明: ${base}`,
    "",
    "出力は本文だけ（箇条書きOK）",
  ].join("\n");

  try {
    const result = await geminiModel.generateContent(prompt);
    const text = result.response.text();

    // 変な時はfallbackへ
    if (!text || text.trim().length < 20) return base;
    return text.trim();
  } catch {
    return base;
  }
}
```

`generateContent()` → `result.response.text()` という呼び方も公式サンプルに載ってるよ👍 ([Firebase][2])

---

## 手順④：UIに「AIで説明」ボタンを付ける🧷✨

例として、ログイン画面で `error` があるときに出すコンポーネント👇

```tsx
// src/features/auth/AuthErrorHelp.tsx
import { useState } from "react";
import { aiExplainAuthError } from "../../lib/ai/geminiUx";

export function AuthErrorHelp(props: {
  error: unknown;
  scene: "login" | "signup" | "reset";
}) {
  const [aiText, setAiText] = useState<string>("");
  const [loading, setLoading] = useState(false);

  const hasError = !!props.error;

  if (!hasError) return null;

  return (
    <div style={{ padding: 12, border: "1px solid #ddd", borderRadius: 8 }}>
      <div style={{ marginBottom: 8 }}>
        <strong>エラーが出たよ😵</strong>
      </div>

      <button
        type="button"
        disabled={loading}
        onClick={async () => {
          setLoading(true);
          const text = await aiExplainAuthError({ error: props.error, scene: props.scene });
          setAiText(text);
          setLoading(false);
        }}
      >
        {loading ? "AIが考え中…🤖⏳" : "AIでやさしく説明💬"}
      </button>

      {aiText && (
        <div style={{ marginTop: 10, whiteSpace: "pre-wrap", lineHeight: 1.6 }}>
          {aiText}
        </div>
      )}
    </div>
  );
}
```

これをログイン/サインアップ画面で、エラー表示エリアに差し込めばOKだよ🔧✨

---

## ミニ課題🎯：ログイン画面の「補足文」もAIで作る📝✨

## お題

ログイン画面に「パスワードの注意」みたいな補足を出したい🙂
でも毎回文言考えるのダルい…👉 AIに“良い感じの一言”を作らせよう！

## ルール

* 画面が開いた時に毎回AI呼び出し❌（重い＆回数も増える）
* **初回だけ生成して localStorage に保存**✅（実用寄り）

ヒント：`localStorage.getItem("login_hint_v1")` が無ければAI生成、あればそれを表示✨

---

## よくあるハマりどころ😵‍💫🧯

* **AI Logic 側のセットアップが未完了**
  → コンソールの Firebase AI Logic 画面で “Get started” が終わってるか確認👀 ([Firebase][2])

* **モデル名が古い/廃止予定**
  → 2026-03-31 のretire予定が明記されてるモデルがあるので、今作るなら新しめを選ぶ👍 ([Firebase][1])

* **本番で使うのに保護が弱い**
  → App Check を検討（最初は後回しでもOKだけど、ちゃんと運用するなら重要）🛡️ ([Firebase][2])

---

## Antigravity / Gemini CLI で“楽して強くする”🚀🧠

## Antigravity の使いどころ（超相性いい）🛰️

Antigravityは “Mission Control” で複数エージェントが計画→実装→検証まで回せるタイプの開発環境だよ🛠️✨ ([Google Codelabs][3])

おすすめ指示（そのまま投げてOK）👇

* 「Authエラー一覧を整理して、`FALLBACK_MAP` を増やして」📚
* 「このプロジェクトでエラーメッセージが表示される箇所を全部探して、統一コンポーネントに寄せて」🧹
* 「“AIで説明”のボタンが連打されないように、クールダウン（10秒）入れて」⏱️

※ブラウズ機能は強いけど、URL allowlist など安全設定の考え方も公式にあるよ🔒 ([Google Codelabs][3])

## Gemini CLI の使いどころ（リポジトリの巡回が速い）🔎

Gemini CLI は “ターミナルのAIエージェント”で、MCPや内蔵ツールを使って修正・テスト改善とかも狙えるタイプ🧰🤖 ([Google Cloud Documentation][4])

おすすめ依頼👇

* 「`AuthErrorHelp` が呼ばれてない画面がないか探して」
* 「`aiExplainAuthError` のpromptを短くしつつ品質落とさない案ちょうだい」
* 「E2Eテストで“エラー時にAIボタンが出る”を確認するテスト案」🧪

---

## 仕上げチェック✅🎉

* [ ] エラーが出た時に「AIでやさしく説明💬」ボタンが表示される
* [ ] 押したら“短く・やさしく・次の行動が分かる”文章が出る🙂
* [ ] AI呼び出しが失敗しても、既存の日本語メッセージでちゃんと案内できる（fallback）🧯
* [ ] パスワードなどの秘匿情報をAIに渡してない🔒

---

## 確認クイズ（3問）📝💯

1. AIに任せていいのは「判断」or「文章」？🤔
2. AIに渡しちゃダメな情報は何？（例を2つ）🔒
3. 本番運用で検討したい保護機能は？🛡️

---

次の章（第11章）で Googleログインに入るけど、**第10章の“AIでやさしく説明”は、そのままGoogleログインのエラーにも流用できる**よ🌈✨
（`scene` を増やすだけでOK👍）

* [The Verge](https://www.theverge.com/news/822833/google-antigravity-ide-coding-agent-gemini-3-pro?utm_source=chatgpt.com)
* [techradar.com](https://www.techradar.com/ai-platforms-assistants/googles-antigravity-ai-deleted-a-developers-drive-and-then-apologized?utm_source=chatgpt.com)
* [The Verge](https://www.theverge.com/news/692517/google-gemini-cli-ai-agent-dev-terminal?utm_source=chatgpt.com)

[1]: https://firebase.google.com/docs/ai-logic "Gemini API using Firebase AI Logic  |  Firebase AI Logic"
[2]: https://firebase.google.com/docs/ai-logic/get-started "Get started with the Gemini API using the Firebase AI Logic SDKs  |  Firebase AI Logic"
[3]: https://codelabs.developers.google.com/getting-started-google-antigravity "Getting Started with Google Antigravity  |  Google Codelabs"
[4]: https://docs.cloud.google.com/gemini/docs/codeassist/gemini-cli "Gemini CLI  |  Gemini for Google Cloud  |  Google Cloud Documentation"
