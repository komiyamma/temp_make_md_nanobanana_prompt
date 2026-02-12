# 第20章：三角測量（2ケース目で一般化）📐

## この章のゴール🎯

![画像を挿入予定](./picture/tdd_cs_study_020_deterministic.png)

* 「最初はベタでもOK」→ **2つ目の例で“ルール化（一般化）”する**流れが体に入る🧠✨
* **“一般化が早すぎて複雑化”**を避けられるようになる🚧💦
* 次に足すべきテストケースを、**自分で選べる**ようになる🎲✅

---

## 三角測量ってなに？🤔📐

![画像を挿入予定](./picture/tdd_cs_study_020_triangulation_concept.png)

ざっくり言うとこう👇

* **1個目のテスト**：とりあえず通す（仮実装・ベタ実装でもOK）🩹
* **2個目のテスト**：別の例を追加して、**「あ、共通のルールが必要だ」**って状況を作る✨
* そこで初めて、**ルールとして一般化**する📐✅

ポイントは、**“一般化は2例目が来てから”**ってところだよ〜！😄✨

---

## なぜ三角測量が効くの？🧠🚦

![画像を挿入予定](./picture/tdd_cs_study_020_footsteps_path.png)

TDDをやってると、最初のうちって「この先どうなるか分からん…😵」ってなることあるよね。

そこでいきなり完璧な設計をしようとすると…

* まだ要らない抽象化が増える😇
* クラスが増えて迷子になる🧳💦
* 仕様変更に弱くなる（悲しい）🥲

三角測量はそれを防いで、**“必要になった瞬間にだけ、ちょうどよく一般化する”**ための技だよ📐✨

---

## ハンズオン：ミニ題材「税を足す」☕️🧾（三角測量の最短コース！）

### 今回の超ミニ仕様📋✨

* `AddTax(subtotal)` は **10%の税**を足した金額を返す
* 端数とか丸めは今回は触れない（まずは三角測量に集中！）😌🫶

---

## Step 1：まずは1本目のテストを書く（Red🔴）

![画像を挿入予定](./picture/tdd_cs_study_020_one_dot.png)

テストは「例」を1つだけ置くよ〜👇

```csharp
using Xunit;

public class PriceCalculatorTests
{
    [Fact]
    public void AddTax_100yen_returns_110yen()
    {
        // Arrange
        var calc = new PriceCalculator();

        // Act
        var total = calc.AddTax(100);

        // Assert
        Assert.Equal(110, total);
    }
}
```

まだ `PriceCalculator` が無いから当然落ちる！🔴✨
この「落ちた！」が、TDDのスタート合図だよ〜🚦😆

---

## Step 2：最短で通す（Green🟢）＝仮実装OK🩹

ここ、わざと**ベタ**にいくよ👇（わざと！）

```csharp
public class PriceCalculator
{
    public int AddTax(int subtotal)
    {
        return 110; // 仮実装（100円のケースだけ通す）
    }
}
```

✅ テストが通ったら勝ち！🟢🎉
ここで「ちゃんと式を書かなきゃ！」って焦らないでOKだよ🙆‍♀️✨
（次の一手で“必要になったら”一般化するからね📐）

---

## Step 3：2本目のテストを追加する（Red🔴）＝“一般化が必要な状況”を作る📐

![画像を挿入予定](./picture/tdd_cs_study_020_two_dots.png)

次は **別の例** を置くよ〜👇

```csharp
[Fact]
public void AddTax_200yen_returns_220yen()
{
    // Arrange
    var calc = new PriceCalculator();

    // Act
    var total = calc.AddTax(200);

    // Assert
    Assert.Equal(220, total);
}
```

今の実装は `110` 固定だから、当然落ちる！🔴😆
はい、ここでやっとこう思う👇

> 「あ、`110` 固定じゃダメだ。共通ルール（一般化）が必要だ…！」📐✨

これが三角測量の「測量できた瞬間」だよ〜🥳

---

## Step 4：一般化する（Green🟢➡️📐）

![画像を挿入予定](./picture/tdd_cs_study_020_ruler_connect.png)

2例そろったので、やっと式にする！✨

```csharp
public class PriceCalculator
{
    public int AddTax(int subtotal)
    {
        return subtotal + (subtotal / 10); // 10%（今回は割り切れる値だけで進めてる）
    }
}
```

✅ 2本とも通った！🟢🎉
この瞬間が最高に気持ちいいやつ〜〜😆✨

---

## Step 5：Refactor（整理）🧹✨（今やるのは“読みやすさ”中心）

ここは小さく整えるだけでOK🙆‍♀️
たとえば「10%」が分かるように名前を付けるとか👇

```csharp
public class PriceCalculator
{
    private const int TaxRatePercent = 10;

    public int AddTax(int subtotal)
    {
        return subtotal + (subtotal * TaxRatePercent / 100);
    }
}
```

✅ テストがあるから、安心して置き換えできる🛡️✨
（Refactorのたびにテスト回すの忘れないでね〜🔁🧪）

