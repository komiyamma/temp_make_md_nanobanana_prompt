# 第13章：Fake / Stub / Mock をゆるく使い分け 🎭🧪

この章は「I/O境界をインターフェースで包めた！」の次の一歩だよ〜😊✨
**“外の世界”をテスト用の偽物に差し替えて**、テストをサクサク書けるようになるのがゴール！

---

## 13.0 この章でできるようになること ✅💖

* Fake / Stub / Mock のざっくり違いがわかる👀✨
* 「今このテストはどれが必要？」が迷いにくくなる🧭
* C#で **手書き** と **ライブラリ（Moqなど）** の両方で使えるようになる🛠️
* “モック地獄”に落ちないコツがわかる🕳️🚫

---

## 13.1 まず大前提：「テストダブル」ってなに？🎭

![testable_cs_study_013_test_doubles.png](./picture/testable_cs_study_013_test_doubles.png)

テストのとき、本物の依存（DB・ファイル・HTTP・時間…）をそのまま使うと…

* 遅い🐢
* 不安定（ネット落ちる・時刻変わる）😵
* 環境がないと動かない💥

だから、**依存を “偽物（テストダブル）” に置き換える**んだよ〜🎭✨
そして、その偽物にも種類があるのが今回のテーマ！

---

## 13.2 Fake / Stub / Mock の違い（超ざっくり）🍰

![testable_cs_study_013_stub_fake_mock_trio.png](./picture/testable_cs_study_013_stub_fake_mock_trio.png)

ここ、まずはこの3つだけ覚えればOKだよ😊✨

### ✅ Stub（スタブ）📌：返す値を固定する子

* 目的：**テストを成立させるために、必要な値を返す**
* 例：`IClock.Now` がいつも `2026-01-01` を返す🕰️

👉 「**結果（戻り値）をコントロールしたい**」とき！

---

### ✅ Fake（フェイク）🧸：それっぽく動く簡易実装

* 目的：**軽量な“代用品”としてちゃんと動く**
* 例：DBの代わりに **メモリ上のList** に保存するRepository🗃️

👉 「**状態を持って、それっぽく動いてほしい**」とき！

---

### ✅ Mock（モック）👀：呼ばれたかどうかを検証する子

* 目的：**「呼び出された？」を確認する**
* 例：`IEmailSender.Send()` が **1回呼ばれた**ことを確認📮

👉 「**やった/やってない（相互作用）を確認したい**」とき！

---

## 13.3 迷ったらこれ！3秒で選ぶミニルール ⚡🧭

1. **値が欲しいだけ？** → Stub📌
2. **状態を保存したい？** → Fake🧸
3. **呼び出し確認したい？** → Mock👀

そして初心者は基本これでOK👇
**FakeかStub中心で進めて、必要なところだけMock** 😊💖

---

## 13.4 C#での作り方：まずは“手書き”が最強 👑✍️

ライブラリを使う前に、まずは手書きでいこう！
手書きは「何が起きてるか」が透明で、理解が一気に進むよ😊✨

---

## 13.5 ミニ題材：会員登録したらウェルカムメールを送る📮🎉

登場する境界（I/O）をインターフェースにしておくよ！

* ユーザー保存（本当はDB）🗄️
* メール送信（本当は外部）🌐
* 現在時刻（テストの敵）🕰️

---

### 13.5.1 まずは本体コード（UseCase）📦

```csharp
public record User(string Email, DateTimeOffset RegisteredAt);

public interface IUserRepository
{
    Task AddAsync(User user);
    Task<User?> FindByEmailAsync(string email);
}

public interface IEmailSender
{
    Task SendWelcomeAsync(string email);
}

public interface IClock
{
    DateTimeOffset Now { get; }
}

public sealed class RegisterUserUseCase
{
    private readonly IUserRepository _users;
    private readonly IEmailSender _email;
    private readonly IClock _clock;

    public RegisterUserUseCase(IUserRepository users, IEmailSender email, IClock clock)
    {
        _users = users;
        _email = email;
        _clock = clock;
    }

    public async Task RegisterAsync(string email)
    {
        // 例：すでに存在したら何もしない（簡略）
        var existing = await _users.FindByEmailAsync(email);
        if (existing is not null) return;

        var user = new User(email, _clock.Now);
        await _users.AddAsync(user);
        await _email.SendWelcomeAsync(email);
    }
}
```

