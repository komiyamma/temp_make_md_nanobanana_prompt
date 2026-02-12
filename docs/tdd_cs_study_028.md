# 第28章：小さな設計の基本（超入門：責務を分ける）🧩

この章は「TDDで増えてきたロジックを、**壊さずにスッキリ分ける**」練習だよ〜😊🧪
（このロードマップは .NET 10（LTS）＋C# 14 世代の前提でOK🙆‍♀️✨ そして xUnit v3系で進めるよ〜） ([Microsoft][1])

---

## 1) 今日のゴール🎯✨

![画像を挿入予定](./picture/tdd_cs_study_028_clean_code_goal.png)

章の終わりに、こうなれたら勝ち！🏆

* 「このクラス、**“やること”が2個以上あるな…**」を嗅ぎ分けられる👃🚨
* テストが守ってくれてる状態で、**安全にクラス分割**できる🛡️🧪
* 分けた後に「どこ読めばいいか」が分かる **名前付け** ができる📝✨
* **分けすぎ事故**（細切れ地獄）を回避できる🍰🙅‍♀️

---

## 2) 「責務」ってなに？（超やさしく）🧠💡
![Responsibility Overload](./picture/tdd_cs_study_028_responsibility_overload.png)


責務＝そのクラスの「担当」だよ👩‍🏫✨
学園祭でたとえると…

* 出店の会計係💰
* 呼び込み係📣
* 在庫チェック係📦

…みたいに **担当が分かれてると強い** でしょ？😊
コードも同じで、**1つのクラスが“全部係”**になると、だんだん破綻する😵‍💫

---

## 3) 「分けるべき？」を判断する3つの質問🧩🔍
![Separation Questions](./picture/tdd_cs_study_028_separation_questions.png)


### ✅ 質問A：説明するとき「そして」が入る？

たとえば…

* ❌「注文を計算する **そして** クーポンも処理する **そして** 税も丸める」
  → “そして” が増えるほど、責務が混ざってるサイン🚨

### ✅ 質問B：変更理由が複数ある？

* 税率が変わる
* 割引ルールが増える
* 端数処理が変わる
  これ全部が同じクラスに来ると、修正が怖くなる😱💥

### ✅ 質問C：テストのArrangeがつらい？

Arrangeが長い＝「準備しないと動かない」＝依存や責務が重いサイン👃🚨
（テストの辛さは設計のアラームだよ🔔）

---

## 4) 分割の“最小ルール”🍀（分けすぎ防止つき）
![Refactoring Map](./picture/tdd_cs_study_028_refactor_map.png)


### 🌱 ルール1：まずは **メソッド抽出** から

いきなり新クラス乱立しない🙅‍♀️
まずは `Extract Method` で「塊」に名前を付ける📝✨

### 🌱 ルール2：クラスにするのは「変わりそうな塊」

税・割引・丸め…みたいに、**ルールが増えそう／変わりそう**なところから🙂

### 🌱 ルール3：クラス名は「名詞＋役割」で

* `TaxCalculator`（税の計算）
* `DiscountCalculator`（割引の計算）
* `CheckoutService`（会計の流れを指揮）

### 🌱 ルール4：分けたら“責務の地図”を作る🗺️

* 誰が何をやる？
* どこにルールがある？
  これが見えたら勝ち✨

---

## 5) ハンズオン：カフェ会計を「責務で分ける」☕️🧾✨

ここでは、ありがちな「全部入り会計」を、テストを守りながらスッキリ分けるよ〜😊🧪
（途中で何回テスト回してもOK！むしろ回して！🚦）

---

### 5-1) まずは題材（ざっくり仕様）📘

* 小計＝商品の合計
* クーポンがあれば割引（例：10%）
* 税（例：10%）を足す
* 最後に「円」想定で四捨五入（例として）🔢

---

### 5-2) テストを書く（仕様を固定）🧪✅

