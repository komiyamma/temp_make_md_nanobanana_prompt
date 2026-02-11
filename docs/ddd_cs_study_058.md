# 第58章 クリーンアーキテクチャの取捨選択

![クリーンアーキテクチャの取捨選択](./picture/ddd_cs_study_058_clean_select.png)

## 1人ならフォルダとプロジェクトを軽くして迷子を防ぐよ〜🧭✨

「クリーンアーキテクチャ」って聞くと、急にプロジェクトが増えて、フォルダも増えて、ルールも増えて…😵‍💫 ってなりがち。
でもね、**大事な“芯”だけ残して軽量化**すれば、1人開発だとむしろ爆速になります🏎️💨

ちなみに最新のC#は **C# 14**（.NET 10）だよ〜🧡 ([Microsoft Learn][1])

---

## 1 クリーンアーキテクチャの芯はこれだけ🧠✨

![058_dependency_flow](./picture/ddd_cs_study_058_dependency_flow.png)

クリーンアーキテクチャの本質は、超ざっくり言うと👇

* **大事なルール（ドメイン）を中心に置く** 🏰
* **外側（DB・Web・外部API）を付け替え可能にする** 🔌
* **依存の向きは一方通行** ➡️（中心が外側を知らない）

ここだけ守れたら、ぶっちゃけ「完璧な型」にこだわらなくてOKです🙆‍♀️🌸

---

## 2 1人開発で残すべきもの 捨てていいもの🧹✨

### 残すべきもの 迷わないための最低限🧱

* **ドメインは孤立させる**（DBやWebの都合を入れない）🧼
* **ユースケースの置き場所を作る**（アプリの操作手順）🎮
* **外側の技術は差し替え前提にする**（EF Core・APIクライアントなど）🔁

### 捨てていいもの 1人には重いかも⚖️

* なんでもかんでも **プロジェクト分割しすぎ**（10個とか）📦📦📦
* 役割が薄いのに **インターフェースを増やしすぎ**（逆に読みにくい）🌀
* 「図の通りにしなきゃ…」っていう **儀式化** 🙏💦

---

## 3 迷わないための結論は3パターンだけ💡🧭

ここからは「おすすめ構成」を3つ出すね！
1人開発なら、まずこれで迷いゼロになります😊✨

---

### パターンA 正統派の4プロジェクト構成📚

しっかりした中〜大規模向き！

* `Domain`
* `Application`
* `Infrastructure`
* `Web`

✅良いところ

* 境界がガチガチに守れる🛡️
* テストしやすい🧪
* 後で人が増えても崩れにくい👥

⚠️つらいところ

* 1人だと「作業の移動」が増える🚶‍♀️💦
* DI設定とかも増えがち

---

### パターンB 1人最強の3プロジェクト構成🏆

**おすすめはこれ**！軽いのに強い💪✨

* `Domain`
* `Application`
* `Web`（ここにインフラ実装を置いちゃう）

✅良いところ

* 境界は守れる
* プロジェクト数が少なくて脳が疲れない🧠💤
* 1人の速度が出る🚀

⚠️注意点

* `Web` に「インフラ置き場フォルダ」を作って、そこだけ隔離するのがコツ🏝️

---

### パターンC 1プロジェクト フォルダ分割のみ🧳

小さく始めたい時だけ！

* `Domain/`
* `Application/`
* `Infrastructure/`
* `Presentation/`

✅良いところ

* 最速で作り始められる⚡
  ⚠️弱いところ
* 依存ルールが破られやすい（AIが特に破りがち）🤖💥
* 後で分割する時に移植作業が発生
 
 ```mermaid
 flowchart TD
    Start["プロジェクト構成どうする？🤔"] --> Q1{"チーム人数は？"}
    Q1 -- "3人以上 or<br/>長期運用 🏢" --> A["パターンA: 4プロジェクト<br/>(Domain/App/Infra/Web)"]
    Q1 -- "ほぼ1人 🏃‍♀️" --> Q2{"将来拡大する？"}
    
    Q2 -- "するかも/ちゃんとやりたい" --> B["パターンB: 3プロジェクト 👑<br/>(Domain/App/Web)"]
    Q2 -- "プロトタイプ/超短期" --> C["パターンC: 1プロジェクト 🎒<br/>(フォルダ分けのみ)"]
    
    style B fill:#f9f,stroke:#333,stroke-width:4px
 ```
 
 ---

## 4 今回のおすすめはパターンBでいこう😊✨

ディレクトリはこんな感じが超いいよ📁💕

* `src/`

  * `TaskApp.Domain/`
  * `TaskApp.Application/`
  * `TaskApp.Web/`

    * `Infrastructure/` ← ここが大事🌟

---

## 5 ミニ題材で体験しよう タスク追加ユースケース📝✨

### Domain タスクという概念だけを置く🏰

![058_domain_king](./picture/ddd_cs_study_058_domain_king.png)

```csharp
namespace TaskApp.Domain.Tasks;

public sealed class TaskItem
{
    public TaskId Id { get; }
    public string Title { get; private set; }
    public bool Done { get; private set; }

    public TaskItem(TaskId id, string title)
    {
        if (string.IsNullOrWhiteSpace(title))
            throw new ArgumentException("タイトルは必須だよ🙂", nameof(title));

        Id = id;
        Title = title.Trim();
        Done = false;
    }

    public void MarkDone() => Done = true;
}

public readonly record struct TaskId(Guid Value)
{
    public static TaskId New() => new(Guid.NewGuid());
}

public interface ITaskRepository
{
    Task AddAsync(TaskItem task, CancellationToken ct);
    Task<TaskItem?> FindAsync(TaskId id, CancellationToken ct);
}
```

