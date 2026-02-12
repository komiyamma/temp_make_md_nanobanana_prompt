# 第15章：パラメータ化（同じ形でケースを増やす）🔁

（＝「1つのテストの型」で、境界値や例外ケースをスイスイ増やす回だよ〜！😆💞）

---

### 1) 今日のゴール🏁✨

![画像を挿入予定](./picture/tdd_cs_study_015_exception_test.png)

この章が終わったら、こんな感じになれるよ💪😊

* `xUnit` の **`[Fact]` と `[Theory]` の違い**が説明できる🙂
* **`[InlineData]` でケースを増やす**のがスッとできる🧪🔁
* データが複雑になったら **`[MemberData]` / `TheoryData<>` に逃がせる**🏃‍♀️💨
* **境界値テスト**を「追加しやすい形」で作れる📏✨
* ケースが増えても **読みやすさを落とさない工夫**ができる📘💕

※この章は “最新のxUnit v3系” 前提でいくよ（`xunit.v3` など）✨
（xUnit v3の対応フレームワークやパッケージ情報は公式NuGetと公式ドキュメントに準拠）([NuGet][1])

---

## 2) まずは超ざっくり：`Fact` と `Theory` の気持ち🥺🫶

![画像を挿入予定](./picture/tdd_cs_study_015_fact_vs_theory.png)

### ✅ `[Fact]`

* **入力がない**テスト（固定の1本）
* 例：`null` のとき例外、みたいな単発

### ✅ `[Theory]`

* **入力がある**テスト（同じ形で複数ケースを流す）
* 例：`0円 / 1円 / 999円 / 上限超え`…みたいにいっぱい試したいとき

そして大事な罠⚠️😵‍💫

* `[Theory]` は **データが無いと実行されない**よ！
  （公式アナライザーでも「データ無いTheoryは走らない」って明言されてる）([xUnit.net][2])

---

## 3) ハンズオン：まずは `[InlineData]` で “境界値5連発” やってみよ🔫✨

![画像を挿入予定](./picture/tdd_cs_study_015_inline_bottles.png)

題材は「カフェ会計」の超ミニ版☕️🧾
「小計（円）に税率をかけて、**円に四捨五入**して合計（円）を返す」ってことにするね😊
（四捨五入の仕様はテストで固定するのがTDDっぽい👍）

### ✅ 3-1. 先にテストを書く（Red）🚦🔴

ポイントはこれ👇

* 1テスト1意図🍰🙅‍♀️（前章のルールを守る）
* “同じ意図” の中で、入力だけ変えるのがパラメータ化🔁

```csharp
using Xunit;

public class CafePriceTests
{
    [Theory]
    // subtotalYen, taxRate, expectedTotalYen
    [InlineData(0,    0.10, 0)]
    [InlineData(1,    0.10, 1)]     // 1.1 => 1（四捨五入）
    [InlineData(9,    0.10, 10)]    // 9.9 => 10（四捨五入）
    [InlineData(10,   0.10, 11)]    // 11.0 => 11
    [InlineData(999,  0.10, 1099)]  // 1098.9 => 1099
    public void Total_with_tax_is_rounded(int subtotalYen, double taxRate, int expectedTotalYen)
    {
        // Arrange
        var sut = new CafePriceCalculator();

        // Act
        var total = sut.TotalWithTax(subtotalYen, taxRate);

        // Assert
        Assert.Equal(expectedTotalYen, total);
    }
}
```

`InlineData` は「Theoryに inline の値を渡すための属性」って公式APIにもあるよ🧪✨([api.xunit.net][3])

---

### ✅ 3-2. 最小実装（Green）🚦🟢

いったん “雑でも通す” でOK（この章はパラメータ化が主役だからね）😊

```csharp
public class CafePriceCalculator
{
    public int TotalWithTax(int subtotalYen, double taxRate)
    {
        var raw = subtotalYen * (1.0 + taxRate);
        return (int)Math.Round(raw, MidpointRounding.AwayFromZero);
    }
}
```

> ここで「四捨五入の方式（Midpoint）」までテストで縛ると、ブレなくて安心😇🫶
> もし仕様が「切り捨て」なら、テストがそう導いてくれるよ✨

---

## 4) “InlineDataの限界” を知ろう😵‍💫➡️✨

![画像を挿入予定](./picture/tdd_cs_study_015_long_scroll.png)

