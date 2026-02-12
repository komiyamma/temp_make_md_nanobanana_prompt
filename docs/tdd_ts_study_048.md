# 第48章：乱数の固定（フレーク撲滅の基本）🎲🚫

![固定されたサイコロ](./picture/tdd_ts_study_048_fixed_dice.png)

## 🎯 目的（この章でできるようになること）

* 「たまに落ちるテスト（フレーク）」の超あるある原因＝**乱数**を見つけて潰せる🕵️‍♀️✨
* `Math.random()` や `crypto.randomUUID()` みたいな“ランダム依存”を、**テストで100%再現できる形**にできる🔒✅
* 乱数を **注入（DI）** or **スパイ（spy）** で固定して、毎回同じ結果にする🧪💖

---

## 📚 学ぶ：乱数がテストを壊すワケ（超シンプル）

### ✅ 乱数は「依存」だよ

* 同じ入力を入れても、乱数があると出力が変わる

![slot_machine](./picture/tdd_ts_study_048_slot_machine.png)
  → **テストが「運ゲー」**になる🎰💥

### ✅ `Math.random()` は“シード指定できない”

`Math.random()` は実装側が初期シードを選ぶだけで、ユーザーが選んだりリセットできないよ

![wild_horse](./picture/tdd_ts_study_048_wild_horse.png)（だから「再現」ができない）📌 ([MDNウェブドキュメント][1])

### ✅ セキュリティ用途に `Math.random()` はNG

暗号やトークンみたいな用途は `Math.random()` じゃなくて Web Crypto を使うべき、とMDNでも注意されてるよ🔐 ([MDNウェブドキュメント][2])
（でもテストでは、どのみち“固定できる形”が必要！）

---

## 🧪 手を動かす：フレークを「わざと作って」→「潰す」💥➡️✨

### 0) お題：くじ引き関数（たまにテストが落ちるやつ）

* 3つの景品からランダムに選ぶ🎁

```ts
// src/lottery.ts
export function drawPrize(): "A" | "B" | "C" {
  const r = Math.random()
  if (r < 0.6) return "A"
  if (r < 0.9) return "B"
  return "C"
}
```

テストを「Bが出るはず！」って書いたら…運が悪いと落ちる🤣

![flaky_banana](./picture/tdd_ts_study_048_flaky_banana.png)

```ts
// tests/lottery.test.ts
import { describe, it, expect } from "vitest"
import { drawPrize } from "../src/lottery"

describe("drawPrize", () => {
  it("Bが出る（はず）", () => {
    expect(drawPrize()).toBe("B") // ←運ゲー😭
  })
})
```

---

## ✅ 解決策その1（本命）：乱数源を注入する（DI）📦➡️🎲

### 1) 乱数を「引数でもらう」形にする

ポイントはこれ👇

* **本番は Math.random を渡す**
* **テストは固定の偽物RNGを渡す**

![loaded_dice](./picture/tdd_ts_study_048_loaded_dice.png)

```ts
// src/lottery.ts
export type Rng = () => number

export function drawPrize(rng: Rng = Math.random): "A" | "B" | "C" {
  const r = rng()
  if (r < 0.6) return "A"
  if (r < 0.9) return "B"
  return "C"
}
```

### 2) テストは「固定の乱数」を渡す

```ts
// tests/lottery.test.ts
import { describe, it, expect } from "vitest"
import { drawPrize } from "../src/lottery"

describe("drawPrize", () => {
  it("rng=0.7ならB", () => {
    const fixed = () => 0.7
    expect(drawPrize(fixed)).toBe("B")
  })

  it("rng=0.95ならC", () => {
    const fixed = () => 0.95
    expect(drawPrize(fixed)).toBe("C")
  })
})
```

💯 これで「毎回同じ」！フレーク消滅！🎉

---

## ✅ 解決策その2（応急処置）：`Math.random` を spy して固定する🕵️‍♀️🎲

「今さら関数の形を変えられない…😭」って時の救急箱🚑

Vitest は `vi.spyOn` / `mockReturnValueOnce` みたいなモック機能があるよ

![magician_force](./picture/tdd_ts_study_048_magician_force.png)（基本のモック機能）🧰 ([Vitest][3])

