# 第18章：AIボタンをUIに組み込む 🤖✨

この章では、管理画面の「詳細フォーム」に **“AIで整形”ボタン** を付けて、文章を読みやすく整えてから **ユーザーが確認して反映** できるUIを作ります📝➡️🤖➡️✅
（※「AIの出力を勝手に保存しない」設計がポイントだよ〜😆）

---

## 0) まず知っておくと安心な考え方 🧠🛡️

## なんで“ブラウザからGemini直呼び”は危ないの？😱

![Direct API Call Risk](./picture/firebase_frontend_foundation_ts_study_018_01_direct_call_risk.png)

WebでGemini APIを直接呼ぶやり方は **プロトタイプ向け** で、**キー露出や悪用** のリスクが出やすいです⚠️
公式の学習資料でも「本番を見据えるなら Firebase AI Logic に移行してね」と案内されています。([Google for Developers][1])

## そこで **Firebase AI Logic** が強い 💪🔥

![Firebase AI Logic Architecture](./picture/firebase_frontend_foundation_ts_study_018_02_ai_logic_arch.png)

Firebaseの **Firebase AI Logic** は、Web/モバイルのクライアントSDKからGemini/Imagenを呼べて、**セキュリティ機能（App Check連携など）** や **Firebase/Google Cloud 連携** がやりやすいのが売りです🧩✨([Firebase][2])
さらに **AIリクエストのゲートウェイ（プロキシ）** を用意してくれて、**Gemini APIキーをアプリのコードに埋めない** 方向に寄せられます🔐([Firebase][2])

---

## 1) この章の完成イメージ 🏁✨

![AI Suggestion Workflow](./picture/firebase_frontend_foundation_ts_study_018_03_ui_workflow.png)

* 詳細フォームに「🤖 AIで整形」ボタン
* 押すと **整形案** が出る（保存しない）
* ユーザーが「✅反映する」を押したらフォームに反映
* 最後にいつもの「💾保存」ボタンでFirestoreへ保存（ここで初めてDB更新）

---

## 2) 読むパート：UIにAIを入れる時の“3点セット”📦✨

1. **確認ステップを必ず入れる**（AI案→人がOK）✅
2. **状態管理**：`loading / error / suggestion` を揃える🔁
3. **悪用対策**：App Check + 乱用（レート）対策🛡️

   * AI Logic は App Check と一緒に使うのを強く推奨されています([Firebase][3])
   * さらに **ユーザー単位のレート制限** も用意されています（デフォルト有効）([Firebase][2])

---

## 3) 手を動かすパート：実装していこう 🛠️🔥

## Step 1) Firebase側で AI Logic を有効化する 🤖⚙️

![Enable AI Logic UI](./picture/firebase_frontend_foundation_ts_study_018_04_enable_ai_logic.png)

Firebase コンソールの AI Logic で「Get started」→ **Gemini Developer API** を選ぶのが入門におすすめです（必要なら後で Vertex AI 側にも切り替え可能）([Firebase][3])
このとき **Gemini APIキーが作られますが、アプリのコードに入れないでね** と明確に書かれています🔑❌([Firebase][3])

> ついでに：モデルは `gemini-2.5-flash` が手軽で速い系です⚡（公式の例でもこれ）([Firebase][3])
> ちなみに `gemini-2.0-flash` / `gemini-2.0-flash-lite` は **2026-03-31に廃止予定** と案内があります📅⚠️([Firebase][2])

---

## Step 2) フロントにAI Logic SDKを入れる 📦

`firebase` を入れていればOKです（AI LogicはJS SDKの中に含まれるよ）([Firebase][3])

```bash
npm install firebase
```

---

## Step 3) `firebase.ts` に “AIの出口” を追加する 🔌🤖

既にある `firebase.ts`（第10章のやつ）に、AIを足します✨
ポイントは **モデルを1回作ってexport** しておくこと！（呼び出し側が楽になる👍）

```ts
// src/firebase.ts
import { initializeApp } from "firebase/app";

// ここは既にある想定（Auth/Firestore/Storageなど）
export const app = initializeApp({
  // ... your firebase config
});

// ✅ ここからAI Logic（Gemini Developer API backend）
import { getAI, getGenerativeModel, GoogleAIBackend } from "firebase/ai";

const ai = getAI(app, { backend: new GoogleAIBackend() });

// 迷ったらまずこれ（速い・安い寄り）
export const geminiModel = getGenerativeModel(ai, { model: "gemini-2.5-flash" });
```

この書き方（`getAI` / `GoogleAIBackend` / `getGenerativeModel`）は公式ガイドのWeb例そのままです🧠✨([Firebase][3])
あと本番運用を意識するなら **Remote Configでモデル名を後から変えられるように** するのが推奨されています（将来のモデル変更に強い💪）([Firebase][3])

---

