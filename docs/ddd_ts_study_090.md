# 第90章：まとめ演習：割引＋期限＋エラーを統合🎓✨

![まとめ演習：割引＋期限＋エラーの統合](./picture/ddd_ts_study_090_integration_curry.png)

この章は「むずかしいやつ全部のせ🍛」です！
**Specification（条件）＋ Clock（時間）＋ エラー（例外/Result）**を、1本のユースケースに“きれいに”通します💪✨
（この章をクリアできると、次の **Domain Event** がめちゃスムーズになります⚡）

---

## 0) まずは“今日の最新メモ”だけ押さえよ〜🧠🆕

* **TypeScript の最新は 5.9 系**（`import defer` などが入ってます）📦✨ ([typescriptlang.org][1])
* **Node は TypeScript を「型を剥がして」そのまま実行できる案内が公式にあります**（いわゆる type stripping）🏃‍♀️💨 ([nodejs.org][2])
* **Vitest は 4.x が安定運用ラインで、4.1 以降は “tags” でテストにタグ付けできる**のが便利です🏷️🧪 ([main.vitest.dev][3])
* **Node v24 は Active LTS**（今どき開発の安定ラインとして選ばれやすい）🧱✨ ([nodejs.org][4])

---

## 1) お題（例題）☕🧾：カフェの「学生＆平日＆期限つき割引」🎟️

### 🎯 やりたい仕様（ざっくり）

* 「学生」なら **10% OFF** 🎓💖
* ただし「平日」だけ📅✨
* さらに「キャンペーン期間内」だけ⏰🔥
* 条件を満たさないなら、**ユーザー向けメッセージ**を返したい👤
* そして運用のために **ログ用の情報**も欲しい🛠️

---

## 2) 受け入れ条件（Given/When/Then）✅🧪

### ✅ 成功パターン

* **Given** 学生で、平日で、キャンペーン期間内
* **When** 割引適用を実行
* **Then** 注文合計に 10% 割引が入る 🎉

### ❌ 失敗パターン（例）

* **Given** 学生だけど土日

  * **Then** 「平日は学生割が使えません」みたいな表示メッセージ
* **Given** 学生で平日だけど期限切れ

  * **Then** 「キャンペーンは終了しました」
* **Given** 注文が存在しない

  * **Then** 「注文が見つかりません」
* **Given** 支払い済み（割引後に変更禁止）

  * **Then** 「支払い後は割引を変更できません」

---

## 3) 設計の“勝ち筋”🌈✨（この章の狙い）

ここが超大事💡

* **Specification**：条件は “if” に散らさず、**読める部品**にする🔎📄
* **Clock 注入**：`Date.now()` を直で呼ばず、**テストできる「今」**を渡す⏰🧪
* **エラー**：

  * ドメイン内部は **ドメイン例外**で「仕様違反」を表す🧯
  * 外へ返すのは **Result** で「表示メッセージ＋ログ用情報」を整える📦👤🛠️

---

## 4) 今回作るもの（完成形イメージ）🧩✨

* `Specification<T>`（AND/OR/NOT 合成つき）🧷
* `Clock`（SystemClock / FakeClock）⏰
* `DiscountCampaign`（期間・割引率・適用条件）🎟️
* `ApplyDiscountToOrder` ユースケース（統合ポイント）🎬
* Result 型（成功/失敗を型で表現）📦
* Vitest のテスト（できれば tags も）🏷️🧪

---

## 5) 実装：まずは Result とエラー土台📦🧯

### 5-1) Result 型（アプリ層で使う）

```ts
// app/shared/result.ts
export type Result<T, E> =
  | { ok: true; value: T }
  | { ok: false; error: E };

export const ok = <T>(value: T): Result<T, never> => ({ ok: true, value });
export const err = <E>(error: E): Result<never, E> => ({ ok: false, error });
```

### 5-2) 外に返すエラー（ユーザー向け＋ログ向け）

