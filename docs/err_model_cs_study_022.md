# 第22章：APIエラー設計② ProblemDetails（RFC 9457）🧾✨

この章では **「APIの失敗レスポンスを“標準の形”で返す」** をやるよ〜😊
ゴールはシンプル👇

* クライアントが **失敗を機械的に扱える**（分岐しやすい）🤖✨
* 人間も **状況がすぐ分かる**（運用しやすい）👀🔎
* しかも **エラーを増やしても破綻しにくい** 🧱💪

---

## 1) ProblemDetailsってなに？🧠🧾

**ProblemDetails** は、HTTP API のエラー内容を返すための **標準JSONフォーマット** だよ📦✨
RFC 9457 では、JSONとして返すときのメディアタイプが **`application/problem+json`** って決まってるよ。 ([RFCエディタ][1])

たとえば 403 の例はこんな感じ（RFCの例と同じ雰囲気）👇 ([RFCエディタ][1])

```json
{
  "type": "https://example.com/probs/out-of-credit",
  "title": "You do not have enough credit.",
  "detail": "Your current balance is 30, but that costs 50.",
  "instance": "/account/12345/msgs/abc",
  "balance": 30,
  "accounts": ["/account/12345", "/account/67890"]
}
```

ここで大事なのは **「type が“エラーの種類ID”」になってる**こと！🆔✨
クライアントは `type` を見て、分岐・表示・リトライ判断がしやすくなるよ〜😊

---

## 2) 5つの基本フィールド（まずこれだけ覚えよう）🖐️✨

![Problem Details Document](./picture/err_model_cs_study_022_problem_details_doc.png)

RFC 9457 の基本メンバーはこの5つ👇 ([RFCエディタ][1])

### ✅ type（最重要）🔑

* **問題タイプ（エラー種別）のID**（URI）
* 無い場合は **`about:blank`** がデフォルトになるよ。 ([RFCエディタ][1])
* できれば **絶対URI推奨**（相対URIは混乱しやすいよ〜ってRFCも言ってる）🌀 ([RFCエディタ][1])
* `type` が https なら、そのURLを開いたとき **人間向け説明（HTMLなど）** があるのが望ましい（ただしクライアントが勝手に自動アクセスするのは非推奨）📄⚠️ ([RFCエディタ][1])

### ✅ title（短い見出し）📰

* **短い要約**（原則タイプごとに固定、翻訳だけ変えてOK）🌍 ([RFCエディタ][1])

### ✅ status（HTTPステータスのコピー）🚦

* HTTPレスポンスのステータスコードを入れる
* ただし **HTTPのステータスと一致させる必要あり**（ズレると事故る）⚠️ ([RFCエディタ][1])

### ✅ detail（今回の事情）🧩

* **この発生に固有の説明**（ユーザーが直せる方向へ！）🫶
* **debug情報をベラベラ書かない**＆ **detail を機械解析しない**（欲しい情報は拡張で！）ってRFCが明言してるよ。 ([RFCエディタ][1])

### ✅ instance（今回の出来事ID）🪪

* **この発生（occurrence）を識別するURI**
* サポート/調査で「あのエラーどれ？」が一発になるやつ！🔎 ([RFCエディタ][1])

---

## 3) 拡張フィールド（Extensions）で“あなたのAPI仕様”を入れる🎀✨

ProblemDetailsは **基本5つ＋自由な追加メンバー** がOK！
RFCではこれを **Extension Members** と呼んでいて、**知らない拡張は無視できる設計**になってるよ（これが強い💪） ([RFCエディタ][1])

✅ 追加しがちなおすすめ拡張👇

* `code`：エラーカタログのエラーコード 🏷️
* `category`：Domain / Infrastructure / Bug（第6章の分類）🧩
* `retryable`：リトライしていい？🔁
* `traceId` / `correlationId`：ログ追跡用🧵🔎
* `errors`：バリデーション詳細（複数件）📝

RFCの例だと、バリデーションは `errors` という拡張で **配列＋pointer** を入れてたよ。 ([RFCエディタ][1])

> ✅注意：複数の“別タイプの問題”が同時に起きたら、RFCは「いちばん重要な問題を返すのがおすすめ」って言ってるよ（なんでも盛り合わせにしない）🍱❌ ([RFCエディタ][1])

---

## 4) type（問題タイプURI）をどう設計する？🧭✨

ここ、センス出る！😆
おすすめはこの2択👇

### A) 自分のドメインで管理（いちばん運用しやすい）🏠

