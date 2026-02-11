# 第91章：Domain Event入門：「起きた事実」📣

![Domain Event入門：起きた事実](./picture/ddd_ts_study_091_domain_event_intro.png)

## 🎯 ねらい

ドメインの状態が変わった瞬間を、**「出来事（＝起きた事実）」として扱える**ようになることだよ〜！😊✨
（例：*「注文が確定した」*、*「支払いが完了した」* など）

## ✅ ゴール

この章が終わったら…

* Domain Event を **「過去形の事実」**として説明できる🗣️
* Aggregate（例：Order）が **自分でイベントを溜める**実装ができる🧺✨
* テストで **「イベントが出た／出てない」**を確認できる🧪💕

---

## 0) 最新情報メモ（2026-02-07 時点）📝✨

* TypeScript の安定版は **5.9.3**（npm の最新版表記）だよ〜 ([npm][1])
* TypeScript 6.0 は「橋渡し版」で、**2026-02-10 に Beta、2026-03-17 に Final**予定（公式Issueの計画表） ([GitHub][2])
* Vitest は **4.0**が 2025-10-22 に出てるよ〜 ([Vitest][3])

---

## 1) Domain Eventってなに？🧠✨（超やさしく）

![Fact vs Command](./picture/ddd_ts_study_091_fact_vs_command.png)

Domain Eventは一言でいうと…

> **ドメインで「起きた事実」を、あとから使える形で残すもの**📣

### ✅ 例（カフェ注文）

* ✅ OrderPlaced（注文が確定した）☕🧾
* ✅ PaymentCompleted（支払いが完了した）💳✨

### ❌ これは Domain Eventじゃない（よく混ざる！）

* ❌ PlaceOrder（注文してね）→ **命令（Command）**🧑‍🍳📢
* ❌ GetOrder（注文ちょうだい）→ **照会（Query）**🔎

**コツ：イベントは「過去形」**にするとブレにくいよ〜😊💡

---

## 2) Domain Eventの「3点セット」📦✨

Domain Event はだいたいこの3つを持つと強い！

1. **type**：何が起きた？（例：`order.placed`）🏷️
2. **occurredAt**：いつ起きた？⏰
3. **payload**：最低限な中身（IDとか合計とか）📮

⚠️ 入れすぎ注意：イベントが太ると、依存が増えて将来つらい…！💦
（「必要最小限」が基本だよ〜）

---

## 3) 実装の方針（この章の型）🧩✨

この章では、いきなり難しい仕組み（メッセージキュー等）はやらずに、

* **Aggregateがイベントを“発行したことにして”溜める**
* そのイベントを **あとで取り出せる（pull）**ようにする

ここまでをやるよ〜😊
（“どこで配る？”は次章でしっかりやる前提だよ！）

---

## 4) 実装：DomainEvent と AggregateRoot 🏗️🧺

### 4-1) `DomainEvent` 型（共通の形）📣

```ts
// src/domain/shared/DomainEvent.ts
export interface DomainEvent<TType extends string = string, TPayload = unknown> {
  readonly eventId: string;
  readonly type: TType;
  readonly occurredAt: Date;
  readonly payload: TPayload;
}
```

ポイント：**immutable（変更しない）**前提で `readonly` にしてるよ〜🧊✨

---

### 4-2) `Clock`（時間の注入）⏰🧪

イベントの `occurredAt` をテストで固定したいから、Clockを使うよ〜！

```ts
// src/domain/shared/Clock.ts
export interface Clock {
  now(): Date;
}

export const SystemClock: Clock = {
  now: () => new Date(),
};
```

---

### 4-3) AggregateRoot：イベントを溜めて、あとで取り出す🧺✨

