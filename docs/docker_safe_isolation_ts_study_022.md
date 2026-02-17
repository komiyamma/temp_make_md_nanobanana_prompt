# 第22章：ログ・エラー・デバッグで漏らさない（ここで漏れる）🫣🧯

この章は「秘密をちゃんと隠してるつもりなのに、**ログとエラーで全部バラす**」事故を止める回です😂
**“漏らさない作法”をコードに固定**して、以後ずっと楽できる形にします💪✨

---

## 1) まず結論：漏れる場所トップ3 🥇🥈🥉

![Top 3 Secret Leaks](./picture/docker_safe_isolation_ts_study_022_01_three_leaks.png)

1. **console.log / logger に “うっかり” 出す**（env全部、headers全部、例外オブジェクト全部…）🫠
2. **エラー応答にスタックトレースや内部情報を返す**（開発のノリのまま本番へ）💥
3. **デバッグ用に出したログが、永遠に残って共有される**（チケット、チャット、AI相談）📎🤖

ログは「自分だけが見るメモ」じゃなくて、現実には **“配布物”** になりがちです📦
（コンテナのログは `docker logs` / `docker compose logs` で誰でも見れたり、収集基盤に送られたりします）

---

## 2) 「秘密っぽいもの」一覧：これが1文字でもログに出たら負け😇🔒

![Forbidden Log Items](./picture/docker_safe_isolation_ts_study_022_02_forbidden_words.png)

最低限これらは **絶対にログに出さない** ルールにします👇

* **パスワード / APIキー / トークン / JWT / Cookie / セッションID** 🍪🔑
* `Authorization` ヘッダ（特に `Bearer ...`）🪪
* `.env` の中身、`process.env` の丸ごとダンプ 🌋
* `/run/secrets/*` の中身（Compose secrets の実体）📄

  * secrets はコンテナ内に **`/run/secrets/<secret_name>`** としてマウントされます ([Docker Documentation][1])
* 個人情報（メール、住所、電話、IP、カード情報など）🧑‍🦰📞💳

ログ設計の考え方としても「必要な情報だけ」「機密は記録しない」が強く推奨されます ([cheatsheetseries.owasp.org][2])

---

## 3) 今日からの作戦：3段ロックで守る🔐🔐🔐

![Three Layer Defense](./picture/docker_safe_isolation_ts_study_022_03_three_locks.png)

## ロックA：**“出すログ”を最小化**（そもそも入れない）✂️

* **リクエストボディは基本ログに入れない**（特にログイン、決済、設定系）🙅‍♂️
* `headers` を丸ごと出さない（必要なら許可リストで数個だけ）👀
* エラーも「全部 `err` を丸ごと出す」ではなく、**必要情報だけ構造化**する🧩

## ロックB：**ログライブラリで自動マスク**（うっかり保険）🧤

`pino` みたいに **redact（自動マスク）**を持つロガーを使うと、事故が激減します。
`pino` の redaction はパス指定で値をマスクできます ([GitHub][3])
※重要：**redact のパス文字列はユーザー入力から作らない**（安全上の注意） ([GitHub][3])

## ロックC：**収集基盤（OpenTelemetry等）側でも削る**（最後の砦）🏰

テレメトリは一度流れると外部に出ていく可能性があるので、**そもそも機密を載せない責任は実装側にある**、という前提です ([OpenTelemetry][4])
さらに Collector 側で **属性削除・マスク**もできます（redaction processor / transform など） ([GitHub][5])

---

## 4) 実装：TypeScriptで「漏らさない logger」を固定する🧱✨

ここからは「テンプレ化」して、以後ずっと使い回すやつです😄

## 4-1. logger.ts：pino + redact で “危険キー” を自動マスク🧤🪓

![Pino Redact Mechanism](./picture/docker_safe_isolation_ts_study_022_04_pino_redact.png)

