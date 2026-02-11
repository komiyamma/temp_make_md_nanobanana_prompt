# 第84章：Specification実装②：合成（AND/OR）🧷

この章は「条件を“文章みたいに読める形”にする」回だよ〜！🫶
前章で作った **単体Specification** を、**AND / OR** で組み合わせて「ルールの組み立て」をできるようにします🎀

---

## 1️⃣ まずは“if地獄”を見てみよ…👀💥

条件が増えると、こうなること多いよね😵‍💫

```ts
// ❌ 条件が増えるほど読みにくくなる例
function canApplyStudentWeekdayDiscount(order: Order): boolean {
  if (!order.customer.isStudent) return false
  if (order.status !== 'PAID') return false
  const day = order.orderedAt.getDay() // 0=日, 1=月...
  if (day === 0 || day === 6) return false // 土日NG
  if (order.totalYen < 500) return false
  return true
}
```

これを **Specification合成** にすると、こう読めるようになるよ〜😍

```ts
const eligible =
  new IsStudentCustomerSpec()
    .and(new IsPaidOrderSpec())
    .and(new IsWeekdayOrderSpec())
    .and(new TotalAtLeastYenSpec(500))

eligible.isSatisfiedBy(order) // ✅ 条件が文章みたい
```

**「仕様（条件）の意味」がコードに残る**のが最高ポイント✨

---

## 2️⃣ Specification合成ってなに？🧩

Specificationは「ある条件を満たす？」を判定するオブジェクト。
そして **合成** は、それらを **木（ツリー）みたいに繋げる**感じ🌳

* `A AND B`：AもBも満たす
* `A OR B`：AかBどっちか満たす
* `NOT A`：Aじゃない

この「Composite Specification（合成仕様）」の考え方自体が、古典DDDの文脈でも整理されてるよ📚✨ ([martinfowler.com][1])

---

## 3️⃣ 実装しよう：合成できるSpecification基盤🛠️✨

ここは **“一回作ったら使い回し”** の土台だよ！💪
（この章のメイン🎉）

### ✅ 3-1. インターフェース（最小ルール）

```ts
export interface Specification<T> {
  isSatisfiedBy(candidate: T): boolean
}
```

### ✅ 3-2. 合成できるabstract class（便利メソッドつき）💎

TypeScriptだと **abstract classに “and/or” を持たせる**のが分かりやすいよ〜😊

```ts
export abstract class Spec<T> implements Specification<T> {
  abstract isSatisfiedBy(candidate: T): boolean

  and(other: Specification<T>): Specification<T> {
    return new AndSpec(this, other)
  }

  or(other: Specification<T>): Specification<T> {
    return new OrSpec(this, other)
  }

  not(): Specification<T> {
    return new NotSpec(this)
  }
}
```

### ✅ 3-3. AND / OR / NOT の合成クラス🧷

ポイントは **短絡評価（ショートサーキット）**！
`&&` と `||` を使えば「左で決まったら右を評価しない」挙動が自然に出るよ👌

```ts
import type { Specification } from './Specification'

export class AndSpec<T> implements Specification<T> {
  constructor(
    private readonly left: Specification<T>,
    private readonly right: Specification<T>,
  ) {}

  isSatisfiedBy(candidate: T): boolean {
    return this.left.isSatisfiedBy(candidate) && this.right.isSatisfiedBy(candidate)
  }
}

export class OrSpec<T> implements Specification<T> {
  constructor(
    private readonly left: Specification<T>,
    private readonly right: Specification<T>,
  ) {}

  isSatisfiedBy(candidate: T): boolean {
    return this.left.isSatisfiedBy(candidate) || this.right.isSatisfiedBy(candidate)
  }
}

export class NotSpec<T> implements Specification<T> {
  constructor(private readonly inner: Specification<T>) {}

  isSatisfiedBy(candidate: T): boolean {
    return !this.inner.isSatisfiedBy(candidate)
  }
}
```

---

## 4️⃣ 例題：学生割（平日限定）をSpecificationで組む☕🎓📅

### ✅ 4-1. 例のモデル（最低限）

```ts
export type OrderStatus = 'DRAFT' | 'CONFIRMED' | 'PAID' | 'CANCELLED'

export type Customer = {
  isStudent: boolean
}

export type Order = {
  status: OrderStatus
  customer: Customer
  orderedAt: Date
  totalYen: number
}
```

### ✅ 4-2. 単体Specificationを作る🧩

```ts
import { Spec } from './Spec'
import type { Order } from './Order'

export class IsStudentCustomerSpec extends Spec<Order> {
  isSatisfiedBy(order: Order): boolean {
    return order.customer.isStudent
  }
}

export class IsPaidOrderSpec extends Spec<Order> {
  isSatisfiedBy(order: Order): boolean {
    return order.status === 'PAID'
  }
}

export class IsWeekdayOrderSpec extends Spec<Order> {
  isSatisfiedBy(order: Order): boolean {
    const day = order.orderedAt.getDay() // 0=日,6=土
    return day !== 0 && day !== 6
  }
}

export class TotalAtLeastYenSpec extends Spec<Order> {
  constructor(private readonly minYen: number) {
    super()
  }
  isSatisfiedBy(order: Order): boolean {
    return order.totalYen >= this.minYen
  }
}
```

### ✅ 4-3. 合成して“文章”にする💖

```ts
const eligibleForStudentWeekdayDiscount =
  new IsStudentCustomerSpec()
    .and(new IsPaidOrderSpec())
    .and(new IsWeekdayOrderSpec())
    .and(new TotalAtLeastYenSpec(500))

eligibleForStudentWeekdayDiscount.isSatisfiedBy(order)
```

