# 第17章：Resultの中身設計（どの情報を持たせる？）🧾🧠

Resultって「成功/失敗の箱」🎁なんだけど、**失敗側に入れる情報の設計**で、使いやすさも運用の強さもぜんぜん変わるよ〜！😳✨
ここで作るのは、次の章以降（APIのProblemDetailsやログ方針）にもそのまま繋がる“芯”💪

ちなみに今どきの.NETは **.NET 10（2025-11-11リリース、LTS）** が軸で進む感じだよ🪟✨ ([Microsoft for Developers][1])
APIのエラー返却も **Problem Details（RFC 9457）** が現行の標準で、RFC 7807を置き換え（obsoletes）してるよ🧾 ([RFCエディタ][2])
ASP.NET Core でも `AddProblemDetails()` を使う流れがちゃんと案内されてる🧩 ([Microsoft Learn][3])

---

## 1) まず結論：Errorに入れる情報は「誰のため？」で決める👥🎯

失敗の情報って、実は“受け取り手”が複数いるの👇

* ユーザー向け：画面に出す文言💬🎀（やさしく、短く、原因を責めない）
* 開発者向け：調査に必要なヒント🔎🧠（例外種別、文脈、依存先）
* 運用/サポート向け：問い合わせ対応の材料📞🧾（コード、再現条件）
* 機械向け：分岐判断の材料🤖🚦（retryable か、カテゴリは何か、など）

だから、**Errorは「表示用」と「調査用」を混ぜない**のが超だいじ！🙅‍♀️💥
混ぜると「SQLのエラーをユーザーに見せちゃった…」みたいな事故が起きる😱

---

## 2) “ちょうどいい”Error設計のおすすめセット🧰✨

### 最小構成（第16章のResultに足すならまずコレ）🥚➡️🐣

* `Code`：**安定した識別子**（ログ集計・問い合わせ・API仕様で核になる）🏷️
* `UserMessage`：ユーザーに見せる文章💬
* `Category`：ドメイン / インフラ / バグ（第6章の地図に戻れる🗺️）🧩

### 実戦構成（運用・UXまで見据えるならコレ）🔥

* `Retryable`：再試行していい？🔁
* `Action`：ユーザーに次にしてほしいこと（例：再試行、時間をおいて、入力修正）👉
* `DevMessage`：開発者向け説明（ユーザーには出さない）🧑‍💻
* `Meta`：調査に役立つ追加情報（例：`endpoint`, `productId`, `dependency`, `timeoutMs`）🧾
* `FieldErrors`：入力エラーを項目別に出す（UIが超やさしくなる）🪞✨

---

## 3) ありがちな設計ミスあるある🙅‍♀️💥（先に潰そ！）

### ❌ Codeが無い（または毎回変わる）

* 問い合わせ「このエラー何？」→追えない😵‍💫
* ログ集計「多い失敗どれ？」→集計できない📉

### ❌ UserMessageに内部情報を混ぜる

* 例外メッセージ、SQL、URL、スタックトレース…⚠️
  → セキュリティ的にもUX的にもアウト😱

### ❌ ErrorにExceptionそのものを入れて運び回る

* シリアライズ地獄になりがち＆境界を越えて漏れる危険💣
  例外は「境界で捕まえてログ」🧯、上には**整形したError**を渡すのが安全✨

---

## 4) おすすめの型（そのまま雛形にしてOK）🧷✨

![App Error Structure](./picture/err_model_cs_study_017_app_error_structure.png)

「Resultは第16章の最小構成を維持」しつつ、Errorを強化する版だよ🎁
（この章のゴールは“中身設計”なので、作り込みすぎずスッキリで！）

```csharp
public enum ErrorCategory
{
    Domain,   // 業務ルール違反（想定内の失敗）
    Infra,    // DB/ネットワーク/外部API（想定内の失敗）
    Bug       // 不変条件違反など（想定外）
}

public sealed record FieldError(
    string Field,
    string Message,
    string? Code = null
);

public sealed record AppError(
    string Code,                 // 安定した識別子（例: "ORDER_OUT_OF_STOCK"）
    string UserMessage,          // ユーザー表示（安全な文言）
    ErrorCategory Category,
    bool Retryable = false,      // 再試行していい？
    string? Action = null,       // 次にしてほしい行動（例: "RetryLater"）
    string? DevMessage = null,   // 開発者向け補足（ユーザーには出さない）
    IReadOnlyDictionary<string, object?>? Meta = null,
    IReadOnlyList<FieldError>? FieldErrors = null
);
```

### Code命名のコツ🏷️✨

* **英大文字＋アンダースコア**が扱いやすい（ログ/検索/文書化）🔎
* “場所”じゃなく“意味”で付ける

  * ❌ `DB_TIMEOUT`（場所寄り）
  * ✅ `PAYMENT_SERVICE_TIMEOUT`（意味＋依存先が分かる）
