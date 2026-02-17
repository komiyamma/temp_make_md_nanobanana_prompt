# 第10章：リクエストID（相関ID）：1リクエストを追跡する 🧵🪪

ログが増えてくると、こうなるんだよね👇😵‍💫
「/slow を叩いたら遅い…でもどのログがその1回分？」
そこで **リクエストID（相関ID）** を付けると、ログが **“1本の糸”** でつながります🧵✨

---

## ① 今日のゴール 🎯

* 1つのHTTPリクエストに **reqId** を付けて返せる 🪪
* **同じreqId** を持つログだけを追って「この1回で何が起きたか」を読める 👀
* クライアントにも **X-Request-Id** を返して「問い合わせの合言葉」にできる 📞🧾

---

## ② 図（1枚）🖼️

![Request ID Thread Analogy](./picture/docker_observability_ts_study_010_01_request_id_thread.png)

```text
Client
  |  (X-Request-Id: abc...  あれば渡す / なければ空)
  v
API(Express)
  1) 受け取る or 作る (UUID)
  2) reqId を req / logger に紐付ける
  3) レスポンスにも X-Request-Id を返す
  4) 出るログ全部に reqId が乗る
  |
  v
Logs
  - reqId=abc... の行だけ拾えば、その1回分が全部読める 🧵
```

---

## ③ 手を動かす（手順 5〜10個）🛠️

ここでは **Express + pino + pino-http** を使って「reqIdを自動で紐付ける」最短ルートでいくよ🚀
（`pino-http` は `genReqId` でリクエストID生成を差し替えできる＆デフォルトが連番なので本番では変えたい、という事情もここで解消👍）([GitHub][1])

### 手順1：依存を入れる 📦

```bash
npm i express pino pino-http
npm i -D typescript tsx @types/node @types/express
```

### 手順2：ファイル構成（今回追加・変更する最小セット）🗂️

```text
.
├─ src/
│  ├─ app.ts
│  ├─ logger.ts
│  ├─ httpLogger.ts
│  └─ types/
│     └─ express.d.ts
├─ package.json
└─ tsconfig.json
```

### 手順3：logger（アプリ共通のロガー）🌲

`src/logger.ts`

```ts
import pino from "pino";

export const logger = pino({
  level: process.env.LOG_LEVEL ?? "info",
});
```

### 手順4：HTTPロガー + reqId 生成（ここが主役！）🧵🪪

![Request ID Generation Flow](./picture/docker_observability_ts_study_010_02_id_generation_flow.png)

`src/httpLogger.ts`

```ts
import pinoHttp from "pino-http";
import { randomUUID } from "node:crypto";
import { logger } from "./logger.js";

// 1) x-request-id が来てたらそれを採用
// 2) 無ければ UUID を作る
// 3) レスポンスヘッダにも返す
export const httpLogger = pinoHttp({
  logger,
  quietReqLogger: true, // req.log は reqId だけをバインド（ログがスリムになる）
  genReqId(req, res) {
    const header = req.headers["x-request-id"];
    const existing = Array.isArray(header) ? header[0] : header;

    const id = existing && existing.length > 0 ? existing : randomUUID();
    res.setHeader("X-Request-Id", id);
    return id;
  },
});
```

`crypto.randomUUID()` は RFC 4122 の v4 UUID を暗号学的な乱数で生成するので、reqId用途にちょうど良いです🧬✨（Node.js では v14.17.0 / v15.6.0 で追加）([Node.js][2])
（2026年2月時点だと Node.js v24 が Active LTS なので、このへん普通に使えます👍）([Node.js][3])

### 手順5：型を足す（TypeScriptで怒られないように）🧠

`src/types/express.d.ts`

```ts
import "express-serve-static-core";
import type { Logger } from "pino";

declare module "express-serve-static-core" {
  interface Request {
    id: string;
    log: Logger;
  }
}
```

### 手順6：アプリに組み込む（middlewareとして app.use）🔌

![Pino Middleware Magic](./picture/docker_observability_ts_study_010_05_pino_middleware.png)

`src/app.ts`

```ts
import express from "express";
import { httpLogger } from "./httpLogger.js";
import { logger } from "./logger.js";

const app = express();
app.use(httpLogger);

// reqId を「毎回」返す（pino-http の genReqId で付いてる id を返すだけ）
app.use((req, res, next) => {
  res.setHeader("X-Request-Id", req.id);
  next();
});

app.get("/ping", async (req, res) => {
  req.log.info({ route: "/ping" }, "handler start 🏁");
  res.json({ ok: true });
});

app.get("/slow", async (req, res) => {
  req.log.info({ route: "/slow" }, "handler start 🐢");
  await new Promise((r) => setTimeout(r, 800));
  req.log.info({ route: "/slow" }, "handler end ✅");
  res.json({ ok: true, waitedMs: 800 });
});

// 例：エラー（reqId を持ったままエラーが追える）
app.get("/boom", async (req, res) => {
  req.log.warn({ route: "/boom" }, "about to explode 💥");
  throw new Error("boom!");
});

// Express のエラーハンドラ（最後に置く）
app.use((err: unknown, req: express.Request, res: express.Response, _next: express.NextFunction) => {
  req.log.error({ err }, "request failed ❌");
  res.status(500).json({ error: "internal_error", reqId: req.id });
});

const port = Number(process.env.PORT ?? 3000);
app.listen(port, () => logger.info({ port }, "server started 🚀"));
```

