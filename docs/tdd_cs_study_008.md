# 第08章：VSのテスト実行に慣れる（赤の読み方）🔍

まず「本日時点の最新」だけサクッと押さえるね☺️

* Visual Studio 2026 の最新アップデートは **18.2.0（2026/01/13）**だよ🆕 ([Microsoft Learn][1])
* .NET 10 の最新は **10.0.2（2026/01/13）**だよ🆕 ([xUnit.net][2])
* xUnit は **v3.2.2**、VSアダプタは **3.1.5** が案内されてるよ🧪 ([xUnit.net][3])
* Microsoft.NET.Test.Sdk は **18.0.1（2025/11/11）** が出てるよ🧰

---

## この章でできるようになること🎯💖

* テストが赤くなったときに、**「失敗の種類」を一瞬で分類**できる🙆‍♀️
* 失敗詳細から **「どこが壊れてる？」→「次に何を見る？」** を決められる🕵️‍♀️
* **Debug（デバッグ実行）**で原因箇所までスッと行ける🧑‍💻✨ ([Microsoft Learn][4])

---

## 0) まずは「赤の読み方」テンプレ📌✨

![画像を挿入予定](./picture/tdd_cs_study_008_triangulation.png)

赤が出たら、焦らずこの順で見ればOKだよ🥹💕

1. **どのテスト名が落ちた？**（1テスト1意図が効いてくるやつ🫶）
2. **メッセージ**（Expected/Actual、例外メッセージなど）
3. **スタックトレース**（自分のコードの行番号が出る！）
4. **何を直して、どのテストを再実行する？**（最小の修正で！）

Visual Studio の Test Explorer は、失敗したテストを選ぶと **メッセージとスタックトレース**を表示してくれるよ👀✨ ([Microsoft Learn][5])

---

## 1) Test Explorerの「最低限ここだけ」操作🪟🧪

### 開き方＆実行

* メニューから Test Explorer を開いて、**Run All**（全部実行）でOK🙆‍♀️ ([Microsoft Learn][6])
* テストが見つからないときは、まず **ビルド**してみてね（テスト検出の基本）🏗️ ([Microsoft Learn][5])

### 便利な使い方

* **フィルタ**（名前で絞れる）
* **失敗だけ再実行**（赤が消えるまで回す）
* テストを右クリックして **Run / Debug** できるよ✨ ([Microsoft Learn][6])

---

## 2) 赤の3大パターン（この章の主役）💥🧠

ここを分類できると一気に強くなるよ💪💕

### A. Assert失敗（期待と結果が違う）❌➡️✅

* 典型：Expected と Actual が違う
* 「実装が間違い」か「テスト（仕様）の期待が違う」かを切り分ける✨

### B. 例外で落ちる（エラーが飛んできた）💣

* 典型：NullReferenceException とか InvalidOperationException とか
* スタックトレースで **最初に自分のコードが出る行**が重要👀

### C. タイムアウト（終わらない/遅すぎる）⏳😵

xUnit v3 は **Fact に Timeout を付けられる**し、タイムアウト時は **CancellationToken も使える**よ🧪 ([xUnit.net][7])
（ポイント：タイムアウトしても「強制停止」じゃないケースがあるから、キャンセルに反応する作りが安心だよ🫶） ([xUnit.net][7])

---

## 3) ハンズオン：3種類の失敗を“わざと”起こして読めるようにする👩‍🔬🧪✨

前章で作ったソリューション（App/Tests）に、練習用の超ミニ題材を足すよ🎀

### 3-1) 題材クラス（App側）🧩

```csharp
namespace App;

public class MiniCalc
{
    public int Add(int a, int b) => a + b;

    public int Divide(int a, int b) => a / b;
}
```

---

### 3-2) テスト（Tests側）🧪

```csharp
using App;
using Xunit;

public class MiniCalcTests
{
    [Fact]
    public void Add_2_and_3_should_be_6_demo_assert_fail()
    {
        // わざと間違える：本当は5なのに6を期待する
        var sut = new MiniCalc();
        var result = sut.Add(2, 3);

        Assert.Equal(6, result);
    }

    [Fact]
    public void Divide_by_zero_demo_exception()
    {
        // わざと例外で落とす（0除算）
        var sut = new MiniCalc();
        _ = sut.Divide(10, 0);
    }

    [Fact(Timeout = 200)]
    public async Task Too_slow_demo_timeout()
    {
        // タイムアウト時にキャンセルが通知される（xUnit v3）
        var ct = TestContext.Current.CancellationToken;

        await Task.Delay(TimeSpan.FromSeconds(5), ct);
    }
}
```

> タイムアウト系は「無限ループ」を書くより、こういう **Delay + CancellationToken** が安全でおすすめだよ🧸✨
> xUnit v3 のタイムアウトとキャンセルの話はここが根拠だよ🧪 ([xUnit.net][7])

---

## 4) 実行して“赤”を読む（ここが本番）🔍🚦

### Step 1：Run All する🏃‍♀️💨

3つとも赤になるはず！

### Step 2：1個ずつクリックして詳細を見る👆

