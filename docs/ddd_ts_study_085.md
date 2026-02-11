# 第85章：Policy（方針）入門：条件→行動🧠➡️🏃‍♀️

この章はね、**Specificationで「条件（真/偽）」をきれいにしたあとに**、
**「じゃあ条件を満たしたら、何をするの？」**をスッキリ書くための道具が **Policy（方針）**だよ〜！🫶✨

---

## 1) 今日のゴール 🎯✨

* 「条件（Specification）」と「行動（Policy）」を**分けて考えられる**🧩
* ifが増えても、**読むのがラクな形**で「運用ルール」を書ける🌿
* Policyを**ドメインの言葉として**コードに残せる📘💛

---

## 2) Policyってなに？（超やさしく）🧠💡

### ✅ Specification：質問する人 🙋‍♀️

* 「この注文、学生割の対象？」
* 「この注文、合計が1200円以上？」
  → **真/偽を返す**（Yes/No）だけの係

Specificationは「ビジネスルールを組み合わせる」ためのパターンとしてDDD文脈でもよく使われるよ〜。([ウィキペディア][1])

### ✅ Policy：決める人 🧑‍⚖️➡️📝

* 「学生割の対象なら、**10%割引を適用して**、**次回クーポン通知も予約する**」
  → **条件→行動（方針）**を表現する係

DDDの文脈でも、Policyは「ルールを明示的に分離する」目的で使われ、**STRATEGY（戦略）と同じ発想**として紹介されてるよ。([fabiofumarola.github.io][2])

---

## 3) なんで必要？（if地獄の未来👀⚠️）

たとえば「キャンペーン」が増えると…

* 学生割 🎓
* 平日限定 📅
* アプリ決済限定 📱
* 初回注文限定 🌟
* 雨の日ボーナス ☔

これをアプリ層で全部 if で書くと、**読みづらい・直しづらい・漏れる**の三重苦😵‍💫💥
だからこうするのが気持ちいい✨

* 条件はSpecification（質問）
* “どうするか”はPolicy（方針）
* 実際の副作用（通知送信など）はアプリ層（実行）

---

## 4) 章のメイン例題 ☕🧾：「学生・平日・合計1200円以上なら…」

**方針（Policy）**：
🎓学生 かつ 📅平日 かつ 💴合計1200円以上 なら
➡️ **10%割引を適用**して、📩 **次回クーポン通知を予約する**

ここで大事ポイント💡
Policyは「通知を送る」みたいな副作用を**直接やらない**で、
**“やるべきこと（計画）”を返す**のが扱いやすいよ〜🫶✨

---

## 5) 実装してみよう（最小セット）🧩🧠➡️🏃‍♀️

> ここでは、Specificationは第82〜84章の資産がある前提で「最小の形」だけ置くね✨
> （合成AND/ORは、今まで通り使う想定だよ〜！）

### 5-1. ドメイン：Specification（質問）🔎📄

```ts
// domain/specification/Specification.ts
export interface Specification<T> {
  isSatisfiedBy(candidate: T): boolean;
}

export class AndSpecification<T> implements Specification<T> {
  constructor(
    private readonly left: Specification<T>,
    private readonly right: Specification<T>,
  ) {}

  isSatisfiedBy(candidate: T): boolean {
    return this.left.isSatisfiedBy(candidate) && this.right.isSatisfiedBy(candidate);
  }
}
```

### 5-2. ドメイン：例題の型（Orderなど）☕🧾

```ts
// domain/order/Order.ts
export type OrderDayType = "weekday" | "weekend";

export class Money {
  private constructor(private readonly yen: number) {}

  static ofYen(yen: number): Money {
    if (!Number.isInteger(yen) || yen < 0) throw new Error("Money must be a non-negative integer yen.");
    return new Money(yen);
  }

  toYen(): number {
    return this.yen;
  }

  isGte(other: Money): boolean {
    return this.yen >= other.yen;
  }

  percentOff(rate: number): Money {
    // rate: 0.10 = 10% off
    if (!(rate > 0 && rate < 1)) throw new Error("rate must be between 0 and 1.");
    const discount = Math.floor(this.yen * rate);
    return Money.ofYen(discount);
  }

  minus(discount: Money): Money {
    const v = this.yen - discount.yen;
    if (v < 0) throw new Error("total cannot be negative.");
    return Money.ofYen(v);
  }
}

export class Customer {
  constructor(
    public readonly customerId: string,
    public readonly isStudent: boolean,
  ) {}
}

export class Order {
  private discount: Money = Money.ofYen(0);

  constructor(
    public readonly orderId: string,
    public readonly customer: Customer,
    public readonly dayType: OrderDayType,
    private readonly subtotal: Money,
  ) {}

  getSubtotal(): Money {
    return this.subtotal;
  }

  getDiscount(): Money {
    return this.discount;
  }

  getTotal(): Money {
    return this.subtotal.minus(this.discount);
  }

  applyDiscount(discount: Money): void {
    // 例：割引は小計を超えちゃダメ、とかもここで守れるよ✨
    this.discount = discount;
  }
}
```