例：

* `https://api.example.com/problems/out-of-stock`
* `https://api.example.com/problems/budget-exceeded`

`type` のURLを開いたら、**人間向けの説明ページ**（原因/対処/例）を置けると最高📄✨ ([RFCエディタ][1])

### B) 既存の登録済みタイプを再利用（相互運用したい時）♻️

IANAに **HTTP Problem Types レジストリ** があるよ！📚
`about:blank` 以外にも、登録済みのタイプが載ってる（増えていく）✨ ([iana.org][2])

---

## 5) Result → ProblemDetails 変換マップを作ろう🗺️✨（この章のコア！）

第21章で決めた「ステータス」と、第6章の「分類」、第13章の「エラーカタログ」を合体させるよ〜😊

### 変換の基本ルール（おすすめ）📌

* **Domainエラー**：クライアントが直せる

  * `type`：ドメイン問題URI
  * `title`：短い固定
  * `detail`：今回の事情（ただし安全な範囲）
  * `extensions`：`code`, `errors` など

* **Infrastructureエラー**：再試行の可能性

  * `retryable: true/false` を拡張に入れる🔁
  * 状況により **Retry-After** ヘッダも検討（RFCは問題タイプ定義でRetry-Afterを使ってよいと言ってる）⏳ ([RFCエディタ][1])

* **Bug（不変条件違反）**：ユーザーに詳細を見せない

  * `type`：`about:blank` でもOK（追加意味なし） ([RFCエディタ][1])
  * `detail`：固定の一般文言（ログにだけ詳細）🧯

---

## 6) C#での実装（Minimal API例）🧰✨

### (1) まずは Results.Problem の形を知ろう📌

`Results.Problem(...)` は **detail / instance / status / title / type / extensions** を渡せるよ。 ([Microsoft Learn][3])

### (2) 変換コード例（Result → IResult）🎁➡️🧾

```csharp
using Microsoft.AspNetCore.Mvc;

public enum ErrorCategory { Domain, Infrastructure, Bug }

public sealed record AppError(
    string Code,
    string Title,          // タイプごとに固定の短い見出し
    string Detail,         // 今回の事情（安全な範囲）
    ErrorCategory Category,
    bool Retryable = false,
    string? Type = null,   // problem type URI
    IDictionary<string, object?>? Extra = null
);

public readonly struct Result<T>
{
    public bool IsSuccess { get; }
    public T? Value { get; }
    public AppError? Error { get; }

    private Result(T value) { IsSuccess = true; Value = value; Error = null; }
    private Result(AppError error) { IsSuccess = false; Value = default; Error = error; }

    public static Result<T> Ok(T value) => new(value);
    public static Result<T> Fail(AppError error) => new(error);
}

public static class ResultToProblemDetails
{
    public static IResult ToHttpResult<T>(this Result<T> result, HttpContext http)
    {
        if (result.IsSuccess) return Results.Ok(result.Value);

        var e = result.Error!;

        // Chapter21で決めたステータス方針をここに寄せる（例）
        var statusCode = e.Category switch
        {
            ErrorCategory.Domain => 400,
            ErrorCategory.Infrastructure => e.Retryable ? 503 : 502,
            ErrorCategory.Bug => 500,
            _ => 500
        };

        // instance は「今回の出来事ID」：ここではリクエストパス＋traceId風
        var instance = $"{http.Request.Path}#{http.TraceIdentifier}";

        var extensions = new Dictionary<string, object?>
        {
            ["code"] = e.Code,
            ["category"] = e.Category.ToString(),
            ["retryable"] = e.Retryable,
            ["traceId"] = http.TraceIdentifier
        };

        if (e.Extra is not null)
        {
            foreach (var (k, v) in e.Extra) extensions[k] = v;
        }

        // Bugは情報を出しすぎない（detailは固定に寄せるなどが安全）
        var safeDetail = e.Category == ErrorCategory.Bug
            ? "予期しないエラーが発生しました。時間をおいて再度お試しください。"
            : e.Detail;

        return Results.Problem(
            detail: safeDetail,
            instance: instance,
            statusCode: statusCode,
            title: e.Title,
            type: e.Type ?? "about:blank",
            extensions: extensions
        );
    }
}
```

💡ポイント

* `type` は **できれば絶対URI**（安定IDにする） ([RFCエディタ][1])
* `detail` は **直し方寄り**、解析用は拡張へ（RFCが推奨） ([RFCエディタ][1])
* 拡張は **知らなければ無視される前提**だから、あとから増やしやすい✨ ([RFCエディタ][1])

