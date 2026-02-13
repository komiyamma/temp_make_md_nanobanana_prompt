# 第14章：時間（DateTime.Now）を境界にする 🕰️🚧✨

この章のテーマはひとことで言うと👇
**「“いま” をコードの外から渡せるようにして、テストを安定させる」**だよ〜😊💖

---

## 1) なんで “今” はテストの敵なの？😈🧪

![testable_cs_study_014_time_instability.png](./picture/testable_cs_study_014_time_instability.png)

`DateTime.Now` / `DateTime.UtcNow` を **重要ロジックの中で直読み**すると、テストがこうなる👇

* ⏱️ 実行する“瞬間”で結果が変わる（＝不安定）
* 🌙 深夜0時またぎ・月末またぎ・DST（夏時間）で事故る
* 💻 CI（自動テスト環境）だけ落ちる…みたいな“謎”が増える

つまり **時間は I/O（外の世界）** だから、境界に出してあげると強い💪✨
いまの .NET には、そのための標準の仕組みとして **`TimeProvider`** が用意されてるよ（.NET 8 で導入、`DateTimeOffset` ベースの抽象化）🧁✨ ([Microsoft Learn][1])

---

## 2) まずは “ダメな例” を見てみよう 💥😵‍💫

「期限切れチェック」って超ありがちだよね👇

```csharp
public sealed record Coupon(string Code, DateTimeOffset ExpiresAtUtc);

public sealed class CouponService
{
    public bool IsValid(Coupon coupon)
    {
        // ❌ 重要ロジックの中で “今” を直読み
        return coupon.ExpiresAtUtc > DateTimeOffset.UtcNow;
    }
}
```

これ、テストで「期限切れのはず」って固定したくても、**テスト実行時刻に依存**しちゃうの😢
で、たま〜に落ちるテスト（フレイキー）が爆誕🔥

---

## 3) 解決の考え方：時間を “境界” にする 🧃🚪✨


![testable_cs_study_014_freeze_time.png](./picture/testable_cs_study_014_freeze_time.png)

やりたいことはシンプル👇

* ✅ ロジック側は「今が何時か」を知らない
* ✅ 「今」は外から注入（差し替え可能）
* ✅ テストでは“偽物の時計”で固定できる🎭

ここから2つのやり方を紹介するね！
どっちもOKだけど、**今どきのおすすめは `TimeProvider`**（標準で、テスト用のFakeも用意されてる）だよ〜🫶 ([Microsoft Learn][2])

---

## 4) やり方A：自分で `IClock` を作る（超わかりやすい）🧩🕰️

## 4-1) インターフェースを作る

![testable_cs_study_014_iclock_blueprint.png](./picture/testable_cs_study_014_iclock_blueprint.png)

ポイントは **返す型を `DateTimeOffset` にする**こと💡
「“今” を曖昧にしない」用途に向いてるってMicrosoftも説明してるよ〜🧠✨ ([Microsoft Learn][3])

```csharp
public interface IClock
{
    DateTimeOffset UtcNow { get; }
}
```

## 4-2) 本番用の時計（SystemClock）

```csharp
public sealed class SystemClock : IClock
{
    public DateTimeOffset UtcNow => DateTimeOffset.UtcNow;
}
```

## 4-3) ロジック側は “時計を受け取る”

```csharp
public sealed record Coupon(string Code, DateTimeOffset ExpiresAtUtc);

public sealed class CouponService
{
    private readonly IClock _clock;

    public CouponService(IClock clock)
    {
        _clock = clock;
    }

    public bool IsValid(Coupon coupon)
        => coupon.ExpiresAtUtc > _clock.UtcNow;
}
```

## 4-4) テスト用の偽物時計（FakeClock）

```csharp
public sealed class FakeClock : IClock
{
    public DateTimeOffset UtcNow { get; set; }
}
```

## 4-5) テスト（固定できて気持ちいい！）🎉🧪

