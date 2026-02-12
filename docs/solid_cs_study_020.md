# 第20章：ISP実戦：読み取り用・更新用を分ける📖✍️

この章は **「読むだけの人に、書く道具を持たせない」** がテーマだよ〜😊
同じ“注文データ”でも、使う側（画面・バッチ・テスト…）で必要な操作って全然ちがうよね？そこを **インターフェースでちゃんと分ける** 練習をします💪💕

（ちなみに2026の最新前提として、.NET 10 は 2025/11/11 リリースの LTS、C# 14 は .NET 10 対応、Visual Studio 2026 に .NET 10 SDK が含まれるよ🆕✨） ([Microsoft][1])

---

## この章のゴール🎯✨

* 「太いインターフェース」が何を壊すのか体感する😵‍💫💥
* **Read（参照）** と **Write（更新）** を分けて、利用者の負担を減らす✂️💕
* 画面・バッチ・テストなど、**利用者視点で“必要な約束だけ”作れる** ようになる😊🌸

---

## まず、ありがちな“太いインターフェース”😈📦

![Fat Interface Bloat](./picture/solid_cs_study_020_fat_interface_bloat.png)


例：注文を扱う `IOrderRepository` が全部盛り…🍔🍟🥤

```csharp
public interface IOrderRepository
{
    Task<Order?> GetByIdAsync(Guid id, CancellationToken ct = default);
    Task<IReadOnlyList<Order>> SearchAsync(string keyword, CancellationToken ct = default);

    Task SaveAsync(Order order, CancellationToken ct = default);
    Task UpdateStatusAsync(Guid id, OrderStatus newStatus, CancellationToken ct = default);
    Task DeleteAsync(Guid id, CancellationToken ct = default);
}

public enum OrderStatus { Draft, Paid, Shipped, Cancelled }

public sealed record Order(Guid Id, string CustomerName, decimal Total, OrderStatus Status);
```

### これの何がツラいの？😇💦

![Screen Delete Risk](./picture/solid_cs_study_020_screen_delete_risk.png)


たとえば「注文一覧を表示する画面」は、`SearchAsync` しか使わないのに…

* **更新/削除メソッドまで見えちゃう** → 誤用の誘惑が増える🙈💥
* **モック/フェイクが重くなる**（テストで Delete まで実装させられる）😵‍💫
* 将来、更新系の仕様変更が入ると、参照側まで巻き添えコンパイルエラー🤯

ISPの気持ち：
👉 **“使わないメソッドに依存させないで”** ってことだよ✂️💕

---

## 使う人（利用者）を分けてみよ〜👥✨

![User Types](./picture/solid_cs_study_020_user_types.png)


同じ注文でも、利用者タイプで必要な操作が違うよね😊

* 注文一覧画面：検索・詳細表示だけ見たい👀📄
* 管理画面：ステータス更新したい🛠️✨
* バッチ：期限切れ注文をキャンセルしたい⏰🧹
* テスト：読み取りだけのフェイクが欲しい🧪💕

この“違い”がそのままインターフェース分割の根拠になるよ👍💡

---

## 解決：Read と Write を分ける📖✍️✂️

![Viewer with Reader Glasses vs Admin with Writer Pen. Read/Write segregation.](./picture/solid_cs_study_020_isp_read_write.png)

### ✅ After（分割版）

```csharp
public interface IOrderReader
{
    Task<Order?> GetByIdAsync(Guid id, CancellationToken ct = default);
    Task<IReadOnlyList<Order>> SearchAsync(string keyword, CancellationToken ct = default);
}

public interface IOrderWriter
{
    Task SaveAsync(Order order, CancellationToken ct = default);
    Task UpdateStatusAsync(Guid id, OrderStatus newStatus, CancellationToken ct = default);
    Task DeleteAsync(Guid id, CancellationToken ct = default);
}
```

これだけで世界がだいぶ平和になるよ🕊️✨
「読む側」は `IOrderReader` だけ持てばOK、「更新する側」は `IOrderWriter` だけ持てばOK😊

---

## “利用者ごと”に依存を貼る（ここが実戦！）🔥

![Targeted Dependency](./picture/solid_cs_study_020_targeted_dependency.png)


### ① 注文一覧（読むだけ）👀📄

```csharp
public sealed class OrderListUseCase
{
    private readonly IOrderReader _reader;

    public OrderListUseCase(IOrderReader reader) => _reader = reader;

    public Task<IReadOnlyList<Order>> SearchAsync(string keyword, CancellationToken ct = default)
        => _reader.SearchAsync(keyword, ct);
}
```

💡 ここがポイント：
このクラスは **更新の存在すら知らない** ✨（だから壊れにくい！）

---

### ② ステータス変更（書く側）🛠️🚚

```csharp
public sealed class ChangeOrderStatusUseCase
{
    private readonly IOrderWriter _writer;

    public ChangeOrderStatusUseCase(IOrderWriter writer) => _writer = writer;

    public Task ExecuteAsync(Guid orderId, OrderStatus status, CancellationToken ct = default)
        => _writer.UpdateStatusAsync(orderId, status, ct);
}
```

---

### ③ 「読む＋書く」両方必要なケースもあるよね🙂🔁

![Dual Dependency](./picture/solid_cs_study_020_dual_dependency.png)


そのときは **両方に依存してOK**（無理に1本化しないのがISP脳！）

