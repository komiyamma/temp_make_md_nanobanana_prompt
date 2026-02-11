# 第87章：設計の「賞味期限」🍰✨

〜1年後に作り直す前提で、今の設計を決める〜

> 今日の合言葉：**「捨てる前提＝雑に作る、じゃない」**🙅‍♀️
> **「捨てやすく作る」**のがプロっぽい選択だよ〜🧹✨

---

### この章でできるようになること🎯

* 「ここはちゃんと設計する」「ここは1年後に捨てる」を**切り分け**できる🪓
* 1年後の作り直しが怖くない、**“捨てやすい構造”**を作れる🏗️
* AI（Copilot など）を使って、**判断・記録・リライト計画**を爆速にできる🤖💨

![Design Shelf Life Concept](./picture/ddd_cs_study_087_shelf_life.png)

---

## 1) 「設計の賞味期限」ってなに？🍩

設計って、冷蔵庫のケーキみたいに…
**時間が経つと“前提”が腐る**んだよね😂🍰

たとえば👇

* リリース前：「ユーザー登録はメールだけ」📧
* 半年後：「SNSログインもほしい」🔐
* 1年後：「法人アカウント、権限、監査ログ…」🏢📜

こうなると、最初の設計がいくらキレイでも
**前提が変わって詰む**ことがあるの🥲

だから第87章のテーマはこれ👇
✅ **“1年後に作り直してOK”を前提に、今の設計を決める**
→ その代わり、**作り直しが簡単になる工夫**を最初から入れる💡✨

ちなみに今のC#は **C# 14 が .NET 10 と一緒に提供**されてて、言語もツールも新しめで書きやすいよ〜🧁✨ ([Microsoft for Developers][1])

---

## 2) 「捨てる前提」にしていい場所／ダメな場所🚦

ここ、めちゃ重要〜‼️🥹

### ✅ 1年後に捨てていい候補（捨てやすく作る）

* 画面の見た目（UI）🎨
* 検索や一覧の表示方法🔎
* 管理画面の都合の仕様🛠️
* 外部API連携のつなぎ方（変わりやすい）🌐
* とりあえずのCRUD画面📝

### ❌ 1年後に捨てたら泣くやつ（守る）

* **ドメインルール**（ビジネスの核）💎
* **データ**（ユーザー・注文・課金…）💾
* **テスト**（安全ネット）🧪
* **用語**（ユビキタス言語）📚
* 「なぜそうしたか」の意思決定メモ（ADR）🗒️

EF Core 10 も .NET 10 世代でLTSとして整理されてるから、基盤側は「数年は安定して使える」前提で考えやすいよ✨ ([Microsoft Learn][2])
（でも“要件”は平気で毎月変わる😇）

---

## 3) 1年設計のコツ：**「捨てやすさ」を作る4ルール**🧹✨

### ルール①：変わるものは外側へ、変わらないものは内側へ🧅
 
 ```mermaid
 block-beta
   block:Outer["🗑️ 変わるもの (捨てやすく)"]
      style Outer fill:#ffcccc,stroke:#900
      
      block:Inner["💎 変わらないもの (守る)"]
         style Inner fill:#caffbf,stroke:#383
         Domain["Domain Logic"]
      end
   end
   
   space
   
   UI["UI / API"] --> Domain
   Infra["DB / Ext"] --> Domain
 ```
 
 * **内側**：ドメイン（ルール）💎
 * **外側**：DB / API / UI / フレームワーク都合🧰

これだけで「全部作り直し」じゃなくて
**外側だけ差し替える**ができるようになるよ✨

---

### ルール②：取り替えポイント（“継ぎ目”）を作る🧷

例えば「メール送信」が変わりやすいなら👇

```csharp
public interface IEmailSender
{
    Task SendAsync(string to, string subject, string body, CancellationToken ct);
}
```

* 最初はダミー実装でもOK🙆‍♀️
* 1年後に SendGrid → 別サービスに変えても、差し替えで済む🎛️

---

### ルール③：大改造は「段階的に」やる（いきなり全部書き直さない）🐢

ここで超有名な考え方が2つあるよ👇

* **Branch by Abstraction**：新旧の実装を“抽象”の下に入れて、段階的に切り替える方法 ([martinfowler.com][3])
* **Strangler Fig（ストラングラーフィグ）**：古い機能の周りに新しい機能を巻き付けて、少しずつ置き換えるやつ ([martinfowler.com][4])

要するに…
💥「全部書き直して一発公開！」じゃなくて
🪴「小さく置き換えて、いつでも戻せる」ってこと！

---

### ルール④：意思決定を“軽く”残す（ADR）🗒️✨

ADRは「この設計にした理由」を1枚で残すやつだよ〜📌
後から見返した時に「なんでこうしたんだっけ？」が消える🥹

ADRの考え方（1つの意思決定と理由を記録する）が整理されてるよ ([Architectural Decision Records][5])

---

## 4) ミニケース：割引計算を「1年後に作り直す前提」で作る💸🎟️

### 状況📖

* 今：クーポンは1種類
* でも未来：キャンペーン増える予感しかしない🎉😇
* だから「今は雑に増えないようにしつつ、捨てやすく」したい

### ✅ やること：抽象を1枚だけ作る（Branch by Abstractionの入口）🧩

