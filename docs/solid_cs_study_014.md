# 第14章：OCPの現実：どこまで抽象化する？（やりすぎ注意）⚖️😅

この章は「OCPって大事なのは分かった！でも…抽象化しすぎて逆に辛くなるのが怖い🥺」を解決する回だよ〜✨
（ちなみに今の最新ラインは **.NET 10 / C# 14 / Visual Studio 2026** だよ🧡 ([Microsoft Learn][1])）

---

## 1) この章でできるようになること 🎯✨

* 「ここは拡張点にするべき✅／まだ早い❌」を判断できるようになる
* 抽象化の“やりすぎサイン”を見抜けるようになる
* “必要になったらスッと拡張できる”くらいの、ちょうどいい設計にできる😌💕

---

## 2) まず大前提：OCPは「未来予知」じゃないよ🔮❌
![Over-Engineering](./picture/solid_cs_study_014_false_future_prophecy.png)


OCPって聞くと「将来の追加に備えて、最初から全部インターフェースにする！」ってなりがちだけど…
それやると高確率で **“未来の妄想”にコードが支配される** のね😵‍💫💦

OCPのコツはこれ👇

* **変化しそうな場所だけ**、ちゃんと“差し替え口”を作る🚪✨
* それ以外は **シンプルに直書き** してOK🙆‍♀️✨（その方が読みやすい）

---

## 3) 抽象化しすぎると起きる「3大事故」🚑💥
![Too Many Abstractions](./picture/solid_cs_study_014_confusing_map.png)


### 事故①：クラスが増えすぎて迷子😇🗂️

`IOrderServiceFactoryProvider` みたいなのが生まれて、見るだけで疲れるやつ…🥲

### 事故②：変更が“簡単”じゃなくなる🌀

本当は1行直せばいいのに、
「インターフェース→実装→登録→テスト→差し替え…」って手順が増える😵

### 事故③：抽象の名前がウソになる🤥

最初は `IPaymentProcessor` が「支払い処理」だったのに、
気づいたら「割引もポイントも配送も…全部ここ」みたいに肥大化しがち💦

---

## 4) ちょうどいい抽象化の判断フレーム（これだけでOK）🧭✨

![Traffic light: Red (YAGNI), Yellow (Wait 3 times), Green (Abstract).](./picture/solid_cs_study_014_abstraction_traffic_light.png)

次の質問に「YES」が多いほど、拡張点にする価値が上がるよ👇

### ✅ Q1：その変更、**近いうちに来そう？**（確度高め？）🔜

「そのうち来るかも」程度なら、まだ早いことが多い😌

### ✅ Q2：変更が来たら、**既存コードを壊しやすい？**💣

たとえば `switch` の塊、巨大な `if`、複雑な分岐ロジックは壊れやすい💥

### ✅ Q3：変更が来るたびに、**同じ場所を毎回いじる？**🔁

“同じところ”を触り続けるなら、そこはホットスポット🔥

### ✅ Q4：その違いは、**「種類が増える」系？**🧩

例：支払い方法が増える、配送方法が増える、割引ルールが増える
→ こういうのは Strategy が効きやすい🎭✨

### ✅ Q5：抽象化したら、**テストが楽になる？**🧪

差し替えできるとテストが爆速＆安定しやすい👍✨

---

## 5) 実例で体感しよ：支払い方法を増やす場面💳📱✨

ここ、めちゃくちゃ“起きがち”だから最高の練習になるよ〜！😊

### ステップ0：最初はベタ書きでOK（1種類しかない）👌✨

「カード払いしかない」なら、最初からStrategyにしないで大丈夫🙆‍♀️
（読む人がラクなのが正義👑）

```csharp
public sealed class PaymentService
{
    public void Pay(Order order)
    {
        // まずはカード払いだけ
        ChargeCreditCard(order);
    }

    private void ChargeCreditCard(Order order)
    {
        // カード決済処理（仮）
    }
}
```

### ステップ1：2種類目が来たら“分岐”が生まれる😅

「PayPayも追加して〜」みたいな要求が来た瞬間、分岐が増えるよね💦

```csharp
public enum PaymentType { CreditCard, PayPay }

public sealed class PaymentService
{
    public void Pay(Order order, PaymentType type)
    {
        switch (type)
        {
            case PaymentType.CreditCard:
                ChargeCreditCard(order);
                break;
            case PaymentType.PayPay:
                ChargePayPay(order);
                break;
            default:
                throw new ArgumentOutOfRangeException(nameof(type));
        }
    }

    private void ChargeCreditCard(Order order) { }
    private void ChargePayPay(Order order) { }
}
```

ここで判断🧠✨
*支払いが今後も増えそう*なら、ここが拡張点の候補だよ🎯

---

## 6) 「ちょうどいいOCP」：Strategyに切り出す🎭✨
![Simple Strategy](./picture/solid_cs_study_014_simple_plug_adapter.png)


### 6-1) まず“差し替え口”を作る（インターフェース）🚪

