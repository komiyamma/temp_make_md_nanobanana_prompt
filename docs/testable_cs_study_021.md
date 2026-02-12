# 第21章：テストしやすい形に“分解”する練習 🧱💖

まず「今の最新版」だけサクッと押さえるね👀✨
2026-01-16時点では、.NET 10 が最新の LTS で（2025-11-11 公開、2028-11-10 までサポート）だよ📌 ([Microsoft for Developers][1])
C# 14 は .NET 10 SDK / Visual Studio 2026 で使えるよ🧩 ([Microsoft Learn][2])
Visual Studio 2026 は 2026-01-13 に 18.2.0 の更新が出てるよ🛠️ ([Microsoft Learn][3])
（.NET 10 も 10.0.1 が配布されてるのが確認できるよ） ([Microsoft][4])
テストは xUnit を使うなら、xUnit v3 は Microsoft Testing Platform 対応も含めて整ってるよ🧪🤖 ([xUnit.net][5])

---

## 21-1. 今日のゴール 🧭✨

この章でできるようになりたいのはこれ👇💖

* デカい関数を「役割ごと」に切れる✂️🧩
* “判断（if）” と “I/O（外の世界）” を分けられる🎯🚪
* 「ユースケース単位」で組み立てられる🏗️✨（＝読みやすい＋テストしやすい）

---

## 21-2. 分解の地図を1枚持とう 🗺️😊

コードの中身って、だいたいこの3つが混ざってるのが原因だよ〜😵‍💫💥

### A) ルール（ピュア）🌿

* 計算、判定、変換（入力が同じなら結果も同じ）
* テストが超ラク＆爆速⚡🧪

### B) I/O（外の世界）🌍

* DB、ファイル、HTTP、時刻、乱数、UI…
* 落ちる・遅い・揺れる・環境依存😈

### C) つなぎ役（ユースケース）🧩

* “ルール”を呼んで、必要なI/Oを順に実行する係
* **ここはテストでは Fake に差し替え**できるようにする🎭✨

イメージはこんな感じ👇

* ルール（中）📦：純粋に「どうするべきか」を決める
* ユースケース（中〜外の境目）🧠：決めた通りに進行する
* I/O（外）🌍：保存・送信・表示などを実行する

---

## 21-3. 分解の型 5つ 🧰✨


![testable_cs_study_021_decomposition.png](./picture/testable_cs_study_021_decomposition.png)

### 型1：I/Oに蛍光ペンを引く🖍️

「Console」「Http」「DB」「File」「DateTime.Now」「Random」…見つけたら全部マーキング✅
→ それが “外の世界” だよ🚪🌍

### 型2：“判断”を先に終わらせる🎯

I/Oしながら判断しない！
先に「どうする？」を決めて、後で「実行」する✨

* Decide（計画を作る）📝
* Do（I/Oを実行する）🔌

### 型3：if を2種類に分ける🔀

* ルール if：割引条件、期限チェック、在庫判定…（ピュアにできる🌿）
* I/O if：失敗したらログ、再試行、保存しない…（ユースケース側へ🧩）

### 型4：引数で渡せる形にする🎁

「今の時刻」「乱数」「ユーザー情報」などを引数へ
→ その瞬間からテストが安定する🧪✨

### 型5：ユースケース単位に箱を作る📦

「注文する」「登録する」「応募する」みたいに、**1つの目的＝1つの入口**にする😊
→ テストも「その目的単位」で書ける🎉

---

## 21-4. ハンズオン：混ざりまくり関数を分解してみよう 🛒💥➡️🧱✨

題材は「購入処理」だよ〜😊
やりがちポイント全部入りにしてある（わざとね！）😈✨

### 21-4-1. Before：ぜんぶ混ぜた地獄コード 👻


![testable_cs_study_021_bad_spaghetti.png](./picture/testable_cs_study_021_bad_spaghetti.png)

```csharp
using System.Net.Http.Json;

public class CheckoutService
{
    private readonly string _connectionString;

    public CheckoutService(string connectionString)
    {
        _connectionString = connectionString;
    }

    public async Task<string> CheckoutAsync()
    {
        // UI I/O
        Console.Write("UserId: ");
        var userId = Console.ReadLine();

        Console.Write("CouponCode (empty ok): ");
        var coupon = Console.ReadLine();

        // 時刻 I/O
        var now = DateTime.Now;

        // DB I/O（ここでは擬似的に…本当はSqlConnectionとか書かれがち）
        var user = await FakeDbLoadUserAsync(userId!);

        // ルール（割引判定）＋I/O（ログ/出力）が混ざる
        var discountRate = 0m;
        if (user.IsStudent && now.Month == 12) discountRate = 0.20m; // 12月学割
        if (!string.IsNullOrWhiteSpace(coupon)) discountRate += 0.05m;

        // 外部API I/O
        using var http = new HttpClient();
        var price = await http.GetFromJsonAsync<decimal>("https://example.com/api/price/today");

        var total = price * (1m - discountRate);

        // ついでに画面表示 I/O
        Console.WriteLine($"Total = {total:0.00}");

        // DB I/O（保存）
        await FakeDbSaveOrderAsync(userId!, total, now);

        return "OK";
    }

    private Task<(bool IsStudent)> FakeDbLoadUserAsync(string userId)
        => Task.FromResult((IsStudent: userId.StartsWith("s")));

    private Task FakeDbSaveOrderAsync(string userId, decimal total, DateTime now)
        => Task.CompletedTask;
}
```

