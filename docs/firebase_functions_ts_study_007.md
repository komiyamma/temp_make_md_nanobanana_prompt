# 第07章：HTTPでJSONを正しく扱う（入力と出力）📦

この章は「APIっぽい！」を一段上げる回です🌐🔥
`POST /echo` を作って、**JSONの入力→検証→JSONで返す**、さらに **200/400 を使い分け**できるようになります🙂

---

## 7-1. まず大事な前提：FunctionsのHTTPは“Expressっぽい”🧩

FirebaseのHTTP関数は `onRequest()` で作れて、`(req, res)` を受け取って返します🌟
サンプルでも `req.body` をそのまま使っているので、**Request/Response は Express 互換**だと思ってOKです👌 ([Firebase][1])

そして超重要ポイント👉
**Content-Type に応じて本文が自動解析される**ので、普通は `req.body` を見ればOKです（必要なら `req.rawBody` も取れます）🧠 ([Google Cloud Documentation][2])

---

## 7-2. HTTPでJSONを扱うときの「3点セット」✅✅✅

APIはこれだけ守ると一気に安定します💪

1. **Content-Type を確認する**（JSON前提ならここから）🧾
2. **入力を検証する**（型・必須・長さ・範囲）🔎
3. **エラーもJSONで返す**（status code + エラー形式を統一）📮

---

## 7-3. 今回作る `POST /echo` の仕様（ミニAPI設計）🧪

### リクエスト（JSON）

* `message`: **必須** string（1〜200文字）
* `count`: 任意 number（1〜10） ※あったら繰り返して返す

例👇

```json
{
  "message": "hello",
  "count": 3
}
```

### 成功レスポンス（200）

* いつも同じ形で返す（フロントが楽😊）

```json
{
  "ok": true,
  "data": {
    "echo": "hello",
    "repeat": ["hello", "hello", "hello"]
  }
}
```

### 失敗レスポンス（400 / 415 / 405）

```json
{
  "ok": false,
  "error": {
    "code": "invalid_argument",
    "message": "message is required"
  }
}
```

---

## 7-4. 実装（TypeScript / `onRequest`）🛠️✨

> ここでは **1ファイルで完結**させます（初心者向けに迷子防止🎈）
> 分割したい人は、後半の「おまけ」を見てね🙂

`functions/src/index.ts` にこう書きます👇
（FirebaseのHTTP関数は `onRequest()` で作れます）([Firebase][1])

```ts
import { onRequest } from "firebase-functions/v2/https";

// ✅ 返す形を統一（成功も失敗もこれ）
type ApiOk<T> = { ok: true; data: T };
type ApiErr = { ok: false; error: { code: string; message: string; details?: unknown } };

function sendOk<T>(res: any, data: T, status = 200) {
  const body: ApiOk<T> = { ok: true, data };
  res.status(status).json(body);
}

function sendErr(res: any, status: number, code: string, message: string, details?: unknown) {
  const body: ApiErr = { ok: false, error: { code, message, details } };
  res.status(status).json(body);
}

// ✅ unknown を安全に扱うための小物
function isRecord(v: unknown): v is Record<string, unknown> {
  return typeof v === "object" && v !== null && !Array.isArray(v);
}

function asString(v: unknown): string | null {
  return typeof v === "string" ? v : null;
}

function asNumber(v: unknown): number | null {
  return typeof v === "number" && Number.isFinite(v) ? v : null;
}

type EchoInput = { message: string; count?: number };

function validateEchoInput(body: unknown): { ok: true; value: EchoInput } | { ok: false; msg: string } {
  if (!isRecord(body)) return { ok: false, msg: "body must be a JSON object" };

  const message = asString(body.message);
  if (!message) return { ok: false, msg: "message is required (string)" };

  const trimmed = message.trim();
  if (trimmed.length < 1 || trimmed.length > 200) return { ok: false, msg: "message length must be 1..200" };

  const countRaw = body.count;
  if (countRaw === undefined) return { ok: true, value: { message: trimmed } };

  const count = asNumber(countRaw);
  if (count === null) return { ok: false, msg: "count must be a number" };
  if (!Number.isInteger(count) || count < 1 || count > 10) return { ok: false, msg: "count must be integer 1..10" };

  return { ok: true, value: { message: trimmed, count } };
}

export const echo = onRequest(async (req, res) => {
  // ① Methodチェック（APIの基本）
  if (req.method !== "POST") {
    res.set("Allow", "POST");
    return sendErr(res, 405, "method_not_allowed", "use POST");
  }

  // ② Content-Typeチェック（JSON前提ならここ大事）
  // Cloud Run / Functions は Content-Type に応じて本文を自動解析して req.body に入れてくれる想定👍
  // なので JSONを送る側が Content-Type: application/json を付けるのが超重要！
  // （Content-Type 기반で自動解析されるのが公式に書かれてます）🧠
  //   - req.body / req.rawBody にアクセス可能 :contentReference[oaicite:3]{index=3}
  const contentType = (req.headers["content-type"] ?? "").toString();
  if (!contentType.includes("application/json")) {
    return sendErr(res, 415, "unsupported_media_type", "Content-Type must be application/json");
  }

  // ③ 入力検証
  const validated = validateEchoInput(req.body);
  if (!validated.ok) {
    return sendErr(res, 400, "invalid_argument", validated.msg);
  }

  // ④ “APIっぽい”レスポンスを返す
  const { message, count } = validated.value;
  const repeat = Array.from({ length: count ?? 1 }, () => message);

  return sendOk(res, { echo: message, repeat });
});
```

