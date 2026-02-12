# 第29章：依存ってなに？（時間・乱数・外部）⏰🎲

ここからが「テストしやすい設計」の入口だよ〜！🚪💡
この章は、**テストを壊す“外部要因（依存）”を見つけられる目**を作る回です👀🧪

---

## 0. この章のゴール🎯

![画像を挿入予定](./picture/tdd_cs_study_029_dependency_isolation.png)

読み終わったら、これができるようになるよ😊✨

* 「このコード、何に依存してる？」を**言葉にできる**🗣️
* 依存を **時間⏰ / 乱数🎲 / 外部I/O🌐💾** に分類できる🧺
* “たまに落ちるテスト（フレーク）😵‍💫”が **なぜ起きるか**説明できる
* 自分の題材で **依存リスト**を作れる📝

---

## 1. そもそも「依存」ってなに？🤔🔌

超ざっくり言うと…

> **コードの外側にあって、あなたが自由にコントロールできないもの**
> （そして、テストの結果を不安定にしがちなもの）

代表例はこの3つが鉄板👑

### ✅ 依存の三大カテゴリ
![3 Types of Dependency](./picture/tdd_cs_study_029_dependency_types.png)


* **時間**：今何時？今日何日？締切超えた？⏰📅
* **乱数**：ガチャ、抽選、ランダムID、シャッフル🎲
* **外部**：ファイル、DB、ネット、OS、環境変数、Web API💾🌐🖥️

---

## 2. 依存があると、何が困るの？😵‍💫💥
![Flaky Test](./picture/tdd_cs_study_029_flaky_test.png)


テストが理想的なのはこれ👇

* **いつ実行しても同じ結果（決定性）**🎯
* **速い（サクサク回る）**⚡
* **他と独立してる（順番に依存しない）**🧍‍♀️🧍‍♂️
* **外部が落ちてもテストは落ちない**🛡️

でも依存があると…こうなる😇

* 23:59に走ったら落ちる（翌日になった）🌙➡️🌅
* 乱数でたまに外れる🎲
* CIだけ落ちる（ネット遅い/権限違う/時刻違う）🏗️💥
* 他のテストと同時実行で壊れる（共有状態）🧵💣

ちなみに、xUnitは **テストコレクションを並列実行するのがデフォルト**なので、共有状態やグローバル依存があると事故りやすいよ〜⚠️🧵（設定で無効化もできる）([xunit.net][1])

---

## 3. まずは“依存レーダー”を頭に入れる📡🧠
![Dependency Radar](./picture/tdd_cs_study_029_dependency_radar.png)


コードを見たら、これが出てきた時点で「依存だ！」って反射してOK🙆‍♀️✨

### ⏰ 時間依存あるある

* `DateTime.Now` / `DateTimeOffset.Now`
* `DateTime.UtcNow` / `Stopwatch` / `Task.Delay` / `Thread.Sleep`

### 🎲 乱数依存あるある

* `Random.Shared` / `new Random()`（シードが固定されてない）
* `Guid.NewGuid()`（実質ランダム）

### 🌐💾 外部依存あるある

* `File.ReadAllText` / `File.WriteAllText`
* DBアクセス、HTTP、クラウドSDK
* `Environment.GetEnvironmentVariable`
* OSロケール、タイムゾーン、マシン名、カレントディレクトリ

---

## 4. ミニ題材：推し活アプリの「今日のピックアップ」🎀📦✨

### 4-1. まず“ダメな例”（依存が隠れてる）🙅‍♀️💥
![Hidden Dependency](./picture/tdd_cs_study_029_hidden_dependency.png)


「今日のおすすめグッズをランダムで1個出す」機能を、ついこう書いちゃう👇

```csharp
public sealed class DailyPickup
{
    public string Pick(IReadOnlyList<string> items)
    {
        // 隠れ依存：現在日時
        var today = DateTimeOffset.Now.Date;

        // 隠れ依存：乱数（しかも共有）
        var index = Random.Shared.Next(items.Count);

        return $"{today:yyyy-MM-dd}: {items[index]}";
    }
}
```

これ、テストが超つらい😵‍💫

* 実行日によって文字列が変わる⏰
* 乱数で結果が変わる🎲
* 並列実行で揺れる可能性もある🧵

### 4-2. “フレークなテスト”の例😇🎲

