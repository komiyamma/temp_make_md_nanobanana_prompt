# 第32章：仕様追加の手順（壊れない増やし方）➕

![仕様の追加](./picture/tdd_ts_study_032_plus_sign.png)

今日は「**機能追加するときに、前の仕様を壊さない増やし方**」を、手順ごとに体にしみ込ませるよ〜！🥰
TDDって「新規開発」だけじゃなくて、**仕様追加（変更）にめちゃ強い**のが最高ポイントなんだよね💪💕

なお今どきの組み合わせとして、TypeScript は **5.9 系**、テストは **Vitest 4 系**、Node は **24 LTS 系**あたりが現役ど真ん中だよ（2026-01-19 時点）🧑‍💻✨ ([typescriptlang.org][1])

---

## 🎯 この章のゴール

* 仕様を1個追加するときに、**壊さず・迷子にならず**進められる🧭✨
* 「1仕様＝1〜2テスト」のリズムで、**増やしても整理され続ける**🧹🧡
* 追加が続いても、次の章（決定表）につながる形で「限界サイン」が分かる👃🚨

---

## 😵 仕様追加で壊れる “あるある” と対策

### あるある①：コードを先にいじっちゃう✋💥

* 変更の途中で「何が正しい状態か」分からなくなる…
  ✅ 対策：**先にテストで“追加後の約束”を固定**してから触る！

### あるある②：変更がデカすぎる📦💦

* 追加 + リファクタ + ついで修正…で爆発🔥
  ✅ 対策：**1回の追加は“最小の差分”**（ベイビーステップの出番👶）

### あるある③：既存テストが “実装の写し” で守ってくれない🫠

✅ 対策：テストは「**振る舞い（入力→出力）**」中心に✨

---

## ✅ 壊れない仕様追加：鉄板の5ステップ 🧱✨

1. **追加する仕様を1個だけ決める**（今日はコレ！って絞る）🎯
2. **代表ケースのテストを1本**書く（まず Red）🔴
3. **最小実装で Green**（賢くしない！）🟢
4. **境界テストを1本足す**（必要なら）🧷
5. **Refactor**（読みやすくして、次の追加に備える）🧹✨

> コツ：コミットするなら
> **test → feat → test(境界) → feat → refactor** みたいに分けると神👼✨

---

## 🧪 手を動かす：カフェ会計に「割引」を段階追加しよう ☕️🧾➕

ここでは、すでにある「合計計算」に、仕様を1個ずつ増やすよ〜！💕

### 今日の追加順（わざと “簡単→やや難” にする）✨

* 仕様A：クーポン `"OFF200"` があれば **200円引き**（ただし0円未満にはしない）🎟️
* 仕様B：学生割 `"STUDENT10"` は **10%引き（切り捨て）** 🧑‍🎓
* 仕様C：割引上限 `"maxDiscount"` で **最大500円まで**🧢

---

## 0) 現状の最小（ベースライン）を用意する 🌱

### `src/checkout.ts`（最初は割引なし）

```ts
export type Money = number;

export type Item = {
  name: string;
  price: Money;
  qty?: number;
};

export function calcTotal(items: Item[]): Money {
  return items.reduce((sum, item) => {
    const qty = item.qty ?? 1;
    return sum + item.price * qty;
  }, 0);
}
```

### `tests/checkout.test.ts`（既存仕様のテスト）

```ts
import { describe, it, expect } from "vitest";
import { calcTotal } from "../src/checkout";

describe("calcTotal（割引なし）", () => {
  it("合計金額を返す", () => {
    const total = calcTotal([
      { name: "coffee", price: 450 },
      { name: "sand", price: 600 },
    ]);
    expect(total).toBe(1050);
  });

  it("数量があれば掛け算される", () => {
    const total = calcTotal([{ name: "cookie", price: 120, qty: 3 }]);
    expect(total).toBe(360);
  });
});
```

ここまでが “守られてる世界” 🌍🛡️
この状態を壊さずに、仕様を増やすよ〜！✨

---

## ✅ 仕様A：クーポン "OFF200"（200円引き、0円未満は0）🎟️✨

## 1) まずはテストを1本（代表ケース）🔴

「割引が効いてほしい世界」を先に書いちゃう💕