```csharp
using Xunit;

public class CouponServiceTests
{
    [Fact]
    public void IsValid_returns_true_when_not_expired()
    {
        var clock = new FakeClock
        {
            UtcNow = new DateTimeOffset(2026, 1, 1, 0, 0, 0, TimeSpan.Zero)
        };
        var sut = new CouponService(clock);

        var coupon = new Coupon("HELLO", clock.UtcNow.AddMinutes(10));

        Assert.True(sut.IsValid(coupon));
    }

    [Fact]
    public void IsValid_returns_false_when_expired()
    {
        var clock = new FakeClock
        {
            UtcNow = new DateTimeOffset(2026, 1, 1, 0, 0, 0, TimeSpan.Zero)
        };
        var sut = new CouponService(clock);

        var coupon = new Coupon("BYE", clock.UtcNow.AddSeconds(-1));

        Assert.False(sut.IsValid(coupon));
    }
}
```

> ✅ これでテストが “時間に揺れない” 🎯✨

---

## 5) やり方B：`TimeProvider` を使う（今どき本命🔥）🧁🕰️

## 5-1) `TimeProvider` ってなに？

* .NET 標準の「時間の抽象化」だよ
* `DateTimeOffset` で “今” を提供する仕組み✨
* **テスト可能・予測可能にするため**に用意されてるよ〜 ([Microsoft Learn][1])

本番ではふつうに `TimeProvider.System` を使える（標準で用意されてる）よ🧠✨ ([Microsoft Learn][2])

## 5-2) ロジック側（TimeProvider注入）

```csharp
public sealed record Coupon(string Code, DateTimeOffset ExpiresAtUtc);

public sealed class CouponService
{
    private readonly TimeProvider _time;

    public CouponService(TimeProvider time)
    {
        _time = time;
    }

    public bool IsValid(Coupon coupon)
        => coupon.ExpiresAtUtc > _time.GetUtcNow();
}
```

## 5-3) テストでは `FakeTimeProvider` を使う 🎭✨

![testable_cs_study_014_fake_time_controller.png](./picture/testable_cs_study_014_fake_time_controller.png)

`FakeTimeProvider` は **Microsoft公式のテスト用 TimeProvider**で、時間を進めたり固定したりできるよ〜！
`Advance` / `SetUtcNow` みたいなAPIがあるのが強い🧪⚡ ([Microsoft Learn][4])

### テストコード例（時間を固定＆進める）

```csharp
using Microsoft.Extensions.Time.Testing;
using Xunit;

public class CouponService_TimeProviderTests
{
    [Fact]
    public void IsValid_changes_when_time_advances()
    {
        var tp = new FakeTimeProvider(
            new DateTimeOffset(2026, 1, 1, 0, 0, 0, TimeSpan.Zero)
        );

        var sut = new CouponService(tp);
        var coupon = new Coupon("NEWYEAR", tp.GetUtcNow().AddSeconds(5));

        Assert.True(sut.IsValid(coupon));

        tp.Advance(TimeSpan.FromSeconds(10)); // ⏩ 時間を進める

        Assert.False(sut.IsValid(coupon));
    }
}
```

---

## 6) “Now vs UtcNow” で迷子にならないコツ 🧭🌏✨


![testable_cs_study_014_utc_strategy.png](./picture/testable_cs_study_014_utc_strategy.png)

ここ、事故りやすいからルールを決めちゃうのがおすすめ👇

## ✅ ルール（超おすすめ）

* 🧊 **内部ロジック・保存・比較は UTC**
* 🌸 画面表示やユーザー入力だけ「ローカル時間」に変換（外側で！）
* 🧾 時刻はなるべく `DateTimeOffset`（“いつ”を曖昧にしない） ([Microsoft Learn][3])

`TimeProvider` も `GetUtcNow()` で UTC の“今”をくれるよ🕰️✨ ([Microsoft Learn][2])

---

## 7) よくある落とし穴あるある ⚠️😵

## 🕳️ 落とし穴1：比較演算子が境界でズレる

![testable_cs_study_014_boundary_tightrope.png](./picture/testable_cs_study_014_boundary_tightrope.png)

* `ExpiresAtUtc > now` か `>=` か、**仕様で固定**しよ！
* 「期限ちょうどの瞬間はOK？NG？」を最初に決めるのが大事😊📝

