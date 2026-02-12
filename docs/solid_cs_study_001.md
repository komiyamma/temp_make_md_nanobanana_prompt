# 第01章：ようこそSOLID！なにが嬉しいの？🎀

## この章のゴール🎯💖

この章が終わったら、こんな状態になってたらOKです😊

* 「SOLIDって、結局なにが嬉しいの？」を自分の言葉で言える🗣️✨
* 「変更が怖いコード」って何が起きてるか、だいたい説明できる😵‍💫➡️😌
* 次章以降でやる改善（リファクタ）の“目的地”がイメージできる🗺️💡
* AI（Copilot/Codex系）を「設計の相談相手」として使うコツがわかる🤖💞

---

## SOLIDが欲しくなる瞬間（あるあるドラマ）🎬😇

想像してみてね🫶✨

あなた：「注文の決済に *Apple Pay* を追加して〜！」
先輩：「OK！CheckoutServiceの `if` 増やしとくね〜！」
…数時間後🕒
先輩：「あれ？送料の計算が壊れた…😨」
あなた：「え、決済追加しただけなのに…？😭」

これが **“変更が怖い”** の正体あるあるです💥

* 1か所直したつもりが、別の場所が壊れる😱
* どこに影響が出るか読めない🌀
* 修正が増えるほど、触るのが怖くなる🫠

SOLIDは、こういう状況を **「起きにくくするための考え方セット」** だよ〜🧰✨

---

## なぜ「単一責任」なの？ (Why)
![Responsibility Overload](./picture/solid_cs_study_001_responsibility_overload.png)
## SOLIDってなに？（超ざっくり5行で）🧩🌈

SOLIDは、オブジェクト指向設計の基本指針（5つ）だよ😊
（元ネタは Robert C. Martin の設計原則の文脈で、後に “SOLID” として広まった、という説明が一般的です📚）([Baeldung on Kotlin][1])

* **S**：1つのクラスに「いろいろ詰め込みすぎ」ない📌
* **O**：追加に強く、既存コードを壊しにくく🚪✨
* **L**：継承で「入れ替えたら壊れる」を防ぐ🧱
* **I**：使わない機能まで押し付けない✂️
* **D**：大事なロジックを、細かい実装の都合から守る🛡️

まだ暗記しなくてOKだよ〜！🙆‍♀️💕
この章は「まず嬉しさを体感する」がテーマ🎀

---

## “変更が怖い”の正体はだいたいこれ😵‍💫🔍

![変更が怖い vs SOLID](./picture/solid_cs_study_001_fear_of_change.png)

設計が崩れてるコードって、多くの場合こうなってるよ👇

### ① 1つのクラスに責務が混ざってる🧺💥

* 入力チェック
* 計算
* DB保存
* 外部API呼び出し
* メール送信
  ぜんぶ1クラスに入ってる、みたいなやつ😇

### ② 影響の波が読めない🌊😱

Aを直したら、BとCも変えないといけない
でもBとCがどこにあるか分からない…🫥

### ③ “追加”のたびに“修正”が増える🧨

機能が増えるほど、既存コードを毎回いじる必要が出る
→ バグの確率が上がる📈💦

SOLIDは、この3つを減らす方向に効いてきます🧼✨

---

## ミニ体験：1クラスに詰め込むとどうなる？🧱😈

まずは「よくある地獄」を、軽く見てみよ〜😂
（※わざと雑です！安心してね💞）

```csharp
public class CheckoutService
{
    public async Task<string> CheckoutAsync(Order order, string paymentType)
    {
        // 1) Validate
        if (order.Items.Count == 0) throw new InvalidOperationException("Empty order");
        if (order.Total <= 0) throw new InvalidOperationException("Total must be > 0");

        // 2) Discount rules (とりあえずの特別ルール)
        if (order.CustomerRank == "Gold") order.Total *= 0.9m;

        // 3) Payment（増え続ける if）
        if (paymentType == "Card") { /* call card API */ }
        else if (paymentType == "PayPay") { /* call paypay API */ }
        else throw new NotSupportedException(paymentType);

        // 4) Shipping fee
        if (order.DestinationPref == "Okinawa") order.ShippingFee = 1200;
        else order.ShippingFee = 600;

        // 5) Save to DB
        await _db.Save(order);

        // 6) Send email
        await _email.SendAsync(order.CustomerEmail, "Thanks!");

        return "OK";
    }

    private readonly OrderDb _db = new();
    private readonly EmailSender _email = new();
}
```

