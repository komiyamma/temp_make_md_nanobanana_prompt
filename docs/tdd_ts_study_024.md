# 第24章：ミニ演習①：カフェ会計（税・端数）☕️🧾

![カフェ会計](./picture/tdd_ts_study_024_cafe_counter.png)

この章は「TDDの基礎セット（正常→境界→異常 / AAA / 命名）」を **1本の小さなアプリに凝縮して完走**する回だよ〜！💪🧪
（テストは **Vitest v4系**が現行だよ🧪✨ ([NPM][1])）

---

## ゴール🎯

* 注文（明細）から、**小計 / 税額 / 合計**を出す関数をTDDで作る☕️
* **端数処理（切り捨て/切り上げ/四捨五入）**をテストで固定する💡
* 税額は「**税率ごとにまとめて1回だけ端数処理**」する（日本のインボイス制度の考え方に寄せる）📌
  ※実務でも「税率ごとにまとめて丸め」はよく使われるよ〜 ([Stripe][2])

---

## お題（仕様）📘

### 入力（注文）

* 明細の配列：`name`, `unitPriceYen`, `qty`, `taxRatePercent`（8 or 10 など）
* 端数処理モード：`'floor' | 'ceil' | 'halfUp'`

### 出力（会計結果）

* `subtotalYen`（税抜小計）
* `taxYen`（税額）
* `totalYen`（税込合計）
* （おまけ）税率ごとの内訳 `taxByRate`（学習が捗る✨）

---

![Integer Math](./picture/tdd_ts_study_024_integer_math.png)

## 実装方針（ミスりにくいコツ）🧠✨

* お金は **小数を使わず、円の整数で扱う**（浮動小数の誤差を避ける）💴
* 税は `taxable * rate / 100` で「割り切れない」ことがある → **端数処理が必要**🌀
* 端数処理は **「税率ごとの合計」に対して1回だけ**やる
  （行ごとに丸めるのと結果がズレることがあるよ⚠️ ([Stripe][2])）

---

## まずファイルを用意📁

* `src/cafeBilling.ts`
* `tests/cafeBilling.test.ts`

---

![TDD Steps](./picture/tdd_ts_study_024_tdd_steps.png)

## テストから作る🧪（TDDの順番：小さく！）

以下は「**この順番でコミットしていく**」想定だよ😊✨
（1コミット＝1〜2テスト＋最小実装＋軽い整理、が気持ちいい💞）

---

## ステップ1：空の注文は0円🫧

**tests/cafeBilling.test.ts**

```ts
import { describe, it, expect } from 'vitest'
import { calcCafeBill } from '../src/cafeBilling'

describe('calcCafeBill', () => {
  it('空の注文は 0円', () => {
    const result = calcCafeBill([], { rounding: 'floor' })
    expect(result).toEqual({
      subtotalYen: 0,
      taxYen: 0,
      totalYen: 0,
      taxByRate: {},
    })
  })
})
```

**src/cafeBilling.ts（最小実装）**

```ts
export type RoundingMode = 'floor' | 'ceil' | 'halfUp'

export type LineItem = {
  name: string
  unitPriceYen: number
  qty: number
  taxRatePercent: number
}

export type CafeBill = {
  subtotalYen: number
  taxYen: number
  totalYen: number
  taxByRate: Record<string, number>
}

export function calcCafeBill(items: LineItem[], opts: { rounding: RoundingMode }): CafeBill {
  if (items.length === 0) {
    return { subtotalYen: 0, taxYen: 0, totalYen: 0, taxByRate: {} }
  }
  // 次のステップで育てる🌱
  return { subtotalYen: 0, taxYen: 0, totalYen: 0, taxByRate: {} }
}
```

✅ **チェック**：まず“形”だけ通す！ここで頑張りすぎない🙆‍♀️

---

## ステップ2：明細1つ（10%）☕️

「コーヒー 500円 ×1、税10%、切り捨て」

```ts
it('コーヒー 500円×1（10%・切り捨て）=> 小計500 税50 合計550', () => {
  const result = calcCafeBill(
    [{ name: 'coffee', unitPriceYen: 500, qty: 1, taxRatePercent: 10 }],
    { rounding: 'floor' }
  )
  expect(result.subtotalYen).toBe(500)
  expect(result.taxYen).toBe(50)
  expect(result.totalYen).toBe(550)
  expect(result.taxByRate).toEqual({ '10': 50 })
})
```

実装（まずベタでもOK🙆‍♀️）

