# 第08章：純粋関数の作り方（I/Oゼロの中心）🍰✨

![testable_ts_study_008_pure_function.png](./picture/testable_ts_study_008_pure_function.png)

## 0. この章のゴール🎯🌈

この章が終わったら…👇



* 「これ純粋関数だね✨」って自信を持って言えるようになる
* “中心（ロジック）”を **I/Oゼロ** に近づけるコツがわかる
* 文字列整形🍩と料金計算💰で、**純粋関数＋テスト**を気持ちよく書けるようになる

---

## 0.5. いまの最新ざっくりメモ🆕📝

（2026/01/16時点）



* TypeScript は **5.9.3** が latest として配布されています📦✨ ([npm][1])
* Vitest は **4.0 系が登場**（メジャーアップデート）しています🧪🚀 ([Vitest][2])
* Node.js は **24 が Active LTS**（1/13に 24.13.0 のリリース告知）です🟢 ([Node.js][3])

---

## 1. 純粋関数ってなに？🍰✨

![testable_ts_study_008_pure_definition.png](./picture/testable_ts_study_008_pure_definition.png)

（いちばん大事）純粋関数（Pure Function）は、ざっくり言うとこの2つを満たす関数だよ☺️👇



### ✅ 条件A：同じ入力なら、同じ出力🎯* `f(10)` を100回呼んでも、毎回同じ結果になるやつ✨

### ✅ 条件B：外の世界を変えない（副作用なし）

🚫🌍* 例：ログ出す📝、DB保存🗄️、ファイル書く📁、画面表示🖥️、通信する🌐
  こういうのを **関数の中で勝手にやらない**！

---

## 2. なんで純粋関数が「中心」に効くの？💪🧠✨

純粋関数が増えると、いいことがドバドバ出ます🥤✨



* テストが速い⚡（I/O待ちゼロ！）
* テストが安定する🧊（時間や乱数でブレない！）
* リファクタが怖くない🛠️（壊したらすぐ検知できる）
* 変更に強い🏰（外側が変わっても中心は守られる）

「中心（ロジック）」が純粋だと、**“守る”のがめちゃラク**になるんだよね😊💖

---

## 3. 純粋にするためのコツ3つ🔑✨### コツ①：必要なものは「引数」で受け取る🎁

![testable_ts_study_008_pure_tips.png](./picture/testable_ts_study_008_pure_tips.png)

➡️外から取ってくるのをやめて、入力として渡す！
例：時刻⏰、税率📊、割引率🎫、設定⚙️…ぜんぶ引数へ！

### コツ②：「計算」と「I/O」を分ける✂️

🍱* 外側：読む/書く/取ってくる（I/O）


* 中心：受け取ったデータで計算する（純粋）

### コツ③：失敗を「throw」より「結果」で返す（入門編）

🧯🎀例外は便利だけど、乱用するとテストが読みにくくなることも😵‍💫
この章では、まず **Result型**（成功/失敗を戻り値で表す）を触ってみよ〜✨

---

## 4. 純粋関数チェックリスト✅🧪関数を見たら、これで判定してね👀✨

![testable_ts_study_008_checklist.png](./picture/testable_ts_study_008_checklist.png)



* [ ] `Date` / `Math.random` / `fetch` / ファイル / DB を触ってない？⛔
* [ ] `console.log` してない？📝（ログもI/Oだよ！）
* [ ] グローバル変数を書き換えてない？🌍💥
* [ ] 引数以外のものに依存してない？（環境変数とか）⚙️
* [ ] 同じ引数なら結果が固定？🎯

---

## 5. ハンズオン①：文字列整形（地味に超強い）

![testable_ts_study_008_string_norm.png](./picture/testable_ts_study_008_string_norm.png)

🍩🔤✨### お題🎀ユーザー入力って、だいたいこうなる👇😇



* 前後にスペース
* 連続スペース
* 大文字小文字ぐちゃぐちゃ

これを「表示用の名前」に整形しよう✨

仕様📌

* 前後の空白は削除
* 途中の連続空白は1つに
* 各単語の先頭だけ大文字（Title Caseっぽく）
* 空文字（整形後に空）なら失敗を返す

---

### 実装（純粋関数）

