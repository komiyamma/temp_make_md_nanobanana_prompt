# 第64章：Entity Framework Core と DDDの折り合い 🧩✨

![Entity Framework Core と DDDの折り合い](./picture/ddd_cs_study_064_efcore_bridge.png)

**〜マッピングの苦労を最小限にするコツ〜** 🥰📦

DDDって「ドメインをきれいにしたい」し、EF Coreって「DBに保存したい」ので、最初はケンカしがちです😵‍💫💥
でも大丈夫！**“折り合いの付け方” はだいたいパターン化**できます😊🧠

---

## この章のゴール 🎯✨

読み終わったら、こうなります👇

* ✅ **ドメイン層をEF Core汚染させずに**保存できる（がんばりすぎないDDD）
* ✅ **Value Object / 集約 / private set** を保ったままマッピングできる
* ✅ EF Coreの「ここで詰まる！」が先回りで回避できる 😎✨

EF Coreは最新の安定版が **EF Core 10.0**（.NET 10向け）で、サポートも長めです📌 ([Microsoft Learn][1])

---

## まず結論：勝ちパターンはこれ 🏆✨

### ✅ ルールはたった2つ！

1. **ドメインモデルは “DBの都合” を知らない**（なるべく）🙈
2. **DB都合は Infrastructure 側で吸収**する（Fluent APIで）🧹✨
 
 ```mermaid
 classDiagram
    class Domain_Order {
        +OrderId Id
        +Money Total
        -List~OrderLine~ _lines
    }
    note for Domain_Order "DB属性は一切つけない！🚫"
    
    class Infra_OrderConfig {
        +Configure(builder)
    }
    note for Infra_OrderConfig "テーブル名、カラム名、\n変換ルールは全部こっち！🏗️"
    
    Infra_OrderConfig ..> Domain_Order : 設定を外付け
 ```
 
 EF Coreは .NETのリリースと足並みを揃えて進化する方針なので、**「EF Core側で吸収する設計」**が長期的にラクです😊 ([Microsoft Learn][1])

---

## DDDとEF Coreがぶつかるポイントあるある 😭⚡（そして解決法）

### ① `public set;` をやめたい（不変にしたい）😤

DDDでは「勝手に書き換え禁止！」が基本です🔒✨
でもEF Coreは「読み込み時に値入れたい」ので、雑にやると `public set;` になりがち。

✅ **解決**：`private set;` / privateフィールド / backing field を使う
→ **“外から変更できないけど、EF Coreは内部的に詰められる”** を作ります🥳

---

### ② 引数なしコンストラクタ問題 🤔

DDDでは「必須情報ないと生成させない！」ってしたいですよね😌
でもEF Coreは読み込みに **引数なしコンストラクタ** を要求する場面があります。

✅ **解決**：`private` な引数なしコンストラクタを用意する
→ 外から使えないのでDDDの美しさは守れます💅✨

---

### ③ Value Object をどう保存するの？（一番つらい）😇

例：`Money` / `Email` / `OrderId` みたいなやつ。

✅ **解決は2択**（だいたいこれでOK）👇

* **Owned Entity Type**（“埋め込み型”）📦
* **ValueConverter**（1カラムに変換して保存）🔄

---

### ④ 集約の中のコレクション（`List<T>`）がしんどい 😵‍💫

DDD的にはこうしたい👇

* 集約内部のコレクションは **private List**
* 外には **IReadOnlyCollection** で見せる
* 追加はメソッド経由（不変条件を守る）💪

✅ **解決**：**フィールドマッピング** + `OwnsMany`（または別テーブル）
→ EF Coreは「privateフィールド」をマッピングできます🎉（Fluent APIで）

---

## 最小サンプル：DDDっぽい集約をEF Coreで保存する 🛒✨

題材：注文（Order）集約

* `Order`（集約ルート）
* `OrderId`（Value Object）
* `Money`（Value Object）
* 注文明細（OrderLine）を集約内に持つ

---

### 1) ドメイン側（きれいに保つ）🧼✨

```csharp
// Domain/Orders/OrderId.cs
public readonly record struct OrderId(Guid Value)
{
    public static OrderId New() => new(Guid.NewGuid());
}
```

