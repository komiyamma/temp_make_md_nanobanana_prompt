# 第57章：オニオンアーキテクチャ 🧅✨

![オニオンアーキテクチャ](./picture/ddd_cs_study_057_onion_layers.png)

〜「ドメインを真ん中」に置くと、変更が怖くなくなる〜

DDDって聞くと「なんか難しそう…😵‍💫」ってなりがちだけど、オニオンアーキテクチャは発想がめちゃシンプルです💡
**“大事なルール（ドメイン）を中心に置いて、外側は付け替え可能にする”** ただそれだけ🧅💕

---

## 1) オニオンアーキテクチャって何？🧅

玉ねぎみたいに **内側ほど大事**、外側ほど **交換しやすい** って考え方だよ〜😊

* 🧠 **中心（いちばん内側）**：ドメイン（ビジネスルール）
* 🧰 **中間**：アプリケーション（ユースケース）
* 🔌 **外側**：DB、外部API、UI（Web/画面）など

ポイントはこれ👇

✅ **内側は外側を“知らない”**
（ドメインが「EF Core」や「ASP.NET」を知ってたら負け🥲）

---

## 2) これ、1人開発×AI時代にめちゃ効く理由🤖✨

### ✅ (1) 変更が来ても、中心が壊れにくい🛡️

DBを SQLite → SQL Server にしても、UIを Web → WPF にしても、
**中心のドメインは守られる** からメンタルが安定する😌💕

### ✅ (2) テストがやりやすい🧪

ドメインが外部に依存しない＝**ユニットテストが超ラク**！
「DB起動しないとテストできない😇」みたいな地獄を避けられるよ〜

### ✅ (3) AIに指示が通りやすくなる📣🤖

AIって「ここはドメイン」「ここはインフラ」って境界があると、
**ブレずに量産してくれる**のよ…！✨

---

## 3) たった1つの最重要ルール：依存は内側へ！➡️🧅

**依存の向きは必ず“内側へ”** です🙆‍♀️

* Domain は何にも依存しない👑
* Application は Domain に依存してOK👍
* Infrastructure は Domain / Application に依存してOK👍
* Web(UI) は Application に依存してOK👍（起動時にDIでつなぐ）

「内側が外側を知らない」を守るだけで、設計がキレイになるよ✨
 
 ```mermaid
 graph TD
     subgraph Outer["外側 (Infrastructure / Web)"]
         Infra["Infrastructure 🔌"]
         Web["Web API 🌐"]
     end
     
     subgraph Middle["中間 (Application)"]
         App["Application Service 🧭"]
     end
     
     subgraph Core["中心 (Domain)"]
         Domain["Domain 👑"]
     end
     
     Web --> App
     Infra --> App
     Infra --> Domain
     App --> Domain
     
     style Domain fill:#ff9,stroke:#333,stroke-width:4px
     %% note for Domain "中心は誰にも依存しない！🙅‍♀️"
 ```
 
 ---

## 4) C#（.NET 10 / C# 14）で作る、最小の玉ねぎ構成🍳

2025の最新ど真ん中は **.NET 10（LTS）** ＆ **C# 14** の組み合わせだよ〜！🌟 ([Microsoft][1])
EF Core も **EF Core 10** が .NET 10 前提で揃ってるよ🧩 ([Microsoft Learn][2])

---

## 5) プロジェクト構成（これがいちばん迷わない🏁）

ソリューション配下を、4つに分けるのが定番です✨

* 📦 `MyApp.Domain`（Class Library）
* 📦 `MyApp.Application`（Class Library）
* 📦 `MyApp.Infrastructure`（Class Library）
* 🌐 `MyApp.Web`（ASP.NET Core Web API）

依存関係はこう👇

* `Application` → `Domain`
* `Infrastructure` → `Application` と `Domain`
* `Web` → `Application`（起動時に `Infrastructure` も参照してDI登録）

---

## 6) ミニ題材：Todoアプリで「玉ねぎ」を体験しよう📝🧅

### 6-1) Domain：ルールを持つ「Todo」👑

