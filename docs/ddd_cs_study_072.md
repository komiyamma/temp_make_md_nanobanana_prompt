# 第72章：モック（Moq / NSubstitute）の使い方🧸✨ 〜1人でも「偽物」を作って爆速開発〜

この章では、**「DBや外部APIがなくても、テストを秒速で回せる」**ようになるための“モック”を覚えます💨
1人開発だと、**確認作業がぜんぶ自分**に降ってくるので、ここを押さえると一気にラクになります🥹🫶

※いまの最新ど真ん中は **.NET 10 + C# 14** あたりの世代です（C# 14 が最新で .NET 10 対応） ([Microsoft Learn][1])

---

## 1. モックってなに？🪄（超ざっくり）

テストで使う「偽物の相棒」です🤝✨
本物（DB / メール送信 / 外部API）を使うと…

* 遅い🐢
* 不安定（ネット落ちたら終わり）📡💥
* テストが準備地獄になる😇

そこで、**外側の依存を“偽物”に差し替えて**、ロジックだけをサクッと検証します✅

よくある用語のイメージ👇

* **Stub（スタブ）**：返り値だけ用意する偽物（「こう返してね」）
* **Mock（モック）**：呼ばれ方までチェックできる偽物（「1回呼んだ？」）
* **Fake（フェイク）**：簡易実装の偽物（メモリ内DBみたいなやつ）

この章は **Mock中心**でいきます💪😺

![Mocking Concept](./picture/ddd_cs_study_072_mocking.png)

---

## 2. どこをモックするの？（迷わないルール）🧭✨

![ddd_cs_study_072_boundary_mock](./picture/ddd_cs_study_072_boundary_mock.png)

モックは基本ここだけ👇

✅ **アプリの“外側”にあるもの**
 
 ```mermaid
 flowchart LR
     subgraph App["アプリ (本物を使う)"]
       Logic[ロジック]
       Domain["Domain<br/>(ValueObject/Entity)"]
     end
     
     subgraph Boundary["境界 (モックする)"]
       Repo[Repository]
       Mail[MailSender]
       Time[Clock]
     end
     
     subgraph External["外の世界 (触らない)"]
       DB[(Database)]
       SMTP((SMTP Server))
       RealTime((Real Time))
     end
     
     Logic --> Domain
     Logic --> Repo
     Logic --> Mail
     Logic --> Time
     
     Repo -.-> DB
     Mail -.-> SMTP
     Time -.-> RealTime
     
     style Boundary fill:#f9f9f9,stroke:#333,stroke-dasharray: 5 5
     style External fill:#ddd,stroke:#999
     style App fill:#e3f2fd,stroke:#2196f3
 ```
 
 * DB（Repository）🗄️
 * メール送信✉️
* 外部API🌐
* 時刻（DateTime）⏰ ←地味に超重要！

🚫 **ドメインの中身はなるべくモックしない**

* 値オブジェクトやエンティティは「本物」でテストした方が早いです🙂
* “本物なのに軽い”のがDDDの強みなので✨

---

## 3. Moq と NSubstitute、どっち使う？🤔🎀

![ddd_cs_study_072_moq_vs_nsubstitute](./picture/ddd_cs_study_072_moq_vs_nsubstitute.png)

どっちも人気です！

* **Moq**：Setup/Verify で明示的に書けるタイプ。超定番。NuGet上の最新版例：4.20.72 ([NuGet][2])
* **NSubstitute**：英語っぽい読みやすさでサクサク書けるタイプ。最新版例：5.3.0 ([NuGet][3])

この章では **両方の書き方を同じ題材で見せる**ので、好きな方を選べます🍩✨

---

## 4. お題：会員登録ユースケースをテストする👩‍💻✨

やりたいこと👇
「メールで会員登録する」

* すでに登録済みなら失敗（DB確認が必要）
* 新規なら登録して、歓迎メールを送る（メール送信が必要）
* 作成日時は固定したい（時刻が必要）

つまり **DB / メール / 時刻**をモックしたい👏

---

## 5. 実装（最小構成）🧩

### 5-1. Domain（メールとユーザー）

```csharp
namespace MyApp.Domain;

public sealed record EmailAddress
{
    public string Value { get; }

    private EmailAddress(string value) => Value = value;

    public static EmailAddress Create(string value)
    {
        if (string.IsNullOrWhiteSpace(value))
            throw new ArgumentException("メールが空です", nameof(value));

        value = value.Trim();

        if (!value.Contains('@'))
            throw new ArgumentException("メール形式が変です", nameof(value));

        return new EmailAddress(value);
    }

    public override string ToString() => Value;
}

public readonly record struct UserId(Guid Value);

public sealed class User
{
    public UserId Id { get; }
    public EmailAddress Email { get; }
    public DateTimeOffset CreatedAt { get; }

    public User(UserId id, EmailAddress email, DateTimeOffset createdAt)
    {
        Id = id;
        Email = email;
        CreatedAt = createdAt;
    }
}
```

