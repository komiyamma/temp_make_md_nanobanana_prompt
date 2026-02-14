# 第17章：総まとめミニプロジェクト（設計→実装→最小テスト）💪🎉

この章は「いままでの全部を、1回でつなげる回」だよ〜😊✨
今回は **C# 14（最新）＋ .NET 10** を前提に進めるね（C# 14 は .NET 10 でサポート＆最新リリース扱い）。([Microsoft Learn][1])
あと **Visual Studio 2026 が GA（一般提供）** になってて、AI 活用も深く統合されてるよ〜🤖🧠([Microsoft for Developers][2])

---

## 0) 今日のゴール（完成判定）✅✨

![Todo App Architecture](./picture/hc_lc_cs_study_017_todo_app_architecture.png)

### ✅ 完成物（合格ライン）

* **4つの箱**に分かれてる：`UI / Application / Domain / Infrastructure` 📦📦📦📦
* **Domain** が外側（UI/Infra）を知らない（依存の矢印が内向き）🛡️
* `IClock / INotifier / ITodoRepository` が **差し替え可能**（低結合）🔌
* **最小テスト 1〜3本**が通ってる🧪✅（とくに「壊れやすいルール」を守る）

---

## 1) 題材はこれにするよ：ToDo＋締切通知✅⏰📣

### MVP要件（最小の仕様）🎯

1. ToDoを追加できる（タイトル必須）➕
2. 期限（任意）を付けられる⏳
3. 一覧表示できる📋
4. 完了にできる✅
5. **期限が24時間以内**の未完了ToDoを通知する📣

ここで学べること：

* **高凝集**：Domainにルールを集める（タイトル必須、期限判定など）🏠✨
* **低結合**：通知・時刻・保存を interface で外に逃がす🔌✨
* **依存の向き**：内側（Domain）を守る🛡️

---

## 2) 17A：まず“設計だけ”する（ここ超大事）🗺️✍️

## 2-1) 変更理由（＝境界の根拠）を3つ書く🧠✨

例：

* 通知方法が変わる（Console → LINE風 → Slack風…）📣🔁
* 保存先が変わる（JSONファイル → DB → Web API）💾🔁
* 期限判定ルールが変わる（24h → 48h、休日は除外…）⏰🔁

この「変わり方」が違うものは、**同じクラスに混ぜない**よ🍲❌

## 2-2) 4つの箱に仕分け（責務の住所）📦✨

* **UI**：入力/表示（Consoleメニューなど）🖥️
* **Application**：ユースケース（Add/Complete/List/Notify）🧭
* **Domain**：ルール（タイトル必須、期限が近い判定、完了の状態遷移）🏛️
* **Infrastructure**：保存/時刻/通知の実装（Json/Clock/Console）🧰

## 2-3) クラス一覧（最小セット）📄✨

**Domain（ルールの中心）**

* `TodoTitle`（空を禁止）🏷️
* `DueDate`（過去を禁止 ※作る時に now と比較）⏳
* `TodoItem`（完了・期限判定）✅⏰

**Application（やりたいこと＝ユースケース）**

* `AddTodoUseCase`
* `CompleteTodoUseCase`
* `ListTodosUseCase`
* `NotifyDueSoonUseCase`

**Application側の interface（ポート）🔌**

* `ITodoRepository`（保存）
* `IClock`（現在時刻）
* `INotifier`（通知）

**Infrastructure（差し替え可能な実装）🧰**

* `JsonFileTodoRepository`
* `SystemClock`
* `ConsoleNotifier`

## 2-4) 依存の矢印（これだけ守れば迷子激減）🕸️✨

* UI → Application → Domain
* Infrastructure → Application（の interface を実装）
* ❌ Domain → Infrastructure は禁止（内側が外側を知らない）🛡️

```mermaid
classDiagram
    direction TB
    
    namespace UI {
        class Program
    }
    
    namespace Application {
        class AddTodoUseCase
        class NotifyDueSoonUseCase
        class ITodoRepository { <<interface>> }
        class INotifier { <<interface>> }
    }
    
    namespace Domain {
        class TodoItem
        class DueDate
        class TodoTitle
    }
    
    namespace Infrastructure {
        class JsonFileTodoRepository
        class ConsoleNotifier
        class SystemClock
    }

    UI ..> Application : 呼ぶ
    UI ..> Infrastructure : 組み立てる(new)

    Application ..> Domain : 使う
    Application ..> Application : (Interface定義)

    Infrastructure ..|> Application : 実装する (Rep/Notifier)
    
    %% 依存の矢印チェック
    %% Domainは誰にも依存しない🛡️
```

