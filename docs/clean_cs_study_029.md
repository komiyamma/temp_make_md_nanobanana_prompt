# 第29章：Controllerの責務（“受け取って呼ぶだけ”）🚪

この章は **「Controllerを薄くして、設計が崩れない土台を作る」** 回だよ〜！😊💕
クリーンアーキでのControllerは、ざっくり言うと **“外の世界（HTTP）を、内側（UseCase）が食べられる形に変換して渡す係”** です🍱✨（変換層＝Interface Adaptersの仕事だね）

---

## この章のゴール 🎯✨

![Controller Diet](./picture/clean_cs_study_029_controller_diet.png)

できるようになったら勝ち〜！😆🎉

* Controllerの **やること／やらないこと** を説明できる📣
* 「薄いController」の型（テンプレ）を持てる📐✨
* Fat Controller（太りすぎ）を見つけて、UseCaseやAdapterに戻せる🧹✅

---

## まず結論：Controllerの仕事はコレだけ！🫶✨

![Controller Relay Baton](./picture/clean_cs_study_029_relay_baton.png)

![薄いControllerの仕事](./picture/clean_cs_study_029_thin_controller.png)

### ✅ Controllerがやること（OK）

* HTTPリクエストを受け取る（ルーティング）🛣️
* 入力（DTO等）を **UseCaseのRequestModel** に変換する🔄
* **InputPort（UseCase）を呼ぶ** 📞
* Presenter等が作った結果を **HTTPレスポンスに変換して返す** 📨
* “薄く”ログ・認可などの入口設定をつける（ただしロジックは置かない）🔐📝

### ❌ Controllerがやってはいけないこと（NG）

* ビジネスルール判断（例：タイトル長いから…等の“仕様”）🚫
* DB操作（DbContext直叩き）🗄️💥
* トランザクション制御💳
* 仕様に関わるValidation（＝不変条件）をここに散らす🚧
* “便利だから”でUseCaseをすっ飛ばすショートカット🏃💨

> 「ビジネスロジックは中心へ」っていう依存逆転の考え方がクリーンアーキの核だよ〜🧠⭕
> （Application Coreを中心に置き、外側詳細が内側に依存する形） ([Microsoft Learn][1])

---

## なんでControllerを薄くするの？🥺👉💡

![Controller Collapse](./picture/clean_cs_study_029_controller_collapse.png)

Controllerが太ると、こうなるよ…😇💦

* 画面（HTTP）変更のたびにロジックが壊れる😵‍💫
* テストがつらい（HTTPやDBに巻き込まれる）🧪💦
* “どこが仕様？”が散らばって、修正が怖い😱
* UseCaseが空洞化して、クリーンアーキが形だけになる🎭

なのでControllerは **「受け取って→変換して→呼ぶ」** の3点セットに寄せます🫶✨
（Controllerは入力をUseCase向けに変換する、って説明もまさにこのニュアンスだよ〜） ([Qiita][2])

---

## “薄いController”の黄金テンプレ 🏆✨

![Minimal API Actors Lineup](./picture/clean_cs_study_029_actors_lineup.png)

### 🌟 パターンA：Minimal APIでのController（Endpoint）版（おすすめ）

.NET 10ではMinimal APIまわりも充実してて、**Validationも標準サポート**が入ってるよ〜！ ([Microsoft Learn][3])
さらに **Endpoint Filters** で共通処理をパイプラインに逃がしやすいのが強い💪✨ ([Microsoft Learn][4])

#### 役者（登場人物）👪✨

* `CreateMemoApiDto`：HTTPで受ける入力（外の形）🍱
* `CreateMemoRequest`：UseCaseが欲しい入力（中の形）📨
* `ICreateMemoInputPort`：UseCaseの入口🔌
* `CreateMemoPresenter`：出力をHTTP向けに整形🎤📦

---

## 実装例：CreateMemo を“薄い”まま作る 🧱✨

### 1) API DTO（外の入力）🍱

```csharp
public sealed record CreateMemoApiDto(
    string Title,
    string? Body
);
```

> DTOは「HTTPの都合」を引き受ける係だよ😊
> （次章30で “DTOとRequestを分ける” をもっと深掘りするよ〜！）

---

### 2) UseCase Request（中の入力）📨

```csharp
public sealed record CreateMemoRequest(
    string Title,
    string? Body
);
```

---

### 3) InputPort（UseCaseの入口）🔌➡️

```csharp
public interface ICreateMemoInputPort
{
    Task HandleAsync(CreateMemoRequest request, CancellationToken ct = default);
}
```

---

### 4) Presenter（OutputPort実装：結果をHTTP向けに保持）🎤📦

※ここでは“例”として、Presenterが `IResult` を返せるようにしておくよ（Minimal API向け）😊

```csharp
public sealed class CreateMemoPresenter : ICreateMemoOutputPort
{
    public IResult Result { get; private set; } = Results.StatusCode(500);

    public Task PresentAsync(CreateMemoResponse response, CancellationToken ct = default)
    {
        if (response.IsSuccess)
        {
            Result = Results.Created($"/memos/{response.MemoId}", new
            {
                id = response.MemoId,
                title = response.Title
            });
        }
        else
        {
            // ここでHTTP表現（ProblemDetails等）に落とす
            Result = Results.BadRequest(new
            {
                error = response.ErrorCode,
                message = response.Message
            });
        }

        return Task.CompletedTask;
    }
}
```

---

### 5) Controller（Endpoint）本体：マジで“薄く”する ✨🚪

