# 第11章：SRP実戦（サービス分割してみよう）⚔️🔥

今回はついに **「でっかいOrderServiceをバラして、読みやすく・テストしやすく」**していくよ〜！🥳✨
SRP（単一責任）って、理解するより **手を動かした瞬間に“気持ちよさ”が分かる**タイプなんだよね🧸💕


![SRP Violation Office](./picture/solid_ts_study_011_srp_violation_office.png)

---

## この章でできるようになること🎯✨

* 「このクラス、なんで変更されるの？」を言語化できる🗣️💡
* でっかいサービスを **計算 / 保存 / 出力** みたいに分割できる✂️🧩
* 分割した結果、**テストがスルッと書ける**のを体験できる✅🧫
* 「分けすぎ地獄」も避けられるようになる⚠️😇

---

## まずSRPを“実戦用”に言い換えるね💬🌸

SRPはこれだけ覚えてればOK！👇✨

> **「変更される理由（Change Reason）」が1つだけになるようにする**🧠🔧

逆に、こういう“変更理由が複数”になってるとSRP違反になりやすいよ〜😵💥

* 料金ルールが変わったら直す必要がある💰
* DB保存方法が変わったら直す必要がある🗄️
* レシートの見た目が変わったら直す必要がある🧾

↑これ全部を1クラスが抱えると、未来で泣く😭💦

![Change Reason Examples](./picture/solid_ts_study_011_change_reason_examples.png)

---

## 今日の題材：まずは“わざと最悪”からスタート😈🧪

「Campus Café 注文アプリ」☕️🍰の注文処理で、ありがちな **God Service（全部入り）** を用意するよ！

### 🍱 悪い例：なんでも屋の `OrderService`（SRP違反）

![God Service Burden](./picture/solid_ts_study_011_god_service_burden.png)

```ts
// src/order/OrderService.ts
type OrderItem = { sku: string; name: string; price: number; qty: number };
type Coupon = { code: string; type: "PERCENT" | "FLAT"; value: number };

type Order = {
  id: string;
  items: OrderItem[];
  coupon?: Coupon;
  createdAt: Date;
};

export class OrderService {
  private orders: Order[] = []; // なんと保存までここで…😇

  placeOrder(items: OrderItem[], coupon?: Coupon): { orderId: string; total: number } {
    // ① 料金計算（ビジネスルール）💰
    const subtotal = items.reduce((sum, i) => sum + i.price * i.qty, 0);

    let discount = 0;
    if (coupon) {
      if (coupon.type === "PERCENT") discount = Math.floor(subtotal * (coupon.value / 100));
      if (coupon.type === "FLAT") discount = coupon.value;
    }

    const total = Math.max(0, subtotal - discount);

    // ② 注文作成（ドメイン/状態）📦
    const order: Order = {
      id: crypto.randomUUID(),
      items,
      coupon,
      createdAt: new Date(),
    };

    // ③ 保存（永続化）🗄️
    this.orders.push(order);

    // ④ レシート出力（表示/フォーマット/副作用）🧾🖨️
    const lines: string[] = [];
    lines.push("=== Campus Café Receipt ===");
    lines.push(`OrderId: ${order.id}`);
    lines.push(`Date: ${order.createdAt.toISOString()}`);
    lines.push("--- items ---");
    for (const item of items) {
      lines.push(`${item.name} x${item.qty} = ${item.price * item.qty}`);
    }
    lines.push(`Subtotal: ${subtotal}`);
    if (coupon) lines.push(`Coupon(${coupon.code}): -${discount}`);
    lines.push(`Total: ${total}`);
    lines.push("===========================");

    console.log(lines.join("\n"));

    return { orderId: order.id, total };
  }
}
```

うん、最高に“あるある”だね😂🧨
この `OrderService` は **変更理由が4つ** あるから、何か直すたびに事故りやすい💥

---

## 分割方針：責務を“3つの箱”に入れていくよ📦📦📦

![3 Layers](./picture/solid_ts_study_011_layer_boxes.png)

