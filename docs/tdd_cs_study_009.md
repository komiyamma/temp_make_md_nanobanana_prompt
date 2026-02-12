# 第09章：dotnet test（CLI）も使えるようにする⌨️

この章は「IDE（Visual Studio）を開かなくても、テストを回して原因を特定できる」ようになる回だよ〜😊
CI（自動テスト）でもほぼ同じコマンドを使うから、ここ押さえると一気に“現場っぽさ”が出るやつ💪🔥

---

## 1) この章のゴール🎯✨

![CLI Switch Toggle](./picture/tdd_cs_study_009_cli_switch.png)

できるようになればOK👇

* ✅ `dotnet test` を **ソリューション/プロジェクト/フォルダ**単位で実行できる
* ✅ **1本だけ**テストを走らせる（フィルタ）できる
* ✅ 失敗ログを読んで「どこが怪しいか」を絞れる
* ✅ 結果（TRX）やカバレッジをファイルに残せる
* ✅ CIでも困らない“CLIの型”が身につく

`dotnet test` は、成功なら終了コード 0 / 失敗があると 1 を返すので、CIが判定しやすい仕組みになってるよ🧠✅ ([Microsoft Learn][1])

---

## 2) まず「どこで打つか」だけ迷子防止🧭🪟

基本は **ソリューション（`.sln`）があるフォルダ**へ移動してから打つのがラク😊
（フォルダ指定でも動くけど、迷子が減る✨）

---

## 3) `dotnet test` のいちばん基本🧪✨

![Scope Pyramid](./picture/tdd_cs_study_009_scope_pyramid.png)

![画像を挿入予定](./picture/tdd_cs_study_009_fake_it.png)

`dotnet test` は **いろんな単位で実行できる**よ👇（覚えやすい！）

* `.sln` を指定
* `.csproj` を指定
* “今いるディレクトリ”を指定（省略したらこれ）
* さらには DLL/EXE 指定もOK ([Microsoft Learn][1])

### ✅ まずは普通に全部実行

```bat
dotnet test
```

### ✅ ソリューション指定（おすすめ）

```bat
dotnet test MyApp.sln
```

### ✅ テストプロジェクト指定（軽く回したいとき）

```bat
dotnet test tests\MyApp.Tests\MyApp.Tests.csproj
```

---

## 4) 「1本だけ実行」できるようになる（超重要）🔍🔥

![Filter Funnel](./picture/tdd_cs_study_009_filter_funnel.png)

ここが第9章の主役！
開発中は「全部回す」より「今いじってる所だけ回す」が速いから、手が止まらないよ🚀✨

### 4.1 テスト名を一覧で見る（走らせない）📃

```bat
dotnet test -t
```

`-t|--list-tests` は「発見したテスト一覧を出すだけ」だよ🧪 ([Microsoft Learn][1])

---

### 4.2 フィルタで絞って実行する🎯

![Filter Tags](./picture/tdd_cs_study_009_filter_tags.png)

`--filter` が使える！ ([Microsoft Learn][1])

フィルタはこんな形👇
`<property><operator><value>` を組み合わせる（OR/AND もできる） ([Microsoft Learn][1])

xUnit だと主にこのプロパティが使えるよ👇

* `FullyQualifiedName`
* `DisplayName`
* `Category` ([Microsoft Learn][1])

#### ✅ 例1：メソッド名の一部で絞る（いちばん手軽）✨

（operator省略だと `FullyQualifiedName~` 扱いになるよ） ([Microsoft Learn][1])

```bat
dotnet test --filter PriceCalculatorTests
```

#### ✅ 例2：完全修飾名で“contains”絞り（確実）🧠

```bat
dotnet test --filter FullyQualifiedName~MyApp.Tests.PriceCalculatorTests
```

#### ✅ 例3：表示名で絞る（`DisplayName`を付けた場合）🏷️

```bat
dotnet test --filter DisplayName~"割引が上限を超えない"
```

#### ✅ 例4：カテゴリで絞る（Traitで“カテゴリ”を付ける）🎛️

