# 第06章：最小サンプルで掴む「分離」🧪✨

（税計算ロジック🧮＝ピュア／レシート出力🧾＝I/O を分けてみるよ！）

---

## この章でできるようになること 🎯💖

* 「ここがI/Oだ！」を見抜けるようになる👀🔍
* **混ざってるコードはテストしにくい**を体験する😵‍💫💥
* **分けたらテストが一瞬**を体験する⚡🎉
* “分け方”の最小テンプレ（考え方）を持ち帰る🧰✨

---

## 1) まずは「混ぜるとつらい」例 😇➡️😱

![testable_cs_study_006_bad_mix_blender.png](./picture/testable_cs_study_006_bad_mix_blender.png)

やりがちな例：**税計算しつつ、そのままレシートを書き出す**🧾🗂️
こういうの、動くんだけど…テストがしんどい💦

```csharp
using System;
using System.IO;
using System.Globalization;

public sealed class ReceiptService_Bad
{
    public void CreateReceiptAndSave(decimal subtotal, decimal taxRate, string filePath)
    {
        // 税計算（本来はピュアにできる）
        var tax = Math.Round(subtotal * taxRate, 0, MidpointRounding.AwayFromZero);
        var total = subtotal + tax;

        // レシート文字列（ここもピュア寄りにできる）
        var now = DateTime.Now; // ← “今”はI/Oっぽい（外の世界）
        var receipt =
            $"---- RECEIPT ----{Environment.NewLine}" +
            $"Date: {now:yyyy-MM-dd HH:mm}{Environment.NewLine}" +
            $"Subtotal: {subtotal.ToString("C", CultureInfo.CurrentCulture)}{Environment.NewLine}" +
            $"Tax: {tax.ToString("C", CultureInfo.CurrentCulture)}{Environment.NewLine}" +
            $"Total: {total.ToString("C", CultureInfo.CurrentCulture)}{Environment.NewLine}" +
            $"-----------------{Environment.NewLine}";

        // 出力（I/Oのど真ん中）
        File.WriteAllText(filePath, receipt); // ←I/O
    }
}
```

## これが何でつらいの？😵‍💫💥

* `DateTime.Now` が入ってると、毎回結果が変わる🕰️🌪️
* `File.WriteAllText` が入ってると、**ファイル環境**に依存する🗂️💥
* 結果：**「税計算だけ」確かめたいのに、ファイルや時刻まで巻き込まれる**😇🔫

---

## 2) 分離の合言葉：「ルールは中へ、I/Oは外へ」📦➡️🌍✨


![testable_cs_study_006_scissors_separation.png](./picture/testable_cs_study_006_scissors_separation.png)

ここで分けたいものは2つ👇

* **税計算（ルール）**＝同じ入力なら同じ出力🧮🌿（ピュア）
* **レシート出力（I/O）**＝ファイル・画面・プリンタなど🧾🗂️（外の世界）

---

## 3) “ピュアな核”を作る（税計算）🧮🌿

![testable_cs_study_006_pure_calculator_robot.png](./picture/testable_cs_study_006_pure_calculator_robot.png)

まずは「税計算だけ」を **純粋関数**にしちゃうよ✨
入力：`subtotal`, `taxRate` → 出力：`tax`, `total`（それだけ！）

```csharp
using System;

public static class TaxCalculator
{
    public static (decimal tax, decimal total) Calculate(decimal subtotal, decimal taxRate)
    {
        var tax = Math.Round(subtotal * taxRate, 0, MidpointRounding.AwayFromZero);
        var total = subtotal + tax;
        return (tax, total);
    }
}
```

✅ これで税計算は **ファイルも時刻も関係ない**🎉
→ テストが超やりやすくなる土台できた💖

---

## 4) I/O（レシート出力）を “境界” に押し出す🚧🧾

![testable_cs_study_006_interface_boundary_slot.png](./picture/testable_cs_study_006_interface_boundary_slot.png)

次に、出力は「差し替えできる形」にするよ🧩✨
最小のやり方：**インターフェース1個**で包む！

```csharp
public interface IReceiptSink
{
    void Write(string receiptText);
}
```

ファイルに書く本物実装（I/O担当）🗂️👇

```csharp
using System.IO;

public sealed class FileReceiptSink : IReceiptSink
{
    private readonly string _filePath;

    public FileReceiptSink(string filePath)
    {
        _filePath = filePath;
    }

    public void Write(string receiptText)
    {
        File.WriteAllText(_filePath, receiptText);
    }
}
```

---

## 5) “組み立て役”を作る（ルール＋I/Oを接続）🔌✨


![testable_cs_study_006_assembly_lego.png](./picture/testable_cs_study_006_assembly_lego.png)

税計算（ピュア）と、出力（I/O）を **混ぜずに接続**する場所を作るよ😊

