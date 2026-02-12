# 第05章：テストは仕様書（読み物にする）📘

![設計図を見ながら建てる](./picture/tdd_ts_study_005_blueprint.png)

この章はひとことで言うと…
**「テストを “未来の自分＆仲間が読める仕様書” に育てる回」だよ〜！🥰🧪**

---

## 🎯 この章でできるようになること

* テストを見ただけで「何を保証してるか」を説明できる🙂📖
* “読めるテスト”の型（AAA）で、毎回迷わず書ける🧱✨
* テスト名だけで「状況→行動→期待結果」が伝わる📝💡
* 実装の写し（＝壊れやすいテスト）を避けられる🛡️

---

## 📘 なんで「テスト＝仕様書」なの？（超たいせつ）

TDDって、**テストが最初にできる仕様書**なんだよね🧪
そして未来でバグが起きた時は、だいたいこうなる👇

* テストが落ちる 😵‍💫
* 落ちたメッセージとテスト名を見る 👀
* **「何が壊れたか」が一瞬で分かる** → すぐ直せる🔧✨

だから、テストは「通すための儀式」じゃなくて、
**読んだ人を助ける文章**であるのが最強なの📘💕

---

## 🧱 “読めるテスト”の3点セット（ここだけ覚えてOK）✨

### 1) 📝 テスト名は「1行仕様」にする

おすすめはこのどっちか👇（混ぜないのがコツ！）

* ✅ **Should型**：「〜すべき」
  例：

  * should return 0 when cart is empty
  * should throw when zip code is invalid

* ✅ **Given/When/Then型**（状況が強い）
  例：

  * given empty cart, when calculate total, then returns 0

※ Given/When/Then は「状況→行動→結果」を強制できるから、仕様書っぽくなりやすいよ🧠✨（この考え方自体が一般的に紹介されてるよ） ([sonarsource.com][1])

---

### 2) 🧱 形は AAA（Arrange / Act / Assert）で固定

AAAは「読みやすさのための型」だよ📚
（AAAは定番パターンとして広く紹介されてるよ） ([Semaphore][2])

* **Arrange**：準備（入力・前提・依存）
* **Act**：実行（対象を1回呼ぶ）
* **Assert**：確認（期待結果を比べる）

👉 この型にすると、テストが **短い物語**みたいに読める📖✨

---

### 3) 🧸 データは「最小」かつ「意味がある」

ダメな例👇

* x = 3, y = 5（意味が伝わらない）😵
  良い例👇
* price = 1000, taxRate = 0.1（意図が読める）😊

「テストデータ＝説明文の一部」って思うと強いよ🧸📘

---

## 🚫 “実装の写し”にならないコツ（ここ超重要）🛡️

![画像を挿入予定](./picture/tdd_ts_study_005_anti_pattern_mirror.png)

テストが壊れやすくなる原因の代表👇

* 内部の関数や内部状態をベタベタ触る（実装変更で崩壊）💥
* 「どうやって」を確認してしまう（手順を縛る）🪢
* 1つのテストで色々確認しすぎる（何が壊れたか不明）😇

✅ 仕様書テストが見るのは基本これだけ：

* **入力**
* **出力**（またはエラー）
* **大事な副作用（必要なら）**

---

## 🧪 実践：悪いテストを “読み物” に直してみよう✨

ここから手を動かすよ〜！✊🥰
題材：郵便番号を正規化する関数（例）

* 入力「 123-4567 」→ 出力「1234567」みたいなやつ📮

### 😵 まず “悪い例”（読みにくい）

```ts
import { describe, it, expect } from "vitest";
import { normalizeZipCode } from "./normalizeZipCode";

describe("zip", () => {
  it("t1", () => {
    const r = normalizeZipCode(" 123-4567 ");
    expect(r).toBe("1234567");
    expect(r.length).toBe(7);
  });

  it("t2", () => {
    try {
      normalizeZipCode("12-34");
    } catch (e: any) {
      expect(e.message).toContain("invalid");
    }
  });
});
```

どこがツラい？😵‍💫

* 「t1」「t2」←仕様が読めない
* 1本のテストで2個assert（どっちが仕様の主役？）
* try/catchの書き方が読みにくい
* describe名が「zip」だけで曖昧

---

### ✅ “仕様書テスト”に変換（読み物へ📘）

