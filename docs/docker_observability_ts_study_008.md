# 第08章：ログレベル入門：DEBUG/INFO/WARN/ERROR 🎚️🟢🟡🔴

## ① 今日のゴール 🎯

* `DEBUG / INFO / WARN / ERROR` を「どんな時に使うか」説明できるようになる🙂
* `LOG_LEVEL` 環境変数で **ログの量を切り替え**できるようになる🔁
* 「同じ操作なのに、ログの出る量が変わる！」を体験する👀✨

---

## ② まずはイメージ図（超ざっくり）🖼️

![Log Levels Knob](./picture/docker_observability_ts_study_008_01_log_levels_knob.png)

ログレベルは「重要度（危険度）＋出す量のツマミ」だと思うと楽です🎛️

* `DEBUG`：開発中の虫めがね🔍（細かい内部状態）
* `INFO`：通常運転の記録🧾（いつ何が起きた）
* `WARN`：黄色信号🟡（変だけど処理は続く）
* `ERROR`：赤信号🔴（失敗した／期待通り動いてない）

そして **LOG_LEVEL は “最低ライン”** です👇

![Log Filtering Logic](./picture/docker_observability_ts_study_008_02_filtering_logic.png)

例：`LOG_LEVEL=INFO` なら、`INFO/WARN/ERROR` は出るけど `DEBUG` は消える🙈

---

## ③ どれをどこで使う？（迷ったらこれ）🧭

![Log Level Use Cases](./picture/docker_observability_ts_study_008_03_use_cases_icons.png)

| レベル   | いつ使う？                | 例（この教材のミニAPI想定）                             |
| ----- | -------------------- | ------------------------------------------- |
| DEBUG | 「原因調査に必要だけど、普段はいらない」 | ルート内部の分岐、DB呼び出し直前の状態、計測の途中経過                |
| INFO  | 「運用上ふつうに見たい」         | 起動ログ、アクセスログ（method/path/status/ms）、ジョブ開始/完了 |
| WARN  | 「変。放置すると事故りそう」       | リトライ発生、外部APIが遅い、想定外パラメータ（ただし処理は継続）          |
| ERROR | 「失敗した。調べないとダメ」       | 例外で落ちた、5xx、依存サービス接続失敗                       |

💡コツ：

* **“ユーザー操作の失敗”**（4xx）は *WARN か INFO* になりがち（プロダクト方針による）
* **“自分たちのミス/障害”**（5xx・例外）は基本 *ERROR* 🧯

---

## ④ なんで本番で DEBUG を垂れ流しちゃダメ？ 💸😇

![Stdout and Stderr Streams](./picture/docker_observability_ts_study_008_04_stdout_streams.png)

* ログは基本「イベントの流れ」として **stdout に出し、外側（Docker/基盤）が回収する**のが定石です📣（アプリ側は保管やローテーションを頑張らない）([12factor.net][1])
* コンテナのログは Docker 側の仕組み（logging driver）で保存・転送されます。大量に出すと **ディスクを食い尽くす**などの事故につながるので、運用ではローテーションされる driver を推奨しています🧯([Docker Documentation][2])
* だから本番は `INFO` 以上に絞り、調査時だけ一時的に `DEBUG` に上げるのが王道です🎚️

---

## ⑤ ハンズオン：LOG_LEVEL でログ量を切り替える 🛠️🚀

ここでは **ライブラリなし**で「最小のログレベルスイッチ」を作ります（理解が最優先！）🙂
次章の「構造化ログ（JSON）」にもつなげやすい形にしておきます🧱

## 0) 追加するファイル構成 📁

* `src/logger.ts` ← 新規
* （既存）`src/server.ts`（または `src/app.ts`） ← 少し編集
* （既存）`compose.yml`（または `docker-compose.yml`） ← 少し編集

---

## 1) logger.ts を作る 🎚️

![Logger Logic Flow](./picture/docker_observability_ts_study_008_05_logger_logic.png)

`src/logger.ts` を作って、これを貼り付けます👇

