# 第15章：OCP実戦（料金計算を拡張できる形へ）💰🧾

この章では「割引が増えても、料金計算の本体をほぼ触らずに追加できる」形にしていくよ〜！😊🎟️
今のTypeScriptは **5.9** が最新ラインとして整理されてるので、型機能も安心して使ってOKだよ✨ ([TypeScript][1])
（ついでにNode.jsは **LTS（長期サポート）** を選ぶのが安全運用の王道だよ〜🛡️）([Node.js][2])
テストは **Vitest 4系** が現行メジャーとして使いやすいよ🧪⚡ ([vitest.dev][3])


![Lego Tower](./picture/solid_ts_study_015_lego_tower.png)

---

## 今日のゴール🎯✨

* 割引が増えても **if/switch地獄** にならない💥🙅‍♀️
* 「割引の追加」は **新しいクラス（または関数）を足すだけ** に寄せる🌱
* 料金計算の本体（コア）は **変更しにくく**、拡張だけしやすくする🔁🧠

---

## まず“地獄の未来”を見よう👀💦（ダメ実装）

「割引タイプでswitchして計算」って最初はラクなんだけど…
割引が増えるほど **毎回ここを編集** することになるよね😵‍💫

```ts
type DiscountType = "NONE" | "STUDENT" | "RAINY" | "SET";

export function calcTotalBad(subtotalYen: number, discount: DiscountType): number {
  switch (discount) {
    case "STUDENT":
      return Math.max(0, subtotalYen - 300); // 学割300円引き
    case "RAINY":
      return Math.floor(subtotalYen * 0.9); // 雨の日10%OFF
    case "SET":
      return Math.max(0, subtotalYen - 200); // セット割200円引き（仮）
    case "NONE":
    default:
      return subtotalYen;
  }
}
```

### これの困りごと😢🌀

* 割引が増えるたび **calcTotalBadを編集**（＝既存の重要コードを触る）✋💥
* 修正でバグると **全注文が壊れる**（影響範囲デカすぎ）😱
* “割引ロジック”が増えるほど **テストも読みづらい** 🧫📉

👉 ここをOCPで直していくよ〜！💪✨

---

## OCPの考え方（超ざっくり）🚪✨

**「拡張はOK！でも“既存の重要なところ”はなるべく触らないでね」**って感じ😊
だから「変更されやすいところ（割引）」を **差し替え口** に分離するよ🎯🔁

---

## 料金計算の“設計方針”を決める🧭✨

今回の軸はこれ👇

* **変わりやすい**：割引ルール（学割・雨の日割・セット割…増える）🎟️☔🍱
* **変わりにくい**：合計計算の流れ（小計→割引適用→合計）🧾

なので…

✅ 合計計算は **ルールの配列を順番に適用するだけ** にする
✅ 割引は **ルールとして外に増やせる** ようにする

---

## 1) ドメインモデル（最小セット）を用意📦✨

「値段は小数にしない」でいくよ（浮動小数の誤差こわい😇）
日本円は整数で扱うのが楽ちん💴

```ts
export type Yen = number;

export type Item = {
  sku: string;
  name: string;
  unitPriceYen: Yen;
  quantity: number;
};

export type PricingContext = {
  items: Item[];
  isStudent: boolean;
  isRainyDay: boolean;
};
```

小計計算も用意〜🧮✨

```ts
import type { PricingContext, Yen } from "./types";

export function calcSubtotalYen(ctx: PricingContext): Yen {
  return ctx.items.reduce((sum, item) => sum + item.unitPriceYen * item.quantity, 0);
}
```

---

## 2) “拡張ポイント”＝PricingRule を作る🧩🔁

ここが超大事！✨
「割引ルールはこの形で追加してね」っていう **約束（interface）** を作るよ😊

```ts
import type { PricingContext, Yen } from "./types";

export interface PricingRule {
  readonly name: string;
  apply(currentTotalYen: Yen, ctx: PricingContext): Yen;
}
```

---

## 3) 料金計算のコア（ここは“閉じる”）🛡️✨

PricingRuleの配列を **reduceで順番に適用** するだけにするよ〜！

