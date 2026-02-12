# 第12章：インターフェースでI/Oを包む 🧩📮✨

ここから一気に「テストできる世界」に入っていくよ〜！😊🎉
第12章のテーマは超重要で、ひとことで言うと👇

**「外の世界（I/O）に触る部分は、インターフェース越しにする」**🚪🌍✨
そうすると、テストで “偽物” に差し替えできて、ロジックを安定して検証できるようになるよ〜！🧪💖

---

## 1) この章のゴール 🎯✨

できるようになってほしいことはこれ👇

* I/Oっぽい処理を見つけたら「インターフェースで包む」を自然に思い出せる 🧠💡
* **インターフェースは “内側（ロジック側）” に置く** のが基本だとわかる 📦✅
* 命名や粒度の “ちょうど良さ” を掴める 📝✨
* テストでは Fake/Stub で差し替えできる 🎭🧪

---

## 2) そもそも「I/Oを包む」ってどういうこと？🔌📦


![testable_cs_study_012_wrapping_io.png](./picture/testable_cs_study_012_wrapping_io.png)

たとえば、こういうの👇（全部 “外の世界” だよ〜）

* 時刻：`DateTime.Now` 🕰️
* ファイル：`File.ReadAllText` 🗂️
* ネット：HTTP呼び出し 🌐
* メール送信 ✉️
* DBアクセス 🗄️

こういう **I/Oをロジックのど真ん中で直に呼ぶ** と、テストが苦しくなるの😵‍💫💥
（遅い・落ちる・環境が必要・結果が揺れる…）

だから👇

## ✅ ロジックは「インターフェース」にだけ依存する

* 本番：インターフェースの **本物実装** を注入する 🔌
* テスト：インターフェースの **偽物実装** を注入する 🎭

この切り替えができるようになるのが、テスタブル設計の“中核”だよ💎✨

---

## 3) どこにインターフェースを書くのが正解？📍😊


![testable_cs_study_012_interface_placement.png](./picture/testable_cs_study_012_interface_placement.png)

ここ、めちゃ大事！！🚨

## ✅ 原則：インターフェースは「内側」に置く

* “内側” = ルール・ユースケース・大事なロジック 📦✨
* “外側” = I/Oの実装（ファイル、HTTP、DB、メール…）🌍🔌

つまり👇
**「ロジックが欲しい形」を内側で決めて、外側が合わせに行く** って感じ🧩✨

この考え方は、後で出てくるクリーン/ヘキサゴナルにもそのまま繋がるよ〜🌉💖

---

## 4) 最小サンプル　メール送信を包む ✉️🧩

「メール送信」って、完全にI/Oだよね🌍
なので **IEmailSender** みたいに包むよ〜！

## 4-1) インターフェースを作る

```csharp
public interface IEmailSender
{
    Task SendAsync(string to, string subject, string body, CancellationToken ct = default);
}
```

ポイント👇

* “送る” という役割が見える名前でOK 📝✨
* 余計な機能を盛らない（最初は最小で！）🧼

## 4-2) ロジック側はインターフェースだけを見る

```csharp
public sealed class WelcomeService
{
    private readonly IEmailSender _emailSender;

    public WelcomeService(IEmailSender emailSender)
        => _emailSender = emailSender;

    public Task WelcomeAsync(string email, CancellationToken ct = default)
    {
        var subject = "ようこそ！";
        var body = "登録ありがとう〜！🎉";
        return _emailSender.SendAsync(email, subject, body, ct);
    }
}
```

ここが最高に大事👇

* ロジック側に「SMTP」とか「API」とか一切出てこない🧠✨
* テストでは `_emailSender` を偽物にできる🎭🧪

---

## 5) テストでFakeを差し替える 🎭🧪✨

## 5-1) Fake実装を作る

```csharp
public sealed class FakeEmailSender : IEmailSender
{
    public List<(string To, string Subject, string Body)> Sent { get; } = new();

    public Task SendAsync(string to, string subject, string body, CancellationToken ct = default)
    {
        Sent.Add((to, subject, body));
        return Task.CompletedTask;
    }
}
```

## 5-2) xUnitでテストする

```csharp
using Xunit;

public class WelcomeServiceTests
{
    [Fact]
    public async Task WelcomeAsync_sends_welcome_mail()
    {
        var fake = new FakeEmailSender();
        var sut = new WelcomeService(fake);

        await sut.WelcomeAsync("test@example.com");

        Assert.Single(fake.Sent);
        Assert.Equal("test@example.com", fake.Sent[0].To);
        Assert.Equal("ようこそ！", fake.Sent[0].Subject);
    }
}
```

できた〜！🎉
メール環境ゼロでも、爆速で安定してテストできる⚡💖

---

## 6) 2026っぽい最新ネタ　時間は TimeProvider が便利 🕰️✨

「IClock作る」でも全然OKなんだけど、今どきは **TimeProvider** っていう公式の抽象があるよ〜！
`.NET 10 + C# 14` が現行の最新ラインで、C# 14 は .NET 10 でサポートされてるよ。([Microsoft Learn][1])