---

## 3) 17B：実装する（“崩れない順番”で）🛠️✨

## 3-1) プロジェクト構成（これにすると超ラク）📁✨

* `TodoMini.Domain`（クラスライブラリ）
* `TodoMini.Application`（クラスライブラリ：Domain参照）
* `TodoMini.Infrastructure`（クラスライブラリ：Application参照）
* `TodoMini.Ui`（Consoleアプリ：Application/Infrastructure参照）
* `TodoMini.Tests`（xUnit：Domain/Application参照）🧪

---

## 3-2) Domain（ルール）から書く🏛️✨

```csharp
// TodoMini.Domain/TodoTitle.cs
namespace TodoMini.Domain;

public sealed record TodoTitle
{
    public string Value { get; }

    public TodoTitle(string value)
    {
        if (string.IsNullOrWhiteSpace(value))
            throw new ArgumentException("タイトルは必須だよ🥺", nameof(value));

        Value = value.Trim();
    }

    public override string ToString() => Value;
}
```

```csharp
// TodoMini.Domain/DueDate.cs
namespace TodoMini.Domain;

public sealed record DueDate
{
    public DateTimeOffset Value { get; }

    private DueDate(DateTimeOffset value) => Value = value;

    public static DueDate Create(DateTimeOffset value, DateTimeOffset now)
    {
        if (value < now)
            throw new ArgumentException("期限が過去なのはダメだよ〜😵‍💫");
        return new DueDate(value);
    }
}
```

```csharp
// TodoMini.Domain/TodoItem.cs
namespace TodoMini.Domain;

public sealed class TodoItem
{
    public Guid Id { get; }
    public TodoTitle Title { get; }
    public DueDate? Due { get; }
    public bool IsCompleted { get; private set; }
    public DateTimeOffset CreatedAt { get; }
    public DateTimeOffset? CompletedAt { get; private set; }

    private TodoItem(Guid id, TodoTitle title, DueDate? due, DateTimeOffset createdAt)
    {
        Id = id;
        Title = title;
        Due = due;
        CreatedAt = createdAt;
    }

    public static TodoItem CreateNew(string title, DateTimeOffset now, DateTimeOffset? dueOrNull)
    {
        var t = new TodoTitle(title);
        DueDate? due = dueOrNull is null ? null : DueDate.Create(dueOrNull.Value, now);
        return new TodoItem(Guid.NewGuid(), t, due, now);
    }

    public void Complete(DateTimeOffset now)
    {
        if (IsCompleted) return; // 冪等：2回押しても壊れない🧯
        IsCompleted = true;
        CompletedAt = now;
    }

    public bool IsDueSoon(DateTimeOffset now, TimeSpan window)
        => !IsCompleted && Due is not null && Due.Value.Value <= now + window;
}
```

🌟ポイント：Domainは **ConsoleもJsonも知らない**よ！これが強い🛡️✨

---

## 3-3) Application（ユースケース）を書く🧭✨

```csharp
// TodoMini.Application/Ports.cs
using TodoMini.Domain;

namespace TodoMini.Application;

public interface IClock
{
    DateTimeOffset Now { get; }
}

public interface INotifier
{
    Task NotifyAsync(string message, CancellationToken ct);
}

public interface ITodoRepository
{
    Task<IReadOnlyList<TodoItem>> ListAsync(CancellationToken ct);
    Task<TodoItem?> FindAsync(Guid id, CancellationToken ct);
    Task UpsertAsync(TodoItem item, CancellationToken ct);
}
```

```csharp
// TodoMini.Application/AddTodoUseCase.cs
using TodoMini.Domain;

namespace TodoMini.Application;

public sealed class AddTodoUseCase
{
    private readonly ITodoRepository _repo;
    private readonly IClock _clock;

    public AddTodoUseCase(ITodoRepository repo, IClock clock)
    {
        _repo = repo;
        _clock = clock;
    }

    public async Task<Guid> ExecuteAsync(string title, DateTimeOffset? due, CancellationToken ct)
    {
        var now = _clock.Now;
        var item = TodoItem.CreateNew(title, now, due);
        await _repo.UpsertAsync(item, ct);
        return item.Id;
    }
}
```

