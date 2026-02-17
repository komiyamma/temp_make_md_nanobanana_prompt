# 第11章：エラーを逃さない：例外・Promise・プロセス終了 🧯⚠️

## ① 今日のゴール 🎯

この章を終えると、こんな状態になれます👇✨

* どんなエラーでも「最後に必ずログに残る」安全網を作れる 🕸️🧾
* **例外**（throw）と **Promiseの失敗**（reject）の“逃げ方の違い”がわかる 🧠
* `docker compose stop` で止めたとき（SIGTERM）に「最後のログを残してから」綺麗に終了できる 🚪🧹
* “落ちた理由”と“落ちたタイミング”がログから追える 🔍🧵

> ちなみに Node は、未処理の Promise 失敗（unhandled rejection）の扱いが昔より厳しめで、最近の Node は **デフォルトが `throw`**（未処理なら実質クラッシュ）です。([Node.js][1])
> そして 2026-02-10 時点では、Node の **LTS が 24.13.1 / Current が 25.6.1** になっています。([Node.js][2])

---

## ② 図（1枚）🖼️：エラーの“逃げ道マップ” 🗺️

![Error Escape Map Building](./picture/docker_observability_ts_study_011_01_error_escape_map.png)

ざっくりこの3階建てで守ります🏰✨

* **1F：ルート内のエラー**（Express が拾える）

  * `throw new Error()`（同期）✅
  * Express 5 なら `async` で投げた/失敗した Promise も ✅（自動で `next(err)`）([Express][3])

* **2F：非同期コールバック内のエラー**（Express が拾えないことがある）

  * `setTimeout(() => { throw ... })` みたいなやつ 💣
  * ここで落ちると「ルートの try/catch」では守れないことがある 🌀

* **3F：プロセス最終防衛線**（何があってもログを残す）

  * `process.on('uncaughtException')`（例外が最終的に漏れた）
  * `process.on('unhandledRejection')`（Promise の失敗が未処理）
  * ここで **ログ→安全に終了**（graceful shutdown）🧯🚪

---

## ③ 手を動かす（手順 5〜10個）🛠️✨

ここからは「いま動いてるミニAPI」に **“絶対に逃さない仕組み”** を足します💪😆

### 今回追加するファイル（例）📁

* `src/processHooks.ts`（プロセスの最終防衛線）
* `src/shutdown.ts`（終了手順を1箇所にまとめる）
* `src/app.ts`（わざと壊すエンドポイント追加）
* `src/index.ts`（起動時に hook を仕込む）

---

### 手順1：わざと壊すエンドポイントを追加 💥😈

`src/app.ts` に “事故再現用” の3つを足します（本番には置かないでね🙏）

```ts
import express from "express";

export function createApp() {
  const app = express();

  app.get("/ping", (_req, res) => res.json({ ok: true }));

  // ① Expressが拾える同期throw（これは普通にエラーハンドラへ行く）
  app.get("/throw-boom", (_req, _res) => {
    throw new Error("THROW_BOOM");
  });

  // ② Expressが拾えない典型：setTimeoutコールバックでthrow（未捕捉例外になりがち）
  app.get("/timer-boom", (_req, res) => {
    setTimeout(() => {
      throw new Error("TIMER_BOOM");
    }, 10);
    res.json({ ok: true, note: "10ms後に落ちるよ" });
  });

  // ③ 未処理Promise（unhandledRejection）をわざと起こす
  app.get("/promise-boom", (_req, res) => {
    void (async () => {
      throw new Error("PROMISE_BOOM");
    })(); // catchしないので未処理になりやすい
    res.json({ ok: true, note: "Promiseが裏で死ぬよ" });
  });

  return app;
}
```

---

### 手順2：終了手順（graceful shutdown）を1つにまとめる 🚪🧹

![Graceful Shutdown Sequence](./picture/docker_observability_ts_study_011_03_graceful_shutdown.png)

ポイントはこれ👇

* **2回目以降の shutdown を無視**（多重実行防止）🧯
* **新規リクエストは受けない**（任意）🛑
* **HTTPサーバーを close**（イベントループを空にして自然終了させる）🧼
* でも「待ちすぎ」は Docker に SIGKILL されるので、**締切タイマー**も持つ ⏳

`src/shutdown.ts`