ここは「DBの都合」とか一切考えないでOK🙆‍♀️
**“どうあるべきか”** だけを書くよ✨

```csharp
namespace MyApp.Domain.Todos;

public readonly record struct TodoId(Guid Value)
{
    public static TodoId New() => new(Guid.NewGuid());
}

public sealed class TodoItem
{
    public TodoId Id { get; }
    public string Title { get; private set; }
    public bool IsDone { get; private set; }

    public TodoItem(TodoId id, string title)
    {
        if (string.IsNullOrWhiteSpace(title))
            throw new ArgumentException("タイトルは必須だよ🥺", nameof(title));

        Id = id;
        Title = title.Trim();
        IsDone = false;
    }

    public void Rename(string newTitle)
    {
        if (string.IsNullOrWhiteSpace(newTitle))
            throw new ArgumentException("タイトルは必須だよ🥺", nameof(newTitle));

        Title = newTitle.Trim();
    }

    public void MarkDone() => IsDone = true;
}
```

✅ ここでの気持ち：
「Todoはタイトル空じゃダメ！」みたいな **現実のルール** を閉じ込める🏰✨

---

### 6-2) Domain：リポジトリ“インターフェース”だけ置く📮

保存先（DBとか）はまだ考えない！
「こういう保存ができればいいよね」だけ宣言するよ😊

```csharp
namespace MyApp.Domain.Todos;

public interface ITodoRepository
{
    Task<TodoItem?> FindByIdAsync(TodoId id, CancellationToken ct);
    Task AddAsync(TodoItem todo, CancellationToken ct);
    Task SaveAsync(TodoItem todo, CancellationToken ct);
}
```

✅ 大事：**Domainは“保存方法”を知らない**🧅

---

### 6-3) Application：ユースケースを書く🎮✨

Applicationは「ユーザーがやりたいこと」を実現する場所だよ〜！

```csharp
using MyApp.Domain.Todos;

namespace MyApp.Application.Todos;

public sealed class CreateTodoUseCase
{
    private readonly ITodoRepository _repo;

    public CreateTodoUseCase(ITodoRepository repo) => _repo = repo;

    public async Task<TodoId> ExecuteAsync(string title, CancellationToken ct)
    {
        var todo = new TodoItem(TodoId.New(), title);
        await _repo.AddAsync(todo, ct);
        return todo.Id;
    }
}
```

✅ ここは「手順」寄りでOK！
でも **ドメインのルールは必ずドメインに聞く** のがコツだよ🧠✨

---

### 6-4) Infrastructure：EF Coreで“実装”する🛠️🗄️

Infrastructureは「DBに保存する現実」と向き合う場所😇
DomainにEF Coreの属性とか持ち込まないで、ここで吸収するよ！

（※超ミニ例：細かいマッピングは章が進んだら丁寧にやろうね🙏）

```csharp
using Microsoft.EntityFrameworkCore;
using MyApp.Domain.Todos;

namespace MyApp.Infrastructure;

public sealed class AppDbContext : DbContext
{
    public DbSet<TodoRecord> Todos => Set<TodoRecord>();

    public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) { }
}

public sealed class TodoRecord
{
    public Guid Id { get; set; }
    public string Title { get; set; } = "";
    public bool IsDone { get; set; }
}

public sealed class EfTodoRepository : ITodoRepository
{
    private readonly AppDbContext _db;
    public EfTodoRepository(AppDbContext db) => _db = db;

    public async Task<TodoItem?> FindByIdAsync(TodoId id, CancellationToken ct)
    {
        var row = await _db.Todos.FirstOrDefaultAsync(x => x.Id == id.Value, ct);
        return row is null ? null : new TodoItem(new TodoId(row.Id), row.Title) { };
    }

    public async Task AddAsync(TodoItem todo, CancellationToken ct)
    {
        _db.Todos.Add(new TodoRecord
        {
            Id = todo.Id.Value,
            Title = todo.Title,
            IsDone = todo.IsDone
        });
        await _db.SaveChangesAsync(ct);
    }

    public async Task SaveAsync(TodoItem todo, CancellationToken ct)
    {
        var row = await _db.Todos.FirstAsync(x => x.Id == todo.Id.Value, ct);
        row.Title = todo.Title;
        row.IsDone = todo.IsDone;
        await _db.SaveChangesAsync(ct);
    }
}
```

