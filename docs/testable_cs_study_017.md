# 第17章：DBを境界にする（Repository入門）🗄️🚧✨

（ねらい：**DBの都合を、アプリの大事なロジックから遠ざける**💖）

---

## 17.1 まず、DB直アクセスが“しんどい理由”🐘💦

![testable_cs_study_017_direct_db_pain.png](./picture/testable_cs_study_017_direct_db_pain.png)

DBをロジックのど真ん中で直に叩くと…👇

* テストが遅い（DB起動・接続・初期化が重い）🐢
* テストが不安定（環境差・ネットワーク・同時実行で落ちる）🌪️
* “ロジックの正しさ”を見たいのに“DBの都合”で失敗する😵‍💫
* 変更に弱い（DBやORMの変更が、ロジックまで雪崩れる）🧊💥

だからここでも合言葉は同じ！
**I/O（DB）は外へ！ルールは中へ！** 📦➡️🌍✨

---

## 17.2 Repositoryってなに？（超ざっくり）🧩😊

![testable_cs_study_017_repository_window.png](./picture/testable_cs_study_017_repository_window.png)

Repositoryは一言でいうと…

> **「DB（外の世界）への出入口を、アプリ都合の形に整える“窓口”」** 🪟✨

ポイントはこれ👇

* ロジック側は **“DBがある/ない”を意識しない** 🙈
* ロジック側は **インターフェース（抽象）だけ知ってる** 🧩
* 本番はDB実装、テストはインメモリ実装に差し替え🔁🎭

そして、2026の今なら **.NET 10（LTS） + C# 14** が最新ラインで、C# 14は .NET 10 を前提にサポートされています。([Microsoft Learn][1])
EF Core も **EF Core 10（LTS）** が .NET 10 前提です。([Microsoft Learn][2])
さらに **Visual Studio 2026** も .NET 10 SDK を含む流れになっています。([Microsoft Learn][1])

---

## 17.3 最小サンプルで体験しよう🧪✨（ポイント付与アプリ🎁）

## 🎯やりたいこと（ルール）

* 会員にポイントを加算する
* **マイナス加算は禁止** ❌
* **1回の加算は最大 5000**（上限）🔒
* DBには「会員の現在ポイント」を保存する（これはI/O）🗄️

ここで大事なのは、**ルール部分はピュアにする**こと！🌿✨
DBは後でつなぐ！🔌

---

## 17.4 設計の形（これが“境界”）🚧😊


![testable_cs_study_017_repository_boundary.png](./picture/testable_cs_study_017_repository_boundary.png)

ざっくりこう分けます👇

* **内側（ルール）**：ポイント加算の判断・計算📦
* **境界（抽象）**：`IMemberRepository` 🧩
* **外側（I/O）**：EF Core / SQL / 実DB 🗄️🌍

---

## 17.5 まずは「ドメイン（ルール）」をピュアに書く🌿✨

![testable_cs_study_017_pure_domain_logic.png](./picture/testable_cs_study_017_pure_domain_logic.png)

```csharp
public sealed record MemberId(Guid Value);

public sealed class Member
{
    public MemberId Id { get; }
    public int Points { get; private set; }

    public Member(MemberId id, int points)
    {
        if (points < 0) throw new ArgumentOutOfRangeException(nameof(points));
        Id = id;
        Points = points;
    }

    public void AddPoints(int amount)
    {
        if (amount <= 0) throw new ArgumentOutOfRangeException(nameof(amount), "ポイントはプラスで！🙂");
        if (amount > 5000) throw new ArgumentOutOfRangeException(nameof(amount), "1回の上限オーバー！🚫");

        Points += amount;
    }
}
```

✅ここにはDBの気配ゼロ！最高！🎉
これだけでテストが超ラクになります💖

---

## 17.6 DBを境界にする：Repositoryインターフェース🧩🗄️


![testable_cs_study_017_repository_pattern.png](./picture/testable_cs_study_017_repository_pattern.png)

「会員を取り出す」「保存する」だけ、まずは最小でOK🙆‍♀️

