# 第17章：LSPが壊れる典型：例外投げちゃう・条件が変わる🙅‍♀️💥

この章はね、**「継承したのに、呼ぶ側が急に壊れる🥲」**の代表パターンを、めちゃ具体例でつかむ回だよ〜！🧠✨
前章（第16章）で触れた「親の代わりに子を入れても大丈夫」の“**大丈夫**”を、ちゃんと言語化していこうね🧩💕

---

## 1) この章のゴール 🎯✨

この章が終わると、こんなことができるようになるよ！🫶

* **LSP違反の典型パターン**（例外ドーン💥 / 条件ガラッ😇）を見抜ける
* **「事前条件」「事後条件」**を、超やさしい言葉で説明できる
* 「それ継承で作るの無理じゃない？」を**早めに察知**できる👀✨
* テストで **「置換できる」** を守る方法がわかる🧪✅

---

## 2) まず“LSPの中身”を1分で整理 🧠⏱️

LSPって要するにこう👇

> **呼び出し側（クライアント）は、親型として扱ってるだけ**
> だから、子に差し替えても **同じ約束（契約）で動いてほしい** 🙏✨

![LSP Surprise Box](./picture/solid_cs_study_017_lsp_surprise_box.png)

この「約束」を言語化すると、よく **設計の契約（Design by Contract っぽい考え）** で言う👇の3つになるよ😊

* **事前条件（Preconditions）**：呼ぶ前に守ってね（入力の条件）
* **事後条件（Postconditions）**：呼んだ後に保証するよ（結果の条件）
* **不変条件（Invariants）**：いつでも守るよ（状態のルール）

![Design by Contract](./picture/solid_cs_study_017_design_by_contract.png)

そしてLSPの超重要ルールはこれ👇

* 子は **事前条件を強くしちゃダメ**（親より厳しくしない）
* 子は **事後条件を弱くしちゃダメ**（親より保証を減らさない）
* 子は **親が投げない例外を増やしちゃダメ**（普通に使ってたら急に落ちるの禁止） ([ウィキペディア][1])

---

## 3) 典型パターンA：子が「それ無理」で例外を投げる 🙅‍♀️💥

### ✅ ありがち状況

![Exception Violation](./picture/solid_cs_study_017_exception_violation.png)

「親ではできる（契約上できる）」のに、子にした瞬間 **NotSupportedException** とか **InvalidOperationException** が出るやつ😇

### 👇 ダメ例（“支払い”の継承で事故る）

```
public abstract class PaymentMethod
{
    // 契約：注文を支払う（成功したら true）
    public abstract bool Pay(Order order);
}

public sealed class CreditCardPayment : PaymentMethod
{
    public override bool Pay(Order order)
    {
        // ふつうに支払える
        return true;
    }
}

// 代引き（Cash on Delivery）
public sealed class CashOnDeliveryPayment : PaymentMethod
{
    public override bool Pay(Order order)
    {
        // デジタル商品は代引きできません！
        if (order.IsDigital)
            throw new NotSupportedException("デジタル商品は代引き不可です");

        return true;
    }
}
```

### 💥 何が壊れるの？

呼び出し側はこういう気持ちなの👇

```
public bool Checkout(Order order, PaymentMethod payment)
{
    // 親型として「支払いできる」前提で呼ぶ
    return payment.Pay(order);
}
```

これ、`CashOnDeliveryPayment` に差し替えた瞬間に **例外で落ちる**。
つまり **「親の代わりに子を入れたら壊れる」＝LSP違反** 😭💥 ([ウィキペディア][1])

---

### ✅ 直し方の考え方（この章の範囲でいけるやつ）🛠️✨

ポイントはこれ👇
**「できないパターンがあるなら、そもそも“同じ型”に入れない」** が基本！

たとえば：

* 「どの注文でも支払える」ものだけを `PaymentMethod` にする
* 代引きみたいに条件があるなら、**別の種類として扱う**（選択ロジック側で弾く）
* “通常フロー”の失敗を例外にしない（Result型/エラー戻りにする）※ただし契約を揃える

例外はね、
**「プログラムのバグ」や「想定外」には強いけど、仕様の分岐（普通に起きる失敗）に使うと事故りやすい**よ〜🥺

---

## 4) 典型パターンB：子が「呼ぶ前の条件」を勝手に厳しくする 😵‍💫📌

![Parent Gate (open) vs Child Gate (narrow). LSP Precondition Violation.](./picture/solid_cs_study_017_lsp_preconditions.png)

### ✅ イメージ

親：「金額0以上ならOKだよ〜」
子：「1000円以上じゃないとダメ！」
これ、**子が事前条件を強くしてる**のね🙅‍♀️

### 👇 ダメ例（親より厳しい条件にする）

```
public class DiscountPolicy
{
    // 契約：金額が0以上なら適用できる（割引額を返す）
    public virtual decimal Calculate(decimal totalAmount)
    {
        if (totalAmount < 0) throw new ArgumentOutOfRangeException(nameof(totalAmount));
        return 0m;
    }
}

public class PremiumMemberDiscount : DiscountPolicy
{
    public override decimal Calculate(decimal totalAmount)
    {
        // 子が勝手に条件を追加！
        if (totalAmount < 1000) throw new InvalidOperationException("1000円未満は対象外");
        return totalAmount * 0.1m;
    }
}
```

### 💥 何が困る？

呼び出し側は親の契約で呼ぶのに、子だと落ちる。
これが **「事前条件を強めちゃダメ」** の意味だよ🧠✨ ([ウィキペディア][1])

### ✅ じゃあどうする？

* その割引は「いつでも計算できる」型じゃなくて、**適用可否の判定とセット**にする
* もしくは「対象外なら0円」みたいに、**親と同じ契約**に合わせる（例外にしない）

