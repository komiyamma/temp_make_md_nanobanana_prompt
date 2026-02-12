# 第19章：ISPの入口「太いインターフェースは使う人を苦しめる」😵‍💫

この章はひとことで言うと…
**「使わないメソッドまで“知ってることにされる”のをやめよう」**って話だよ〜！😊✨

---

## 1) ISPってなに？（超やさしく）📌😊

![Universal Remote (complex) vs Specific Purpose Remote (simple).](./picture/solid_cs_study_019_isp_universal_remote.png)

ISP（Interface Segregation Principle）は、だいたいこういう意味👇

* **使わないメソッドに依存させない**
* **“万能インターフェース”をやめて、用途別に小さくする**

有名な言い方だと👇
**「クライアントは、使わないメソッドに依存させられるべきではない」**って感じ🫶✨ ([Object Mentor][1])

> イメージ：
> 「テレビ見るだけなのに、エアコン・照明・カーテンまでボタンが付いてるリモコン」📺🧊💡😇
> 使う側も、作る側も、事故りやすいよね〜！

---

## 2) “太いインターフェース”が生む地獄あるある🔥😇

### あるある①：実装クラスがムダに苦しい💦

* 使わないメソッドまで **実装を強制**される
* 結果：`throw new NotImplementedException()` が出てくる💣

### あるある②：利用側が事故りやすい⚠️

* 画面は「参照だけ」したいのに `Delete()` が見えてる😨
* “間違って呼べる” ＝ “間違いが起きる” 🫠

### あるある③：変更の波及が増える🌊

* 1個の変更（例：保存の仕様）で、参照しかしてない画面まで影響…
* **依存が太い**ほど、影響範囲が太る🫃（太るな！😂）

---

## 3) ISP違反を見抜くチェックリスト✅🕵️‍♀️

次のどれかが出たら、ISP疑い濃厚だよ〜！✨

* `IService` / `IManager` / `IRepository` が **なんでも屋**になってる🧺
* メソッド数が増え続けて **10個超え**が当たり前😵
* 実装に **ダミー**や **NotImplemented** が混ざる💣
* テスト用Fakeが作れなくて **泣く**😭
* 「参照だけの人」まで「更新系メソッド」を知ってる📖✍️

---

## 4) 例：ミニECの「太すぎRepository」問題🛒💥

![God Interface Monster](./picture/solid_cs_study_019_god_interface_monster.png)

まず、わざと“太い”やつを見てみよっか😈

```csharp
public interface IOrderRepository
{
    // 読み取り
    Order? GetById(Guid id);
    IReadOnlyList<Order> Search(string keyword);

    // 更新
    void Add(Order order);
    void Update(Order order);
    void Delete(Guid id);

    // 永続化・トランザクションっぽいもの
    Task SaveChangesAsync(CancellationToken ct = default);
    IDisposable BeginTransaction();
}
```

### 参照画面（検索）だけしたいクラスなのに…😇

![Client Burden](./picture/solid_cs_study_019_client_heavy_backpack.png)

```csharp
public sealed class OrderQueryService
{
    private readonly IOrderRepository _repo;

    public OrderQueryService(IOrderRepository repo) => _repo = repo;

    public IReadOnlyList<Order> Search(string keyword)
        => _repo.Search(keyword);
}
```

この `OrderQueryService`、**Searchしか使ってない**のに、依存は `IOrderRepository` 全部🥲
つまり **Delete/SaveChanges/BeginTransaction まで“知ってる側”** になっちゃうの。

### テストでも地獄（Fakeが太る）😭🧪

![Mocking Hell](./picture/solid_cs_study_019_mocking_hell.png)

```csharp
public sealed class FakeOrderRepository : IOrderRepository
{
    private readonly List<Order> _orders = new();

    public Order? GetById(Guid id) => _orders.FirstOrDefault(x => x.Id == id);
    public IReadOnlyList<Order> Search(string keyword) => _orders;

    public void Add(Order order) => throw new NotImplementedException();
    public void Update(Order order) => throw new NotImplementedException();
    public void Delete(Guid id) => throw new NotImplementedException();
    public Task SaveChangesAsync(CancellationToken ct = default) => throw new NotImplementedException();
    public IDisposable BeginTransaction() => throw new NotImplementedException();
}
```

**参照テストしたいだけ**なのに、未使用メソッドのせいで、Fakeが爆発する〜〜〜😭💥

---

## 5) ISPの解決： “使う人ごと”にインターフェースを分ける✂️✨

ポイントは超シンプル👇
**「誰（クライアント）が、どれを使うの？」を先に分ける**😊

### Step 1：クライアント（利用者タイプ）を出す👥

例）

* 参照画面（検索・詳細）📖
* 管理画面（追加・更新・削除）✍️
* バッチ（出荷ステータス更新）🤖

### Step 2：使うメソッドだけをグルーピング🧩

* 参照だけ → “読むインターフェース”
* 更新だけ → “書くインターフェース”

### Step 3：小さいインターフェースに分割✂️

![Interface Split](./picture/solid_cs_study_019_interface_split_scissors.png)

