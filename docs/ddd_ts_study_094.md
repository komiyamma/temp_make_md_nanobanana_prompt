# 第94章：同期処理でのイベント購読（まずは簡単に）🔔

![同期処理でのイベント購読](./picture/ddd_ts_study_094_sync_subscription.png)

この章はね、**「Domain Event 出したあと、別の処理を“くっつけずに”動かす」**を、いちばんカンタンな形（同期・同一プロセス）で体験する回だよ〜！🧁💕

---

## 2026/02/07 時点の“最新メモ”🗞️🧠

（教材の前提じゃなくて、今の流れを把握するためのメモね！）

* TypeScript の安定版は **5.9.3**（npm の “Latest”）だよ。([npm][1])
* TypeScript チームは **「6.0が最後の“JS実装のメジャー”」**って明言してて、7系はネイティブ移行（高速化）を進めてるよ。([Microsoft for Developers][2])
* そして TypeScript 6.0 は **Beta が 2026-02-10、Final が 2026-03-17** 予定として、公式Issueにスケジュールが出てる。([GitHub][3])
* Node.js は **v25 が Current（2026-02-02更新）**、**v24 が Active LTS（2026-01-12更新）** になってる。([nodejs.org][4])
* テストは **Vitest 4.0** がリリース済みで、いまどきのTS開発でよく使われてるよ。([Vitest][5])
* Jest は **30.0 が Stable** として案内されてるよ。([jestjs.io][6])

---

## この章のゴール🎯💖

### ✅ できるようになること

* 集約が発行した Domain Event を **アプリ層で集めて**
* **イベント購読者（subscriber/handler）に同期で配る**
* その結果として **「レシート作成」みたいな副作用**を、疎結合のまま実行できる✨

---

## まず超大事な考え方（ここだけ覚えれば勝ち）🏆🔑

### 1) Domain Event は「起きた事実」📣

* 例：`PaymentCompleted`（支払いが完了した）
* “お願い”じゃないよ！「やって」じゃなくて「起きた」💡

### 2) 購読側（Subscriber）は「後始末 / 連携 / 派生処理」🧹📮

* 例：レシート作る、通知する、ポイント付与する、監査ログ残す…など

### 3) 同期購読は “まず動く” の最短ルート🚀

* メリット：理解しやすい、デバッグしやすい、構成が小さい
* デメリット：重い処理を入れると遅くなる、失敗時の扱いが難しくなる（→次章の非同期へ布石）⏳💦

---

## 今日のミニ題材☕🧾

![Sync Chain](./picture/ddd_ts_study_094_sync_chain.png)

**「支払い完了 → レシート発行」**をイベントでつなぐよ🔗✨

* 集約（Order）が `PaymentCompleted` を発行
* 購読者 `CreateReceiptOnPaymentCompleted` がそれを受けて Receipt を作る

---

## 全体の形（最小構成）🧩✨

