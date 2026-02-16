# 第21章：Output Port（出力境界）を設計する🔌➡️

（※2026/01/23 時点の前提：C# 14 / .NET 10 が最新ラインで、Visual Studio 2026 で扱えるよ〜）([Microsoft Learn][1])

## この章のゴール🎯✨

* Output Port が **なにを守る仕組み**なのか説明できる😌
* 「ユースケースの戻り値」を **Presenterに依存しない形**で設計できる🧼
* **ResponseModel（ユースケースの出力データ）**を、外側（Web/DB/UI）に汚されずに作れる🧩

---

## 1) Output Portってなに？🤔

![Output Port Role](./picture/clean_cs_study_021_output_port_role.png)



![Output Portの役割](./picture/clean_cs_study_021_output_port.png)

クリーンアーキでは、ユースケース（Use Case / Interactor）は **“内側”** にいて、UIやWeb、DBみたいな **“外側”** を知らないようにするのが大事だよね⭕️

でもユースケースって、処理した結果を「画面に出す」とか「APIで返す」とか、最終的には外側に届けたい…！

そこで出てくるのが **Output Port（出力境界）** だよ🔌➡️
ユースケースは **Presenterを直接呼べない**（呼ぶと依存が外向きになっちゃう）から、

* ユースケース側に **“インターフェース（Output Port）”** を置く
* 外側の Presenter がそれを **実装する**

って形にするの。これが “依存は内側へ” のルールを守る王道パターンだよ✨([Clean Coder Blog][2])

> つまり：
> **ユースケースは「こういう形で結果を渡すよ」だけ約束して、
> “どう表示するか/どうHTTPにするか” は外側がやる🎤**

---

## 2) 「UseCaseの戻り値」はどうするの？（超大事）🧠💥

![Output Port vs Return](./picture/clean_cs_study_021_why_output_port.png)



初心者が一番やりがちな事故はこれ👇💦

* ✅やりたい：`return Ok(...)` とか `ActionResult` を返す
* ❌でもそれは **ASP.NET Core の型**だから外側の都合…！

ユースケースが `ActionResult` や `HttpResponse` を返した瞬間に、内側が外側依存になっちゃう😭

だから基本はこう👇

### ✅方針A（おすすめ）：ユースケースは「Output Port を呼ぶ」だけ🎯

* ユースケースは `outputPort.Present(...)` を呼ぶ
* 返すなら `Task` だけ（結果データは引数で渡す）

---

## 3) ResponseModel（出力データ）ってなに？📦✨

![Response Model Content](./picture/clean_cs_study_021_response_model.png)



Output Port には、だいたい **ResponseModel** を渡すよ！

ResponseModel は「ユースケースが外へ伝えたい結果」を表す、**ユースケース用の“出力DTO”** みたいなもの😊
ただし **APIレスポンスDTO** と同一にしないのがコツ！

### ResponseModel の鉄則💎

* ✅ “結果として必要な情報” だけ持つ（最小限）
* ✅ 表示のための整形（文字列フォーマット、ローカライズ）は入れない
* ✅ HTTPコード、ヘッダ、URL、ページングリンク…みたいな **Web都合は入れない**
* ✅ Domain Entity をそのまま返さなくてもOK（返すと漏れがち）

---

## 4) 具体例：メモ作成（CreateMemo）の Output Port を作る✍️📝

![Presenter Implementation](./picture/clean_cs_study_021_presenter_impl.png)



### 4-1. ResponseModel を作る（UseCases 層）📦

`record` が相性いいよ〜（不変で扱いやすい✨）

```csharp
namespace MyApp.UseCases.Memos.CreateMemo;

public sealed record CreateMemoResponse(
    Guid MemoId,
    string Title,
    DateTime CreatedAtUtc
);
```

ポイント🧁

* `DateTime` は “表示形式” じゃなくて “値” のまま（表示はPresenterで！）
* `Title` はVOで持ってても、ResponseModelでは string にしてもOK（方針次第）

---

### 4-2. Output Port（interface）を作る（UseCases 層）🔌➡️

成功と失敗をどう表現するかで設計が分かれるけど、まずは分かりやすい形でいこ💖

#### ✅シンプル版：成功だけ Present

```csharp
namespace MyApp.UseCases.Memos.CreateMemo;

public interface ICreateMemoOutputPort
{
    Task PresentAsync(CreateMemoResponse response, CancellationToken ct = default);
}
```

#### ✅実務寄り：成功/失敗を分ける（おすすめ）⚠️✨

失敗も「仕様」だから、ちゃんと境界で表現しよ〜！