```csharp
public interface IOrderReader
{
    Order? GetById(Guid id);
    IReadOnlyList<Order> Search(string keyword);
}

public interface IOrderWriter
{
    void Add(Order order);
    void Update(Order order);
    void Delete(Guid id);
    Task SaveChangesAsync(CancellationToken ct = default);
}
```

✅ これで「参照画面」は `IOrderReader` だけ知ってればOK！
✅ 「管理画面」は `IOrderWriter` を使えばOK！

参照サービスはこうなるよ👇✨

![Happy Client](./picture/solid_cs_study_019_happy_client_light.png)

```csharp
public sealed class OrderQueryService
{
    private readonly IOrderReader _reader;

    public OrderQueryService(IOrderReader reader) => _reader = reader;

    public IReadOnlyList<Order> Search(string keyword)
        => _reader.Search(keyword);
}
```

Fakeも一気に軽くなる〜！🥹💕

![Clean Fake Joy](./picture/solid_cs_study_019_clean_fake_joy.png)

```csharp
public sealed class FakeOrderReader : IOrderReader
{
    private readonly List<Order> _orders = new();

    public Order? GetById(Guid id) => _orders.FirstOrDefault(x => x.Id == id);
    public IReadOnlyList<Order> Search(string keyword) => _orders;
}
```

---

## 6) 分割するときの命名のコツ（初心者向け）📝✨

迷ったらこのどれかでだいたい勝てるよ👍

* `IOrderReader` / `IOrderWriter`（読み書きで分ける）📖✍️
* `IOrderQueryService` / `IOrderCommandService`（用途で分ける）🔎🛠️
* `IOrderSearch` / `IOrderDetail`（画面単位で分ける）🖥️

> 大事なのは **“実装都合”じゃなく“利用者都合”** で切ることだよ😊

---

## 7) Visual Studioでの実践ヒント🪄🪟

* **Find All References（参照の検索）**で「誰が何を使ってるか」を洗い出す🔎
* クラスから **Extract Interface** して、必要なものだけ残す✂️
* いきなり全部分けず、まずは
  **「参照用」「更新用」** の2つに割るのが成功しやすい😊✨

---

## 8) “分けすぎ”注意！⚖️😅（ISPの落とし穴）

ISPは大事なんだけど、こうなると逆に辛いよ〜👇

* `IOrderGetById` とか **1メソッド1インターフェース** 量産😵‍💫
* プロジェクト全体がインターフェースだらけで迷子🧭

目安としては、

* **「利用者タイプが違う」**
* **「変更理由が違う」**
* **「テストで差し替えたい境界」**

このへんが揃ったら分けどき！✨

---

## 9) 🤖AI（Copilot/Codex系）に頼むと超はかどるプロンプト集💖

### ① “太い原因”を見つける

* 「このインターフェースが太い理由を、利用者視点で箇条書きして。未使用メソッド依存のリスクも」

### ② “誰が何を使うか”をマトリクス化

* 「参照画面／管理画面／バッチの3種類の利用者を想定して、必要メソッド一覧表を作って」

### ③ 分割案を作る

* 「ISPに従って、役割別インターフェース（Reader/Writerなど）へ分割して。命名案を3パターン出して」

### ④ 安全に直す手順（コミット単位）

* 「破壊しないリファクタ手順をコミット単位で提案して（1コミット＝1目的）」

さらに、リポジトリに **カスタム指示**を置くと、設計の癖が統一されて強いよ🧠✨
GitHub Copilot は “リポジトリのカスタム指示ファイル” に対応してるよ（Visual Studio も選べる）📄🤝 ([GitHub Docs][2])

---

## 10) まとめ🎀✨

* ISPは **「使わないメソッドに依存させない」** 原則だよ😊 ([Object Mentor][1])
* “太いインターフェース”は
  **実装もテストも利用も**つらくする😭
* 解決は **利用者ごと（役割ごと）に小さく分割**✂️✨
  → Fakeが軽くなる、事故が減る、変更が局所化する💪

---

## 次章予告（第20章）📖✍️✨

次はまさに今日の続き！
**「読み取り用／更新用」を実戦で分けて、設計をキレイにする**よ〜！🥳🎉

---

### （最新環境メモ）🧷

この教材の前提になってる **.NET 10 は 2025/11/11 リリースのLTS**で、サポートも継続中だよ✅ ([Microsoft][3])
**Visual Studio 2026** も提供されていて、**C# 14** の新機能も “VS 2026 や .NET 10 SDK” で試せるよ✨ ([learn.microsoft.com][4])

[1]: https://objectmentor.com/resources/articles/isp.pdf?utm_source=chatgpt.com "The Interface Segregation Principle - Object Mentor"
[2]: https://docs.github.com/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot?utm_source=chatgpt.com "Adding repository custom instructions for GitHub Copilot"
[3]: https://dotnet.microsoft.com/ja-jp/platform/support/policy/dotnet-core?utm_source=chatgpt.com ".NET および .NET Core の公式サポート ポリシー"
[4]: https://learn.microsoft.com/en-us/visualstudio/releases/2026/release-notes?utm_source=chatgpt.com "Visual Studio 2026 Release Notes"