```csharp
public sealed class CheckoutUseCase
{
    private readonly IOrderReader _reader;
    private readonly IOrderWriter _writer;

    public CheckoutUseCase(IOrderReader reader, IOrderWriter writer)
        => (_reader, _writer) = (reader, writer);

    public async Task PayAsync(Guid orderId, CancellationToken ct = default)
    {
        var order = await _reader.GetByIdAsync(orderId, ct);
        if (order is null) throw new InvalidOperationException("Order not found.");

        var paid = order with { Status = OrderStatus.Paid };
        await _writer.SaveAsync(paid, ct);
    }
}
```

---

## 実装クラスは1つでもOK（でも見せる顔を変える）🎭✨

![One Class Two Faces](./picture/solid_cs_study_020_one_class_two_faces.png)


「実装は1クラス」で、**インターフェースを2つ実装**すればOKだよ😊

```csharp
using System.Collections.Concurrent;

public sealed class InMemoryOrderStore : IOrderReader, IOrderWriter
{
    private readonly ConcurrentDictionary<Guid, Order> _db = new();

    public Task<Order?> GetByIdAsync(Guid id, CancellationToken ct = default)
        => Task.FromResult(_db.TryGetValue(id, out var v) ? v : null);

    public Task<IReadOnlyList<Order>> SearchAsync(string keyword, CancellationToken ct = default)
    {
        var list = _db.Values
            .Where(o => o.CustomerName.Contains(keyword, StringComparison.OrdinalIgnoreCase))
            .ToList()
            .AsReadOnly();

        return Task.FromResult((IReadOnlyList<Order>)list);
    }

    public Task SaveAsync(Order order, CancellationToken ct = default)
    {
        _db[order.Id] = order;
        return Task.CompletedTask;
    }

    public Task UpdateStatusAsync(Guid id, OrderStatus newStatus, CancellationToken ct = default)
    {
        if (_db.TryGetValue(id, out var old))
            _db[id] = old with { Status = newStatus };

        return Task.CompletedTask;
    }

    public Task DeleteAsync(Guid id, CancellationToken ct = default)
    {
        _db.TryRemove(id, out _);
        return Task.CompletedTask;
    }
}
```

🌟 重要：
利用者は **`InMemoryOrderStore` を直接知らなくていい**。
「読む人には読む口（IOrderReader）だけ」「書く人には書く口（IOrderWriter）だけ」見せるのがISPだよ〜✂️💕

---

## ありがち事故と対策🚑💦

### ❌ 事故1：分けたのに、結局 “全部入り” を注入しちゃう

* 利用者クラスのコンストラクタが `IOrderReader` じゃなくて `InMemoryOrderStore` とか `IOrderRepository` になってる😇
  ✅ **依存先を必ず細い方にする**（利用者が見たい約束だけ）

### ❌ 事故2：Read側が更新メソッドを返し始める

* 例：`GetByIdAsync` が「追跡付きEntity」を返して、触っただけで更新される系😵‍💫
  ✅ “読む”は読む。必要なら**Read用DTO**にする（軽くCQRSっぽい発想）📖✨

### ❌ 事故3：細かくしすぎて迷子

✅ 最初は **Read / Write の2分割**で十分！
（もっと細くしたくなったら「誰が困ってる？」を根拠に✂️）

---

## Copilot / AI の使いどころ🤖✨（超実戦）

Visual Studio 2026 はAI統合が強化されていて、Copilotも統合的に使える流れだよ🧠⚡ ([Microsoft Learn][2])
（CopilotはVSの対応バージョン要件があるので、そこだけ注意ね🔧） ([GitHub Docs][3])

### 使えるプロンプト例💬✨

* 「この `IOrderRepository` を “読み取り用” と “更新用” に分割して。利用者クラスごとに必要なメソッドも整理して」
* 「注文一覧画面が依存すべき最小インターフェースを提案して」
* 「分割後に発生するコンパイルエラーを直す手順を、変更箇所の順番付きで出して」
* 「Read側のフェイク実装（テスト用）を最小で作って」

---

## 演習（手を動かすやつ）🧩🔥

![Exercise Kit](./picture/solid_cs_study_020_exercise_kit.png)


### 演習1：利用者タイプを書き出す📝

あなたのサンプルで、利用者を3つ挙げてね😊
例：画面・管理・バッチ・テスト…など！

### 演習2：太いIFを2つに分割✂️

* `IOrderRepository` → `IOrderReader` / `IOrderWriter`
* 利用者クラスの依存を「細い方」に付け替え

### 演習3：テストがラクになったのを味わう🧪✨

* 「注文一覧」用に **Readだけのフェイク**を作ってみてね
* Writeメソッドを実装しなくてよくなる快感…🥹💕

---

## ミニまとめ🌈✨

* ISPは **“利用者が必要な約束だけ持つ”** ための原則✂️😊
* 実戦で一番効く型が **Read/Write 分離**（読む人に書く道具を渡さない）📖✍️
* テストも変更もラクになるよ〜🧪🧼💕

---

次の第21章では、外部APIみたいに「向こう都合で変な形」になってるやつを **Adapterで内側を守る**やつに進むよ🔌🛡️✨

[1]: https://dotnet.microsoft.com/en-us/platform/support/policy/dotnet-core?utm_source=chatgpt.com "NET and .NET Core official support policy"
[2]: https://learn.microsoft.com/en-us/visualstudio/releases/2026/release-notes?utm_source=chatgpt.com "Visual Studio 2026 Release Notes"
[3]: https://docs.github.com/copilot/using-github-copilot/getting-code-suggestions-in-your-ide-with-github-copilot?utm_source=chatgpt.com "Getting code suggestions in your IDE with GitHub Copilot"
