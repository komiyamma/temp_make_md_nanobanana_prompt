# 第55章【演習】C#で「お金(Money)」と「メールアドレス(Email)」を値オブジェクトで作る💰📧

![C#で「お金(Money)」と「メールアドレス(Email)」を値オブジェクトで作る](./picture/ddd_cs_study_055_money_email_ex.png)

ここはDDDの“手触り”が一気に分かる神回です✨
`decimal` や `string` をそのまま使うのをやめて、**「意味を持った型」**にしていきます😊

---

## この章のゴール🎯

* `Money`（金額＋通貨）を **不変** な値オブジェクトとして作れる
* `Email`（メールアドレス）を **不正な値が生まれない** ように作れる
* “値の表現”が整うと、設計が迷いにくくなるのを体感できる✨

---

## まずイメージしてみよっ🧠💡

![primitive_obsession](./picture/ddd_cs_study_055_primitive_obsession.png)

たとえば、こんなコード…よくあります👇

* `decimal price`
* `string email`

これ、**意味が弱い**んだよね😢
`price` に `-100` が入ってもコンパイル通っちゃうし、`email` に `"aaa"` が入っても通っちゃう。

DDDだとここをこうする🎉

* `Money price`
* `Email email`

すると、**不正な値がそもそも作れない**世界にできる✨
（“後でチェックする”じゃなくて、“最初から生まれない”！👶🚫）
 
 ```mermaid
 classDiagram
    class BadExample {
        -decimal price ❌
        -string email ❌
        note: "マイナスや変な文字が<br/>入り放題😱"
    }
    
    class GoodExample {
        -Money price ✅
        -Email email ✅
        note: "方の中で<br/>ルールが守られる🛡️"
    }
    
    BadExample ..> GoodExample : 進化 ✨
 ```
 
 ---

## 演習のお題📘✍️

### ✅ お題1：Money を作ろう💰

ルール例（最低限これだけ守ろう）👇

* 金額は `decimal`
* 通貨は `"JPY"`, `"USD"` みたいな 3文字想定
* **通貨が違う Money 同士は足せない**（超重要❗）
* 不正な値（NaN的なものはdecimalに無いけど、マイナスや通貨の空など）は作れないようにする

### ✅ お題2：Email を作ろう📧

ルール例👇

* 空文字・空白はNG
* `@` を含まないのはNG
* 前後の空白は削る
* 比較しやすいように **小文字に正規化**（ケースの差で別物扱いしない）

### ✅ お題3：軽く使ってみよう🧪

* `Order`（注文）みたいなクラスを作って

  * `Email CustomerEmail`
  * `Money Total`
  * を持たせてみてね😊

---

## 実装例（解答）✅✨

この章は「動けばOK」じゃなくて、**“迷わない型”を作る**のが目的だよ〜！💪🌸

---

### 1) Resultパターン（簡易）を用意🎁（例外を乱用しない）

※前の章（Resultパターン）を軽く使う想定で、最小構成にしてるよ😊

```csharp
namespace MyApp.Domain.Shared;

public sealed record Error(string Code, string Message);

public sealed class Result<T>
{
    public bool IsSuccess { get; }
    public T? Value { get; }
    public Error? Error { get; }

    private Result(bool isSuccess, T? value, Error? error)
    {
        IsSuccess = isSuccess;
        Value = value;
        Error = error;
    }

    public static Result<T> Ok(T value) => new(true, value, null);
    public static Result<T> Fail(string code, string message) => new(false, default, new Error(code, message));
}
```

---

### 2) Money（値オブジェクト）💰

![money_currency](./picture/ddd_cs_study_055_money_currency.png)

ポイントはこれ👇

* **不変**（`readonly record struct`）
* **生成時にバリデーション**
* **加算は同一通貨のみ**

```csharp
namespace MyApp.Domain.ValueObjects;

using MyApp.Domain.Shared;

public readonly record struct Money
{
    public decimal Amount { get; }
    public string Currency { get; }

    private Money(decimal amount, string currency)
    {
        Amount = amount;
        Currency = currency;
    }

    public static Result<Money> Create(decimal amount, string currency)
    {
        currency = (currency ?? "").Trim().ToUpperInvariant();

        if (currency.Length != 3)
            return Result<Money>.Fail("Money.Currency.Invalid", "通貨は3文字（例: JPY, USD）にしてね💦");

        // ここは要件で変えてOK！
        // 例: 返品や残高などを扱うならマイナス許可の方が自然な場合もあるよ🌀
        if (amount < 0)
            return Result<Money>.Fail("Money.Amount.Negative", "金額は0以上にしてね💦");

        // 通貨ごとの小数桁とか厳密にやりたくなったら、ここを拡張する✨
        return Result<Money>.Ok(new Money(decimal.Round(amount, 2), currency));
    }

    public Result<Money> Add(Money other)
    {
        if (Currency != other.Currency)
            return Result<Money>.Fail("Money.Currency.Mismatch", $"通貨が違うよ❗ {Currency} と {other.Currency} は足せないよ💦");

        return Result<Money>.Ok(new Money(Amount + other.Amount, Currency));
    }

    public override string ToString() => $"{Amount} {Currency}";
}
```

> 🌟「演習としてはこれで十分」！
> でも実戦では、JPYは小数なし、USDは2桁…みたいに“通貨ごとのルール”が出てくるので、拡張余地も残してあるよ😊

---

### 3) Email（値オブジェクト）📧

![email_normalization](./picture/ddd_cs_study_055_email_normalization.png)

ここは「正規化」が大事✨

* Trimして
* 小文字にして
* 最低限の形式チェック！

```csharp
namespace MyApp.Domain.ValueObjects;

using MyApp.Domain.Shared;

public readonly record struct Email
{
    public string Value { get; }

    private Email(string value) => Value = value;

    public static Result<Email> Create(string input)
    {
        if (input is null)
            return Result<Email>.Fail("Email.Null", "メールアドレスがnullだよ💦");

        var value = input.Trim().ToLowerInvariant();

        if (value.Length == 0)
            return Result<Email>.Fail("Email.Empty", "メールアドレスが空だよ💦");

        if (value.Contains(' ') || value.Contains('\t') || value.Contains('\n'))
            return Result<Email>.Fail("Email.Whitespace", "メールアドレスに空白が入ってるよ💦");

        var atIndex = value.IndexOf('@');
        if (atIndex <= 0 || atIndex != value.LastIndexOf('@') || atIndex == value.Length - 1)
            return Result<Email>.Fail("Email.Format", "メールアドレスの形が変だよ💦（例: a@b.com）");

        return Result<Email>.Ok(new Email(value));
    }

    public override string ToString() => Value;
}
```

> ✅ 正規表現でガチガチにするより、最初は「最低限のルール」でOKだよ😊
> 本当に厳密にやると沼りやすいので、必要になってから強化しよう〜🌀

---

### 4) 使ってみる（ミニ注文モデル）🛒✨

```csharp
namespace MyApp.Domain.Orders;

using MyApp.Domain.ValueObjects;

public sealed class Order
{
    public Email CustomerEmail { get; }
    public Money Total { get; }

    public Order(Email customerEmail, Money total)
    {
        CustomerEmail = customerEmail;
        Total = total;
    }

    public override string ToString() => $"Order: {CustomerEmail} / Total: {Total}";
}
```

---

## 動作確認用ミニコード（コンソールでOK）🧪🎮

```csharp
using MyApp.Domain.ValueObjects;
using MyApp.Domain.Orders;

var emailResult = Email.Create("  KomiYamma@Example.com ");
var moneyResult = Money.Create(1200m, "jpy");

if (!emailResult.IsSuccess) Console.WriteLine(emailResult.Error);
if (!moneyResult.IsSuccess) Console.WriteLine(moneyResult.Error);

if (emailResult.IsSuccess && moneyResult.IsSuccess)
{
    var order = new Order(emailResult.Value!.Value, moneyResult.Value!.Value);
    Console.WriteLine(order);
}
```

---

## 追加ミッション（ちょいレベルアップ）🔥✨

### ⭐ ミッションA：Moneyの演算を増やす

* `Subtract`
* `Multiply(decimal rate)`（割引とか税とか📉）

ただし👇

* **通貨が違う減算はNG**
* 0未満がダメなら、減算でマイナスになる場合はエラーにする

### ⭐ ミッションB：Emailに「ドメイン制限」を入れる

例：大学アプリなら

* `@univ.ac.jp` しか許可しない🎓✨

### ⭐ ミッションC：AIにテストを書かせる🧠🤝

![test_automation](./picture/ddd_cs_study_055_test_automation.png)

CopilotやAIにこう頼むと超速いよ👇

* 「Money.Create の境界値テストを書いて」
* 「Email.Create の失敗パターンを網羅して」

その後、あなたは **“テストケースの妥当性チェック”**だけやればOK👌✨
AI時代の強い動き方だよ〜🚀

---

## よくあるハマりポイント集⚠️💦

* 😵 `Money` を `decimal` だけで持って通貨を忘れる
  → 後で「USDとJPYを足しちゃった！」事故が起きる

* 😵 `Email` を `string` のまま放置
  → `"aaa"` が混入して、ログインや通知が壊れる

* 😵 値オブジェクトなのに `set;` を生やしちゃう
  → いつの間にか値が変わって地獄👻（不変は正義！）

---

## まとめ🎉

この章で作ったのは、ただのクラスじゃなくて…

✅ **「不正な値を生まれさせない防波堤」**
✅ **「コードを読んだ瞬間に意味が分かる型」**

これが増えるほど、設計の迷いが減っていくよ😊✨

---

次の章以降で、この `Money` や `Email` が **エンティティ**や**集約**の中でどう効いてくるか、どんどん気持ちよくなっていくので楽しみにしててね〜💪💖
