# 第36章：観測ちょい入門：ログをどこに置く？🪪📊

![hex_ts_study_036[(./picture/hex_ts_study_036_observability_logging.png)

([Past chat][1])([Past chat][2])([Past chat][3])([Past chat][4])([Past chat][5])

# 第36章 観測ちょい入門：ログをどこに置く？🪪📊✨

この章は、「**障害が起きたときに最短で原因に辿りつける**」ようにする入門だよ😊
ヘキサゴナル的に **“中心を静かに保つ🧠✨”** まま、外側（Adapter）でログを整えるのがテーマ！

ちなみに今（2026/01時点）は **Node.js v24 が Active LTS**、TypeScript は **5.9.3 が最新**として話を進めるね🧩✨ ([Node.js][6])

---

## 1. この章のゴール 🎯✨

読み終わったら、こうなれるよ👇😊

* **ログを置く場所**を迷わない（中心は静か／外側で観測）🧠🪟
* **相関ID（Correlation ID）**で「このリクエストのログどれ？」が一瞬で追える🪪🔎
* **構造化ログ（JSON）**で、あとから検索・集計しやすいログになる📦📊
* File保存やHTTP入口など、**Adapterの“現場”に必要なログ**を入れられる🧩🚪💾

---

## 2. そもそも「観測（Observability）」って？👀✨

ざっくり“三本柱”があるよ👇

* **Logs（ログ）**：起きたことの記録（今回の主役）🪵
* **Metrics（メトリクス）**：回数・割合・時間などの数値📈
* **Traces（トレース）**：1リクエストの旅路（どこで遅い？）🗺️

最初はログだけでOK！でも、相関IDを入れておくと将来トレースへつながる✨（あとで気持ちよく育つ🌱）

---

## 3. ログの種類を分けるとラク😊🪄

ログって全部同じに見えるけど、実は役割が違うよ👇

* **アクセス系**：HTTPの開始/終了、ステータス、時間など🚪🌐
* **I/O系**：ファイル読めない、DB遅い、外部API落ちた💾😵‍💫
* **デバッグ系**：開発中だけ見たい情報（本番では控えめ）🧪
* **監査（Audit）系**：ビジネス的に「誰が何をした」📜（これは“仕様”寄り）

この章では **アクセス系 + I/O系**を中心にやるよ💪✨

---

## 4. ヘキサゴナルで「ログはどこに置く？」🧭🛡️

結論これ👇😊

### ✅ Adapterに置いていいログ

* HTTP入口：リクエスト開始/終了、ステータス、処理時間、相関ID 🚪🌐⏱️
* FileRepository：読み書きの失敗、リトライ判断、I/O時間 💾⏱️
* Composition Root：起動時の設定（どのRepoを使う等）🏗️✨
* 例外キャッチして **中心のエラーを“外側の表現”に変換したとき**のログ😵‍💫➡️🧩

### ❌ 中心（domain/app）に入れないログ

* 「タイトル空は禁止」みたいな **仕様の判定ログ**をベタベタ残す
* ユースケースの手順を “実況中継” するログ
* HTTP/ファイルの都合を中心へ持ち込むログ

中心は「静かに正しく判断して、結果（成功/失敗）を返す」だけが美しい🧠✨
ログは外側で「見える化」するのがヘキサゴナルの勝ち筋だよ🛡️

---

## 5. 相関IDってなに？🪪✨（超だいじ！）

**相関ID**は「この一連の処理をまとめて追うためのID」だよ😊
HTTPだと 1リクエストにつき1つ。CLIでも 1コマンド実行につき1つ、みたいに使う。

### よくある運用

* リクエストに `x-request-id` が来てたらそれを使う
* 来てなかったらサーバー側で新規発行
* レスポンスヘッダにも同じIDを返す（ユーザーが問い合わせしやすい）🧾✨

さらに将来の分散トレースでは、標準の `traceparent` ヘッダを使う世界もあるよ🌐（W3C標準） ([W3C][7])
OpenTelemetry などはこの文脈（Trace ID/Span ID）をログへ関連付ける考え方を持ってるよ📎✨ ([OpenTelemetry][8])

---

## 6. 実装方針：Context（相関ID）を “勝手に” 取れるようにする🪄

ここが今日のキモ👇😊

* リクエストの最初で **相関IDをContextへ入れる**
* どこでログしても **自動で相関IDが混ざる**
* でも中心（domain/app）は一切知らない🧠✨

Node.js には `AsyncLocalStorage` があって、非同期の流れをまたいでも「今のリクエストのContext」を追えるよ。しかも Stable 扱い。 ([Node.js][9])
（`async_hooks` の低レベルAPIより `AsyncLocalStorage` を推す流れもはっきりしてる） ([Node.js][10])

---

## 7. ハンズオン：ToDoミニに “最小ログ基盤” を入れる😊🔧

ここから手を動かすよ〜！💻✨
（ファイル名は一例。`domain/ app/ adapters/` の方針はそのまま🧩）

---

### 7.1 まずは logger を用意（構造化ログ）📦🪵

Nodeのログは **JSONで出す**のが後から強いよ💪
高速で定番の `pino` を使う例にするね（速い/JSON前提で扱いやすいと言われがち） ([dash0.com][11])

```ts
// src/adapters/observability/logger.ts
import pino from "pino";
import { getCorrelationId } from "./requestContext";

export type Logger = {
  info: (obj: object, msg?: string) => void;
  warn: (obj: object, msg?: string) => void;
  error: (obj: object, msg?: string) => void;
  debug: (obj: object, msg?: string) => void;
};

export function createLogger(): Logger {
  const base = pino({
    level: process.env.LOG_LEVEL ?? "info",
  });

  // 毎回 correlationId を混ぜる薄いラッパ（中心に入れない！）
  const withCid = (obj: object) => ({
    correlationId: getCorrelationId(),
    ...obj,
  });

  return {
    info: (obj, msg) => base.info(withCid(obj), msg),
    warn: (obj, msg) => base.warn(withCid(obj), msg),
    error: (obj, msg) => base.error(withCid(obj), msg),
    debug: (obj, msg) => base.debug(withCid(obj), msg),
  };
}
```

ポイント😊

* `Logger` は Port にしない（今回は **観測はAdapter側の都合**だから）
* “毎回IDを渡す” をやめる（渡し忘れ事故が起きる😇）

---

### 7.2 Context（相関ID）を入れる箱を作る🪪📦

```ts
// src/adapters/observability/requestContext.ts
import { AsyncLocalStorage } from "node:async_hooks";

type Store = { correlationId: string };

const als = new AsyncLocalStorage<Store>();

export function runWithCorrelationId<T>(correlationId: string, fn: () => T): T {
  return als.run({ correlationId }, fn);
}

export function getCorrelationId(): string | undefined {
  return als.getStore()?.correlationId;
}
```

ここで `AsyncLocalStorage` を使って、**非同期をまたいでも correlationId を取れる**ようにしたよ✨ ([Node.js][9])

---

### 7.3 HTTP Inbound Adapter で相関IDを作って入れる🚪🌐🪪

HTTPの入口でやることは超シンプル👇😊

1. 相関IDを決める（ヘッダ優先、なければ新規）
2. Context に入れる
3. 開始ログ / 終了ログを出す（時間も！）

Express風の例：

```ts
// src/adapters/http/requestLoggingMiddleware.ts
import type { Request, Response, NextFunction } from "express";
import { randomUUID } from "node:crypto";
import { runWithCorrelationId } from "../observability/requestContext";
import type { Logger } from "../observability/logger";

export function requestLoggingMiddleware(logger: Logger) {
  return (req: Request, res: Response, next: NextFunction) => {
    const cid = (req.header("x-request-id") ?? randomUUID()).toString();
    res.setHeader("x-request-id", cid);

    const start = Date.now();

    runWithCorrelationId(cid, () => {
      logger.info(
        { event: "http_request_start", method: req.method, path: req.path },
        "request start"
      );

      res.on("finish", () => {
        logger.info(
          {
            event: "http_request_end",
            method: req.method,
            path: req.path,
            statusCode: res.statusCode,
            durationMs: Date.now() - start,
          },
          "request end"
        );
      });

      next();
    });
  };
}
```

✅ これで、以後どこでログしても correlationId が勝手に付く✨
（中心は何も知らない🧠）

---

### 7.4 Outbound Adapter（FileRepository）に “現場ログ” を入れる💾🪵

I/O系は Adapter の責任範囲なので、ここはログを置いてOK😊

```ts
// src/adapters/repositories/FileTodoRepository.ts
import type { Logger } from "../observability/logger";

export class FileTodoRepository {
  constructor(
    private readonly filePath: string,
    private readonly logger: Logger
  ) {}

  async loadAll(): Promise<unknown[]> {
    const start = Date.now();
    try {
      // ...ファイル読み込み処理（省略）
      const data: unknown[] = [];
      this.logger.info(
        { event: "repo_load_success", repo: "FileTodoRepository", durationMs: Date.now() - start },
        "load ok"
      );
      return data;
    } catch (e) {
      this.logger.error(
        { event: "repo_load_fail", repo: "FileTodoRepository", err: toErr(e), durationMs: Date.now() - start },
        "load failed"
      );
      throw e; // 外側でラップする設計ならそこでラップしてもOK
    }
  }
}

function toErr(e: unknown) {
  if (e instanceof Error) return { name: e.name, message: e.message, stack: e.stack };
  return { message: String(e) };
}
```

💡 コツ

* `event` を固定値にすると検索が超ラク（`repo_load_fail` で一発）🔎
* エラーは “全部文字列化” じゃなく、最低 `name/message/stack` を持たせると強い💪

---

### 7.5 Composition Root で logger を作って Adapter に渡す🏗️🧩

Composition Root は “合体場所” だから、ここで `createLogger()` して配るのがキレイ😊

```ts
// src/compositionRoot.ts
import { createLogger } from "./adapters/observability/logger";
import { FileTodoRepository } from "./adapters/repositories/FileTodoRepository";

export function buildApp() {
  const logger = createLogger();

  const todoRepo = new FileTodoRepository("data/todos.json", logger);

  // HTTP adapter も CLI adapter も logger を受け取るようにする
  return { logger, todoRepo };
}
```

---

## 8. ログに何を入れる？おすすめ最小フィールド📌✨

迷ったらこれでOK😊

* `event`：固定イベント名（検索キー）🔎
* `correlationId`：相関ID（自動で付く）🪪
* `adapter` / `repo` / `useCase`：どこで起きた？🧩
* `durationMs`：遅い原因に効く⏱️
* `err`：失敗の中身（ただし秘匿情報は入れない）🔒

---

## 9. 逆に「入れちゃダメ」🙅‍♀️🔒

* アクセストークン、Cookie、生パスワード、秘密鍵 🔑💥
* 個人情報（メール、住所、電話）を丸ごと
* リクエストボディ丸ごと（必要なら“要約”や“マスク”）

「ログは便利だけど、漏れると事故」なので、ここは最初から慎重が勝ち😊✨

---

## 10. よくある失敗あるある😇（先に潰す）

* **相関IDがない**
  → ログが増えたのに追えない地獄になる😵‍💫
* **ログが文章だらけ**（構造化されてない）
  → 検索・集計・可視化が弱い😢
* **中心でログしてしまう**
  → じわじわ中心が汚れて設計が崩れる🧨

---

## 11. ミニ課題🎀📝（やると定着する！）

### 課題A：CLIにも相関IDを付けよう⌨️🪪

* コマンド開始時に UUID を作る
* `runWithCorrelationId()` で包む
* FileRepoのログにも同じIDが出てくるのを確認✨

### 課題B：遅い処理をあぶり出そう⏱️🔥

* FileRepoの読み込みにわざと `setTimeout` を挟む
* `durationMs` を見て「遅いのどこ？」が一瞬でわかるようにする

### 課題C：監査ログの“置き場所”を考えてみよう📜🤔

* 「完了にした」という“仕様イベント”は、ログじゃなく **ドメインイベント**として設計したくなる
* そのイベントを **外側でログ化**する、みたいな分離を妄想してみてね🧠✨

---

## 12. 今日のまとめ🎁💖

* ログは **Adapterで出す**（中心は静かに保つ）🧠🛡️
* 相関IDは **入口で作って、Contextで伝搬**🪪🪄
* 構造化ログ（JSON）＋ `event` 固定名で **検索性爆上がり**📦🔎
* `AsyncLocalStorage` は request-scope context に使える（Stable）✨ ([Node.js][9])
* 将来は `traceparent` や OpenTelemetry とも自然につながる🌐✨ ([W3C][7])

---

次の章（AI活用）へ行く前に、もしよければ「今のToDoミニのHTTP入口は Express ？それとも別？」みたいな形に合わせて、**あなたの構成にピッタリの差分パッチ**として章内コードを整形して出せるよ😊🧩

[1]: https://chatgpt.com/c/6972e69a-8e08-8321-b4f6-596e652a4f69 "Adapterの役割と注意点"
[2]: https://chatgpt.com/c/6972bb61-5e8c-8321-b99c-acbecfed6646 "Portとは何か🔌"
[3]: https://chatgpt.com/c/6970458f-7110-8321-8e2c-01eb1ab5a08b "ヘキサゴナル設計の略語"
[4]: https://chatgpt.com/c/6972b799-1568-8323-b58e-469e4b724359 "New chat"
[5]: https://chatgpt.com/c/696c6433-c6d4-8321-820c-cf446b14327d "第12章 Portの逆転技"
[6]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
[7]: https://www.w3.org/TR/trace-context/?utm_source=chatgpt.com "Trace Context"
[8]: https://opentelemetry.io/docs/concepts/context-propagation/?utm_source=chatgpt.com "Context propagation"
[9]: https://nodejs.org/api/async_context.html?utm_source=chatgpt.com "Asynchronous context tracking | Node.js v25.4.0 ..."
[10]: https://nodejs.org/api/async_hooks.html?utm_source=chatgpt.com "Async hooks | Node.js v25.4.0 Documentation"
[11]: https://www.dash0.com/guides/nodejs-logging-libraries?utm_source=chatgpt.com "The Top 7 Node.js Logging Libraries Compared"
