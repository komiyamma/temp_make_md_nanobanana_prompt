# 第33章：Money VO：通貨・丸め・ゼロ禁止？💴

この章は「金額」っていう **バグが出やすい地雷原** を、Value Object（VO）で安全に歩けるようにする回だよ〜！🧯✨
カフェ注文ドメインを前提に「Money（お金）」を **型と不変性でガチガチに守る** 練習をするね☺️🧡

---

## 1) なんで「お金」はそんなに危険なの？😵‍💫💸

### ありがちな事故①：小数（浮動小数点）の誤差💥

![ddd_ts_study_033_floating_point](./picture/ddd_ts_study_033_floating_point.png)

JavaScriptのNumberは **2進数の浮動小数点** だから、0.1みたいな値を正確に持てなくて、計算すると端数がズレることがあるの🥲
（「見た目は合ってるのに、内部がちょっと違う」系のやつ）([GitHub][1])

### ありがちな事故②：通貨によって小数桁が違う🌍💱

「ドルは小数2桁」「円は小数0桁」みたいに、通貨ごとに扱いが違うよね。
**ISO 4217** は通貨コード（JPY, USD…）と、通貨の小数桁（minor unit）を扱う考え方があるよ。([ISO][2])

### ありがちな事故③：丸め（四捨五入）のルールが曖昧🌀

「1.235ドルって、1.24ドル？ 1.23ドル？」
どんな丸め（half-up / floor / ceil）かを決めてないと、**仕様がブレて揉める**やつ〜😇

---

## 2) この章のゴール🎯✨

* Money VOを **不変（immutable）** に作る🧊
* 金額は **最小通貨単位の整数** で持つ（円なら “円”、ドルなら “セント”）💡
  実際の決済APIでもこの形を要求することが多いよ（例：Stripeのamountは最小通貨単位の整数）。([Stripe Docs][3])
* **通貨コード** と **小数桁（minor unit）** をセットで扱う🌍
* 丸め・ゼロ・負数の方針を “コードのルール” に落とす🛡️

---

## 3) 設計方針（Money VOの責務）🧠💎

![ddd_ts_study_033_money_structure](./picture/ddd_ts_study_033_money_structure.png)

Money VOが守ることは、ざっくりこの4つ！

1. ✅ **通貨（currency）を必ず持つ**（JPYとUSDを混ぜない）
2. ✅ **最小通貨単位の整数（minor units）** で金額を持つ（誤差を出さない）
3. ✅ **丸めルールを固定**（どの桁で、どう丸める？）
4. ✅ **比較は値の等価性**（currency + amountMinor が同じなら同じ）

---

## 4) 実装してみよう！Money VO（BigInt版）🛠️💴

![ddd_ts_study_033_rounding_modes](./picture/ddd_ts_study_033_rounding_modes.png)

> BigIntは「任意の大きさの整数」を安全に扱える型だよ（Numberの安全範囲を超えても壊れにくい）([developer.mozilla.org][4])
> ※ BigIntは小数を持てないので、**“最小通貨単位の整数”** と相性がいいの🙆‍♀️

````ts
// money.ts

export type CurrencyCode = "JPY" | "USD" | "EUR" | "KWD";

/**
 * 通貨ごとの小数桁（minor unit）を最低限だけ持つ。
 * - JPY: 0（円）
 * - USD/EUR: 2（セント）
 * - KWD: 3（例として）
 *
 * 実務では、対応通貨を増やす or 通貨テーブルで管理することが多いよ🌍
 */
const CURRENCY_META: Record<CurrencyCode, { minorUnit: number }> = {
  JPY: { minorUnit: 0 },
  USD: { minorUnit: 2 },
  EUR: { minorUnit: 2 },
  KWD: { minorUnit: 3 },
};

type RoundingMode = "half-up" | "floor" | "ceil";

function pow10(n: number): bigint {
  let x = 1n;
  for (let i = 0; i < n; i++) x *= 10n;
  return x;
}

function isAllZero(s: string): boolean {
  for (const ch of s) if (ch !== "0") return false;
  return true;
}

/**
 * 文字列の金額（例 "12.34"）を、通貨のminor unitに合わせて amountMinor（bigint）へ変換。
 * - "half-up": 0.5以上は切り上げ（負数はゼロから遠ざかる方向へ）
 * - "floor":   -∞方向へ丸め
 * - "ceil":    +∞方向へ丸め
 */
