# 第19章：仮実装（ベタでもいいから先に通す）🩹

この章はね、**「とにかく最短でGreenにする」**ためのズル技…じゃなくて😂、TDDの正規テク「仮実装（Fake it）」を身につける回だよ〜🧪💕

---

## 1) この章のゴール🎯✨

![画像を挿入予定](./picture/tdd_cs_study_019_isolation.png)

読み終わったら、これができるようになるよ👇😊

* ✅ **Red→Greenを“最短距離”で到達**できる（迷子にならない🧭）
* ✅ 「仮実装していい瞬間／ダメな瞬間」が分かる🙆‍♀️🙅‍♀️
* ✅ **仮実装を“永住させない”**で、次のテストで追い出して一般化できる🏃‍♀️💨
* ✅ AI（Copilot/Codexなど）を使っても、**主導権をテスト側に置ける**🤖✅

---

## 2) 仮実装ってなに？（超ざっくり）🩹

**仮実装（Fake it）＝「今だけ通すための“ベタ実装”でGreenにして、あとで育てる」**だよ😊

たとえば…

* 仕様：合計金額を返す
* まず：いつでも 0 を返す（ベタ）
* テスト増やす：0じゃダメになる
* 次：条件分岐でしのぐ（まだベタ）
* さらに増やす：ベタが通用しなくなる
* 最後：ちゃんと一般化した実装にする✨

TDDには「Greenにする」ための代表的な手があって、仮実装はその1つだよ〜🧪
（他に「三角測量」「明白な実装」もあるやつ！） ([stanislaw.github.io][1])

---

## 3) なんで仮実装が効くの？💡😳

### ✅ いいところ①：頭が止まっても前に進める🚶‍♀️✨

「正しい実装がまだ分からない…」って時、**考え込みすぎて固まる**のが一番つらい😵‍💫
仮実装は、**“一旦通して次へ行く”**ことで流れを切らない🧪⚡️

### ✅ いいところ②：設計を後回しにできる（でも放置はしない）🧹

いきなり美しい設計にしなくてOK🙆‍♀️
先に「この仕様がほしい」をテストで固定して、あとから整えるのがTDDの気持ちよさだよ〜🛡️✨

---

## 4) 仮実装を使っていいタイミング🙆‍♀️ / ダメなタイミング🙅‍♀️

### 🙆‍♀️ 使っていい（むしろ使うと強い）💪

* 🤔 実装がまだ見えない（アルゴリズムが固まってない）
* 🧩 仕様の粒度がまだ小さい（最初の1〜2テスト）
* 😵 迷ってRedのまま止まりそう
* 🧪 「まずは仕様を確定したい」気持ちが強い

### 🙅‍♀️ 使っちゃダメ（事故りやすい）💥

* 🚨 もう十分テストが増えてるのに、ベタ実装を温存しようとしてる
* 🧟‍♀️ 仮実装が“本実装”になって、誰も直さないまま残ってる
* 🧯 例外やI/Oの失敗など、現実の挙動を誤魔化すと危険な場所

---

## 5) 実演：カフェ会計①☕️🧾 を「仮実装」でGreen最短ルート！

ここでは「第18章のミニ演習（カフェ会計①）」の続きとして、**合計金額（税込）**を返す処理を育てるよ〜😊✨

### 今回の小仕様（まずはこれだけ）📌

* カートが空なら合計は 0 円
* 1品だけなら「価格×1.1（10%税）」を四捨五入して整数円
* 複数品なら合計してから税をかける（この章の後半で一般化）

> .NET 10 の最新パッチは 10.0.2（2026/01/13）で、C# 14.0 対応も明記されてるよ ([Microsoft][2])
> xUnit v3 も NuGet 上で 3.2.2 が公開されてる ([NuGet][3])

---

### ✅ Step0：テスト側の準備（ざっくりイメージ）🧪

