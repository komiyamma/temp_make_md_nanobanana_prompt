# 第23章：小さなアプリで総復習（ConsoleでOK）🎮✨

この章は「**I/Oを外に出す**」を、**小さな完成品**で体に染み込ませる回だよ〜！🧠💖
今日の時点だと、.NET 10 は最新パッチが **10.0.2（2026-01-13）**で、SDK も **10.0.101** が出てるよ📌 ([Microsoft][1])
（そして Visual Studio 2026 も安定版が出てる〜！🎉 2026-01-13 に 18.2.0 が出てるよ） ([Microsoft Learn][2])
C# は **C# 14** が .NET 10 / Visual Studio 2026 で使えるよ〜🧩 ([Microsoft Learn][3])

---

## 23.1 今日つくるミニアプリ：英単語クイズ（ミニ）📚🎯

**動きのイメージ**👇

* 「開始！」→ 3問出る
* ユーザーが入力
* 正解/不正解を表示
* 最後にスコア表示

ポイントはこれだけ！✨

* 入力/表示（Console）＝ **I/O（外側）** 🖥️🚪
* 出題データ（問題リスト）＝ **交換可能**にする 🧩🔁
* 乱数でシャッフル＝ **境界**（IRandom）🎲🚧
* まとめると「テストで全部差し替えできる」🧪🎭

---

## 23.2 設計の地図（超ざっくり）🗺️😊

![testable_cs_study_023_architecture_map.png](./picture/testable_cs_study_023_architecture_map.png)

![testable_cs_study_023_mini_app_arch.png](./picture/testable_cs_study_023_mini_app_arch.png)

![testable_cs_study_023_console_layers.png](./picture/testable_cs_study_023_console_layers.png)

「**内側（ルール）**」と「**外側（I/O）**」を分けるよ📦↔️🌍

* **内側（テストしやすい）**

  * Question（問題）
  * QuizGame（進行役。I/Oはインターフェース越し）
  * 判定ロジック（文字比較など）

* **外側（本物I/O）**

  * SystemConsole（Consoleを叩く実装）
  * InMemoryQuestionSource（問題の供給）
  * DotNetRandom（Randomの実装）

* **組み立て（Composition Root）**

  * Program.cs に「本物の接続」を寄せる🏗️✨

---

## 23.3 ソリューション構成（おすすめ）📦✨

プロジェクトを **3つ**に分けるよ〜（これが “分離” の練習にちょうどいい！）💪😊

* `QuizApp.Core`（クイズの中身：ロジックとインターフェース）
* `QuizApp.ConsoleApp`（コンソール実装：本物I/O）
* `QuizApp.Tests`（テスト：Fake/Stubで検証）

## CLIで作る場合（VS Code派でもOK）⌨️✨

```powershell
mkdir QuizApp
cd QuizApp

dotnet new sln -n QuizApp

dotnet new classlib -n QuizApp.Core
dotnet new console  -n QuizApp.ConsoleApp
dotnet new xunit    -n QuizApp.Tests

dotnet sln add .\QuizApp.Core\QuizApp.Core.csproj
dotnet sln add .\QuizApp.ConsoleApp\QuizApp.ConsoleApp.csproj
dotnet sln add .\QuizApp.Tests\QuizApp.Tests.csproj

dotnet add .\QuizApp.ConsoleApp\QuizApp.ConsoleApp.csproj reference .\QuizApp.Core\QuizApp.Core.csproj
dotnet add .\QuizApp.Tests\QuizApp.Tests.csproj      reference .\QuizApp.Core\QuizApp.Core.csproj
```

## Visual Studio派の場合 🧑‍💻✨

* 「空のソリューション」作成
* プロジェクトを3つ追加（Class Library / Console / xUnit Test）
* 参照（Console→Core、Tests→Core）を追加

---

## 23.4 Core（内側）を書く：I/Oは “形” だけにする🧩🚧

## ① ドメイン：Question

`QuizApp.Core` に `Question.cs` を作るよ📄✨

