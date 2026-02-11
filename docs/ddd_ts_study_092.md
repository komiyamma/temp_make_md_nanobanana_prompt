# 第92章：いつ発行する？どこで発行する？📍⚡

![いつ発行する？どこで発行する？](./picture/ddd_ts_study_092_event_location.png)

第91章で「Domain Event＝起きた事実📣」を掴んだよね✨
第92章はその次の壁👇

* **いつイベントを出すの？（タイミング）**⏱️
* **どこでイベントを作るの？（責務の場所）**🏠
* **どこで配るの？（配信の場所）**📮

ここがブレると、DDDが一気に「それっぽいだけ」になっちゃうの…！😵‍💫
逆にここが決まると、後半（非同期・Outbox）へ超キレイに繋がるよ〜！🌈

---

## 0) まず超重要：この章の“用語の整理”🧠✨

![Raise vs Dispatch](./picture/ddd_ts_study_092_raise_vs_dispatch.png)

DDDの「発行」って、実は2段階に分けて考えるとスッキリするよ👇

### ✅ A. **イベントを“発生”させる（raise / record）**⚡️

* 「起きた事実」を **イベントオブジェクトとして作る**
* **集約の中に一旦ためる**（まだ外に配らない）

### ✅ B. **イベントを“配信”する（dispatch / publish）**📮

* 集約の外（アプリ層など）で、購読者に配る
* 必要なら「保存が成功した後」にやる（超大事）🧷

この分離がDDDのコア！✨
Domain Eventは「状態変更の副作用を、あとで扱える形にする」ためのパターンだよ。 ([martinfowler.com][1])

---

## 1) いつ発行する？（タイミング）⏰✅

![Timing Check](./picture/ddd_ts_study_092_timing_check.png)

結論からいくね👇

### ✅ 発行（raise）は「ドメイン的に意味のある状態変更が成立した直後」🎯

つまり…

* ルールチェック（不変条件）を通過✅
* 状態が変わった✅
* 「起きた事実」が確定✅
  → **ここでイベントを作って記録する**⚡️

たとえばカフェ注文だと☕🧾

* 注文が確定した → `OrderConfirmed`
* 支払いが完了した → `PaymentCompleted`
* 提供が完了した → `OrderFulfilled`

Domain Eventは「〜する予定」じゃなくて、**過去形（起きた）**が基本だよ📣（“fact”だからね） ([martinfowler.com][1])

---

## 2) どこで発行する？（イベントを“作る場所”）🏯⚡️

![Location Aggregate](./picture/ddd_ts_study_092_location_aggregate.png)

ここが第92章の本題〜！🎉

### ✅ イベントを“作る”のは **集約（Aggregate Root）の中**🏯👑

理由はカンタン👇

* 集約が **不変条件の守護神🛡️** だから
* その集約で起きた「重要な事実」は、集約が一番正しく判断できるから
* アプリ層で作ると「作り忘れ」「二重発行」が起きやすい😇

> イベントは、集約の整合性を守ったうえで登録される、という考え方が定番だよ🧷 ([Microsoft Learn][2])

---

## 3) どこで配るの？（“配信の場所”）📮🧑‍🍳

### ✅ 配るのは **アプリ層（Application Service / UseCase）**が基本🎬

![Dispatch After Save](./picture/ddd_ts_study_092_dispatch_after_save.png)

流れはこう👇

1. Repoで集約を取る📚
2. 集約メソッドを呼ぶ（ここでイベントが「記録」される）⚡️
3. Repoで保存する💾
4. **保存がうまくいったら**イベントを取り出して配信📮

「保存前に配る」のは危険だよ⚠️
あとで保存が失敗したら、「起きてないのに通知した」状態になるからね😱
この“コミット後に配る”考え方は多くの実装ガイドで強調されるよ。 ([kamilgrzybek.com][3])

---

## 4) 図でイメージする（この章の正解ルート）🗺️✨

![Flow Diagram](./picture/ddd_ts_study_092_flow_diagram.png)

```text
UI/Controller
   │
   ▼
Application Service（ユースケース）🎬
   │  load
   ▼
Repository 📚  ──→ Aggregate（Order）🏯
                      │
                      │  pay() など
                      ▼
               （内部で event を記録）⚡️
                      │
   ▲                  ▼
   │  save        Repository 📚
   │                  │
   │          （保存成功）✅
   │                  ▼
   └────── dispatch events 📮 ──→ Handlers 🔔（レシート作る等）
```

---

## 5) TypeScriptで実装してみよう🧁⚡️（最小で気持ちいい形）

> ちなみにTypeScriptは少なくとも 5.9 系のドキュメントが 2026-02 頃も更新されてるよ。 ([TypeScript][4])
> テストは Vitest みたいな軽い選択肢が人気。 ([Vitest][5])

