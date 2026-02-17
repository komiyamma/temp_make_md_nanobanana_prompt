# 第03章：コンテナで見えにくいポイントを先に知る 📦🕳️

## ① 今日のゴール 🎯

* 「コンテナだと**デバッグが見えにくくなる理由**」を3つ言えるようになる 😵‍💫
* **“手がかり（ログ）をコンテナの中に置かない”**の意味が腹落ちする 📣
* 落としても `logs` で追えて、「どこで何が起きたか」を説明できる 👀✅

---

## ② まずは絵でつかむ 🖼️

![The Flow of Logs in Containers](./picture/docker_observability_ts_study_003_01_log_flow.png)

コンテナ時代の基本ルートはこれ👇

アプリ（Node/TS）
→ `stdout / stderr`（標準出力/標準エラー）
→ Docker が回収（ログドライバ）
→ `docker logs` / `docker compose logs` で見る 🔍

「**アプリがコンテナ内ファイルにログを書いても、外からは見えにくい**」が最初の落とし穴です 🙈
“ログはイベントストリームとして `stdout` に出す” という考え方は Twelve-Factor でも明言されています。([12factor.net][1])
そして Docker は基本的に `stdout`/`stderr` に出たものをログとして扱います。([dash0.com][2])

---

## ③ コンテナで見えにくい「3つの正体」🧩

![Three Container Log Challenges](./picture/docker_observability_ts_study_003_02_three_challenges.png)

### A) 「入るのが面倒」🚪😮‍💨

* つい `docker exec` で中に入りたくなる（でも毎回やるのはしんどい）
* しかも本番に近い環境ほど、シェルが無い/ツールが無い…みたいになりがち 😇
  ✅ 対策：**まずログで追う**（“入らないで解決”を基本にする）📣

### B) 「再現が短命」⏳💨

* コンテナは落ちたら再起動、作り直し…で、状態がスッと消える
* 「中で一時的に直した」とか「中のファイルにメモした」は、次の作り直しで消えがち 🫠
  ✅ 対策：**証拠は外に出す（stdout/stderr）**。([12factor.net][1])

### C) 「数が増える」👯‍♂️📈

* サービスが増える / レプリカが増えると、ログが混ざってカオス 🤯
  ✅ 対策：`docker compose logs <service>` で**サービス単位に絞る**。`--tail` や `--since` で**必要な範囲だけ**見る。([Docker Documentation][3])

---

## ④ 今日の最重要ルール 🧠📌

![The Stdout Rule](./picture/docker_observability_ts_study_003_03_stdout_rule.png)

### ✅ 「コンテナの中に“手がかり”を置かない」＝ログは `stdout/stderr` に出す 📣🖥️

* Node では `console.log` は `stdout`、`console.error` は `stderr` に出ます。([Node.js][4])
* Docker はデフォルトで `json-file` ログドライバを使い、コンテナログを保持します。([Docker Documentation][5])
* だから「アプリ → stdout/stderr → Docker が拾う → logsで見える」が最短ルートです 🔥

---

## ⑤ ハンズオン 🛠️：ログの出口を “console.log / console.error” に統一する 📣

ここは「設計ガチ勢のロガー」を作る回じゃないです 🙆‍♂️
**“出す場所を統一して、落ちても追える”**を体験する回です 😆

## 0) ファイル構成（そのまま作ってOK）📁

* `obs-ch3/`

  * `compose.yml`
  * `Dockerfile`
  * `package.json`
  * `tsconfig.json`
  * `src/`

    * `index.ts`
    * `log.ts`

---

## 1) `src/log.ts`（ログの出口を1本化）🔌

![Log Splitting Code Logic](./picture/docker_observability_ts_study_003_04_log_split.png)

