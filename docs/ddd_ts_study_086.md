# 第86章：時間の設計：Clock注入⏰🧪

時間って、コードの中では **めちゃ地雷** です💣😵‍💫
とくに「締切」「有効期限」「キャンセル可能時間」「〇分以内」みたいな仕様が入った瞬間、**Date.now() 直呼び**がじわじわ効いてきます…🥲

この章は、その地雷を踏まないための **Clock注入（クロックちゅうにゅう）** を、カフェ注文ドメインで手を動かしながら身につける回だよ☕🧡

---

## 1) まず結論：時間は「依存」だよ⏳➡️🔌

![1) まず結論：時間は「依存」だよ⏳➡️🔌](./picture/ddd_ts_study_086_visual_1.png)


**「今（now）」は値じゃなくて、外から来る依存**だと思うとラクになるよ✨
だから…

* ❌ `Date.now()` をドメインで直に呼ぶ
* ✅ `clock.now()` を呼ぶ（Clockを注入する）

に変えるだけで、テストが急に平和になります🕊️🌸

---

## 2) なぜ `Date.now()` 直呼びがダメになりやすいの？😵‍💫

### 事故① テストが不安定（たまに落ちる）🎲

「1msズレただけ」で境界テストがコケたりするの、あるある🥺

### 事故② “境界”が鬼門（10分以内って、ちょうど10分はOK？）⏱️😈

![事故② “境界”が鬼門（10分以内って、ちょうど10分はOK？）⏱️😈](./picture/ddd_ts_study_086_visual_2.png)


仕様の日本語が曖昧だと、実装もテストもブレるよね💦
なので、**境界をコードで固定**していく必要があるよ✅

### 事故③ タイムゾーン・DST（夏時間）で爆発💥🌍

時間は「世界」を持ってるので、雑に扱うといつか爆発する…
（この章はまず「今」を固定するのが主役！でも後半で注意点もまとめるよ😊）

---

## 3) 今日のゴール🎯✨

* 「ドメインの中から `Date.now()` を追放」できる🏃‍♀️💨
* 期限判定や“〇分以内”を **テストで100%再現**できる🧪✅
* ついでに「時間系の設計の型」を覚える📦

---

## 4) Clock注入の“型”🧩🧠

### ✅ 基本形（おすすめ）

![✅ 基本形（おすすめ）](./picture/ddd_ts_study_086_visual_3.png)


* `domain` に `Clock` インターフェースを置く
* `infra` に `SystemClock`（本物の時計）を置く
* `test` に `FixedClock`（止まった時計）を置く

こうすると依存がきれいに守れるよ🏰➡️🧱

---

## 5) 例題：注文は「10分以内ならキャンセルOK」☕🧾⏰

仕様をこう決めちゃおう👇（曖昧さを潰すの大事！）

* **「10分以内」＝ 作成時刻 + 10分 まではOK**
* **それより後（>）はNG**

つまり、`now > createdAt + 10min` なら失敗💥
（`now === limit` はOK✨）

---

## 6) 実装してみよう（Clock注入フルセット）🧑‍💻💖

### 6.1 domain：Clock と “時刻VO” を用意する⏰📦

ポイント：この章では **UTCの瞬間（epoch ms）** として扱うとラクだよ🙂
「表示」や「ローカル時刻」は外側でやる感じ！

```ts
// src/domain/time/Clock.ts
export interface Clock {
  now(): UtcInstant;
}

// src/domain/time/UtcInstant.ts
export class UtcInstant {
  private constructor(public readonly epochMs: number) {}

  static fromEpochMs(epochMs: number): UtcInstant {
    if (!Number.isFinite(epochMs)) throw new Error("epochMs must be a finite number");
    return new UtcInstant(epochMs);
  }

  addMinutes(minutes: number): UtcInstant {
    if (!Number.isFinite(minutes)) throw new Error("minutes must be finite");
    return UtcInstant.fromEpochMs(this.epochMs + minutes * 60_000);
  }

  isAfter(other: UtcInstant): boolean {
    return this.epochMs > other.epochMs;
  }
}
```

---

### 6.2 domain：キャンセル失敗を表す軽い例外🧯（次章の布石）

![6.2 domain：キャンセル失敗を表す軽い例外🧯（次章の布石）](./picture/ddd_ts_study_086_visual_4.png)


次の第87章で「例外作法」をガッツリやるけど、ここでは最小でOK✨