まずは雑にこれでOK！✨（細かい美学は後で育てよう🌱）

| 箱             | 役割            | 変更理由の例          |
| ------------- | ------------- | --------------- |
| 🧠 計算（純粋ロジック） | 金額・割引・合計      | 割引ルール追加、丸め変更    |
| 🗄️ 保存（I/O）   | どこにどう保存するか    | DB導入、API保存、形式変更 |
| 🧾 出力（見た目）    | レシート文面/フォーマット | 表示変更、桁区切り、言語対応  |

この分け方、**テストしやすさが爆上がり**するよ🔥✅

---

## Step 1：料金計算を `PriceCalculator` に切り出す💰✂️

![Extracting Logic](./picture/solid_ts_study_011_extract_logic.png)

SRP分割の最初の一手はだいたいこれ！

> **副作用がない純粋ロジック（計算）を外へ出す**🧼✨

```ts
// src/pricing/PriceCalculator.ts
export type OrderItem = { sku: string; name: string; price: number; qty: number };
export type Coupon = { code: string; type: "PERCENT" | "FLAT"; value: number };

export type PriceBreakdown = {
  subtotal: number;
  discount: number;
  total: number;
};

export class PriceCalculator {
  calc(items: OrderItem[], coupon?: Coupon): PriceBreakdown {
    const subtotal = items.reduce((sum, i) => sum + i.price * i.qty, 0);

    const discount = coupon ? this.calcDiscount(subtotal, coupon) : 0;
    const total = Math.max(0, subtotal - discount);

    return { subtotal, discount, total };
  }

  private calcDiscount(subtotal: number, coupon: Coupon): number {
    if (coupon.type === "PERCENT") return Math.floor(subtotal * (coupon.value / 100));
    if (coupon.type === "FLAT") return coupon.value;
    // 将来typeが増えた時に気づけるように…😉
    return 0;
  }
}
```

これで「割引ルールを変えたい」って時、**PriceCalculatorだけを触ればいい**状態に近づいたよ〜！🥳✨

---

## Step 2：保存を `OrderRepository` に分離する🗄️✂️

![Repository Isolation](./picture/solid_ts_study_011_repository_isolation.png)

次は「保存先が変わる」って理由を外へ逃がすよ！

```ts
// src/order/Order.ts
import type { OrderItem, Coupon } from "../pricing/PriceCalculator.js";

export type Order = {
  id: string;
  items: OrderItem[];
  coupon?: Coupon;
  createdAt: Date;
};
```

```ts
// src/order/OrderRepository.ts
import type { Order } from "./Order.js";

export interface OrderRepository {
  save(order: Order): Promise<void>;
}
```

まずは簡単にメモリ保存でOK！（DBは後でやる✨）

```ts
// src/order/InMemoryOrderRepository.ts
import type { Order } from "./Order.js";
import type { OrderRepository } from "./OrderRepository.js";

export class InMemoryOrderRepository implements OrderRepository {
  private readonly orders: Order[] = [];

  async save(order: Order): Promise<void> {
    this.orders.push(order);
  }

  // テスト用に覗けるようにしてもOK（本番では隠すこと多いよ）😉
  getAll(): readonly Order[] {
    return this.orders;
  }
}
```

---

## Step 3：レシート出力を `ReceiptBuilder` に分離する🧾✂️

![Receipt Builder](./picture/solid_ts_study_011_receipt_builder.png)

レシートは「見た目」が変わりやすいから、ここも別箱へ📦✨
ポイントは **“文字列を作るだけ”** にして、副作用（console.log）と分けるとさらに強いよ💪

