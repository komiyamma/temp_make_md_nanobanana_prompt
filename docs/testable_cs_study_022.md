# 第22章：どこに“組み立て”を書く？（Composition Root入門）🏗️✨

この章のテーマはひとことで言うと👇
**「new（本物の部品づくり）を“1か所”に集めて、テストしやすさを守ろう」**です📍🧩

---

## 0. いまの“最新”前提をサクッと共有🆕✨

2026/01/16 時点だと、.NET は **.NET 10** が最新の LTS で、**10.0.2（2026/01/13）**が最新更新です📦⚡ ([Microsoft][1])
また .NET 10 世代では **C# 14** の機能も扱えます🧠✨ ([Microsoft Learn][2])

---

## 1. Composition Root ってなに？🏗️🔌


![testable_cs_study_022_composition_root.png](./picture/testable_cs_study_022_composition_root.png)

**Composition Root（コンポジションルート）**は、ざっくり言うと👇

* アプリの部品たち（クラス）を
  **「どれとどれを繋ぐか」決めて**🔌
  **「本物を組み立てる」場所**🏗️
* ここ以外では、基本 **“重要ロジックの中で new しない”**（第10〜11章の続き！）🚫🧊
* つまり **「本番の配線室」**みたいなところです🧰✨

.NET（特に ASP.NET Core）だと、だいたい **Program.cs が Composition Root** になりがちです📍 ([Microsoft Learn][3])

---

## 2. なんで “1か所” がそんなに大事？😵‍💫➡️😊

## ✅ new が散らばると起きること💥

* テストで差し替えたいのに、あちこちで `new` されてて差し替え不能😱
* 「本番の DB」「本番の API」へうっかりアクセスしちゃう🫠🌪️
* 変更が怖い（どこに影響出るか分からない）😢

## ✅ new が “1か所” だと嬉しいこと🎉

* テストは **Fake/Stub** に差し替えるだけでOK🎭✨
* 本番は **本物**をつなぐだけでOK🔌🚀
* 「ロジック」と「配線」が混ざらなくなる🧼🌿

---

## 3. “どこ”に置くの？（アプリ種類別）🗺️✨

よくある置き場所はこんな感じ👇

## 🌐 Web（ASP.NET Core）

* **Program.cs**（いまの主流）📍✨ ([Microsoft Learn][3])
* `builder.Services.Add...` が “配線” の中心です🔌

## 🖥️ Console アプリ

* **Program.cs** がそのまま Composition Root📍
* 小さければ “手配線（手で new）” でもOK🙆‍♀️
* ちょっと大きくなるなら DI コンテナも便利🧰

## 🪟 WPF / WinForms

* 起動点（WPF: App 起動、WinForms: Program.cs）あたりに集約しがち🏁
* “UI は薄く”で、配線は起動側へ寄せるのが気持ちいいです🧁✨

---

## 4. まずはイメージ：内側と外側と“配線室”📦🌍🏗️

* **内側（ルール / ユースケース）**：純粋に近い、判断の中心🧠🌿
* **外側（I/O実装）**：DB / ファイル / HTTP / 時刻など🌐🗄️🗂️🕰️
* **配線室（Composition Root）**：
  「内側の入口」に「外側の本物」を接続する🔌🏗️

> ポイント：**内側は“インターフェース”だけ知ってる**🧩
> 本物実装は、配線室が連れてくる🚚✨

---

## 5. 実例で掴む：レシート出力つき会計（超ミニ）🧾✨

ここでは例として👇

* ルール：合計金額を計算する🧠
* I/O：レシートをファイルに出す🗂️
* ついでに「時刻」も使う🕰️（第14章の復習）

## 5-1) インターフェース（境界）🧩🚧

```csharp
public interface IClock
{
    DateTimeOffset Now { get; }
}

public interface IReceiptWriter
{
    Task WriteAsync(string text);
}
```

## 5-2) 内側（ユースケース）📦✨

