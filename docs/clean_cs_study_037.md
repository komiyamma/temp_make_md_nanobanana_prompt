# 第37章：Adapter層の完成チェック（変換が一箇所に集約されてる？）✅

この章は **「変換が散らばってないか」** を点検して、**事故りやすい“境界のモヤモヤ”をスッキリさせる回**だよ〜😊💖
（Adapter層＝Controller/Endpoint・Presenter・Repository実装・外部API Client実装…みたいな「内と外をつなぐ層」ね！）

---

## 1) まずゴールをハッキリさせよっ 🧭✨

![変換の集約 (Centralized Mapping)](./picture/clean_cs_study_037_centralized_mapping.png)

Adapter層が完成してる状態って、ひと言でいうと👇

* **変換（マッピング）が“決まった場所”に集まってる** 🧺
* **内側の型（Entity/UseCase）に外側の都合が混ざってない** 🧼
* **Controller/Endpoint と Presenter が薄い** 🍃
* **依存の向きがキレイ（外→内だけ）** ➡️⭕
  ※「内側は外側を知らない。名前すら出さない」が大原則だよ〜！ ([クリーンコーダーブログ][1])

Microsoftの .NET アーキテクチャガイドも「中心（Application Core）が詳細（インフラ等）に依存しないように、**Coreに抽象（interface）を置いて外側が実装する**」って説明してるよ。 ([Microsoft Learn][2])

---

## 2) Adapter層で起きがちな「変換の散乱」あるある 😵‍💫💥

![Scattered Mapping Accident](./picture/clean_cs_study_037_mapping_scattered.png)

散乱が起きると、こうなる👇

* いろんな場所に `ToDto()` が生えて **仕様がズレる** 😭
* 変換のルール（null扱い、丸め、日付の時刻、ID生成）が **統一されない** 🌀
* Controllerが「ちょい加工」を始めて **いつの間にかロジック持つ** 🐘
* DBモデルに合わせてDomainが歪んで **中心が汚れる** 🧟‍♀️

だからこの章は **「変換の地図」を作って、散らばりを回収する** 回だよ！🗺️💕

---

## 3) 変換を3種類に分けると一気に整理できるよ 🧠🔍

![Three Types of Mapping](./picture/clean_cs_study_037_three_baskets.png)

Adapter層の変換って、だいたいこの3つに分かれる👇

### A. 入力変換（外 → 内）📥➡️⭕

* HTTPのRequest DTO / JSON / Query など
  → **UseCaseのRequestModel** へ変換

### B. 出力変換（内 → 外）⭕➡️📤

* **UseCaseのResponseModel**
  → ViewModel / Response DTO / ProblemDetails へ変換

### C. 永続化・外部I/O変換（内 ↔ 外）🗄️🌍

* Domain Entity / VO
  ↔ DBモデル（EF用） / 外部API用モデル

ここを分けるだけで「どこで何をすべきか」が一気にクリアになるよ😊✨

---

## 4) Adapter層 完成チェックリスト ✅✅✅（ここが本体！）

### 4-1. 依存の向きチェック（最重要）➡️⭕

![Dependency Direction (One-Way Mirror)](./picture/clean_cs_study_037_one_way_mirror.png)

* [ ] **Core（Entities/UseCases）が、外側の型名を1ミリも知らない** ([クリーンコーダーブログ][1])
  例：Coreが `Controller` / `DbContext` / `HttpRequest` / `IActionResult` / EF属性 を参照してない
* [ ] Coreにあるのは **Entity/VO/UseCase と interface（Port）だけ** ([Microsoft Learn][2])

### 4-2. Controller/Endpoint が薄いチェック 🚪🍃

* [ ] Controller/Endpoint は **「受け取る→入力変換→InputPort呼ぶ」だけ**
* [ ] if/for/try-catch が増殖してない（増殖してたら危険信号🚨）
* [ ] **HTTPの都合（status code / ProblemDetails / validation）**はここ or 近く（Filterなど）で完結できてる

