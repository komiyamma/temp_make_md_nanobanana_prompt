# 第19章：システム系メトリクス：CPU/メモリ/イベントループ 🧠⚙️

この章は「アプリの中身（ログやHTTPメトリクス）だけじゃなく、**実行してる“エンジン側”の悲鳴**も数字で拾おう！」がテーマだよ〜😊
CPUが燃えてる🔥／メモリが増え続ける💧／イベントループが詰まる🚧…を、**“気配”じゃなく“数値”で見える化**する！

（ちなみに本日時点だと、Nodeは **v24 が Active LTS**、v25 が Current という位置づけだよ〜📌）([Node.js][1])

---

## ① 今日のゴール 🎯

![Engine Health Monitoring Dashboard](./picture/docker_observability_ts_study_019_engine_room.png)

* **CPU**・**メモリ**・**イベントループ**の3つを「いまヤバいのどれ？」って判断できる 👀
* `/metrics` に **システム系メトリクス**を増やして、負荷をかけたら数値が動くのを体験する 🧪
* 「CPUが高い」と「イベントループが詰まってる」を**別物**として説明できるようになる ✨

---

## ② 図（1枚）🖼️

アプリの外に出すのは “観測用の蛇口” 🚰 だけ。中を覗かないで判断するのがポイント！

![The Observability Faucet](./picture/docker_observability_ts_study_019_observability_faucet.png)

```text
[Client] ──HTTP──▶ [Node/TS API in Docker]
                       │
                       │ ① ふだんの処理
                       │
                       ├─ ② /metrics 🚰（観測用）
                       │      ├ CPU（process_cpu_*）
                       │      ├ Memory（rss/heap/external）
                       │      ├ Event loop lag（p99とか）
                       │      └ (追加) Event Loop Utilization（ELU）
                       │
                       └─ ③ (この章の実験) /cpu /leak /block 💥
```

---

## ③ 手を動かす（手順 5〜10個）🛠️

ここでは **prom-client の “デフォルトメトリクス”**をONにして、CPU/メモリ/イベントループの土台を一気に揃えるよ📦
（prom-client は v15.1.3 が最新リリースとして広く参照されてるよ）([GitHub][2])

---

### 0) まずファイル構成（この章で触るところ）📁

```text
/
  compose.yml
  Dockerfile
  package.json
  tsconfig.json
  src/
    server.ts
    metrics.ts
```

---

### 1) `collectDefaultMetrics()` を有効化する 🌱📏

**ここが最短ルート！**
`collectDefaultMetrics()` を呼ぶだけで、CPU・メモリ・イベントループ遅延・GC など “定番セット” が入るよ。([テスル][3])

`src/metrics.ts`（新規 or 追記）👇

```ts
import { Registry, collectDefaultMetrics, Gauge } from "prom-client";
import { eventLoopUtilization } from "node:perf_hooks";

export const register = new Registry();

/**
 * ✅ 1回だけ呼ぶ（2回呼ぶとメトリクス重複で死にがち）
 */
collectDefaultMetrics({
  register,
  // イベントループ遅延のサンプリング間隔(ms)。小さすぎるとオーバーヘッド増えがち😵‍💫
  eventLoopMonitoringPrecision: 10,
});

// ---- 追加：ELU（Event Loop Utilization）をGaugeで出す ----
// ELUは「イベントループがどれだけ“動きっぱなし”か」を 0〜1 で表すよ（1に近いほど詰まりやすい）🧱
export const nodejsEventLoopUtilization = new Gauge({
  name: "nodejs_eventloop_utilization",
  help: "Event Loop Utilization (0..1). High means event loop is busy/blocking.",
  registers: [register],
});

let prevElu = eventLoopUtilization();

setInterval(() => {
  const next = eventLoopUtilization(prevElu);
  prevElu = eventLoopUtilization();
  nodejsEventLoopUtilization.set(next.utilization);
}, 5000).unref();
```

ポイント：

* `collectDefaultMetrics` は **スクレイプ時（`registry.metrics()` が呼ばれた時）に収集される**設計だよ（常時バックグラウンドで集めない）([テスル][3])
* デフォルトで入る代表例：

  * CPU: `process_cpu_user_seconds_total`, `process_cpu_system_seconds_total`
  * メモリ: `process_resident_memory_bytes`, `nodejs_heap_size_used_bytes`, `nodejs_external_memory_bytes`
  * Event loop lag: `nodejs_eventloop_lag_p99_seconds` など ([テスル][3])

---

### 2) `/metrics` エンドポイントで吐き出す 🚰

