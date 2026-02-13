# 第18章：HTTP/外部APIを境界にする 🌐🚧

外部APIって、**落ちる・遅い・仕様が変わる**の三拍子がそろいがち…😵‍💫💥
だからこそこの章は、合言葉これです👇

**「外部APIは “境界” の外！中（ルール）に混ぜない！」** 📦➡️🌍✨

---

## 1) この章でできるようになること 🎯💖

* 外部API呼び出しを **`IExternalApiClient` みたいな境界**で包めるようになる 🧩
* “中のロジック” を **Fakeで爆速テスト**できるようになる 🧪⚡
* C#のHTTPまわりで **やりがちな事故（new HttpClient地獄など）**を避けられるようになる 🧯😇
* **IHttpClientFactory + 回復性(resilience)** の「今どきの基本形」を触れる 🤝✨
  （.NET 10 は LTS で、2026-01-13時点の最新パッチは 10.0.2 になってます） ([Microsoft][1])

---

## 2) 外部APIが “テストの敵” な理由 😈🌪️

![testable_cs_study_018_api_pain_points.png](./picture/testable_cs_study_018_api_pain_points.png)

外の世界はコントロール不能…！たとえば👇

* ネットワークが不安定でタイムアウトする 🐢💤
* 429(制限) や 500(障害) が返る 🤯
* 仕様変更でレスポンス形式が変わる 🔁💥
* たまに落ちる（そしてたまに復活する）👻

なので、**重要ロジックの中に HttpClient 直書き**すると…
テストが「運ゲー」になりがちです 🎲😵‍💫

---

## 3) まず “やらない形” 🙅‍♀️💣（混ぜるとつらい）

![testable_cs_study_018_socket_exhaustion.png](./picture/testable_cs_study_018_socket_exhaustion.png)

* 重要ロジックの中で `new HttpClient()` して叩く
* 重要ロジックが `HttpResponseMessage` やステータスコードの都合に引きずられる
* あちこちにURLや認証ヘッダが散らばる

さらに、`HttpClient` をリクエストごとに作るのは **ソケット枯渇**につながる可能性があるので注意です⚠️（重い負荷で `SocketException` が出たり） ([Microsoft Learn][2])

---

## 4) “正解の形” ✅🧩（境界で包む）


![testable_cs_study_018_api_boundary.png](./picture/testable_cs_study_018_api_boundary.png)

ポイントはこれ👇

1. **中（ルール）**：

   * 「何をしたいか」だけを書く（例：為替レートが欲しい、送料が欲しい、住所検証したい、など）
   * **HTTPの都合を知らない**（URL/ヘッダ/JSON/ステータスコードを知らない）📦✨

2. **外（I/O）**：

   * HTTPで叩く、JSONを読む、認証する…を担当 🌐🔑
   * 失敗するのもここ（遅い・落ちる）😵

その橋渡しが **境界インターフェース**です👇

* `IExchangeRateApi` / `IShippingFeeApi` / `ICustomerScoreClient` みたいなやつ ✨

---

## 5) ハンズオン：為替レートAPIを “境界化” してみる 💱🌐✨

ここでは例として「USD→JPYのレートを外部APIから取って、金額変換する」やつを作ります😊

---

## 5-1) 境界（インターフェース）を作る 🧩📮

![testable_cs_study_018_return_type_simplification.png](./picture/testable_cs_study_018_return_type_simplification.png)

```csharp
public interface IExchangeRateApi
{
    Task<decimal> GetUsdToJpyAsync(CancellationToken ct = default);
}
```

✅ ここ大事：**戻り値は “中でほしい形”** に寄せる

* `HttpResponseMessage` とか返さない 🙅‍♀️
* 「レート」だけ返す（中が使いやすい）🎯

---

## 5-2) 中（ルール側）のサービスを書く 📦✨

```csharp
public sealed class CurrencyConverter
{
    private readonly IExchangeRateApi _exchangeRateApi;

    public CurrencyConverter(IExchangeRateApi exchangeRateApi)
    {
        _exchangeRateApi = exchangeRateApi;
    }

    public async Task<decimal> ConvertUsdToJpyAsync(decimal usd, CancellationToken ct = default)
    {
        if (usd < 0) throw new ArgumentOutOfRangeException(nameof(usd));

        var rate = await _exchangeRateApi.GetUsdToJpyAsync(ct);

        // ここは「ビジネスのルール」：レートが変でも計算しない、など
        if (rate <= 0) throw new InvalidOperationException("Invalid exchange rate.");

        return Math.Round(usd * rate, 0, MidpointRounding.AwayFromZero);
    }
}
```

🌟この `CurrencyConverter` は **HTTPを一切知らない** ので、テストが超ラクになります🧪💖

---

## 5-3) 外（HTTP実装）を書く 🌐🔧

![testable_cs_study_018_http_client_factory.png](./picture/testable_cs_study_018_http_client_factory.png)

`HttpClient` は **IHttpClientFactory（AddHttpClient）** 経由で使うのが定番です。 ([Microsoft Learn][3])

まず、外部APIのレスポンス（例）用DTOを作って：

