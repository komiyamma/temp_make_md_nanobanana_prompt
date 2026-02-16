# 第27章：UseCaseを増やしても崩れない“型”を作る📐

今まで作ってきた **InputPort / Interactor / OutputPort / Presenter / Repository** の流れ、1個なら作れるけど……
ユースケースが増えてくると、だんだんこうなりがち👇😵‍💫

* 「毎回ファイル配置がバラバラ」📁💥
* 「命名が揺れる（Createなの？Addなの？）」🤯
* 「Interactorが肥大化して “なんでも屋” になる」🧟‍♂️
* 「Controller/Presenterが混ざって境界が溶ける」🫠

この章は、それを防ぐために **“増やしても崩れない型（テンプレ）”** を作ります💪💖
しかも、AI（Copilot / Codex系）に **雛形生成を手伝わせやすい形** にします🤖🪄

※2026年1月時点の最新として、.NET 10（LTS, 2025年11月リリース）＆C# 14 前提で書いてるよ📌✨ ([Microsoft Dev Blogs][1])

---

## 1) この章のゴール🎯💞

![Chaos vs Order in Expansion](./picture/clean_cs_study_027_chaos_vs_order.png)

ユースケースを追加するとき、毎回「悩む」をゼロに近づける✨

* ✅ 置き場所が一瞬で決まる（フォルダ構成が固定）📦
* ✅ クラス名が迷わない（命名規則が固定）🏷️
* ✅ Interactorの責務が膨らまない（やることが固定）🧱
* ✅ 依存ルールが自然に守られる（型が境界を守る）🛡️

---

## 2) “型”の全体図（これを毎回コピペ脳で作る🧠📋）

![UseCase Kit](./picture/clean_cs_study_027_usecase_kit.png)

ユースケース1つにつき、**この6点セット**を作るのが型です👇✨

1. **Request**（入力データ）📨
2. **InputPort**（入口インターフェース）🔌⬅️
3. **Interactor**（手順の本体）🧱
4. **Response**（出力データ）📦
5. **OutputPort**（出口インターフェース）🔌➡️
6. **Presenter**（外側向けに整形）🎤
   ＋（必要なら）**Repository/Gateway interface**（外部I/Oの出口）🚪

「Dependency Rule：依存は内側へ」って話の、まさに実戦版だね⭕➡️ ([blog.cleancoder.com][2])

---

## 3) 迷わないフォルダ構成（Featureフォルダ方式）📁✨

![Featureフォルダ構成](./picture/clean_cs_study_027_feature_folders.png)

**“ユースケース名でフォルダを切る”** のがいちばん迷子になりにくいです😊💕

例：メモアプリで `CreateMemo` を作るなら👇

* `UseCases/Memos/CreateMemo/`

  * `CreateMemoRequest.cs`
  * `ICreateMemoInputPort.cs`
  * `CreateMemoInteractor.cs`
  * `CreateMemoResponse.cs`
  * `ICreateMemoOutputPort.cs`

Presenterはアダプタ層に置くので👇

* `Adapters/Presenters/Memos/CreateMemoPresenter.cs`

この時点で **「どこに何置く？」が消えます**🫶✨

---

## 4) “結果の形”を統一して、毎回の悩みを消す🍱✨

![Result Pattern Output](./picture/clean_cs_study_027_result_pattern.png)

ユースケースごとに
「成功はこれ、失敗は例外？エラー？戻り値？」って揺れると崩れます💥

そこでこの章では、出力を **Result型で統一**しちゃいます✌️😆

* 成功：`Result.Ok(value)` 🎉
* 失敗：`Result.Fail(code, message)` ⚠️

### 共通のResult（UseCasesに1回だけ作る）🧩

```csharp
namespace CleanMemo.UseCases.Abstractions;

public sealed record Error(string Code, string Message);

public readonly record struct Result<T>(T? Value, Error? Error)
{
    public bool IsSuccess => Error is null;

    public static Result<T> Ok(T value) => new(value, null);

    public static Result<T> Fail(string code, string message)
        => new(default, new Error(code, message));
}
```

---

## 5) “型”の雛形（CreateMemoで完成形を見せるよ✨）🧱💕

ここから **コピペして名前だけ変える**のが正解です😆🫶

### (1) Request（入力）📨

```csharp
namespace CleanMemo.UseCases.Memos.CreateMemo;

public sealed record CreateMemoRequest(
    string Title,
    string Body
);
```

### (2) InputPort（入口）🔌⬅️

```csharp
namespace CleanMemo.UseCases.Memos.CreateMemo;

public interface ICreateMemoInputPort
{
    Task HandleAsync(CreateMemoRequest request, CancellationToken ct = default);
}
```

### (3) Response（出力の中身）📦

```csharp
namespace CleanMemo.UseCases.Memos.CreateMemo;

public sealed record CreateMemoResponse(
    Guid MemoId
);
```

### (4) OutputPort（出口）🔌➡️

※出力は **Resultで統一**✨

```csharp
using CleanMemo.UseCases.Abstractions;

namespace CleanMemo.UseCases.Memos.CreateMemo;

public interface ICreateMemoOutputPort
{
    Task PresentAsync(Result<CreateMemoResponse> result, CancellationToken ct = default);
}
```

### (5) Interactor（本体）🧱

※Interactorは「手順」だけ。HTTPもDBも知らない🙂‍↔️✨