```ts
import type { PricingContext, Yen } from "./types";
import { calcSubtotalYen } from "./subtotal";
import type { PricingRule } from "./rule";

export class PriceCalculator {
  constructor(private readonly rules: readonly PricingRule[]) {}

  calcTotal(ctx: PricingContext): Yen {
    const subtotal = calcSubtotalYen(ctx);

    const total = this.rules.reduce((current, rule) => {
      return rule.apply(current, ctx);
    }, subtotal);

    return Math.max(0, total); // 念のためマイナス禁止
  }
}
```

✅ ここがポイント：**割引が増えても PriceCalculator は変更しない** 🎉
（“ルールを追加する”だけで拡張できる！）

---

## 4) 割引ルールを“追加するだけ”で増やす🎟️✨

### 学割（固定300円引き）👩‍🎓💖

```ts
import type { PricingContext, Yen } from "./types";
import type { PricingRule } from "./rule";

export class StudentDiscountRule implements PricingRule {
  readonly name = "StudentDiscount";

  apply(currentTotalYen: Yen, ctx: PricingContext): Yen {
    if (!ctx.isStudent) return currentTotalYen;
    return Math.max(0, currentTotalYen - 300);
  }
}
```

### 雨の日（10%OFF）☔✨

```ts
import type { PricingContext, Yen } from "./types";
import type { PricingRule } from "./rule";

export class RainyDayDiscountRule implements PricingRule {
  readonly name = "RainyDayDiscount";

  apply(currentTotalYen: Yen, ctx: PricingContext): Yen {
    if (!ctx.isRainyDay) return currentTotalYen;
    return Math.floor(currentTotalYen * 0.9);
  }
}
```

### セット割（例：ドリンク+サンドの組み合わせで200円引き）🥪🥤🎉

「組み合わせ割引」みたいな **ちょい複雑** も、ルール側に閉じ込められるのが嬉しいところ！

```ts
import type { PricingContext, Yen } from "./types";
import type { PricingRule } from "./rule";

function countSku(ctx: PricingContext, sku: string): number {
  return ctx.items
    .filter(i => i.sku === sku)
    .reduce((sum, i) => sum + i.quantity, 0);
}

export class SetDiscountRule implements PricingRule {
  readonly name = "SetDiscount";

  // 例：COFFEE と SAND が1セットで200円引き
  apply(currentTotalYen: Yen, ctx: PricingContext): Yen {
    const coffee = countSku(ctx, "COFFEE");
    const sand = countSku(ctx, "SAND");
    const sets = Math.min(coffee, sand);
    const discount = sets * 200;

    return Math.max(0, currentTotalYen - discount);
  }
}
```

---

## 5) “組み立て”だけで拡張する（Composition Root）🧩✨

最後に「使うルール一覧」を作って注入するだけ！

```ts
import { PriceCalculator } from "./price-calculator";
import { StudentDiscountRule } from "./rule-student";
import { RainyDayDiscountRule } from "./rule-rainy";
import { SetDiscountRule } from "./rule-set";
import type { PricingContext } from "./types";

const calculator = new PriceCalculator([
  new StudentDiscountRule(),
  new RainyDayDiscountRule(),
  new SetDiscountRule(),
]);

const ctx: PricingContext = {
  items: [
    { sku: "COFFEE", name: "コーヒー", unitPriceYen: 450, quantity: 1 },
    { sku: "SAND", name: "サンド", unitPriceYen: 650, quantity: 1 },
  ],
  isStudent: true,
  isRainyDay: false,
};

console.log(calculator.calcTotal(ctx));
```

✅ 割引を追加したい？
→ **新しいRuleを1個作って、配列に足すだけ** 🎉🎉

---

## 6) テストで「拡張しても壊れない」を確保🧪✅

Vitest 4系でサクッといくよ〜！⚡ ([vitest.dev][3])

### ルール単体テスト

```ts
import { describe, it, expect } from "vitest";
import { StudentDiscountRule } from "../src/rule-student";

describe("StudentDiscountRule", () => {
  it("学生なら300円引き", () => {
    const rule = new StudentDiscountRule();
    const total = rule.apply(1000, { items: [], isStudent: true, isRainyDay: false });
    expect(total).toBe(700);
  });

  it("学生じゃないなら変化なし", () => {
    const rule = new StudentDiscountRule();
    const total = rule.apply(1000, { items: [], isStudent: false, isRainyDay: false });
    expect(total).toBe(1000);
  });
});
```