```csharp
namespace QuizApp.Core;

public sealed record Question(string Prompt, string Answer);
```

## ② 境界（インターフェース）を定義

`IConsole.cs`（入出力の境界）🖥️🚪

```csharp
namespace QuizApp.Core;

public interface IConsole
{
    void WriteLine(string message);
    string? ReadLine();
}
```

`IQuestionSource.cs`（問題供給の境界）📚🚪

```csharp
namespace QuizApp.Core;

public interface IQuestionSource
{
    IReadOnlyList<Question> GetQuestions();
}
```

`IRandom.cs`（乱数の境界）🎲🚪

```csharp
namespace QuizApp.Core;

public interface IRandom
{
    int Next(int maxExclusive);
}
```

## ③ 進行役（ユースケース）：QuizGame

![testable_cs_study_023_game_master.png](./picture/testable_cs_study_023_game_master.png)

`QuizGame.cs` を作るよ🎮✨
「**Consoleを直接触らない**」で、IConsole 経由にするのがキモ！💡

```csharp
namespace QuizApp.Core;

public sealed record QuizResult(int Total, int Correct);

public sealed class QuizGame
{
    private readonly IConsole _console;
    private readonly IQuestionSource _source;
    private readonly IRandom _random;

    public QuizGame(IConsole console, IQuestionSource source, IRandom random)
    {
        _console = console;
        _source = source;
        _random = random;
    }

    public QuizResult Play(int count)
    {
        var questions = _source.GetQuestions().ToList();
        Shuffle(questions, _random);

        var total = Math.Min(count, questions.Count);
        var correct = 0;

        _console.WriteLine("🎉 ミニ英単語クイズ開始！ 🎉");
        _console.WriteLine($"全部で {total} 問だよ〜✍️");

        for (var i = 0; i < total; i++)
        {
            var q = questions[i];

            _console.WriteLine("");
            _console.WriteLine($"Q{i + 1}: {q.Prompt}");

            var input = (_console.ReadLine() ?? "").Trim();

            if (IsCorrect(input, q.Answer))
            {
                correct++;
                _console.WriteLine("✅ 正解〜！えらいっ👏✨");
            }
            else
            {
                _console.WriteLine($"❌ ざんねん！正解は「{q.Answer}」だよ〜😇");
            }
        }

        _console.WriteLine("");
        _console.WriteLine($"🎯 結果: {correct}/{total} 正解！");
        return new QuizResult(total, correct);
    }

    private static bool IsCorrect(string input, string answer)
        => string.Equals(input.Trim(), answer.Trim(), StringComparison.OrdinalIgnoreCase);

    private static void Shuffle<T>(IList<T> items, IRandom random)
    {
        // Fisher–Yates shuffle
        for (int i = items.Count - 1; i > 0; i--)
        {
            int j = random.Next(i + 1);
            (items[i], items[j]) = (items[j], items[i]);
        }
    }
}
```

ここでの嬉しいポイント💖

* `QuizGame` は **Console/Random/問題供給**を「外からもらう」
* だからテストで **Fake/Stub**に差し替えできる🎭✨

---

## 23.5 Console側（外側）を書く：本物I/Oを実装する🔌🖥️

`QuizApp.ConsoleApp` に実装を置くよ〜！

## ① SystemConsole（本物Console）

```csharp
using QuizApp.Core;

namespace QuizApp.ConsoleApp;

public sealed class SystemConsole : IConsole
{
    public void WriteLine(string message) => Console.WriteLine(message);
    public string? ReadLine() => Console.ReadLine();
}
```

## ② 問題の供給：InMemoryQuestionSource

まずはベタ書きでOK（小さく完成させるのが正義💪✨）

```csharp
using QuizApp.Core;

namespace QuizApp.ConsoleApp;

public sealed class InMemoryQuestionSource : IQuestionSource
{
    private static readonly Question[] Questions =
    {
        new("apple = ?", "りんご"),
        new("cat = ?", "ねこ"),
        new("book = ?", "ほん"),
        new("water = ?", "みず"),
        new("sun = ?", "たいよう"),
    };

    public IReadOnlyList<Question> GetQuestions() => Questions;
}
```