```ts
// app/shared/appError.ts
export type AppError = {
  code:
    | "ORDER_NOT_FOUND"
    | "DISCOUNT_NOT_ELIGIBLE"
    | "DISCOUNT_EXPIRED"
    | "ORDER_ALREADY_PAID"
    | "UNKNOWN";
  userMessage: string; // 画面に出す
  logMessage: string;  // ログに出す
  details?: Record<string, unknown>; // 調査用メタ
};
```

### 5-3) ドメイン例外（仕様違反）

```ts
// domain/errors/domainError.ts
export abstract class DomainError extends Error {
  abstract readonly kind: string;
}

export class DiscountNotEligibleError extends DomainError {
  readonly kind = "DiscountNotEligible";
}

export class DiscountExpiredError extends DomainError {
  readonly kind = "DiscountExpired";
}

export class OrderAlreadyPaidError extends DomainError {
  readonly kind = "OrderAlreadyPaid";
}
```

---

## 6) 実装：Clock（時間の注入）⏰🧪

```ts
// domain/time/clock.ts
export interface Clock {
  now(): Date;
}

export class SystemClock implements Clock {
  now(): Date {
    return new Date();
  }
}
```

テスト用の FakeClock：

```ts
// test/fakes/fakeClock.ts
import type { Clock } from "../../domain/time/clock";

export class FakeClock implements Clock {
  constructor(private current: Date) {}
  now(): Date {
    return this.current;
  }
  set(d: Date) {
    this.current = d;
  }
}
```

---

## 7) 実装：Specification（条件を部品化）🔎📄🧷

### 7-1) まずインターフェイス＋合成

```ts
// domain/spec/specification.ts
export interface Specification<T> {
  isSatisfiedBy(candidate: T): boolean;

  and(other: Specification<T>): Specification<T>;
  or(other: Specification<T>): Specification<T>;
  not(): Specification<T>;
}

export abstract class BaseSpec<T> implements Specification<T> {
  abstract isSatisfiedBy(candidate: T): boolean;

  and(other: Specification<T>): Specification<T> {
    return new AndSpec(this, other);
  }
  or(other: Specification<T>): Specification<T> {
    return new OrSpec(this, other);
  }
  not(): Specification<T> {
    return new NotSpec(this);
  }
}

class AndSpec<T> extends BaseSpec<T> {
  constructor(private a: Specification<T>, private b: Specification<T>) { super(); }
  isSatisfiedBy(candidate: T): boolean {
    return this.a.isSatisfiedBy(candidate) && this.b.isSatisfiedBy(candidate);
  }
}

class OrSpec<T> extends BaseSpec<T> {
  constructor(private a: Specification<T>, private b: Specification<T>) { super(); }
  isSatisfiedBy(candidate: T): boolean {
    return this.a.isSatisfiedBy(candidate) || this.b.isSatisfiedBy(candidate);
  }
}

class NotSpec<T> extends BaseSpec<T> {
  constructor(private a: Specification<T>) { super(); }
  isSatisfiedBy(candidate: T): boolean {
    return !this.a.isSatisfiedBy(candidate);
  }
}
```

### 7-2) 今回の判定コンテキスト

```ts
// domain/discount/discountContext.ts
export type CustomerType = "student" | "regular";

export type DiscountContext = {
  customerType: CustomerType;
  now: Date;
};
```

### 7-3) 「学生か？」Spec 🎓

```ts
// domain/discount/specs/isStudentSpec.ts
import { BaseSpec } from "../../spec/specification";
import type { DiscountContext } from "../discountContext";

export class IsStudentSpec extends BaseSpec<DiscountContext> {
  isSatisfiedBy(candidate: DiscountContext): boolean {
    return candidate.customerType === "student";
  }
}
```

### 7-4) 「平日か？」Spec 📅