ポイント🧡

* ドメインは「DBのこと知らない」🙅‍♀️🗄️
* ここにEF Coreの属性とか置かないよ〜！

---

### Application ユースケースを置く🎯

![058_app_conductor](./picture/ddd_cs_study_058_app_conductor.png)

```csharp
using TaskApp.Domain.Tasks;

namespace TaskApp.Application.Tasks;

public sealed record AddTaskCommand(string Title);

public sealed class AddTaskUseCase(ITaskRepository repo)
{
    public async Task<TaskId> HandleAsync(AddTaskCommand cmd, CancellationToken ct)
    {
        var task = new TaskItem(TaskId.New(), cmd.Title);
        await repo.AddAsync(task, ct);
        return task.Id;
    }
}
```

ポイント💛

* **“操作手順”がここ**だよ（ユーザーがやりたいこと）🧭
* ここもDB知らない！Repositoryにお願いするだけ🙏✨

---

### Web 側でDIしてインフラ実装を書く🔧

![058_infra_toolbox](./picture/ddd_cs_study_058_infra_toolbox.png)

`TaskApp.Web/Infrastructure/` に実装を隔離しよう🏝️

```csharp
using Microsoft.EntityFrameworkCore;
using TaskApp.Domain.Tasks;

namespace TaskApp.Web.Infrastructure;

public sealed class AppDbContext(DbContextOptions<AppDbContext> options) : DbContext(options)
{
    public DbSet<TaskEntity> Tasks => Set<TaskEntity>();
}

public sealed class TaskEntity
{
    public Guid Id { get; set; }
    public string Title { get; set; } = "";
    public bool Done { get; set; }
}

public sealed class EfTaskRepository(AppDbContext db) : ITaskRepository
{
    public async Task AddAsync(TaskItem task, CancellationToken ct)
    {
        db.Tasks.Add(new TaskEntity
        {
            Id = task.Id.Value,
            Title = task.Title,
            Done = task.Done
        });
        await db.SaveChangesAsync(ct);
    }

    public async Task<TaskItem?> FindAsync(TaskId id, CancellationToken ct)
    {
        var e = await db.Tasks.FirstOrDefaultAsync(x => x.Id == id.Value, ct);
        return e is null ? null : new TaskItem(new TaskId(e.Id), e.Title);
    }
}
```

ポイント🩵

* **DomainのインターフェースをWebで実装**するのがクリーンの気持ちよさ✨
* もしDBを変えても、DomainとApplicationはほぼ無傷だよ🛡️

---

### Web エンドポイントでUseCaseを呼ぶ📮

![058_web_receptionist](./picture/ddd_cs_study_058_web_receptionist.png)

```csharp
using TaskApp.Application.Tasks;
using TaskApp.Domain.Tasks;
using TaskApp.Web.Infrastructure;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddDbContext<AppDbContext>(/* ここは好きなDBで */);
builder.Services.AddScoped<ITaskRepository, EfTaskRepository>();
builder.Services.AddScoped<AddTaskUseCase>();

var app = builder.Build();

app.MapPost("/tasks", async (AddTaskCommand cmd, AddTaskUseCase useCase, CancellationToken ct) =>
{
    var id = await useCase.HandleAsync(cmd, ct);
    return Results.Created($"/tasks/{id.Value}", new { id = id.Value });
});

app.Run();
```

---

## 6 AIに頼るときの最強ルールはこれ🤖🧠✨

AIって便利なんだけど、**境界を平気で壊す**ことあるの…！😇💥
だから、AIに投げるときは“役割”を短く固定すると強いよ💪

### コピペ用プロンプト例📋✨

* 「`Domain` はDBやWebを知らない。EF Core型やDTOを入れない」
* 「`Application` はユースケース。Repositoryインターフェースを呼ぶだけ」
* 「DB操作や外部APIは `Web/Infrastructure` に閉じ込める」
* 「依存の向きは Domain ← Application ← Web の順」

これだけで、生成コードの事故率がグッと下がります🚑✨

---

## 7 よくある事故あるある集😵‍💫🚨

* Domainに `DbContext` が出現する🗄️👻
* Applicationが `EntityFrameworkCore` を参照しだす📌
* 「とりあえずDTO」をDomainに置く🎁（それは外側！）
* なんでもかんでも `Service` で巨大クラスになる🧟‍♀️

見つけたら「外側に追放！」って気持ちでOKです🏹✨

---

## 8 ミニ演習 今日からできるやつ🎒🌸

### お題

あなたのアプリの「いちばん小さい機能」1つだけを、パターンBに寄せてみよう😊✨

1. ドメインの概念を1個だけ作る（例：`Money`, `TaskItem`, `UserId`）💎
2. ユースケースを1本だけ作る（例：追加、更新）🎯
3. DBやAPIは `Web/Infrastructure` に隔離する🏝️
4. AIにレビューさせる：「境界破ってない？」って聞く🤖🔍

---

## まとめ 1人開発のクリーンは軽くていい🧡✨

* クリーンアーキテクチャは「型」より「依存の向き」が命➡️
* 1人なら **3プロジェクト構成**が最強バランス🏆
* AI時代は「境界」を人間が決めると、AIが超働く🤝🤖

次の章では、さらに具体的に **ベストなプロジェクト構成**に落としていくよ〜📁✨（第59章へつづくっ💕）

[1]: https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-14?utm_source=chatgpt.com "What's new in C# 14"
