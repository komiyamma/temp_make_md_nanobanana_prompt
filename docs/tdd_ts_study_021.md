# 第21章：テストデータ最小化（Arrangeを軽く）🧸✨

![最小限のテストデータ](./picture/tdd_ts_study_021_toy_doll.png)

この章は「テストが読みにくい」「準備（Arrange）が長すぎてやる気が消える😭」を救う章だよ〜！
**TDDが続くかどうかは、Arrangeを軽くできるかで決まる**と言っても過言じゃない✊💕

---

## 🎯 この章のゴール

* Arrange（準備）を**半分の行数**にできる✂️✨
* “意味のある値だけ”で、**テストが読み物**になる📘
* もしデータが重いなら、**型/入力の形を小さくする**発想が持てる🧠🧩

---

## 📚 2026の前提メモ（超短く）

* TypeScript は **5.9系**が最新ラインのひとつ（2026年1月時点）だよ🧠✨ ([GitHub][1])
* Vitest は **4系が中心**で、移行ガイドも4.0向けが整ってる🧪 ([Vitest][2])
* VS Code では Vitest 拡張で **Testingビュー連携**できるよ🔎🧪 ([GitHub][3])

（※この章の本題は「テストデータの作り方」なので、バージョンの話はここまで！🙂）

---

## 😵 Arrangeが重くなる典型パターン（あるある）

1. **関係ない項目まで全部埋めてる**
2. **巨大なfixture（JSON）を読み込んでる**（ユニットテストなのに…）
3. **ランダム値や現在時刻が混ざってる**（読みづらい＋不安定の元）
4. **「とりあえず本物っぽく」**でデータを盛りすぎ🍰

👉 目的は「リアルっぽさ」じゃなくて、**仕様を説明すること**だよ📘✨

---

## ✅ まず覚える合言葉（超大事）🪄

### 🧸「Arrangeはデータ入力じゃなくて、物語（ストーリー）」

* **なぜその値なの？**が説明できる値だけ置く
* 余計な情報は、読者の脳内メモリを奪う😵‍💫

### ✂️「最小」＝「少ない」じゃなくて「意味が濃い」

* `1`、`0`、`-1`、`100` みたいな “雑な数字” だけだと意味が薄い
* 例：送料の境界なら `4999` と `5000` が意味が濃い✨

---

## 🧠 テストデータ最小化の3つの技（これだけで強い）💪✨

### 技①：関係あるフィールドだけにする（まず削る）✂️

「このテストで使う情報って何？」をはっきりさせよう🙂
**使ってないフィールドは作らない！**

---

### 技②：入力の型（形）を小さくする（設計の最短ルート）🧩✨

もし毎回「でっかいOrder全部」を作ってるなら、
**関数が受け取るべき情報がデカすぎる**可能性が高いよ👀

👉 対策：`Pick` を使って **必要な情報だけ受け取る関数**にする！

---

### 技③：データビルダー（デフォルト＋上書き）で書く🧸🛠️

毎回オブジェクト手書きで疲れるならこれ！

* 基本は “普通のデータ” を自動で用意
* テストごとの差分だけ上書き

---

## 🧪 ハンズオン：Arrangeを“半分”にする練習✂️✨

## 0) お題：送料無料判定をテストする📦

「日本国内で、会員なら3000円以上で送料無料。ゲストは5000円以上」みたいなルールにするね🙂

---

## 1) **ダメな例**（Arrangeが重い😭）

```ts
// isFreeShipping.test.ts
import { describe, it, expect } from "vitest";
import { isFreeShipping, Order } from "./isFreeShipping";

describe("isFreeShipping", () => {
  it("Gold会員で3000円以上なら送料無料", () => {
    const order: Order = {
      id: "order-2026-0001",
      createdAt: new Date("2026-01-01T10:00:00Z"),
      customer: {
        id: "user-999",
        name: "Hanako",
        email: "hanako@example.com",
        address: {
          country: "JP",
          prefecture: "Tokyo",
          city: "Chiyoda",
          line1: "1-1-1",
          postalCode: "100-0001",
        },
        tier: "Gold",
      },
      items: [
        { sku: "A001", name: "Pen", priceYen: 1500, qty: 1 },
        { sku: "B001", name: "Note", priceYen: 1600, qty: 1 },
      ],
      totalYen: 3100,
      shipping: { country: "JP", method: "Standard", feeYen: 500 },
      note: "please deliver after 18:00",
      metadata: { source: "web", campaign: "winter" },
    };

    expect(isFreeShipping(order)).toBe(true);
  });
});
```

✅ 通るけど…
😵「何が重要？」が埋もれるし、読むのに疲れる！

---

## 2) **改善①：関数の入力を小さくする（Pickで必要な情報だけ）**🧩✨

