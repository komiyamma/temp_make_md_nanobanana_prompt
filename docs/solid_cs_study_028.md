# 第28章：総合演習[3]：疎結合にして「完成」させる（DIP/DI/Test）🔌🧪🚀

ここまででクラス構造はかなり綺麗になってるはず！✨
でも、まだ **「new があちこちに散らばってる」** と、最後の一歩として *疎結合* が完成しないの😵‍💫
この章では **DIPで依存の向きを直して、DIで組み立てを1か所に集めて、テストで“挙動が変わってない”を証明** してゴールしよう〜！🥳🎉

（C# 14 / .NET 10 / Visual Studio 2026 で進めてOKだよ〜） ([Microsoft Learn][1])

---

## 1) この章のゴール🎯✨

最終ゴールはこれ👇💕

* ✅ **“業務ロジック（上位）” が “DB/HTTP/外部API（下位）” に振り回されない**（DIP） ([Microsoft Learn][2])
* ✅ **依存の組み立てを Program.cs（Composition Root）に集約**（DI） ([Microsoft Learn][3])
* ✅ **外部I/Oを Fake/Mock で差し替え可能にして高速テスト**（安心して改修できる）🧪 ([Microsoft Learn][2])
* ✅ Before/After の挙動が同じだと **テストで証明**（これ超大事！）✅

---

## 2) 完成形イメージ（ざっくり設計図）🗺️✨

![Swappable Robot Assembly: Core Battery (Domain) stays, Arms/Legs (Infrastructure) are swapped.](./picture/solid_cs_study_028_final_assembly_swappable.png)

「どこに何を書くか」を最後に固定しちゃうよ💡

* **Core（ドメイン）**：エンティティ / 値オブジェクト / ドメインサービス
* **Application（ユースケース）**：注文作成・支払い・発送など、アプリのやりたいこと
* **Infrastructure**：DB、外部決済、メール送信、配送API…（現実の面倒なところ）
* **App（Program.cs）**：全部を “組み立てるだけ” 🧱✨（ここが Composition Root）

この「組み立て1か所ルール」が、後々ずーーーっと効くよ😎✨ ([Microsoft Learn][3])

---

## 3) Step0：まずは “守るべき挙動” をテストで固定しよ🧷🧪

![Test Stake](./picture/solid_cs_study_028_test_stake.png)

リファクタの最終局面でありがちなのがこれ👇

> 「綺麗になったけど、実は挙動が変わってた😇」

だから先に、**重要なユースケースだけでも** テストで“杭（くい）”を打つよ🔨✨

例：ミニECならこのへん👇

* 注文できる（在庫OK）
* 割引が正しく入る
* 支払い成功ならステータスが Paid になる
* 支払い失敗なら Paid にならない
* 発送ラベルが作られる（配送先が入る）

テスティングは xUnit でいくのが定番で、xUnit v3 は .NET 8+ 対応だから .NET 10 でもOK👌 ([xunit.net][4])

---

## 4) Step1：外部I/Oを “抽象（interface）” に逃がす（DIP）🏰🔁

![DIP Escape](./picture/solid_cs_study_028_dip_escape.png)

### 4-1. 「外部っぽいもの」を洗い出す👀📝

まず、コードからこの匂いを探すよ😈

* `new SqlConnection(...)` / `DbContext`
* `HttpClient` 直叩き
* `DateTime.Now`（時間依存）
* `Guid.NewGuid()`（乱数依存）
* `File.ReadAllText`（ファイル依存）
* 外部SDK直呼び

これらを **“インターフェース越し”** にするのがコツ✨
.NET の DI はこの形を前提に設計されてるよ💡 ([Microsoft Learn][2])

### 4-2. Core or Application 側に「欲しい能力」を interface で置く📌

例（決済・注文保存・時計）👇

```csharp
public interface IPaymentGateway
{
    Task<PaymentResult> ChargeAsync(Order order, CancellationToken ct);
}

public interface IOrderRepository
{
    Task SaveAsync(Order order, CancellationToken ct);
    Task<Order?> FindAsync(OrderId id, CancellationToken ct);
}

public interface IClock
{
    DateTimeOffset Now { get; }
}
```

👉ポイント：**“どう実現するか” は書かない**
「欲しい能力」だけを書くのがDIPの気持ちだよ🫶✨ ([Microsoft Learn][2])

---

## 5) Step2：new を消して “コンストラクタ注入” にする🎁✨

![Constructor Injection Gift](./picture/solid_cs_study_028_constructor_gift.png)

