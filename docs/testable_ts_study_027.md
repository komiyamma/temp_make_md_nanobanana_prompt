# 第27章：テストの粒度（ユニット/結合）と基本方針🍱🧪

![testable_ts_study_027_test_pyramid.png](./picture/testable_ts_study_027_test_pyramid.png)

## この章でできるようになること🎯✨* 「ここはユニットで守る？ 結合で守る？」を迷わず決められる🙂🔍


* **中心（ロジック）＝ユニットで速く大量に**、**外側（I/O）＝最小の結合で要所だけ**の型を作れる⚡🔌
* 同じ機能を **ユニットテスト版** と **結合テスト版** の両方で作れる💪🧪

---

## 1) 粒度ってなに？（テストの“距離感”）

📏🙂## ユニットテスト（Unit）

🍪* **小さい**：関数・クラス1個くらい


* **速い**：ミリ秒～数十ミリ秒で終わりやすい⚡
* **安定**：外部要因（ネット・ファイル・時刻）に揺れない🧊
* 主戦場：**中心（純粋ロジック）** 🏠✨

## 結合テスト（Integration）

🍱* **つなぎ目**を見る：境界（interface）をまたいで「配線が合ってる？」を確認🔌


* 例：Repository実装が本当に読み書きできる？DTO→Domain変換が合ってる？など🔁
* 主戦場：**外側（I/Oアダプタ）＋境界の変換** 🌍🧩

## E2E（必要なら）

🏔️* 画面やAPIを “ユーザー目線で最初から最後まで”


* 強いけど **遅い＆壊れやすい** ので数は絞るのがコツ😵‍💫

> テストはピラミッド型（ユニット多め・結合そこそこ・E2E少なめ）が王道だよ〜📐✨ ([TestRail | The Quality OS for QA Teams][1])

---

## 2) まずは基本方針を1枚で🍙📝## 基本方針（この講座の型）

✅1. **中心はユニットでガチガチに守る** 🏠🧪
2. **外側は“要所だけ”結合で守る** 🌍🔌
3. **外側のI/Oそのもの（ネット・本物DB）に毎回行かない**（速さと安定優先）🏃‍♀️🧊
4. 「バグが出やすい変換・境界・配線」を結合でピンポイントに刺す🎯✨

## 迷ったらこの質問🧠❓* **Q1**：これ、同じ入力で同じ出力になる？（副作用なし？）



  * YES → ユニット向き🍪
* **Q2**：これ、外部の都合（ファイル形式・HTTP・SQL・DTO）を扱ってる？

  * YES → 結合で要所確認🍱
* **Q3**：「配線ミスったら全部死ぬ」場所？（DI/compose/変換/設定）

  * YES → 結合で1本あると安心🔌✅

---

## 3) 2026のTypeScriptテスト事情（超ざっくり）

🧪🌈* **Vitest** は現代TS/ESM環境で人気で、4.0系が最新メジャー（2025-10-22に4.0発表）📦✨ ([Vitest][2])


* **Jest** も現役で、安定版は 30.0 系📦✨ ([Jest][3])
* Nodeは **24.x がActive LTS** として更新が続いてるよ（例：24.13.0は2026-01-13リリース）🟢🔧 ([Node.js][4])

この章のハンズオンは **Vitest前提の書き味** でいくね🙂🧪（Jestでも考え方は同じ！）

---

## 4) ハンズオン：同じ機能を「中心テスト」「結合テスト」で作る🙂🔁題材：**クーポン付き注文の合計金額** 🛒💰



* 中心：合計計算（純粋ロジック）
* 外側：クーポンをJSONファイルから読む（I/O）
* 境界：`CouponRepository` interface（差し替え点）

## 4-1) フォルダ構成（おすすめ）

📁✨* `src/core/` … 中心🏠


* `src/infra/` … 外側（I/O）🌍
* `tests/unit/` … ユニット🍪
* `tests/integration/` … 結合🍱

そしてVitestは **パスに含まれる文字でテストファイルを絞れる** よ（例：`vitest unit` みたいに）🔎 ([Vitest][5])

---

