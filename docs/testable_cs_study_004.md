# 第04章：純粋ロジックってなに 🌿✨

ここからが「テスタブル設計」の気持ちよさゾーンです😆💖
“ピュア”を掴むと、テストが一気にラクになります🧪⚡

---

## この章のゴール 🎯

読み終わったら、これができるようになります👇✨

* 「純粋ロジック（ピュア）」を説明できる😊
* コードを見て「ここ副作用あるね！」って指させる👀👉
* “ピュアに寄せる書き方”をC#でできる🧼✨
* テストが爆速になる理由が腹落ちする⚡🚀

---

## 純粋ロジックの定義はこれだけ 🎯🌿


![testable_cs_study_004_pure_function.png](./picture/testable_cs_study_004_pure_function.png)

**純粋ロジック（ピュア）**＝だいたいこういう関数👇

* ✅ **同じ入力なら、必ず同じ出力**（ブレない🎯）
* ✅ **副作用がない**（外の世界を触らない🧤）
* ✅ **状態を持たない**（または外から渡される📦）

「外の世界」って？ → ファイル🗂️、DB🗄️、ネット🌐、時刻🕰️、乱数🎲、UI🖥️… みたいなやつ！

---

## まずは例で一発理解しよ 😆🧡

![testable_cs_study_004_pure_vs_impure_factory.png](./picture/testable_cs_study_004_pure_vs_impure_factory.png)

## ピュアな例 ✅

税計算とか、割引計算とか、文字列整形とかはピュアにしやすいです🌿

```csharp
public static class PriceLogic
{
    public static decimal AddTax(decimal price, decimal taxRate)
        => Math.Round(price * (1m + taxRate), 0, MidpointRounding.AwayFromZero);
}
```

* 入力：`price`, `taxRate`
* 出力：計算結果
* 外部アクセス：なし✨
* 毎回同じ結果：出る🎯

---

## ピュアじゃない例 ❌

「今の時刻を読む」「ログ出す」「ファイル読む」などが混ざると副作用です😵‍💫

```csharp
public static class PriceLogic
{
    public static decimal AddTaxWithLog(decimal price, decimal taxRate)
    {
        var result = Math.Round(price * (1m + taxRate), 0, MidpointRounding.AwayFromZero);

        Console.WriteLine($"[{DateTime.Now}] result={result}"); // 👈 I/O + 時刻（副作用）

        return result;
    }
}
```

これ、**計算ロジック自体は同じ**なのに、

* `DateTime.Now` が毎回変わる🕰️
* `Console.WriteLine` が外に影響を与える🖥️
  → テストが「環境っぽいもの」に引きずられやすくなります😇💦

---

## 副作用ってなに？ありがちなやつ一覧 🚨

![testable_cs_study_004_side_effect_monsters.png](./picture/testable_cs_study_004_side_effect_monsters.png)

「副作用＝外の世界を触る or 外の世界に依存する」って思えばOK🙆‍♀️✨

* 🕰️ 時刻：`DateTime.Now`, `DateTime.UtcNow`
* 🎲 乱数：`new Random().Next()`
* 🌐 ネット：HTTP、外部API
* 🗂️ ファイル：`File.ReadAllText` / `WriteAllText`
* 🗄️ DB：クエリ発行
* 🖥️ UI：画面入力、表示
* 🧷 グローバル状態：`static`な可変フィールド、シングルトンの状態
* 🔥 例外を「投げる/握る」も設計次第で境界の話になってくる（後でやるよ👀）

---

## ピュアだとテストが爆速になる理由 ⚡🧪

![testable_cs_study_004_test_speed.png](./picture/testable_cs_study_004_test_speed.png)

ピュアな関数はこうなるからです👇✨

* ✅ **準備がラク**：入力を渡すだけ📦
* ✅ **片付け不要**：ファイル消すとかDB戻すとか要らない🧹
* ✅ **再現性MAX**：同じ入力なら同じ結果🎯
* ✅ **並列実行しやすい**：テスト同士が邪魔しない👯‍♀️

しかも、今どきの .NET は **.NET 10 がLTS**で、C#も **C# 14 が最新**になってて、開発体験も安定路線です😊✨（.NET 10は2025-11-11リリースのLTSで、2026-01-13時点の最新パッチも公開されています📌） ([Microsoft][1])

---

## C#でピュアに寄せるコツ 7つ 🧼✨

![testable_cs_study_004_tips_toolbox.png](./picture/testable_cs_study_004_tips_toolbox.png)

## 1 依存は引数で渡す 📦

「中で取りに行かない」→「外から渡す」へ🔁
例：`DateTime.Now` を読まず、`now` を引数で受け取る🕰️

```csharp
public static bool IsExpired(DateTime now, DateTime expiresAt)
    => now >= expiresAt;
```

## 2 返り値で返す 🎁

結果は「return」へ。ログ・画面表示は別の場所へ🖥️🚪

## 3 staticは悪じゃないけど “状態” は持たせない 🧊

`static` でも **純粋な関数置き場**なら全然OK🙆‍♀️
危ないのは **staticな可変状態**（カウンタ増えるとか）⚠️

## 4 ミュータブルな共有を避ける 🧯

共有Listをいじる…みたいなのは事故りやすい😵
「入力→変換→出力」に寄せると安全✨

## 5 record で値っぽく扱うと楽 💎

C#は record が強いです💖（値オブジェクト感が出る）

