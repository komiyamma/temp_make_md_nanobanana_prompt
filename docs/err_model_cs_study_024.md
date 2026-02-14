# 第24章：ログ設計① 何を残す？（構造化ログ）🔎🧾

## この章のゴール🎯

「あとから原因に辿りつけるログ」を、**迷わず設計できる**ようになることだよ😊
とくに今回は **“構造化ログ（structured logging）”** を軸に、
「何を」「どのレベルで」「どんな形で」残すかを決めるよ〜🧠✨ ([Microsoft Learn][1])

---

## 1) そもそもログって何のため？📌

ログはざっくり言うと、この3つのためにあるよ🧾✨

1. **調査（トラブル対応）**：なぜ失敗した？どこで？🕵️‍♀️
2. **運用（監視・傾向）**：最近エラー増えてない？📈
3. **説明（行動の証跡）**：ユーザーが何をした？🧍‍♀️🛒

ここで大事なのは…
ログは **「気持ち」じゃなくて「あとから検索して答えが出る形」** にすること！🔍✨

---

## 2) 構造化ログってなに？🧩✨（超重要！）

![Structured Log](./picture/err_model_cs_study_024_structured_log.png)

### ❌ ありがちな“文字ログ”

* `"購入に失敗しました。ユーザーID=123 商品ID=ABC 在庫=0"`
  → 文字列の中に情報が埋まってて、検索・集計がつらい😵‍💫

### ✅ 構造化ログ（structured）

* メッセージは **テンプレ**
* 値は **プロパティ（フィールド）** として別で持つ

`ILogger` はこういう **高性能で構造化向きのログ** をサポートしてるよ✨ ([Microsoft Learn][2])

例（イメージ）👇

* message: `"Purchase failed for {UserId} with {ProductId}"`
* props: `{ UserId: 123, ProductId: "ABC" }`

こうすると **UserId=123 で検索** とか **ProductIdごとの失敗率集計** が一気にラクになるよ〜🥰

---

## 3) ログレベルの基本セット🎚️✨（迷子防止）

![Log Levels Hierarchy](./picture/err_model_cs_study_024_log_levels.png)

ざっくり指針はこれ👇

* **Trace / Debug**：開発中の細かい流れ（本番は基本OFF寄り）🐾
* **Information**：正常な重要イベント（購入開始・完了など）✅
* **Warning**：放置すると困るかも（リトライで回復した、外部が遅い等）⚠️
* **Error**：処理として失敗（注文作成できなかった等）❌
* **Critical**：サービスとしてヤバい（DB壊滅、起動不能級）🔥

フィルタは **設定（Configuration）でやるのが推奨**だよ🛠️ ([Microsoft Learn][1])

---

## 4) 「何を残す？」の最小チェックリスト✅🧾

![Log Content Checklist](./picture/err_model_cs_study_024_log_checklist.png)

ログに入れる情報は、基本このへんが強いよ💪✨

### A. 追跡に必要な“軸”🧵

* **ErrorCode**（エラーカタログのコード）🏷️
* **ErrorType**（Domain / Infra / Bug）🧩
* **Operation**（何の処理？ 例: `Purchase`）🎯
* **EntityId**（注文ID/商品IDなど）🆔
* **UserId（または匿名ID）** 🙋‍♀️

### B. 原因に近づく“状況”🌦️

* 外部依存の情報（例：`Provider=PaymentX`, `HttpStatus=503`）🌐
* リトライ可否（`Retryable=true/false`）🔁
* 実行時間（`ElapsedMs`）⏱️

### C. 例外（Exception）は“丸ごと”扱う🧯

* **例外があるときは例外オブジェクトも渡す**（stack traceが超重要）
  → `LogError(ex, "...")` みたいにね😊

---

## 5) エラー分類（ドメイン/インフラ/バグ）ごとのログ方針🚦✨

![Category Logging Strategy](./picture/err_model_cs_study_024_category_strategy.png)

ここが「エラーモデリング」らしさポイントだよ🫶

### 5-1) ドメインエラー（想定内の失敗）💗

例：在庫不足、予算オーバー、期限切れ

* 基本：**Information 〜 Warning**（重要度で）
* 例外：**通常は付けない**（想定内だから）
* 残すもの：`ErrorCode`, `UserId`, `ProductId`, `Reason` など

👉 コツ：
**“ユーザーに優しい失敗”は、ログでも「想定内」とわかるように**する✨

### 5-2) インフラエラー（DB/ネット/外部API）🌩️

例：DB接続失敗、外部API 503

* 基本：**Warning（回復した） / Error（回復できず失敗）**
* 例外：**付ける**（原因解析が必要）
* 残すもの：`Provider`, `HttpStatus`, `Timeout`, `Retryable`, `ElapsedMs`

### 5-3) バグ（不変条件違反）⚡🧱

例：ありえない状態、null前提崩壊

* 基本：**Error 〜 Critical**
* 例外：**付ける（必須）**
* 残すもの：`Invariant`, `StateSnapshot(必要最小限)`, `ErrorCode(BUG系)`
* 目的：**すぐ直すための情報**🔥

---

## 6) C#での構造化ログ：最低限の書き方✍️✨

![Structured vs String Interpolation](./picture/err_model_cs_study_024_structured_vs_string.png)

