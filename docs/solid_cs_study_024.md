# 第24章：.NETのDIで“組み立て場所”を作る🧱🧩

この章はね、ひとことで言うと…
**「new だらけでゴチャつく問題」を、1か所に“まとめてスッキリ”させる章**だよ〜☺️🌸

---

## 1. 今日のゴール🎯✨

章末までに、あなたはこうなれるよ👇😊

* ✅ **依存の登録（AddScopedなど）を、1か所に集約**できる
* ✅ `Program.cs` が肥大化しないように、**登録を “分割して整理”**できる
* ✅ **Singleton / Scoped / Transient の選び方**がふんわりじゃなくなる
* ✅ “やっちゃダメDI” を避けられる（Service Locator、寿命事故など）😇💥

---

## 2. 「組み立て場所」ってなに？🧩🔧

DIの世界では、**アプリの部品を組み立てる場所**が必要になるよね。

* どのインターフェースに、どの実装を使う？
* それって Singleton？Scoped？Transient？
* 設定（Options）やHttpClientもどう渡す？

これらを **あちこちに散らす**と、こうなる👇😵‍💫

* どこで何が登録されてるか分からない
* 追加のたびに `Program.cs` が巨大化
* 寿命（lifetime）事故で、実行時に爆発💥

だからこそ、**登録（＝組み立て）を「ここ！」に寄せる**のがComposition Rootだよ🧱✨
.NETのDIは `IServiceCollection` に登録して、最終的に `IServiceProvider` で解決する仕組みになってるよ。 ([Microsoft Learn][1])

---

## 3. 依存の寿命（Lifetime）を“ざっくり確実に”選ぶ🕒✨

.NETの基本寿命はこの3つ👇（ここ超大事！）
Microsoftの公式ガイドでもこの3寿命と注意点がまとまってるよ。 ([Microsoft Learn][2])

### Transient（毎回新品）🧼

* **軽い処理・状態を持たない**もの向き
* 例：計算、フォーマッタ、マッパー、ドメインサービス（状態なし）

### Scoped（リクエスト単位）🧷

* Webだと基本「**1リクエスト＝1スコープ**」
* 例：DBコンテキスト、UnitOfWork、リポジトリ

### Singleton（アプリ全体で1個）👑

* **重い生成コスト** or **共有したい状態**があるもの向き
* 例：キャッシュ、時計、重い設定読み込みのラッパなど

---

## 4. ありがち寿命事故：「SingletonがScopedを抱える」😇💥（Captive Dependency）

これ、初心者が一番踏む地雷💣

* Singleton はアプリ中ずっと生きる
* Scoped はリクエスト単位で生まれて消える
* なのに Singleton が Scoped をコンストラクタで受け取ると…
  **“1回つかんだScoped”をずっと握り続ける**ことが起きる（危険）😱

.NET公式ガイドも「スコープ検証を有効にして早期に見つけよう」って言ってるよ。 ([Microsoft Learn][2])

---

## 5. 実戦：ミニEC「注文→支払い→発送」をDIで組み立てる🛒💳📦✨

ここから手を動かそ〜！😊🎀
（コードは短め＆理解しやすさ優先だよ）

---

### 5.1 ドメイン側（インターフェース）📦

```csharp
public interface IOrderRepository
{
    Task SaveAsync(Order order, CancellationToken ct);
}

public interface IPaymentGateway
{
    Task<PaymentResult> ChargeAsync(Money amount, CancellationToken ct);
}

public interface IShippingService
{
    Task<ShippingLabel> CreateLabelAsync(Order order, CancellationToken ct);
}

public interface IClock
{
    DateTimeOffset Now { get; }
}
```

---

### 5.2 アプリケーションサービス（上位：業務側）🏰✨

```csharp
public sealed class OrderService
{
    private readonly IOrderRepository _repo;
    private readonly IPaymentGateway _payment;
    private readonly IShippingService _shipping;
    private readonly IClock _clock;
    private readonly ILogger<OrderService> _logger;

    public OrderService(
        IOrderRepository repo,
        IPaymentGateway payment,
        IShippingService shipping,
        IClock clock,
        ILogger<OrderService> logger)
    {
        _repo = repo;
        _payment = payment;
        _shipping = shipping;
        _clock = clock;
        _logger = logger;
    }

    public async Task<Guid> PlaceOrderAsync(Order order, CancellationToken ct)
    {
        _logger.LogInformation("PlaceOrder start at {Time}", _clock.Now);

        var pay = await _payment.ChargeAsync(order.Total, ct);
        if (!pay.IsSuccess) throw new InvalidOperationException("Payment failed 😢");

        var label = await _shipping.CreateLabelAsync(order, ct);

        order.MarkAsPaid(pay.TransactionId);
        order.AttachShippingLabel(label);

        await _repo.SaveAsync(order, ct);
        return order.Id;
    }
}
```