### 5-2. Application（依存はインターフェースで！）

```csharp
using MyApp.Domain;

namespace MyApp.Application;

public interface IUserRepository
{
    Task<bool> ExistsByEmailAsync(EmailAddress email, CancellationToken ct);
    Task AddAsync(User user, CancellationToken ct);
}

public interface IEmailSender
{
    Task SendWelcomeAsync(EmailAddress email, CancellationToken ct);
}

public interface IClock
{
    DateTimeOffset UtcNow { get; }
}

public sealed record RegisterUserResult(bool Success, string? Error, UserId? UserId)
{
    public static RegisterUserResult Ok(UserId id) => new(true, null, id);
    public static RegisterUserResult Fail(string error) => new(false, error, null);
}

public sealed class RegisterUserService
{
    private readonly IUserRepository _users;
    private readonly IEmailSender _mailer;
    private readonly IClock _clock;

    public RegisterUserService(IUserRepository users, IEmailSender mailer, IClock clock)
    {
        _users = users;
        _mailer = mailer;
        _clock = clock;
    }

    public async Task<RegisterUserResult> RegisterAsync(string email, CancellationToken ct = default)
    {
        EmailAddress mail;
        try
        {
            mail = EmailAddress.Create(email);
        }
        catch
        {
            return RegisterUserResult.Fail("InvalidEmail");
        }

        if (await _users.ExistsByEmailAsync(mail, ct))
            return RegisterUserResult.Fail("AlreadyRegistered");

        var user = new User(new UserId(Guid.NewGuid()), mail, _clock.UtcNow);

        await _users.AddAsync(user, ct);
        await _mailer.SendWelcomeAsync(mail, ct);

        return RegisterUserResult.Ok(user.Id);
    }
}
```

---

## 6. テスト（Moq版）🐮✨

NuGetで **Moq** を追加して、テストで使います（最新版例：4.20.72） ([NuGet][2])

```csharp
using Moq;
using MyApp.Application;
using MyApp.Domain;
using Xunit;

public sealed class RegisterUserService_MoqTests
{
    [Fact]
    public async Task 既に登録済みなら_失敗して_登録もメールもされない()
    {
        var users = new Mock<IUserRepository>();
        var mailer = new Mock<IEmailSender>();
        var clock = new Mock<IClock>();

        users.Setup(x => x.ExistsByEmailAsync(
                It.Is<EmailAddress>(m => m.Value == "a@example.com"),
                It.IsAny<CancellationToken>()))
            .ReturnsAsync(true);

        var sut = new RegisterUserService(users.Object, mailer.Object, clock.Object);

        var result = await sut.RegisterAsync("a@example.com");

        Assert.False(result.Success);
        Assert.Equal("AlreadyRegistered", result.Error);

        users.Verify(x => x.AddAsync(It.IsAny<User>(), It.IsAny<CancellationToken>()), Times.Never);
        mailer.Verify(x => x.SendWelcomeAsync(It.IsAny<EmailAddress>(), It.IsAny<CancellationToken>()), Times.Never);
    }

    [Fact]
    public async Task 新規なら_登録されて_歓迎メールが1回送られる()
    {
        var users = new Mock<IUserRepository>();
        var mailer = new Mock<IEmailSender>();
        var clock = new Mock<IClock>();

        var now = new DateTimeOffset(2025, 12, 31, 0, 0, 0, TimeSpan.Zero);
        clock.SetupGet(x => x.UtcNow).Returns(now);

        users.Setup(x => x.ExistsByEmailAsync(It.IsAny<EmailAddress>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(false);

        var sut = new RegisterUserService(users.Object, mailer.Object, clock.Object);

        var result = await sut.RegisterAsync("b@example.com");

        Assert.True(result.Success);
        Assert.Null(result.Error);

        users.Verify(x => x.AddAsync(
                It.Is<User>(u => u.Email.Value == "b@example.com" && u.CreatedAt == now),
                It.IsAny<CancellationToken>()),
            Times.Once);

        mailer.Verify(x => x.SendWelcomeAsync(
                It.Is<EmailAddress>(m => m.Value == "b@example.com"),
                It.IsAny<CancellationToken>()),
            Times.Once);
    }
}
```

### Moqのコツ🎯

![ddd_cs_study_072_mock_role](./picture/ddd_cs_study_072_mock_role.png)

* `Setup(...)`：こう呼ばれたらこう返してね
* `Verify(...)`：本当に呼ばれた？回数は？
* `SetupGet(...)`：プロパティの返り値固定（時刻モックに便利⏰）

---

## 7. テスト（NSubstitute版）🦄✨

NuGetで **NSubstitute** を追加（最新版例：5.3.0） ([NuGet][3])

