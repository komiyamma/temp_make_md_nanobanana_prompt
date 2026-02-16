# 第19章：Request Model（入力データ）を整える📨

## 今日のゴール🎯

* 「APIで受け取った形（DTO）」と「UseCaseがほしい形（Request Model）」を**分ける理由**を説明できる😊
* Request Modelを**“必要最小限”**にして、設計がブレないコツを掴む🧠🔧
* Controller / Endpointで**DTO → Request Model 変換**をスッと書けるようになる✍️✨

---

## 1) Request Modelってなに？🤔📦

![Request Model Definition](./picture/clean_cs_study_019_request_model_definition.png)



![Request Modelのフィルタリング](./picture/clean_cs_study_019_request_model.png)

Request Model（入力モデル）は、**UseCaseに渡すための“入力専用の箱”**だよ📨✨
ポイントは「内側（UseCase）が扱いやすい形にして渡す」こと！

Uncle Bobも「境界をまたいでデータを渡すなら、**内側にとって都合のいい形**で渡すべき」って趣旨をはっきり書いてるよ🧼🧱 ([クリーンコーダーブログ][1])

---

## 2) なんでAPI DTOと分けるの？🍱➡️🧠

![Independence from Frameworks](./picture/clean_cs_study_019_independence.png)



API DTOは「外側（HTTP/JSON）」の都合が強いよね📡

* JSONの項目名
* 互換性のための古いフィールド
* フロント都合の形（ネスト、配列、表示用っぽい項目）

DTOはネットワーク越しに運ぶための形（Data Transfer Object）としてよく使われるし、**プレゼン層とドメインを切り離す**目的があるよ📦✨ ([Microsoft Learn][2])

でもそのDTOをそのままUseCaseに入れちゃうと…😵

* フロントの変更＝UseCase変更、になりやすい
* JSON都合（null許容とか）に引きずられて、UseCaseがグラつく
* 「本当に必要な入力」が見えなくなる

だから、**DTOは外側で受けて、UseCaseにはRequest Modelとして“整えて渡す”**のが王道だよ😊🔌

---

## 3) “いいRequest Model” 7つのルール🌟✅

![Contents of Request Model](./picture/clean_cs_study_019_model_contents.png)



### ルール1：UseCaseが本当に必要なものだけ🎯

「DBに入れる全項目」じゃなくてOK🙆‍♀️
**そのユースケースに必要な入力**だけにする！

### ルール2：HTTP/JSONの匂いを持ち込まない🚫🌐

Request Modelに入れない例👇

* `HttpContext` / `ClaimsPrincipal`
* `IFormFile`（ファイルは外で受けて、必要情報だけ渡す）
* JSON属性（`JsonPropertyName`とか）

### ルール3：名前は“ユースケースの言葉”にする🗣️✨

DTOの `title` より、UseCase側は `MemoTitle` / `Title` みたいに
**意味が伝わる命名**が強い💪

### ルール4：null前提をやめる（できる範囲で）🧼

外側はnullが来るかもだけど、内側は「来ない前提」に寄せたい😊

* 必須は必須
* 任意は `string?` などで明示

### ルール5：不変条件はDomainで守る🚧💎

形式チェック（文字数とか空文字とか）は入口でもやるけど、
最終的に「壊れた状態を作れない」はDomain側が強い💪✨

### ルール6：1ユースケース = 1 Request Model が基本📦

Create用とUpdate用は分けた方がスッキリしやすい😊
（“全部入り万能Request” は肥大化しがち😇）

### ルール7：変換はAdapter（Controller/Endpoint）で一箇所に集める🔁

DTO→Request変換が散らばると地獄👹
**入口でまとめて変換**しよう！

---

## 4) 例：メモ作成（CreateMemo）で作ってみよう📝✨

### 4-1. Entities側（すでにある想定のVO）💎

![Value Objects in Request Model](./picture/clean_cs_study_019_vo_in_request.png)



（第9〜10章で作ったイメージね！）

```csharp
namespace MyApp.Core.Entities;

public readonly record struct UserId(Guid Value);

public sealed record MemoTitle
{
    public string Value { get; }
    public MemoTitle(string value)
    {
        if (string.IsNullOrWhiteSpace(value)) throw new ArgumentException("タイトルは必須です");
        if (value.Length > 100) throw new ArgumentException("タイトルは100文字までです");
        Value = value;
    }
}

public sealed record TagName
{
    public string Value { get; }
    public TagName(string value)
    {
        if (string.IsNullOrWhiteSpace(value)) throw new ArgumentException("タグ名は必須です");
        if (value.Length > 30) throw new ArgumentException("タグ名は30文字までです");
        Value = value;
    }
}
```

> ここで大事なのは「Request ModelがVOを使える」ってこと💡
> UseCasesはEntitiesを参照できる（内側へ）ので、意味が強くなるよ😊🧠

---

### 4-2. UseCases側：Request Model（最小の入力）📨