```csharp
// TodoMini.Application/CompleteTodoUseCase.cs
namespace TodoMini.Application;

public sealed class CompleteTodoUseCase
{
    private readonly ITodoRepository _repo;
    private readonly IClock _clock;

    public CompleteTodoUseCase(ITodoRepository repo, IClock clock)
    {
        _repo = repo;
        _clock = clock;
    }

    public async Task<bool> ExecuteAsync(Guid id, CancellationToken ct)
    {
        var item = await _repo.FindAsync(id, ct);
        if (item is null) return false;

        item.Complete(_clock.Now);
        await _repo.UpsertAsync(item, ct);
        return true;
    }
}
```

```csharp
// TodoMini.Application/ListTodosUseCase.cs
using TodoMini.Domain;

namespace TodoMini.Application;

public sealed class ListTodosUseCase
{
    private readonly ITodoRepository _repo;

    public ListTodosUseCase(ITodoRepository repo) => _repo = repo;

    public Task<IReadOnlyList<TodoItem>> ExecuteAsync(CancellationToken ct)
        => _repo.ListAsync(ct);
}
```

```csharp
// TodoMini.Application/NotifyDueSoonUseCase.cs
namespace TodoMini.Application;

public sealed class NotifyDueSoonUseCase
{
    private readonly ITodoRepository _repo;
    private readonly IClock _clock;
    private readonly INotifier _notifier;

    public NotifyDueSoonUseCase(ITodoRepository repo, IClock clock, INotifier notifier)
    {
        _repo = repo;
        _clock = clock;
        _notifier = notifier;
    }

    public async Task<int> ExecuteAsync(TimeSpan window, CancellationToken ct)
    {
        var now = _clock.Now;
        var items = await _repo.ListAsync(ct);

        var dueSoon = items.Where(x => x.IsDueSoon(now, window)).ToList();
        foreach (var x in dueSoon)
        {
            await _notifier.NotifyAsync($"⏰締切近いよ！: {x.Title}", ct);
        }

        return dueSoon.Count;
    }
}
```

🌟ポイント：Applicationは **“どう保存するか/どう通知するか” を知らない**🎀
知ってるのは interface だけ（低結合のコア）🔌✨

---

## 3-4) Infrastructure（実装）を書く🧰✨

```csharp
// TodoMini.Infrastructure/SystemClock.cs
using TodoMini.Application;

namespace TodoMini.Infrastructure;

public sealed class SystemClock : IClock
{
    public DateTimeOffset Now => DateTimeOffset.Now;
}
```

```csharp
// TodoMini.Infrastructure/ConsoleNotifier.cs
using TodoMini.Application;

namespace TodoMini.Infrastructure;

public sealed class ConsoleNotifier : INotifier
{
    public Task NotifyAsync(string message, CancellationToken ct)
    {
        Console.WriteLine(message);
        return Task.CompletedTask;
    }
}
```

```csharp
// TodoMini.Infrastructure/JsonFileTodoRepository.cs
using System.Text.Json;
using TodoMini.Application;
using TodoMini.Domain;

namespace TodoMini.Infrastructure;

public sealed class JsonFileTodoRepository : ITodoRepository
{
    private readonly string _path;
    private static readonly JsonSerializerOptions _json = new() { WriteIndented = true };

    public JsonFileTodoRepository(string path) => _path = path;

    public async Task<IReadOnlyList<TodoItem>> ListAsync(CancellationToken ct)
        => (await LoadAsync(ct)).Select(FromDto).ToList();

    public async Task<TodoItem?> FindAsync(Guid id, CancellationToken ct)
        => (await ListAsync(ct)).FirstOrDefault(x => x.Id == id);

    public async Task UpsertAsync(TodoItem item, CancellationToken ct)
    {
        var dtos = await LoadAsync(ct);

        var idx = dtos.FindIndex(x => x.Id == item.Id);
        var dto = ToDto(item);

        if (idx >= 0) dtos[idx] = dto;
        else dtos.Add(dto);

        Directory.CreateDirectory(Path.GetDirectoryName(_path)!);
        await File.WriteAllTextAsync(_path, JsonSerializer.Serialize(dtos, _json), ct);
    }

    private async Task<List<TodoDto>> LoadAsync(CancellationToken ct)
    {
        if (!File.Exists(_path)) return new List<TodoDto>();
        var json = await File.ReadAllTextAsync(_path, ct);
        return JsonSerializer.Deserialize<List<TodoDto>>(json, _json) ?? new List<TodoDto>();
    }

    private static TodoDto ToDto(TodoItem x) => new(
        x.Id,
        x.Title.Value,
        x.Due?.Value,
        x.IsCompleted,
        x.CreatedAt,
        x.CompletedAt
    );

    private static TodoItem FromDto(TodoDto d)
    {
        // Domainのpublic APIだけで復元したいので、ここは「復元用の作り方」を簡易に実装するよ
        // 目的：教材を短くするため（実務では Factory/Mapper を整理すると◎）🎀
        var title = new TodoTitle(d.Title);

        // Dueは「過去かどうか」判定が本来必要だけど、永続化データなのでここでは許容して読み込む
        // （厳密にしたい場合は "読み込み時の整合性チェック" を別責務で持たせると高凝集！）✨
        DueDate? due = d.Due is null ? null : UnsafeDue(d.Due.Value);

        var item = (TodoItem)typeof(TodoItem)
            .GetConstructor(System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance,
                binder: null,
                types: new[] { typeof(Guid), typeof(TodoTitle), typeof(DueDate), typeof(DateTimeOffset) },
                modifiers: null)!
            .Invoke(new object?[] { d.Id, title, due, d.CreatedAt });

        if (d.IsCompleted)
        {
            item.Complete(d.CompletedAt ?? d.CreatedAt);
        }
        return item;
    }

    private static DueDate UnsafeDue(DateTimeOffset value)
        => (DueDate)typeof(DueDate)
            .GetConstructor(System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance,
                binder: null, types: new[] { typeof(DateTimeOffset) }, modifiers: null)!
            .Invoke(new object?[] { value });

    private sealed record TodoDto(
        Guid Id,
        string Title,
        DateTimeOffset? Due,
        bool IsCompleted,
        DateTimeOffset CreatedAt,
        DateTimeOffset? CompletedAt
    );
}
```

