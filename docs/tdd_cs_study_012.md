# 第12章：Assertの基本（何を確認すべき？）✅

## 0) この章のゴール🎯✨

この章が終わると、テストで「何を」「どれくらい強く」確認すべきかが分かって、Assertがスッと選べるようになります😊👍
（Assertが弱いと“通るだけテスト”になるし、強すぎると“壊れやすいテスト”になるので、そのバランス感覚を作る章だよ〜🧠✨）

---

## 1) Assertってなに？（超ざっくり）👀✅

![画像を挿入予定](./picture/tdd_cs_study_012_naming.png)

Assertは、テストの中で **「期待（仕様）と現実（実行結果）を比べて、違ったら落とす」** ところです💥
つまり Assert が“仕様の本体”になりやすい！📘✨

💡コツ：
**「そのテストで本当に守りたいこと」＝Assertにする**
逆に言うと、守りたいことが曖昧だとAssertもフワッとします😇

---

## 2) Assert選びの大原則（弱いAssert → 強いAssertへ）🏋️‍♀️✨

### ✅ 原則A：できるだけ “意味が伝わるAssert” を使う

* 🙅‍♀️ Assert.True(a == b)（意味が読み取りづらい）
* 🙆‍♀️ Assert.Equal(b, a)（「等しい」を意図として宣言できる） ([api.xunit.net][1])

### ✅ 原則B：チェックは「必要十分」にする（見た目まで縛らない）

* **仕様として重要なことだけ**を縛る
* どうでもいい詳細までAssertすると、リファクタでテストが邪魔になります😵‍💫

---

## 3) “何を確認すべき？”の4カテゴリ📦✅（ここ覚えたら勝ち✨）

### ① 値（戻り値・計算結果）🔢✅

いちばん王道！

* Assert.Equal（同じ） ([api.xunit.net][1])
* Assert.NotEqual（違う） ([api.xunit.net][1])
* Assert.InRange（範囲内） ([api.xunit.net][1])

💡小数や日時は「完全一致」にしないのがコツ👇

* doubleは **許容誤差（tolerance）** か **桁（precision）** で比較できるよ🧮✨ ([api.xunit.net][1])
* DateTimeは **TimeSpanの精度** を指定して比較できるよ⏱️✨ ([api.xunit.net][1])

---

### ② 例外（異常系）💥🚫

「エラーになること」も立派な仕様！

* Assert.Throws（特定の例外が出る） ([api.xunit.net][1])
* Assert.ThrowsAny（派生型でもOK） ([api.xunit.net][1])
* async版（ThrowsAsync / ThrowsAnyAsync）もあるよ🌙✨ ([api.xunit.net][1])

さらに、**引数名（paramName）まで縛れる** overload もあるのが地味に強い💪 ([api.xunit.net][1])

---

### ③ コレクション（配列・List）📚✅

* Assert.Empty / NotEmpty（空かどうか）
* Assert.Single（1件だけ）
* Assert.Contains（含む） ([api.xunit.net][1])
* Assert.All（全部が条件を満たす） ([api.xunit.net][1])
* Assert.Collection（順番・各要素を“意図つき”で検査） ([api.xunit.net][1])

💡「順番が仕様じゃない」なら、順番まで縛るAssertは避けよ〜🙈

---

### ④ 状態変化（オブジェクトの中身が変わる）🔄✅

例：注文を確定したら Status が Confirmed になる、みたいなやつ😊

* 実行前→実行後のプロパティを Assert で確認する✨

---

## 4) ミニ実装で体に入れよ〜☕️🧾（Assert全部盛り練習）

### 題材：カフェ会計ミニ（合計・入力チェック・検索）☕️✨

#### ✅ 仕様（この章のためのミニ仕様だよ）

1. 合計 = 単価 × 個数
2. 個数が0以下なら ArgumentOutOfRangeException
3. 商品検索は「部分一致」で候補リストを返す（順番は保証しない）

---

### 4-1) 値のAssert（Equal / InRange）🔢✅

```csharp
using Xunit;

public sealed class CafeMathTests
{
    [Fact]
    public void CalcTotal_単価120円が2個なら_240円()
    {
        // Arrange
        var unitPrice = 120;
        var qty = 2;

        // Act
        var total = CafeMath.CalcTotal(unitPrice, qty);

        // Assert
        Assert.Equal(240, total);
    }

    [Fact]
    public void CalcTax_小数が絡むなら_誤差つきで確認する()
    {
        // 例：税 = 0.1（10%）として、誤差許容でチェック（doubleの例）
        var tax = CafeMath.CalcTax(999, 0.1);

        Assert.Equal(99.9, tax, tolerance: 0.0001);
    }
}

public static class CafeMath
{
    public static int CalcTotal(int unitPrice, int qty) => unitPrice * qty;

    public static double CalcTax(int basePrice, double rate) => basePrice * rate;
}
```

doubleの Assert.Equal は「許容誤差」指定ができるよ、って話ね🧠✨ ([api.xunit.net][1])