```csharp
// Domain/Shared/Money.cs
public sealed record Money
{
    public decimal Amount { get; }
    public string Currency { get; }

    private Money(decimal amount, string currency)
    {
        if (amount < 0) throw new ArgumentOutOfRangeException(nameof(amount));
        if (string.IsNullOrWhiteSpace(currency)) throw new ArgumentException("Currency is required.", nameof(currency));

        Amount = amount;
        Currency = currency;
    }

    public static Money Of(decimal amount, string currency = "JPY") => new(amount, currency);
}
```

```csharp
// Domain/Orders/OrderLine.cs
public sealed class OrderLine
{
    public string ProductCode { get; private set; } = default!;
    public int Quantity { get; private set; }
    public Money UnitPrice { get; private set; } = default!;

    private OrderLine() { } // EF Core用

    public OrderLine(string productCode, int quantity, Money unitPrice)
    {
        if (string.IsNullOrWhiteSpace(productCode)) throw new ArgumentException(nameof(productCode));
        if (quantity <= 0) throw new ArgumentOutOfRangeException(nameof(quantity));

        ProductCode = productCode;
        Quantity = quantity;
        UnitPrice = unitPrice;
    }

    public Money LineTotal() => Money.Of(UnitPrice.Amount * Quantity, UnitPrice.Currency);
}
```

```csharp
// Domain/Orders/Order.cs
public sealed class Order
{
    // ★ public set なし！
    public OrderId Id { get; private set; }
    public DateTimeOffset CreatedAt { get; private set; }

    // ★ 集約内コレクションは private
    private readonly List<OrderLine> _lines = new();
    public IReadOnlyCollection<OrderLine> Lines => _lines.AsReadOnly();

    public Money Total { get; private set; } = Money.Of(0);

    private Order() { } // EF Core用

    private Order(OrderId id)
    {
        Id = id;
        CreatedAt = DateTimeOffset.UtcNow;
        Total = Money.Of(0);
    }

    public static Order CreateNew() => new(OrderId.New());

    public void AddLine(string productCode, int quantity, Money unitPrice)
    {
        _lines.Add(new OrderLine(productCode, quantity, unitPrice));
        RecalcTotal();
    }

    private void RecalcTotal()
    {
        var sum = _lines.Sum(x => x.LineTotal().Amount);
        Total = Money.Of(sum, "JPY");
    }
}
```

ポイント：

* ドメインは **EF Core参照ゼロ**でいけます😊✨
* なのに **保存できる**ようにInfra側でがんばる💪

---

### 2) Infrastructure側（EF Coreマッピングで吸収する）🧰✨

```csharp
// Infrastructure/AppDbContext.cs
using Microsoft.EntityFrameworkCore;
using YourApp.Domain.Orders;

public sealed class AppDbContext : DbContext
{
    public DbSet<Order> Orders => Set<Order>();

    public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) {}

    protected override void OnModelCreating(ModelBuilder modelBuilder)
        => modelBuilder.ApplyConfigurationsFromAssembly(typeof(AppDbContext).Assembly);
}
```

```csharp
// Infrastructure/Orders/OrderConfiguration.cs
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using YourApp.Domain.Orders;
using YourApp.Domain.Shared;

public sealed class OrderConfiguration : IEntityTypeConfiguration<Order>
{
    public void Configure(EntityTypeBuilder<Order> b)
    {
        b.ToTable("Orders");

        // OrderId(Value Object) を1カラムに変換して保存（ValueConverter）
        b.HasKey(x => x.Id);
        b.Property(x => x.Id)
            .HasConversion(
                id => id.Value,
                value => new OrderId(value));

        b.Property(x => x.CreatedAt);

        // Money(Value Object) は Owned で2カラムに展開
        b.OwnsOne(x => x.Total, money =>
        {
            money.Property(x => x.Amount).HasColumnName("TotalAmount");
            money.Property(x => x.Currency).HasColumnName("TotalCurrency");
        });

        // private List<OrderLine> _lines を OwnsMany で別テーブル化
        b.OwnsMany<OrderLine>("_lines", lines =>
        {
            lines.ToTable("OrderLines");
            lines.WithOwner().HasForeignKey("OrderId");

            // 明細側の主キー（Shadow Key）
            lines.Property<int>("Id");
            lines.HasKey("Id");

            lines.Property(x => x.ProductCode).HasMaxLength(64);
            lines.Property(x => x.Quantity);

            // UnitPrice も Money なので Owned
            lines.OwnsOne(x => x.UnitPrice, money =>
            {
                money.Property(x => x.Amount).HasColumnName("UnitPriceAmount");
                money.Property(x => x.Currency).HasColumnName("UnitPriceCurrency");
            });
        });

        // 読み取り専用コレクションはEFに「フィールドで触ってね」と教える
        b.Navigation(nameof(Order.Lines)).UsePropertyAccessMode(PropertyAccessMode.Field);
    }
}
```

