# 第16章：テストデータの作り方（小さく・分かりやすく）🧸

（テーマ：Arrange をスッキリさせる 💅🧪）

---

## この章のゴール🎯💖

![画像を挿入予定](./picture/tdd_cs_study_016_cluttered_desk.png)

![画像を挿入予定](./picture/tdd_cs_study_016_parameterized_test.png)

* **Arrange（準備）が長すぎるテスト**を、読みやすく整えられる✨
* 「テスト用データはこう作る！」の**基本パターン**を持てる🧠
* “共通化しすぎて意図が消える事故”を避けられる🚫🌀

ちなみに今どきは xUnit v3 系が普通に使われていて、リリースも継続してます🧪✨（例：`xunit.v3` の 3.x）([xUnit.net][1])
（.NET も .NET 10 LTS が進んでる時期だね🪟✨）([Microsoft][2])

---

## まず結論：良いテストデータの条件🌟

![画像を挿入予定](./picture/tdd_cs_study_016_good_data_crystal.png)

テストデータは「リアルっぽさ」より、**読みやすさ**が大事だよ😊💕

### 良い感じの条件✅

1. **小さい**：必要な項目だけ入れる✂️
2. **分かりやすい**：値に意味がある（“なぜこの値？”が伝わる）📝
3. **テストが依存する値は明示**：隠さない🙈
4. **毎回同じ結果**：ランダムは基本NG（使うなら固定）🎲🚫

---

## ありがちな「つらいArrange」例😵‍💫

![画像を挿入予定](./picture/tdd_cs_study_016_stage_crew_block.png)

「何をテストしてるのか」より「データ作る作業」が目立っちゃうやつ…💦

```csharp
using Xunit;

public class PriceCalculatorTests
{
    [Fact]
    public void ApplyCoupon_PremiumUser_DiscountIsCapped()
    {
        var user = new User(
            id: Guid.Parse("11111111-1111-1111-1111-111111111111"),
            name: "Aki",
            email: "aki@example.com",
            isPremium: true,
            birthday: new DateOnly(2004, 4, 1),
            address: new Address("JP", "Tokyo", "Shibuya", "1-2-3")
        );

        var cart = new Cart(new[]
        {
            new CartLine(new Item("Latte", 580m), quantity: 2),
            new CartLine(new Item("Cookie", 280m), quantity: 1),
        });

        var coupon = new Coupon(code: "SAVE20", percent: 20, maxDiscountYen: 300);

        var calc = new PriceCalculator();

        var total = calc.Total(user, cart, coupon);

        Assert.Equal(1420m, total);
    }
}
```

これ、**テストの主役が「割引上限」なのに**、データ準備が主役になってるよね🥲💔

---

## ステップ1：まずは「ローカル関数で最小ヘルパー化」🧩✨

![画像を挿入予定](./picture/tdd_cs_study_016_helper_box.png)

いきなり大げさな仕組みにしない！まずこれが一番強い💪💕

```csharp
using Xunit;

public class PriceCalculatorTests
{
    [Fact]
    public void ApplyCoupon_PremiumUser_DiscountIsCapped()
    {
        var user = PremiumUser();
        var cart = SimpleCart();
        var coupon = PercentCoupon(code: "SAVE20", percent: 20, maxDiscountYen: 300);

        var calc = new PriceCalculator();

        var total = calc.Total(user, cart, coupon);

        Assert.Equal(1420m, total);
    }

    private static User PremiumUser() =>
        new(
            id: Guid.Parse("11111111-1111-1111-1111-111111111111"),
            name: "Aki",
            email: "aki@example.com",
            isPremium: true,
            birthday: new DateOnly(2004, 4, 1),
            address: new Address("JP", "Tokyo", "Shibuya", "1-2-3")
        );

    private static Cart SimpleCart() =>
        new(new[]
        {
            new CartLine(new Item("Latte", 580m), 2),
            new CartLine(new Item("Cookie", 280m), 1),
        });

    private static Coupon PercentCoupon(string code, int percent, int maxDiscountYen) =>
        new(code, percent, maxDiscountYen);
}
```

### この段階での嬉しさ💖

* テスト本文が **「何をしたいテストか」** だけになってくる😊✨
* しかも、共通化が **テストクラス内だけ** だから、壊れにくい🛡️

---

## ステップ2：同じ形が増えてきたら「テストデータビルダー」🧸🧱

![画像を挿入予定](./picture/tdd_cs_study_016_lego_builder.png)

ここで登場！この章の主役💃✨
**Test Data Builder** は「妥当なデフォルト」を用意して、必要な所だけ上書きできる作り方だよ🎀

> 注意：ビルダーで値を省略したとき、その値にテストが依存しだすと地獄になりがち😇
> “指定してない値は信用しない”くらいが安全だよ！([colinjack.blogspot.com][3])

### 例：UserBuilder（最小）🧸

```csharp
public sealed class UserBuilder
{
    private Guid _id = Guid.NewGuid();
    private string _name = "Test User";
    private string _email = "test@example.com";
    private bool _isPremium = false;

    public static UserBuilder Default() => new();

    public UserBuilder Premium()
    {
        _isPremium = true;
        return this;
    }

    public UserBuilder WithEmail(string email)
    {
        _email = email;
        return this;
    }

    public UserBuilder WithName(string name)
    {
        _name = name;
        return this;
    }

    public User Build() => new(_id, _name, _email, _isPremium);
}
```