function parseDecimalToMinor(
  value: string,
  minorUnit: number,
  rounding: RoundingMode,
): bigint {
  const s = value.trim();

  // シンプルに：符号 + 数字 + (小数部) だけ許可
  const m = s.match(/^([+-])?(\d+)(?:\.(\d+))?$/);
  if (!m) throw new Error(`Invalid money string: ${value}`);

  const sign = m[1] === "-" ? -1n : 1n;
  const intPart = m[2];
  const fracPart = m[3] ?? "";

  const absMajor = BigInt(intPart);
  const base = pow10(minorUnit);

  if (minorUnit === 0) {
    // 例: "100" OK / "100.00" も許す（ただし小数部は全部0だけ）
    if (fracPart.length > 0 && !isAllZero(fracPart)) {
      throw new Error(`Currency has no minor units, but got decimals: ${value}`);
    }
    const absMinor = absMajor; // JPYは「円」が最小単位
    return sign * absMinor;
  }

  // 小数部を minorUnit 桁に合わせる（足りない分は0埋め）
  const need = minorUnit;
  const kept = fracPart.slice(0, need).padEnd(need, "0");
  const discarded = fracPart.slice(need);

  let absMinor = absMajor * base + BigInt(kept);

  // 丸めが必要？
  const hasRemainder = discarded.length > 0 && !isAllZero(discarded);

  if (hasRemainder) {
    let inc = 0n;

    if (rounding === "half-up") {
      const nextDigit = discarded[0] ?? "0";
      if (nextDigit >= "5") inc = 1n;
      // half-up は「負数はゼロから遠ざかる」ので、absに+1して最後に符号を付ければOK
    } else if (rounding === "floor") {
      // floor: 正なら切り捨て、負なら（端数があれば）より小さくする => absに+1
      if (sign < 0n) inc = 1n;
    } else if (rounding === "ceil") {
      // ceil: 正なら（端数があれば）より大きくする => absに+1、負なら切り捨て
      if (sign > 0n) inc = 1n;
    }

    absMinor += inc;
  }

  return sign * absMinor;
}

export class Money {
  private readonly amountMinor: bigint;
  public readonly currency: CurrencyCode;

  private constructor(currency: CurrencyCode, amountMinor: bigint) {
    this.currency = currency;
    this.amountMinor = amountMinor;
    Object.freeze(this); // 念のため（浅いfreezeだけど気持ち的に🧊）
  }

  static fromMinor(currency: CurrencyCode, amountMinor: bigint): Money {
    return new Money(currency, amountMinor);
  }

  static fromDecimalString(
    currency: CurrencyCode,
    amount: string,
    rounding: RoundingMode = "half-up",
  ): Money {
    const minorUnit = CURRENCY_META[currency].minorUnit;
    const minor = parseDecimalToMinor(amount, minorUnit, rounding);
    return new Money(currency, minor);
  }

  /** 「ゼロ以上」の金額が欲しいとき用（例：価格、支払い額） */
  static nonNegativeFromMinor(currency: CurrencyCode, amountMinor: bigint): Money {
    if (amountMinor < 0n) throw new Error("Money must be non-negative");
    return new Money(currency, amountMinor);
  }

  /** 「ゼロ禁止」にしたいとき用（例：最低金額が必要な料金） */
  static positiveFromMinor(currency: CurrencyCode, amountMinor: bigint): Money {
    if (amountMinor <= 0n) throw new Error("Money must be positive");
    return new Money(currency, amountMinor);
  }

  isZero(): boolean {
    return this.amountMinor === 0n;
  }

  isNegative(): boolean {
    return this.amountMinor < 0n;
  }

  equals(other: Money): boolean {
    return this.currency === other.currency && this.amountMinor === other.amountMinor;
  }

  toMinor(): bigint {
    return this.amountMinor;
  }

  /** 表示用の "12.34" みたいな文字列（通貨のminor unitに合わせる） */
  toDecimalString(): string {
    const minorUnit = CURRENCY_META[this.currency].minorUnit;
    const sign = this.amountMinor < 0n ? "-" : "";
    const abs = this.amountMinor < 0n ? -this.amountMinor : this.amountMinor;

    if (minorUnit === 0) return `${sign}${abs.toString()}`;

    const base = pow10(minorUnit);
    const major = abs / base;
    const frac = abs % base;

    const fracStr = frac.toString().padStart(minorUnit, "0");
    return `${sign}${major.toString()}.${fracStr}`;
  }

