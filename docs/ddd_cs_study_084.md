# 第84章：スモールスタートの極意 🎈✨

**〜最初から完璧な集約を作ろうとしない〜**

## この章でできるようになること 🎯

* 「集約ってどこまで作ればいいの？」の迷いを減らす 🙆‍♀️
* 最小の集約（最初の1歩）をサクッと作れる 🧩
* 仕様が増えたら、集約を“育てる”感覚で拡張できる 🌱
* AI（Copilot/Codex）に**暴走させず**に手伝ってもらえる 🤝🤖

![Small Start Concept](./picture/ddd_cs_study_084_small_start.png)

---

## なんで「最初から完璧な集約」は危ないの？⚠️😵

DDDを始めた人がハマりがちな罠がこれ👇

* 仕様がまだ固まってないのに、将来を全部想像して作る 🧙‍♂️💭
* 「たぶん必要」なルールを先に入れて、後で変更地獄 🔥
* 何が重要な不変条件（絶対守りたいルール）か分からず、全部盛り 🍱
* AIに「全部入りで作って」と頼むと、それっぽい巨大設計が出てくる 🐘📦（そしてしんどい）

✅ 結論：**最初は“完璧”より“通る”が正義**です 🚀

---

## スモールスタートの3原則 🌟

### ① まず「1ユースケース」だけ通す 🛣️

最初はこれだけでOK👇

* 作成する
* 追加する
* 確定する

「配送」「割引」「キャンセル」「在庫引当」…は後で！😆

### ② 不変条件は“最小”にする 🔒

最初に入れる不変条件は、**今この瞬間に絶対必要**なものだけ✅
（例：数量は1以上、確定後は変更不可）

### ③ 集約は“育てる”もの 🌱

集約は最初から完成品じゃなくてOK。
動く → ルール増える → テスト足す → モデル育つ、で正解です 🧪✨

---

## 集約の「成長ステップ」イメージ 🪜
 
 集約を最初から100点にしないために、こう育てるのがおすすめ👇
 
 ```mermaid
 flowchart LR
     v1((v1<br/>最小通過)) --> v2((v2<br/>ルール追加))
     v2 --> v3((v3<br/>VO化))
     v3 --> v4((v4<br/>分割))
     
     subgraph S1 [Step 1: 最小]
       direction TB
       Draft[下書き] --> Confirmed[確定]
     end
     
     subgraph S2 [Step 2: 守る]
       direction TB
       Rule1[変更禁止]
       Rule2[個数制限]
     end
     
     v1 -.-> S1
     v2 -.-> S2
     
     style v1 fill:#caffbf,stroke:#383,stroke-width:2px
     style v4 fill:#ffdfba,stroke:#f80,stroke-width:2px
 ```
 
 * **Step0**：まず手続きでもいい（雑でも通す）🏃‍♀️💨
 * **Step1**：最小の集約（ルート + 最低限の状態と操作）🧩
* **Step2**：値オブジェクトを足す（Money/Email/ProductIdなど）💎
* **Step3**：永続化（Repository）とアプリ層（UseCase）につなぐ 🗃️
* **Step4**：必要なら分割（集約がデブったらダイエット）🏋️‍♀️

この章は **Step1** が主役です 😊🎉

---

## 例：注文（Order）をスモールスタートで作る 🛒✨

最初の目標はこれだけ👇

* 注文を作る
* 商品を追加する
* 注文を確定する
* 確定後は追加できない（最小の不変条件）

### v1：最小の集約（まずこれでOK）🧩

```csharp
namespace Shop.Domain.Orders;

public enum OrderStatus
{
    Draft,
    Confirmed
}

public readonly record struct OrderId(Guid Value)
{
    public static OrderId New() => new(Guid.NewGuid());
}

public readonly record struct ProductId(Guid Value);

public sealed class Order
{
    private readonly List<OrderItem> _items = new();

    public OrderId Id { get; }
    public OrderStatus Status { get; private set; } = OrderStatus.Draft;

    public IReadOnlyList<OrderItem> Items => _items;

    private Order(OrderId id)
    {
        Id = id;
    }

    public static Order Create()
        => new(OrderId.New());

    public void AddItem(ProductId productId, int quantity)
    {
        if (Status != OrderStatus.Draft)
            throw new InvalidOperationException("確定後の注文は変更できません。");

        if (quantity <= 0)
            throw new ArgumentOutOfRangeException(nameof(quantity), "数量は1以上です。");

        _items.Add(new OrderItem(productId, quantity));
    }

    public void Confirm()
    {
        if (Status != OrderStatus.Draft)
            throw new InvalidOperationException("すでに確定済みです。");

        if (_items.Count == 0)
            throw new InvalidOperationException("商品が1つもない注文は確定できません。");

        Status = OrderStatus.Confirmed;
    }
}

public sealed record OrderItem(ProductId ProductId, int Quantity);
```