```ts
import type http from "node:http";

type ShutdownOptions = {
  server: http.Server;
  logger: (level: "info" | "warn" | "error" | "fatal", msg: string, extra?: unknown) => void;
  // DBやキューがあるなら close関数をここに足していく
};

let shuttingDown = false;

export function createShutdown({ server, logger }: ShutdownOptions) {
  return async function shutdown(reason: string, err?: unknown) {
    if (shuttingDown) return;
    shuttingDown = true;

    logger("warn", `shutdown start: ${reason}`, err);

    // ここ重要：いきなり process.exit() しない！（ログが途中で切れたりする）
    // まずは exit code をセットして、自然終了を狙う
    process.exitCode = 1;

    // 締切：DockerにSIGKILLされる前に自分で終わる（例：8秒）
    const hardTimeoutMs = 8000;
    const timer = setTimeout(() => {
      logger("fatal", `shutdown timeout (${hardTimeoutMs}ms). forcing exit...`);
      process.exit(1);
    }, hardTimeoutMs);
    timer.unref();

    // HTTPサーバーを閉じる（新規接続を受けない）
    await new Promise<void>((resolve) => {
      server.close(() => resolve());
    });

    clearTimeout(timer);
    logger("info", "shutdown complete ✅");
    // ここでイベントループが空なら自然に落ちる
  };
}
```

---

### 手順3：プロセス最終防衛線を仕込む 🧯🕸️

![Process Hooks Shield](./picture/docker_observability_ts_study_011_05_process_hooks_shield.png)

`process.on('uncaughtException')` と `process.on('unhandledRejection')` は「最後の砦」です🏰
Node はデフォルトだと未捕捉例外で **stderrに出して exit(1)** しますが、ハンドラを付けると挙動が変わるので **“ログ→shutdown” を自分でやる** のが大事です。([Node.js][4])

`src/processHooks.ts`

```ts
export function installProcessHooks(params: {
  shutdown: (reason: string, err?: unknown) => Promise<void>;
  logger: (level: "info" | "warn" | "error" | "fatal", msg: string, extra?: unknown) => void;
}) {
  const { shutdown, logger } = params;

  // 未処理Promise（デフォルトは throw モード。未処理なら実質クラッシュ）:contentReference[oaicite:4]{index=4}
  process.on("unhandledRejection", (reason) => {
    logger("fatal", "unhandledRejection", reason);
    void shutdown("unhandledRejection", reason);
  });

  // 未捕捉例外（本来はstderr+exit(1)。ハンドラを付けるとデフォルト終了は消える）:contentReference[oaicite:5]{index=5}
  process.on("uncaughtException", (err, origin) => {
    logger("fatal", `uncaughtException (origin=${origin})`, err);
    void shutdown("uncaughtException", err);
  });

  // SIGTERM/SIGINT（Docker停止やCtrl+C）
  // ※非Windows環境だと、SIGTERM/SIGINT に listener を付けると “デフォルトで終了” が消える！
  // だから自分で shutdown して終わらせる必要があるよ🧨:contentReference[oaicite:6]{index=6}
  process.on("SIGTERM", () => {
    logger("warn", "received SIGTERM");
    void shutdown("SIGTERM");
  });
  process.on("SIGINT", () => {
    logger("warn", "received SIGINT");
    void shutdown("SIGINT");
  });
}
```

---

### 手順4：起動コードで「server」と「shutdown」と「hooks」をつなぐ 🔗🚀

`src/index.ts`

```ts
import http from "node:http";
import { createApp } from "./app";
import { createShutdown } from "./shutdown";
import { installProcessHooks } from "./processHooks";

function logger(level: "info" | "warn" | "error" | "fatal", msg: string, extra?: unknown) {
  const payload = {
    level,
    msg,
    time: new Date().toISOString(),
    ...(extra ? { extra } : {}),
  };
  // 第9章でJSONログにしてる想定なら、こんな感じでOK
  if (level === "error" || level === "fatal") console.error(JSON.stringify(payload));
  else console.log(JSON.stringify(payload));
}

const app = createApp();
const server = http.createServer(app);

const shutdown = createShutdown({ server, logger });
installProcessHooks({ shutdown, logger });

const port = Number(process.env.PORT ?? 3000);
server.listen(port, () => logger("info", `listening on :${port}`));
```

---

### 手順5：動作確認（3タイプを順番に壊す）🧪🔨

ターミナルで起動して（Composeでも直起動でもOK）、別ターミナルで叩きます👇

* ✅ まず普通

  * `curl http://localhost:3000/ping`

* 💥 同期throw（Expressが拾ってエラーハンドラへ）

  * `curl http://localhost:3000/throw-boom`

* 💣 timer-boom（プロセスが落ちる系）

  * `curl http://localhost:3000/timer-boom`

* 🧨 promise-boom（未処理Promise）

  * `curl http://localhost:3000/promise-boom`

期待すること（目標）🎯

* `timer-boom` / `promise-boom` で **fatalログが出て**、その後 **shutdownログが出て**、プロセスが終了する ✅
* 終了時に「最後のログが欠けない」✅

