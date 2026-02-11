# 第86章：スクリプト言語的アプローチ 🧪✨

### 〜Python / PHP / JS / TS の経験を、C#開発の“爆速”に変える方法〜🚀💻

この章はひとことで言うと…

**「C#を“ガチガチ設計言語”だと思い込みすぎないで、スクリプト言語みたいに“試して→育てる”流れを作ろうね」**って話です😊🌱

![Script Language Approach](./picture/ddd_cs_study_086_script_approach.png)

---

## 1) この章でできるようになること ✅✨

* **1ファイルだけで** C# を実行して、サクッと試作できる 🧷
* “書き捨てスクリプト”を、あとから **ちゃんとした構造（DDD寄り）へ育てる** 手順がわかる 🌳
* Python/JSの **map/filter/reduce感覚** を C#（LINQ）で使えるようになる 🧠⚡
* AI（Copilot等）に **「スクリプト→設計へ」** のリファクタを手伝わせるコツがわかる 🤝🤖

---

## 2) そもそも「スクリプト言語的アプローチ」ってなに？📝

DDDって、ちゃんとやると強い💪✨
でも一人開発だと、最初から全部DDDで固めると…

* 仕様がまだフワフワなのに、構造だけ立派になる 😵‍💫
* AIに頼んだら “綺麗っぽいけど違う” コードが量産される 🌀
* 試作の速度が落ちて、やる気も落ちる 😭

そこで便利なのが **スクリプト言語的アプローチ**です😊
つまり、

**「まず1本の手順コードで動かして理解する → 固まった所だけ設計にする」** ✨

この順番にすると、迷いが減ります🧭💕

---

## 3) 2025〜最新のC#は「1ファイル実行」が超つよい 🔥

いまのC#は **“1ファイルで動かせる”** 方向にかなり寄ってます。
C# 14 は最新のC#で、.NET 10 で使えます。 ([Microsoft Learn][1])
.NET 10 は 2025年11月に LTS として出ています。 ([Microsoft][2])

そして超重要ポイント👇

### ✅ File-based apps（ファイルだけでアプリ）が公式になった

**`.csproj` なしで**、C#ファイル1枚から build/run/publish までできる仕組みです。 ([Microsoft Learn][3])

---

## 4) C#をスクリプトっぽく使う「3つの型」🧰✨

### A) 1ファイル実行（いちばん今っぽい）🧨

`dotnet run file.cs` でそのまま走ります。 ([Microsoft Learn][3])

さらに短く **`dotnet file.cs`** でもOK。 ([Microsoft Learn][3])

---

### B) Top-level statements（昔の Main を書かない）🧁

Consoleアプリでも、`Program.cs` にそのまま上から書いて動きます。
「JSの1ファイル感」に近くて、学習にも試作にも便利😊

---

### C) .csx / C# Interactive / dotnet-script（“REPL寄り”）🧪

* Visual Studio の C# Interactive
* `.csx` スクリプト
* `dotnet-script`（外部ツール）

この辺は「ちょっと遊ぶ」には便利だけど、今は **A（file-based apps）** が強いです✨
（“スクリプトっぽいのに、そのまま本番へ育てられる”のが大きい💡） ([Microsoft for Developers][4])

---

## 5) まずは体験：1ファイルで「注文合計」を作る ☕🧾

### 🎯やること

* 注文明細から合計を計算
* クーポンがあれば割引
* “手順コード”でOK（まずは速さ優先）🏃‍♀️💨

#### ① `order.cs` を作る

フォルダに `order.cs` を作って、こう書きます👇

```csharp
using System.Text.Json;

var json = """
{
  "items": [
    { "name": "ラテ", "price": 520, "qty": 1 },
    { "name": "マフィン", "price": 380, "qty": 2 }
  ],
  "coupon": "STUDENT10"
}
""";

using var doc = JsonDocument.Parse(json);

var items = doc.RootElement.GetProperty("items");

decimal subtotal = 0;
foreach (var item in items.EnumerateArray())
{
    var price = item.GetProperty("price").GetDecimal();
    var qty = item.GetProperty("qty").GetInt32();
    subtotal += price * qty;
}

var coupon = doc.RootElement.TryGetProperty("coupon", out var c) ? c.GetString() : null;
var discountRate = coupon == "STUDENT10" ? 0.10m : 0m;

var discount = subtotal * discountRate;
var total = subtotal - discount;

Console.WriteLine($"小計: {subtotal}円");
Console.WriteLine($"割引: {discount}円");
Console.WriteLine($"合計: {total}円");
```