```ts
import { describe, it, expect } from "vitest";
import { calcTotal } from "../src/checkout";

describe("calcTotal（割引あり）", () => {
  it("クーポン OFF200 で200円引き", () => {
    const total = calcTotal(
      [{ name: "coffee", price: 450 }, { name: "sand", price: 600 }],
      { kind: "coupon", code: "OFF200" }
    );
    expect(total).toBe(850);
  });
});
```

当然いまは落ちるよね！それでOK〜！🔴😆
（**落ちること＝仕様が追加された証拠**）

## 2) 最小で通す（Green）🟢

実装は “賢くしない” が正義だよ💪✨

```ts
export type Money = number;

export type Item = {
  name: string;
  price: Money;
  qty?: number;
};

export type Discount =
  | { kind: "coupon"; code: "OFF200" };

export function calcTotal(items: Item[], discount?: Discount): Money {
  const subtotal = items.reduce((sum, item) => {
    const qty = item.qty ?? 1;
    return sum + item.price * qty;
  }, 0);

  if (!discount) return subtotal;

  if (discount.kind === "coupon" && discount.code === "OFF200") {
    return Math.max(0, subtotal - 200);
  }

  return subtotal;
}
```

はい、まずはこれでOK〜！🟢🎉
“未来の拡張” は今やらない！（次の仕様で自然に育つから🌱）

## 3) 境界テストを1本（0円未満防止）🧷

「落とし穴だけ」追加するのが上手い増やし方😎

```ts
it("OFF200 でも0円未満にはならない", () => {
  const total = calcTotal([{ name: "water", price: 100 }], {
    kind: "coupon",
    code: "OFF200",
  });
  expect(total).toBe(0);
});
```

---

## ✅ 仕様B：学生割 "STUDENT10"（10%引き・切り捨て）🧑‍🎓✨

## 1) 代表ケーステストを追加（Red）🔴

```ts
it("学生割 STUDENT10 で10%引き（切り捨て）", () => {
  const total = calcTotal([{ name: "lunch", price: 1050 }], {
    kind: "student",
    code: "STUDENT10",
  });
  // 1050 * 0.9 = 945（端数が出るケースは次でやる）
  expect(total).toBe(945);
});
```

## 2) 最小実装で通す（Green）🟢

```ts
export type Discount =
  | { kind: "coupon"; code: "OFF200" }
  | { kind: "student"; code: "STUDENT10" };

export function calcTotal(items: Item[], discount?: Discount): Money {
  const subtotal = items.reduce((sum, item) => {
    const qty = item.qty ?? 1;
    return sum + item.price * qty;
  }, 0);

  if (!discount) return subtotal;

  if (discount.kind === "coupon" && discount.code === "OFF200") {
    return Math.max(0, subtotal - 200);
  }

  if (discount.kind === "student" && discount.code === "STUDENT10") {
    const discounted = Math.floor(subtotal * 0.9);
    return Math.max(0, discounted);
  }

  return subtotal;
}
```

## 3) 境界テスト：端数切り捨て🧷

```ts
it("学生割は端数切り捨て", () => {
  const total = calcTotal([{ name: "snack", price: 101 }], {
    kind: "student",
    code: "STUDENT10",
  });
  // 101 * 0.9 = 90.9 → 90
  expect(total).toBe(90);
});
```

---

## ✅ 仕様C：割引上限 maxDiscount（最大500円）🧢✨

ここが “仕様追加が怖くなる” ポイントだから、手順で守るよ〜！🛡️💕

## 1) まずテスト（Red）🔴

学生割が強すぎるケースを作る（上限が効いてほしい）✨

```ts
it("学生割は上限 maxDiscount を超えない", () => {
  const total = calcTotal([{ name: "party", price: 10000 }], {
    kind: "student",
    code: "STUDENT10",
    maxDiscount: 500,
  });
  // 本来10%引きなら 1000円引きだけど、上限500円なので
  expect(total).toBe(9500);
});
```

## 2) 最小実装で通す（Green）🟢

ここでやっと「割引額」という考えが欲しくなるよね？
でも一気に設計しないで、**最小の抽出**だけやるよ🧸✨