> ちなみに最近の ASP.NET Core（10.0系ドキュメント）では、Minimal API に **Validationサポート** や **ProblemDetails（AddProblemDetails）** も整ってきてるので、HTTP都合を境界で揃えやすいよ〜😊🧰 ([Microsoft Learn][3])

### 4-3. Presenter が薄いチェック 🎤🍃

* [ ] Presenter は **OutputPortを実装して「変換だけ」**
* [ ] 画面/HTTP都合の整形（成功/失敗レスポンス統一、表示文言整形）は Presenter 側
* [ ] UseCase側が `IActionResult` や `Results<...>` を返してない（返したら境界崩壊⚠️）

### 4-4. Repository/Client 実装の責務チェック 🗄️🌍

* [ ] Core側にあるのは `IMemoRepository` みたいな **interfaceだけ**
* [ ] 実装（EF/SQL/HTTP client）は外側
* [ ] DBモデルや外部APIモデルとのマッピングは **実装の近くで完結**（Coreに持ち込まない）

---

## 5) “変換の台帳（だいちょう）”を作ると勝ちやすいよ 📒💖

![Mapping Ledger](./picture/clean_cs_study_037_mapping_ledger.png)

Adapter層が荒れてるとき、最強の立て直しはこれ👇

### 変換台帳テンプレ

| 変換名   | From            | To             | 置き場所（理想）              | 備考（ルール）       |
| ----- | --------------- | -------------- | --------------------- | ------------- |
| 入力変換  | ApiRequestDto   | UseCaseRequest | Controller/Endpoint近く | 空文字→nullにしない等 |
| 出力変換  | UseCaseResponse | ApiResponseDto | Presenter             | エラー文言の統一      |
| 永続化変換 | DomainEntity    | DbEntity       | Persistence Adapter   | 日付のUTC統一など    |

**ポイント**：
「置き場所（理想）」が書けない変換は、だいたい散乱の元だよ😆💥

---

## 6) 実践：散らばった変換を“回収”する手順 🧹✨

### Step 1：変換を検索してリスト化 🔎

Visual Studio の “検索（ソリューション全体）” で👇を探すよ

* `ToDto` / `FromDto` / `Map` / `Convert`
* `new XxxDto` が大量に出てくる場所
* `Select(x => new ...)` がControllerにある場所

### Step 2：変換の置き場所を決める 🧠

迷ったらこのルールでOK👇

* **HTTP ↔ UseCase**：Web Adapter（Endpoint/Controller）側
* **UseCase ↔ 画面/レスポンス**：Presenter側
* **Domain ↔ DB/外部**：Persistence/External Adapter側

### Step 3：回収して“1箇所”へ 🧺

よくある回収先は👇

* `Adapters.Web/Mappings/`
* `Adapters.Persistence/Mappings/`
* `Adapters.External/Mappings/`

---

## 7) コード例：変換は「拡張メソッド」でまとめるのがラクだよ 🧩✨

![Extension Method Tool](./picture/clean_cs_study_037_extension_tool.png)

### 7-1. 入力変換（API DTO → UseCase Request）

```csharp
// Adapters.Web/Mappings/CreateMemoMappings.cs
namespace Adapters.Web.Mappings;

public static class CreateMemoMappings
{
    public static CreateMemoRequest ToUseCaseRequest(this CreateMemoApiRequest dto)
        => new(
            Title: dto.Title?.Trim() ?? "",
            Body: dto.Body ?? ""
        );
}
```

Controller/Endpoint 側はこうなる👇（薄い！えらい！😊）

```csharp
public async Task<IResult> CreateMemo(
    CreateMemoApiRequest dto,
    ICreateMemoInputPort inputPort)
{
    await inputPort.Handle(dto.ToUseCaseRequest());
    return Results.Ok();
}
```

### 7-2. 出力変換（UseCase Response → API Response）

