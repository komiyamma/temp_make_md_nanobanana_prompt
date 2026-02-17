# 第13章：ログ量と保存：増えすぎ問題と“削る設計”💽🌀

## ① 今日のゴール 🎯

* ログが増えすぎると **「ディスクが死ぬ」「探せない」「遅くなる」** を体感する 😇
* **ログを“削る設計”**（出し方の工夫）を入れて、読めるログに戻す ✂️🧾
* **保存（ローテーション/保持）** をDocker側で最低限ガードできるようになる 🛡️📦

---

## ② 図（1枚）🖼️（イメージ）

![Log Hell vs Log Pruning](./picture/docker_observability_ts_study_013_01_log_hell_vs_pruning.png)

* ログは放置するとこうなる👇
  **アプリ** 📣（大量出力）→ **Dockerログ保存** 💽（肥大化）→ **見る人** 👀（迷子）
* “削る設計”を入れるとこう👇
  **アプリ** ✂️（必要だけ出す）＋ **Docker** 🌀（ローテーション）→ **見る人** 😌（追える）

---

## ③ 手を動かす（ハンズオン：ログ地獄→救出）🛠️🔥

> この章は「わざと壊す」→「直す」がテーマです 😈➡️🩹
> 既にあるミニAPI（/ping /slow /boom など）に **/spamlog** を足します。

---

## A. まず「ログ地獄」を作る 😇🔥

### 1) /spamlog を追加する（まずは最悪版）💥

![Spam Log Attack](./picture/docker_observability_ts_study_013_02_spam_log_attack.png)

**ファイル構成（例）📁**

* /src/app.ts
* /src/logger.ts
* compose.yml

**/src/logger.ts（例：pinoでJSONログ）**

```ts
import pino from "pino";

export const logger = pino({
  level: process.env.LOG_LEVEL ?? "info",
});
```

**/src/app.ts（/spamlog を追加）**

```ts
import express from "express";
import { logger } from "./logger";

export const app = express();

app.get("/spamlog", (req, res) => {
  const count = Math.min(Number(req.query.count ?? "2000"), 20000);
  const bytes = Math.min(Number(req.query.bytes ?? "300"), 2000);
  const payload = "x".repeat(bytes);

  for (let i = 0; i < count; i++) {
    // 💣 最悪：毎回でかいpayloadを出す（地獄の始まり）
    logger.info({ i, payload }, "spam");
  }

  res.json({ ok: true, count, bytes });
});
```

### 2) 叩いてみる（ログの洪水）🌊

* ブラウザでもOK
* コマンドなら（PowerShellでも確実に動くように `curl.exe` 推奨）👇

```bash
curl.exe "http://localhost:3000/spamlog?count=5000&bytes=800"
```

### 3) ログを見る（…終わる）👀💦

```bash
docker compose logs api --tail 50
docker compose logs api --tail 20 --follow
```

`--follow`（追従）や `--tail`（末尾だけ）や `--since`（時間で絞る）は、この手の“救出”で超重要です。([Docker Documentation][1])

---

## B. “削る設計”でログを救う ✂️🧾✨

ここからが本番です 😤🔥
ポイントは **「出す場所（Docker）で工夫」より先に、「出し方（アプリ）」を直す** こと！

---

### 4) まず「巨大payloadをログに出さない」🙈⛔

![Log Summarization](./picture/docker_observability_ts_study_013_03_log_summary.png)

/spamlog を “救出版” に差し替えます👇

```ts
app.get("/spamlog", (req, res) => {
  const count = Math.min(Number(req.query.count ?? "2000"), 20000);
  const bytes = Math.min(Number(req.query.bytes ?? "300"), 2000);

  // ✅ でかい中身は捨てて、要約だけ残す（これが“削る設計”）
  logger.warn({ count, bytes }, "spamlog requested");

  res.json({ ok: true, count, bytes });
});
```

✅ 「情報として価値があるのは *count と bytes*」
❌ payload本体は “コストの割に価値が低い” ので切る ✂️

---

### 5) 次に「成功ログをサンプリングする」🎲📉

![Log Sampling Logic](./picture/docker_observability_ts_study_013_04_sampling_logic.png)

**全部の成功ログを残す必要はありません**（特に /ping や健康診断系）
サンプリングは「割合で残す」発想です🧠✨

**/src/logPolicy.ts（追加）**

```ts
export function shouldSampleSuccess(): boolean {
  const rate = Number(process.env.LOG_SAMPLE_SUCCESS_RATE ?? "0.01"); // 1% 既定
  return Math.random() < rate;
}
```

**アクセスログのミドルウェア（例：最後に1行出す想定）**

```ts
import { shouldSampleSuccess } from "./logPolicy";
import { logger } from "./logger";

app.use((req, res, next) => {
  const start = Date.now();

  res.on("finish", () => {
    const ms = Date.now() - start;
    const status = res.statusCode;

    // ✅ 失敗は全部残す（あとで原因追跡に必須）
    const isError = status >= 500;

    // ✅ 成功はサンプルだけ
    const okSampled = status < 500 && shouldSampleSuccess();

    // ✅ /health みたいな超多発は、さらに絞るのもアリ
    const isNoisyRoute = req.path === "/health" || req.path === "/ping";

    if (isError || (okSampled && !isNoisyRoute)) {
      logger.info({ method: req.method, path: req.path, status, ms }, "access");
    }
  });

  next();
});
```

---

### 6) 「同じ警告を秒1回まで」みたいに抑える（レート制限）🚦⏱️