```csharp
public record CartItem(string Name, int Qty, decimal UnitPrice);

public static decimal CalcTotal(IEnumerable<CartItem> items)
    => items.Sum(x => x.UnitPrice * x.Qty);
```

## 6 例外より「判定結果」を返す設計もピュアにしやすい ✅

（ここは後半で深掘りするけど👀）
たとえば `bool` とか `Result` 的なもの。

## 7 “境界の外” に出すクセをつける 🚪

ログ、保存、送信、UI表示…は **あとで境界として包む**（第5章以降の主役🧩）

---

## ミニ実験 ピュアに分けると一気にキレイになる 🎉

![testable_cs_study_004_discount_refactor.png](./picture/testable_cs_study_004_discount_refactor.png)

題材：会員ランクで割引して合計を出す💳✨
「割引計算」はピュアにできる典型です🌿

## ありがちな混ぜ混ぜ版 😵‍💫

```csharp
public decimal Checkout(string memberRank, decimal price)
{
    Console.WriteLine("計算開始");              // I/O
    var now = DateTime.Now;                     // 時刻
    if (memberRank == "Gold" && now.DayOfWeek == DayOfWeek.Friday)
        price *= 0.9m;

    Console.WriteLine($"合計={price}");         // I/O
    return price;
}
```

## ピュア部分だけ抜き出す ✨

```csharp
public static class DiscountLogic
{
    public static decimal ApplyMemberDiscount(
        decimal price,
        string memberRank,
        DayOfWeek dayOfWeek)
    {
        if (memberRank == "Gold" && dayOfWeek == DayOfWeek.Friday)
            return price * 0.9m;

        return price;
    }
}
```

こうすると…

* テスト：`dayOfWeek` を渡すだけで金曜判定できる🧪✨
* I/O：別の場所で好きに出せる🖥️
* 第14章の `IClock` にも繋げやすい🕰️🚧

---

## テストの雰囲気だけ先に見せるね 🧪👀

![testable_cs_study_004_test_case_matrix.png](./picture/testable_cs_study_004_test_case_matrix.png)

（テスト環境の作り方は第8章でしっかりやるよ🛠️✨）

```csharp
using Xunit;

public class DiscountLogicTests
{
    [Fact]
    public void Gold_and_Friday_gets_10_percent_off()
    {
        var result = DiscountLogic.ApplyMemberDiscount(
            price: 1000m,
            memberRank: "Gold",
            dayOfWeek: DayOfWeek.Friday);

        Assert.Equal(900m, result);
    }
}
```

今の xUnit は v3 系が .NET 8 以上に対応していて、現行の .NET（例：.NET 10）でも使えます🧪✨ ([xunit.net][2])

---

## ピュア判定チェックリスト ✅👀

この質問に「うん…」が混ざったら、だいたいピュアじゃないです🤣💦

* 同じ入力でも結果が変わる可能性ある？（時刻🕰️/乱数🎲）
* ファイル/DB/ネット/Console を触ってる？🗂️🗄️🌐🖥️
* `static` な可変フィールドを読んだり書いたりしてる？🧷
* 関数の外に影響（ログ・保存・送信）を出してる？📨

---

## AIに手伝ってもらうコツ 🤖💡

![testable_cs_study_004_ai_refactoring.png](./picture/testable_cs_study_004_ai_refactoring.png)

Copilot/Codex にこう頼むと超便利です🧡✨

* 「このメソッドの **副作用** を列挙して、**純粋ロジック** に分離して」
* 「入力と出力を整理して、関数のシグネチャ案を3つ出して」
* 「このロジックのテストケースを網羅的に提案して（境界値/異常系も）」
* 「副作用が残ってないかチェックして」👀✅

⚠️ 注意：AIはたまに “しれっと I/O” を混ぜてきます（`DateTime.Now` とか）😇
出てきたコードは、さっきのチェックリストで必ず確認してね✅✨

---

## 練習問題 やってみよ 🏋️‍♀️✨

## 問1 ピュアかどうか判定 👀

次のうちピュアなのはどれ？（複数OK）

1. `return Guid.NewGuid().ToString();`
2. `return input.Trim().ToUpperInvariant();`
3. `File.ReadAllText(path)`
4. `return items.Sum(x => x.Price);`

## 問2 ピュア化リファクタ ✂️

「締切チェック」のロジックをピュアにしてみて🕰️✨

* ヒント：`DateTime.Now` を中で読まない！

## 問3 テストケース出し 🧪

「金曜だけ10%オフ」を、境界値も含めてテストケース列挙してみて📋✨
（AIに出させてもOK！でもチェックは自分でね👀✅）

---

## まとめ 🌿💖

* ピュア＝**同じ入力→同じ出力**、**副作用なし**🎯✨
* I/O・時刻・乱数・グローバル状態はピュアの敵😈
* ピュアにできると、テストは **速い・安い・安心**🧪⚡
* 次章で「境界」という考え方に繋がって、I/Oを外に追い出す設計が完成していくよ🚧🚪✨

次は **第5章 境界の考え方** で、「じゃあI/Oはどこに置くの？」を気持ちよく整理しようね😆🧩💖

[1]: https://dotnet.microsoft.com/en-us/platform/support/policy/dotnet-core?utm_source=chatgpt.com "NET and .NET Core official support policy"
[2]: https://xunit.net/?utm_source=chatgpt.com "xUnit.net: Home"