✅ ここでの気持ち：
「DBはDBの都合がある。だから外側（Infrastructure）で受け止める😌」

---

### 6-5) Web：DIで“つなぐ”🔗🌐

Webは **配線係**！🧑‍🔧✨
「どのインターフェースにどの実装を刺すか」を決める場所だよ〜

```csharp
using Microsoft.EntityFrameworkCore;
using MyApp.Application.Todos;
using MyApp.Domain.Todos;
using MyApp.Infrastructure;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddDbContext<AppDbContext>(opt =>
    opt.UseSqlite("Data Source=app.db"));

builder.Services.AddScoped<ITodoRepository, EfTodoRepository>();
builder.Services.AddScoped<CreateTodoUseCase>();

var app = builder.Build();

app.MapPost("/todos", async (string title, CreateTodoUseCase useCase, CancellationToken ct) =>
{
    var id = await useCase.ExecuteAsync(title, ct);
    return Results.Ok(new { id = id.Value });
});

app.Run();
```

---

## 7) よくある事故ポイント（ここ踏むと玉ねぎ腐る🥲🧅）

### ❌ DomainにEF Coreのことを書いちゃう

* `[Key]` とか `[Column]` とか付けたくなる…けど我慢！🥺
  → それは外側の都合だよ〜

### ❌ DomainからInfrastructureを参照しちゃう

* `using MyApp.Infrastructure;` がDomainに出たらアウト🚨

### ❌ 「DTOがドメイン」になっちゃう

* ただのデータ袋だけだと、ルールが行方不明になるよ〜😵‍💫

---

## 8) AI（Copilot/Codex）に境界を守らせるプロンプト例🤖🧠

### ✅ ドメイン生成（ルール中心）

* 「`MyApp.Domain` に、外部依存なしで TodoItem と TodoId を作って。タイトル必須、Rename/Doneの振る舞いも含めて。」

### ✅ “違反チェック”させる（これ超おすすめ！）

* 「このコード、Domain層がEF CoreやASP.NETに依存してない？依存違反があれば指摘して修正案も出して。」

### ✅ 配線（DI）だけ作らせる

* 「Web層でDI登録だけ書いて。DomainやApplicationには触れないで。」

AIに作業を振る時も、**層の名前を毎回言う**のがコツだよ📣✨
（境界が“仕様書”になる感じ！）

---

## 9) ミニ演習 🎓✨（30〜60分でできる！）

### 演習A：玉ねぎ分解チャレンジ🧅🔪

1. 小さいアプリ（自作でもOK）を1つ選ぶ
2. 「ドメインっぽいルール」を3つ書き出す✍️（例：タイトル必須、上限10件など）
3. それを `Domain` に移す（クラスに“振る舞い”を持たせる）
4. DB操作は `Infrastructure` に押し出す
5. `Web` はDIで配線だけにする

### 演習B：AIレビュー🤖📝

* AIに「依存違反がないか」レビューさせて、指摘が減るまで直す✨

---

## まとめ 🧅💕

オニオンアーキテクチャは、要するにこれです👇

* 👑 **ドメインを中心に置く**
* 🔁 **外側（DB/UI）は交換できる**
* ➡️ **依存は内側へだけ向ける**
* 🤖 **AIに境界を教えると、暴走しにくい**

次の章では、この玉ねぎ構造を「クリーンアーキテクチャ」と比べて、
**1人開発ならどこまでやるのがちょうどいいか**を一緒に整理していこうね😊✨

[1]: https://dotnet.microsoft.com/en-US/download/dotnet/10.0?utm_source=chatgpt.com "Download .NET 10.0 (Linux, macOS, and Windows) | .NET"
[2]: https://learn.microsoft.com/en-us/ef/core/what-is-new/ef-core-10.0/whatsnew?utm_source=chatgpt.com "What's New in EF Core 10"
