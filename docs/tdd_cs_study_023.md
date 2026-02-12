# 第23章：“におい”を嗅ぐ（テストが設計の警報器）👃🚨

> **この章の結論**：**テストがつらい＝あなたの根性不足じゃない**です😂
> それはだいたい **「設計をちょい整えるタイミングだよ〜」** っていう警報です🚨✨（しかも超ありがたい）

---

## 今日の“最新メモ”🗓️✨（本日時点のリサーチ反映）

* Microsoft公式の **ユニットテスト Best Practices** は 2025/03/22 更新で、AAA（Arrange/Act/Assert）などの基本が整理されています🧱🧪 ([Microsoft Learn][1])
* Visual Studio の **Test Explorer** 公式ガイドは 2025/11/25 更新で、AAAの説明も含めて手順がまとまっています🪟🔍 ([Microsoft Learn][2])
* xUnit は **v3 の Getting Started / What’s new** が 2025/08 更新で公開されています🧪✨ ([xunit.net][3])
* xUnit には **公式アナライザー規則一覧**があり、Theory/InlineData などのありがちな事故を静かに防いでくれます🧯 ([xunit.net][4])
* テストの “におい（Test Smells）” は **xUnit Test Patterns（Meszaros）** にまとまった代表例があります👃 ([xunitpatterns.com][5])

---

## 1) この章でできるようになること🎯✨

![画像を挿入予定](./picture/tdd_cs_study_023_safety_net.png)

### ゴール✅

* テストを書いていて **「つらっ😇」** ってなったときに、**どの種類の“におい”か** を言語化できる
* “におい”から **「設計のどこが苦しいのか」** を推理できる
* **最小のリファクタ**で、テストも実装もラクにできる（大改造しない🧸）

---

## 2) 「におい」って何？🤔👃

![画像を挿入予定](./picture/tdd_cs_study_023_sniffing.png)

**におい＝表面の症状**です👃

* 例：Arrangeが長すぎる、モックだらけ、テストがたまに落ちる、遅い、何が壊れたか分からない…
* それはたいてい **設計のどこかに原因**があります（責務が混ざってる、依存が漏れてる、I/Oが中心に入り込んでる…）📦🧩

コードやテストの“smell”は「たぶん奥に原因があるよ」というサイン、って考え方がよく使われます🐾 ([scg.unibe.ch][6])

---

## 3) 代表的な “テストのにおい” 図鑑📚👃✨

ここは「まず覚えると一生使える」やつだけに絞るね😊
（テストのにおい一覧の考え方は xUnit Test Patterns にまとまっています👃） ([xunitpatterns.com][5])

---

### A. Arrange がデカすぎる（準備が重い）🏋️‍♀️📦

![画像を挿入予定](./picture/tdd_cs_study_023_giant_arrange.png)

**症状**

* Arrange が 20行、Act が 1行、Assert が 1行😇
* オブジェクト生成が連鎖して「何をテストしてるの？」ってなる

**だいたいの原因（設計側）**

* 1クラスに責務が集まりすぎ（神クラス👑）
* “必要な情報”が遠くにあって、セットアップが大工事

**効く処方箋（最小）**

* テストデータを **小さく作る**（値を減らす🧸）
* “そのテストに必要なもの”だけを引数で渡す（後の章でDIに進化するやつ✨）

---

### B. テストが壊れやすい（実装をちょっと変えたら全滅）🧨

![画像を挿入予定](./picture/tdd_cs_study_023_house_of_cards.png)

**症状**

* リファクタしただけなのにテストが大量死…😭
* “振る舞い”ではなく “内部手順” を検証している

**原因**

* 実装詳細に依存してる（privateな動きとか、呼び出し順とか）

**処方箋**

* Assert を **結果（出力・状態・副作用）** に寄せる
* AAAで「何をした」「何を期待」かを分ける（Microsoftも推奨の定番）🧱 ([Microsoft Learn][1])

---

### C. テストがたまに落ちる（フレーク）🎲🚫

![画像を挿入予定](./picture/tdd_cs_study_023_slot_machine.png)

**症状**

* ローカルだと通るのに、たまに落ちる😵‍💫
* 実行順で挙動が変わる

**原因**

* 時間・乱数・並列・共有状態（static等）
* テストが独立してない

**処方箋**

* “変わるもの”を固定する（時間/乱数）
* 共有状態を消す（または初期化を徹底）

---

### D. どの Assert が落ちたか分からない（Assertion Roulette）🎰😇

![画像を挿入予定](./picture/tdd_cs_study_023_roulette_wheel.png)

**症状**

* Assert がいっぱい並んでて、落ちた理由が分かりにくい
* 失敗ログが読みづらい

**原因**

