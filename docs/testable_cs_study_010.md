# 第10章：依存ってなに？newの怖さ（超入門）😳🔗

（いまの最新の土台は **.NET 10（LTS）**で、2026年1月13日時点の最新パッチは **10.0.2** です📌 ([Microsoft][1])
また、最新の **C# 14** は **.NET 10 SDK** や **Visual Studio 2026** で試せます✨ ([Microsoft Learn][2])）

---

## この章のゴール🎯✨

* 「依存（Dependency）」って言葉がふわっとじゃなくなる☺️
* **“怖い new”** と **“安全な new”** を見分けられる👀
* **差し替えできる場所（テストの逃げ道）** を作る発想が持てる🚪🧪

---

## 1) そもそも「依存」ってなに？🤔🧩

超ざっくり言うと…

> **ある処理が、他のモノ（クラス・関数・外部サービス）に頼って動くこと**＝依存

たとえば👇

* 時刻に頼る：`DateTime.Now` 🕰️
* 乱数に頼る：`new Random()` 🎲
* ファイルに頼る：`File.ReadAllText(...)` 🗂️
* Webに頼る：`HttpClient` 🌐
* DBに頼る：`SqlConnection` 🗄️

こういう「頼り先」が、テストを難しくすることが多いんだよね😵‍💫

---

## 2) `new` は悪じゃない🙆‍♀️ でも「場所」が大事📍

## ✅ 安全な `new`（だいたいOK）😊

* `new List<int>()` みたいな **ただの入れ物** 📦
* `new Money(1000)` みたいな **値オブジェクト（ただのデータ）** 💰
* `new StringBuilder()` みたいな **純粋に計算/整形する道具** ✍️

👉 これらは **外の世界（I/O）に触らない** から、テストもしやすい✨

## ⚠️ 怖くなりやすい `new`（要注意）😱

* `new Random()`（結果が揺れる）🎲
* `new HttpClient()`（ネットに行く、遅い/落ちる/変わる）🌐
* `new SqlConnection()`（DB必要、重い）🐘
* `new FileStream()`（ファイル必要、環境依存）🗂️

👉 これらは **I/O（外の世界）に近い** から、**重要ロジックの中で `new` するとテストが地獄**になりやすい👻

---

## 3) 「重要ロジックの中の new」が困る理由💥

## 理由A：テストで“偽物”にできない🎭

`new` しちゃうと、その瞬間に **本物** が確定しちゃうの😭
テストでは「偽物（Fake/Stub）」にしたいのに、差し替えできない💦

## 理由B：環境が必要になって遅い＆不安定🐌🌪️

ネット、DB、ファイル、現在時刻…
テストが **PC環境・ネット状態・時間** に左右されると、失敗が増える😇

## 理由C：変更が怖くなる😵

「メール送る仕組み変えたい」ってなった時、
ロジックの中に `new SmtpClient()` が埋まってると、あちこち壊しがち💣

---

## 4) 体験：`new` が混ざるとテストがつらい😵‍💫💥

## ❌ ダメ寄り例：時間＆乱数が直で混ざってる

```csharp
public class GreetingService
{
    public string BuildMessage(string name)
    {
        var now = DateTime.Now;            // “今”に依存🕰️
        var random = new Random();         // 乱数に依存🎲

        var suffix = random.Next(0, 2) == 0 ? "✨" : "🌸";
        return $"{now:HH:mm} {name}さん、こんにちは{suffix}";
    }
}
```

これ、テストで「結果が毎回変わる」からしんどい😇
**“正しいかどうか”を固定して確かめられない**のが痛いポイント💥

---

## 5) 解決の考え方：「差し替えできる場所」を作る🚪✨

合言葉はこれ👇

> **重要ロジックの中では、外の世界っぽいものを作らない（newしない）**
> **外から“渡してもらう”形にする**

つまり **依存を外に出す**（I/O境界の分離の一部だよ〜📦➡️🌍）

---

## 6) “渡してもらう”に変えるとどうなる？🎁🧪


![testable_cs_study_010_hard_vs_soft_dependency.png](./picture/testable_cs_study_010_hard_vs_soft_dependency.png)

## ✅ 改善例：時刻と乱数を「受け取る」形に

```csharp
public interface IClock
{
    DateTime Now { get; }
}

public interface IRandom
{
    int Next(int minValue, int maxValue);
}

public class GreetingService
{
    private readonly IClock _clock;
    private readonly IRandom _random;

    public GreetingService(IClock clock, IRandom random)
    {
        _clock = clock;
        _random = random;
    }

    public string BuildMessage(string name)
    {
        var now = _clock.Now;
        var suffix = _random.Next(0, 2) == 0 ? "✨" : "🌸";
        return $"{now:HH:mm} {name}さん、こんにちは{suffix}";
    }
}
```

