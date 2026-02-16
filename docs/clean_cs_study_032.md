# 第32章：Validationの責務（Adapterで止める/Domainで守る）🛑

この章は「検証（Validation）をどこに置くと、コードが散らからず、クリーンアーキが崩れないか？」を**“ルール化”**する回だよ〜！😊💕

---

## 1) この章でできるようになること ✅🌸

* 「入力チェック」を**Adapterで止めるもの**と、**Domainが絶対守るもの**に分けられる✨
* ルールが散って「ControllerにもUseCaseにもEntityにも同じifが…😵‍💫」を防げる
* Minimal API / Controller どっちでも、**Validation → ProblemDetails**の流れを作れる💡
  （.NET 10 では Minimal API にも組み込み検証が入ったよ！）([Microsoft Learn][1])

---

## 2) まず結論：Validationは “2段構え” が正解 🥋💖

![バリデーションの2段構え](./picture/clean_cs_study_032_validation.png)

Validation をざっくり2種類に分けると、迷わなくなるよ😊✨

### A. Adapterで止める（形式・プロトコルのチェック）🚧📮

![Adapter Validation Gate](./picture/clean_cs_study_032_adapter_gate.png)

「HTTPで受け取った入力が、最低限まともか？」を止めるイメージ！

* 必須項目がない（null / 空）
* 文字数が長すぎる
* フォーマットがおかしい（メール、URL、日付文字列など）
* クエリ/ヘッダ/ボディの型が合わない

.NET 10 の Minimal API は `AddValidation()` を有効化すると、**DataAnnotationsで定義した検証を、ハンドラ実行前に自動で走らせて**、失敗時は **ProblemDetails (400)** を返してくれるよ✨([Microsoft Learn][1])
（Controller でも `[ApiController]` が同じ感じで、モデル検証エラーは自動で 400 になるよ）([Microsoft Learn][2])

### B. Domainで守る（不変条件＝壊れた状態を作れない）🛡️👑

![Domain Protection Shield](./picture/clean_cs_study_032_domain_shield.png)

「外側がどう来ようが、Domainは絶対に壊れない」っていう守護神ポジション！

* タイトルは空じゃダメ（仕様）
* タグ名はこの文字種だけ（仕様）
* タグ重複禁止（仕様）
* 状態遷移の制約（例：Archive済みはRename不可）

👉 **Domainは“最後の砦”**だから、Adapterがすり抜けても壊れないのが正解✨

---

## 3) 最新：.NET 10 の Minimal API は “組み込みValidation” があるよ！🎉🧡

Minimal API で Validation を有効にすると、**Query / Header / Body** に対して検証してくれるよ〜！([Microsoft Learn][1])
カスタムの検証エラーレスポンスを作りたい場合も、`IProblemDetailsService` で整えられる設計が用意されてるよ✨([Microsoft Learn][3])

---

## 4) ルール表：どこで止める？どこで守る？🧠📋✨

![Rule Sorting System](./picture/clean_cs_study_032_rule_sorting.png)

「CreateMemo」を例に、置き場所を決めるとこうなるよ👇

| ルール例           | 置き場所                               | 理由              |
| -------------- | ---------------------------------- | --------------- |
| Title が null/空 | Adapter（DTO検証） + Domain（VO/Entity） | 早めに親切エラー＋最後の砦   |
| Title 最大100文字  | Adapter + Domain                   | 同上（UI都合の表示も助かる） |
| Tags が最大10個    | Domain                             | 仕様（ビジネスルール）     |
| Tags の重複禁止     | Domain                             | 仕様（不変条件）        |
| MemoId が存在しない  | UseCase                            | “外部状態”に依存（DBの話） |
| 外部APIがタイムアウト   | UseCase                            | “処理の結果”として扱う    |

ポイントはこれ👇😊💡

* **「形式」＝Adapter**（入口で弾く）
* **「仕様・不変条件」＝Domain**（壊れない）
* **「外部状態に依存」＝UseCase**（存在チェック等）

---

## 5) 実装例（Minimal API）：Adapterで止める 🛑🌷

![Minimal API Validation Pipeline](./picture/clean_cs_study_032_minimal_api_pipeline.png)

### 5-1) DTOに DataAnnotations（Adapter側）🧾✨

```csharp
using System.ComponentModel.DataAnnotations;

public sealed record CreateMemoRequestDto(
    [Required, MaxLength(100)]
    string? Title,

    [MaxLength(4000)]
    string? Body,

    // 例：タグは “形式” として最大数だけ先に止めるのはアリ
    [MaxLength(10)]
    string[]? Tags
);
```

### 5-2) 組み込みValidationを有効化して、先に弾く🧯✨

```csharp
var builder = WebApplication.CreateBuilder(args);

// .NET 10: Minimal API validation を有効化
builder.Services.AddValidation();

var app = builder.Build();

app.MapPost("/memos", async (CreateMemoRequestDto dto) =>
{
    // ここに来た時点で DataAnnotations 的にOK（NGなら自動で 400 + ProblemDetails）
    return Results.Ok();
});

app.Run();
```

この「ハンドラ実行前に検証してくれる」仕組みが .NET 10 の目玉のひとつだよ✨([Microsoft Learn][1])

---

## 6) Domainで守る：VOで “壊れた値” を作れなくする 🛡️💎

