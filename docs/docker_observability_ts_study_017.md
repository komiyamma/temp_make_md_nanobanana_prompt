# 第17章：レスポンス時間を測る：ヒストグラムで速度を見る ⏱️📉

## ① 今日のゴール 🎯

* 「平均が速い＝安心」じゃない理由を説明できる 😅
* **ヒストグラム**で `http_request_duration_seconds` を出せる 🧱
* /slow を叩いたら、`_bucket / _sum / _count` が増えるのを確認できる ✅

---

## ② 図（1枚）🖼️（イメージを先に掴む）

```text
リクエスト
   │
   ▼
API(Express)
   │ ①開始時刻を取る
   │ ②レスポンス完了で「秒」を計測
   ▼
prom-client Histogram に observe()
   │
   ▼
/metrics に _bucket / _sum / _count が出る
   │
   ▼
（次章以降で）Prometheus/Grafanaで p95/p99 を見る
```

---

## ③ 平均がダメな理由（超ざっくり）😵‍💫

平均って「全員の平均点」みたいなもので、**一部の“めちゃ遅い”**が隠れがちなんだよね…🫠

たとえばこんな感じ👇

* 99回：100ms（速い！）
* 1回：10,000ms（激遅！）

このとき平均は「199ms」くらいになって、**“そんなに悪くないっぽい”**顔をしちゃう😇
でもユーザーからすると「たまに10秒待たされる」のは普通にキツい💥

そこで **p95 / p99**（95%点、99%点）みたいな“上のほうの遅さ”を見る発想が大事になるよ〜📌
ヒストグラムは、この「分布（ばらつき）」を見るための王道だよ🧠✨ ([prometheus.io][1])

---

## ④ 手を動かす（手順 5〜10個）🛠️✨

> ここでは「前章までで /metrics はある」前提で、**“レスポンス時間ヒストグラム”を追加**していくよ😊
> もしまだなら `prom-client` を入れてね（※すでに入ってたらスキップでOK）！

### 0) 依存（まだなら）

```bash
npm i prom-client
npm i -D @types/express
```

---

### 1) `src/metrics.ts` を作る（ヒストグラム定義）🧱

ポイントは2つ👇

* **単位は seconds（秒）**に統一する（Prometheus流）([prometheus.io][2])
* ラベルは**低カーディナリティ**（増えすぎない）にする（後述）([CNCF][3])

```ts
// src/metrics.ts
import * as client from "prom-client";
import type { Request, Response } from "express";

export const register = new client.Registry();

// ついでにプロセス/GCなどの「デフォルトメトリクス」も載せる（便利）
client.collectDefaultMetrics({ register });

// これが今回の主役：レスポンス時間（秒）のヒストグラム
export const httpRequestDurationSeconds = new client.Histogram({
  name: "http_request_duration_seconds",
  help: "HTTP request duration in seconds",
  // 低カーディナリティの定番3点セット
  labelNames: ["method", "route", "status_code"] as const,

  // ざっくり「Web APIでありがちな速度帯」をカバーするバケツ
  // ※自分のAPIに合わせて調整してOK！（後でコツを説明するよ）
  buckets: [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10],

  registers: [register],
});

export async function metricsHandler(_req: Request, res: Response) {
  res.setHeader("Content-Type", register.contentType);
  res.end(await register.metrics());
}
```

---

### 2) `src/metricsMiddleware.ts` を作る（計測の本体）⏱️

ここがキモ！

* リクエスト開始時に `startTimer()`
* レスポンス完了（`finish`）で `end({ labels... })`

`prom-client` のREADMEでも、**「先に一部ラベルを入れて、後でステータス等を足す」**例が載ってるよ👍 ([GitHub][4])

```ts
// src/metricsMiddleware.ts
import type { Request, Response, NextFunction } from "express";
import { httpRequestDurationSeconds } from "./metrics";

function normalizeRoute(req: Request): string {
  // Expressの route 情報が取れるなら「/users/:id」みたいに正規化された形になりやすい
  if (req.route?.path) {
    const base = req.baseUrl ?? "";
    return `${base}${req.route.path}`;
  }
  // ルーティングに乗らない（404等）場合は "unmatched" にまとめる（重要！）
  return "unmatched";
}

export function metricsMiddleware(req: Request, res: Response, next: NextFunction) {
  // タイマー開始（まだ status_code や route は確定しないので後で入れる）
  const end = httpRequestDurationSeconds.startTimer();

  res.on("finish", () => {
    end({
      method: req.method,
      route: normalizeRoute(req),
      status_code: String(res.statusCode),
    });
  });

  next();
}
```

---

### 3) `src/index.ts` に組み込む（middleware と /metrics）🔌

```ts
// src/index.ts
import express from "express";
import { metricsMiddleware } from "./metricsMiddleware";
import { metricsHandler } from "./metrics";

const app = express();

app.use(metricsMiddleware);

app.get("/ping", (_req, res) => res.status(200).send("pong"));

app.get("/slow", async (_req, res) => {
  // 遅いのを“わざと”作る（例：800ms）
  await new Promise((r) => setTimeout(r, 800));
  res.status(200).json({ ok: true });
});

app.get("/boom", (_req, _res) => {
  throw new Error("boom!");
});

app.get("/metrics", metricsHandler);

app.listen(3000, () => {
  console.log("listening on http://localhost:3000");
});
```

