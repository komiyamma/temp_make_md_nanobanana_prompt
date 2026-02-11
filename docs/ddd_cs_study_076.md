# 第76章：トランザクションスクリプト 🧾⚡（いちばん速い「手順書」設計）

DDDを学び始めると、**値オブジェクト！集約！ドメインイベント！**ってワードがどんどん増えて、ちょっと疲れますよね🥺💦
そこで今回は、DDDが重く感じたときの“逃げ道”として超重要な **トランザクションスクリプト** を扱います✨
これは悪者じゃなくて、**「最短で動くものを作る」ための正当な武器**です🗡️😎

---

## 1. トランザクションスクリプトって何？🤔

![ddd_cs_study_076_recipe_card](./picture/ddd_cs_study_076_recipe_card.png)

ひとことで言うと…

> **「1ユースケース = 1つの手順書（メソッド）」**で、上から下へ順番に処理を書くスタイル
 
 たとえば「注文する」「ユーザー登録する」「在庫を減らす」みたいな、**“やりたいこと単位”**でメソッドが存在して、その中で：
 
 ```mermaid
 flowchart TD
     Start([開始]) --> Input[1. 入力チェック]
     Input --> Load[2. データ取得]
     Load --> Logic[3. ロジック判定]
     Logic --> Update[4. 更新処理]
     Update --> Save[5. 保存]
     Save --> Return([終了])
     
     style Start fill:#eee,stroke:#333
     style Return fill:#eee,stroke:#333
     style Logic fill:#ffebd0,stroke:#f80
 ```
 
 * 入力チェック✅
 * DBから取得📥
* 条件分岐🔀
* 更新📤
* 保存💾
* 返す🎁

…を **ぜんぶ順番に書きます**。

DDDっぽく言うと、ドメインモデルを育てる前の段階で、**アプリケーションサービスが主役**になります👑✨

![Transaction Script List](./picture/ddd_cs_study_076_transaction_script_list.png)

---

## 2. いつ使うと幸せ？🍀（向いてるケース）

トランザクションスクリプトは、こんなとき強いです💪🔥

* 仕様がまだ固まってない（変更しまくる）🌀
* ルールが少ない・単純（CRUD寄り）🧺
* とにかく早く出したい（MVP）🚀
* 1人開発で「設計に悩む時間」を減らしたい⌛
* AIにサクッとコードを作らせたい🤖✨（手順が明確だから）

逆に、こんなときはキツくなりがちです😵‍💫

* ルールが複雑で増え続ける（例：料金計算、割引、権限、締め処理）🧠💥
* 同じルールがいろんなユースケースに散らばる（コピペ地獄）📎📎📎

---

## 3. “DDDの敵”じゃないよ🙅‍♀️❤️（共存できる）

![ddd_cs_study_076_script_evolution](./picture/ddd_cs_study_076_script_evolution.png)

大事な考え方はこれ👇

✅ **最初はトランザクションスクリプトでOK**
✅ **複雑になった部分だけDDDの部品（値オブジェクト等）へ移す**

つまり、最初から全部DDDにしなくていいんです🎉
「必要になったら育てる」が現実的です🌱

---

## 4. 最小の形：こういうコードになります🧩

題材は「ポイントを使って注文する」📦✨
ルールはシンプルに：

* ユーザーはポイントを持っている
* 注文金額からポイントを引ける（ポイント不足なら失敗）
* 注文を作って保存する

### 4.1 DTO（入力）📝

```csharp
public sealed class PlaceOrderCommand
{
    public required int UserId { get; init; }
    public required int TotalPrice { get; init; }
    public required int UsePoints { get; init; }
}
```

### 4.2 Result（成功/失敗を返す）🎯

```csharp
public sealed class Result<T>
{
    public bool IsSuccess { get; }
    public string? Error { get; }
    public T? Value { get; }

    private Result(bool isSuccess, T? value, string? error)
        => (IsSuccess, Value, Error) = (isSuccess, value, error);

    public static Result<T> Ok(T value) => new(true, value, null);
    public static Result<T> Fail(string error) => new(false, default, error);
}
```

### 4.3 トランザクションスクリプト本体（ユースケース）⚡

