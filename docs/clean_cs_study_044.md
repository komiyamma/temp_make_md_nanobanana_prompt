# 第44章：UseCaseのテスト（Port差し替えで外部なし）🎭

## 📌 2026年1月時点の“最新テスト事情”だけ先にサクッと🥰

* いまの最新は **.NET 10（LTS）**で、2026/01/13 時点の最新リリースが **10.0.2** になってるよ📦✨ ([Microsoft][1])
* **Visual Studio 2026** は 2026/01/20 に **18.2.1** が出てるよ🧰✨ ([Microsoft Learn][2])
* `dotnet test` は **VSTest（既定）**と、.NET 10 SDK で入った **Microsoft Testing Platform（MTP）モード**の“2モード”が公式に整理されたよ🧪🔁 ([Microsoft Learn][3])
  （でも！この章では、まずは **いつものテンプレのまま（VSTest既定）**で全然OK👌 迷子にならないのが大事✨）

---

## この章でできるようになること🎯💖

* **DBなし / HTTPなし**で UseCase（Interactor）をテストできる🥳
* **Repository / Presenter を Fake に差し替え**て、UseCaseの手順だけ検証できる🔌🎭
* 「落ちるテスト」じゃなくて「仕様が読めるテスト」が書ける📖✨

---

## 1) UseCaseテストってどこを狙うの？🏹🎯

![Fakeで動かすUseCase (UseCase Testing)](./picture/clean_cs_study_044_usecase_testing.png)

UseCaseのテストは、気持ちとしては **“ほぼ単体テスト寄り”**だよ🫶
ポイントはこれ👇

* 単体テストは「**自分のコントロール下のコードだけ**をテストして、DB/ネットワークみたいなインフラ問題は含めない」って公式にも書かれてるのね✨ ([Microsoft Learn][4])
* クリーンアーキのUseCaseは、もともと **外部（DB/HTTP）を Port（interface）越しにする**から、差し替えが超やりやすい😳💡

つまり…
**Port差し替え = 外部を切っても UseCase の仕様は検証できる！** 🎉

---

## 2) 今日の主役：Fake / Stub / Spy を“ゆるく”覚える😆🧸

この章では難しい言葉をガチ暗記しなくてOK🙆‍♀️💕
ざっくりこう使うよ👇

* **Fake**：それっぽく動くニセ実装（インメモリRepositoryとか）🧪📦
* **Spy**：呼ばれたか・何が渡ったかを記録する子（Presenterでよく使う）🕵️‍♀️📝
* **Stub**：決まった値を返すだけ（Getで固定のMemo返すとか）🧷

---

## 3) テストプロジェクトの作り方（迷子ゼロ版）🧰✨

### ✅ 依存のルール（ここ超だいじ💗）

テストプロジェクトは基本こう👇

* 参照していい：**Entities / UseCases（Core側）** ✅
* 参照しない：**Web（ASP.NET） / EF Core / 外部API Adapter** ❌

これだけで「UseCaseテストが重くなる病」だいぶ防げるよ🥹✨

### ✅ 実行方法（2つ）

* Visual Studio：**テスト エクスプローラー**で実行▶️🧪
* CLI：`dotnet test` で実行🖥️🧪
  ※ `dotnet test` は VSTestが既定で、.NET 10からMTPモードもあるよ〜って整理が公式にあるよ📚 ([Microsoft Learn][3])
  （最初は既定のままでOK👌）

---

## 4) 例題：CreateMemo UseCase を “外部なし”で叩く🎮🧪

ここから **「Fake Repository」＋「Spy Presenter」**でやるよ🎭✨
（最小構成のサンプルだから、自分の実コードに合わせて読み替えてね🫶）

### 🧩 Core側（UseCaseとPort）イメージ

