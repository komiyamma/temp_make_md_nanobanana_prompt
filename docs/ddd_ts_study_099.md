# 第99章：統合演習：注文→支払い→レシート（イベント連携）🎉

![統合演習：最終フロー](./picture/ddd_ts_study_099_integration_map.png)

この章では、**「支払いが完了したらレシートを発行する」**流れを、**ドメインイベントで“ゆるく”つなぐ**ところまで一気に完成させるよ〜！🥳✨
（やることはガッツリだけど、順番どおりにやればちゃんと動くよ💪🧁）

---

## 0) 本日の“最新メモ”🗓️🔎

* **TypeScript の最新安定版（npm の latest）**は **5.9.3**（2025-09-30公開）だよ。([npm][1])
* **TypeScript 6.0**は、**2026-02-10にBeta、2026-03-17にFinal**の予定が公開されてるよ（計画）。([GitHub][2])
* **Node.js は v24 が Active LTS（推奨）**、v25 は Current（新しめ枠）だよ。([Node.js][3])
* テストは **Vitest 4.0 が2025-10-22に発表**、GitHub上では **4.1系のbeta**も動いてる。([Vitest][4])

> この教材のコードは **TypeScript 5.9.x + Node 24系**あたりで気持ちよく回る想定で書くね🧡

---

## 1) 今日つくる完成形（ゴール）🎯✨

### ✅ ユースケースの流れ

1. **PayOrder（支払い）**が成功する 💳✅
2. **Order 集約が PaymentCompleted イベントを発行**する 📣
3. アプリ層がイベントを **EventBus に publish** する 🚌
4. **購読ハンドラ**が受け取って **Receipt を発行**する 🧾✨
5. ついでに **ReceiptIssued を発行**してもOK（拡張しやすくなる）📮

### 🔥 ここがDDDっぽいポイント

* **Order は Receipt を知らない**（疎結合！）🧩
* 「支払い完了」という事実が **イベントとして残る** 📣
* 「レシート発行」は **別の責務**として外に出せる 🧾➡️🏭

---

## 2) よくある事故（先に回避）⚠️😂

* ❌ **Order の中で Receipt を作り始める** → 密結合＆巨大集約化しがち
* ❌ イベントに **Order の中身全部**を詰める → 肥大化（第93章の罠📦💥）
* ❌ **保存前に publish**して、失敗したのにイベントだけ飛ぶ → 整合性が崩れる
* ❌ 受け取り側が **二重実行**されてレシート二重発行 → 事故りがち（冪等性の入口🔁）

この章では、**「保存→イベント配信」**の順にして、さらに**簡易冪等**も入れるよ🛡️✨

---

## 3) ミニ構成（ファイルの置き場）📦🧠

ざっくりこんな感じ（必要な分だけ）：

* `src/domain/**` … ルールとモデル（Order / Receipt / DomainEvent）
* `src/app/**` … ユースケースとイベント配信、購読ハンドラ
* `src/infra/**` … InMemoryリポジトリ、EventBus実装、PaymentGatewayのダミー
* `test/**` … 統合テスト

---

## 4) 実装ステップ①：DomainEvent と AggregateRoot 📣🏯

### ✅ DomainEvent（最小の共通形）

```ts
// src/domain/shared/DomainEvent.ts
export type DomainEvent = Readonly<{
  eventId: string;
  type: string;
  occurredAt: Date;
}>;
```

### ✅ AggregateRoot（イベントをためて、後でまとめて渡す）

```ts
// src/domain/shared/AggregateRoot.ts
import { DomainEvent } from "./DomainEvent";

export abstract class AggregateRoot {
  private _domainEvents: DomainEvent[] = [];

  protected addDomainEvent(event: DomainEvent) {
    this._domainEvents.push(event);
  }

  /** イベントを取り出して、内部は空にする（重要✨） */
  pullDomainEvents(): DomainEvent[] {
    const events = this._domainEvents;
    this._domainEvents = [];
    return events;
  }
}
```

---

## 5) 実装ステップ②：Order が PaymentCompleted を出す 💳➡️📣

今回は“最小の注文”でいくね（合計金額と状態だけ）☕🧾

