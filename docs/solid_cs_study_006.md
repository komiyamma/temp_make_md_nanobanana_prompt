# 第06章：テストは“設計の味方”だよ🧪✨

この章はひとことで言うと…
**「SOLIDをやる前に、コードを触っても怖くない状態を作ろう」**です😊💕

テストがあると、リファクタリングしても
「動きが変わってないよね？✅」を機械が毎回チェックしてくれるので、設計改善が一気にラクになります✨

---

## 6.1 この章のゴール🎯💖

この章が終わったら、次ができるようになります👇✨

* 単体テストの基本形 **AAA（Arrange/Act/Assert）** が書ける🧁
![AAA Pattern Comic](./picture/solid_cs_study_006_aaa_pattern_comic.png)
* **“仕様を守るテスト”** を数本作って、安心してコード整理できる🧹✨
* 「テストしづらいコード＝設計の臭い👃💦」を見つけられる
* （ちょい最新✨）**Microsoft.Testing.Platform** が何者かを薄く理解する🤖
  ※Visual Studioのテストエクスプローラーとも統合されてるよ～！ ([Microsoft Learn][1])

---

## 6.2 テストがあると、SOLIDが進む理由💡🧸

![安全ネットとしてのテスト](./picture/solid_cs_study_006_testing_safety_net.png)

SOLIDって、だいたい「クラス分ける」「依存を差し替える」「境界を作る」みたいに**構造を動かす**んだけど…

構造を動かすのが怖い最大の理由って👇これです😇

* **動作が変わったら困る**
* でも人間の目では「変わってない」を保証しきれない

だからテストがあると、

* **Before/Afterの挙動が同じ**を短時間で何回も確認できる✅✨
* 「変更しても壊れてない」が見えるので、設計改善が進む🚀

---

## 6.3 まずは超入門：AAA（Arrange / Act / Assert）🍰✨

単体テストは、基本この3つだけ覚えればOKです😊💕

* **Arrange（準備）**：入力データや対象クラスを用意する🧺
* **Act（実行）**：メソッドを呼ぶ🎬
* **Assert（確認）**：結果が期待どおりかチェックする✅

この形があるだけで、テストが読みやすくなるよ～📚✨

---

## 6.4 テストプロジェクトを作る🧰🪄

### Visual Studioで作る（いちばん楽💕）

1. ソリューションを右クリック → **追加** → **新しいプロジェクト**
2. **xUnit テストプロジェクト**（または MSTest / NUnit）を選ぶ
3. `MiniECommerce.Tests` みたいな名前にする🧁
4. テストエクスプローラー（Test Explorer）で **Run All** ✅

> ちなみに .NET 10 は C# 14 とセットで、Visual Studio 2026 が対応しています📦✨ ([Microsoft][2])

### コマンドでも作れる（VS Code派にも◎）

```bash
dotnet new xunit -n MiniECommerce.Tests
dotnet test
```

---

## 6.5 サンプル題材：注文合計（割引＋送料）をテストする🛒💰✨

ここから「ミニEC」の“合計金額計算”を例にします😊
テストは **「仕様の見張り番👮‍♀️」** って感じで作るよ！

### まずはプロダクトコード（合計計算）📦

```csharp
using System;
using System.Collections.Generic;
using System.Linq;

public sealed record OrderItem(string Sku, decimal UnitPrice, int Quantity);

public enum ShippingMethod
{
    Standard,
    Express
}

public sealed class Order
{
    public List<OrderItem> Items { get; } = new();
    public decimal? CouponRate { get; init; } // 0.10m = 10% OFF
    public ShippingMethod Shipping { get; init; } = ShippingMethod.Standard;
}

public sealed class PriceCalculator
{
    public decimal CalculateTotal(Order order)
    {
        if (order is null) throw new ArgumentNullException(nameof(order));
        if (order.Items.Count == 0) return 0m;

        var subtotal = order.Items.Sum(i => i.UnitPrice * i.Quantity);

        var discount = order.CouponRate is { } rate ? subtotal * rate : 0m;
        var afterDiscount = subtotal - discount;

        var shippingFee = order.Shipping switch
        {
            ShippingMethod.Standard => afterDiscount >= 5000m ? 0m : 500m,
            ShippingMethod.Express => 900m,
            _ => throw new InvalidOperationException("Unknown shipping method.")
        };

        return afterDiscount + shippingFee;
    }
}
```