---

## 三角測量の「テストケース選び」コツ集🎯✨

### コツ1：2本目は“同じ実装で通らない例”を選ぶ📌

![画像を挿入予定](./picture/tdd_cs_study_020_smash_fixed.png)

* 今回なら `100→110` の次に `200→220` を置いたから、固定値が死ぬ💀✨
* もし `100→110` の次に `110→121` とかだと、偶然通る実装が残ることもある😇💦

### コツ2：迷ったら「真逆」を置く🧲

* 境界の反対側（小さい/大きい、0/正、内側/外側）を置くと、ルールが見えやすい👀✨

### コツ3：2例でもルールが確定しないなら、3例目を足す🧩

* 「AかBか分からん…」ってなったら、**決め手になる3例目**を置くのが正解🙆‍♀️✨

---

## よくあるミスあるある😵‍💫💦（ここ超大事）

* **1本目から一般化しすぎる**（まだ要件が見えてないのに抽象化して迷子）🧳
* **2本目も似すぎてて一般化が起きない**（固定値でも通っちゃう）😇
* **“テスト2本まとめて”書いてから実装する**（TDDのリズムが崩れやすい）🥲
* **Refactorで一気に変えすぎる**（小さく置き換え→テスト、が安全）🛡️🔁

---

## AIの使いどころ（この章のおすすめ）🤖✨

AIは「次の一手」を出すのが得意だよ〜😆🫶
ただし採用条件は **テストが決める**✅🧪

### 使い方1：次に足すべきテストケースを出させる🎲

* 「この仕様で“2本目”に最適な例を3つ提案して。固定値実装を殺せるやつで」

### 使い方2：2例で曖昧なときの“決め手の3例目”を出させる🧩

* 「この2例だとルールが複数ありえる。分岐を潰す3例目を提案して」

### 使い方3：リファクタ案を“小さく”出させる🧹

* 「このコードを読みやすくする最小のリファクタ案を3つ。変更は小さく」

---

## ミニ演習（今日の宿題）🧪💪🎀

### 演習A：送料計算📦✨

![画像を挿入予定](./picture/tdd_cs_study_020_shipping_scale.png)

仕様：

* `ShippingFee(totalPrice)`
* `totalPrice < 3000` なら送料 `500`
* `totalPrice >= 3000` なら送料 `0`

やり方（これが三角測量の型！）👇

1. まず `1000 -> 500` をテスト（仮実装でもOK）🩹
2. 次に `3000 -> 0` をテスト（境界を刺す！🎯）
3. 一般化（ifでOK、これは“仕様のルール”だから正義🙆‍♀️）✨

### 演習B：ポイント計算🎁✨（余裕ある人向け）

仕様：

* `Points(amount)` は `amount / 100`（整数）ポイント
* 例：`100 -> 1`, `250 -> 2`

1例目で仮実装→2例目で一般化、やってみてね📐🧪

---

## セルフチェック✅✨（これ全部Yesなら勝ち！）

* [ ] 1例目はベタ実装でもOKだと分かる🩹
* [ ] 2例目で「一般化が必要」になる感覚がある📐
* [ ] 2例目は“固定値を殺す”ように選べる💀
* [ ] 2例で曖昧なら3例目を足す判断ができる🧩
* [ ] Refactorは小さく、テストをこまめに回せる🔁
* [ ] AIは「案出し」に使い、採用はテストで決める✅🧪

---

## さいごに：今日のまとめ💡🎉

三角測量は「設計を育てる」ための超いい技だよ〜📐✨
**“必要になるまで一般化しない”**って、実はめちゃ強い！😆🫶

---

## 最新メモ（2026-01-18時点）🗞️✨

* .NET 10 の最新SDKは **10.0.2（2026-01-13更新）**だよ。 ([Microsoft][1])
* **C# 14 は .NET 10 でサポート**されてるよ。 ([Microsoft Learn][2])
* xUnit v3 の最新安定版は **3.2.2**（NuGet/公式リリースノート）。 ([xUnit.net][3])
* Visual Studio 2026 は **.NET 10 / C# 14 をサポート**する前提のリリース情報が出てるよ。 ([Microsoft Learn][4])

---

次の章（第21章：明白な実装🌼）に行く前に、もしよければこの章の演習A（送料計算📦）を“テスト→仮実装→2本目→一般化”の流れで一緒に作って、コミット単位まで整えるところまでやろう〜！😆🧪✨

[1]: https://dotnet.microsoft.com/en-US/download/dotnet/10.0?utm_source=chatgpt.com "Download .NET 10.0 (Linux, macOS, and Windows) | .NET"
[2]: https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-14?utm_source=chatgpt.com "What's new in C# 14"
[3]: https://xunit.net/releases/?utm_source=chatgpt.com "Release Notes"
[4]: https://learn.microsoft.com/en-us/visualstudio/releases/2026/release-notes?utm_source=chatgpt.com "Visual Studio 2026 Release Notes"