### 5-3. ドメイン：今回のSpecificationたち（条件）🎓📅💴

```ts
// domain/promotion/specs.ts
import { Money, Order } from "../order/Order";
import { Specification } from "../specification/Specification";

export class StudentCustomerSpec implements Specification<Order> {
  isSatisfiedBy(order: Order): boolean {
    return order.customer.isStudent;
  }
}

export class WeekdaySpec implements Specification<Order> {
  isSatisfiedBy(order: Order): boolean {
    return order.dayType === "weekday";
  }
}

export class SubtotalAtLeastSpec implements Specification<Order> {
  constructor(private readonly min: Money) {}

  isSatisfiedBy(order: Order): boolean {
    return order.getSubtotal().isGte(this.min);
  }
}
```

### 5-4. ドメイン：Policy（方針）🧠➡️🏃‍♀️

「何をするべきか」を **Decision（決定）**として返すよ✨

```ts
// domain/policy/StudentWeekdayPromotionPolicy.ts
import { Money, Order } from "../order/Order";
import { AndSpecification } from "../specification/Specification";
import { StudentCustomerSpec, SubtotalAtLeastSpec, WeekdaySpec } from "../promotion/specs";

export type PromotionDecision =
  | { kind: "none" }
  | {
      kind: "apply";
      discount: Money;
      shouldScheduleCouponNotification: boolean;
      notificationMessage: string;
    };

export class StudentWeekdayPromotionPolicy {
  private readonly eligibleSpec: AndSpecification<Order>;

  constructor() {
    const isStudent = new StudentCustomerSpec();
    const isWeekday = new WeekdaySpec();
    const minSubtotal = new SubtotalAtLeastSpec(Money.ofYen(1200));

    this.eligibleSpec = new AndSpecification(
      new AndSpecification(isStudent, isWeekday),
      minSubtotal,
    );
  }

  decide(order: Order): PromotionDecision {
    if (!this.eligibleSpec.isSatisfiedBy(order)) {
      return { kind: "none" };
    }

    const discountRate = 0.10; // 10%
    const discount = order.getSubtotal().percentOff(discountRate);

    return {
      kind: "apply",
      discount,
      shouldScheduleCouponNotification: true,
      notificationMessage: "学生さん平日特典だよ🎓✨ 次回使えるクーポンを用意したよ〜！",
    };
  }
}
```

> ✅ ここがキレイポイント✨
>
> * 条件はSpecificationで読める
> * Policyは「決める」だけ
> * 副作用は外（アプリ層）で実行しやすい

---

## 6) アプリ層で“実行”する（通知はここで）📨🧑‍🍳

```ts
// app/ApplyPromotionToOrder.ts
import { StudentWeekdayPromotionPolicy } from "../domain/policy/StudentWeekdayPromotionPolicy";
import { Order } from "../domain/order/Order";

export interface NotificationPort {
  scheduleCoupon(customerId: string, message: string): Promise<void>;
}

export class ApplyPromotionToOrder {
  constructor(
    private readonly policy: StudentWeekdayPromotionPolicy,
    private readonly notification: NotificationPort,
  ) {}

  async execute(order: Order): Promise<void> {
    const decision = this.policy.decide(order);

    if (decision.kind === "none") return;

    order.applyDiscount(decision.discount);

    if (decision.shouldScheduleCouponNotification) {
      await this.notification.scheduleCoupon(order.customer.customerId, decision.notificationMessage);
    }
  }
}
```

---

## 7) テスト（Vitestでサクッと）🧪✨

2026年頭時点でも、Vitestは継続的に更新されてて、直近は v4.x 系が出てるよ〜。([NPM][3])
TypeScript自体も 5.9 系（npm上は 5.9.3 が “latest” 表示）になってる。([NPM][4])