Test Explorer の詳細ペインに **メッセージとスタックトレース**が出るよ✨ ([Microsoft Learn][5])

---

## 5) それぞれ「何を読む？」ガイド🧭💖

### A) Assert失敗の読み方✅❌

見る場所はここ👇

* メッセージの **Expected / Actual**
* 「テスト名が何を言ってるか」
* 自分の意図と一致してるか（仕様がズレてない？）

ありがちパターン💡

* 実装が正しいのにテストが間違ってる
* テストが正しいのに実装がズレてる
* そもそも仕様を誤解してた（テストが“仕様書”になる理由ここ🥹）

---

### B) 例外の読み方💥

見る場所はここ👇

* 例外の型（例：NullReferenceException）
* スタックトレースの中で **最初に出てくる自分のコードの行**
* 「入力が悪い？状態が悪い？依存が悪い？」を考える🧠

---

### C) タイムアウトの読み方⏳

見る場所はここ👇

* 「時間がかかりすぎ」なのか「終わらない」なのか
* どこで待ってる？（I/O、ロック、await、ループ…）
* xUnit v3 はタイムアウト時にキャンセルが使えるから、**キャンセルに反応する設計**にすると強いよ🧪 ([xUnit.net][7])

---

## 6) Debug（デバッグ実行）で“真犯人”まで会いに行く🕵️‍♀️🧑‍💻✨

やり方は簡単だよ👇

* Test Explorer でテストを選んで右クリック → **Debug**🧷 ([Microsoft Learn][4])
* ブレークポイントを置いて、ステップ実行で追いかける🔎

---

## 7) AIの使いどころ（この章はここが超おいしい）🤖💖

### 7-1) ログを貼るときの「最小セット」🧺

* 失敗したテスト名
* メッセージ（Expected/Actual or 例外）
* スタックトレース（自分のコードが出てる所まで）

### 7-2) コピペ用プロンプト（そのまま使ってOK）✨

* 「この失敗ログを見て、原因候補を3つ。各候補の確認手順を順番に」
* 「Expected/Actualの差から、仕様の解釈違いの可能性も含めて説明して」
* 「スタックトレースの読み方を、どの行から追うべきかで教えて」

### 7-3) Visual Studio 2026の“テスト失敗→AIでデバッグ”も使えるよ🪄

Visual Studio 2026 では、失敗したテストを右クリックして **Debug with Copilot** みたいな流れ（Debugger Agent）も案内されてるよ🤖🛠️ ([Microsoft Learn][8])
（ただし！最終判断は自分＆テストね😉✅）

---

## 8) 仕上げ課題（提出物つき）🎒✨

### 課題🎀

1. 3つの赤（Assert/例外/タイムアウト）を全部起こす
2. それぞれについて、メモを1行ずつ書く

   * 「失敗の種類」
   * 「最初に見た場所」
   * 「直すなら次に何をする？」

### 提出物📦

* コミット1：練習用の3テスト追加（わざと赤）
* コミット2：それぞれを直して全部グリーン✅（直し方は自由！）

---

## おまけ：テストが見つからない時の“まずこれ”🧯

* まずビルド（テスト検出の基本）🏗️ ([Microsoft Learn][5])
* Theory みたいな動的テストは、状況によって再検出が必要なこともあるよ🌀 ([Microsoft Learn][9])

---

次の章（dotnet test / CLI）に行く前に、もしよければ☺️💕
いま出てる赤ログ（どれでも1個）を貼ってくれたら、いっしょに「読む順番」でサクッと犯人探ししてみよ〜〜〜🔍✨🫶

[1]: https://learn.microsoft.com/en-us/visualstudio/releases/2026/release-notes "Visual Studio 2026 Release Notes | Microsoft Learn"
[2]: https://xunit.net/releases/visualstudio/3.1.5 "Visual Studio adapter 3.1.5 [2025 September 27] | xUnit.net "
[3]: https://xunit.net/ "Home | xUnit.net "
[4]: https://learn.microsoft.com/ja-jp/visualstudio/test/debug-unit-tests-with-test-explorer?view=visualstudio&utm_source=chatgpt.com "テスト エクスプローラーを使用して単体テストをデバッグする"
[5]: https://learn.microsoft.com/en-us/visualstudio/test/run-unit-tests-with-test-explorer?view=visualstudio "Run Unit Tests with Test Explorer - Visual Studio (Windows) | Microsoft Learn"
[6]: https://learn.microsoft.com/ja-jp/visualstudio/test/run-unit-tests-with-test-explorer?view=visualstudio&utm_source=chatgpt.com "テスト エクスプローラーで単体テストを実行する - Visual Studio ..."
[7]: https://xunit.net/docs/getting-started/v3/whats-new "What's New in v3? [2025 August 14] | xUnit.net "
[8]: https://learn.microsoft.com/en-us/visualstudio/releases/2026/release-notes?utm_source=chatgpt.com "Visual Studio 2026 Release Notes"
[9]: https://learn.microsoft.com/en-us/visualstudio/test/test-explorer-faq?view=visualstudio "Review Test Explorer FAQ Issues and Answers - Visual Studio (Windows) | Microsoft Learn"
