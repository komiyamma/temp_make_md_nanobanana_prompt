# 第08章：C#のテスト基盤を用意しよう（Windows/VS）🛠️✨

この章のゴールはコレだよ〜！🎯✨
**「テストを書いて、Test Explorerで実行できて、つまずいた時に直せる」**ところまで一気にいきます😊💕

---

## 0) いまの “最新” テスト環境ざっくり地図 🗺️✨

* **C# は “C# 14” が最新**（.NET 10 対応）だよ〜🆕✨ ([Microsoft Learn][1])
* **.NET は 2026/1/9 時点で .NET 10.0.2 / 9.0.12 / 8.0.23** のサービスリリースが出てるよ🧯✨ ([Microsoft for Developers][2])
* **Visual Studio 2026** の情報・更新も出てる（テスト/カバレッジ周りも強化）🧰✨ ([Microsoft Learn][3])

---

## 1) まず “正しい形” のソリューションを作る 📦✨

![testable_cs_study_008_solution_structure.png](./picture/testable_cs_study_008_solution_structure.png)

テストは「本体プロジェクト」と「テストプロジェクト」を **分ける** のが基本だよ😊🧩

例：

* `MyApp`（本体：クラスライブラリ or アプリ）
* `MyApp.Tests`（テスト）

**おすすめフォルダ構成（あとで拡張しやすい）**📁✨

* `src/MyApp/`
* `tests/MyApp.Tests/`

---

## 2) Visual Studioでテストプロジェクトを追加する（王道ルート）🪄🖱️

## A. 本体プロジェクトを作る（例：Class Library）

1. **「新しいプロジェクトの作成」**
2. 「**Class Library**」で作成（C#）
3. できたら、ソリューション名もいい感じに整える😊✨

## B. テストプロジェクトを追加する

1. ソリューションを右クリック → **追加** → **新しいプロジェクト**
2. 検索欄に `test` と入れる
3. 好きなフレームワークのテンプレを選ぶ（後で比較するよ）🧪✨ ([Microsoft Learn][4])

---

## 3) テストフレームワーク3兄弟を “ゆるく” つかむ 🧪💕

結論：**どれでもOK**！ただし「迷ったら」基準があるよ😊✨

* **MSTest**：Microsoft公式寄りで安心感つよい🧡（サポート明記） ([NuGet Gallery][5])
* **xUnit**：現場採用が多く、書き味がモダン✨（NuGetで配布） ([NuGet Gallery][6])
* **NUnit**：昔から人気、属性ベースで分かりやすい💙 ([NuGet Gallery][7])

💡この教材では、**最初は MSTest か xUnit** を推しにするね😊
（どっちでも “I/O境界の分離” の練習は同じノリで進められるよ〜！）

---

## 4) “テストが発見される” の三種の神器 🔍🧰

Visual Studio の Test Explorer がテストを見つけて実行するには、だいたいこの3点が大事！

1. **テストSDK**（土台）
2. **フレームワーク本体**（MSTest/xUnit/NUnit）
3. **アダプター**（VSが認識するための橋渡し）

たとえば MSTest は公式に「発見と実行のために Adapter を入れてね」って書いてあるよ🧩✨ ([NuGet Gallery][5])

---

## 5) .csproj の “正解例” を見て安心しよう 😌🧾✨

テンプレで作れば基本OKだけど、壊れたときに直せるように「あるべき姿」を見ておこうね〜😊

## MSTest の例（よく見る形）

```xml
<Project Sdk="Microsoft.NET.Sdk">

  <PropertyGroup>
    <TargetFramework>net10.0</TargetFramework>
    <IsPackable>false</IsPackable>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="Microsoft.NET.Test.Sdk" Version="18.0.1" />
    <PackageReference Include="MSTest.TestAdapter" Version="4.0.2" />
    <PackageReference Include="MSTest.TestFramework" Version="4.0.2" />
  </ItemGroup>

  <ItemGroup>
    <ProjectReference Include="..\..\src\MyApp\MyApp.csproj" />
  </ItemGroup>

</Project>
```

* `Microsoft.NET.Test.Sdk` はテストプロジェクトの土台だよ🧱 ([NuGet Gallery][8])
* MSTest は `TestFramework` と `TestAdapter` の2つが目印👀✨ ([NuGet Gallery][5])

## xUnit の例（v2系のイメージ）

```xml
<ItemGroup>
  <PackageReference Include="Microsoft.NET.Test.Sdk" Version="18.0.1" />
  <PackageReference Include="xunit" Version="2.9.3" />
  <PackageReference Include="xunit.runner.visualstudio" Version="2.8.2" />
</ItemGroup>
```

xUnit は NuGet で配布されてて、`xunit` のページで最新バージョンが分かるよ📦✨ ([NuGet Gallery][6])

（※xUnit は v3 系もあるので、チームの方針があるならそれに合わせるのがいちばん！公式のパッケージ案内もあるよ🧭✨ ([xunit.net][9]) ）

## NUnit の例（VSアダプターが重要）

```xml
<ItemGroup>
  <PackageReference Include="Microsoft.NET.Test.Sdk" Version="18.0.1" />
  <PackageReference Include="NUnit" Version="4.4.0" />
  <PackageReference Include="NUnit3TestAdapter" Version="6.1.0" />
</ItemGroup>
```

