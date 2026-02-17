# 第16章：/metrics を生やす：最小のprom-client 🌱📏

## ① 今日のゴール 🎯

* `GET /metrics` にアクセスすると **Prometheus形式のテキスト**が返るようになる 📄✨
* まずは最小でOK：**「HTTPリクエスト数」カウンタ**を1つだけ作って増やす 🔢⬆️
* 「メトリクスは *押し込む* んじゃなくて、*取りに来てもらう（pull）*」の感覚をつかむ 🧲👣
  Prometheus系は「アプリがHTTPエンドポイントでメトリクスを公開する」スタイルが基本です。([prometheus.io][1])

---

## ② 図（1枚）🖼️

![Prometheus Pull Model](./picture/docker_observability_ts_study_016_01_prometheus_pull_model.png)

```text
      (ブラウザ / curl)                (後でPrometheusがやること)
           │  GET /metrics                    │  定期的にGET /metrics
           ▼                                  ▼
   ┌────────────────┐                 ┌────────────────┐
   │   Node API      │                 │   Prometheus    │
   │  + prom-client  │<── scrape ───── │  (時系列DB)      │
   └────────────────┘                 └────────────────┘
           │
           └─ "text/plain; version=0.0.4" みたいな形式で返す 📄
```

`prom-client` は `await registry.metrics()` の結果を返せばOK、という方針です。([GitHub][2])
また、Prometheusは `Accept` ヘッダでフォーマットをやり取りする前提があるので、**Content-Typeを正しく返す**のが大事です。([prometheus.io][3])

---

## ③ 手を動かす（手順 5〜10個）🛠️

### ステップ0：今回使うライブラリの“最新”メモ 📝

* `prom-client` の最新リリースは **v15.1.3（2024-06-27）**として案内されています（npm/GitHub）。([GitHub][4])
* Node.jsは本日時点で、**v24 がActive LTS、v25 がCurrent**の並びです（例：v24.13.1 / v25.6.1）。([nodejs.org][5])

> バージョンを暗記するより、「公式のやり方どおりに /metrics を返せる」ことが勝ちです 💪✨

---

### ステップ1：`prom-client` を追加する 📦

PowerShell（またはVS Codeターミナル）で：

```bash
npm i prom-client
```

---

### ステップ2：メトリクス専用ファイルを作る（分けるのがコツ）🧩

![Metrics File Separation](./picture/docker_observability_ts_study_016_02_metrics_file_structure.png)

ファイル構成イメージ：

```text
.
├─ src
│  ├─ server.ts
│  └─ metrics.ts   ← 追加！
└─ package.json
```

`src/metrics.ts`（最小の “カウンタ1個” ）：

```ts
import { Counter, Registry } from "prom-client";

// ここでは「専用のRegistry」を使います（グローバル汚さない作戦✨）
export const registry = new Registry();

// リクエスト総数カウンタ（Counterは増えるだけ⬆️）
export const httpRequestsTotal = new Counter({
  name: "http_requests_total",
  help: "Total number of HTTP requests",
  labelNames: ["method", "route", "status"],
  registers: [registry],
});
```

* Counterは「総数」なので `_total` を付けるのが定番です 👍（命名の話は公式の推奨が強いです）([prometheus.io][6])
* ラベルは便利だけど、増やしすぎると地獄になるので注意（例：userId を入れるのは危険）⚠️🔥([prometheus.io][6])

---

### ステップ3：`/metrics` エンドポイントを生やす 🌱

`src/server.ts` に追記（Express想定の最小例）：

```ts
import express from "express";
import { httpRequestsTotal, registry } from "./metrics";

const app = express();

app.get("/ping", (req, res) => {
  res.status(200).json({ ok: true });

  httpRequestsTotal.inc({
    method: req.method,
    route: "/ping",
    status: String(res.statusCode),
  });
});

app.get("/slow", async (req, res) => {
  await new Promise((r) => setTimeout(r, 800));
  res.status(200).json({ ok: true, slow: true });

  httpRequestsTotal.inc({
    method: req.method,
    route: "/slow",
    status: String(res.statusCode),
  });
});

// ★ここが本題：Prometheusが見に来る出口
app.get("/metrics", async (_req, res) => {
  res.setHeader("Content-Type", registry.contentType);
  res.end(await registry.metrics());
});

app.listen(3000, () => {
  console.log("Listening on http://localhost:3000");
});
```

ポイントはここ👇