### テストがこうなる😍

```csharp
using Xunit;

public class PriceCalculatorTests
{
    [Fact]
    public void ApplyCoupon_PremiumUser_DiscountIsCapped()
    {
        var user = UserBuilder.Default().Premium().Build();
        var cart = CartBuilder.Default()
            .Add("Latte", 580m, 2)
            .Add("Cookie", 280m, 1)
            .Build();
        var coupon = CouponBuilder.Default()
            .Percent(20)
            .WithMaxDiscountYen(300)
            .WithCode("SAVE20")
            .Build();

        var calc = new PriceCalculator();

        var total = calc.Total(user, cart, coupon);

        Assert.Equal(1420m, total);
    }
}
```

**読みやすさ、爆上がり**だよね🥹✨
Arrange が「仕様の説明」っぽくなるのが最高💕

---

## 「共通化しすぎて意図が消える」事故を防ぐ🧯🚨

![画像を挿入予定](./picture/tdd_cs_study_016_iceberg_dependency.png)

ビルダーは便利だけど、やりすぎると逆に読めなくなる😇

### よくある事故😵

* `TestDataFactory.CreateDefault()` が何でも作って、**中身が見えない**
* `Build()` のデフォルト値にテストが依存して、**変更で大量死**💀
* 便利メソッドが増えすぎて、**どれ使えばいいか迷子**🗺️💦

### 安全ルール（これ守ると強い）💪✨

* **そのテストが依存する値は、必ず明示**（`.Premium()` とか `.WithMaxDiscountYen(300)` とか）
* ビルダーのメソッド名は「意味」が伝わるように（`WithX` / `Premium` みたいに）
* 置き場所は基本 **Tests プロジェクト内**、しかも **ドメイン単位で小さく**

---

## ランダムデータ、使っていい？🎲👀

基本は **固定値でOK**！
でも「大量のダミーデータがほしい」時は、生成ライブラリを使うのもアリだよ😊
たとえば Bogus は .NET 向けのフェイクデータ生成で有名だね✨([GitHub][4])

**使うなら絶対これ：結果を固定する（Seed固定）**🔒
（“たまに落ちるテスト”＝フレークは最悪だからね😵‍💫）

---

## さらにラクしたい人へ：AutoFixture（ただし使いすぎ注意）🧰✨

AutoFixture は「Arrange を減らす」目的のライブラリだよ🧪
“テストで重要じゃない部分のオブジェクト生成”には便利！([GitHub][5])

でも、**テストの意図が読み取りにくくなる**こともあるから、まずは Builder / 小ヘルパーが基本でOK🙆‍♀️✨

---

## AIの使いどころ🤖💖（この章のおすすめ）

AIは「ひな形作り」と「削る」がめっちゃ相性いいよ✨

### 使えるプロンプト例（コピペOK）🪄

* 「このテストの Arrange が長いです。**最小の Test Data Builder** に整理して。**テストが依存する値は明示**して、隠しデフォルトに依存しない形で」
* 「Builder のメソッド名を、**意図が誤解されない命名**にして（3案）」
* 「共通化しすぎを避けたい。**最小構成**に削って」

xUnit のデータ属性まわりはルール違反すると検出されることもあるから、AI案を採用する時もテスト＆ルールで守るのが安心だよ🛡️✨([xUnit.net][6])

---

## ミニ演習（手を動かすやつ）✍️🧪✨

### お題🎀

いま持ってるテスト（またはサンプル）で、Arrange が長いものを1つ選んで…

1. **ローカル関数**で整理（ステップ1）🧩
2. 同じ形が2〜3個出てきたら **Builder** に進化（ステップ2）🧸
3. 最後に「このテストが依存する値」を見て、**隠してる値がないか**チェック🔍

### 完了チェック✅

* テスト本文が **3〜8行くらい**に収まってる✨
* Arrange が「何の条件なのか」読める💕
* Builder のメソッド名が “仕様の言葉” になってる📝

---

## 理解チェック（サクッと）🧠🍭

1. テストデータで一番優先するのは？
   → **読みやすさ（意図が伝わること）**💖

2. Builder のデフォルト値にテストが依存しだすと何が起きる？
   → **変更に弱くなって大量に壊れる**💥（地味に一番つらい）([colinjack.blogspot.com][3])

3. まずやるべき整理は？
   → **ローカル関数（小ヘルパー化）**が最強🧩✨

---

次は、この章で作った「データ作成の型」を使って、**テストが毎回同じ結果になる工夫（決定性）**とかに繋げると気持ちよく進められるよ〜🎲🚫✨

[1]: https://xunit.net/releases/?utm_source=chatgpt.com "Release Notes"
[2]: https://dotnet.microsoft.com/ja-jp/platform/support/policy?utm_source=chatgpt.com "公式の .NET サポート ポリシー | .NET"
[3]: https://colinjack.blogspot.com/2008/08/test-data-builder-and-object-mother.html?utm_source=chatgpt.com "Test Data Builder and Object Mother"
[4]: https://github.com/bchavez/Bogus?utm_source=chatgpt.com "bchavez/Bogus: :card_index: A simple fake data generator ..."
[5]: https://github.com/AutoFixture/AutoFixture?utm_source=chatgpt.com "AutoFixture is an open source library ..."
[6]: https://xunit.net/xunit.analyzers/rules/?utm_source=chatgpt.com "Roslyn Analyzer Rules"