```ts
function assertValidItem(item: LineItem): void {
  if (!Number.isInteger(item.unitPriceYen) || item.unitPriceYen < 0) throw new Error('unitPriceYen')
  if (!Number.isInteger(item.qty) || item.qty <= 0) throw new Error('qty')
  if (!Number.isInteger(item.taxRatePercent) || item.taxRatePercent < 0) throw new Error('taxRatePercent')
}

function calcTaxFromTaxable(taxableYen: number, ratePercent: number, rounding: RoundingMode): number {
  const numerator = taxableYen * ratePercent // 例: 500*10=5000
  const div = Math.floor(numerator / 100)
  const rem = numerator % 100

  if (rounding === 'floor') return div
  if (rounding === 'ceil') return rem === 0 ? div : div + 1
  // halfUp（四捨五入）: 0.50円以上を切り上げ
  return rem >= 50 ? div + 1 : div
}

export function calcCafeBill(items: LineItem[], opts: { rounding: RoundingMode }): CafeBill {
  const rounding = opts.rounding

  let subtotal = 0
  const taxableByRate: Record<string, number> = {}

  for (const item of items) {
    assertValidItem(item)
    const line = item.unitPriceYen * item.qty
    subtotal += line

    const key = String(item.taxRatePercent)
    taxableByRate[key] = (taxableByRate[key] ?? 0) + line
  }

  const taxByRate: Record<string, number> = {}
  let tax = 0
  for (const [rate, taxable] of Object.entries(taxableByRate)) {
    const rateNum = Number(rate)
    const t = calcTaxFromTaxable(taxable, rateNum, rounding)
    taxByRate[rate] = t
    tax += t
  }

  return {
    subtotalYen: subtotal,
    taxYen: tax,
    totalYen: subtotal + tax,
    taxByRate,
  }
}
```

✅ **チェック**：

* 税が `10%` でちゃんと50円になってる？💴
* `taxByRate` が **税率別**になってる？🧾

---

## ステップ3：数量（qty）を増やす🍰

```ts
it('ケーキ 420円×2（10%・切り捨て）=> 小計840 税84 合計924', () => {
  const result = calcCafeBill(
    [{ name: 'cake', unitPriceYen: 420, qty: 2, taxRatePercent: 10 }],
    { rounding: 'floor' }
  )
  expect(result).toMatchObject({
    subtotalYen: 840,
    taxYen: 84,
    totalYen: 924,
    taxByRate: { '10': 84 },
  })
})
```

✅ **チェック**：テスト名が「仕様」になってる？📝✨

---

## ステップ4：複数商品を合算🍩🥤

```ts
it('複数商品 => 小計を合算して税計算', () => {
  const result = calcCafeBill(
    [
      { name: 'coffee', unitPriceYen: 500, qty: 1, taxRatePercent: 10 },
      { name: 'donut', unitPriceYen: 180, qty: 2, taxRatePercent: 10 },
    ],
    { rounding: 'floor' }
  )
  expect(result.subtotalYen).toBe(860)
  expect(result.taxYen).toBe(86)
  expect(result.totalYen).toBe(946)
})
```

---

![Tax Rounding Strategy](./picture/tdd_ts_study_024_tax_rounding_strategy.png)

## ステップ5：税率ごとにまとめて「1回だけ」丸める📌（重要！）

日本のインボイス制度では、端数処理は **税率ごとにまとめて1回**という考え方が案内されてるよ（運用としても多い）🧾✨ ([Stripe][2])

違いが出る “わざと” の例👇

* 99円を8%で税計算すると 7.92円 → 切り捨てで7円
* **行ごと丸め**：7円 + 7円 = 14円
* **税率ごとに合算して丸め**：198円×8% = 15.84円 → 切り捨てで15円（違う！😳）

```ts
it('税は税率ごとに合算してから丸める（行ごと丸めない）', () => {
  const result = calcCafeBill(
    [
      { name: 'snackA', unitPriceYen: 99, qty: 1, taxRatePercent: 8 },
      { name: 'snackB', unitPriceYen: 99, qty: 1, taxRatePercent: 8 },
    ],
    { rounding: 'floor' }
  )
  expect(result.subtotalYen).toBe(198)
  expect(result.taxByRate).toEqual({ '8': 15 })
  expect(result.taxYen).toBe(15)
  expect(result.totalYen).toBe(213)
})
```

✅ **チェック**：

* “行ごと丸め” してない？（税率別にまとめてから丸めてる？）👀✨

---

![Rounding Modes](./picture/tdd_ts_study_024_rounding_modes.png)

## ステップ6：端数処理モードをテストで固定🧷

