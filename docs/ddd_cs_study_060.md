# 第60章：依存性注入（DI）の真の目的💉✨

![依存性注入（DI）の真の目的](./picture/ddd_cs_study_060_di_swappable.png)

**テスト時に「本物のDB」を使わなくて済むようにする🧪🗄️**

---

## 今日のゴール🎯

この章が終わると、次の状態になれます😊

* 「DIって結局なにが嬉しいの？」にスパッと答えられる💡
* **DBなしでユースケースをテスト**できるようになる🧪✨
* そして、AI（Copilot/Codex）に頼んでも**設計が崩れにくくなる**🚀

---

## 1. DIなしだと、なにがつらいの？😇（あるある地獄）

![060_battery_swap](./picture/ddd_cs_study_060_battery_swap.png)

たとえば「ユーザー登録」を作るとします。

### ❌よくある“直書き”パターン

* アプリの処理の中で **DBに直接つなぐ**

* そのせいでテストしたいのに…

* DBが必要😵

* 接続文字列が必要😵

* テーブル作成が必要😵

* テストが遅い😵

* テストデータ掃除が面倒😵

つまり…
**「ユースケースのテスト」なのに「DBの準備」で詰む**んです🫠

---

## 2. 依存（Dependency）ってなに？🧩

![060_constructor_injection](./picture/ddd_cs_study_060_constructor_injection.png)

「ユーザー登録」の処理が、DBアクセスの部品に頼ってる（＝依存してる）状態。

* ユースケース（主役）🎬
* DBアクセス（脇役）🧰

主役が脇役に**ベッタリ**だと、脇役が用意できないと何もできない…ってなります😢

---

## 3. 発想を逆にする💡「newしないで、外から渡す」

![060_manual_assembly](./picture/ddd_cs_study_060_manual_assembly.png)

DIのコアはこれだけです👇

> **必要な部品を、自分で new しない**
> **外から渡してもらう**（注入する）💉
 
 ```mermaid
 sequenceDiagram
    participant App as UseCase
    participant Repo as Repository
    participant DB as Database
    
    Note over App, DB: ❌ newする場合 (依存)
    App->>Repo: new Repository()
    Repo-->>DB: 接続が必要💥
    
    Note over App, DB: ⭕ DIする場合 (注入)
    participant Test as Test/Main
    Test->>Repo: new Repository()
    Test->>App: new UseCase(repo) 💉
    App->>Repo: Save()
    Note right of App: DBのことは知らない！😌
 ```
 
 .NET にはDIがフレームワークの一部として組み込まれていて、設定やログ等とも一緒に使える前提になっています。([Microsoft Learn][1])

---

## 4. “DBそのもの”じゃなくて“約束（インターフェース）”に依存する🤝

![060_interface_socket](./picture/ddd_cs_study_060_interface_socket.png)

DDDの流れだと、ここで出てくるのが **Repository** でしたね🙂
DIのために、まず **「保存する」約束** を作ります。

### ✅Domain / Application 側（約束だけ持つ）

```csharp
public interface IUserRepository
{
    Task AddAsync(User user, CancellationToken ct);
    Task<User?> FindByEmailAsync(Email email, CancellationToken ct);
}
```

ポイントはここ✨

* Applicationは **IUserRepository（約束）** だけ知ってる
* 「EF Core？SQL？知らん！」でOK🙆‍♀️

---

## 5. これが本題🔥 テスト用に“偽物DB”を差し込める🧪✨

本物DBを使わないために、テストではこうします👇

### ✅テスト用 InMemory 実装（偽物）

```csharp
public sealed class InMemoryUserRepository : IUserRepository
{
    private readonly List<User> _users = new();

    public Task AddAsync(User user, CancellationToken ct)
    {
        _users.Add(user);
        return Task.CompletedTask;
    }

    public Task<User?> FindByEmailAsync(Email email, CancellationToken ct)
    {
        var user = _users.FirstOrDefault(x => x.Email == email);
        return Task.FromResult(user);
    }
}
```

これでテストは…

* DB不要😍
* 超高速😍
* 失敗原因が分かりやすい😍

**ユースケースのロジックだけ**を安心してテストできます🧪✨

---

## 6. ユースケース（Applicationサービス）をDIできる形にする🧠

「ユーザー登録」ユースケース例です👇

```csharp
public sealed class RegisterUserUseCase
{
    private readonly IUserRepository _userRepository;

    public RegisterUserUseCase(IUserRepository userRepository)
    {
        _userRepository = userRepository;
    }

    public async Task<Result> ExecuteAsync(string emailRaw, CancellationToken ct)
    {
        var email = Email.Create(emailRaw);
        if (email.IsFailure) return email.Error!;

        var exists = await _userRepository.FindByEmailAsync(email.Value!, ct);
        if (exists is not null) return Result.Failure("このメールアドレスは既に登録されています");

        var user = User.Create(email.Value!);
        await _userRepository.AddAsync(user, ct);

        return Result.Success();
    }
}
```