```ts
// src/domain/order/Order.ts
import { AggregateRoot } from "../shared/AggregateRoot";
import { DomainEvent } from "../shared/DomainEvent";

export type OrderStatus = "CONFIRMED" | "PAID";

export class Order extends AggregateRoot {
  private constructor(
    public readonly id: string,
    private status: OrderStatus,
    private totalYen: number
  ) {
    super();
  }

  static confirmed(id: string, totalYen: number) {
    if (totalYen <= 0) throw new Error("合計金額は1円以上だよ💰");
    return new Order(id, "CONFIRMED", totalYen);
  }

  getStatus() {
    return this.status;
  }

  getTotalYen() {
    return this.totalYen;
  }

  /** 支払い成功後に呼ばれる（外部連携はアプリ層の責務✨） */
  completePayment(args: { paymentId: string; paidAt: Date; eventId: string }) {
    if (this.status !== "CONFIRMED") {
      throw new Error("支払いできるのはCONFIRMEDだけだよ🚫");
    }

    this.status = "PAID";

    const event: DomainEvent & {
      type: "PaymentCompleted";
      orderId: string;
      paymentId: string;
      totalYen: number;
    } = {
      eventId: args.eventId,
      type: "PaymentCompleted",
      occurredAt: args.paidAt,
      orderId: this.id,
      paymentId: args.paymentId,
      totalYen: this.totalYen,
    };

    this.addDomainEvent(event);
  }
}
```

> ✅ イベントの情報は **最小（ID＋時刻＋重要値）**にしてるよ📦✨
> 「明細ぜんぶ欲しい！」ってなったら、購読側が必要に応じて取りに行けばOK🙆‍♀️

---

## 6) 実装ステップ③：Receipt（発行物）🧾✨

```ts
// src/domain/receipt/Receipt.ts
export class Receipt {
  private constructor(
    public readonly id: string,
    public readonly orderId: string,
    public readonly issuedAt: Date,
    public readonly totalYen: number
  ) {}

  static issue(args: { id: string; orderId: string; issuedAt: Date; totalYen: number }) {
    if (args.totalYen <= 0) throw new Error("レシート金額が変だよ😵");
    return new Receipt(args.id, args.orderId, args.issuedAt, args.totalYen);
  }
}
```

---

## 7) 実装ステップ④：Repository（ポート）📚🔌

```ts
// src/domain/order/OrderRepository.ts
import { Order } from "./Order";

export interface OrderRepository {
  findById(id: string): Promise<Order | null>;
  save(order: Order): Promise<void>;
}
```

```ts
// src/domain/receipt/ReceiptRepository.ts
import { Receipt } from "./Receipt";

export interface ReceiptRepository {
  findByOrderId(orderId: string): Promise<Receipt | null>;
  save(receipt: Receipt): Promise<void>;
}
```

---

## 8) 実装ステップ⑤：EventBus（アプリ層の道具）🚌🔔

### ✅ EventBusインターフェース

```ts
// src/app/event/EventBus.ts
import { DomainEvent } from "../../domain/shared/DomainEvent";

export type EventHandler = (event: DomainEvent) => Promise<void> | void;

export interface EventBus {
  subscribe(eventType: string, handler: EventHandler): void;
  publish(events: DomainEvent[]): Promise<void>;
}
```

### ✅ 同期 InMemory 実装（この章は“動く体験”優先✨）

```ts
// src/infra/event/InMemoryEventBus.ts
import { EventBus, EventHandler } from "../../app/event/EventBus";
import { DomainEvent } from "../../domain/shared/DomainEvent";

export class InMemoryEventBus implements EventBus {
  private handlers = new Map<string, EventHandler[]>();

  subscribe(eventType: string, handler: EventHandler): void {
    const list = this.handlers.get(eventType) ?? [];
    list.push(handler);
    this.handlers.set(eventType, list);
  }

  async publish(events: DomainEvent[]): Promise<void> {
    for (const event of events) {
      const list = this.handlers.get(event.type) ?? [];
      for (const handler of list) {
        await handler(event);
      }
    }
  }
}
```

---

## 9) 実装ステップ⑥：PayOrder（支払いユースケース）💳🎬

「外部決済→成功→Order更新→保存→イベント配信」って順番にするよ✨
（保存前にイベント飛ばすと、失敗した時に事故るからね…😇）

```ts
// src/app/payment/PaymentGateway.ts
export interface PaymentGateway {
  charge(args: { orderId: string; amountYen: number; idempotencyKey: string }): Promise<{ paymentId: string }>;
}
```

```ts
// src/infra/payment/FakePaymentGateway.ts
import { PaymentGateway } from "../../app/payment/PaymentGateway";

export class FakePaymentGateway implements PaymentGateway {
  async charge(args: { orderId: string; amountYen: number; idempotencyKey: string }) {
    // いつでも成功するダミー💖
    return { paymentId: `pay_${args.idempotencyKey}` };
  }
}
```

