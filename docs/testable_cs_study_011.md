# 第11章：DIの最小（コンストラクタ注入）✉️✨

（テーマ：**依存を「引数で渡せる形」にして、テストで偽物に差し替える**🎭）

---

## 1. この章でできるようになること ✅😊

* 「DIってなに？」を**ふわっと**じゃなく、**手を動かして**理解できる👐✨
* “重要ロジックの中の `new`” を減らして、**差し替え可能**にできる🔁
* テストで `Fake` を渡して、**安定した単体テスト**が書ける🧪💖
* .NETの標準DI（`Microsoft.Extensions.DependencyInjection`）を**最小だけ**使える🧰✨ ([Microsoft Learn][1])

---

## 2. DIをひとことで言うと？🧠💡

**「クラスが必要なもの（依存）を、自分で作らずに外から渡してもらう」**ことだよ〜✉️😊

* 自分で作る：`new` して固定される🧊
* 外から渡す：テストで偽物に差し替えられる🎭

.NETではDIがフレームワークの“標準装備”として用意されているよ（構成/ログ/Options と並ぶ基本機能の1つ）📦✨ ([Microsoft Learn][1])

---

## 3. 「コンストラクタ注入」が最小で最強な理由 🏆✨


![testable_cs_study_011_constructor_injection.png](./picture/testable_cs_study_011_constructor_injection.png)

コンストラクタ注入（Constructor Injection）は、DIの中でもいちばん基本で、いちばん効くやつ💪😊

### 👍 いいところ

* **依存が見える化**する👓

  * コンストラクタ引数＝「このクラスが必要なもの一覧」📋
* **渡し忘れがない**（作る時点で必須になる）🚫
* テストで**偽物（Fake/Stub）をそのまま渡せる**🎭🧪
* “I/O境界” の分離に直結する🚧✨（外の世界は差し替えたいからね）

---

## 4. まず「DIコンテナ無し」で理解しよう 🧠➡️👐

いきなりDIコンテナを触るより、まずは **「渡す」だけ**でOK！😊

### 4.1 例題：期限チェック（“今”がI/O）🕰️🚧

**やりたいこと**：締切が過ぎてたら `true` を返す
でも `DateTime.Now` を直で読むとテストが不安定になる😵‍💫

#### ❌ 悪い例：クラスの中で `DateTime.Now` 直読み

```csharp
public sealed class DeadlineService
{
    public bool IsOverdue(DateTime deadline)
    {
        return DateTime.Now > deadline; // “今”が固定できない😵
    }
}
```

**困ること**

* テスト実行した瞬間の時刻に左右される🌀
* テストが「たまに落ちる」系になりがち💥

---

## 5. IClock を作って、コンストラクタで受け取ろう ✉️✨

### 5.1 境界インターフェースを用意 🧩

```csharp
public interface IClock
{
    DateTimeOffset Now { get; }
}
```

### 5.2 本番用の実装（外の世界につながる）🌍

```csharp
public sealed class SystemClock : IClock
{
    public DateTimeOffset Now => DateTimeOffset.Now;
}
```

### 5.3 ✅ コンストラクタ注入で受け取る（これがDI最小！）🎉

```csharp
public sealed class DeadlineService
{
    private readonly IClock _clock;

    public DeadlineService(IClock clock) // ← 依存を受け取る✉️
    {
        _clock = clock;
    }

    public bool IsOverdue(DateTimeOffset deadline)
    {
        return _clock.Now > deadline; // ← “今”は境界経由🕰️🚧
    }
}
```

これで **「今」をテストで固定**できるようになったよ〜🎭✨

---

## 6. テストで偽物を渡す（Fake Clock）🎭🧪

### 6.1 FakeClock（固定のNowを返す）📌

```csharp
public sealed class FakeClock : IClock
{
    public FakeClock(DateTimeOffset now) => Now = now;
    public DateTimeOffset Now { get; }
}
```

### 6.2 単体テスト例（xUnit想定）🧪💖

```csharp
using Xunit;

public sealed class DeadlineServiceTests
{
    [Fact]
    public void 締切を過ぎていたら_true()
    {
        // Arrange
        var clock = new FakeClock(new DateTimeOffset(2026, 1, 16, 12, 0, 0, TimeSpan.FromHours(9)));
        var sut = new DeadlineService(clock);

        // Act
        var result = sut.IsOverdue(new DateTimeOffset(2026, 1, 16, 11, 59, 0, TimeSpan.FromHours(9)));

        // Assert
        Assert.True(result);
    }

    [Fact]
    public void まだ締切前なら_false()
    {
        var clock = new FakeClock(new DateTimeOffset(2026, 1, 16, 12, 0, 0, TimeSpan.FromHours(9)));
        var sut = new DeadlineService(clock);

        var result = sut.IsOverdue(new DateTimeOffset(2026, 1, 16, 12, 1, 0, TimeSpan.FromHours(9)));

        Assert.False(result);
    }
}
```

✨ポイント

* `sut`（System Under Test）に **Fake を渡すだけ**でテストが安定する🎯
* DIコンテナ不要！「渡せる形」になってるのが勝ち🏆

