# 第15章：OCP実戦：料金計算・割引・ポイントを“追加に強く”する💰🎫

この章は、**追加ルールが増え続けがちな「料金計算」**を題材にして、OCP（拡張に開く／変更に閉じる）をガッツリ体に入れていくよ〜😊🧠✨
（.NET 10 は LTS で、2028/11/10 までサポート予定だよ✅） ([Microsoft for Developers][1])
（C# 14 は .NET 10 上で動く最新版として案内されてるよ✅） ([Microsoft Learn][2])

---

## 1. この章のゴール 🎯✨

### できるようになること 💪😊

* **割引ルールが増えても**、既存コードをなるべく触らずに追加できる🎁
* 「if/switch 追加祭り💥」から卒業して、**新クラス追加**で拡張できる🌱
* **テスト**で「壊してない」を確認しながら前に進める🧪✅

### 今日の合言葉 🗝️

* **「追加＝新しい部品を足す」**
* **「修正＝既存コードをいじる」**（できるだけ減らしたい）

---

## 2. まず“あるある地獄”を見よう 😇🔥（OCP違反の典型）

例えば「合計金額」を計算するところに、割引やポイントがどんどん増えると…こうなりがち👇

* 会員ランク割引（Silver/Gold/Platinum）✨
* クーポン割引（% / 固定額）🎫
* 期間キャンペーン（ブラックフライデー等）🛍️
* 初回購入割引🆕
* 送料割引🚚
* ポイント付与率の変更🎁
* “この条件のときだけ例外” 😵‍💫

そしてコードは…

```csharp
public class PriceService
{
    public PriceResult Calculate(Cart cart, Customer customer, Coupon? coupon, DateTime now)
    {
        decimal subtotal = cart.Items.Sum(x => x.Price * x.Quantity);

        // 会員割引
        if (customer.Rank == "Gold") subtotal *= 0.95m;
        else if (customer.Rank == "Platinum") subtotal *= 0.90m;

        // クーポン
        if (coupon != null)
        {
            if (coupon.Type == "Percent") subtotal *= (1m - coupon.Value);
            else if (coupon.Type == "Fixed") subtotal -= coupon.Value;
        }

        // キャンペーン
        if (now.Month == 11 && now.Day >= 20) subtotal *= 0.90m; // 雑！

        // ポイント
        int points = (int)(subtotal * 0.01m);

        return new PriceResult(subtotal, points);
    }
}
```

この状態の問題点はね…👇😢

* ルールが増えるたびに **このメソッドを編集**（＝変更が怖い）😱
* if/switch が伸び続ける（＝読むのがつらい）📈
* テストが書きづらい（＝安心できない）🧪💦
* 「割引の順番」や「併用可否」がカオスになりやすい🌀

---

## 3. OCPの方針を決めよう 🧭✨（料金計算は“ルールの集合”）

料金計算って、正体はだいたいこう👇

* **小計（Subtotal）**を出す
* **割引ルール**を適用する（1個〜複数）
* **ポイントルール**を適用する
* 結果をまとめる

つまり、OCP的にはこうするのが気持ちいい😊✨

> 「割引」や「ポイント」を **差し替え可能な“部品（ルール）”** にして、
> **本体はルールを並べて実行するだけ** にする🎠

---

## 4. 設計：拡張ポイントを作る（インターフェース）🧩✨

### 4.1 まずは必要なデータを整理 📦

「割引ルール」が判断に必要な情報を1つにまとめると便利だよ😊

```csharp
public sealed record CartItem(string Sku, decimal UnitPrice, int Quantity);

public sealed record Cart(IReadOnlyList<CartItem> Items)
{
    public decimal Subtotal => Items.Sum(x => x.UnitPrice * x.Quantity);
}

public sealed record Customer(string Id, MemberRank Rank, bool IsFirstPurchase);

public enum MemberRank { Regular, Silver, Gold, Platinum }

public sealed record Coupon(string Code, CouponType Type, decimal Value);
public enum CouponType { Percent, Fixed }

public sealed record PricingContext(
    Cart Cart,
    Customer Customer,
    Coupon? Coupon,
    DateTime Now
);
```

### 4.2 割引ルール用のインターフェース 🎫✨

ポイントはここ👇
「割引を適用できるか？」「適用したらいくらになる？」を**ルール自身**に持たせる👍

