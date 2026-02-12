# 第08章：SRPの感覚「変更理由は1つ」ってどういうこと？🎯

この章は、SRP（単一責務の原則）の**いちばん大事な感覚**をつかむ回だよ〜😊💡
結論から言うと、SRPはこう👇

* ✅ **“メソッドが1つ”じゃない**
* ✅ **“クラスが小さい”だけでもない**
* ✅ **「変更理由（＝変わる理由）」が1つ**ってこと！🎯

SRPはだいたい「クラスは1つの理由でしか変更されるべきじゃない」って表現されるよ📌 ([blog.cleancoder.com][1])
さらに最近の説明だと「1つのアクター（利害関係者のグループ）に対して責務を持つ」って言い方もよく使われるよ👥✨ ([ウィキペディア][2])

---

## 8.1 この章のゴール🎓💖

この章を終えると、こうなれるよ👇

* ✅ **「責務＝変更理由」**で説明できるようになる🗣️✨
* ✅ 1つのクラスに**複数の変更理由が混ざってる**のを見つけられる🔎
* ✅ いきなり分割せずに、まず**“分けるべき境界の候補”**を言語化できる🧠💡

（分割テク自体は次章以降でガッツリやるよ〜🧹✨）

---

## 8.2 「変更理由」ってなに？🧩💭

![変更理由カード](./picture/solid_cs_study_008_change_reason_cards.png)

### 🔥 変更理由＝「誰の都合で変わる？」

![stakeholder_tug_of_war](./picture/solid_cs_study_008_stakeholder_tug_of_war.png)

SRPの“理由”は、だいたいこれ👇

* 🧑‍💼 **経理**「請求書の税計算を変えて」
* 🛍️ **営業/マーケ**「注文メールの文章変えて」
* 🧑‍🔧 **運用**「配送会社を切り替えるよ」
* 🔐 **セキュリティ**「ログの出し方を変えて」
* 🧑‍⚖️ **法務**「規約に合わせて表示を変えて」

この「誰の要望で変わる？」が違うのに、**同じクラスに全部入ってる**と…
💥「え、税計算を直しただけなのにメールも壊れた」みたいな地獄が起きる😇🔥

---

## 8.3 SRPのよくある誤解ランキング😵‍💫➡️😌

![misconception_buster](./picture/solid_cs_study_008_misconception_buster.png)

### ❌ 誤解1：「クラスは小さくしろ！短ければOK！」

短くても、**別の変更理由が混ざってたらアウト**だよ〜😇

### ❌ 誤解2：「1クラス1メソッドにすればSRP！」

それはただの“細切れ”🍣
変更理由が同じなら、まとめてOKなことも多いよ🙆‍♀️✨

### ❌ 誤解3：「責務＝機能1個」

SRPの責務は「機能の数」より **“変化の単位”**が本体だよ🎯 ([blog.cleancoder.com][1])

---

## 8.4 体験してみよう：SRP違反クラスを“変更理由”で読む👀📌

ここでは、ミニECっぽい「注文確定」処理の“ぐちゃぐちゃ版”を例にするね🛒💥
（わざと密集させるよ😈✨）

```csharp
public class OrderService
{
    public async Task PlaceOrderAsync(OrderRequest request)
    {
        // ①入力チェック（仕様変更されがち）
        if (request.Items.Count == 0) throw new ArgumentException("No items");
        if (request.ShippingAddress is null) throw new ArgumentException("No address");

        // ②割引・税計算（経理・販促で変わりがち）
        decimal subtotal = request.Items.Sum(i => i.UnitPrice * i.Quantity);
        decimal discount = request.CouponCode == "WELCOME10" ? subtotal * 0.10m : 0m;
        decimal tax = (subtotal - discount) * 0.10m;
        decimal total = subtotal - discount + tax;

        // ③支払い（決済会社変更で変わりがち）
        var paymentOk = await FakePaymentGateway.ChargeAsync(request.CardToken, total);
        if (!paymentOk) throw new InvalidOperationException("Payment failed");

        // ④保存（DB都合で変わりがち）
        FakeDb.Orders.Add(new Order { Total = total, CreatedAt = DateTimeOffset.Now });

        // ⑤メール送信（文言・デザイン変更で変わりがち）
        string body = $"Thanks! Total: {total:0.00}";
        FakeEmail.Send(request.Email, "Order Confirmed", body);

        // ⑥ログ（運用・監査で変わりがち）
        Console.WriteLine($"Order placed: {request.Email} total={total:0.00}");
    }
}
```

### ✅ このクラス、変更理由が何個ある？🎯

![code_color_coding](./picture/solid_cs_study_008_code_color_coding.png)

ざっくりでも、もう**5〜6個**あるよね😇💦

* ✅ 入力チェック（ルールが増える）
* ✅ 割引（キャンペーンが増える）
* ✅ 税（税率・端数処理が変わる）
* ✅ 決済（決済会社やAPIが変わる）
* ✅ DB（保存方式が変わる）
* ✅ メール（テンプレ・文言が変わる）
* ✅ ログ（監査要件が変わる）

