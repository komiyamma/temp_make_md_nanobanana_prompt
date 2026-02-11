# 第89章：エラー設計③：ユーザー向けと開発者向けを分ける👤🛠️

## この章のゴール🎯💖

![この章のゴール🎯💖](./picture/ddd_ts_study_089_visual_1.png)


* ユーザーには「優しく・安全な」エラー表示を出せるようになる🙂🌷
* 開発者は「原因が一発で追える」ログを残せるようになる🔍🧰
* そして… **“表示は優しいのに、運用は強い”** アプリに近づく💪✨

---

## 1) なんで分ける必要あるの？😳💭

エラーって、ひとつに見えて **実は2種類の情報** が混ざりがちなの👇

### ✅ ユーザー向け（優しさ担当）👤🌸

* 何が起きたか（ざっくり）
* 次にどうすればいいか（再試行・入力見直し・時間置く）
* 不安にさせない言い方（スタックトレースとか絶対NG🙅‍♀️）

### ✅ 開発者向け（解析担当）🛠️🧠

![✅ 開発者向け（解析担当）🛠️🧠](./picture/ddd_ts_study_089_visual_2.png)


* エラーコード（分類）
* どこで起きた？（ユースケース名、集約ID、状態）
* 何が入ってた？（入力の要点 ※ただし秘密は除外）
* 追跡ID（requestId / traceId）
* 例外のスタックトレース（内部だけ）

ここが混ざると事故ります💥
たとえばユーザー画面に **DB名・SQL・スタックトレース** が出ると、攻撃者にヒントを渡しちゃう＆普通のユーザーも怖い😱
**こういう“内部情報をユーザーに見せる”のは危険**って、セキュリティの世界でも強く注意されてるよ⚠️ ([owasp.org][1])

---

## 2) まず大原則：ユーザーには「安全な文」、内部には「詳しい記録」🧯🧾

ざっくりルールを決めちゃうのが最強💪

* **想定内の失敗（業務ルール違反）**
  → ユーザーに「具体的で直せる」メッセージOK🙂✅
  （例：期限切れ、数量が0、支払い済みで変更不可）

* **想定外の失敗（バグ・障害）**
  → ユーザーには「一般的で優しい」メッセージ🙂🌧️
  → 詳細はログへ（スタックトレース含む）🛠️🧯

この「ユーザーは汎用表示＋内部ログで解析」という形は、セキュリティの定番設計としても推奨されてるよ📌 ([cheatsheetseries.owasp.org][2])

---

## 3) “どこで分ける？”の答え：境界で分ける🚧✨

DDDの感覚でいうとこう👇

* **ドメイン層**：ルール違反を “種類（コード）” として表現する（例外でもResultでもOK）
* **アプリ層 / プレゼン層（API/UI）**：

  * ユーザー向け文を決める（翻訳する）👤
  * 開発者向けログを残す🛠️

つまり、ドメインは **「表示文章」より「意味（コード）」** を持つのがスッキリ✨
ユーザー向け文章は、最終的にUI側で調整しやすいし、文言修正も安全🎀

---

## 4) 最小で強い“エラーの型”を作ろう📦💎

### 4-1. エラーコード（分類）を固定する🏷️

![4-1. エラーコード（分類）を固定する🏷️](./picture/ddd_ts_study_089_visual_3.png)


「何が起きたか」を文字列で固定すると、ログも分析も楽になるよ✨

```ts
// domain/errors/ErrorCode.ts
export type ErrorCode =
  | "ORDER_NOT_FOUND"
  | "ORDER_ALREADY_PAID"
  | "ORDER_ALREADY_CONFIRMED"
  | "INVALID_QUANTITY"
  | "UNEXPECTED";
```

### 4-2. ドメインのエラー（表示文は入れすぎない）🧠

```ts
// domain/errors/DomainError.ts
import type { ErrorCode } from "./ErrorCode";

export class DomainError extends Error {
  constructor(
    public readonly code: ErrorCode,
    message: string,
    public readonly meta: Record<string, unknown> = {},
    options?: { cause?: unknown }
  ) {
    super(message, options);
    this.name = "DomainError";
  }
}
```

* `message`：開発者が読む用（ログに出てもOKな範囲）🛠️
* `meta`：調査に必要な追加情報（ただし秘密は入れない🙅‍♀️🔑）

---

## 5) ユーザー向けは“翻訳辞書”で作る📖🌸

ユーザーへ出す文は **エラーコード→文** の辞書で管理すると超安全✨
（ドメインの都合で文章が変に引きずられない🎀）

```ts
// app/errors/PublicError.ts
import type { ErrorCode } from "../../domain/errors/ErrorCode";

export type PublicError = Readonly<{
  code: ErrorCode;
  message: string;      // ユーザー表示
  supportId: string;    // 問い合わせ用ID（requestId/traceIdなど）
}>;
```