### 5-1) DomainEvent の型を作る📣

```ts
// domain/events/DomainEvent.ts
export interface DomainEvent {
  readonly eventName: string;        // 例: "PaymentCompleted"
  readonly occurredAt: Date;         // いつ起きた？
  readonly eventId: string;          // 重複対策や追跡に使える
}
```

`eventName` を文字列にしておくと、最小実装がラクだよ🧸
（後で「型安全にしたい！」ってなったら改良できる✨）

---

### 5-2) AggregateRoot の“イベント箱”を作る📦⚡️

```ts
// domain/shared/AggregateRoot.ts
import { DomainEvent } from "../events/DomainEvent";

export abstract class AggregateRoot {
  private domainEvents: DomainEvent[] = [];

  protected record(event: DomainEvent): void {
    this.domainEvents.push(event);
  }

  /** 外に配る用：取り出したら空にする（ワンショット） */
  pullDomainEvents(): DomainEvent[] {
    const events = this.domainEvents;
    this.domainEvents = [];
    return events;
  }
}
```

ポイント👇

* 集約の中では **record（記録）**するだけ⚡️
* “配る”のはやらない📮（責務が混ざるからね）

---

### 5-3) イベントを定義する（例：支払い完了）💳✨

```ts
// domain/order/events/PaymentCompleted.ts
import { DomainEvent } from "../../events/DomainEvent";

export class PaymentCompleted implements DomainEvent {
  readonly eventName = "PaymentCompleted";
  readonly occurredAt: Date;
  readonly eventId: string;

  constructor(
    readonly orderId: string,
    readonly paidAmountYen: number,
    now: Date,
    eventId: string
  ) {
    this.occurredAt = now;
    this.eventId = eventId;
  }
}
```

`now` と `eventId` を外から渡すのは、テストが楽になるからだよ🧪✨
（第86章のClock注入のノリ！⏰）

---

### 5-4) Order集約で「状態変更＋イベント記録」する🏯⚡️

![Event Creation](./picture/ddd_ts_study_092_event_creation.png)

```ts
// domain/order/Order.ts
import { AggregateRoot } from "../shared/AggregateRoot";
import { PaymentCompleted } from "./events/PaymentCompleted";

type OrderStatus = "Draft" | "Confirmed" | "Paid";

export class Order extends AggregateRoot {
  private status: OrderStatus = "Draft";

  constructor(
    readonly id: string,
    private totalYen: number
  ) {
    super();
  }

  confirm(): void {
    if (this.status !== "Draft") throw new Error("すでに確定済みだよ😵‍💫");
    this.status = "Confirmed";
  }

  pay(now: Date, eventId: string): void {
    if (this.status !== "Confirmed") throw new Error("確定してから支払ってね💦");
    this.status = "Paid";

    // ✅ 状態変更が成立したあとに「起きた事実」を記録
    this.record(new PaymentCompleted(this.id, this.totalYen, now, eventId));
  }

  getStatus(): OrderStatus {
    return this.status;
  }
}
```

ここが第92章の答えその1！✅
**イベントは集約メソッドの中で“記録”する**⚡️

---

### 5-5) 配信側（Dispatcher）を超シンプルに作る🔔📮

```ts
// app/events/DomainEventDispatcher.ts
import { DomainEvent } from "../../domain/events/DomainEvent";

type Handler<E extends DomainEvent = DomainEvent> = (event: E) => Promise<void> | void;

export class DomainEventDispatcher {
  private handlers = new Map<string, Handler[]>();

  on(eventName: string, handler: Handler): void {
    const list = this.handlers.get(eventName) ?? [];
    list.push(handler);
    this.handlers.set(eventName, list);
  }

  async dispatch(events: DomainEvent[]): Promise<void> {
    for (const event of events) {
      const list = this.handlers.get(event.eventName) ?? [];
      for (const h of list) await h(event);
    }
  }
}
```

---

### 5-6) アプリ層（ユースケース）で「保存→配信」する🎬📮

```ts
// app/usecases/PayOrder.ts
import { Order } from "../../domain/order/Order";
import { DomainEventDispatcher } from "../events/DomainEventDispatcher";

export interface OrderRepository {
  findById(id: string): Promise<Order | null>;
  save(order: Order): Promise<void>;
}

export class PayOrder {
  constructor(
    private readonly repo: OrderRepository,
    private readonly dispatcher: DomainEventDispatcher
  ) {}

  async execute(input: { orderId: string; now: Date; eventId: string }): Promise<void> {
    const order = await this.repo.findById(input.orderId);
    if (!order) throw new Error("注文が見つからないよ🥺");

    order.pay(input.now, input.eventId);

    // ✅ 先に保存
    await this.repo.save(order);

    // ✅ 保存後にイベントを取り出して配信
    const events = order.pullDomainEvents();
    await this.dispatcher.dispatch(events);
  }
}
```