* 将来、エラーカタログ（第13章）に載せやすい形にする📚✨

---

## 5) 「表示用」と「ログ用」を分ける設計の書き方🪞🔎

![UI vs Log](./picture/err_model_cs_study_017_ui_vs_log.png)

同じ失敗でも、こう分けると事故りにくいよ👇

### 例：外部APIがタイムアウトした（インフラ）🌩️⏳

* ユーザー表示：
  「通信が混み合っています。少し時間をおいてもう一度お試しください🙏」💬
* ログ用：
  `dependency=payment`, `timeoutMs=3000`, `endpoint=/pay`, `traceId=...` など🧾

```csharp
var err = new AppError(
    Code: "PAYMENT_SERVICE_TIMEOUT",
    UserMessage: "通信が混み合っています。少し時間をおいてもう一度お試しください🙏",
    Category: ErrorCategory.Infra,
    Retryable: true,
    Action: "RetryLater",
    DevMessage: "Payment API timeout.",
    Meta: new Dictionary<string, object?>
    {
        ["dependency"] = "payment",
        ["timeoutMs"] = 3000,
        ["endpoint"] = "/pay"
    }
);
```

---

## 6) FieldErrors（項目別エラー）があるとUIが一気に優しくなる🎀✨

たとえば入力チェックのResult失敗にこう入れる👇

```csharp
var err = new AppError(
    Code: "VALIDATION_FAILED",
    UserMessage: "入力内容を確認してください🙏",
    Category: ErrorCategory.Domain,
    FieldErrors: new[]
    {
        new FieldError("email", "メールアドレスの形式が正しくありません", "INVALID_EMAIL"),
        new FieldError("age", "年齢は18以上で入力してください", "AGE_TOO_LOW")
    }
);
```

UI側は「フォームの横に出す」だけで超親切になるよ🪞💗

---

## 7) ミニ演習📝✨（“同じエラー”を2つに書き分けよう！）

### お題🎀

「在庫不足」で購入できなかったケースを、次の2種類で書いてね👇

1. **画面に出す用**（UserMessage / Action 중심）💬
2. **ログに残す用**（DevMessage / Meta 중심）🔎

### 例の答え（こういう感じ！）✅

```csharp
// 画面に出す用（ユーザー向け）
var uiErr = new AppError(
    Code: "ORDER_OUT_OF_STOCK",
    UserMessage: "ごめんね🙏 在庫が足りなくて購入できなかったよ。入荷を待つか、数量を減らしてみてね🛍️",
    Category: ErrorCategory.Domain,
    Retryable: false,
    Action: "ChangeQuantity"
);

// ログに残す用（開発/運用向け）
var logErr = uiErr with
{
    DevMessage = "Stock insufficient for order.",
    Meta = new Dictionary<string, object?>
    {
        ["productId"] = 12345,
        ["requestedQty"] = 3,
        ["availableQty"] = 1
    }
};
```

ポイントは、**UI用に内部数量を出さない**こと！（「残り1個です！」が仕様なら別だけどね😉）

---

## 8) AI活用🤖✨（この章でめちゃ効く使い方）

### ✅ 1) ユーザー文言を“やさしく”言い換え

* プロンプト例💬
  「次のエラー文を、女子大生向けに“短く・責めない・次の行動が分かる”感じで3案ください：『在庫が不足しています』」

### ✅ 2) Code命名案を量産して、あなたが選ぶ🏷️

* 「“支払いタイムアウト”のCodeを10案。英大文字＋アンダースコア。依存先名も入れて」

### ✅ 3) Metaの候補（調査に役立つ項目）を洗い出し🔎

* 「PAYMENT_SERVICE_TIMEOUT でログに残すべきMeta項目を、PIIを避けて列挙して」

※最後に決めるのはあなた（AIは案出し担当）🤝✨

---

## 9) まとめ🎓✨（第17章の持ち帰り）

* Errorは「誰のための情報？」で設計する👥🎯
* **Code / UserMessage / Category** は最優先セット🏷️💬🧩
* **Retryable / Action / DevMessage / Meta / FieldErrors** があると運用とUXが強くなる🔥
* 「表示用」と「ログ用」を混ぜないのが安全＆上品🪞🔎

次の第18章は、このResultを**呼び出し側が読みやすく扱う書き方（switch/Matchの感覚）**に進むよ〜🔀✨

[1]: https://devblogs.microsoft.com/dotnet/announcing-dotnet-10/ "Announcing .NET 10 - .NET Blog"
[2]: https://www.rfc-editor.org/rfc/rfc9457.html?utm_source=chatgpt.com "RFC 9457: Problem Details for HTTP APIs"
[3]: https://learn.microsoft.com/en-us/aspnet/core/fundamentals/error-handling-api?view=aspnetcore-10.0 "Handle errors in ASP.NET Core APIs | Microsoft Learn"
