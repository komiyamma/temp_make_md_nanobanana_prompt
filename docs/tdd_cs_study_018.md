# 第18章：ここまでの総合ミニ演習：カフェ会計①☕️🧾

この章は「いままでの型（AAA・命名・境界値・刻み方）」を、**1つの小さい題材でぜんぶ使う回**だよ〜！😊🎉
今日は **テスト3本**だけでOK👌（追加は“おかわり”で✨）

---

## 0) 今日つくる“最小仕様”📌（まずはシンプル！）

**カフェ会計**の合計金額（円）を出すだけ☕️

* 注文は「明細の配列（複数OK）」
* 各明細は：`単価(円) × 数量` を足して **小計**
* 税は **10%**（小計 × 0.10）
* 税の端数は **1円未満切り捨て**（floor）
* 合計 = 小計 + 税
* 注文が空なら合計は 0 円

> 端数ルール（切り捨て）をテストで固定するのが今日のキモだよ〜🎯✨

---

## 1) 今日のゴール🥅✨

![画像を挿入予定](./picture/tdd_cs_study_018_cleanup.png)

できたら勝ち！🎉

* ✅ **AAA** でテストがスッと読める
* ✅ **命名**が「仕様」になってる
* ✅ **境界値**（端数/空注文）を押さえる
* ✅ **Red → Green → Refactor** を小さく3回まわせる

---

## 2) プロジェクトの形（最小）🏗️🧪

作るのはこの2つだけ：

* `CafeCheckout`（本体：クラスライブラリ）
* `CafeCheckout.Tests`（テスト）

テストフレームワークは **xUnit v3系**が最新安定だよ〜🧪✨（2026/01/18時点で `xunit.v3 3.2.2`、VSアダプタは `xunit.runner.visualstudio 3.1.5`） ([xUnit.net][1])

---

## 3) まずはテストを書く（Red）🚦🔴

### テストファイル：`CafeCheckoutTests.cs`

狙い：**「1品だけ」**の合計（小計＋税）が出ること☕️

```csharp
using Xunit;

public class CafeCheckoutTests
{
    [Fact]
    public void Given_single_item_When_calculate_total_Then_subtotal_plus_tax_is_returned()
    {
        // Arrange
        var items = new[]
        {
            new LineItem(name: "Coffee", unitPriceYen: 500, quantity: 1),
        };

        // Act
        var total = CafeCheckout.CalculateTotalYen(items);

        // Assert
        Assert.Equal(550, total); // 500 + tax(50)
    }
}
```

ここで当然コンパイル通らないよね😇（`LineItem`も`CafeCheckout`も無い）
それでOK！それが **Red** 🔴✨

---

## 4) 最小実装で通す（Green）🟢✨

### 本体側：`CafeCheckout` に最小の形を作る

```csharp
public readonly record struct LineItem(string Name, long UnitPriceYen, int Quantity);

public static class CafeCheckout
{
    private const decimal TaxRate = 0.10m;

    public static long CalculateTotalYen(IEnumerable<LineItem> items)
    {
        ArgumentNullException.ThrowIfNull(items);

        long subtotal = 0;
        foreach (var item in items)
        {
            subtotal += item.UnitPriceYen * item.Quantity;
        }

        var tax = (long)Math.Floor(subtotal * TaxRate);
        return subtotal + tax;
    }
}
```

✅ テスト実行して **緑🟢** になった？🎉
なったら次！「まだ美しくしない」よ〜！ここは最短でOK🙆‍♀️✨

---

## 5) 2本目：複数明細の合算（Red → Green）🧾➕🧾

次は「複数アイテムの合算」🙂

```csharp
[Fact]
public void Given_multiple_items_When_calculate_total_Then_sum_and_tax_are_applied()
{
    // Arrange
    var items = new[]
    {
        new LineItem("Coffee", 500, 1), // 500
        new LineItem("Cake",   400, 2), // 800
    };

    // Act
    var total = CafeCheckout.CalculateTotalYen(items);

    // Assert
    // subtotal = 1300, tax = 130, total = 1430
    Assert.Equal(1430, total);
}
```

これ、いまの実装でたぶん通るよね？😆🟢
通ったら「Redが短すぎる…」って思うけど、そういう回もある！OK！👌✨

---

## 6) 3本目：端数（切り捨て）を固定（Red → Green）🎲🚫

ここが今日の山場⛰️✨
**小計が101円**だと税は **10.1円** → **10円（切り捨て）** にしたい！

```csharp
[Fact]
public void Given_fractional_tax_When_calculate_total_Then_tax_is_floored()
{
    // Arrange
    var items = new[]
    {
        new LineItem("Mini", 101, 1),
    };

    // Act
    var total = CafeCheckout.CalculateTotalYen(items);

    // Assert
    // subtotal = 101, tax = floor(10.1) = 10, total = 111
    Assert.Equal(111, total);
}
```

いまの実装は `Math.Floor` だから通るはず🟢✨
もし通らなかったら、**税の計算方法（decimal/丸め）**がズレてる可能性大だよ〜🔍💦

