# 第07章：テストの型（AAA）で迷わなくする📐🧪

![testable_ts_study_007_aaa_pattern.png](./picture/testable_ts_study_007_aaa_pattern.png)

この章は「テストって毎回どう書けばいいの〜😵‍💫」を卒業して、**同じ型でサクサク書ける状態**を作る回だよ〜！🎀
型はこれだけ👇

**AAA = Arrange / Act / Assert** 🧁
（準備 → 実行 → 確認）

---

## 1) AAAってなに？なんで効くの？🧠✨

テストで迷う理由の多くは、「何をどの順番で書くか」が毎回バラバラだからなんだよね💦
AAAに固定すると、脳みそがこうなる👇

* **Arrange（準備）**：入力データ、前提条件を作る🧺
* **Act（実行）**：テスト対象の関数を呼ぶ▶️
* **Assert（確認）**：結果が期待どおりかチェック✅

この順にするだけで、テストが **読みやすい**＆**増やしやすい**🎉

---

## 2) まずは“型”だけ覚える（最小テンプレ）

📌🧪コメントで区切ってもいいし、**空行で区切る**だけでもOKだよ〜☺️✨



```ts
import { expect, test } from "vitest";
import { calcTotal } from "./calcTotal";

test("税込み合計を返す（税10%）", () => {
  // Arrange
  const price = 1000;
  const taxRate = 0.1;

  // Act
  const actual = calcTotal(price, taxRate);

  // Assert
  expect(actual).toBe(1100);
});
```

ポイントはこれだけ🫶

* **Actは1行**（できるだけ）
* **Assertは1個**（できるだけ）
* Arrangeは「読者にやさしい名前」👀✨

---

## 3) “良いテスト名”の型も決めちゃう📝

💖テスト名は「仕様の日本語」っぽくすると強いよ💪✨

おすすめの型👇

* **〜を返す（条件）**
* **〜になる（条件）**
* **〜しない（条件）**
* **〜のときエラー（条件）**

たとえば👇

* `割引率が0のとき、割引なしの合計を返す`
* `価格が0のとき、0を返す`
* `税率がマイナスのとき、例外を投げる`（※第25章あたりで扱う方向でもOK）

---

## 4) 境界値テストの考え方（ここ超大事）

🚧✨テストケースが思いつかないときは、まず「端っこ」を攻めるのがコツ😼🧪

よくある境界たち👇

* **0**（ない）
* **1**（最小の存在）
* **最大**（上限）
* **空**（空文字、空配列）
* **ちょうど境界**（例：1000円以上で送料無料、の1000円）
* **境界のちょい手前/ちょい先**（999 / 1000 / 1001 みたいに）

---

## 5) 同じ関数にテストケースを“増やして慣れる”📈🧪✨

ここからハンズオンだよ〜！🎮💕



### お題：合計計算（純粋関数）

🧾✨例として、こういう関数があるとするね👇
（中身は第6章で作ったものの延長でOK🙆‍♀️）

```ts
// calcTotal.ts
export function calcTotal(price: number, taxRate: number): number {
  return Math.round(price * (1 + taxRate));
}
```

---

## 6) AAAで“3本”増やす（コピペでもいいから型を固定）

🧁🧪

```ts
import { describe, expect, test } from "vitest";
import { calcTotal } from "./calcTotal";

describe("calcTotal", () => {
  test("税率0のとき、価格そのままを返す", () => {
    // Arrange
    const price = 1000;
    const taxRate = 0;

    // Act
    const actual = calcTotal(price, taxRate);

    // Assert
    expect(actual).toBe(1000);
  });

  test("価格0のとき、0を返す", () => {
    // Arrange
    const price = 0;
    const taxRate = 0.1;

    // Act
    const actual = calcTotal(price, taxRate);

    // Assert
    expect(actual).toBe(0);
  });

  test("端数が出るとき、四捨五入される", () => {
    // Arrange
    const price = 101;
    const taxRate = 0.1; // 111.1 → 111

    // Act
    const actual = calcTotal(price, taxRate);

    // Assert
    expect(actual).toBe(111);
  });
});
```

この時点で、もう「書き方で迷う」ことが減るはず！🥳✨

---

