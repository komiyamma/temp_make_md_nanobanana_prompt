# 第53章：C# の型システムでビジネスルールを表現する🧠✨ 〜「if地獄」を型で消す〜

![C# の型システムでビジネスルールを表現する](./picture/ddd_cs_study_053_type_rules.png)

「ルールが増えるほど if が増える…😵‍💫」
これ、1人開発だと**未来の自分が一番つらい**やつです💥

この章では、C#の「型」の力を使って、**if を減らして、間違いにくいコード**にしていきます💪😊
キーワードはこれ👇

✅ **ありえない状態を“型で表現できない”ようにする**（＝コンパイル時に守られる）
✅ **分岐ではなく“振る舞い”を型に持たせる**

---

## 今日のゴール🎯✨

* 「if を書かないと守れないルール」を、**型に閉じ込める**感覚がわかる😊
* “不正な状態”を**作れない設計**を作れるようになる💎
* AIにコード生成させても、**型がガードして暴走しにくい**形にできる🤖🛡️

---

## 1. まずは「if地獄」例😇➡️😱

例：会員ランクで割引が変わる、よくあるやつ🎫✨

```csharp
public decimal CalcPrice(decimal basePrice, string memberRank, bool hasCoupon)
{
    if (memberRank == "Gold")
    {
        basePrice *= 0.9m;
    }
    else if (memberRank == "Silver")
    {
        basePrice *= 0.95m;
    }

    if (hasCoupon)
    {
        basePrice -= 500;
    }

    if (basePrice < 0)
    {
        basePrice = 0;
    }

    return basePrice;
}
```

問題点あるある😭👇

* 「Gold」「Silver」みたいな文字列が散らばる🌀
* ルール追加で if が増殖🌱🌱🌱
* AIにちょっと改変させると、どこかの if を破壊しがち💥🤖

---

## 2. 発想転換💡「分岐」をやめて「型」にルールを持たせる✨

### 2-1. 文字列（rank）をやめて「会員ランク型」にする👑

「Gold」って文字列、ミスり放題です😇（"GOLD" とか "gold" とか…）

だから、**会員ランクを“型の世界”に引き上げる**✨

```csharp
public abstract record MemberRank
{
    public abstract decimal ApplyDiscount(decimal price);

    public sealed record Gold : MemberRank
    {
        public override decimal ApplyDiscount(decimal price) => price * 0.9m;
    }

    public sealed record Silver : MemberRank
    {
        public override decimal ApplyDiscount(decimal price) => price * 0.95m;
    }

    public sealed record Normal : MemberRank
    {
        public override decimal ApplyDiscount(decimal price) => price;
    }
}
```

こうすると、計算側はこう書けます😊

```csharp
public decimal CalcPrice(decimal basePrice, MemberRank rank, bool hasCoupon)
{
    var price = rank.ApplyDiscount(basePrice);

    if (hasCoupon)
    {
        price -= 500;
    }

    return price < 0 ? 0 : price;
}
```

ここで起きた変化✨👇

* 「ランクによる分岐」が消えた🎉
* ランク追加は **型を追加するだけ**（計算側は触らない）🧩
* AIが勝手に if を増やしにくい（型の形が道になる）🤖🧭
 
 ```mermaid
 classDiagram
    class MemberRank {
        <<abstract>>
        +ApplyDiscount(price)
    }
    class Gold {
        +ApplyDiscount(price) : 10% OFF
    }
    class Silver {
        +ApplyDiscount(price) : 5% OFF
    }
    class Normal {
        +ApplyDiscount(price) : No Discount
    }
    
    MemberRank <|-- Gold
    MemberRank <|-- Silver
    MemberRank <|-- Normal
    
    note for MemberRank "if文の代わりに<br/>この型を使う！✨"
 ```
 
 ---

## 3. 「クーポン有り/無し」を bool で持つのをやめる🎫➡️🧱

bool も地味に危険です😵‍💫

* true が何を意味するのか読み手が迷う
* 条件が増えると bool が増殖して崩壊💥（isVip, isCampaign, isNewUser…）

なので、**クーポンも型にします**✨

```csharp
public abstract record Coupon
{
    public abstract decimal Apply(decimal price);

    public sealed record None : Coupon
    {
        public override decimal Apply(decimal price) => price;
    }

    public sealed record FixedDiscount(decimal Amount) : Coupon
    {
        public override decimal Apply(decimal price) => price - Amount;
    }
}
```

計算はこう👀

```csharp
public decimal CalcPrice(decimal basePrice, MemberRank rank, Coupon coupon)
{
    var price = rank.ApplyDiscount(basePrice);
    price = coupon.Apply(price);

    return price < 0 ? 0 : price;
}
```

これで「クーポンありなら〜」の if が消えました🎉🎉
しかも将来「%割引クーポン」も簡単に追加できます💪✨

---

## 4. 「ありえない状態」を型で作れないようにする🛡️✨

ここがDDDっぽい気持ちよさです💎
たとえば「価格はマイナスになってはいけない」なら…

### 4-1. Money（お金）型に“マイナス禁止”を閉じ込める💰🚫

```csharp
public readonly record struct Money
{
    public decimal Value { get; }

    private Money(decimal value)
    {
        Value = value;
    }

    public static bool TryCreate(decimal value, out Money money)
    {
        if (value < 0)
        {
            money = default;
            return false;
        }

        money = new Money(value);
        return true;
    }

    public Money Subtract(Money other)
    {
        var v = Value - other.Value;
        return v < 0 ? new Money(0) : new Money(v);
    }

    public Money Multiply(decimal rate)
        => new Money(Value * rate);
}
```

こうすると、**「マイナスチェック」が各所に散らばらない**です😊✨
（ルールは Money 型の中で一生守られる🛡️）

---

## 5. 「状態」を型で表すと、禁止ルールが自然に守れる📦➡️🚦

たとえば注文📦

* 下書き（Draft）では発送できない🚫
* 支払い済み（Paid）なら発送できる✅

これを if で書くと増殖します😇
そこで「注文の状態」を型にします✨

```csharp
public abstract record OrderState
{
    public sealed record Draft : OrderState;
    public sealed record Paid : OrderState;
    public sealed record Shipped : OrderState;
}

public sealed class Order
{
    public OrderState State { get; private set; } = new OrderState.Draft();

    public void Pay()
    {
        State = State switch
        {
            OrderState.Draft => new OrderState.Paid(),
            _ => throw new InvalidOperationException("この状態では支払いできません")
        };
    }

    public void Ship()
    {
        State = State switch
        {
            OrderState.Paid => new OrderState.Shipped(),
            _ => throw new InvalidOperationException("この状態では発送できません")
        };
    }
}
```

これ、switch は残ってるけどポイントはここ👇
✅ 「状態の種類」が型として固定される
✅ 追加・変更があったら、コンパイラが教えてくれる（分岐漏れが見つかる）✨

---

## 6. どこまでやる？やりすぎ防止ライン⚖️😊

型で全部やると、逆に重くなります😵‍💫
初心者のうちは、この基準がちょうどいいです👇

### 型で表現すると強いもの💪✨

* **ID**（UserId みたいに混ぜたら事故るやつ）🪪
* **金額 / 日付 / メール**（ルールがある値）💰📅📧
* **状態**（下書き/確定/完了…）🚦
* **区分**（会員ランク、支払い方法、配送種別…）🏷️

### まだ if でOKなもの👌

* UIのちょい分岐（表示/非表示）🖥️
* その場限りの単純条件（1回しか出ない）🍀

---

## 7. 【ミニ演習】if を 2個、型で消してみよう🧪✨

次の if を消すチャレンジ🔥

```csharp
public decimal Calc(decimal price, string rank)
{
    if (rank == "Gold") return price * 0.9m;
    if (rank == "Silver") return price * 0.95m;
    return price;
}
```

やること👇

1. **MemberRank 型**を作る（Gold/Silver/Normal）👑
2. **ApplyDiscount** を持たせる✨
3. Calc から if を消す🎉

---

## 8. AIに頼むときの「勝ちプロンプト」例🤖✨

### 8-1. 仕様から型を提案させる🧠

「会員ランクは Gold/Silver/Normal。割引率は 10%/5%/なし。
文字列比較は禁止。record ベースの型で、割引計算をランク型に持たせて。」

### 8-2. “ありえない状態”洗い出し🛡️

「この機能で “本来ありえない状態” を列挙して。
それを C# の型で表現して、作れないようにする案を出して。」

### 8-3. 実装後のチェック✅

「if が増えすぎていないかレビューして。
分岐が増えそうな場所を“型に押し込める”案を3つ出して。」

---

## まとめ🎀✨（今日の持ち帰り）

* if を減らすコツは、「条件」を消すんじゃなくて **条件の居場所を変える**こと🏠✨
* **文字列・bool** はルールが増えるとすぐ崩れる😵‍💫
* “会員ランク”“クーポン”“状態”みたいなものは、**型にすると一気に安全**🛡️💎
* AI時代は特に、**型がガードレール**になってくれる🚧🤖✨

---

次の章（第54章）では、この「DDDのパーツ」をAIに安定して作らせるための**指示テンプレ**に進みますよ〜📣😊✨