## テスト用の“固定”実装（Fake）🧸

```csharp
public sealed class FixedClock : IClock
{
    public DateTime Now { get; }
    public FixedClock(DateTime now) => Now = now;
}

public sealed class FixedRandom : IRandom
{
    private readonly int _value;
    public FixedRandom(int value) => _value = value;
    public int Next(int minValue, int maxValue) => _value;
}
```

## テストが安定する🎉（例：xUnitっぽい書き方）

```csharp
[Fact]
public void BuildMessage_時間と乱数を固定できる()
{
    var clock = new FixedClock(new DateTime(2026, 1, 16, 9, 0, 0));
    var random = new FixedRandom(0); // 0なら✨に寄せる
    var sut = new GreetingService(clock, random);

    var msg = sut.BuildMessage("こみやんま");

    Assert.Equal("09:00 こみやんまさん、こんにちは✨", msg);
}
```

やったー！これで **“毎回同じ結果”** にできるから、テストが超ラクになる🥳💖

---

## 7) じゃあ `new` はどこでやるの？🏗️📍

答えはシンプル👇

> **外側（アプリ起動時とか）でまとめて new して、内側（重要ロジック）に渡す**

たとえば雰囲気だけ👇（次章でちゃんとやるよ✌️）

```csharp
// アプリの外側（入口）で本物を作って渡すイメージ
var service = new GreetingService(new SystemClock(), new SystemRandom());
```

ここがのちに **“組み立て場所（Composition Root）”** って呼ばれる考え方に繋がるよ🏗️✨（第22章でまた出る！）

---

## 8) AI（Copilot/Codex）に手伝わせるコツ🤖💡

AIにお願いするときは「依存探し」が相性いいよ〜！

おすすめプロンプト例👇📝✨

* 「このクラスの依存（I/O、時刻、乱数、外部通信）を列挙して」
* 「テストしにくい理由を3つ指摘して、改善案を出して」
* 「`new` を内側から外へ移動するリファクタ手順を提案して」
* 「インターフェースを最小で切るならどんな形？」

⚠️注意：AIはときどき「何でも抽象化しよう」としがち😇
**“重要ロジックのテストに必要な分だけ”** に絞るのがコツだよ🎯

---

## 9) よくあるQ&A💬😊

## Q1. 「全部 `new` しちゃダメなの？」

A. 全然そんなことないよ🙆‍♀️
**“外の世界っぽい依存”を重要ロジックに混ぜない**のがポイント✨

## Q2. 「インターフェース増やしすぎになりそう…」

A. それ正解の感覚！👏
まずは **困ったものだけ**（時刻・乱数・ファイル・HTTP・DB）からでOK🧩

## Q3. 「static（`DateTime.Now` とか）も同じ？」

A. うん、同じ“怖さ”枠だよ😈
**差し替え不能**になりやすいから、境界として外に逃がすと安定する🧪✨

---

## 10) 練習問題✍️🧠（ミニでいこ！）

## 問1：この中で「怖い依存」はどれ？👀

```csharp
var list = new List<int>();
var now = DateTime.Now;
var rng = new Random();
var text = File.ReadAllText("a.txt");
```

✅答え：`DateTime.Now` 🕰️ / `new Random()` 🎲 / `File.ReadAllText` 🗂️ が「怖い」寄り！
`new List<int>()` はだいたい安全📦✨

---

## 問2：次を“テストしやすく”するには？🎯

```csharp
public bool IsCampaignDay()
{
    return DateTime.Now.DayOfWeek == DayOfWeek.Friday;
}
```

✅改善案（どれでもOK）

* `DateTime now` を引数で受け取る🫶
* `IClock` を受け取る🧩（おすすめ）
* `Func<DateTime>` を受け取る（最小テク）⚡

---

## 問3：「new を外へ」の一言メモ📌

* **内側（ルール/判断）**：できるだけ“作らない・触らない”📦
* **外側（I/O/入口）**：本物を作ってつなぐ🌍🔌

---

## まとめ🎀✨

* 依存＝「処理が頼ってる相手」だよ🔗
* `new` は悪じゃないけど、**重要ロジックの中で I/O寄りを new すると差し替え不能**になりやすい😱
* 解決は「差し替えできる場所」を作ること🚪✨（外から渡す！）

次章（第11章）はいよいよ **DIの最小：コンストラクタ注入**✉️✨
この章の「外から渡す」が、そのまま気持ちよく繋がるよ〜🥳💖

[1]: https://dotnet.microsoft.com/ja-jp/platform/support/policy?utm_source=chatgpt.com "公式の .NET サポート ポリシー | .NET"
[2]: https://learn.microsoft.com/ja-jp/dotnet/csharp/whats-new/csharp-14?utm_source=chatgpt.com "C# 14 の新機能"