## ③ 乱数：DotNetRandom

```csharp
using QuizApp.Core;

namespace QuizApp.ConsoleApp;

public sealed class DotNetRandom : IRandom
{
    private readonly Random _random = new();

    public int Next(int maxExclusive) => _random.Next(maxExclusive);
}
```

---

## 23.6 Composition Root（組み立て）：Program.cs に集める🏗️✨

![testable_cs_study_023_program_wiring.png](./picture/testable_cs_study_023_program_wiring.png)

`Program.cs` は「配線するだけ」🔌
ここに “本物” を集めるのがコツだよ〜！📍😊

```csharp
using QuizApp.Core;
using QuizApp.ConsoleApp;

IConsole console = new SystemConsole();
IQuestionSource source = new InMemoryQuestionSource();
IRandom random = new DotNetRandom();

var game = new QuizGame(console, source, random);
game.Play(count: 3);

console.WriteLine("👋 またね〜！");
```

これで実行すると、ちゃんとクイズが動くはず！🎉🎮

---

## 23.7 テストを書く：Fake差し替えで “速い・安定” を体感🧪⚡

![testable_cs_study_023_test_setup_fakes.png](./picture/testable_cs_study_023_test_setup_fakes.png)

ここが今日のメインイベント🥳✨
`QuizApp.Tests` に Fake/Stub を置いて、`QuizGame` をテストするよ！

## xUnit について（2026の最新寄り）🧪

xUnit v3 では **`xunit.v3`** がコアで、`dotnet test` や VS の Test Explorer で回すには **`xunit.runner.visualstudio`** を入れるのが定番だよ📌 ([xUnit.net][4])

> ※ Visual Studio のテンプレが v2 のこともあるけど、仕組みとしては「テストフレームワーク + VSTestアダプタ」って覚えればOK🙆‍♀️✨

## ① FakeConsole（入力を流して、出力を記録する）🎭

```csharp
using QuizApp.Core;

namespace QuizApp.Tests;

public sealed class FakeConsole : IConsole
{
    private readonly Queue<string?> _inputs;

    public List<string> Outputs { get; } = new();

    public FakeConsole(IEnumerable<string?> inputs)
    {
        _inputs = new Queue<string?>(inputs);
    }

    public void WriteLine(string message) => Outputs.Add(message);

    public string? ReadLine()
        => _inputs.Count == 0 ? null : _inputs.Dequeue();
}
```

## ② StubQuestionSource（問題を固定で返す）📌

```csharp
using QuizApp.Core;

namespace QuizApp.Tests;

public sealed class StubQuestionSource : IQuestionSource
{
    private readonly IReadOnlyList<Question> _questions;

    public StubQuestionSource(params Question[] questions)
    {
        _questions = questions;
    }

    public IReadOnlyList<Question> GetQuestions() => _questions;
}
```

## ③ DeterministicRandom（シャッフルを固定化）🎲➡️📌

```csharp
using QuizApp.Core;

namespace QuizApp.Tests;

public sealed class DeterministicRandom : IRandom
{
    private readonly Queue<int> _values;

    public DeterministicRandom(IEnumerable<int> values)
    {
        _values = new Queue<int>(values);
    }

    public int Next(int maxExclusive)
    {
        if (maxExclusive <= 0) return 0;
        if (_values.Count == 0) return 0;

        var v = _values.Dequeue();
        if (v < 0) v = -v;
        return v % maxExclusive;
    }
}
```

## ④ テスト本体：正解数が合うかを見る✅