### 合成（パイプライン）テスト

```ts
import { describe, it, expect } from "vitest";
import { PriceCalculator } from "../src/price-calculator";
import { StudentDiscountRule } from "../src/rule-student";
import { RainyDayDiscountRule } from "../src/rule-rainy";

describe("PriceCalculator", () => {
  it("小計→学割→雨割の順で適用される", () => {
    const calc = new PriceCalculator([new StudentDiscountRule(), new RainyDayDiscountRule()]);
    const total = calc.calcTotal({
      items: [{ sku: "COFFEE", name: "コーヒー", unitPriceYen: 1000, quantity: 1 }],
      isStudent: true,
      isRainyDay: true,
    });

    // 小計1000 → 学割で700 → 雨割10%OFFで630
    expect(total).toBe(630);
  });
});
```

💡「ルールの順番で結果が変わる」ことがあるから、**順番を仕様として固定**するか、**ルールを“順序なし設計”にするか**は設計判断だよ〜🤔✨
（初心者段階では「順番固定」で全然OK！）

---

## 7) OCPチェックリスト✅🧠

新しい割引（例：**誕生日割** 🎂、**初回注文割** 🆕、**会員ランク割** 👑）を追加するとき…

* [ ] PriceCalculator を編集しない（理想）🙆‍♀️
* [ ] 既存のルールも編集しない（理想）🙆‍♀️
* [ ] やることは「Ruleを新規作成＋登録」だけ✨
* [ ] テストは「新Ruleのテストを足す」だけ🧪➕

これができたら、OCPの勝ち〜！🏆🎉

---

## 8) AI（Copilot/Codex系）に頼るときのコツ🤖📝✨

### 便利プロンプト例（そのまま投げてOK）💬

* 「PricingRule interfaceに従って “BirthdayDiscountRule” を実装して。入力は PricingContext、割引は合計から200円引き。テストもVitestで書いて」🎂🧪
* 「SetDiscountRuleの仕様を、COFFEE+SANDだけじゃなく TEA+CAKEも対象にして。読みやすくリファクタして」🍰🫖
* 「このルール適用順で不具合が出るケースある？境界値テスト案を出して」🧠🔍

### ただし注意⚠️

AIは“それっぽい嘘”も混ぜることあるから、
✅ **テスト** と ✅ **差分レビュー** は人間が握ろうね〜！👩‍💻🔍

---

## 9) ミニ課題（やってみよ〜！）🎒✨

### 課題A：誕生日割🎂（固定200円引き）

* `isBirthday: boolean` を PricingContext に追加して
* `BirthdayDiscountRule` を新規作成
* PriceCalculatorは **編集禁止** 🙅‍♀️（組み立てで追加するだけ！）

### 課題B：上限つき割引🧢（割引は最大500円まで）

* 雨の日割を「最大500円割引まで」に変更したい
  → 既存Ruleを修正してもOKだけど、できれば
  「RainyDayDiscountRuleV2」を新規追加して差し替える案も考えてみてね🤔✨

### 課題C：ルールの順序をテストで守る🔒

* 「学割→雨割」順を守りたいなら、順序が変わると落ちるテストを書いてみよう🧪💥

---

## まとめ🌸✨

* OCPは「**変わりやすいところに差し替え口を作る**」がコツ🎯
* 料金計算のコアは **ルールを適用するだけ** にすると強い🛡️
* 新割引は **Ruleを追加するだけ** に寄せられると、未来が平和〜🕊️💖

---

次の章（第16章）は、差し替えが増えたときに爆発しがちな **LSP（置換可能性）** に突入するよ〜！🔁🧩✨

[1]: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-9.html "TypeScript: Documentation - TypeScript 5.9"
[2]: https://nodejs.org/en/about/previous-releases "Node.js — Node.js Releases"
[3]: https://vitest.dev/blog/vitest-4 "Vitest 4.0 is out! | Vitest"
