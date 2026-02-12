# 第22章：失敗の種類を増やす（例外のテスト入門）🚫🧪

この章でやることはシンプルだよ〜😊✨
**「うまくいく時」だけじゃなくて、** **「うまくいかない時」も仕様としてテストに書ける**ようになるのがゴールです💪🧁

---

## 1) 例外テストって、なんで必要？🤔💥

![画像を挿入予定](./picture/tdd_cs_study_022_gold_master.png)

普通のテスト（正常系）だけだと…

* 間違った入力が来た時に、**どんな失敗をするのが正しいのか**が曖昧になりがち😵
* 結果として「たまたま落ちた」「別の例外で落ちた」が混ざって、**バグなのか仕様なのか分からない**…😭

だから、**失敗も仕様として固定**するよ📌✨
特に「引数が変」「状態が変」は、APIを使う側にとって超大事！

---

## 2) まず覚える“例外3兄弟”👭✨（超入門）

### ✅ ArgumentNullException（nullはダメ！）

「null が来たらダメ」をはっきり伝える例外だよ🙂
`ThrowIfNull` が便利で、**引数名もいい感じに入れてくれる**のがポイント✨ ([Microsoft Learn][1])

### ✅ ArgumentException / ArgumentOutOfRangeException（値が変！範囲外！）

* `ArgumentException`：形式がダメ（空文字、条件違反など）
* `ArgumentOutOfRangeException`：範囲がダメ（負数、上限超えなど）

`ArgumentException` は **ParamName** で「どの引数が悪いか」が表せるよ📝 ([Microsoft Learn][2])

### ✅ InvalidOperationException（状態がダメ！）

「今その操作しちゃダメ（状態的に）」のときに使う候補だよ🚦

---

## 3) xUnitで例外をテストする基本セット🧪✨

### ① `Assert.Throws<T>`：**“その型ぴったり”**を期待する

xUnitの `Throws` は **派生型ではダメで、完全一致**を期待するよ📌 ([api.xunit.net][3])

### ② `Assert.ThrowsAny<T>`：**“その型 or 派生型OK”**

「細かい型は今は気にしない（派生も許可）」ならこっち😊 ([api.xunit.net][4])

### ③ `Assert.ThrowsAsync<T>`：async版（`Func<Task>` を渡す）

非同期メソッドなら `ThrowsAsync`！
`Func<Task>` を渡して、**await する**のがコツだよ⚡ ([api.xunit.net][5])

### ④ `Record.Exception`：例外を“録画”して、あとで見る

「例外が出る/出ない」だけじゃなく、**例外の中身を見て追加検証したい**ときに便利👀 ([api.xunit.net][6])

---

## 4) ハンズオン：カフェ会計に“無効入力”を追加する☕️🧾🚫

### 今日の題材：クーポン適用メソッド🎟️✨

仕様（まずは超ミニ）👇

* `code` が **null** → `ArgumentNullException`
* `code` が **空/空白** → `ArgumentException`
* `subtotal` が **負数** → `ArgumentOutOfRangeException`
* `code` が知らない値 → `ArgumentException`（今は単純にこれでOK）

---

## 5) Red → Green → Refactor で作るよ🚦✨

### ✅ Step 1: Red（落ちるテストを書く）🔴

```csharp
using Xunit;

public class CouponServiceTests
{
    [Fact]
    public void ApplyCoupon_CodeIsNull_ThrowsArgumentNullException()
    {
        // Arrange
        string? code = null;

        // Act & Assert
        Assert.Throws<ArgumentNullException>("code", () =>
            CouponService.ApplyCoupon(code!, 100m));
    }

    [Fact]
    public void ApplyCoupon_CodeIsWhitespace_ThrowsArgumentException()
    {
        // Arrange
        var code = "   ";

        // Act & Assert
        Assert.Throws<ArgumentException>("code", () =>
            CouponService.ApplyCoupon(code, 100m));
    }

    [Fact]
    public void ApplyCoupon_SubtotalIsNegative_ThrowsArgumentOutOfRangeException()
    {
        // Arrange
        var code = "OFF10";

        // Act & Assert
        Assert.Throws<ArgumentOutOfRangeException>("subtotal", () =>
            CouponService.ApplyCoupon(code, -1m));
    }

    [Fact]
    public void ApplyCoupon_UnknownCode_ThrowsArgumentException()
    {
        // Arrange
        var code = "???";

        // Act & Assert
        var ex = Assert.Throws<ArgumentException>("code", () =>
            CouponService.ApplyCoupon(code, 100m));

        // 例外メッセージまで固定したい時だけ（今回は例として）
        Assert.Contains("unknown", ex.Message, StringComparison.OrdinalIgnoreCase);
    }
}
```

ポイント💡

* `Assert.Throws<ArgumentException>("code", ...)` みたいに **paramName まで検証**できるの、地味に強いよ🧷
  （xUnitの `Throws` は `ArgumentException` 派生なら paramName を見れる形がある） ([api.xunit.net][3])
* メッセージ検証は **壊れやすい**から、基本は「型＋paramName」くらいが安定🥹✨

---

### ✅ Step 2: Green（最小実装で通す）🟢