```ts
import { describe, it, expect, vi, afterEach } from "vitest"
import { drawPrize } from "../src/lottery"

afterEach(() => {
  vi.restoreAllMocks() // 他テストへの汚染を防ぐ✨
})

describe("drawPrize (spy)", () => {
  it("Math.randomを0.7に固定してB", () => {
    vi.spyOn(Math, "random").mockReturnValue(0.7)
    expect(drawPrize()).toBe("B")
  })

  it("1回目A、2回目C（順番固定）", () => {
    vi.spyOn(Math, "random")
      .mockReturnValueOnce(0.1)
      .mockReturnValueOnce(0.95)

    expect(drawPrize()).toBe("A")
    expect(drawPrize()).toBe("C")
  })
})
```

### ⚠️ spy方式の注意点

* グローバルを書き換えるので、**戻し忘れると地獄**😇
* なので `vi.restoreAllMocks()` とセット運用がほぼ必須だよ（モックはテスト間でクリア/復元すべし、というガイドの流れ）🧼 ([Vitest][3])

---

## ✅ 解決策その3：シード付きPRNGで「再現できるランダム列」を作る🌱🎲

「ゲームのリプレイ」「疑似ランダムの検証」「ランダムケースを100回回す」みたいに、
**ランダム感は欲しいけど再現もしたい**ときはこれ！

たとえば `seedrandom` は “シードから再現できる疑似乱数列” を作れるライブラリ

![plant_seed](./picture/tdd_ts_study_048_plant_seed.png)として説明されてるよ🌱 ([tessl.io][4])

イメージ（使い方の雰囲気）👇

```ts
// （例）シード付きRNGを作って注入するイメージ
import seedrandom from "seedrandom"
import { drawPrize } from "./lottery"

const rng = seedrandom("my-seed") // rng() が 0..1 を返す
console.log(drawPrize(rng))       // 何度実行しても同じ順で出る✨
```

---

## 🌟 よくある「乱数っぽい依存」も同じ考え方で固定するよ

### 🎯 ID生成（例：UUID）

* 本番：`crypto.randomUUID()` みたいにランダム
* テスト：固定IDを返す関数を注入

![fixed_stamp](./picture/tdd_ts_study_048_fixed_stamp.png)

```ts
// src/id.ts
export type IdGen = () => string

export function createOrderId(idGen: IdGen = () => crypto.randomUUID()): string {
  return idGen()
}
```

テスト👇

```ts
import { expect, it } from "vitest"
import { createOrderId } from "../src/id"

it("IDを固定できる", () => {
  const fixed = () => "ORDER-0001"
  expect(createOrderId(fixed)).toBe("ORDER-0001")
})
```

---

## 🤖 AIの使いどころ（この章はめっちゃ相性いい）💖

### ✅ おすすめプロンプト例

* 「この関数、`Math.random()` を直接呼んでるんだけど、**DIで差し替え可能にする最小変更**を提案して。テストも書いて。」
* 「乱数が複数回呼ばれるから、**返す値の列を指定できる stubRng** を作って」

AI案が出たら、あなたはこれだけ見る👇

* その変更で「テストが毎回同じ」になる？🎯
* グローバル汚染（spy）なら、戻し忘れ対策ある？🧼
* “たまたま通るテスト”になってない？🎰🚫

---

## ✅ チェックリスト（合格ライン）🧪✅

* [ ] テストを **10回連続**で回しても落ちない（運要素ゼロ）🔁💯
* [ ] `Math.random()` / `crypto.randomUUID()` を直接使う場所が、**境界（注入可能）**になってる📦
* [ ] spy を使った場合、**必ず復元**してる（`vi.restoreAllMocks()` など）🧼 ([Vitest][3])
* [ ] 「乱数を固定しないと再現できないバグ」が出ても、**再現手段（seedや固定値）**が残せる🌱✨

---

## 💡 ミニ演習（超おすすめ）🎮

### 🧩 演習：shuffle（並び替え）を“固定乱数”でテストする

* `shuffle(items, rng)` にして
* `rng` を固定列（0.8, 0.1, 0.4…）で渡す
* 期待する並びをテストでピタッと固定📌✨

（ここまでできたら、乱数フレークはもう怖くないよ〜！🎲🚫💕）

[1]: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Math/random?utm_source=chatgpt.com "Math.random() - JavaScript - MDN Web Docs"
[2]: https://developer.mozilla.org/ja/docs/Web/JavaScript/Reference/Global_Objects/Math/random?utm_source=chatgpt.com "Math.random() - JavaScript - MDN Web Docs - Mozilla"
[3]: https://vitest.dev/guide/mocking?utm_source=chatgpt.com "Mocking | Guide"
[4]: https://tessl.io/registry/tessl/npm-seedrandom/3.0.0/files/docs/index.md?utm_source=chatgpt.com "tessl/npm-seedrandom@3.0.x - Registry"
