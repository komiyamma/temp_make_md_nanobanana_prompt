# 第23章：テストの独立性（順序依存を消す）🧵

![独立したテストの糸](./picture/tdd_ts_study_023_isolated_threads.png)

たま〜に落ちるテスト（フレーク）って、**心が削れる**よね…😵‍💫💦
この章はそれを防ぐために、**「どのテストも単体で動く」**状態を作る練習だよ〜💪🌸

---

## 🎯 この章のゴール

* ✅ **テストを1本だけ実行しても**落ちないようにできる
* ✅ テストの実行順が変わっても（並列でも）**結果が変わらない**ようにできる
* ✅ **beforeEach / afterEach** を「正しく」使えるようになる✨

---

## 📚 学ぶこと（超重要ポイント3つ）📌

![Order Dependency](./picture/tdd_ts_study_023_order_dependency.png)

### 1) 「順序依存」ってなに？🧩

**テストAが先に実行される前提**で、テストBがこっそり成立してる状態😇
たとえば👇

* テストAで何かを追加 → テストBは「追加された状態」を勝手に期待してる
* テストAでモックしたのを戻してなくて → テストBに漏れてる

こういうのは、**テストを1本だけ実行した瞬間に壊れる**💥

---

![Parallel Execution](./picture/tdd_ts_study_023_parallel_execution.png)

### 2) なぜ今すぐ直すべき？（最新の事情）⚡

Vitestは **デフォで「テストファイルは並列」**で走るよ〜🏃‍♀️🏃‍♂️💨
そして **同一ファイル内のテストは基本「定義順に順番」**だけど、**その順番に依存しちゃダメ**🙅‍♀️
（将来シャッフルしたり、並列設定にすると一瞬で壊れる） ([Vitest][1])

さらに、Vitestには **実行順をランダムにできる `--sequence.shuffle`** があるよ🎲✨
順序依存を見つける最強のライト ensure 🔥 ([Vitest][2])

---

![One Test One World](./picture/tdd_ts_study_023_one_test_one_world.png)

### 3) 独立性の合言葉🪄

> **1テスト＝1つの世界🌎**（毎回つくり直す）

* 共有（グローバル）状態を作らない🙅‍♀️
* もし触ったら、必ず戻す（掃除する）🧹✨
* 「前のテストがやってくれたはず」は禁止〜🚫💦

---

## 🧪 手を動かす：わざと順序依存を作って→直す💥➡️✅

![Shared State Issue](./picture/tdd_ts_study_023_shared_state_issue.png)

### ステップ0：わざとダメな実装（共有状態）を作る😈

`src/cart.ts`

```ts
export type Item = { name: string; price: number }

// ❌ モジュールの外に状態がある（共有状態）
const items: Item[] = []

export function add(item: Item) {
  items.push(item)
}

export function total() {
  return items.reduce((sum, x) => sum + x.price, 0)
}
```

`src/cart.test.ts`

```ts
import { describe, expect, test } from "vitest"
import { add, total } from "./cart"

describe("cart（わざと順序依存）", () => {
  test("追加できる", () => {
    add({ name: "coffee", price: 500 })
    expect(total()).toBe(500)
  })

  test("合計が出る（←ここ、実は自分で準備してない）", () => {
    // ❌ 追加してないのに 500 を期待してる（前のテストに依存）
    expect(total()).toBe(500)
  })
})
```

---

![Shuffle Execution](./picture/tdd_ts_study_023_shuffle_execution.png)

### ステップ1：壊れ方を体験する😵‍💫（超大事）

* VS Codeで **2個目のテストだけ実行**してみてね👉
  → たぶん落ちる！💥（totalが0のはずだから）

さらに、順序依存を炙り出すために **シャッフル実行**もやってみよ🎲✨
Vitestは `--sequence.shuffle` で **ファイルやテストの順番をランダム**にできるよ ([Vitest][2])

`package.json` の scripts に追加（例）：

```json
{
  "scripts": {
    "test": "vitest",
    "test:shuffle": "vitest run --sequence.shuffle"
  }
}
```

そして👇を何回か実行！

```powershell
npm run test:shuffle
```

---

## ✅ 直し方（王道）：状態を「外」に出して、毎回作り直す👶✨

![Fresh Creation](./picture/tdd_ts_study_023_fresh_creation.png)

### ステップ2：Cartを「作る関数」にする（独立性の基本）🧱