```csharp
using NSubstitute;
using MyApp.Application;
using MyApp.Domain;
using Xunit;

public sealed class RegisterUserService_NSubstituteTests
{
    [Fact]
    public async Task 既に登録済みなら_失敗して_登録もメールもされない()
    {
        var users = Substitute.For<IUserRepository>();
        var mailer = Substitute.For<IEmailSender>();
        var clock = Substitute.For<IClock>();

        users.ExistsByEmailAsync(
                Arg.Is<EmailAddress>(m => m.Value == "a@example.com"),
                Arg.Any<CancellationToken>())
            .Returns(true);

        var sut = new RegisterUserService(users, mailer, clock);

        var result = await sut.RegisterAsync("a@example.com");

        Assert.False(result.Success);
        Assert.Equal("AlreadyRegistered", result.Error);

        await users.DidNotReceive()
            .AddAsync(Arg.Any<User>(), Arg.Any<CancellationToken>());

        await mailer.DidNotReceive()
            .SendWelcomeAsync(Arg.Any<EmailAddress>(), Arg.Any<CancellationToken>());
    }

    [Fact]
    public async Task 新規なら_登録されて_歓迎メールが1回送られる()
    {
        var users = Substitute.For<IUserRepository>();
        var mailer = Substitute.For<IEmailSender>();
        var clock = Substitute.For<IClock>();

        var now = new DateTimeOffset(2025, 12, 31, 0, 0, 0, TimeSpan.Zero);
        clock.UtcNow.Returns(now);

        users.ExistsByEmailAsync(Arg.Any<EmailAddress>(), Arg.Any<CancellationToken>())
            .Returns(false);

        var sut = new RegisterUserService(users, mailer, clock);

        var result = await sut.RegisterAsync("b@example.com");

        Assert.True(result.Success);

        await users.Received(1)
            .AddAsync(Arg.Is<User>(u => u.Email.Value == "b@example.com" && u.CreatedAt == now),
                      Arg.Any<CancellationToken>());

        await mailer.Received(1)
            .SendWelcomeAsync(Arg.Is<EmailAddress>(m => m.Value == "b@example.com"),
                              Arg.Any<CancellationToken>());
    }
}
```

### NSubstituteのコツ🎯

* `Substitute.For<IFoo>()`：偽物を作る
* `Returns(...)`：返り値固定
* `Received(1)` / `DidNotReceive()`：呼ばれた回数チェック📞✨

---

## 8. 1人開発で“爆速”になる使い方🛼💨

![ddd_cs_study_072_test_stability](./picture/ddd_cs_study_072_test_stability.png)

### ✅ まずテストで「安心ライン」を作る

* 新規登録は成功する🎉
* 既存登録は弾く🚫
* メールは1回だけ送る✉️

これがあるだけで、あとから改修しても怖くないです😌🫶

### ✅ “時刻”は絶対モックする⏰

![ddd_cs_study_072_time_mock](./picture/ddd_cs_study_072_time_mock.png)

`DateTime.UtcNow` を直で使うとテストが不安定になりがち…
`IClock` は地味だけど超効きます💊✨

---

## 9. やりがち注意⚠️（ここで詰まる子多い！）

* ❌ **内部の実装までVerifyしすぎる**
  → テストが「仕様」じゃなくて「実装の監視カメラ」になる📹😇
  → リファクタで壊れやすい

* ❌ **ドメインモデルをモックする**
  → それ、DDDの旨味が減る🥲
  → 軽い本物を作ってテストした方が早いこと多い

* ✅ **モックは“境界”だけ！**
  Repository / 外部I/O / 時刻 くらいに絞ると勝ちです🏆✨

---

## 10. AIに手伝ってもらうプロンプト例🤖💗

そのままコピペOK系👇（あなた好みに変えてね）

```text
RegisterUserService のユニットテストを xUnit で作って。
依存は IUserRepository, IEmailSender, IClock。
テストは2本：
(1) 既存メールなら AlreadyRegistered を返し、AddAsync と SendWelcomeAsync は呼ばれない
(2) 新規メールなら成功し、AddAsync と SendWelcomeAsync が1回呼ばれる。CreatedAt は IClock.UtcNow を使う
モックは Moq（または NSubstitute）で。
```

AIが出したコードは、**必ず自分で「何を保証してるテストか」だけ確認**してね☺️🔍
（テストがズレてたら、守ってくれないので…！）

---

## 今日のまとめ🌸✨

* モックは「外側（DB/メール/外部/時刻）」を偽物にして、テストを速く・安定させる🧸
* Moqは `Setup/Verify`、NSubstituteは `Returns/Received` で覚える🎯
* 1人開発ほど、**モックで“安心”を買う**と、後半が爆速になる🏎️💨

---

次の章（第73章）は「設計ルールを破ったらビルドを落とす」系の話で、また違うタイプの“守り”が増えていきます🛡️✨

[1]: https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-14?utm_source=chatgpt.com "What's new in C# 14"
[2]: https://www.nuget.org/packages/moq/?utm_source=chatgpt.com "Moq 4.20.72"
[3]: https://www.nuget.org/packages/nsubstitute/?utm_source=chatgpt.com "NSubstitute 5.3.0"