```csharp
public static class CouponService
{
    public static decimal ApplyCoupon(string code, decimal subtotal)
    {
        ArgumentNullException.ThrowIfNull(code); // nullチェックはこれが気持ちいい✨

        if (string.IsNullOrWhiteSpace(code))
            throw new ArgumentException("Coupon code must not be empty.", nameof(code));

        if (subtotal < 0)
            throw new ArgumentOutOfRangeException(nameof(subtotal), "Subtotal must be >= 0.");

        if (!string.Equals(code, "OFF10", StringComparison.OrdinalIgnoreCase))
            throw new ArgumentException("Unknown coupon code.", nameof(code));

        // OFF10: 10% OFF（仮）
        return subtotal * 0.9m;
    }
}
```

ここでの学び🎀

* `ThrowIfNull` は「paramName を自分で渡さないのが推奨」って話があるよ（引数名をうまく拾ってくれるため） ([Microsoft Learn][1])
* 引数チェックは **asyncの“前”に済ませるのがおすすめ**（非同期に入ってから投げると追跡がダルくなることある） ([Microsoft Learn][7])

---

### ✅ Step 3: Refactor（読みやすく整える）🧼✨

この例だと、いまの時点で無理に抽象化しなくてOK😊
ただ、増えてきたらこうするのはアリ👇

* クーポン判定を `IsKnownCoupon(code)` に分ける
* 割引計算を `ApplyOff10(subtotal)` に分ける

でも今日は **「例外も仕様」** が主役だから、やりすぎ禁止〜🍰🙅‍♀️

---

## 6) 例外テストの“よくある事故”あるある😵‍💫🧨

* ✅ **Assertの外でメソッド呼んじゃう**
  → 例外が先に飛んでテストが落ちる（`Assert.Throws` のラムダの中で呼ぶ！）
* ✅ asyncなのに `Throws` を使う / `await` しない
  → 正しく検証できない（`Assert.ThrowsAsync` ＋ `await`！） ([api.xunit.net][5])
* ✅ なんでも `ThrowsAny<Exception>` にしがち
  → 仕様がユルユルになって、バグを見逃しやすい😂（最初は型をちゃんと決めよ）

---

## 7) AIの使いどころ（この章向け）🤖💡

AIはここでめちゃ便利✨
ただし **採用はテストが主役** ね😊✅

### 使えるプロンプト例🎀

* 「このメソッドにありそうな**無効入力パターン**を、正常/異常/境界値で列挙して」
* 「無効入力ごとに、**どの例外型**が自然か候補を出して（理由つき）」
* 「このテスト、`paramName` まで検証した方がいいケースある？」

---

## 8) ミニ確認問題（3分）📝✨

Q1️⃣ `Assert.Throws<ArgumentException>` で、`ArgumentOutOfRangeException`（派生）が投げられたらどうなる？
→（ヒント：`Throws` は“完全一致”） ([api.xunit.net][3])

Q2️⃣ 「派生でもOK」にしたいときはどれ？
→（ヒント：名前に Any がある） ([api.xunit.net][4])

Q3️⃣ `ThrowIfNull` を使うとき、`paramName` を自分で渡さないのが推奨なのはなぜ？ ([Microsoft Learn][1])

---

## 9) この章の“提出物”（おすすめコミット単位）📦✨

* `test: add exception specs for ApplyCoupon (null/blank/negative/unknown)` 🧪
* `feat: implement ApplyCoupon argument validation and OFF10` 🧩
* `refactor: tidy validation messages and ordering` 🧼

---

### おまけ：今日の“最新メモ”🗞️✨

* .NET 10 は 2026/01/13 のアップデートで **10.0.2** が案内されてるよ🪟 ([GitHub][8])
* xUnit v3 の `xunit.v3` パッケージは **3.2.2** が見えてるよ🧪 ([nuget.org][9])
  （教材の中身はバージョンに強く依存しない書き方にしてあるから安心してね😊）

---

次は第23章の「テストが設計の警報器👃🚨」に入る準備ができた感じだよ〜！
もしこの章の題材を「カフェ会計②（割引・クーポン・上限）」側に寄せて、**割引ルールを増やす版**に作り替えたいなら、それ用の課題設計もすぐ出せるよ☕️🎟️✨

[1]: https://learn.microsoft.com/ja-jp/dotnet/api/system.argumentnullexception.throwifnull?view=net-10.0&utm_source=chatgpt.com "ArgumentNullException.ThrowIfNull Method (System)"
[2]: https://learn.microsoft.com/en-us/dotnet/api/system.argumentexception?view=net-10.0&utm_source=chatgpt.com "ArgumentException Class (System)"
[3]: https://api.xunit.net/v3/1.0.1/v3.1.0.1-Xunit.Assert.Throws.html "Method Throws | xUnit.net "
[4]: https://api.xunit.net/v3/3.2.2/v3.3.2.2-Xunit.Assert.ThrowsAny.html "Method ThrowsAny | xUnit.net "
[5]: https://api.xunit.net/v3/2.0.0/v3.2.0.0-Xunit.Assert.ThrowsAsync.html "Method ThrowsAsync | xUnit.net "
[6]: https://api.xunit.net/v3/2.0.3/v3.2.0.3-Xunit.Record.Exception.html?utm_source=chatgpt.com "Method Exception"
[7]: https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/exceptions/creating-and-throwing-exceptions?utm_source=chatgpt.com "Creating and Throwing Exceptions - C#"
[8]: https://github.com/dotnet/core/issues/10204?utm_source=chatgpt.com "NET January 2026 non security Updates - .NET 10.0.2, . ..."
[9]: https://www.nuget.org/packages/xunit.v3?utm_source=chatgpt.com "xunit.v3 3.2.2"
