# 第87章：エラー設計①：ドメイン例外の作法🧯📌

DDDって「ルールを守る設計」だよね？✨
そのルールが破られそうなとき、**どう“失敗”を表現するか**がめちゃ大事です💥
この章では、**ドメイン例外（Domain Exception）を“仕様の一部”として設計する作法**を、カフェ注文ドメインで手を動かしながら覚えます☕🧾

---

## 0. 今日のゴール🎯✨

* 「これはドメイン例外で投げるべき？」が判断できる👀
* 例外に **型・メッセージ・原因（cause）・文脈（meta）** を持たせられる🧠
* アプリ層で **安全にcatchして扱える**（unknown対策も）🧤
* デバッグが一気にラクになる🛠️🎉

---

## 1. そもそも「ドメイン例外」って何？🤔💡

### ✅ ドメイン例外＝「仕様違反」を表すエラー

例：

* 支払い済みの注文に、もう一回 `pay()` しようとした💳💥
* 確定済みの注文に `addItem()` しようとした🧾🚫
* 数量が 0 とか -1 とかになった📏😵

こういうのは **“システムが壊れた” じゃなくて “操作が仕様に合ってない”** だよね。

### ❌ ドメイン例外じゃないもの（混ぜない！）

* DB接続失敗、ネットワーク失敗、ファイル読めない…みたいな「技術的な失敗」🌩️
  → それは **インフラ側** の責任（後半でやるやつ）

---

## 2. ドメイン例外の設計で、最低限そろえる4点セット🧰✨

ドメイン例外は、次を“セット”で持つと強いです🔥

1. **型（例外クラス）**：`instanceof` で捕まえたい🪤
2. **コード**：機械的に分岐・ログ集計しやすい🏷️
3. **メッセージ**：開発者が読んで原因が分かる文章📝
4. **原因（cause）と文脈（meta）**：デバッグが超ラクになる🧠🔍

`cause` は **ES2022のError機能**で、元エラーを繋げられます（ブラウザもNodeも広く対応）([MDN ウェブドキュメント][1])
（「ラップしても根っこの原因を辿れる」やつ！✨）

---

## 3. catchで事故らないコツ（unknownが基本）🧤⚠️

TypeScriptは「投げられるものは何でも投げられる」世界なので、`catch (e)` の `e` を **unknown扱い**にするのが安全です🧠
それを強制してくれるのが `useUnknownInCatchVariables` ✨([typescriptlang.org][2])

---

## 4. 実装：DomainErrorの“土台”を作ろう🏗️🧯

ここからコードいくよ〜！🧡
（例題：注文 `Order` が「状態に応じて操作できる/できない」を守る）

### 4-1. tsconfigのポイント（causeとunknown）⚙️🪄

`Error(message, { cause })` を型的に扱うには ES2022 以上がラクです（`Error()` が options を受け取る仕様）([MDN ウェブドキュメント][1])
あと `useUnknownInCatchVariables` もON推しです([typescriptlang.org][2])

```ts
// tsconfig.json（必要部分だけのイメージ）
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2022", "DOM"],
    "useUnknownInCatchVariables": true
  }
}
```

※ちなみに本日時点で npm の stable は **TypeScript 5.9.3** です([NPM][3])
（TypeScript 6.0 は 2026-02-10 に Beta、2026-03-17 に Final予定、という公式の作業計画が出てます）([GitHub][4])
さらに「6.0はJavaScript実装の最後のブリッジ版」ってMicrosoftが明言してます([Microsoft for Developers][5])

---

### 4-2. DomainError（基底クラス）🧯✨

* **code**：機械で扱う
* **message**：人（開発者）が読む
* **meta**：デバッグ用の材料（orderIdとかstatusとか）
* **cause**：元エラー（あれば）を繋ぐ

```ts
// domain/errors/DomainError.ts
export type DomainErrorCode =
  | "ORDER_STATUS_INVALID"
  | "ORDER_ALREADY_PAID"
  | "INVALID_QUANTITY";

export type DomainErrorMeta = Record<string, unknown>;

export class DomainError extends Error {
  readonly code: DomainErrorCode;
  readonly meta?: DomainErrorMeta;

  constructor(
    code: DomainErrorCode,
    message: string,
    options?: { cause?: unknown; meta?: DomainErrorMeta }
  ) {
    super(message, { cause: options?.cause }); // ES2022 Error options
    this.name = `DomainError(${code})`;
    this.code = code;
    this.meta = options?.meta;
  }
}
```

---

