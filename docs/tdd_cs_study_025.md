# 第25章：テスト側のリファクタ（テストもコード）🧹

この章はひとことで言うと、**「テストが増えても読みやすく保つお掃除テク」**だよ〜😊💕
（実装だけじゃなく、**テストも育てる**のがTDDの気持ちいいところ！）

※最新状況メモ：.NET 10 の最新パッチは 10.0.2（2026-01-13時点）で、Visual Studio 2026 も同日にアップデートが出てるよ📌 ([Microsoft][1])
xUnit は v3 系が正式リリースされてるよ🧪 ([xunit.net][2])

---

## 1) この章のゴール🎯✨

![画像を挿入予定](./picture/tdd_cs_study_025_dry_trap.png)

章末にこうなれたら勝ち〜！😆🎉

* ✅ テストの「読みづらさ」を**におい**で嗅ぎ分けられる👃🚨
* ✅ 重複を減らしつつ、**意図（仕様）が見える**テストに直せる👀📘
* ✅ 共通化をやりすぎずに、ちょうどよく整えられる🧼✨
* ✅ AIに手伝わせても、**“意図が消える共通化”**を回避できる🤖🛡️

---

## 2) テストもリファクタが必要な理由🧪➡️📚

テストって、増えるとこうなりがち👇😵‍💫

* Arrange（準備）が毎回長い…😇
* 似たテストが大量にコピペ…📄📄📄
* ちょっと仕様追加すると、修正箇所が10個…😱
* テストが読めなくて、壊れた時に直せない…🫠

でも逆に言うと、テストがスッキリしてると👇😍

* 失敗した時に「何が壊れたか」すぐ分かる⚡
* 仕様追加も、最小の修正で済む✂️
* AIの提案を採用する判断も速い🏎️💨

---

## 3) “テストのにおい”チェックリスト👃🚨（見つけたらお掃除チャンス！）

### においA：Arrangeが長すぎる🧱🧱🧱

* テストの本題（Act/Assert）に辿り着く前に疲れる…😮‍💨
* **原因**：テストデータ作りが毎回ベタ書き
* **対策**：テストデータビルダー／ヘルパー／Factory化🧸✨

### においB：同じAssertが散らばる✅✅✅

* 似た確認があちこちに…
* **対策**：カスタムAssert（意味のある名前の検証関数）📌

### においC：テスト名は違うのに、中身ほぼ同じ👯‍♀️

* **対策**：パラメータ化（Theory/InlineData）🔁

### においD：ヘルパーが増えすぎて、逆に読めない🌪️

* **対策**：共通化は“最小”だけ。**意図が見える名前**にする📝✨

---

## 4) リファクタ道具箱🧰✨（この章の“型”）

### 道具①：Arrangeの共通化（ただしやりすぎ注意）🧸

* **小さなヘルパー**：`CreateCart()` みたいに、意図が伝わるやつ
* **テストデータビルダー**：設定が多い時に強い

### 道具②：カスタムAssert（意味を名前に閉じ込める）✅📌

たとえば「税込合計が正しい」みたいな**仕様っぽい言葉**で書けるようにする✨

### 道具③：パラメータ化（ケース増殖に耐える）🔁

xUnit v3 でも `[Fact]` / `[Theory]` を使ってデータ駆動できるよ🧪 ([xunit.net][3])
（ここでは基本の `InlineData` でいくね！）

---

## 5) 実演：カフェ会計テストを“育てる”☕️🧾🧹

ここからは「ありがちな汚れ」をわざと作って、**段階的に整える**よ〜😊✨

### 5-1) お掃除前：コピペ増殖テスト（あるある）😇

```csharp
using Xunit;

public class CafeCheckoutTests
{
    [Fact]
    public void Total_with_tax_should_be_correct_case1()
    {
        // Arrange
        var items = new[]
        {
            new LineItem("Coffee", 500, 1),
            new LineItem("Cake", 450, 1),
        };
        var taxRate = 0.10m;

        // Act
        var result = CafeCheckout.CalculateTotal(items, taxRate);

        // Assert
        Assert.Equal(1045, result);
    }

    [Fact]
    public void Total_with_tax_should_be_correct_case2()
    {
        // Arrange (ほぼ同じ…)
        var items = new[]
        {
            new LineItem("Coffee", 500, 2),
            new LineItem("Cake", 450, 1),
        };
        var taxRate = 0.10m;

        // Act
        var result = CafeCheckout.CalculateTotal(items, taxRate);

        // Assert (ここも同じ…)
        Assert.Equal(1595, result);
    }
}
```

👀つらいポイント：

* Arrangeが毎回同じで長い🧱
* Assertも同じ✅
* ケース増えるほどコピペ地獄📄😵‍💫

---

### 5-2) ステップ1：まずはパラメータ化🔁✨（コピペを減らす）

```csharp
using Xunit;

public class CafeCheckoutTests
{
    [Theory]
    [InlineData(1, 1045)]
    [InlineData(2, 1595)]
    public void Total_with_tax_should_be_correct(int coffeeQty, int expectedTotal)
    {
        // Arrange
        var items = new[]
        {
            new LineItem("Coffee", 500, coffeeQty),
            new LineItem("Cake", 450, 1),
        };
        var taxRate = 0.10m;

        // Act
        var result = CafeCheckout.CalculateTotal(items, taxRate);

        // Assert
        Assert.Equal(expectedTotal, result);
    }
}
```

✅これだけで「ケースを増やすコスト」が激減！🎉
でも…Arrangeがまだ重いよね？😇

---

### 5-3) ステップ2：Arrangeを“意図が分かる形”で短くする🧸✨