```ts
// src/receipt/ReceiptBuilder.ts
import type { Order } from "../order/Order.js";
import type { PriceBreakdown } from "../pricing/PriceCalculator.js";

export class ReceiptBuilder {
  build(order: Order, price: PriceBreakdown): string {
    const lines: string[] = [];
    lines.push("=== Campus Café Receipt ===");
    lines.push(`OrderId: ${order.id}`);
    lines.push(`Date: ${order.createdAt.toISOString()}`);
    lines.push("--- items ---");

    for (const item of order.items) {
      lines.push(`${item.name} x${item.qty} = ${item.price * item.qty}`);
    }

    lines.push(`Subtotal: ${price.subtotal}`);
    if (order.coupon) lines.push(`Coupon(${order.coupon.code}): -${price.discount}`);
    lines.push(`Total: ${price.total}`);
    lines.push("===========================");

    return lines.join("\n");
  }
}
```

そして「出力する役」を小さく作る🖨️✨

```ts
// src/receipt/ReceiptPrinter.ts
export interface ReceiptPrinter {
  print(text: string): void;
}
```

```ts
// src/receipt/ConsoleReceiptPrinter.ts
import type { ReceiptPrinter } from "./ReceiptPrinter.js";

export class ConsoleReceiptPrinter implements ReceiptPrinter {
  print(text: string): void {
    console.log(text);
  }
}
```

---

## Step 4：薄くなった `OrderService`（司令塔だけやる）🧠✨

![Thin Coordinator](./picture/solid_ts_study_011_thin_coordinator.png)

最後に `OrderService` を「注文フローの組み立て役」だけにするよ！

```ts
// src/order/OrderService.ts
import { PriceCalculator, type OrderItem, type Coupon } from "../pricing/PriceCalculator.js";
import type { Order } from "./Order.js";
import type { OrderRepository } from "./OrderRepository.js";
import { ReceiptBuilder } from "../receipt/ReceiptBuilder.js";
import type { ReceiptPrinter } from "../receipt/ReceiptPrinter.js";

export class OrderService {
  constructor(
    private readonly priceCalculator: PriceCalculator,
    private readonly orderRepo: OrderRepository,
    private readonly receiptBuilder: ReceiptBuilder,
    private readonly receiptPrinter: ReceiptPrinter,
  ) {}

  async placeOrder(items: OrderItem[], coupon?: Coupon): Promise<{ orderId: string; total: number }> {
    const order: Order = {
      id: crypto.randomUUID(),
      items,
      coupon,
      createdAt: new Date(),
    };

    const price = this.priceCalculator.calc(items, coupon);

    await this.orderRepo.save(order);

    const receipt = this.receiptBuilder.build(order, price);
    this.receiptPrinter.print(receipt);

    return { orderId: order.id, total: price.total };
  }
}
```

どう？✨
**OrderServiceがめちゃ薄くなって、読んだ瞬間に流れが分かる**ようになったよね🥹💕

---

## ここで“SRPの勝利”が起きる🏆✨（テストが楽！）

![Testability Win](./picture/solid_ts_study_011_testability_win.png)

### ✅ 料金計算は、単体テストが超簡単💰

（Vitestは4系が継続的にリリースされてるよ〜） ([GitHub][1])

```ts
// test/PriceCalculator.test.ts
import { describe, it, expect } from "vitest";
import { PriceCalculator } from "../src/pricing/PriceCalculator.js";

describe("PriceCalculator", () => {
  it("クーポンなしの合計が出せる", () => {
    const calc = new PriceCalculator();
    const price = calc.calc([
      { sku: "A", name: "Coffee", price: 300, qty: 2 },
      { sku: "B", name: "Cake", price: 450, qty: 1 },
    ]);

    expect(price.subtotal).toBe(1050);
    expect(price.discount).toBe(0);
    expect(price.total).toBe(1050);
  });

  it("PERCENTクーポンが効く", () => {
    const calc = new PriceCalculator();
    const price = calc.calc(
      [{ sku: "A", name: "Coffee", price: 300, qty: 2 }],
      { code: "STUDENT10", type: "PERCENT", value: 10 },
    );

    expect(price.subtotal).toBe(600);
    expect(price.discount).toBe(60);
    expect(price.total).toBe(540);
  });
});
```

### ✅ OrderServiceは「差し替え」でテストできる🎭✨

