# 第04章：“観測の実験場”ミニAPIを用意する 🧪🚀

この章で作るのは「わざと遅い」を再現できる、超ミニマムAPIです😊
次章以降のログ🧾・メトリクス📈・ヘルスチェック💚は、この“実験場”にどんどん足していきます！

---

## ① 今日のゴール 🎯

* Docker Composeで **APIが起動**する 📦✅
* `GET /ping` が **常にOK**を返す 🏓
* `GET /slow` が **わざと遅い**（待たせる）を再現できる 🐢
* ついでに、Windowsから叩いて **動作確認**できる 🪟💪

---

## ② 図（1枚）🖼️

（ざっくりこういう関係になります👇）

```text
Windowsのブラウザ / curl.exe
        |
        |  http://localhost:3000
        v
Dockerコンテナ（Node/TSのミニAPI）
        |
        |  /ping → すぐ返す
        |  /slow → わざと待ってから返す
        v
標準出力ログ（次章以降で育てる🧾）
```

---

## ③ 手を動かす（手順 5〜10個）🛠️

ここでは **Node.jsは安定運用向きのActive LTS（v24系）**をベースに固定します（実務でも安心枠）([Node.js][1])
TypeScriptは **安定版5.9系**でOK（6.0はBetaが出たばかりなので教材は安定版でいきます）([typescriptlang.org][2])
Composeファイル名は **`compose.yaml`** が今どきの推奨です([Docker Documentation][3])

---

### 手順1）フォルダ作成 📁✨

VS Codeで新規フォルダを作って開きます。

例：`obs-mini-api`

---

### 手順2）最低限のファイル構成を作る 🧱

最終的にこうなります👇

```text
obs-mini-api/
  compose.yaml
  Dockerfile
  package.json
  tsconfig.json
  src/
    server.ts
```

---

### 手順3）package.json を用意 📦

プロジェクト直下に `package.json` を作成：

```json
{
  "name": "obs-mini-api",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "tsx watch src/server.ts",
    "start": "node dist/server.js",
    "build": "tsc -p tsconfig.json"
  },
  "dependencies": {
    "express": "^4.19.2"
  },
  "devDependencies": {
    "@types/express": "^4.17.21",
    "@types/node": "^24.0.0",
    "tsx": "^4.20.0",
    "typescript": "^5.9.0"
  }
}
```

ポイント😊

* `dev` は **TSをそのまま実行＆watch**（実験場に最高）
* `build/start` は将来「本番っぽい形」に寄せたくなった時用（今は使わなくてもOK）

---

### 手順4）tsconfig.json を作る 🧠

```json
{
  "compilerOptions": {
    "target": "ES2023",
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "outDir": "dist",
    "rootDir": "src",
    "strict": true,
    "skipLibCheck": true
  },
  "include": ["src"]
}
```

---

### 手順5）ミニAPI本体（/ping と /slow）を書く 🧪

`src/server.ts` を作成：

```ts
import express from "express";

const app = express();
app.use(express.json());

const port = Number(process.env.PORT ?? 3000);

// 🏓 常にOK（観測の“基準点”）
app.get("/ping", (_req, res) => {
  res.status(200).json({ ok: true, message: "pong" });
});

// 🐢 わざと遅くする（観測の“再現装置”）
// /slow?ms=1200 みたいに指定できるようにする
app.get("/slow", async (req, res) => {
  const raw = String(req.query.ms ?? "");
  const requested = Number.parseInt(raw, 10);

  // 変な値が来ても暴れないようにガード（超入門の設計ポイント✨）
  const ms = Number.isFinite(requested) ? requested : 800;
  const clamped = Math.min(Math.max(ms, 0), 10_000); // 0〜10秒に制限

  await new Promise<void>((r) => setTimeout(r, clamped));
  res.status(200).json({ ok: true, waitedMs: clamped });
});

// 終了時に落ち着いて終わる（後でログにも効く）
const server = app.listen(port, () => {
  console.log(`[boot] api listening on http://localhost:${port}`);
});

process.on("SIGTERM", () => {
  console.log("[shutdown] SIGTERM received. closing server...");
  server.close(() => {
    console.log("[shutdown] server closed.");
    process.exit(0);
  });
});
```

ここ、地味に大事😎

* `/slow` は **「遅い」症状を確実に作れる**ので、後のログ・メトリクスでめちゃ便利！
* `clamped` は“設計超入門”の第一歩：**変な入力が来ても壊れない**🛡️

---

### 手順6）Dockerfile を作る 🐳

```dockerfile
FROM node:24-slim