```csharp
using MyApp.Core.Entities;

namespace MyApp.Core.UseCases.Memos.Create;

public sealed record CreateMemoRequest(
    UserId OwnerId,
    MemoTitle Title,
    IReadOnlyList<TagName> Tags
);
```

* `OwnerId`：誰のメモ？（認可の“主体”情報は **IDだけ**渡すのがコツ）👤
* `Title`：VOで意味を固定💎
* `Tags`：必要なら。不要なら削ってOK✂️

---

### 4-3. Input Port（18章の続きとつながる）🔌⬅️

```csharp
namespace MyApp.Core.UseCases.Memos.Create;

public interface ICreateMemoInputPort
{
    Task HandleAsync(CreateMemoRequest request, CancellationToken ct);
}
```

ここで **UseCaseの入口（窓口）** が固まるよ😊✨

---

## 5) Web側：API DTO を受けて Request Model に変換する🍱➡️📨

### 5-1. API DTO（外側の都合）🌐

```csharp
namespace MyApp.Web.ApiContracts;

public sealed class CreateMemoDto
{
    public string? Title { get; set; }
    public List<string>? Tags { get; set; }
}
```

### 5-2. Endpointで変換（ここが“境界”🚪）

![Conversion Boundary](./picture/clean_cs_study_019_conversion_boundary.png)



```csharp
using MyApp.Core.Entities;
using MyApp.Core.UseCases.Memos.Create;
using MyApp.Web.ApiContracts;

app.MapPost("/memos", async (
    CreateMemoDto dto,
    ICreateMemoInputPort useCase,
    HttpContext http,
    CancellationToken ct) =>
{
    // 例：ログインユーザーIDを外側で取得して、IDだけ渡す👤
    var ownerId = new UserId(Guid.Parse(http.User.FindFirst("sub")!.Value));

    // DTO -> Request Model（UseCaseが欲しい形へ整える✨）
    var request = new CreateMemoRequest(
        OwnerId: ownerId,
        Title: new MemoTitle(dto.Title ?? ""),
        Tags: (dto.Tags ?? new List<string>())
            .Select(t => new TagName(t))
            .ToList()
    );

    await useCase.HandleAsync(request, ct);
    return Results.Ok();
});
```

ここが超重要ポイント💖

* DTOは外側の形🍱
* Request ModelはUseCaseの形📨
* **変換で“波”を止める**🌊✋

---

## 6) バリデーション、どこでやるの？🛑🧠

![Validation vs Invariant](./picture/clean_cs_study_019_validation_placement.png)



よく混乱するから、シンプルに分けよう😊

* **Adapter（入口）**：形式っぽいチェック

  * nullチェック
  * JSONの形式
  * “空っぽで来てる” みたいな雑な入力
* **Domain（VO/Entity）**：ルール（不変条件）

  * 「空タイトル禁止」
  * 「100文字まで」
  * 「タグは30文字まで」

こうすると、どこに何を書くか迷子になりにくいよ🧭✨

---

## 7) Request Modelが肥大化してきたサイン🚨

### サインA：DTOのフィールドがそのまま増殖してる🧟‍♀️

→ 「本当にUseCaseで必要？」を毎回問い詰めよう😆🔍

### サインB：表示用っぽい情報が混ざってきた🎀

例：`DisplayTitle` とか `LocalizedDateText` とか
→ それ、Presenter側の仕事だよ〜！🎤✨

### サインC：1つのRequestが“万能”になってる🧰

→ Create/Update/Searchで分割しよ😊✂️

---

## 8) ミニ課題（手を動かそう）🧪✨

1. **CreateMemoRequestからTagsを一度消す**✂️

   * 本当に必要か、要件から判断してみてね😊
2. **UpdateMemoRequestを作る**🛠️

   * `MemoId`（VOでもOK）と、更新可能な項目だけ
3. EndpointでDTO→Request変換を実装して、**変換場所が散らばってないか**確認👀✅

---

## 9) Copilot / Codexに頼むと便利な聞き方🤖💬

* 「このユースケース説明から、Request Modelの必須フィールドだけ抽出して」
* 「DTOにあるけどUseCaseに不要そうな項目を指摘して」
* 「DTO→Request変換コードを書いて。null/空の扱いも提案して」
* 「Request Modelが肥大化する兆候チェックリストを作って」

---

## まとめ🎉

* Request Modelは **UseCaseの入力専用の箱**📨
* DTO（外側の形）をそのまま入れず、**境界で整えて渡す**🚪✨（内側に都合のいい形で渡すのが筋）([クリーンコーダーブログ][1])
* DTOは層を分けるのに役立つけど、だからこそ **UseCase側とは分離**が効く🍱➡️🧠 ([Microsoft Learn][2])

次の第20章では、このRequest Modelを受け取って動く **Interactorの骨格**を組み立てていくよ🧱🔥

[1]: https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html?utm_source=chatgpt.com "The Clean Architecture by Uncle Bob - Clean Coder Blog"
[2]: https://learn.microsoft.com/en-us/aspnet/web-api/overview/data/using-web-api-with-entity-framework/part-5?utm_source=chatgpt.com "Create Data Transfer Objects (DTOs)"