つまりこの `OrderService` は、**いろんな部署の事情が全部のっかってる**状態👥💥
これが「変更が怖いコード」の代表例だよ〜😵‍💫

---

## 8.5 SRPを見抜くコツ：変更理由の“カード分け”🃏✨

ここからがSRPの本番！🎉
やることはシンプル👇

### Step 1：変更要求を“カード”として書き出す📝💗

例：

* 「クーポン条件を増やして」
* 「税率を変えて」
* 「決済をStripeに変えて」
* 「注文メールをHTMLにして」
* 「ログに注文ID入れて」

### Step 2：“同じ理由で一緒に変わるもの”をグループ化🧺✨

* クーポン条件と割引計算 → 同じグループになりがち🎫
* メール文言とメール件名 → 同じグループになりがち📩
* DB保存とDBスキーマ → 同じグループになりがち🗄️

### Step 3：グループに「名前」を付ける🏷️💡

![grouping_cards](./picture/solid_cs_study_008_grouping_cards.png)

ここが超大事！✨
名前が付く＝責務として独立できる可能性が高いよ😊

例：

* `OrderValidation`
* `Pricing`（割引・税・合計）
* `Payment`
* `OrderRepository`
* `OrderNotification`
* `OrderAuditLog`

この章では、**分ける“判断”ができれば勝ち**🏆✨
（実際の分割のやり方は9章でガッツリやるよ🧹💖）

---

## 8.6 “1つの理由”をもっと上手く言う言い方🎀

![actor_spotlight](./picture/solid_cs_study_008_actor_spotlight.png)

SRPを語るとき便利なテンプレだよ👇✨

* 「このクラスが変わる理由は、**◯◯が変わるとき**です」
* 「このクラスが責任を持つのは、**◯◯という関心事**です」
* 「◯◯の変更は、**△△の担当（アクター）**が決めます」

アクター（誰が変えたいと言うか）で考える説明は、SRPの理解を助けるって話が多いよ👥 ([ウィキペディア][2])

---

## 8.7 SRPチェックリスト✅✨（迷ったらこれ）

* ✅ **変更要求が2種類以上**ある（税とメール、みたいに）
* ✅ その変更要求は、**同じ人/同じ部署が決めてない**
* ✅ 片方の変更のたびに、もう片方のテストも不安になる😇
* ✅ 「そしてついでに…」が増えてきた（危険ワード⚠️）
* ✅ クラス説明が「〜して、〜して、さらに〜する」になってる（盛りすぎ🍰）

---

## 8.8 🤖AI活用（Copilot/Codex系）でSRP感覚を爆速にするプロンプト集✨

そのまま貼って使えるやつ置いとくね📎💕

### ① 変更理由を列挙させる

* 「このクラスが変更される理由を5〜10個、具体例つきで列挙して」

### ② アクター（誰の都合）で分類させる

* 「変更理由を“利害関係者（経理/運用/マーケ等）”ごとに分類して」

### ③ “分ける単位”の候補名を出させる

* 「SRPの観点で責務を分割するとしたら、クラス候補名を10個出して」

### ④ やりすぎ警告もセットで

* 「分割案のうち、やりすぎ（細かすぎ）になりそうな点も指摘して」

※AIは“提案が得意”だけど、最終判断はあなたが握ってOKだよ〜🫶✨

---

## 8.9 ミニクイズ🎯💕

Q1：`OrderService` に「メール文言の変更」と「税率変更」が入ってるのはSRP的にどう？

* A：🟥ダメ（変更理由が別）
* B：🟩OK（どっちも注文処理だから）

✅ 正解：**A**（税とメールはだいたい別アクターで変わる）👥💥

Q2：「クラスが長い＝SRP違反」？
✅ 正解：**必ずしもじゃない**（長い理由が1つならOKな場合もある）😊

---

## 8.10 まとめ🌸✨（次章につながるよ）

* SRPは「1クラス1機能」じゃなくて、**“1クラス1変更理由”**🎯 ([blog.cleancoder.com][1])
* 「誰の都合で変わる？」（アクター）で考えると見抜きやすい👥✨ ([ウィキペディア][2])
* この章では、**分ける境界を言語化できれば勝ち**🏆💕

次の第9章では、SRPの鉄板パターン
**「入力・判断・出力を分ける（I/Oとロジック分離）」**を、実際にリファクタしていくよ〜📥🧠📤✨

[1]: https://blog.cleancoder.com/uncle-bob/2014/05/08/SingleReponsibilityPrinciple.html?utm_source=chatgpt.com "The Single Responsibility Principle - Clean Coder Blog"
[2]: https://en.wikipedia.org/wiki/Single-responsibility_principle?utm_source=chatgpt.com "Single-responsibility principle"