ここでのポイントは1つだけ😊
**UseCaseの中に I/O の直呼びが無い**（全部インターフェース越し）✨

---

## 13.6 Stub：時刻を固定してテストを安定させる🕰️📌

![testable_cs_study_013_stub_clock_nail.png](./picture/testable_cs_study_013_stub_clock_nail.png)

```csharp
public sealed class StubClock : IClock
{
    public DateTimeOffset Now { get; }

    public StubClock(DateTimeOffset now) => Now = now;
}
```

これで「今日っていつ？」問題が消えるよ〜😊✨

---

## 13.7 Fake：インメモリRepositoryで“それっぽく動かす”🧸🗃️

![testable_cs_study_013_fake_repo_basket.png](./picture/testable_cs_study_013_fake_repo_basket.png)

```csharp
public sealed class FakeUserRepository : IUserRepository
{
    private readonly List<User> _store = new();

    public Task AddAsync(User user)
    {
        _store.Add(user);
        return Task.CompletedTask;
    }

    public Task<User?> FindByEmailAsync(string email)
    {
        var user = _store.FirstOrDefault(x => x.Email == email);
        return Task.FromResult(user);
    }
}
```

Fakeは **DBを使わずに「保存された事実」を確認できる**のが強い💪✨

---

## 13.8 Mock：メールが送られたことを検証する👀📮

![testable_cs_study_013_mock_detective.png](./picture/testable_cs_study_013_mock_detective.png)

### A) まずは“手書きMock”でやってみる（初心者に超おすすめ）✍️💖

```csharp
public sealed class MockEmailSender : IEmailSender
{
    public int CallCount { get; private set; }
    public List<string> SentTo { get; } = new();

    public Task SendWelcomeAsync(string email)
    {
        CallCount++;
        SentTo.Add(email);
        return Task.CompletedTask;
    }
}
```

「呼ばれた？」が **変数で見える**から安心😊✨

---

## 13.9 まとめテスト（xUnit例）🧪🎉

```csharp
using Xunit;

public sealed class RegisterUserUseCaseTests
{
    [Fact]
    public async Task 新規登録したら_保存して_メールを送る()
    {
        // Arrange
        var repo = new FakeUserRepository();                 // Fake🧸
        var email = new MockEmailSender();                   // Mock👀（手書き）
        var clock = new StubClock(new DateTimeOffset(2026, 1, 1, 0, 0, 0, TimeSpan.Zero)); // Stub📌

        var sut = new RegisterUserUseCase(repo, email, clock);

        // Act
        await sut.RegisterAsync("a@example.com");

        // Assert（保存された？）
        var saved = await repo.FindByEmailAsync("a@example.com");
        Assert.NotNull(saved);
        Assert.Equal("a@example.com", saved!.Email);
        Assert.Equal(clock.Now, saved.RegisteredAt);

        // Assert（メール送った？）
        Assert.Equal(1, email.CallCount);
        Assert.Contains("a@example.com", email.SentTo);
    }

    [Fact]
    public async Task 既に登録済みなら_メールを送らない()
    {
        // Arrange
        var repo = new FakeUserRepository();
        await repo.AddAsync(new User("a@example.com", DateTimeOffset.MinValue));

        var email = new MockEmailSender();
        var clock = new StubClock(DateTimeOffset.UtcNow);

        var sut = new RegisterUserUseCase(repo, email, clock);

        // Act
        await sut.RegisterAsync("a@example.com");

        // Assert
        Assert.Equal(0, email.CallCount);
    }
}
```

🎉 これで「I/O境界を偽物に差し替えてテストする」が一通りできた！

---

## 13.10 ライブラリでMockする（“必要になったら”でOK）🧰✨

手書きで慣れたら、**モックライブラリ**を使うと「呼ばれたか検証」がサクッと書けるよ😊

C#でよく使われる代表はこのへん👇（2026年時点でも定番）

* **Moq**（NuGetで `4.20.72` が案内されてるよ） ([NuGet Gallery][1])
* **NSubstitute**（NuGetで `5.3.0` が案内されてるよ） ([NuGet Gallery][2])
* **FakeItEasy**（NuGetで `9.0.0` が案内されてるよ） ([NuGet Gallery][3])

