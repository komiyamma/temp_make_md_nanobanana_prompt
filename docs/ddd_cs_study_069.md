# 第69章：設定値（appsettings.json）とドメインの距離 📏🧠

この章は一言でいうと…
**「ドメインは “設定ファイルの存在” を知らない方が強い」** です 💪✨
（設定を読んでいい場所・ダメな場所をスッキリ分けます😊）

---

## 今日のゴール 🎯😊

* `appsettings.json` の値を、**ドメイン層に漏らさない**ようにできる 🙆‍♀️
* 「それって設定？それともビジネスルール？」を見分けられる 👀✨
* DI（`IOptions<T>`）で **“安全に設定を使う型”** が身につく 🧩✅

![App Settings Injection](./picture/ddd_cs_study_069_appsettings.png)

---

## まず結論：ドメイン層は appsettings を読まない 📵📦

![domain_ignores_settings](./picture/ddd_cs_study_069_domain_ignores_settings.png)

**ドメイン層**は「業務ルールの中心」なので、ここに…

* `IConfiguration`
* `IOptions<>`
* `Microsoft.Extensions.*`
* `appsettings.json` のキー名（例：`"TaxRate": 0.1`）

が登場したら、距離が近すぎです ⚠️😵‍💫

理由はカンタン👇
ドメインが設定に依存すると、将来こうなりがちです：

* 設定キー名を変えたらドメインが壊れる 😱
* テストが面倒（設定読み込みが必要）🧪💦
* 「インフラ都合」がドメインを汚染する 🫠

---

## じゃあ “設定” はどこで読むの？ 🏠🔧

![reading_locations](./picture/ddd_cs_study_069_reading_locations.png)

基本はこの3択です👇

* **Web（入口）**：`Program.cs` / Controller など 🌐
* **Infrastructure（外部）**：DB・外部API・メール送信など 🧱
* **Application（ユースケース）**：ドメインに渡す値を組み立てる 🧑‍🍳

ドメインは **「値を受け取るだけ」** が理想です 🙆‍♀️✨

---

## 例1：外部APIの設定（これは “設定” でOK）🌍⚙️

外部APIの `BaseUrl` とか `Timeout` は、ビジネスルールじゃなくて **環境の都合** なので、`appsettings.json` に置いてOKです😊

### appsettings.json 🗂️

```json
{
  "PaymentApi": {
    "BaseUrl": "https://api.example.com",
    "TimeoutSeconds": 10
  }
}
```

### Options クラス（Infrastructure か Web 側）🧩

```csharp
public sealed class PaymentApiOptions
{
    public required string BaseUrl { get; init; }
    public int TimeoutSeconds { get; init; } = 10;
}
```

### Program.cs でバインドして DI 登録 🧷

```csharp
var builder = WebApplication.CreateBuilder(args);

builder.Services
    .AddOptions<PaymentApiOptions>()
    .Bind(builder.Configuration.GetSection("PaymentApi"))
    .Validate(opt => !string.IsNullOrWhiteSpace(opt.BaseUrl), "PaymentApi:BaseUrl is required")
    .Validate(opt => opt.TimeoutSeconds is >= 1 and <= 60, "TimeoutSeconds must be 1..60")
    .ValidateOnStart();

var app = builder.Build();
app.Run();
```

✅これで「設定が壊れてたら起動時に落ちる」ので、事故が減ります🚑✨

![fail_fast](./picture/ddd_cs_study_069_fail_fast.png)

---

## 例2：「税率」「送料」みたいな数値は注意⚠️（設定に見える罠🕳️）

![rule_vs_config](./picture/ddd_cs_study_069_rule_vs_config.png)

たとえば `TaxRate=0.1`。
これ、つい `appsettings.json` に置きたくなるけど…👀

* 税率が **“業務のルール”** として扱われるなら
  👉 **ドメインの概念として持つ**方が自然です 💡
* 環境で変わる（検証用・本番用で違う）だけなら
  👉 設定でもOKです 🙆‍♀️

### 見分けのコツ（超大事）🧠✨

次の質問を自分にします👇