ここが気持ちいいところ😊

* `RegisterUserUseCase` は **DBを知らない**
* Repositoryを差し替えるだけで、テストも本番も回る♻️

---

## 7. .NETのDIコンテナに「本番の部品」を登録する🧰

![060_di_container](./picture/ddd_cs_study_060_di_container.png)

本番では当然、EF CoreなどのRepository実装を使いたいですよね🙂
そこで `.NET標準DI` に登録します。

### ✅ASP.NET Coreの例（Program.cs）

```csharp
var builder = WebApplication.CreateBuilder(args);

// 例：本番用の実装を登録
builder.Services.AddScoped<IUserRepository, EfUserRepository>();

var app = builder.Build();
app.Run();
```

`AddScoped` / `AddTransient` / `AddSingleton` などのライフタイムがあり、.NETの公式ドキュメントでも基本として整理されています。([Microsoft Learn][2])

ざっくり感覚はこれ👇（超入門版）

* `AddTransient`：毎回new（軽い部品向き）
* `AddScoped`：リクエスト中は同じ（DBアクセス系でよく使う）
* `AddSingleton`：ずっと同じ（設定・キャッシュ系）

---

## 8. じゃあ「DIの真の目的」って結局なに？💡（答え）

ここまでの話を一言にすると…

### ✅DIの真の目的

**「差し替え可能にして、テストをラクにする」**🧪✨

特に強いのがこれ👇

* **“本物DB”を使わないテストができる**
* だから **速い・安定・原因が分かる**
* そして **変更に強い**（DBや外部APIが変わっても、約束さえ守ればOK）

---

## 9. やりすぎ注意⚠️（DIで迷子になるパターン）

DIは便利なんですが、初心者がハマりがち😇

### ❌全部インターフェースにする

* 変更しない・差し替えない部品まで抽象化すると
  “読むコスト”が増えて逆に遅くなります💦

### ✅目安（1人開発向け）

* **外部に触るもの**（DB / HTTP / ファイル / 時刻 / 乱数 / メール送信）
  → 抽象化してDIする価値が高い💎
* **純粋な計算**（副作用なし）
  → そのままでOK🙆‍♀️

---

## 10. AI（Copilot/Codex）に頼むときのコツ🤖✨

AIはDIの“型”を作らせると超強いです💪

### ✅おすすめプロンプト（そのまま投げてOK）

* 「`IUserRepository` を定義して、InMemory実装も作って。スレッドセーフは不要。メソッドは Add と FindByEmail。」
* 「`RegisterUserUseCase` をDI前提（コンストラクタ注入）で書いて。例外は投げず Result で返して。」
* 「xUnitで、DBなしで通るテストを書いて。既存メールは失敗になるケースも。」

**コツは“設計の骨格（境界）を人間が決める”こと**🦴✨
ここが決まってると、AIが大量に書いても崩れにくいです😊

---

## 11. ミニ演習🧪✨「DBなしでユーザー登録をテストする」

やることは3つだけ！

### Step1：InMemoryUserRepository を用意（上のコードでOK）

### Step2：UseCase を new するときに注入する

```csharp
var repo = new InMemoryUserRepository();
var useCase = new RegisterUserUseCase(repo);
```

### Step3：xUnitでテスト（例）

```csharp
using Xunit;

public class RegisterUserUseCaseTests
{
    [Fact]
    public async Task 新規メールなら登録成功する()
    {
        var repo = new InMemoryUserRepository();
        var useCase = new RegisterUserUseCase(repo);

        var result = await useCase.ExecuteAsync("test@example.com", CancellationToken.None);

        Assert.True(result.IsSuccess);
    }

    [Fact]
    public async Task 既存メールなら失敗する()
    {
        var repo = new InMemoryUserRepository();
        var useCase = new RegisterUserUseCase(repo);

        await useCase.ExecuteAsync("test@example.com", CancellationToken.None);
        var result2 = await useCase.ExecuteAsync("test@example.com", CancellationToken.None);

        Assert.True(result2.IsFailure);
    }
}
```

これができたら、あなたはもう
**「DBに振り回されない設計」**の入り口に立ってます🚪✨

---

## まとめ📌🎉

* DIは「カッコいい技術」じゃなくて、**差し替えのための仕組み**💉
* 真のご褒美は **テストで本物DBを使わなくていいこと**🧪🗄️
* だから、開発が速くなって、壊れにくくなる🚀
* AIにコード生成を任せても、境界が守れて事故りにくい🤖✨

---

次の章（第61章）では、このDIと相性バツグンな **「アプリケーションサービス（ユースケース層）」** を、もう少しキレイに整理していきますよ〜😊📚

[1]: https://learn.microsoft.com/en-us/dotnet/core/extensions/dependency-injection?utm_source=chatgpt.com "Dependency injection - .NET"
[2]: https://learn.microsoft.com/en-us/aspnet/core/fundamentals/dependency-injection?view=aspnetcore-10.0&utm_source=chatgpt.com "Dependency injection in ASP.NET Core"
