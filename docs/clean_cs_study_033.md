# 第33章：Persistence Adapterの考え方（DBは“詳細”）🗄️

この章はひとことで言うと、**「DBの都合を、Core（Entities / UseCases）に一切入れない」**ための作法だよ〜！😺💕

---

## 1) 今日のゴール 🎯💡

章の終わりに、これができたら勝ち🏆✨

* ✅ UseCase側は **「IMemoRepository」みたいな “口（interface）”** だけ知ってる
* ✅ DB（EF Core / SQL Server / SQLite…）は **外側の実装（Adapter）** に押し込める
* ✅ **InMemory → EF Core** に差し替えても、UseCaseのコードがほぼ変わらない
* ✅ 「依存は内側へ」のルールを、コードとプロジェクト参照で守れてる
  （依存ルールの原典は Uncle Bob の Clean Architecture の説明がわかりやすいよ） ([blog.cleancoder.com][1])

---

## 2) なんで「DBは詳細」なの？🤔🧩

![DB Noise vs Core Silence](./picture/clean_cs_study_033_db_noise.png)

DBは便利だけど、こんな“外側都合”が山ほどあるよね👇

* テーブル設計、カラム追加、インデックス…📚
* EF Coreの設定、マイグレーション、接続文字列…🔧
* DB製品の違い（SQL Server / PostgreSQL / SQLite…）🧠

これらは **ビジネスルール（Core）の本質じゃない** ので、**外側に閉じ込める**のがクリーンアーキの気持ちよさ🌿✨
Microsoft のアーキテクチャガイドでも「UIはCoreのinterfaceを見て、Infrastructureの実装を知らないのが理想」って説明されてるよ ([Microsoft Learn][2])

---

## 3) まず“絵”で理解しよ！🖼️➡️

![Persistence Adapterの構造](./picture/clean_cs_study_033_persistence_adapter.png)

ポイントはこれ👇

* **Core**：`IMemoRepository` を *宣言*（interfaceだけ）
* **Persistence Adapter**：`EfMemoRepository` を *実装*（EF CoreのDbContextでゴリゴリ）
* **DI**：実行時に “どっちの実装を刺すか” を決める（InMemoryでもEFでもOK）

イメージ（依存方向が超大事）👇

```text
[Web(API)] ───────→ [Adapters(Persistence)] ───────→ [Core]
   (参照する)              (参照する)                 (参照しない)
   ASP.NET Core            EF Core / DB                ルールと口(interface)だけ
```

---

## 4) 作るもの：Repoを InMemory → EF Core に差し替え 🪄💾

ここでは題材を「Memo」でいくね📝✨（他でも同じ！）

### 4-1. Core側：Repository “口” を定義する（interface）🔌

![The Interface Contract](./picture/clean_cs_study_033_interface_contract.png)

> 置き場所の例：`Core/UseCases/Ports/IMemoRepository.cs`
> ※ここに **EF Coreの型（DbContext / DbSet / IQueryable）を絶対に入れない** 🙅‍♀️

```csharp
namespace MyApp.Core.UseCases.Ports;

public interface IMemoRepository
{
    Task AddAsync(Memo memo, CancellationToken ct);
    Task<Memo?> FindByIdAsync(Guid id, CancellationToken ct);
    Task UpdateAsync(Memo memo, CancellationToken ct);
    Task DeleteAsync(Guid id, CancellationToken ct);
}
```

🧠コツ：

* メソッドは **UseCaseが本当に必要な分だけ** に絞る（“汎用化しすぎ”禁止🚫）
* `IQueryable` を返すのは、EFの都合が漏れやすいので初心者は特に避けよ〜🙅‍♂️💦

---

### 4-2. Adapter側：まず InMemory 実装で動かす 🧸✅

![InMemory Implementation](./picture/clean_cs_study_033_inmemory_box.png)

> 置き場所の例：`Adapters.Persistence/InMemory/InMemoryMemoRepository.cs`

```csharp
using System.Collections.Concurrent;
using MyApp.Core.UseCases.Ports;

namespace MyApp.Adapters.Persistence.InMemory;

public sealed class InMemoryMemoRepository : IMemoRepository
{
    private readonly ConcurrentDictionary<Guid, Memo> _store = new();

    public Task AddAsync(Memo memo, CancellationToken ct)
    {
        _store[memo.Id] = memo;
        return Task.CompletedTask;
    }

    public Task<Memo?> FindByIdAsync(Guid id, CancellationToken ct)
    {
        _store.TryGetValue(id, out var memo);
        return Task.FromResult(memo);
    }

    public Task UpdateAsync(Memo memo, CancellationToken ct)
    {
        _store[memo.Id] = memo;
        return Task.CompletedTask;
    }

    public Task DeleteAsync(Guid id, CancellationToken ct)
    {
        _store.TryRemove(id, out _);
        return Task.CompletedTask;
    }
}
```