```ts
// src/logger.ts
export type LogLevel = "debug" | "info" | "warn" | "error" | "silent";

const LEVEL_WEIGHT: Record<Exclude<LogLevel, "silent">, number> = {
  debug: 10,
  info: 20,
  warn: 30,
  error: 40,
};

function normalizeLevel(input: string | undefined): LogLevel {
  const v = (input ?? "").toLowerCase().trim();
  if (v === "debug" || v === "info" || v === "warn" || v === "error" || v === "silent") return v;
  return "info"; // 変な値だったら安全に info
}

const CURRENT_LEVEL: LogLevel = normalizeLevel(process.env.LOG_LEVEL);

function shouldLog(level: Exclude<LogLevel, "silent">): boolean {
  if (CURRENT_LEVEL === "silent") return false;
  return LEVEL_WEIGHT[level] >= LEVEL_WEIGHT[CURRENT_LEVEL];
}

function safeJson(obj: unknown): string {
  try {
    return JSON.stringify(obj);
  } catch {
    return '"[unserializable]"';
  }
}

function formatLine(level: string, msg: string, ctx?: Record<string, unknown>): string {
  const time = new Date().toISOString();
  const base = `${time} ${level.toUpperCase()} ${msg}`;
  return ctx ? `${base} ${safeJson(ctx)}` : base;
}

export const logger = {
  debug(msg: string, ctx?: Record<string, unknown>) {
    if (!shouldLog("debug")) return;
    console.log(formatLine("debug", msg, ctx));
  },
  info(msg: string, ctx?: Record<string, unknown>) {
    if (!shouldLog("info")) return;
    console.log(formatLine("info", msg, ctx));
  },
  warn(msg: string, ctx?: Record<string, unknown>) {
    if (!shouldLog("warn")) return;
    console.warn(formatLine("warn", msg, ctx));
  },
  error(msg: string, ctx?: Record<string, unknown>) {
    if (!shouldLog("error")) return;
    console.error(formatLine("error", msg, ctx));
  },
};
```

✅ポイント

* `LOG_LEVEL=info` なら `debug()` は出ない🙈
* `warn/error` は `console.warn/console.error`（stderr寄り）へ🧯
* 変な値が来ても `info` にフォールバックして事故を避ける🛡️

![Safe Fallback Mechanism](./picture/docker_observability_ts_study_008_06_safe_fallback.png)

---

## 2) ルートにログを仕込む 🚪🧾

例として `src/server.ts` がこんな感じだとして…（あなたのファイル名に合わせてOK）👇

```ts
// src/server.ts（例）
import express from "express";
import { logger } from "./logger";

const app = express();

app.get("/ping", (req, res) => {
  logger.info("GET /ping", { route: "/ping" });
  logger.debug("ping: headers (debug only)", { ua: req.headers["user-agent"] });
  res.json({ ok: true });
});

app.get("/slow", async (req, res) => {
  const start = Date.now();
  logger.info("GET /slow: start");
  // わざと遅くする
  await new Promise((r) => setTimeout(r, 800));
  const ms = Date.now() - start;

  // 遅かったらWARNにする（目安なので適当でOK）
  if (ms >= 700) {
    logger.warn("GET /slow: slow response", { ms });
  } else {
    logger.info("GET /slow: ok", { ms });
  }

  res.json({ ok: true, ms });
});

app.get("/boom", (req, res) => {
  try {
    throw new Error("boom!");
  } catch (e) {
    logger.error("GET /boom: failed", { err: (e as Error).message });
    res.status(500).json({ ok: false });
  }
});

app.listen(3000, () => {
  logger.info("server started", { port: 3000, logLevel: process.env.LOG_LEVEL ?? "info" });
});
```

💡ここでの学び

* 「普段見たい」＝ `INFO`
* 「遅い/怪しい」＝ `WARN`
* 「失敗した」＝ `ERROR`
* 「調査用の細かい情報」＝ `DEBUG` 🔍

---

## 3) Compose で LOG_LEVEL を渡せるようにする 🧩

`compose.yml` の `api` サービスに環境変数を足します👇

```yaml
services:
  api:
    environment:
      LOG_LEVEL: ${LOG_LEVEL:-info}
```

これで、外側（あなたの端末側）で `LOG_LEVEL` を変えるだけで切り替え可能🎛️

---

## 4) 動かして確認（Windows PowerShell例）🪟💻

### A) まずは INFO（デフォルト）で起動 🟢

```powershell
docker compose up -d --build
docker compose logs -f api
```