`ILogger` のテンプレログはこんな感じ😊 ([Microsoft Learn][2])

```csharp
logger.LogInformation(
    "Purchase started. UserId={UserId} ProductId={ProductId} Quantity={Quantity}",
    userId, productId, quantity);
```

### 🙅‍♀️ やりがち注意

* 文字列補間でログを作る：`$"UserId={userId}"`
  → 構造化が弱くなる（検索・集計が辛くなる）になりやすい💦

---

## 7) スコープ（BeginScope）で“文脈”を付ける🧠🧵

![Log Scope Container](./picture/err_model_cs_study_024_scope_container.png)

「この処理中のログ全部に UserId を付けたい！」みたいなとき便利✨

```csharp
using (logger.BeginScope(new Dictionary<string, object>
{
    ["UserId"] = userId,
    ["Operation"] = "Purchase"
}))
{
    logger.LogInformation("Validating request");
    logger.LogInformation("Saving order");
}
```

さらに、.NET のロギングは **トレース文脈（TraceId/SpanId 等）をログに乗せる設定**もできるよ🧵✨（相関は次章で本格的にやるね） ([NuGet][3])

---

## 8) 高性能ログ：LoggerMessage（ソースジェネレータ）🌪️✨

![LoggerMessage Performance](./picture/err_model_cs_study_024_logger_message.png)

ログは地味に頻度が高いから、性能も大事だよ〜😌
`LoggerMessageAttribute` を使うと、**実行時の割り当て等を減らして高速化**できる仕組みが用意されてるよ🚀 ([Microsoft Learn][4])

```csharp
internal static partial class Log
{
    [LoggerMessage(
        EventId = 1201,
        Level = LogLevel.Information,
        Message = "Purchase completed. OrderId={OrderId} UserId={UserId}")]
    public static partial void PurchaseCompleted(ILogger logger, string orderId, string userId);
}
```

使う側👇

```csharp
Log.PurchaseCompleted(logger, orderId, userId);
```

---

## 9) 成果物：「ログ方針 1枚シート」📄✨（テンプレ）

![Log Policy Sheet](./picture/err_model_cs_study_024_policy_sheet.png)

この章のミニ成果物はこれ！📌（そのままコピペして埋めてOK💗）

* **目的**：障害調査 / 運用 / 監査（必要なら）
* **ログレベル運用**：

  * Domain：Info/Warn
  * Infra：Warn/Error（例外あり）
  * Bug：Error/Critical（例外あり）
* **必須フィールド**：

  * `ErrorCode`, `ErrorType`, `Operation`, `UserId(匿名ID)`, `EntityId`, `ElapsedMs`
* **例外の方針**：

  * Infra/Bug は例外込みで記録、Domain は基本例外なし
* **機密情報ルール**：

  * パスワード、トークン、カード情報、個人情報は原則ログに出さない🙅‍♀️🔒
* **イベントID方針**：

  * 主要イベントは EventId を付ける（例：購入完了=1201）🎫

---

## 10) ミニ演習📝✨（30〜45分目安）

### お題：推し活グッズ購入🛍️💖

1. 「購入開始」「検証失敗（ドメイン）」「外部決済失敗（インフラ）」「不変条件違反（バグ）」の4箇所にログを入れる
2. それぞれ **ErrorType / ErrorCode / EntityId / UserId** を構造化で入れる
3. ログ方針シートを埋める📄✨

---

## 11) AI活用🤖✨（この章で強い使い方）

AIは「案出し・漏れチェック」に使うのが超相性いいよ🫶

### ✅ そのまま使えるプロンプト例

* 「この処理（購入）で、ログに残すべきフィールド候補をチェックリスト化して」
* 「このログ、構造化として検索しやすい？ 改善案出して」
* 「Domain/Infra/Bug のどれとして記録するのが自然？理由も添えて」
* 「PII/機密情報が混ざってないか観点を列挙して」🔒

---

## まとめ🎀✨

* ログは **“検索して答えが出る形”** が正義🔍
* **構造化ログ**で、値はプロパティとして残す🧩
* エラー分類（Domain/Infra/Bug）で **レベル・例外の扱い**を分ける🚦
* `LoggerMessage` で **高性能ログ**もできる🚀 ([Microsoft Learn][4])
* 成果物は **「ログ方針 1枚シート」**📄✨

次の第25章で、ここに **相関ID（TraceId/CorrelationId）** を載せて「1リクエストを追える」状態にして、ミニ総合演習まで完成させようね〜🧵🎓✨ ([OpenTelemetry][5])

[1]: https://learn.microsoft.com/en-us/aspnet/core/fundamentals/logging/?view=aspnetcore-10.0&utm_source=chatgpt.com "Logging in .NET and ASP.NET Core"
[2]: https://learn.microsoft.com/en-us/dotnet/core/extensions/logging?utm_source=chatgpt.com "Logging in C# - .NET"
[3]: https://www.nuget.org/packages/microsoft.extensions.logging/?utm_source=chatgpt.com "Microsoft.Extensions.Logging 10.0.2"
[4]: https://learn.microsoft.com/en-us/dotnet/core/extensions/logger-message-generator?utm_source=chatgpt.com "Compile-time logging source generation - .NET"
[5]: https://opentelemetry.io/docs/languages/dotnet/logs/correlation/?utm_source=chatgpt.com "Log correlation"
