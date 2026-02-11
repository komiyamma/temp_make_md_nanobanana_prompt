# 第80章：DRYの罠 🤹‍♀️💥

**1人開発なら「似てるコード」を無理にまとめない方が速いこと、めっちゃあるよ！**😊✨

---

## 0. 今日のゴール 🎯

この章を読み終わったら…

* 「DRYにした方がいい重複」と「放置してOKな重複」を見分けられる👀✅
* **AIが“まとめたがる”提案**を、冷静に採用/却下できる🤖🧠
* DDD的に **境界（コンテキスト）を壊さない**判断ができる🚧✨

![DRY Trap](./picture/ddd_cs_study_080_factory.png)

---

## 1. DRYってなに？（超ざっくり）🔁

![Knowledge vs Code Duplication

**Labels to Render**:
- Code: "見た目 (OK)"
- Knowledge: "知識 (NG)"

**Visual Details**:
1. Core Concept: Distinguishing bad duplication.
2. Metaphor: Two identical looking boxes (Code) are fine. Two identical rule books (Knowledge) are bad.
3. Action: Comparison.
4. Layout: Side-by-side.](./picture/ddd_cs_study_080_knowledge_vs_code.png)

DRY = “Don’t Repeat Yourself（繰り返すな）” ってやつだね😊
でもここで大事なのは…

### ✅ DRYが本当に嫌ってるのは「知識の重複」

つまり、**同じルール（仕様）が2か所以上に散らばってる状態**がヤバい😇💦
（例：送料計算ルールが3つのクラスにコピペされてる…みたいな）

### ⚠️ でも「コードが似てる」だけでまとめるのは危険

**“たまたま今は似てるだけ”**のことが多いからね😵‍💫

---

## 2. 1人開発で起きがちなDRYの罠 🕳️🐿️

![Utility Mess

**Labels to Render**:
- Utility: "便利クラス"
- Mess: "ぐちゃぐちゃ"

**Visual Details**:
1. Core Concept: Over-centralization.
2. Metaphor: A giant box labeled 'Utility' overflowing with unrelated tools (hammer, spoon, ladder).
3. Action: Overflowing.
4. Layout: Messy pile.](./picture/ddd_cs_study_080_utility_mess.png)

1人だと、ついこうなる👇

* 「同じっぽいから共通化しよ！」
* 「フォルダに Utility / Helper 作ろ！」
* 「ジェネリック＋delegateで汎用化しよ！」

で、数日後…

* どこを直せばいいか分からない😇
* “便利クラス”が肥大化して地獄😇😇
* ちょっと変更したいだけなのに、影響範囲が広い😇😇😇

---

## 3. まず結論：1人開発のDRYは「遅らせる」が強い 🐢✨

![Solo Dev Priority

**Labels to Render**:
- 1st: "読みやすさ"
- 2nd: "直しやすさ"
- 3rd: "DRY"

**Visual Details**:
1. Core Concept: Prioritization.
2. Metaphor: A winner's podium. 1st place is a readable book. 2nd is a wrench. 3rd is a DRY symbol.
3. Action: Standing on podium.
4. Layout: Podium.](./picture/ddd_cs_study_080_priority_podium.png)

最初はこう考えると安定するよ😊

### 🌟 1人開発の優先順位

1. **読みやすい**（未来の自分が助かる）📖✨
2. **直しやすい**（変更がラク）🔧✨
3. その次に、**重複を減らす**🔁

---

## 4. “放置してOK”な重複の特徴 🟢😌

![Context Branching

**Labels to Render**:
- Now: "現在 (似てる)"
- Future: "未来 (別物)"

**Visual Details**:
1. Core Concept: Divergent evolution.
2. Metaphor: Two plants that look identical as seedlings but grow into completely different trees.
3. Action: Growing.
4. Layout: Timeline.](./picture/ddd_cs_study_080_context_branch.png)

次のどれかなら、無理にまとめなくてOKなこと多いよ👇

### ✅ A) 変更される未来が別々っぽい（＝分岐しそう）🌿

例：

* 「会員登録」と「管理者登録」
  今は似てても、後から違う制約が入りやすいよね😺

### ✅ B) まだ2回しか出てきてない（育ってない）🌱

2回くらいの重複は、**観察期間**でOK😊
（“3回目が来たら考える”がラク✨）

### ✅ C) DDDの境界をまたいでる 🚧

境界づけられたコンテキスト（別世界）をまたいで共通化すると、
**未来の変更が連鎖して爆発**しやすい💣😇

---

## 5. “今すぐDRYすべき”重複の特徴 🔴🧨

![Scattered Rules

**Labels to Render**:
- Rule: "税計算"
- Map: "コード全体"

**Visual Details**:
1. Core Concept: Distributed logic.
2. Metaphor: Red pins scattered all over a map, representing the same business rule copied everywhere.
3. Action: Pinning.
4. Layout: Map view.](./picture/ddd_cs_study_080_scattered_rules.png)

これは早めにまとめた方がいいやつ👇

### ✅ A) 同じビジネスルールが複数箇所にある（知識の重複）📌

* 税計算
* 割引条件
* メールアドレスの形式チェック
* パスワードルール
  みたいな「仕様そのもの」が散らばってたら危険⚠️

### ✅ B) 直し忘れでバグりそう（変更が怖い）😱

「ここ直したけど、あっち直し忘れた…」ってなるやつ💦

---

## 6. 例：AIが“共通化しすぎ”て読みにくくするパターン 🤖💥

### (1) まずは素直な実装（読みやすい）😊

「物理商品」と「デジタル商品」の購入処理が似てるケース👇

