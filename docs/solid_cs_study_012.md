# 第12章：OCPの目的「追加で直す場所を減らす」🧩

この章は **OCP（Open-Closed Principle）＝拡張に開き、変更に閉じる** の“狙い”をつかむ回だよ😊
定義としては「ソフトウェア要素（クラス/関数など）は**拡張はできる**けど、**既存コードの修正は最小**にしようね」という考え方だよ〜📌 ([ウィキペディア][1])

---

## 12.0 この章のゴール🎯✨

読み終わったら、こんな状態になってたらOK👍

* 「追加仕様が来たとき、**どこが壊れやすいか**」を見抜ける👀💥
* 「既存コードをいじる箇所が増えるのは危険」って理由を説明できる🗣️
* “増えそうな分岐ポイント”を先に見つけて、**拡張ポイント**として設計できる🔧
* 次章（Strategy）に入る前の“土台”ができる🎭✨

---

## 12.1 OCPを一言でいうと？🗣️💡

**「追加が来たら、“既存のあちこち”を直すんじゃなくて、“新しい部品を足す”で済ませたい」** これ！

### よくある勘違い⚠️😅

* ❌「既存コードを絶対に1文字も変更しちゃダメ」
  → そんな宗教じゃないよ😂（バグ修正や設計の整理は当然直す！）
* ✅「追加のたびに“修正の連鎖”が起きないように、変更点を局所化しよう」
  → これが本質🧠✨ ([objectmentor.com][2])

---

## 12.2 “追加のたびに壊れる”の正体：分岐の増殖🌱➡️🌳💥

ミニECみたいなアプリでありがちなのがこれ👇

* 支払い方法が増える
* 配送方法が増える
* 割引ルールが増える
* 税計算の例外が増える

この「増えるもの」を、雑に `if / switch` で押し込めると…

* 1個追加するたびに `switch` が長くなる📏😵‍💫
* 変更箇所が増える（複数ファイルに散る）🧩🧩🧩
* 既存ケースをうっかり壊す（回帰）💥
* しかもレビューで差分がデカくなる😇

この「変更が連鎖するコード」を、OCPは嫌うんだよ〜🧯✨ ([objectmentor.com][2])

---

## ポリモーフィズム (Polymorphism)
![Plug and Play](./picture/solid_cs_study_012_plug_and_play.png)

## 12.3 OCPが守りたいもの：「変わらない核」と「変わる端」🧊🔥

![Robot skeleton (Core) vs detachable armor plates (Variations).](./picture/solid_cs_study_012_ocp_core_variation.png)

OCPって、イメージ的にはこう👇

* **核（コア）**：注文の流れ、支払いの結果の扱い、領収書の作り方…みたいな「アプリの骨格」🦴
* **端（バリエーション）**：支払い手段、割引、配送など「増える種類」🍬🍭

OCPは、**増える種類（端）を部品化**して、
**骨格（核）をできるだけ触らなくて済む**ようにする考え方だよ🧩✨

---

## 12.4 “増えそうポイント”の見つけ方🔮👀

「ここ、将来増えるぞ…」を当てにいくコツは、この3つだけ覚えてね😉💕

### ① “種類”という単語が仕様に出たら危険🚨

* 「支払い方法の種類」
* 「配送会社の種類」
* 「会員ランクの種類」
  → だいたい増える😇

### ② 仕様書/会話で「今はAとBだけ」が出たら危険🚨

それ、将来Cが来るフラグだよ😂

### ③ `enum` + `switch` が育ってたら危険🚨

`enum` 自体が悪ではないけど、
**「増えるenumをswitchで捌く」**が増殖しはじめたら、OCPチャンス🌱✨

---

## 12.5 例：支払い方法の追加で毎回switchを直す地獄😇💸

まずは“わざと”OCPに反する例ね（体感が大事！）🔥

```csharp
public enum PaymentMethod
{
    CreditCard,
    BankTransfer,
    ConvenienceStore
}

public sealed class Order
{
    public required decimal TotalAmount { get; init; }
    public required PaymentMethod PaymentMethod { get; init; }
}

public sealed class PaymentService
{
    public string Pay(Order order)
    {
        // ❌ 追加のたびにここを編集する未来が見える…
        return order.PaymentMethod switch
        {
            PaymentMethod.CreditCard => $"カード決済: 手数料={order.TotalAmount * 0.03m:0}円",
            PaymentMethod.BankTransfer => "銀行振込: 手数料=0円（入金確認が必要）",
            PaymentMethod.ConvenienceStore => "コンビニ払い: 手数料=120円",
            _ => throw new NotSupportedException("未対応の支払い方法です")
        };
    }
}
```

### ここに「PayPay追加」とか来たら…？📣😇

* `PaymentMethod` に値を追加
* `switch` に case を追加
* 既存のcaseに影響ないか確認
* テストも増やす（しかも既存が壊れてないか全部見たい）

これ、**「追加」なのに「修正」が発生しまくってる**のがポイントだよ⚠️

---

## 12.6 OCPのゴール形：「追加＝新しい部品を足す」🧱✨

OCPでは、ざっくりこうしたい👇

* 「支払い」を **差し替え可能な部品**にする🎁
* `PaymentService` 側は「部品を呼ぶだけ」にする☎️
* 新しい支払い方法が来たら、**新しい部品を追加するだけ**に寄せる🧩✨

この章では“完成形”までガチガチに作り込まず、**方向性**を掴むよ😊
（実装の王道は次章の Strategy でやるよ〜🎭）

### 方向性のミニ例（雰囲気つかむ用）👀✨

