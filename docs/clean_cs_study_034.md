# 第34章：DBモデルとDomainモデルは分けてOK（変換で吸収）🔁

この章は「**DomainをDB都合に合わせない**」ための超重要テクだよ〜！✨
いまの最新前提だと **.NET 10（LTS）＋ C# 14 ＋ EF Core 10** が現行ど真ん中🧡（2026-01-22時点）([Microsoft][1])

---

## 1) 今日のゴール🎯✨

* ✅ **Domainモデル**（業務ルール・不変条件・ふるまい）をキレイに保つ💎
* ✅ **DBモデル**（テーブル形状・外部キー・NULL・INDEXなどの都合）を外側に閉じ込める🗄️
* ✅ その間を **マッピング（変換）** で吸収できるようになる🔁

---

## 2) なぜ「分ける」って話が出るの？😵‍💫➡️😍

DBは現実的にこういう都合が出がち👇

* `NULL` が混ざる（でもDomainは「NULL禁止」で守りたい）😇💥
* 列名・型・長さ・正規化・外部キー…「保存の事情」が多い🗃️
* EFの都合（追跡、遅延ロード、ナビゲーションなど）をDomainに持ち込みたくない🙅‍♀️

だから、**DomainはDomainの言葉で**作って、
**DBの事情は永続化側（外側）で吸収**しようね、って流れ✨

Microsoftのガイドでも「EF Coreは永続化層でマッピングして、Domainを“汚染”しない」方向が推されてるよ🫶([Microsoft Learn][2])

---

## 3) 2つのモデルの役割をハッキリさせよ〜🧠✨

![Domain Model vs DB Model](./picture/clean_cs_study_034_db_mapping.png)

### 💎 Domainモデル（Core側）

* 目的：**業務ルールを守る**
* 特徴：

  * 不変条件（例：タイトル空禁止）🚧
  * ふるまい（例：Archiveする）🎬
  * VO（Value Object）で「string地獄」回避💍

### 🗄️ DBモデル（Persistence/EF側）

* 目的：**DBに正しく保存・復元する**
* 特徴：

  * `Guid` / `string` / `int` などDB向きの型
  * 外部キー・ナビゲーション・列制約
  * `NULL` 許可、既定値、ConcurrencyToken…など保存都合

---

## 4) いつ「分ける」べき？分けないでもOK？🤔✨

### ✅ 分けると強いケース💪

* Domainに **VOや不変条件が多い**（ちゃんと設計したい）💎
* DB側が複雑（JOIN多い、履歴、監査列、Nullable多い）🗄️
* EFの都合をDomainに一切入れたくない（純度命）🧼✨

### ✅ 分けなくてもいいケース🙂

* ほぼCRUDで、Domainのルールが薄い
* 早く作って検証したいプロトタイプ
* EF CoreのマッピングでDomainを汚さずいける設計にできる

※ EF Coreは **Fluent APIでDomainモデルを汚さずにマップできる**考え方も用意されてるよ🫶([Microsoft Learn][2])
この章は「分ける」パターンをがっつり練習するね！🔁✨

---

## 5) 置き場所（クリーンアーキ的にどこに置く？）🧭🧡

* **Core（Entities）**：Domain（Entity/VO/ルール）💎
* **Core（UseCases）**：Repositoryの`interface`（出口）🚪
* **Adapters（Persistence）**：EF CoreのDbContext、DBモデル、Repository実装、Mapper 🔁
* **Frameworks**：接続文字列、Migration、EF設定など🧰

---

## 6) 実装例：Memoで「分離＋マッピング」やってみよ〜✍️🗒️✨

### 6-1) Domain側（Core/Entities）💎

```csharp
namespace Core.Entities;

public readonly record struct MemoId(Guid Value);

public sealed class MemoTitle
{
    public const int MaxLength = 100;
    public string Value { get; }

    public MemoTitle(string value)
    {
        value = (value ?? "").Trim();
        if (value.Length == 0) throw new ArgumentException("タイトルは必須だよ🥺");
        if (value.Length > MaxLength) throw new ArgumentException($"タイトル長すぎ！最大{MaxLength}文字だよ🥺");
        Value = value;
    }

    public override string ToString() => Value;
}

public sealed class Memo
{
    public MemoId Id { get; }
    public MemoTitle Title { get; private set; }
    public bool IsArchived { get; private set; }
    public DateTimeOffset CreatedAtUtc { get; }

    private Memo(MemoId id, MemoTitle title, bool isArchived, DateTimeOffset createdAtUtc)
    {
        Id = id;
        Title = title;
        IsArchived = isArchived;
        CreatedAtUtc = createdAtUtc;
    }

    public static Memo CreateNew(MemoTitle title, DateTimeOffset nowUtc)
        => new(new MemoId(Guid.NewGuid()), title, isArchived: false, createdAtUtc: nowUtc);

    // DBから復元するとき用（Rehydrateパターン）🧟‍♀️✨
    public static Memo Rehydrate(MemoId id, MemoTitle title, bool isArchived, DateTimeOffset createdAtUtc)
        => new(id, title, isArchived, createdAtUtc);

    public void Rename(MemoTitle newTitle) => Title = newTitle;

    public void Archive() => IsArchived = true;
}
```