```csharp
using CleanMemo.UseCases.Abstractions;

namespace CleanMemo.UseCases.Memos.CreateMemo;

public sealed class CreateMemoInteractor : ICreateMemoInputPort
{
    private readonly IMemoRepository _repo;
    private readonly ICreateMemoOutputPort _output;

    public CreateMemoInteractor(IMemoRepository repo, ICreateMemoOutputPort output)
    {
        _repo = repo;
        _output = output;
    }

    public async Task HandleAsync(CreateMemoRequest request, CancellationToken ct = default)
    {
        // 1) 入力を使ってドメインを作る（例：Memoエンティティの生成）
        //    ※ここでは雛形として最小にしてるよ
        if (string.IsNullOrWhiteSpace(request.Title))
        {
            await _output.PresentAsync(
                Result<CreateMemoResponse>.Fail("Validation.TitleEmpty", "タイトルが空っぽだよ🥺"),
                ct
            );
            return;
        }

        var newId = Guid.NewGuid();

        // 2) 保存（外部I/Oは Repository に任せる）
        await _repo.AddAsync(newId, request.Title, request.Body, ct);

        // 3) 出力
        await _output.PresentAsync(
            Result<CreateMemoResponse>.Ok(new CreateMemoResponse(newId)),
            ct
        );
    }
}
```

### (6) Repository（外部I/Oの出口）🚪

※「UseCaseが必要な操作だけ」を置くのがコツ✂️✨

```csharp
namespace CleanMemo.UseCases;

public interface IMemoRepository
{
    Task AddAsync(Guid id, string title, string body, CancellationToken ct = default);
    Task<bool> ExistsAsync(Guid id, CancellationToken ct = default);
    Task UpdateTitleAsync(Guid id, string title, CancellationToken ct = default);
    Task ArchiveAsync(Guid id, CancellationToken ct = default);
}
```

---

## 6) Presenter（Adapter側）🎤✨（超重要！）

![Presenter Plug](./picture/clean_cs_study_027_presenter_plug.png)

Presenterは **OutputPortを実装**して、外側（APIレスポンス等）に変換します🔄

```csharp
using CleanMemo.UseCases.Abstractions;
using CleanMemo.UseCases.Memos.CreateMemo;

namespace CleanMemo.Adapters.Presenters.Memos;

public sealed class CreateMemoPresenter : ICreateMemoOutputPort
{
    // Controllerが取り出せるように保持する（例）
    public object? ViewModel { get; private set; }

    public Task PresentAsync(Result<CreateMemoResponse> result, CancellationToken ct = default)
    {
        ViewModel = result.IsSuccess
            ? new { ok = true, memoId = result.Value!.MemoId }
            : new { ok = false, error = result.Error!.Code, message = result.Error!.Message };

        return Task.CompletedTask;
    }
}
```

ここまでが「型」👏🥰
**この型を守る限り、ユースケースが増えても構造が崩れにくい**です🛡️✨

---

## 7) ミニ課題：テンプレで2ユースケース追加しよう🎮💕

### 課題A：UpdateMemoTitle（タイトル変更）✍️

* Request：`MemoId, NewTitle`
* Response：`MemoId`
* 失敗例：Memoが存在しない / タイトルが空

### 課題B：ArchiveMemo（アーカイブ）🗃️

* Request：`MemoId`
* Response：`MemoId`
* 失敗例：Memoが存在しない

作り方は同じです😆✨
フォルダだけ増やして、名前を置換して、中身の手順だけ書く！

---

## 8) AI（Copilot/Codex）に雛形を作らせるコツ🤖🪄

![AI Blueprint Generation](./picture/clean_cs_study_027_ai_blueprint.png)

AIに投げるときは「型」をそのまま指示すると事故が減ります👍💕

### おすすめプロンプト例💬✨

* 「`UpdateMemoTitle` をこの構造で生成して：Request/InputPort/Interactor/Response/OutputPort。出力は `Result<T>` で統一。UseCases層にASP.NET型やEF型を絶対に入れないこと。」
* 「Interactorは Repository と OutputPort だけに依存。ControllerやIActionResultは禁止。」

### AIがやりがちな事故あるある🚨

* ❌ Interactorが `IActionResult` を返す
* ❌ UseCases内で `Microsoft.AspNetCore.*` を参照しちゃう
* ❌ EF Coreの `DbContext` を直に触る
* ❌ RequestにAPI DTOをそのまま流し込む

このへんは **Dependency Rule**違反になりやすいので要注意だよ🙂‍↔️🛡️ ([blog.cleancoder.com][2])

---

## 9) “型が崩れてない？”チェックリスト✅✨

![Dependency Scanner Check](./picture/clean_cs_study_027_dependency_scanner.png)

ユースケースを追加したら、これだけ見てね👀💕

* ✅ UseCasesプロジェクトが **ASP.NET / EF Core** を参照してない
* ✅ Interactorの依存は **Repository + OutputPort + Domain** だけ
* ✅ 変換（DTO↔Request、Response↔DTO）は **Adapter側**にある
* ✅ 例外でドーンじゃなく、`Result.Fail()` に落としている

---

## まとめ🎀✨

この章のポイントはこれだけ👇💖

* ユースケース追加が辛くなる原因は **“毎回の揺れ”**😵‍💫
* 揺れを消すには **型（テンプレ）を固定**する📐
* 出力は **Resultで統一**すると、成功/失敗の扱いがブレない🍱
* AIには **「型＋禁止事項」**までセットで渡すと強い🤖✨

---

次に第28章で、この「型」で増やしたUseCasesが **ちゃんと外側を知らないまま保ててるか**、完成チェックしていこうね✅🥰

[1]: https://devblogs.microsoft.com/dotnet/dotnet-conf-2025-recap/?utm_source=chatgpt.com "Celebrating .NET 10, Visual Studio 2026, AI, Community, & ..."
[2]: https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html?utm_source=chatgpt.com "The Clean Architecture by Uncle Bob - Clean Coder Blog"