この `CheckoutService`、ぱっと見でも「やってること多すぎ」だよね😂💦
しかも `new` で中で作っちゃってるから、差し替えもしにくい😵‍💫

---

## ワーク：仕様変更カード🃏✨（いまのコードだとどこが怖い？）

次の“変更”が来たとき、どこを直すか想像してみてね😊
（紙でもメモ帳でもOKだよ📝💕）

### カードA：決済方法を追加したい💳➕🍎

* Apple Pay を追加
* ついでに「決済失敗時のログ」も欲しい

👉 どこを触る？何が壊れそう？😨

### カードB：割引ルールが増えた🎫✨

* 学割10%
* ゴールド会員は送料も無料にしたい

👉 どこに書く？順番は？テストは？🧪

### カードC：メール仕様が変わった📩💌

* 文面をテンプレート化したい
* 注文完了以外に「発送通知」も送りたい

👉 Checkoutの中に足す？別の場所？🤔

**ポイントはこれ👇**

> 「変更が来たとき、1か所直すだけで済みそう？」
> 「それとも、同じクラスを毎回いじる感じ？」😵‍💫

この“毎回いじる”が増えるほど、怖くなるんだよ〜😭

---

## “変更が怖くないコード”ってどんな状態？✅💖

この教材で目指すイメージはこんな感じ✨

* 決済手段を増やす → **新しいクラスを追加するだけ**（既存は触らない/最小）🧩
* 送料計算を変える → **送料の担当だけ**直す📦
* メール文面変更 → **メールの担当だけ**直す📩
* そしてテストが守ってくれる🧪🛡️

つまり、変更が「局所化」してる状態だよ😊✨
SOLIDは、その“局所化”を作るためのガイドになってくれます🗺️💕

---

## 🤖AI（Copilot/Codex系）を「設計の相談相手」にするコツ💞

AIは、いきなり「正解コード」を出させるより、**整理役**にすると超強いよ〜！💪✨
この章は特に「言語化」を手伝わせるのが最強🤖📝

### 使えるプロンプト例（コピペOK）📋✨

* 「この `CheckoutService` の“責務（変更理由）”を思いつく限り列挙して」
* 「仕様変更：Apple Pay追加。影響箇所と壊れやすい理由を説明して」
* 「このクラスを分割するとしたら、分割単位の候補名を10個出して」
* 「ここにテストが無いと怖い点を5つ挙げて（観点だけでOK）」

### AIと組むときの注意⚠️😌

* AIの案は“下書き”📝（そのまま採用しない）
* **「変更理由が混ざってない？」** を必ずチェック👀
* 後の章でテストを書いて「壊してない」を確認するのが本筋🧪✨

---

## ちょいメモ：2026の“今どきC#”感だけ🌸

いまのC#は **C# 14** が最新で、**.NET 10** 上で使うのが前提だよ〜📌([Microsoft Learn][2])
あと **Visual Studio 2026** は .NET 10 SDK を含む形で案内されてるよ🧰✨([Microsoft Learn][2])

（この章はセットアップしないけど、「ちゃんと最新で進むよ」って安心材料ね😊💞）

---

## この章のまとめ🎀✨

* SOLIDは「変更が怖い」を減らすための考え方セット🧰
* 怖さの原因は、だいたい **責務の混在** と **影響範囲の不明** 😵‍💫
* まずは“痛み”を言語化できると、次の章から改善が気持ちよくなる🧹✨
* AIは「責務の棚卸し」「変更の影響予測」に使うと超頼れる🤖💞

---

## チェックリスト✅💕（できたら最高！）

* [ ] “変更が怖い”理由を、3つ以上言葉にできた🗣️✨
* [ ] `CheckoutService` がやってることを、5個以上列挙できた🧾
* [ ] 仕様変更カードA〜Cの「影響箇所」をざっくり想像できた🧠💡
* [ ] AIに「責務（変更理由）」を出させて、読んで納得できた🤖✅

---

次は第2章で、サクッと環境を整えて「いつでも実験できる作業場」を作るよ〜🧰🪄💕

[1]: https://www.baeldung.com/solid-principles?utm_source=chatgpt.com "A Solid Guide to SOLID Principles"
[2]: https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-14?utm_source=chatgpt.com "What's new in C# 14"