```ts
// domain/discount/specs/isWeekdaySpec.ts
import { BaseSpec } from "../../spec/specification";
import type { DiscountContext } from "../discountContext";

export class IsWeekdaySpec extends BaseSpec<DiscountContext> {
  isSatisfiedBy(candidate: DiscountContext): boolean {
    const day = candidate.now.getDay(); // 0=Sun ... 6=Sat
    return day >= 1 && day <= 5;
  }
}
```

### 7-5) 「期間内か？」は、Specより先に VO っぽくまとめる⏳✨

```ts
// domain/time/dateRange.ts
import { DomainError } from "../errors/domainError";

export class InvalidDateRangeError extends DomainError {
  readonly kind = "InvalidDateRange";
}

export class DateRange {
  private constructor(
    private readonly start: Date,
    private readonly end: Date
  ) {}

  static create(start: Date, end: Date): DateRange {
    if (start.getTime() > end.getTime()) throw new InvalidDateRangeError();
    return new DateRange(start, end);
  }

  contains(d: Date): boolean {
    const t = d.getTime();
    return this.start.getTime() <= t && t <= this.end.getTime();
  }
}
```

---

## 8) 実装：割引キャンペーン（期間＋条件＋エラー）🎟️🧯

割引は「条件に合えば計算する」だけじゃなくて、**合わない理由**も分かりたいよね👀
今回は **期限切れ**と **条件不一致**を別エラーにするよ✌️

```ts
// domain/discount/discountCampaign.ts
import type { Specification } from "../spec/specification";
import type { DiscountContext } from "./discountContext";
import { DateRange } from "../time/dateRange";
import { DiscountExpiredError, DiscountNotEligibleError } from "../errors/domainError";

export class DiscountCampaign {
  constructor(
    private readonly name: string,
    private readonly period: DateRange,
    private readonly percent: number, // 10 = 10%
    private readonly eligibility: Specification<DiscountContext>
  ) {}

  assertApplicable(ctx: DiscountContext): void {
    if (!this.period.contains(ctx.now)) {
      throw new DiscountExpiredError(`${this.name} is expired`);
    }
    if (!this.eligibility.isSatisfiedBy(ctx)) {
      throw new DiscountNotEligibleError(`${this.name} is not eligible`);
    }
  }

  discountAmount(base: number): number {
    // 金額は本来 Money VO が理想だけど、ここは統合が主役なので最小で！
    return Math.floor((base * this.percent) / 100);
  }
}
```

---

## 9) 実装：注文（超ミニ版）🧾🛡️

「支払い済みなら割引変更できない」っていう **不変条件**を入れるよ🔒

```ts
// domain/order/order.ts
import { OrderAlreadyPaidError } from "../errors/domainError";

export type OrderStatus = "draft" | "paid";

export class Order {
  private discount = 0;

  constructor(
    readonly id: string,
    private total: number,
    private status: OrderStatus
  ) {}

  getTotal(): number {
    return this.total - this.discount;
  }

  getBaseTotal(): number {
    return this.total;
  }

  applyDiscount(amount: number): void {
    if (this.status === "paid") throw new OrderAlreadyPaidError("already paid");
    if (amount < 0) throw new Error("discount must be >= 0");
    if (amount > this.total) throw new Error("discount too large");
    this.discount = amount;
  }
}
```

---

## 10) 統合ポイント：ユースケースで全部つなぐ🎬✨（第90章の主役）

Repository は前に作った想定で、ここは **最小の interface** にするね📚

```ts
// domain/order/orderRepository.ts
import type { Order } from "./order";

export interface OrderRepository {
  findById(id: string): Promise<Order | null>;
  save(order: Order): Promise<void>;
}
```

ユースケース本体（例外 → AppError にマッピング）：

