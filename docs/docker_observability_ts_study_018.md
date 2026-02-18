# 第18章：エラー率を見る：失敗の数え方 🧯🧾

「落ちた！💥」って時、ログで原因を追うのは大事だけど…
**“今どれだけヤバいか”** を一瞬で判断するなら、やっぱり **エラー率** が強いです😎📈

---

## ① 今日のゴール 🎯

* **成功/失敗を“割合”で話せる**ようになる（例：5xx率 2%）
* **HTTPステータス別にカウント**して、/metrics に出せる
* `/boom` を叩いて **5xxが増える**のを確認できる ✅

> prom-client（Node向けPrometheusクライアント）は、npm上で最新 15.1.3 が案内されています（本日時点の表示）。([npm][1])
> Node.jsは **v24 が Active LTS**、v25が Current として公開されています（本日時点）。([Node.js][2])

---

## ② 図（1枚）🖼️

エラー率は「失敗の数」÷「全部の数」ってだけ！超シンプル😆

![Error Rate Formula Visualization](./picture/docker_observability_ts_study_018_error_rate_formula.png)

```text
          ┌──────────────┐
request → │  API (Express) │ → response(status)
          └──────┬───────┘
                 │
                 ▼
        http_requests_total (Counter)
     labels: method / route / status / status_class
                 │
                 ▼
      5xx率 = (5xxの増え方) / (全体の増え方)
```

---

## ③ 手を動かす（手順 5〜10個）🛠️

ここでは **「ステータス別のカウンタ」** を追加していくよ〜🧱✨
（前章までで `/metrics` が出てる前提でOK！）

---

### A. まずは“設計の型”を1つ決める 🧠📌

**エラー率に使う“失敗”は何？** を先に決めるのが超大事！

![5xx vs 4xx Policy](./picture/docker_observability_ts_study_018_5xx_vs_4xx.png)

* **5xx**：だいたい「サーバ側の失敗」＝アラート対象になりやすい 🔥
* **4xx**：ユーザー操作ミスや入力ミスも多い（全部を障害扱いにすると疲れる😵‍💫）

この章では、まず **5xx を “失敗” として数える** でいきます🫡

---

### B. 追加するメトリクスを作る（Counter）🧾➕

**ファイル例：`src/metrics/httpRequestsTotal.ts`**

```ts
import client from "prom-client";

// 例：HTTPリクエスト総数（ステータス別に分ける）
export const httpRequestsTotal = new client.Counter({
  name: "http_requests_total",
  help: "Total number of HTTP requests",
  labelNames: ["method", "route", "status", "status_class"] as const,
});
```

✅ Prometheusでは「メトリクス名にラベル名を埋め込まず、**ラベルで次元を分ける**」のが推奨されます。([prometheus.io][3])

---

### C. middlewareで「レスポンスの結果」を数える 🧩🔢

Expressは **処理の最後に statusCode が決まる**から、`finish` イベントで数えるのがコツだよ😊

![Middleware Counting Flow](./picture/docker_observability_ts_study_018_middleware_flow.png)

**ファイル例：`src/middlewares/metricsCounter.ts`**

```ts
import type { Request, Response, NextFunction } from "express";
import { httpRequestsTotal } from "../metrics/httpRequestsTotal";

function statusClass(statusCode: number) {
  return `${Math.floor(statusCode / 100)}xx`;
}

function routeLabel(req: Request) {
  // ルートがマッチした時は route.path が取れることが多い（例: "/users/:id"）
  // 404などは取れないので固定ラベルにする
  const r = (req as any).route?.path;
  return typeof r === "string" ? r : "(unmatched)";
}

export function metricsCounter(req: Request, res: Response, next: NextFunction) {
  // /metrics 自体を数えたくない場合は除外（好みでOK）
  if (req.path === "/metrics") return next();

  res.on("finish", () => {
    const status = String(res.statusCode);
    httpRequestsTotal.inc({
      method: req.method,
      route: routeLabel(req),
      status,
      status_class: statusClass(res.statusCode),
    });
  });

  next();
}
```

---

### D. appにmiddlewareを差し込む 🚪🧷

**例：`src/app.ts`（または server.ts）**

```ts
import express from "express";
import { metricsCounter } from "./middlewares/metricsCounter";

const app = express();

app.use(metricsCounter);

// 例：成功
app.get("/ping", (_req, res) => {
  res.status(200).send("pong");
});

// 例：わざと失敗（5xx）
app.get("/boom", (_req, res) => {
  res.status(500).json({ message: "boom 💥" });
});

export default app;
```

---

### E. 動かして叩く（Windows向け）🪟💥

1. 起動（Compose運用ならこれ）

```bash
docker compose up --build
```

2. まず成功を増やす（PowerShell）

```powershell
1..20 | % { iwr http://localhost:3000/ping -UseBasicParsing | Out-Null }
```

3. つぎに失敗を増やす（500は例外扱いになるので try/catch）

```powershell
1..5 | % {
  try { iwr http://localhost:3000/boom -UseBasicParsing | Out-Null }
  catch { }
}
```

4. /metrics を見て、増えてるか確認 👀