* **domain/**

  * `Order`（集約）
  * `PaymentCompleted`（Domain Event）
* **app/**

  * `EventBus`（イベント配信）
  * `CreateReceiptOnPaymentCompleted`（購読者）
  * `PayOrderService`（ユースケース）
* **infra/**

  * InMemory の Repository（ここでは簡略化）

---

## 実装ステップ（順番が超大事）🪜💨

### Step 1) DomainEvent の共通形を作る📦

```ts
// domain/events/DomainEvent.ts
export interface DomainEvent {
  readonly type: string;        // 例: "payment.completed"
  readonly occurredAt: Date;    // いつ起きた？
}
```

---

### Step 2) AggregateRoot に「イベント溜め」を持たせる🧺⚡

```ts
// domain/shared/AggregateRoot.ts
import { DomainEvent } from "../events/DomainEvent";

export abstract class AggregateRoot {
  private _domainEvents: DomainEvent[] = [];

  protected addDomainEvent(event: DomainEvent): void {
    this._domainEvents.push(event);
  }

  // アプリ層がまとめて取り出して配る
  pullDomainEvents(): DomainEvent[] {
    const events = this._domainEvents;
    this._domainEvents = [];
    return events;
  }
}
```

---

### Step 3) 今回のイベントを定義する（最小情報で）🔔

「情報を盛りすぎない」がポイントだよ〜！🍱⚖️
（必要になったら、**別のQueryで取りに行く**ほうが安全なことが多い）

```ts
// domain/order/events/PaymentCompleted.ts
import { DomainEvent } from "../../events/DomainEvent";

export class PaymentCompleted implements DomainEvent {
  readonly type = "payment.completed" as const;

  constructor(
    public readonly orderId: string,
    public readonly paidAmountYen: number,
    public readonly occurredAt: Date
  ) {}
}
```

---

### Step 4) Order 集約がイベントを発行するようにする🏯✨

```ts
// domain/order/Order.ts
import { AggregateRoot } from "../shared/AggregateRoot";
import { PaymentCompleted } from "./events/PaymentCompleted";

type OrderStatus = "Draft" | "Confirmed" | "Paid" | "Cancelled";

export class Order extends AggregateRoot {
  private constructor(
    public readonly id: string,
    private status: OrderStatus,
    private totalYen: number
  ) {
    super();
  }

  static create(id: string, totalYen: number): Order {
    return new Order(id, "Confirmed", totalYen); // ここは簡略化（本当は作成〜確定など）
  }

  getStatus(): OrderStatus {
    return this.status;
  }

  getTotalYen(): number {
    return this.totalYen;
  }

  pay(paidAt: Date): void {
    if (this.status !== "Confirmed") {
      throw new Error("支払いできない状態だよ😵‍💫");
    }

    this.status = "Paid";

    // ✅ ここで「起きた事実」を発行する
    this.addDomainEvent(
      new PaymentCompleted(this.id, this.totalYen, paidAt)
    );
  }
}
```

---

### Step 5) EventBus（同期の配達係）を作る📮🏃‍♀️

![Event Bus](./picture/ddd_ts_study_094_event_bus.png)

* **subscribe**：購読登録
* **publishAll**：イベントを順に配る（同期＝“この処理が終わるまで待つ”）

```ts
// app/events/InMemoryEventBus.ts
import { DomainEvent } from "../../domain/events/DomainEvent";

export type EventHandler<E extends DomainEvent = DomainEvent> =
  (event: E) => Promise<void> | void;

export class InMemoryEventBus {
  private handlers = new Map<string, EventHandler[]>();

  subscribe<E extends DomainEvent>(type: E["type"], handler: EventHandler<E>): void {
    const list = this.handlers.get(type) ?? [];
    list.push(handler as EventHandler);
    this.handlers.set(type, list);
  }

  async publish(event: DomainEvent): Promise<void> {
    const list = this.handlers.get(event.type) ?? [];
    for (const handler of list) {
      await handler(event);
    }
  }

  async publishAll(events: DomainEvent[]): Promise<void> {
    for (const e of events) {
      await this.publish(e);
    }
  }
}
```

> 💡 “同期”って言っても、TSの世界では `await` で順番に待つのが実用的だよ〜！✨

---

### Step 6) 購読者：レシート作成ハンドラを作る🧾🎀

![Receipt Flow](./picture/ddd_ts_study_094_receipt_flow.png)

```ts
// domain/receipt/Receipt.ts
export class Receipt {
  private constructor(
    public readonly id: string,
    public readonly orderId: string,
    public readonly issuedAt: Date,
    public readonly amountYen: number
  ) {}

  static issue(params: { id: string; orderId: string; issuedAt: Date; amountYen: number }): Receipt {
    return new Receipt(params.id, params.orderId, params.issuedAt, params.amountYen);
  }
}
```

![Idempotency Check](./picture/ddd_ts_study_094_idempotency_check.png)

```ts
// app/handlers/CreateReceiptOnPaymentCompleted.ts
import { randomUUID } from "node:crypto";
import { Receipt } from "../../domain/receipt/Receipt";
import { PaymentCompleted } from "../../domain/order/events/PaymentCompleted";

export interface ReceiptRepository {
  save(receipt: Receipt): Promise<void>;
  findByOrderId(orderId: string): Promise<Receipt | null>;
}

export class CreateReceiptOnPaymentCompleted {
  constructor(private readonly receiptRepo: ReceiptRepository) {}

  async handle(event: PaymentCompleted): Promise<void> {
    // ✅ “二重発行”の超かんたん対策（冪等性は第96章で本格的に！）
    const exists = await this.receiptRepo.findByOrderId(event.orderId);
    if (exists) return;

    const receipt = Receipt.issue({
      id: randomUUID(),
      orderId: event.orderId,
      issuedAt: event.occurredAt,
      amountYen: event.paidAmountYen,
    });

    await this.receiptRepo.save(receipt);
  }
}
```

---

### Step 7) ユースケースで「保存→イベント配布」をつなぐ🎬🔗

![App Flow](./picture/ddd_ts_study_094_app_flow.png)

ここがこの章のメイン！✨
「ドメインがイベントを溜める」→「アプリ層が回収して配る」

```ts
// app/usecases/PayOrderService.ts
import { Order } from "../../domain/order/Order";
import { InMemoryEventBus } from "../events/InMemoryEventBus";

export interface OrderRepository {
  findById(id: string): Promise<Order | null>;
  save(order: Order): Promise<void>;
}

export class PayOrderService {
  constructor(
    private readonly orderRepo: OrderRepository,
    private readonly eventBus: InMemoryEventBus
  ) {}

  async execute(orderId: string, paidAt: Date): Promise<void> {
    const order = await this.orderRepo.findById(orderId);
    if (!order) throw new Error("注文が見つからないよ🥺");

    order.pay(paidAt);

    // ① 保存
    await this.orderRepo.save(order);

    // ② イベント回収して配る（同期）
    const events = order.pullDomainEvents();
    await this.eventBus.publishAll(events);
  }
}
```

> ⚠️ ここは超重要メモ：
> **保存が終わったあとに購読処理が失敗**すると、状態が“途中”になる可能性があるよね💦
> だから現場では「トランザクション」「Outbox」みたいな仕組みを入れて堅くする（第97章へつながる）📤📬✨

---

## InMemory Repo（テスト用の最小）🧪📦

![InMemory Bus](./picture/ddd_ts_study_094_inmemory_bus.png)

```ts
// infra/InMemoryRepos.ts
import { Order } from "../domain/order/Order";
import { Receipt } from "../domain/receipt/Receipt";

export class InMemoryOrderRepository {
  private store = new Map<string, Order>();

  async findById(id: string): Promise<Order | null> {
    return this.store.get(id) ?? null;
  }

  async save(order: Order): Promise<void> {
    this.store.set(order.id, order);
  }

  seed(order: Order): void {
    this.store.set(order.id, order);
  }
}

export class InMemoryReceiptRepository {
  private store = new Map<string, Receipt>(); // receiptId -> receipt

  async save(receipt: Receipt): Promise<void> {
    this.store.set(receipt.id, receipt);
  }

  async findByOrderId(orderId: string): Promise<Receipt | null> {
    for (const r of this.store.values()) {
      if (r.orderId === orderId) return r;
    }
    return null;
  }
}
```

---

## テスト（Vitest）で “動いた！” を作る🧁🧪

```ts
// test/pay-order.spec.ts
import { describe, it, expect } from "vitest";
import { Order } from "../src/domain/order/Order";
import { InMemoryEventBus } from "../src/app/events/InMemoryEventBus";
import { PayOrderService } from "../src/app/usecases/PayOrderService";
import { InMemoryOrderRepository, InMemoryReceiptRepository } from "../src/infra/InMemoryRepos";
import { CreateReceiptOnPaymentCompleted } from "../src/app/handlers/CreateReceiptOnPaymentCompleted";
import { PaymentCompleted } from "../src/domain/order/events/PaymentCompleted";

describe("PayOrderService + sync domain events", () => {
  it("支払い完了イベントでレシートが発行される🧾✨", async () => {
    const orderRepo = new InMemoryOrderRepository();
    const receiptRepo = new InMemoryReceiptRepository();
    const bus = new InMemoryEventBus();

    const handler = new CreateReceiptOnPaymentCompleted(receiptRepo);
    bus.subscribe<PaymentCompleted>("payment.completed", (e) => handler.handle(e as PaymentCompleted));

    const order = Order.create("order-1", 1200);
    orderRepo.seed(order);

    const usecase = new PayOrderService(orderRepo, bus);
    await usecase.execute("order-1", new Date("2026-02-07T10:00:00Z"));

    const receipt = await receiptRepo.findByOrderId("order-1");
    expect(receipt).not.toBeNull();
    expect(receipt!.amountYen).toBe(1200);
  });
});
```

---

## ありがちな事故あるある（ここ避けるだけで強い）⚠️😂

### ❌ 事故1：購読者が “Order の中身を直接いじる”🌀

* 購読者は基本「別の関心ごと」をやる場所だよ〜
* Orderの不変条件は **Order自身**で守らせるのが筋✨

### ❌ 事故2：イベントに情報を詰め込みすぎ🍱💥

* 画像みたいにデカいDTOをイベントに入れがち
* まずは **ID + 最小の重要値** が目安（第93章の復習だね）📦⚖️

### ❌ 事故3：同期購読で外部API叩いて遅くなる🐢🌩️

![Sync Risk](./picture/ddd_ts_study_094_sync_risk.png)

* 体感が一気に悪くなる
* 重い/不安定な連携は “非同期” へ（次章でやるよ）⏳🌍

### ❌ 事故4：購読処理が失敗した時に中途半端になる💔

* いまの最小構成だと起きうる
* 現場は「トランザクション」や「Outbox」で固める（第97章）📤📬

---

## AI（OpenAI Codex / GitHub Copilot）に頼むと強いプロンプト例🤖💬✨

### 1) “イベントの最小フィールド”を決めたい

* 「`PaymentCompleted`に入れるべき最小フィールドを、理由付きで提案して。入れすぎNG。購読者はレシート発行をする想定。」

### 2) “購読者の責務が肥大化してないか”チェック

* 「この handler の責務が重すぎないかレビューして。副作用の切り分け案も出して。」

### 3) “テストの抜け”を探してほしい

* 「このユースケースとイベント購読のテストケースを、正常/異常で追加提案して（特に二重処理・順序・例外）。」

---

## 理解チェック（3問だけ）📝✨

1. Domain Event は「命令」？それとも「事実」？📣
2. イベントはどこで発行して、どこで配るのがキレイ？🏯📮
3. 同期購読で重い外部連携をやると、どんな問題が出る？🐢💥

---

## ミニ演習（やると一気に定着）🎮🌸

* 演習A：`ReceiptIssued` イベントを追加して、「レシート発行ログ」を購読で残す🧾🗒️
* 演習B：購読者を2つに増やして（例：ポイント付与✨）、**順序依存が出たらどうする？**を考える🔁
* 演習C：購読者が例外を投げたとき、`publishAll` を「止める/続ける」どっちが嬉しい？方針を決める⚖️

---

次の第95章で「じゃあ非同期はなんで必要なの？🤔」を、今日の同期モデルと比較しながらスッキリ理解していこうね〜！⏳🌍✨（第94章の構成ができてると、めちゃ気持ちよく繋がるよ🔗💕）

（※ちなみに TypeScript のネイティブ移行の話は Microsoft の公式アップデートでも触れられてるので、気になるならそこも読むとテンション上がるやつ！([Microsoft for Developers][2])）

[1]: https://www.npmjs.com/package/typescript?utm_source=chatgpt.com "typescript"
[2]: https://devblogs.microsoft.com/typescript/progress-on-typescript-7-december-2025/?utm_source=chatgpt.com "Progress on TypeScript 7 - December 2025"
[3]: https://github.com/microsoft/TypeScript/issues/63085?utm_source=chatgpt.com "TypeScript 6.0 Iteration Plan · Issue #63085"
[4]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
[5]: https://vitest.dev/blog/vitest-4?utm_source=chatgpt.com "Vitest 4.0 is out!"
[6]: https://jestjs.io/versions?utm_source=chatgpt.com "Jest Versions"
