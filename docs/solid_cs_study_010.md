# 第10章：SRPの分割パターン②：検証（バリデーション）を整理する✅🧾

この章はね、「入力チェックが増えるほど、サービスが太って死ぬ😇」問題を、**SRP（単一責務）**でスッキリ治す回だよ〜！🌸✨
（本日時点：.NET 10 は 2025-11-11 にリリースされた LTS だよ📅）([Microsoft][1])

---

## 1. 今日のゴール🎯💕

終わるころには、こんな状態になってるのが理想！✨

* ✅ **「検証」って一口に言っても種類がある**って分かる
* ✅ **どこに置くべきか（入口 / ドメイン / 境界）**を決められる
* ✅ “巨大サービスにベタ書き検証”をやめて、**Validator に責務を分離**できる
* ✅ ついでに **テストしやすさが爆上がり**する🧪🚀

---

## 2. あるある：検証が増えると何が起きる？😵‍💫💥

例えば注文作成で…

* `null/空文字` チェックが増える
* 桁数、メール形式、範囲、配列の要素数…増える
* 「クーポン期限」「在庫」「購入制限」みたいな業務ルールも増える
* 結果、**OrderService が “検証 + 業務 + DB + 外部API” の全部入り**になって読むのが地獄👹

SRP的にいうと、**変更理由が多すぎる**のがアウトだよ〜🧹✨

---

## 3. SRPで考える「検証の置き場所」マップ🗺️✅

![バリデーションのゾーン分け](./picture/solid_cs_study_010_validation_zones.png)

検証はだいたい **3つのゾーン**に分けると整理しやすいよ💡

### A) 入口（Boundary）検証：受け取った瞬間に落とすやつ🚪🧯

* 例：必須、形式、長さ、数値範囲、JSONの形が壊れてる…など
* 目的：**“変なデータ”を中に入れない**
* 実装例：MVCならモデル検証、Minimal APIならフィルターで検証など🧩([Microsoft Learn][2])

### B) ドメイン検証（不変条件）：ドメインが絶対守るルール🏰🔒

* 例：「注文は明細が1件以上」「数量は1以上」「金額は0より大きい」
* 目的：**“正しいドメインしか存在できない”**
* 実装場所：Entity / ValueObject / Factory（生成時に保証）

### C) ユースケース検証（業務ルール）：DBや外部を見ないと判断できない🧠📦

* 例：「在庫が足りる？」「購入上限超えてない？」「クーポン有効？」
* 目的：**その操作（ユースケース）として成立するか**
* 実装場所：Application Service / UseCase（Repository/外部サービスと協力）

---

## 4. 悪い例：サービスに検証がベタ書き😇🧱

こんな感じ、見覚えあるはず…！💦

```csharp
public class OrderService
{
    public async Task PlaceOrderAsync(PlaceOrderRequest req)
    {
        // 入口検証（形式）
        if (string.IsNullOrWhiteSpace(req.CustomerEmail))
            throw new ArgumentException("Email is required.");

        if (!req.CustomerEmail.Contains("@"))
            throw new ArgumentException("Email format is invalid.");

        if (req.Items == null || req.Items.Count == 0)
            throw new ArgumentException("Items are required.");

        foreach (var i in req.Items)
        {
            if (i.Quantity <= 0)
                throw new ArgumentException("Quantity must be >= 1.");
        }

        // 業務ルール（DB必要）
        var stockOk = await CheckStockAsync(req.Items);
        if (!stockOk) throw new InvalidOperationException("Out of stock.");

        // 本来の処理
        await SaveAsync(req);
        await SendMailAsync(req.CustomerEmail);
    }
}
```

このクラス、変更理由が多すぎるよね🥺

* 入力形式が変わるたび修正
* ドメインルール追加で修正
* 在庫ルール追加で修正
* メール仕様で修正
  → **“何か変わるたびにここを触る”**＝怖いコード完成😱

---

## 5. 改善の方針：検証を「責務」で分ける✂️✨

合言葉はこれっ👇💕

> **“検証の変更理由は、検証ルールが変わることだけ”**
> だから **Validator を別クラスにして隔離**しよう🧊✨

---

## 6. ステップ①：入口検証を Validator に逃がす✅📥

### 6.1 まずは DataAnnotations で「形」を守る🧷✨

ASP.NET Core では DataAnnotations によるモデル検証が基本として案内されてるよ📚([Microsoft Learn][2])