#### ② 実行する（PowerShell）

```powershell
dotnet run order.cs
```

これだけで動くのが、今のC#の強みです✨ ([Microsoft Learn][3])

---

## 6) スクリプト言語経験 → C#での対応表（ここ超大事）📌✨

### ✅ Python / PHP の「辞書・配列」感覚

* list → `List<T>`
* dict → `Dictionary<TKey, TValue>`
* “とりあえずJSON” → `System.Text.Json`（まずこれでOK）😌

### ✅ JS/TS の map/filter/reduce

* `map` → `Select`
* `filter` → `Where`
* `reduce` → `Aggregate`

例👇

```csharp
var prices = new[] { 520m, 380m, 380m };
var subtotal = prices.Sum(); // JSでいう reduce 的な感覚✨
```

### ✅ async/await は同じノリでOK 🌙

C#の `async/await` は、JS/TS経験者ならかなり入りやすいです😊
（ただし戻り値が `Task` / `Task<T>` になるのがポイント）

---

## 7) 「スクリプトで書いたものを、設計へ育てる」黄金手順 🥚➡️🐣➡️🐓
 
 スクリプトは速い。でも放置すると事故る💥
 だから **“育て方”を決め打ち**しておくと迷いません🧭✨
 
 ```mermaid
 flowchart LR
     Script["🥚 Script<br/>(1ファイル)"] --> Separate["🐣 Logic分離<br/>(関数化)"]
     Separate --> Project["🐓 Project<br/>(DDD化)"]
     
     subgraph S1 [Step 1: 試作]
       direction TB
       Run[dotnet run] 
     end
     
     subgraph S2 [Step 2: 整理]
       direction TB
       ValueObject[VO追加]
       Tests[Test追加]
     end
     
     Script -.-> S1
     Separate -.-> S2
     
     style Script fill:#ffdfba,stroke:#f80
     style Project fill:#caffbf,stroke:#383,stroke-width:2px
 ```
 
 ### ステップ①：I/O と計算を分ける（最優先）✂️

* JSON読む / DB触る / HTTP叩く → **外側**
* 合計計算 / 割引ルール → **内側**

まずは “計算だけの関数” を作る👇

```csharp
static decimal CalculateTotal(decimal subtotal, string? coupon)
{
    var discountRate = coupon == "STUDENT10" ? 0.10m : 0m;
    return subtotal - (subtotal * discountRate);
}
```

### ステップ②：値オブジェクト化（string/int を信じない）🔒

「円」を `decimal` のまま持つのをやめて、`Money` にする✨

```csharp
public readonly record struct Money(decimal Amount)
{
    public static Money operator +(Money a, Money b) => new(a.Amount + b.Amount);
    public static Money operator *(Money a, int n) => new(a.Amount * n);
}
```

### ステップ③：ルールに名前を付ける（ドメイン語彙）🗣️

`discountRate` じゃなくて
`StudentDiscountPolicy` とかにすると、未来の自分が助かる🥹✨

### ステップ④：テストを1本だけ作る 🧪

スクリプトを育てる“保険”です✅
AIに雛形作らせるのが最強（後述）🤖✨

### ステップ⑤：大きくなったら「プロジェクト化」する 🏗️

file-based apps は **プロジェクトへ変換**できます。
`dotnet project convert file.cs` で `.csproj` を作ってくれます。 ([Microsoft Learn][3])

---

## 8) AI（Copilot等）に手伝わせる“勝ちパターン”🤖🏆

Visual Studio では Copilot が修正提案（ライトバルブ等）に入ってきたりします。 ([Microsoft Learn][5])
Copilot Chat 側には「提案が公開コードに似てるか」などの参照情報も出せます。 ([Microsoft Learn][6])