ポイントまとめ💡

* **`req.body` を “unknown” として扱って検証**すると事故が減ります🔎
* **status code をちゃんと分ける**とフロントが最高に楽になります😊
* `Content-Type` を見て弾くのは、地味に最強の防御🛡️
* `req.body` は Content-Type に基づいて自動解析される（だから送る側が正しく付ける）([Google Cloud Documentation][2])

---

## 7-5. Windowsで叩いて確認しよう🪟🔫（安全なテスト）

### ✅ PowerShell（おすすめ）💙

```powershell
$URL = "https://<YOUR_REGION>-<YOUR_PROJECT>.cloudfunctions.net/echo"

## 成功（200）
Invoke-RestMethod `
  -Method Post `
  -Uri $URL `
  -ContentType "application/json" `
  -Body '{"message":"hello","count":3}'
```

### ❌ わざと失敗させる（400）😈

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri $URL `
  -ContentType "application/json" `
  -Body '{"count":3}'
```

### ❌ Content-Type を外す（415）🧱

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri $URL `
  -Body '{"message":"hello"}'
```

---

## 7-6. つまずきポイント集（ここ超あるある）🕳️🤣

* **「req.body が空っぽ」**
  → だいたい `Content-Type: application/json` を付け忘れです📌（自動解析は Content-Type を見てる）([Google Cloud Documentation][2])

* **「message が string じゃなくて壊れる」**
  → `unknown` 扱い→検証、が最強です🛡️

* **「エラー時にHTMLが返ってきてフロントが混乱」**
  → エラーも必ず JSON で返す！（この章の `sendErr()` 方式）📦✨

* **「POST以外も通ってしまう」**
  → `405 + Allowヘッダ` は正義👮‍♂️

---

## 7-7. AI活用（Antigravity / Gemini CLI）🤖🛸✨

ここ、AIに手伝わせると爆速になります⚡
Firebase側は **MCP server + Gemini CLI拡張**で、`/firebase:init` みたいな **slash command**が用意されてます🧰 ([Firebase][3])

### 使い方イメージ（お願いの仕方テンプレ）🗣️✨

* 「`POST /echo` を作りたい。入力は message と count。400/415/405 を分けたい。レスポンスは ok/data と ok/error で統一して」
* 「TypeScriptで、unknown→検証する関数も作って。Zodなしで」
* 「PowerShellのテストコマンドも付けて」

### AIに任せっぱなし禁止の“3秒レビュー”✅

* status code が分かれてる？（200/400/415/405）
* エラーも JSON？（HTMLになってない？）
* `req.body` をそのまま信じてない？（unknown→検証になってる？）

### FirebaseのAIサービスも絡める小ネタ🧠✨

AI機能（例：文章要約、分類、画像生成など）をアプリに入れるとき、**APIの入出力がグチャると地獄**になります😇
だからこの章の「入力検証＋JSON統一」は、将来 **Firebase AI Logic や Genkit**を触るときの土台になります🏗️（AI機能を足すガイドやプロンプト群も整備されています）([Firebase][4])

---

## 7-8. ミニ課題（5〜10分）✍️🔥

1. `message` が **201文字以上**なら 400 にしてみよう📏
2. `count` が無いときは `repeat` を 1回にする（もうできてるね😉）
3. `code` を `invalid_argument` / `unsupported_media_type` / `method_not_allowed` に揃える（もう揃ってる！😆）

---

## 7-9. この章のチェック✅✅

* [ ] `POST` 以外は **405** で返せる👮‍♂️
* [ ] `Content-Type` が違うと **415** で返せる🧱
* [ ] 入力が変でも **400 + JSONエラー**で返せる📦
* [ ] 成功も失敗も「同じ形」で返せる（フロントが楽）🧡
* [ ] `req.body` を信じず **unknown→検証**できた🔎✨

---

### おまけ：ランタイムの最新ざっくりメモ🧩（迷子防止）

* Firebase Functions側は **Node.js 20/22 が現役**で、古いものは非推奨の流れです（公式の“管理/運用”ドキュメントで案内あり）([Firebase][5])
* もし「Firebaseの外」で **Cloud Run functions** を使うなら、ランタイム表に **.NET（例：.NET 8）** や **Node.js 24** なども載っています📌 ([Google Cloud Documentation][6])

---

次の第8章（CORS）に行くと、いよいよ **Reactフロントからこの `echo` を呼ぶ**ときの“最初の壁”を壊せます🧱➡️💥😆

[1]: https://firebase.google.com/docs/functions/http-events "Call functions via HTTP requests  |  Cloud Functions for Firebase"
[2]: https://docs.cloud.google.com/run/docs/write-functions "Write Cloud Run functions  |  Google Cloud Documentation"
[3]: https://firebase.google.com/docs/ai-assistance/prompt-catalog "AI prompt catalog for Firebase  |  Develop with AI assistance"
[4]: https://firebase.google.com/docs/ai-assistance/prompt-catalog/add-ai-features "AI Prompt: Add AI features  |  Develop with AI assistance  |  Firebase"
[5]: https://firebase.google.com/docs/functions/get-started "Get started: write, test, and deploy your first functions  |  Cloud Functions for Firebase"
[6]: https://docs.cloud.google.com/functions/docs/runtime-support "Runtime support  |  Cloud Run functions  |  Google Cloud Documentation"