```ts
// src/domain/errors/DomainRuleError.ts
export class DomainRuleError extends Error {
  constructor(
    public readonly code: string,
    message: string,
  ) {
    super(message);
    this.name = "DomainRuleError";
  }
}
```

---

### 6.3 domain：Order に「キャンセル」ルールを閉じ込める🛡️

```ts
// src/domain/order/Order.ts
import { Clock } from "../time/Clock";
import { UtcInstant } from "../time/UtcInstant";
import { DomainRuleError } from "../errors/DomainRuleError";

export type OrderStatus = "Draft" | "Confirmed" | "Paid" | "Canceled";

export class Order {
  private status: OrderStatus;

  private constructor(
    public readonly id: string,
    private readonly createdAt: UtcInstant,
    status: OrderStatus,
  ) {
    this.status = status;
  }

  static create(id: string, clock: Clock): Order {
    return new Order(id, clock.now(), "Draft");
  }

  getStatus(): OrderStatus {
    return this.status;
  }

  cancel(clock: Clock): void {
    if (this.status === "Paid") {
      throw new DomainRuleError("ORDER_CANNOT_CANCEL_PAID", "支払い済みの注文はキャンセルできません🥲");
    }
    if (this.status === "Canceled") {
      throw new DomainRuleError("ORDER_ALREADY_CANCELED", "すでにキャンセル済みです🙇‍♀️");
    }

    const limit = this.createdAt.addMinutes(10);
    const now = clock.now();

    // 「10分以内」＝ limit まではOK、超えたらNG
    if (now.isAfter(limit)) {
      throw new DomainRuleError("ORDER_CANCEL_WINDOW_EXPIRED", "キャンセル期限（10分）を過ぎました⏰💦");
    }

    this.status = "Canceled";
  }
}
```

ここがめちゃ重要👇✨
**「時間に依存するルール」でも Order が自分で守ってる**🛡️
アプリ層が if で頑張らないのがDDDっぽい💖

---

### 6.4 infra：SystemClock（本物の時計）🕰️

```ts
// src/infra/time/SystemClock.ts
import { Clock } from "../../domain/time/Clock";
import { UtcInstant } from "../../domain/time/UtcInstant";

export class SystemClock implements Clock {
  now(): UtcInstant {
    return UtcInstant.fromEpochMs(Date.now());
  }
}
```

---

### 6.5 test：FixedClock（止まった時計）🧊⏰

![6.5 test：FixedClock（止まった時計）🧊⏰](./picture/ddd_ts_study_086_visual_5.png)


```ts
// src/test/time/FixedClock.ts
import { Clock } from "../../domain/time/Clock";
import { UtcInstant } from "../../domain/time/UtcInstant";

export class FixedClock implements Clock {
  constructor(private current: UtcInstant) {}

  now(): UtcInstant {
    return this.current;
  }

  setNow(next: UtcInstant): void {
    this.current = next;
  }
}
```

---

## 7) テスト（Vitest）で境界までバッチリ🧪💯

Vitest は **Fake Timers** とか **setSystemTime** があるけど、そもそも今回みたいに **Clock注入**してると、グローバルをいじらずに済むのが強みだよ😊
（Vitest側のFake Timers APIは `vi.useFakeTimers()` や `vi.setSystemTime(...)` が用意されてるよ📌）([vitest.dev][1])

```ts
// src/domain/order/Order.test.ts
import { describe, it, expect } from "vitest";
import { Order } from "./Order";
import { FixedClock } from "../../test/time/FixedClock";
import { UtcInstant } from "../time/UtcInstant";
import { DomainRuleError } from "../errors/DomainRuleError";

describe("Order.cancel", () => {
  it("作成から10分以内ならキャンセルできる✅", () => {
    const t0 = UtcInstant.fromEpochMs(1_700_000_000_000); // 適当な固定時刻
    const clock = new FixedClock(t0);

    const order = Order.create("order-1", clock);

    // ちょうど10分後（OK）
    clock.setNow(t0.addMinutes(10));
    order.cancel(clock);

    expect(order.getStatus()).toBe("Canceled");
  });

  it("10分を1msでも超えるとキャンセルできない⛔", () => {
    const t0 = UtcInstant.fromEpochMs(1_700_000_000_000);
    const clock = new FixedClock(t0);

    const order = Order.create("order-1", clock);

    // 10分 + 1ms（NG）
    clock.setNow(UtcInstant.fromEpochMs(t0.epochMs + 10 * 60_000 + 1));

    expect(() => order.cancel(clock)).toThrowError(DomainRuleError);
  });

  it("支払い済みはキャンセル不可💳⛔", () => {
    const t0 = UtcInstant.fromEpochMs(1_700_000_000_000);
    const clock = new FixedClock(t0);

    // ここは簡略化：テスト用に「Paid状態のOrder」を作る方法が必要だけど、
    // 章の主題じゃないので、実プロジェクトなら factory / helper を用意しよう😊
  });
});
```