```csharp
public sealed record ExchangeRateResponse(Dictionary<string, decimal> rates);
```

次にクライアント実装：

```csharp
using System.Net.Http.Json;

public sealed class ExchangeRateApiClient : IExchangeRateApi
{
    private readonly HttpClient _http;

    public ExchangeRateApiClient(HttpClient http)
    {
        _http = http;
    }

    public async Task<decimal> GetUsdToJpyAsync(CancellationToken ct = default)
    {
        // 例：GET /latest?base=USD&symbols=JPY みたいなAPIを想定
        var res = await _http.GetFromJsonAsync<ExchangeRateResponse>(
            "latest?base=USD&symbols=JPY",
            ct);

        if (res is null || res.rates is null) throw new HttpRequestException("Empty response.");

        if (!res.rates.TryGetValue("JPY", out var jpy))
            throw new HttpRequestException("JPY rate not found.");

        return jpy;
    }
}
```

✅ “HTTPの面倒” はぜんぶここで引き受ける感じです🌐🧹

---

## 6) 組み立て（DI登録）で本物を接続する 🔌🏗️✨

## 6-1) Typed Client として登録する（おすすめ）🧩

![testable_cs_study_018_resilience_shield.png](./picture/testable_cs_study_018_resilience_shield.png)

```csharp
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;

var builder = Host.CreateApplicationBuilder(args);

builder.Services.AddHttpClient<IExchangeRateApi, ExchangeRateApiClient>(http =>
{
    http.BaseAddress = new Uri("https://api.example.com/"); // 例
})
// 回復性（resilience）をサクッと追加できる 💪✨
.AddStandardResilienceHandler();

builder.Services.AddTransient<CurrencyConverter>();

var app = builder.Build();
```

* `AddHttpClient` で **IHttpClientFactory** ベースにできるのがポイント ✨ ([Microsoft Learn][3])
* `AddStandardResilienceHandler()` は **標準の回復性パイプライン**（リトライ/タイムアウト/遮断など）をまとめて入れてくれます 🔥 ([Microsoft for Developers][4])
* しかも標準パイプラインは **429/500系/タイムアウト**などを扱う前提が入ってます（現場で超ありがち）🙏 ([Microsoft for Developers][4])

> なお、昔よく使われた `Microsoft.Extensions.Http.Polly` は NuGet 上 “deprecated” 扱いで、今は `Microsoft.Extensions.Http.Resilience` 系が推奨です。 ([NuGet][5])

---

## 7) テスト戦略：単体はFake、結合は少しだけ 🤏🧪✨

## 7-1) 中（ルール）の単体テスト：Fakeで一瞬 🎉⚡

![testable_cs_study_018_fake_api_swap.png](./picture/testable_cs_study_018_fake_api_swap.png)

```csharp
public sealed class FakeExchangeRateApi : IExchangeRateApi
{
    private readonly decimal _rate;

    public FakeExchangeRateApi(decimal rate) => _rate = rate;

    public Task<decimal> GetUsdToJpyAsync(CancellationToken ct = default)
        => Task.FromResult(_rate);
}
```

```csharp
using Xunit;

public class CurrencyConverterTests
{
    [Fact]
    public async Task ConvertUsdToJpyAsync_UsesRate()
    {
        var api = new FakeExchangeRateApi(rate: 150m);
        var sut = new CurrencyConverter(api);

        var jpy = await sut.ConvertUsdToJpyAsync(usd: 2m);

        Assert.Equal(300m, jpy);
    }

    [Fact]
    public async Task ConvertUsdToJpyAsync_NegativeUsd_Throws()
    {
        var api = new FakeExchangeRateApi(rate: 150m);
        var sut = new CurrencyConverter(api);

        await Assert.ThrowsAsync<ArgumentOutOfRangeException>(
            () => sut.ConvertUsdToJpyAsync(-1m));
    }
}
```

💖 速い・安定・気持ちいい！
外部APIが落ちててもテストは落ちません✨

---

## 7-2) 外（HTTPクライアント）のテスト：HttpMessageHandlerでネット無し 🧪🌐❌


![testable_cs_study_018_simulated_network.png](./picture/testable_cs_study_018_simulated_network.png)

「シリアライズ/URL/ヘッダが合ってる？」みたいな確認は、**ネットに出ずに**できます😊

```csharp
using System.Net;
using System.Net.Http;
using System.Text;
using System.Text.Json;

public sealed class StubHttpMessageHandler : HttpMessageHandler
{
    private readonly Funcstring _json;

    public StubHttpMessageHandler(string json) => _json = json;

    protected override Task<HttpResponseMessage> SendAsync(HttpRequestMessage request, CancellationToken cancellationToken)
    {
        var response = new HttpResponseMessage(HttpStatusCode.OK)
        {
            Content = new StringContent(_json, Encoding.UTF8, "application/json")
        };
        return Task.FromResult(response);
    }
}
```

