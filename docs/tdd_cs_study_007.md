# 第07章：Visual Studioでテストが回る土台を作る🏗️

この章のゴールはシンプルだよ〜😊
**「新規ソリューションを作って、テストが1分で実行できる状態にする」** こと！🚀
（この“土台”ができると、次章からのTDDがスイスイ進むよ〜🧡）

---

## この章でできるようになること🎯✨

* ✅ ソリューション（アプリ側＋テスト側）をキレイに分けて作れる
* ✅ xUnitでテストを1本作って、Test Explorerで実行できる
* ✅ 「テストが見つからない😭」を避ける最低限の設定ができる
* ✅ AIにREADMEの雛形を作らせて、学習ログが残せる🤖📝

---

## 今日つくる“最小の形”📦✨（おすすめ構成）

![Solution Structure Folders](./picture/tdd_cs_study_007_structure_folders.png)

フォルダはこうしておくと後でラクだよ〜😊

* src（アプリ側）
* tests（テスト側）

プロジェクト名は例として👇にするね（好きに変えてOK！）

* src：TddPlayground（クラスライブラリ）
* tests：TddPlayground.Tests（xUnit）

---

## Step 1：空のソリューションを作る🧩✨

![Blank Solution Canvas](./picture/tdd_cs_study_007_empty_canvas.png)

![画像を挿入予定](./picture/tdd_cs_study_007_baby_steps.png)

1. Visual Studio を起動🪟✨
2. 「新しいプロジェクトの作成」→ **“空のソリューション”**（Blank Solution）を選ぶ😊
3. ソリューション名：TddPlayground（例）
4. 場所：作業用フォルダ（Git管理するならリポジトリ直下が気持ちいい👍）

---

## Step 2：アプリ側（src）にクラスライブラリを追加📚✨

![Building Blocks Projects](./picture/tdd_cs_study_007_building_blocks.png)

1. ソリューションを右クリック → 「追加」→「新しいプロジェクト」
2. **“クラス ライブラリ”** を選ぶ
3. プロジェクト名：TddPlayground
4. 保存場所：src フォルダの中（ここ大事〜！🫶）

✅ ここで「アプリ側」は **UIじゃなくてロジック置き場** だと思ってね😊
TDDはまずロジックから育てるのがやりやすいよ🧠✨

---

## Step 3：テスト側（tests）にxUnitプロジェクトを追加🧪✨

1. ソリューションを右クリック → 「追加」→「新しいプロジェクト」
2. **“xUnit テスト プロジェクト”** を選ぶ
3. プロジェクト名：TddPlayground.Tests
4. 保存場所：tests フォルダの中📁✨

---

## Step 4：テストからアプリを参照する🔗✨（ここ超重要！）

![Reference Bridge](./picture/tdd_cs_study_007_reference_bridge.png)

テストはアプリの中身を使いたいので、参照を追加するよ😊

1. TddPlayground.Tests を右クリック
2. 「依存関係」→「プロジェクト参照の追加」
3. **TddPlayground にチェック** → OK ✅

これでテストからアプリ側のクラスを呼べるようになるよ〜🎉

---

## Step 5：NuGet（最低限）を確認する🧰✨

![NuGet Toolbox](./picture/tdd_cs_study_007_nuget_toolbox.png)

最近の構成だと、テストがちゃんと見つかるために主にこの3つが効くよ〜😊
（バージョンは“今の最新”の例ね✨）

* Microsoft.NET.Test.Sdk（最新は 18.0.1）([NuGet][1])
* xunit.v3（例：3.2.2）([NuGet][2])
* xunit.runner.visualstudio（例：3.1.5、Test Explorer用）([NuGet][3])

Visual Studioのテンプレが自動で入れてくれることも多いけど、
**xUnit v3で進めたい場合は “xunit.v3” が入ってるか** だけチラ見してね👀✨ ([NuGet][2])

---

## Step 6：最初のテストを1本だけ作る✍️🧪✨

テストプロジェクトに、こういう最小テストを作るよ〜😊
（ファイル名は CalculatorTests.cs とかでOK！）

```csharp
using Xunit;

public class CalculatorTests
{
    [Fact]
    public void TwoPlusTwo_IsFour()
    {
        Assert.Equal(4, 2 + 2);
    }
}
```

---

## Step 7：Test Explorerで実行してみる▶️✨

![Test Explorer Dashboard](./picture/tdd_cs_study_007_test_explorer_dashboard.png)