```csharp
// Port（出口）: 保存
public interface IMemoRepository
{
    Task AddAsync(Memo memo, CancellationToken ct);
    Task<Memo?> FindByIdAsync(Guid id, CancellationToken ct);
    Task UpdateAsync(Memo memo, CancellationToken ct);
}

// Port（出口）: 出力
public interface ICreateMemoOutputPort
{
    void Present(CreateMemoResponse response);
}

// 入力モデル
public sealed record CreateMemoRequest(string Title);

// 出力モデル（成功/失敗を“結果”で返す派）
public sealed record CreateMemoResponse(
    bool IsSuccess,
    Guid? MemoId,
    string? Title,
    string? ErrorCode,
    string? ErrorMessage
)
{
    public static CreateMemoResponse Success(Guid id, string title)
        => new(true, id, title, null, null);

    public static CreateMemoResponse Failure(string code, string message)
        => new(false, null, null, code, message);
}

// 例：Entity（最小）
public sealed class Memo
{
    public Guid Id { get; }
    public string Title { get; private set; }

    public Memo(Guid id, string title)
    {
        if (string.IsNullOrWhiteSpace(title))
            throw new ArgumentException("Title is required.", nameof(title));
        if (title.Length > 100)
            throw new ArgumentException("Title is too long.", nameof(title));

        Id = id;
        Title = title;
    }

    public void Rename(string newTitle)
    {
        if (string.IsNullOrWhiteSpace(newTitle))
            throw new ArgumentException("Title is required.", nameof(newTitle));
        if (newTitle.Length > 100)
            throw new ArgumentException("Title is too long.", nameof(newTitle));

        Title = newTitle;
    }
}

// ちょい工夫：ID生成も差し替えるとテストが安定💖
public interface IIdGenerator
{
    Guid NewGuid();
}

public sealed class SystemIdGenerator : IIdGenerator
{
    public Guid NewGuid() => Guid.NewGuid();
}

// UseCase（Interactor）
public sealed class CreateMemoInteractor
{
    private readonly IMemoRepository _repo;
    private readonly IIdGenerator _ids;
    private readonly ICreateMemoOutputPort _out;

    public CreateMemoInteractor(IMemoRepository repo, IIdGenerator ids, ICreateMemoOutputPort output)
    {
        _repo = repo;
        _ids = ids;
        _out = output;
    }

    public async Task HandleAsync(CreateMemoRequest request, CancellationToken ct)
    {
        try
        {
            var id = _ids.NewGuid();
            var memo = new Memo(id, request.Title);

            await _repo.AddAsync(memo, ct);

            _out.Present(CreateMemoResponse.Success(memo.Id, memo.Title));
        }
        catch (ArgumentException ex)
        {
            // ここは例：ドメイン/入力エラーを結果で返す
            _out.Present(CreateMemoResponse.Failure("ValidationError", ex.Message));
        }
    }
}
```

---

## 5) テスト側：Fake Repository と Spy Presenter を用意🎭🕵️‍♀️

### ✅ Fake Repository（インメモリ）

```csharp
public sealed class FakeMemoRepository : IMemoRepository
{
    private readonly Dictionary<Guid, Memo> _store = new();

    public int AddCallCount { get; private set; }
    public int UpdateCallCount { get; private set; }

    public Task AddAsync(Memo memo, CancellationToken ct)
    {
        AddCallCount++;
        _store.Add(memo.Id, memo);
        return Task.CompletedTask;
    }

    public Task<Memo?> FindByIdAsync(Guid id, CancellationToken ct)
    {
        _store.TryGetValue(id, out var memo);
        return Task.FromResult(memo);
    }

    public Task UpdateAsync(Memo memo, CancellationToken ct)
    {
        UpdateCallCount++;
        _store[memo.Id] = memo;
        return Task.CompletedTask;
    }
}
```

### ✅ Spy Presenter（呼ばれた内容を覚える）