---

### 4-2) 例外のAssert（Throws / paramName）💥✅

```csharp
using Xunit;

public sealed class CafeMathExceptionTests
{
    [Fact]
    public void CalcTotal_個数が0以下なら_例外()
    {
        // paramName まで縛ると「どの引数がダメか」も仕様になるよ✨
        Assert.Throws<ArgumentOutOfRangeException>("qty", () =>
        {
            CafeMath2.CalcTotal(120, 0);
        });
    }
}

public static class CafeMath2
{
    public static int CalcTotal(int unitPrice, int qty)
    {
        if (qty <= 0) throw new ArgumentOutOfRangeException(nameof(qty));
        return unitPrice * qty;
    }
}
```

paramName までチェックできる Throws の形が用意されてるよ〜🧷✨ ([api.xunit.net][1])

---

### 4-3) コレクションのAssert（Contains / All / Collection）📚✅

```csharp
using System;
using System.Collections.Generic;
using System.Linq;
using Xunit;

public sealed class ProductSearchTests
{
    [Fact]
    public void Search_部分一致で候補が返る()
    {
        var repo = new[] { "Latte", "Mocha", "Tea", "Matcha Latte" };

        var results = ProductSearch.Search(repo, "Latte");

        // 「含まれる」は順番を縛らないから強い✨
        Assert.Contains("Latte", results);
        Assert.Contains("Matcha Latte", results);

        // 全部が検索語を含む、も“仕様”にできる✨
        Assert.All(results, x => Assert.Contains("Latte", x, StringComparison.OrdinalIgnoreCase));
    }

    [Fact]
    public void Collection_順番が仕様のときだけ_Collectionで縛る()
    {
        var xs = new[] { 10, 20, 30 };

        Assert.Collection(
            xs,
            x => Assert.Equal(10, x),
            x => Assert.Equal(20, x),
            x => Assert.Equal(30, x)
        );
    }
}

public static class ProductSearch
{
    public static IReadOnlyList<string> Search(IEnumerable<string> all, string keyword)
        => all.Where(x => x.Contains(keyword, StringComparison.OrdinalIgnoreCase)).ToList();
}
```

Assert.All と Assert.Collection は “意図が伝わる検査” に便利だよ〜📚✨ ([api.xunit.net][1])

---

## 5) よくある事故💣😇（ここ回避できるだけで強い！）

### 🚫 事故1：Assertが弱すぎてバグを通す

例：戻り値の一部しか見てない、例外の種類を縛ってない、など🙈

### 🚫 事故2：Assertが強すぎてリファクタ不能

例：コレクションの順番まで縛ったけど、順番はどうでもよかった…😵

### 🚫 事故3：「実装の写し」Assertになってる

例：内部の private な構造に依存したチェック（あとで崩壊しがち）🫠

---

## 6) AI活用コーナー🤖✨（Assertの観点を増やす）

この章はAIがめっちゃ役に立つよ〜！🥳
おすすめプロンプト（コピペOK）👇

* 「この仕様で **Assertすべき観点** を “値/例外/コレクション/状態” に分類して列挙して」
* 「このテストのAssert、**弱いところ**ない？ もっと意味が伝わるAssertに直して」
* 「順番を縛るべき？縛らないべき？ 理由もつけて」

Visual Studio側もAI連携が強化されてて、CopilotがNuGetの更新提案なども扱える流れが進んでるよ🧰🤖（パッケージ更新をAIで補助） ([Microsoft Learn][2])

---

## 7) まとめ🎀✅（この章の一言）

* Assertは **仕様そのもの**📘✨
* 「値・例外・コレクション・状態」の4カテゴリで考えると迷わない🧠✅
* **意味が伝わるAssert**を選んで、強すぎ弱すぎを避ける😌🌱

---

## おまけ：2026/01/18時点の“最新メモ”🆕✨

サンプルの想定に近いところだと、.NET 10.0.2（2026/01/13）・C# 14.0・Visual Studio 2026 (v18.2) が案内されてるよ〜📌 ([Microsoft][3])
xUnit v3 も 3.2.2 までリリースノートに並んでる（v3系）🧪✨ ([xUnit.net][4])

---

次の第13章（テスト名の付け方📝✨）に行く前に、もし希望あったら👇
「あなたの題材（実案件っぽい処理）」に合わせて **“Assertの型”テンプレ**（この場合はEqual／この場合はThrows、みたいな早見表）も作れるよ〜🧠💖

[1]: https://api.xunit.net/v3/3.0.0/Xunit.Assert.html "Class Assert | xUnit.net "
[2]: https://learn.microsoft.com/en-us/visualstudio/releases/2026/release-notes "Visual Studio 2026 Release Notes | Microsoft Learn"
[3]: https://dotnet.microsoft.com/en-US/download/dotnet/10.0 "Download .NET 10.0 (Linux, macOS, and Windows) | .NET"
[4]: https://xunit.net/releases/ "Release Notes | xUnit.net "
