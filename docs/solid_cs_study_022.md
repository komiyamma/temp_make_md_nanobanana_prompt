# 第22章：DIPの入口「上位（業務）を下位（DB/HTTP）の都合にしない」🏰

この章は「**DIP（依存性逆転の原則）**って何？どう嬉しいの？」を、ミニEC（注文→支払い→発送）の文脈で“体感”する回だよ😊🧡
（いまの最新だと .NET 10 は 2025/11/11 リリース＆LTS、C# 14 はその上で動く最新言語、Visual Studio 2026 は .NET 10/C# 14 をサポートしてるよ📌） ([Microsoft][1])

---

## 1. 今日のゴール🎯✨

章末でこう言えたら勝ち🏆💕

* 「**依存の向き**って何？どうすると事故る？」を説明できる🧭
* 「上位（業務ロジック）が下位（DB/外部API）に振り回される」状態を直せる🛠️
* DIPの基本形：**“抽象（interface）に依存する”**を手で書ける✍️

---

## 2. DIPってひとことで言うと？🧲🔁

![Bad Dependency (Top-Heavy) vs Good Dependency (DIP/Socket).](./picture/solid_cs_study_022_dip_arrow_reversal.png)

DIPはざっくりこう👇😊

* **上位モジュール（業務ロジック）**は
  **下位モジュール（DB/HTTP/ファイル/外部SDK）**に依存しない🙅‍♀️
* 代わりに **“抽象（interface）”** に依存する✅
* そして **下位側（実装）が抽象に合わせる**（＝依存の向きが“逆転”）🔃

イメージはこれ👇

* ❌ 悪い例：`CheckoutService → SqlOrderRepository → SQL Server`（上位が下位に直結）
* ✅ 良い例：`CheckoutService → IOrderRepository ← SqlOrderRepository`（実装が契約に合わせる）

---

## 3. まず「DIPなし」だと何がツラいの？😇💥

ミニECでありがち “最初の実装” を想像してね🛒✨

* 支払いに Stripe みたいな外部SDK使う💳
* 注文保存は SQL に入れる🗄️
* いったん動けばOK！ってなる（これは普通だよ😊）

でも、こうなると……👇

### 変更が来た瞬間に地獄🧨

* DBを SQL → SQLite → CosmosDB に変えたい
* 支払いが Stripe → 別決済 に変わる
* テストで外部API呼びたくない（遅い・課金・不安定）🧪💸

「上位（業務）」が下位の都合に直結だと、上位のコードが毎回巻き込まれるの😭

---

## 4. 悪い例（Before）：上位が下位を `new` してる😵‍💫

ポイントは「**上位クラスの中で下位クラスを直接作ってる**」ことだよ⚠️

```csharp
// Applicationっぽい場所にあるつもりの業務クラス（でも依存がベタベタ…）
public sealed class CheckoutService
{
    public async Task CheckoutAsync(Order order)
    {
        // ❌ 下位の詳細（DB/外部API）を上位が直に知ってる
        var repo = new SqlOrderRepository("Server=...;Database=...");
        var gateway = new StripePaymentGateway("api-key-...");

        var payment = await gateway.ChargeAsync(order.TotalPrice);
        if (!payment.Success) throw new Exception("Payment failed 😢");

        await repo.SaveAsync(order);
    }
}
```

### これの何が困るの？🥲

* `CheckoutService` をテストするときに **Stripe本番API**叩きそうになる💥
* DB接続が必要になって **テストが重い＆壊れやすい**🧪🐢
* `SqlOrderRepository` を別実装に変えると `CheckoutService` を修正する羽目😇

---

## 5. DIPの基本形（After）：上位は interface に依存する💎✨

ここでやることはシンプルだよ😊💕

1. 上位が欲しいのは「SQLの詳細」じゃなくて
   **“注文を保存できること”**
2. “できること” を **interface（契約）** にする📜
3. 下位実装（SQL）はその契約を満たすように作る🧱