```csharp
public interface IMemberRepository
{
    Member? FindById(MemberId id);
    void Save(Member member);
}
```

✨**ポイント**

* `DbContext` とか `IQueryable` とか **ORMの型を漏らさない** 🙅‍♀️
* **アプリが欲しい形**で操作できる窓口にする🪟

---

## 17.7 ユースケース（アプリの処理）でRepositoryを使う🧰✨

![testable_cs_study_017_usecase_flow.png](./picture/testable_cs_study_017_usecase_flow.png)

```csharp
public sealed class AddPointsUseCase
{
    private readonly IMemberRepository _repo;

    public AddPointsUseCase(IMemberRepository repo)
        => _repo = repo;

    public void Execute(MemberId memberId, int amount)
    {
        var member = _repo.FindById(memberId)
            ?? throw new InvalidOperationException("会員が見つからないよ😢");

        // ここが「ルールの中心」🎯
        member.AddPoints(amount);

        // 保存はI/Oだから、Repositoryへ✨
        _repo.Save(member);
    }
}
```

✅ユースケースは「やることの順番」を組み立てる場所🧩
✅ルールは `Member.AddPoints` に寄せてるからキレイ✨

---

## 17.8 テストでは“インメモリRepository”に差し替える🎭🧪

![testable_cs_study_017_test_double_swap.png](./picture/testable_cs_study_017_test_double_swap.png)

DBなしでテストできるのが、今日の勝ち筋！🏆✨

## Fake（それっぽく動く簡易実装🧸）

```csharp
public sealed class InMemoryMemberRepository : IMemberRepository
{
    private readonly Dictionary<Guid, Member> _store = new();

    public void Seed(Member member) => _store[member.Id.Value] = member;

    public Member? FindById(MemberId id)
        => _store.TryGetValue(id.Value, out var m) ? m : null;

    public void Save(Member member)
        => _store[member.Id.Value] = member;
}
```

## xUnitでユースケースをテスト🎉

```csharp
using Xunit;

public sealed class AddPointsUseCaseTests
{
    [Fact]
    public void ポイントが加算されて保存される()
    {
        var repo = new InMemoryMemberRepository();
        var id = new MemberId(Guid.NewGuid());
        repo.Seed(new Member(id, points: 100));

        var useCase = new AddPointsUseCase(repo);

        useCase.Execute(id, amount: 200);

        var updated = repo.FindById(id)!;
        Assert.Equal(300, updated.Points);
    }

    [Fact]
    public void マイナスはエラー()
    {
        var repo = new InMemoryMemberRepository();
        var id = new MemberId(Guid.NewGuid());
        repo.Seed(new Member(id, points: 100));
        var useCase = new AddPointsUseCase(repo);

        Assert.Throws<ArgumentOutOfRangeException>(() => useCase.Execute(id, amount: -1));
    }
}
```

🥳これで「DBが落ちた」とか「接続文字列が…」とか一切なし！
テストが速い！安定！気持ちいい！⚡💖

---

## 17.9 本番側：EF Core 10でRepositoryを実装する🗄️🔧

EF Core 10 は .NET 10 前提のLTSで、2025年11月リリース＆2028年までサポートの流れです。([Microsoft Learn][2])

## DbContext（外側）🧱

```csharp
using Microsoft.EntityFrameworkCore;

public sealed class AppDbContext : DbContext
{
    public DbSet<MemberRow> Members => Set<MemberRow>();

    public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) { }
}

public sealed class MemberRow
{
    public Guid Id { get; set; }
    public int Points { get; set; }
}
```

## Repository実装（外側）🧩➡️🗄️

```csharp
using Microsoft.EntityFrameworkCore;

public sealed class EfMemberRepository : IMemberRepository
{
    private readonly AppDbContext _db;

    public EfMemberRepository(AppDbContext db) => _db = db;

    public Member? FindById(MemberId id)
    {
        var row = _db.Members.SingleOrDefault(x => x.Id == id.Value);
        return row is null ? null : new Member(new MemberId(row.Id), row.Points);
    }

    public void Save(Member member)
    {
        var row = _db.Members.SingleOrDefault(x => x.Id == member.Id.Value);
        if (row is null)
        {
            row = new MemberRow { Id = member.Id.Value, Points = member.Points };
            _db.Members.Add(row);
        }
        else
        {
            row.Points = member.Points;
        }

        _db.SaveChanges();
    }
}
```