### ✅ 使い方のコツ：AIには「変換」を頼む

AIはゼロから設計を“決める”のは苦手。
でも **変換・分解・命名・テスト化**は得意です✨

#### そのまま使える指示（コピペOK）📌

* 「この `order.cs` から **ビジネスルールだけ** 抜き出して、**副作用のない関数**にして」
* 「`decimal` を `Money` 値オブジェクトに置き換えて。演算子オーバーロードも用意して」
* 「`CalculateTotal` の **ユニットテスト（xUnit）を3ケース** 作って」
* 「I/O（JSON解析）と計算処理を分離して、`Application` と `Domain` に分ける案を出して」

---

## 9) VS Code派の人へ：最低限これだけ覚えればOK 🧩✨

VS Code なら **C# Dev Kit** を使うと、Solution Explorerやテスト実行がまとまって便利です。 ([Microsoft Learn][7])

（学習・試作は VS Code、ガッツリ開発は Visual Studio、みたいな使い分けもアリ😊）

---

## 10) つまずきポイント集（先回り）⚠️💡

* **スクリプトが巨大化して死ぬ**
  → 「I/O と計算を分離」だけ最初にやる✂️
* **“とりあえずstring”が増えて死ぬ**
  → `Money`, `UserId`, `Email` みたいな“薄い型”を作る🧱
* **AIが勝手に設計を盛ってくる**
  → 「変換だけ頼む」「責務を固定してから頼む」🧭
* **NuGetを最新追従しすぎて壊れる**
  → スクリプトでも、できればバージョン固定が安心😌
  （`#:package` は書けるよ、という話） ([Microsoft Learn][3])

---

## 11) ミニ演習（30〜60分）🎓✨

### 演習A（15分）🧪

1ファイルで「日付→メッセージ」みたいな小ツールを作って `dotnet run file.cs` で実行してみよう。 ([Microsoft for Developers][4])

### 演習B（20分）✂️

さっきの `order.cs` を、

* JSON解析（外側）
* 合計計算（内側）
  に分けて、計算部分を関数にしてね✅

### 演習C（20分）🤖

Copilotにこう頼んで、xUnitテストを作ってもらう🧪

* 「合計計算のテストを3ケース作って（クーポンあり/なし/不正クーポン）」

---

## まとめ 🌸

スクリプト言語的アプローチは、DDDの敵じゃなくて **DDDの“前段階の加速装置”**です🚀
**「動かして理解」→「固まったら設計」** を回すと、一人開発でも迷いにくくなります🧭✨

次に進むときの合言葉はこれ👇
**“スクリプトは鉛筆、DDDはペン入れ”** ✏️➡️🖊️😊

---

必要なら、この第86章の内容に合わせて、次は **「1ファイル試作→最小クリーンアーキテクチャへ変換するテンプレ一式」**（フォルダ構成＋最小コード＋Copilot用プロンプト）も作って渡せますよ📦✨

[1]: https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-14 "What's new in C# 14 | Microsoft Learn"
[2]: https://dotnet.microsoft.com/en-us/platform/support/policy/dotnet-core?utm_source=chatgpt.com "NET and .NET Core official support policy"
[3]: https://learn.microsoft.com/en-us/dotnet/core/sdk/file-based-apps "File-based apps - .NET | Microsoft Learn"
[4]: https://devblogs.microsoft.com/dotnet/announcing-dotnet-run-app/ "Announcing dotnet run app.cs - A simpler way to start with C# and .NET 10 - .NET Blog"
[5]: https://learn.microsoft.com/en-us/visualstudio/releases/2022/release-notes-v17.12?utm_source=chatgpt.com "Visual Studio 2022 version 17.12 Release Notes"
[6]: https://learn.microsoft.com/en-us/visualstudio/ide/visual-studio-github-copilot-chat?view=visualstudio&utm_source=chatgpt.com "About GitHub Copilot Chat in Visual Studio"
[7]: https://learn.microsoft.com/ja-jp/visualstudio/subscriptions/vs-c-sharp-dev-kit?utm_source=chatgpt.com "Visual Studio Code 用 C# 開発キット"
