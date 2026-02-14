# 第28章：ログ設計② requestIdで一本道にする🧵🚶‍♀️

「ログ見ても、どの行が同じリクエストの話なのか分からない〜😭」ってなるやつ、**requestId**で一発解決しにいこっ💪😊
この章は「**1回のリクエスト（あるいは1つのユーザー操作）を、ログ上で一本の線にする**」のがテーマだよ〜🧵✨

---

## 1) requestIdってなに？なんで“一本道”になるの？🛣️🔎

### ✅ requestIdの正体

* **1つのリクエストに付けるユニークな番号**だよ🆔✨
* ログ1行1行に **同じrequestId** を付けると、あとで検索したときに「この1件の流れ」がズラーッと出る📚🔍

### ✅ 具体的に嬉しいこと😍

* 例：ログが100万行あっても、`requestId=abc123` で絞ればその件だけ見れる✨
* 障害調査が「当てずっぽう」から「一本道の追跡」になる🧵🚶‍♀️

![追跡の糸：迷宮の中で一本の道しるべを辿る[(./picture/err_model_ts_study_028_trace_thread.png)

---

## 2) requestId / correlationId / traceId の違い（超やさしく）🧠🌸

ここ、ちょい用語が似てて混乱しがちなので、**最短で整理**するね😊

### 🆔 requestId（今回の主役）

* **1回のHTTPリクエスト**に付けるIDのことが多いよ
* たとえば `GET /api/orders` 1回に1つ

### 🧵 correlationId（“取引全体”のID）

* 「ユーザーの1操作」が裏で複数のリクエスト/ジョブを生むとき、**全部を束ねる親ID**として使うことが多いよ
* ただ、最初は **requestId = correlationId** として運用しても全然OK🙆‍♀️✨（成長したら分ければいい）

### 🧭 traceId（分散トレーシングのID）

* 複数サービスをまたいで追跡する標準の世界では、**W3C Trace Context**の `traceparent` で **trace-id** を運ぶのが王道だよ📦✨ ([W3C][1])
* Google Cloudなども `traceparent` / `tracestate` による伝播を説明してるよ🌐 ([Google Cloud Documentation][2])

> まとめると：
> **まずはrequestIdで一本道** → 慣れたら **traceId（traceparent）** もログに出す、が気持ちいい流れ😊✨ ([OpenTelemetry][3])

---

## 3) requestId設計の基本ルール（ここだけ守れば強い）🧱✨

### ルールA：入口で作る🚪

* **最初に受け取る場所（APIの入口）**で作るのが基本！
* もしクライアントやゲートウェイが `X-Request-ID` を付けてくれてたら、それを採用してもOK（ただし検証はしてね）

  * 例：Herokuは `X-Request-ID` を付けてアプリに渡す仕組みを説明してるよ🧾 ([Heroku Dev Center][4])
  * `X-Request-ID` は非公式だけど「追跡用によく使う」ヘッダとして紹介されてるよ🔍 ([HTTP.DEV][5])

### ルールB：レスポンスにも返す📤

* `X-Request-ID` をレスポンスヘッダに返すと、

  * ユーザーから「このエラー出た😭」って来たときに requestId を聞ける📞✨
* pino-http の例でも `X-Request-Id` をレスポンスにセットしてるよ🌲 ([GitHub][6])

### ルールC：下流にも渡す（伝播）📨

* 自分のサーバ → 外部API → DB → キュー…みたいに流れるなら
  **次の呼び出しにも requestId を付けて渡す**と追跡が途切れない🧵✨

### ルールD：ログは“構造化”して常に同じキー名で🧾✨

* `requestId` というキーで統一（`reqId` と混ぜない）
* 検索しやすさが命🔥

---

## 4) TypeScriptで実装：最小で強いパターン🧪💪✨

### AsyncLocalStorageで「どこでもrequestIdが取れる」ようにする🧵

Nodeの **AsyncLocalStorage** を使うと、関数引数で requestId を渡し回さなくても
「今の処理のrequestId」を取り出せるようになるよ✨
Node公式も、リクエストごとにIDを付ける例を出してて、AsyncLocalStorageを推奨してるよ😊 ([Node.js][7])

---

### 4-1) requestContext（保存場所）を作る🧺🧵

```ts
// src/requestContext.ts
import { AsyncLocalStorage } from "node:async_hooks";

export type RequestContext = {
  requestId: string;
};

const als = new AsyncLocalStorage<RequestContext>();

export function runWithRequestContext(ctx: RequestContext, fn: () => void) {
  als.run(ctx, fn);
}

export function getRequestContext(): RequestContext | undefined {
  return als.getStore();
}

export function getRequestId(): string | undefined {
  return als.getStore()?.requestId;
}
```

---

### 4-2) どこでも使える logger（自作の超軽量版）🪶🧾

```ts
// src/logger.ts
import { getRequestId } from "./requestContext";

type Level = "debug" | "info" | "warn" | "error";

export function log(level: Level, message: string, extra: Record<string, unknown> = {}) {
  const requestId = getRequestId();

  // JSONログ（構造化ログ）
  const line = {
    ts: new Date().toISOString(),
    level,
    message,
    requestId: requestId ?? null,
    ...extra,
  };

  // ここは本番なら pino 等に差し替えやすい形✨
  // とりあえずconsoleでもOK！
  console.log(JSON.stringify(line));
}
```

---

### 4-3) Expressで「入口で発行→ALSに入れる→レスポンスに返す」🚪📤✨

```ts
// src/server.ts
import express from "express";
import { randomUUID } from "node:crypto";
import { runWithRequestContext } from "./requestContext";
import { log } from "./logger";

const app = express();

app.use((req, res, next) => {
  // 既存のX-Request-IDがあれば採用（なければ生成）
  const incoming = req.header("x-request-id");
  const requestId = (typeof incoming === "string" && incoming.length > 0) ? incoming : randomUUID();

  // レスポンスにも返す
  res.setHeader("X-Request-ID", requestId);

  // ここがポイント：このリクエストの“文脈”として保存🧵
  runWithRequestContext({ requestId }, () => next());
});

app.get("/api/hello", async (_req, res) => {
  log("info", "handler start");
  // 何か処理した気分
  await new Promise(r => setTimeout(r, 50));
  log("info", "handler end");
  res.json({ ok: true });
});

app.listen(3000, () => {
  console.log("http://localhost:3000");
});
```

これで `/api/hello` を叩くと、ログがこうなるイメージだよ👇😍

```txt
{"ts":"...","level":"info","message":"handler start","requestId":"b3c..."}
{"ts":"...","level":"info","message":"handler end","requestId":"b3c..."}
```

---

## 5) フレームワークの“標準機能”も使えるよ（Fastify / pino）🌲⚡

### Fastifyは「デフォでrequest id」を持ってる🆔✨

Fastifyは **リクエストごとにIDを付ける**のが標準で、`request-id` ヘッダがあればそれを使う、なければ生成…みたいな挙動が説明されてるよ😊 ([Fastify][8])

### pino-httpは `genReqId` で `x-request-id` を拾って返せる🌲

pino-http のREADME例でも `x-request-id` を拾って、なければUUIDを作って `X-Request-Id` をレスポンスに返してるよ✨ ([GitHub][6])

> 「自作で理解」→「pino/fastifyで実戦投入」って流れがめっちゃ学びやすい😊💗

---

## 6) 外部APIを呼ぶとき：requestIdを“渡して続きの線”を作る📨🧵

### fetchラッパーを作る（超おすすめ）🪄✨

```ts
// src/fetchWithRequestId.ts
import { getRequestId } from "./requestContext";

export async function fetchWithRequestId(input: RequestInfo | URL, init: RequestInit = {}) {
  const requestId = getRequestId();

  const headers = new Headers(init.headers);
  if (requestId) headers.set("X-Request-ID", requestId);

  return fetch(input, { ...init, headers });
}
```

これで「外部API側のログ」も `X-Request-ID` で繋がる可能性が上がるよ🧵✨
（相手が対応してれば最強💪）

---

## 7) “標準の世界”に寄せたい人へ：traceparent（W3C Trace Context）🧭✨

サービスが増えてくると、requestIdだけじゃなくて **分散トレース**も欲しくなるよね😊
そのときの標準が **W3C Trace Context**で、`traceparent` / `tracestate` が定義されてるよ🌐 ([W3C][1])

OpenTelemetryのJSドキュメントでも、Nodeでは `AsyncLocalStorage` や `async_hooks` でコンテキスト伝播する話が出てるよ🧵 ([OpenTelemetry][3])
（つまり：**ログに traceId を出す**と、ログ↔トレースの相互参照がしやすくなる😍）

### ⚠️ちょい最新メモ（2026）

OpenTelemetry JSは Nodeのセキュリティ話題（async_hooks周り）について声明を出してるよ。計測系を入れてる場合は、追従アップデート意識すると安心だよ〜🛡️ ([OpenTelemetry][9])

---

## 8) requestIdログ設計のチェックリスト✅🧾✨

### ✅ ログに入れる最低限（この章のコア）

* `requestId`
* `message`
* `level`
* `ts`（ISO文字列）
* `event`（任意：`"http.in"`, `"db.query"`, `"http.out"` みたいに分類できると神✨）

### ✅ エラー時はこう入れる（Errorモデリングと接続）💥🧠

* `requestId` は **絶対**入れる
* `error.name`, `error.message`（stackは環境に応じて）
* もしアプリ標準エラー（domain/infra/bug）に正規化してるなら、`error.type` / `error.code` も入れると最強💪✨

---

## 9) ミニ演習📝：ログを“一本道”にしてみよう🧵🚶‍♀️

### お題🎀

「プロフィール更新API」を想像してね😊
流れはこんな感じ：

1. `PATCH /api/profile` を受ける（入口）🚪
2. DB更新する（成功/失敗あり）🗃️
3. 外部の通知APIを叩く（失敗することがある）📨
4. どこで失敗しても、**同じrequestIdで追える**ようにログを設計する🧵✨

### やること✅

* (1) 入口で `X-Request-ID` を発行してレスポンスに返す
* (2) DB処理ログに `requestId` を付ける
* (3) 外部API呼び出しに `X-Request-ID` を付ける
* (4) 失敗時ログにも `requestId` を付ける（これが一番大事！）

### ゴール🌈

障害が起きても `requestId` で検索したら、
「入口→DB→外部API→失敗地点」まで **1本の線で出る**こと🧵😍

---

## 10) AI活用🤖✨（Copilot / Codex想定）

そのままコピって使えるプロンプト集だよ〜💗

### 🤖 ① ミドルウェア生成

* 「Expressで `X-Request-ID` を受け取り、なければUUIDを生成してレスポンスにも返すミドルウェアをTypeScriptで書いて。AsyncLocalStorageで requestId を保持して。」

### 🤖 ② ログ項目の監査👮‍♀️

* 「このログ設計で“追跡できない穴”がないかレビューして。特に非同期や外部API呼び出しで requestId が途切れないか確認して。」

### 🤖 ③ 事故シナリオ作り😱➡️🧵

* 「外部通知APIがタイムアウトするケースで、調査担当が requestId で追えるログの例を10行くらい作って。」

### 🤖 ④ 命名統一✨

* 「requestId / correlationId / traceId の命名をチームで混乱しないように、命名規約案を3つ出してメリデメ比較して。」

---

## 今日のまとめ🎀✨

* requestIdは「ログを一本道にする」ための最強アイテム🧵😍
* **入口で発行 → レスポンスに返す → 下流に伝播 → 全ログに付ける** が黄金ルール✨
* Nodeなら **AsyncLocalStorage** で requestId を迷子にしない設計が作れるよ🧠🧵 ([Node.js][7])
* 将来は `traceparent`（W3C Trace Context）で traceId まで出すと、分散でも追いやすくなるよ🌐 ([W3C][1])

---

次の章（第29章）は、タイムアウト/キャンセル/リトライで「落ちる現実」に強くなるやつだよ⏳🛑🔁✨

[1]: https://www.w3.org/TR/trace-context-2/?utm_source=chatgpt.com "Trace Context Level 2"
[2]: https://docs.cloud.google.com/trace/docs/trace-context?utm_source=chatgpt.com "Trace context"
[3]: https://opentelemetry.io/docs/languages/js/context/?utm_source=chatgpt.com "Context"
[4]: https://devcenter.heroku.com/articles/http-request-id?utm_source=chatgpt.com "HTTP Request IDs"
[5]: https://http.dev/x-request-id?utm_source=chatgpt.com "X-Request-ID - Expert Guide to HTTP headers"
[6]: https://github.com/pinojs/pino-http?utm_source=chatgpt.com "pinojs/pino-http: 🌲 high-speed HTTP logger for Node.js"
[7]: https://nodejs.org/api/async_context.html?utm_source=chatgpt.com "Asynchronous context tracking | Node.js v25.3.0 ..."
[8]: https://fastify.io/docs/v5.4.x/Reference/Logging/?utm_source=chatgpt.com "Logging"
[9]: https://opentelemetry.io/blog/2026/oteljs-nodejs-dos-mitigation/?utm_source=chatgpt.com "OpenTelemetry JS Statement on Node.js DOS Mitigation"
