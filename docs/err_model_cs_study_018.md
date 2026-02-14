# 第18章：Resultの扱い方（switch/Matchの感覚）🔀✨

この章はね、**「Result を受け取った側が、読みやすく・事故らず・迷わず分岐できる」**ようになる回だよ〜😊💪
（2026年1月時点だと .NET 10 は LTS で、1/13 に 10.0.2 が出てるよ🧊✨） ([Microsoft][1])
C# 14 も 2025年11月にリリース済みだよ〜🧡 ([Microsoft Learn][2])

---

## 1) Result を受け取ったら「まず失敗をその場で確定」🛑➡️✅

![Railway Switch](./picture/err_model_cs_study_018_railway_switch.png)

Result を受け取る側の鉄板はこれ👇
**「成功だけ先へ。失敗はその場で return（もしくは UI 表示）」**✨

* ✅ ネストが増えない（if地獄回避）
* ✅ 失敗の扱いが統一される
* ✅ “どこで失敗したか”が追いやすい🔎

---

## 2) 今日のサンプル（Result と Error）🎁🧾

第16〜17章で作った “最小Result” を想定して、受け取り側の練習をするね😊
（ここでは **Match / switch** を使うために、必要な形だけ置くよ）

```csharp
public abstract record AppError(string Code, string Message);

public sealed record DomainError(string Code, string Message) : AppError(Code, Message);
public sealed record InfraError(string Code, string Message, bool Retryable) : AppError(Code, Message);
public sealed record BugError(string Code, string Message) : AppError(Code, Message);

public readonly record struct Result<T>(T? Value, AppError? Error)
{
    public bool IsSuccess => Error is null;

    public static Result<T> Ok(T value) => new(value, null);
    public static Result<T> Fail(AppError error) => new(default, error);

    public TResult Match<TResult>(Func<T, TResult> onSuccess, Func<AppError, TResult> onFailure)
        => IsSuccess ? onSuccess(Value!) : onFailure(Error!);
}
```

---

## 3) 受け取り側の基本形①：if で “失敗だけ先に返す” 🧯

一番わかりやすい型👇（まずこれでOK！）

```csharp
Result<OrderId> result = purchaseService.Buy(userId, itemId);

if (!result.IsSuccess)
{
    ShowError(ToUiMessage(result.Error!)); // UIに出す
    return;
}

// 成功だけこの先へ✨
OpenThanksPage(result.Value!);
```

ポイントはこれだよ😊💡

* `!result.IsSuccess` を見た瞬間に “この処理は終わり” を確定させる🛑
* 成功したときの処理が **まっすぐ読める** 📖✨

---

## 4) 受け取り側の基本形②：switch で “エラー型ごとに対応を固定” 🔀

Resultの良さは、**失敗の種類を switch で“仕様として分岐”できる**ところ🎯

### UIメッセージを決める例🪞🎀

```csharp
public sealed record UiMessage(string Title, string Body, bool CanRetry);

public static UiMessage ToUiMessage(AppError error) =>
    error switch
    {
        DomainError de => new(
            "入力を確認してね😊",
            de.Message,
            CanRetry: false),

        InfraError ie when ie.Retryable => new(
            "一時的に混み合ってるみたい🥺",
            "少し待ってからもう一度試してみてね🙏",
            CanRetry: true),

        InfraError ie => new(
            "接続に失敗しちゃった…😢",
            "時間をおいて試すか、状況が続くならサポートへ連絡してね📩",
            CanRetry: false),

        BugError => new(
            "ごめんね、システム側の問題かも…🙇‍♀️",
            "同じ操作で再現するなら、手順をメモして連絡してね📝",
            CanRetry: false),

        _ => new(
            "予期しないエラー😵",
            "もう一度試して、だめなら連絡してね🙏",
            CanRetry: false),
    };
```

ここが超大事💖

* **DomainError**：ユーザーの操作で直せる → 優しい案内
* **InfraError**：運用上起きる → リトライ可否で案内を変える🔁
* **BugError**：本来起きない → 速攻で気づけるように扱う⚡

---

## 5) Match を使うと “Result分岐が1か所に集約” できる🎯✨

if でもOKだけど、**UI側で「成功→画面遷移 / 失敗→表示」をまとめたい**時は Match が気持ちいい😊