これ、何がツラい？😵‍💫

* テストで Console 入力できない🖥️💥
* DateTime.Now で結果が揺れる🕰️🌪️
* HttpClient が外に出る＆遅い＆落ちる🌐😇
* ロジックが1か所にベタ付けで、テストしたい「割引判定」だけ抜けない✂️😭

---

## 21-5. Step 1：I/Oに名前を付けて外へ逃がす 🚪🏃‍♀️💨

まずは “外の世界” をインターフェースにして包むよ📦✨

```csharp
public interface IUserRepository
{
    Task<User> LoadAsync(string userId);
}

public interface IPriceClient
{
    Task<decimal> GetTodayPriceAsync();
}

public interface IClock
{
    DateTime Now { get; }
}

public interface IOrderRepository
{
    Task SaveAsync(Order order);
}

public interface IConsoleUi
{
    string Ask(string message);
    void Show(string message);
}

public sealed record User(string Id, bool IsStudent);
public sealed record Order(string UserId, decimal Total, DateTime OrderedAt);
```

ポイント💡

* ここではまだ「分解できた感」少なくてOK🙆‍♀️
* **“差し替え可能な形” を作った**のが勝ち🎉

---

## 21-6. Step 2：“判断だけ”をピュアに抜き出す 🌿🎯

次は「割引率を決める」みたいな **ルール** を関数に分離するよ✂️✨
I/O いっさい無しにするのがコツ🧼

```csharp
public static class CheckoutRules
{
    public static decimal CalculateDiscountRate(User user, DateTime now, string? coupon)
    {
        decimal rate = 0m;

        if (user.IsStudent && now.Month == 12)
            rate += 0.20m;

        if (!string.IsNullOrWhiteSpace(coupon))
            rate += 0.05m;

        // 割引は最大30%まで、みたいな“ルール”もここへ置ける
        if (rate > 0.30m) rate = 0.30m;

        return rate;
    }
}
```

これで「割引判定」だけなら **最速で単体テスト**できる⚡🧪💖

---

## 21-7. Step 3：ユースケースで組み立てる 🧩🏗️✨

つなぎ役を “UseCase” として作るよ😊
ここが「判断（ルール）」と「I/O」をつなぐ場所！

```csharp
public sealed class CheckoutUseCase
{
    private readonly IUserRepository _users;
    private readonly IPriceClient _prices;
    private readonly IClock _clock;
    private readonly IOrderRepository _orders;
    private readonly IConsoleUi _ui;

    public CheckoutUseCase(
        IUserRepository users,
        IPriceClient prices,
        IClock clock,
        IOrderRepository orders,
        IConsoleUi ui)
    {
        _users = users;
        _prices = prices;
        _clock = clock;
        _orders = orders;
        _ui = ui;
    }

    public async Task<string> ExecuteAsync()
    {
        var userId = _ui.Ask("UserId: ");
        var coupon = _ui.Ask("CouponCode (empty ok): ");

        var now = _clock.Now;

        var user = await _users.LoadAsync(userId);
        var price = await _prices.GetTodayPriceAsync();

        var discountRate = CheckoutRules.CalculateDiscountRate(user, now, coupon);
        var total = price * (1m - discountRate);

        _ui.Show($"Total = {total:0.00}");

        await _orders.SaveAsync(new Order(userId, total, now));

        return "OK";
    }
}
```

ここまで来ると、テストはこうなる🎭✨

* ルールのテスト：超簡単（ピュア）
* ユースケースのテスト：Fake を差して「保存された？表示された？」を見る

---

## 21-8. テストを書いて “分解のご褒美” を味わう 🧪🍰✨

### 21-8-1. ルールのテストは爆速⚡

```csharp
using Xunit;

public class CheckoutRulesTests
{
    [Fact]
    public void StudentInDecember_Gets20Percent()
    {
        var user = new User("s123", isStudent: true);
        var now = new DateTime(2026, 12, 1);

        var rate = CheckoutRules.CalculateDiscountRate(user, now, coupon: "");

        Assert.Equal(0.20m, rate);
    }

    [Fact]
    public void Coupon_Adds5Percent()
    {
        var user = new User("u999", isStudent: false);
        var now = new DateTime(2026, 1, 16);

        var rate = CheckoutRules.CalculateDiscountRate(user, now, coupon: "HELLO");

        Assert.Equal(0.05m, rate);
    }

    [Fact]
    public void Discount_IsCappedAt30Percent()
    {
        var user = new User("s123", isStudent: true);
        var now = new DateTime(2026, 12, 1);

        var rate = CheckoutRules.CalculateDiscountRate(user, now, coupon: "ANY");

        Assert.Equal(0.30m, rate);
    }
}
```