## 5. 例題：Orderで「仕様違反」を投げる☕🧾🚫

### 5-1. 状態とルールの例🚦

* `Draft`：明細追加OK、支払いNG
* `Confirmed`：支払いOK、明細追加NG
* `Paid`：二重支払いNG、キャンセルNG（例）

### 5-2. Orderの実装例（必要な部分だけ）🏯✨

```ts
// domain/order/Order.ts
import { DomainError } from "../errors/DomainError";

export type OrderStatus = "Draft" | "Confirmed" | "Paid";

export class Order {
  private status: OrderStatus = "Draft";
  private totalCents = 0;

  static createDraft() {
    return new Order();
  }

  addItem(priceCents: number, quantity: number) {
    if (quantity < 1) {
      throw new DomainError(
        "INVALID_QUANTITY",
        `quantity must be >= 1, got ${quantity}`,
        { meta: { quantity } }
      );
    }

    if (this.status !== "Draft") {
      throw new DomainError(
        "ORDER_STATUS_INVALID",
        `cannot addItem when status=${this.status}`,
        { meta: { status: this.status, allowed: ["Draft"] } }
      );
    }

    this.totalCents += priceCents * quantity;
  }

  confirm() {
    if (this.status !== "Draft") {
      throw new DomainError(
        "ORDER_STATUS_INVALID",
        `cannot confirm when status=${this.status}`,
        { meta: { status: this.status, allowed: ["Draft"] } }
      );
    }
    this.status = "Confirmed";
  }

  pay() {
    if (this.status === "Paid") {
      throw new DomainError(
        "ORDER_ALREADY_PAID",
        `order already paid`,
        { meta: { status: this.status } }
      );
    }
    if (this.status !== "Confirmed") {
      throw new DomainError(
        "ORDER_STATUS_INVALID",
        `cannot pay when status=${this.status}`,
        { meta: { status: this.status, allowed: ["Confirmed"] } }
      );
    }
    this.status = "Paid";
  }

  getStatus() {
    return this.status;
  }

  getTotalCents() {
    return this.totalCents;
  }
}
```

### 💡ポイント

* `throw new Error("だめ")` じゃなくて、**「仕様違反の種類」を型で表す**🧯
* `meta` に「status」「allowed」みたいな情報を入れると、ログ見た瞬間に分かる😎✨
* メッセージは「開発者が原因を特定できる文章」に寄せるのがコツ📝

---

## 6. アプリ層でのcatch：unknown → DomainErrorだけ扱う🧤🎬

`useUnknownInCatchVariables` をONにすると `catch (e)` の `e` は unknown になります([typescriptlang.org][2])
だから **型ガード（instanceof）**で丁寧に分けようね✨

```ts
// app/payOrder.ts
import { DomainError } from "../domain/errors/DomainError";
import { Order } from "../domain/order/Order";

type PayOrderResult =
  | { ok: true }
  | { ok: false; reason: "domain"; code: DomainError["code"] };

export function payOrderUseCase(order: Order): PayOrderResult {
  try {
    order.pay();
    return { ok: true };
  } catch (e) {
    if (e instanceof DomainError) {
      // 章88で Result型をもっと育てるよ🌱
      return { ok: false, reason: "domain", code: e.code };
    }
    // DomainError じゃない = 予期せぬ例外（バグ or インフラ）
    throw e;
  }
}
```

---

## 7. causeの使いどころ（エラーの“原因を保持”）🔗🧠

`cause` は「元のエラーを繋ぐ」ための標準機能です([MDN ウェブドキュメント][6])
Nodeでも `new Error(message, { cause })` で `error.cause` が使えるって明記されています([nodejs.org][7])

DDD的には、

* **ドメイン層**：基本は「仕様違反」をそのまま投げる（cause不要なこと多い）
* **アプリ/インフラ層**：外部I/Oを包むときに `cause` がめちゃ効く✨

例：リポジトリが落ちたのを「保存失敗」で包む（イメージ）

```ts
export class InfraError extends Error {
  constructor(message: string, options?: { cause?: unknown }) {
    super(message, { cause: options?.cause });
    this.name = "InfraError";
  }
}
```

---

## 8. テスト：例外は「仕様のテスト」になる🧪💎

例外が設計されてると、テストが超書きやすいです✨