```ts
// app/errors/publicMessageMap.ts
import type { ErrorCode } from "../../domain/errors/ErrorCode";

export const publicMessageMap: Record<ErrorCode, string> = {
  ORDER_NOT_FOUND: "注文が見つからなかったよ…🥺 もう一度読み込みしてみてね🙏",
  ORDER_ALREADY_PAID: "この注文は支払い済みだよ💳✨ 変更できないみたい…！",
  ORDER_ALREADY_CONFIRMED: "この注文は確定済みだよ✅ 変更できないよ〜🙇‍♀️",
  INVALID_QUANTITY: "数量が正しくないみたい…😵‍💫 1以上で入れてね！",
  UNEXPECTED: "ごめんね、予期しないエラーが起きたよ…😢 もう一度試してみてね🙏",
};
```

---

## 6) “ログ用”の情報は、別でまとめる🧾🛠️

ログは **検索しやすい形（構造化）** が強いよ🔍✨
そして **追跡できるID** が命！

### 6-1. 追跡ID（supportId）って？🆔

![6-1. 追跡ID（supportId）って？🆔](./picture/ddd_ts_study_089_visual_4.png)


ユーザーに「この番号を教えてね」って出せるやつ！
運用でめちゃ助かる🎯✨

* requestId（リクエストごとのID）
* traceId（分散トレースのID）

ログとトレースを紐づけるなら、**traceId/spanId をログに入れる**のが標準的な考え方だよ🔗
OpenTelemetry のログ仕様でも **TraceId / SpanId フィールド**が定義されてる📌 ([OpenTelemetry][3])

---

## 7) 例：PlaceOrder で「ユーザー表示」と「ログ」を分離する☕🧾✨

### 7-1. 変換関数：unknown → PublicError + logFields

```ts
// app/errors/toPublicAndLog.ts
import { DomainError } from "../../domain/errors/DomainError";
import type { PublicError } from "./PublicError";
import { publicMessageMap } from "./publicMessageMap";
import type { ErrorCode } from "../../domain/errors/ErrorCode";

type LogFields = Record<string, unknown>;

export function toPublicAndLog(
  e: unknown,
  ctx: { supportId: string; usecase: string; traceId?: string; spanId?: string }
): { publicError: PublicError; logFields: LogFields; level: "warn" | "error" } {
  // 想定内（業務ルール）
  if (e instanceof DomainError) {
    const code = e.code;
    return {
      publicError: {
        code,
        message: publicMessageMap[code],
        supportId: ctx.supportId,
      },
      logFields: {
        ...ctx,
        kind: "domain",
        code,
        meta: e.meta, // 秘密は入れない前提✨
      },
      level: "warn",
    };
  }

  // 想定外（バグ/障害）
  const code: ErrorCode = "UNEXPECTED";
  return {
    publicError: {
      code,
      message: publicMessageMap[code],
      supportId: ctx.supportId,
    },
    logFields: {
      ...ctx,
      kind: "unexpected",
      // Errorならstackも取れる（ログ側だけ！）
      stack: e instanceof Error ? e.stack : undefined,
    },
    level: "error",
  };
}
```

### 7-2. ユースケース側：返すのは PublicError、ログは別で残す🧾✨

![7-2. ユースケース側：返すのは PublicError、ログは別で残す🧾✨](./picture/ddd_ts_study_089_visual_5.png)


```ts
// app/usecases/PlaceOrder.ts
import type { Result } from "../utils/Result";
import { ok, err } from "../utils/Result";
import type { PublicError } from "../errors/PublicError";
import { toPublicAndLog } from "../errors/toPublicAndLog";

export class PlaceOrder {
  constructor(
    private readonly deps: {
      // repo / factory / logger など
      logger: { warn: (obj: any, msg: string) => void; error: (obj: any, msg: string) => void };
    }
  ) {}

  async execute(input: unknown, ctx: { supportId: string; traceId?: string; spanId?: string })
    : Promise<Result<{ orderId: string }, PublicError>> {
    try {
      // …ドメイン操作（例：注文作成）
      return ok({ orderId: "order-123" });
    } catch (e) {
      const { publicError, logFields, level } = toPublicAndLog(e, {
        supportId: ctx.supportId,
        usecase: "PlaceOrder",
        traceId: ctx.traceId,
        spanId: ctx.spanId,
      });

      // ログは構造化で残す（JSONになるイメージ）🧾
      if (level === "warn") this.deps.logger.warn(logFields, "placeOrder failed (domain)");
      else this.deps.logger.error(logFields, "placeOrder failed (unexpected)");

      // ユーザーへ返すのは安全なPublicErrorだけ👤🌸
      return err(publicError);
    }
  }
}
```

---

## 8) APIなら「Problem Details（RFC 9457）」で返すのが今どき📮✨

もしWeb APIを作るなら、エラーレスポンスを “標準形式” に寄せるとクライアントが超楽になるよ🎉

いまの標準は **RFC 9457（RFC 7807をobsolete）** で、`application/problem+json` を使うよ📌
これは IETF のRFCとして公開されてる📝 ([RFCエディタ][4])

例（イメージ）👇

