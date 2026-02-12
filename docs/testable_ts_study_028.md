# 第28章：観測（ログ）もI/O！テスタブルにする📈📝

![testable_ts_study_028_spy_logger.png](./picture/testable_ts_study_028_spy_logger.png)

## この章でできるようになること🎯✨* `console.log` を卒業して、**差し替えできるLogger**にできる🧩


* 「あとで調査できるログ」を**設計**できる🕵️‍♀️🔎
* テストでは **スパイ（記録係）Logger** で「大事なログが出た？」を確認できる👀🧪
* ついでに「危ないログ（個人情報とか）」を避けられるようになる🚫🙅‍♀️ ([OWASP Cheat Sheet Series][1])

---

## 28-1. まず大前提：ログは “外の世界” に出る＝I/O だよ📣🌍ログって「画面に出すだけ」っぽく見えるけど、実際は…



* コンソール
* ファイル
* 監視サービス（Datadog / Grafana / Cloud Loggingとか）
* ログ収集基盤（Elastic など）

…みたいに **外部に送られるデータ**なんだよね🛰️
だからログを中心ロジックにベタ書きすると、**テストが不安定**になったり、**設計が汚れやすい**の🥲

✅ 結論：ログも `fetch` や DB と同じで「境界の外」扱いにして、**差し替え可能**にするのが勝ち✌️✨

---

## 28-2. “良いログ” の条件（ざっくり7つ）

🌟📝ログは「出せばOK」じゃなくて、**あとで読む未来の自分を助ける道具**だよ🥹💗



### ✅ ① まず “イベント” として書く「いま何が起きた？」を、**イベント名**で固定するのが超強い💪
例：

* `order.place.started`
* `order.place.succeeded`
* `order.place.failed`

→ 文言が多少変わっても、イベント名が同じなら検索できる🔎✨

### ✅ ② 構造化（JSONっぽく）

する文字列だけだと検索がつらい😵‍💫
`{ event, orderId, userId, elapsedMs }` みたいに **キー付き**が最強！
（Pinoみたいな構造化ロガーが人気なのはこの理由だよ📦） ([getpino.io][2])

### ✅ ③ レベル（debug/info/warn/error）

を決める* `info`：正常系の重要イベント🌈


* `warn`：仕様上ありえる失敗（在庫なし等）⚠️
* `error`：外部都合や想定外（通信失敗等）🔥

### ✅ ④ “理由” を残す（失敗ログが命）

失敗のときは特に、



* 何がダメだった？
* どのID？
* どの分岐？

が分かる情報を残すと未来の自分が泣いて喜ぶ😭✨

### ✅ ⑤ 個人情報・秘密は絶対に入れない🙅‍♀️

🔒パスワード、トークン、住所、メール本文…は基本ログに出さない！
OWASPも「機密情報のログ出力は危険」って強く言ってるよ🚨 ([OWASP Cheat Sheet Series][1])

### ✅ ⑥ 相関ID（requestId）

で “一本の物語” にする🧵同じリクエストのログを追えると捜査が一気に楽になるよ🕵️‍♀️
Nodeなら `AsyncLocalStorage` を使う方法がよく紹介されてる✨ ([dash0.com][3])

### ✅ ⑦ テストが壊れにくい形にする🧪ログの文字列を丸ごと一致させるテストは、だいたい地獄👿
→ **イベント名 + 必須フィールドだけ**を検証するのが安定👍

---

## 28-3. 設計の型：「中心はログの “中身” を決める、外側が “出力” する」🏠➡️

🌍ここがこの章のキモだよ〜💡✨



### パターンA：Loggerを注入する（いちばん分かりやすい）

🎁中心（UseCase）は `logger.info(...)` みたいに呼ぶけど、実体は外から渡す。

### パターンB：中心は “ドメインイベント” を返す（よりキレイ）

💎中心は「起きたこと」をイベントとして返す
外側がそれをログにする。
（中心がI/Oをより知らなくて済む👍）

この章では **分かりやすさ優先でパターンA**で行くね😊✨
（Bも最後にチラ見せするよ👀）

---

## 28-4. Loggerを “最小の約束” にする📜✨### ① まず型を決める（イベント中心）

🧠