```ts
// app/usecases/applyDiscountToOrder.ts
import type { OrderRepository } from "../../domain/order/orderRepository";
import type { Clock } from "../../domain/time/clock";
import type { DiscountCampaign } from "../../domain/discount/discountCampaign";
import { ok, err, type Result } from "../shared/result";
import type { AppError } from "../shared/appError";
import type { CustomerType } from "../../domain/discount/discountContext";
import {
  DiscountExpiredError,
  DiscountNotEligibleError,
  OrderAlreadyPaidError,
  DomainError,
} from "../../domain/errors/domainError";

export class ApplyDiscountToOrder {
  constructor(
    private readonly repo: OrderRepository,
    private readonly clock: Clock,
    private readonly campaign: DiscountCampaign
  ) {}

  async execute(input: {
    orderId: string;
    customerType: CustomerType;
  }): Promise<Result<{ total: number }, AppError>> {
    const order = await this.repo.findById(input.orderId);
    if (!order) {
      return err({
        code: "ORDER_NOT_FOUND",
        userMessage: "注文が見つかりませんでした🥲",
        logMessage: "order not found",
        details: { orderId: input.orderId },
      });
    }

    try {
      const ctx = { customerType: input.customerType, now: this.clock.now() };

      this.campaign.assertApplicable(ctx);

      const discount = this.campaign.discountAmount(order.getBaseTotal());
      order.applyDiscount(discount);

      await this.repo.save(order);

      return ok({ total: order.getTotal() });
    } catch (e) {
      return err(this.mapError(e, input.orderId));
    }
  }

  private mapError(e: unknown, orderId: string): AppError {
    if (e instanceof DiscountExpiredError) {
      return {
        code: "DISCOUNT_EXPIRED",
        userMessage: "キャンペーン期間が終了しています⏰💦",
        logMessage: "discount expired",
        details: { orderId },
      };
    }
    if (e instanceof DiscountNotEligibleError) {
      return {
        code: "DISCOUNT_NOT_ELIGIBLE",
        userMessage: "この条件では割引が使えませんでした🙇‍♀️",
        logMessage: "discount not eligible",
        details: { orderId },
      };
    }
    if (e instanceof OrderAlreadyPaidError) {
      return {
        code: "ORDER_ALREADY_PAID",
        userMessage: "支払い後は割引を変更できません💳🚫",
        logMessage: "order already paid",
        details: { orderId },
      };
    }
    if (e instanceof DomainError) {
      return {
        code: "UNKNOWN",
        userMessage: "処理に失敗しました🥲",
        logMessage: `unknown domain error: ${e.kind}`,
        details: { orderId },
      };
    }
    return {
      code: "UNKNOWN",
      userMessage: "処理に失敗しました🥲",
      logMessage: "unknown error",
      details: { orderId },
    };
  }
}
```

---

## 11) 組み立て：キャンペーン条件を“文章みたいに”読む🧷📖✨

「学生 AND 平日」って読みたいよね🥰

```ts
// composition example (どこかの組み立て場所で)
import { DiscountCampaign } from "./domain/discount/discountCampaign";
import { DateRange } from "./domain/time/dateRange";
import { IsStudentSpec } from "./domain/discount/specs/isStudentSpec";
import { IsWeekdaySpec } from "./domain/discount/specs/isWeekdaySpec";

const eligibility = new IsStudentSpec().and(new IsWeekdaySpec());

const period = DateRange.create(
  new Date("2026-02-01T00:00:00Z"),
  new Date("2026-02-28T23:59:59Z")
);

export const studentWeekdayCampaign = new DiscountCampaign(
  "Student Weekday 10% OFF",
  period,
  10,
  eligibility
);
```

---

## 12) テスト（Vitest）🧪💕：FakeClock で期限を操る⏰✨

### 12-1) キャンペーン期限切れのテスト