```ts
type Level = "INFO" | "ERROR";

function format(meta: Record<string, unknown>) {
  const pairs = Object.entries(meta).map(([k, v]) => `${k}=${String(v)}`);
  return pairs.length ? " " + pairs.join(" ") : "";
}

function write(level: Level, msg: string, meta: Record<string, unknown> = {}) {
  const time = new Date().toISOString();
  const line = `${time} ${level} ${msg}${format(meta)}`;

  // 重要：INFOはstdout、ERRORはstderrに寄せる 📣
  if (level === "ERROR") console.error(line);
  else console.log(line);
}

export const info = (msg: string, meta?: Record<string, unknown>) =>
  write("INFO", msg, meta);

export const error = (msg: string, meta?: Record<string, unknown>) =>
  write("ERROR", msg, meta);
```

ポイントはこれだけ👇

* “どこに出すか” を **このファイルに集約** ✅
* `INFO` は `console.log`、`ERROR` は `console.error` ✅（Nodeの標準出力/標準エラーの考え方そのまま）([Node.js][4])

---

## 2) `src/index.ts`（落としても追える実験サーバ）🧪

```ts
import http from "node:http";
import { randomUUID } from "node:crypto";
import { info, error } from "./log.js";

const port = Number(process.env.PORT ?? 3000);

const server = http.createServer(async (req, res) => {
  const start = Date.now();
  const reqId = randomUUID();

  const method = req.method ?? "GET";
  const url = new URL(req.url ?? "/", `http://${req.headers.host ?? "localhost"}`);
  const path = url.pathname;

  try {
    if (path === "/ping") {
      res.writeHead(200, { "content-type": "application/json", "x-request-id": reqId });
      res.end(JSON.stringify({ ok: true }));
      info("request", { reqId, method, path, status: 200, ms: Date.now() - start });
      return;
    }

    if (path === "/boom") {
      // 例外を投げる（落ちないが 500 を返す）💥
      throw new Error("boom! for observability practice");
    }

    if (path === "/exit") {
      // プロセス自体を落とす（落ちても logs で追える体験）💀
      res.writeHead(200, { "content-type": "text/plain", "x-request-id": reqId });
      res.end("bye\n");
      info("process exiting by /exit", { reqId });

      setTimeout(() => process.exit(1), 50);
      return;
    }

    res.writeHead(404, { "content-type": "application/json", "x-request-id": reqId });
    res.end(JSON.stringify({ error: "not found" }));
    info("request", { reqId, method, path, status: 404, ms: Date.now() - start });
  } catch (e) {
    error("request failed", {
      reqId,
      method,
      path,
      status: 500,
      ms: Date.now() - start,
      err: (e as Error).message,
    });

    res.writeHead(500, { "content-type": "application/json", "x-request-id": reqId });
    res.end(JSON.stringify({ error: "internal error", reqId }));
  }
});

server.listen(port, () => {
  info("server started", { port });
});
```

---

## 3) `package.json`（依存は最小）📦

※ TypeScript の安定版は 5.9 系、6.0 はベータが出ています。([NPM][6])

```json
{
  "name": "obs-ch3",
  "private": true,
  "type": "module",
  "scripts": {
    "build": "tsc -p tsconfig.json",
    "start": "node dist/index.js"
  },
  "devDependencies": {
    "@types/node": "^25.0.0",
    "typescript": "^5.9.0"
  }
}
```

## 4) `tsconfig.json`（最小）🧩

```json
{
  "compilerOptions": {
    "target": "ES2023",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "outDir": "dist",
    "rootDir": "src",
    "strict": true
  }
}
```

---

## 5) `Dockerfile`（ビルドして実行）🐳

Node は 24 が Active LTS、25 は Current（奇数系は LTS になりません）なので、まずは LTS を使うのが無難です。([Node.js][7])

```dockerfile
FROM node:24-bookworm-slim AS build
WORKDIR /app

COPY package.json ./
RUN npm install

COPY tsconfig.json ./
COPY src ./src
RUN npm run build

FROM node:24-bookworm-slim
WORKDIR /app
ENV NODE_ENV=production
COPY --from=build /app/dist ./dist
CMD ["node", "dist/index.js"]
```

---

## 6) `compose.yml`（ログを見る道具もセット）🧰

```yml
services:
  api:
    build: .
    ports:
      - "3000:3000"