```ts
// src/app/usecases/PayOrder.ts
import { randomUUID } from "node:crypto";
import { OrderRepository } from "../../domain/order/OrderRepository";
import { EventBus } from "../event/EventBus";
import { PaymentGateway } from "../payment/PaymentGateway";

export class PayOrder {
  constructor(
    private readonly orderRepo: OrderRepository,
    private readonly paymentGateway: PaymentGateway,
    private readonly eventBus: EventBus
  ) {}

  async execute(input: { orderId: string }) {
    const order = await this.orderRepo.findById(input.orderId);
    if (!order) throw new Error("注文が見つからないよ🫥");

    // 外部決済（成功した想定）
    const idempotencyKey = `${order.id}`; // 超簡易（本当は支払い試行単位などで設計）
    const charged = await this.paymentGateway.charge({
      orderId: order.id,
      amountYen: order.getTotalYen(),
      idempotencyKey,
    });

    // ドメイン更新（イベント発行）
    const now = new Date();
    order.completePayment({
      paymentId: charged.paymentId,
      paidAt: now,
      eventId: randomUUID(),
    });

    // 保存してからイベント配信✨
    await this.orderRepo.save(order);
    await this.eventBus.publish(order.pullDomainEvents());
  }
}
```

---

## 10) 実装ステップ⑦：購読ハンドラ「支払い完了→レシート発行」🧾🔔

ここで **ReceiptRepository** を使って保存するよ✨
さらに **簡易冪等**：すでに同じ注文のレシートがあったら何もしない🔁🛡️

```ts
// src/app/handlers/IssueReceiptOnPaymentCompleted.ts
import { randomUUID } from "node:crypto";
import { DomainEvent } from "../../domain/shared/DomainEvent";
import { OrderRepository } from "../../domain/order/OrderRepository";
import { ReceiptRepository } from "../../domain/receipt/ReceiptRepository";
import { Receipt } from "../../domain/receipt/Receipt";
import { EventBus } from "../event/EventBus";

export class IssueReceiptOnPaymentCompleted {
  constructor(
    private readonly orderRepo: OrderRepository,
    private readonly receiptRepo: ReceiptRepository,
    private readonly eventBus: EventBus
  ) {}

  /** EventBusから呼ばれる想定 */
  async handle(event: DomainEvent) {
    if (event.type !== "PaymentCompleted") return;

    const orderId = (event as any).orderId as string;

    // ✅ 簡易冪等：二重発行を防ぐ
    const existing = await this.receiptRepo.findByOrderId(orderId);
    if (existing) return;

    const order = await this.orderRepo.findById(orderId);
    if (!order) throw new Error("レシート発行中に注文が見つからないよ😵");

    const receipt = Receipt.issue({
      id: randomUUID(),
      orderId: order.id,
      issuedAt: new Date(),
      totalYen: order.getTotalYen(),
    });

    await this.receiptRepo.save(receipt);

    // （拡張）ReceiptIssued を出すと、あとで通知とか繋げやすい📮✨
    await this.eventBus.publish([
      {
        eventId: randomUUID(),
        type: "ReceiptIssued",
        occurredAt: new Date(),
        // 最小でOK（必要なら購読側が取りに行く）
        ...( { receiptId: receipt.id, orderId: receipt.orderId } as any ),
      },
    ]);
  }
}
```

> 💡 `as any` を減らして型をキレイにしたくなるはず！それ、めちゃ良い感覚😚✨
> この章は「流れを通す」が優先だから、次章以降でイベント型の整理を強化していこ〜💪📘

---

## 11) 実装ステップ⑧：InMemory Repository（動かすための土台）🧪📦

```ts
// src/infra/repo/InMemoryOrderRepository.ts
import { OrderRepository } from "../../domain/order/OrderRepository";
import { Order } from "../../domain/order/Order";

export class InMemoryOrderRepository implements OrderRepository {
  private store = new Map<string, Order>();

  async findById(id: string): Promise<Order | null> {
    return this.store.get(id) ?? null;
  }

  async save(order: Order): Promise<void> {
    this.store.set(order.id, order);
  }
}
```

```ts
// src/infra/repo/InMemoryReceiptRepository.ts
import { ReceiptRepository } from "../../domain/receipt/ReceiptRepository";
import { Receipt } from "../../domain/receipt/Receipt";

export class InMemoryReceiptRepository implements ReceiptRepository {
  private storeByOrderId = new Map<string, Receipt>();

  async findByOrderId(orderId: string): Promise<Receipt | null> {
    return this.storeByOrderId.get(orderId) ?? null;
  }

  async save(receipt: Receipt): Promise<void> {
    this.storeByOrderId.set(receipt.orderId, receipt);
  }
}
```

---

## 12) 統合テスト（この章のメイン！）🧪🎉

「PayOrderしたら Receipt ができる」を確認するよ✨
Vitestのメジャー4系が出てるよ〜ってのも押さえつつね🧡([Vitest][4])