---

## 7) フレームワーク側の ProblemDetails 自動生成も使おう🤝✨

ASP.NET Core では、ProblemDetails を自動生成＆カスタムできる仕組みが用意されてるよ〜😊
代表的には👇

* `AddProblemDetails()` でサービス登録
* `UseExceptionHandler()` / `UseStatusCodePages()` と組み合わせ
* カスタムは

  * `ProblemDetailsOptions.CustomizeProblemDetails`
  * `IProblemDetailsWriter`
  * `IProblemDetailsService.WriteAsync`
    などが使えるってMicrosoft Learnにまとまってるよ📚✨ ([Microsoft Learn][4])

たとえば `CustomizeProblemDetails` で拡張を追加できる（Learnの例）👇 ([Microsoft Learn][4])

```csharp
builder.Services.AddProblemDetails(options =>
    options.CustomizeProblemDetails = ctx =>
        ctx.ProblemDetails.Extensions.Add("nodeId", Environment.MachineName));
```

---

## 8) ミニ演習🧪✨（Result→ProblemDetails変換マップ作り）

### 🎯 お題：購入APIの失敗をProblemDetailsで統一しよう🛍️💖

**ステップ1：3つだけエラーを作る**（カタログの最小版）🏷️

* `OUT_OF_STOCK`（Domain）
* `PAYMENT_TIMEOUT`（Infrastructure, Retryable=true）
* `INVARIANT_BROKEN`（Bug）

**ステップ2：各エラーの ProblemDetails を設計**🗺️

* `type`（URI）
* `title`（固定）
* `detail`（今回の事情）
* `extensions`（code/category/retryable/traceId など）

**ステップ3：変換コードを実装**🎁➡️🧾

* 成功は `200 OK`
* 失敗は `Results.Problem(...)` に統一

**ステップ4：チェック✅**

* `Content-Type` が `application/problem+json` になってる？ ([RFCエディタ][1])
* `status` とHTTPステータスが一致してる？ ([RFCエディタ][1])
* `type` が安定IDになってる？（相対URIにしてない？） ([RFCエディタ][1])

---

## 9) AI活用コーナー🤖💬（おすすめプロンプト付き）

### ① `type/title/detail` の文章を整える✍️✨

**プロンプト例：**
「次のエラーカタログから、ProblemDetailsの `type/title/detail` の案を作って。titleは短く固定、detailは今回の事情で“直し方寄り”。機密情報は含めない。コードは `OUT_OF_STOCK` …」

### ② extensions設計の相談🧠🧾

「クライアントが分岐しやすい extensions を提案して。`code/category/retryable/traceId` は必須。バリデーションの複数エラー表現も案を2つ出して。」

### ③ 変換テーブル（Result→ProblemDetails）をレビュー👀✅

「この変換マップの矛盾（status/title/type/detailの責務ズレ）を指摘して、改善案を出して。」

---

## まとめ🎀✨

* **ProblemDetailsは“失敗の標準フォーマット”**で、`type` が超重要🆔✨ ([RFCエディタ][1])
* **基本5要素＋拡張（extensions）**で、機械にも人にも優しいAPIになる🤖🫶 ([RFCエディタ][1])
* C#では `Results.Problem(...)` と `AddProblemDetails()` で実装しやすいよ🧰✨ ([Microsoft Learn][3])
* `detail` は「直し方寄り」、機械が読む情報は **extensions** へ📌 ([RFCエディタ][1])

---

次の第23章（UIエラー設計）では、**ProblemDetailsの“中身”をどうユーザー向け文言に落とすか**（出す/隠す・再試行誘導・項目別エラー）を、もっとやさしく整理していくよ〜🫶🎀😊

[1]: https://www.rfc-editor.org/rfc/rfc9457.html "RFC 9457: Problem Details for HTTP APIs"
[2]: https://www.iana.org/assignments/http-problem-types/http-problem-types.xhtml "Hypertext Transfer Protocol (HTTP) Problem Types"
[3]: https://learn.microsoft.com/en-us/dotnet/api/microsoft.aspnetcore.http.results.problem?view=aspnetcore-10.0&utm_source=chatgpt.com "Results.Problem Method (Microsoft.AspNetCore.Http)"
[4]: https://learn.microsoft.com/ja-jp/aspnet/core/fundamentals/error-handling?view=aspnetcore-10.0 "ASP.NET Core のエラーを処理する | Microsoft Learn"