この形にすると、DDD側は **きれいなまま**、EF Core側は **現実的に保存できる**ようになります🥹✨
EF Core 10.0 の安定版とサポート期間もMicrosoftが公開してます📌 ([Microsoft Learn][1])

---

## ここがラクになる！実務の “最小苦労” ルール 7つ 🧠🪄

1. **ドメイン層に `[Column]` とか属性を貼らない**（貼ると増殖する😇）
2. マッピングは **`IEntityTypeConfiguration<T>` に分割**（見失わない📁✨）
3. Value Objectは基本 **Owned**、1カラムで済むなら **Converter**
4. 集約内の子はまず **`OwnsMany`** を検討（小さく済む）
5. **ナビゲーションプロパティを無理に public set にしない**（フィールドでOK）
6. DB都合で例外が出たら、まず **Infrastructureで吸収できないか？** を考える
7. どうしても無理なら、そこで初めて **“DDDの理想を少し折る”**（最小限で✨）

---

## AIに手伝わせると爆速になるところ 🚀🤖✨（でも注意！）

EF Coreマッピングは「書く量が多い」ので、AIがめっちゃ得意です😊💕

### ✅ AIに投げると良いもの

* `OrderConfiguration` みたいな Fluent API の下書き
* Owned / Converter の候補出し
* “この例外、原因なに？” の切り分け

### ⚠️ でも最後にあなたがチェックする場所

* **集約の境界**が壊れてない？（子を勝手にDbSetにしてない？）😇
* **不変条件**が守られてる？（AddLineを無視してList直接いじってない？）😇
* **ドメインがDB用の形**になってない？（逆転してない？）😇

---

## よくあるエラーTOP3（先に潰す）💣🧯

### 🧨「The entity type requires a primary key」

→ `OwnsMany` の子（OrderLines）にキーがない
✅ `lines.Property<int>("Id"); lines.HasKey("Id");` を足す！

### 🧨「Cannot access a disposed context」

→ だいたい **Lazy Loading** を入れて事故ってる
✅ 1人開発ならまず **Lazy Loadingなし**がおすすめ🥹（読み込みは明示的に）

### 🧨「A second operation started on this context」

→ 同じDbContextを同時に使ってる（await絡み）
✅ まずは「1リクエスト=1DbContext」を徹底✨（DIのスコープ）

---

## まとめ 🎀✨

DDDとEF Coreは、**ガチガチに完全一致させようとすると疲れます**😵‍💫
でもこの章の形なら、こうなります👇

* ドメインは **きれい** 🧼✨
* EF Coreは **現実に強い** 🧰✨
* 変更に強いまま、保存もできる 💪📦

ちなみにEF Coreの安定版リリースとサポート期限はMicrosoftが一覧で出してます（EF Core 10.0は .NET 10向けで 2028年までサポート）📌 ([Microsoft Learn][1])

---

## 次章チラ見せ 👀✨（第65章）

**「トランザクション管理」**です！
「集約をまたいで更新したい…どうするの？」っていう、めっちゃ現実の壁を一緒に越えます🧱🔥

---

必要なら、この章のサンプルを **「4プロジェクト構成（Domain/Application/Infrastructure/Web）」にして、最小APIで動く完成形**にした版も書けますよ😊✨

[1]: https://learn.microsoft.com/en-us/ef/core/what-is-new/ "EF Core releases and planning | Microsoft Learn"
