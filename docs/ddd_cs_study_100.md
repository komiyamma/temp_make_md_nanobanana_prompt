# 第100章：総括 🎉 今日からできる「1つだけの小さな設計」✨

![小さな設計](./picture/ddd_cs_study_100_small_design.png)

ここまで来たあなたはもう、「コードを書く人」から「迷わず作れる人」への入口に立ってます🚪🌸
この最終章は、“DDDを完璧にやる”じゃなくて、**今日から一生使える「最小の設計ループ」**を身体に入れる回だよ💪💕

---

## この章のゴール 🎯

![Design Loop](./picture/ddd_cs_study_100_design_loop.png)

**たった1つの機能**を題材にして、次の流れを1周できるようになること！

1. ユースケースを1行にする📝
2. ルールを3行にする📌
3. 値オブジェクトを1個作る💎
4. 集約を1個作る👑
5. テストを1本書く🧪
6. 外側（API）を1個だけ繋ぐ🌐
7. AIにレビューさせて「迷い」を削る🤖✨

これができると、**AIにコードを作らせても“壊れない軸”**が残ります👍

---

## 今日やる題材：ポイント利用（最小DDDサンプル）🎫✨

「会員がポイントを使う」って地味だけど、**ルールがある**からDDDの練習にちょうどいいの🎮

### ユースケース（1行）📝

「会員は、持ってるポイント以内でポイントを使える」

### ルール（3行）📌

![Point Rules](./picture/ddd_cs_study_100_point_rules.png)

* 使うポイントは **1以上**
* 残高が足りないと **失敗**
* 成功したら「ポイントが使われた」イベントが起きたことにする📣

この3行が“設計の芯”だよ🧠✨

---

## 最小プロジェクト構成（これだけでOK）📦

![Minimal Structure](./picture/ddd_cs_study_100_minimal_structure.png)

* **Domain**：ルールの中心（値オブジェクト・集約・イベント）
* **Application**：ユースケース実行（コマンド）
* **Infrastructure**：保存（今回はメモリでOK）
* **Web**：API（最小）

「大きく作る」より、「**分ける練習**」が目的ね😊

---

## 1) Domain：値オブジェクト（Points / MemberId）💎

![Value Object Gem](./picture/ddd_cs_study_100_value_object_gem.png)

> ここが最重要💖
> `int` や `Guid` をそのまま撒かないで、「意味のある型」にするだけで迷いが激減するよ✨

```csharp
// Domain/Shared/Result.cs
namespace PointSample.Domain.Shared;

public sealed record Error(string Message);

public sealed class Result
{
    public bool IsSuccess { get; }
    public Error? Error { get; }

    protected Result(bool isSuccess, Error? error)
        => (IsSuccess, Error) = (isSuccess, error);

    public static Result Ok() => new(true, null);
    public static Result Fail(string message) => new(false, new Error(message));
}

public sealed class Result<T> : Result
{
    public T? Value { get; }

    private Result(bool isSuccess, T? value, Error? error) : base(isSuccess, error)
        => Value = value;

    public static Result<T> Ok(T value) => new(true, value, null);
    public static new Result<T> Fail(string message) => new(false, default, new Error(message));
}
```

```csharp
// Domain/Members/MemberId.cs
namespace PointSample.Domain.Members;

public readonly record struct MemberId(Guid Value)
{
    public static MemberId New() => new(Guid.NewGuid());
    public override string ToString() => Value.ToString();
}
```

```csharp
// Domain/Points/Points.cs
using PointSample.Domain.Shared;

namespace PointSample.Domain.Points;

public readonly record struct Points
{
    public int Value { get; }

    private Points(int value) => Value = value;

    public static Result<Points> Create(int value)
        => value < 0
            ? Result<Points>.Fail("ポイントは0以上にしてね🥺")
            : Result<Points>.Ok(new Points(value));

    public static Result<Points> Positive(int value)
        => value <= 0
            ? Result<Points>.Fail("ポイントは1以上にしてね🥺")
            : Result<Points>.Ok(new Points(value));

    public static Points Zero => new(0);

    public static Points operator +(Points a, Points b) => new(a.Value + b.Value);

    public static Result<Points> Subtract(Points a, Points b)
        => (a.Value - b.Value) < 0
            ? Result<Points>.Fail("残高不足だよ🥺")
            : Result<Points>.Ok(new Points(a.Value - b.Value));
}
```