ここが重要！
**共通化＝短くすること**じゃなくて、**読みやすくすること**だよ😊💕

```csharp
using Xunit;

public class CafeCheckoutTests
{
    [Theory]
    [InlineData(1, 1045)]
    [InlineData(2, 1595)]
    public void Total_with_tax_should_be_correct(int coffeeQty, int expectedTotal)
    {
        // Arrange
        var items = StandardOrder(coffeeQty);
        var taxRate = StandardTaxRate();

        // Act
        var result = CafeCheckout.CalculateTotal(items, taxRate);

        // Assert
        Assert.Equal(expectedTotal, result);
    }

    private static LineItem[] StandardOrder(int coffeeQty)
        => new[]
        {
            new LineItem("Coffee", 500, coffeeQty),
            new LineItem("Cake", 450, 1),
        };

    private static decimal StandardTaxRate() => 0.10m;
}
```

✨ポイント

* `StandardOrder` って名前が「このテストで使う標準注文だよ」って伝えてくれる📝
* ヘルパーは **“小さく・意味のある名前”** が正義👑

---

### 5-4) ステップ3：カスタムAssertで“仕様っぽく”する✅📘✨

`Assert.Equal` が増えだすと、テストが「数字当てゲーム」になりがち😇
**“何を保証したいのか”** を名前に入れるよ！

```csharp
using Xunit;

public class CafeCheckoutTests
{
    [Theory]
    [InlineData(1, 1045)]
    [InlineData(2, 1595)]
    public void Total_with_tax_should_be_correct(int coffeeQty, int expectedTotal)
    {
        var items = StandardOrder(coffeeQty);
        var taxRate = StandardTaxRate();

        var total = CafeCheckout.CalculateTotal(items, taxRate);

        AssertTotalIs(total, expectedTotal);
    }

    private static LineItem[] StandardOrder(int coffeeQty)
        => new[]
        {
            new LineItem("Coffee", 500, coffeeQty),
            new LineItem("Cake", 450, 1),
        };

    private static decimal StandardTaxRate() => 0.10m;

    private static void AssertTotalIs(int actual, int expected)
        => Assert.Equal(expected, actual);
}
```

ここでは小さめだけど、例えば将来「端数処理」や「上限」や「割引」みたいな条件が増えたら、
`AssertTotalIs` を `AssertTotalWithTaxIs(...)` とかにして、意図をもっと強くできるよ😊✨

---

## 6) でも注意！やりすぎ共通化の“地雷”💣😵

### 地雷①：ヘルパーが増えすぎて迷子🗺️

* `CreateDefault()` が大量にある
* どれが何のテスト用かわからん😇

✅対策：ヘルパーは **テストクラス内で完結**させるのが最初は楽✨
共通化は「同じ意味の重複」が3回くらい出てからでOK👌

### 地雷②：何でもBuilderにして“賢くしすぎる”🤯

* Builderの中が条件分岐だらけ
* テストを読むよりBuilderを読む時間が長い😵‍💫

✅対策：Builderは「設定が多い時だけ」使う。
そして **メソッド名で意図を表現**する（例：`WithCoupon()` とか）🎟️

---

## 7) AIの使い方🤖✨（この章にちょうどいい頼み方）

AIには「共通化の候補」を出させるのは強い！
でも採用は**最小**でね😊🧡

### コピペ用プロンプト📝🤖

* 「このテスト、重複してるArrange/Assertを **3つ** 指摘して。共通化案も出して」
* 「共通化しすぎて **意図が消えそうな所** があれば警告して」
* 「このテスト群をTheory化するなら、InlineDataの案を作って」

---

## 8) 練習問題（手を動かすやつ）✍️🧪✨

### 課題A：Theory化でコピペ退治🔁

1. 似たテストを3本用意（数量・税率・商品点数など）
2. `[Theory]` + `InlineData` にまとめる
3. テスト名を「何が保証されるか」に寄せる📝

### 課題B：Arrangeを短くしつつ意図を残す🧸

* Arrangeが10行超えるテストを1本選ぶ
* `StandardOrder()` みたいに「意味ある名前」のヘルパーに分解
* ただし **ヘルパーは2〜3個まで**を目標に（増えたらやりすぎサイン🚨）

### 課題C：カスタムAssertを1個作る✅

* “仕様っぽい言葉”で `Assert...` を1つ作る
  例：`AssertTotalIs(...)` / `AssertDiscountApplied(...)` など✨

---

## 9) 今日の持ち帰りチェック✅🎒✨

最後にこれだけ覚えとけばOK！😆💕

* ✅ テストもコード。読めないならリファクタ対象🧹
* ✅ 共通化は「短くする」じゃなく「意図を見せる」ため✨
* ✅ まずは **Theory化** → 次に **Arrange整理** → 最後に **カスタムAssert** ✅
* ✅ ヘルパー増殖は危険信号。最小で止める🚨

---

次の章（第26章：カフェ会計②）では、仕様が増えてきた時に「このテストの整え方」が効いてくるよ〜☕️🎟️🧾✨

[1]: https://dotnet.microsoft.com/en-US/download/dotnet/10.0?utm_source=chatgpt.com "Download .NET 10.0 (Linux, macOS, and Windows) | .NET"
[2]: https://xunit.net/releases/v3/3.0.0?utm_source=chatgpt.com "Core Framework v3 3.0.0 [2025 July 13]"
[3]: https://xunit.net/docs/getting-started/netcore/cmdline?utm_source=chatgpt.com "Getting Started with xUnit.net v3 [2025 August 13]"
