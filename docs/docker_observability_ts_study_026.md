# 第26章：/ready を作る：依存サービスがOKかチェック 🧩🔌

## ① 今日のゴール 🎯

この章が終わると…👇

* `/ready` が **「今、リクエストを受けていい状態か？」** を返せるようになります 🙆‍♂️
* DBなど依存が死んだら **200 → 503** に切り替わるのを体験できます 💥
* 「軽い疎通」「タイムアウト」「キャッシュ（叩きすぎ防止）」のコツが分かります 🧠✨

> イメージはお店🍜：
> `/health` = 店員は店にいる（生存）
> `/ready` = 開店準備できた（仕込みOK、レジOK、電気OK）

---

## ② 図（1枚）🖼️

![Readiness Check Flow](./picture/docker_observability_ts_study_026_01_readiness_check_flow.png)

```text
      ブラウザ / LB / 監視ツール
                 |
                 |  GET /ready
                 v
            APIコンテナ（Node）
                 |
                 |  軽い疎通（SELECT 1）
                 v
            DBコンテナ（Postgres）
```

ポイント：**「APIが生きてる」だけじゃ足りない**んです。依存（DBなど）が落ちてたら、受け付けると事故ります 😵‍💫

---

## ③ 手を動かす（手順 5〜10個）🛠️

### 0) まず知っておくこと（超重要）📌

Composeはデフォで「依存が“起動した”」までは並べてくれますが、「依存が“利用可能になった”」までは待ってくれません。なので**依存チェックは自分で作る**のが基本です。([Docker Documentation][1])
（起動順をちゃんと制御したい場合は `depends_on` の `condition: service_healthy` を使う手もあります。これもDocker Docsに例が載ってます。([Docker Documentation][1])）

---

### 1) ComposeにDB（Postgres）を追加する 🐘🧩

`compose.yml`（または `docker-compose.yml`）に `db` を足します👇
（Docker Docsにも `pg_isready` を使った例が出てきます。([Docker Documentation][1])）

```yaml
services:
  api:
    build: .
    ports:
      - "3000:3000"
    environment:
      DATABASE_URL: "postgres://app:app@db:5432/appdb"
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:18
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: app
      POSTGRES_DB: appdb
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB}"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 10s
    volumes:
      - db-data:/var/lib/postgresql/data

volumes:
  db-data:
```

✅ ここで大事：**`db` はコンテナ内のホスト名**です。`localhost` じゃないです 🙅‍♂️💦

---

### 2) DBクライアント（pg）を追加する 📦

```powershell
npm i pg
npm i -D @types/pg
```

---

### 3) Readinessチェック本体を作る（キャッシュ＋タイムアウト付き）⏱️🧠

![Readiness Cache Logic](./picture/docker_observability_ts_study_026_02_readiness_cache_logic.png)

`src/readiness.ts` を作ります👇

```ts
import { Pool } from "pg";

type CheckOk = { ok: true };
type CheckNg = { ok: false; reason: string };
type CheckResult = CheckOk | CheckNg;

type Cache = { at: number; result: CheckResult };

const TTL_MS = 3_000;      // /ready が連打されてもDBを叩きすぎない
const DB_TIMEOUT_MS = 1_000; // “軽い疎通” は短く失敗してほしい

function withTimeout<T>(p: Promise<T>, ms: number): Promise<T> {
  return Promise.race([
    p,
    new Promise<T>((_, rej) => setTimeout(() => rej(new Error("db check timeout")), ms)),
  ]);
}

export function createReadinessChecker(pool: Pool) {
  let cache: Cache | null = null;

  async function checkDb(): Promise<CheckResult> {
    try {
      // “軽い疎通”の王道：SELECT 1
      await withTimeout(pool.query("SELECT 1"), DB_TIMEOUT_MS);
      return { ok: true };
    } catch (e) {
      const reason = e instanceof Error ? e.message : String(e);
      return { ok: false, reason };
    }
  }

  return async function checkReady(): Promise<CheckResult> {
    const now = Date.now();
    if (cache && now - cache.at < TTL_MS) return cache.result;

    const result = await checkDb();
    cache = { at: now, result };
    return result;
  };
}
```

✨ コツ：

* **毎回DBを叩かない**（TTLキャッシュ）🧊
* **長く待たない**（タイムアウト）⏱️
* **重いSQLは絶対やらない**（`SELECT 1` で十分）🪶

---

### 4) `/ready` エンドポイントを生やす 🌱

![Response Switch](./picture/docker_observability_ts_study_026_03_response_switch.png)

たとえば `src/server.ts`（あなたのExpress起動ファイル）に追加👇