### ここがポイントだよ 💡😊

* **“Draft（下書き）”か“Confirmed（確定）”か**だけ持つ（最小！）✍️✅
* ルールは今必要なものだけ（確定後は追加できない、数量は1以上、空注文は確定不可）🔒
* まだ「金額」「割引」「在庫」「配送先」…何も入れてない！でもOK！🎉

---

## 「完璧をやめる」ためのチェックリスト ✅📝

集約を作ってるときに、これを自分に聞いてみてね👇

* それ、**今日のユースケース**で必要？🤔
* そのルール、**今決まってる？**（仮なら後回しでOK）🌀
* その責務、**別の集約**になりそう？（迷うなら入れない）🚪
* それ入れると、AIが理解する範囲を超えない？（デブ化注意）🐷💦

---

## 仕様が増えたらどうする？「育て方」🌱✨

例えば「同じ商品は1行にまとめたい」が来たら…

* v1：そのまま追加（同じ商品が複数行になってもOK）
* v2：仕様が固まったら、`AddItem`を変更してまとめる
* v2以降：テストを足して守る 🧪🛡️

**“必要になった瞬間に、必要な分だけ”**でいいんです 🙆‍♀️💕

---

## ミニテスト（最小の安心）🧪✨

「確定後に追加できない」を守りたいなら、テスト1本でOK👍

```csharp
using Shop.Domain.Orders;
using Xunit;

public class OrderTests
{
    [Fact]
    public void ConfirmedOrder_CannotAddItem()
    {
        var order = Order.Create();
        order.AddItem(new ProductId(Guid.NewGuid()), 1);
        order.Confirm();

        Assert.Throws<InvalidOperationException>(() =>
            order.AddItem(new ProductId(Guid.NewGuid()), 1));
    }
}
```

テストは最初から大量にいらないよ〜！
**「壊れたら困る最小ルール」だけ**で十分 🧸🛡️

---

## AIに頼むときの“ちょうどいい”頼み方 🤖🗣️✨

AIには「全部やって」じゃなくて、こう頼むのがコツ👇

### ✅ プロンプト例（コピペOK）📋

* 「注文の集約を最小で作りたい。ユースケースは *作成/追加/確定* だけ。**最小の不変条件**を3つまでに絞って提案して」
* 「今の `Order` が太りそう。**次に増えそうな仕様**を想像して、拡張ポイントをコメントで入れて」
* 「この集約のテスト、**最小で3本**だけ作るなら何が良い？」
* 「“まだ入れない方がいい責務”を列挙して、理由も一言で」

💡AIに“制限”を渡すと、暴走しにくくなります 😆🧯

---

## よくある失敗あるある 😭➡️😄

* ❌ 「将来のために割引も配送も在庫も全部 Order に入れた」
  ✅ → “今のユースケースだけ”に絞って、増えたら育てる 🌱
* ❌ 「集約の境界が分からないから、とりあえず巨大クラス」
  ✅ → まず最小で作って、**太ったら分ける**でOK 🐘➡️🪓
* ❌ 「正しいDDDが分からないから進めない」
  ✅ → 正しさより、**変更できる形**が大事 💃✨

---

## 【演習】あなたの題材でスモールスタートしてみよう 🎓💖

次のどれかを選んで、**“作成/追加/確定”**に当てはめてみてね👇（1つでOK）

* 🗓️ 予約（予約を作る→時間を追加→確定）
* 🎮 ゲームの装備セット（セット作る→装備追加→確定）
* 📝 タスク管理（リスト作る→タスク追加→確定）
* 🏯 戦国武将図鑑（リスト作る→武将追加→公開確定）✨

やることはこれだけ👇

1. 状態（Draft/Confirmed）を決める
2. 追加メソッドを1つ作る
3. 確定メソッドを1つ作る
4. 不変条件を2〜3個だけ入れる

できたらもう勝ちです 🎉🎉🎉

---

## まとめ 🎀

* 集約は**最初から完璧にしない**でOK 🙆‍♀️✨
* まずは **1ユースケース**だけ通す 🛣️
* 不変条件は **最小**、増えたら **育てる** 🌱
* AIには「制限付き」で頼むと超うまくいく 🤖💕

次の章が「マイクロサービスは1人開発には毒か？」だから、
この章の“スモールスタート”がめっちゃ効いてくるよ〜！😆🚀
