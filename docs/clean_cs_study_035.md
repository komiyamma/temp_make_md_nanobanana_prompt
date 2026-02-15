# 第35章：Queryの置き場所（検索/一覧の扱い）🔎

検索や一覧って、作りはじめは簡単なのに、気づくと **Controllerが肥大化**したり、**Repositoryが何でも屋**になったりしがち…😇
この章では「読み取り（Query）」を **速く・きれいに・境界を守って**育てる置き方を身につけるよ〜！💪💖

ちなみに本日時点の最新スタックは **.NET 10 / ASP.NET Core 10 / EF Core 10（LTS）**だよ🧁（2025/11/11 リリース）。([Microsoft for Developers][1])

---

## 1) 今日のゴール🎯✨

* ✅ 一覧/検索が増えても **クリーンアーキが崩れない**置き方がわかる
* ✅ 「読み取りは最適化してOK」を **どこまでOKにするか**言語化できる
* ✅ Repositoryが **巨大化しない**設計ができる
* ✅ EF Coreの読み取りを **速くする基本（NoTracking / Projection / Compiled Query）**がわかる([Microsoft Learn][2])

---

## 2) まず結論🌟（ここだけ覚えても勝てる）

![Queryの最適化戦略](./picture/clean_cs_study_035_query_optimization.png)

### 🔥 一覧/検索（Query）は、Domain Entityを無理に通さなくていい場面が多い

一覧画面ってだいたい **「表示用の軽い形」**が欲しいだけだよね？
だから、Queryはこんな方針が超強い💎

* UseCase側：**「こういう条件で、こういう形で返してね」**だけ決める（仕様）🧾
* Adapter側：**DBに近い最適化（JOIN、Projection、NoTracking、Index前提）**をやってOK🚀
* 返すもの：**Read Model（DTO/Projection）**でOK（Domain EntityじゃなくてOK）📦✨

### 🚫 ただし、境界違反はダメ🙅‍♀️

特にこれ👇は避けたい〜！

* `DbContext` を Controller から直叩き 😱
* Core側（UseCases/Entities）に EF Core の型が混ざる 😵
* Repositoryが `IQueryable` を外へ漏らす（ORMが染み出す）🫠
  ※Microsoftのガイドでも「Repositoryから `IQueryable` を返すのは推奨しない」って扱いだよ([Microsoft Learn][3])

---

## 3) よくある事故あるある🧨😂

### 事故A：Repositoryが「検索API全部入り」になる🍱

`SearchByKeywordAndTagAndDateAnd...` が増殖して地獄へ…👻
→ **Query専用の入口**を作って分離するとスッキリ✨

### 事故B：一覧のためにDomain Entityを大量ロードして重い🐢

一覧は「要約」だけでいいのに、Entity丸ごと＋関連読み込みでメモリが苦しい…🥲
→ **Projection（必要項目だけSelect）**が基本！([Microsoft Learn][4])

### 事故C：`IQueryable` を外に出して、UseCaseがEF依存😵‍💫

便利だけど、あとで **DB都合がUseCaseに侵食**して崩れやすい⚡
→ IQueryableは **Adapterの中で閉じる**のが安全🧼([Microsoft Learn][3])

---

## 4) Queryの置き場所：おすすめパターン3つ🧩✨

### パターン①：**Query UseCase + Query Gateway（おすすめ💯）**

* UseCaseに「検索仕様」を置く
* Core側に `IMemoSearchQuery` みたいな **Query用インターフェース**を置く
* 実装（EF Core）は Adapter側

👉 いちばんクリーンに伸びる🌱

### パターン②：Domain Repositoryで頑張る（ほどほどに）

* `GetById` や Aggregateの取得みたいに **ドメインルールのためにEntityが必要**ならOK
* でも一覧/検索まで全部Repositoryに押し込むと太りやすい😇

### パターン③：ガッツリCQRS（読みDB分離など）（将来の拡張）

* 将来、読み取りが爆伸びしたらアリ
* この教材では「まずは①」をしっかり固めよう💪

---

## 5) 例題：メモ検索（一覧）をクリーンに作ろう📝🔎

**欲しいUI**（例）

* キーワード検索
* タグ絞り込み
* アーカイブ除外
* 並び順（新しい順）
* ページング（20件ずつ）

ここでのコツ✨
👉 **Domainの `Memo` Entity** じゃなくて、一覧用の **`MemoSummary`（要約DTO）** を返す！