## Step 4) AI整形の “呼び出し処理” を hook にする 🪝✨

![AI Code Structure](./picture/firebase_frontend_foundation_ts_study_018_05_code_structure.png)

UIから直接API叩くより、hookにすると見通しが良いです😆

```ts
// src/hooks/useAiPolishText.ts
import { useCallback, useState } from "react";
import { geminiModel } from "../firebase";

type UseAiPolishTextResult = {
  loading: boolean;
  error: string | null;
  suggestion: string | null;
  run: (input: string) => Promise<void>;
  clear: () => void;
};

export function useAiPolishText(): UseAiPolishTextResult {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [suggestion, setSuggestion] = useState<string | null>(null);

  const clear = useCallback(() => {
    setError(null);
    setSuggestion(null);
  }, []);

  const run = useCallback(async (input: string) => {
    setLoading(true);
    setError(null);
    setSuggestion(null);

    try {
      const prompt = [
        "あなたは文章の校正・整形アシスタントです。",
        "次の文章を、意味を変えずに読みやすく整えてください。",
        "条件：",
        "・箇条書きOK",
        "・敬語は丁寧すぎなくてOK",
        "・長い文は短く",
        "・出力は整形後の本文だけ",
        "",
        "【本文】",
        input,
      ].join("\n");

      const result = await geminiModel.generateContent(prompt);
      const text = result.response.text();

      setSuggestion(text);
    } catch (e) {
      console.error(e);
      setError("AIの呼び出しに失敗しました😢 もう一度試してみてね");
    } finally {
      setLoading(false);
    }
  }, []);

  return { loading, error, suggestion, run, clear };
}
```

---

## Step 5) 詳細フォームに「🤖AIで整形」→「✅反映」UIを付ける 🧩

![AI Editor Component](./picture/firebase_frontend_foundation_ts_study_018_06_ui_component.png)

例として「記事本文（body）」を整形するUIを付けます📄✨

```tsx
// src/components/PostBodyEditor.tsx
import { useMemo, useState } from "react";
import { useAiPolishText } from "../hooks/useAiPolishText";

type Props = {
  initialBody: string;
  onChange: (next: string) => void;
};

export function PostBodyEditor({ initialBody, onChange }: Props) {
  const [body, setBody] = useState(initialBody);
  const { loading, error, suggestion, run, clear } = useAiPolishText();

  const canRun = useMemo(() => body.trim().length > 0 && !loading, [body, loading]);

  return (
    <div className="space-y-3">
      <label className="block text-sm font-medium">本文</label>

      <textarea
        className="w-full rounded-lg border p-3"
        rows={8}
        value={body}
        onChange={(e) => {
          const next = e.target.value;
          setBody(next);
          onChange(next);
        }}
        placeholder="ここに本文..."
      />

      <div className="flex items-center gap-2">
        <button
          className="rounded-lg border px-3 py-2 disabled:opacity-50"
          disabled={!canRun}
          onClick={() => run(body)}
        >
          {loading ? "🤖整形中..." : "🤖 AIで整形"}
        </button>

        <button
          className="rounded-lg border px-3 py-2"
          onClick={() => {
            clear();
          }}
        >
          🧹クリア
        </button>
      </div>

      {error && <p className="text-sm text-red-600">⚠️ {error}</p>}

      {suggestion && (
        <div className="rounded-xl border p-3 space-y-2">
          <div className="flex items-center justify-between">
            <p className="font-medium">✨整形案（まだ保存しない）</p>
            <button
              className="rounded-lg border px-3 py-2"
              onClick={() => {
                setBody(suggestion);
                onChange(suggestion);
                clear();
              }}
            >
              ✅反映する
            </button>
          </div>

          <pre className="whitespace-pre-wrap text-sm leading-6">{suggestion}</pre>

          <p className="text-xs opacity-70">
            📝ポイント：ここで“人が確認してOK”してからフォームに反映！そのあとに保存ボタンでFirestore更新だよ〜
          </p>
        </div>
      )}
    </div>
  );
}
```

---

## 4) （重要）悪用対策：App Check をONにしよう 🛡️🔥

![App Check Protection](./picture/firebase_frontend_foundation_ts_study_018_07_app_check_shield.png)

AI Logicのガイドでも **App Check を早めに入れるのが強く推奨** されています📌([Firebase][3])
Webの場合、App Check を使うと「正規のアプリからの呼び出し」を判定しやすくなって、不正アクセスの抑止になります🧱✨

実装例（App Check Webの初期化）👇

```ts
// src/firebase.ts（例：必要ならここに追記）
import { initializeAppCheck, ReCaptchaV3Provider } from "firebase/app-check";
import { app } from "./firebase";

// reCAPTCHA site key はコンソールの案内で作る
initializeAppCheck(app, {
  provider: new ReCaptchaV3Provider("YOUR_RECAPTCHA_SITE_KEY"),
  isTokenAutoRefreshEnabled: true,
});
```

