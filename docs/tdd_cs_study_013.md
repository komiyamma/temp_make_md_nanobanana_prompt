# 第13章：テスト名の付け方（読むだけで仕様）📝✨

この章はね、**「テストが落ちた瞬間に、何が壊れたか一発で分かる名前」**を作る練習だよ〜！😊
TDDって回せるようになってくると、最後に効いてくるのがここ🎯
**テスト名＝仕様書の見出し**だからね📘✨

---

## 1) この章のゴール🎯✨

![画像を挿入予定](./picture/tdd_cs_study_013_suite.png)

読み終わったら、こうなってたらOK！

* ✅ 失敗したテスト名だけで「状況（条件）」「やったこと」「期待結果」が分かる
* ✅ テスト名が**実装の都合**じゃなくて、**ユーザー視点のふるまい**になってる
* ✅ 長すぎる・見づらい時に、**表示名（DisplayName）**や**表示ルール（methodDisplay）**で読みやすくできる

xUnit では `[Fact]` に `DisplayName` を付けて、テストランナー上の表示を分かりやすくできるよ🧪✨ ([api.xunit.net][1])
さらに、`xunit.runner.json` の `methodDisplay` で **「クラス名＋メソッド名」か「メソッド名だけ」**かを切り替えられるよ📌 ([xUnit.net][2])

---

## 2) なんでテスト名がそんなに大事？😳💥

![画像を挿入予定](./picture/tdd_cs_study_013_cryptic_error.png)

テストが落ちたとき、最初に目に入るのはだいたいこれ👇

* 🔴 テスト一覧の名前（テストエクスプローラー）
* 🔴 CIのログに出たテスト名
* 🔴 「どれが壊れた？」の検索ワード

つまりテスト名が弱いと…

* 「何が壊れたの？」が分からない😵
* 調べるためにテストを開く→実装も開く→沼る🌀
* “壊れた理由”より“探す時間”が増える⏳

逆に強い名前だと…

* テスト名を見るだけで **修正ポイントが見える**👀✨
* バグの再現条件が、名前に書いてある🧠
* テストが「仕様一覧」になる📘✨

---

## 3) 良いテスト名の「必須3点セット」🧩✨

![画像を挿入予定](./picture/tdd_cs_study_013_naming_formula.png)

テスト名には、基本この3つが入ってると強いよ💪

1. **状況（条件）**：どんな状態？どんな入力？
2. **行動（When）**：何をした？
3. **結果（Then）**：どうなってほしい？

例（英語パターン）👇

* `CalculateTotal_WhenCouponApplied_ShouldApplyDiscount` 🎟️
* `AddItem_WhenQuantityIsZero_ShouldThrow` 🚫

例（日本語パターン）👇

* `合計金額_クーポン適用時_割引が反映される` 🎟️
* `数量が0のとき_商品追加すると_例外になる` 🚫

どっちでもOK！ただし **チーム内で統一**が超大事だよ〜😊✨

---

## 4) 命名テンプレ3選（これだけでだいぶ勝てる）🥇🥈🥉

![画像を挿入予定](./picture/tdd_cs_study_013_naming_stencils.png)

### テンプレA：`Method_WhenCondition_ShouldResult`（いちばん定番）✅

読みやすくて、落ちた時に強い！

* `CalculateTax_WhenAmountIs1000_ShouldReturn100` 💰
* `ApplyCoupon_WhenExpired_ShouldNotChangeTotal` ⛔️

### テンプレB：`Given_When_Then`（BDDっぽく、仕様っぽい）📘✨

「状況→行動→結果」が明確！

* `GivenMember_WhenPurchaseOverLimit_ThenDiscountIsCapped` 👑
* `GivenEmptyCart_WhenCheckout_ThenThrows` 🛒🚫

### テンプレC：日本語でも“仕様見出し”にする（読み物化）📖💕

教育用途だとめっちゃ効く✨

* `会計_端数処理_四捨五入される` 🔢
* `クーポン_期限切れ_適用されない` ⛔️

> コツ：**名詞（ドメイン語）を前に置く**と、一覧が仕様書っぽくなるよ📘✨

---

## 5) ダメになりがちな名前（あるある）😇💦

![画像を挿入予定](./picture/tdd_cs_study_013_implementation_leak.png)

### ❌ 実装の写し（“どうやって”を書いちゃう）

* `CalculateTotal_UsesDiscountService` ← 実装変えたら名前が嘘になる😵
  → ✅ `CalculateTotal_WhenCouponApplied_ShouldApplyDiscount` 🎟️

### ❌ 情報が足りない

* `CalculateTotal_Test1` 😇
* `ShouldWork` 😇
  → **条件と期待結果がゼロ！**

### ❌ 期待結果が曖昧

* `ReturnsTrue` / `ReturnsOk`
  → ✅ 何がどうOK？を名前に書く✨

---

## 6) 長すぎ問題の解決：DisplayName を使う🎀✨

![画像を挿入予定](./picture/tdd_cs_study_013_display_name_sticker.png)

テストメソッド名を分かりやすくすると、どうしても長くなりがちだよね😂
そんな時は、**表示名だけ人間向けにする**のが超便利！

xUnit の `[Fact]`（や `[Theory]`）には `DisplayName` があるよ🧪✨ ([api.xunit.net][1])

```csharp
using Xunit;

public class CafeCheckoutTests
{
    [Fact(DisplayName = "合計: クーポン適用時、割引が反映される 🎟️")]
    public void CalculateTotal_WhenCouponApplied_ShouldApplyDiscount()
    {
        // Arrange / Act / Assert
    }
}
```