---

## 2) Domain：集約（PointAccount）👑

![Aggregate Guard](./picture/ddd_cs_study_100_aggregate_guard.png)

「ポイント口座」は関連ルールをまとめる“チーム”だよ🏀✨
**外から残高を直接いじらせない**のがコツ！

```csharp
// Domain/Points/Events/PointsUsed.cs
using PointSample.Domain.Members;

namespace PointSample.Domain.Points.Events;

public interface IDomainEvent;

public sealed record PointsUsed(MemberId MemberId, int Amount, DateTimeOffset OccurredAt) : IDomainEvent;
```

```csharp
// Domain/Points/PointAccount.cs
using PointSample.Domain.Members;
using PointSample.Domain.Points.Events;
using PointSample.Domain.Shared;

namespace PointSample.Domain.Points;

public sealed class PointAccount
{
    private readonly List<IDomainEvent> _events = new();

    public MemberId MemberId { get; }
    public Points Balance { get; private set; }

    public IReadOnlyList<IDomainEvent> Events => _events;

    private PointAccount(MemberId memberId, Points balance)
        => (MemberId, Balance) = (memberId, balance);

    public static PointAccount Create(MemberId memberId)
        => new(memberId, Points.Zero);

    public void Earn(Points points)
        => Balance = Balance + points;

    public Result Use(Points points)
    {
        // ルール：引けないなら失敗
        var next = Points.Subtract(Balance, points);
        if (!next.IsSuccess) return Result.Fail(next.Error!.Message);

        Balance = next.Value!.Value; // Points
        _events.Add(new PointsUsed(MemberId, points.Value, DateTimeOffset.UtcNow));
        return Result.Ok();
    }

    public void ClearEvents() => _events.Clear();
}
```

---

## 3) Application：ユースケース（UsePoints）🎯

“アプリケーション層”は **手順係**。
ドメインに「使うルール」を押し付けないで、**呼び出すだけ**にするのが気持ちいい✨

```csharp
// Application/UsePoints/UsePointsCommand.cs
namespace PointSample.Application.UsePoints;

public sealed record UsePointsCommand(Guid MemberId, int Amount);
```

```csharp
// Application/UsePoints/UsePointsHandler.cs
using PointSample.Domain.Members;
using PointSample.Domain.Points;
using PointSample.Domain.Points.Events;
using PointSample.Domain.Shared;

namespace PointSample.Application.UsePoints;

public interface IPointAccountRepository
{
    Task<PointAccount?> Find(MemberId memberId, CancellationToken ct);
    Task Save(PointAccount account, CancellationToken ct);
}

public interface IDomainEventPublisher
{
    Task Publish(IEnumerable<IDomainEvent> events, CancellationToken ct);
}

public sealed class UsePointsHandler
{
    private readonly IPointAccountRepository _repo;
    private readonly IDomainEventPublisher _publisher;

    public UsePointsHandler(IPointAccountRepository repo, IDomainEventPublisher publisher)
        => (_repo, _publisher) = (repo, publisher);

    public async Task<Result> Handle(UsePointsCommand cmd, CancellationToken ct)
    {
        var memberId = new MemberId(cmd.MemberId);

        var account = await _repo.Find(memberId, ct);
        if (account is null) return Result.Fail("会員が見つからないよ🥺");

        var amount = Points.Positive(cmd.Amount);
        if (!amount.IsSuccess) return Result.Fail(amount.Error!.Message);

        var used = account.Use(amount.Value!.Value);
        if (!used.IsSuccess) return used;

        await _repo.Save(account, ct);
        await _publisher.Publish(account.Events, ct);
        account.ClearEvents();

        return Result.Ok();
    }
}
```

---

## 4) Infrastructure：まずはメモリ保存でOK 🧊

DBはあとでいいよ〜！今日は設計の芯が目的だからね😊

