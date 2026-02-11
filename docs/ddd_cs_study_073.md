# 第73章：アーキテクチャテスト🧱✅ 〜設計ルールを破ったらビルドで止める！〜

### 0. 今日の気持ち☕️

![ddd_cs_study_073_broken_window](./picture/ddd_cs_study_073_broken_window.png)

「DDDっぽく分けたのに、いつの間にか *Domain が汚れてた…* 😱」
これ、1人開発あるあるです。

そこで **アーキテクチャテスト**✨
= **“設計の交通ルール”を自動で取り締まるテスト** です🚓💨

---

## 1. アーキテクチャテストってなに？🤔

普通のユニットテストは「計算が合ってる？」みたいな **動きのテスト**だよね。

アーキテクチャテストはそれじゃなくて、

* 「Domain が Infrastructure に依存してない？」
* 「Web が Domain を直接触ってない？」
* 「`*Repository` の実装が Domain に紛れ込んでない？」

みたいな **構造のテスト**です🏗️
これをテストで落とせば、CIでもローカルでも **“ビルド失敗扱い”** にできます✅
（テスト落ち＝`dotnet test` が失敗＝パイプライン止まる！）

※概念としての説明はこういう感じです（「ユニットテストっぽいけど構造をチェックする」）([nikolatech.net][1])

![Architecture Test Concept](./picture/ddd_cs_study_073_arch_test.png)

---

## 2. 今日のゴール🎯

この章が終わったら、最低限これができるようになります💪✨

* ✅ Domain は “純粋” を守る（外側の技術に触れない）
* ✅ 依存の向き（Domain中心）をテストで固定する
* ✅ うっかり破ったら **即テスト失敗** にする

---

## 3. まずは「守るルール」を3つだけ決めよ🧠✨

最初から10個作るとしんどいので、**3つだけ**でOKです🙆‍♀️💕

### ルールA：Domain は外側に依存しない🧼

![ddd_cs_study_073_dependency_rules](./picture/ddd_cs_study_073_dependency_rules.png)
 
 ```mermaid
 flowchart TB
     Web["Web (UI/API)"]
     App["Application (UseCase)"]
     Infra["Infrastructure (DB/Ext)"]
     Domain["Domain (Rules)"]
     
     Web --> App
     Web --> Infra
     App --> Domain
     Infra --> Domain
     Infra --> App
     
     Domain -- "❌ 依存禁止" --> Infra
     Domain -- "❌ 依存禁止" --> App
     Domain -- "❌ 依存禁止" --> Web
     
     style Domain fill:#ffebd0,stroke:#f66,stroke-width:3px
 ```
 
 * Domain → Application / Infrastructure / Web に依存しない
* Domain → EF Core とか ASP.NET とか触らない

### ルールB：Application は Infrastructure に依存しない🧭

* Application は「ユースケース」
* DBや外部API（Infrastructure）は知らない

### ルールC：Web は Domain を直接いじらない🧷

* Web → Application を呼ぶ
* Domain を直に触ると、ぐちゃりやすい😵‍💫

---

## 4. いちばん簡単：NetArchTest.Rules でやる✅（サクッと派）

![ddd_cs_study_073_netarchtest_scanner](./picture/ddd_cs_study_073_netarchtest_scanner.png)

`NetArchTest.Rules` は fluent API で書けて初心者に優しいです🧸
（NuGetにパッケージがあります）([NuGet][2])

### 4-1. テストプロジェクトを作る🧪

ソリューションに `MyApp.ArchTests`（xUnit）を追加して、NuGetでこれを入れます👇

* `NetArchTest.Rules`

### 4-2. ルールを書いてみる✍️

