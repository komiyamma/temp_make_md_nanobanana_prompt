# 第20章：テスト名（仕様が読める命名）📝

![仕様が書かれた青い本](./picture/tdd_ts_study_020_blue_book.png)

テストって「落ちたときに読むもの」なんだよね😵‍💫💥
だから**テスト名＝そのまま“ミニ仕様書”**にしちゃうと、未来の自分（とチーム）がめちゃ助かるよ〜！✨

Vitestの公式ガイドでも、テスト名はわかりやすい英文1文（例：`adds 1 + 2 to equal 3`）みたいに「何が起きるべき？」をそのまま書く例になってるよ🧪📘 ([Vitest][1])

---

## 🎯 この章のゴール

* ✅ テストが落ちた瞬間に「原因の方向性」が分かる名前を付けられる
* ✅ 「関数名の暗記テスト」じゃなくて「**振る舞い（仕様）**」を表す名前にできる
* ✅ Given/When/Thenの考え方で、**読みやすい構造**にできる 💡

---

## 🧠 まず大事：テスト名が“悪い”と何が困るの？😿

### 😱 ありがち事故

* 失敗ログが「`should work` が落ちた」
  → **どれが何のテストか不明**で、調査が長引く⌛️
* テスト名が「`calcDiscount のテスト`」
  → **仕様じゃなくて実装名**だから、関数名変更で意味が壊れる🫠
* 1つのテストで「AもBもCも」確認してる
  → 落ちたときに「どれが原因？」ってなる💥

---

## 🧩 命名の基本ルール（最重要5つ）🌟

### 1) **“何を呼ぶか”じゃなくて “何が起きるべきか”**を書く 🧠✨

Roy Osherove も「テスト名は要求（requirement）を表すべき」って強調してるよ📌 ([Roy Osherove][2])

✅ 良い：`invalid coupon returns error`
❌ ダメ：`applyCoupon のテスト`

---

### 2) 3点セットで書くと強い（状況・操作・結果）🧱

有名な形がこれ👇

* **状態（Scenario / State）**
* **操作（Action / Unit of work）**
* **期待結果（Expected behavior）**

「UnitOfWork_StateUnderTest_ExpectedBehavior」みたいな整理の考え方が定番だよ🧩 ([Dan In a Can][3])
（.NETのベストプラクティスでも “3つの要素で命名” を推してるくらい、考え方が強い🙆‍♀️） ([Microsoft Learn][4])

---

### 3) Given / When / Then を“テスト名 or 構造”に持ち込むと爆読みやすい📚💕

Martin Fowler が Given-When-Then を「振る舞いを例で仕様化するスタイル」として紹介してるよ🧠 ([martinfowler.com][5])

おすすめは **describeをGiven/Whenにして、itをThenにする** 方式👇

```ts
import { describe, it, expect } from "vitest";
import { calcTotal } from "./calcTotal";

describe("Given カートが空である", () => {
  describe("When 合計金額を計算する", () => {
    it("Then 0円を返す", () => {
      expect(calcTotal([])).toBe(0);
    });
  });
});
```

👀 これ、ログに出たときにそのまま読めるのが最高〜！

---

### 4) “should” は使ってもOKだけど、**中身が命**😺

「`should` を付けるかどうか」よりも、「**具体的な期待**が書いてあるか」が本体だよね、って話はよく出るよ🧁 ([Hacker News][6])

✅ 良い：`should reject when coupon is expired`
❌ ダメ：`should work`

---

### 5) 1テスト = 1つの約束（1つの理由で落ちる）🧷

テスト名も「約束1つ」に合わせると綺麗✨
`A and B and C` って入れたくなったら、だいたい分割チャンスだよ〜✂️💕

---

## 🧪 “良い命名”のテンプレ3種（迷ったらここから！）

### ✅ テンプレA：文章型（短くて強い）📝

* `returns 0 when cart is empty`
* `throws error on invalid email`

Vitest公式の例も「短い英文で振る舞い」を書いてる感じだよ🧪 ([Vitest][1])

---

### ✅ テンプレB：Given/When/Then（読み物最強）📘

* describe: `Given ...`
* describe: `When ...`
* it: `Then ...`

（Given-When-Then は BDD の文脈で有名だよ〜） ([martinfowler.com][5])

---

### ✅ テンプレC：3要素（状態・操作・結果）🧱

* `calcTotal_emptyCart_returns0`
* `applyCoupon_expired_returnsError`

この形は定番としてよく紹介されるやつだよ🧩 ([Dan In a Can][3])

---