```powershell
(iwr http://localhost:3000/metrics -UseBasicParsing).Content `
  | Select-String "http_requests_total"
```

---

### F. 期待する出力（例）✅

/metrics の中に、こんな感じで出てきたら勝ち！🏆

```text
## HELP http_requests_total Total number of HTTP requests
## TYPE http_requests_total counter
http_requests_total{method="GET",route="/ping",status="200",status_class="2xx"} 20
http_requests_total{method="GET",route="/boom",status="500",status_class="5xx"} 5
```

---

### G. エラー率を“手計算”で感じる 🧮😆

この例だと…

* 全体：20 + 5 = 25
* 5xx：5
* **5xx率：5/25 = 0.2（20%）** 😱

もちろん実運用はPrometheus/Grafanaで“自動計算”するけど、
最初にこの感覚を身体に入れるのが大事〜💪✨

---

### H. （予告）Prometheusでの計算はこうなる 🕸️📥

Counters（カウンタ）は基本「増えるだけ」なので、Prometheus側では **rate()**（増え方）で見るのが王道だよ📈

![Rate Function Logic](./picture/docker_observability_ts_study_018_rate_function.png)

`rate()` は **カウンタに適用する**のが前提として説明されています。([prometheus.io][4])

* 全体のRPS（1秒あたりリクエスト数）

```text
sum(rate(http_requests_total[5m]))
```

* 5xxのRPS

```text
sum(rate(http_requests_total{status_class="5xx"}[5m]))
```

* **5xxエラー率（割合）**

![PromQL Error Rate Calculation](./picture/docker_observability_ts_study_018_promql_query.png)

```text
sum(rate(http_requests_total{status_class="5xx"}[5m]))
/
sum(rate(http_requests_total[5m]))
```

> ラベルは次元を増やすほど「時系列」が増えます（＝重くなりがち）。([prometheus.io][5])

---

## ④ つまづきポイント（3つ）🪤😵‍💫

1. **routeラベルが爆発する問題** 💣
   `/users/1` `/users/2` みたいに“値入りパス”をそのまま入れると、時系列が無限に増えます😇

   ![Label Cardinality Explosion](./picture/docker_observability_ts_study_018_cardinality_explosion.png)

   ➡️ `req.route.path`（`/users/:id` みたいな形）を優先して使うのが安全寄り！

2. **コンテナ再起動でカウンタが0に戻る** 🔁
   だから「生の数字」じゃなく、Prometheusでは **rate()/increase()** で見るのが基本！([prometheus.io][6])

3. **4xxを全部“障害”にすると運用が死ぬ** ☠️📣
   最初は **5xxだけ** をアラート対象にするのが平和です🕊️
   （4xxは「増え方」を別グラフで見るのはアリ👍）

---

## ⑤ ミニ課題（15分）⏳✍️

1. `status_class="4xx"` の増え方も見られるように、PromQL（予告の式）を自分で組み立ててみてね🧩
2. `/metrics` を除外した時と、除外しない時で `http_requests_total` の伸びがどう変わるか確認👀
3. 404（存在しないURL）を叩いて、`route="(unmatched)"` が増えるのを見てみよう🚪❌

---

## ⑥ AIに投げるプロンプト例（コピペOK）🤖📋✨

**1) middleware生成（Express + TS）**

```text
Express(TypeScript)で、レスポンス完了時に statusCode を取得して
prom-client の Counter に method/route/status/status_class をラベルとして inc する middleware を書いて。
route は req.route.path を優先し、取れない場合は "(unmatched)" にして。
/metrics はカウントしないようにして。
```

**2) PromQL（エラー率）**

```text
Prometheusのメトリクス http_requests_total{status_class="2xx|4xx|5xx"} があるとして、
5xxエラー率を 5分窓で計算する PromQL を3種類出して：
(1) 全体の5xx率 (2) route別の5xx率 (3) method別の5xx率
```

**3) ラベル設計レビュー**

```text
Prometheusのラベル設計レビューをして。
route に req.path を入れたいけど危険？なぜ？
安全な代替案（正規化・固定ラベル・ルートテンプレ化）の提案もして。
```

---

## チェック ✅🎉

* `/ping` を叩くと `status_class="2xx"` が増える
* `/boom` を叩くと `status_class="5xx"` が増える
* /metrics で `http_requests_total` が見えてる

ここまで来たら、次は **CPU/メモリ/イベントループ**みたいな「アプリ以外のボトルネック」に進める準備が整ってるよ〜🧠⚙️✨

[1]: https://www.npmjs.com/package/prom-client?utm_source=chatgpt.com "prom-client"
[2]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
[3]: https://prometheus.io/docs/practices/naming/?utm_source=chatgpt.com "Metric and label naming"
[4]: https://prometheus.io/docs/tutorials/understanding_metric_types/?utm_source=chatgpt.com "Understanding metric types"
[5]: https://prometheus.io/docs/concepts/data_model/?utm_source=chatgpt.com "Data model"
[6]: https://prometheus.io/docs/prometheus/latest/querying/functions/?utm_source=chatgpt.com "Query functions"