---

## 5) 典型パターンC：子が「結果の保証」を弱くする（返り値が別物）😇📉

### ✅ イメージ

![Postcondition Violation](./picture/solid_cs_study_017_postcondition_violation.png)

親：「成功したら TrackingNumber は必ず入ってるよ！」
子：「成功しても空文字返すことあるよ！」
→ それ **事後条件を弱めてる** 😭

```
public class Shipment
{
    public string TrackingNumber { get; init; } = "";
}

public class ShippingService
{
    // 契約：成功したShipmentのTrackingNumberは空じゃない
    public virtual Shipment CreateShipment(Order order)
    {
        return new Shipment { TrackingNumber = "TRK-123" };
    }
}

public class TestShippingService : ShippingService
{
    public override Shipment CreateShipment(Order order)
    {
        // テスト用だから…って空文字返しちゃう
        return new Shipment { TrackingNumber = "" };
    }
}
```

呼ぶ側が
「TrackingNumberある前提で画面表示」
とかすると、子でUIが壊れるよね🥲

---

## 6) 典型パターンD：ルール（不変条件）が子で変わる 🧨🧱

![Invariant Violation](./picture/solid_cs_study_017_invariant_violation.png)

これは初心者さんが一番引っかかりやすい雰囲気👇

* 親：「確定した注文は編集できません」
* 子：「特別会員は確定後も編集できまーす」
  → 親の世界の前提が崩れて、呼び出し側のロジックが破綻しやすい💥

こういうのが出たら、だいたい **継承で表現するのが無理筋** のサインだよ🚨✨

---

## 7) 見つけ方チェックリスト ✅👀（超実戦）

![LSP Warning Signs](./picture/solid_cs_study_017_lsp_warning_signs.png)

次の匂いがしたらLSPを疑ってOK🙆‍♀️

* `override` の中に **NotSupportedException** / **InvalidOperationException** が出てくる💣
* 子だけ `if (条件) throw` みたいな **追加ルール**がある🧯
* 子だけ「-1は未定」みたいな **特別値（番兵値）** を返す😇
* 呼び出し側に `if (x is ChildType)` が増える（子の都合が漏れてる）🫠

---

## 8) テストで守る：「置換できる」テスト（コントラクトテスト）🧪✨

![Contract Testing](./picture/solid_cs_study_017_contract_testing.png)

やり方はシンプルで、**親の契約テストを1セット作って、全部の実装に同じテストを流す**のが強いよ💪

例：支払いメソッドの契約テスト（雰囲気）

```
public abstract class PaymentContractTests
{
    protected abstract PaymentMethod Create();

    [Fact]
    public void Pay_Should_NotThrow_For_NormalOrders()
    {
        var payment = Create();
        var order = new Order { IsDigital = false };

        // 「親として普通に使う範囲」で例外が出ないこと
        var ex = Record.Exception(() => payment.Pay(order));
        Assert.Null(ex);
    }
}
```

このテスト、代引きが混ざってると落ちる→
「じゃあ同じ型に入れない方がいいね」って判断できるのが最高✨

---

## 9) 🤖AI（Copilot / Codex系）に頼ると爆速になるプロンプト例 💬✨

コピペで使ってOK〜！🫶

* 「この継承関係で **LSP違反になりそうな点**を、呼び出し側視点で説明して」
* 「親クラスの **契約（事前条件/事後条件）** を箇条書きにして」
* 「このクラス群に対して、**コントラクトテスト**をxUnitで作って」
* 「NotSupportedException を投げている override を列挙して、代替設計案を3つ出して」

Visual Studio 2026 系のビルドでは、Copilot がIDEに深く統合されていく流れもあるから、こういう“設計レビューの壁打ち”は相性いいよ🤖✨ ([Visual Studio][2])

---

## 10) まとめ 🎀✨（この章で覚えたいこと）

* LSPは「親の代わりに子を入れても壊れない」🧱➡️🧱
* 壊れ方の代表はこの2つ！

  * **例外を増やす**（子だけ落ちる）💥
  * **条件を変える**（子だけ厳しい／保証が弱い）😇
* 対策は

  * 「同じ型に入れない（モデルを分ける）」
  * 「契約を揃える」
  * 「契約テストで守る」🧪✅

---

## おまけ：今のC#周り（最新確認メモ）📌✨

* C# 14 の新機能は Microsoft Learn に整理されていて、**Visual Studio 2026 か .NET 10 SDK** で試せるよ ([Microsoft Learn][3])
* .NET 10 の配布ページでは、例えば **10.0.1 の最新リリース日が 2025-12-09** として案内されてるよ ([Microsoft][4])

（※LSP自体は言語が新しくなっても“設計の約束”なので、ずっと効くやつ😊）

---

次の第18章は、ここで詰んだ継承を **「合成（コンポジション）で救う」** 回だよ🧩✨
第17章の内容で、「あ、これは継承じゃなくて別の作り方だな」って嗅ぎ分けられるようになるのが超大事👍💕

[1]: https://en.wikipedia.org/wiki/Liskov_substitution_principle?utm_source=chatgpt.com "Liskov substitution principle"
[2]: https://visualstudio.microsoft.com/insiders/?utm_source=chatgpt.com "Visual Studio 2026 Insiders - Faster, smarter IDE - Microsoft"
[3]: https://learn.microsoft.com/ja-jp/dotnet/csharp/whats-new/csharp-14?utm_source=chatgpt.com "C# 14 の新機能"
[4]: https://dotnet.microsoft.com/en-US/download/dotnet/10.0?utm_source=chatgpt.com "Download .NET 10.0 (Linux, macOS, and Windows) | .NET"
