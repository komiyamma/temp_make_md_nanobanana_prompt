# 第29章：リファクタ安全運転（小さく）🛡️

![安全なリファクタリングの盾](./picture/tdd_ts_study_029_shield.png)

（テーマ：**壊さず整理する**＝「振る舞いは変えない」リファクタ✨）
※「小さく変更→すぐテスト」を徹底するのがコツだよ🧪✅（“小さく・毎回テスト”は定番の教え方として超有名！）([Fars][1])

---

## 🎯 この章でできるようになること

![Refactor vs Feature](./picture/tdd_ts_study_029_refactor_vs_feature.png)

* **リファクタと機能追加の違い**が説明できる🙂
* **1回の変更を小さく**して、**毎回テストで安全確認**できる🧪✅
* VS Codeの **Rename / Extract** を使って、怖くない整理ができる🪄🧰([Visual Studio Code][2])
* AIに助けてもらいつつ、**“採用は最小だけ”**にできる🤖✂️

---

## 🧠 まず大事：リファクタ安全運転の「7つのルール」🛡️

![7 Rules Cycle](./picture/tdd_ts_study_029_7_rules_cycle.png)

1. **振る舞いを変えない**（変えるのは別コミット！）🚦
2. **変更は小さく**（1〜5分で戻せる粒度）🧩
3. **1手ごとにテスト**（watch最高）🔁🧪
4. **型チェックも味方**（`tsc --noEmit`）🧷
5. **自動整形は機械に任せる**（Prettierなど）🧹✨([Prettier][3])
6. **Lintは事故の予兆を拾う**（ESLint＋typescript-eslint）🚨([ESLint][4])
7. **1回で“キレイにし切らない”**（今日は3回に分ける！）🧊➡️🧊➡️🧊

---

## 🛠️ 今日の題材（ミニ会計ロジック）☕️🧾

「動いてるけど読みにくい」コードを、**3回に分けて**安全に整えるよ💪✨
（テストはもうある前提で進めるよ🧪）

### ✅ 先に“安全装置”を用意（package.jsonの例）

```json
{
  "scripts": {
    "test": "vitest",
    "test:run": "vitest run",
    "test:watch": "vitest --watch",
    "typecheck": "tsc --noEmit"
  }
}
```

Vitestは4.0が出ていて、4.1系も動きがあるよ（追従は「安定優先」でOK）([Vitest][5])
TypeScriptは現時点の安定版として 5.9.3 が出てるよ🧷([GitHub][6])（6.0/7.0も動きはあるけど、教材は安定が大事☺️）([Microsoft for Developers][7])

---

## 🧪 まず“現状”（テストはある・コードが読みにくい）😵‍💫

![Spaghetti Code](./picture/tdd_ts_study_029_spaghetti_code.png)

### src/checkout.ts（わざと読みにくい例）

```ts
export type Item = { price: number; qty: number };

export function calcTotal(items: Item[], coupon?: { type: "percent" | "yen"; value: number }) {
  let total = 0;

  for (const it of items) {
    total += it.price * it.qty;
  }

  // 5000円以上で10%OFF（仕様）
  if (total >= 5000) {
    total = total - Math.floor(total * 0.1);
  }

  if (coupon) {
    if (coupon.type === "percent") {
      total = total - Math.floor(total * (coupon.value / 100));
    } else {
      total = total - coupon.value;
    }
  }

  if (total < 0) total = 0;

  // 端数は切り捨て（円）
  total = Math.floor(total);

  return total;
}
```

### tests/checkout.test.ts（最低限）

```ts
import { describe, it, expect } from "vitest";
import { calcTotal } from "../src/checkout";

describe("calcTotal", () => {
  it("合計が5000未満なら割引なし", () => {
    expect(calcTotal([{ price: 1000, qty: 2 }])).toBe(2000);
  });

  it("合計が5000以上なら10%OFF", () => {
    expect(calcTotal([{ price: 2500, qty: 2 }])).toBe(4500);
  });

  it("percentクーポンが効く", () => {
    expect(calcTotal([{ price: 3000, qty: 2 }], { type: "percent", value: 10 })).toBe(4800);
  });

  it("yenクーポンでマイナスにならない", () => {
    expect(calcTotal([{ price: 1000, qty: 1 }], { type: "yen", value: 5000 })).toBe(0);
  });
});
```