> Node の `--unhandled-rejections=mode` は、`throw/strict/warn/...` を選べて、**デフォルトは `throw`** です。([Node.js][1])

---

### 手順6：Docker停止で「最後のログ」を残せるか確認 🐳🛑🧾

![Signal Flow (Docker to Node)](./picture/docker_observability_ts_study_011_06_signal_flow.png)

Docker は停止時に、コンテナのメインプロセスへ **SIGTERM を送り**、猶予後に **SIGKILL** します。([Docker Documentation][5])
Compose でも同様に、`docker compose stop` は **SIGTERM → デフォルト10秒待つ → SIGKILL** です。([Docker Documentation][6])

* `docker compose up`（起動）
* `docker compose stop`（停止）

期待すること✅

* SIGTERM を受けたログが出る
* shutdown が走って、10秒以内に終了する（＝SIGKILLされない）

---

## ④ つまづきポイント（3つ）🪤😵‍💫

1. **「try/catch したのに落ちるんだけど！？」**

   ![Route vs Async Error](./picture/docker_observability_ts_study_011_02_route_vs_async_error.png)

   `setTimeout` やイベントのコールバックの中で `throw` すると、ルートの try/catch の外に飛びます💥
   → 対策：**その場で try/catch** するか、最終防衛線（`uncaughtException`）で拾う 🧯

2. **SIGTERM にリスナーを付けたら、逆に止まらなくなった**
   非Windows環境（コンテナ内Linuxなど）では、`SIGTERM`/`SIGINT` に listener を付けると **デフォルトの終了が消えます**。([Node.js][4])
   → 対策：必ず `shutdown()` で server close して、終わるところまで責任を持つ 🚪

3. **`process.exit()` を即呼びするとログが欠ける**

   ![Shutdown Timer Race](./picture/docker_observability_ts_study_011_04_shutdown_timer_race.png)

   `process.exit()` は “強制終了” なので、最後の出力が間に合わないことがあります😇
   → 対策：まず `process.exitCode = 1`、**close して自然終了**、締切だけ `setTimeout(() => process.exit(1))` ⏳

---

## ⑤ ミニ課題（15分）⏳🏃‍♂️

次の3つをやって、ログを貼って説明できたら勝ちです🏆✨

1. `/timer-boom` を叩いて、**fatal → shutdown** が出るのを確認 🧨
2. `/promise-boom` を叩いて、**unhandledRejection** が残るのを確認 🧯
3. `docker compose stop` をして、**SIGTERM を受けてから10秒以内に終了**できるのを確認 🐳✅([Docker Documentation][6])

---

## ⑥ AIに投げるプロンプト例（コピペOK）🤖📋

**プロセス最終防衛線を作る**🧯

```text
Node(TypeScript)のAPIで、process.on('uncaughtException') と process.on('unhandledRejection') を実装したいです。
要件：fatalログをJSONで出す / 多重shutdown防止 / server.closeして自然終了 / 8秒で強制exitの締切。
src/processHooks.ts と src/shutdown.ts に分けた例をください。
```

**「Expressが拾えないエラー」再現エンドポイント**💥

```text
Expressのルートで「setTimeout内でthrowしてプロセスが落ちる例」と、
「未処理Promise(reject)になる例」をそれぞれ作ってください。
本番に入れない注意コメントも付けてください。
```

**ログの形を第9章の構造化ログに寄せる**🧾🧱

```text
console.log(JSON.stringify(...))の簡易loggerを、
level/msg/time/requestId(あれば)/err(stack含む) を揃える形に改善してください。
fatalだけstderrに出す方針で。
```

---

## おまけ：この章の“超重要まとめ”🧠✨

* ルート内で拾えないエラーは確実に存在する（特にコールバック地獄系）💣
* **最終防衛線（process events）＋ graceful shutdown** があると “落ちた理由” が残せる 🧾
* Docker/Compose は止めるとき **SIGTERM → 猶予 → SIGKILL** なので、shutdown は時間勝負 ⏳🐳([Docker Documentation][5])

---

次章（第12章）は「秘密情報を守る：マスキングと禁止ルール 🙈🔒」なので、今回の fatal ログにも **token や Authorization が混ざらない** ように整えていきますよ〜😆✨

[1]: https://nodejs.org/api/cli.html "Command-line API | Node.js v25.6.1 Documentation"
[2]: https://nodejs.org/en/blog/release "Node.js"
[3]: https://expressjs.com/en/guide/error-handling.html "Express error handling"
[4]: https://nodejs.org/api/process.html "Process | Node.js v25.6.1 Documentation"
[5]: https://docs.docker.com/reference/cli/docker/container/stop/ "docker container stop | Docker Docs"
[6]: https://docs.docker.com/compose/support-and-feedback/faq/ "FAQs | Docker Docs"