```csharp
using System.ComponentModel.DataAnnotations;

public sealed class PlaceOrderRequest
{
    [Required, EmailAddress]
    public string CustomerEmail { get; init; } = "";

    [MinLength(1)]
    public List<OrderItemRequest> Items { get; init; } = new();
}

public sealed class OrderItemRequest
{
    [Required]
    public string Sku { get; init; } = "";

    [Range(1, 999)]
    public int Quantity { get; init; }
}
```

これだけでも「空」「範囲」「形式」みたいな **入口の雑務**がスッと整理できるよ〜😊✨

---

### 6.2 Minimal API なら「Endpoint Filter」で入口検証を一箇所にまとめる🧹🚀

Minimal API は **フィルターでリクエストを検証する**パターンが公式ドキュメントにもあるよ🧩([Microsoft Learn][3])

ここでは DataAnnotations を使って「入口で弾く」フィルターを作るよ✅

```csharp
using System.ComponentModel.DataAnnotations;

public sealed class DataAnnotationsValidationFilter<T> : IEndpointFilter where T : class
{
    public async ValueTask<object?> InvokeAsync(EndpointFilterInvocationContext ctx, EndpointFilterDelegate next)
    {
        // 0番目の引数がリクエスト（MapPostの引数順）
        var model = ctx.GetArgument<T>(0);

        var results = new List<ValidationResult>();
        var isValid = Validator.TryValidateObject(
            model,
            new ValidationContext(model),
            results,
            validateAllProperties: true);

        if (!isValid)
        {
            var errors = results
                .GroupBy(r => r.MemberNames.FirstOrDefault() ?? "")
                .ToDictionary(g => g.Key, g => g.Select(r => r.ErrorMessage ?? "").ToArray());

            return Results.ValidationProblem(errors);
        }

        return await next(ctx);
    }
}
```

そしてエンドポイントに付ける✨

```csharp
app.MapPost("/orders", async (PlaceOrderRequest req, OrderUseCase useCase) =>
{
    var orderId = await useCase.PlaceOrderAsync(req);
    return Results.Created($"/orders/{orderId}", new { orderId });
})
.AddEndpointFilter<DataAnnotationsValidationFilter<PlaceOrderRequest>>();
```

こうすると、入口検証が **全部フィルター側に集まる**ので、UseCase がスッキリするよ〜🥰🧼

---

## 7. ステップ②：ドメイン検証（不変条件）を “生成時” に閉じ込める🏰🔒✨

入口で弾いても、**ドメイン側でも守る**のが大事だよ！（二重？って思うけど、意味が違うの！）

* 入口：ユーザー入力が変でも落とす
* ドメイン：**何が来ても**「不正な注文」は存在できない

### 7.1 超シンプルなドメイン生成（Factory）例🧪

```csharp
public sealed class Order
{
    public string CustomerEmail { get; }
    public IReadOnlyList<OrderItem> Items { get; }

    private Order(string customerEmail, List<OrderItem> items)
    {
        CustomerEmail = customerEmail;
        Items = items;
    }

    public static Order Create(string customerEmail, IEnumerable<OrderItem> items)
    {
        if (string.IsNullOrWhiteSpace(customerEmail))
            throw new DomainException("CustomerEmail is required.");

        var list = items?.ToList() ?? new List<OrderItem>();
        if (list.Count == 0)
            throw new DomainException("Order must have at least 1 item.");

        return new Order(customerEmail, list);
    }
}

public sealed class OrderItem
{
    public string Sku { get; }
    public int Quantity { get; }

    private OrderItem(string sku, int quantity)
    {
        Sku = sku;
        Quantity = quantity;
    }

    public static OrderItem Create(string sku, int quantity)
    {
        if (string.IsNullOrWhiteSpace(sku))
            throw new DomainException("Sku is required.");
        if (quantity <= 0)
            throw new DomainException("Quantity must be >= 1.");

        return new OrderItem(sku, quantity);
    }
}

public sealed class DomainException : Exception
{
    public DomainException(string message) : base(message) { }
}
```

ポイントはここ💡

* `OrderService` にベタ書きしない
* **Order が Order の正しさを守る**（責務が自然）🌿✨

---

## 8. ステップ③：DB/外部が必要な検証は UseCase に置く🧠📦✅

例えば「在庫が足りるか」は **DBを見ないと分からない**よね？
これは入口でもドメインでもなく、**ユースケース（アプリ層）の検証**が担当✨