```csharp
using Xunit;

public class ExchangeRateApiClientTests
{
    [Fact]
    public async Task GetUsdToJpyAsync_ReadsJpyRate()
    {
        var json = """{"rates":{"JPY":150.0}}""";
        var handler = new StubHttpMessageHandler(json);
        var http = new HttpClient(handler)
        {
            BaseAddress = new Uri("https://api.example.com/")
        };

        var sut = new ExchangeRateApiClient(http);

        var rate = await sut.GetUsdToJpyAsync();

        Assert.Equal(150.0m, rate);
    }
}
```

---

## 7-3) 結合テスト（本物API）は “少しだけ” 🤏✅

* 「本当に繋がる？」の最終確認は価値あるけど、
* 常時やると不安定＆遅い 😵‍💫

なのでおすすめは👇

* 単体テスト（Fake）を主力にする 🧪⚡
* 本物APIは「最低限の本数」だけ持つ 🤏✨
* 認証キーが要るなら、環境変数などで切り替え（コードに直書きしない）🔑🙅‍♀️

---

## 8) よくある落とし穴まとめ ⚠️😇

## 落とし穴A：`new HttpClient()` を毎回やる 🧨

* ソケット枯渇の原因になりがちです ([Microsoft Learn][2])
  ➡️ `IHttpClientFactory` か、長寿命HttpClient戦略で回避が推奨 ([Microsoft Learn][6])

## 落とし穴B：Factoryで作った `HttpClient` を長期間キャッシュしちゃう 🧊

* `IHttpClientFactory` は「短命クライアント前提」の設計思想があり、長期保持はDNS更新などで問題になり得ます ([Microsoft Learn][7])
  ➡️ Typed client を singleton に突っ込むのも注意 ⚠️ ([Microsoft Learn][7])

## 落とし穴C：リトライしすぎて相手を殴る 👊😵

![testable_cs_study_018_infinite_retry.png](./picture/testable_cs_study_018_infinite_retry.png)

* 回復性は大事だけど、**無限リトライ**とかは逆効果
  ➡️ 標準パイプラインの考え方（制限/タイムアウト/遮断）を使うと安全寄り 💪 ([Microsoft for Developers][4])

---

## 9) AI活用（Copilot/Codex）に頼むと捗るやつ 🤖💡✨

そのままコピって投げてOKなお願い例👇

* 「`IExchangeRateApi` の Fake を作って。成功/失敗パターンも欲しい」🎭
* 「`CurrencyConverter` の単体テストを xUnit で AAA(Arrange/Act/Assert) で書いて」🧪
* 「HTTPクライアント実装で、DTOとドメイン型が混ざってないかレビューして」🔍
* 「AddHttpClient + AddStandardResilienceHandler の登録例を最小で」🏗️

⚠️ ただしAIは、たまに平気で

* ロジック側にHTTPを混ぜる
* DTOをドメインに漏らす
  ので、**“境界が守れてる？”** を最優先でチェックしてね👀✨

---

## 10) ミニチェッククイズ ✅🎓

1. 重要ロジックの中に `HttpClient` を直置きすると何がつらい？😵‍💫
2. 境界インターフェースは「戻り値」を何に寄せるのが気持ちいい？🎯
3. 単体テストで外部APIの代わりに何を使う？🎭
4. `IHttpClientFactory` を使う主なメリットは？🧰
5. 429 が返る外部APIに、やみくもリトライすると何が起きる？💥

---

## まとめ 🎉💖

* 外部APIは **落ちる・遅い・変わる** 😵‍💫
* だから **`IExternalApiClient` 的な境界で包んで**、中は純粋ロジックに寄せる 📦🧩
* 単体テストは **Fakeで安定＆爆速** 🧪⚡
* HTTPは `AddHttpClient` +（必要なら）**標準回復性**で堅くする 💪✨ ([Microsoft Learn][3])

---

次の章（第19章）は、**UIもI/O**として同じ発想で薄くする話に進むよ〜🖥️🚧✨

[1]: https://dotnet.microsoft.com/en-us/platform/support/policy/dotnet-core ".NET and .NET Core official support policy | .NET"
[2]: https://learn.microsoft.com/en-us/dotnet/fundamentals/runtime-libraries/system-net-http-httpclient "System.Net.Http.HttpClient class - .NET | Microsoft Learn"
[3]: https://learn.microsoft.com/ja-jp/aspnet/core/fundamentals/http-requests?view=aspnetcore-10.0 "ASP.NET Core で IHttpClientFactory を使用して HTTP 要求を行う | Microsoft Learn"
[4]: https://devblogs.microsoft.com/dotnet/building-resilient-cloud-services-with-dotnet-8/ "Building resilient cloud services with .NET 8 - .NET Blog"
[5]: https://www.nuget.org/packages/microsoft.extensions.http.polly/ "
        NuGet Gallery
        \| Microsoft.Extensions.Http.Polly 10.0.2
    "
[6]: https://learn.microsoft.com/en-us/dotnet/fundamentals/networking/http/httpclient-guidelines "HttpClient guidelines for .NET - .NET | Microsoft Learn"
[7]: https://learn.microsoft.com/en-us/dotnet/core/extensions/httpclient-factory-troubleshooting "Troubleshoot IHttpClientFactory issues - .NET | Microsoft Learn"