## 7) コピペ地獄を救う：`test.each`（テーブル駆動）

🧪🍱ケースが増えるとコピペしたくなるけど…
**`test.each`** を使うとスッキリするよ〜！✨

Vitestでも `test.each` が使える（Jest互換）って公式に書いてあるよ💡([Vitest][1])

```ts
import { describe, expect, test } from "vitest";
import { calcTotal } from "./calcTotal";

describe("calcTotal（test.each版）", () => {
  test.each([
    { price: 1000, taxRate: 0.1, expected: 1100 },
    { price: 1000, taxRate: 0, expected: 1000 },
    { price: 0, taxRate: 0.1, expected: 0 },
    { price: 101, taxRate: 0.1, expected: 111 },
  ])("price=$price tax=$taxRate → $expected", ({ price, taxRate, expected }) => {
    // Arrange
    // （この例だと Arrange は入力そのものなので、ここは最小でOK）

    // Act
    const actual = calcTotal(price, taxRate);

    // Assert
    expect(actual).toBe(expected);
  });
});
```

**test名に値が出る**から、落ちたときの原因特定が一気にラクになるよ〜😆🔍

---

## 8) テスト実行の小ワザ（速く回す）

⚡🧪Vitestは通常 `vitest` をスクリプトに入れて回す形が基本で、`vitest run` で“一回だけ実行”もできるよ〜💡([Vitest][2])
（「保存するたび動く」⇄「1回だけ」切り替えられるの助かる✨）

あと、VS Code向けの公式拡張も案内されてるよ🧩💖([Vitest][2])

---

## 9) よくある事故 → AAAで防げるやつ🧯😵‍💫### 事故1：Assertが多すぎて、落ちたとき何が悪いか不明👻✅ まずは **Assertは1個** で固定（慣れたら増やす）



### 事故2：Arrangeが長すぎて、テストが小説📚✅ 「テストの主役は何？」って自問して、不要データは削る✂️

### 事故3：1テストで2つのことを検証しちゃう🍱🍰✅ テストを2つに割る（落ちたときの意味が明確になる✨

）

---

## 10) AI（Copilot/Codex）

での“賢い使い方”🤖🎀AAAはAIにも指示しやすいのが強み！✨
おすすめの頼み方👇

* 「この関数の境界値テストケースを10個、**AAA形式のテスト名**で列挙して」
* 「`test.each` にできる形で、入力と期待値の表にして」
* 「落ちやすいケース（0/1/最大/境界前後）を優先して」

⚠️ ただし、AIが出したケースは**“仕様として正しいか”**だけは自分でチェックね😉✅

---

## 11) ミニ練習問題（やってみよ〜！

）🎒🧪✨### 練習A：ケースを増やす📈`calcTotal` に対して、次のケースを **AAAで** 追加してみてね👇



* `price=1, taxRate=0.1` のときどうなる？🧐
* `price=999, taxRate=0.1`（境界手前っぽい）
* `price=1000, taxRate=0.08`（税率違い）

### 練習B：`test.each` 化🍱いま書いたテストを、`test.each` にまとめてみる🎉

---

## まとめ（この章で持ち帰るもの）

🎁✨* テストは **AAA（準備→実行→確認）** で固定すると迷わない📐🧪


* ケースが増えたら **境界値** を狙う🚧✨
* コピペ地獄は **`test.each`** で救える🍱💖([Vitest][1])

ちなみに、いまどきの選択肢として **Vitest 4系**の安定版リリースが続いてるよ（例：v4.0.13）([GitHub][3])
一方で **Jest** も安定版が進んでいて（Jest 30.0 が stable として案内）([Jest][4])、AAAはどっちでもそのまま使えるよ〜🙆‍♀️✨

---

次の章（第8章）では、このAAAがめちゃくちゃ効く **“純粋関数（I/Oゼロの中心）”** を気持ちよく量産していくよ🍰✨

[1]: https://vitest.dev/api/ "Test API Reference | Vitest"
[2]: https://vitest.dev/guide/ "Getting Started | Guide | Vitest"
[3]: https://github.com/vitest-dev/vitest/releases "Releases · vitest-dev/vitest · GitHub"
[4]: https://jestjs.io/versions "Jest"