  private assertSameCurrency(other: Money): void {
    if (this.currency !== other.currency) {
      throw new Error(`Currency mismatch: ${this.currency} vs ${other.currency}`);
    }
  }

  add(other: Money): Money {
    this.assertSameCurrency(other);
    return new Money(this.currency, this.amountMinor + other.amountMinor);
  }

  subtract(other: Money): Money {
    this.assertSameCurrency(other);
    return new Money(this.currency, this.amountMinor - other.amountMinor);
  }

  /** 図解：加算の流れ ➕ */
  /*
  ```mermaid
  flowchart LR
    A[Money: 100 JPY] 
    B[Money: 50 JPY] 
    
    A & B --> Check{Currency同じ?}
    Check -- No --> Error[Throw Error 💥]
    Check -- Yes --> Calc[100 + 50 = 150]
    Calc --> New[New Money: 150 JPY 🆕]
    
    style New fill:#ccffcc,stroke:#333
  ```
  */

  /**
   * 比率で掛ける（例：税込み = 110/100）
   * 端数は rounding で決める。
   */
  multiplyRatio(numerator: bigint, denominator: bigint, rounding: RoundingMode = "half-up"): Money {
    if (denominator === 0n) throw new Error("denominator must not be zero");

    // 符号を整理（denominatorを正に寄せる）
    if (denominator < 0n) {
      numerator = -numerator;
      denominator = -denominator;
    }

    const product = this.amountMinor * numerator;
    const q = product / denominator;
    const r = product % denominator;

    if (r === 0n) return new Money(this.currency, q);

    const sign = product < 0n ? -1n : 1n;
    const absR = r < 0n ? -r : r; // rはproductと同符号
    const absD = denominator;

    let adjust = 0n;

    if (rounding === "half-up") {
      // 2*remainder >= denom なら切り上げ（負はゼロから遠ざかる）
      if (absR * 2n >= absD) adjust = 1n * sign;
    } else if (rounding === "floor") {
      if (sign < 0n) adjust = -1n;
    } else if (rounding === "ceil") {
      if (sign > 0n) adjust = 1n;
    }

    return new Money(this.currency, q + adjust);
  }
}
````

---

## 5) 使い方イメージ（カフェ注文）☕🧾

### 価格（Price）はゼロ以上にしたいよね？

```ts
import { Money } from "./money";

const lattePrice = Money.nonNegativeFromMinor("JPY", 550n); // 550円
const cakePrice = Money.fromDecimalString("USD", "4.25");   // 4.25ドル

// 合計
const total = lattePrice.add(Money.nonNegativeFromMinor("JPY", 200n)); // +200円
console.log(total.toDecimalString()); // "750"
```

### 税率を「比率」で安全に掛ける（10%なら110/100）🧾✨

![ddd_ts_study_033_tax_calculation](./picture/ddd_ts_study_033_tax_calculation.png)

```ts
import { Money } from "./money";

const subtotal = Money.nonNegativeFromMinor("JPY", 1000n);

const taxed = subtotal.multiplyRatio(110n, 100n, "half-up"); // 税込み
console.log(taxed.toDecimalString()); // "1100"
```

---

## 6) ここが超大事：ゼロ禁止？負数禁止？どうするの？🚫0️⃣➖

![ddd_ts_study_033_zero_negative](./picture/ddd_ts_study_033_zero_negative.png)

結論：**Money自体は負数もゼロも持てるほうが便利** なことが多いよ🙂
だってさ…

* 返金（refund）＝負の金額っぽく扱いたい場合もある💸
* 割引（discount）＝負で表すと計算が簡単な場合もある🏷️
* でも「価格」や「支払い額」は **ゼロ以上** にしたいことが多い✨

だからおすすめは👇

* Money VOは「通貨 + 最小単位整数 + 丸め」を責務にする
* 「ゼロ禁止」「負数禁止」は **用途側のFactory**（nonNegative / positive）で縛る

この章の実装はその方針だよ🧡

---

## 7) テストしよう（Vitest）🧪💎