```ts
// test/StudentWeekdayPromotionPolicy.test.ts
import { describe, it, expect } from "vitest";
import { Customer, Money, Order } from "../src/domain/order/Order";
import { StudentWeekdayPromotionPolicy } from "../src/domain/policy/StudentWeekdayPromotionPolicy";

const createOrder = (params: { isStudent: boolean; dayType: "weekday" | "weekend"; subtotalYen: number }) => {
  const customer = new Customer("CUST-1", params.isStudent);
  return new Order("ORDER-1", customer, params.dayType, Money.ofYen(params.subtotalYen));
};

describe("StudentWeekdayPromotionPolicy", () => {
  it("学生×平日×小計1200円以上なら、10%割引＋通知予約", () => {
    const policy = new StudentWeekdayPromotionPolicy();
    const order = createOrder({ isStudent: true, dayType: "weekday", subtotalYen: 2000 });

    const decision = policy.decide(order);

    expect(decision.kind).toBe("apply");
    if (decision.kind === "apply") {
      expect(decision.discount.toYen()).toBe(200); // 2000の10%
      expect(decision.shouldScheduleCouponNotification).toBe(true);
    }
  });

  it("学生じゃないなら対象外", () => {
    const policy = new StudentWeekdayPromotionPolicy();
    const order = createOrder({ isStudent: false, dayType: "weekday", subtotalYen: 2000 });

    expect(policy.decide(order).kind).toBe("none");
  });

  it("休日なら対象外", () => {
    const policy = new StudentWeekdayPromotionPolicy();
    const order = createOrder({ isStudent: true, dayType: "weekend", subtotalYen: 2000 });

    expect(policy.decide(order).kind).toBe("none");
  });

  it("小計が足りないなら対象外", () => {
    const policy = new StudentWeekdayPromotionPolicy();
    const order = createOrder({ isStudent: true, dayType: "weekday", subtotalYen: 1199 });

    expect(policy.decide(order).kind).toBe("none");
  });
});
```

---

## 8) よくある失敗あるある 😂⚠️

### ❌ Policyが“何でも屋”になる

* Policyの中でDB保存したり、API叩いたり、ログ出したり…
  → 「決める」じゃなく「全部やる」になって破綻しがち😇

✅ 対策：Policyは **Decisionを返すだけ**に寄せる✨

### ❌ SpecificationとPolicyが混ざる

* 「isSatisfiedByの中で割引適用までやる」みたいなやつ
  → “質問”なのか“行動”なのか分からなくなる🌀

✅ 対策：

* Specification = 真/偽（質問）
* Policy = 行動方針（決める）

### ❌ ifの塊をPolicyに移しただけ

* 「Policyにしたけど中身がifだらけ」😵‍💫
  ✅ 対策：条件はSpecificationに寄せて、Policyは読み物にする📘✨

---

## 9) AIの使いどころ（超効く）🤖💞

### 🪄 Policy候補を洗い出すプロンプト

* 「カフェ注文ドメインで “条件→行動” になっている運用ルールを10個出して。条件と行動を分けて書いて」

### 🪄 Decision設計を整えるプロンプト

* 「このPolicyが返すDecisionの型を、将来の追加に強い形にしたい。union型の案を3つ出して、メリデメも書いて」

### 🪄 テスト抜けを見つけるプロンプト

* 「このPolicyのテスト観点を網羅して。正常系/境界値/例外系/将来の追加に弱い点も含めて」

---

## 10) ミニ演習（やると一気に強くなる）🎮✨

### 演習A：方針を1個追加してみよ🧠➡️🏃‍♀️

* 「雨の日（RainyDaySpec）ならホットドリンクをおすすめ通知する」☔☕
  → Policyは通知“計画”を返すだけにしてね✨

### 演習B：Policyを2段にしてみよ🪜

* 「複数キャンペーンがあるとき、どれを優先する？」
  → PromotionPolicyを “合成” できる形にしてみる（Decisionをマージ）🧩

---

## 11) まとめ 🎀✨

* Specificationは「条件（質問）」🔎
* Policyは「条件→行動（方針）」🧠➡️🏃‍♀️
* Policyは **副作用を直接やらず**、Decision（やること）を返すと超キレイ💎
* DDDでもPolicyはルールを明示的に分離するために使われ、Strategy的な考え方で語られるよ📘✨ ([fabiofumarola.github.io][2])

---

## 次章へのつなぎ ⏰🧪✨

次の第86章は **時間（今）をテスト可能にするClock注入**だよ〜！
Policyって「期限」「曜日」「時間帯」と相性が良すぎるから、ここが揃うと一気に実務っぽくなる💘🔥

必要なら、この章の例をそのまま **Clock対応版**に進化させた形もセットで作れるよ〜！🥳💞

[1]: https://en.wikipedia.org/wiki/Specification_pattern?utm_source=chatgpt.com "Specification pattern"
[2]: https://fabiofumarola.github.io/nosql/readingMaterial/Evans03.pdf "Microsoft Word _ Book_AfterFinal_doc"
[3]: https://www.npmjs.com/package/vitest?utm_source=chatgpt.com "vitest"
[4]: https://www.npmjs.com/package/typescript?utm_source=chatgpt.com "typescript"