別ターミナルで叩く：

```powershell
curl http://localhost:3000/ping
curl http://localhost:3000/slow
curl http://localhost:3000/boom
```

👉 **期待**：`INFO/WARN/ERROR` は見えるけど、`DEBUG` は見えない🙈

---

### B) DEBUG に上げて再起動 🔍

```powershell
$env:LOG_LEVEL="debug"
docker compose up -d --force-recreate
docker compose logs -f api
```

👉 **期待**：さっきは出なかった `ping: headers (debug only)` が出る✨

---

### C) ERROR まで絞る（本番寄り）🔴

```powershell
$env:LOG_LEVEL="error"
docker compose up -d --force-recreate
```

👉 **期待**：`/ping` や `/slow` は静かになる（障害っぽい時だけ鳴る）🧯

---

## 5) ログの出方（例）👀

INFO のとき：

* `INFO server started ...`
* `INFO GET /ping ...`
* `WARN GET /slow: slow response ...`
* `ERROR GET /boom: failed ...`

DEBUG のとき：

* 上に加えて `DEBUG ping: headers (debug only) ...` が増える🔍

---

## ⑥ つまづきポイント（あるある3つ）🪤

1. **LOG_LEVEL を変えたのに反映されない**😵
   → Compose の環境変数は「コンテナ作り直し」が必要なことが多いです。`--force-recreate` を付けると確実👍

2. **typo（`debgu` とか）で全部出なくなった/増えた**🙃
   → 今回の logger は **変な値なら info** に逃がしてるので大事故は防げます🛡️

3. **DEBUG に “秘密” を入れちゃう**🙈🔒

   ![Secret Leak Trap](./picture/docker_observability_ts_study_008_07_secret_leak_trap.png)

   → 「開発のつもりが本番でオンになってた」って事故が起きがち。
   `Authorization` とか `token` とかは、たとえ DEBUG でも基本出さない癖をつけるのが安全です✅

---

## ⑦ ミニ課題（15分）⏳🧩

次のルールでログを整理してみてください🙂

* `/ping`：アクセスは `INFO`、細かい情報は `DEBUG`
* `/slow`：700ms以上は `WARN`
* `/boom`：必ず `ERROR`（エラーメッセージ付き）

そして `LOG_LEVEL=info` と `LOG_LEVEL=debug` で **出る行数がどう変わるか**を比べてメモ📝✨

---

## ⑧ AIに投げるプロンプト例（コピペOK）🤖📋

```text
あなたはNode.js/TypeScriptのレビュー係です。
このAPI（/ping /slow /boom）のログ設計を、DEBUG/INFO/WARN/ERRORの観点で改善してください。

条件：
- INFOは運用で毎日見る前提
- DEBUGは調査用で普段はOFF
- WARNは「放置すると事故りそう」
- ERRORは「失敗した」
出力：
- どのログをどのレベルにするか（箇条書き）
- 追加すると便利なctxフィールド案（例：route, ms, status）
- やってはいけないログ（秘密情報など）
```

---

## ⑨ 章のまとめ 🏁🌈

* ログレベルは **「重要度」＋「量のコントロール」** 🎚️
* `LOG_LEVEL` で **調査時だけ DEBUG**、普段は INFO 以上が基本🧠
* コンテナ時代のログは「stdoutに出して外側が回収」が王道📣([12factor.net][1])
* Docker 側は logging driver で扱うので、出しすぎはディスク事故の元💥（`local` driver 推奨などの話もここにつながる）([Docker Documentation][2])

---

## 次章（第9章）へのつなぎ 🧱🔎

次はこの logger を **“1行文字列” → “JSON（構造化ログ）”** に進化させます。
そうすると検索が超ラクになって、`reqId`（第10章）とも相性抜群になります🧵✨

ちなみに本日時点の Node.js は **v24 が Active LTS** で、プロダクションは LTS 系を使うのが推奨、という立て付けです🟢([nodejs.org][3])

[1]: https://12factor.net/logs?utm_source=chatgpt.com "Treat logs as event streams"
[2]: https://docs.docker.com/engine/logging/configure/ "Configure logging drivers | Docker Docs"
[3]: https://nodejs.org/en/about/previous-releases "Node.js — Node.js Releases"