```csharp
var uiAction = result.Match(
    onSuccess: orderId => new { Kind = "Navigate", OrderId = orderId },
    onFailure: err => new { Kind = "ShowError", Message = ToUiMessage(err) }
);

if (uiAction.Kind == "Navigate")
{
    OpenThanksPage(uiAction.OrderId);
}
else
{
    ShowError(uiAction.Message);
}
```

✅ “成功/失敗の整理” がまず Match の中で終わるから、呼び出し側がスッキリするよ〜🧼✨

---

## 6) ちょい実戦：API風に「成功は200、失敗はいい感じに返す」🌐🚦

（ProblemDetails は第22章でガッツリやるから、ここは雰囲気だけね😊）

```csharp
app.MapPost("/buy", (BuyRequest req, PurchaseService svc) =>
{
    var result = svc.Buy(req.UserId, req.ItemId);

    return result.Match(
        onSuccess: orderId => Results.Ok(new { orderId }),
        onFailure: err => err switch
        {
            DomainError de => Results.BadRequest(new { code = de.Code, message = de.Message }),
            InfraError ie when ie.Retryable => Results.StatusCode(503),
            InfraError => Results.StatusCode(502),
            BugError => Results.StatusCode(500),
            _ => Results.StatusCode(500),
        }
    );
});
```

この形にしておくと、後で **「Result → ProblemDetails」** に置き換えるのが超ラクになるよ🧾✨（第22章への伏線🧵）

---

## 7) よくある事故ポイント（ここだけ避ければ勝ち🥇）⚠️

### 事故①：成功前提で `Value!` を触る😇💥

* **対策**：成功判定（or Match）の中でだけ触る！

### 事故②：失敗を握りつぶして “なんか失敗した” にする🫥

* **対策**：`Domain/Infra/Bug` を保って UI 文言を出し分ける💬

### 事故③：分岐が増えて同じメッセージだらけ🐙

* **対策**：`ToUiMessage()` みたいに **変換を1か所に集約**🧹✨

---

## 8) ミニ演習（手を動かすと一気に身につくよ🧪💕）

### 演習A：ToUiMessage を完成させよう🪞✨

1. `DomainError / InfraError(Retryable true/false) / BugError` を switch で分岐
2. `UiMessage(Title, Body, CanRetry)` を返す
3. **Body は“ユーザーに優しい日本語”**にする😊💬

### 演習B：Result の呼び出し側を “一直線” にしよう📏✨

* Before：`try/catch` でぐちゃぐちゃ
* After：`if (!IsSuccess) return` で早期return
* 成功側は1本道にする🚶‍♀️✨

---

## 9) AI活用（Copilot / Codex向け）🤖🧠✨

そのままコピペで使えるプロンプト例だよ〜📎💕

* ✅ **switch の分岐を作ってもらう**
  「`AppError` の派生型（DomainError/InfraError/BugError）で switch 式を書いて。InfraError は Retryable でメッセージを変えて。戻り値は `UiMessage`。」

* ✅ **文言を“優しい日本語”に整える**
  「このエラーメッセージを、責めない・短い・次にやる行動がわかる文章に直して。絵文字も少し入れて。」

* ✅ **重複削減レビュー**
  「この Result の分岐コード、重複を減らして読みやすくして。変換関数 `ToUiMessage` に寄せたい。」

最後に一言だけ⚠️
AIの提案は便利だけど、**“分類（Domain/Infra/Bug）” の最終決定は自分が握る**のが安全だよ🤝✨

---

## まとめ（この章のゴール達成チェック✅🎓）

* ✅ Result を受け取ったら **失敗をその場で確定（早期return / UI表示）**できる
* ✅ `switch` で **エラー型ごとの対応**を仕様として書ける
* ✅ `Match` で **成功/失敗の分岐を1か所に集約**できる
* ✅ UIメッセージ変換を **1関数にまとめて重複を消せる**🧹✨

---

次の第19章は、この Result を **「つなぐ（伝播）」**回だよ⛓️✨
ネスト地獄を完全に終わらせに行こ〜😊🔁

[1]: https://dotnet.microsoft.com/en-us/platform/support/policy/dotnet-core ".NET and .NET Core official support policy | .NET"
[2]: https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-version-history "The history of C# | Microsoft Learn"