```csharp
public interface IStockService
{
    Task<bool> HasEnoughStockAsync(string sku, int quantity);
}

public sealed class OrderUseCase
{
    private readonly IStockService _stock;

    public OrderUseCase(IStockService stock)
    {
        _stock = stock;
    }

    public async Task<Guid> PlaceOrderAsync(PlaceOrderRequest req)
    {
        // ドメインに変換（生成時に不変条件を保証）
        var items = req.Items.Select(i => OrderItem.Create(i.Sku, i.Quantity)).ToList();
        var order = Order.Create(req.CustomerEmail, items);

        // ユースケース検証（DB/外部が必要）
        foreach (var item in order.Items)
        {
            if (!await _stock.HasEnoughStockAsync(item.Sku, item.Quantity))
                throw new InvalidOperationException($"Out of stock: {item.Sku}");
        }

        // 本来の処理（保存とか）
        return Guid.NewGuid();
    }
}
```

これで責務が超きれいになるよ〜！😍✨

* 入口＝フィルター
* ドメイン＝生成時
* ユースケース＝外部チェック

---

## 9. テストがめちゃ簡単になる🧪✨（SRPのご褒美）

### 9.1 ドメインのテスト（最小でOK！）

* `Order.Create` が「明細なし」を弾く
* `OrderItem.Create` が「quantity<=0」を弾く

こういうテストは **DBなし・爆速**で回せるよ🚀💕

---

## 10. よくあるミス集⚠️😂

### ミス1：入口検証を飛ばしてドメインだけに全部書く

→ ドメイン例外が API からそのまま出ると、エラーが雑になりがち🥺
入口は入口で “丁寧に” 落とすのが親切💖

### ミス2：ユースケース検証をドメインに入れちゃう

→ 在庫チェックを `Order` に入れると、Order が DB を欲しがり始める😇
それは SRP も DIP も崩れやすい〜💥

### ミス3：共通化しすぎて「Validatorのための設計」になる

→ 最初は **分けるだけで勝ち**🏆✨
抽象化は増えてからでOK（この判断は後の章で磨いていくよ😉）

---

## 11. 🤖AI活用メモ（Copilot/Codex系）✨

そのままコピって使ってOKだよ〜💕

* 「この PlaceOrderRequest に必要なバリデーションを “入口/ドメイン/ユースケース” に分類して、理由付きで箇条書きして」🗂️
* 「DataAnnotations で妥当な属性案を提案して（過剰にならないように）」🧷
* 「Order.Create / OrderItem.Create のテスト観点を5個ずつ出して」🧪
* 「このサービスに混ざってる検証処理を抽出して Validator クラス案を3つ出して」✂️
* 「エラーメッセージをユーザー向けに優しく整えて」💬🌸

Visual Studio 側の Copilot 連携もどんどん強化されてるので、こういう“整理タスク”はAIが得意だよ🤖✨([Microsoft for Developers][4])

---

## 12. 章末ミニ課題🎒✨（手を動かすと最強💪）

### 課題A（分類力）🗂️

次のルールを、A/B/C（入口/ドメイン/ユースケース）に分類してみてね👇

1. Email必須
2. Email形式
3. 注文明細は1件以上
4. 数量は1以上
5. 在庫が足りる
6. クーポンが期限内
7. SKUが存在する（DBにある）
8. 合計金額が0より大きい
9. 同一ユーザーの1日購入上限
10. 支払い方法が利用可能（外部決済の状態）

### 課題B（実装）🧩

* `PlaceOrderRequest` に DataAnnotations を付ける
* Filter を付けて、変な入力が来たら 400 で返す✅
* ドメイン生成で不変条件を保証する🏰

---

## 13. まとめ🌈✨

* 検証は **入口 / ドメイン / ユースケース** に分けると迷子にならない🗺️
* “検証が増えるほどサービスが太る” のは SRP違反のサイン😇
* Validator（入口）＋ Factory（ドメイン）＋ UseCase（外部チェック）でスッキリ🧼✨

---

次の **第11章**では、いよいよ「肥大化サービスをSRPで分割して“読める塊”にする」実戦に入るよ〜！🧱➡️✨

[1]: https://dotnet.microsoft.com/en-us/platform/support/policy/dotnet-core?utm_source=chatgpt.com "NET and .NET Core official support policy"
[2]: https://learn.microsoft.com/en-us/aspnet/core/mvc/models/validation?view=aspnetcore-10.0&utm_source=chatgpt.com "Model validation in ASP.NET Core MVC and Razor Pages"
[3]: https://learn.microsoft.com/en-us/aspnet/core/fundamentals/minimal-apis/min-api-filters?view=aspnetcore-10.0 "Filters in Minimal API apps | Microsoft Learn"
[4]: https://devblogs.microsoft.com/dotnet/dotnet-conf-2025-recap/?utm_source=chatgpt.com "Celebrating .NET 10, Visual Studio 2026, AI, Community, & ..."