```csharp
using Xunit;

public sealed class DailyPickupTests
{
    [Fact]
    public void Pick_returns_expected_item()
    {
        var sut = new DailyPickup();
        var items = new[] { "アクスタ", "缶バッジ", "ペンライト" };

        var result = sut.Pick(items);

        // これ、当たる日もあれば外れる日もある…😇
        Assert.Contains("アクスタ", result);
    }
}
```

「テストがたまに落ちる」って、メンタル削るやつ…🫠🪓
だからここで **依存を見える化**するよ！

---

## 5. 今日の結論：依存は“悪”じゃない。隠すのが良くない😌🔦

### ✅ 合言葉

* **依存は、外に出す（見える化する）**👀✨
* **中心ロジックは“純粋（ピュア）”に寄せる**🧼
* 外部I/Oは“端っこ（境界）”に寄せる🚪

---

## 6. 依存を見える化する：一番カンタンなやり方（引数で渡す）📦✨
![Dependency Injection (Argument)](./picture/tdd_cs_study_029_inject_dependency.png)


この章では、まだインターフェースもDIも最小でOK🙆‍♀️
まずは **「必要なものを引数にする」** が一番わかりやすいよ！

```csharp
public sealed class DailyPickup
{
    public string Pick(
        IReadOnlyList<string> items,
        DateOnly today,     // ⏰ 時間依存を外に出した
        Random rng)         // 🎲 乱数依存を外に出した
    {
        var index = rng.Next(items.Count);
        return $"{today:yyyy-MM-dd}: {items[index]}";
    }
}
```

### ✅ テストが安定する（決定性）🎯✨

```csharp
using Xunit;

public sealed class DailyPickupTests
{
    [Fact]
    public void Pick_is_deterministic_with_fixed_inputs()
    {
        var sut = new DailyPickup();
        var items = new[] { "アクスタ", "缶バッジ", "ペンライト" };

        var today = new DateOnly(2026, 1, 18);
        var rng = new Random(12345); // シード固定🎲🔒

        var result1 = sut.Pick(items, today, rng);

        // 同じシードを使うなら、同じ順序で再現できる✨
        rng = new Random(12345);
        var result2 = sut.Pick(items, today, rng);

        Assert.Equal(result1, result2);
    }
}
```

> ポイントは「テストが世界を支配できてる」感じになること👑🧪✨
> “今が何時か”も“何が出るか”も、テストが決める！

---

## 7. もう一段いい感じ：.NETの公式な“時間の抽象”TimeProvider⏰🧰

「時間って引数で渡せばいい」でも全然OKなんだけど、
最近の .NET では **TimeProvider** が用意されてるよ〜✨（.NET 8で導入）([Microsoft Learn][2])

* `TimeProvider` を使うと **“時間を差し替え可能”**にできて
* テストで「今」を固定できる🎯

さらに **FakeTimeProvider**（テスト用）も NuGet で用意されてる💖
`Microsoft.Extensions.TimeProvider.Testing` に入ってるよ([Microsoft Learn][3])

> ここは次章以降（依存の差し替え）で本格的に使うけど、
> 「こういう公式の道具がある」って知っておくと安心😊✨

---

## 8. 外部依存（ファイル/ネット/DB）はどう扱う？💾🌐
![Pure Core vs Impure Shell](./picture/tdd_cs_study_029_pure_vs_impure.png)


### ✅ 初心者向けの鉄則（まずこれだけ覚えて）📌

* ユニットテストでは **外部に触れない**（触れるなら別枠）🧪🚫
* ロジックは「データを受け取って返す」に寄せる📦➡️📦
* ファイル読むのは“外側”、計算するのは“中心”に分ける🚪🧠

たとえば…

❌ 中心でファイル読む（テストしにくい）

```csharp
public int LoadAndCount(string path)
{
    var text = File.ReadAllText(path); // 💾外部依存
    return text.Length;
}
```

✅ 外部は外で、中心はピュアに

```csharp
public int CountTextLength(string text) => text.Length;
```

こうするとテストは超楽ちん🎉

---

## 9. 実践ワーク：依存リストを作ろう📝✨（この章の“手を動かす”）

### ワークA：依存を見つける（3分）🔍

次のコードの「依存」を全部書き出して、分類してみてね👇