```csharp
public interface IDiscountRule
{
    int Priority { get; } // 適用順の目安（小さいほど先）
    bool IsMatch(PricingContext ctx);
    decimal Apply(decimal currentTotal, PricingContext ctx);
}
```

> これで「新しい割引」を追加したいときは、`IDiscountRule` の実装クラスを増やすだけ🌱✨
> 既存の計算本体は“なるべく”触らない＝OCP💕

---

## 5. 実装：割引を“ルールのパイプライン”で流す 🎠✨

![Conveyor belt with modular robot arms for Discounts, Taxes, Fees.](./picture/solid_cs_study_015_pricing_pipeline.png)

```csharp
public sealed record PriceResult(decimal Total, int Points, decimal Subtotal);

public sealed class PricingEngine
{
    private readonly IReadOnlyList<IDiscountRule> _discountRules;
    private readonly IPointRule _pointRule;

    public PricingEngine(IReadOnlyList<IDiscountRule> discountRules, IPointRule pointRule)
    {
        _discountRules = discountRules.OrderBy(r => r.Priority).ToList();
        _pointRule = pointRule;
    }

    public PriceResult Calculate(PricingContext ctx)
    {
        var subtotal = ctx.Cart.Subtotal;

        decimal total = subtotal;

        foreach (var rule in _discountRules)
        {
            if (!rule.IsMatch(ctx)) continue;
            total = rule.Apply(total, ctx);
        }

        // 0円未満にならない保険（※実務だとここもルール化することあるよ）
        total = Math.Max(0m, total);

        var points = _pointRule.CalculatePoints(total, ctx);

        return new PriceResult(total, points, subtotal);
    }
}
```

---

## 6. ルールを作ってみよう ✨（例：会員割引・クーポン・キャンペーン）

### 6.1 会員ランク割引 👑✨

```csharp
public sealed class MemberRankDiscountRule : IDiscountRule
{
    public int Priority => 100;

    public bool IsMatch(PricingContext ctx)
        => ctx.Customer.Rank is MemberRank.Gold or MemberRank.Platinum;

    public decimal Apply(decimal currentTotal, PricingContext ctx)
        => ctx.Customer.Rank switch
        {
            MemberRank.Gold => currentTotal * 0.95m,
            MemberRank.Platinum => currentTotal * 0.90m,
            _ => currentTotal
        };
}
```

### 6.2 クーポン割引 🎫✨

```csharp
public sealed class CouponDiscountRule : IDiscountRule
{
    public int Priority => 200;

    public bool IsMatch(PricingContext ctx) => ctx.Coupon is not null;

    public decimal Apply(decimal currentTotal, PricingContext ctx)
    {
        var coupon = ctx.Coupon!;
        return coupon.Type switch
        {
            CouponType.Percent => currentTotal * (1m - coupon.Value), // 例：0.10mで10%OFF
            CouponType.Fixed => currentTotal - coupon.Value,
            _ => currentTotal
        };
    }
}
```

### 6.3 期間キャンペーン（例：11月後半は10%OFF）🛍️✨

```csharp
public sealed class LateNovemberCampaignRule : IDiscountRule
{
    public int Priority => 50; // 先に適用したいなら小さめ

    public bool IsMatch(PricingContext ctx)
        => ctx.Now.Month == 11 && ctx.Now.Day >= 20;

    public decimal Apply(decimal currentTotal, PricingContext ctx)
        => currentTotal * 0.90m;
}
```

---

## 7. ポイントも“差し替え可能”にしちゃおう 🎁✨

```csharp
public interface IPointRule
{
    int CalculatePoints(decimal finalTotal, PricingContext ctx);
}

public sealed class StandardPointRule : IPointRule
{
    public int CalculatePoints(decimal finalTotal, PricingContext ctx)
        => (int)Math.Floor(finalTotal * 0.01m); // 1%
}
```

> これで「特定期間はポイント2倍！」とかも追加しやすいよ〜😊✨

---

## 8. ✅OCP達成の瞬間：新しい割引を“追加だけ”で入れる 🎉✨

### 例：初回購入は500円引き🆕🎫

**やることは「新クラス追加」だけ！**（既存の `PricingEngine` は触らない）

```csharp
public sealed class FirstPurchaseFixedDiscountRule : IDiscountRule
{
    public int Priority => 150;

    public bool IsMatch(PricingContext ctx) => ctx.Customer.IsFirstPurchase;

    public decimal Apply(decimal currentTotal, PricingContext ctx)
        => currentTotal - 500m;
}
```