```ts
// src/domain/shared/AggregateRoot.ts
import { DomainEvent } from "./DomainEvent.js";

export abstract class AggregateRoot {
  private _domainEvents: DomainEvent[] = [];

  protected addDomainEvent(event: DomainEvent): void {
    this._domainEvents.push(event);
  }

  /** 取り出したら空にする（重要！） */
  pullDomainEvents(): DomainEvent[] {
    const events = [...this._domainEvents];
    this._domainEvents = [];
    return events;
  }
}
```

✅ `pullDomainEvents()` が超大事！
これがないと「前に出したイベント」がずっと残って二重処理の原因になりがち😭💦

---

## 5) 例題：Order がイベントを出す☕🧾→📣

### 5-1) Order のイベント型を決める🏷️

```ts
// src/domain/order/OrderEvents.ts
import { DomainEvent } from "../shared/DomainEvent.js";

export type OrderPlaced = DomainEvent<
  "order.placed",
  { orderId: string; totalYen: number }
>;

export type PaymentCompleted = DomainEvent<
  "payment.completed",
  { orderId: string; paidYen: number }
>;
```

---

### 5-2) Order Aggregate（イベントを溜める）🏯✨

```ts
// src/domain/order/Order.ts
import { AggregateRoot } from "../shared/AggregateRoot.js";
import { Clock } from "../shared/Clock.js";
import type { OrderPlaced, PaymentCompleted } from "./OrderEvents.js";

type OrderStatus = "draft" | "placed" | "paid";

export class Order extends AggregateRoot {
  private status: OrderStatus = "draft";
  private totalYen: number = 0;

  constructor(
    private readonly orderId: string,
    private readonly clock: Clock,
  ) {
    super();
  }

  place(totalYen: number): void {
    if (this.status !== "draft") {
      throw new Error("注文はすでに作成済みだよ🥺");
    }
    if (totalYen <= 0) {
      throw new Error("合計金額が0以下はダメだよ🥺");
    }

    this.totalYen = totalYen;
    this.status = "placed";

    const event: OrderPlaced = {
      eventId: crypto.randomUUID(),
      type: "order.placed",
      occurredAt: this.clock.now(),
      payload: { orderId: this.orderId, totalYen: this.totalYen },
    };
    this.addDomainEvent(event);
  }

  pay(paidYen: number): void {
    if (this.status !== "placed") {
      throw new Error("支払いできる状態じゃないよ🥺");
    }
    if (paidYen !== this.totalYen) {
      throw new Error("支払い金額が合計と違うよ🥺");
    }

    this.status = "paid";

    const event: PaymentCompleted = {
      eventId: crypto.randomUUID(),
      type: "payment.completed",
      occurredAt: this.clock.now(),
      payload: { orderId: this.orderId, paidYen },
    };
    this.addDomainEvent(event);
  }
}
```

🎀 ここでの大事ポイント

* **状態が変わった直後にイベントを追加**してる📣✨
* 例外が出たら **イベントは出ない**（ルール違反だから）🧯

---

## 6) テスト：イベントが出た？出てない？🧪💖（Vitest）

```ts
// src/domain/order/Order.test.ts
import { describe, it, expect } from "vitest";
import { Order } from "./Order.js";
import type { Clock } from "../shared/Clock.js";

class FixedClock implements Clock {
  constructor(private readonly fixed: Date) {}
  now(): Date {
    return this.fixed;
  }
}

describe("Order Domain Events", () => {
  it("placeすると OrderPlaced が1つ出る📣", () => {
    const clock = new FixedClock(new Date("2026-02-07T10:00:00.000Z"));
    const order = new Order("order-1", clock);

    order.place(1200);

    const events = order.pullDomainEvents();
    expect(events).toHaveLength(1);
    expect(events[0].type).toBe("order.placed");
    expect(events[0].occurredAt.toISOString()).toBe("2026-02-07T10:00:00.000Z");
  });

  it("ルール違反ならイベントは出ない🧯", () => {
    const clock = new FixedClock(new Date("2026-02-07T10:00:00.000Z"));
    const order = new Order("order-1", clock);

    expect(() => order.place(0)).toThrow(); // 0円はダメ
    expect(order.pullDomainEvents()).toHaveLength(0);
  });

  it("payすると PaymentCompleted が出る💳📣", () => {
    const clock = new FixedClock(new Date("2026-02-07T10:00:00.000Z"));
    const order = new Order("order-1", clock);

    order.place(1200);
    order.pullDomainEvents(); // place の分はこのテストでは捨てる（=配った想定）

    order.pay(1200);

    const events = order.pullDomainEvents();
    expect(events).toHaveLength(1);
    expect(events[0].type).toBe("payment.completed");
    expect(events[0].payload).toEqual({ orderId: "order-1", paidYen: 1200 });
  });
});
```