### 21-8-2. ユースケースは Fake で安定 🧸✨

```csharp
using Xunit;

public class CheckoutUseCaseTests
{
    [Fact]
    public async Task SavesOrder_AndShowsTotal()
    {
        var users = new FakeUsers(new User("s1", true));
        var prices = new FakePrices(100m);
        var clock = new FakeClock(new DateTime(2026, 12, 1));
        var orders = new FakeOrders();
        var ui = new FakeUi(new[] { "s1", "COUPON" }); // Askが2回呼ばれる想定

        var sut = new CheckoutUseCase(users, prices, clock, orders, ui);

        var result = await sut.ExecuteAsync();

        Assert.Equal("OK", result);
        Assert.Single(orders.Saved);
        Assert.Contains("Total =", ui.ShownMessages[0]);
    }

    private sealed class FakeUsers : IUserRepository
    {
        private readonly User _user;
        public FakeUsers(User user) => _user = user;
        public Task<User> LoadAsync(string userId) => Task.FromResult(_user with { Id = userId });
    }

    private sealed class FakePrices : IPriceClient
    {
        private readonly decimal _price;
        public FakePrices(decimal price) => _price = price;
        public Task<decimal> GetTodayPriceAsync() => Task.FromResult(_price);
    }

    private sealed class FakeClock : IClock
    {
        public FakeClock(DateTime now) => Now = now;
        public DateTime Now { get; }
    }

    private sealed class FakeOrders : IOrderRepository
    {
        public List<Order> Saved { get; } = new();
        public Task SaveAsync(Order order) { Saved.Add(order); return Task.CompletedTask; }
    }

    private sealed class FakeUi : IConsoleUi
    {
        private readonly Queue<string> _answers;
        public List<string> ShownMessages { get; } = new();

        public FakeUi(IEnumerable<string> answers) => _answers = new Queue<string>(answers);

        public string Ask(string message) => _answers.Dequeue();
        public void Show(string message) => ShownMessages.Add(message);
    }
}
```

やった〜！🎉
「Console も HTTP も DB も無し」で、購入処理のテストが回せるようになった🧪💖

---

## 21-9. 分解トレーニング 3本勝負 🏋️‍♀️🔥✨

### 練習1：締切チェックを分解 🕰️✂️

* “応募できる？” の判定だけピュアにしてテストする🎯
* 締切の時刻は IClock で渡す🧩

### 練習2：抽選ロジックを分解 🎲✂️

* “当たり判定” をピュア（または IRandom を境界）にする🎯
* 乱数を固定できるようにしてテスト安定🌪️➡️🧪

### 練習3：ファイル読み込み→変換→表示を分解 🗂️✂️

* 読み込み（I/O）と、変換（ピュア）を分ける📦
* 変換だけを重点的に単体テストする✨

コツは全部同じだよ😉✨

1. I/Oに蛍光ペン🖍️
2. 判断を先に終わらせる🎯
3. ユースケースで実行する🧩

---

## 21-10. AIを“分解コーチ”にするプロンプト集 🤖💡✨

Copilot/Codex に投げるときは、こういう頼み方が効くよ〜😊💖

* 「このメソッドの I/O を列挙して、境界インターフェース案を出して」🧾
* 「この if を “ルール if” と “I/O if” に分類して、分離の方針を提案して」🔀
* 「ピュア関数に抜くなら、引数と戻り値は何が良い？」🎯
* 「ユースケース Execute の形に組み直して、Fake でテストできるようにして」🧪🎭

⚠️注意ポイントも一個だけ！
AIが “便利だから” って、ユースケースの中に new を増やしたり、I/Oを混ぜ直したらアウト〜😇💥
**境界が増えてるか？差し替えできるか？** を必ず目でチェック👀✅

---

## 21-11. まとめ 🎓✨

この章の合言葉はこれだよ〜😊💖

* **大きい関数は、分解できるサイン！** 🧱✨
* **判断（ルール）を先に、I/Oは後で！** 🎯🚪
* **ユースケース単位で組み立てる！** 🧩🏗️

次の第22章では、「じゃあ new（組み立て）はどこに置くのが正解？」っていう **Composition Root** をやるよ〜📍✨
ここまで分解できてると、次章がめっちゃ気持ちよく繋がるよ😉💖

[1]: https://devblogs.microsoft.com/dotnet/announcing-dotnet-10/?utm_source=chatgpt.com "Announcing .NET 10"
[2]: https://learn.microsoft.com/ja-jp/dotnet/csharp/whats-new/csharp-14?utm_source=chatgpt.com "C# 14 の新機能"
[3]: https://learn.microsoft.com/en-us/visualstudio/releases/2026/release-notes?utm_source=chatgpt.com "Visual Studio 2026 Release Notes"
[4]: https://dotnet.microsoft.com/en-US/download/dotnet/10.0 "Download .NET 10.0 (Linux, macOS, and Windows) | .NET"
[5]: https://xunit.net/docs/getting-started/v3/microsoft-testing-platform?utm_source=chatgpt.com "Microsoft Testing Platform (xUnit.net v3) [2025 November 2]"
