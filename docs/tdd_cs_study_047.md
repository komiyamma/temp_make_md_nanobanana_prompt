# 第47章：Blazorの“テストしやすい分離”を作る（UIとロジックを分ける）🧩

この章はひとことで言うと、**「Blazorの画面（Razorコンポーネント）を“薄く”して、ロジックを“テストできる場所”に引っ越す」**練習だよ〜😊💡
Blazor Web App テンプレートは **1つのプロジェクトからSSR/クライアント側の両方を扱える**形になっていて便利だけど、油断すると **UIにロジックが混ざりやすい**のが罠⚠️
（※Blazor Web App テンプレの説明は Microsoft Docs にもあるよ） ([Microsoft Learn][1])

---

## この章のゴール🎯✨

![画像を挿入予定](./picture/tdd_cs_study_047_blazor_separation.png)

* ✅ **UI（.razor）は「表示＋イベント配線」だけ**にできる
* ✅ 重要なルール（計算・検証）を **クラスライブラリへ移して xUnit でテスト**できる
* ✅ 仕様変更が来ても、**UIを壊しにくく**できる（安心感〜🥹🛡️）

---

## 今日つくるミニ題材🎀📦

「推し活グッズ管理」の超ミニ版として、

* グッズを追加（名前/カテゴリ/単価/数量）
* 合計金額・合計点数を表示

を作るよ〜😊
ポイントは、**合計計算や入力チェックをUIに書かない**こと🧠✨

---

## まず結論：Blazorで“分離できてる”状態って？👀✅

### ✅ 良い感じ（おすすめ）🌼

* `.razor`：表示、ボタン押下などのイベント、画面の状態（入力欄の文字列とか）
* `Core`（クラスライブラリ）：入力チェック、計算、ルール（＝テストしたいもの）
* `Tests`：CoreをxUnitでガンガン検証🧪✨

### ❌ ありがち地獄（つらい）😵‍💫

* `@code { ... }` の中に

  * `if` が増える
  * 計算式が増える
  * 例外処理が増える
  * 画面更新とルールが絡まり始める
    → テストしにくい＆変更が怖い💥

---

## 最新の前提の“確認だけ”してから進むよ🔍✨

* .NET 10 の最新は **10.0.2（2026-01-13）** ([Microsoft][2])
* Visual Studio 2026 のリリースノート上でも **2026-01-13 の更新（18.2.0）**が出てるよ ([Microsoft Learn][3])
* C# 14 は **.NET 10 SDK / Visual Studio 2026** で試せるよ、って Microsoft Docs にも明記されてるよ ([Microsoft Learn][4])

（ここは“確認”だけね😊 この章の主役は分離！）

---

## ハンズオン：UIを薄くして、ロジックをテストへ引っ越す🏃‍♀️💨🧪

### 1) ソリューション構成をこうする📁✨

最低限これでOK！

* `OshiGoods.Blazor`（Blazor Web App）
* `OshiGoods.Core`（クラスライブラリ：ルール置き場）
* `OshiGoods.Core.Tests`（xUnit：テスト）

> コツ：**テストしたいものは Core に置く**。UIは“薄く”。

---

### 2) まずCoreに「ドメイン（グッズ）」を作る🎁

### GoodsItem（入力チェックはここへ！）🧷

```csharp
namespace OshiGoods.Core;

public sealed record GoodsItem
{
    public string Name { get; }
    public string Category { get; }
    public decimal UnitPrice { get; }
    public int Quantity { get; }

    private GoodsItem(string name, string category, decimal unitPrice, int quantity)
    {
        Name = name;
        Category = category;
        UnitPrice = unitPrice;
        Quantity = quantity;
    }

    public static GoodsItem Create(string name, string category, decimal unitPrice, int quantity)
    {
        if (string.IsNullOrWhiteSpace(name))
            throw new ArgumentException("Name is required.", nameof(name));

        if (string.IsNullOrWhiteSpace(category))
            throw new ArgumentException("Category is required.", nameof(category));

        if (unitPrice < 0)
            throw new ArgumentOutOfRangeException(nameof(unitPrice), "UnitPrice must be >= 0.");

        if (quantity <= 0)
            throw new ArgumentOutOfRangeException(nameof(quantity), "Quantity must be > 0.");

        return new GoodsItem(name.Trim(), category.Trim(), unitPrice, quantity);
    }

    public decimal LineTotal => UnitPrice * Quantity;
}
```