```csharp
public interface IPaymentProcessor
{
    PaymentMethod Method { get; }
    string Pay(Order order);
}

public sealed class CreditCardProcessor : IPaymentProcessor
{
    public PaymentMethod Method => PaymentMethod.CreditCard;

    public string Pay(Order order)
        => $"カード決済: 手数料={order.TotalAmount * 0.03m:0}円";
}

public sealed class BankTransferProcessor : IPaymentProcessor
{
    public PaymentMethod Method => PaymentMethod.BankTransfer;

    public string Pay(Order order)
        => "銀行振込: 手数料=0円（入金確認が必要）";
}

public sealed class PaymentService
{
    private readonly IReadOnlyList<IPaymentProcessor> _processors;

    public PaymentService(IReadOnlyList<IPaymentProcessor> processors)
        => _processors = processors;

    public string Pay(Order order)
    {
        var processor = _processors.Single(p => p.Method == order.PaymentMethod);
        return processor.Pay(order);
    }
}
```

✅ ここに新しい支払い方法が来たら？
→ `PayPayProcessor` みたいな **新クラス追加**で済む世界に近づく✨

（ただし今は手で `_processors` を渡してるけど、DIでキレイに組み立てるのは後半章でやるよ🔌🧩）

---

## 12.7 「閉じる」対象を間違えないチェックリスト✅🧠

OCPって「なんでも抽象化しよう！」になりがちだから、まずこのチェックだけでOK👌✨

### OCPを効かせると嬉しいやつ👍

* 追加頻度が高い（毎月増える）📅
* 種類が増えるのが“確定”してる（プラグイン的）🔌
* 追加のたびに事故が起きてる（回帰バグ）💥
* `switch` がすでに太ってる🐷💦

### まだ急がなくていいやつ😌

* 種類が増える予定が薄い
* 仕様が固まってないのに先に抽象化して迷子になる
  → これは次章以降（やりすぎ注意⚖️😅）でちゃんと扱うよ✨

---

## 12.8 🤖AIと一緒に「増えそうポイント」を当てに行く🔍✨

Copilot / Codex系に投げるときは、**“未来の追加”を具体例で言わせる**のがコツだよ😊💕

### プロンプト例①：増えそうな分岐ポイントを探す🔮

「このコードで、今後仕様追加が来たときにswitch/ifが増殖しそうなポイントを列挙して。理由も添えて。」

### プロンプト例②：拡張ポイント候補を出させる🧩

「“追加される可能性が高い種類”を見つけて、部品化（インターフェース化）するならどこ？候補名も10個出して。」

### プロンプト例③：安全に分ける手順を作らせる🪄

「既存の動作を壊さずにOCP寄りに直す最小ステップを、1→2→3…で出して。先にテストを足すなら何を足す？」

---

## 12.9 演習（手を動かす）✍️💪✨

### 演習A：分岐ポイント探しゲーム👀🎮

ミニECのコード（注文/支払い/発送/割引）を見て、次をメモしてね📝

* `switch` / `if` がある場所を全部リストアップ
* それぞれについて

  * 「何の種類を分岐してる？」
  * 「それ増えそう？」
  * 「増えたらどこを直す？」
    を3行で書く

👉 これだけでOCP脳が育つよ🌱✨

---

### 演習B：追加仕様を1つ想定して“修正箇所数”を数える🧮😇

例えば「コンビニ払いに“手数料の地域差”が入った」とするね🏪

* いまの設計だと、どこを何ヶ所直す？
* OCP寄りにすると、理想は何ヶ所？

**目標：修正箇所が“1ヶ所”に寄る**こと（ゼロじゃなくていいよ！）✨

---

## 12.10 ミニクイズ🧠🎯（サクッと！）

Q1️⃣ OCPの狙いは「既存コードを絶対変更しない」ことである。

* A: はい / B: いいえ
  👉 正解：**B**（変更の連鎖を防ぐのが狙い！） ([objectmentor.com][2])

Q2️⃣ `enum + switch` が増殖してきた。OCPの観点でまず疑うべきことは？

* A: enumを消すべき
* B: “増える種類”をswitchで抱えてないか
  👉 正解：**B** 😊✨

Q3️⃣ OCPで一番おいしい瞬間は？

* A: 仕様追加が来たのに既存の重要ロジックを触らずに済んだ
* B: クラス数が増えて嬉しい
  👉 正解：**A** 😂👍

---

## 12.11 まとめ🎀✨（次章につなぐよ〜！）

* OCPは「追加が来ても、既存のあちこちを直さない」ための考え方🧩
* “増える種類”を `if/switch` で抱えると、修正箇所が増えて壊れやすい💥
* まずは **増えそうポイントを見つける**のが勝ち筋🔮✨
* 次章では、その“増える種類”をキレイに差し替える王道パターン **Strategy** を、手を動かして作るよ🎭🔁

ちなみに、C# 14 は .NET 10 SDK や Visual Studio 2026 で試せるよ〜（この教材のコードもそのまま動かせる想定だよ）✨ ([Microsoft Learn][3])

---

次、**第13章：Strategyで差し替え🎭🔁** に進めるけど、もし「この章の題材を“支払い”じゃなくて“配送”にしたい」とかあったら、その前提で例を差し替えて続き作れるよ😊📦💕

[1]: https://en.wikipedia.org/wiki/Open%E2%80%93closed_principle?utm_source=chatgpt.com "Open–closed principle"
[2]: https://objectmentor.com/resources/articles/ocp.pdf?utm_source=chatgpt.com "The Open-Closed Principle - Object Mentor"
[3]: https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-14?utm_source=chatgpt.com "What's new in C# 14"