まずテストに Trait を付けるよ👇

```csharp
using Xunit;

public class PriceCalculatorTests
{
    [Fact]
    [Trait("Category", "Fast")]
    public void Tax_is_rounded()
    {
        Assert.True(true);
    }
}
```

そしてCLIで絞る👇

```bat
dotnet test --filter Category=Fast
```

---

## 5) 「わざと失敗」してログに慣れる🚨➡️🔍

TDDって **失敗を味方にする**から、ここで“赤の読み方”を練習しよ😊

### 手順（ミニ演習）🧪

1. 既存テストの `Assert` をわざと間違える（例：`Assert.True(false)`）
2. そのテストだけ回す👇

```bat
dotnet test --filter FullyQualifiedName~Tax_is_rounded
```

3. エラーメッセージで「期待値/実際値」「どの行」が出るのを観察👀✨

---

## 6) ログを読みやすくする小ワザ集🛠️✨

![Verbosity Knob](./picture/tdd_cs_study_009_verbosity_knob.png)

### 6.1 詳細ログがほしい（原因調査向け）🧾

`-v|--verbosity` があるよ ([Microsoft Learn][1])
（例）

```bat
dotnet test -v detailed
```

### 6.2 Terminal Logger のON/OFF（表示が崩れる時など）🖥️

`--tl:[auto|on|off]` があって、環境チェックして自動ONにもできるよ ([Microsoft Learn][1])
（例）

```bat
dotnet test --tl:off
```

---

## 7) 結果をファイルに残す（TRX）📁✅

![TRX Report Printer](./picture/tdd_cs_study_009_trx_printer.png)

CIやあとからの共有で便利なのが **TRX（テスト結果ファイル）**✨
`--logger` で指定できるよ ([Microsoft Learn][1])

### ✅ TRX を出す（ファイル名も指定）

```bat
dotnet test --logger "trx;LogFileName=test-results.trx"
```

### ✅ 出力先フォルダを固定する

`--results-directory` は結果の置き場を指定できて、無ければ作ってくれるよ（既定は `TestResults`） ([Microsoft Learn][1])

```bat
dotnet test --logger "trx;LogFileName=test-results.trx" --results-directory .\artifacts\TestResults
```

---

## 8) “固まる/落ちる”系のトラブルを追う🕵️‍♀️💥

### 8.1 落ちる犯人探し：`--blame` 🧷

テストホストがクラッシュする時に、実行順を記録してくれるモードだよ ([Microsoft Learn][1])

```bat
dotnet test --blame
```

### 8.2 さらに深掘り：`--diag`（診断ログ）🧠

テストプラットフォームの診断ログをファイルに出せるよ ([Microsoft Learn][1])

```bat
dotnet test --diag .\artifacts\diag\test.diag.txt
```

---

## 9) 速く回すための“定番オプション”⚡🐢➡️🚀

![Turbo Button Speed](./picture/tdd_cs_study_009_turbo_button.png)

### 9.1 すでにビルド済みなら `--no-build` 🌪️

`--no-build` は「ビルドせずにテスト実行」＋暗黙で `--no-restore` も入るよ ([Microsoft Learn][1])

```bat
dotnet test --no-build
```

### 9.2 さらに restore も省略（状況が安定してる時）📦

```bat
dotnet test --no-restore
```

> 体感ルール：
> ✅ ふだんは `dotnet test`
> ✅ 速さが欲しい時は `dotnet test --no-build`
> ✅ CIは “ビルド→テスト” を分けることが多いよ😊

---

## 10) カバレッジもCLIで取れる🧪📊✨（おまけだけど強い）

`--collect` でデータコレクタを有効化できて、カバレッジも取れるよ ([Microsoft Learn][1])
特に `XPlat Code Coverage` は Coverlet を使う方式として案内されてるよ ([Microsoft Learn][1])

### 10.1 事前：カバレッジ用パッケージを追加（テストプロジェクト）

（CI例だけど分かりやすいので同じことやる感じ） ([Microsoft Learn][2])

```bat
dotnet add .\tests\MyApp.Tests\MyApp.Tests.csproj package coverlet.collector
```