`src/server.ts`（必要部分だけ）👇
※ すでに `/metrics` があるなら、`register` をこの章のものに合わせればOK！

```ts
import express from "express";
import { register } from "./metrics";

const app = express();
app.use(express.json());

app.get("/metrics", async (_req, res) => {
  res.setHeader("Content-Type", register.contentType);
  res.end(await register.metrics());
});

export default app;
```

---

### 3) “CPUっぽさ / メモリっぽさ / 詰まりっぽさ” を作るエンドポイントを追加 💥

同じく `src/server.ts` に追記👇（実験用だよ〜🧪）

```ts
// ✅ CPUを燃やす（=イベントループも止まりやすい）
app.get("/cpu", (req, res) => {
  const ms = Math.min(Number(req.query.ms ?? 200), 5000);

  const end = Date.now() + ms;
  let x = 0;
  while (Date.now() < end) {
    x += Math.sqrt(Math.random());
  }

  res.json({ ok: true, burnedMs: ms, x });
});

// ✅ メモリを “増え続ける” 状態にする（リーク疑い体験）
const leak: Buffer[] = [];

app.get("/leak", (req, res) => {
  const mb = Math.min(Number(req.query.mb ?? 10), 200);
  leak.push(Buffer.alloc(mb * 1024 * 1024, 1));
  res.json({ ok: true, leakedMB: mb, chunks: leak.length });
});

// ✅ ただイベントループをブロックする（I/Oじゃなく「詰まり」を作る）
app.get("/block", (req, res) => {
  const ms = Math.min(Number(req.query.ms ?? 300), 5000);
  const end = Date.now() + ms;
  while (Date.now() < end) {}
  res.json({ ok: true, blockedMs: ms });
});

![CPU Burn Loop Visualization](./picture/docker_observability_ts_study_019_cpu_burn_loop.png)
![Memory Leak Array Visualization](./picture/docker_observability_ts_study_019_memory_leak_array.png)
![Event Loop Blocking Visualization](./picture/docker_observability_ts_study_019_event_loop_block.png)
```

---

### 4) 起動して、まずは “平常時” の数値を見る 👀

PowerShell で👇（`curl` の罠回避で `curl.exe` が安全！）

```powershell
docker compose up -d --build
curl.exe -s http://localhost:3000/metrics | Select-String -Pattern "process_cpu|process_resident|nodejs_heap_size_used|nodejs_eventloop_lag_p99|nodejs_eventloop_utilization"
```

“それっぽい行”が出ればOK！例👇（値は環境で変わるよ）

```text
process_cpu_user_seconds_total 0.12
process_resident_memory_bytes 123994112
nodejs_heap_size_used_bytes 35639296
nodejs_eventloop_lag_p99_seconds 0.0023
nodejs_eventloop_utilization 0.03
```

---

### 5) 負荷をかけて、数値が動くのを体験する 🐢➡️🔥

CPU燃焼🔥（50回叩く）

```powershell
1..50 | % { curl.exe -s "http://localhost:3000/cpu?ms=150" > $null }
curl.exe -s http://localhost:3000/metrics | Select-String -Pattern "process_cpu|nodejs_eventloop_lag_p99|nodejs_eventloop_utilization"
```

メモリ増加💧（10MBずつ5回）

```powershell
1..5 | % { curl.exe -s "http://localhost:3000/leak?mb=10" > $null }
curl.exe -s http://localhost:3000/metrics | Select-String -Pattern "process_resident|heap_size_used|external_memory"
```

イベントループ詰まり🚧（ブロック300msを連打）

```powershell
1..30 | % { curl.exe -s "http://localhost:3000/block?ms=300" > $null }
curl.exe -s http://localhost:3000/metrics | Select-String -Pattern "nodejs_eventloop_lag_p99|nodejs_eventloop_utilization"
```

---

## ここで “何が起きてるか” の読み方 👓✨

### 🧯 CPU（燃えてる？）

* `process_cpu_user_seconds_total` / `process_cpu_system_seconds_total` は **累積秒**（増え続けるカウンタ）だよ。([テスル][3])
* 「CPU何%？」は **差分**で見る（次章でPrometheus入れたら `rate()` で一発になる）💡

### 💧 メモリ（増え続けてる？）

![Node.js Memory Types Structure](./picture/docker_observability_ts_study_019_memory_types.png)