ポイント💡
`OrderService` は **“実装を知らない”** のが最高！DIPの勝ち🏆✨

---

## 6. Composition Root：Program.cs に“組み立て”を置く🧱✨

![Factory assembly line (Composition Root) snapping Service robots together.](./picture/solid_cs_study_024_composition_root_assembly.png)

ASP.NET Core のDIはここが入口になりやすいよ。 ([Microsoft Learn][3])

### 6.1 まずベタ書き版（最初はこれでOK）📝

```csharp
var builder = WebApplication.CreateBuilder(args);

builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

// ✅ 寿命の例
builder.Services.AddScoped<OrderService>();                    // リクエスト単位でOK
builder.Services.AddScoped<IOrderRepository, SqlOrderRepository>(); // DB系はScopedが基本
builder.Services.AddScoped<IShippingService, ShippingService>();

builder.Services.AddSingleton<IClock, SystemClock>();          // 時刻はSingletonでOK（状態なし）

var app = builder.Build();

app.MapPost("/orders", async (PlaceOrderRequest req, OrderService service, CancellationToken ct) =>
{
    var order = Order.From(req);
    var id = await service.PlaceOrderAsync(order, ct);
    return Results.Ok(new { OrderId = id });
});

app.Run();
```

---

## 7. Program.cs が太る問題 → “分割して整理”する✂️✨（ここが本題！）

ベタ書きは分かりやすいけど、育つとこうなる👇😵‍💫

* 登録が100行超える
* どれが業務でどれがDBでどれが外部か混ざる

だから、登録を **用途ごとに分割して**、Composition Rootに“集約”するよ🧱🧩

---

### 7.1 IServiceCollection 拡張メソッドで「登録モジュール化」📦✨

**フォルダ例**（イメージ）

* `Composition/ServiceCollectionExtensions.cs`
* `Application/`
* `Infrastructure/`
* `External/`

#### Application（業務側）登録

```csharp
public static class ApplicationServiceCollectionExtensions
{
    public static IServiceCollection AddApplication(this IServiceCollection services)
    {
        services.AddScoped<OrderService>();
        services.AddSingleton<IClock, SystemClock>();
        return services;
    }
}
```

#### Infrastructure（DBなど）登録

```csharp
public static class InfrastructureServiceCollectionExtensions
{
    public static IServiceCollection AddInfrastructure(this IServiceCollection services, IConfiguration config)
    {
        services.AddScoped<IOrderRepository, SqlOrderRepository>();
        return services;
    }
}
```

#### External（外部API）登録：HttpClientFactoryで安全に✨🌐

HttpClientは「毎回new」は危険（ソケット枯渇の原因になりやすい）ので、Factory推奨だよ。 ([Microsoft Learn][4])
Typed client は実質 Transient で、ハンドラがプールされる仕組みも押さえると安心😊 ([Microsoft Learn][5])

```csharp
public static class ExternalServiceCollectionExtensions
{
    public static IServiceCollection AddExternalServices(this IServiceCollection services, IConfiguration config)
    {
        services.AddHttpClient<IPaymentGateway, PaymentGateway>(client =>
        {
            client.BaseAddress = new Uri(config["Payment:BaseUrl"]!);
            client.Timeout = TimeSpan.FromSeconds(10);
        });

        return services;
    }
}
```

---

### 7.2 Program.cs は“呼ぶだけ”にして美しくする😍✨

```csharp
var builder = WebApplication.CreateBuilder(args);

builder.Services
    .AddApplication()
    .AddInfrastructure(builder.Configuration)
    .AddExternalServices(builder.Configuration);

var app = builder.Build();
app.Run();
```

**これが「組み立て場所」を整えるコツ**だよ〜🧱🧩✨

---

## 8. Options（設定）もDIで受け取れるようにする🎛️✨

「設定値（APIキーとかURLとか）」を直読みすると、テストもしんどい😇
Optionsパターンで **型付き設定**にすると超ラクだよ。 ([Microsoft Learn][6])

```csharp
public sealed class PaymentOptions
{
    public string BaseUrl { get; init; } = "";
    public string ApiKey { get; init; } = "";
}
```