※ `FromDto` の反射は「教材を短くするための近道」だよ💦
実務なら **復元専用Factory** をDomainに用意する／Dto用の別モデルを置く、がキレイ✨

---

## 3-5) UI（Console）＋ Composition Root（組み立て場所）🏗️🖥️

```csharp
// TodoMini.Ui/Program.cs
using TodoMini.Application;
using TodoMini.Infrastructure;

var dataPath = Path.Combine(AppContext.BaseDirectory, "data", "todos.json");

ITodoRepository repo = new JsonFileTodoRepository(dataPath);
IClock clock = new SystemClock();
INotifier notifier = new ConsoleNotifier();

var add = new AddTodoUseCase(repo, clock);
var complete = new CompleteTodoUseCase(repo, clock);
var list = new ListTodosUseCase(repo);
var notify = new NotifyDueSoonUseCase(repo, clock, notifier);

while (true)
{
    Console.WriteLine();
    Console.WriteLine("1) 追加 ➕  2) 一覧 📋  3) 完了 ✅  4) 締切通知 ⏰📣  0) 終了 👋");
    Console.Write(">");
    var cmd = Console.ReadLine()?.Trim();

    if (cmd == "0") break;

    if (cmd == "1")
    {
        Console.Write("タイトル:");
        var title = Console.ReadLine() ?? "";

        Console.Write("期限(例: 2026-01-13 18:00) / 空でなし:");
        var dueText = Console.ReadLine();
        DateTimeOffset? due = DateTimeOffset.TryParse(dueText, out var d) ? d : null;

        var id = await add.ExecuteAsync(title, due, CancellationToken.None);
        Console.WriteLine($"追加したよ〜🎉 id={id}");
    }
    else if (cmd == "2")
    {
        var items = await list.ExecuteAsync(CancellationToken.None);
        foreach (var x in items.OrderBy(x => x.IsCompleted).ThenBy(x => x.Due?.Value))
        {
            var due = x.Due is null ? "-" : x.Due.Value.Value.ToString("yyyy-MM-dd HH:mm");
            var done = x.IsCompleted ? "✅" : "⬜";
            Console.WriteLine($"{done} {x.Id} | {x.Title} | due={due}");
        }
    }
    else if (cmd == "3")
    {
        Console.Write("完了にするid:");
        var idText = Console.ReadLine();
        if (Guid.TryParse(idText, out var id))
        {
            var ok = await complete.ExecuteAsync(id, CancellationToken.None);
            Console.WriteLine(ok ? "完了にしたよ✅✨" : "そのid見つからなかった🥺");
        }
    }
    else if (cmd == "4")
    {
        var count = await notify.ExecuteAsync(TimeSpan.FromHours(24), CancellationToken.None);
        Console.WriteLine($"通知 {count} 件📣✨");
    }
}
```

🌟ポイント：**new はUI（組み立て場所）に集める**🏗️
他の層で `new JsonFile...` し始めると結合が上がって壊れやすいよ〜😱

---

## 4) 17C：最小テスト（まず1本でOK）🧪✨