---

## ⑤ 動作チェック ✅（/slow → /metrics）

### 1) まず起動

```bash
npm run dev
```

### 2) /slow を何回か叩く（Windowsなら PowerShell がラク）🪟💪

```powershell
1..20 | % { iwr http://localhost:3000/slow -UseBasicParsing | Out-Null }
```

### 3) /metrics を開く（ブラウザでもOK）👀

```text
http://localhost:3000/metrics
```

---

## ⑥ 期待する出力（ここが見えたら勝ち！🏆）

/metrics の中に、だいたいこんなのが出てくるよ👇（一部だけ例）

```text
## HELP http_request_duration_seconds HTTP request duration in seconds
## TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{method="GET",route="/slow",status_code="200",le="0.5"} 0
http_request_duration_seconds_bucket{method="GET",route="/slow",status_code="200",le="1"} 20
http_request_duration_seconds_bucket{method="GET",route="/slow",status_code="200",le="2.5"} 20
http_request_duration_seconds_bucket{method="GET",route="/slow",status_code="200",le="+Inf"} 20
http_request_duration_seconds_sum{method="GET",route="/slow",status_code="200"} 16.0
http_request_duration_seconds_count{method="GET",route="/slow",status_code="200"} 20
```

見どころはここ👇👀✨

* `_count`：何回観測した？（回数）
* `_sum`：合計何秒かかった？（合計秒）
* `_bucket`：どの時間帯に何回入った？（分布）

ヒストグラム/サマリーが `_sum` と `_count` を持つこと、そして平均も出せることは Prometheus の解説でも触れられてるよ📚 ([prometheus.io][1])

---

## ⑦ バケット（buckets）の“いい感じ”入門 🪣✨

バケットは「秒の区切り」だよ〜⏱️
コツはざっくり3つ👇

1. **“普段の速さ”の周辺を細かく**する

* 普段 50〜200ms が多いなら、その辺にバケットを多めに置く🎯

2. **“たまに遅い”も拾える上限**を用意する

* 1秒、2.5秒、5秒、10秒…みたいに「尻尾」も見えるようにする🐍

3. **秒で統一**（msにしない）

* Prometheusはベース単位（seconds）推奨だよ📏 ([prometheus.io][2])

---

## ⑧ つまづきポイント（3つ）🪤😇

1. **msで測ってしまった**
   → そのまま `observe(800)` とかすると「800秒」扱いで地獄😱
   ✅ 秒に直す（`ms / 1000`）か、今回みたいに `startTimer()` を使うのが安全👍 ([GitHub][4])

2. **route ラベルが増えすぎる（爆発）**
   例：`/users/123`, `/users/456` をそのまま入れると、ユーザー数だけ時系列が増える💥
   ✅ `req.route.path` を優先して `"/users/:id"` みたいな形に寄せる（今回の実装）
   （カーディナリティ注意は公式系の解説でも強く言われてるよ）([CNCF][3])

3. **404 や例外のとき route が取れない**
   ✅ そういう時は `"unmatched"` にまとめちゃう（ラベル爆発を防ぐ）🧯

---

## ⑨ ミニ課題（15分）⏳✍️

1. `/ping` を 50回叩く → `/slow` を 20回叩く
   → `route="/ping"` と `route="/slow"` の **分布の違い**を /metrics で見て説明してみて👀✨

2. バケットを調整してみる

* 例：`0.2, 0.3, 0.5, 0.8, 1.0` を足して「800ms付近が見やすい」ようにする🎚️

3. `"unmatched"` をわざと作る

* 存在しないURLを叩いて 404 を出す → `route="unmatched"` が増えるか確認✅

---

## ⑩ AIに投げるプロンプト例（コピペOK）🤖📋

* 「Express + TypeScriptで、`res.on('finish')` で prom-client Histogram を更新する middleware を書いて。`method/route/status_code` ラベル付きで」
* 「`req.route.path` と `req.baseUrl` を使って、カードinalityが増えない route 正規化関数を提案して」
* 「このAPIの想定レスポンス時間が 30ms〜2s のとき、良い histogram buckets を提案して（理由付きで）」

---

## ⑪ 次にどう繋がる？（ちょい予告）🔭✨

この章で作ったヒストグラムは、あとで Prometheus 側で **p95/p99** を計算して可視化できるようになるよ！
`histogram_quantile()` の基本形は公式ドキュメントに例がある👇 ([prometheus.io][5]) ([prometheus.io][1])

（第20〜21章あたりで、Grafanaで「p95が悪化した！」が目で見えるようになる😆📊）

---

必要なら、この第17章の続きとして「**/boom の例外も“必ず計測される”ようにする（例外時に end されない問題対策）**」まで含めた強化版も書けるよ🧯🔥

[1]: https://prometheus.io/docs/practices/histograms/ "Histograms and summaries | Prometheus"
[2]: https://prometheus.io/docs/practices/naming/ "Metric and label naming | Prometheus"
[3]: https://www.cncf.io/blog/2025/07/22/prometheus-labels-understanding-and-best-practices/ "Prometheus Labels: Understanding and Best Practices | CNCF"
[4]: https://github.com/siimon/prom-client "GitHub - siimon/prom-client: Prometheus client for node.js"
[5]: https://prometheus.io/docs/prometheus/latest/querying/functions/ "Query functions | Prometheus"