```ts
// isFreeShipping.ts
export type MemberTier = "Guest" | "Member" | "Gold";

export type FreeShippingInput = {
  totalYen: number;
  shippingCountry: "JP" | "US";
  memberTier: MemberTier;
};

export function isFreeShipping(input: FreeShippingInput): boolean {
  if (input.shippingCountry !== "JP") return false;

  const threshold = input.memberTier === "Guest" ? 5000 : 3000;
  return input.totalYen >= threshold;
}
```

🎉 これだけで、テストのArrangeが激軽になる！

---

## 3) **改善②：最小データでテストを書く（意味のある値で）**🧸✨

```ts
// isFreeShipping.test.ts
import { describe, it, expect } from "vitest";
import { isFreeShipping } from "./isFreeShipping";

describe("isFreeShipping", () => {
  it("Gold会員で3000円以上なら送料無料", () => {
    expect(
      isFreeShipping({ totalYen: 3000, shippingCountry: "JP", memberTier: "Gold" })
    ).toBe(true);
  });

  it("Guestは5000円未満だと送料無料にならない（境界の1つ手前）", () => {
    expect(
      isFreeShipping({ totalYen: 4999, shippingCountry: "JP", memberTier: "Guest" })
    ).toBe(false);
  });
});
```

✨ Arrangeが「仕様の説明」になったよね？
しかも `4999` は “意味がある” 値だから強い💪💕

---

## 🧸 さらにラクに：データビルダーで差分だけ書く🛠️✨

「毎回 `shippingCountry: "JP"` 書くのめんどい〜😫」ってなったら、ビルダー！

```ts
// testData.ts
import type { FreeShippingInput } from "./isFreeShipping";

export function aFreeShippingInput(
  overrides: Partial<FreeShippingInput> = {}
): FreeShippingInput {
  return {
    totalYen: 3000,
    shippingCountry: "JP",
    memberTier: "Member",
    ...overrides,
  };
}
```

```ts
// isFreeShipping.test.ts
import { describe, it, expect } from "vitest";
import { isFreeShipping } from "./isFreeShipping";
import { aFreeShippingInput } from "./testData";

describe("isFreeShipping", () => {
  it("Guestは5000円以上で送料無料", () => {
    const input = aFreeShippingInput({ memberTier: "Guest", totalYen: 5000 });
    expect(isFreeShipping(input)).toBe(true);
  });
});
```

✅ “普通の入力”を1個決めると、テストがどんどん速く書けるよ🔁✨

---

## 🧠 どこまで抽出していいの？（ルールあるよ📏）

## 📏 ルール・オブ・スリー（3回出たら抽出）✨

* 1回だけ → **その場にベタ書き**（読みやすさ優先）
* 2回 → まだ我慢（早すぎ共通化は読みにくくなる）
* 3回 → **ビルダー/ヘルパー化**を検討✅

---

## 🤖 AIの使い方（この章のコツ）✨

AIに頼む時は、こう言うと成功しやすいよ💕

### ✅プロンプト例①：Arrange削り

* 「このテストのArrangeを**半分の行数**にして。**仕様が伝わる値**だけ残して。意味のないフィールドは削除してOK」

### ✅プロンプト例②：値の意味を強く

* 「このテストに出てくる数字を、**境界が分かる値**に置き換えて（例：4999/5000みたいに）」

### ✅プロンプト例③：ビルダー導入

* 「このテスト群に合う `aXxx(overrides)` 形式のテストデータビルダーを作って。**デフォルトは“普通のケース”**にして」

⚠️ ただし：AIが“リアルっぽさ”でデータを盛り始めたら、即ストップ🛑😆
「最小で！最小で！」って言ってOKだよ💕

---

## ✅ チェックリスト（章の合格ライン）🎓✨

* [ ] Arrangeが長いテストを1つ選んで、**行数を半分**にできた✂️
* [ ] 使ってないフィールドを作ってない🙅‍♀️
* [ ] 値を「なぜその値？」って説明できる（境界/意味がある）🧠
* [ ] でかい型を受け取っていたら、`Pick` などで **入力の形を小さく**できた🧩
* [ ] 抽出はやりすぎてなくて、テストが読みやすい📘✨

---

## ✅ ミニ宿題（15〜25分）🍀

1. 自分のテスト（またはこの章の例）で、**Arrangeが重いテストを1本**選ぶ
2. まずは **削れるフィールドを削る**✂️
3. まだ重いなら **入力型を小さくする（Pick / 新しいInput型）**🧩
4. 3本以上同じArrangeが出たら **ビルダー化**🧸🛠️

---

次の第22章は、ここで軽くしたArrangeを武器にして、**パラメータ化テスト（ケース増殖の味方）🔁**へ進むよ〜！🧪✨

[1]: https://github.com/microsoft/typescript/releases?utm_source=chatgpt.com "Releases · microsoft/TypeScript"
[2]: https://vitest.dev/blog/vitest-4?utm_source=chatgpt.com "Vitest 4.0 is out!"
[3]: https://github.com/vitest-dev/vscode?utm_source=chatgpt.com "vitest-dev/vscode: VS Code extension for Vitest"
