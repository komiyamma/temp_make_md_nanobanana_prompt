# 第40章：DI（依存の差し込み）で依存向きを守る🪄

この章のゴールはこれだよ〜！🎯💕

* **Dependency Rule（依存は内側へ）**を、**実行時の配線（DI）で守れる**ようになる🧭✨
* **Core（Entities/UseCases）に new を持ち込まず**、外側で組み立てできるようになる🧼🏗️
* **よくあるDI事故（ライフタイム・循環参照・登録漏れ）**を避けられるようになる🧯😵‍💫➡️😌

※2026年1月時点では **.NET 10 / ASP.NET Core 10** の更新が出ているので、コードもその流儀（いまの主流の書き方）でいくね💎✨ ([マイクロソフトサポート][1])

---

## 1) そもそもDIって何がうれしいの？🥰🧩

![DIによる依存注入 (Dependency Injection)](./picture/clean_cs_study_040_di.png)

クリーンアーキで一番大事なのは **「内側が外側を知らない」** だったよね？（Dependency Rule）🧠➡️⭕
でも実際にはアプリを動かすには、**UseCaseがDBや外部APIを呼ぶ必要**がある…🤔💦

そこで登場するのが **DI（Dependency Injection）**！🎉

* **Core側**：`interface`（ポート）だけを知ってる🧼
* **外側**：その `interface` を実装したクラス（アダプター）を作る🔧
* **起動時（最外周）**：DIで「このinterfaceはこの実装を使ってね」って**合体（配線）**する🪄

ASP.NET Coreには **組み込みのDIコンテナ（IServiceProvider）** があって、
サービス登録→コンストラクタへ注入、までを面倒みてくれるよ✨ ([Microsoft Learn][2])

---

## 2) “DIの型” はこれだけ覚えればOK👌💕

DIをクリーンアーキ的に言うと、基本はこの4点セットだよ📦✨

1. **Coreに interface（ポート）を置く**🧼
2. **外側に実装（アダプター）を置く**🔧
3. **起動時に登録（Composition Root）する**🧵（※次章で深掘りするよ！）
4. **使う側はコンストラクタで受け取る**🎁（newしない！）

---

## 3) ハンズオン：Repository差し替えをDIでやってみよ〜！🧪🎮

題材：`IMemoRepository` を **InMemory版** と **DB版** で差し替えできるようにする💡✨
（ポイント：**Core側はどっちでも動く**こと！）

### 3-1) Core（UseCases）に「ポート（interface）」を置く🧼🔌

```csharp
// Core/UseCases/Ports/IMemoRepository.cs
public interface IMemoRepository
{
    Task SaveAsync(Memo memo, CancellationToken ct);
    Task<Memo?> FindByIdAsync(Guid id, CancellationToken ct);
}

// Core/Entities/Memo.cs（超ざっくり）
public sealed class Memo
{
    public Guid Id { get; }
    public string Title { get; private set; }

    public Memo(Guid id, string title)
    {
        if (string.IsNullOrWhiteSpace(title)) throw new ArgumentException("タイトルは必須だよ");
        Id = id;
        Title = title;
    }
}
```

ここが超重要💖：**Coreは「保存できる」ことしか知らない**。
DBとかEF Coreとか、そういう単語すら出てこないのが勝ち🏆✨

---

### 3-2) UseCaseは「interface」をコンストラクタで受け取る🎁✨

```csharp
// Core/UseCases/CreateMemo/CreateMemoInteractor.cs
public sealed class CreateMemoInteractor
{
    private readonly IMemoRepository _repo;

    public CreateMemoInteractor(IMemoRepository repo) // ← DIで入る
    {
        _repo = repo;
    }

    public async Task<Guid> HandleAsync(string title, CancellationToken ct)
    {
        var memo = new Memo(Guid.NewGuid(), title);
        await _repo.SaveAsync(memo, ct);
        return memo.Id;
    }
}
```

**newしてない！**えらい！🥳🎉
これで **依存方向は内向きのまま**で、実行時に差し込めるようになるよ🪄

---

### 3-3) 外側（Adapters/Infrastructure）で実装を書く🔧🗄️

#### InMemory実装（まずはこれでOK！）🧠💾