```ts
// src/lib/logger.ts
import pino from "pino";

const isProd = process.env.NODE_ENV === "production";

/**
 * ここで “絶対に出しちゃダメなキー” を固定
 * ※ユーザー入力から paths を作らないこと（pinoの注意）
 */
const REDACT_PATHS = [
  "req.headers.authorization",
  "req.headers.cookie",
  "req.headers.set-cookie",
  "req.body.password",
  "req.body.pass",
  "req.body.token",
  "req.body.apiKey",
  "req.query.token",
  "user.password",
  "user.token",
  "secrets",
  "process.env", // “丸ごと出し”事故の保険（ただし process.env をそのまま渡さない運用が前提）
] as const;

export const logger = pino({
  level: process.env.LOG_LEVEL ?? (isProd ? "info" : "debug"),
  redact: {
    paths: [...REDACT_PATHS],
    censor: "[REDACTED]",
  },
  // 本番は人間より機械向け(JSON)でOK。開発はprettyでも良いが、まずは統一で。
  base: undefined,
  timestamp: pino.stdTimeFunctions.isoTime,
});
```

ポイント💡

* **“危険キーの辞書”をコードに固定**して、毎回悩まない📌
* `LOG_LEVEL=debug` にしても **redact は効く**（大事）🧯
* `process.env` を直接 logger に渡さないのが基本（保険としてパスは置いてるだけ）

---

## 4-2. リクエストログ：必要最小だけ書く（bodyは捨てる）🧾🚫

![Request Log Filtering](./picture/docker_safe_isolation_ts_study_022_05_request_filter.png)

```ts
// src/middleware/requestLog.ts
import type { Request, Response, NextFunction } from "express";
import { randomUUID } from "crypto";
import { logger } from "../lib/logger.js";

export function requestLog(req: Request, res: Response, next: NextFunction) {
  const requestId = req.headers["x-request-id"]?.toString() ?? randomUUID();
  res.setHeader("x-request-id", requestId);

  const start = Date.now();

  res.on("finish", () => {
    const ms = Date.now() - start;

    // ✅ “必要情報だけ”に絞る（headers/bodyは基本出さない）
    logger.info(
      {
        requestId,
        method: req.method,
        path: req.originalUrl,
        status: res.statusCode,
        ms,
      },
      "http_request"
    );
  });

  next();
}
```

これで、**追跡に必要な情報（いつ/どこ/何/どれくらい）**は残るのに、
**秘密が混ざりやすい部分（headers/body）を避けられます**👍

---

## 4-3. エラーハンドリング：返すメッセージは “控えめ”、ログは “十分” 🧯📦

![Production Error Shield](./picture/docker_safe_isolation_ts_study_022_06_error_shield.png)

Express は **本番環境だとスタックトレースをレスポンスに含めない**挙動が明記されています ([expressjs.com][6])
（ただし、自分の実装次第で簡単に漏れるので、ここで固定します）

```ts
// src/middleware/errorHandler.ts
import type { Request, Response, NextFunction } from "express";
import { logger } from "../lib/logger.js";

export function errorHandler(err: unknown, req: Request, res: Response, _next: NextFunction) {
  const isProd = process.env.NODE_ENV === "production";

  // “ログには十分” ただし req 全部や env 全部を渡さない
  logger.error(
    {
      method: req.method,
      path: req.originalUrl,
      // headersは丸ごと渡さない。必要なら許可リストで。
      err: normalizeError(err),
    },
    "unhandled_error"
  );

  // “返すのは控えめ”
  res.status(500).json({
    error: "Internal Server Error",
    ...(isProd ? {} : { detail: normalizeError(err) }), // 開発だけ詳細を返す
  });
}

function normalizeError(err: unknown) {
  if (err instanceof Error) {
    return {
      name: err.name,
      message: err.message,
      // stack は開発だけ使う運用にしてもOK（ここは返却側で制御）
      stack: err.stack,
    };
  }
  return { message: String(err) };
}
```

✅ これで

* クライアントには**余計な内部情報を返さない**
* サーバ側ログには**原因調査に必要な情報を残す**
  が両立できます😄

---

## 5) Compose secrets とログ：**“読み方”はOK、”出力”はNG**📄🙅‍♂️

Compose secrets はコンテナ内で `/run/secrets/<name>` のファイルになります ([Docker Documentation][1])
読み込むのは普通にOK。でも **値をログに出した瞬間に終わり**です😂

```ts
// src/lib/secrets.ts
import { readFileSync } from "node:fs";

export function readSecret(name: string): string {
  const path = `/run/secrets/${name}`;
  // ✅ 読むだけ。ログに出さない。
  return readFileSync(path, "utf-8").trim();
}
```

さらに注意⚠️