```ts
import express from "express";
import { Pool } from "pg";
import { performance } from "node:perf_hooks";
import { createReadinessChecker } from "./readiness";

const app = express();

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  connectionTimeoutMillis: 1000, // 接続自体もダラダラ待たない
  max: 5,
});

const checkReady = createReadinessChecker(pool);

// 状態変化のときだけログを出す（ログ爆発を防ぐ）🧯
let lastReady: boolean | null = null;

app.get("/ready", async (_req, res) => {
  const t0 = performance.now();
  const r = await checkReady();
  const ms = Math.round(performance.now() - t0);

  if (lastReady !== r.ok) {
    console.log(`[ready] state changed -> ${r.ok ? "READY ✅" : "NOT READY ❌"}`);
    lastReady = r.ok;
  }

  if (r.ok) {
    return res.status(200).json({
      ok: true,
      checks: { db: { ok: true, ms } },
    });
  }

  return res.status(503).json({
    ok: false,
    checks: { db: { ok: false, ms, reason: r.reason } },
  });
});

export default app;
```

---

### 5) 起動して動作確認 🚀

```powershell
docker compose up -d --build
curl http://localhost:3000/ready
```

期待する感じ（例）👇

* **OK時**：`200` と `{ ok: true, ... }`
* **NG時**：`503` と `{ ok: false, ... }`

ステータスコードも見たいとき👇

```powershell
curl -i http://localhost:3000/ready
```

---

### 6) 依存を止める → /ready が失敗に変わる 😈➡️💥

![Failure State](./picture/docker_observability_ts_study_026_04_failure_state.png)

```powershell
docker compose stop db
curl -i http://localhost:3000/ready
```

✅ ここで **503** が返れば勝ちです 🏆✨
（理由が `reason` に入ってるのも最高👍）

---

### 7) 依存復帰 → /ready がOKに戻る 🩹➡️✅

```powershell
docker compose start db
curl -i http://localhost:3000/ready
```

---

## ④ つまづきポイント（3つ）🪤

![Localhost Trap](./picture/docker_observability_ts_study_026_05_localhost_trap.png)

1. **DBホストを `localhost` にしてしまう** 🥲
   コンテナ内から見た `localhost` は「APIコンテナ自身」です。DBは `db`（サービス名）にします 👍

2. **/ready が重くて遅い** 🐢
   `SELECT * FROM big_table` とかやると逆に障害を作ります 😇
   “軽い疎通”だけにするのが鉄則です 🪶（依存チェックは軽く！）

3. **監視が連打してDBが死ぬ** 🔁💥
   ロードバランサやオーケストレータは高頻度で叩きます。
   だから **TTLキャッシュ**が地味に超重要です 🧊✨

---

## ⑤ ミニ課題（15分）⏳

![Since Field](./picture/docker_observability_ts_study_026_06_since_field.png)

できそうなのを1つやってみてね 😊

* **課題A（おすすめ）**：`/ready` のレスポンスに `since`（最終チェック時刻）を入れる ⏱️
* **課題B**：DBが落ちた時、`reason` を「人間向けメッセージ」に変換して返す（例：`DBに接続できません`）🗣️
* **課題C**：依存チェックを増やす（例：Redisや外部HTTP）➕🔌

  * ただし「軽く」「短く」「叩きすぎない」ルールは守ること 🙏

---

## ⑥ AIに投げるプロンプト例（コピペOK）🤖📋

Copilot / Codex に投げる用👇

```text
Express + TypeScriptで /ready エンドポイントを実装したい。
要件:
- DB(PostgreSQL)への軽い疎通として SELECT 1 を使う
- タイムアウト(1秒)で失敗扱いにする
- /ready が連打されてもDBを叩きすぎないように TTLキャッシュ(3秒)を入れる
- readyなら200 + JSON、readyでなければ503 + JSON(reason付き)
- 状態が変わった時だけログを出す（READY/NOT READY）
コード例を src/readiness.ts と src/server.ts の形で出して。
```

---

## おまけ：この章の“設計のキモ”だけ一言で言うと 🧠✨

**「受け付けていいか」を外に宣言するのが `/ready`** です。
Composeも含めて、起動順やルーティング判断は “ready情報” があると超ラクになります。([Docker Documentation][1])

次章（第27章）で、この考え方を **DockerのHEALTHCHECK** に接続して「コンテナ自身の健康状態」にしていきます 🧪📦（`start_period` などの意味も、Docker Docsに定義があります）([Docker Documentation][2])

[1]: https://docs.docker.com/compose/how-tos/startup-order/ "Control startup order | Docker Docs"
[2]: https://docs.docker.com/reference/dockerfile/?utm_source=chatgpt.com "Dockerfile reference | Docker Docs"
