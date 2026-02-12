# 第26章：三角測量（2例目で一般化）📐

![三角測量](./picture/tdd_ts_study_026_triangle.png)

## 🎯 今日のゴール

* 「最初はベタでOK」→ **2つ目の例（テスト）で“ちゃんと一般化”**できるようになる💪✨
* **2例目の選び方**が分かって、TDDがスムーズに回るようになる🔁💕

---

![Triangulation Concept](./picture/tdd_ts_study_026_triangulation_concept.png)

## 📌 三角測量ってなに？（超かんたん）

TDDって、最初は「通すための超ベタ実装（仮実装）」でもOKだよね🩹
でもそのままだと “たまたま通ってるだけ” になりがち…😵‍💫

そこで **三角測量（Triangulation）**✨

* **1つ目の例**：まず通す（ベタでもOK）
* **2つ目の例**：ベタが通らなくなるように “別の例” を追加
* するとコードが **自然に一般化**される（＝ちゃんとしたロジックになる）📐

この考え方は「抽象化（一般化）は、例が2つ以上そろってからが一番安全」という超保守的なやり方として紹介されてるよ📘✨ ([スタニスワフのテックノート][1])

---

## ✅ 2例目の“いい選び方” 3ルール 📏✨

![Rule 1 Different Result](./picture/tdd_ts_study_026_rule_different_result.png)

### ルール1：**結論（期待値）が変わる例**を選ぶ

同じ結果になる例を追加しても、ベタ実装が壊れない＝一般化が起きない😿
👉「送料500円」→ 次は「送料0円」みたいに、**結果が変わる**のが強い💥

![Rule 2 One Variable](./picture/tdd_ts_study_026_rule_one_variable.png)

### ルール2：**変える要素は1つだけ**

いきなり「境界＋例外＋丸め」みたいに盛ると、どこで壊れたか分からなくなる🥺
👉 2例目は “最小の差分” にするのがコツ🎯

### ルール3：**境界（しきい値）を狙うと当たりやすい**

「◯円以上なら無料」みたいな仕様って多いよね🧾
👉 2例目を **ちょうど境界**に置くと、最小の追加で一般化できる💡

---

## 🧪 ハンズオン：送料無料ラインの計算（三角測量の定番）📦✨

### お題：送料を決める関数

* 小計が **3000円以上** → 送料 **0円** 🆓
* 小計が **3000円未満** → 送料 **500円** 🚚

### ① まず1本目：未満なら500円（ここはベタでOK）🩹

**テスト**（1本目）👇

```ts
import { describe, it, expect } from "vitest";
import { calcShippingFee } from "../src/shipping";

describe("calcShippingFee", () => {
  it("小計が送料無料ライン未満なら送料は500円", () => {
    expect(calcShippingFee(2500)).toBe(500);
  });
});
```

**実装**（仮実装）👇
「とにかく通す」だけ✨

```ts
export function calcShippingFee(subtotalYen: number): number {
  return 500; // 仮実装🩹
}
```

ここまででOK！気持ちよくGreen🎉

---

![Boundary Break](./picture/tdd_ts_study_026_boundary_break.png)

### ② 2本目のテスト：境界をまたいで「0円」を要求する🆓💥

ここが **三角測量のキモ**📐✨
“同じ500円”じゃなくて、**結果が変わる例**を入れるよ！

```ts
import { describe, it, expect } from "vitest";
import { calcShippingFee } from "../src/shipping";

describe("calcShippingFee", () => {
  it("小計が送料無料ライン未満なら送料は500円", () => {
    expect(calcShippingFee(2500)).toBe(500);
  });

  it("小計が送料無料ライン以上なら送料は0円", () => {
    expect(calcShippingFee(3000)).toBe(0);
  });
});
```

この時点で、さっきの仮実装は確実に落ちるよね😄（ずっと500返してるから）

---

![Generalization Step](./picture/tdd_ts_study_026_generalization_step.png)

### ③ 最小の一般化：条件分岐にする（必要な分だけ）🌿