## 🕳️ 落とし穴2：テストで `Thread.Sleep()` しちゃう

![testable_cs_study_014_sleep_sloth.png](./picture/testable_cs_study_014_sleep_sloth.png)

* 遅い🐢＆不安定😵
* Fakeで時間を進めるほうが100倍ラク💖（`FakeTimeProvider.Advance` など） ([NuGet][5])

## 🕳️ 落とし穴3：ロジックの中に “変換” が混ざる

* `ToLocalTime()` とか `TimeZoneInfo` を内側に混ぜると、テスト地獄👻
* 変換は外側で！ロジックは UTC で！

---

## 8) ミニ演習（手を動かすと一気に身につくよ〜✍️💕）

## 演習1：無料体験の判定 🎁🧪

仕様👇

* 登録時刻 `RegisteredAtUtc`
* 7日以内なら `IsTrialActive = true`
* “ちょうど7日” は **false** にする（例）

やること👇

* `DateTimeOffset.UtcNow` 直読みをやめる
* `IClock` か `TimeProvider` を注入
* テストで「6日23時間」「7日0時間」を書く

## 演習2：締切まで残り○日を計算 📅✨

仕様👇

* 期限 `DeadlineUtc`
* 残り日数を返す（マイナスなら0で丸める）

やること👇

* Fakeで時間を動かしてテスト（残りが減るのを確認）⏳

---

## 9) Copilot/Codexに頼むときのプロンプト例 🤖💬✨

そのままコピペでOK系👇

* 「このクラス内の `DateTime.Now` / `UtcNow` 直呼びをやめて、`TimeProvider` を注入する形にリファクタして。APIは `GetUtcNow()` を使ってね」
* 「`FakeTimeProvider` を使ったxUnitテストを追加して。`Advance(TimeSpan)` で期限切れになるケースも作って」
* 「“ちょうど期限の瞬間” の仕様を `>` と `>=` どっちにすべきか、メリデメ整理して提案して」
* 「UTCで内部処理して、表示はローカル変換に分ける設計に直して。変換は外側に寄せて」
* 「このメソッドのテストがフレイキーになりそうな要因を列挙して、対策コードに直して」

※ 出てきたコードが「ロジックの中にI/Oが混ざってない？」だけは毎回チェックね👀⚠️

---

## 10) まとめ 🎀✨

* 🕰️ **時間はI/O（外の世界）**だから、ロジックから切り離すとテストが安定する！
* 🧩 方法は2つ：

  * `IClock` を自作（わかりやすい）
  * `TimeProvider` を使う（標準で今どき本命） ([Microsoft Learn][1])
* 🎭 テストは Fake で時間を固定・進める！`FakeTimeProvider` が便利すぎる🧪⚡ ([NuGet][5])
* 🌍 迷ったら **内部はUTC、表示は外側で変換** が安全💖

---

## 次章ちら見せ 👀✨

次は **乱数（Random）** を境界にするよ〜🎲🚧
「抽選・シャッフル・ゲーム」みたいな“ブレる処理”をテストで安定させるワザをやろうね😊🎉

[1]: https://learn.microsoft.com/en-us/dotnet/standard/datetime/timeprovider-overview?utm_source=chatgpt.com "What is the TimeProvider class - .NET"
[2]: https://learn.microsoft.com/en-us/dotnet/api/system.timeprovider?view=net-10.0&utm_source=chatgpt.com "TimeProvider Class (System)"
[3]: https://learn.microsoft.com/en-us/dotnet/standard/datetime/choosing-between-datetime?utm_source=chatgpt.com "Compare types related to date and time - .NET"
[4]: https://learn.microsoft.com/en-us/dotnet/api/microsoft.extensions.time.testing.faketimeprovider?view=net-10.0-pp "FakeTimeProvider Class (Microsoft.Extensions.Time.Testing) | Microsoft Learn"
[5]: https://www.nuget.org/packages/Microsoft.Extensions.TimeProvider.Testing/ "
        NuGet Gallery
        \| Microsoft.Extensions.TimeProvider.Testing 10.2.0
    "