🌟 ここが大事！
入力チェック（名前必須、単価マイナス禁止、数量0禁止）を **UIじゃなくCoreに入れた**よね😊✅
→ だから **テストで守れる**！

---

### 3) 次にCoreへ「集計ロジック」を作る📊✨

```csharp
namespace OshiGoods.Core;

public sealed record GoodsSummary(int TotalQuantity, decimal TotalPrice);

public static class GoodsSummaryCalculator
{
    public static GoodsSummary Calculate(IEnumerable<GoodsItem> items)
    {
        if (items is null) throw new ArgumentNullException(nameof(items));

        int totalQty = 0;
        decimal totalPrice = 0m;

        foreach (var item in items)
        {
            totalQty += item.Quantity;
            totalPrice += item.LineTotal;
        }

        return new GoodsSummary(totalQty, totalPrice);
    }
}
```

---

### 4) ここでTDD！テストを先に書くよ🧪🚦

`OshiGoods.Core.Tests` にテストを書く（xUnit）✨

```csharp
using OshiGoods.Core;
using Xunit;

public class GoodsItemTests
{
    [Fact]
    public void Create_ValidInput_CreatesItem()
    {
        var item = GoodsItem.Create("アクスタ", "グッズ", 1200m, 2);

        Assert.Equal("アクスタ", item.Name);
        Assert.Equal("グッズ", item.Category);
        Assert.Equal(1200m, item.UnitPrice);
        Assert.Equal(2, item.Quantity);
        Assert.Equal(2400m, item.LineTotal);
    }

    [Theory]
    [InlineData("")]
    [InlineData("   ")]
    public void Create_EmptyName_Throws(string name)
    {
        Assert.Throws<ArgumentException>(() => GoodsItem.Create(name, "グッズ", 100m, 1));
    }

    [Fact]
    public void Create_NegativePrice_Throws()
    {
        Assert.Throws<ArgumentOutOfRangeException>(() => GoodsItem.Create("アクスタ", "グッズ", -1m, 1));
    }

    [Fact]
    public void Create_ZeroQuantity_Throws()
    {
        Assert.Throws<ArgumentOutOfRangeException>(() => GoodsItem.Create("アクスタ", "グッズ", 100m, 0));
    }
}
```

```csharp
using OshiGoods.Core;
using Xunit;

public class GoodsSummaryCalculatorTests
{
    [Fact]
    public void Calculate_Empty_ReturnsZero()
    {
        var summary = GoodsSummaryCalculator.Calculate(Array.Empty<GoodsItem>());

        Assert.Equal(0, summary.TotalQuantity);
        Assert.Equal(0m, summary.TotalPrice);
    }

    [Fact]
    public void Calculate_MultipleItems_SumsCorrectly()
    {
        var items = new[]
        {
            GoodsItem.Create("アクスタ", "グッズ", 1200m, 2), // 2400
            GoodsItem.Create("缶バッジ", "グッズ", 500m, 3),   // 1500
        };

        var summary = GoodsSummaryCalculator.Calculate(items);

        Assert.Equal(5, summary.TotalQuantity);
        Assert.Equal(3900m, summary.TotalPrice);
    }
}
```

🎉 これで、**UIなしで仕様が守れる**ようになった！
（しかも速い⚡️）

---

### 5) 最後にBlazor UIを“薄く”作る🎨🪶

`OshiGoods.Blazor` のページ例（`Pages/Goods.razor`）
※UIは「入力→Coreで生成→一覧に足す→Coreで集計」だけ！