---

## 7) ここでリファクタ（Refactor）🧹✨（でも“小さく”ね！）

### 目的：読みやすくする（仕様は変えない）📘

例えば、**小計計算**と**税計算**を分けるだけで、意図がスッと入るよ🙂

```csharp
public static class CafeCheckout
{
    private const decimal TaxRate = 0.10m;

    public static long CalculateTotalYen(IEnumerable<LineItem> items)
    {
        ArgumentNullException.ThrowIfNull(items);

        var subtotal = CalculateSubtotal(items);
        var tax = CalculateTax(subtotal);

        return subtotal + tax;
    }

    private static long CalculateSubtotal(IEnumerable<LineItem> items)
    {
        long subtotal = 0;
        foreach (var item in items)
        {
            subtotal += item.UnitPriceYen * item.Quantity;
        }
        return subtotal;
    }

    private static long CalculateTax(long subtotal)
        => (long)Math.Floor(subtotal * TaxRate);
}
```

✅ リファクタのたびにテスト実行🟢🟢🟢
「緑のまま整える」が最強だよ〜🛡️✨

---

## 8) “空注文”はどうする？（今日の小さい境界値）🍩➡️0円

ここは追加で1本だけ（すぐ終わるやつ）🎯

```csharp
[Fact]
public void Given_no_items_When_calculate_total_Then_zero_is_returned()
{
    // Arrange
    var items = Array.Empty<LineItem>();

    // Act
    var total = CafeCheckout.CalculateTotalYen(items);

    // Assert
    Assert.Equal(0, total);
}
```

これも今の実装なら通るね🟢✨
**「空」って境界値**だから、こうやってテストに残すのえらい👏😊

---

## 9) 今日の“コミットの切り方”例（めちゃ大事）💾✨

おすすめはこんな感じ👇（超小刻み！）

1. 🔴 `Add failing test for single item total`
2. 🟢 `Make single item test pass with minimal implementation`
3. 🧹 `Extract subtotal/tax helpers (no behavior change)`
4. 🔴 `Add test for multiple items`
5. 🟢 `Make multiple items test pass`（通ってたならそのままでもOK）
6. 🔴 `Add rounding (floor) tax test`
7. 🟢 `Ensure tax rounding uses floor`（すでにOKなら確認コミットでもOK）
8. 🔴 `Add empty order test`（おかわり）
9. 🟢 `Pass empty order test`

---

## 10) AIの使いどころ（この章は“テスト案だけ”🤖🧪）

実装をAIに丸投げすると、**Greenで作り込みがち**で事故るから⚠️
今日はこれがおすすめ〜😊✨

### ✅ 使ってOKプロンプト例

* 「この仕様の**テストケース**を、正常/境界値で10個ちょうだい」
* 「端数処理の境界値（101円みたいな）をもっと挙げて」
* 「いまのテスト名、誤解が少ない命名案を3つ出して」

### ❌ 今日は封印（事故りやすい）

* 「実装全部書いて」👉 だいたい作り込みすぎる😵‍💫

---

## 11) できたかチェックリスト✅✨

* ✅ テストが **AAA** の形でそろってる？
* ✅ テスト名だけで仕様わかる？📝
* ✅ 税の端数（切り捨て）がテストで固定されてる？🎯
* ✅ 1回の変更がデカくなってない？（10分以内目安⏱️）

---

## 12) 2026/01/18時点の“最新情報メモ”📌✨（リサーチ結果）

* 2026年1月のサービス更新で **.NET 10 は 10.0.2** が案内されてるよ ([Microsoft for Developers][2])
* **C# 14** は .NET 10 でサポートされてるよ ([Microsoft Learn][3])
* **Visual Studio 2026** は 2026/01/13 に **18.2.0** の更新が出てるよ ([Microsoft Learn][4])
* **xUnit v3** は `xunit.v3 3.2.2`、VSアダプタは `xunit.runner.visualstudio 3.1.5` が最新安定として並んでるよ ([xUnit.net][1])

---

## おかわり（次章へつながる追加課題）🍰✨

余裕があったら1本だけ追加してみてね😊

* 🧪 **数量0**はOKにする？NGにする？（仕様を決めてテストにする）
* 🧪 **単価マイナス**はどうする？（例外にする？無視？）
* 🧪 税率を固定じゃなく引数にする（でもやりすぎ注意！）

---

次は（第19章）で、**「仮実装」**っていう“通すための技”を使って、もっと気持ちよく回せるようにするよ〜🩹✨

[1]: https://xunit.net/releases/ "Release Notes | xUnit.net "
[2]: https://devblogs.microsoft.com/dotnet/dotnet-and-dotnet-framework-january-2026-servicing-updates/ ".NET and .NET Framework January 2026 servicing releases updates - .NET Blog"
[3]: https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-14?utm_source=chatgpt.com "What's new in C# 14"
[4]: https://learn.microsoft.com/en-us/visualstudio/releases/2026/release-notes "Visual Studio 2026 Release Notes | Microsoft Learn"