### “組み立て”例（いったん手動でOK）🧩

```csharp
var rules = new List<IDiscountRule>
{
    new LateNovemberCampaignRule(),
    new MemberRankDiscountRule(),
    new FirstPurchaseFixedDiscountRule(),
    new CouponDiscountRule(),
};

var engine = new PricingEngine(rules, new StandardPointRule());

var ctx = new PricingContext(cart, customer, coupon, DateTime.Now);
var result = engine.Calculate(ctx);
```

> ここ、**後の章（DIP/DI）**で「DIコンテナで登録して自動組み立て」に進化させると超きれいになるよ🔌✨
> でも今は“手で並べる”だけでも OCP の感覚は十分つかめる👍😊

---

## 9. テストを書いて“追加しても壊れない”を作る 🧪✅

xUnit 例（超ミニ）👇

```csharp
using Xunit;

public class FirstPurchaseFixedDiscountRuleTests
{
    [Fact]
    public void FirstPurchase_Gets_500YenOff()
    {
        var rule = new FirstPurchaseFixedDiscountRule();

        var cart = new Cart(new[]
        {
            new CartItem("A", 1000m, 1),
        });

        var customer = new Customer("u1", MemberRank.Regular, IsFirstPurchase: true);
        var ctx = new PricingContext(cart, customer, coupon: null, Now: new DateTime(2026, 1, 1));

        var total = cart.Subtotal;
        var after = rule.Apply(total, ctx);

        Assert.Equal(500m, after);
    }
}
```

ポイント：**ルール単体**でテストできるのが最高なの🥹💕

---

## 10. よくある落とし穴（現実の料金計算あるある）⚠️😵‍💫

### 10.1 「適用順」が仕様になる問題 🌀

* 先に%OFF → 後に固定額OFF
* 先に固定額OFF → 後に%OFF
  結果が変わるよね😵‍💫

✅対策

* `Priority` を用意して順序を明示
* もしくは「割引の種類ごとにフェーズを分ける」（後で発展でOK）✨

### 10.2 「併用不可クーポン」問題 🚫🎫

* “キャンペーンとクーポンは併用できません” みたいなやつ😭

✅対策の方向性

* `PricingContext` に「適用済み情報」を持つ（例：Flags）
* もしくは `DiscountResult` を返して「次を止める」など
  （このへんは実務寄りなので、必要になったら一緒に育てよ😊🌱）

### 10.3 「ルール増えすぎ」問題 📈

✅対策

* ルールは**粒度を揃える**（細かすぎると管理がつらい）
* “本当に増えるところ”だけを拡張点にする（第14章の話⚖️😅）

---

## 11. 🤖AIメモ（Copilot/Codex系）✨🧠

使いどころを絞るとめちゃ強いよ〜！💕

* 「`IDiscountRule` を実装するクラスを作って。条件：◯◯のとき△△%OFF。Priorityは120。テストもxUnitで」
* 「割引の優先順位（Priority）案を提案して。会員割引、クーポン、キャンペーン、初回割引がある」
* 「“併用不可”仕様を入れるなら、ルール設計をどう拡張する？（既存コードを最小変更で）」
* 「この料金計算、OCP違反になりそうな点を指摘して、改善案を3つ」

---

## 12. 演習（ここ大事！）✍️😊✨

### 演習A：新割引ルールを追加してみよう 🎫

1. 「誕生月は 8%OFF 🎂」ルールを追加（新クラス追加のみ）
2. テストを書く（誕生月/誕生月じゃない）🧪✅

### 演習B：ポイントルールを差し替えよう 🎁

1. 「Gold以上はポイント2%」にする
2. 既存の `StandardPointRule` を壊さずに、新しい `VipPointRule` を作る
3. `PricingEngine` の組み立て側で差し替えるだけにする✨

---

## 13. まとめ 🌈✨

* 料金計算は「ルールが増える前提」の世界💰🎫
* OCPのコツは **“増えるものを部品化（ルール化）”** して、**本体は流すだけ**にする🎠✨
* 追加が来たら **新クラス追加**で済むようにすると、変更が怖くなくなる😊💕

次の章からは LSP に入って、「継承の約束」を守る話に進むよ〜🧱➡️🧱✨

[1]: https://devblogs.microsoft.com/dotnet/announcing-dotnet-10/?utm_source=chatgpt.com "Announcing .NET 10"
[2]: https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-14?utm_source=chatgpt.com "What's new in C# 14"