xUnit v3 で進めるときの基本は「xunit.v3」「runner（VSTest連携）」みたいな構成になるよ〜 ([NuGet][4])
（細かい作業は第7〜10章でやった前提でOK👌）

---

### ✅ Step1：最初のテスト（空なら0円）→ 仮実装でGreen🩹✅

#### 🔴 まずRed（失敗するテストを書く）

```csharp
using Xunit;

public class CafeCheckoutTests
{
    [Fact]
    public void TotalYen_WhenCartIsEmpty_Returns0()
    {
        var sut = new CafeCheckout();
        var cart = new Cart();

        var total = sut.TotalYen(cart);

        Assert.Equal(0, total);
    }
}
```

#### 🟢 つぎにGreen（最短で通す：常に0円返す）

```csharp
public class CafeCheckout
{
    public int TotalYen(Cart cart)
    {
        return 0; // 仮実装🩹：まず通す！
    }
}

public class Cart
{
}
```

💡ポイント：ここで「合計の計算ロジック」を作り込まない！
**Greenは“合格最低点”でOK**だよ〜😂✅

---

### ✅ Step2：2つ目のテスト（1000円→1100円）→ 仮実装でしのぐ🩹✅

#### 🔴 テストを追加（0固定じゃ落ちる）

```csharp
[Fact]
public void TotalYen_WhenSingleItem1000Yen_Returns1100()
{
    var sut = new CafeCheckout();
    var cart = new Cart();
    cart.AddItem(priceYen: 1000);

    var total = sut.TotalYen(cart);

    Assert.Equal(1100, total);
}
```

テストが増えたので Cart に最低限だけ足す👇

```csharp
using System.Collections.Generic;

public class Cart
{
    private readonly List<int> _prices = new();

    public void AddItem(int priceYen) => _prices.Add(priceYen);

    public bool IsEmpty => _prices.Count == 0;

    public IReadOnlyList<int> Prices => _prices;
}
```

#### 🟢 実装は…まだ“ベタ”でいい！（条件分岐でしのぐ）🩹

```csharp
public class CafeCheckout
{
    public int TotalYen(Cart cart)
    {
        if (cart.IsEmpty) return 0;

        return 1100; // 仮実装🩹：このテストに合わせて一旦通す
    }
}
```

😇 ここ、罪悪感いらないよ！
**目的は「次のテストを追加できる状態」を作ること**だからね🧪✨

---

### ✅ Step3：3つ目のテスト（2000円も入れたら？）→ もうベタが限界→一般化✨

#### 🔴 テスト追加（ベタ1100が破綻するようにする）📐

```csharp
[Fact]
public void TotalYen_WhenSingleItem2000Yen_Returns2200()
{
    var sut = new CafeCheckout();
    var cart = new Cart();
    cart.AddItem(priceYen: 2000);

    var total = sut.TotalYen(cart);

    Assert.Equal(2200, total);
}
```

これで「1100固定」は死ぬ☠️
だから、ここでやっと一般化に進むよ〜✨

#### 🟢 一般化（合計して税）✅

```csharp
using System;
using System.Linq;

public class CafeCheckout
{
    private const decimal TaxRate = 0.10m;

    public int TotalYen(Cart cart)
    {
        if (cart.IsEmpty) return 0;

        var subtotal = cart.Prices.Sum(p => (decimal)p);
        var taxed = subtotal * (1m + TaxRate);

        return (int)Math.Round(taxed, MidpointRounding.AwayFromZero);
    }
}
```

✅ ここで全テストGreenになったら勝ち🎉✨

---

## 6) 「仮実装を永住させない」ための3ルール🏡🚫

### ルール①：仮実装は“次のテストで殺す”前提🔪🧪

* 仮実装を書いたら、**次に追加するテストは「その仮実装が通らない」やつ**にする！

### ルール②：仮実装のコミットは小さく（寿命短く）⏱️

* 「仮実装コミット → 追い出しコミット」くらいのテンポが理想😊