### 10.2 実行（カバレッジ取得）

```bat
dotnet test --collect:"XPlat Code Coverage" --results-directory .\artifacts\TestResults
```

---

## 11) xUnit で `dotnet test` が動く最低条件（ハマりやすい）🧩😵‍💫

「テストが見つからないんだけど…？」ってなりがちなので先に予防線😊

* xUnit の `dotnet test` 実行は、VSTest 経由なら `xunit.runner.visualstudio` 参照でサポートされるよ ([xUnit.net][3])
* `xunit.runner.visualstudio` は xUnit v1/v2/v3 を走らせられる VSTest アダプタだよ ([NuGet][4])

> もし「No test is available」と出たら、まず
> ✅ `Microsoft.NET.Test.Sdk`
> ✅ `xunit`（または `xunit.v3`）
> ✅ `xunit.runner.visualstudio`
> がテストプロジェクトに入ってるか見よ〜👀✨（ここが9割）

---

## 12) AIの使いどころ（第9章は相性よすぎ）🤖💡✨

CLIは“暗記ゲー”になりがちだから、AIでメモ化しちゃお😊

### おすすめプロンプト例🪄

* 「このテスト名で `dotnet test --filter` を作って（3パターン）」
* 「この失敗ログから、原因候補→確認手順を順番に」
* 「この章のコマンドを“チートシート1枚”にまとめて」

---

## 13) ミニ課題（コミット単位まで）📝🎁

### 課題A：1本だけ実行できるようにする🎯

* `--list-tests` でテスト名を確認
* `--filter` で狙った1本を実行
* できたらスクショ or コマンドを README に貼る✨

### 課題B：わざと失敗→直す🚦

* 1本をわざと失敗させる
* `--filter` でその1本だけ回す
* 直してGreenに戻す💚

### 提出物（おすすめ）📦

* `docs/testing-cli-cheatsheet.md`（自分用コマンド集）
* `artifacts/TestResults/`（TRXが出る設定の確認）

---

## 14) まとめ🎉

* `dotnet test` は **CIでもそのまま使う“基本スキル”**🧪✨ ([Microsoft Learn][1])
* `--filter` と `--list-tests` が使えると、TDDの回転が爆速になる🚀 ([Microsoft Learn][1])
* つらいときは `--blame` と `--diag` で深掘りできる🕵️‍♀️ ([Microsoft Learn][1])

---

### （最新メモ🗓️）この章の前提に関わる“今”の情報だけ置いとくね

* .NET 10 は **10.0.2（2026-01-13）**、SDK は **10.0.102** が案内されてるよ ([Microsoft][5])
* .NET 10.0.2 は Windows Update/WSUS でも配布される形になってるよ ([Microsoft サポート][6])

---

次の章（第10章）がもし「VS Code補足」なら、**CLI×VS Code の“気持ちよく回る最小構成”**を、迷子ゼロ手順で書けるよ😊🧩✨

[1]: https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-test-vstest "dotnet test command with VSTest - .NET CLI | Microsoft Learn"
[2]: https://learn.microsoft.com/en-us/azure/devops/pipelines/ecosystems/dotnet-core?view=azure-devops&utm_source=chatgpt.com "Build, test, and deploy .NET Core projects - Azure Pipelines"
[3]: https://xunit.net/docs/getting-started/v3/microsoft-testing-platform "Microsoft Testing Platform (xUnit.net v3) [2025 November 2] | xUnit.net "
[4]: https://www.nuget.org/packages/xunit.runner.visualstudio "
        NuGet Gallery
        \| xunit.runner.visualstudio 3.1.5
    "
[5]: https://dotnet.microsoft.com/en-US/download/dotnet/10.0 "Download .NET 10.0 (Linux, macOS, and Windows) | .NET"
[6]: https://support.microsoft.com/en-us/topic/-net-10-0-update-january-13-2026-64f1e2a4-3eb6-499e-b067-e55852885ad5 ".NET 10.0 Update - January 13, 2026 - Microsoft Support"