💡 ここ、めっちゃDDDっぽい体験！
「状態が変わった」ことを、**イベントとして検証できる**のが嬉しいの😊✨

---

## 7) よくある落とし穴（先に回避〜！）⚠️😂

* **イベント名が未来形**：`OrderWillBePaid` みたいなのは迷子になりがち💦（過去形推奨）
* **payloadがでかすぎ**：Order全体を突っ込むのはやりすぎ😭
* **pullせずに溜めっぱなし**：二重処理の原因💥
* **イベント発行と副作用を混ぜる**：Domain内でメール送信とかはNG寄り✉️🚫
  → “確実に”やるなら Outbox 等の考え方が出てくるよ（後半で登場！） ([Stack Overflow][4])

---

## 8) 🤖 AI活用プロンプト（コピペOK）✨

### A) イベント名の候補を作る

「注文ドメインで、過去形のDomain Event名を10個。ユビキタス言語を優先。typeは `order.xxx` 形式。曖昧なら理由も。」

### B) payloadの最小化チェック

「このイベントpayloadは太りすぎ？最小限に削って。
“後から購読側が困る情報”と“入れるべきでない情報”を分けて教えて。」

### C) テスト観点の追加

「OrderPlaced/PaymentCompleted で“イベントが出ない”ケースを3つ追加して（ルール違反の観点で）。」

---

## 9) 小演習（やると一気に定着）🏋️‍♀️💖

### 演習1：キャンセルイベントを追加😢📣

* `OrderCancelled` を追加（type例：`order.cancelled`）
* `cancel()` を実装して、`placed` のときだけ可能にする
* テストで **「cancelしたらイベントが出る」**を確認🧪✨

### 演習2：イベントを太らせない練習📦⚖️

* `OrderPlaced` の payload に「注文者名」「メニュー一覧」も入れたくなったら…

  * **本当に必要？**
  * 必要なら “別のイベント” に分けた方がいい？
    この判断をAIに壁打ちしてみてね🤖💬

---

## 10) 理解チェック✅（サクッと）

* Q1：Domain Event は「命令」？「事実」？どっち？📣
* Q2：イベント名は基本何形（過去形/未来形）？⏳
* Q3：イベントを溜めたあと、なぜ `pullDomainEvents()` で空にするの？🧺

---

次の第92章では、**「いつ発行する？どこで発行する？」**を、責務を混ぜずに組み立てるよ〜📍⚡
（Aggregateは“溜める”、Applicationが“配る”、が気持ちよく繋がる！😊✨）

[1]: https://www.npmjs.com/package/typescript?activeTab=versions&utm_source=chatgpt.com "typescript"
[2]: https://github.com/microsoft/TypeScript/issues/63085?utm_source=chatgpt.com "TypeScript 6.0 Iteration Plan · Issue #63085"
[3]: https://vitest.dev/blog/vitest-4?utm_source=chatgpt.com "Vitest 4.0 is out!"
[4]: https://stackoverflow.com/questions/43436458/is-it-safe-to-publish-domain-event-before-persisting-the-aggregate?utm_source=chatgpt.com "c# - Is it safe to publish Domain Event before persisting the ..."