* 👍 メソッド名：検索・規約のための“機械向け”
* 👍 DisplayName：一覧で読むための“人間向け”

この分業、教育にもチーム開発にもめちゃ強いよ😊✨

---

## 7) 一覧表示を読みやすくする：methodDisplay（超おすすめ）👀✨

![画像を挿入予定](./picture/tdd_cs_study_013_clean_view.png)

「テストエクスプローラーで、クラス名まで付いて長くて読めない〜！」ってなることある🥺
それ、**表示ルールを変える**とスッキリするよ！

### 方法A：`xunit.runner.json`（おすすめ）

`methodDisplay` を `"method"` にすると、**クラス名なしでメソッド名だけ**表示できるよ📌 ([xUnit.net][2])

```json
{
  "methodDisplay": "method",
  "methodDisplayOptions": "replaceUnderscoreWithSpace"
}
```

* `methodDisplay`: `"method"` / `"classAndMethod"` が選べる ([xUnit.net][2])
* `methodDisplayOptions`: 例えば `_` をスペースに変換できる（読みやすさUP） ([xUnit.net][3])

### 方法B：`.runsettings`（VSTestでまとめたい時）

RunSettings でも `MethodDisplay` を設定できるよ📌 ([xUnit.net][4])

```xml
<?xml version="1.0" encoding="utf-8"?>
<RunSettings>
  <xUnit>
    <MethodDisplay>method</MethodDisplay>
  </xUnit>
</RunSettings>
```

---

## 8) 実践：弱いテスト名を10個、強くする🔥📝

### ステップ1：ダメ名を並べる（例）

* `Test1`
* `DiscountTest`
* `ShouldThrow`
* `CalculateTotal_ReturnsCorrectValue`

### ステップ2：テンプレに当てはめて改善✨

* ✅ `CalculateTotal_WhenCartIsEmpty_ShouldReturnZero` 🛒0
* ✅ `ApplyDiscount_WhenOverLimit_ShouldCapDiscount` 🧢
* ✅ `AddItem_WhenQuantityIsZero_ShouldThrowArgumentOutOfRange` 🚫

### ステップ3：DisplayNameで“読み物化”（任意）📘

* ✅ `"合計: 空のカートは 0円になる 🛒0"`
* ✅ `"割引: 上限を超えない 🧢"`

---

## 9) ミニ演習：カフェ会計①のテスト名だけ先に作る☕️🧾✨

「実装はまだ！」でOK😊
テスト名だけで仕様を作ってみよう💡

例（あなたの仕様に合わせて増減OK）👇

* `CalculateTotal_WhenNoItems_ShouldReturnZero` 🛒0
* `CalculateTotal_WhenOneItem100Yen_ShouldReturn100` ☕️
* `CalculateTotal_WhenTax10Percent_ShouldIncludeTax` 💰
* `CalculateTotal_WhenRoundingRequired_ShouldRoundHalfUp` 🔢
* `ApplyCoupon_WhenExpired_ShouldNotChangeTotal` ⛔️🎟️

💡ここでのポイント：
**“どう実装するか”を考えない**で、**“どう振る舞うべきか”だけを書く**😊✨

---

## 10) AIの使いどころ（命名はAIが得意！）🤖💡✨

命名ってしんどいけど、AIがかなり役立つよ〜！

### コピペ用プロンプト🎁

* 「この仕様を Given/When/Then 形式の**テスト名**にして。候補を10個」
* 「このテスト名、**実装に寄りすぎてない？** 仕様っぽく直して」
* 「短くしつつ意味を落とさない案を3つ」
* 「テスト一覧で読みやすいように **先頭にドメイン名詞**を付けた案にして」

👉 ただし最後は、**自分の意図（仕様）に合ってるか**で採用判断ね✅✨

---

## 11) セルフチェック（3問）✅📝

1. テスト名に「条件」が入ってないと、何が困る？😵
2. テスト名が「実装の写し」になると、何が起きる？💥
3. 長い名前を読みやすくする手段を2つ言える？（DisplayName / methodDisplay など）🎀👀

---

## おまけ：最近の“名前まわり”小ネタ（最新）📌✨

* xUnit v3 では、テスト結果の読みやすさ向上のための仕組みが増えていて、**Theory の複雑なパラメータを分かりやすくラベル付けして表示する**用途も想定されてるよ（表示名と組み合わせて使う想定）🧪✨ ([xUnit.net][5])
* また、`.runner.json` の `methodDisplay` などは **v3 でも引き続き使える**よ📌 ([xUnit.net][2])

---

次の第14章は「1テスト1意図（欲張り禁止）🍰🙅‍♀️」だよね？
この第13章の命名が整ってると、第14章の“分割”がめっちゃ気持ちよく進むよ〜😊✨

[1]: https://api.xunit.net/v3/3.0.1/v3.3.0.1-Xunit.FactAttribute.DisplayName.html?utm_source=chatgpt.com "Property DisplayName"
[2]: https://xunit.net/docs/config-xunit-runner-json "Config with xunit.runner.json [2025 July 30] | xUnit.net "
[3]: https://xunit.net/docs/running-tests-in-msbuild "Running xUnit.net tests in MSBuild | xUnit.net "
[4]: https://xunit.net/docs/config-runsettings "Config with RunSettings (VSTest) [2025 July 30] | xUnit.net "
[5]: https://xunit.net/releases/v3/3.0.0 "Core Framework v3 3.0.0 [2025 July 13] | xUnit.net "
