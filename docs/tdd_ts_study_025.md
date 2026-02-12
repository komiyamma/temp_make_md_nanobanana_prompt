# 第25章：仮実装（まず通す）🩹

![仮実装の絆創膏](./picture/tdd_ts_study_025_band_aid.png)

## 🎯 今日のゴール

* 「**とにかく最短でGreenにする**」やり方（仮実装＝Fake It）を身につけるよ🥰
* そして、**仮のまま放置しない**（ちゃんと一般化して卒業する）までできるようにするよ✅

---

## 💡 仮実装（Fake It）ってなに？

超ざっくり言うと👇

* まずは **定数で返す / ベタ書きで通す**
* 次のテストで **そのベタ書きが壊れるようにして**
* そこで **必要になった分だけ一般化**していく

Kent Beck の TDD でも「まず定数を返して、だんだん変数に置き換えていく」って説明されてるよ🧁 ([スタニスワフのテックノート][1])

---

## 🩹 いつ使うのが上手い？

こんなときにめっちゃ効くよ💪✨

* 実装がちょっと面倒で、**いったん前に進みたい**とき🚶‍♀️
* APIの形（関数名・戻り値）を先に固定したいとき🧷
* 「正解のロジック」を書く前に、**テストの意図が合ってるか**確認したいとき🔍
* AIが“立派すぎる実装”を出してきがちなとき（まずは小さく！）🤖🧯

---

## ✅ ルール（これ守ると気持ちよく回る）

1. **Greenは最短距離**（汚くてOK、ただし仮）🩹
2. 2本目のテストは「仕様追加」じゃなくて、**仮実装を壊すため**に入れる💣
3. 仮実装が残ってたら、**それは未返済の借金**💸（次のリファクタで返す！）
4. 仮実装を増やすほど、プロダクトコードに `if (x===100)` が増えて地獄😇 → **早めに一般化**！

---

## 🧪 ハンズオン：税込み合計をTDDで作る（仮実装→一般化）💰✨

作る関数：`totalWithTax(subtotal: number): number`
仕様：**税率10%で、端数は切り捨て**（`Math.floor`）にするよ🧾

---

## ① Red：最初のテストを書く（1ケースだけ）🟥

まずは「100円 → 110円」だけ決めるよ🙂

```ts
// tests/totalWithTax.test.ts
import { describe, it, expect } from "vitest";
import { totalWithTax } from "../src/totalWithTax";

describe("totalWithTax", () => {
  it("100円なら110円になる", () => {
    expect(totalWithTax(100), "税率10%の税込が欲しいよ").toBe(110);
  });
});
```

※Vitest の `expect` は、失敗時に分かりやすくするため **第2引数にメッセージ**を付けられるよ📣（地味に助かる！） ([Vitest][2])

---

## ② Green：仮実装で通す（定数でOK）🟩🩹

はい、ここが今日の主役✨
いったん **110を返すだけ**で通すよ！

```ts
// src/totalWithTax.ts
export function totalWithTax(subtotal: number): number {
  return 110; // 🩹 仮実装！いまはこれでOK
}
```

この時点では「200円でも110円になっちゃう」けど、**まだテストが要求してない**から気にしない🙆‍♀️
（“必要な分だけ”がTDDのコアだよ🧠）

---

## ③ Red：仮実装を壊すテストを追加する💣🟥

次は「200円 → 220円」を追加して、**110固定を爆破**するよ💥

```ts
// tests/totalWithTax.test.ts
import { describe, it, expect } from "vitest";
import { totalWithTax } from "../src/totalWithTax";

describe("totalWithTax", () => {
  it("100円なら110円になる", () => {
    expect(totalWithTax(100), "税率10%の税込が欲しいよ").toBe(110);
  });

  it("200円なら220円になる（仮実装を壊す）", () => {
    expect(totalWithTax(200)).toBe(220);
  });
});
```

---

## ④ Green：最小の一般化をする🟩✨

ここでやっと、ちゃんと計算するよ✅

```ts
// src/totalWithTax.ts
export function totalWithTax(subtotal: number): number {
  return Math.floor(subtotal * 1.1);
}
```

---

## ⑤ Refactor：読みやすくする（でもやりすぎない）🧹✨

「1.1」って何？になりがちだから、**意図が読める**ようにだけするよ🙂

```ts
// src/totalWithTax.ts
const TAX_RATE = 0.1;

export function totalWithTax(subtotal: number): number {
  return Math.floor(subtotal * (1 + TAX_RATE));
}
```

---

## ⑥ 仕上げ：端数のテストを1本だけ足す（不安つぶし）🧷🧪

端数が怖いから、1個だけ確認して安心しよ💕

```ts
it("101円なら111円になる（端数は切り捨て）", () => {
  expect(totalWithTax(101)).toBe(111); // 101*1.1=111.1 → floorで111
});
```

---

## 🤖 AIの使い方（この章で強いプロンプト）✨

## 1) 「仮実装で最短Green」案を出させる🩹

* 「**最短でGreenにする仮実装**を提案して」
* 「ただし、**次のテストで壊れる前提**で、後で一般化する方針も書いて」

## 2) 「仮が残ってないか監査」させる🔍

* 「この実装の中に、**仮実装が永住しそうな匂い**がある？（定数、条件分岐、マジックナンバー）」
* 「残ってたら、**最小の一般化**手順を1ステップで提案して」

## 3) 「次に足すテスト」を出させる💣

* 「今の仮実装を**確実に壊す**次のテストケースを3つ出して」
* 「そのうち、**いちばん小さい爆破**はどれ？」

---

## 😵‍💫 よくある事故（ここだけ注意！）🚧

* **仮実装がそのまま本番コードになる**（あるある😇）
  → “壊すテスト”が足りない or リファクタしてない
* `if (x===100)` が増殖して、**条件地獄**になる🌪️
  → 2〜3本目あたりで一般化へ移行！
* AIが「完成形」を出して、**学びが飛ぶ**🛫
  → まずは仮実装→壊す→一般化、の順番を固定しよ🧷

---

## ✅ チェック（合格ライン）🎉

* [ ] 1本目で **仮実装（定数）** を入れても罪悪感ゼロで進めた🩹
* [ ] 2本目で **仮実装を壊す** 目的のテストを入れられた💣
* [ ] 一般化して、**仮が消えた**（永住してない）🏠❌
* [ ] テスト失敗時に原因が分かる（メッセージや命名が効いてる）📣 ([Vitest][2])

---

次の第26章は「三角測量（2例目で一般化）📐」で、**“壊すための2例目”じゃなくて、“答えを見つけるための2例目”**の考え方に入っていくよ〜😊✨

[1]: https://stanislaw.github.io/2016-01-25-notes-on-test-driven-development-by-example-by-kent-beck.html?utm_source=chatgpt.com "Notes on \"Test-Driven Development by Example\" by Kent ..."
[2]: https://vitest.dev/api/expect.html?utm_source=chatgpt.com "expect"
