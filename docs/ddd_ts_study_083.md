# 第83章：Specification実装①：単体条件を作る🧩

今日は「if文の条件」を、そのまま“再利用できる部品”にしちゃう回だよ〜！☺️☕
（2026年時点の最新として、TypeScriptは 5.9 系が現行の安定版ラインだよ〜）([Microsoft for Developers][1])

---

## この章のゴール✅🎯

* 条件チェックを「ifの塊」から「名前つき部品」に変える🧩
* 1つの条件＝1つの Specification として書けるようになる✍️
* テストが“秒速”で書けるようになる🧪⚡
* 次章（AND/OR 合成）に気持ちよく繋げる🧷✨

---

## まずイメージ🌸（if から卒業🎓）

たとえば「提供していい注文？」を考えるとき…

* if で書くと：条件が増えるたびに巨大化😵‍💫
* Specification だと：条件が“部品化”されて読みやすい📘✨

つまり…
**「条件そのものに名前をつける」＝仕様がそのままコードになる**って感じだよ😊💕

---

## Specification の最小形（超ミニ）🍼🧩

Specificationは「この子（candidate）は条件を満たしてる？」を true/false で返すだけ。

```ts
// src/domain/specification/Specification.ts
export interface Specification<T> {
  isSatisfiedBy(candidate: T): boolean;
}
```

このシンプルさが大事〜！✨
（この章では“単体条件”だけ。合成（AND/OR）は次章でやるよ🧷）

---

## 例題ドメイン（カフェ注文）☕🧾

注文（Order）にありがちな状態を用意して、そこに条件を当てていくよ〜😊

```ts
// src/domain/order/OrderStatus.ts
export type OrderStatus =
  | "Draft"
  | "Confirmed"
  | "Paid"
  | "Fulfilled"
  | "Cancelled";
```

Orderの形は、今回の説明に必要な最小だけ👇

```ts
// src/domain/order/Order.ts
import { OrderStatus } from "./OrderStatus";
import { Money } from "../valueObjects/Money";

export type OrderLine = Readonly<{
  menuItemId: string;
  quantity: number;
}>;

export type Order = Readonly<{
  status: OrderStatus;
  lines: ReadonlyArray<OrderLine>;
  total: Money;
  pickupDueAt: Date; // ※時間の扱いを綺麗にするのは第86章で強化するよ⏰
}>;
```

Money は超ミニでOK（本当は第33章のMoney VOを使う想定💴）

```ts
// src/domain/valueObjects/Money.ts
export class Money {
  private constructor(private readonly cents: number) {}

  static ofYen(yen: number): Money {
    // 例を単純化：1円=1cents扱い（プロダクトなら通貨や丸めをちゃんとやろうね💡）
    if (!Number.isInteger(yen)) throw new Error("Money must be integer.");
    if (yen < 0) throw new Error("Money cannot be negative.");
    return new Money(yen);
  }

  greaterThanOrEqual(other: Money): boolean {
    return this.cents >= other.cents;
  }
}
```

---

## 単体Specificationを3つ作ろう🧩🧩🧩

この章のコツはこれ👇
**「条件を1個だけ言う」**（欲張ると次章の仕事になっちゃう😂）

---

### ①「支払い済み？」🧾✅

```ts
// src/domain/order/specs/OrderIsPaidSpec.ts
import { Specification } from "../../specification/Specification";
import { Order } from "../Order";

export class OrderIsPaidSpec implements Specification<Order> {
  isSatisfiedBy(order: Order): boolean {
    // Fulfilled も「支払い済み扱い」にするのは自然だよね☕
    return order.status === "Paid" || order.status === "Fulfilled";
  }
}
```

---

### ②「明細が1件以上ある？」🧾➕✅

```ts
// src/domain/order/specs/OrderHasAtLeastOneLineSpec.ts
import { Specification } from "../../specification/Specification";
import { Order } from "../Order";

export class OrderHasAtLeastOneLineSpec implements Specification<Order> {
  isSatisfiedBy(order: Order): boolean {
    return order.lines.length >= 1;
  }
}
```

---