```csharp
namespace MyApp.UseCases.Memos.CreateMemo;

public interface ICreateMemoOutputPort
{
    Task PresentSuccessAsync(CreateMemoResponse response, CancellationToken ct = default);
    Task PresentFailureAsync(CreateMemoFailure failure, CancellationToken ct = default);
}

public sealed record CreateMemoFailure(
    string Code,        // 例: "TitleEmpty", "TitleTooLong"
    string Message      // 例: "タイトルは1文字以上にしてね"
);
```

> ここで `Exception` をそのまま流すより、
> **失敗の種類（Code）** があると外側が扱いやすいよ😊✨

---

### 4-3. Interactor から Output Port を呼ぶ（UseCases 層）🧱

```csharp
namespace MyApp.UseCases.Memos.CreateMemo;

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
        if (string.IsNullOrWhiteSpace(request.Title))
        {
            await _output.PresentFailureAsync(
                new CreateMemoFailure("TitleEmpty", "タイトルは空にできないよ🥺"),
                ct
            );
            return;
        }

        var memo = Memo.CreateNew(request.Title); // Entity側で不変条件を守る想定
        await _repo.SaveAsync(memo, ct);

        var response = new CreateMemoResponse(
            memo.Id.Value,
            memo.Title.Value,
            memo.CreatedAtUtc
        );

        await _output.PresentSuccessAsync(response, ct);
    }
}
```

ここが気持ちよすぎポイント😍

* Interactor が **WebもControllerも知らない**
* `Ok()` とか `BadRequest()` が一切出てこない
* でも結果はちゃんと外へ渡せる🔌✨

---

## 5) なぜ Output Port が効くの？（1番のご褒美）🎁✨

![Controller and Presenter](./picture/clean_cs_study_021_controller_presenter.png)



### ✅UIが増えてもユースケースが無傷💪

たとえば同じ `CreateMemo` を、

* Web API（JSONで返す）
* CLI（コンソール表示）
* デスクトップ（画面表示）

全部で使い回せるよ！

Presenter を差し替えるだけでOK🎤✨
これが “Ports & Adapters / Clean Architecture” の強さだよ〜！([Microsoft Learn][3])

---

## 6) よくあるミス集（ここ踏むと崩れる）💣😇

![Output Port Mistakes](./picture/clean_cs_study_021_common_mistakes.png)



* ❌ Output Port が `ActionResult` を返す（UseCaseがWeb依存）
* ❌ ResponseModel に HTTP ステータスやエラーレスポンス形を入れる（外側都合）
* ❌ Domain Entity をそのまま ResponseModel に詰める（情報漏れ・循環依存の温床）
* ❌ Output Port が汎用すぎる（`IOutputPort` 1個で全部…）→ だいたい地獄😂
  → **UseCaseごとに Output Port を作る**のが安定！

---

## 7) ミニ課題（手を動かすやつ）🧪💖

### 課題A：ResponseModel を削ぎ落とす✂️

`CreateMemoResponse` から「表示都合っぽいもの」を探して削る（例：`CreatedAtText` とか）

### 課題B：失敗パターンを3つ追加⚠️

* タイトル長すぎ
* 禁止文字が含まれる
* 同名メモ禁止（仕様なら）

### 課題C：Presenter を2種類作る（次章への伏線）🎤✨

* Web用Presenter（APIレスポンスへ変換）
* CLI用Presenter（Console表示へ変換）

ユースケースは一切変えないのが勝ち🏆

---

## 8) AIに手伝わせるプロンプト例🤖✨

そのままコピペでOKだよ〜！

* 「CreateMemo の Output Port を、成功/失敗を含めて **C#のinterface**で3案出して。メリデメも🙏」
* 「ResponseModel に **入れるべき/入れないべき** を箇条書きで。理由つきで！」
* 「この Interactor は責務が肥大してる？Output Port の呼び方は適切？レビューして🧐」
* 「Failure の Code 設計を提案して。運用で増えても破綻しない形にして！」

---

## 9) 章末チェックリスト✅✨

* Output Port は **UseCases（内側）** に置いた？
* ResponseModel は **HTTP/UI/DB を一切知らない**？
* Interactor は **Output Port を呼ぶだけ**になってる？
* 失敗も “仕様” として外へ渡せる？⚠️

---

次の「第22章」で Presenter を作ると、今日作った Output Port が一気に気持ちよく繋がるよ〜！🎤➡️💖
もし「Web API用の Presenter を Minimal API で薄く書く例」も続けて欲しかったら、そのまま第22章として出すね😊✨

[1]: https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-14?utm_source=chatgpt.com "What's new in C# 14"
[2]: https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html?utm_source=chatgpt.com "Clean Architecture by Uncle Bob - The Clean Code Blog"
[3]: https://learn.microsoft.com/en-us/dotnet/architecture/modern-web-apps-azure/common-web-application-architectures?utm_source=chatgpt.com "Common web application architectures - .NET"