Adapterは「入口で止める」だけ。
Domainは「そもそも不正な値が生成できない」が理想だよ😊✨

```csharp
public sealed class Title
{
    public const int MaxLength = 100;
    public string Value { get; }

    private Title(string value) => Value = value;

    public static Result<Title> Create(string? raw)
    {
        if (string.IsNullOrWhiteSpace(raw))
            return Result.Fail("TITLE_EMPTY");

        var value = raw.Trim();

        if (value.Length > MaxLength)
            return Result.Fail("TITLE_TOO_LONG");

        return Result.Ok(new Title(value));
    }
}
```

> ✅ **DomainはDataAnnotationsを持たない**（外側の都合だからね）
> ✅ “生成時にチェック” すると不変条件が守りやすい💕

---

## 7) 「じゃあ重複しない？」問題：同じルールを2回書いてOK？🤔💭

![Double Check Strategy](./picture/clean_cs_study_032_double_check.png)

結論：**OK！ただし “正” はDomain** 😊✨

* Adapterの検証：ユーザーに早く・親切に返すため💌
* Domainの検証：絶対壊れないため🛡️

**ズレが怖い**なら、Domain側の `const` を Adapter が参照して揃えるのはアリだよ（Adapter→Domain依存はOK）👍✨
（例：`Title.MaxLength` を DTO の `MaxLength` に使う、など）

---

## 8) 複雑なValidationはどうする？（FluentValidationの扱い）🧩✨

### 超重要⚠️：`FluentValidation.AspNetCore` は “非推奨・非サポート”

昔よく使われた自動連携パッケージは、**今はサポートされてない**よ〜！([GitHub][4])

だから今どきの使い分けはこんな感じ👇😊

* **軽い形式チェック**：DataAnnotations（組み込み検証と相性◎）([Microsoft Learn][1])
* **条件分岐が多い・DTOが複雑**：FluentValidation “本体” を使って **手動で呼ぶ**（Adapter側で）([FluentValidation][5])
* **仕様（不変条件）**：Domain（VO/Entity）で守る🛡️

### FluentValidation（手動）ミニ例：Adapter側で呼ぶ 🎛️

```csharp
using FluentValidation;

public sealed class CreateMemoRequestDtoValidator : AbstractValidator<CreateMemoRequestDto>
{
    public CreateMemoRequestDtoValidator()
    {
        RuleFor(x => x.Title)
            .NotEmpty()
            .MaximumLength(Title.MaxLength);

        RuleFor(x => x.Tags)
            .Must(tags => tags is null || tags.Length <= 10)
            .WithMessage("TAGS_TOO_MANY");
    }
}
```

```csharp
app.MapPost("/memos", async (
    CreateMemoRequestDto dto,
    IValidator<CreateMemoRequestDto> validator) =>
{
    var vr = await validator.ValidateAsync(dto);
    if (!vr.IsValid)
        return Results.ValidationProblem(vr.ToDictionary()); // 400 の整形は方針でOK✨

    return Results.Ok();
});
```

---

## 9) ミニ課題（やってみよ〜！）🎮💖

### 課題A：ルール表をあなたの題材で作る📋✨

最低10個！
「Adapter / Domain / UseCase」の列を作って分類してね😊

### 課題B：CreateMemo に3つだけ “Domain不変条件” を追加🛡️

おすすめ：

* Title空禁止
* Title最大長
* Tags重複禁止

### 課題C：テストで守る🧪✨

* Domain（VO/Entity）のテストを3本
* 「Adapter検証をすり抜けたとしてもDomainが守る」ことを確認👍

---

## 10) AI（Copilot/Codex）に頼るコツ🤖💞

![AI Mistake - Annotation Pollution](./picture/clean_cs_study_032_ai_mistake.png)

使いどころ、めっちゃあるよ〜！

* 「このDTOに必要そうなDataAnnotationsを提案して」
* 「このDomain不変条件の境界値テスト案を10個出して」
* 「Validationの置き場所がズレてないか、ルール表をレビューして」

⚠️ ただし、AIがやりがちな事故はこれ：

* Domainに DataAnnotations を付けようとする（外側の都合混入😵‍💫）
* Controller/UseCaseに if が増殖する（散らかる😵‍💫）

その時はこの合言葉👇
**「形式は入口、仕様は中心」** 🛑🛡️✨

---

次の章（第33章）は **「Persistence Adapter（DBは“詳細”）」** で、今回作った「境界の考え方」がそのまま効いてくるよ〜！🗄️💖

[1]: https://learn.microsoft.com/en-us/aspnet/core/fundamentals/minimal-apis?view=aspnetcore-10.0&utm_source=chatgpt.com "Minimal APIs quick reference"
[2]: https://learn.microsoft.com/en-us/aspnet/core/web-api/?view=aspnetcore-10.0&utm_source=chatgpt.com "Create web APIs with ASP.NET Core"
[3]: https://learn.microsoft.com/ja-jp/aspnet/core/fundamentals/minimal-apis?view=aspnetcore-10.0&utm_source=chatgpt.com "Minimal API クイック リファレンス"
[4]: https://github.com/FluentValidation/FluentValidation.AspNetCore?utm_source=chatgpt.com "ASP.NET Core Integration for FluentValidation"
[5]: https://fluentvalidation.net/aspnet?utm_source=chatgpt.com "ASP.NET Core — FluentValidation documentation"