---

## 6) 実装：Core側（UseCases）に置くもの🧠📦

### ✅ Request / Response（UseCase用）

* API DTOとは分ける（第30章の話👏）

```csharp
public sealed record SearchMemosRequest(
    string? Keyword,
    string? Tag,
    bool IncludeArchived,
    int Page = 1,
    int PageSize = 20,
    string Sort = "createdDesc"
);

public sealed record MemoSummary(
    Guid Id,
    string Title,
    DateTimeOffset CreatedAt,
    bool IsArchived,
    string[] Tags
);

public sealed record PagedResult<T>(
    IReadOnlyList<T> Items,
    int Page,
    int PageSize,
    int TotalCount
);
```

### ✅ Query Gateway（Core側のインターフェース）

ポイント：**EFの型を一切出さない**🧼✨

```csharp
public interface IMemoSearchQuery
{
    Task<PagedResult<MemoSummary>> SearchAsync(
        SearchMemosRequest request,
        CancellationToken ct
    );
}
```

### ✅ Interactor（UseCaseの手順）

読み取りでも「仕様の中心」はUseCaseに置けるよ📌
（例：Pageは1以上に丸める、とか、Sortの許可リスト、とか）

```csharp
public sealed class SearchMemosInteractor
{
    private readonly IMemoSearchQuery _query;

    public SearchMemosInteractor(IMemoSearchQuery query)
        => _query = query;

    public Task<PagedResult<MemoSummary>> HandleAsync(
        SearchMemosRequest request,
        CancellationToken ct)
    {
        // ここで「検索の仕様」を守る（最低限の正規化）✨
        var normalized = request with
        {
            Page = request.Page < 1 ? 1 : request.Page,
            PageSize = request.PageSize is < 1 or > 200 ? 20 : request.PageSize
        };

        return _query.SearchAsync(normalized, ct);
    }
}
```

---

## 7) 実装：Adapter側（EF Core）に置くもの🗄️⚙️

ここは **最適化OKゾーン**🚀
ただし、Core側へ漏らさないでね🫶

### ✅ EF Coreの読み取り基本セット

* `AsNoTracking()`：読み取り専用なら速くなりやすい🏎️([Microsoft Learn][2])
* Projection（`Select`で必要項目だけ）：一覧の王道👑([Microsoft Learn][4])
* ページング：`Skip/Take`
* 並び順：許可したものだけ（安全✨）

```csharp
public sealed class EfMemoSearchQuery : IMemoSearchQuery
{
    private readonly AppDbContext _db;

    public EfMemoSearchQuery(AppDbContext db) => _db = db;

    public async Task<PagedResult<MemoSummary>> SearchAsync(
        SearchMemosRequest request,
        CancellationToken ct)
    {
        var q = _db.Memos
            .AsNoTracking() // 追跡しない（読み取り高速化）✨
            .AsQueryable();

        if (!request.IncludeArchived)
            q = q.Where(x => !x.IsArchived);

        if (!string.IsNullOrWhiteSpace(request.Keyword))
        {
            var kw = request.Keyword.Trim();
            q = q.Where(x => x.Title.Contains(kw));
        }

        if (!string.IsNullOrWhiteSpace(request.Tag))
        {
            var tag = request.Tag.Trim();
            q = q.Where(x => x.Tags.Any(t => t.Name == tag));
        }

        // TotalCount は先に（ページング前）数える
        var total = await q.CountAsync(ct);

        // Sort（許可リスト方式が安全）🛡️
        q = request.Sort switch
        {
            "createdAsc"  => q.OrderBy(x => x.CreatedAt),
            "createdDesc" => q.OrderByDescending(x => x.CreatedAt),
            _             => q.OrderByDescending(x => x.CreatedAt)
        };

        var skip = (request.Page - 1) * request.PageSize;

        // 一覧は Entity 丸ごとじゃなく「要約DTO」に投影するのがコツ👑
        var items = await q
            .Skip(skip)
            .Take(request.PageSize)
            .Select(x => new MemoSummary(
                x.Id,
                x.Title,
                x.CreatedAt,
                x.IsArchived,
                x.Tags.Select(t => t.Name).ToArray()
            ))
            .ToListAsync(ct);

        return new PagedResult<MemoSummary>(items, request.Page, request.PageSize, total);
    }
}
```

### 💡 もっと速くしたい時：Compiled Query（ホットパス向け）🔥