```csharp
// Adapters/Persistence/InMemoryMemoRepository.cs
public sealed class InMemoryMemoRepository : IMemoRepository
{
    private readonly Dictionary<Guid, Memo> _store = new();

    public Task SaveAsync(Memo memo, CancellationToken ct)
    {
        _store[memo.Id] = memo;
        return Task.CompletedTask;
    }

    public Task<Memo?> FindByIdAsync(Guid id, CancellationToken ct)
    {
        _store.TryGetValue(id, out var memo);
        return Task.FromResult(memo);
    }
}
```

---

### 3-4) 最外周（起動時）でDI登録する🪄🧵

ASP.NET Coreはサービス登録→注入をやってくれるよ✨ ([Microsoft Learn][2])

```csharp
// Web/Program.cs
var builder = WebApplication.CreateBuilder(args);

// UseCase（アプリの手順書）もDIで作る
builder.Services.AddScoped<CreateMemoInteractor>();

// Repositoryは「interface → 実装」を登録する
builder.Services.AddSingleton<IMemoRepository, InMemoryMemoRepository>();

var app = builder.Build();

app.MapPost("/memos", async (string title, CreateMemoInteractor usecase, CancellationToken ct) =>
{
    var id = await usecase.HandleAsync(title, ct);
    return Results.Ok(new { id });
});

app.Run();
```

これで、エンドポイントが `CreateMemoInteractor` を受け取るとき、
DIが勝手に `IMemoRepository` まで芋づる式に解決してくれるよ〜！🍠✨

---

## 4) ライフタイム（Singleton / Scoped / Transient）で事故らないコツ🧯😵‍💫

DIには寿命（ライフタイム）があって、ここでミスると爆発する💥
Microsoftのガイドでも **スコープ検証（ValidateScopes）** や **Singletonの扱い** に注意が書かれてるよ📌 ([Microsoft Learn][3])

ざっくり指針はこれ👇💕

* **Singleton**：アプリ全体で1個。状態持つなら慎重に🧊
* **Scoped**：Webなら「1リクエスト=1スコープ」感覚で使いやすい🧃
* **Transient**：毎回新規。軽いやつ向き🫧

💣ありがち事故：

* **SingletonがScoped（例：DbContext）を抱え込む** → 例外で死ぬ or バグる😇
  → 対策：**スコープ検証をON**（次のコード）＋設計見直し✨ ([Microsoft Learn][3])

```csharp
builder.Host.UseDefaultServiceProvider(options =>
{
    options.ValidateScopes = true;
    options.ValidateOnBuild = true;
});
```

---

## 5) 実装の差し替え：開発はInMemory、本番はDB🪄🏗️

「差し替えたい」のがDIの一番おいしい所だよね🍰💕

```csharp
if (builder.Environment.IsDevelopment())
{
    builder.Services.AddSingleton<IMemoRepository, InMemoryMemoRepository>();
}
else
{
    builder.Services.AddScoped<IMemoRepository, EfMemoRepository>(); // 例：DB版
}
```

✅Coreは一切変更なし！
**外側の配線だけ**変えて挙動が変わるのがクリーンアーキの気持ちよさ🥰✨

---

## 6) “複数実装” を同時に使いたい時：Keyed Services🔑✨

最近のASP.NET Coreでは **Keyed services** が使えるよ！
`AddKeyedSingleton/AddKeyedScoped/AddKeyedTransient` で「キー付き登録」して、
取り出すときは `[FromKeyedServices]` を使うスタイルが公式に説明されてるよ🔑📌 ([Microsoft Learn][4])

例：同じ `IMemoRepository` でも「高速版」「監査ログ版」を使い分けたい…みたいなときに便利💕

```csharp
builder.Services.AddKeyedScoped<IMemoRepository, InMemoryMemoRepository>("fast");
builder.Services.AddKeyedScoped<IMemoRepository, AuditingMemoRepository>("audit");

app.MapGet("/memos/{id:guid}", async (
    Guid id,
    [FromKeyedServices("fast")] IMemoRepository repo,
    CancellationToken ct) =>
{
    var memo = await repo.FindByIdAsync(id, ct);
    return memo is null ? Results.NotFound() : Results.Ok(memo);
});
```

※ただし！クリーンアーキ的には
「**どれを使うかの判断**」は **できるだけ外側（起動時 or adapter）** に寄せるのが安定だよ〜🧠💕

---

## 7) 外部HTTP連携は HttpClientFactory が王道🌍📡✨