```csharp
using Xunit;

public class CheckoutTests
{
    [Fact]
    public void Total_NoCoupon_AddsTaxAndRounds()
    {
        var order = new Order()
            .AddItem("Coffee", 480m, 1)
            .AddItem("Cake", 520m, 1);

        var total = new CheckoutService().CalculateTotal(order, coupon: null);

        // 小計 1000 → 税10%で 1100 → 丸め 1100
        Assert.Equal(1100m, total);
    }

    [Fact]
    public void Total_WithTenPercentCoupon_DiscountsThenAddsTax()
    {
        var order = new Order()
            .AddItem("Coffee", 480m, 1)
            .AddItem("Cake", 520m, 1);

        var coupon = Coupon.TenPercentOff();

        var total = new CheckoutService().CalculateTotal(order, coupon);

        // 小計1000 → 割引10%で900 → 税10%で990 → 丸め990
        Assert.Equal(990m, total);
    }
}
```

> ポイント💡
>
> * テストが「仕様書」だよ📘✨
> * ここで決めた挙動は、リファクタしても変えない🛡️

---

### 5-3) “全部入り実装”（まずは通す）🩹➡️✅
![Monolithic Class](./picture/tdd_cs_study_028_before_split.png)


```csharp
public sealed class CheckoutService
{
    public decimal CalculateTotal(Order order, Coupon? coupon)
    {
        decimal subtotal = 0m;

        foreach (var item in order.Items)
            subtotal += item.UnitPrice * item.Quantity;

        if (coupon is not null)
            subtotal = subtotal * 0.9m; // 10% OFF（例）

        var taxed = subtotal * 1.10m; // 税10%（例）

        return decimal.Round(taxed, 0, MidpointRounding.AwayFromZero);
    }
}
```

これ、動くけど…
**「小計」「割引」「税」「丸め」全部やってる**よね？😵‍💫💥
責務が4つ混ざってる！

---

## 6) リファクタ：テストを守りながら分ける🚦🛡️✨

ここからが本番！
**1手ごとにテスト実行**ね🙂🧪（怖くない！）

---

### Step 1：メソッド抽出で “塊” に名前を付ける📝✨
![Method Extraction](./picture/tdd_cs_study_028_step1_extract.png)


```csharp
public sealed class CheckoutService
{
    public decimal CalculateTotal(Order order, Coupon? coupon)
    {
        var subtotal = CalculateSubtotal(order);
        var discounted = ApplyCouponIfAny(subtotal, coupon);
        var taxed = ApplyTax(discounted);
        return RoundToYen(taxed);
    }

    private static decimal CalculateSubtotal(Order order)
        => order.Items.Sum(i => i.UnitPrice * i.Quantity);

    private static decimal ApplyCouponIfAny(decimal subtotal, Coupon? coupon)
        => coupon is null ? subtotal : subtotal * 0.9m;

    private static decimal ApplyTax(decimal amount)
        => amount * 1.10m;

    private static decimal RoundToYen(decimal amount)
        => decimal.Round(amount, 0, MidpointRounding.AwayFromZero);
}
```

✅ ここでいったん「読める」ようになった！
でも責務はまだ同じクラスの中だね🙂

---

### Step 2：「変わりやすい塊」をクラスにする（税・割引）🧩✨
![Class Extraction](./picture/tdd_cs_study_028_step2_class.png)


まずは税から🧾（税率変わりがち！）

```csharp
public sealed class TaxCalculator
{
    private readonly decimal _rate; // 0.10m みたいなやつ

    public TaxCalculator(decimal rate) => _rate = rate;

    public decimal Apply(decimal amount) => amount * (1m + _rate);
}
```

割引も分けちゃう🎟️

```csharp
public sealed class DiscountCalculator
{
    public decimal Apply(decimal subtotal, Coupon? coupon)
        => coupon is null ? subtotal : subtotal * coupon.Multiplier;
}

public sealed class Coupon
{
    public decimal Multiplier { get; }

    private Coupon(decimal multiplier) => Multiplier = multiplier;

    public static Coupon TenPercentOff() => new Coupon(0.9m);
}
```

Checkoutは「流れ」だけにする🚦✨