---

## 6.6 1本目のテスト：AAAで書く🧪🍓

```csharp
using Xunit;

public class PriceCalculatorTests
{
    [Fact]
    public void CalculateTotal_Standard_IsFreeShipping_WhenAfterDiscountIsAtLeast5000()
    {
        // Arrange 🧺
        var order = new Order
        {
            Shipping = ShippingMethod.Standard,
            CouponRate = 0.10m
        };
        order.Items.Add(new OrderItem("BOOK", 6000m, 1)); // 6000 → 10%OFF → 5400
        var sut = new PriceCalculator();

        // Act 🎬
        var total = sut.CalculateTotal(order);

        // Assert ✅
        Assert.Equal(5400m, total); // 送料0円
    }
}
```

この時点で、すでに価値が出てます✨
あとで内部の実装をどれだけ整理しても、このテストが通る限り「大丈夫そう😊」って言える！

---

## 6.7 テストを“仕様の箇条書き”にする（Theoryで増やす）🧁📌

「同じ形のテストを、入力だけ変えて何個もやりたい」ってときは **Theory** が便利✨

```csharp
using Xunit;

public class PriceCalculatorTheoryTests
{
    [Theory]
    [InlineData(4000, null, ShippingMethod.Standard, 4500)] // 4000 + 送料500
    [InlineData(5000, null, ShippingMethod.Standard, 5000)] // 5000 + 送料0
    [InlineData(3000, 0.10, ShippingMethod.Standard, 3200)] // 3000→2700 + 送料500 = 3200
    [InlineData(3000, 0.10, ShippingMethod.Express, 3600)]  // 3000→2700 + 送料900 = 3600
    public void CalculateTotal_WorksForCommonCases(
        decimal subtotal,
        double? couponRate,
        ShippingMethod shipping,
        decimal expected)
    {
        // Arrange 🧺
        var order = new Order
        {
            Shipping = shipping,
            CouponRate = couponRate is null ? null : (decimal)couponRate.Value
        };
        order.Items.Add(new OrderItem("SKU", subtotal, 1));
        var sut = new PriceCalculator();

        // Act 🎬
        var total = sut.CalculateTotal(order);

        // Assert ✅
        Assert.Equal(expected, total);
    }
}
```

✅ こういうテストが増えるほど、**安心してSOLID改善に突っ込める**ようになります🔥✨

---

## 6.8 「テストしにくいコード」は設計の赤信号🚨😵‍💫

よくある“テストしづらい元凶”👇

* `DateTime.Now` / `Guid.NewGuid()` / `Random`（毎回変わる）⏰🎲
* `new HttpClient()` とか、DBアクセス直書き（外部I/O）🌐🗄️
* `static` だらけ（差し替えできない）🧱
* 1メソッドが長くて、入力と出力がぐちゃぐちゃ（I/Oとロジック混在）🍝

これ、SOLIDの入口でめっちゃ効いてきます😇
だからこの章では **「差し替えできる形にする」** を小さく体験しよ✨

---

## 6.9 例：時間に依存する処理をテスト可能にする⌛🧸

### ダメな例（テストが不安定💦）

```csharp
public sealed class CampaignService
{
    public bool IsCampaignActive()
        => DateTime.Now.Hour >= 9 && DateTime.Now.Hour < 18;
}
```

テストが「朝は落ちる」「夜は通る」みたいになる😵‍💫💥

### いい例：時計を外から渡す🎁✨

```csharp
public interface IClock
{
    DateTime Now { get; }
}

public sealed class SystemClock : IClock
{
    public DateTime Now => DateTime.Now;
}

public sealed class CampaignService
{
    private readonly IClock _clock;

    public CampaignService(IClock clock) => _clock = clock;

    public bool IsCampaignActive()
        => _clock.Now.Hour >= 9 && _clock.Now.Hour < 18;
}
```

### テスト（好きな時間を作れる💖）