```csharp
public sealed class ReceiptService
{
    public string CreateReceipt(string customerId)
    {
        var now = DateTimeOffset.Now;          // ?
        var id = Guid.NewGuid().ToString("N"); // ?
        var path = $"receipts/{customerId}.txt";

        File.AppendAllText(path, $"{now:o},{id}\n"); // ?
        return id;
    }
}
```

**答え（例）**✅

* ⏰ 時間：`DateTimeOffset.Now`
* 🎲 乱数：`Guid.NewGuid()`
* 💾 外部：`File.AppendAllText`、ファイルパス（環境差）

---

### ワークB：自分の題材で「依存リスト」を作る（10分）🧠📝
![Dependency Checklist](./picture/tdd_cs_study_029_dependency_list.png)


あなたの今の題材（例：推し活グッズ管理 / カフェ会計）で、これを埋めてみて👇

**依存リスト（テンプレ）**

* ⏰ 時間：例）締切判定、日付表示、期限切れ…
* 🎲 乱数：例）抽選、ID生成、シャッフル…
* 💾 外部I/O：例）ファイル保存、DB、HTTP、設定…
* 🧵 共有状態：例）`static`、シングルトン、キャッシュ…
* 🖥️ 環境差：例）タイムゾーン、カルチャ、パス、権限…

---

## 10. AIの使いどころ（この章は相性いい🤖💖）

### ✅ 依存洗い出しに使うプロンプト例

* 「このコードの依存（時間/乱数/外部I/O）を列挙して、テストが不安定になる理由も説明して」
* 「依存を“引数で渡す形”に直すなら、最小の変更案を出して」
* 「この処理の“境界（I/O）”と“中心ロジック”を分ける案を3つ出して」

AIは“見落とし探し”が得意だから、依存リストの穴埋めにめちゃ便利だよ🧠✨

---

## 11. まとめ🎁✨（この章で一番大事）

* 依存は **時間⏰ / 乱数🎲 / 外部💾🌐** がまず三本柱
* テストが壊れる原因はだいたい **依存が隠れてる**せい
* まずは **引数で外に出す**だけで、テストが安定する🎯
* xUnitは並列実行が絡むので、共有状態やグローバル依存は特に注意🧵⚠️([xunit.net][1])
* .NETには `TimeProvider`（時間の抽象）もあるよ⏰🧰([Microsoft Learn][2])

---

## 次章につながる予告📣✨（第30章）

次は今日見つけた依存を、**“差し替え可能”にする最小の形**を作るよ〜！🔁
「Clockをinterface化」ってやつだね⏰➡️🧩

---

## 参考：この教材で前提にしてる“周辺の最新状況”メモ🧪🛠️

* xUnit v3 は NuGet の `xunit.v3`（例：3.2.2）として提供されてるよ([nuget.org][4])
* .NET 10 系は 2026-01-13 に 10.0.2 のアップデートが出てる([Microsoft for Developers][5])
* Visual Studio 側も .NET 10 / C# 14 を扱う前提の情報が出てる（Insiders/Preview系）([visualstudio.microsoft.com][6])

---

必要なら、この第29章の内容を「推し活グッズ管理①」に直結させて、**“依存リスト → テスト設計 → 次章の差し替え”**まで一気に通す演習にして出すよ🎀🧪✨

[1]: https://xunit.net/docs/config-xunit-runner-json?utm_source=chatgpt.com "Config with xunit.runner.json [2025 July 30]"
[2]: https://learn.microsoft.com/en-us/dotnet/standard/datetime/timeprovider-overview?utm_source=chatgpt.com "What is the TimeProvider class - .NET"
[3]: https://learn.microsoft.com/ja-jp/dotnet/standard/datetime/timeprovider-overview "TimeProvider クラスとは - .NET | Microsoft Learn"
[4]: https://www.nuget.org/packages/xunit.v3 "
        NuGet Gallery
        \| xunit.v3 3.2.2
    "
[5]: https://devblogs.microsoft.com/dotnet/dotnet-and-dotnet-framework-january-2026-servicing-updates/ ".NET and .NET Framework January 2026 servicing releases updates - .NET Blog"
[6]: https://visualstudio.microsoft.com/insiders/ "
	Visual Studio 2026 Insiders - Faster, smarter IDE"