登録側：

```csharp
services
    .AddOptions<PaymentOptions>()
    .BindConfiguration("Payment")
    .ValidateDataAnnotations();
```

---

## 9. DIの“安全装置”🛡️✨（起動時にミスを発見！）

開発環境では、`ValidateOnBuild` / `ValidateScopes` が有効になって早めに落としてくれる挙動が入ってるよ（.NET 9以降の変更点として整理されてる）。 ([Microsoft Learn][7])

つまり…

* ❌ 実行してしばらくしてから爆発
* ✅ 起動時に「その依存つながらないよ！」って怒られる

最高〜☺️💕

---

## 10. 絶対やりたくないDI（アンチパターン）🙅‍♀️💥

### 10.1 Service Locator（業務コードで IServiceProvider を使う）😱

```csharp
// ❌ こういうのは避けたい…
public class OrderService
{
    public OrderService(IServiceProvider sp)
    {
        var repo = sp.GetRequiredService<IOrderRepository>(); // ←隠れ依存😇
    }
}
```

理由：

* 依存がコンストラクタに出てこない
* テストで差し替えしにくい
* “依存が見えない設計”になる

---

## 11. 🤖AI活用メモ（Copilot / Codex系）💡✨

この章でAIに頼ると気持ちいいところ👇😍

* 「このプロジェクトのサービス登録、`AddApplication` / `AddInfrastructure` に分割して提案して」
* 「このクラス群の寿命（Singleton/Scoped/Transient）をおすすめして、理由も書いて」
* 「Program.cs を薄くするための `IServiceCollection` 拡張メソッドを作って」

ただし！
AIがたまに **ScopedをSingletonに混ぜる提案**をすることがあるから、そこだけ人間がチェックね👀💥
（公式ガイドの寿命ルールを基準にすると安定だよ） ([Microsoft Learn][2])

---

## 12. ミニ演習✍️✨（手を動かすと覚える！）

### 演習A：登録を3分割してみよう🧩

* `AddApplication()`
* `AddInfrastructure()`
* `AddExternalServices()`

に分けて、`Program.cs` を10行くらいにしてね😊

### 演習B：寿命を説明してみよう🕒

次を口で説明できたら勝ち🏆✨

* `OrderService` が Scoped な理由
* `IClock` が Singleton でいい理由
* `HttpClientFactory` を使う理由 ([Microsoft Learn][4])

---

## 13. まとめ🌈✨

* Composition Root は **「組み立てはここ！」を決める**考え方🧱🧩
* `Program.cs` に全部書くと育ったとき詰む😇
* `IServiceCollection` 拡張メソッドで **登録を“モジュール化”**するとスッキリ😍
* 寿命（Singleton/Scoped/Transient）は事故ると痛いので、公式ガイド基準で選ぶと安心🛡️ ([Microsoft Learn][2])

---

次の第25章は、このDI構造がいちばん気持ちよく効くところ…
**テストで差し替えて「怖くない変更」を作る🧪🔁✨**に突入だよ〜☺️💕

[1]: https://learn.microsoft.com/en-us/dotnet/core/extensions/dependency-injection?utm_source=chatgpt.com "Dependency injection - .NET"
[2]: https://learn.microsoft.com/en-us/dotnet/core/extensions/dependency-injection-guidelines?utm_source=chatgpt.com "Dependency injection guidelines - .NET"
[3]: https://learn.microsoft.com/en-us/aspnet/core/fundamentals/dependency-injection?view=aspnetcore-10.0&utm_source=chatgpt.com "Dependency injection in ASP.NET Core"
[4]: https://learn.microsoft.com/en-us/dotnet/fundamentals/networking/http/httpclient-guidelines?utm_source=chatgpt.com "HttpClient guidelines for .NET"
[5]: https://learn.microsoft.com/en-us/dotnet/architecture/microservices/implement-resilient-applications/use-httpclientfactory-to-implement-resilient-http-requests?utm_source=chatgpt.com "Use IHttpClientFactory to implement resilient HTTP requests"
[6]: https://learn.microsoft.com/en-us/aspnet/core/fundamentals/configuration/options?view=aspnetcore-10.0&utm_source=chatgpt.com "Options pattern in ASP.NET Core"
[7]: https://learn.microsoft.com/en-us/dotnet/core/compatibility/aspnet-core/9.0/hostbuilder-validation?utm_source=chatgpt.com "HostBuilder enables ValidateOnBuild/ValidateScopes in ..."
