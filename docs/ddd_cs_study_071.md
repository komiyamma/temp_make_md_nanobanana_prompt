# 第71章：ユニットテストの戦略 🎯🧪

〜どこを重点的にテストし、どこをAIに任せる？🤖✨〜

DDDを始めたばかりの人がいちばん困るのが、これ👇
**「テスト、どこまで書けばいいの？」** 😵‍💫

全部テストしようとすると疲れて止まるし、
テストしないと後で自分が泣くし…😭💥

この章では、**1人開発×DDD×AI前提**で、迷わないための“テストの地図”を作ります🗺️✨

---

## 今日のゴール 🏁✨

読み終わったら、これができるようになります👇

* ✅ **どこをユニットテストで固めるべきか**が分かる
* ✅ **AIに任せていいテスト／任せちゃダメなテスト**が分かる
* ✅ DDDの「Domain / Application / Infrastructure」で、**テストの優先順位**が決められる

![Unit Test Strategy](./picture/ddd_cs_study_071_unit_test.png)

---

## 1) ユニットテストってなに？🧪

ユニットテストは超シンプルに言うと、

**「小さい部品が、約束どおり動くかを確認するテスト」**です😊

DDDだと「小さい部品」って、だいたいこれ👇

* 値オブジェクト（Money, Emailなど）💰📧
* エンティティ／集約のルール（Orderはマイナス数量ダメ等）🧺
* ドメインサービス（割引計算、判定など）🧠

そして重要ポイントはこれ👇
**ユニットテストは “速い・軽い・いつでも回せる” のが命**⚡️

---

## 2) 1人開発×DDDの「テスト優先順位」🏆
 
 ここが今日の本題です😊✨
 DDDの構造（Domain / Application / Infrastructure / Web）で、優先順位をこうします👇
 
 ```mermaid
 block-beta
   columns 1
   block:Domain ["🥇 Domain (最優先)"]
     style Domain fill:#ffdfba,stroke:#f80,stroke-width:2px
   end
   block:Application ["🥈 Application (要所だけ)"]
     style Application fill:#ffffba,stroke:#aa0,stroke-width:2px
   end
   block:Infra ["🥉 Infra / Web (統合テストでカバー)"]
     style Infra fill:#bae1ff,stroke:#00a,stroke-width:2px
   end
 ```
 
 ### 🥇最優先：Domain（ドメイン層）🛡️✨

**ここはガチで固める価値が最大**です💪🔥
理由はカンタンで、ここが壊れると「仕様そのもの」が壊れるから😇

**Domainで特にテストすべきもの**👇

* 値オブジェクトのバリデーション（不正値が生まれない）🚫
* 集約の不変条件（在庫マイナス禁止、注文の状態遷移など）🔒
* ドメインサービスの計算（割引、料金、判定）🧾

👉 ここを守ると、AIにコードを増やさせても崩れにくいです🤖🧱✨

---

### 🥈次点：Application（ユースケース層）🎬

Applicationは「手続きの流れ」なので、
**“重要な分岐だけ” テスト**がちょうどいいです🙂

例👇

* 登録できる／できない（バリデーション失敗時の戻り）✅❌
* 決済成功時に注文確定、失敗時は確定しない 💳
* 重要な外部連携の結果で分岐するところ 🌐

💡Applicationはテストしすぎると「実装の細部に依存」してツラくなりがち😭

---

### 🥉ほどほど：Infrastructure（DB/外部API）🧰

ここはユニットテストより、**統合テスト（Integration Test）**が向いてます🧪✨

* EF Coreのマッピングが正しいか
* リポジトリが保存／取得できるか
* 外部APIの変換（ACL）が期待通りか

全部を細かくユニットテストしようとすると、モック地獄になりやすいです😵‍💫（次章で扱うやつ！）

---

### 🧁最後にちょびっと：Web/UI（画面）🖥️

UIはE2EテストをちょびっとでOK👌✨
1人開発なら「大事な導線だけ」守れば十分なことが多いです😊

---

## 3) AIに任せていいところ／ダメなところ 🤖✅❌

### ✅ AIに任せていい（むしろ任せてラク！）✨

* テストの雛形（xUnitの形、AAAの枠）🧱
* データパターンの列挙（TheoryのInlineData）📚
* “境界値っぽい候補”を出させる（0、最大、空文字など）🎯
* テストデータBuilderの作成（読みやすくする道具）🧰
* 失敗ケースの洗い出し（ただし採用は人間が判断！）👀

### ❌ AIに任せちゃダメ（ここが設計者の仕事）🧠🔥

* **何が仕様として正しいか**の判断
* **本当に守りたい不変条件**の選定
* 「この条件はテスト必須」みたいな**優先順位づけ**
* テストが通るように仕様を変える（AIがやりがち🤣）

👉 AIは“テストを書く”のは得意。でも“守るべきルールを決める”のは人間の役目💪✨

---

## 4) まずは超定番：Value Object をテストしよう 💰🧪

例として Money を使います😊
「不正な金額は生まれない」「計算が正しい」を守りたい！

### Money（例）