## 🚫 よくある“ダメ命名”パターン集（あるある😂）

### ❌ 1) 抽象的すぎ

* `should work`
* `handles edge case`

👉 **何が？どの状況で？どうなる？** がゼロ😵‍💫

---

### ❌ 2) 実装に寄りすぎ（ホワイトボックス臭）

* `calls fetch once`
* `uses parseInt`

👉 仕様じゃなくて「内部事情」になりがち
（内部変えても仕様が同じならテスト名は変わらないのが理想💖）

---

### ❌ 3) 関数名が主役

* `calcDiscount test`
* `test parseUser`

👉 関数名は変更されるし、仕様は残る。主役は仕様👑

---

## 🧪 手を動かす：テスト名を10個改善しよう🎯✨

ここでは「悪い例 → 良い例」を10本セットで練習するよ💪💕

1. `should work`
   → `returns 0 when cart is empty`

2. `calcTotal test`
   → `calcTotal returns sum of item prices`

3. `error test`
   → `throws error when email is empty`

4. `coupon`
   → `rejects coupon when expired`

5. `discount boundary`
   → `applies max discount cap when discount exceeds limit`

6. `tax`
   → `rounds tax down to nearest yen`

7. `array test`
   → `preserves item order when sorting is not requested`

8. `should not fail`
   → `returns ok for valid input`

9. `parse user`
   → `maps dto to domain model and fills defaults when missing`

10. `async test`
    → `rejects when server returns 500`

🌸コツ：**名詞（cart/coupon/tax）＋条件（empty/expired/over limit）＋結果（returns/throws/applies）** を並べると強いよ！

---

## 🤖 AIの使い方（命名だけで頼ると超便利）✨🤖

### ① 仕様文 → テスト名案を3〜5個出してもらう📝

**プロンプト例：**

```text
次の仕様を Vitest のテスト名にしたいです。
短く、具体的で、失敗時に原因が想像できる命名を5案ください。
Given/When/Then 版も1案ください。

仕様：
「クーポンが期限切れなら、割引は適用せず、エラーを返す」
```

### ② “今の名前”を貼って改善案を出させる🧹

```text
次のテスト名が曖昧です。誤解が少ない名前に3案リネームしてください。
各案について「どの情報が増えたか」も説明して。

現状：should work
テスト内容：空のカートなら合計は0円
```

### ③ 失敗ログから「読むべきテスト名」へ寄せる📛

```text
この失敗ログを見て、原因が追いやすいテスト名に変えたい。
現状の名前と、改善案を3つください。

（ログを貼る）
```

⚠️ ただし最後に決めるのは自分ね😉（AIが“仕様”を勝手に作らないように✨）

---

## ✅ 章末チェックリスト（これが全部OKなら合格〜💮）

* ✅ テスト名だけ見て「状況・操作・期待」が想像できる
* ✅ 関数名変更しても、テスト名の意味が壊れにくい
* ✅ 1つのテストが「1つの理由」で落ちる（分割できてる）
* ✅ describe / it の階層が “物語” になってる（読める）

---

## 🎁 おまけ：迷った時の“即席ルール”🍬

![画像を挿入予定](./picture/tdd_ts_study_020_name_improvement.png)

* **it/test は「結果」だけ書く**（returns/throws/applies）
* **describe は「前提」だけ書く**（Given/When）
* “何の仕様？”が分からないなら、名詞（ドメイン語）を先に置く（cart/coupon/tax…）

---

次の章（第21章：テストデータ最小化🧸✨）に行く前に、もし今ある自分のテストコードがあれば、テスト名だけ10〜20個貼ってくれてもOKだよ😊💕
一緒に「落ちた瞬間に分かる名前」に整えていこ〜！🧪🎀

[1]: https://vitest.dev/guide/?utm_source=chatgpt.com "Getting Started | Guide"
[2]: https://osherove.com/blog/2005/4/3/naming-standards-for-unit-tests.html?utm_source=chatgpt.com "Naming standards for unit tests"
[3]: https://daninacan.com/naming-conventions-for-tests-in-c/?utm_source=chatgpt.com "Naming conventions for tests in C# - Dan In a Can"
[4]: https://learn.microsoft.com/en-us/dotnet/core/testing/unit-testing-best-practices?utm_source=chatgpt.com "Best practices for writing unit tests - .NET"
[5]: https://martinfowler.com/bliki/GivenWhenThen.html?utm_source=chatgpt.com "Given When Then"
[6]: https://news.ycombinator.com/item?id=34761915&utm_source=chatgpt.com "Start test names with “should” (2020)"