### ルール③：分岐で延命しすぎたら黄色信号🚥

* if がテストケース分だけ増えてきたら
  **「一般化まだ？」**って自分に聞いてね😂

---

## 7) AIの使いどころ（この章はここが気持ちいい🤖💕）

### ✅ AIに頼ってOKなやつ

* 🧠 次に追加するテスト案（境界値とか）
* 🧹 一般化の候補（重複消し、命名、抽出）
* 🔍 失敗ログの読み解き補助

### 🙅‍♀️ AIに任せすぎ注意なやつ

* 「最終実装を一発で完成させて」系
  → TDDの学びが消えちゃう😇💦

#### コピペ用プロンプト（第19章版）📋✨

* 「今の実装を“仮実装のまま放置”しないために、次に追加すべきテストを3つ提案して。ベタ実装が通らないケースにして」
* 「この仕様に対して、三角測量に移るなら“2つ目の例”は何が良い？」

---

## 8) よくある事故と対処法💥🧯

### 😵 事故①：仮実装が残ってしまった

* ✅ 対処：**“殺すテスト”を追加**する（価格を変える・複数にする）

### 😵 事故②：Greenで作り込みしちゃう

* ✅ 対処：Greenの目的を思い出す
  「次のテストに進むため」だよ〜🚶‍♀️✨

### 😵 事故③：条件分岐の迷路になった

* ✅ 対処：**テストケース増やして一般化**へ
  次章の「三角測量」に繋がるよ📐✨ ([stanislaw.github.io][1])

---

## 9) この章のミニ課題（コミット単位）🧩🎁

### 🎯課題A：複数品を追加して、一般化を完成させよう

* テスト：1000円 + 2000円 → 3300円（税10%）
* 最初はベタでもOK、でも最後は一般化で✨

### 🎯課題B：四捨五入の挙動をテストで固定しよう

* 例：1円 → 1.1円 → 四捨五入で 1円？2円？
  どっちにしたいかを**テストで決める**🧪✨

---

## 10) 次章へのつながり📐✨

第20章は「三角測量」！
今日やった“仮実装で通す→次のテストで殺す”が、三角測量の感覚にそのまま繋がるよ〜😊🧠✨

---

### 参考（最新情報ソース）📚

* .NET 10.0 の最新パッチや、対応する Visual Studio / C# バージョン ([Microsoft][2])
* Visual Studio 2026 のリリースノート（2026/01/13 の更新も含む）([Microsoft Learn][5])
* xUnit v3 のリリースと NuGet の最新バージョン ([xUnit.net][6])
* TDDの「Fake it / Triangulation」系の説明 ([stanislaw.github.io][1])

---

次、あなたの手元の「カフェ会計①」のコードに合わせて、**“あなたの今の状態から”第19章の演習をそのまま差し込める形**（ファイル名・クラス名・命名ルール込み）に整えた版も作れるよ〜☕️🧪💕

[1]: https://stanislaw.github.io/2016-01-25-notes-on-test-driven-development-by-example-by-kent-beck.html?utm_source=chatgpt.com "Notes on \"Test-Driven Development by Example\" by Kent ..."
[2]: https://dotnet.microsoft.com/en-US/download/dotnet/10.0 "Download .NET 10.0 (Linux, macOS, and Windows) | .NET"
[3]: https://www.nuget.org/packages/xunit.v3?utm_source=chatgpt.com "xunit.v3 3.2.2"
[4]: https://www.nuget.org/packages/xunit.runner.visualstudio "
        NuGet Gallery
        \| xunit.runner.visualstudio 3.1.5
    "
[5]: https://learn.microsoft.com/en-us/visualstudio/releases/2026/release-notes "Visual Studio 2026 Release Notes | Microsoft Learn"
[6]: https://xunit.net/releases/v3/3.0.0 "Core Framework v3 3.0.0 [2025 July 13] | xUnit.net "