`InlineData` は便利なんだけど、こうなりがち👇

* ケースが増えるほど **縦に長くて読みづらい**📜😵
* 引数が増えると **何が何だか分からない**🌀
* オブジェクトを渡したいときつらい（基本は値中心）🧸💦
* さらに、値の数が合ってないと怒られる（アナライザーで検出もされる）😇([xUnit.net][4])

だから次の逃げ道が超大事👇✨

---

## 5) ケースが育ってきたら `[MemberData]` で “データを外に出す”🏃‍♀️📦

![画像を挿入予定](./picture/tdd_cs_study_015_warehouse_memberdata.png)

### ✅ MemberDataって？

`[MemberData]` は「**public static のプロパティ/フィールド/メソッド**からデータを取ってくる」方式だよ📌✨([api.xunit.net][5])
（テスト本文がスッキリして読みやすくなるのが強い😊）

### ✅ 例：境界値セットを外に出す🧾📏

```csharp
using System.Collections.Generic;
using Xunit;

public class CafePriceTests
{
    public static IEnumerable<object[]> TotalWithTaxCases =>
        new List<object[]>
        {
            new object[] { 0,   0.10, 0 },
            new object[] { 1,   0.10, 1 },
            new object[] { 9,   0.10, 10 },
            new object[] { 10,  0.10, 11 },
            new object[] { 999, 0.10, 1099 },
        };

    [Theory]
    [MemberData(nameof(TotalWithTaxCases))]
    public void Total_with_tax_is_rounded(int subtotalYen, double taxRate, int expectedTotalYen)
    {
        var sut = new CafePriceCalculator();
        var total = sut.TotalWithTax(subtotalYen, taxRate);
        Assert.Equal(expectedTotalYen, total);
    }
}
```

💡`nameof(...)` を使うのは超おすすめ！
メンバー名ミスで死ぬ事故を減らせるよ（MemberDataは「存在するメンバーを指せ」系のルールもある）🧠✨([xUnit.net][6])

---

## 6) v3の推し：`TheoryData<>` で “型安全” にしよ🧷💖

![画像を挿入予定](./picture/tdd_cs_study_015_shape_sorter_theory.png)

`IEnumerable<object[]>` は動くけど、**型が弱くて事故りやすい**のが欠点🥺
そこで `TheoryData<>` が便利！✨（公式APIとして用意されてるよ）([api.xunit.net][7])

```csharp
using Xunit;

public class CafePriceTests
{
    public static TheoryData<int, double, int> TotalWithTaxCases => new()
    {
        { 0,   0.10, 0 },
        { 1,   0.10, 1 },
        { 9,   0.10, 10 },
        { 10,  0.10, 11 },
        { 999, 0.10, 1099 },
    };

    [Theory]
    [MemberData(nameof(TotalWithTaxCases))]
    public void Total_with_tax_is_rounded(int subtotalYen, double taxRate, int expectedTotalYen)
    {
        var sut = new CafePriceCalculator();
        var total = sut.TotalWithTax(subtotalYen, taxRate);
        Assert.Equal(expectedTotalYen, total);
    }
}
```

さらに v3 だと、MemberData の戻り値の許容が増えてたり（`TheoryDataRow<>` や async enumerable など）アナライザーにも案内があるよ📌✨([xUnit.net][8])
（今は「へぇ〜」でOK！必要になったら使う感じで😊）

---

## 7) “読みやすさが死ぬ” のを防ぐコツ🧠💡

パラメータ化って、やりすぎると逆に読みにくくなるの…😵‍💫💔
なので、ルールを持とう👇✨

### ✅ コツ1：データ列の順番は “意図の順番” にする📘

おすすめは基本これ👇

* input…, expected（期待値は最後）
  （読みながら「で、どうなるの？」が最後に来る）

### ✅ コツ2：ケースが多いなら “意味で分ける” 🧩

* 正常系セット
* 境界値セット
* 異常系セット（例外）

みたいに **Theoryを分割**すると、読んだ瞬間に理解できる😊✨

### ✅ コツ3：同じ意図の複数AssertはOK、意図が混ざったら分割🍰

* 「合計が正しい」意図なら `Assert.Equal(...)` だけに集中🎯
* 「例外型 + メッセージ」まで見るなら、それは別のTheoryに分けてもいいよ🧯

---

## 8) Test Explorerで “Theoryの表示が変” になったら📌👀