### ③「合計が最低金額以上？」💴✅

```ts
// src/domain/order/specs/OrderTotalAtLeastSpec.ts
import { Specification } from "../../specification/Specification";
import { Order } from "../Order";
import { Money } from "../../valueObjects/Money";

export class OrderTotalAtLeastSpec implements Specification<Order> {
  constructor(private readonly min: Money) {}

  isSatisfiedBy(order: Order): boolean {
    return order.total.greaterThanOrEqual(this.min);
  }
}
```

---

### おまけ：時間系「期限内？」⏰✅（この章では“暫定”でOK）

本当は第86章で Clock 注入にして“テストしやすい今”にするんだけど、
この章は「単体条件の作り方」を体に入れるのが優先だから、いったんこう👇

```ts
// src/domain/order/specs/OrderIsWithinPickupDeadlineSpec.ts
import { Specification } from "../../specification/Specification";
import { Order } from "../Order";

export class OrderIsWithinPickupDeadlineSpec implements Specification<Order> {
  constructor(private readonly now: Date) {}

  isSatisfiedBy(order: Order): boolean {
    return this.now.getTime() <= order.pickupDueAt.getTime();
  }
}
```

---

## テストを書こう🧪💖（Vitest）

2026年の最新ラインだと、Vitest は 4.0.x が “latest” になってるよ〜([NPM][2])
（beta もあるけど、教材では stable を推しがち😊）

### テスト用の注文ファクトリ（テスト内でOK）

```ts
// src/domain/order/specs/_testHelpers.ts
import { Order } from "../Order";
import { Money } from "../../valueObjects/Money";

export const makeOrder = (patch: Partial<Order> = {}): Order => {
  const base: Order = {
    status: "Draft",
    lines: [{ menuItemId: "latte", quantity: 1 }],
    total: Money.ofYen(500),
    pickupDueAt: new Date("2026-02-07T10:00:00.000Z"),
  };
  return { ...base, ...patch };
};
```

---

### ① OrderIsPaidSpec のテスト🧾✅

```ts
// src/domain/order/specs/OrderIsPaidSpec.test.ts
import { describe, it, expect } from "vitest";
import { OrderIsPaidSpec } from "./OrderIsPaidSpec";
import { makeOrder } from "./_testHelpers";

describe("OrderIsPaidSpec", () => {
  it("Paid なら true", () => {
    const spec = new OrderIsPaidSpec();
    const order = makeOrder({ status: "Paid" });
    expect(spec.isSatisfiedBy(order)).toBe(true);
  });

  it("Fulfilled なら true", () => {
    const spec = new OrderIsPaidSpec();
    const order = makeOrder({ status: "Fulfilled" });
    expect(spec.isSatisfiedBy(order)).toBe(true);
  });

  it("Confirmed なら false", () => {
    const spec = new OrderIsPaidSpec();
    const order = makeOrder({ status: "Confirmed" });
    expect(spec.isSatisfiedBy(order)).toBe(false);
  });
});
```

---

### ② OrderTotalAtLeastSpec のテスト💴✅

```ts
// src/domain/order/specs/OrderTotalAtLeastSpec.test.ts
import { describe, it, expect } from "vitest";
import { OrderTotalAtLeastSpec } from "./OrderTotalAtLeastSpec";
import { makeOrder } from "./_testHelpers";
import { Money } from "../../valueObjects/Money";

describe("OrderTotalAtLeastSpec", () => {
  it("合計が最小以上なら true", () => {
    const spec = new OrderTotalAtLeastSpec(Money.ofYen(500));
    const order = makeOrder({ total: Money.ofYen(500) });
    expect(spec.isSatisfiedBy(order)).toBe(true);
  });

  it("合計が足りないなら false", () => {
    const spec = new OrderTotalAtLeastSpec(Money.ofYen(600));
    const order = makeOrder({ total: Money.ofYen(500) });
    expect(spec.isSatisfiedBy(order)).toBe(false);
  });
});
```

---

### ③ 期限内Spec のテスト⏰✅