このAPI名（`initializeAppCheck` / `ReCaptchaV3Provider` / `isTokenAutoRefreshEnabled`）は公式のWebドキュメントに載っています📚([Firebase][4])

---

## 5) ミニ課題 🎯😆

次のどれか1つやってみよう！

1. **“トーン選択”** を付ける（やさしい／ビジネス／短く）🎚️
2. **“JSONで返して”** を試す（`{ title, body }` みたいに）🧾
3. **入力が短すぎる時はAIボタンを無効**（5文字未満とか）🚧

---

## 6) チェックリスト ✅✅

* AIの結果が **勝手に保存されてない**（反映→保存の順になってる？）
* `loading` 中にボタン連打できない？👆💥
* 失敗時にユーザーが次の行動を取れるメッセージになってる？😇
* App Check を入れた（または入れる予定が決まった）？🛡️([Firebase][3])

---

## 7) よくあるつまづき 💥😵‍💫

* **Q: `result.response.text()` が空っぽ**
  A: セーフティ設定や入力が短すぎる/曖昧すぎる時に起きがち。入力の条件を少し足してみよう（例：「箇条書きOK」「出力は本文だけ」など）🧠

* **Q: AIがそれっぽい嘘を書く**
  A: あるある！😆 今回は「整形」用途なので、**“意味を変えずに”** をプロンプトに入れて、しかも **人が確認して反映** で事故を潰そう✅

---

## 8) おまけ：Antigravity / Gemini CLIで“実装速度”を上げる 🛸⌨️✨

ここは第19章に近いけど、今でも超効くので軽く紹介！

* **Firebase MCP server** を使うと、AIエージェントがFirebaseの情報（例：Firestoreやルール周り）にアクセスしやすくなります🧩([Firebase][5])
* さらに **Gemini CLI の Firebase拡張** を入れると、MCPツールとプロンプトがまとまって使える…という公式案内があります🚀([Firebase][6])
* そして **2026-02-11に「Extension settings」** が入って、拡張の設定がかなり楽になったよ、という更新も出ています（地味に助かるやつ！）🧰✨([Google Developers Blog][7])

---

## 9) ちょい寄り道：サーバー側にAIを置きたくなったら？🏗️☁️

UIからの呼び出しだけじゃ足りない（重い処理・秘密情報・複雑なツール連携）となったら、次の逃げ道があるよ👇

* Cloud Functions for Firebase（Node.js 22/20 など）([Firebase][8])
* Cloud Functions for Firebase（Python 3.10/3.11 ランタイム）([Firebase][8])
* .NETを使うなら Microsoft の **.NET 10（LTS）** が軸になりやすい📌([Microsoft][9])
* ただし Python は **3.14.3 / 3.13.12（2026-02-03時点）** みたいに新しいのも出てるので、用途によってはCloud Runなども視野👀([Python documentation][10])

---

次は「整形」だけじゃなくて、**画像（Imagen）** や **構造化出力（JSON）** に繋げると、一気に“管理画面が賢くなる”感じが出ます🤖✨
第18章の続きとして、あなたのアプリの「どのフォームにAIボタン付けたいか」（記事？ユーザープロフィール？）に合わせて、プロンプトとUIを最適化する版も作れるよ😆

[1]: https://developers.google.com/learn/pathways/solution-ai-gemini-getting-started-web?utm_source=chatgpt.com "Getting started with the Gemini API and Web apps"
[2]: https://firebase.google.com/docs/ai-logic "Gemini API using Firebase AI Logic  |  Firebase AI Logic"
[3]: https://firebase.google.com/docs/ai-logic/get-started "Get started with the Gemini API using the Firebase AI Logic SDKs  |  Firebase AI Logic"
[4]: https://firebase.google.com/docs/app-check/web/recaptcha-provider "Get started using App Check with reCAPTCHA v3 in web apps  |  Firebase App Check"
[5]: https://firebase.google.com/docs/studio/mcp-servers "Connect to Model Context Protocol (MCP) servers  |  Firebase Studio"
[6]: https://firebase.google.com/docs/ai?utm_source=chatgpt.com "AI | Firebase Documentation"
[7]: https://developers.googleblog.com/making-gemini-cli-extensions-easier-to-use/?utm_source=chatgpt.com "Making Gemini CLI extensions easier to use"
[8]: https://firebase.google.com/docs/functions/manage-functions "Manage functions  |  Cloud Functions for Firebase"
[9]: https://dotnet.microsoft.com/en-us/platform/support/policy?utm_source=chatgpt.com "The official .NET support policy | .NET"
[10]: https://docs.python.org/3/whatsnew/3.13.html?utm_source=chatgpt.com "What's New In Python 3.13"