🍰✨

```ts
// src/core/normalizeDisplayName.ts

export type NormalizeError =
  | { kind: "EMPTY" };

export type Result<T, E> =
  | { ok: true; value: T }
  | { ok: false; error: E };

export function normalizeDisplayName(input: string): Result<string, NormalizeError> {
  const trimmed = input.trim();
  if (trimmed.length === 0) {
    return { ok: false, error: { kind: "EMPTY" } };
  }

  const normalizedSpaces = trimmed.replace(/\s+/g, " ");
  const words = normalizedSpaces.split(" ");

  const titled = words
    .map(w => w.slice(0, 1).toUpperCase() + w.slice(1).toLowerCase())
    .join(" ");

  return { ok: true, value: titled };
}
```

ポイント🎯✨

* どこにも I/O がない！
* 失敗は `throw` じゃなく Result で返してる（入門として読みやすい）😊

---

### テスト（AAAで書く）

🧪📐✨

```ts
// src/core/normalizeDisplayName.test.ts
import { describe, it, expect } from "vitest";
import { normalizeDisplayName } from "./normalizeDisplayName";

describe("normalizeDisplayName", () => {
  it("前後の空白を消して整形する", () => {
    // Arrange
    const input = "   aLIce   ";

    // Act
    const result = normalizeDisplayName(input);

    // Assert
    expect(result).toEqual({ ok: true, value: "Alice" });
  });

  it("連続スペースを1つにする", () => {
    const input = "alice     bob";
    const result = normalizeDisplayName(input);
    expect(result).toEqual({ ok: true, value: "Alice Bob" });
  });

  it("空っぽは失敗にする", () => {
    const input = "    ";
    const result = normalizeDisplayName(input);
    expect(result).toEqual({ ok: false, error: { kind: "EMPTY" } });
  });
});
```

---

## 6. ハンズオン②：料金計算（テスタブル設計の王道）

![testable_ts_study_008_pricing_flow.png](./picture/testable_ts_study_008_pricing_flow.png)

💰🛒✨### お題🎀「カフェの会計」っぽくしてみる☕🍰
仕様📌

* 小計（items合計）
* 会員なら 10% 引き（小計に適用）
* 税率をかける（例：10%）
* 端数は **円で四捨五入**（ここは仕様として固定でOK）

I/Oなしで、入力→出力が固定の **計算関数**にするよ🧠✨

---

### 実装（純粋関数）

🍰✨

```ts
// src/core/calcTotal.ts

export type LineItem = {
  name: string;
  priceYen: number; // 例: 450
  qty: number;      // 例: 2
};

export type PricingInput = {
  items: LineItem[];
  isMember: boolean;
  taxRate: number; // 例: 0.1
};

export type PricingOutput = {
  subtotal: number;
  discount: number;
  taxedTotal: number;
};

function roundYen(value: number): number {
  return Math.round(value);
}

export function calcTotal(input: PricingInput): PricingOutput {
  const subtotal = input.items.reduce((sum, item) => {
    return sum + item.priceYen * item.qty;
  }, 0);

  const discount = input.isMember ? roundYen(subtotal * 0.1) : 0;
  const afterDiscount = subtotal - discount;

  const taxedTotal = roundYen(afterDiscount * (1 + input.taxRate));

  return { subtotal, discount, taxedTotal };
}
```

ポイント🎯✨

* 税率は引数で受け取る（外から注入🎁）
* 丸めも「関数の中で完結」＝純粋✨
* `roundYen` を分けたのは、あとで仕様が変わっても差し替えやすいから🛠️💕

---

### テスト🧪🎉

```ts
// src/core/calcTotal.test.ts
import { describe, it, expect } from "vitest";
import { calcTotal } from "./calcTotal";

describe("calcTotal", () => {
  it("会員じゃない場合：割引なしで税計算", () => {
    const result = calcTotal({
      items: [
        { name: "Latte", priceYen: 450, qty: 2 }, // 900
        { name: "Cake", priceYen: 520, qty: 1 },  // 520
      ],
      isMember: false,
      taxRate: 0.1,
    });

    // subtotal=1420, discount=0, total=1562
    expect(result).toEqual({ subtotal: 1420, discount: 0, taxedTotal: 1562 });
  });

  it("会員の場合：小計の10%引き→税", () => {
    const result = calcTotal({
      items: [{ name: "Latte", priceYen: 450, qty: 2 }], // 900
      isMember: true,
      taxRate: 0.1,
    });

    // subtotal=900, discount=90, after=810, total=891
    expect(result).toEqual({ subtotal: 900, discount: 90, taxedTotal: 891 });
  });
});
```