```

---

## ⑥ 動かす（コマンド）🏃‍♂️💨

## 1) 起動する 🚀

```bash
docker compose up --build -d
docker compose ps
```

## 2) 叩く（Windowsなら `curl.exe` が安心）🪟🔧

```bash
curl.exe http://localhost:3000/ping
curl.exe http://localhost:3000/boom
```

## 3) ログを見る 👀（まずは “絞って→追う” が正義）

```bash
docker compose logs api --tail 50 --follow --timestamps
```

`--tail` / `--follow` / `--since` などのオプションは公式でも整理されています。([Docker Documentation][3])

---

## ⑦ “落としても logs で追える” を体験する 💥➡️🔍

![Post-Mortem Log Analysis](./picture/docker_observability_ts_study_003_05_post_mortem.png)

## 1) プロセスを落とす 💀

```bash
curl.exe http://localhost:3000/exit
```

## 2) コンテナ状態を見る 👀

```bash
docker compose ps -a
```

## 3) 死因（ログ）を拾う 🕵️‍♂️

```bash
docker compose logs api --tail 200 --timestamps
```

ここで「最後に何が起きた？」が追えたら勝ちです 🏆✨
（Docker はデフォルトで `json-file` ログドライバなので、落ちてもログ自体は追えることが多いです）([Docker Documentation][5])

---

## ⑧ つまづきポイント（よくある）🪤😵‍💫

1. **PowerShell の `curl` が別物問題**
   　`curl` が `Invoke-WebRequest` の別名になることがあるので、困ったら `curl.exe` に固定しちゃうのがラクです 🧠🪟

2. **ログが何も出ない**
   　アプリが「ファイルにだけ」書いてると、`docker logs` は静か…🙈
   　→ **まず `console.log/error` に寄せる**（今回やったやつ）📣

3. **ログが多すぎて読めない**
   　→ `--tail 50` + `--follow` の組み合わせが神です 🙏✨([Docker Documentation][3])

---

## ⑨ ミニ課題（15分）⏳✅

次の3つをやって、スクショじゃなく「文章」で説明してみてください ✍️😆

1. `/ping` を叩いた時のログ1行を抜き出す 🧾
2. `/boom` を叩いた時に **ERROR が stderr 側**に出てる雰囲気を確認（`console.error` を使ってるだけでもOK）🔴
3. `/exit` で落とした後に、`docker compose logs api --tail 200` で「最後のメッセージ」を見つける 🕵️‍♂️

---

## ⑩ AIに投げるプロンプト例（コピペOK）🤖📋

* 「`src/log.ts` を、`INFO` は `stdout`、`ERROR` は `stderr` に出し分けつつ、`reqId/method/path/status/ms` を毎回同じ順番で出すように整えて」
* 「`docker compose logs` で、直近5分だけ見たい。`--since` を使ったコマンドを3パターン出して（相対時間/絶対時間/サービス指定）」([Docker Documentation][3])
* 「落ちた時に “最後に出るべきログ” のチェックリストを5個作って（初心者向け）」

---

## ✅ この章のまとめ 🧠✨

* コンテナは **入るのが面倒**・**短命**・**数が増える**で見えにくい 📦🕳️
* だから最初にやるのは **stdout/stderr に証拠を出す**こと 📣([12factor.net][1])
* `docker compose logs --tail --follow` で「読める量」にして追う 👀([Docker Documentation][3])

次の章（第4章）で、この“実験場ミニAPI”をちゃんと「観測の実験台」として育てていきましょ〜🧪🚀

[1]: https://12factor.net/logs?utm_source=chatgpt.com "Treat logs as event streams"
[2]: https://www.dash0.com/guides/mastering-docker-logs?utm_source=chatgpt.com "Mastering Docker Logs: A Comprehensive Tutorial"
[3]: https://docs.docker.com/reference/cli/docker/compose/logs/?utm_source=chatgpt.com "docker compose logs"
[4]: https://nodejs.org/api/console.html?utm_source=chatgpt.com "Console | Node.js v25.6.1 Documentation"
[5]: https://docs.docker.com/engine/logging/configure/?utm_source=chatgpt.com "Configure logging drivers"
[6]: https://www.npmjs.com/package/typescript?utm_source=chatgpt.com "TypeScript"
[7]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