### 5-1. まず抽象（interface）を作る✍️

```csharp
public interface IOrderRepository
{
    Task SaveAsync(Order order);
}

public interface IPaymentGateway
{
    Task<PaymentResult> ChargeAsync(Money amount);
}
```

### 5-2. 上位（業務）は抽象だけ見る👀✨

```csharp
public sealed class CheckoutService
{
    private readonly IOrderRepository _repo;
    private readonly IPaymentGateway _gateway;

    // ✅ ここがキモ：下位の具体クラスを知らない
    public CheckoutService(IOrderRepository repo, IPaymentGateway gateway)
    {
        _repo = repo;
        _gateway = gateway;
    }

    public async Task CheckoutAsync(Order order)
    {
        var payment = await _gateway.ChargeAsync(order.TotalPrice);
        if (!payment.Success) throw new InvalidOperationException("Payment failed 😢");

        await _repo.SaveAsync(order);
    }
}
```

### 5-3. 下位（SQL/Stripe）は抽象に合わせる🔧

```csharp
public sealed class SqlOrderRepository : IOrderRepository
{
    private readonly string _connectionString;

    public SqlOrderRepository(string connectionString)
    {
        _connectionString = connectionString;
    }

    public Task SaveAsync(Order order)
    {
        // ここにSQL保存の詳細を書く（省略）
        return Task.CompletedTask;
    }
}

public sealed class StripePaymentGateway : IPaymentGateway
{
    private readonly string _apiKey;

    public StripePaymentGateway(string apiKey)
    {
        _apiKey = apiKey;
    }

    public Task<PaymentResult> ChargeAsync(Money amount)
    {
        // ここに外部SDKの詳細を書く（省略）
        return Task.FromResult(PaymentResult.Successful());
    }
}
```

---

## 6. “逆転”ってどこが逆転なの？🌀🧠

普通の感覚だと「上位が下位を使う」から、上位→下位に依存しがち。
でもDIPでは……

* 上位は **抽象（interface）** に依存する（＝具体を知らない）
* 下位は **抽象を実装** する（＝抽象に依存する）

つまり「詳細（下位）が、上位が決めた契約に従う」形になるよ😆✨
この考え方は .NET のDI（依存関係の注入）とも相性バツグンで、公式ドキュメントでも DI は .NET の主要パターンとして整理されてるよ📚 ([Microsoft Learn][2])

---

## 7. DIPとDI、名前が似てて混乱しがち問題😵‍💫➡️😌

ここ、超大事なのでスッキリさせよ〜！🧼✨

* **DIP（原則）**：設計のルール📏

  * 「抽象に依存しようね」
* **DI（手法）**：依存を外から渡すやり方🎁

  * 「`new` せずに、コンストラクタで受け取ろうね」

DIPは“考え方”、DIは“実装テク”って感じ😊
次章（第23章）でDIをしっかりやるよ！🚀

---

## 8. ちょい実演：テストが一気にラクになる🧪✨

DIPが効く瞬間、いちばん分かりやすいのがテストだよ💕

```csharp
public sealed class FakePaymentGateway : IPaymentGateway
{
    private readonly bool _success;
    public FakePaymentGateway(bool success) => _success = success;

    public Task<PaymentResult> ChargeAsync(Money amount)
        => Task.FromResult(_success ? PaymentResult.Successful() : PaymentResult.Failed());
}

public sealed class InMemoryOrderRepository : IOrderRepository
{
    public List<Order> Saved { get; } = new();

    public Task SaveAsync(Order order)
    {
        Saved.Add(order);
        return Task.CompletedTask;
    }
}
```

これで `CheckoutService` は、外部APIもDBも無しで動かせる😆🎉
（次章で “.NETのDIコンテナで組み立てる場所” を作るとさらに気持ちよくなるよ🧱✨）

---

## 9. DIPの“良い抽象”ってどう作るの？🤔💎

ここで初心者がやりがちなのが👇