```ts
import { describe, it, expect } from "vitest";
import { normalizeZipCode } from "./normalizeZipCode";

describe("normalizeZipCode", () => {
  it("should remove spaces and hyphen, and return 7 digits", () => {
    // Arrange
    const input = " 123-4567 ";

    // Act
    const result = normalizeZipCode(input);

    // Assert
    expect(result).toBe("1234567");
  });

  it("should throw when input is not 7 digits after normalization", () => {
    // Arrange
    const input = "12-34";

    // Act & Assert
    expect(() => normalizeZipCode(input)).toThrow();
  });
});
```

✨ 変換ポイント：

* テスト名がそのまま仕様文になった📝
* AAAで読みやすい📖
* assertは主役だけ（必要なら別テストに分ける）🧪
* 失敗テストは「落ち方」まで仕様にできる🚫

---

## 🗂️ 「仕様書っぽさ」を爆上げする小ワザ3つ🔥

### ① describe を “機能（仕様のまとまり）” で切る

「関数名」でもOKだし、「機能名」でもOKだよ😊

例：

* normalizeZipCode
* shipping fee calculation
* discount rules

---

### ② ケースが増えるなら “表で仕様” にする（テーブル駆動）📋✨

同じ仕様を入力違いでたくさん書きたいときは、Vitestの **test.each / test.for** が便利だよ🧪
（test.each と test.for の使い分けは公式APIにあるよ） ([Vitest][3])

```ts
import { describe, expect, test } from "vitest";
import { normalizeZipCode } from "./normalizeZipCode";

describe("normalizeZipCode", () => {
  test.each([
    { input: "123-4567", expected: "1234567" },
    { input: " 1234567 ", expected: "1234567" },
    { input: "１２３-４５６７", expected: "1234567" }, // 例：対応するなら
  ])("should normalize: $input -> $expected", ({ input, expected }) => {
    expect(normalizeZipCode(input)).toBe(expected);
  });
});
```

テスト名に値が埋まるから、落ちたとき **「どのケースが壊れたか」** が一瞬で分かるよ👀✨ ([Vitest][3])

---

### ③ describe.each / describe.for で「状況」をまとめて仕様化する🧩

「同じ状況で複数の仕様を確認したい」時に便利！
describe.each / describe.for も公式にあるよ📘 ([Vitest][3])

---

## 🤖 AIの使い方（この章のおすすめ🎀）

AIは「仕様を作る人」じゃなくて、**読みやすくする編集者**にするのが安全だよ✍️🤖✨

使える依頼例👇

1. **このテストが保証してることを1文にして**
2. **テスト名を “should型” で3案出して**
3. **AAAの境界が変なところを指摘して**
4. **このテスト、実装の写しになってない？怪しい点を3つ挙げて**
5. **境界値を追加するなら候補を5つ**

⚠️ 注意：AIの提案は採用前に「仕様として正しい？」を必ず自分で判断ね🥰🛡️

---

## ✅ チェックリスト（提出前にこれ見ると強い💪✨）

* テスト名だけで「状況→行動→結果」が想像できる？📝
* AAAが自然に読める？（準備→実行→確認）🧱
* そのテストは「1つの約束」だけを見てる？🤝
* 失敗したとき、どこが壊れたかすぐ分かる？👀
* 実装の手順を縛ってない？（内部に依存してない？）🛡️

---

## 🧪 ミニ課題（手を動かす✨）🎀

### お題：normalizeZipCode の仕様書テストを作ってね📮

次の仕様をテストで表現してみよう！

* ハイフンと前後スペースは消す
* 正規化後に7桁じゃないならエラー
* （任意）全角数字を半角に直す（対応するなら）

### 提出物イメージ📦

* 仕様が読めるテスト名で **3〜5本**
* AAAが揃ってる
* 可能なら test.each で表にする（ケース多いなら） ([Vitest][3])

---

必要なら、あなたが書いた “課題のテストコード” を貼ってくれたら、
**「仕様書として読みやすいか」観点で、命名・AAA・分割の改善案**を一緒に作るよ〜🥰📘✨

[1]: https://www.sonarsource.com/resources/library/code-coverage-unit-tests/?utm_source=chatgpt.com "Achieving High Code Coverage with Effective Unit Tests"
[2]: https://semaphore.io/blog/aaa-pattern-test-automation?utm_source=chatgpt.com "The Arrange, Act, and Assert (AAA) Pattern in Unit Test ..."
[3]: https://vitest.dev/api/ "Test API Reference | Vitest"