同じ入力で、丸めだけ変えるテストを作るよ〜💡

```ts
it('端数処理：floor（切り捨て）', () => {
  const r = calcCafeBill([{ name: 'x', unitPriceYen: 99, qty: 1, taxRatePercent: 8 }], { rounding: 'floor' })
  // 99*8%=7.92 => 7
  expect(r.taxYen).toBe(7)
})

it('端数処理：ceil（切り上げ）', () => {
  const r = calcCafeBill([{ name: 'x', unitPriceYen: 99, qty: 1, taxRatePercent: 8 }], { rounding: 'ceil' })
  // 7.92 => 8
  expect(r.taxYen).toBe(8)
})

it('端数処理：halfUp（四捨五入）', () => {
  const r = calcCafeBill([{ name: 'x', unitPriceYen: 125, qty: 1, taxRatePercent: 8 }], { rounding: 'halfUp' })
  // 125*8%=10.00 => 10（ちょうど）
  expect(r.taxYen).toBe(10)
})
```

✅ **チェック**：

* 端数処理が「なんとなく」じゃなく、テストでガチガチに固定できた？🔒💕

---

![Invalid Input Guard](./picture/tdd_ts_study_024_invalid_input_guard.png)

## ステップ7：異常系（入力ミス）も仕様にする🚫

「負の値」「数量0」みたいなミスは、ちゃんとエラーにして守るよ🛡️

```ts
it('異常：qtyが0以下ならエラー', () => {
  expect(() =>
    calcCafeBill([{ name: 'coffee', unitPriceYen: 500, qty: 0, taxRatePercent: 10 }], { rounding: 'floor' })
  ).toThrow()
})

it('異常：unitPriceYenが負ならエラー', () => {
  expect(() =>
    calcCafeBill([{ name: 'coffee', unitPriceYen: -1, qty: 1, taxRatePercent: 10 }], { rounding: 'floor' })
  ).toThrow()
})
```

---

![Refactoring Broom](./picture/tdd_ts_study_024_refactoring_broom.png)

## 仕上げのリファクタ（小さくね🧹✨）

ここは「大工事しない」ルールでいくよ😊

* ✅ 関数名を “会計っぽい言葉” に（`taxableByRate` とか）
* ✅ テストの重複を **消しすぎない**（読み物として残す📘）
* ✅ 端数処理は `calcTaxFromTaxable` に閉じ込める（責務がキレイ✨）

---

## 🤖AIの使い方（この章で強い！）

### 1) テストケース増やし（抜け探し）🔍

コピペして使ってOK👇

```text
「カフェ会計」のTDDをしています。
仕様：小計(円)→税(税率ごとに合算して1回丸め)→合計。
端数処理は floor/ceil/halfUp。
不足していそうなテスト観点を、正常/境界/異常に分けて10個出して。
ただし“実装の詳細”に依存しない観点だけにして。
```

### 2) テスト名の改善📝

```text
このテスト名を「仕様が読める名前」に直して。Given/When/Thenの雰囲気で3案。
（短く、でも誤解がない名前に）
```

---

## 最終チェック✅（合格ライン🎉）

* ✅ テストが **仕様書みたいに読める**📘✨
* ✅ 正常→境界→異常が揃ってる🧪
* ✅ 税の丸めが「税率ごとに1回」になってる🧾 ([Stripe][2])
* ✅ 端数処理モードがテストで固定されてる🔒
* ✅ お金の計算で小数を直接扱ってない💴✨

---

## ちょい豆知識（2026時点の“今”）🗓️✨

* Vitest は **v4.0.17 が現行の latest**（最近も更新されてるよ🧪）([NPM][1])
* TypeScript は **npm上の最新が 5.9.3**（5.9系）だよ🧠([NPM][3])
* Node.js は **v24 が Active LTS**（LTS表で確認できるよ）🟢([Node.js][4])

---

次はこの会計を土台にして、もうちょい条件が増える「ミニ演習②（割引・クーポン）」に繋げると超気持ちいいよ〜🎟️🧾💕
必要なら、この章を「コミット手順（例：test→feat→refactor）」まで書いた“提出用フォーマット”に整えて渡すね😊✨

[1]: https://www.npmjs.com/package/vitest?utm_source=chatgpt.com "vitest"
[2]: https://stripe.com/resources/more/how-to-calculate-consumption-tax-under-the-japanese-invoice-system?utm_source=chatgpt.com "Calculate consumption tax under Japan's Invoice System"
[3]: https://www.npmjs.com/package/typescript?utm_source=chatgpt.com "TypeScript"
[4]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