```ts
export type Discount =
  | { kind: "coupon"; code: "OFF200" }
  | { kind: "student"; code: "STUDENT10"; maxDiscount?: Money };

function clampDiscount(discount: Money, maxDiscount?: Money): Money {
  if (maxDiscount == null) return discount;
  return Math.min(discount, maxDiscount);
}

export function calcTotal(items: Item[], discount?: Discount): Money {
  const subtotal = items.reduce((sum, item) => {
    const qty = item.qty ?? 1;
    return sum + item.price * qty;
  }, 0);

  if (!discount) return subtotal;

  if (discount.kind === "coupon" && discount.code === "OFF200") {
    return Math.max(0, subtotal - 200);
  }

  if (discount.kind === "student" && discount.code === "STUDENT10") {
    const rawDiscount = Math.floor(subtotal * 0.1); // “割引額”で考える
    const applied = clampDiscount(rawDiscount, discount.maxDiscount);
    return Math.max(0, subtotal - applied);
  }

  return subtotal;
}
```

---

## 🧹 このタイミングでの “ちょうどいい” リファクタ（Refactor）✨

仕様を3つ足したら、ちょっと `if` が増えてきたよね？👀
ここでやるリファクタは **“次の仕様追加がラクになる分だけ”** が正解💮

おすすめはこれ👇

* `calcTotal` の中から **割引計算だけ**を関数に逃がす
* `subtotal` は先に出す（これはもうOK）
* まだ「ルール表」にはしない（それは次章：決定表でやる🗂️✨）

例：

```ts
function calcDiscount(subtotal: Money, discount: Discount): Money {
  if (discount.kind === "coupon" && discount.code === "OFF200") {
    return Math.min(200, subtotal);
  }
  if (discount.kind === "student" && discount.code === "STUDENT10") {
    const raw = Math.floor(subtotal * 0.1);
    return clampDiscount(raw, discount.maxDiscount);
  }
  return 0;
}

export function calcTotal(items: Item[], discount?: Discount): Money {
  const subtotal = items.reduce((sum, item) => sum + item.price * (item.qty ?? 1), 0);
  if (!discount) return subtotal;
  return subtotal - calcDiscount(subtotal, discount);
}
```

この形にしておくと、次の章で「条件×結果」を表にしていくときに超ラクになるよ〜！🥳🗂️

---

## 🤖 AIの使いどころ（この章はここが強い！）✨

### 使ってOK（むしろ強い）💪🤖

* 「代表ケース1つ」と「境界ケース1つ」を提案させる
* “壊れそうポイント” の指摘（0未満、端数、上限、未対応コード…）

### 使い方テンプレ（そのままコピペでOK）📝💕

* 「この仕様追加で、代表ケース1つ＋境界ケース1つを提案して。期待値も書いて」
* 「この差分で、既存仕様を壊す可能性がある点を3つ挙げて」
* 「テスト名を、仕様が読める日本語に3案出して」

### 注意（やりがち）⚠️🥺

* AIに「設計ごと全部作り直して！」はダメ🙅‍♀️
  → 変更範囲が増えて、TDDの良さ（安全運転）が消えちゃう💦

---

## ✅ チェックリスト（合格ライン）🎉

* [ ] 追加仕様ごとに **Red→Green→Refactor** が回ってる🚦
* [ ] **代表テスト1本 + 境界1本（必要なら）** で増やしてる🧷
* [ ] 既存テストが落ちた時に「なぜ？」が説明できる🗣️
* [ ] `if` が増えたら「次章（決定表）行きかも👃🚨」が分かる
* [ ] 追加後に、コードが前より “次の追加に優しい”🌱✨

---

## 🌟 次章へのつなぎ（ちょい予告）🗂️✨

仕様が増えると `if` が増えるのは自然！😆
でも一定ラインを超えると「条件の抜け漏れ」が出やすくなる…🕳️💦
そこで次の **第33章：決定表で整理（if地獄回避）** が効いてくるよ〜！🎉

---

次、もしこの章の理解を “ガチ固め” したいなら、ここまでのコードに **「クーポンと学生割は併用できない」** みたいな仕様を1個だけ足してみよっか？😈➕（めっちゃ学べるやつ！）

[1]: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-9.html?utm_source=chatgpt.com "Documentation - TypeScript 5.9"
