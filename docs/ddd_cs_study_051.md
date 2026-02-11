# 第51章：副作用のない関数 🧼✨

![副作用のない関数](./picture/ddd_cs_study_051_pure_func.png)

**〜何度実行しても同じ結果が出る、テストしやすいロジック〜**

---

## 0. 今日のゴール 🎯😊

この章を読み終えると、こんな状態になれます👇

* 「副作用ってなに？」が説明できる 🧠
* “計算だけする関数” と “保存や通知をする処理” を分けられる ✂️
* ドメイン（ビジネスルール）を **テストしやすい形** にできる ✅
* AIにコードを生成させても、**暴走しにくい形** を保てる 🤖🧷

---

## 1. 「副作用」ってなに？💥

ざっくり言うと…

> **関数を呼んだら、戻り値以外にも世界が変わっちゃうこと** 🌍💫

たとえばこんなの👇（全部 “副作用” になりがち）

* DBに保存する 🗄️
* ファイルに書く 📄
* ネットワーク通信する 🌐
* メール送る ✉️
* `DateTime.Now` を読む（時間は毎回変わる）⏰
* `Guid.NewGuid()` を作る（毎回変わる）🆔
* 乱数を使う 🎲
* `static` 変数を更新する 🧨
* `Console.WriteLine` で出力する 🖥️

「え、時間読むのも副作用なの？」って思うよね🙂
でも **同じ入力でも結果が変わる** なら、テストが急にめんどくさくなるのです…😇
 
 ```mermaid
 flowchart TD
    subgraph Impure["❌ 副作用あり (Impure)"]
      I_Input[入力] --> I_Func[関数]
      I_Func --> I_DB[(DB保存)]
      I_Func --> I_Time[現在時刻]
      I_Func --> I_Output["出力 (毎回違うかも?)"]
    end

    subgraph Pure["⭕ 副作用なし (Pure)"]
      P_Input[入力] --> P_Func[関数]
      P_Func --> P_Output["出力 (常に同じ!)"]
    end
 ```
 
 ---

## 2. 副作用のない関数（＝“純粋な関数”）ってなに？🫧

副作用のない関数は、こういう性質を持ちます👇

### ✅ ルール1：同じ入力 → 同じ出力

* 何回呼んでも結果が同じ 😺

### ✅ ルール2：戻り値以外で世界を変えない

* DB保存しない、ログ出さない、外部に触らない 🙅‍♀️

---

## 3. DDDでなぜ大事？🏰✨

DDDでは、いちばん守りたいのは **ドメインのルール**（利益が出る部分）だよね💎

そのドメインが…

* DBや外部APIにべったり
* 時刻や乱数に依存
* ログ出しながら状態を変える

…みたいになると、**ルールの検証（テスト）が地獄** になります🔥😵‍💫

逆に、ドメインを「計算だけ」に寄せると…

* ユニットテストが秒で書ける ⚡✅
* AIが生成しても壊れにくい 🧱🤖
* 将来DBを変えても影響が少ない 🔁

っていう、**1人開発で最強のメリット**が出ます💪✨

---

## 4. ダメな例（副作用あり）→ 良い例（副作用なし）に直す 🛠️

### 4-1. ダメな例：割引計算が “今の時刻” に依存してる 😵

```csharp
public static decimal CalcTotalWithCampaign(decimal subtotal)
{
    // 19時以降は5%引き（例）
    if (DateTime.Now.Hour >= 19)
        return subtotal * 0.95m;

    return subtotal;
}
```

これ、テストしようとすると…
「19時以降じゃないとテスト落ちる」みたいな **時間ガチャ** が発生します🎰😇

---

### 4-2. 良い例：必要な情報を引数でもらう（純粋）✨

```csharp
public static decimal CalcTotalWithCampaign(decimal subtotal, DateTime now)
{
    if (now.Hour >= 19)
        return subtotal * 0.95m;

    return subtotal;
}
```

これならテストが超ラク👇💡

```csharp
using Xunit;

public class CampaignTests
{
    [Fact]
    public void After19_Discounted()
    {
        var now = new DateTime(2026, 1, 2, 19, 0, 0);
        var total = Calc.CalcTotalWithCampaign(1000m, now);
        Assert.Equal(950m, total);
    }

    [Fact]
    public void Before19_NotDiscounted()
    {
        var now = new DateTime(2026, 1, 2, 18, 59, 0);
        var total = Calc.CalcTotalWithCampaign(1000m, now);
        Assert.Equal(1000m, total);
    }
}

public static class Calc
{
    public static decimal CalcTotalWithCampaign(decimal subtotal, DateTime now)
    {
        if (now.Hour >= 19)
            return subtotal * 0.95m;

        return subtotal;
    }
}
```

**時間を“読む”のをやめて、時間を“受け取る”** ようにするだけで勝ちです🏆🥳

---

## 5. DDDっぽくする：ドメインは「計算」、外側が「保存」🧅✨

### 5-1. ドメイン側（副作用なし）🫧