```ts
import { describe, it, expect } from "vitest";
import { DateRange } from "../domain/time/dateRange";
import { DiscountCampaign } from "../domain/discount/discountCampaign";
import { IsStudentSpec } from "../domain/discount/specs/isStudentSpec";
import { IsWeekdaySpec } from "../domain/discount/specs/isWeekdaySpec";
import { DiscountExpiredError } from "../domain/errors/domainError";

describe("DiscountCampaign", () => {
  it("期限外なら DiscountExpiredError", () => {
    const eligibility = new IsStudentSpec().and(new IsWeekdaySpec());
    const period = DateRange.create(
      new Date("2026-02-01T00:00:00Z"),
      new Date("2026-02-10T00:00:00Z")
    );

    const campaign = new DiscountCampaign("camp", period, 10, eligibility);

    expect(() =>
      campaign.assertApplicable({
        customerType: "student",
        now: new Date("2026-02-20T00:00:00Z"),
      })
    ).toThrow(DiscountExpiredError);
  });
});
```

### 12-2) “tags”でテストを分類（使えたら便利）🏷️🧪

Vitest の tags は 4.1+ でドキュメントにあります🏷️✨ ([main.vitest.dev][3])

```ts
import { describe, it, expect } from "vitest";

describe("UseCase", () => {
  it(
    "学生&平日&期限内なら割引適用",
    { tags: ["happy-path"] },
    async () => {
      expect(true).toBe(true);
    }
  );
});
```

---

## 13) よくある事故ポイント（ここで潰す！）😂🧯

![設計のアンチパターン](./picture/ddd_ts_study_090_anti_patterns.png)

* `Date.now()` をドメインのあちこちで呼んで、**テスト不能**になる⛔
* 期限判定が `>=` / `>` でブレて、**境界の日に事故る**📅💥
* 条件が増えて `if (A && (B || C) && !D ...` になり、**読めない**😵‍💫
* エラーを全部 “例外メッセージ” で返して、**ユーザー表示が荒れる**🥲
* 「期限切れ」と「条件不一致」が同じ扱いで、**問い合わせ対応が地獄**📞🔥

→ だから **Spec / Clock / Result** の出番です✨

---

## 14) AIの使いどころ（この章向け）🤖💡

コツは「骨格だけ作らせて、ルールは自分で握る」だよ✊✨

### 🧠 使えるプロンプト例

* 「DiscountCampaign のテスト観点を **境界値込みで** 10個出して。Given/When/Thenで」
* 「`mapError()` の分岐が漏れてないかレビューして。不足があれば指摘して」
* 「Specification の命名を “文章として読める” 形にリネーム案ちょうだい」
* 「このユースケースのログ `details` に入れるべき項目を提案して（個人情報は避けて）」

---

## 15) ふりかえりチェック✅✨（合格ライン）

* [ ] 条件が if じゃなく **Spec の合成**で読める🧷
* [ ] テストで「期限内/期限外」を **FakeClock で一撃**できる⏰
* [ ] 失敗が Result で返って、**ユーザー向け文言とログ情報が分離**されてる👤🛠️
* [ ] 「期限切れ」と「条件不一致」が別扱いになってる🎯

---

## 16) 次（第91章）につながる“伏線”⚡📮

この章で「割引適用できた！」ってなったら、次はこうしたくなるはず👇

* 割引適用を **出来事（Domain Event）** にして
* 「通知」「レシート」「分析」みたいな副作用を **疎結合**にしたい✨

つまり… **第91章のDomain Eventが気持ちよく入ってきます**🥰⚡

---

必要なら、この第90章を「実際に動く最小プロジェクト構成（ファイル一覧＋package scripts＋テスト実行コマンド）」まで“教材用テンプレ”として整えた版も出せるよ📦✨

[1]: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-9.html?utm_source=chatgpt.com "Documentation - TypeScript 5.9"
[2]: https://nodejs.org/en/learn/typescript/run-natively?utm_source=chatgpt.com "Running TypeScript Natively"
[3]: https://main.vitest.dev/api/test?utm_source=chatgpt.com "Vitest"
[4]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