```csharp
using Xunit;

public sealed class FakeClock : IClock
{
    public DateTime Now { get; set; }
}

public class CampaignServiceTests
{
    [Fact]
    public void IsCampaignActive_ReturnsTrue_DuringBusinessHours()
    {
        // Arrange 🧺
        var clock = new FakeClock { Now = new DateTime(2026, 1, 9, 10, 0, 0) };
        var sut = new CampaignService(clock);

        // Act 🎬
        var active = sut.IsCampaignActive();

        // Assert ✅
        Assert.True(active);
    }
}
```

これが **「依存を外から渡す」** の超ミニ版🎀
あとでDIP/DIに入ったとき、「あ、これだ！」ってなるやつです😊✨

---

## 6.10 テスト実行の“最新寄り”メモ🧪🤖

最近の .NET では **Microsoft.Testing.Platform** という軽量テスト実行基盤が整備されていて、CLI/CI/Visual Studio/VS Code など色んな場面で動かしやすい方向です✨ ([Microsoft Learn][3])
xUnit v3 も Microsoft Testing Platform にネイティブ対応しています📦 ([xunit.net][4])

（でもね！）初心者のうちは難しく考えなくてOK😊
**Test Explorerで回せて、dotnet test で回せたら勝ち🏆** です✨

---

## 6.11 おまけ：カバレッジを“ざっくり”取る🧁📈

「テストがどこまで通ってるか」をざっくり見るなら、`dotnet test --collect:"XPlat Code Coverage"` が定番✨
テンプレートも既定で coverlet と統合されてる説明があります📌 ([Microsoft Learn][5])

```bash
dotnet test --collect:"XPlat Code Coverage"
```

> カバレッジは **高ければ偉い**じゃなくて、
> 「大事な分岐・大事な仕様を守れてる？」を見るための道具だよ😊💕

---

## 6.12 AIの使いどころ（この章は相性良すぎ🤖💕）

AIにはこう頼むと強いです👇✨

* 「このメソッドのテスト観点を5〜10個、理由つきで出して」🧠
* 「境界値（0、1、最大、null、空）を列挙して」📌
* 「AAAの形でxUnitテストを書いて。命名も提案して」🧁
* 「このテスト、足りないケースある？」🔍

⚠️ 注意：AIは“それっぽいけどズレた期待値”を置くことあるので、
**期待値は人間が仕様から決める**のが安全だよ😊✅

---

## 6.13 章末ミニ演習🎮✨（所要20〜40分）

### 演習A：送料ルールを守るテストを増やす📦

次をテストで守ってね👇😊

* Standard：5000以上なら送料0円
* Standard：4999以下なら送料500円
* Express：常に送料900円

### 演習B：例外・空の注文も守る😈

* `order = null` → `ArgumentNullException`
* `Itemsが空` → 合計0円

---

## 6.14 この章のチェックリスト✅💖

* [ ] テストはAAAで書けた🧁
* [ ] “仕様を守るテスト”が最低3〜6本ある🛡️
* [ ] テストしづらい原因（Now/Random/I/O/static）が分かる👃
* [ ] 1つだけでも依存を外から渡してテストできた🎁

---

次の章（第7章）では、ここで作った「安心の土台」を使って、**SOLID全体を地図みたいに整理**していきます🗺️🌈
「どこがどの原則に引っかかってるの？」を見分けられるようにしよ～😊✨

[1]: https://learn.microsoft.com/ja-jp/dotnet/core/testing/microsoft-testing-platform-intro?utm_source=chatgpt.com "Microsoft.Testing.Platform の概要 - .NET"
[2]: https://dotnet.microsoft.com/en-US/download/dotnet/10.0?utm_source=chatgpt.com "Download .NET 10.0 (Linux, macOS, and Windows) | .NET"
[3]: https://learn.microsoft.com/en-us/dotnet/core/testing/microsoft-testing-platform-intro?utm_source=chatgpt.com "Microsoft.Testing.Platform overview - .NET"
[4]: https://xunit.net/docs/getting-started/v3/microsoft-testing-platform?utm_source=chatgpt.com "Microsoft Testing Platform (xUnit.net v3) [2025 November 2]"
[5]: https://learn.microsoft.com/ja-jp/dotnet/core/testing/unit-testing-code-coverage?utm_source=chatgpt.com "単体テストにコードカバレッジを使用する - .NET"