```ts
// test/payment-to-receipt.integration.test.ts
import { describe, it, expect } from "vitest";
import { InMemoryEventBus } from "../src/infra/event/InMemoryEventBus";
import { InMemoryOrderRepository } from "../src/infra/repo/InMemoryOrderRepository";
import { InMemoryReceiptRepository } from "../src/infra/repo/InMemoryReceiptRepository";
import { FakePaymentGateway } from "../src/infra/payment/FakePaymentGateway";
import { Order } from "../src/domain/order/Order";
import { PayOrder } from "../src/app/usecases/PayOrder";
import { IssueReceiptOnPaymentCompleted } from "../src/app/handlers/IssueReceiptOnPaymentCompleted";

describe("支払い→レシート発行（イベント連携）", () => {
  it("PayOrder を実行すると Receipt が作られる🧾✨", async () => {
    const eventBus = new InMemoryEventBus();
    const orderRepo = new InMemoryOrderRepository();
    const receiptRepo = new InMemoryReceiptRepository();
    const paymentGateway = new FakePaymentGateway();

    // ハンドラ購読
    const handler = new IssueReceiptOnPaymentCompleted(orderRepo, receiptRepo, eventBus);
    eventBus.subscribe("PaymentCompleted", (e) => handler.handle(e));

    // 事前に注文を用意（CONFIRMED）
    const order = Order.confirmed("order_1", 1200);
    await orderRepo.save(order);

    // 実行！
    const payOrder = new PayOrder(orderRepo, paymentGateway, eventBus);
    await payOrder.execute({ orderId: "order_1" });

    const receipt = await receiptRepo.findByOrderId("order_1");
    expect(receipt).not.toBeNull();
    expect(receipt!.totalYen).toBe(1200);
  });

  it("二重実行してもレシートは二重発行されない🔁🛡️", async () => {
    const eventBus = new InMemoryEventBus();
    const orderRepo = new InMemoryOrderRepository();
    const receiptRepo = new InMemoryReceiptRepository();
    const paymentGateway = new FakePaymentGateway();

    const handler = new IssueReceiptOnPaymentCompleted(orderRepo, receiptRepo, eventBus);
    eventBus.subscribe("PaymentCompleted", (e) => handler.handle(e));

    const order = Order.confirmed("order_2", 800);
    await orderRepo.save(order);

    const payOrder = new PayOrder(orderRepo, paymentGateway, eventBus);

    await payOrder.execute({ orderId: "order_2" });
    // 2回目は Order 側が「PAIDなので支払い不可」になる想定（=ドメインが守る💪）
    await expect(payOrder.execute({ orderId: "order_2" })).rejects.toThrow();

    const receipt = await receiptRepo.findByOrderId("order_2");
    expect(receipt).not.toBeNull();
  });
});
```

---

## 13) デモ用シナリオ（人に見せるやつ）🎥✨

AIに「デモ台本」を作らせると超ラクだよ🤖📜
たとえばこんな流れ：

1. 注文作成（CONFIRMED）☕
2. 支払い実行 💳
3. Receipt が保存されてることを表示 🧾✅
4. （拡張）ReceiptIssued を購読して「通知」ログを出す 🔔

---

## 14) AIに投げる“おいしい指示”テンプレ🍰🤖

### ✅ 設計レビュー（イベントが太ってない？）

* 「PaymentCompletedイベントのpayloadが最小かチェックして。入れすぎなら削る案も出して」

### ✅ テスト観点を増やす

* 「支払い成功→レシート発行の統合テストで、落とし穴のケースを追加して（例：注文が存在しない、ハンドラで例外、二重配信）」

### ✅ リファクタ提案（次章への布石）

* 「DomainEventをunionで型安全にして、EventBusのsubscribeで型が効く形を提案して」

---

## 15) この章の“合格チェック”✅🎓

できたらクリア！🎉

* [ ] Order は **PaymentCompleted を発行**している📣
* [ ] アプリ層が **保存→publish** の順で動いてる🧠✨
* [ ] Receipt 発行が **購読側に分離**できてる🧾➡️
* [ ] 統合テストで「支払い→レシート」が通る🧪✅
* [ ] “二重発行”の最低限のガードがある🔁🛡️

---

## 16) 次（第100章）へつながる一言🚀✨

この章でついに、**イベントが「実際に役立つ」体験**になったはず！🥳
次は「DDDっぽいだけ」を卒業するために、**境界・依存・不変条件・テスト・イベント**を“最終点検”して完成だよ〜🎓🌸

---

必要なら、この第99章の内容を **そのまま動く最小リポジトリ構成（package.json / tsconfig / npm scripts）**まで一式で書き下ろして、コピペで起動できる形にもしてあげるね🧁💻✨

[1]: https://www.npmjs.com/package/typescript?utm_source=chatgpt.com "typescript"
[2]: https://github.com/microsoft/TypeScript/issues/63085?utm_source=chatgpt.com "TypeScript 6.0 Iteration Plan · Issue #63085"
[3]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
[4]: https://vitest.dev/blog/vitest-4?utm_source=chatgpt.com "Vitest 4.0 is out!"