```csharp
public sealed record Money
{
    public decimal Amount { get; }

    public Money(decimal amount)
    {
        if (amount < 0) throw new ArgumentOutOfRangeException(nameof(amount), "金額は0以上だよ🙅‍♀️");
        Amount = amount;
    }

    public Money Add(Money other) => new(Amount + other.Amount);

    public Money Subtract(Money other)
    {
        if (Amount - other.Amount < 0) throw new InvalidOperationException("マイナス残高はダメ🙅‍♀️");
        return new Money(Amount - other.Amount);
    }
}
```

### ✅ テスト（xUnit例）

```csharp
using FluentAssertions;
using Xunit;

public class MoneyTests
{
    [Fact]
    public void Ctor_Amountがマイナスなら例外()
    {
        var act = () => new Money(-1m);
        act.Should().Throw<ArgumentOutOfRangeException>();
    }

    [Fact]
    public void Add_足し算できる()
    {
        var a = new Money(100m);
        var b = new Money(50m);

        var result = a.Add(b);

        result.Amount.Should().Be(150m);
    }

    [Fact]
    public void Subtract_引き算でマイナスになるなら例外()
    {
        var a = new Money(10m);
        var b = new Money(20m);

        var act = () => a.Subtract(b);

        act.Should().Throw<InvalidOperationException>();
    }
}
```

💡ポイント✨

* **“仕様”をテストしてる**（内部実装をテストしてない）
* Moneyが守るべきルールが、テスト名から読み取れる📖😊

---

## 5) 集約（Aggregate）で「ルールの守り」をテストする 🧺🔒

DDDで本当においしいのはここ😍
**「集約がルールを破らない」**をテストで固定します🧱✨

例：Order が「数量は1以上じゃないとダメ」みたいなルールを持つとします。

```csharp
public sealed class Order
{
    private readonly List<OrderItem> _items = new();
    public IReadOnlyList<OrderItem> Items => _items;

    public void AddItem(string productId, int quantity)
    {
        if (quantity <= 0) throw new ArgumentOutOfRangeException(nameof(quantity), "数量は1以上だよ🙅‍♀️");
        _items.Add(new OrderItem(productId, quantity));
    }
}

public sealed record OrderItem(string ProductId, int Quantity);
```

テスト👇

```csharp
using FluentAssertions;
using Xunit;

public class OrderTests
{
    [Fact]
    public void AddItem_数量が0以下なら例外()
    {
        var order = new Order();

        var act = () => order.AddItem("P001", 0);

        act.Should().Throw<ArgumentOutOfRangeException>();
    }

    [Fact]
    public void AddItem_正常なら明細が増える()
    {
        var order = new Order();

        order.AddItem("P001", 2);

        order.Items.Should().HaveCount(1);
        order.Items[0].ProductId.Should().Be("P001");
        order.Items[0].Quantity.Should().Be(2);
    }
}
```

✅ これだけでも「集約が守るべきルール」が固定されるので、未来の自分が助かります😭✨

---

## 6) テストが迷子にならない “3つの合言葉” 🧭✨

### 合言葉①：**「壊れたら困る順」**で書く 🥺

* 壊れたら売上に直撃 → 最優先💥
* 壊れたら一部の画面だけ → 後回し🙂
* 壊れてもすぐ直せる → さらに後🙂

### 合言葉②：**「実装」じゃなくて「ふるまい」をテスト**👀

* ❌ privateメソッドの中身を当てる
* ✅ 入力→出力、ルールが守られること

### 合言葉③：**「軽いテストを増やす」**⚡️

遅いテストが多いと、だんだん回さなくなる→崩壊😇

---

## 7) AIに投げるプロンプトテンプレ（コピペOK）🤖📝

AIにテストを書かせるときは、これが超効きます👇

**テンプレ**（そのまま使ってOK）✨

```text
次のC#コードに対して、xUnit + FluentAssertionsでユニットテストを書いてください。

- 目的：仕様（ビジネスルール）を守るテストにする
- 実装の詳細に依存しない
- 正常系と異常系を最低3本ずつ
- テスト名は「メソッド_条件_期待結果」の形式
- 追加で「見落としやすい境界値」も提案して
コード：
（ここに貼る）
```

💡AIが出したテストは、**「それ本当に仕様？」**って目でチェックして採用するのがコツです👀✨

---

## 8) ミニ演習（10〜20分）📝✨

次の3つ、ユニットテストを書いてみてください😊🧪

1. Money：`new Money(0)` は作れる ✅
2. Order：`AddItem("P001", -1)` は例外 ❌
3. Order：`AddItem` を2回呼ぶと Items が2件 ✅

書けたら、AIにこう聞いてみてね👇

* 「このテスト、仕様テストになってる？」🤔
* 「実装依存になってるところある？」👀
* 「見落としそうなケースある？」🧠

---

## まとめ 🎁✨

* **Domainをユニットテストでガチ固め**🛡️
* Applicationは「重要分岐だけ」🎬
* Infrastructureは「統合テスト寄り」🧰
* AIには **雛形・パターン列挙を任せる**🤖
* でも **守るべきルールを決めるのは人間**💪✨

---

次の第72章では、いよいよ **モック（Moq / NSubstitute）**で
「1人でも偽物を作って爆速開発」する話に入ります🧪🚀✨