---

## 7. 次に：.NET標準DIコンテナで“組み立て”を楽にする 🧰✨

ここからは「本番では毎回 `new` するの面倒だよ〜😵」を解決するための道具！
.NETには `Microsoft.Extensions.DependencyInjection` が用意されてるよ📦✨ ([Microsoft Learn][1])

### 7.1 最小の登録＆解決（ConsoleでもOK）🧩

```csharp
using Microsoft.Extensions.DependencyInjection;

var services = new ServiceCollection();

// 依存の登録（IClock は SystemClock を使う）
services.AddSingleton<IClock, SystemClock>();

// 本体も登録（コンストラクタ注入される）
services.AddTransient<DeadlineService>();

using var provider = services.BuildServiceProvider();

// 取り出す（依存は自動で解決される）
var deadlineService = provider.GetRequiredService<DeadlineService>();

Console.WriteLine(deadlineService.IsOverdue(DateTimeOffset.Now.AddMinutes(-1)));
```

> “コンストラクタ引数に必要なもの”を、登録済みのサービスから自動で注入してくれるよ🤖✨ ([Microsoft Learn][1])

---

## 8. ここだけ押さえる！ライフタイム3兄弟 👪✨

DIコンテナを使うときに必ず出てくるのが **ライフタイム**（寿命）だよ〜🕯️
`AddSingleton / AddScoped / AddTransient` という登録方法があるよね🧩 ([Microsoft Learn][2])

* **Transient**：毎回新しく作る（軽いサービス向き）🐣
* **Scoped**：スコープ内で同じ（Webだと「1リクエストで同じ」）📦
* **Singleton**：アプリ全体で1個（重い共有・状態注意）👑

※Web（ASP.NET Core）ではDIが「ど真ん中機能」として使われるよ〜🌐 ([Microsoft Learn][2])

---

## 9. よくあるミス集（ここで事故る）🚨😵‍💫

### ❌ 1) “重要ロジック”の中で `new` しちゃう

* 差し替えできない＝テストがつらい💥
* **対策**：`new` は外側へ（のちの章のComposition Rootへ）🏗️✨

### ❌ 2) `IServiceProvider` を注入して中で `GetService`（サービスロケータ）

* 依存が隠れる👻（見える化の逆！）
* **対策**：必要なものをコンストラクタ引数に全部書く✉️

### ❌ 3) 依存が増えすぎ（コンストラクタ引数が8個とか）😇

* それ、たぶん責務が多すぎるサイン🚥
* **対策**：分割する／ユースケース単位にまとめる🧱

---

## 10. AI（Copilot/Codex）活用：この章で使うと強いプロンプト集 🤖💡

### ✅ 10.1 インターフェース＆Fake作成を任せる

* 「`IClock` と `SystemClock` と `FakeClock` を作って。`DateTimeOffset`で」📝
* 「この `DeadlineService` をコンストラクタ注入にリファクタして」🛠️

### ✅ 10.2 テストの骨組み（AAA）を作らせる

* 「xUnitで Arrange/Act/Assert の形で2ケース書いて」🧪

### ⚠️ 10.3 鵜呑み禁止チェック

* コンストラクタ引数が増えすぎてない？👀
* `DateTime.Now` や `new HttpClient()` が中に残ってない？🔍
* テストがI/O触ってない？（ファイル・ネット・DB）🚫

---

## 11. ミニ演習（手を動かすやつ）🏃‍♀️💨

### 演習A：`DateTime.Now` を追放しよう🕰️🚪

1. `IClock` を作る
2. `DeadlineService` をコンストラクタ注入に
3. `FakeClock` でテスト2本🧪

### 演習B：次章への布石（I/O境界の香り）🌸

* 「ログ出力」「メール送信」みたいなI/Oも
  `IEmailSender` みたいな形で“引数で渡せる”ようにしてみよう📮✨

---

## 12. まとめ（この章の合言葉）📣💖

* **DIの最小は「コンストラクタで受け取る」**✉️✨
* 受け取れる＝**テストで偽物に差し替えできる**🎭🧪
* .NETには標準DIがあって、登録＆解決もできる🧰✨ ([Microsoft Learn][1])
* そして今の最新ラインだと **.NET 10 / C# 14 / Visual Studio 2026** が揃ってるよ📦🚀 ([Microsoft][3])

---

次の章（第12章）では、この「受け取る」をさらに進めて、**“外の世界（I/O）をインターフェースで包む”**をガッツリやるよ〜🧩📮✨

[1]: https://learn.microsoft.com/en-us/dotnet/core/extensions/dependency-injection?utm_source=chatgpt.com "Dependency injection - .NET"
[2]: https://learn.microsoft.com/en-us/aspnet/core/fundamentals/dependency-injection?view=aspnetcore-10.0&utm_source=chatgpt.com "Dependency injection in ASP.NET Core"
[3]: https://dotnet.microsoft.com/en-us/platform/support/policy/dotnet-core?utm_source=chatgpt.com "NET and .NET Core official support policy"