```ts
// money.test.ts
import { describe, it, expect } from "vitest";
import { Money } from "./money";

describe("Money", () => {
  it("USD: decimal string -> minor units", () => {
    const m = Money.fromDecimalString("USD", "12.34");
    expect(m.toMinor()).toBe(1234n);
    expect(m.toDecimalString()).toBe("12.34");
  });

  it("JPY: allows .00 but must be all zeros", () => {
    const m = Money.fromDecimalString("JPY", "100.00");
    expect(m.toMinor()).toBe(100n);
    expect(m.toDecimalString()).toBe("100");
  });

  it("rounding: half-up", () => {
    expect(Money.fromDecimalString("USD", "1.234", "half-up").toMinor()).toBe(123n);
    expect(Money.fromDecimalString("USD", "1.235", "half-up").toMinor()).toBe(124n);
  });

  it("rounding: negative half-up goes away from zero", () => {
    expect(Money.fromDecimalString("USD", "-1.235", "half-up").toMinor()).toBe(-124n);
  });

  it("currency mismatch throws", () => {
    const usd = Money.fromMinor("USD", 100n);
    const jpy = Money.fromMinor("JPY", 100n);
    expect(() => usd.add(jpy)).toThrow();
  });

  it("multiplyRatio: tax 10%", () => {
    const subtotal = Money.fromMinor("JPY", 999n);
    const taxed = subtotal.multiplyRatio(110n, 100n, "half-up");
    expect(taxed.toMinor()).toBe(1099n); // 999 * 1.1 = 1098.9 -> 1099
  });

  it("nonNegativeFromMinor rejects negative", () => {
    expect(() => Money.nonNegativeFromMinor("JPY", -1n)).toThrow();
  });
});
```

---

## 8) AIの使いどころ（おすすめプロンプト）🤖🪄

### ① 仕様の穴を見つけてもらう🕳️👀

* 「このMoney VOに潜むバグや仕様の穴を10個挙げて。通貨の小数桁、負数、丸め、巨大値、文字列パース観点で！」

### ② テストケース増殖マンになってもらう🧪✨

* 「VitestでMoneyの境界値テストを追加して。0、負数、桁あふれ、通貨ミスマッチ、丸めの境界（…5）を中心に！」

### ③ レビュー観点を固定化する🧾📌

* 「Money VOのレビュー観点チェックリストを作って。禁止すべき設計（Numberで保持、通貨なし、丸め未定義など）も入れて！」

---

## 9) ちょい現実の話：将来は Decimal が来るかも？🌈🔮

![ddd_ts_study_033_decimal_future](./picture/ddd_ts_study_033_decimal_future.png)

いまのJavaScriptは “お金のための標準Decimal型” がまだ無いので、現場では「最小通貨単位の整数」で持つ設計がめっちゃ多いよ。
一方で、TC39では Decimal を扱う提案も進んでる（ただし現時点ではStage 1）。([GitHub][1])

だから現状のおすすめはこう👇

* **今すぐ安定**：最小通貨単位の整数（今回の設計）✅
* **将来**：Decimalが標準になったら、置き換え可能なように VO で包む ✅（←ここ超重要！）

---

## 10) まとめ（この章で一気に強くなる💪✨）

* Moneyは **「通貨 + 最小通貨単位の整数 + 丸め」** をVOに閉じ込める💴🧊
* Numberでお金を計算すると誤差の沼がある😵‍💫（だから避ける）([GitHub][1])
* ゼロ禁止・負数禁止は **用途側のFactoryで縛る**とキレイ🏷️🛡️
* テストは「境界（0/負/…5/巨大値/通貨ミスマッチ）」が主戦場🧪🔥

---

## 理解チェック（サクッと）✅💡

1. Moneyに currency を持たせる理由は？🌍
2. 「最小通貨単位の整数」で持つと何が嬉しい？🧊
3. JPY と USD を add したらどうすべき？🧨
4. 1.235 を “half-up” で2桁にしたら？（正・負どっちも）🌀
5. ゼロ禁止のルールは Money の中に入れるべき？それとも用途側？🤔

---

次の第34章（Quantity VO）では「数量と単位」の地雷をVOで封印するよ〜！📏💥

[1]: https://github.com/tc39/proposal-decimal "GitHub - tc39/proposal-decimal: Built-in exact decimal numbers for JavaScript"
[2]: https://www.iso.org/iso-4217-currency-codes.html?utm_source=chatgpt.com "ISO 4217 — Currency codes"
[3]: https://docs.stripe.com/api/charges/create?utm_source=chatgpt.com "Create a charge | Stripe API Reference"
[4]: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Data_structures?utm_source=chatgpt.com "JavaScript data types and data structures - MDN Web Docs"