ここから先は、**常にテストGreenのまま**進めるよ🟢🧪

---

## 🛡️ リファクタ①（最小）：名前を直す＋マジックナンバーを外に出す🪄

![Refactor Step 1 Rename](./picture/tdd_ts_study_029_refactor_step1_rename.png)

**狙い：読みやすさを上げる（振る舞いは絶対そのまま）**🙂

✅ やること

* `total` を意味ある名前に（例：`amount`）
* `5000` / `0.1` を定数へ
* テスト→OK🧪✅

### 変更例

```ts
const DISCOUNT_THRESHOLD_YEN = 5000;
const DISCOUNT_RATE = 0.1;

export function calcTotal(items: Item[], coupon?: { type: "percent" | "yen"; value: number }) {
  let amount = 0;

  for (const it of items) {
    amount += it.price * it.qty;
  }

  if (amount >= DISCOUNT_THRESHOLD_YEN) {
    amount = amount - Math.floor(amount * DISCOUNT_RATE);
  }

  // ...以下同じ
  return Math.floor(Math.max(0, amount));
}
```

🧪 ここで **必ず `npm run test:run`** ✅
（コミット例：`refactor: rename vars and extract constants`）📝

---

## 🛡️ リファクタ②（最小）：処理を Extract して“役割”を見える化🧩✨

![Refactor Step 2 Extract](./picture/tdd_ts_study_029_refactor_step2_extract.png)

**狙い：1関数が“やりすぎ”にならないようにする**👀
VS Codeの「Extract Function / Extract Variable」も使えるよ（Ctrl+. の候補に出る）🧰([Visual Studio Code][8])

✅ やること

* 小関数に分ける（合計 / 割引 / クーポン / 下限0 / 円丸め）
* テスト→OK🧪✅

### 変更例（分割）

```ts
export type Item = { price: number; qty: number };
export type Coupon = { type: "percent" | "yen"; value: number };

const DISCOUNT_THRESHOLD_YEN = 5000;
const DISCOUNT_RATE = 0.1;

export function calcTotal(items: Item[], coupon?: Coupon) {
  const subtotal = calcSubtotal(items);
  const discounted = applyThresholdDiscount(subtotal);
  const afterCoupon = coupon ? applyCoupon(discounted, coupon) : discounted;
  return roundYen(clampToZero(afterCoupon));
}

function calcSubtotal(items: Item[]) {
  let amount = 0;
  for (const it of items) amount += it.price * it.qty;
  return amount;
}

function applyThresholdDiscount(amount: number) {
  if (amount < DISCOUNT_THRESHOLD_YEN) return amount;
  return amount - Math.floor(amount * DISCOUNT_RATE);
}

function applyCoupon(amount: number, coupon: Coupon) {
  if (coupon.type === "percent") {
    return amount - Math.floor(amount * (coupon.value / 100));
  }
  return amount - coupon.value;
}

function clampToZero(amount: number) {
  return amount < 0 ? 0 : amount;
}

function roundYen(amount: number) {
  return Math.floor(amount);
}
```

🧪 ここでテスト✅
（コミット例：`refactor: extract small functions (subtotal/discount/coupon)`）📝

---

## 🛡️ リファクタ③（最小）：分岐の意図をはっきりさせる（読み物化）📘✨

![Refactor Step 3 Clarify](./picture/tdd_ts_study_029_refactor_step3_clarify.png)

**狙い：あとで見た人が“仕様”として読める**🙂

✅ やること

* 「%クーポン」「円クーポン」を関数で分ける（読みやすさUP）
* “丸め”の場所を最後に固定（事故りにくい）
* テスト→OK🧪✅

### 変更例（クーポンを読みやすく）