```csharp
public sealed class CheckoutUseCase
{
    private readonly IClock _clock;
    private readonly IReceiptWriter _receiptWriter;

    public CheckoutUseCase(IClock clock, IReceiptWriter receiptWriter)
    {
        _clock = clock;
        _receiptWriter = receiptWriter;
    }

    public async Task RunAsync(decimal total)
    {
        // ルール（内側）
        if (total < 0) throw new ArgumentOutOfRangeException(nameof(total));

        var text =
            $"購入日時: {_clock.Now:yyyy-MM-dd HH:mm}\n" +
            $"合計: {total:N0} 円\n" +
            "ありがとうございました！\n";

        // I/O（外側）はインターフェース越し
        await _receiptWriter.WriteAsync(text);
    }
}
```

---

## 6. ここが本題：Composition Root を書く🏗️✨

## パターンA：小さければ “手で new” でもOK🙆‍♀️（超わかりやすい）

```csharp
// Program.cs（Composition Root）
var clock = new SystemClock();
var receiptWriter = new FileReceiptWriter("receipt.txt");

var useCase = new CheckoutUseCase(clock, receiptWriter);

await useCase.RunAsync(total: 1200m);
```

**手配線のメリット**：読みやすい👀✨
**デメリット**：大きくなると配線が増えてしんどい😵‍💫

---

## パターンB：DI コンテナで配線（少し大きくなったら便利）🧰🔌

.NET の DI は “サービス登録” と “ライフタイム（寿命）” が大事です🧠✨ ([Microsoft Learn][4])

```csharp
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;

var builder = Host.CreateApplicationBuilder(args);

// ここが “配線” 🔌（Composition Root）
builder.Services.AddSingleton<IClock, SystemClock>();
builder.Services.AddSingleton<IReceiptWriter>(_ => new FileReceiptWriter("receipt.txt"));
builder.Services.AddTransient<CheckoutUseCase>();

await using var host = builder.Build();

// Console でも “スコープ” を切る癖があると安心🧁
using var scope = host.Services.CreateScope();
var useCase = scope.ServiceProvider.GetRequiredService<CheckoutUseCase>();

await useCase.RunAsync(total: 1200m);
```

### ライフタイムの超ざっくりイメージ🧁

* **Singleton**：1個を使い回す（重いもの・共有したいもの向き）♻️
* **Transient**：毎回 new（軽いユースケースとかに便利）✨
* **Scoped**：リクエスト単位（Webでよく使う）🌐

「間違った寿命」で事故りがちなので、Microsoft のガイドラインも意識すると安全です🛡️✨ ([Microsoft Learn][5])

---

## 7. “良い Composition Root” の書き方のコツ🪄✨

## ✅ コツ1：Program.cs を“太らせない”🍔🚫

「登録行」が増えると読みにくいので、拡張メソッドで分けるのが定番です📦✨

```csharp
// Program.cs
builder.Services.AddUseCases();
builder.Services.AddInfrastructure();
```

```csharp
public static class ServiceCollectionExtensions
{
    public static IServiceCollection AddUseCases(this IServiceCollection services)
    {
        services.AddTransient<CheckoutUseCase>();
        return services;
    }

    public static IServiceCollection AddInfrastructure(this IServiceCollection services)
    {
        services.AddSingleton<IClock, SystemClock>();
        services.AddSingleton<IReceiptWriter>(_ => new FileReceiptWriter("receipt.txt"));
        return services;
    }
}
```

👉 こうすると「内側」と「外側」の接続が見やすいです👀🔌✨

---

## ✅ コツ2：Service Locator（必要な時に取りに行く）を避ける🙅‍♀️🕳️

* `IServiceProvider` をロジックに注入して、途中で `GetService()` しまくるのは事故の元😵‍💫
* **依存はコンストラクタで受け取る**（第11章の正攻法）✉️✨

---

## ✅ コツ3：本物の I/O は “外側” に閉じ込める🗂️🗄️🌐

* `FileReceiptWriter` や `SqlRepository` や `ExternalApiClient` みたいな子たちは
  **インフラ層**に置いて、Composition Root でだけ登場させるのが綺麗です🧼✨

---

## 8. テスト側の “別の組み立て” 🧪🎭

Composition Root を分けると、テストはこうなります👇

## ✅ 単体テスト：DI を使わず “直 new” が一番わかりやすいこと多い🙆‍♀️