```csharp
app.MapPost("/memos", async (
    CreateMemoApiDto dto,
    ICreateMemoInputPort inputPort,
    CreateMemoPresenter presenter,
    CancellationToken ct) =>
{
    // ① HTTPの形 → ② UseCaseの形 に変換するだけ
    var request = new CreateMemoRequest(dto.Title, dto.Body);

    // ③ 呼ぶだけ
    await inputPort.HandleAsync(request, ct);

    // ④ Presenterが用意した結果を返すだけ
    return presenter.Result;
});
```

✅ これでControllerは **変換＋呼び出し＋返却** しかしてない！えらい！😆🎉
「仕様の判断」はUseCase/Entities側に寄せられるので、設計が崩れにくいよ🧼✨

---

## Validationはどこでやる？🛑🤔（Controllerが太る最大原因！）

![Validation Gates](./picture/clean_cs_study_029_validation_gates.png)

ここ超大事〜！💘

### ✅ ルール：Validationを2種類に分ける ✂️✨

* **形式チェック（Adapter側）**：空文字、JSON形式、型、最大長“入力制約”など🧾
* **仕様チェック（Domain側）**：不変条件、業務ルール、状態遷移など👑🚧

Minimal APIでは **Validationの標準サポート**が入っていて、エラー応答のカスタムも `IProblemDetailsService` で調整できるよ〜（Controllerにif文を書き散らさずに済む！） ([Microsoft Learn][3])

MVC Controllerを使う場合も、Model Binding/Validation結果は `ModelState` に入って `ModelState.IsValid` で見られる（＝Controllerで雑に肥大化しやすいポイント） ([Microsoft Learn][5])
だからこそ「形式はパイプラインへ」「仕様は内側へ」って分けるのが安定😊✨

---

## Controllerを薄く保つための“禁止ワード集”🧨😇

Controller内でこれが出たら黄色信号だよ〜🚥💦

* `DbContext` / `SqlConnection` / `Dapper` / `TransactionScope`
* `if (user.IsPremium) ...` みたいな仕様分岐
* `DateTime.Now` を使った業務判断（※時間は依存になりやすい）
* `try { ... } catch { ... }` が10行超えてる（例外設計が散ってる）
* `foreach` が回りだす（集計・判断が始まってる）

---

## “共通処理”はControllerに置かない：Filtersへ逃がす 🏃‍♀️💨✨

![Pipeline Filters](./picture/clean_cs_study_029_pipeline_filters.png)

たとえば👇みたいなやつ

* リクエストログ📝
* 例外→ProblemDetails変換⚠️
* 入力の前処理（トリム等）✂️
* “形式チェック”の強制🛑

Minimal APIなら **Endpoint Filters** が「前後処理」「引数や結果の横取り」に使えるよ〜！ ([Microsoft Learn][4])
Controller（Endpoint）をさらに薄くできて最高☺️💕

---

## ミニ課題（手を動かすやつ）🧪✨

### 課題1：Controllerをテンプレ化しよ〜📐

* `CreateMemo` と同じ型で `UpdateMemo` Endpointも作る
* ただしControllerは **変換→呼ぶ→返す** の3点セットだけ！

✅ 合格ライン：Endpoint内が **10〜15行以内** 😆✨

---

### 課題2：わざとFat Controllerを作って、戻す💥➡️🧼

1回わざとやると目が育つよ👀✨

* Controllerに `if` と `DbContext` を入れて太らせる
* 「どの責務が混ざったか」をメモして
* UseCase / Presenter / Adapterへ戻す

---

## Copilot / Codex への頼み方（薄く作る用）🤖✨

コピペで使えるプロンプト例だよ〜（生成されたコードは必ず目でレビューしてね👀💕）

* 「Minimal APIで `/memos` のPOSTを作って。Controller（Endpoint）は DTO→Request 変換、InputPort呼び出し、PresenterのResult返却だけにして」
* 「Controller内にビジネスロジックが混ざらないように、禁止事項チェックリストも添えて」

---

## まとめ 🎀✨

* Controllerは **“HTTPの世界”と“UseCaseの世界”の通訳** 🗣️🔄
* やるのは **変換→呼ぶ→返す** だけ🚪➡️🔌➡️📨
* 共通処理や形式Validationはパイプラインへ（Filters/仕組みへ）🏃‍♀️💨
* 仕様（不変条件）は内側（Entities/UseCase）へ👑🚧

---

## おまけ：いまの最新前提メモ（安心用）🧾✨

この章で使ってる “Minimal APIのValidation” や “Filters” は **ASP.NET Core（.NET 10 世代）** のドキュメントに基づいてるよ〜😊
.NET 10 はLTSで、2026年1月にも更新が出てるよ📦✨ ([endoflife.date][6])

[1]: https://learn.microsoft.com/en-us/dotnet/architecture/modern-web-apps-azure/common-web-application-architectures?utm_source=chatgpt.com "Common web application architectures - .NET"
[2]: https://qiita.com/nrslib/items/a5f902c4defc83bd46b8?utm_source=chatgpt.com "実装クリーンアーキテクチャ #オブジェクト指向"
[3]: https://learn.microsoft.com/en-us/aspnet/core/fundamentals/minimal-apis?view=aspnetcore-10.0&utm_source=chatgpt.com "Minimal APIs quick reference"
[4]: https://learn.microsoft.com/en-us/aspnet/core/fundamentals/minimal-apis/min-api-filters?view=aspnetcore-10.0&utm_source=chatgpt.com "Filters in Minimal API apps"
[5]: https://learn.microsoft.com/en-us/aspnet/core/mvc/models/model-binding?view=aspnetcore-10.0&utm_source=chatgpt.com "Model Binding in ASP.NET Core"
[6]: https://endoflife.date/dotnet?utm_source=chatgpt.com "Microsoft .NET"