* それは「ビジネスの言葉」で説明する？（税率・手数料・締日…）📘
* それが変わると「仕様変更」扱い？（ルール変更）📝
* 監査・履歴・いつ変えたかが必要？ 🕵️‍♀️

✅YESが多いほど「ドメイン寄り」です。

---

## ドメインに “設定を渡す” 正しいやり方 🎁📦

![gift_wrapping](./picture/ddd_cs_study_069_gift_wrapping.png)

ドメインはこういう感じが気持ちいいです👇
**設定を読まずに、必要な値だけもらう**✨

### ドメイン側（設定の存在を知らない）🧠

```csharp
public readonly record struct TaxRate(decimal Value)
{
    public static TaxRate Create(decimal value)
        => value is >= 0m and <= 1m ? new(value) : throw new ArgumentOutOfRangeException(nameof(value));
}

public sealed class Order
{
    public decimal Subtotal { get; }

    public Order(decimal subtotal) => Subtotal = subtotal;

    public decimal CalculateTotal(TaxRate taxRate)
        => Subtotal * (1m + taxRate.Value);
}
```

### Application 側（設定→ドメイン型に変換して渡す）🍳

```csharp
public sealed class BillingService
{
    private readonly TaxRate _taxRate;

    // ここで “設定” を受け取る（ドメインじゃないのでOK）
    public BillingService(decimal taxRateFromConfig)
    {
        _taxRate = TaxRate.Create(taxRateFromConfig);
    }

    public decimal CalcTotal(decimal subtotal)
    {
        var order = new Order(subtotal);
        return order.CalculateTotal(_taxRate);
    }
}
```

💡ポイント：
**「設定値（decimal）」をそのままドメインに入れない**で、
 **ドメインの型（TaxRate）にしてから渡す**のが強いです💪✨
 
 ```mermaid
 sequenceDiagram
    participant Config as appsettings.json
    participant App as Application Service
    participant VO as TaxRate (VO)
    participant Dom as Order (Domain)
    
    Config->>App: TaxRate = 0.1 (decimal)
    
    Note over App, VO: ここで変換！🔄
    App->>VO: Create(0.1)
    VO-->>App: TaxRateオブジェクト
    
    App->>Dom: CalculateTotal(TaxRate)
    
    Note over Dom: 「0.1」て数字じゃなく<br/>「税率」として扱う😎
 ```
 
 ---

## “距離感” チェックリスト ✅📋✨

![distance_check](./picture/ddd_cs_study_069_distance_check.png)

あなたのコードを見て、これが守れてたらかなり良いです😊

* [ ] Domain に `IConfiguration` / `IOptions` が出てこない 📵
* [ ] Domain は「設定キー名」を知らない（`"PaymentApi:BaseUrl"` みたいなのが無い）🙅‍♀️
* [ ] 設定値は Application / Infrastructure で **ドメイン型に変換**してから渡してる 🔁
* [ ] 「ビジネスルールっぽい値」は、設定に置く前に一度疑ってる 🤔✨

---

## AI（Copilot/Codex）に頼むときの “良いお願い” 🧑‍💻🤖💬

そのままコピペでOKです👇（地味に効きます✨）

```text
appsettings.json の設定を IOptions<T> でバインドして。
ただし Domain プロジェクトには IConfiguration / IOptions を一切入れないで。
設定値は Application 層でドメイン型（Value Object）に変換してから渡す形にして。
ValidateOnStart も付けて、必須項目と範囲チェックも入れて。
```

---

## ミニ演習（15分）🧪⏰✨

### お題：外部API設定と、ビジネスルールっぽい値を分けよう😊

1. `ExternalServices:WeatherApi`（BaseUrl/Timeout）を `IOptions` で登録 🌦️
2. `DiscountRate` を「設定に置くべきか？」考える 🤔
3. ドメインに `DiscountRate` の値オブジェクトを作って、Application から渡す 🎁

できたら最後に、自分のコードへ質問👇
「Domain が appsettings の存在を知ってない？」👀✨

---

次の第70章は、こうして分けた構造を **図にして一瞬で共有**する回です 🗺️✨
（Mermaid / PlantUML で “迷わない地図” を作ります😊📌）