```ts
function applyCoupon(amount: number, coupon: Coupon) {
  return coupon.type === "percent"
    ? applyPercentCoupon(amount, coupon.value)
    : applyYenCoupon(amount, coupon.value);
}

function applyPercentCoupon(amount: number, percent: number) {
  return amount - Math.floor(amount * (percent / 100));
}

function applyYenCoupon(amount: number, yen: number) {
  return amount - yen;
}
```

🧪 テスト✅
（コミット例：`refactor: clarify coupon branches`）📝

---

## 🧰 VS Codeで“安全運転”を加速する操作集🚀

* **Rename Symbol**：`F2`（変数名変更の事故が激減）✨
* **Quick Fix / Refactor**：`Ctrl + .`（Extract Function/Variable など）🪄([Visual Studio Code][2])
* **テストをwatch**：保存→即Red/Greenが見える🔁🧪
* **Type Check**：`npm run typecheck`（テストだけじゃ拾えない事故も防ぐ）🧷

---

## 🤖 AIの使い方（安全運転モード）🛡️🤖

![AI Safety Gear](./picture/tdd_ts_study_029_ai_safety_gear.png)

AIはめちゃ便利だけど、**“一気に大改造”提案を受けると事故る**ので、質問を固定しよ〜😆💕

### ✅ おすすめプロンプト（そのまま使ってOK）

```text
次のTypeScriptコードを「振る舞いを変えないリファクタ」にしたいです。
条件：
- 変更は“最小ステップ”を3〜5個に分けて
- 各ステップでテストが通る前提
- 提案は「Rename / Extract Function / 条件分岐の読みやすさ」中心
出力：
1) ステップ一覧
2) 各ステップの差分（小さく）
3) 注意点（事故ポイント）
```

💡 そして、AIの差分を採用したら **必ずテスト**🧪✅（ここ超大事！）

---

## ✅ チェックリスト（合格ライン）💯✨

* [ ] 変更は**3回に分けて**コミットできた🧊🧊🧊
* [ ] 各コミットの直後にテストが通ってる🧪✅
* [ ] 関数が「合計」「割引」「クーポン」「下限0」「丸め」に分かれて読める📘
* [ ] `typecheck` も通る🧷✅
* [ ] 途中で仕様変更（=振る舞い変更）を混ぜてない🚦

---

## 🧸 宿題（やさしめ）💕

1. `DISCOUNT_THRESHOLD_YEN` と `DISCOUNT_RATE` を **引数で渡せる**形にしてみて（でも振る舞いは同じ！）🧩
2. テストを1本追加：**「5000ちょうど」**のケースを書いて安心度UP🧪✨
3. 余裕があったら：`applyThresholdDiscount` を **名前でもっと仕様っぽく**してみて（例：`applyMembershipDiscount` とか）📝💕

---

必要なら次は、同じ“安全運転”で **「重複のにおい（第28章）」→「テスト側リファクタ（第30章）」**に自然につなげる流れで、教材を1セットにして整えるよ🧹✨

[1]: https://fars.ee/RfmE.pdf?utm_source=chatgpt.com "Refactoring: Improving the Design of Existing Code, 2/e"
[2]: https://code.visualstudio.com/docs/editing/refactoring?utm_source=chatgpt.com "Refactoring"
[3]: https://prettier.io/blog/2026/01/14/3.8.0?utm_source=chatgpt.com "Prettier 3.8: Support for Angular v21.1"
[4]: https://eslint.org/blog/2026/01/eslint-v10.0.0-rc.0-released/?utm_source=chatgpt.com "ESLint v10.0.0-rc.0 released"
[5]: https://vitest.dev/blog/vitest-4?utm_source=chatgpt.com "Vitest 4.0 is out!"
[6]: https://github.com/microsoft/typescript/releases?utm_source=chatgpt.com "Releases · microsoft/TypeScript"
[7]: https://devblogs.microsoft.com/typescript/progress-on-typescript-7-december-2025/?utm_source=chatgpt.com "Progress on TypeScript 7 - December 2025"
[8]: https://code.visualstudio.com/docs/languages/typescript?utm_source=chatgpt.com "TypeScript in Visual Studio Code"