```csharp
@page "/goods"
@using OshiGoods.Core

<h3>推し活グッズ管理（ミニ）🎀📦</h3>

<div style="display:grid; gap:8px; max-width:520px;">
    <input placeholder="名前（例：アクスタ）" @bind="name" />
    <input placeholder="カテゴリ（例：グッズ）" @bind="category" />
    <input placeholder="単価（例：1200）" @bind="unitPriceText" />
    <input placeholder="数量（例：2）" @bind="quantityText" />

    <button @onclick="Add">追加する➕✨</button>

    @if (!string.IsNullOrWhiteSpace(error))
    {
        <div style="color:red;">⚠️ @error</div>
    }
</div>

<hr />

<h4>一覧🧾</h4>
<ul>
    @foreach (var item in items)
    {
        <li>@item.Name（@item.Category）: @item.UnitPrice 円 × @item.Quantity 個 = @item.LineTotal 円</li>
    }
</ul>

@{
    var summary = GoodsSummaryCalculator.Calculate(items);
}
<h4>集計📊</h4>
<p>合計点数：@summary.TotalQuantity 個</p>
<p>合計金額：@summary.TotalPrice 円</p>

@code {
    private string name = "";
    private string category = "";
    private string unitPriceText = "";
    private string quantityText = "";
    private string error = "";

    private readonly List<GoodsItem> items = new();

    private void Add()
    {
        error = "";

        try
        {
            if (!decimal.TryParse(unitPriceText, out var unitPrice))
                throw new ArgumentException("単価は数字で入れてね🥺");

            if (!int.TryParse(quantityText, out var qty))
                throw new ArgumentException("数量は整数で入れてね🥺");

            // ✅ ここが主役：入力チェックはUIじゃなくCoreに寄せる
            var item = GoodsItem.Create(name, category, unitPrice, qty);

            items.Add(item);

            // 入力欄クリア（UI都合）
            name = category = unitPriceText = quantityText = "";
        }
        catch (Exception ex)
        {
            error = ex.Message;
        }
    }
}
```

### ね、UIが薄いでしょ？😊✨

* ルール：`GoodsItem.Create` / `GoodsSummaryCalculator`（Core）
* UI：入力して押して表示するだけ🎨

---

## この章の“分離ルール”まとめ（超だいじ）🧠✅

### ✅ UI（.razor）に残していいもの🙆‍♀️

* 入力欄の文字列
* ボタン押下やイベント
* 表示の切り替え（エラーメッセージ出す等）
* 画面の状態（一覧を保持、選択中のIDなど）

### ✅ Coreへ追い出すもの🏃‍♀️💨

* 入力の妥当性（必須、範囲、形式）
* 計算（合計、割引、上限）
* 条件分岐のルール（カテゴリ別、在庫の扱い等）
* 仕様として守りたいもの全部🧪✨

---

## AI（Copilot/Codex）使い方：この章の勝ちパターン🤖🏆

AIは便利だけど、**UIにロジックをベタ貼り**しがち😇
だからお願いの仕方を固定しよ〜！

* 「この仕様を **Core（UIなし）** で表現するとしたら、どんなクラス？」🤖✨
* 「xUnitで **境界値** を含むテストケースを列挙して🧪」
* 「このCreateメソッド、例外の種類はこれでいい？改善案ある？」🧯
* 「UI側は薄くしたい。`@code` から追い出す候補を指摘して👀」

最後の採用条件はいつもこれ👇
**✅ テストが通る ＋ ✅ 意図どおり ＋ ✅ UIが薄い**

---

## よくある落とし穴（先に潰す）🕳️💥

* ❌ `@code` に計算式が増えていく（その瞬間、Coreへ引っ越し！）
* ❌ 入力チェックをUIにだけ書く（テスト不能になりがち）
* ❌ 例外を握りつぶして無言（最低でもメッセージは出そ）
* ❌ 「とりあえず動いた！」で止める（**テストが仕様**だよ〜🧪）

---

## ミニ課題（10〜20分）⏱️🎀

1. ✅ 「カテゴリが空ならエラー」を `GoodsItem.Create` に追加してテストを書く🧪
2. ✅ 合計金額が **10,000円超えたら “買いすぎ警告”** をUIに出す（※警告条件はCoreに置いてもOK）⚠️
3. ✅ `GoodsSummary` に「平均単価」を追加してテストを書く📊

---

もし次へ進めるなら、**第48章（bUnitでコンポーネントテスト）**に入る前に、
この章の状態（UI薄い＆Coreがテストされてる）を作れてるとめちゃ強いよ〜😊🧪✨

[1]: https://learn.microsoft.com/en-us/aspnet/core/blazor/project-structure?view=aspnetcore-10.0&utm_source=chatgpt.com "ASP.NET Core Blazor project structure"
[2]: https://dotnet.microsoft.com/en-US/download/dotnet/10.0?utm_source=chatgpt.com "Download .NET 10.0 (Linux, macOS, and Windows) | .NET"
[3]: https://learn.microsoft.com/en-us/visualstudio/releases/2026/release-notes?utm_source=chatgpt.com "Visual Studio 2026 Release Notes"
[4]: https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-14?utm_source=chatgpt.com "What's new in C# 14"