さらに、TimeProviderの概要と、テスト向けの FakeTimeProvider も公式で用意されてるのが強い💪✨([Microsoft Learn][2])

## 6-1) ロジック側は TimeProvider を受け取る

```csharp
public sealed class ExpiryChecker
{
    private readonly TimeProvider _time;

    public ExpiryChecker(TimeProvider time)
        => _time = time;

    public bool IsExpired(DateTimeOffset expiresAtUtc)
        => _time.GetUtcNow() >= expiresAtUtc;
}
```

## 6-2) テストでは FakeTimeProvider を使う

```csharp
using Microsoft.Extensions.Time.Testing;
using Xunit;

public class ExpiryCheckerTests
{
    [Fact]
    public void IsExpired_returns_true_when_time_passed()
    {
        var fakeTime = new FakeTimeProvider();
        fakeTime.SetUtcNow(new DateTimeOffset(2026, 01, 01, 0, 0, 0, TimeSpan.Zero));

        var sut = new ExpiryChecker(fakeTime);

        var expires = new DateTimeOffset(2025, 12, 31, 23, 0, 0, TimeSpan.Zero);
        Assert.True(sut.IsExpired(expires));
    }
}
```

**“今”が固定できる** って、テストでは神だよね😇🧪✨
（FakeTimeProvider は `Microsoft.Extensions.TimeProvider.Testing` パッケージで提供されるよ）([Microsoft Learn][2])

---

## 7) 命名のコツ　動詞より「役割」📝✨

命名って悩むよね〜😵‍💫 でもコツがあるよ！

## ✅ よくある良い例

* `IEmailSender` ✉️
* `IClock` or `TimeProvider` 🕰️
* `IFileSystem` / `IFileStore` 🗂️
* `IPaymentGateway` 💳

## ❌ ありがちNG例

* `IUtil` / `IHelper`（何する人？ってなる）🙅‍♀️
* `IService`（デカくなりがち）🐘💥
* `IDoEverything`（破滅の香り）🔥

---

## 8) 粒度のコツ　インターフェースは「細め」が正義🧼✨

インターフェースが大きいと、Fake作るのが地獄になるよ〜😇💦

## ✅ 小さくするコツ

* そのクラスが **本当に必要な操作だけ** を入れる
* “汎用” より “用途特化” を優先する
* 迷ったら **まず1〜3メソッド** にする🧩✨

---

## 9) 便利な既製品　IFileSystemなら System.IO.Abstractions も人気 🗂️✨

ファイルI/Oは自作で包んでもいいけど、**System.IO.Abstractions** みたいに「File/Directory APIを注入可能にした」定番ライブラリもあるよ〜！([GitHub][3])

（第16章でファイルI/Oをやる時に、採用するか検討すると気持ちいい👍✨）

---

## 10) AIの使いどころ　この章は相性よすぎ 🤖💖

Copilot/Codexに頼むとラクになるところ👇

## 使えるお願い例 📝✨

* 「このクラスのI/O部分をインターフェースに抽出して」
* 「このインターフェースのFake実装を作って」
* 「AAA形式のxUnitテストを3つ提案して」
* 「命名を “役割ベース” に直して候補を出して」

## 鵜呑み禁止ポイント⚠️😆

* インターフェースが **大きくなりすぎてない？** 🐘
* ロジックにI/Oが **混ざり直してない？** 🔥
* 命名が `IService` 祭りになってない？🎪

---

## 11) ミニ演習　I/Oを包んでテストしよう 🧪🎓✨

## お題：次のコードを “包んでテスト可能” にしてみてね

```csharp
public sealed class PasswordResetService
{
    public bool CanReset(DateTimeOffset expiresAtUtc)
        => DateTimeOffset.UtcNow <= expiresAtUtc;
}
```

## ゴール例 🎯

* `DateTimeOffset.UtcNow` をやめる
* `TimeProvider` を受け取る（または `IClock` を作る）
* `FakeTimeProvider` で期限切れテストを書く 🧪✨

（第14章の先取りにもなるよ〜！🕰️💖）

---

## 12) まとめ　この章の合言葉 📦➡️🌍✨

* **外の世界はインターフェース越し** 🚪🧩
* **インターフェースは内側に置く** 📦✅
* **小さく作って、Fakeで差し替える** 🎭🧪
* 時刻は **TimeProvider + FakeTimeProvider** が強い🕰️💪([Microsoft Learn][2])

---

## 次章チラ見せ 👀✨

次は「Fake / Stub / Mock の使い分け」だよ〜！🎭🧪
この章で作ったインターフェースたちが、そこで超活躍するから楽しみにしててね😊💖

[1]: https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-14?utm_source=chatgpt.com "What's new in C# 14"
[2]: https://learn.microsoft.com/en-us/dotnet/standard/datetime/timeprovider-overview?utm_source=chatgpt.com "What is the TimeProvider class - .NET"
[3]: https://github.com/TestableIO/System.IO.Abstractions?utm_source=chatgpt.com "TestableIO/System.IO.Abstractions"