外部API呼び出しをDIで扱うなら、**IHttpClientFactory** を使うのが基本だよ☕✨
公式ドキュメントでも、`IHttpClientFactory` の登録と利点がまとまってる🧾 ([Microsoft Learn][5])

（クリーンアーキ的には）

* Core：`IWeatherClient` みたいな **ポート**
* 外側：`WeatherClient`（HttpClient使う実装）
* DI：Typed clientとして登録
  って分けると超きれい🥰

---

## 8) よくあるDIエラーと即死回避💥➡️🧯

### ✅「登録してないよ」系

* 例外：`No service for type ... has been registered`
* 原因：`AddScoped<Interface, Impl>()` を忘れてる😇
* 対策：**起動時登録を1か所に集約**（次章のComposition Root）🧵✨

### ✅ 循環参照（AがB、BがA）

* 原因：設計的に責務が絡まってるサイン🌀
* 対策：**ポートを切る**／依存を片方に寄せる／ユースケース分割🔪✨

### ✅ ライフタイム事故（Singleton ← Scoped）

* 対策：`ValidateScopes` ON ＋ Singletonを減らす（ガイドでも注意あり）📌 ([Microsoft Learn][3])

---

## 9) Copilot / Codexに手伝わせるときのコツ🤖💕

DIは「配線が多くてミスりやすい」から、AIがめっちゃ役立つよ✨
おすすめプロンプト👇

* 「このSolution構成で、**Coreが外側参照しない**DI登録を提案して」🧼➡️🪄
* 「この登録、**ライフタイム不整合**ない？（SingletonがScoped掴んでない？）」🧯
* 「`IMemoRepository` の **InMemory/Ef** を差し替える設計、クリーンアーキ的に変な所ある？」🩺✨

最後に人間が **“依存向き” と “責務”** だけチェックすればOK🙆‍♀️💕

---

## 10) ミニ課題🎮📘✨

### 課題1：差し替え成功チェック✅

* InMemory登録→DB登録に変えても、**Core/UseCasesは一切変更しない**で動かしてみてね🪄

### 課題2：ライフタイム事故をわざと起こす💥（学習用）

* RepositoryをSingletonにして、内部でScopedなものを掴む設定を想像してみて
* 何が危ないか、言葉で説明できたら勝ち🏆✨（スコープ検証の意味が腹落ちするよ） ([Microsoft Learn][3])

### 課題3：Keyed servicesで2実装を並走🔑

* `fast` と `audit` を登録して、エンドポイントで使い分けてみよ〜！ ([Microsoft Learn][4])

---

## 章まとめ📝💖

* DIは **依存方向を守ったまま**、実行時に「外側の実装」を内側へ差し込む魔法🪄✨ ([Microsoft Learn][2])
* Coreは **interfaceだけ**、外側は **実装**、最外周は **登録（配線）**🔌
* ライフタイムと登録漏れが事故ポイント！`ValidateScopes` などのガイドも活用しよ🧯 ([Microsoft Learn][3])
* 最新のASP.NET Coreには **Keyed services** もあるから、複数実装の扱いもやりやすいよ🔑✨ ([Microsoft Learn][4])

次の第41章は、この章で出てきた「登録（配線）」を **散らかさずに1か所へ集約する（Composition Root）** をガッツリやるよ〜🧵💖

[1]: https://support.microsoft.com/en-us/topic/-net-10-0-update-january-13-2026-64f1e2a4-3eb6-499e-b067-e55852885ad5?utm_source=chatgpt.com ".NET 10.0 Update - January 13, 2026"
[2]: https://learn.microsoft.com/ja-jp/aspnet/core/fundamentals/dependency-injection?view=aspnetcore-10.0 "ASP.NET Core での依存関係の挿入 | Microsoft Learn"
[3]: https://learn.microsoft.com/en-us/dotnet/core/extensions/dependency-injection-guidelines "Dependency injection guidelines - .NET | Microsoft Learn"
[4]: https://learn.microsoft.com/en-us/aspnet/core/fundamentals/dependency-injection?view=aspnetcore-10.0 "Dependency injection in ASP.NET Core | Microsoft Learn"
[5]: https://learn.microsoft.com/ja-jp/aspnet/core/fundamentals/http-requests?view=aspnetcore-10.0&utm_source=chatgpt.com "ASP.NET Core で IHttpClientFactory を使用して HTTP 要求 ..."