Application のユースケース（例：PlaceOrderUseCase）が、直接インフラを作ってたらアウト🙅‍♀️
こうする👇

```csharp
public sealed class PlaceOrderUseCase
{
    private readonly IPaymentGateway _payment;
    private readonly IOrderRepository _orders;
    private readonly IClock _clock;

    public PlaceOrderUseCase(
        IPaymentGateway payment,
        IOrderRepository orders,
        IClock clock)
    {
        _payment = payment;
        _orders = orders;
        _clock = clock;
    }

    public async Task<OrderId> ExecuteAsync(PlaceOrderCommand cmd, CancellationToken ct)
    {
        var order = Order.Create(cmd.CustomerId, cmd.Items, _clock.Now);

        var payment = await _payment.ChargeAsync(order, ct);
        if (!payment.Success)
            throw new InvalidOperationException("支払い失敗");

        order.MarkPaid(payment.TransactionId);

        await _orders.SaveAsync(order, ct);
        return order.Id;
    }
}
```

✅ これで「上位（ユースケース）」は「下位（決済/DB）」の都合から自由になる🥳
まさにDIP〜！ ([Microsoft Learn][2])

---

## 6) Step3：Program.cs に “組み立て” を集める（DI/Composition Root）🧱🧩

![Program Assembly](./picture/solid_cs_study_028_program_assembly.png)

.NET の DI は標準機能として用意されてるよ📦✨ ([Microsoft Learn][2])
そして「どこで登録するか？」の答えが **Program.cs（Composition Root）**！

### 6-1. いちばん素直な登録例✅

（ConsoleでもWebでも考え方は同じだよ）

```csharp
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;

var builder = Host.CreateApplicationBuilder(args);

// --- インフラ ---
builder.Services.AddSingleton<IClock, SystemClock>();
builder.Services.AddTransient<IPaymentGateway, StripePaymentGateway>();
builder.Services.AddScoped<IOrderRepository, SqlOrderRepository>();

// --- アプリ（ユースケース）---
builder.Services.AddTransient<PlaceOrderUseCase>();

var host = builder.Build();

// 例：実行してみる
var useCase = host.Services.GetRequiredService<PlaceOrderUseCase>();
// await useCase.ExecuteAsync(...);
```

### 6-2. lifetime（Singleton/Scoped/Transient）の選び方💡

ここ、事故りやすいから要点だけ押さえよ！🧯

* **Transient**：軽いサービス、状態持たない、毎回作ってOK
* **Scoped**：1リクエスト（or 1処理単位）で同じインスタンスにしたい（DB系は多い）
* **Singleton**：アプリ全体で共有（重い生成コスト・グローバル共有・スレッドセーフが前提）

このへんの注意点は公式のガイドにもまとまってるよ✅ ([Microsoft Learn][5])

---

## 7) Step4：テストで “Fake差し替え” をやる（ここが気持ちいい！）🧪✨

![Fake Moon Swap](./picture/solid_cs_study_028_fake_moon_swap.png)

### 7-1. Fake を用意する（手書きでOK）✍️

```csharp
public sealed class FakePaymentGateway : IPaymentGateway
{
    public bool ShouldSucceed { get; set; } = true;

    public Task<PaymentResult> ChargeAsync(Order order, CancellationToken ct)
        => Task.FromResult(ShouldSucceed
            ? PaymentResult.Success("tx_123")
            : PaymentResult.Failure("NG"));
}

public sealed class FakeClock : IClock
{
    public DateTimeOffset Now { get; set; } = new(2026, 1, 1, 0, 0, 0, TimeSpan.Zero);
}
```

### 7-2. テスト側だけ “別のDI構成” にする🎛️

```csharp
using Microsoft.Extensions.DependencyInjection;
using Xunit;

public class PlaceOrderUseCaseTests
{
    [Fact]
    public async Task 支払い成功ならPaidになる()
    {
        var services = new ServiceCollection();

        // Fake差し替え
        var fakePayment = new FakePaymentGateway { ShouldSucceed = true };
        var fakeClock = new FakeClock();

        services.AddSingleton<IPaymentGateway>(fakePayment);
        services.AddSingleton<IClock>(fakeClock);
        services.AddSingleton<IOrderRepository, InMemoryOrderRepository>();

        services.AddTransient<PlaceOrderUseCase>();

        using var sp = services.BuildServiceProvider();

        var sut = sp.GetRequiredService<PlaceOrderUseCase>();

        // Act
        var id = await sut.ExecuteAsync(new PlaceOrderCommand(/*...*/),
            CancellationToken.None);

        // Assert（例）
        var repo = sp.GetRequiredService<IOrderRepository>();
        var saved = await repo.FindAsync(id, CancellationToken.None);
        Assert.NotNull(saved);
        Assert.True(saved!.IsPaid);
    }
}
```