```csharp
public interface IDiscountPolicy
{
    decimal Apply(decimal originalPrice);
}
```

#### いまの実装（とりあえず）

```csharp
public sealed class NoDiscount : IDiscountPolicy
{
    public decimal Apply(decimal originalPrice) => originalPrice;
}
```

#### 1年後に増えた実装（差し込み）

```csharp
public sealed class PercentageDiscount : IDiscountPolicy
{
    private readonly decimal _rate; // 0.10m = 10% off
    public PercentageDiscount(decimal rate) => _rate = rate;

    public decimal Apply(decimal originalPrice)
        => originalPrice * (1m - _rate);
}
```

### ✅ “切り替え”を簡単にする（後で差し替えが楽）🎚️

```csharp
public sealed class PriceCalculator
{
    private readonly IDiscountPolicy _policy;
    public PriceCalculator(IDiscountPolicy policy) => _policy = policy;

    public decimal Calculate(decimal originalPrice) => _policy.Apply(originalPrice);
}
```

これで「割引計算の作り直し」が来ても、
**差し替える場所がここだけ**になる🎯✨

---

## 5) AI（Copilot等）で“1年設計”を爆速にする🤖💨

Visual Studio では GitHub Copilot が統合されてて、補完＋チャットが一体で使える流れだよ✨ ([Visual Studio][6])
Copilot Chat は IDE 上で、説明・修正提案・テスト生成とか頼めるよ🧪 ([GitHub Docs][7])

### 使えるプロンプト例（コピペOK）📎✨

#### ✅ 「賞味期限を決める」相談

* 「この機能は1年後に捨てる前提で良い？捨てたくない部分はどこ？理由もつけて」

#### ✅ ADRを1枚生成

* 「この設計判断をADR形式で1枚にして。Context/Decision/Consequencesで、1年後に作り直す前提も書いて」

#### ✅ Strangler Figの作戦を作る

* 「このモジュールをStrangler Figで段階置換する手順を作って。最初に作る“新入口”と、切り替えポイントも提案して」 ([martinfowler.com][4])

---

## 6) チェックリスト：この設計、賞味期限いつ？🧠🗓️

YESが多いほど「短命設計（1年で捨てやすく）」がおすすめ🙆‍♀️✨

* 仕様が月1で変わりそう😇
* まだ検証中で、方向性が決まってない🧪
* UI/運用都合が強くて、プロダクトの核じゃない🎛️
* 外部API・法規・料金体系が変わりやすい🌪️
* 1人開発で、まず出して反応を見たい🚀

逆に👇は「守る設計」寄り💎

* お金・権限・在庫など、破綻すると致命傷💥
* ルールが複雑で、間違えると信用が死ぬ⚠️
* データの整合性が命💾

---

## 7) よくある失敗あるある🤣（でも笑えない）

* 「捨てる前提」＝「テストなし」→ 1年待たずに地獄🔥
* 「捨てる前提」＝「境界ゼロ」→ 捨てたくても捨てられない🕸️
* データ移行を後回し → 作り直しで詰む💾😇

---

## 8) ミニ演習（30〜60分）✍️✨

### 演習A：あなたのアプリを2色で塗る🎨

* 💎守る（ドメインルール／データ／テスト）
* 🧹捨てる（UI／CRUD／外部連携の都合）

### 演習B：ADRを1枚書く🗒️

* 「このモジュールは1年で作り直す前提」
* 「だから継ぎ目（interface）をここに作った」
* 「テストはここだけ厚くする」

### 演習C：Branch by Abstractionを1箇所だけ入れる🧩

* 「あとで差し替えたい処理」を1つ選んで、`I～` を作るだけでOK🙆‍♀️

---

## まとめ🎁✨

* 設計は永遠じゃない。**前提が腐る**🍰
* だから「1年後に作り直す前提」は超アリ👍
* ただしコツは **雑に作る**じゃなくて
  ✅ **捨てやすく作る**（境界・継ぎ目・テスト・ADR）🧹✨
* 大改造は **段階的に**（Branch by Abstraction / Strangler Fig）で安全にいこう🐢🪴 ([martinfowler.com][3])

次は「1人でのコードレビュー術（AIに意地悪レビュアーをやらせる）」に繋がるから、ここで作ったADRや継ぎ目がめちゃ効いてくるよ〜😈🧠✨

[1]: https://devblogs.microsoft.com/dotnet/introducing-csharp-14/ "Introducing C# 14 - .NET Blog"
[2]: https://learn.microsoft.com/en-us/ef/core/what-is-new/ef-core-10.0/whatsnew?utm_source=chatgpt.com "What's New in EF Core 10"
[3]: https://martinfowler.com/bliki/BranchByAbstraction.html?utm_source=chatgpt.com "Branch By Abstraction"
[4]: https://martinfowler.com/bliki/StranglerFigApplication.html?utm_source=chatgpt.com "Strangler Fig"
[5]: https://adr.github.io/?utm_source=chatgpt.com "Architectural Decision Records"
[6]: https://visualstudio.microsoft.com/github-copilot/ "
	Visual Studio With GitHub Copilot - AI Pair Programming"
[7]: https://docs.github.com/ja/copilot/how-tos/chat-with-copilot/chat-in-ide?utm_source=chatgpt.com "IDE で GitHub Copilot に質問する"