```csharp
public sealed class CheckoutService
{
    private readonly DiscountCalculator _discounts = new();
    private readonly TaxCalculator _tax = new(rate: 0.10m);

    public decimal CalculateTotal(Order order, Coupon? coupon)
    {
        var subtotal = order.Subtotal();
        var discounted = _discounts.Apply(subtotal, coupon);
        var taxed = _tax.Apply(discounted);
        return decimal.Round(taxed, 0, MidpointRounding.AwayFromZero);
    }
}
```

✅ 責務の地図ができた🗺️✨

* Order：小計を出す
* DiscountCalculator：割引
* TaxCalculator：税
* CheckoutService：順番に呼ぶだけ

---

### Step 3：Order側も “責務として自然” に寄せる📦✨
![Final Responsibility Map](./picture/tdd_cs_study_028_responsibility_map.png)


```csharp
public sealed class Order
{
    private readonly List<OrderItem> _items = new();
    public IReadOnlyList<OrderItem> Items => _items;

    public Order AddItem(string name, decimal unitPrice, int quantity)
    {
        _items.Add(new OrderItem(name, unitPrice, quantity));
        return this;
    }

    public decimal Subtotal()
        => _items.Sum(i => i.UnitPrice * i.Quantity);
}

public sealed record OrderItem(string Name, decimal UnitPrice, int Quantity);
```

✅ 「注文＝明細を持つ、小計を出せる」って自然だよね😊

---

## 7) 分けた後の“チェックリスト”✅✨（分けすぎ防止つき）

* クラスの説明が **1文で言える**？（“そして”無し）🙂
* そのクラスが変わる理由は **1種類**？🎯
* 名前が「何をするか」伝わる？📝
* **小さくしすぎて**、追いかけるファイルが増えすぎてない？📁😵‍💫

  * 目安：今の段階は **3〜5クラスくらい**で十分🙆‍♀️✨

---

## 8) AIの使いどころ（この章の“勝ちパターン”）🤖✅✨

AIは便利だけど、ここでは **「分割案」と「命名案」だけ**使うのが安全😊🛡️

### そのままコピペ用プロンプト📎✨

* 「このクラスの責務が混ざってる点を3つ指摘して。分けるなら最小でどの塊？」
* 「`TaxCalculator` と `DiscountCalculator` の命名候補を5つ。誤解が少ない順に」
* 「このリファクタを“差分最小”でやる手順を、コミット単位で提案して」

> 採用条件はいつもこれ👇
> **テストが全部通る✅ ＋ 意図に一致✅**

---

## 9) 練習問題（1〜2コミットでOK）🎒✨

### 問題A：クーポンをもう1種類追加🎟️

* 「200円引きクーポン」を追加してね
* テストを先に書いて、通してね🧪✅
* ヒント：`Coupon` に `AmountOff` を持たせる？それとも別クラス？（どっちでもOK🙆‍♀️）

### 問題B：丸めの責務を分けたい人向け🔢✨

* `RoundToYen` を `RoundingPolicy` として切り出す
* ただし **やりすぎ注意**（今すぐ必要？を自問してね🙂）

---

## 10) ミニ復習クイズ🧠🎓✨

1. 「責務が混ざってる」サインはどれ？（複数OK）

* A. クラスの説明に「そして」が増える
* B. テストが短くて読みやすい
* C. 変更理由が2種類以上ある
* D. 1メソッドが長い

👉 正解：A / C / D ✅✨

---

## まとめ🎀✨

* **責務を分ける**と、テストも実装も読みやすくなる🧪📘
* いきなりクラス乱立じゃなくて、
  **メソッド抽出 → 変わりやすい塊だけクラス化** が安定🍀
* テストがあるから、分割しても怖くない🛡️✨

次の章以降（依存を切るパート）に行くと、ここで分けた「税」「割引」みたいな部品がさらに活きてくるよ〜🔌✨

[1]: https://dotnet.microsoft.com/en-US/download/dotnet/10.0?utm_source=chatgpt.com "Download .NET 10.0 (Linux, macOS, and Windows) | .NET"