```csharp
public sealed class SpyCreateMemoPresenter : ICreateMemoOutputPort
{
    public int PresentCallCount { get; private set; }
    public CreateMemoResponse? LastResponse { get; private set; }

    public void Present(CreateMemoResponse response)
    {
        PresentCallCount++;
        LastResponse = response;
    }
}
```

### ✅ Fixed ID Generator（テストを確定させる✨）

```csharp
public sealed class FixedIdGenerator : IIdGenerator
{
    private readonly Guid _fixed;
    public FixedIdGenerator(Guid fixedId) => _fixed = fixedId;
    public Guid NewGuid() => _fixed;
}
```

---

## 6) Given-When-Then でテストを書く（超読みやすい💖）🧁✨

### ✅ 成功ケース：タイトルOK → 保存されて、成功が出力される

```csharp
using Xunit;

public sealed class CreateMemoInteractorTests
{
    [Fact]
    public async Task Given_ValidTitle_When_HandleAsync_Then_SavesAndPresentsSuccess()
    {
        // Given 🎁
        var repo = new FakeMemoRepository();
        var presenter = new SpyCreateMemoPresenter();
        var fixedId = Guid.Parse("11111111-1111-1111-1111-111111111111");
        var ids = new FixedIdGenerator(fixedId);

        var sut = new CreateMemoInteractor(repo, ids, presenter);

        // When ⚡
        await sut.HandleAsync(new CreateMemoRequest("Hello Memo"), CancellationToken.None);

        // Then ✅
        Assert.Equal(1, repo.AddCallCount);
        Assert.Equal(1, presenter.PresentCallCount);

        Assert.NotNull(presenter.LastResponse);
        Assert.True(presenter.LastResponse!.IsSuccess);
        Assert.Equal(fixedId, presenter.LastResponse.MemoId);
        Assert.Equal("Hello Memo", presenter.LastResponse.Title);
    }
}
```

### ✅ 失敗ケース：タイトル空 → 保存されない＆失敗が出力される

```csharp
using Xunit;

public sealed partial class CreateMemoInteractorTests
{
    [Fact]
    public async Task Given_EmptyTitle_When_HandleAsync_Then_DoesNotSaveAndPresentsFailure()
    {
        // Given 🎁
        var repo = new FakeMemoRepository();
        var presenter = new SpyCreateMemoPresenter();
        var ids = new FixedIdGenerator(Guid.NewGuid());

        var sut = new CreateMemoInteractor(repo, ids, presenter);

        // When ⚡
        await sut.HandleAsync(new CreateMemoRequest("   "), CancellationToken.None);

        // Then ✅
        Assert.Equal(0, repo.AddCallCount);              // 保存されない
        Assert.Equal(1, presenter.PresentCallCount);     // 失敗が通知される

        Assert.NotNull(presenter.LastResponse);
        Assert.False(presenter.LastResponse!.IsSuccess);
        Assert.Equal("ValidationError", presenter.LastResponse.ErrorCode);
    }
}
```

> ね？💖 **DBもHTTPも一切いらない**のに、UseCaseの仕様がちゃんと確認できるでしょ🥳✨

---

## 7) UpdateMemo も同じノリでいけるよ✍️🧪（ミニ版）

「既存メモを取得 → Rename → Update → 成功出力」って流れをテストするだけ🎯

### 🧩 UseCase（最小サンプル）