Theoryは「データが変わると表示名や安定性が変わる」ことがあるよ〜😵‍💫
xUnit公式に **Test ExplorerでのTheoryデータ表示の安定性**の解説ページがあるので、困ったらそこを見るのが早い✨([xUnit.net][9])

---

## 9) AI（Copilot/Codex）活用：この章は “ケース出し” に最強🤖💞

![画像を挿入予定](./picture/tdd_cs_study_015_ai_variations.png)

AIはこの章と相性よすぎる😆✨
おすすめプロンプトはこれ👇（コピペOK）

* 「この仕様の **境界値** を、少なくとも10個。理由も一言つけて」📏
* 「正常/異常/境界値に分類して、**TheoryData形式**で出して」🧪
* 「入力の組合せが多いから、**分割方針（Theoryを何本にするか）**を提案して」🧩
* 「このInlineData、読みづらいから **MemberDataに移して**」📦

⚠️ ただし最後にこれだけは守ってね👇

* **採用条件：テストが通る + 意図に一致** ✅😇
  （AIが作った“それっぽい”は簡単に混ざるので、テストが門番！🚪🛡️）

---

## 10) ミニ課題🎀📝（コミット単位のおすすめ付き）

### 課題A：境界値を “あと5ケース” 増やしてみよ📏✨

例（どれでもOK）👇

* `subtotalYen = -1`（無効入力にする？例外？丸める？仕様決めよ）🚫
* `taxRate = 0`（税なし）
* `taxRate = 0.08`（別税率）
* すごい大きい値（上限テスト）🗻
* `subtotalYen = 5`（0.5系の丸め確認）🎯

おすすめコミット：

1. InlineDataで5個足す ➜ テストRed確認🚦🔴
2. 実装を最小修正で通す🚦🟢
3. ケースが増えたら MemberData/ TheoryData に整理🧹✨

---

## 11) よくあるミス集（先に潰す）💣🧯

* `[Theory]` にデータ付け忘れ → **0件実行**で気づきにくい😵‍💫（公式も注意してる）([xUnit.net][2])
* `InlineData` の値の個数が引数と合ってない → アナライザーで怒られる😇([xUnit.net][4])
* ケース増やしすぎて「何を守ってるテスト？」になる → Theory分割しよ🧩
* データ生成が賢すぎて、逆に読めない → まずはベタでOK🙆‍♀️✨

---

## 12) まとめ🎁✨

パラメータ化はね、**「品質を上げる」ってより「ちゃんと試すのをラクにする」**技だよ🧪💖
ラクになると、境界値や異常系をサボらなくなる → 結果、強くなる💪🔥

次の章（テストデータの作り方🧸）にもつながるから、
この章のうちに **InlineData → MemberData/ TheoryData** の流れだけは体に入れちゃおう😆✨

---

必要なら、この第15章を “講義台本” にして👇も付けて出せるよ😊🎀

* 5〜10分ごとの進行（先生トーク）🎤
* 受講生が詰まるポイントと救済セリフ🛟
* 小テスト（選択式/穴埋め）📝

[1]: https://www.nuget.org/packages/xunit.v3?utm_source=chatgpt.com "xunit.v3 3.2.2"
[2]: https://xunit.net/xunit.analyzers/rules/xUnit1003?utm_source=chatgpt.com "xUnit1003"
[3]: https://api.xunit.net/v3/3.0.0/Xunit.InlineDataAttribute.html?utm_source=chatgpt.com "Class InlineDataAttribute"
[4]: https://xunit.net/xunit.analyzers/rules/?utm_source=chatgpt.com "Roslyn Analyzer Rules"
[5]: https://api.xunit.net/v3/3.0.1/Xunit.MemberDataAttribute.html?utm_source=chatgpt.com "Class MemberDataAttribute"
[6]: https://xunit.net/xunit.analyzers/rules/xUnit1015?utm_source=chatgpt.com "xUnit1015"
[7]: https://api.xunit.net/v3/1.1.0/Xunit.TheoryData.html?utm_source=chatgpt.com "Class TheoryData"
[8]: https://xunit.net/xunit.analyzers/rules/xUnit1042?utm_source=chatgpt.com "xUnit1042"
[9]: https://xunit.net/docs/theory-data-stability-in-vs?utm_source=chatgpt.com "Theory Data Stability in Test Explorer [2025 November 27]"