```ts
// core/logger.ts
export type LogLevel = "debug" | "info" | "warn" | "error";

export type LogEntry = {
  level: LogLevel;
  event: string;          // 固定したイベント名
  message?: string;       // 人間向け補助（なくてもOK）
  meta?: Record<string, unknown>; // 検索したい付帯情報
  err?: unknown;          // 例外があるならここ
};

export interface Logger {
  log(entry: LogEntry): void;

  debug(event: string, meta?: Record<string, unknown>): void;
  info(event: string, meta?: Record<string, unknown>): void;
  warn(event: string, meta?: Record<string, unknown>): void;
  error(event: string, err?: unknown, meta?: Record<string, unknown>): void;
}
```

ポイントはこれ👇💖

* `event` を必須にして、**ブレない軸**を作る🔩
* `meta` は検索のために **キー付き**にする🔎
* `error` は `err` を別枠にしておく（スタック追いやすい）🔥

---

## 28-5. 中心ロジックでログを “イベントとして” 出す📦📝

題材：注文を確定する `placeOrder`（すごく簡略版）🛒🍕



```ts
// core/placeOrder.ts
import { Logger } from "./logger";

type PlaceOrderInput = { orderId: string; userId: string; totalYen: number };

type PlaceOrderResult =
  | { ok: true }
  | { ok: false; reason: "INSUFFICIENT_STOCK" | "PAYMENT_FAILED" };

export async function placeOrder(
  input: PlaceOrderInput,
  deps: { logger: Logger; pay: (yen: number) => Promise<boolean>; reserveStock: (orderId: string) => Promise<boolean> }
): Promise<PlaceOrderResult> {
  const { logger, pay, reserveStock } = deps;

  logger.info("order.place.started", { orderId: input.orderId, userId: input.userId });

  const reserved = await reserveStock(input.orderId);
  if (!reserved) {
    logger.warn("order.place.failed", { orderId: input.orderId, reason: "INSUFFICIENT_STOCK" });
    return { ok: false, reason: "INSUFFICIENT_STOCK" };
  }

  const paid = await pay(input.totalYen);
  if (!paid) {
    logger.warn("order.place.failed", { orderId: input.orderId, reason: "PAYMENT_FAILED" });
    return { ok: false, reason: "PAYMENT_FAILED" };
  }

  logger.info("order.place.succeeded", { orderId: input.orderId });
  return { ok: true };
}
```

ここ最高ポイント😍✨

* 「開始/成功/失敗」が **イベントで固定**されてる
* 失敗の理由 `reason` が **meta**に入ってる
* テストは `order.place.failed` が出たか？を見ればいい👀🧪

---

## 28-6. 外側：Pinoで “本番のLogger” を作る🚀🧰Node/TypeScript界隈だと **Pino** は「速い・構造化しやすい」で定番寄りだよ📌 ([getpino.io][2])

しかも **redaction（伏せ字）** とか **child logger**（共通metaを付けた子ロガー）も用意されてるのが強い💪 ([getpino.io][2])

```ts
// infra/pinoLogger.ts
import pino from "pino";
import { Logger, LogEntry } from "../core/logger";

export function createPinoLogger(): Logger {
  const base = pino({
    level: "info",
    // 例：うっかり入れても伏せたいキー（実運用ではもっと慎重に！）
    redact: {
      paths: ["meta.password", "meta.token", "meta.authorization"],
      remove: true,
    },
  });

  const log = (entry: LogEntry) => {
    const { level, event, message, meta, err } = entry;
    // Pinoはオブジェクトを渡すと構造化ログになる✨
    (base as any)[level]({ event, ...meta, err }, message ?? event);
  };

  return {
    log,
    debug: (event, meta) => log({ level: "debug", event, meta }),
    info: (event, meta) => log({ level: "info", event, meta }),
    warn: (event, meta) => log({ level: "warn", event, meta }),
    error: (event, err, meta) => log({ level: "error", event, err, meta }),
  };
}
```

※「何を伏せるか」は本当に大事だよ〜！
OWASPも「機密情報をログに出すな」ってはっきり言ってる🚫 ([OWASP Cheat Sheet Series][1])

---

## 28-7. テスト：SpyLoggerで “ログが出た？” を検証する🕵️

‍♀️🧪### ① テスト用SpyLogger（記録係）

を作る📝