```csharp
// Infrastructure/InMemoryPointAccountRepository.cs
using System.Collections.Concurrent;
using PointSample.Application.UsePoints;
using PointSample.Domain.Members;
using PointSample.Domain.Points;

namespace PointSample.Infrastructure;

public sealed class InMemoryPointAccountRepository : IPointAccountRepository
{
    private readonly ConcurrentDictionary<Guid, PointAccount> _store = new();

    public Task<PointAccount?> Find(MemberId memberId, CancellationToken ct)
        => Task.FromResult(_store.TryGetValue(memberId.Value, out var a) ? a : null);

    public Task Save(PointAccount account, CancellationToken ct)
    {
        _store[account.MemberId.Value] = account;
        return Task.CompletedTask;
    }

    // デモ用：口座を事前に作る
    public PointAccount Seed(MemberId memberId, int balance)
    {
        var acc = PointAccount.Create(memberId);
        var p = Points.Create(balance).Value!.Value;
        acc.Earn(p);
        _store[memberId.Value] = acc;
        return acc;
    }
}

public sealed class NoopDomainEventPublisher : IDomainEventPublisher
{
    public Task Publish(IEnumerable<PointSample.Domain.Points.Events.IDomainEvent> events, CancellationToken ct)
        => Task.CompletedTask;
}
```

---

## 5) Web：APIを1個だけ繋ぐ 🌐✨

「外側」は薄く！薄く！が正義🪽

```csharp
// Web/Program.cs
using PointSample.Application.UsePoints;
using PointSample.Infrastructure;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddSingleton<InMemoryPointAccountRepository>();
builder.Services.AddSingleton<IPointAccountRepository>(sp => sp.GetRequiredService<InMemoryPointAccountRepository>());
builder.Services.AddSingleton<IDomainEventPublisher, NoopDomainEventPublisher>();
builder.Services.AddScoped<UsePointsHandler>();

var app = builder.Build();

// デモ用：起動時に会員を1人作る（ログにID出す）
app.Lifetime.ApplicationStarted.Register(() =>
{
    var repo = app.Services.GetRequiredService<InMemoryPointAccountRepository>();
    var memberId = PointSample.Domain.Members.MemberId.New();
    repo.Seed(memberId, balance: 100);

    app.Logger.LogInformation("Demo MemberId: {MemberId}", memberId.Value);
});

app.MapPost("/members/{memberId:guid}/points/use",
    async (Guid memberId, UsePointsRequest body, UsePointsHandler handler, CancellationToken ct) =>
    {
        var result = await handler.Handle(new UsePointsCommand(memberId, body.Amount), ct);
        return result.IsSuccess
            ? Results.Ok(new { message = "OK✨ ポイント使えたよ！" })
            : Results.BadRequest(new { message = result.Error!.Message });
    });

app.Run();

public sealed record UsePointsRequest(int Amount);
```

---

## 6) テストを1本だけ書く 🧪💖（これが“迷わない保険”）

![Test Insurance](./picture/ddd_cs_study_100_test_insurance.png)

「残高不足なら失敗」だけでもOK！

```csharp
// Tests/PointAccountTests.cs
using PointSample.Domain.Members;
using PointSample.Domain.Points;
using Xunit;

public class PointAccountTests
{
    [Fact]
    public void Use_should_fail_when_insufficient_balance()
    {
        var memberId = MemberId.New();
        var acc = PointAccount.Create(memberId);

        acc.Earn(Points.Create(10).Value!.Value);

        var result = acc.Use(Points.Positive(20).Value!.Value);

        Assert.False(result.IsSuccess);
    }
}
```

---

## 7) AIを「設計の壁打ち」にするテンプレ 🧠🤖✨

![AI Sparring](./picture/ddd_cs_study_100_ai_sparring.png)

AIは“速い”けど、“境界線”は人間が握るのがコツ💡
Copilotは、開いてるファイルや選択範囲などをコンテキストにして提案してくれるから、**関係ファイルを開いてから聞く**のが効くよ📂✨ ([GitHub][1])
Visual StudioでもCopilot Chatは統合されてて、提案を差分表示で取り込める流れが用意されてるよ🪄 ([Microsoft Learn][2])

### プロンプト例①：ルールが型に閉じてるかチェック✅

* 「あなたはDDDの厳しめレビュアーです。`PointAccount` の不変条件（ルール）が破られる経路がないか、抜け道を探して指摘して。修正案もください。」

### プロンプト例②：境界線チェック🧱

* 「Domain層に“外部都合（DB/HTTP/JSON）”が混ざってないか確認して。混ざってたらどこに逃がすべき？」

### プロンプト例③：テスト追加🧪