ポイント🎀

* Domainは **DB列名もEF属性も知らない**🧼
* DB復元用に `Rehydrate` を用意して、生成と復元を分けてるよ✨

---

### 6-2) Repository interface（Core/UseCases側に置く）🚪

```csharp
using Core.Entities;

namespace Core.UseCases.Ports;

public interface IMemoRepository
{
    Task<Memo?> FindByIdAsync(MemoId id, CancellationToken ct);
    Task SaveAsync(Memo memo, CancellationToken ct);
}
```

---

### 6-3) DBモデル（Adapters/Persistence側）🗄️

```csharp
namespace Adapters.Persistence.Ef.Models;

// 「DBに保存する形」だけを表すクラス🗄️
internal sealed class MemoRow
{
    public Guid Id { get; set; }
    public string Title { get; set; } = "";
    public bool IsArchived { get; set; }
    public DateTimeOffset CreatedAtUtc { get; set; }
}
```

---

### 6-4) DbContext（Adapters/Persistence側）🧰✨

```csharp
using Adapters.Persistence.Ef.Models;
using Microsoft.EntityFrameworkCore;

namespace Adapters.Persistence.Ef;

internal sealed class AppDbContext : DbContext
{
    public DbSet<MemoRow> Memos => Set<MemoRow>();

    public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) { }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        var b = modelBuilder.Entity<MemoRow>();
        b.ToTable("Memos");
        b.HasKey(x => x.Id);

        b.Property(x => x.Title)
            .HasMaxLength(100)
            .IsRequired();

        b.Property(x => x.CreatedAtUtc)
            .IsRequired();
    }
}
```

---

### 6-5) Mapper（ここが本章の主役）🔁🌟

```csharp
using Adapters.Persistence.Ef.Models;
using Core.Entities;

namespace Adapters.Persistence.Ef.Mapping;

internal static class MemoMapper
{
    public static MemoRow ToRow(Memo domain)
        => new()
        {
            Id = domain.Id.Value,
            Title = domain.Title.Value,
            IsArchived = domain.IsArchived,
            CreatedAtUtc = domain.CreatedAtUtc
        };

    public static Memo ToDomain(MemoRow row)
        => Memo.Rehydrate(
            new MemoId(row.Id),
            new MemoTitle(row.Title),
            row.IsArchived,
            row.CreatedAtUtc
        );
}
```

ここ大事〜〜❣️

* “変換” を **1か所に集める** と、あとで仕様が変わっても壊れにくいよ🔁✨

---

### 6-6) Repository実装（EF Coreを使うのは外側だけ）🧩🗄️

```csharp
using Adapters.Persistence.Ef.Mapping;
using Microsoft.EntityFrameworkCore;
using Core.Entities;
using Core.UseCases.Ports;

namespace Adapters.Persistence.Ef;

internal sealed class EfMemoRepository : IMemoRepository
{
    private readonly AppDbContext _db;

    public EfMemoRepository(AppDbContext db) => _db = db;

    public async Task<Memo?> FindByIdAsync(MemoId id, CancellationToken ct)
    {
        var row = await _db.Memos.AsNoTracking()
            .SingleOrDefaultAsync(x => x.Id == id.Value, ct);

        return row is null ? null : MemoMapper.ToDomain(row);
    }

    public async Task SaveAsync(Memo memo, CancellationToken ct)
    {
        // Upsertっぽく保存（学習用にシンプル）
        var existing = await _db.Memos.SingleOrDefaultAsync(x => x.Id == memo.Id.Value, ct);

        if (existing is null)
        {
            _db.Memos.Add(MemoMapper.ToRow(memo));
        }
        else
        {
            existing.Title = memo.Title.Value;
            existing.IsArchived = memo.IsArchived;
            // CreatedAtUtcは不変、更新しない方針✨
        }

        await _db.SaveChangesAsync(ct);
    }
}
```

---

## 7) マッピングの地雷💣あるある集（超大事）😱➡️😌

### 💣 地雷1：IDの生成場所がブレる

* Domainで作る？DBで作る？が混ざると地獄👹
  おすすめ：**Domainで生成**（ルールが明確）✨

### 💣 地雷2：UTC/ローカル時刻混在