ここが第92章の答えその2！✅
**配信はアプリ層で、基本は“保存のあと”**📮✨
（DBトランザクションがあるなら「コミット後」ね🧷 ([kamilgrzybek.com][3])）

---

## 6) “どこで発行する？”のよくある事故パターン😂⚠️

![Accident Patterns](./picture/ddd_ts_study_092_accident_patterns.png)

### ❌ 事故1：アプリ層がイベントを勝手に作る

* 「支払い完了」イベントを、集約の状態を見ずに作っちゃう
  → **不正なイベントが飛ぶ**😱

### ❌ 事故2：集約の中で dispatcher を呼ぶ

* `order.pay()` の中で `dispatcher.dispatch()` してしまう
  → 集約が“外の世界”に依存して、境界が崩れる🧨

### ❌ 事故3：保存前に配る

* 保存失敗したのに「支払い完了」が通知される
  → 事件です🚓💥

### ❌ 事故4：イベントが多すぎ（細かすぎ）

* `OrderTotalCalculated` とかまで全部イベント化
  → ノイズで死ぬ😇（第93章で整理するよ！）

---

## 7) テストの書き方（この章の“勝ち筋”）🧪💖

![Test Separation](./picture/ddd_ts_study_092_test_separation.png)

### ✅ テストは2種類に分けるとキレイ✨

1. **集約のテスト**：イベントが記録されるか？
2. **ユースケースのテスト**：保存後に配信されるか？

Vitestの方向性（軽量・Vite連携・Jest互換）も押さえておくと便利だよ。 ([Vitest][5])

### 7-1) 集約テスト例：payでイベントが出る？💳⚡️

```ts
import { describe, it, expect } from "vitest";
import { Order } from "../../domain/order/Order";

describe("Order.pay", () => {
  it("確定済みの注文を支払うとPaymentCompletedを記録する", () => {
    const order = new Order("o-1", 1200);
    order.confirm();

    order.pay(new Date("2026-02-07T00:00:00Z"), "evt-1");

    const events = order.pullDomainEvents();
    expect(events).toHaveLength(1);
    expect(events[0].eventName).toBe("PaymentCompleted");
  });
});
```

---

## 8) AIの使いどころ（この章は相性いい🤖💞）

### ✅ AIに頼むと強いこと

* 「イベント候補を列挙して、どれが“意味ある”か」🗂️
* 「発行ポイントがズレてないかレビュー」👀
* 「テスト観点の漏れ探し」🧪

### 💬 そのまま使えるプロンプト例

* 「`Order` 集約のメソッド一覧がこれ。どのメソッドでDomain Eventを記録するべき？理由もセットで💡」
* 「このイベントを“集約で記録→アプリ層で配信”に直したい。責務の混在がある場所を指摘して🥺」
* 「保存前配信になってない？事故パターンに当てはめてチェックして✅」

---

## 9) 章末ミニ演習🎓✨（手を動かすやつ！）

### 演習A：OrderConfirmed を追加しよう☕🧾

* `confirm()` の成功時に `OrderConfirmed` を記録する
* ユースケース側で dispatch されることもテストする

### 演習B：配信順のルールを決めよう🔁

* 同一ユースケース内で複数イベントが出る場合

  * 発生順で配る？
  * 種類ごとにまとめる？
    → “運用ルール”として決めてメモしておこう📝

---

## 10) この章のまとめ（暗記じゃなく感覚で！）🧠💖

* **イベントを作る（記録する）場所**：✅ 集約（Aggregate Root）🏯
* **イベントを配る場所**：✅ アプリ層（UseCase）🎬
* **タイミング**：✅ 状態変更が成立した直後に記録／保存（コミット）後に配信📮
* **やっちゃダメ**：集約内で外部配信、保存前配信、アプリ層で勝手にイベント生成😵‍💫

Domain Eventは「設計をキレイに分けるための橋」だよ🌉✨
次の第93章で「イベントに何を入れる？」を整えると、もっと気持ちよくなる〜！📦⚖️

[1]: https://martinfowler.com/eaaDev/DomainEvent.html?utm_source=chatgpt.com "Domain Event"
[2]: https://learn.microsoft.com/en-us/dotnet/architecture/microservices/microservice-ddd-cqrs-patterns/domain-events-design-implementation?utm_source=chatgpt.com "Domain events: Design and implementation - .NET"
[3]: https://www.kamilgrzybek.com/blog/posts/how-to-publish-handle-domain-events?utm_source=chatgpt.com "How to publish and handle Domain Events"
[4]: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-9.html?utm_source=chatgpt.com "Documentation - TypeScript 5.9"
[5]: https://vitest.dev/?utm_source=chatgpt.com "Vitest | Next Generation testing framework"