> メモ：Express 5 系は安定版として前に進んでいて、公式サイトでも v5 ラインの案内がまとまっています🧭([expressjs.com][4])
> （この章のコードは Express 4/5 どちらでもほぼ同じ感覚で動きます👌）

### 手順7：起動（開発）▶️

`package.json` の例（必要なら）

```json
{
  "type": "module",
  "scripts": {
    "dev": "tsx watch src/app.ts"
  }
}
```

起動：

```bash
npm run dev
```

### 手順8：動作確認（X-Request-Id が返る！）🧾

PowerShell なら `curl` が別物なことがあるので `curl.exe` を使うのが安全👍

```bash
curl.exe -i http://localhost:3000/ping
```

期待するレスポンス（例）👇

```text
HTTP/1.1 200 OK
X-Request-Id: 7f7d0c65-....-....
Content-Type: application/json; charset=utf-8

{"ok":true}
```

### 手順9：同じreqIdでログがつながるのを見る 🧵👀

`/slow` を叩いてみる：

```bash
curl.exe -i http://localhost:3000/slow
```

ログ例（雰囲気）👇 ※実際は `time` や順序は環境で変わるよ

```text
{"level":30,"time":...,"reqId":"7f7d0c65-...","route":"/slow","msg":"handler start 🐢"}
{"level":30,"time":...,"reqId":"7f7d0c65-...","route":"/slow","msg":"handler end ✅"}
{"level":30,"time":...,"reqId":"7f7d0c65-...","msg":"request completed", ...}
```

**ポイント**：同じ `reqId` の行だけ追えば、その1回の流れが読める！🧵✨

![Log Grouping by ID](./picture/docker_observability_ts_study_010_03_log_grouping.png)

---

## ④ つまづきポイント（3つ）🪤

1. **reqId がログに出ない** 😭
   → `console.log` じゃなくて `req.log.info(...)` を使ってる？（`req.log` は pino-http が作るやつ🌲）([GitHub][1])

2. **req.id / req.log が TypeScript で怒られる** 😡
   → `src/types/express.d.ts` を `tsconfig` の `include` 配下に置いてる？（`src/**` に入れておけばだいたいOK👌）

3. **reqId が連番っぽい** 😨
   → `pino-http` のデフォルトは連番フォールバックがあり得るので、`genReqId` で UUID に変えるのが安全（複数インスタンスだと特に）([GitHub][1])

---

## ⑤ ミニ課題（15分）⏳🎮

**課題A（5分）**：`/boom` を叩いて、レスポンスJSONに `reqId` が入るのを確認 💥🪪

```bash
curl.exe -i http://localhost:3000/boom
```

**課題B（10分）**：クライアントから reqId を“持ち込み”してみる 🧳

![Bring Your Own ID](./picture/docker_observability_ts_study_010_04_bring_your_own_id.png)

```bash
curl.exe -i -H "X-Request-Id: my-test-123" http://localhost:3000/slow
```

→ レスポンスヘッダでも `my-test-123` が返る？ログの `reqId` も同じ？🧵✨

---

## ⑥ AIに投げるプロンプト例（コピペOK）🤖📋

### 1) まずは“実装だけ”作ってもらう 🛠️

```text
Express + TypeScript で request id (x-request-id) を
「受け取る→なければ生成→レスポンスヘッダに返す→全ログに含める」
middleware 構成を提案して。pino + pino-http を使い、genReqId と型拡張(d.ts)も含めて。
```

### 2) “ログの形”を揃える（第9章の構造化ログと接続）🧱

```text
pino のログを JSON 構造化して、必ず
{ level, time, msg, reqId, route, status, ms }
が揃うようにしたい。pino-http の設定(customSuccessObject等)の例を出して。
```

### 3) もう一歩：別サービス呼び出しでも reqId を伝搬させる 🔁

```text
自サービス→別サービスへ fetch する時に、受け取った X-Request-Id を
そのまま下流にも送って“相関”を維持したい。Express ハンドラ内の具体例を出して。
```

---

## おまけ：さらに設計っぽくしたい人向け（任意）🎁🧠

![Async Local Storage Concept](./picture/docker_observability_ts_study_010_06_async_local_storage.png)

「深い関数まで `req` を渡したくない…😵‍💫」ってなったら、`AsyncLocalStorage` で **“今のreqId” をスレッドローカルみたいに扱う** という手もあります🧵🧠
（手軽だけど、非同期の扱いでハマりどころもあるので、まずはこの章の “req.log を渡す” 方式が安全👍）([dash0.com][5])

---

## 今日のまとめ 🧾✨

* **受け取る→なければ作る→返す** の3点セットが命 🧵🪪
* ログは **reqId で“1回分”に切り出す** と読みやすさが爆上がり👀✨
* UUID は `crypto.randomUUID()` が手軽で強い🧬([Node.js][2])

次の章（第11章）では、**例外・未処理Promise・プロセス終了**まで含めて「落ちた理由を絶対ログに残す🧯⚠️」に進めるよ！

[1]: https://github.com/pinojs/pino-http "GitHub - pinojs/pino-http:  high-speed HTTP logger for Node.js"
[2]: https://nodejs.org/api/crypto.html "Crypto | Node.js v25.6.1 Documentation"
[3]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
[4]: https://expressjs.com/2024/10/15/v5-release.html?utm_source=chatgpt.com "Introducing Express v5: A New Era for the Node. ..."
[5]: https://www.dash0.com/guides/contextual-logging-in-nodejs?utm_source=chatgpt.com "Contextual Logging Done Right in Node.js with ..."