* 保存は基本 **UTC** に寄せるのが安全🙆‍♀️
  （表示はPresenter/外側でローカルへ）🕒

### 💣 地雷3：NULLとDomain不変条件の衝突

* DBにNULLが入ったら `new MemoTitle(row.Title)` が例外で落ちる💥
  対策：
* DB制約でNULLを防ぐ
* それでも怖いなら「不正データ検知→隔離ログ」みたいな方針を決める🧯

### 💣 地雷4：既定値がDomainとズレる

* DBの既定値（DEFAULT）とDomainの既定値がズレると事故る💥
  対策：**既定値はなるべくDomainで確定**して保存する✨

---

## 8) さらに上級：VOは「値変換」でも扱えるよ🪄（分けないルート）

「DomainをそのままEFでマップ」したい場合は、**Value Converter** が便利✨
EFの公式でも「DBとの読み書き時に値を変換できる」って説明されてるよ📚([Microsoft Learn][3])

イメージ👇（※この章のメインは“分ける”だから、参考としてね）

```csharp
// 例：MemoTitle を string に変換して保存する
builder.Property(x => x.Title)
    .HasConversion(
        v => v.Value,
        v => new MemoTitle(v)
    );
```

あと、複数カラムをまとめたいときは **Owned Entity Types** って仕組みもあるよ〜🧩([Microsoft Learn][4])

---

## 9) テストで守ると安心🧪💖（マッピングテスト）

「変換が壊れてない？」を自動で見れると最強✨

```csharp
using Core.Entities;
using Adapters.Persistence.Ef.Mapping;
using Xunit;

public class MemoMappingTests
{
    [Fact]
    public void RoundTrip_Domain_to_Row_to_Domain_keeps_data()
    {
        var now = DateTimeOffset.UtcNow;
        var memo = Memo.CreateNew(new MemoTitle("テストだよ〜💖"), now);

        var row = MemoMapper.ToRow(memo);
        var restored = MemoMapper.ToDomain(row);

        Assert.Equal(memo.Id, restored.Id);
        Assert.Equal(memo.Title.Value, restored.Title.Value);
        Assert.Equal(memo.IsArchived, restored.IsArchived);
        Assert.Equal(memo.CreatedAtUtc, restored.CreatedAtUtc);
    }
}
```

---

## 10) ミニ課題✍️✨（手を動かすやつ）

### 課題A：列追加に強くなる💪

1. Domainに `LastUpdatedAtUtc` を追加🕒
2. DBモデル（MemoRow）に列追加
3. MapperとRepositoryを更新
4. マッピングテストも更新✅

### 課題B：バグ仕込み→検出ゲーム🎮

* わざと `Title` のマッピングを `Trim()` し忘れる
* テストで落ちるのを確認する😆

---

## 11) Copilot / Codex に頼るコツ🤖💬✨

### ✅ 使える指示例（そのまま貼ってOK）

* 「`Memo` と `MemoRow` の相互変換メソッドを作って。NULLや既定値の注意点もコメントで入れて」
* 「マッピングのround-tripテスト（xUnit）を書いて。比較すべき項目を列挙して」
* 「このRepositoryのUpsertをもう少し安全にして。CreatedAtは不変で」

### ⚠️ ただし注意！

AIが作ったMapperって、**項目の追加時に漏れ**やすいの🥺
だから

* ✅ “Mapperだけのテスト” を置く
* ✅ 追加したプロパティは **Domain→DB→Domain** で必ず検査
  これでかなり事故減るよ〜🧪💖

---

## まとめ🎀✨

* Domainは💎、DBは🗄️。役割が違う！
* 分けたら **Mapper（変換）** が生命線🔁
* 地雷（NULL/既定値/UTC/ID）を最初から潰す💣➡️✅
* テストで“変換の破綻”を自動検出🧪✨

次（第35章）は「検索/一覧（Query）をどこに置く？」で、読み取り最適化がテーマになるよ〜🔎💖

[1]: https://dotnet.microsoft.com/en-us/platform/support/policy/dotnet-core?utm_source=chatgpt.com "NET and .NET Core official support policy"
[2]: https://learn.microsoft.com/en-us/dotnet/architecture/microservices/microservice-ddd-cqrs-patterns/infrastructure-persistence-layer-implementation-entity-framework-core?utm_source=chatgpt.com "Implementing the infrastructure persistence layer with ..."
[3]: https://learn.microsoft.com/en-us/ef/core/modeling/value-conversions?utm_source=chatgpt.com "Value Conversions - EF Core"
[4]: https://learn.microsoft.com/en-us/ef/core/modeling/owned-entities?utm_source=chatgpt.com "Owned Entity Types - EF Core"