```csharp
// Adapters.Web/Presenters/CreateMemoPresenter.cs
public sealed class CreateMemoPresenter : ICreateMemoOutputPort
{
    public IResult Result { get; private set; } = Results.StatusCode(500);

    public void Ok(CreateMemoResponse response)
        => Result = Results.Created($"/memos/{response.MemoId}",
            new CreateMemoApiResponse(response.MemoId));

    public void Invalid(string message)
        => Result = Results.BadRequest(new { message });
}
```

> 最近の ASP.NET Core では ProblemDetails を標準化しやすくなってるので、エラー返却の統一もやりやすいよ〜🧯✨ ([Microsoft Learn][4])

---

## 8) “薄いEndpoint”を保つ小ワザ：Filterで横断関心を外に出す 🧼🪄

![Filter for Cross-Cutting Concerns](./picture/clean_cs_study_037_filter_net.png)

「ログ」「例外整形」「入力の軽い共通チェック」みたいな横断処理は、Minimal API の Filter で外に逃がせるよ〜😊
（Endpointが太るのを予防できる！）

Minimal API filters は、Endpointの前後で処理を差し込める仕組みとして公式に説明されてるよ。 ([Microsoft Learn][5])

---

## 9) AI（Copilot/Codex）に手伝わせるコツ 🤖✨（超使える！）

### 9-1. 変換台帳づくりをAIにやらせる

プロンプト例👇
「CreateMemoApiRequest / CreateMemoRequest / CreateMemoResponse / CreateMemoApiResponse の型定義を貼る → 台帳にして」

* “どの変換がどこに置かれるべきか” を表にしてもらう📒✨

### 9-2. マッピング雛形を作らせる（でも最終判断は人間！）

プロンプト例👇

* 「このDTO→Requestの変換拡張メソッドを作って。Trimやnull方針はこう」
* 「このResponse→ApiResponseの変換、成功/失敗の型を統一して」

**注意**：AIは油断するとControllerにロジック混ぜがち😇💥
生成後にこの章のチェックリストで殴ってOK！👊😆

---

## 10) ミニ課題（30〜45分）🎯💪💖

### お題：Adapter層の“変換回収”を1ユースケースで完了させよう！

1. 1つユースケースを選ぶ（例：CreateMemo）
2. 変換を検索して全部メモる（どこに散らばってる？）
3. 変換台帳を作る📒
4. `Mappings/` に回収して、Controller/Presenter を薄くする🍃
5. 最後にチェックリストで合格判定✅

**合格ライン**：

* Controller/Endpoint が “変換して呼ぶだけ”
* Presenter が “整形して返すだけ”
* Core が外の型名を知らない ([クリーンコーダーブログ][1])

---

## まとめ：第37章で手に入る最強スキル 🏆💖

* 「変換が散らばってる」を **発見できる** 👀✨
* 「どこに置けばいいか」を **即断できる** 🧠⚡
* Adapter層が整って、**修正が怖くなくなる** 😌🌸

次の第38章（違反パターン診断🩺）が、ここまで整ってるとめちゃくちゃ楽しくなるよ〜😆🎉

[1]: https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html?utm_source=chatgpt.com "Clean Architecture by Uncle Bob - The Clean Code Blog"
[2]: https://learn.microsoft.com/en-us/dotnet/architecture/modern-web-apps-azure/common-web-application-architectures?utm_source=chatgpt.com "Common web application architectures - .NET"
[3]: https://learn.microsoft.com/en-us/aspnet/core/release-notes/aspnetcore-10.0?view=aspnetcore-10.0&utm_source=chatgpt.com "What's new in ASP.NET Core in .NET 10"
[4]: https://learn.microsoft.com/en-us/aspnet/core/fundamentals/error-handling-api?view=aspnetcore-10.0&utm_source=chatgpt.com "Handle errors in ASP.NET Core APIs"
[5]: https://learn.microsoft.com/en-us/aspnet/core/fundamentals/minimal-apis/min-api-filters?view=aspnetcore-10.0&utm_source=chatgpt.com "Filters in Minimal API apps"