WORKDIR /app

## 依存関係だけ先に入れる（キャッシュ効いて速い💨）
COPY package.json ./
RUN npm install

## ソースを配置
COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]
```

---

### 手順7）compose.yaml を作る 🧩

```yaml
services:
  api:
    build: .
    ports:
      - "3000:3000"
    environment:
      - PORT=3000
      # Windowsのバインドマウントでwatchが効きづらい時の保険🔥
      - CHOKIDAR_USEPOLLING=true
    volumes:
      - .:/app
      - node_modules:/app/node_modules

volumes:
  node_modules: {}
```

ここも大事ポイント😊

* `volumes` の `node_modules` は「Windows側のnode_modules混入」で地獄になりがちなのを避ける保険🧯
* `CHOKIDAR_USEPOLLING=true` は **watchが反応しない**時の強い味方

---

### 手順8）起動する ▶️

VS Codeのターミナルで：

```bash
docker compose up --build
```

---

### 手順9）動作確認する ✅

PowerShellだと `curl` が別物だったりするので、まずは **`curl.exe`** 推奨です🪟👍

```bash
curl.exe http://localhost:3000/ping
```

期待する返り（例）：

```json
{"ok":true,"message":"pong"}
```

次に遅い方：

```bash
curl.exe "http://localhost:3000/slow?ms=1200"
```

期待する返り（例）：

```json
{"ok":true,"waitedMs":1200}
```

---

### 手順10）止める ⏹️

```text
Ctrl + C
```

---

## ④ 期待する出力（ログの例）🧾✨

`docker compose up` すると、だいたいこんな雰囲気が出ます👇

```text
api-1  | [boot] api listening on http://localhost:3000
```

（ログ編でここを育てます🌱 いまは“出てればOK”）

---

## ⑤ つまづきポイント（3つ）🪤

1. **3000番がすでに埋まってる** 🔥

* エラーっぽかったら、他アプリが使ってる可能性あり
* 対処：`compose.yaml` の `ports` を `"3001:3000"` に変えて、アクセスも `localhost:3001` にする

2. **PowerShellの `curl` が想定と違う** 😵

* 対処：**`curl.exe`** を使う（これが一番ラク）

3. **コード変更しても反映されない（watchが効かない）** 🫠

* まず `CHOKIDAR_USEPOLLING=true` が効いてるか確認
* それでもダメなら、一度止めて `docker compose up --build` で再起動（手早く確実）

---

## ⑥ ミニ課題（15分）⏳💪

次のどれか1つやってみてね😊（全部やってもOK！）

* 🧪 `/slow` に `?ms=` が無いとき、`800` じゃなくて `200` にしてみる
* 🎲 `/slow` を「800ms〜1200msのランダム」にしてみる
* 🏓 `/ping?name=komiyanma` みたいに渡したら、その名前を返すようにする（入力ガード付きで！）

---

## ⑦ AIに投げるプロンプト例（コピペOK）🤖📋

### A）“最小で正しい” slow を作りたい

```text
TypeScript + Expressで /slow を作りたいです。
要件：
- /slow?ms=1200 のようにms指定可能
- msが無い/変/負数/大きすぎる時は安全に丸める（0〜10000）
- 返り値は { ok: true, waitedMs: number }
実装例のコードだけ出してください。
```

### B）watchが効かない時の改善案が欲しい

```text
Docker ComposeでWindowsホストのバインドマウント上で tsx watch が反応しないことがあります。
CHOKIDAR_USEPOLLING以外の改善案（環境変数、composeの工夫、フォルダ構成の工夫）を、優先度順に箇条書きで出してください。
```

### C）次章（ログ）に備えて「最低限の1行ログ」を足したい

```text
今のExpress APIに“1行だけ”アクセスログを足したいです。
method, path, status, elapsedMs を1行で出すだけのミドルウェア案をください。
ログはconsole.logのみ、余計な依存は増やさない方向で。
```

---

ここまでできたら🎉
あなたは「遅い🐢」をいつでも再現できる“観測の実験場”を手に入れました！
次の章から、このAPIにログ🧾やメトリクス📈を“武装”していきます😆

[1]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
[2]: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-9.html?utm_source=chatgpt.com "Documentation - TypeScript 5.9"
[3]: https://docs.docker.com/reference/compose-file/?utm_source=chatgpt.com "Compose file reference"