これができると、外部APIが落ちてようがDBがなくても、**秒でテスト回せる**🥹✨
.NET のDIは「こういう差し替え」を超やりやすくするためにある感じだよ💞 ([Microsoft Learn][2])

---

## 8) Step5：“Before/After の挙動が同じ” を証明する✅🧪

![Balance Scale](./picture/solid_cs_study_028_balance_scale.png)

最後にやるのはこれ！

* **大事なユースケースのテストが全部通る** ✅
* 「例外ケース」のテストも通る ✅
* （できれば）**割引計算や料金計算みたいな純粋ロジックは、ユニットテストが分厚い**🧁✨

ここまで揃うと、もう **変更が怖くない状態** に到達だよ🥳🎉

---

## 9) つまずきやすいポイント集（先に潰そう）🧯💥

### ❌ 1) Singleton が Scoped を抱えちゃった

![Singleton Trap](./picture/solid_cs_study_028_singleton_trap.png)

「Singleton → Scoped」を直接注入すると破綻しやすいよ😵‍💫
スコープ検証なども含めて、公式ガイドの注意があるので要チェック✅ ([Microsoft Learn][5])

### ❌ 2) interface を作りすぎて迷子

「外部I/O」「差し替えたいもの」からでOK！
“全部インターフェース” はやりすぎになりがち😅

### ❌ 3) DateTime.Now でテストが不安定

時計は `IClock` に逃がすと世界が平和になる🕊️✨

---

## 10) AI（Copilot/Codex系）に投げると爆速になるお願い文🤖✨

コピペして使ってOKだよ〜！💕

* 「このクラスが触っている外部依存（DB/HTTP/時間/乱数/ファイル）を列挙して、interface化の案を出して」🤖📝
* 「new を消してコンストラクタ注入に直したい。最小差分でリファクタ案を出して」🧹✨
* 「このユースケースの重要なテスト観点を10個。正常系/異常系を半々で」🧪✅
* 「Fake実装を手書きで用意したい。stateを保持して検証できる InMemoryRepository を作って」📦✨

---

## 11) 仕上げのミニ課題（クリアできたら卒業🎓🎀）

* 🌟課題A：決済を「成功/失敗/タイムアウト」で差し替えテスト
* 🌟課題B：配送ラベル作成を Fake にして、住所のバリデーションもテスト
* 🌟課題C：DI登録を `AddMiniEc()` みたいな拡張メソッドにまとめて、Program.cs をスッキリ✨（ASP.NET Core でもよく使う型だよ） ([Microsoft Learn][3])

---

## まとめ🎉✨

第28章で完成したのはこれ👇💕

* DIPで「依存の向き」を直した 🏰🔁 ([Microsoft Learn][2])
* DIで「組み立て」を Program.cs に集めた 🧱✨ ([Microsoft Learn][3])
* テストで「挙動が同じ」を証明した 🧪✅
* 結果：**変更が怖くないSOLIDアプリ** ができた〜！！！🥳🎉

---

次、もし良ければ🙏✨
あなたが第27章までで作ったサンプルの「主要クラス（Order系、Payment系、Repository系）」のコード断片を貼ってくれたら、**その形に合わせて Chapter28 の“具体的なDI登録＆テスト差し替え”をガチで組み立てた完成例**を作るよ🤖💞

[1]: https://learn.microsoft.com/ja-jp/visualstudio/releases/2026/release-notes?utm_source=chatgpt.com "Visual Studio 2026 リリース ノート"
[2]: https://learn.microsoft.com/en-us/dotnet/core/extensions/dependency-injection?utm_source=chatgpt.com "Dependency injection - .NET"
[3]: https://learn.microsoft.com/en-us/aspnet/core/fundamentals/dependency-injection?view=aspnetcore-10.0&utm_source=chatgpt.com "Dependency injection in ASP.NET Core"
[4]: https://xunit.net/?utm_source=chatgpt.com "xUnit.net: Home"
[5]: https://learn.microsoft.com/en-us/dotnet/core/extensions/dependency-injection-guidelines?utm_source=chatgpt.com "Dependency injection guidelines - .NET"