✅内側（ルール）には EF Core が一切入り込んでないのが重要！🚧✨

---

## 17.10 “組み立て”で本物を接続する🔌🏗️（Composition Rootの気配👀）

（第22章で本格的にやるけど、ここでも軽く！）

```csharp
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;

var services = new ServiceCollection();

services.AddDbContext<AppDbContext>(opt =>
    opt.UseSqlServer("ここに接続文字列🧵"));

services.AddScoped<IMemberRepository, EfMemberRepository>();
services.AddScoped<AddPointsUseCase>();

var provider = services.BuildServiceProvider();

var useCase = provider.GetRequiredService<AddPointsUseCase>();
useCase.Execute(new MemberId(Guid.NewGuid()), 100);
```

💡テストでは `IMemberRepository` を `InMemoryMemberRepository` にするだけでOK！🎭✨

---

## 17.11 Repositoryで“やりがち落とし穴”⚠️😵‍💫（先に踏み抜き回避！）

## ❌ 1) Repositoryが“なんでも屋”になる

![testable_cs_study_017_god_repository.png](./picture/testable_cs_study_017_god_repository.png)

`GetAll()` とか `SearchAny()` とか増やしすぎると地獄👻
➡️ **ユースケースが必要な操作だけ**を足すのが安全🙆‍♀️

## ❌ 2) `IQueryable` を返してしまう

![testable_cs_study_017_iqueryable_leak.png](./picture/testable_cs_study_017_iqueryable_leak.png)

内側がEFのクエリ仕様に依存しちゃう😢
➡️ **内側にORMの型を漏らさない**が鉄則🛡️

## ❌ 3) “Repository作ること”が目的になる

CRUDアプリ全部に無理やり入れると、逆に複雑💥
➡️ **「守りたい重要ロジックがある」時に強い**💎

---

## 17.12 AI（Copilot/Codex）活用のコツ🤖💡（Repository編）

そのまま使えるお願いテンプレ置いとくね！📝✨

* 「`IMemberRepository` に必要なメソッド候補を、ユースケースから逆算して提案して」
* 「インメモリ実装（Fake）を書いて。DictionaryでOK。スレッドセーフは不要」
* 「このユースケースのxUnitテストを AAA で作って。境界のFakeを使って」
* 「EF Core実装で “ORM型を内側に漏らさない” 変換方針になってるかレビューして」✅

⚠️ただしAIが `IQueryable` 返しがちなので、そこだけ人間が止めて！🚫🤣

---

## 17.13 章末ミニ演習✍️🎀（理解が定着するやつ！）

1. `Member.AddPoints` に「ポイント上限（例：合計 20000 まで）」を追加🔒
2. そのテストを追加（DBなしで）🧪
3. Repositoryに `FindById` が `null` の時の挙動をユースケースで整える（例外メッセージ改善）📝
4. 余裕あれば：`Save` を呼んだ回数を記録するMockっぽいFakeを作って検証👀✨

---

## 17.14 まとめ🎁✨

* DBはI/O！だから **ロジックの内側に入れない** 🚧
* Repositoryは **「抽象で守る」窓口** 🧩🛡️
* テストでは **インメモリ実装に差し替え**て爆速・安定🧪⚡
* EF Core 10（.NET 10前提）みたいな強い道具は **外側で使えばOK** 🗄️✨([Microsoft Learn][2])

---

次の章（第18章）は、この考え方を **HTTP/外部API** にも広げていくよ！🌐🚧✨
「外部は落ちる・遅い・変わる」あるあるを、同じ武器で倒しにいこうねっ💪😊💖

[1]: https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-14?utm_source=chatgpt.com "What's new in C# 14"
[2]: https://learn.microsoft.com/en-us/ef/core/what-is-new/ef-core-10.0/whatsnew?utm_source=chatgpt.com "What's New in EF Core 10"