* ❌ 抽象が「技術の言葉」になってる

  * `ISqlRepository`, `IHttpClientWrapper` みたいな命名
* ✅ 抽象は「業務が欲しい能力」になってる

  * `IOrderRepository`, `IPaymentGateway`, `IShippingLabelGenerator` みたいに✨

**抽象＝業務の言葉**にすると、上位が下位に振り回されにくくなるよ😊💕

---

## 10. よくあるミス集（先に潰す！）🧯😂

### ミス1：interface を “下位（Infrastructure）側” に置いちゃう🙅‍♀️

* すると上位が参照できず、依存が崩れることが多い💥
* 目安：**上位が欲しい契約は上位側（Application側）に置く**のが基本🌟

### ミス2：何でもかんでもinterfaceにする😅

* 小さなアプリで、変える予定もテストもしない所まで抽象化すると逆に読みにくい💦
* 目安：

  * **外部I/O（DB/HTTP/ファイル/時刻/乱数）** は抽象化しやすい✅
  * 純粋な計算ロジックはそのままでOKなこと多い✅

### ミス3：抽象がデカすぎる（ISP違反に近い）😇

* `IDataAccess` に全部詰めるのはやめよ〜！✂️
* 役割ごとに分けると最高😊✨

---

## 11. Copilot / Codex に投げると気持ちいい質問例🤖💬✨

そのままコピペでOKだよ👍

* 「このクラスが依存している **外部要因（DB/HTTP/時間/ファイル）** を列挙して」
* 「この業務クラスから **Infrastructure詳細** を追い出すための interface 案を3つ出して」
* 「命名を **業務の言葉** に寄せて。`ISql...` っぽいの禁止で！」
* 「テスト用の Fake 実装を最小コードで作って」

AIは“分割案を出す”のが得意だけど、最後は自分で「業務の言葉になってる？」をチェックすると強いよ😊✅

---

## 12. ミニ演習（15〜25分）⏱️🛠️✨

### 演習A：依存の“矢印”を見つける🧭

次のうち、DIP的に危ない依存を3つ探してみてね👇

* `CheckoutService` が `SqlConnection` を直接触ってる
* `OrderService` が `HttpClient` を直接 `new` してる
* `DiscountCalculator` が `DateTime.Now` を直接参照してる

👉 ヒント：**外部I/Oと“変わりやすいもの”**が混じってたら要注意⚠️

### 演習B：1個だけDIP化してみる💪

「支払い」だけをDIP化してみよ！

1. `IPaymentGateway` を作る
2. `CheckoutService` の中の `new StripePaymentGateway()` を消す
3. コンストラクタで `IPaymentGateway` を受け取る
4. Fake を作ってテスト（or 動作確認）する

---

## 13. まとめ🌈✨

* DIPは「上位（業務）を下位（DB/HTTP）の都合に縛られない」ための原則🏰🔌
* コツは **“業務が欲しい能力” を interface にする**こと💎
* そして **上位はinterfaceだけを見る** → 下位実装が合わせる → 依存が“逆転”🔁
* この形は .NET の DI と相性抜群で、公式ドキュメントでもDIは .NET の重要パターンとして整理されてるよ📚 ([Microsoft Learn][2])

---

## 次章予告👀✨（第23章）

次は「**DI（注入）**」で、`new` をもっと減らして、組み立てをキレイにするよ🎁🧱
「コンストラクタ注入を基本にする理由」を、めちゃ分かりやすくやろうね😊💕

必要なら、第22章の題材（ミニEC）に合わせて「あなたの既存コードっぽい“ぐちゃぐちゃ版”」も私が作って、そこからDIP化の手順を章用に完全固定していけるよ😆🛠️

[1]: https://dotnet.microsoft.com/en-us/platform/support/policy?utm_source=chatgpt.com "The official .NET support policy"
[2]: https://learn.microsoft.com/en-us/dotnet/core/extensions/dependency-injection?utm_source=chatgpt.com "Dependency injection - .NET"