```ts
// src/domain/order/specs/OrderIsWithinPickupDeadlineSpec.test.ts
import { describe, it, expect } from "vitest";
import { OrderIsWithinPickupDeadlineSpec } from "./OrderIsWithinPickupDeadlineSpec";
import { makeOrder } from "./_testHelpers";

describe("OrderIsWithinPickupDeadlineSpec", () => {
  it("今が期限より前なら true", () => {
    const now = new Date("2026-02-07T09:59:59.000Z");
    const spec = new OrderIsWithinPickupDeadlineSpec(now);
    const order = makeOrder({ pickupDueAt: new Date("2026-02-07T10:00:00.000Z") });
    expect(spec.isSatisfiedBy(order)).toBe(true);
  });

  it("今が期限を過ぎてたら false", () => {
    const now = new Date("2026-02-07T10:00:01.000Z");
    const spec = new OrderIsWithinPickupDeadlineSpec(now);
    const order = makeOrder({ pickupDueAt: new Date("2026-02-07T10:00:00.000Z") });
    expect(spec.isSatisfiedBy(order)).toBe(false);
  });
});
```

---

## どこで使うの？（ユースケース側の読みやすさが爆上がり）🎬✨

たとえば「提供（Fulfill）」の前提チェックに使うと…

```ts
// 例：app層のどこか（イメージ）
import { OrderIsPaidSpec } from "../domain/order/specs/OrderIsPaidSpec";

const spec = new OrderIsPaidSpec();
if (!spec.isSatisfiedBy(order)) {
  throw new Error("支払いが完了してない注文は提供できません🥺");
}
```

この時点ではまだ if があるけど、**中身が“意味のある単語”**になるのがポイント😊💕

---

## うまくいくコツ🍀（単体条件の鉄則）

* ✅ Specification は「判定だけ」する（例外投げたり、保存したりしない）
* ✅ 1つのSpecは、1つのルールだけ言う
* ✅ 名前は「口に出して読める」ものにする（ユビキタス言語）🗣️✨
* ✅ テストは「true になる例」と「false になる例」を最低1つずつ🧪

---

## よくある事故😂⚠️

* ❌ Specの中で「DBを読みに行く」
  → それはもうSpecじゃなくて“処理”になってる💦（次のPolicyやアプリ層の仕事寄り）
* ❌ 1クラスに条件を詰め込みすぎる
  → 合成（AND/OR）でやると綺麗になる（次章！）🧷
* ❌ 仕様に名前がない
  → 「なんの条件？」ってなって、結局 if 地獄に戻る😇

---

## AI（Copilot/Codex）に頼むときのテンプレ🤖🪄

そのままコピペで使えるやつ置いとくね😊💕

* 「次の条件を単体Specificationにしてください： “支払い済みであること”。ファイル名とクラス名も提案して。isSatisfiedBy 以外の副作用は入れないで。」
* 「このSpecificationのテストをVitestで作って：trueになるケースとfalseになるケースを最低1つずつ。Arrange/Act/Assertが分かる形で。」
* 「命名案を3つ出して、ユビキタス言語として自然なものを1つ選んで理由も。」

---

## 章末ミニ問題🎓💕

1. 「キャンセル済みじゃない」を単体Specificationにすると、クラス名は何が自然？🗣️
2. 「注文の明細が最大10件まで」を単体Specificationにすると、どんなテスト境界値がいる？🧪
3. 「期限内」Specで Date.now を直接呼ぶと、何が困る？（第86章への伏線⏰）

---

## 今日のまとめ🍰✨

* Specificationは「条件に名前をつける」パターン🧩
* まずは単体条件を小さく作る（1条件＝1クラス）
* テストが楽になる＆次章のAND/OR合成が超気持ちよくなる🧷💖

次の第84章で、今日作った単体Specたちを **AND/OR で合体**させて「文章みたいに読める条件」にしていくよ〜！😊✨

[1]: https://devblogs.microsoft.com/typescript/announcing-typescript-5-9/ "Announcing TypeScript 5.9 - TypeScript"
[2]: https://www.npmjs.com/package/vitest?activeTab=versions&utm_source=chatgpt.com "vitest"