```csharp
using System;
using System.Globalization;

public sealed class ReceiptService
{
    private readonly IReceiptSink _sink;

    public ReceiptService(IReceiptSink sink)
    {
        _sink = sink;
    }

    public void CreateReceipt(decimal subtotal, decimal taxRate, DateTime now)
    {
        // ルール（ピュア）を呼ぶ
        var (tax, total) = TaxCalculator.Calculate(subtotal, taxRate);

        // 文字列化（ここは “ピュア寄り”。nowを引数でもらえば安定！）
        var receipt =
            $"---- RECEIPT ----{Environment.NewLine}" +
            $"Date: {now:yyyy-MM-dd HH:mm}{Environment.NewLine}" +
            $"Subtotal: {subtotal.ToString("C", CultureInfo.CurrentCulture)}{Environment.NewLine}" +
            $"Tax: {tax.ToString("C", CultureInfo.CurrentCulture)}{Environment.NewLine}" +
            $"Total: {total.ToString("C", CultureInfo.CurrentCulture)}{Environment.NewLine}" +
            $"-----------------{Environment.NewLine}";

        // I/Oは境界の向こうへ
        _sink.Write(receipt);
    }
}
```

ポイントはここ👇💡

* `DateTime.Now` を **中で呼ばない**（外から `now` を渡す）🕰️➡️📦
* `File.WriteAllText` を **中で呼ばない**（`IReceiptSink` に任せる）🗂️➡️🚪

---

## 6) これで「一瞬でテストできる」体験🎉⚡

![testable_cs_study_006_fake_printer_bear.png](./picture/testable_cs_study_006_fake_printer_bear.png)

ファイルは使わず、メモリに溜める Fake を作っちゃう🧸✨

```csharp
using System.Collections.Generic;

public sealed class MemoryReceiptSink : IReceiptSink
{
    public List<string> Written { get; } = new();

    public void Write(string receiptText)
    {
        Written.Add(receiptText);
    }
}
```

そして「税計算とレシート生成の結果」をサクッと確認できる🥳
（テストフレームワークの詳しいセットアップは第8章でやる想定で、ここは最小で✨）

```csharp
using System;

public static class MiniCheck
{
    public static void Run()
    {
        var sink = new MemoryReceiptSink();
        var service = new ReceiptService(sink);

        service.CreateReceipt(
            subtotal: 1000m,
            taxRate: 0.1m,
            now: new DateTime(2026, 1, 16, 12, 0, 0)
        );

        // ここでファイルなしで結果を見れる！
        var text = sink.Written[0];

        if (!text.Contains("Total"))
            throw new Exception("Total が出てないよ💦");

        if (!text.Contains("¥") && !text.Contains("￥"))
            Console.WriteLine("通貨記号は環境によって変わるよ〜😊（ここはゆるく見る）");
    }
}
```

🎉 **ファイルも時刻も固定できて、結果が安定！**
→ 「テストしやすい」ってこういうことだよ〜💖

---

## 7) まとめ：この章の “最小パターン”✅✨

![testable_cs_study_006_separation_pattern_icons.png](./picture/testable_cs_study_006_separation_pattern_icons.png)

頭の中はこれだけでOK🧠💡

* ① **ピュア**：計算・判定・変換（同じ入力→同じ出力）🧮🌿
* ② **I/O**：ファイル・DB・HTTP・時刻・乱数・UI 🗂️🌐🕰️🎲🖥️
* ③ ②は **インターフェースで包んで外へ** 🚧🧩
* ④ “今”みたいな揺れるものは **引数でもらう** 🕰️➡️📦

---

## 8) AI（Copilot/Codex）に手伝わせるプロンプト例 🤖💡

そのままコピペで使えるやつ置いとくね📝✨

* 「このメソッドの中から **I/O（File/DateTime/Http/DB）部分**を見つけて、インターフェースに分離して」🔍🚪
* 「税計算部分を **純粋関数**にして、引数と戻り値だけにして」🧮🌿
* 「`IReceiptSink` の Fake 実装（メモリに保存）を作って、呼ばれた内容を検査できるようにして」🧸✅

⚠️注意：AIが**分離しすぎ**（不要な抽象化）を作りがちだから、最小で止めるのがコツだよ😊✋

---

## 9) ミニ課題（手を動かすやつ）✍️🎮

![testable_cs_study_006_exercise_markers.png](./picture/testable_cs_study_006_exercise_markers.png)

## 課題A🧪：境界の発見

上の “Bad” コードから、I/Oっぽい行に 🔥 マークを自分で付けてみて！
（例：`DateTime.Now`, `File.WriteAllText`）

## 課題B🧩：出力先を増やす

`ConsoleReceiptSink` を作って、コンソールにも出せるようにしてみよ🖥️✨
（インターフェースが効いてると、追加がラク！）

## 課題C🕰️：時刻を固定

`now` を必ず引数で受け取るようにして、出力が毎回同じになるのを確認✅

---

## 最新メモ（2026年1月時点）🆕✨

* .NET は **.NET 10** が最新のLTSで、2026-01-13 の 10.0.2 が配布されてるよ📦✨ ([Microsoft][1])
* C# は **C# 14** が最新で、.NET 10 でサポートされてるよ🎯 ([Microsoft Learn][2])
* Visual Studio も **Visual Studio 2026** の情報が公開されてるよ🛠️✨ ([Microsoft Learn][3])

---

次の第7章では「テストの種類（単体/結合/E2E）」を“ゆるく”整理して、**まずどこを固めると幸せか**を一緒に掴みにいこ〜😊💖

[1]: https://dotnet.microsoft.com/en-us/download/dotnet?utm_source=chatgpt.com "Browse all .NET versions to download | .NET"
[2]: https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-14?utm_source=chatgpt.com "What's new in C# 14"
[3]: https://learn.microsoft.com/en-us/visualstudio/releases/2026/release-notes?utm_source=chatgpt.com "Visual Studio 2026 Release Notes"