```ts
// test/OrderService.test.ts
import { describe, it, expect, vi } from "vitest";
import { OrderService } from "../src/order/OrderService.js";
import { PriceCalculator } from "../src/pricing/PriceCalculator.js";
import { ReceiptBuilder } from "../src/receipt/ReceiptBuilder.js";
import type { OrderRepository } from "../src/order/OrderRepository.js";
import type { ReceiptPrinter } from "../src/receipt/ReceiptPrinter.js";

describe("OrderService", () => {
  it("注文すると保存されてレシートが印刷される", async () => {
    const repo: OrderRepository = { save: vi.fn(async () => {}) };
    const printer: ReceiptPrinter = { print: vi.fn() };

    const service = new OrderService(
      new PriceCalculator(),
      repo,
      new ReceiptBuilder(),
      printer,
    );

    const result = await service.placeOrder([{ sku: "A", name: "Coffee", price: 300, qty: 1 }]);

    expect(result.total).toBe(300);
    expect(repo.save).toHaveBeenCalledTimes(1);
    expect(printer.print).toHaveBeenCalledTimes(1);
  });
});
```

**SRPで分けた瞬間、テストが「書ける形」になる**んだよね…！🥹🫶

---

## AI（Copilot/Codex系）を使うなら、この聞き方が強いよ🤖✨

### 💬 分割案を出させるプロンプト例

* 「このクラスの“変更理由”を列挙して、SRPで分割案を3パターン出して」🧠
* 「副作用（I/O）と純粋ロジック（計算）を分けて、テスト例も作って」🧪
* 「分割後に依存関係が増えすぎないように注意点も添えて」⚠️

### ✅ AIの提案を採用する前のチェックリスト🔍

* その分割は「変更理由」が1つに寄ってる？🎯
* `OrderService` が“司令塔”のまま薄い？🧠
* 計算ロジックが副作用から隔離されてる？🧼
* クラス増やしすぎて、逆に読みにくくしてない？😇

---

## よくある失敗あるある（先に潰す）🧯💥

### ❶ 1メソッド1クラス病📛

小さくしすぎて「え、どこ見ればいいの…」になるやつ😂
➡️ **“変更理由”が同じなら同居でOK**だよ〜！

### ❷ 名前がフワッとして責務が混ざる🌫️

`Manager` / `Helper` / `Util` とかが増えると危険🚨
➡️ **名詞＋役割**（Calculator / Builder / Repository）が安定✨

### ❸ 司令塔がまた太る🍖

分割しても `OrderService` にロジックが戻ってくるやつ😭
➡️ **司令塔は「順番」と「つなぐ」だけ！**🔁

---

## まとめ🧸✨

* SRPは **「変更理由を1つにする」** がコア🧠
* 実戦ではまず **計算（純粋）/ 保存（I/O）/ 出力（見た目）** に分けると成功しやすい📦✨
* 分けた瞬間、テストがスルスル書けて気持ちいい✅🫶

---

## ちょい最新トピック豆知識🍬✨（2026年1月時点）

* TypeScriptは **5.9系が最新ライン**として案内されてるよ（npmでは5.9.3）。 ([TypeScript][2])
* 5.9では `import defer` などの新機能も入ってるよ（大規模コードの副作用コントロールに関係するやつ）。 ([TypeScript][3])
* ESLint周り（typescript-eslint）は継続的に更新されてて、直近もリリースされてるよ。 ([GitHub][4])

---

次の第12章（OCP）では、今日作った分割を土台にして **「割引が増えても地獄にならない設計」**に進化させるよ〜🎟️🔥

[1]: https://github.com/vitest-dev/vitest/releases "Releases · vitest-dev/vitest · GitHub"
[2]: https://www.typescriptlang.org/download/ "TypeScript: How to set up TypeScript"
[3]: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-9.html "TypeScript: Documentation - TypeScript 5.9"
[4]: https://github.com/typescript-eslint/typescript-eslint/releases?utm_source=chatgpt.com "Releases · typescript-eslint/typescript-eslint"