```csharp
public sealed record OrderLine(string ItemName, int Quantity, decimal UnitPrice);

public sealed class Order
{
    private readonly List<OrderLine> _lines = new();

    public IReadOnlyList<OrderLine> Lines => _lines;

    public void AddLine(OrderLine line)
    {
        if (line.Quantity <= 0) throw new ArgumentException("数量は1以上");
        if (line.UnitPrice < 0) throw new ArgumentException("単価は0以上");
        _lines.Add(line);
    }

    // ✅ 純粋ロジック：合計計算（副作用なし）
    public decimal CalcSubtotal()
        => _lines.Sum(x => x.UnitPrice * x.Quantity);

    // ✅ 純粋ロジック：ルールに従って割引計算（副作用なし）
    public decimal CalcTotal(DateTime now)
    {
        var subtotal = CalcSubtotal();
        var discounted = ApplyNightDiscount(subtotal, now);
        return discounted;
    }

    private static decimal ApplyNightDiscount(decimal subtotal, DateTime now)
        => now.Hour >= 19 ? subtotal * 0.95m : subtotal;
}
```

ここにはDBもAPIも出てきません🙅‍♀️
だからテストが簡単で、AIに生成させても崩れにくいです🤖🧱✨

---

### 5-2. 外側（Application/Infrastructure）で副作用をやる 🌐🗄️

```csharp
public interface IOrderRepository
{
    Task SaveAsync(Order order, CancellationToken ct);
}

public sealed class PlaceOrderUseCase
{
    private readonly IOrderRepository _repo;

    public PlaceOrderUseCase(IOrderRepository repo)
    {
        _repo = repo;
    }

    public async Task<decimal> PlaceAsync(Order order, DateTime now, CancellationToken ct)
    {
        // ✅ まずは純粋計算
        var total = order.CalcTotal(now);

        // ✅ 最後に副作用（保存）
        await _repo.SaveAsync(order, ct);

        return total;
    }
}
```

イメージはこれ👇🙂

* **内側（ドメイン）**：計算・ルール 💎
* **外側（アプリ/インフラ）**：保存・送信・表示 📦

---

## 6. よくある落とし穴あるある 😭⚠️

### 😵「ログ出すだけだし…」

ログも副作用です🪵
ドメインに入れたくなったら、外側でやる or イベントにするのが安全🙆‍♀️

### 😵「staticにキャッシュ置いちゃえ」

テストが壊れる原因になりがち🧨
（並列テスト、順番依存、環境依存…）

### 😵「Guid.NewGuid() をドメインで生成」

ID生成が必要なら「外側で作って渡す」か、方針を決めて一箇所に寄せると安心🆔✨

---

## 7. “副作用を追い出す” 3ステップ 🧹✨

DDD初心者でも、この手順だけ覚えればOKです😊

1. **その関数が触ってる外部要素をリストアップ**

   * 時刻、乱数、DB、HTTP、ファイル、static、Console…📝

2. **外部要素を “引数” にして渡す**

   * `DateTime.Now` → `now` を引数へ ⏰➡️📦

3. **保存や通知は “外側” に移す**

   * ドメイン：計算
   * 外側：保存・送信・表示

---

## 8. ミニ演習 🧪✨（手を動かすと一気に分かるよ！）

### 演習A：送料計算を “純粋関数” にしてみよう 📦🚚

仕様👇

* 小計が3000円以上なら送料無料
* それ未満は送料500円
* ただし「北海道」は送料+300円

まずは関数だけ作る（副作用なし）🎯

```csharp
public static int CalcShippingFee(int subtotal, string prefecture)
{
    if (subtotal >= 3000) return 0;

    var fee = 500;
    if (prefecture == "北海道") fee += 300;
    return fee;
}
```

次にテストを3本書いてみてね✅😊
（送料無料/通常/北海道）

---

## 9. AIに頼むときのコツ（プロンプト例）🤖📝✨

AIは放っておくと、DBやログまで混ぜがちです😇
最初から “縛り” を書くと成功率が上がるよ！

### ✅ そのままコピペで使える指示テンプレ

```text
次の仕様をC#で実装してください。
ただし「ドメインロジックは副作用なし（純粋関数）」にしてください。

- DateTime.Now / Guid.NewGuid / 乱数 / DBアクセス / HTTP / Console出力は禁止
- 必要な値（現在時刻など）は引数で受け取る
- まず純粋関数（計算）を書き、次にxUnitのユニットテストを3本書く
- コードは読みやすさ優先で、短すぎる省略はしない
仕様：<ここに仕様>
```

これ、CopilotでもCodex系でもめちゃ効きます💪😺✨

---

## まとめ 🎀

* **副作用のない関数**は「同じ入力→同じ出力」で「世界を変えない」🫧
* ドメインは **計算・ルール** に寄せると、1人開発が超ラクになる✨
* 時刻や乱数は **読むな、受け取れ** ⏰➡️📦
* 保存や通知は **外側** に追い出す 🗄️➡️🚪

---

次の章（第52章）では、さらにテストと相性が良い **Resultパターン**（例外じゃなく戻り値でエラーを扱う）に進むよ〜😊🧩