## 5) 実装：中心（core）

🏠✨## `src/core/types.ts

```ts
export type Money = number;

export type OrderLine = {
  sku: string;
  unitPrice: Money;
  qty: number;
};

export type Coupon =
  | { kind: "percent"; value: number } // 10 => 10%
  | { kind: "amount"; value: Money };  // 300 => 300円引き

export type CouponRepository = {
  getByCode(code: string): Promise<Coupon | null>;
};
```

## `src/core/calcTotal.ts`（純粋ロジック🍪）

```ts
import { Coupon, Money, OrderLine } from "./types";

export function calcSubtotal(lines: OrderLine[]): Money {
  return lines.reduce((sum, l) => sum + l.unitPrice * l.qty, 0);
}

export function applyCoupon(subtotal: Money, coupon: Coupon | null): Money {
  if (!coupon) return subtotal;

  if (coupon.kind === "percent") {
    const rate = coupon.value / 100;
    const discounted = subtotal * (1 - rate);
    return roundYen(discounted);
  }

  // amount
  return Math.max(0, subtotal - coupon.value);
}

function roundYen(x: number): Money {
  return Math.round(x);
}
```

## `src/core/orderUsecase.ts`（中心だけど境界を使う🙂🔌）

```ts
import { CouponRepository, Money, OrderLine } from "./types";
import { applyCoupon, calcSubtotal } from "./calcTotal";

export async function calcOrderTotal(
  lines: OrderLine[],
  couponCode: string | null,
  repo: CouponRepository
): Promise<Money> {
  const subtotal = calcSubtotal(lines);
  const coupon = couponCode ? await repo.getByCode(couponCode) : null;
  return applyCoupon(subtotal, coupon);
}
```

---

## 6) 実装：外側（infra）

🌍📁## `src/infra/fileCouponRepository.ts`（I/O担当🍱）

```ts
import { promises as fs } from "node:fs";
import { Coupon, CouponRepository } from "../core/types";

type CouponJson =
  | { kind: "percent"; value: number }
  | { kind: "amount"; value: number };

type DbJson = Record<string, CouponJson>;

export class FileCouponRepository implements CouponRepository {
  constructor(private readonly jsonPath: string) {}

  async getByCode(code: string): Promise<Coupon | null> {
    const raw = await fs.readFile(this.jsonPath, "utf-8");
    const db = JSON.parse(raw) as DbJson;
    const found = db[code];
    return found ?? null;
  }
}
```

---

## 7) ユニットテスト（中心を速く守る🍪⚡）## `tests/unit/calcTotal.test.ts

```ts
import { describe, it, expect } from "vitest";
import { applyCoupon, calcSubtotal } from "../../src/core/calcTotal";

describe("calcSubtotal", () => {
  it("合計を計算できる🧾✨", () => {
    const subtotal = calcSubtotal([
      { sku: "A", unitPrice: 1200, qty: 2 },
      { sku: "B", unitPrice: 500, qty: 1 },
    ]);
    expect(subtotal).toBe(2900);
  });
});

describe("applyCoupon", () => {
  it("percentクーポンで割引できる🎟️✨", () => {
    expect(applyCoupon(2000, { kind: "percent", value: 10 })).toBe(1800);
  });

  it("amountクーポンで割引できる💸✨", () => {
    expect(applyCoupon(2000, { kind: "amount", value: 300 })).toBe(1700);
  });

  it("割引しすぎは0円止まり🧯🙂", () => {
    expect(applyCoupon(200, { kind: "amount", value: 9999 })).toBe(0);
  });
});
```

## `tests/unit/orderUsecase.test.ts`（repoは差し替え🧸）

```ts
import { describe, it, expect } from "vitest";
import { calcOrderTotal } from "../../src/core/orderUsecase";
import { CouponRepository } from "../../src/core/types";

describe("calcOrderTotal (unit)", () => {
  it("クーポン取得をスタブして合計を出せる🧸🧪", async () => {
    const stubRepo: CouponRepository = {
      async getByCode() {
        return { kind: "percent", value: 20 };
      },
    };

    const total = await calcOrderTotal(
      [{ sku: "A", unitPrice: 1000, qty: 2 }],
      "ANY",
      stubRepo
    );

    expect(total).toBe(1600);
  });
});
```