* 1テストに意図が混ざってる（前章の「1テスト1意図」違反🍰🙅‍♀️）

**処方箋**

* テストを分割
* Assert を意味ある単位にする（期待を言葉にする）

---

### E. “謎ゲスト”がいる（Mystery Guest）🕵️‍♀️

**症状**

* どこからデータが来てるか分からない（ファイル/DB/共有Fixture）
* 失敗時に原因が追いにくい

**原因**

* 外部資源に寄りかかっている
* Arrange がブラックボックス

**処方箋**

* テスト内に「必要なデータ」を小さく置く
* データ生成をシンプルに（賢くしすぎない🧸）

---

## 4) “におい” → “原因” を当てる早見表🗺️👃

テストで感じること → 設計の疑い、の対応表だよ😊

* **Arrangeが長い** → 責務が混ざってる / 依存が多い / 入力が作りづらい
* **モックが多い** → クラスがやりすぎ / 境界が曖昧 / 依存が中心に入り込んでる
* **ちょいリファクタでテスト爆発** → 実装詳細をテストしてる
* **たまに落ちる** → 時間/乱数/共有状態/順序依存
* **遅い** → I/O混入（DB/ネット/ファイル）や巨大データ
* **private を直接テストしたくなる** → 公開APIが“意図”を表してない or 責務の切り方が変

---

## 5) ハンズオン：つらいテストを“警報器”として使う🚨🧪✨

ここでは **わざと「つらい」テスト**を作って、
「におい」→「原因」→「最小リファクタ」までやります😊🎮

### お題：カフェ会計（割引つき）☕️🎟️🧾

仕様（超ざっくり）：

* 小計に対して割引（%）を適用
* 合計は 0円未満にならない
* 割引率が不正（負数・100超）は例外

---

### Step 1：つらい版（においが出る形）😇

![画像を挿入予定](./picture/tdd_cs_study_023_tangled_class.png)

「計算」なのに、クラスが色々抱えてる想定👇

```csharp
public sealed class CheckoutService
{
    private readonly ILogger _logger;
    private readonly ICampaignRepository _campaigns;
    private readonly IReceiptPrinter _printer;

    public CheckoutService(ILogger logger, ICampaignRepository campaigns, IReceiptPrinter printer)
    {
        _logger = logger;
        _campaigns = campaigns;
        _printer = printer;
    }

    public decimal Checkout(decimal subtotal, string campaignCode)
    {
        var campaign = _campaigns.FindByCode(campaignCode);  // 外部依存
        if (campaign.DiscountRate < 0 || campaign.DiscountRate > 100)
            throw new ArgumentOutOfRangeException(nameof(campaign.DiscountRate));

        var discounted = subtotal * (100 - campaign.DiscountRate) / 100m;
        if (discounted < 0) discounted = 0;

        _logger.Info("checkout");              // 副作用
        _printer.PrintReceipt(discounted);     // 副作用

        return discounted;
    }
}
```

**この時点での“におい”**👃🚨

* ただの割引計算なのに、**外部依存 + 副作用** が混ざってる
* テストで「計算」だけ見たいのに、周辺が邪魔する

---

### Step 2：テストがつらい（症状を観察）🔍

```csharp
public class CheckoutServiceTests
{
    [Fact]
    public void Checkout_10PercentOff_ReturnsDiscountedTotal()
    {
        // Arrange（長い）
        var logger = new FakeLogger();
        var campaigns = new FakeCampaignRepository(new Campaign("OFF10", 10));
        var printer = new FakeReceiptPrinter();
        var sut = new CheckoutService(logger, campaigns, printer);

        // Act
        var total = sut.Checkout(1000m, "OFF10");

        // Assert（本当は計算だけ見たいのに…）
        Assert.Equal(900m, total);
        Assert.True(logger.Called);
        Assert.Equal(900m, printer.LastPrintedTotal);
    }
}
```

ここで言語化しよう😊✨

* **におい**：Arrangeが重い／副作用確認が混ざる／テストの意図が散る
* **警報**：「計算」と「周辺処理（ログ・印刷・リポジトリ）」の責務が混ざってるかも🚨

---

### Step 3：最小リファクタ（“計算”を外に出す）🧩✨

![画像を挿入予定](./picture/tdd_cs_study_023_clean_box.png)

狙いはこれ👇

* **計算＝純粋ロジック**にして、テストを軽くする🧪
* 周辺（取得・ログ・印刷）は後で別枠テストにする

```csharp
public static class DiscountCalculator
{
    public static decimal ApplyRate(decimal subtotal, int discountRate)
    {
        if (discountRate < 0 || discountRate > 100)
            throw new ArgumentOutOfRangeException(nameof(discountRate));

        var discounted = subtotal * (100 - discountRate) / 100m;
        return discounted < 0 ? 0 : discounted;
    }
}
```

