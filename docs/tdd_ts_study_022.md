# 第22章：パラメータ化テスト（ケース増殖の味方）🔁

![パラメータ化テスト](./picture/tdd_ts_study_022_multiplier.png)

## 🎯 この章のゴール

* 「同じ形のテストが増えてきた…😵‍💫」を、**パラメータ化テスト**でスッキリ整理できるようになる✨
* **境界値（ギリギリの値）**を増やしても、テストが読みやすいまま保てる📚💕

---

## 🌱 まずイメージ：こういう時に効く！

たとえばこんなテスト👇

* 点数 → 評価（A/B/C…）
* 料金 → 送料（重さで段階が変わる）
* 税計算 → 端数処理（切り上げ/切り捨て）

こういうのって、**入力と期待値が違うだけ**で、テストの形がほぼ同じになりがちだよね🥺
そこで **パラメータ化**すると…

* ✅ テスト本体（ロジック）は1回だけ書く
* ✅ ケースは「表（テーブル）」で増やすだけ
* ✅ 境界値を足すのがラクになる💪✨

（Vitestでも `test.each` / `it.each` が公式に用意されてるよ🧪） ([Vitest][1])

---

## 🧠 どこまでパラメータ化する？（やりすぎ防止🚧）

パラメータ化テストが向くのは👇

### ✅ 向く

* **Arrange（準備）が同じ形**
* **Assert（検証）が同じ形**
* 「入力→出力」が同じパターンで並ぶ

### 🚫 向かない（分けた方が読みやすい）

* ケースごとに準備が全然違う（DBっぽい準備が混ざる等）
* 1ケースだけ検証観点が違う（例：例外・ログ・副作用だけ別）
* “仕様が違う話”まで同じ表に混ぜちゃう

👉 コツは **「1つのテスト＝1つの約束」**のまま、ケースだけ増やすことだよ🫶✨

---

## 🧪 Vitestのパラメータ化：まずは王道 `test.each` 💖

Vitestの `test.each` は、**配列のケース**でも、**オブジェクトのケース**でもOK！
さらにテスト名に `%i` とか `$a` みたいに値を埋め込めるのが気持ちいい✨ ([Vitest][1])

---

## 🧑‍💻 手を動かす：境界値が増える「点数→評価」を題材にやってみよ📚💯

## ① 仕様（今回はこれ！）

* 0〜59 → `F`
* 60〜69 → `D`
* 70〜79 → `C`
* 80〜89 → `B`
* 90〜100 → `A`

（※例外系は前の章でやってる想定だから、今回は正常系の境界を育てる🪴）

---

## ② まずは最小でスタート（3ケースだけ）🍼

```ts
// src/gradeOf.ts
export type Grade = 'A' | 'B' | 'C' | 'D' | 'F'

export function gradeOf(score: number): Grade {
  if (score <= 59) return 'F'
  if (score <= 69) return 'D'
  if (score <= 79) return 'C'
  if (score <= 89) return 'B'
  return 'A'
}
```

テストはこう👇（最初は3つくらいでOKだよ😊）

```ts
// tests/gradeOf.test.ts
import { describe, expect, test } from 'vitest'
import { gradeOf } from '../src/gradeOf'

describe('gradeOf', () => {
  test.each([
    [0, 'F'],
    [60, 'D'],
    [100, 'A'],
  ])('score=%i -> %s', (score, expected) => {
    expect(gradeOf(score)).toBe(expected)
  })
})
```

📌 ここポイント：`%i` や `%s` でテスト名に値を埋め込めるよ（Vitest公式に書いてあるやつ！） ([Vitest][1])

---

## ③ ここからが第22章：境界値を “5ケース追加” して強くする💪🧪

境界値って、たとえばこういう「段差の両側」だよね👇

* 59 / 60
* 69 / 70
* 89 / 90

じゃあ表（ケース）を増やすだけでOK✨

```ts
import { describe, expect, test } from 'vitest'
import { gradeOf, type Grade } from '../src/gradeOf'

describe('gradeOf', () => {
  test.each([
    [0, 'F'],
    [59, 'F'],   // 境界（手前）
    [60, 'D'],   // 境界（到達）
    [69, 'D'],   // 境界（手前）
    [70, 'C'],   // 境界（到達）
    [89, 'B'],   // 境界（手前）
    [90, 'A'],   // 境界（到達）
    [100, 'A'],
  ] satisfies ReadonlyArray<readonly [number, Grade]>)(
    'score=%i -> %s',
    (score, expected) => {
      expect(gradeOf(score)).toBe(expected)
    },
  )
})
```