* `registry.metrics()` は **await** して返す（今どきはasync前提で書くのが安全）([GitHub][2])
* `Content-Type` は `registry.contentType` を使って正しく返す（交渉の前提がある）([prometheus.io][3])

---

### ステップ4：Dockerで動かして `/metrics` を見に行く 🐳👀

（すでにComposeで起動できる前提で）いつも通り：

```bash
docker compose up --build
```

別ターミナルで確認：

```bash
curl.exe http://localhost:3000/metrics
```

---

### ステップ5：カウンタが増えるのを確認する 🔢⬆️

![Counter Increment Verification](./picture/docker_observability_ts_study_016_03_counter_increment_verification.png)

まず `/ping` を何回か叩く：

```bash
curl.exe http://localhost:3000/ping
curl.exe http://localhost:3000/ping
curl.exe http://localhost:3000/slow
```

それから `/metrics` を絞って見る（PowerShellで便利）：

```powershell
curl.exe http://localhost:3000/metrics | Select-String http_requests_total
```

出力イメージ（だいたいこんな感じ）：

```text
## HELP http_requests_total Total number of HTTP requests
## TYPE http_requests_total counter
http_requests_total{method="GET",route="/ping",status="200"} 2
http_requests_total{method="GET",route="/slow",status="200"} 1
```

---

## ④ つまづきポイント（3つ）🪤

1. **`/metrics` が空っぽ or 500になる** 😵‍💫

* `await registry.metrics()` を忘れてる可能性大（Promiseをそのまま返して事故る）⚠️

2. **メトリクス名がダメって怒られる** 🧨

* `snake_case` + 型っぽい接尾辞（counterなら `_total`）が無難です。命名ルールは公式に寄せるのが吉。([prometheus.io][6])

3. **ラベルで自爆（時系列が爆増）💥**

![Label Explosion (High Cardinality)](./picture/docker_observability_ts_study_016_04_label_explosion.png)

* `userId`、`email`、`uuid`、クエリ文字列…みたいな「無限に増える値」をラベルに入れると、Prometheusがつらいです。([prometheus.io][6])
  まずは `method/route/status` くらいで十分！🙆‍♂️

---

## ⑤ ミニ課題（15分）⏳✨

「/metrics は“計測対象”に含めない」版を作ってみよう 😈➡️😇

* 目的：Prometheusが定期的に `/metrics` を叩くと、そのアクセスまでカウントされて紛らわしい…を防ぐ
* やること：`/metrics` では `httpRequestsTotal.inc(...)` しない（今のコードはすでにそうなってます🙆‍♂️）
* 追加課題：`/boom` があるなら `status="500"` が増えるのも確認（次章の「エラー率」に繋がる）🔥

---

## ⑥ AIに投げるプロンプト例（コピペOK）🤖📋

* 「Express + TypeScript で、`prom-client` を使って `/metrics` を実装して。`Registry` を分離して、`Content-Type` は `registry.contentType` を返すこと。さらに `http_requests_total{method,route,status}` を `/ping` と `/slow` で増やして。」
* 「Prometheusのラベルの“高カーディナリティ問題”を、初心者向けに具体例つきで説明して。ダメな例とOKな例を3つずつ。」([prometheus.io][6])
* 「次章でヒストグラムを入れたい。今回の `metrics.ts` を、後で `request_duration_seconds` を追加しやすい形にリファクタ案を出して。」

---

## ✅ 章のチェック（合格ライン）🎓

* `/metrics` にアクセスすると **テキスト形式のメトリクスが返る**
* `/ping` や `/slow` を叩くと `http_requests_total` が **ちゃんと増える**
* なんとなく「Prometheusが取りに来るための出口を作った」感覚がある 🧲✨

次の第17章では、この出口に **“レスポンス時間（ヒストグラム）”** を流し込んで、p95/p99 の世界に入っていきます ⏱️📉😆

[1]: https://prometheus.io/docs/instrumenting/clientlibs/?utm_source=chatgpt.com "Client libraries"
[2]: https://github.com/siimon/prom-client "GitHub - siimon/prom-client: Prometheus client for node.js"
[3]: https://prometheus.io/docs/instrumenting/content_negotiation/ "Scrape protocol content negotiation | Prometheus"
[4]: https://github.com/siimon/prom-client/releases?utm_source=chatgpt.com "Releases · siimon/prom-client"
[5]: https://nodejs.org/en/about/previous-releases "Node.js — Node.js Releases"
[6]: https://prometheus.io/docs/practices/naming/?utm_source=chatgpt.com "Metric and label naming"