```csharp
public class PurchaseService
{
    public Receipt BuyPhysicalProduct(PhysicalOrder order)
    {
        var total = order.Subtotal + order.ShippingFee;
        // 決済
        // 在庫引き当て
        // 発送手配
        return new Receipt(total);
    }

    public Receipt BuyDigitalProduct(DigitalOrder order)
    {
        var total = order.Subtotal; // 送料なし
        // 決済
        // ライセンス発行
        // ダウンロード案内
        return new Receipt(total);
    }
}
```

似てるけど、**処理の意味がぜんぜん違う**よね？😌✨
この段階で無理にまとめない方が安全なことが多い👍

---

### (2) AIが提案しがちな“共通化”（読みにくい＆未来に弱い）😵‍💫

![Premature Abstraction

**Labels to Render**:
- Simple: "素直"
- Abstract: "共通化"
- Hard: "難解"

**Visual Details**:
1. Core Concept: Complexity cost.
2. Metaphor: Two simple knives (Simple) vs A giant complex machine that requires a manual to operate (Abstract).
3. Action: Comparison.
4. Layout: Side-by-side.](./picture/ddd_cs_study_080_premature_abstraction.png)

```csharp
public class PurchaseService
{
    public Receipt Buy<TOrder>(
        TOrder order,
        Func<TOrder, decimal> calcTotal,
        Action<TOrder> afterPayment)
    {
        var total = calcTotal(order);
        // 決済
        afterPayment(order);
        return new Receipt(total);
    }
}
```

これ、一見キレイだけど…👀💦

* 何をしてるか **読み解きコストが高い**
* “物理”と“デジタル”の違いが **コードから消える**
* 仕様変更で `Func` が増殖しがち😇

**1人開発では、こういう抽象化は負けやすい**です🥲

---

## 7. DDD的な超重要ポイント：境界を壊すDRYはNG 🚧🙅‍♀️

![Boundary Wall

**Labels to Render**:
- Context A: "User"
- Context B: "User"
- Wall: "境界"

**Visual Details**:
1. Core Concept: Protecting boundaries.
2. Metaphor: A brick wall separating two 'User' concepts. Merging them would break the wall.
3. Action: Separating.
4. Layout: Wall.](./picture/ddd_cs_study_080_boundary_wall.png)

DDDは「境界線を守るゲーム」みたいなところがあるよ😊✨
だから…

* 別コンテキストの「User」
* 別コンテキストの「Status」
* 別コンテキストの「Order」

**名前が同じでも意味が違う**ことがある😳
ここを共通化すると、境界が溶けてカオスになる🫠

---

## 8. 1人開発向け：迷わない判断フロー 🧭✨
 
 迷ったらこれでOK😊
 
 ```mermaid
 flowchart TD
     Start(["似てるコード発見👀"]) --> Q1{知識の重複？}
     Q1 -- "NO<br/>(見た目だけ)" --> Separate["分けたままにする🌿"]
     Q1 -- YES --> Q2{将来分岐しそう？}
     Q2 -- YES --> Separate
     Q2 -- NO --> Q3{3回目？}
     Q3 -- NO --> Watch["様子見 (-2回) 👀"]
     Q3 -- YES --> Common["共通化する 🧩"]
     
     style Common fill:#caffbf,stroke:#383,stroke-width:2px
     style Separate fill:#ffdfba,stroke:#f80,stroke-width:2px
 ```
 
 ### ✅ ステップ1：それは「知識の重複」？「見た目の重複」？

* 知識の重複 → DRYしたい📌
* 見た目の重複 → いったん放置OK🔁

### ✅ ステップ2：その2つは将来“別々に変わりそう”？

* はい → 分ける🌿
* いいえ → 次へ

### ✅ ステップ3：3回出てきた？（目安）👀

* まだ → 観察🌱
* 出た → まとめ検討🛠️✨

---

## 9. AI（Copilot/Codex）への“賢い頼み方”🤖💬

AIは「重複＝悪」って判断しがちだから、**境界と意図**を言葉で渡すと強いよ😊✨

### ✅ 使えるプロンプト例

```text
この2つのコードは似ていますが、将来仕様が分岐する可能性があります。
「無理に共通化しない案」も含めて、読みやすさ優先で提案して。
共通化するなら、影響範囲が広がらない最小の形にして。
```

### ✅ “DDD境界”を守らせるプロンプト例

```text
この2つは別の境界づけられたコンテキストです。
共通化は境界を壊す可能性があるので、基本は別実装のままにしたい。
共通化するなら「知識の重複」だけに限定して提案して。
```

---

## 10. ミニ演習（10〜15分）🧪✍️

あなたのプロジェクト（またはサンプル）で…

1. 似てるメソッドを2つ探す👀
2. 次をメモする📝

   * 「同じ仕様（知識）？」それとも「たまたま似てるだけ？」
   * 将来分岐しそう？🌿
3. AIに上のプロンプトで相談🤖
4. **“共通化しない”判断も正解**として残す😊✨

---

## まとめ 🎁

* DRYは正義っぽいけど、**やりすぎると未来の自分を殴る**🥲👊
* 1人開発は **読みやすさ＞抽象化** が勝ちやすい📖✨
* DDDでは特に、**境界をまたぐDRYは事故りやすい**🚧💥
* AIはまとめたがるから、**「共通化しない選択肢」も指示に入れる**と最強🤖💪

ちなみに今の最新世代だと **C# 14 が最新で .NET 10 でサポート**されてるよ。 ([Microsoft Learn][1])

---

次（第81章）は「技術的負債を“意図的に”作る」だね😈✨
「わざと借金する」ってどういうこと？を、気持ちよく整理していこう〜💨

[1]: https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-14?utm_source=chatgpt.com "What's new in C# 14"