※最後のテストみたいに「状態を作る」話が出てくるので、後々 **Factory** や **テスト用ビルダー** が効いてくるよ🏭🧪✨

---

## 8) 「Fake Timers」より Clock注入が気持ちいい理由💖

VitestのFake Timersは便利で、`Date.now` や `new Date()` を丸ごと偽装できるよ🪄([vitest.dev][1])
でも、ドメイン設計としてはこうなりがち👇

* Fake Timers：**テストの都合でグローバルを書き換える**（便利だけど依存が隠れる😶‍🌫️）
* Clock注入：**設計として「時間は依存」って表現できる**（読みやすい＆堅い🛡️）

もちろん、UI側で setTimeout をテストしたい等はFake Timersが向いてるよ🙆‍♀️
でも **期限判定・締切・状態遷移**は、Clock注入が相性最高✨

---

## 9) 時刻APIの最新トピック：Temporal ってどうなの？🗓️✨

最近のJavaScriptでは `Date` の置き換えとして **Temporal** が進んでるよ📈
Temporalは「日時の型を分けて、バグを減らす」設計で、TC39側でも思想がはっきりしてる✨([tc39.es][2])

ただし、MDNでは互換性の都合で “Limited availability” になっていて、環境によってはまだ注意が必要だよ⚠️([MDN ウェブドキュメント][3])
（なのでこの教材では、まず **Clock注入で“今”を制御できる**ようにしておくのが超現実的😊）

---

## 10) よくある落とし穴まとめ（ここだけで事故が減る）🧯✨

![10) よくある落とし穴まとめ（ここだけで事故が減る）🧯✨](./picture/ddd_ts_study_086_visual_6.png)


* ✅ **ドメインは「UTCの瞬間（epoch）」で持つ**（表示は外で）
* ❌ `new Date("2026-02-07")` みたいな **文字列パースをドメインで多用しない**（環境差が出やすい）
* ✅ 「10分以内」みたいな仕様は **境界（ちょうどは？）を先に確定**
* ✅ “今”が必要なら `clock.now()` に寄せる

---

## 11) ミニ演習🎓✨（手を動かすと定着するよ🧡）

### 演習A：支払い期限（30分）を入れてみよう💳⏰

* ルール：「作成から30分過ぎた注文は支払い不可」
* `Order.pay(clock)` にガードを追加
* テストは「29:59はOK」「30:00ちょうどOK/NG（決める）」「30:00+1msはNG」まで作る✅

### 演習B：仕様の言葉を揃える🗣️✨

* 「期限」「締切」「猶予」「有効」
  どれも似てるから、**用語辞書**に1行定義を追加してね📘💕

---

## 12) AIに頼むときのコツ（そのままコピペOK）🤖🧡

![12) AIに頼むときのコツ（そのままコピペOK）🤖🧡](./picture/ddd_ts_study_086_visual_7.png)


### 🧩 Clock導入のリファクタ依頼

```text
DDDのdomain層から Date.now() / new Date() の直呼びを無くしたいです。
Clockインターフェースをdomainに置き、infraにSystemClock、testにFixedClockを置く構成で、
「期限判定」を clock.now() で書き直してください。
ただし、domainはinfraに依存しないようにしてください。
```

### 🧪 境界テストを作らせる

```text
「作成から10分以内ならキャンセルOK、超えたらNG」という仕様です。
境界（ちょうど10分はOK）を含めたVitestのテストケースを3〜5個提案してください。
```

---

## まとめ🎉✨

Clock注入は、地味だけどめちゃ強いよ💪🥰
特に **期限・締切・時間窓・状態遷移**があるドメインでは、最初から入れる価値が高い🧡

次の第87章は、今日ちょっと出てきた「ドメイン例外」を **もっと綺麗に整える作法**に入っていくよ🧯📌✨

[1]: https://vitest.dev/api/vi.html "Vi | Vitest"
[2]: https://tc39.es/proposal-temporal/docs/?utm_source=chatgpt.com "Temporal documentation"
[3]: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Temporal?utm_source=chatgpt.com "Temporal - JavaScript - MDN Web Docs - Mozilla"