```csharp
using QuizApp.Core;
using Xunit;

namespace QuizApp.Tests;

public class QuizGameTests
{
    [Fact]
    public void Play_WhenAnswersAreCorrect_ReturnsCorrectScore()
    {
        // Arrange
        var console = new FakeConsole(new[] { "りんご", "ねこ" }); // 入力2回分
        var source = new StubQuestionSource(
            new Question("apple = ?", "りんご"),
            new Question("cat = ?", "ねこ")
        );

        // シャッフルで順番が変わらないように 0 連打（実質そのまま）
        var random = new DeterministicRandom(new[] { 0, 0, 0, 0 });

        var game = new QuizGame(console, source, random);

        // Act
        var result = game.Play(count: 2);

        // Assert
        Assert.Equal(2, result.Total);
        Assert.Equal(2, result.Correct);

        // 出力も “ちょい確認” できる（UIの完全一致はやりすぎ注意⚠️）
        Assert.Contains(console.Outputs, x => x.Contains("ミニ英単語クイズ開始"));
        Assert.Contains(console.Outputs, x => x.Contains("結果: 2/2"));
    }
}
```

✅ これで、Consoleがなくてもテストが回る！
✅ 乱数が入ってても、揺れない！
✅ 外部環境に依存しない！

これが「I/O境界の分離」の勝ちパターンだよ〜🏆✨

---

## 23.8 よくあるミスあるある 😵‍💫💥（先回りで回避！）

![testable_cs_study_023_direct_access_fail.png](./picture/testable_cs_study_023_direct_access_fail.png)

* **ロジックの中で `Console.ReadLine()` を直接呼ぶ** → テスト不能😇
* **Randomを直接 new して使う** → テストが揺れる🌪️
* **テストで UI 文言を完全一致で縛りすぎる** → 直したいのに直せない牢獄🫠

  * 文字は `Contains` くらいがちょうどいいこと多いよ〜😊

---

## 23.9 Copilot/Codexの使いどころ🤖💡（この章向け）

おすすめの頼み方（そのままコピペでOK）👇

* 「`IConsole` に対する `FakeConsole` を、入力キューと出力ログ付きで作って」🧾
* 「この `QuizGame` に対する xUnit のテストを、Arrange/Act/Assert で書いて」🧱
* 「シャッフルがテストで揺れるので、`IRandom` を差し替え可能にしたい。最小の設計を提案して」🎲

⚠️ ただし注意！
AIが作るコードは、ときどき **境界を破ってくる**（平気で Console直呼びに戻す）ので、
「I/Oはインターフェース越し！」って合言葉でチェックしてね🔍✨

---

## 23.10 練習問題（ミニ）✍️✨

できそうなのからでOK〜！😊💖

1. 問題数をユーザーに選ばせる（でも `ReadLine()` は IConsole 経由ね！）🎚️
2. 正解時にスコアを +10、不正解は +0 にして、最後に点数表示💯
3. `IQuestionSource` をもう1個作って「ファイルから読み込む版」にしてみる🗂️（第16章の復習✨）
4. 「もう一回やる？」でループさせる（無限ループ注意😆）

---

## この章のまとめ 🎀✨

* 小さくても「完成品」を作ると、分離の意味が一気に腑に落ちる🎉
* **I/Oは外へ、ルールは中へ**📦➡️🌍
* Fake/Stub/Deterministicで、テストが **速くて安定**になる🧪⚡

---

次の章（第24章）は、ここまで作った設計を **AIにレビューさせるチェックリスト**にしていくよ🤖✅
このクイズアプリ、そこにピッタリの素材だから、そのまま持っていこう〜！🚀💖

[1]: https://dotnet.microsoft.com/en-US/download/dotnet/10.0 "Download .NET 10.0 (Linux, macOS, and Windows) | .NET"
[2]: https://learn.microsoft.com/en-us/visualstudio/releases/2026/release-history "Visual Studio Release History | Microsoft Learn"
[3]: https://learn.microsoft.com/ja-jp/dotnet/csharp/whats-new/csharp-14 "C# 14 の新機能 | Microsoft Learn"
[4]: https://xunit.net/docs/getting-started/netcore/cmdline?utm_source=chatgpt.com "Getting Started with xUnit.net v3 [2025 August 13]"