```csharp
public sealed class FixedClock : IClock
{
    public FixedClock(DateTimeOffset now) => Now = now;
    public DateTimeOffset Now { get; }
}

public sealed class SpyReceiptWriter : IReceiptWriter
{
    public string? LastText { get; private set; }
    public Task WriteAsync(string text)
    {
        LastText = text;
        return Task.CompletedTask;
    }
}

// テスト
var clock = new FixedClock(new DateTimeOffset(2026, 1, 16, 12, 0, 0, TimeSpan.FromHours(9)));
var spy = new SpyReceiptWriter();

var sut = new CheckoutUseCase(clock, spy);
await sut.RunAsync(1200m);

// spy.LastText を検証できる🎉
```

## ✅ 結合テスト：DI で “テスト用の配線” を作るのもアリ🧰

（本物DBじゃなくインメモリ実装に差し替え、など）

---

## 9. AI（Copilot/Codex）をここで使うと強い🤖💡✨

Composition Root は “定型作業” が多いので AI と相性◎です🎯

## 使えるお願い例📝

* 「このインターフェース群に対して、DI 登録（AddSingleton/Scoped/Transient）の案を出して」🤖
* 「Program.cs が太いので、AddInfrastructure / AddUseCases に分割して」🧩
* 「ライフタイムの危険（Singleton が Scoped を掴む等）がないか確認して」⚠️

※ ただし、AI は “それっぽい” けど寿命や責務がズレることがあるので、最後は自分の目でチェック👀✨（DI ガイドラインも味方！） ([Microsoft Learn][5])

---

## 10. よくある落とし穴あるある⚠️😵‍💫

* **ロジック層に new が復活**（いつの間にか…）🧟‍♂️
* **登録しすぎて何が何だか**（抽象化しすぎ）🌀
* **Singleton にしがち**（とりあえず…は危険）💣
* **Dispose を手でやっちゃう**（コンテナ管理に任せる方針が基本）🧯 ([Microsoft Learn][4])
* （Webなら）**Keyed services** など便利機能の乱用で読みづらくなることもあるので、必要な場面だけにすると綺麗です🗝️✨ ([Microsoft Learn][3])

---

## 11. 章末ミニ課題🎒✨

## 課題A：new を探して “配線室へ移動”🔎➡️🏗️

1. 「重要ロジックっぽい場所」で `new` を検索🔍
2. `IClock` / `IFileStore` / `IRepository` のインターフェースに寄せる🧩
3. 本物実装の `new` は Program.cs（Composition Root）へ📍✨

## 課題B：テスト用 Composition Root を作る🎭🧪

* 本番：`SystemClock` / `FileReceiptWriter`
* テスト：`FixedClock` / `SpyReceiptWriter`
  この差し替えを “気持ちよく” できたら勝ちです🏆✨

---

## まとめ🧡✨

* Composition Root は **「本物をつなぐ配線室」**🏗️🔌
* **new を 1か所に寄せる**と、テストがラクで変更が怖くなくなる🎉
* Program.cs を太らせず、`AddUseCases()` / `AddInfrastructure()` みたいに分割すると見通し◎👀✨
* テストは “別の組み立て” を用意して差し替える🎭🧪

次章（第23章）では、いよいよ小さなアプリで **「入力→処理→出力」**を分離して、最後に Composition Root で本物I/Oを接続して動かします🚀🎮✨

[1]: https://dotnet.microsoft.com/en-US/download/dotnet/10.0?utm_source=chatgpt.com "Download .NET 10.0 (Linux, macOS, and Windows) | .NET"
[2]: https://learn.microsoft.com/ja-jp/dotnet/core/whats-new/dotnet-10/overview?utm_source=chatgpt.com "NET 10 の新機能"
[3]: https://learn.microsoft.com/en-us/aspnet/core/fundamentals/dependency-injection?view=aspnetcore-10.0&utm_source=chatgpt.com "Dependency injection in ASP.NET Core"
[4]: https://learn.microsoft.com/en-us/dotnet/core/extensions/dependency-injection?utm_source=chatgpt.com "Dependency injection - .NET"
[5]: https://learn.microsoft.com/en-us/dotnet/core/extensions/dependency-injection-guidelines?utm_source=chatgpt.com "Dependency injection guidelines - .NET"