✅ ここまでが「中心＝ユニットで守る」だよ〜🏠🍪
速いし安定するから、ここを厚くすると幸せになりやすい🙂✨

---

## 8) 結合テスト（外側の“要所”だけ刺す🍱🎯）

狙い：

* JSONファイルから読む実装が壊れてない？
* usecaseと配線したらちゃんと動く？ 🔌✅

## `tests/integration/fileCouponRepository.int.test.ts

```ts
import { describe, it, expect } from "vitest";
import { promises as fs } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { randomUUID } from "node:crypto";

import { FileCouponRepository } from "../../src/infra/fileCouponRepository";
import { calcOrderTotal } from "../../src/core/orderUsecase";

describe("FileCouponRepository (integration) 🍱", () => {
  it("JSONからクーポンを読んで、usecaseまで通せる🔌✨", async () => {
    // Arrange: 一時ファイルにクーポンDBを作る🧪
    const dir = join(tmpdir(), "coupon-" + randomUUID());
    await fs.mkdir(dir, { recursive: true });
    const path = join(dir, "coupons.json");

    await fs.writeFile(
      path,
      JSON.stringify({
        OFF10: { kind: "percent", value: 10 },
      }),
      "utf-8"
    );

    const repo = new FileCouponRepository(path);

    // Act: “本物のファイルI/O”込みで合計を出す🍱
    const total = await calcOrderTotal(
      [{ sku: "A", unitPrice: 1000, qty: 2 }],
      "OFF10",
      repo
    );

    // Assert
    expect(total).toBe(1800);
  });
});
```

## 実行コマンド例🏃‍♀️

💻* ユニットだけ：`vitest run unit` 🍪


* 結合だけ：`vitest run integration` 🍱
* 全部：`vitest run` 🧪

Vitestは **追加引数を“テストファイルのパスに含まれる文字フィルタ”として使える** 仕様だよ🔎✨ ([Vitest][5])

---

## 9) よくある事故と回避テク🚧😵‍💫## 事故1：結合テストだらけで遅い🐢* 症状：CIが10分超え、誰も回さない😇


* 回避：**中心はユニット**、結合は「変換」「配線」「I/Oアダプタ」だけに絞る🎯

## 事故2：モックしすぎて“現実とズレる”🤖💔* 症状：テストは緑、実運用は赤…


* 回避：境界の「変換」や「設定の読み方」みたいな現実パーツは、**結合で1本**持つ🔌✅

## 事故3：E2Eが不安定で心が折れる🫠* 回避：E2Eは「最重要ユーザーフロー」だけにして、細かい仕様はユニット/結合へ分散📐✨

---

## 10) AI（Copilot/Codex）

に助けてもらうコツ🤖🎀* ✅「この関数、ユニットでテストケース列挙して」


* ✅「境界の変換で落ちそうな欠損/単位/丸めを洗い出して」
* ✅「結合テストは“最小”にしたい。要所はどこ？」
* ❌「全部テスト書いて」← 粒度設計が崩れやすい🙅‍♀️💥

---

## まとめ🍙✨* **中心＝ユニットで厚く**（速い・安定・量産できる🍪⚡）


* **外側＝結合で薄く**（変換・配線・I/Oアダプタを要所だけ🍱🎯）
* この型ができると、変更が怖くなくなるよ🙂🧪✨

[1]: https://www.testrail.com/blog/testing-pyramid/?utm_source=chatgpt.com "The Testing Pyramid: A Comprehensive Guide"
[2]: https://vitest.dev/blog/vitest-4?utm_source=chatgpt.com "Vitest 4.0 is out!"
[3]: https://jestjs.io/versions?utm_source=chatgpt.com "Jest Versions"
[4]: https://nodejs.org/en/blog/release/v24.13.0?utm_source=chatgpt.com "Node.js 24.13.0 (LTS)"
[5]: https://vitest.dev/guide/cli "Command Line Interface | Guide | Vitest"