NUnit本体と、VSで動かすための `NUnit3TestAdapter` が大事だよ〜🧩✨ ([NuGet Gallery][7])

---

## 6) Test Explorer の基本操作（ここできれば勝ち！）🏆👀✨


![testable_cs_study_008_test_explorer.png](./picture/testable_cs_study_008_test_explorer.png)

Visual Studio の **Test Explorer** は「テストの司令塔」だよ📡✨

* **すべて実行** ▶️
* **選んだテストだけ実行** ✅
* **失敗だけ再実行** 🔁
* **デバッグ実行** 🐞（ここ超大事！）

Microsoftのドキュメントでも Test Explorer の流れが説明されてるよ〜📘✨ ([Microsoft Learn][10])

💡コツ：

* テストが増えると迷子になりがちなので、**検索ボックス**で絞り込みが最強🔎✨

---

## 7) まずは “動くテスト” を1本通す（最短ルート）🚀🧪

## 本体側（例：足し算）

```csharp
namespace MyApp;

public static class Calc
{
    public static int Add(int a, int b) => a + b;
}
```

## テスト側（MSTest例）

```csharp
using Microsoft.VisualStudio.TestTools.UnitTesting;
using MyApp;

namespace MyApp.Tests;

[TestClass]
public class CalcTests
{
    [TestMethod]
    public void Add_1_and_2_returns_3()
    {
        var actual = Calc.Add(1, 2);
        Assert.AreEqual(3, actual);
    }
}
```

✅ここまでできたら、Test Explorer で「実行」して緑にしよう〜！💚🎉

---

## 8) VS Code 派のための最低ライン（CLI実行）⌨️✨

Visual Studio がメインでも、たまに **CLI** が便利なときがあるよ😊
（CIや、軽く確認したい時とか！）

* テンプレ一覧：`dotnet new list`
* テスト作成：`dotnet new mstest` / `dotnet new xunit` など
  .NET SDK には単体テスト用テンプレも含まれるよ〜📦✨ ([Microsoft Learn][11])

実行はだいたいこれ：

```powershell
dotnet test
```

---

## 9) “テストが出てこない😵‍💫” ときのチェックリスト ✅🧯

Test Explorer にテストが表示されないときは、だいたいココ！

1. **ビルドできてる？**（まずは Build / Rebuild）🏗️
2. **テストSDK & Adapter 入ってる？**（csproj確認）🧩
3. **本体への ProjectReference ある？**🔗
4. **クラス/メソッドがテストとして認識される形？**（属性ついてる？）🏷️
5. それでもダメなら、`.vs` / `bin` / `obj` を消して再起動🧹✨（よく効く）

---

## 10) ミニ課題（10〜15分）🎒✨

🎯目的：**テスト基盤が “自分の手で” 作れる** 状態にする！

1. `Calc.Subtract(a, b)` を追加する
2. テストを1本追加して、緑にする💚
3. 失敗するテストをわざと作って、**デバッグ実行**で原因を見る🐞👀

---

## 次章へのつなぎ（チラ見せ）🤖💡✨

次の第9章は **AIでテスト学習が爆速になる** 回だよ〜！
「テストケース出して」「AAAの形にして」ってお願いして、**自分でレビューできる目**を作っていこうね😊💕

---

必要なら、この第8章の内容をベースにして、
「xUnit版の最小サンプル」も同じ粒度で作るよ〜🧪✨

[1]: https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-14?utm_source=chatgpt.com "What's new in C# 14"
[2]: https://devblogs.microsoft.com/dotnet/dotnet-and-dotnet-framework-january-2026-servicing-updates/ ".NET and .NET Framework January 2026 servicing releases updates - .NET Blog"
[3]: https://learn.microsoft.com/en-us/visualstudio/releases/2026/release-notes?utm_source=chatgpt.com "Visual Studio 2026 Release Notes"
[4]: https://learn.microsoft.com/en-us/visualstudio/test/getting-started-with-unit-testing?view=visualstudio&utm_source=chatgpt.com "Get started with unit testing - Visual Studio (Windows)"
[5]: https://www.nuget.org/packages/MSTest.TestFramework?utm_source=chatgpt.com "MSTest.TestFramework 4.0.2"
[6]: https://www.nuget.org/packages/xunit?utm_source=chatgpt.com "xunit 2.9.3"
[7]: https://www.nuget.org/packages/nunit/?utm_source=chatgpt.com "NUnit 4.4.0"
[8]: https://www.nuget.org/packages/microsoft.net.test.sdk?utm_source=chatgpt.com "Microsoft.NET.Test.Sdk 18.0.1"
[9]: https://xunit.net/docs/nuget-packages-v3?utm_source=chatgpt.com "What NuGet Packages Should I Use? [xUnit.net v3]"
[10]: https://learn.microsoft.com/en-us/visualstudio/test/unit-test-basics?view=visualstudio&utm_source=chatgpt.com "Unit test basics with Test Explorer - Visual Studio (Windows)"
[11]: https://learn.microsoft.com/ja-jp/dotnet/core/tools/dotnet-new-sdk-templates?utm_source=chatgpt.com "'dotnet new' の .NET の既定のテンプレート - .NET CLI"