```csharp
public interface IPaymentMethod
{
    bool CanHandle(string paymentCode); // "credit", "paypay" など
    void Pay(Order order);
}
```

### 6-2) 実装を増やす（追加は“新クラス追加”で済む✨）

```csharp
public sealed class CreditCardPayment : IPaymentMethod
{
    public bool CanHandle(string paymentCode) => paymentCode == "credit";
    public void Pay(Order order) { /* 決済処理 */ }
}

public sealed class PayPayPayment : IPaymentMethod
{
    public bool CanHandle(string paymentCode) => paymentCode == "paypay";
    public void Pay(Order order) { /* 決済処理 */ }
}
```

### 6-3) 呼び出し側は「選んで呼ぶ」だけ（既存修正が最小に✨）

```csharp
public sealed class PaymentService
{
    private readonly IReadOnlyList<IPaymentMethod> _methods;

    public PaymentService(IEnumerable<IPaymentMethod> methods)
        => _methods = methods.ToList();

    public void Pay(Order order, string paymentCode)
    {
        var method = _methods.FirstOrDefault(x => x.CanHandle(paymentCode))
            ?? throw new InvalidOperationException($"Unknown payment: {paymentCode}");

        method.Pay(order);
    }
}
```

💡この形のいいところ

* 「PayPal追加！」→ `PayPalPayment` を **追加するだけ** でいける🎉
* `PaymentService` は **ほぼ触らない**（OCPっぽい！）✨

---

## 7) でも注意！Strategyも“やりすぎ”がある⚠️😅

### やりすぎサイン①：種類が増えないのに抽象だけ増えてる📈

「支払い増えるかも…」で3年増えないとか、あるある🤣

### やりすぎサイン②：`CanHandle` が複雑になってきた🧠💦

`if (customerRank == ... && region == ... && ...)` みたいになるなら、
それは“支払い”じゃなくて“ルールエンジン”領域かも😇（別設計を考える）

### やりすぎサイン③：抽象の粒度が細かすぎる🧂

`IPaymentLogger` `IPaymentValidator` `IPaymentContextFactory` …みたいに分裂し始めたら、
「今それ必要？」を一回落ち着いて考えよ🫶

---

## 8) 超実戦ルール（迷ったらこれ）📌✨

### ルールA：「2回目が来たら抽象化」🔁
![Rule of Three](./picture/solid_cs_study_014_rule_of_three_stamp.png)


1回目：ベタ書きでOK
2回目：分岐が増えた！→ ここで抽象化を検討
3回目：ほぼ確定で拡張点化🎯

### ルールB：「変化する理由」が同じものだけまとめる🧠

支払い方法（種類が増える）と、割引（計算が変わる）は別物になりがち🌀
混ぜると地獄😇

### ルールC：「抽象化は“削除できる”形が強い✂️✨」

“いらなかったら戻せる”くらい軽い抽象がベスト👍
（重いフレームワーク自作は、だいたい未来の自分を泣かせる🥲）

---

## 9) ミニ演習（手を動かすと一気に分かるよ！）🧩💪✨

### 演習①：配送方法を増やす🚚📦

* `Standard` だけ → `Express` 追加 → `Pickup` 追加
  どのタイミングでStrategyにするか、判断してみてね😊

### 演習②：税計算（国内/海外）💰🌍

* 2種類しか増えないなら `switch` のままでもアリ？
* “国が増える”なら拡張点にする？
  → どっちの方が読みやすいか、理由つきで答えると最強✨

### 演習③：例外の設計🧯

* 未対応の支払いが来たらどうする？
  （例外？エラー結果？ログ？）
  → “呼び出し側が困らない”が正解だよ🫶

---

## 10) 🤖AI活用メモ（Copilot/Codexに投げると強いプロンプト）✨

以下、コピペでOKだよ〜💕

```text
このコードの「将来の追加で壊れやすいホットスポット」を3つ指摘して。
そのうち1つを選んで、OCPに寄せる最小のリファクタ案をステップで出して。
（やりすぎ抽象化は避けて、2回目の変更に耐える程度で）
```

```text
Paymentの分岐が増えてきた。Strategyにしたい。
インターフェース設計（メソッド名・責務）と、実装クラス名の候補を出して。
ついでにユニットテストの観点も5つ。
```

```text
この抽象化、過剰かどうかレビューして。
「過剰ならどう簡略化するか」も提案して。
```

---

## まとめ 🎀✨

* OCPは「全部抽象化しよう！」じゃなくて、**変わる場所だけに拡張点**を作るのがコツ😊
* 判断は「変化の確度」「同じ場所を何度も触るか」「種類が増えるか」「テストが楽になるか」👍
* 迷ったら **“2回目が来たら抽象化”** が超強いルールだよ🔁✨

次の第15章は、まさにこの判断を使って「料金計算・割引・ポイント」を“追加に強い形”へ整える実戦回だよ〜💰🎫🚀

[1]: https://learn.microsoft.com/en-us/visualstudio/releases/2026/release-notes?utm_source=chatgpt.com "Visual Studio 2026 Release Notes"