```ts
// test/spyLogger.ts
import { Logger, LogEntry } from "../core/logger";

export class SpyLogger implements Logger {
  public entries: LogEntry[] = [];

  log(entry: LogEntry): void {
    this.entries.push(entry);
  }
  debug(event: string, meta?: Record<string, unknown>): void {
    this.log({ level: "debug", event, meta });
  }
  info(event: string, meta?: Record<string, unknown>): void {
    this.log({ level: "info", event, meta });
  }
  warn(event: string, meta?: Record<string, unknown>): void {
    this.log({ level: "warn", event, meta });
  }
  error(event: string, err?: unknown, meta?: Record<string, unknown>): void {
    this.log({ level: "error", event, err, meta });
  }
}
```

### ② placeOrder のテスト例（ログも確認）

👀✨（テストランナーは今まで使ってるやつでOK！ここでは雰囲気で書くね🧁）



```ts
// test/placeOrder.test.ts
import { describe, it, expect } from "vitest";
import { placeOrder } from "../core/placeOrder";
import { SpyLogger } from "./spyLogger";

describe("placeOrder", () => {
  it("在庫がないとき、failedログに理由が残る", async () => {
    const logger = new SpyLogger();

    const result = await placeOrder(
      { orderId: "o-1", userId: "u-1", totalYen: 1200 },
      {
        logger,
        reserveStock: async () => false,
        pay: async () => true,
      }
    );

    expect(result).toEqual({ ok: false, reason: "INSUFFICIENT_STOCK" });

    // ✅ 文字列全文一致じゃなく、イベントと必須フィールドを見るのがコツ✨
    const failed = logger.entries.find((e) => e.event === "order.place.failed");
    expect(failed?.level).toBe("warn");
    expect(failed?.meta).toMatchObject({ orderId: "o-1", reason: "INSUFFICIENT_STOCK" });
  });
});
```

このテスト、めちゃ “壊れにくい” 🙌💗

* 文言 `message` を変えても壊れない
* 大事な「イベント」と「理由」が守れる
* ログの役割（調査できる）をテストで固定できる

---

## 28-8. もう一段プロっぽく：相関IDで追跡しやすくする🧵🔎「同じリクエストのログを一本につなぐ」ために requestId を付けると超便利✨
Nodeでは `AsyncLocalStorage` を使う方法がよく紹介されてるよ📌 ([dash0.com][3])

ここでは超シンプルに「外側が logger を child 化する」イメージだけ置いとくね👇
（Pinoの child logger は “共通metaを付けた子” を作れるやつ✨） ([GitHub][4])

* 外側（HTTPハンドラとか）で `requestId` を作る
* `loggerWithReq = logger.child({ requestId })` みたいにして
* その `loggerWithReq` を中心に渡す

→ 中心は何も意識せず、ログに requestId が乗る！最高！🥳

---

## 28-9. （おまけ）

パターンB：中心はイベントを返す💎✨「中心がLogger依存するのすら気になる…！」ってなったら、



* 中心：`DomainEvent[]` を返す
* 外側：それをログにする

にすると、中心がもっとピュアになるよ🍰✨
ただ、最初はパターンAでぜんぜんOK🙆‍♀️（現場でも普通に使う！）

---

## 28-10. まとめ🌈

📝* ログはI/Oだから、**直書きしない**で差し替え可能にする🚪✨


* **イベント名 + 構造化meta**で「調査できるログ」を作る🕵️‍♀️
* テストは **SpyLogger** で「大事なログが出た？」を確認する👀🧪
* 機密情報はログに入れない（ガチで危ない）🚫🔒 ([OWASP Cheat Sheet Series][1])

---

## ミニ課題（15〜25分）

🍬⏳1. `placeOrder` に `elapsedMs`（処理時間）を meta に入れてみよ⏱️✨
2. `order.place.started` が必ず出るテストを書こう🧪
3. **失敗理由が増えた**とき（例：`ADDRESS_INVALID`）でも、ログ設計が崩れないか確認しよ🧠📝

---

次の章（第29章）は「AI拡張と上手に進めるコツ」🤖🎀
この章で作った **ログイベント設計**は、AIにケース洗い出ししてもらうとめっちゃ捗るよ〜🥳

[1]: https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html?utm_source=chatgpt.com "Logging - OWASP Cheat Sheet Series"
[2]: https://getpino.io/?utm_source=chatgpt.com "Pino"
[3]: https://www.dash0.com/guides/contextual-logging-in-nodejs?utm_source=chatgpt.com "Contextual Logging Done Right in Node.js with ..."
[4]: https://github.com/pinojs/pino/blob/main/docs/api.md?utm_source=chatgpt.com "pino/docs/api.md at main · pinojs/pino"