「2つの点」がそろったから、ここで一般化するよ📐✨

```ts
const FREE_SHIPPING_THRESHOLD_YEN = 3000;
const SHIPPING_FEE_YEN = 500;

export function calcShippingFee(subtotalYen: number): number {
  if (subtotalYen >= FREE_SHIPPING_THRESHOLD_YEN) return 0;
  return SHIPPING_FEE_YEN;
}
```

はい、これで2本ともGreen✅🎉
**ベタ実装→2例目で破壊→最小一般化**の流れ、これが三角測量だよ🫶

---

## 🔍 仕上げの“確認テスト”（任意）🧷✨

三角測量の主役は「2例目」だけど、**境界のちょい下**を押さえると安心感UP💕

```ts
it("小計が境界の1円下なら送料は500円", () => {
  expect(calcShippingFee(2999)).toBe(500);
});
```

「境界の扱い」が仕様としてハッキリするよ📘✨

---

![AI Generator](./picture/tdd_ts_study_026_ai_generator.png)

## 🤖 AIの使いどころ（ズルじゃないよ！）😎💞

AIは **“次の一手を小さくする”** のがめちゃ得意！✨

### ✅ 使えるプロンプト例

* 「今の実装（仮実装）が通っちゃうので、**最小の2例目**を3つ提案して。期待値も書いて」
* 「2例目を追加して落ちた。**最小の変更**で通す実装案を出して（読みやすさ優先）」
* 「境界値テスト、**入れすぎずに安心できる本数**を提案して」

※“仕様そのもの”をAIに決めさせるんじゃなくて、**選択肢を増やす係**にするのが安定だよ🤖✨

---

![Anti-Pattern Too Much](./picture/tdd_ts_study_026_anti_pattern_too_much.png)

## ✅ ありがちな失敗あるある（先に潰そ）🧯💥

* ❌ **2例目が弱い**（結果が同じ）
  → 仮実装が壊れず、一般化が起きない😿
* ❌ **2例目で盛りすぎ**（要素を2つ以上変える）
  → どこを直せばいいか迷子になる🌀
* ❌ **一般化しすぎ**
  → 未来の仕様まで勝手に想像して複雑化…😵
  → “今のテストが通る最小”だけでOK👌

---

## ✅ チェックリスト（できたら合格🎀）

* [ ] 1本目は仮実装でも通せた
* [ ] 2本目は **期待値が変わる**例を選べた
* [ ] 実装の変更は **最小の一般化**で済ませた
* [ ] （任意）境界の1円下/上など、仕様が明確になった

---

## 🧠 おまけ：2026年1月時点の“最新メモ”📌✨

* Node.js は **v24 が Active LTS**、v22/v20 は Maintenance LTS という扱いになってるよ🟩 ([Node.js][2])
* TypeScript は GitHub上の最新リリースが **5.9.3**（2025-10-01）になってるよ🧩 ([GitHub][3])
* Vitest は npm 上で **4.0.17** が最新として表示されてるよ🧪 ([NPM][4])
* TypeScript 6.0/7.0 の進捗も公式ブログで継続共有されてるよ（“橋渡しリリース”の話など）📝 ([Microsoft for Developers][5])

---

次の第27章（明白な実装）では、「三角測量をやらずに最初から素直に書いてOKな場面」も整理して、使い分けができるようにするよ🌼✨

[1]: https://stanislaw.github.io/2016-01-25-notes-on-test-driven-development-by-example-by-kent-beck.html?utm_source=chatgpt.com "Notes on \"Test-Driven Development by Example\" by Kent ..."
[2]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
[3]: https://github.com/microsoft/typescript/releases "Releases · microsoft/TypeScript · GitHub"
[4]: https://www.npmjs.com/package/vitest?utm_source=chatgpt.com "vitest"
[5]: https://devblogs.microsoft.com/typescript/progress-on-typescript-7-december-2025/?utm_source=chatgpt.com "Progress on TypeScript 7 - December 2025"