```csharp
public sealed class OrderService(AppDbContext db)
{
    public async Task<Result<int>> PlaceOrderAsync(PlaceOrderCommand cmd, CancellationToken ct)
    {
        // 1) 入力チェック（早期リターン）✅
        if (cmd.TotalPrice <= 0) return Result<int>.Fail("金額が不正です");
        if (cmd.UsePoints < 0) return Result<int>.Fail("ポイントが不正です");
        if (cmd.UsePoints > cmd.TotalPrice) return Result<int>.Fail("ポイントが多すぎます");

        // 2) 必要データ取得📥
        var user = await db.Users.FindAsync([cmd.UserId], ct);
        if (user is null) return Result<int>.Fail("ユーザーが見つかりません");

        // 3) ルール判定🧠
        if (user.Points < cmd.UsePoints)
            return Result<int>.Fail("ポイントが足りません");

        // 4) 更新（副作用）🛠️
        user.Points -= cmd.UsePoints;

        var order = new Order
        {
            UserId = cmd.UserId,
            TotalPrice = cmd.TotalPrice,
            UsedPoints = cmd.UsePoints,
            FinalPrice = cmd.TotalPrice - cmd.UsePoints,
            CreatedAt = DateTimeOffset.UtcNow
        };

        db.Orders.Add(order);

        // 5) 保存💾（必要ならトランザクションも）
        await db.SaveChangesAsync(ct);

        // 6) 返す🎁
        return Result<int>.Ok(order.Id);
    }
}
```

ポイント：**上から下へ読めば全部わかる**📖✨
これがトランザクションスクリプトの強みです😎

---

## 5. 事故りやすいポイント⚠️（ここだけ注意！）

### ✅ 5.1 メソッドが巨大化する（通称：ゴジラ化）🦖

![ddd_cs_study_076_godzilla_method](./picture/ddd_cs_study_076_godzilla_method.png)

**対策：ユースケースを小さく分ける**

* PlaceOrderAsync
* CancelOrderAsync
* RefundOrderAsync
  みたいに、**「動詞 + 名詞」**で分けると迷いにくいです🧭✨

### ✅ 5.2 ルールがコピペされる📎

同じ割引計算が3箇所に…みたいなやつ😇
**対策：重くなってきた“計算だけ”を部品化**します。

例：割引計算を「純粋関数」にする👇

```csharp
public static class PriceCalculator
{
    public static int ApplyPoints(int totalPrice, int usePoints)
        => totalPrice - usePoints;
}
```

これだけでも未来の自分が助かります🛟✨

### ✅ 5.3 DB操作とルールが混ざって読みづらい🍝

![ddd_cs_study_076_block_structure](./picture/ddd_cs_study_076_block_structure.png)

**対策：章立てみたいにブロック分け**すると読みやすいです👇

* Validate
* Load
* Decide
* Update
* Save
* Return

（この順番、超おすすめです💡）

---

## 6. 「DDDに戻りたくなったら」こう進化させる🔁🌱

![ddd_cs_study_076_partial_ddd](./picture/ddd_cs_study_076_partial_ddd.png)

トランザクションスクリプトで進めていて、途中でこう思ったら…

* 「割引ルール増えすぎ…」😵
* 「ポイントの扱い、何回も書いてる…」😇
* 「金額、intのままで怖い…」🥶

そのときが **DDDパーツ導入のタイミング**です✨

小さく始めるなら、まずこれ👇

* 金額 → `Money`（値オブジェクト）💰
* ポイント → `Points`（値オブジェクト）🎮
* 計算 → ドメインサービス or 値オブジェクト内へ🧠

全部を一気に変えなくてOK！
**困ったところから“部分DDD”**で十分勝てます🏆😎

---

## 7. AIに頼むときの指示テンプレ🤖🪄（そのまま使ってOK）

コピペして使えるやつ置いときます👇✨

```text
C#でトランザクションスクリプトとして「注文確定」ユースケースを書いて。
構成は Validate -> Load -> Decide -> Update -> Save -> Return の順。
入力DTO、Result型、メソッド本体を作って。
ルール：
- 金額は0より大きい
- 使用ポイントは0以上、金額以下
- ユーザーの所持ポイントが足りない場合は失敗
戻り値は orderId を Result で返す。
```

AIが変な方向に走りにくくなります🚦✨（手順が固定だから！）

---

## 8. ミニ演習🧪✨（15〜30分）

次のどれか1つを、同じスタイルで作ってみてください💪😊

### 演習A：ユーザー登録👤

* Emailが空なら失敗
* すでに同じEmailがあれば失敗
* できたらUserIdを返す

### 演習B：在庫引き当て📦

* 商品が存在しない→失敗
* 在庫が足りない→失敗
* 在庫を減らして保存

**コツ**：まずは “ベタ書きでOK” → 2回目で整理✨

---

## まとめ🎁✨

* トランザクションスクリプトは **「1ユースケース = 手順書」**📘
* 1人開発のMVPや単純ルールにめちゃ強い🚀
* ただし巨大化・コピペが増えたら黄色信号⚠️
* 困った部分だけDDD化（値オブジェクト等）でOK🌱

次の章（77章）は、さらに“DB寄りで楽”な **Active Record** に行きますよ〜😆📚✨
