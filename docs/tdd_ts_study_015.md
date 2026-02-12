# 第15章：AAAで書く（型を固定）🧱

![AAAの積み木](./picture/tdd_ts_study_015_aaa_blocks.png)

## 🎯 この章のゴール

* テストを「毎回同じ型（書き方）」で書けるようになる🧩
* 失敗したとき、どこが悪いか“すぐ”分かるテストにできる🔍
* Arrange / Act / Assert が自然に体にしみる💪💕

---

## 🧠 AAAってなに？（超ざっくり）

AAA はテストの並べ方の型だよ〜😊✨

* **Arrange（準備）**：入力データや前提を作る🧺
* **Act（実行）**：テストしたい処理を1回だけ呼ぶ▶️
* **Assert（確認）**：期待どおりかチェックする✅

この “3ブロック” に分けるだけで、テストが一気に読み物になるの💖

---

## ✅ なんでAAAが強いの？

TDDでテストを増やすと、**「自分のテストが読めない…」問題**が来がち🥲
AAAにすると、こうなるよ👇

* **迷子にならない**：どこが準備でどこが確認か一目で分かる👀
* **変更に強い**：実装が変わっても、仕様（Assert）だけ残ればOKになりやすい🛡️
* **AIとの相性が良い**：AIに直させても、ブロックで崩れにくい🤖✨
  （Vitestは 4.x が現行の大きな節目で、ドキュメントも整ってて学びやすいよ📚） ([Vitest][1])

---

## 🧪 手を動かす：ぐちゃテスト → AAAに整形しよう🧹✨

ここでは例として「買い物の小計＋送料」みたいな関数をテストするよ🛍️
（“テストの整形”が目的だから、中身はシンプルでOK🙆‍♀️）

### 0) まず対象コード（例）

```ts
// src/price.ts
export function calcTotal(subtotal: number, shipping: number) {
  if (subtotal < 0 || shipping < 0) throw new Error("negative");
  if (subtotal >= 3000) return subtotal; // 3000以上は送料無料
  return subtotal + shipping;
}
```

> 例外テストも出てくるけど、この章は「並べ方（AAA）」が主役ね🙂

---

### 1) “ぐちゃ”なテスト例（読みにくいやつ😵‍💫）

```ts
// tests/price.test.ts
import { describe, test, expect } from "vitest";
import { calcTotal } from "../src/price";

describe("calcTotal", () => {
  test("free shipping", () => {
    const result = calcTotal(3000, 500);
    expect(result).toBe(3000);

    const result2 = calcTotal(5000, 9999);
    expect(result2).toBe(5000);

    const shipping = 500;
    const subtotal = 2999;
    const result3 = calcTotal(subtotal, shipping);
    expect(result3).toBe(3499);
  });
});
```

❌ ここがツラいポイント

* 1つのテストに **別の仕様が混ざってる**（送料無料と送料ありが同居）🌀
* Assertが途中に散ってて、読みながら脳が疲れる🧠💥
* 失敗したとき「どのケースの失敗？」ってなりがち😢

---

### 2) AAAに整形（しかも “1テスト＝1約束” に寄せる✨）

```ts
// tests/price.test.ts
import { describe, test, expect } from "vitest";
import { calcTotal } from "../src/price";

describe("calcTotal", () => {
  test("3000以上なら送料無料になる", () => {
    // Arrange
    const subtotal = 3000;
    const shipping = 500;

    // Act
    const total = calcTotal(subtotal, shipping);

    // Assert
    expect(total).toBe(3000);
  });

  test("3000未満なら送料が足される", () => {
    // Arrange
    const subtotal = 2999;
    const shipping = 500;

    // Act
    const total = calcTotal(subtotal, shipping);

    // Assert
    expect(total).toBe(3499);
  });

  test("負の値が来たらエラーにする", () => {
    // Arrange
    const subtotal = -1;
    const shipping = 500;

    // Act + Assert（例外はこの形が読みやすいことが多い）
    expect(() => calcTotal(subtotal, shipping)).toThrow("negative");
  });
});
```

✅ これで一気に「仕様書」っぽくなった〜！📘💕
（Vitestの expect はアサーションの中心で、Jest互換も意識されてるよ） ([Vitest][2])

---

## 🧠 AAAのコツ（ここだけ覚えよ！）💡✨

### ✅ コツ1：Actは基本「1回だけ」▶️

![015 act once](./picture/tdd_ts_study_015_act_once.png)


Actが2回以上あると、何を検証してるかボケやすい😵
→ それは **テストを分けるサイン**🪓

### ✅ コツ2：Assertは“固める”✅

![015 assert group](./picture/tdd_ts_study_015_assert_group.png)


Assertが途中に散ると読みにくい💦
→ 最後にまとめる（例外だけは Act+Assert になりがちでOK🙆‍♀️）

![015 act assert exception](./picture/tdd_ts_study_015_act_assert_exception.png)


### ✅ コツ3：Arrangeが長くなったら「意味のある値」に寄せる🧸

![015 arrange heavy](./picture/tdd_ts_study_015_arrange_heavy.png)


この章では深入りしないけど、
Arrangeが重くなったら「次章以降で軽くする」流れになるよ😉✨

---

## 🤖 AIの使い方（この章での勝ちパターン）🧠🤖✨

### 目的：AIに “整形” させる（仕様は変えさせない！）🛡️

![015 ai refactoring](./picture/tdd_ts_study_015_ai_refactoring.png)


コピペで使える指示👇

```text
次のVitestのテストを AAA（Arrange/Act/Assert）に整形して。
ルール：
- テストが保証している仕様（意味）は変えない
- 1テスト=1つの約束になるように、必要ならテストを分割してOK
- Assertは原則まとまった塊にする（例外テストは例外でOK）
- 命名（テスト名）も読み物になるように直して
出力はファイル全文で。
```

AIが出したものは、最後にあなたが「仕様が変わってないか」だけチェックすればOK✅💕

---

## ✅ チェックリスト（できたら合格🎉）

* [ ] Arrange / Act / Assert が見た瞬間に分かる👀✨
* [ ] Act が基本1回になってる▶️
* [ ] Assert が散ってない✅
* [ ] 1テストが1つの約束になってる🤝
* [ ] 落ちたとき、原因の見当がすぐ付く🔍

---

## 🌟 最新トピック（この教材の“今”の前提）

* Vitest は 4.0 が大きなメジャー節目で、ガイド・APIが更新されてるよ🧪 ([Vitest][1])
* Node.js は v24 が Active LTS、v22 は Maintenance LTS という位置づけ（安定運用はLTS系が安心）🟢 ([nodejs.org][3])
* TypeScript は npm の latest が 5.9.3（5.9系）として公開されてるよ📦 ([NPM][4])

---

必要なら、この章の「提出物セット」も作れるよ😊
たとえば「ぐちゃテストを1つ選んでAAAに直して、コミット1回で出す🧾✨」みたいに、教材っぽく丸ごとパッケージ化しよっか？🎀

[1]: https://vitest.dev/blog/vitest-4?utm_source=chatgpt.com "Vitest 4.0 is out!"
[2]: https://vitest.dev/api/expect.html?utm_source=chatgpt.com "expect"
[3]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
[4]: https://www.npmjs.com/package/typescript?utm_source=chatgpt.com "TypeScript"