同じ形のクエリを何度も叩くなら、EF Coreの **Compiled Query** が効くことがあるよ🚀([Microsoft Learn][5])
（ただし、動的な条件が多すぎると作りづらいので「定番クエリ」に使うのがコツ🧁）

---

## 8) エンドポイント側（Controller / Minimal API）は薄く🍃

**Controllerの責務は “受け取って呼ぶだけ”**（第29章）だよね😊

```csharp
app.MapGet("/memos/search", async (
    [AsParameters] SearchMemosRequest request,
    SearchMemosInteractor interactor,
    CancellationToken ct) =>
{
    var result = await interactor.HandleAsync(request, ct);
    return Results.Ok(result);
});
```

### 🌟 さらに：Output Caching（安全なGETなら効く）🍪

検索条件が同じならレスポンスをキャッシュして速くできるよ✨（要件とデータ鮮度に注意！）([Microsoft Learn][6])

---

## 9) テスト方針（QueryはFakeでOK）🧪🎭

Queryは **interface** だから、UseCaseテストは超ラク！

* `IMemoSearchQuery` を Fake 実装して
* `SearchMemosInteractor` が「仕様（Page丸め等）」を守ってるかだけテスト✅

```csharp
public sealed class FakeMemoSearchQuery : IMemoSearchQuery
{
    public Task<PagedResult<MemoSummary>> SearchAsync(SearchMemosRequest request, CancellationToken ct)
    {
        var items = new List<MemoSummary>
        {
            new(Guid.NewGuid(), "Hello", DateTimeOffset.UtcNow, false, new[] { "tag1" })
        };
        return Task.FromResult(new PagedResult<MemoSummary>(items, request.Page, request.PageSize, totalCount: 1));
    }
}
```

---

## 10) AI（Copilot/Codex）を使うなら、こう頼むと綺麗に出るよ🤖💞

### 便利プロンプト例（そのままコピペOK）✨

* 「UseCases層に `SearchMemosRequest`, `MemoSummary`, `PagedResult<T>` を `record` で作って。EF Core型は禁止。」
* 「`IMemoSearchQuery` を定義して、InteractorでPage/PageSizeを正規化してから呼ぶ形にして。」
* 「Adapter側で `AsNoTracking` + `Select` projection + paging を使った EF Core 実装を書いて。`IQueryable` を外へ返さないで。」

AIが出したコードは、最後にあなたが **“境界（依存）”チェック**して確定すると最強だよ💪✨

---

## 11) 章末チェックリスト✅🔍

* [ ] Core側（Entities/UseCases）に **EF Coreの型が1つも出てない**
* [ ] Queryは **Read Model（DTO/Projection）**を返してる（Entity丸ごとじゃない）
* [ ] `DbContext` は **Adapterの中に閉じてる**
* [ ] Repositoryが「検索全部入り」になってない（Query Gatewayに分離できてる）
* [ ] 一覧は `AsNoTracking` + Projection が基本になってる([Microsoft Learn][2])
* [ ] 「Repositoryから `IQueryable` を返してない」方針で統一できてる([Microsoft Learn][3])

---

次の章（第36章）では、この考え方をそのまま **外部サービス呼び出し（HTTP等）**にも広げて、「変更に強い外部連携」を作っていくよ〜🌍🔌✨

[1]: https://devblogs.microsoft.com/dotnet/announcing-dotnet-10/?utm_source=chatgpt.com "Announcing .NET 10"
[2]: https://learn.microsoft.com/ja-jp/ef/core/querying/tracking?utm_source=chatgpt.com "追跡クエリと No-Tracking クエリ - EF Core"
[3]: https://learn.microsoft.com/en-us/dotnet/architecture/microservices/microservice-ddd-cqrs-patterns/infrastructure-persistence-layer-implementation-entity-framework-core?utm_source=chatgpt.com "Implementing the infrastructure persistence layer with ..."
[4]: https://learn.microsoft.com/en-us/ef/core/performance/efficient-querying?utm_source=chatgpt.com "Efficient Querying - EF Core"
[5]: https://learn.microsoft.com/en-us/ef/core/performance/advanced-performance-topics?utm_source=chatgpt.com "Advanced Performance Topics - EF Core"
[6]: https://learn.microsoft.com/en-us/aspnet/core/performance/caching/output?view=aspnetcore-10.0&utm_source=chatgpt.com "Output caching middleware in ASP.NET Core"