1. メニューから「テスト」→「テスト エクスプローラー」🔍
2. テストが一覧に出てくるのを確認👀
3. 「すべて実行」▶️✨

✅ 緑になったら勝ち〜〜🎉🎉🎉

---

## Step 8：「赤」をわざと作ってみる🚦❤️（超だいじ！）

![Red Light Failure](./picture/tdd_cs_study_007_red_light_fail.png)

TDDはまず“赤”から始まるので、失敗も体験しとこ😊

```csharp
[Fact]
public void ThisTest_ShouldFail()
{
    Assert.Equal(5, 2 + 2);
}
```

これを実行して、**ちゃんと失敗する**のを確認！💥
失敗が見える＝土台ができてる証拠だよ〜👏✨

---

## Step 9：ミニ実装（アプリ側にクラスを置く）🧱✨

アプリ側（TddPlayground）に Calculator.cs を作ってみよ〜😊

```csharp
namespace TddPlayground;

public class Calculator
{
    public int Add(int a, int b) => a + b;
}
```

次章以降は、こういうのを **テストから育てる** って感じになるよ🪴🧪✨

---

## Step 10：AIでREADMEを“秒で”用意する🤖📝✨

ここはAIがめっちゃ得意！
Copilot / Codexに、こう頼むのが楽だよ〜😊💡

💬 AIへのお願い（コピペOK！）

* 「このソリューションの構成（src/tests）と、Visual Studioでテストを実行する手順をREADME.mdとして短くまとめて。初心者向けで。」

出来たREADMEは、**そのまま貼らずに“自分の言葉で1行だけ追記”**すると学習効果UPだよ🫶✨

---

## 完成チェック✅🎉

ここまでできたら第7章クリア〜！🏁✨

* ✅ src と tests にプロジェクトが分かれてる
* ✅ テストが Test Explorer に表示される
* ✅ “緑（成功）” と “赤（失敗）” の両方が確認できた
* ✅ READMEが1枚ある（短くてOK）

---

## よくある詰まりポイント集🧯💡（最短で助けるよ〜）

### ① テストがTest Explorerに出てこない😵‍💫

* xunit.runner.visualstudio が入ってるか確認してね（Test Explorer連携の要）([NuGet][3])
* Microsoft.NET.Test.Sdk も基本セットだよ〜([NuGet][1])

### ② 実行すると「見つからない」「0 tests」になる🥲

* いったん「ビルド」→「ソリューションのリビルド」🔁✨
* それでもダメなら、NuGetの復元（Restore）✅

### ③ CLIでも動くか不安🥺

次の章で扱うけど、先に安心したいなら
「dotnet test」は公式に “テスト実行コマンド” だよ〜🧡 ([Microsoft Learn][4])

---

## ちょい最新メモ（今の土台が“長持ち”する理由）📌✨

* .NET 10 は LTSで、最新パッチは 10.0.2（2026-01-13）だよ🛡️ ([Microsoft][5])
* Visual Studio 2026 も 2026-01-13 のアップデートが出てるよ〜🧡 ([Microsoft Learn][6])
* C# 14 は “VS 2026 + .NET 10 SDK” で使える前提で案内されてるよ✨ ([Microsoft Learn][7])

---

## 次章につながる一言📣✨

第7章は「走れるコース作り」だよ🏟️✨
次の第8章で、いよいよ **赤の読み方（失敗ログの見方）** を身につけると、TDDが一気に気楽になるよ〜😊🧪💕

必要なら、この第7章に「コミット単位（提出物）」「小テスト」「課題チェック表」まで付けた“授業台本”にもできるよ📘✨

[1]: https://www.nuget.org/packages/microsoft.net.test.sdk?utm_source=chatgpt.com "Microsoft.NET.Test.Sdk 18.0.1"
[2]: https://www.nuget.org/packages/xunit.v3?utm_source=chatgpt.com "xunit.v3 3.2.2"
[3]: https://www.nuget.org/packages/xunit.runner.visualstudio?utm_source=chatgpt.com "xunit.runner.visualstudio 3.1.5"
[4]: https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-test-vstest?utm_source=chatgpt.com "dotnet test command with VSTest - .NET CLI"
[5]: https://dotnet.microsoft.com/en-us/platform/support/policy/dotnet-core?utm_source=chatgpt.com "NET and .NET Core official support policy"
[6]: https://learn.microsoft.com/en-us/visualstudio/releases/2026/release-notes?utm_source=chatgpt.com "Visual Studio 2026 Release Notes"
[7]: https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-14?utm_source=chatgpt.com "What's new in C# 14"