```csharp
public interface IUpdateMemoOutputPort
{
    void Present(UpdateMemoResponse response);
}

public sealed record UpdateMemoRequest(Guid MemoId, string NewTitle);

public sealed record UpdateMemoResponse(
    bool IsSuccess,
    string? ErrorCode,
    string? ErrorMessage
)
{
    public static UpdateMemoResponse Success() => new(true, null, null);
    public static UpdateMemoResponse Failure(string code, string message) => new(false, code, message);
}

public sealed class UpdateMemoInteractor
{
    private readonly IMemoRepository _repo;
    private readonly IUpdateMemoOutputPort _out;

    public UpdateMemoInteractor(IMemoRepository repo, IUpdateMemoOutputPort output)
    {
        _repo = repo;
        _out = output;
    }

    public async Task HandleAsync(UpdateMemoRequest request, CancellationToken ct)
    {
        var memo = await _repo.FindByIdAsync(request.MemoId, ct);
        if (memo is null)
        {
            _out.Present(UpdateMemoResponse.Failure("NotFound", "Memo not found."));
            return;
        }

        try
        {
            memo.Rename(request.NewTitle);
            await _repo.UpdateAsync(memo, ct);
            _out.Present(UpdateMemoResponse.Success());
        }
        catch (ArgumentException ex)
        {
            _out.Present(UpdateMemoResponse.Failure("ValidationError", ex.Message));
        }
    }
}
```

### 🧪 テスト（成功）

```csharp
using Xunit;

public sealed class SpyUpdateMemoPresenter : IUpdateMemoOutputPort
{
    public UpdateMemoResponse? Last { get; private set; }
    public void Present(UpdateMemoResponse response) => Last = response;
}

public sealed class UpdateMemoInteractorTests
{
    [Fact]
    public async Task Given_ExistingMemo_When_Rename_Then_UpdatesAndSuccess()
    {
        // Given 🎁
        var repo = new FakeMemoRepository();
        var presenter = new SpyUpdateMemoPresenter();
        var sut = new UpdateMemoInteractor(repo, presenter);

        var id = Guid.Parse("22222222-2222-2222-2222-222222222222");
        await repo.AddAsync(new Memo(id, "Before"), CancellationToken.None);

        // When ⚡
        await sut.HandleAsync(new UpdateMemoRequest(id, "After"), CancellationToken.None);

        // Then ✅
        Assert.NotNull(presenter.Last);
        Assert.True(presenter.Last!.IsSuccess);
        Assert.Equal(1, repo.UpdateCallCount);
    }
}
```

---

## 8) “良いUseCaseテスト”のチェックリスト✅💖

* **DB/HTTP/ファイル/ネットワークがゼロ**🧼
* **テストが速い**（何十個でも一瞬）⚡
* **テスト名が仕様文**（Given-When-Thenで読める）📖
* **結果はPresenter/Responseで確認**（ログやConsoleに頼らない）🧠
* **ランダム要素（Guid/時刻）は差し替え**🧷（今回の `IIdGenerator` みたいに）

---

## 9) Copilot / Codex を使うなら（この章の“おいしい使い方”🤖🍰）

使いどころはここが最強💪✨

* Fake/Spy の雛形を一瞬で作らせる
* Given-When-Then のテストケースを列挙させる
* 境界値（0文字 / 1文字 / 100文字 / 101文字）を出させる

プロンプト例👇（そのまま投げてOK）

```text
CreateMemoInteractor のテストを書きたいです。
DB/HTTPなしで、FakeMemoRepository と SpyPresenter を使う前提で
Given-When-Then形式のテストケースを10個、境界値多めで提案して。
```

---

## まとめ🎀✨

第44章のコツはひとつだけ😊💖
**UseCaseは Port（interface）越しに外部と話す → だから Fake に差し替えてテストできる** 🎭🔌🧪

次の第45章で、この「依存ルール」を **自動で破れないようにする**（アーキテクチャテスト）に進むよ〜！🔒✅✨

[1]: https://dotnet.microsoft.com/en-us/download/dotnet "Browse all .NET versions to download | .NET"
[2]: https://learn.microsoft.com/en-us/visualstudio/releases/2026/release-notes "Visual Studio 2026 Release Notes | Microsoft Learn"
[3]: https://learn.microsoft.com/ja-jp/dotnet/core/testing/unit-testing-with-dotnet-test "'dotnet test' を使用したテスト - .NET | Microsoft Learn"
[4]: https://learn.microsoft.com/ja-jp/dotnet/core/testing/ ".NET でのテスト - .NET | Microsoft Learn"
