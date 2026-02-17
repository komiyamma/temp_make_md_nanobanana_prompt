# 第05章：ログの基本：まずは“標準出力”に出す 📣🖥️

## ① 今日のゴール 🎯

* 「コンテナのログは **標準出力（stdout）/ 標準エラー（stderr）** に出すのが基本！」を腹落ちさせる 😆
* **起動ログ**・**リクエストログ**・**エラーログ** を分けて出せるようになる 🧾✨
* コンテナを再起動しても（同じコンテナなら）ログを追える感覚をつかむ 🔁👀

---

## ② 図（1枚）🖼️：ログが拾われる道すじ

![Log Pickup Flow](./picture/docker_observability_ts_study_005_01_log_pickup_flow.png)

```text
(アプリ) console.log / console.error
        │
        ▼
stdout / stderr  ← ここに出すのが超大事！📣
        │
        ▼
Docker が回収（ログドライバ経由）🧲
        │
        ▼
docker logs / docker compose logs で見える 👀
```

Docker はコンテナ内プロセスの stdout/stderr を回収してログとして扱います。([Docker Documentation][1])
Node.js 側でも、console.log は stdout、console.error は stderr に出る想定で使えます。([Node.js][2])

---

## ③ 手を動かす（手順 5〜10個）🛠️🚀

ここでは「前章のミニAPI」に、**ログをちゃんと出す仕組み**を足します😊
（まだ無い人向けに、最小構成も丸ごと載せます📦）

---

### ステップ1：ファイル構成（最小）📁

```text
observability-lab/
  compose.yml
  Dockerfile
  package.json
  tsconfig.json
  src/
    server.ts
    logger.ts
```

---

### ステップ2：logger.ts を作る（stdout / stderr を分ける）🎚️🟢🔴

![Logger Split Logic](./picture/docker_observability_ts_study_005_02_logger_split.png)

ポイントは超シンプル👇

* 情報＝stdout（console.log）
* エラー＝stderr（console.error）

```ts
// src/logger.ts
type LogLevel = "INFO" | "ERROR";

function nowIso() {
  return new Date().toISOString();
}

export function logInfo(message: string, fields: Record<string, unknown> = {}) {
  const line = formatLine("INFO", message, fields);
  // stdout
  console.log(line);
}

export function logError(message: string, fields: Record<string, unknown> = {}) {
  const line = formatLine("ERROR", message, fields);
  // stderr
  console.error(line);
}

function formatLine(level: LogLevel, message: string, fields: Record<string, unknown>) {
  // まずは「読みやすい1行」に寄せる（JSON化は第9章でやる想定）🧱
  const base = `time=${nowIso()} level=${level} msg="${escapeQuotes(message)}"`;
  const extras = Object.entries(fields)
    .map(([k, v]) => `${k}=${escapeQuotes(String(v))}`)
    .join(" ");
  return extras ? `${base} ${extras}` : base;
}

function escapeQuotes(s: string) {
  return s.replaceAll(`"`, `\\"`);
}
```

Node.js の console は stdout/stderr を使い分ける設計で説明されています。([Node.js][3])

---

### ステップ3：server.ts に「起動ログ」「リクエストログ」「エラーログ」を入れる 🧾🔥

![Logging Checkpoints](./picture/docker_observability_ts_study_005_03_logging_checkpoints.png)

* 起動時：boot ログ
* リクエスト：1リクエストにつき1行（今は“超入門版”）
* エラー：例外を拾って stderr に吐く

```ts
// src/server.ts
import express from "express";
import { logError, logInfo } from "./logger.js";

const app = express();
app.use(express.json());

// 🧾 リクエストログ（超入門）
// status と ms を finish で拾うのがポイント 👀
app.use((req, res, next) => {
  const start = Date.now();

  res.on("finish", () => {
    const ms = Date.now() - start;
    logInfo("request", {
      method: req.method,
      path: req.originalUrl,
      status: res.statusCode,
      ms,
    });
  });

  next();
});

// 前章の想定：/ping と /slow（無ければこれでOK）🐢
app.get("/ping", (_req, res) => {
  res.json({ ok: true });
});

app.get("/slow", async (_req, res) => {
  await new Promise((r) => setTimeout(r, 800));
  res.json({ ok: true, slow: true });
});

// わざと落とす（/boom）💥
app.get("/boom", () => {
  throw new Error("BOOM! intentional error");
});

// 🧯 エラーハンドラ（ここが “stderr に出す” 本丸）
app.use((err: unknown, req: express.Request, res: express.Response, _next: express.NextFunction) => {
  const e = err instanceof Error ? err : new Error("unknown error");

  logError("unhandled error", {
    method: req.method,
    path: req.originalUrl,
    name: e.name,
    message: e.message,
    // stack は長くなるので好みで（まずは出してOK）📌
    stack: e.stack ?? "",
  });

  res.status(500).json({ ok: false });
});

const port = Number(process.env.PORT ?? 3000);
app.listen(port, () => {
  logInfo("server started", { port });
});
```

---

### ステップ4：package.json / tsconfig.json（最小）⚙️

```json
{
  "name": "observability-lab",
  "private": true,
  "type": "module",
  "scripts": {
    "build": "tsc -p tsconfig.json",
    "start": "node dist/server.js"
  },
  "dependencies": {
    "express": "^4.19.2"
  },
  "devDependencies": {
    "@types/express": "^4.17.21",
    "@types/node": "^22.10.0",
    "typescript": "^5.7.0"
  }
}
```

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ES2022",
    "moduleResolution": "Bundler",
    "outDir": "dist",
    "rootDir": "src",
    "strict": true,
    "esModuleInterop": true
  },
  "include": ["src"]
}
```

（依存バージョンは例です。ここは “動けばOK” で進めて大丈夫👌）

---

### ステップ5：Dockerfile（ログはファイルに出さない！）📦🧠

```dockerfile
FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci
COPY tsconfig.json ./
COPY src ./src
RUN npm run build