## 4-1) 壊れやすいところ＝ルールを守るテスト🎯

![Testing Boundaries](./picture/hc_lc_cs_study_017_testing_boundaries.png)

今回は「期限通知」が壊れやすいので、そこを守るよ📣

```csharp
// TodoMini.Tests/NotifyDueSoonUseCaseTests.cs
using TodoMini.Application;
using TodoMini.Domain;
using Xunit;

public sealed class NotifyDueSoonUseCaseTests
{
    [Fact]
    public async Task DueSoon未完了だけ通知される()
    {
        var clock = new FakeClock(new DateTimeOffset(2026, 1, 12, 12, 0, 0, TimeSpan.FromHours(9)));

        var repo = new InMemoryRepo(new[]
        {
            TodoItem.CreateNew("近い🫣", clock.Now, clock.Now.AddHours(3)),
            TodoItem.CreateNew("遠い🙂", clock.Now, clock.Now.AddDays(3)),
            TodoItem.CreateNew("期限なし🙂", clock.Now, null),
        });

        var notifier = new FakeNotifier();
        var useCase = new NotifyDueSoonUseCase(repo, clock, notifier);

        var count = await useCase.ExecuteAsync(TimeSpan.FromHours(24), CancellationToken.None);

        Assert.Equal(1, count);
        Assert.Single(notifier.Messages);
        Assert.Contains("近い", notifier.Messages[0]);
    }

    private sealed class FakeClock : IClock
    {
        public FakeClock(DateTimeOffset now) => Now = now;
        public DateTimeOffset Now { get; }
    }

    private sealed class FakeNotifier : INotifier
    {
        public List<string> Messages { get; } = new();
        public Task NotifyAsync(string message, CancellationToken ct)
        {
            Messages.Add(message);
            return Task.CompletedTask;
        }
    }

    private sealed class InMemoryRepo : ITodoRepository
    {
        private readonly Dictionary<Guid, TodoItem> _store;

        public InMemoryRepo(IEnumerable<TodoItem> seed)
            => _store = seed.ToDictionary(x => x.Id, x => x);

        public Task<IReadOnlyList<TodoItem>> ListAsync(CancellationToken ct)
            => Task.FromResult((IReadOnlyList<TodoItem>)_store.Values.ToList());

        public Task<TodoItem?> FindAsync(Guid id, CancellationToken ct)
            => Task.FromResult(_store.TryGetValue(id, out var v) ? v : null);

        public Task UpsertAsync(TodoItem item, CancellationToken ct)
        {
            _store[item.Id] = item;
            return Task.CompletedTask;
        }
    }
}
```

🌟このテストが強い理由：

* JsonもConsoleも使ってない（＝速い＆安定）🚀
* 差し替えできる設計になってるかも同時にチェックできる🔌✨

---

## 5) 最終チェック（高凝集・低結合の自己採点）📋✨

## ✅ 高凝集チェック🏠

* Domainに「ルール」が集まってる？（タイトル必須、期限判定、完了）🎯
* Applicationは「手順（ユースケース）」だけ？🧭
* UIは「入出力」だけ？🖥️
* Infrastructureは「技術の都合」だけ？（Json/Console/時計）🧰

## ✅ 低結合チェック🔗

* Applicationが `Console.WriteLine` してない？（してたら混在🍲）
* Domainが `File` を触ってない？（触ってたら依存逆流💥）
* 差し替えしたいものが interface になってる？🔌

  * 時刻（`IClock`）
  * 通知（`INotifier`）
  * 保存（`ITodoRepository`）

---

## 6) AIプロンプト（この章は2つだけ🎀）🤖✨

1. 「この設計案に“責務混在”と“依存増えすぎ”がないか、危険点TOP5」🧠🔍
2. 「最小テスト1本で守るべき仕様（壊れやすい所）を提案して」🧪🎯

---

## 7) クリア後の“次の一歩”🌱✨

* 通知を `ConsoleNotifier` → `Windows Toast` 風に差し替え（INotifierを実装するだけ）📣🔁
* 保存を `JsonFile` → `SQLite` に差し替え（ITodoRepositoryを実装するだけ）💾🔁
* 期限判定を「休日は除外」みたいに進化（Domainの責務として追加）🗓️✨

---

[1]: https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-14 "What's new in C# 14 | Microsoft Learn"
[2]: https://devblogs.microsoft.com/visualstudio/visual-studio-2026-is-here-faster-smarter-and-a-hit-with-early-adopters/ "Visual Studio 2026 is here: faster, smarter, and a hit with early adopters - Visual Studio Blog"

