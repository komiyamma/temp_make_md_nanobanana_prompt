# 第25章：/health を作る：まずは“プロセスが生きてる”✅

この章は「生きてる？」を**最短・最軽量**で返すエンドポイントを作ります 😊
ここができると、監視ツールやコンテナ基盤が「落ちた／生きてる」を判断しやすくなります。たとえば Kubernetes だと、liveness（生存）判定が崩れると再起動のきっかけになります。([Kubernetes][1])

---

## ① 今日のゴール 🎯✅

* GET **/health** が **常に 200** で返る（＝プロセスが動いてるサイン）✨
* **重い処理は一切しない**（DB疎通・外部API呼び出し禁止🙅‍♂️）
  → “生存”チェックは軽く、という考え方が定番です。([Red Hat Docs][2])

---

## ② 図（1枚）🖼️

```text
(外) 監視/基盤   --->  GET /health  --->  (中) Nodeプロセス
     「返る？」                     「返すだけ！(200)」
      ✅ならOK                       ❌なら落ちてる/固まってる
```

---

## ③ 手を動かす（手順 5〜10個）🛠️🚀

### 0) 今回の前提（最新版の目安）🧠✨

* Node は **v24 が Active LTS**（2026-02 時点）([Node.js][3])
  ※この章のコードは v24 系でそのまま動きます 👍

---

## 1) ファイル構成 📁

こうしておくと、あとで /ready（第26章）を足すのがラクです 😆

```text
.
├─ compose.yml
├─ Dockerfile
└─ src
   ├─ server.ts
   └─ routes
      └─ health.ts
```

---

## 2) /health のルートを作る 🩺💚（200固定✅）

`src/routes/health.ts`

```ts
import { Router } from "express";

export const healthRouter = Router();

// 超軽量：200固定（プロセスが動いていればOK）
healthRouter.get("/health", (_req, res) => {
  // bodyは最小でOK（監視はステータスコードを見ることが多い）
  res.status(200).json({
    status: "ok",
    // 便利なオマケ：軽い情報だけ（重い処理はしない）
    uptimeSec: Math.floor(process.uptime()),
    timestamp: new Date().toISOString(),
  });
});
```

✅ポイント

* **process.uptime() / Date** は軽いのでOK（DBや外部はNG🙅‍♂️）
* 200固定なので、ここでは「依存が生きてるか」は見ません（それは次章 /ready でやる）🧩🔌

---

## 3) サーバに組み込む 🌐

`src/server.ts`

```ts
import express from "express";
import { healthRouter } from "./routes/health";

const app = express();

// もし既に /ping /slow /boom があるなら、その下に足してOK
app.use(healthRouter);

const port = Number(process.env.PORT ?? 3000);

// ✅ Dockerからアクセスされるので 0.0.0.0 で待ち受け（ExpressはこれでOK）
app.listen(port, () => {
  console.log(JSON.stringify({ level: "info", msg: "server started", port }));
});
```

---

## 4) Dockerfile（シンプル版）🐳📦

※すでに Dockerfile がある場合はスキップして、/health だけ追加でもOKです 🙆‍♂️
（ここでは “動く最小” を置きます）

`Dockerfile`

```dockerfile
FROM node:24-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

## TSビルドする構成ならここで build を実行
## RUN npm run build

EXPOSE 3000
ENV PORT=3000

CMD ["npm", "run", "dev"]
```

> Node 24 が LTS として提供されている状況（2026-02）を前提にしています。([Node.js][3])

---

## 5) compose.yml（ポートだけ確実に）🧩

`compose.yml`

```yml
services:
  api:
    build: .
    ports:
      - "3000:3000"
    environment:
      - PORT=3000
```

---

## 6) 起動する ▶️

```text
docker compose up -d --build
docker compose logs -f api
```

想定ログ（例）📣✨

```text
{"level":"info","msg":"server started","port":3000}
```

---

## 7) /health を叩いて確認する 🔍✅

PowerShell でOKです（Windowsの curl でいけます）💪

```text
curl http://localhost:3000/health
```

想定レスポンス（例）🎉

```json
{"status":"ok","uptimeSec":12,"timestamp":"2026-02-13T00:00:00.000Z"}
```

---

## 8) 「落ちてたら返らない」を体験する 💥👻

```text
docker compose stop api
curl http://localhost:3000/health
```

👉 当然、繋がらない（＝生存してない）を体験できます。
この“当たり前”が、まず超大事です 😌✅

---

## ④ つまづきポイント（3つ）🪤😵‍💫

## 1) /health をログに出しすぎてログ地獄 🧾🌋

ヘルスチェックは基盤が頻繁に叩くので、**毎回INFOログ**にするとノイズが爆増します 😇

* 対策：/health は**ログ出さない** or **DEBUGだけ** or **サンプリング**
  （ログ量の話は第13章と相性抜群！）🔥

## 2) /health の中で DB や外部 API を呼んじゃう 🧱🐢

それは **/ready** の役目（次章）です 🙅‍♂️
liveness は「プロセスが固まってない？」を見るために**軽く**が基本です。([Red Hat Docs][2])

## 3) `docker compose up` したのに反映されてない 😭

* 対策：変更したら基本これ👇

```text
docker compose up -d --build
```

---

## ⑤ ミニ課題（15分）⏳🎮

## 課題A：ヘルスの“見た目”をそろえる 🧩

レスポンス JSON に以下を追加してみよう👇

* `service`（例：`"api"`）
* `version`（例：`"0.1.0"`：package.json から読みたい気持ちは分かるけど、この章では直書きでOK😊）

## 課題B：ログを増やさずに、異常だけ気づけるようにする 🚨

* /health へのアクセスはログしない
* ただし「サーバ起動」「予期せぬ例外」だけはログに出す
  このバランス感覚が“観測性”っぽさです 😎✨

---

## ⑥ AIに投げるプロンプト例（コピペOK）🤖📋

## Copilot / Codex 向け（実装を一気に）🧠⚡

```text
Express + TypeScript のAPIに GET /health を追加したい。
要件：
- 200固定で返す（DBや外部アクセス禁止）
- JSONで { status: "ok", uptimeSec, timestamp } を返す
- ルートは src/routes/health.ts に分離し、server.ts で app.use する
- /health アクセスはログを出さない（ノイズ防止）
```

## “レビューして”系（設計の超入門に効く）🧑‍🏫✨

```text
この /health 実装は「生存チェック」として適切？
やってはいけないこと（重い処理、依存チェック、ログ過多など）が混ざってないか、
初心者にも分かる理由付きで指摘して、改善案も出して。
```

---

## 次章へのつながり 🔜🧩🔌

* 第25章の /health は「**プロセスが生きてる**」だけを見る ✅
* 次の第26章で、依存（DB/Redisなど）がOKかを見る **/ready** を作って「準備できた？」を返します 😆

必要なら、あなたの現状のミニAPI（/ping /slow /boom）のコード前提に合わせて、**差分パッチ形式**（ここに追記するだけ！）でも書き直しますよ ✍️💚

[1]: https://kubernetes.io/docs/concepts/configuration/liveness-readiness-startup-probes/?utm_source=chatgpt.com "Liveness, Readiness, and Startup Probes"
[2]: https://docs.redhat.com/ja/documentation/red_hat_build_of_node.js/12/html/node.js_runtime_guide/example-health-check-nodejs?utm_source=chatgpt.com "5.4. Node.js のヘルスチェック例"
[3]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