* 例外メッセージに secret を混ぜない（`throw new Error("token="+token)` とか）🫣
* 「デバッグだから一回だけ…」が一番危ない（ログは残る）🪦

---

## 6) ありがちな “漏れ方” デモ（演習）🧪🎯

## 演習1：`process.env` を出してしまう事故を潰す🌋🧯

1. わざとこう書く（悪い例）

```ts
console.log(process.env);
```

2. `docker compose logs` で見て「うわぁ…」ってなる😇
3. 直す：**env を丸ごと出さない**。必要な設定値だけ、しかもマスクして出す。

---

## 演習2：headers丸ごとログで `Authorization` が漏れる🪪💥

悪い例👇

```ts
logger.info({ headers: req.headers }, "debug_headers");
```

直し方（許可リスト方式）👇

```ts
logger.info(
  {
    requestId,
    userAgent: req.headers["user-agent"],
    // authorization/cookie は入れない！
  },
  "debug_request_meta"
);
```

---

## 演習3：本番でスタックトレースを返してしまう事故📉🧨

1. エラー時に `err.stack` をそのまま返す実装を入れてしまう
2. 本番で内部構造が見える（ライブラリ名、パス、SQL、etc…）
3. 直す：この章の `errorHandler` を採用。
   Express の公式ガイドでも、本番ではスタックをレスポンスに含めない方針が示されています ([expressjs.com][6])

---

## 7) AI拡張にログを貼る前の「3秒ルール」🤖⏱️🧼

![AI Log Sanitizer](./picture/docker_safe_isolation_ts_study_022_07_ai_sanitizer.png)

AI相談は便利だけど、ログは貼りがち！📎
**貼る前にこれだけ確認**👇

* `Authorization` / `Cookie` / `token=` / `apiKey=` / `password` の文字が見えたら **即マスク**🧤
* `.env` や secrets の値が混ざってそうなら **まず削る**✂️
* 「長いログ」を丸ごと貼らず、**必要な数十行だけ**にする📏

さらに強くしたいなら：

* **AIに貼る用の “sanitize スクリプト”** を用意して、コピペ前に必ず通す（おすすめ）✨

---

## 8) OpenTelemetry/ログ収集の落とし穴：一度送ると戻らない📡🫠

OpenTelemetryは「何が機密か」を自動判定できないので、**実装者が守る責任がある**と明記されています ([OpenTelemetry][4])
だから順番はこう👇

1. **アプリ側で機密を入れない**（最重要）
2. それでも混ざる前提で、Collector 側で **redaction / transform** で削る ([GitHub][5])

---

## 9) 仕上げ：この章の “合格ライン” ✅🎉

最後にチェック！これが全部YESなら勝ちです😄✨

* [ ] `headers` / `body` を丸ごとログしてない
* [ ] `Authorization` / `Cookie` / `token` 系は **自動マスク**される
* [ ] 本番のエラー応答に **スタックトレースを出してない**（Expressの方針とも整合） ([expressjs.com][6])
* [ ] secrets を読んでも、値をログに出してない（`/run/secrets` の扱いOK） ([Docker Documentation][1])
* [ ] 収集基盤に機密が流れない前提を作ってる（OpenTelemetryの注意点を踏んでる） ([OpenTelemetry][4])

---

次の章（第23章）は「ビルド時の秘密：BuildKit secretsでレイヤに残さない🏗️🤫」に入るはずなので、
この第22章で作った **“ログで漏らさない土台”** が効いてきますよ〜😄🔑

[1]: https://docs.docker.com/compose/how-tos/use-secrets/?utm_source=chatgpt.com "Secrets in Compose"
[2]: https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html?utm_source=chatgpt.com "Logging - OWASP Cheat Sheet Series"
[3]: https://github.com/pinojs/pino/blob/main/docs/redaction.md?utm_source=chatgpt.com "pino/docs/redaction.md at main · pinojs/pino"
[4]: https://opentelemetry.io/docs/security/handling-sensitive-data/?utm_source=chatgpt.com "Handling sensitive data"
[5]: https://github.com/open-telemetry/opentelemetry-collector-contrib/blob/main/processor/redactionprocessor/README.md?utm_source=chatgpt.com "Redaction processor - opentelemetry-collector-contrib"
[6]: https://expressjs.com/en/guide/error-handling.html?utm_source=chatgpt.com "Error handling"