FROM node:22-alpine
WORKDIR /app
ENV NODE_ENV=production
COPY --from=build /app/node_modules ./node_modules
COPY --from=build /app/dist ./dist
EXPOSE 3000
CMD ["node", "dist/server.js"]
```

---

### ステップ6：compose.yml（起動して logs で見る）👀🏃‍♂️

```yaml
services:
  api:
    build: .
    ports:
      - "3000:3000"
    environment:
      - PORT=3000
```

---

### ステップ7：起動して叩く 🚀🔨

```bash
docker compose up -d --build
```

ブラウザや curl で叩く👇

* /ping ✅
* /slow 🐢
* /boom 💥

---

### ステップ8：ログを見る（まずはこれだけ覚えればOK）👀✨

```bash
docker compose logs -f api
```

docker compose logs はサービスのログを見れます（follow や tail などオプションあり）([Docker Documentation][4])

---

## ④ 期待する出力（例）🧾✅

だいたいこんな感じの1行ログが並べば勝ちです😆

```text
api-1  | time=2026-02-13T04:12:10.123Z level=INFO msg="server started" port=3000
api-1  | time=2026-02-13T04:12:15.008Z level=INFO msg="request" method=GET path=/ping status=200 ms=2
api-1  | time=2026-02-13T04:12:20.552Z level=INFO msg="request" method=GET path=/slow status=200 ms=804
api-1  | time=2026-02-13T04:12:25.100Z level=ERROR msg="unhandled error" method=GET path=/boom name=Error message=BOOM! intentional error stack=Error: BOOM! intentional error ...
api-1  | time=2026-02-13T04:12:25.101Z level=INFO msg="request" method=GET path=/boom status=500 ms=1
```

---

## ⑤ チェック：コンテナ再起動しても見える？🔁👀

![Restart vs Down](./picture/docker_observability_ts_study_005_04_restart_vs_down.png)

「ログって消えるの？」を体験します😊

```bash
docker compose restart api
docker compose logs api --tail=20
```

* restart は「同じコンテナを再起動」なので、普通はログをさかのぼれます ✅
* ただし **docker compose down** でコンテナを消すと、ログも一緒に消えます（ログの置き場所がコンテナに紐づくため）⚠️
  ※このへんは “運用” で大事になるので、まずは「消える操作がある」だけ覚えればOK👍

また、docker logs は stdout/stderr を表示します。([docs.docker.jp][5])

---

## ⑥ つまづきポイント（3つ）🪤😵‍💫

![Common Log Mistakes](./picture/docker_observability_ts_study_005_05_common_mistakes.png)

1. **ログをファイルに書いてしまう** 📄➡️💥
   コンテナ内のファイルは「いつでも捨てられる」ので、まずは stdout/stderr に出すのが正解です📣（あとで必要なら“集める仕組み”を足す）

2. **console.log を消したくなる** 😇
   気持ちは分かる！でも最初は **“見えること”が正義**。
   後の章で「量を減らす」「JSON化」「収集して検索」へ進みます🧱🔍

3. **エラーがログに出ない** 🫥
   Express はエラーハンドラを書かないと「落ちた理由」が行方不明になりがち。
   この章の error handler は、とにかく“逃さない”のが目的🧯

---

## ⑦ ミニ課題（15分）⏳🧩

次を満たすように改造してみてね😊

* /ping を叩いたら、**必ず1行** リクエストログが出る ✅
* /boom を叩いたら、**ERROR が stderr 側**に出てる（＝console.error 経由）🔥
* 起動ログに **service=api** を追加してみる（fields に足すだけ）🏷️

---

## ⑧ AIに投げるプロンプト例（コピペOK）🤖📋

Copilot / Codex にそのまま貼ってOK👇

```text
TypeScript + Express の超入門ログを作りたいです。
要件:
- console.log は INFO (stdout)、console.error は ERROR (stderr)
- 起動ログ / リクエストログ / エラーログを出す
- ログは1行の key=value 形式（time, level, msg, method, path, status, ms など）
- Express のエラーハンドラで例外を拾って stderr に出す
src/logger.ts と src/server.ts の完成コードを提案してください。
```

---

## ここまでで得られる感覚 💡✨

* 「コンテナのログは stdout/stderr に出すと、Docker が拾ってくれる」📣🧲
* 「docker compose logs で全部見える」👀
* 「INFO と ERROR を分けると、後で“重要ログだけ拾う”がやりやすい」🎚️

次章（第6章）では、このログを **追いかける・絞る** 操作に集中して、“最短で目的ログを掘り当てる”練習をします🏃‍♂️🔎

[1]: https://docs.docker.com/engine/logging/?utm_source=chatgpt.com "Logs and metrics"
[2]: https://nodejs.org/en/learn/command-line/output-to-the-command-line-using-nodejs?utm_source=chatgpt.com "Output to the command line using Node.js"
[3]: https://nodejs.org/api/console.html?utm_source=chatgpt.com "Console | Node.js v25.6.1 Documentation"
[4]: https://docs.docker.com/reference/cli/docker/compose/logs/?utm_source=chatgpt.com "docker compose logs"
[5]: https://docs.docker.jp/engine/reference/commandline/logs.html?utm_source=chatgpt.com "docker logs — Docker-docs-ja 24.0 ドキュメント"