```json
{
  "type": "https://example.com/problems/order-already-paid",
  "title": "支払い済みの注文です",
  "status": 409,
  "detail": "支払い後は明細を変更できません。",
  "instance": "/orders/order-123",
  "traceId": "4bf92f3577b34da6a3ce929d0e0e4736",
  "errorCode": "ORDER_ALREADY_PAID"
}
```

ポイント💡

* `title/detail` はユーザー寄り（でも内部事情は書かない）
* `traceId` や `errorCode` は運用に効く🛠️✨

---

## 9) ログで絶対やっちゃダメ🙅‍♀️🔑

### ❌ ユーザー画面に出しちゃダメ

* スタックトレース
* DB名、SQL、テーブル名
* 内部エラーコードそのまま（攻撃のヒントになることがある）
  こういうのが漏れる危険性は繰り返し注意されてるよ⚠️ ([owasp.org][1])

### ❌ ログにも出しちゃダメ

![❌ ログにも出しちゃダメ](./picture/ddd_ts_study_089_visual_6.png)


* パスワード、APIキー、アクセストークン
* カード番号、決済情報
* 住所やメールなどの個人情報（必要ならマスク）

「センシティブな情報はログに残さない」方向でガイドがあるよ🧯 ([cheatsheetseries.owasp.org][5])

---

## 10) 使える“運用強化”小ワザ3つ🪄✨

### ① supportId をユーザーに見せる🆔💬

「お問い合わせのとき、この番号を教えてください🙏」
→ ログ検索一発🔍✨

### ② ログに traceId/spanId を入れる🔗

ログとトレースをつなげると、原因追跡が爆速🏎️💨
OpenTelemetryのログ仕様にも TraceId/SpanId があるよ📌 ([OpenTelemetry][3])
実装では “ロガーが自動で trace context を埋める” 方式が推奨されがちだよ🧩 ([docs.datadoghq.com][6])

### ③ エラーは「分類」して集計できるようにする📈

![③ エラーは「分類」して集計できるようにする📈](./picture/ddd_ts_study_089_visual_7.png)


* `code`（エラーコード）
* `usecase`
* `kind`（domain / unexpected）
* `orderId`（あるなら）
  これだけで「最近ORDER_ALREADY_PAID増えてない？」みたいに見える👀✨

---

## 11) AIに頼むと強いプロンプト例🤖💡

そのままコピペでOKだよ👇

* 「このPublicErrorの文言、優しく短くして。責めない感じで。絵文字も少し入れて」🙂🌸
* 「このDomainErrorのmetaに入れるべき項目を、調査しやすさ優先で提案して（ただし個人情報と秘密は除外）」🧾🔍
* 「ログに残してはいけない情報リストを、このプロジェクト（カフェ注文）向けに作って」🙅‍♀️🔑

---

## 12) ミニ演習🎓✨（手を動かすと定着するよ〜！）

1. `ErrorCode` に `PAYMENT_FAILED` を追加💳😵
2. `publicMessageMap` に優しい文言を追加🙂
3. `toPublicAndLog` で `DomainError(code="PAYMENT_FAILED")` を `warn` にする
4. ユーザーには `supportId` が必ず出るようにする🆔✨
5. ログには `usecase`, `code`, `supportId` が必ず入るようにする🧾✅

---

## まとめ🎀✨

* エラーは **ユーザー向け（安全・優しい）** と **開発者向け（解析しやすい）** を分ける👤🛠️
* 想定内＝具体的に、想定外＝汎用表示＋ログで詳しく🧯
* APIなら RFC 9457 の `application/problem+json` が今どき📮 ([RFCエディタ][4])
* ログは traceId/spanId で相関できると運用が強い🔗 ([OpenTelemetry][3])
* 秘密や個人情報は **ユーザーにもログにも出さない**🙅‍♀️🔑 ([cheatsheetseries.owasp.org][5])

---

次の第90章は、割引＋期限＋エラーをまとめて統合して「実戦っぽく」なるところだよ🎓🔥
この章のコード（PublicError＋ログ分離）を土台にすると、めっちゃ気持ちよく進めるはず〜！💖

[1]: https://owasp.org/www-community/Improper_Error_Handling?utm_source=chatgpt.com "Improper Error Handling"
[2]: https://cheatsheetseries.owasp.org/cheatsheets/Error_Handling_Cheat_Sheet.html?utm_source=chatgpt.com "Error Handling - OWASP Cheat Sheet Series"
[3]: https://opentelemetry.io/docs/specs/otel/logs/data-model/?utm_source=chatgpt.com "Logs Data Model"
[4]: https://www.rfc-editor.org/rfc/rfc9457.html?utm_source=chatgpt.com "RFC 9457: Problem Details for HTTP APIs"
[5]: https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html?utm_source=chatgpt.com "Logging - OWASP Cheat Sheet Series"
[6]: https://docs.datadoghq.com/tracing/other_telemetry/connect_logs_and_traces/opentelemetry/?utm_source=chatgpt.com "Correlating OpenTelemetry Traces and Logs"