`src/cart.ts` をこうする👇

```ts
export type Item = { name: string; price: number }

export function createCart() {
  // ✅ createCartを呼ぶたびに新しい配列（新しい世界🌎）
  const items: Item[] = []

  return {
    add(item: Item) {
      items.push(item)
    },
    total() {
      return items.reduce((sum, x) => sum + x.price, 0)
    },
  }
}
```

テストも「毎回作る」👇

`src/cart.test.ts`

```ts
import { beforeEach, describe, expect, test } from "vitest"
import { createCart } from "./cart"

describe("cart（独立になった✨）", () => {
  let cart: ReturnType<typeof createCart>

  beforeEach(() => {
    cart = createCart()
  })

  test("追加できる", () => {
    cart.add({ name: "coffee", price: 500 })
    expect(cart.total()).toBe(500)
  })

  test("合計が出る（自分で準備してる）", () => {
    cart.add({ name: "coffee", price: 500 })
    expect(cart.total()).toBe(500)
  })
})
```

これで👇が全部通るはず！

* どちらのテストだけ実行してもOK✅
* `npm run test:shuffle` でもOK✅
* テストの並列実行でも壊れにくい✅（ファイル並列が基本だからね） ([Vitest][1])

---

![Cleanup Teardown](./picture/tdd_ts_study_023_cleanup_teardown.png)

## 🧼 よくある「漏れ」パターン集（ここ超あるある）🥹

### ① モックが戻ってない🎭💦

`vi.spyOn` したまま放置、とかね。
Vitestは **`afterEach` で `vi.restoreAllMocks()`** が超定番✨
（または `test.restoreMocks` を有効化でもOK） ([Vitest][3])

例👇

```ts
import { afterEach, vi } from "vitest"

afterEach(() => {
  vi.restoreAllMocks()
})
```

---

### ② 環境変数・グローバルを書き換えたまま🌪️

Vitestには `vi.stubEnv` / `vi.stubGlobal` と、それを戻す `vi.unstubAllEnvs` / `vi.unstubAllGlobals` があるよ🧯✨ ([Vitest][3])

---

### ③ ファイル間の並列で壊れる🧨

Vitestは **テストファイルが並列で走る**のが普通だから、
「ファイルAが先にやるはず」は通用しないよ〜🙅‍♀️ ([Vitest][1])

---

## 🤖 AIの使いどころ（この章は“診断”が強い）🩺✨

コピペして使ってOKだよ〜💕

**プロンプト例①：順序依存の原因特定**

* 「このテストが順序依存になる“共有状態”の候補を列挙して。どこで状態が漏れてる？」

**プロンプト例②：修正案を3段階で**

* 「最小修正 / ふつう / 理想 の3案で直して。メリデメも書いて」

**プロンプト例③：beforeEach設計**

* 「beforeEachで“毎回作り直すべきもの”と、“共有していいもの”を分けて提案して」

---

## ✅ チェックリスト（合格ライン）🎓✨

* ✅ **テスト1本だけ実行**しても落ちない
* ✅ `npm run test:shuffle` を何回か回しても落ちない 🎲
* ✅ `beforeAll` で **ミュータブル（書き換える）なもの**を共有してない
* ✅ モック・環境変数・グローバルを触ったら、**必ず戻してる**🧹

---

## 🧠 2026年の“いま”メモ（最新）📌

* Vitestは **v4系**が現行のガイドに載ってるよ（Getting Startedの更新も2026年1月） ([Vitest][4])
* 実行順ランダム化は `--sequence.shuffle` が公式に用意されてる 🎲 ([Vitest][2])
* ファイル並列・テスト順序・ライフサイクルの考え方も公式で整理されてるよ 🧪 ([Vitest][1])

---

次の章（ミニ演習：カフェ会計☕️🧾）に行くと、**独立性ができてる人ほど爆速で気持ちよく進む**よ〜💨💖
もし今のあなたのコード（テスト）が「たまに落ちる」なら、そのテスト貼ってくれたら、**どこが漏れてるか一緒に特定**するよ🔍✨

[1]: https://vitest.dev/guide/parallelism "Parallelism | Guide | Vitest"
[2]: https://main.vitest.dev/config/sequence?utm_source=chatgpt.com "sequence | Config"
[3]: https://vitest.dev/api/vi.html "Vi | Vitest"
[4]: https://vitest.dev/guide/?utm_source=chatgpt.com "Getting Started | Guide"