### 💡 `satisfies` を使う理由（地味に超うれしい）

* ケース表の `expected` を、`Grade` 以外にすると **その場で型エラー**にしてくれる✅
* 「表に間違いが混ざる事故」減るよ〜！🫶
  `satisfies` は「型を保ったまま、条件だけ満たしてるかチェック」できる書き方としてよく使われるよ ([Zenn][2])

---

## ④ もっと読みやすくする：ケースに “名前” を付ける📝💕

境界値って、失敗した時に「どの境界だっけ？」ってなりがち😇
そこで **オブジェクト配列＋ `$name`** が便利！

Vitestはテスト名で `$a` みたいに **オブジェクトのプロパティを埋め込み**できるよ ([Vitest][1])

```ts
import { describe, expect, test } from 'vitest'
import { gradeOf, type Grade } from '../src/gradeOf'

const cases = [
  { name: 'min', score: 0, expected: 'F' },
  { name: 'border 59', score: 59, expected: 'F' },
  { name: 'border 60', score: 60, expected: 'D' },
  { name: 'border 69', score: 69, expected: 'D' },
  { name: 'border 70', score: 70, expected: 'C' },
  { name: 'border 89', score: 89, expected: 'B' },
  { name: 'border 90', score: 90, expected: 'A' },
  { name: 'max', score: 100, expected: 'A' },
] as const satisfies ReadonlyArray<{ name: string; score: number; expected: Grade }>

describe('gradeOf', () => {
  test.each(cases)('$name: score=$score -> $expected', ({ score, expected }) => {
    expect(gradeOf(score)).toBe(expected)
  })
})
```

これ、落ちた時にログがめっちゃ親切になるよ〜🥹✨

---

## ⑤ おまけ：`test.for` って何？（ちょい発展⭐️）

Vitestには `test.each` と別に **`test.for`** もあるよ！
違いはざっくり👇

* `each`：配列ケースを **引数に展開して渡す**
* `for`：配列ケースを **そのまま1つの引数として渡す**（必要なら `TestContext` も使いやすい）

公式にも例があるよ🧪 ([Vitest][1])

```ts
import { expect, test } from 'vitest'

test.for([
  [59, 'F'],
  [60, 'D'],
])('score=%i -> %s', ([score, expected]) => {
  expect(score < 60 ? 'F' : 'D').toBe(expected)
})
```

（最初は `test.each` が分かりやすいから、まずはそっちでOKだよ😊）

---

## 🤖 AIの使いどころ（“ケース作り”に全振りが正解🎯）

AIはこう使うと強いよ〜🤖✨（でも採用判断はあなたがするやつ！🫶）

### ✅ そのまま使えるプロンプト例

* 「この仕様の **境界値** を全部列挙して（段差の両側も）」
* 「不足しがちなケース（見落としやすい境界）を指摘して」
* 「ケース表を `test.each` 用に、**name付き**で作って」
* 「このパラメータ化テスト、**混ぜるべきじゃない仕様**が紛れてないかレビューして」

---

## ✅ この章のチェックリスト（合格ライン🎓✨）

* [ ] “同じ形のテスト” を `test.each` にまとめられた🧪
* [ ] 境界値を **表に足すだけ**で増やせた🔁
* [ ] 失敗した時に「どのケースか」すぐ分かる（`$name` など）📝
* [ ] ケースが増えすぎたら「分ける」判断もできる🚧

---

## 🧸 ミニ課題（サクッと提出用💌）

1. `gradeOf` のケース表に、あなたが思う境界値を **あと5ケース**追加してね🧪✨
2. 追加した理由をコメントで1行ずつ書いてね📝💕（例：「69はDの上限だから」）

---

次の章（第23章）は「テストの独立性」＝**順序依存を消す**🧵✨
パラメータ化でケース増やした後に、そこを固めるとめちゃ強くなるよ〜💪🥰

[1]: https://vitest.dev/api/ "Test API Reference | Vitest"
[2]: https://zenn.dev/tonkotsuboy_com/articles/typescript-as-const-satisfies?utm_source=chatgpt.com "TypeScript 4.9のas const satisfiesが便利。型チェックと ..."