（※どれを選ぶかはチーム方針でOK！まずは1つで十分😊）

---

### 例：Moqで「1回呼ばれた」を検証 👀（雰囲気だけ）

```csharp
using Moq;
using Xunit;

public sealed class MoqExampleTests
{
    [Fact]
    public async Task メール送信が1回呼ばれる()
    {
        var repo = new FakeUserRepository();
        var email = new Mock<IEmailSender>();
        var clock = new StubClock(new DateTimeOffset(2026, 1, 1, 0, 0, 0, TimeSpan.Zero));

        var sut = new RegisterUserUseCase(repo, email.Object, clock);

        await sut.RegisterAsync("a@example.com");

        email.Verify(x => x.SendWelcomeAsync("a@example.com"), Times.Once);
    }
}
```

---

## 13.11 よくある落とし穴（ここ超大事）⚠️🫠

![testable_cs_study_013_mock_hell_strings.png](./picture/testable_cs_study_013_mock_hell_strings.png)

### ❌ なんでもMockにする（モック地獄）🕳️

* 「実装の細部」を検証し始めると、リファクタでテストが壊れがち💥
  ✅ 対策：**まずFake/Stubで“結果”を見る**、必要なときだけMock👀

### ❌ Fakeが賢すぎる（もう本物じゃん…）🤖

* Fakeにロジック盛りすぎると、テストが信用できなくなる😵
  ✅ 対策：Fakeは **雑でOK**。「最低限動く」で止める🧸✨

### ❌ 「何をテストしてるの？」が分からなくなる🌫️

✅ 対策：Assertは基本この2つで整理するとスッキリ！

* **状態（State）**：保存された？戻り値は？
* **相互作用（Interaction）**：呼ばれた？回数は？

---

## 13.12 AI（Copilot/Codex）に頼むときのコツ 🤖💡

AIにお願いするなら、こう言うと強いよ😊✨

* 「このインターフェースの **Fake** を“メモリで保存”する形で作って」🧸
* 「この依存は **Stub** で固定値返すだけにしたい。最小実装を作って」📌
* 「この依存は **Mock** にして“呼ばれた回数”を検証したい。xUnitで例を」👀🧪

⚠️チェックするポイント（AIの出力はここを見る！）

* UseCaseの中に `DateTime.Now` / `File.*` / `HttpClient` 直呼びが混ざってない？🚫
* Fakeが賢すぎない？🧸
* Mockで「内部実装」を縛ってない？（呼び順までガチガチ等）😵

---

## 13.13 やってみよう（演習）🎮✨

### 演習1：Stub練習📌

`IClock` をStubにして、**期限切れチェック**を安定テストしてみよ🕰️

* 期限 `2026-01-10` より前→OK、後→NG みたいなやつ！

### 演習2：Fake練習🧸

`IUserRepository` のFakeに `RemoveAsync` を追加して、
「退会したら見つからなくなる」をテスト🗑️✨

### 演習3：Mock練習👀

「登録済みならメール送らない」を
**メール送信が0回**で検証してみよ📮🚫

---

## 13.14 この章のまとめ 🎀✨

* **Stub**：値固定📌
* **Fake**：軽量な代用品🧸
* **Mock**：呼ばれたか検証👀
* 初心者は **Fake/Stub中心** がいちばん気持ちよく進むよ😊💖
* Mockは便利だけど、使いすぎるとテストが壊れやすくなるので「必要なときだけ」✨

---

次の章（第14章）では、いよいよ **“時間（DateTime.Now）”を境界にする**よ〜🕰️🚧
（ちなみに今どきの.NETは `TimeProvider` が公式に用意されてて、テスト用の `FakeTimeProvider` もあるよ〜っていう小ネタだけ置いとくね😉✨） ([Microsoft Learn][4])

[1]: https://www.nuget.org/packages/moq/?utm_source=chatgpt.com "Moq 4.20.72"
[2]: https://www.nuget.org/packages/nsubstitute/?utm_source=chatgpt.com "NSubstitute 5.3.0"
[3]: https://www.nuget.org/packages/fakeiteasy/?utm_source=chatgpt.com "FakeItEasy 9.0.0"
[4]: https://learn.microsoft.com/en-us/dotnet/standard/datetime/timeprovider-overview?utm_source=chatgpt.com "What is the TimeProvider class - .NET"