✅ここまでで **UseCaseはDBを一切知らずに動く** よ！うれしい〜！🥳🎉

---

## 5) いよいよEF Core実装（本命のPersistence Adapter）🧱🗄️

![EF Core Implementation](./picture/clean_cs_study_033_efcore_vault.png)

2026年1月時点では .NET 10 がLTSで、EF Coreも 10 系が提供されてるよ（例：10.0.2） ([Microsoft for Developers][3])

### 5-1. Adapterプロジェクトに EF Core を追加 📦✨

（例：SQL Server の場合。SQLiteでもOKだよ〜！）

```powershell
dotnet add .\MyApp.Adapters.Persistence\ package Microsoft.EntityFrameworkCore --version 10.0.2
dotnet add .\MyApp.Adapters.Persistence\ package Microsoft.EntityFrameworkCore.SqlServer --version 10.0.2
```

マイグレーションや `dotnet ef` を使うなら、ツールやDesignパッケージも必要になりやすいよ👇 ([NuGet][4])

```powershell
dotnet tool install --global dotnet-ef --version 10.0.2
dotnet add .\MyApp.Web\ package Microsoft.EntityFrameworkCore.Design --version 10.0.2
```

> ⚠️ multi-project構成だと「スタートアッププロジェクト（Web側）」に `Design` が必要って怒られることがあるある！ ([Stack Overflow][5])

---

### 5-2. DB用モデル（永続化用）と DbContext を用意 🧱

> 本格的な「DomainモデルとDBモデルを分ける」は次章（第34章）で厚くやるけど、ここでは “雰囲気” を先に掴もう😺

```csharp
using Microsoft.EntityFrameworkCore;

namespace MyApp.Adapters.Persistence.Ef;

public sealed class AppDbContext : DbContext
{
    public DbSet<MemoRecord> Memos => Set<MemoRecord>();

    public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) { }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<MemoRecord>(b =>
        {
            b.ToTable("Memos");
            b.HasKey(x => x.Id);
            b.Property(x => x.Title).HasMaxLength(200).IsRequired();
            b.Property(x => x.Body).HasMaxLength(4000).IsRequired();
        });
    }
}

public sealed class MemoRecord
{
    public Guid Id { get; set; }
    public string Title { get; set; } = "";
    public string Body { get; set; } = "";
}
```

---

### 5-3. EF Core Repository実装（＝Persistence Adapter）🔁

```csharp
using Microsoft.EntityFrameworkCore;
using MyApp.Core.UseCases.Ports;

namespace MyApp.Adapters.Persistence.Ef;

public sealed class EfMemoRepository : IMemoRepository
{
    private readonly AppDbContext _db;

    public EfMemoRepository(AppDbContext db) => _db = db;

    public async Task AddAsync(Memo memo, CancellationToken ct)
    {
        _db.Memos.Add(ToRecord(memo));
        await _db.SaveChangesAsync(ct);
    }

    public async Task<Memo?> FindByIdAsync(Guid id, CancellationToken ct)
    {
        var record = await _db.Memos.AsNoTracking()
            .FirstOrDefaultAsync(x => x.Id == id, ct);

        return record is null ? null : ToDomain(record);
    }

    public async Task UpdateAsync(Memo memo, CancellationToken ct)
    {
        _db.Memos.Update(ToRecord(memo));
        await _db.SaveChangesAsync(ct);
    }

    public async Task DeleteAsync(Guid id, CancellationToken ct)
    {
        var record = await _db.Memos.FirstOrDefaultAsync(x => x.Id == id, ct);
        if (record is null) return;

        _db.Memos.Remove(record);
        await _db.SaveChangesAsync(ct);
    }

    private static MemoRecord ToRecord(Memo memo) => new()
    {
        Id = memo.Id,
        Title = memo.Title.Value,
        Body = memo.Body.Value
    };

    private static Memo ToDomain(MemoRecord r)
        => Memo.Rehydrate(r.Id, new MemoTitle(r.Title), new MemoBody(r.Body));
}
```

🥰ここが最高ポイント：

* UseCaseは `IMemoRepository` しか知らない
* EFの都合（DbContext/DbSet/AsNoTracking/SaveChangesAsync）は **全部Adapterの中**
  → つまり「DBは詳細」を体現できてる✨ ([Microsoft Learn][6])

---

## 6) DIで“差し替え”を完成させる 🧷✨

![Dependency Injection Switch](./picture/clean_cs_study_033_di_switch.png)