こうなると「条件の読みやすさ」が爆上がりするよ〜🥹✨

---

## 5️⃣ テストで“合成が正しい”を守る🧪🛡️

ここは **Vitest** を例にするね！（TypeScript/ESMを“素で”扱いやすいのが嬉しい✨） ([vitest.dev][2])
`expect` 周りもJest互換の書き味が用意されてるよ🙆‍♀️ ([vitest.dev][3])

### ✅ 5-1. ANDが両方trueのときだけtrue

```ts
import { describe, it, expect } from 'vitest'
import { AndSpec } from './AndSpec'
import type { Specification } from './Specification'

class AlwaysTrue implements Specification<number> {
  isSatisfiedBy(): boolean { return true }
}
class AlwaysFalse implements Specification<number> {
  isSatisfiedBy(): boolean { return false }
}

describe('AndSpec', () => {
  it('true AND true -> true', () => {
    const spec = new AndSpec(new AlwaysTrue(), new AlwaysTrue())
    expect(spec.isSatisfiedBy(1)).toBe(true)
  })

  it('true AND false -> false', () => {
    const spec = new AndSpec(new AlwaysTrue(), new AlwaysFalse())
    expect(spec.isSatisfiedBy(1)).toBe(false)
  })
})
```

### ✅ 5-2. ORはどっちかtrueならtrue

```ts
import { describe, it, expect } from 'vitest'
import { OrSpec } from './OrSpec'

describe('OrSpec', () => {
  it('false OR true -> true', () => {
    const spec = new OrSpec(
      { isSatisfiedBy: () => false },
      { isSatisfiedBy: () => true },
    )
    expect(spec.isSatisfiedBy(1)).toBe(true)
  })
})
```

---

## 6️⃣ 命名のコツ：読める名前がいちばん大事🧠💗

合成すると“文章”になるから、単体Specはこういう感じが気持ちいいよ👇

* `IsPaidOrderSpec` ✅（「支払い済み？」）
* `IsWeekdayOrderSpec` ✅（「平日？」）
* `HasCouponSpec` ✅（「クーポン持ってる？」）

逆に、こういうのは避けたい😵‍💫

* `Check1Spec` ❌（意味が分からん）
* `OrderSpec2` ❌（増殖して地獄）

---

## 7️⃣ よくある落とし穴😂⚠️

### ❌ 7-1. Specificationの中でDBを読みに行く

Specificationは **“純粋に判定するだけ”** に寄せるのが基本💡
（I/Oが入ると、テストが急に難しくなるよ〜😭）

### ❌ 7-2. “今”に依存しすぎる（Date.now直呼び）

この後の章で **Clock注入** をやるから、今は「orderedAtみたいな値から判断」くらいが安全🙆‍♀️

---

## 8️⃣ AI（Copilot/Codex）に頼むと強いところ🤖✨

ここはAIが得意！💕

### 🧠 命名案を出させるプロンプト例

* 「`A AND B` を表すSpec名を、短くて自然な英語で10個ください。対象は “学生割引（平日限定・支払い済み・500円以上）”。」

### 🔍 テスト観点を増やすプロンプト例

* 「AndSpec/OrSpec のテストで“やりがちなバグ”を列挙して、追加すべきテストケースを提案して」

---

## 9️⃣ ミニ演習（やってみよ〜！）🎮💪

### 演習A：ORの実務っぽい例🍰

「**新規会員 OR 誕生日の人** はケーキ無料🎂」みたいなのを作ってみて！

* `IsNewMemberSpec`
* `IsBirthdaySpec`
* `eligibleForFreeCake = new IsNewMemberSpec().or(new IsBirthdaySpec())`

### 演習B：NOTも混ぜる😈

「**平日 AND NOT 雨** ならテラス席OK☀️」
→ `IsWeekdaySpec().and(IsRainySpec().not())`

---

## 🔚 まとめ（この章のゴール達成！）🎉✨

* Specificationを **AND/ORで合成** できるようになった🧷
* 条件が **コードの文章として読める** ようになった📖💗
* if地獄から「ルールの組み立て」へ進化した🚀

次の第85章は **Policy（条件→行動）** で、「満たしたら何する？」の世界に進むよ〜🧠➡️🏃‍♀️✨

---

## 🧩 おまけ：最近のTypeScriptまわり小ネタ（2026視点）🍬

* TypeScript 5.9では `--module node20` みたいに “Node v20の挙動をモデル化した安定オプション” が用意されてたりするよ🧡（モジュール設定が迷子になりにくい！） ([Microsoft for Developers][4])
* さらに先の話として、TypeScript 6.0は“橋渡し”、TypeScript 7系はネイティブ実装のプレビューが進んでて高速化が強く意識されてるよ⚡（大規模でも気持ちよくしたい流れ✨） ([Microsoft for Developers][5])

[1]: https://martinfowler.com/apsupp/spec.pdf "Specification"
[2]: https://vitest.dev/guide/features?utm_source=chatgpt.com "Features | Guide"
[3]: https://vitest.dev/api/expect?utm_source=chatgpt.com "Expect"
[4]: https://devblogs.microsoft.com/typescript/announcing-typescript-5-9/ "Announcing TypeScript 5.9 - TypeScript"
[5]: https://devblogs.microsoft.com/typescript/progress-on-typescript-7-december-2025/ "Progress on TypeScript 7 - December 2025 - TypeScript"