* まず “ざっくり” は `process_resident_memory_bytes`（RSS）を見るのが分かりやすい！([テスル][3])
* `heap` と `external` は性質が違う：

  * Nodeには `process.memoryUsage()` で `rss / heapTotal / heapUsed / external / arrayBuffers` が取れる（意味もここにまとまってる）([Node.js][4])
  * Buffer を溜める系は **external** が伸びやすい（だから “heapだけ見て安心” が危険😈）

### 🚧 イベントループ（詰まってる？）

![Event Loop Lag vs Utilization](./picture/docker_observability_ts_study_019_lag_vs_utilization.png)

* prom-clientのデフォルトで `nodejs_eventloop_lag_p99_seconds` みたいな **分位点**が取れるよ（p99が上がると体感遅延が出やすい）([テスル][3])
* Nodeの `monitorEventLoopDelay()` はイベントループ遅延をサンプリングして、min/max/mean/p99 などを取れる（遅延はナノ秒単位）([Node.js][5])
* さらにこの章で追加した **ELU** は、Nodeが公式に `eventLoopUtilization()` を提供してて、イベントループがどれだけ忙しいかを出せるよ。([Node.js][5])

---

## ④ つまづきポイント（3つ）🪤😵‍💫

1. **`collectDefaultMetrics()` を2回呼んで地獄** 😇

   * メトリクス名が重複して例外になりがち。**1回だけ！**

2. **`eventLoopMonitoringPrecision` を攻めすぎる** 🏎️💨

   * 5msとかにすると精度は上がるけど、オーバーヘッド増えやすい。用途が固まるまで **10ms〜100ms** くらいでOK。([テスル][3])

3. **PowerShellの `curl` が別物問題** 🎭

   * 困ったら `curl.exe` を使うのが安牌！

---

## ⑤ ミニ課題（15分）⏳🏁

### 課題A：リーク“っぽい”判定を書いてみよう 🕵️‍♂️💧

* `/leak?mb=10` を10回叩く
* 次の3つを並べて見て、「どれが伸びてる？」を文章で説明してみてね👇

  * `process_resident_memory_bytes`
  * `nodejs_heap_size_used_bytes`
  * `nodejs_external_memory_bytes` ([テスル][3])

### 課題B：詰まりを“言語化”しよう 🚧🗣️

* `/block?ms=300` を連打して

  * `nodejs_eventloop_lag_p99_seconds` が上がる
  * `nodejs_eventloop_utilization` が上がる
* この2つの違いを一言で言ってみる（例：「遅延そのもの」vs「忙しさ」）✨
  ※ `monitorEventLoopDelay()` と `eventLoopUtilization()` の性格の違いがヒントだよ！([Node.js][5])

---

## ⑥ AIに投げるプロンプト例（コピペOK）🤖📋

1. **いまのメトリクス設計チェック**
   「`/metrics` に `process_resident_memory_bytes` と `nodejs_heap_size_used_bytes` と `nodejs_external_memory_bytes` が出ています。Bufferリークが疑われるとき、どの指標が伸びやすい？どう切り分ける？具体的な手順で教えて。」

2. **ELUの導入レビュー**
   「TypeScriptで `eventLoopUtilization()` を5秒ごとにGaugeへ入れました。更新頻度・命名・メトリクスの説明文の改善案を出して。」

3. **“症状→見るメトリクス” の辞書を作る**
   「症状が『遅い』『落ちる』『メモリが増える』『CPUが張り付く』のとき、まず見るべきメトリクス名を優先度付きで箇条書きにして。prom-clientのデフォルトメトリクス中心で。」

---

次章（第20章）で **Prometheusが定期的に取りに来る**ようになると、ここで出したCPU/メモリ/イベントループが「グラフで気持ちよく動く」ようになるよ〜📈✨
そして第21章でGrafanaに並べた瞬間、テンション爆上がり😆🎉

（おまけ：もっと先に進むと、ログ/メトリクスの次はトレースで OpenTelemetry って流れも増えるよ〜🧵👀）

[1]: https://nodejs.org/en/about/previous-releases "Node.js — Node.js Releases"
[2]: https://github.com/siimon/prom-client/releases?utm_source=chatgpt.com "Releases · siimon/prom-client"
[3]: https://tessl.io/registry/tessl/npm-prom-client/15.1.0/files/docs/default-metrics.md "npm-prom-client@15.1.0 • tessl • Registry • Tessl"
[4]: https://nodejs.org/en/learn/diagnostics/memory/understanding-and-tuning-memory "Node.js — Understanding and Tuning Memory"
[5]: https://nodejs.org/api/perf_hooks.html "Performance measurement APIs | Node.js v25.6.1 Documentation"