Web側（Composition Root）で登録するよ👇

```csharp
using Microsoft.EntityFrameworkCore;
using MyApp.Adapters.Persistence.Ef;
using MyApp.Adapters.Persistence.InMemory;
using MyApp.Core.UseCases.Ports;

var builder = WebApplication.CreateBuilder(args);

// 例：開発はInMemory、本番はEF…みたいに差し替えできる🪄
if (builder.Environment.IsDevelopment())
{
    builder.Services.AddSingleton<IMemoRepository, InMemoryMemoRepository>();
}
else
{
    builder.Services.AddDbContext<AppDbContext>(opt =>
        opt.UseSqlServer(builder.Configuration.GetConnectionString("Default")));

    builder.Services.AddScoped<IMemoRepository, EfMemoRepository>();
}

var app = builder.Build();
app.Run();
```

✅これで、UseCaseは1行も変えずに
**InMemory ⇄ SQL Server（EF Core）** を切り替えられるよ〜！🎉🎉🎉

---

## 7) よくある事故パターン集 🚑💥（ここ超大事！）

![Leaking Abstractions](./picture/clean_cs_study_033_toxic_leak.png)

### ❌事故1：CoreがEF Coreを参照しちゃう

* `DbContext` をUseCaseに注入しちゃう
* `IQueryable` をCoreから返しちゃう
  → 依存ルール違反で、外側の都合が内側に侵入😇

### ❌事故2：Repositoryが“万能すぎる”

* `GetAll()`, `FindByCondition(...)` みたいに増えがち
  → UseCaseごとの意図が消える⚠️

### ❌事故3：DTO/DBモデルをそのままCoreに持ち込む

* 永続化用の `MemoRecord` をCoreで使いはじめる
  → 次章（第34章）の話に直結する罠🪤✨

---

## 8) ミニ課題（手を動かすやつ）✍️🔥

### 課題A：差し替え確認（超重要）✅

1. InMemoryで動く
2. EF Coreで動く
3. UseCaseコードが **変わってない** ことを確認🎯

### 課題B：DBプロバイダを変えてみる（おもしろい）🧪

* SQL Server → SQLite に変えても、UseCaseは無変更のまま
  （EF Coreは色んなDBをサポートしてるよ ([NuGet][7])）

---

## 9) Copilot / Codex に頼ると気持ちいいポイント 🤖💖

そのまま貼って使える“指示文”置いとくね👇

* 🧠設計レビュー
  「`IMemoRepository` のメソッドが汎用化しすぎてないか、UseCase目線で削れる案を出して。IQueryableは禁止で」

* 🔁マッピング安全性
  「Domain↔DBモデル変換で落とし穴（null/既定値/ID/更新競合）を列挙して、ガード案も提案して」

* 🧰EF設定
  「MemoRecordのテーブル設計（制約、インデックス候補）を、検索ユースケース前提で提案して」

---

## 10) まとめ 🌸✨

* Persistence Adapterは **「DBという詳細」を外側に閉じ込める壁** 🧱
* Coreは **interfaceだけ** を持つ（実装を知らない）🔌
* DIで実行時に合体して、**差し替え可能**になる🪄
* 依存ルールが守れると、変更が怖くなくなる😌💕

次の第34章では、ここで出てきた **「DBモデルとDomainモデルを分ける（マッピングで吸収）」** を、もっと“実戦向け”に仕上げようね〜！🔁🔥

[1]: https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html?utm_source=chatgpt.com "Clean Architecture by Uncle Bob - The Clean Code Blog"
[2]: https://learn.microsoft.com/en-us/dotnet/architecture/modern-web-apps-azure/common-web-application-architectures?utm_source=chatgpt.com "Common web application architectures - .NET"
[3]: https://devblogs.microsoft.com/dotnet/dotnet-and-dotnet-framework-january-2026-servicing-updates/?utm_source=chatgpt.com ".NET and .NET Framework January 2026 servicing ..."
[4]: https://www.nuget.org/packages/dotnet-ef?utm_source=chatgpt.com "dotnet-ef 10.0.2"
[5]: https://stackoverflow.com/questions/57071641/cant-create-migration-because-entityframework-design-package-isnt-recognized?utm_source=chatgpt.com "Can't create migration because EntityFramework.Design ..."
[6]: https://learn.microsoft.com/en-us/dotnet/architecture/microservices/microservice-ddd-cqrs-patterns/infrastructure-persistence-layer-design?utm_source=chatgpt.com "Designing the infrastructure persistence layer - .NET"
[7]: https://www.nuget.org/packages/microsoft.entityframeworkcore?utm_source=chatgpt.com "Microsoft.EntityFrameworkCore 10.0.2"