![Rate Limiting Logs](./picture/docker_observability_ts_study_013_05_rate_limit_log.png)

“同じエラー”が連打されると、ログが埋まって本当に大事な1行が消えます 😭

**/src/rateLimitLog.ts**

```ts
const last = new Map<string, number>();

export function allowLog(key: string, intervalMs: number): boolean {
  const now = Date.now();
  const prev = last.get(key) ?? 0;
  if (now - prev < intervalMs) return false;
  last.set(key, now);
  return true;
}
```

使い方（例）👇

```ts
import { allowLog } from "./rateLimitLog";

if (allowLog("db-conn-fail", 1000)) {
  logger.error({ err: "ECONNREFUSED" }, "db connection failed");
}
```

---

## ④ Docker側で「保存（ローテーション）」をかける 🌀📦🛡️

アプリ側で削った上で、最後の保険として **Docker側の“ログ保持上限”** を入れます。

## 7) Composeでログローテーション（localドライバ）🧰

![Log Rotation Mechanism](./picture/docker_observability_ts_study_013_06_log_rotation.png)

Dockerの `local` ログドライバは、stdout/stderrを**パフォーマンスとディスク効率に配慮した形式**で保存し、既定で **コンテナあたり100MB** を保持しつつ **圧縮**もします。さらに `max-size` / `max-file` / `compress` が設定できます。([Docker Documentation][2])

**compose.yml（apiサービスに追記例）**

```yaml
services:
  api:
    # （build, ports, environment などは省略）
    environment:
      LOG_LEVEL: "info"
      LOG_SAMPLE_SUCCESS_RATE: "0.01" # 成功ログ1%
    logging:
      driver: "local"
      options:
        max-size: "10m"
        max-file: "3"
        compress: "true"
```

> これで「1ファイル10MB×最大3世代」みたいに、ログ保存が暴走しにくくなります 💽🌀

**大事：設定変更は“新しく作ったコンテナ”から効く**ので、作り直しが必要です 🔁
（デーモン設定でも同じで、既存コンテナは自動では変わりません）([Docker Documentation][3])

作り直し（例）👇

```bash
docker compose up -d --force-recreate
```

---

## 8) json-file を使う場合の上限（max-size / max-file）🧱

`json-file` でも `max-size` / `max-file` でローテーションできます（設定しないと肥大化しがち）。([Docker Documentation][4])
また `daemon.json` の `log-opts` は **文字列で書く必要**があります。([Docker Documentation][4])

---

## ⑤ つまづきポイント（3つ）🪤😵‍💫

1. **Composeのlogging設定を変えたのに効かない**
   → だいたい **コンテナを作り直してない** パターンです 🔁([Docker Documentation][3])

2. **/ping や /health のログで埋まる**
   → “成功ログはサンプル”、健康診断は“さらに絞る or 切る”が効きます ✂️💚

3. **ログに秘密情報が混ざる**
   → ログは「見える場所に出る」前提。機密や個人情報は出すと危険です 🙈🔒
   （OWASPも“ログに出しちゃダメな情報”を強く警告しています）([OWASP][5])

---

## ⑥ ミニ課題（15分）⏳✍️

次の“ログ方針メモ”を、あなたのミニAPI用に1枚で書いてください📝✨

* **残すログ（必須）**：5xx、起動/停止、外部依存の失敗、想定外例外
* **サンプルで残すログ**：通常アクセスログ（成功系）
* **捨てる/要約するログ**：/ping /health の成功、巨大ボディ、連打される同一警告
* **保存**：local driver で max-size / max-file を設定（例：10m×3）

---

## ⑦ AIに投げるプロンプト例（コピペOK）🤖📋✨

1. **/spamlog を “要約ログだけ” に直したい**

```text
Express + TypeScript の /spamlog を、payloadをログに出さず count と bytes だけを warn で1行出すように修正して。変更差分コードで。
```

2. **成功ログを1%だけ出すサンプリングを入れたい**

```text
アクセスログを res.finish で1行出しています。status>=500は必ず、それ以外は LOG_SAMPLE_SUCCESS_RATE(既定0.01) の確率で出すように変更して。/health と /ping は成功ログを出さない方針で。
```

3. **同じエラーを秒1回までに抑えたい**

```text
同じキーのログを intervalMs 以内は抑制する allowLog(key, intervalMs) を Map で実装して。Node/TSで。使用例も。
```

---

## まとめ 🎉

* ログは **増えるほど価値が落ちる**（読めない・探せない・コスト増）😇💸
* 解決の順番はこれ👇

  1. **アプリで削る設計**（要約・サンプル・レート制限）✂️
  2. **Dockerで保存上限**（local driver などでローテーション）🌀💽([Docker Documentation][2])
* 次章（第14章）で、いよいよ **“集めて検索”**（Loki/Grafana）に入ると、ここで整えたログがめちゃ効きます 🧲🔍📊

[1]: https://docs.docker.com/reference/cli/docker/compose/logs/?utm_source=chatgpt.com "docker compose logs"
[2]: https://docs.docker.com/engine/logging/drivers/local/ "Local file logging driver | Docker Docs"
[3]: https://docs.docker.com/engine/logging/configure/?utm_source=chatgpt.com "Configure logging drivers"
[4]: https://docs.docker.com/engine/logging/drivers/json-file/?utm_source=chatgpt.com "JSON File logging driver"
[5]: https://owasp.org/Top10/2025/A09_2025-Security_Logging_and_Alerting_Failures/?utm_source=chatgpt.com "A09 Security Logging and Alerting Failures"