テストはこうなる👇（急に平和🕊️✨）

```csharp
public class DiscountCalculatorTests
{
    [Theory]
    [InlineData(1000, 10, 900)]
    [InlineData(200,  0,  200)]
    [InlineData(500,  100, 0)]
    public void ApplyRate_ReturnsExpected(decimal subtotal, int rate, decimal expected)
    {
        var total = DiscountCalculator.ApplyRate(subtotal, rate);
        Assert.Equal(expected, total);
    }

    [Theory]
    [InlineData(-1)]
    [InlineData(101)]
    public void ApplyRate_InvalidRate_Throws(int rate)
    {
        Assert.Throws<ArgumentOutOfRangeException>(() =>
            DiscountCalculator.ApplyRate(1000m, rate));
    }
}
```

xUnit の `[Theory]` / `[InlineData]` の基本は v3 Getting Started にも載っています🧪 ([xunit.net][3])
（アナライザー規則もあるので、ミスが減ります🧯） ([xunit.net][4])

---

### Step 4：このリファクタで何が起きた？🌈

* 「つらさ」の原因だった **責務の混在**がほぐれた🧩
* テストが AAA っぽく読みやすくなった（AAAは公式でも基本として説明されています）🧱 ([Microsoft Learn][1])
* しかも、仕様（割引率の範囲）もテストで固定できた🧪✨

> ポイント：この章では **“大改造”じゃなく「計算を外に出す」だけ**。これがちょうどいい最小手術💉😊

---

## 6) AIの使いどころ（この章の勝ちパターン）🤖✅✨

AIは“設計の匂い当て”が得意です👃
でも **採用判断はあなた**（テストが通って、意図に合うか）✅

### コピペ用プロンプト例📝

* 「このテストがつらい理由（におい）を3つに分類して。原因になりそうな設計の問題もセットで」
* 「“最小の変更”でテストが軽くなるリファクタ案を3つ。各案のリスクも」
* 「この仕様から、境界値・異常系のテストケースを列挙して」

---

## 7) よくある失敗あるある😇💥（回避！）

* **においがしたからって、いきなり抽象化しすぎる**（インターフェース増殖🌱🌱🌱）
  → この章は「最小の分離」まででOK😊
* **テストを“実装の写し”にしちゃう**
  → 振る舞い（結果）を見よう🧪
* **共通化しすぎてテストが読めなくなる**
  → “読み物”が最優先📘✨（AAAの意図もそこ） ([Microsoft Learn][1])

---

## 8) 章末チェックリスト✅👃🚨

あなたのテストで、当てはまったら“警報”：

* [ ] Arrange が長すぎて何をテストしてるか曖昧
* [ ] モック/スタブが多すぎて、意図がぼやける
* [ ] たまに落ちる（時間/乱数/順序/共有状態）
* [ ] リファクタしただけでテストが大量死
* [ ] Assertが多すぎて、失敗理由が一瞬で分からない
* [ ] private を直接テストしたくなる衝動がある

→ 2個以上なら、**設計をちょい整えると幸福度が上がる**可能性大😊✨

---

## 9) 今日のミニ宿題🎒🧪

1. 自分のテストで「つらい」やつを1本選ぶ👀
2. この章のチェックリストで **“におい”を3つ言語化**する👃📝
3. **最小リファクタを1つだけ**やる（例：計算を外に出す、入力を引数で渡せる形にする）🧩
4. テストが「短く・読みやすく」なったかを確認✅✨

---

次の第24章は、この章で嗅ぎ当てた“警報”を **安全運転でリファクタする手順**に落とし込む回だよ🛡️🧹✨

[1]: https://learn.microsoft.com/en-us/dotnet/core/testing/unit-testing-best-practices?utm_source=chatgpt.com "Best practices for writing unit tests - .NET"
[2]: https://learn.microsoft.com/en-us/visualstudio/test/unit-test-basics?view=visualstudio&utm_source=chatgpt.com "Unit test basics with Test Explorer - Visual Studio (Windows)"
[3]: https://xunit.net/docs/getting-started/netcore/cmdline?utm_source=chatgpt.com "Getting Started with xUnit.net v3 [2025 August 13]"
[4]: https://xunit.net/xunit.analyzers/rules/?utm_source=chatgpt.com "Roslyn Analyzer Rules"
[5]: https://xunitpatterns.com/TestSmells.html?utm_source=chatgpt.com "Test Smells"
[6]: https://scg.unibe.ch/assets/download/lectures/sma/SMA-08-Code-and-test-smells-Palomba.pdf?utm_source=chatgpt.com "Code and Test Smells"