```ts
// test/order.spec.ts
import { describe, it, expect } from "vitest";
import { Order } from "../domain/order/Order";
import { DomainError } from "../domain/errors/DomainError";

function captureError(fn: () => void): unknown {
  try {
    fn();
    return undefined;
  } catch (e) {
    return e;
  }
}

describe("Order domain errors", () => {
  it("Paidな注文にpayすると ORDER_ALREADY_PAID", () => {
    const order = Order.createDraft();
    order.addItem(500, 1);
    order.confirm();
    order.pay();

    const err = captureError(() => order.pay());
    expect(err).toBeInstanceOf(DomainError);
    if (err instanceof DomainError) {
      expect(err.code).toBe("ORDER_ALREADY_PAID");
    }
  });

  it("Draftのままpayすると ORDER_STATUS_INVALID", () => {
    const order = Order.createDraft();

    const err = captureError(() => order.pay());
    expect(err).toBeInstanceOf(DomainError);
    if (err instanceof DomainError) {
      expect(err.code).toBe("ORDER_STATUS_INVALID");
    }
  });

  it("quantity=0 は INVALID_QUANTITY", () => {
    const order = Order.createDraft();

    const err = captureError(() => order.addItem(500, 0));
    expect(err).toBeInstanceOf(DomainError);
    if (err instanceof DomainError) {
      expect(err.code).toBe("INVALID_QUANTITY");
      expect(err.meta?.quantity).toBe(0);
    }
  });
});
```

---

## 9. AI活用プロンプト例🤖💬（この章向け）

### ✅ 例外設計の候補を出してもらう

* 「Orderの操作（addItem/confirm/pay）ごとに、起こりうる仕様違反を列挙して。DomainErrorCode案も作って」

### ✅ 例外メッセージを“読める文章”に整える

* 「このDomainErrorのmessageを、開発者がログで見て原因が即わかる文章にリライトして。短く、情報（status/allowed/orderId）を含めて」

### ✅ metaに入れるべき情報を提案させる

* 「ORDER_STATUS_INVALID の meta に入れるべき項目を提案して（例：status, allowed, action など）。個人情報は入れないで」

---

## 10. ありがちな事故まとめ😂⚠️

* **文字列をthrowする**：`throw "error"` は地獄への片道切符🎢💀
* **全部 Error で済ませる**：何が起きたか分からない😵
* **ドメインにHTTPやDBの言葉が混ざる**：境界が崩れる🧱💥
* **messageにユーザー表示文言を混ぜる**：後で必ず揉める（次章以降で分離するよ）👤🛠️
* **metaに巨大オブジェクトを突っ込む**：ログが重い＆漏洩リスク💣

---

## 11. ミニ演習（やると身につく！）🎮✨

### 演習A：キャンセルを追加🧾🚫

ルール：

* `Paid` の注文は `cancel()` できない
* `Confirmed` までなら `cancel()` OK

やること：

1. `cancel()` を `Order` に追加
2. 例外コードを追加（例：`ORDER_CANNOT_CANCEL`）
3. テストを書く🧪

### 演習B：ORDER_STATUS_INVALID を“共通化”🧰

同じような例外が増えてきたら、

* `private ensureStatus(allowed, action)` みたいなガード関数を作って整理してみよう✨

---

## まとめ🎒✨

* ドメイン例外は「仕様違反」を表す🧯
* **型 + code + message + meta（+cause）** がそろうと一気に強い💪
* `catch` は unknown 前提で、`instanceof` で安全に扱う🧤
* 例外が整うと、テストもログもデバッグも全部ラクになる🎉

---

次の **第88章** は、この例外を「UIやAPIに返す形（Result型）」としてキレイに型設計していくよ📦✨

[1]: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Error/Error?utm_source=chatgpt.com "Error() constructor - JavaScript - MDN Web Docs"
[2]: https://www.typescriptlang.org/tsconfig/useUnknownInCatchVariables.html?utm_source=chatgpt.com "useUnknownInCatchVariables - TSConfig Option"
[3]: https://www.npmjs.com/package/typescript?activeTab=versions&utm_source=chatgpt.com "typescript"
[4]: https://github.com/microsoft/TypeScript/issues/63085?utm_source=chatgpt.com "TypeScript 6.0 Iteration Plan · Issue #63085"
[5]: https://devblogs.microsoft.com/typescript/progress-on-typescript-7-december-2025/?utm_source=chatgpt.com "Progress on TypeScript 7 - December 2025"
[6]: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Error/cause?utm_source=chatgpt.com "Error: cause - JavaScript - MDN Web Docs"
[7]: https://nodejs.org/api/errors.html?utm_source=chatgpt.com "Errors | Node.js v25.6.0 Documentation"