```csharp
using NetArchTest.Rules;
using Xunit;

public class ArchitectureTests
{
    // 各層のアセンブリを読み込む（Domainの中の適当な型を1つ指定）
    private static readonly System.Reflection.Assembly DomainAssembly =
        typeof(MyApp.Domain.SomeTypeInDomain).Assembly;

    private static readonly System.Reflection.Assembly ApplicationAssembly =
        typeof(MyApp.Application.SomeTypeInApplication).Assembly;

    private static readonly System.Reflection.Assembly InfrastructureAssembly =
        typeof(MyApp.Infrastructure.SomeTypeInInfrastructure).Assembly;

    [Fact]
    public void Domain_Should_Not_Depend_On_Application_Infrastructure_Web()
    {
        var result = Types.InAssembly(DomainAssembly)
            .ShouldNot()
            .HaveDependencyOnAny(
                "MyApp.Application",
                "MyApp.Infrastructure",
                "MyApp.Web")
            .GetResult();

        Assert.True(result.IsSuccessful, result.GetFailingTypeNames());
    }

    [Fact]
    public void Application_Should_Not_Depend_On_Infrastructure()
    {
        var result = Types.InAssembly(ApplicationAssembly)
            .ShouldNot()
            .HaveDependencyOn("MyApp.Infrastructure")
            .GetResult();

        Assert.True(result.IsSuccessful, result.GetFailingTypeNames());
    }

    [Fact]
    public void Infrastructure_Can_Depend_On_Domain_And_Application()
    {
        // 「依存してもいい」を直接テストするより、
        // 「依存してはいけない」を決めた方が事故りにくいけど、
        // 例として“変な依存がないか”チェックする形にしてます
        var result = Types.InAssembly(InfrastructureAssembly)
            .ShouldNot()
            .HaveDependencyOn("MyApp.Web")
            .GetResult();

        Assert.True(result.IsSuccessful, result.GetFailingTypeNames());
    }
}

internal static class NetArchTestExtensions
{
    // 失敗した型名を見やすく表示
    public static string GetFailingTypeNames(this TestResult result)
        => "❌ Violations:\n" + string.Join("\n", result.FailingTypeNames);
}
```

### コツ💡

![ddd_cs_study_073_rule_evolution](./picture/ddd_cs_study_073_rule_evolution.png)

* 「依存してはいけない」を中心にルール化するとラク😌
* ルールは “増やす” より “育てる” 🌱（必要になったら1個足す）

---

## 5. もう少し強力：ArchUnitNET でやる🏋️‍♀️（ガチ寄り）

`ArchUnitNET` はアーキテクチャテスト専用ライブラリで、拡張もあります📦
NuGetに本体と xUnit 用拡張があり、ガイドもあります([NuGet][3])

例：

* `TngTech.ArchUnitNET.xUnit`（xUnit用）

（ここは “選択肢” なので、今すぐじゃなくてOK🙆‍♀️）

---

## 6. 「わざと違反」してみよう😈➡️✅（超大事）

![ddd_cs_study_073_breaking_build](./picture/ddd_cs_study_073_breaking_build.png)

これを一回やると理解が爆速です🚀

### やること

1. Domain に `using MyApp.Infrastructure;` してみる（ダメな参照を作る）
2. テスト実行
3. **落ちるのを見てニヤッ😏**
4. 参照を消す
5. **通って安心😌**

「守れてる」より「破ったら止まる」が価値✨

---

## 7. AI活用プロンプト例🤖📝（そのまま使ってOK）

### プロンプト1：ルール案を作らせる

「このソリューション構成（Domain/Application/Infrastructure/Web）で、依存ルールを3〜5個提案して。初心者でも破りやすい事故中心で」

### プロンプト2：NetArchTest のテストを生成

「次の名前空間を前提に NetArchTest.Rules + xUnit でアーキテクチャテストを書いて：…（名前空間列挙）」

### プロンプト3：落ちた理由を翻訳させる

「このFailingTypeNamesを、何が悪いか日本語で説明して。直し方も3案」

---

## 8. よくあるハマりどころ🧩

* 😵 `GetFailingTypeNames()` みたいな出力が無いと原因が見えにくい
  → **失敗した型名を必ず出す**（上の拡張みたいに）
* 🌀 ルールを細かくしすぎて、変更のたびにテスト修正地獄
  → 最初は **“依存の向き” だけ**で十分🙆‍♀️
* 🧨 名前空間がブレブレでテストが書きにくい
  → 次章（ディレクトリ名で語る設計）とも相性◎✨（74章につながる）

---

## 9. ミニ演習🎓✨（10分）

### 演習A（超おすすめ）🔥

* ルールを1つ追加：
  **「Domain は `Microsoft.EntityFrameworkCore` に依存してはいけない」**
* わざと Domain で EF Core を `using` して落とす
* 元に戻して通す✅

ヒント：`HaveDependencyOn("Microsoft.EntityFrameworkCore")` みたいに書けます💡

---

## まとめ🍓

アーキテクチャテストは、

* 「正しい構造」を“願う”んじゃなくて🙏
* 「破ったら止める」を“仕組み化”する💥✅

ための武器です🗡️✨

次に進むなら、**テストしやすいフォルダ/名前空間設計**（74章）とセットで、さらに気持ちよくなります😆🎉

[1]: https://www.nikolatech.net/blogs/architecture-tests-in-dotnet?utm_source=chatgpt.com "Architecture Tests in .NET"
[2]: https://www.nuget.org/packages/NetArchTest.Rules/?utm_source=chatgpt.com "NetArchTest.Rules 1.3.2"
[3]: https://www.nuget.org/packages/TngTech.ArchUnitNET?utm_source=chatgpt.com "TngTech.ArchUnitNET 0.13.1"