* 「このドメインで追加すべきテストケースを3つ挙げて、xUnitで書いて」

> ちなみにCopilotには「提案が公開コードに一致する可能性」を通知する仕組みも入ってるので、取り込み判断がしやすいよ🔎 ([Microsoft Learn][2])

---

## 🍬 ちょい最新の“嬉しいやつ”メモ（C# 14）

C# 14は .NET 10 と一緒に来てて、`extension` ブロック（拡張メンバー）や `field` キーワードなどが入ってるよ✨ ([Microsoft for Developers][3])
ただ！今日は無理に使わなくてOK🙆‍♀️ 「設計の芯」＝ルールを型に閉じ込める、の方が100倍大事💖

---

## ありがち事故 🧯🥺（ここだけ避ければ勝ち！）

* ❌ いきなり“完璧なアーキテクチャ”を作ろうとする
  → ✅ **機能1個**で回すのが先！
* ❌ なんでもRepositoryをジェネリック化して抽象化しすぎる
  → ✅ 最初は `IPointAccountRepository` みたいに**用途直球**でOK！
* ❌ ルールがDTOやControllerに散らばる
  → ✅ ルールはDomainへ💎（ここが迷いを消す）

---

## 今日からの「一生モノ習慣」🌱✨（超短いチェックリスト）
 
 迷ったらこの順に戻ってね🔁
 
 ```mermaid
 flowchart LR
     One[1. One Line<br/>UseCase] --> Three[2. Three Lines<br/>Rules]
     Three --> Model[3. Minimal<br/>Model]
     Model --> Test[4. Test<br/>First]
     Test --> API[5. Thin<br/>API]
     API --> Review[6. AI<br/>Review]
     Review --> One
     
     style One fill:#ffdfba,stroke:#f80
     style Test fill:#caffbf,stroke:#383
 ```
 
 1. ユースケース1行📝
 2. ルール3行📌
 3. 名詞2つ（値オブジェクト候補）🧸
 4. 動詞2つ（集約メソッド候補）🏃‍♀️
 5. テスト1本🧪
 6. 外側を薄く繋ぐ🌐
 7. AIレビューで「抜け道」を潰す🤖🔨
 
 ---
 
 ## VS Code派の人へ（おまけ）🎁

もしVS Codeをよく使うなら、Codexをパネルとして使ったり、クラウドに大きめ作業を投げる導線も用意されてるよ🧠✨ ([Visual Studio Marketplace][4])

---

## 最後に：あなたの「最初の一歩」👣💖

今日やるのは、たったこれだけでOK👇

✅ **あなたの作りたいアプリの機能を1個だけ選ぶ**
✅ この章の「1行→3行→VO→集約→テスト→API」をそのまま当てはめる
✅ AIに“抜け道レビュー”させて修正する

これを繰り返すと、設計が「知識」じゃなくて「手癖」になるよ😊✨

---

最近のAI開発環境は、エージェント化・統合がどんどん進んでるから、定期的に追いかけると楽しいよ🚀 ([Visual Studio][5])

* [The Verge](https://www.theverge.com/news/808032/github-ai-agent-hq-coding-openai-anthropic?utm_source=chatgpt.com)
* [TechRadar](https://www.techradar.com/pro/openai-launches-gpt-5-codex-with-a-74-5-percent-success-rate-on-real-world-coding?utm_source=chatgpt.com)
* [The Verge](https://www.theverge.com/news/753984/microsoft-copilot-gpt-5-model-update?utm_source=chatgpt.com)

[1]: https://github.com/features/copilot "GitHub Copilot · Your AI pair programmer · GitHub"
[2]: https://learn.microsoft.com/en-us/visualstudio/ide/visual-studio-github-copilot-chat?view=visualstudio "About GitHub Copilot Chat in Visual Studio - Visual Studio (Windows) | Microsoft Learn"
[3]: https://devblogs.microsoft.com/dotnet/introducing-csharp-14/ "Introducing C# 14 - .NET Blog"
[4]: https://marketplace.visualstudio.com/items?itemName=openai.chatgpt "
        Codex – OpenAI’s coding agent - Visual Studio Marketplace
    "
[5]: https://visualstudio.microsoft.com/insiders/ "
	Visual Studio 2026 Insiders - Faster, smarter IDE"