---

## 7. 例外（throw）

の扱い方：まずは“使い分け”だけ😇🧯この講座では「例外を完全禁止！」みたいなことはしないよ🙅‍♀️
ただ、**中心（純粋ロジック）**では、最初はこれが無難👇✨

* 入力が変でも「Resultで返す」🎁
* “本当にありえない”壊れ方だけ throw（例：プログラムのバグ）💥

### 使い分けミニ指針📌* ユーザー入力が原因で起きる失敗 → Result（仕様の失敗）

🙂


* 開発者のミスでしか起きない失敗 → throw（バグ）😵‍💫

---

## 8. よくある「純粋に見えて純粋じゃない」罠👃

![testable_ts_study_008_purity_traps.png](./picture/testable_ts_study_008_purity_traps.png)

💨😱### 罠①：`Date.now()` を呼んでる⏰同じ入力でも時間で変わるよね🫠
→ 次の章以降で **Clock注入** にして止めるよ🧊✨

### 罠②：`Math.random()` を呼んでる🎲毎回変わるよね😂
→ **Random注入**で固定できる🎯

### 罠③：関数の外の変数を書き換える🌍💥

```ts
let count = 0;
export function f(x: number) {
  count++; // ← 副作用！
  return x + count;
}
```

こういうのは中心に置くとテストが地獄になるやつ😇

---

## 9. ミニ問題（ここ、超だいじ！

）🎓🧪✨### Q1：これは純粋？🤔

```ts
export function addTax(price: number, taxRate: number) {
  return Math.round(price * (1 + taxRate));
}
```

👉 純粋！🍰✨（入力だけで決まる＆外を変えない）

### Q2：これは純粋？🤔

```ts
export function greet(name: string) {
  console.log("hello"); // ← I/O！
  return `Hello, ${name}`;
}
```

👉 純粋じゃない🫠（ログもI/Oだよ📝）

---

## 10. AI活用コーナー🤖🎀（速くなるやつ！

![testable_ts_study_008_ai_filter.png](./picture/testable_ts_study_008_ai_filter.png)

）AIはこの章だと特に相性いいよ〜✨



### ✅ 使ってOKな頼み方例🧁* 「この関数を純粋関数にするための“副作用ポイント”を列挙して📝

」


* 「テストケース（境界値/異常系）を10個出して🧪」
* 「Result型で失敗を表す設計案を2パターン出して🔁」

### ⚠️ 注意ポイント👀AIの提案がこうなってたら要注意！



* こっそり `Date.now()` 入れてくる⏰😇
* こっそり `Math.random()` 入れてくる🎲😇
* こっそり `console.log` でデバッグしてる📝😇

「中心はI/Oゼロ！」って合言葉でチェックしてね🍰✨

---

## 11. 宿題（やると一気に身につく）

📚💖### 宿題A🍩`normalizeDisplayName` を改造して、



* `-` や `_` が連続してたら1個にまとめる（例：`a__b` → `A_B`）
  みたいな仕様を追加して、テストも増やしてね🧪✨

### 宿題B💰`calcTotal` にクーポン機能🎫を追加！



* `couponYen?: number` を足して
* 割引は「会員割→クーポン→税」みたいに順番を固定
  （順番を仕様としてテストで守るのが大事だよ〜😊）

---

## 12. 次章の予告チラ見せ👀✨

次は **TypeScriptの型でテストを減らす**🛡️📘
「そもそも不正な値が入らない」ようにできると、テストも設計ももっと楽になるよ〜🌈✨

[1]: https://www.npmjs.com/package/typescript?utm_source=chatgpt.com "TypeScript"
[2]: https://vitest.dev/blog/vitest-4?utm_source=chatgpt.com "Vitest 4.0 is out!"
[3]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
