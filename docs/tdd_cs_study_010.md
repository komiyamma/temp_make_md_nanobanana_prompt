# 第10章：VS Code補足（ミニ構成で迷わない）🧩

（＝「VSが使えない日でも、TDDの学習が止まらない状態」にする章だよ〜😊🧪）

---

## 1) この章のゴール🎯💡

この章が終わると、VS Codeで👇がサクッとできるようになるよ✨

* ✅ ソリューション（.sln）を開いて迷子にならない
* ✅ テストが自動で見つかる（発見される）
* ✅ 1本だけ実行／まとめて実行／デバッグ実行ができる
* ✅ 「テスト出ない😵」「dotnet無い😵」の定番トラブルを即なおせる

C#まわりは **C# Dev Kit** が中心になるよ〜🧰✨（ソリューション管理・テスト探索/実行/デバッグがまとまってる） ([Visual Studio Marketplace][1])

---

## 2) まずは「ミニ構成」だけ覚える📦🧠（これで迷子激減！）

![画像を挿入予定](./picture/tdd_cs_study_010_obvious_implementation.png)

VS Codeは“フォルダの開き方”で迷子になりがちだから、構成を最小に固定しよ😊

おすすめの最小構成👇（これだけでOK✨）

```text
MyApp/
  MyApp.sln
  src/
    MyApp/
      MyApp.csproj
      ...
  tests/
    MyApp.Tests/
      MyApp.Tests.csproj
      ...
```

ポイントはこれだけ👇✨

* 🟦 **src** は本体
* 🟩 **tests** はテスト
* 🧷 “本体を参照するテスト”にする（tests → src）

---

## 3) VS Code側：入れる拡張はほぼこれだけ🧩✨

### 入れるもの（基本セット）

* **C# Dev Kit**：ソリューション管理・テンプレ・テスト探索/実行/デバッグが強い✨ ([Visual Studio Marketplace][1])

  * これを入れると、必要なもの（C#拡張など）もセットで入る動きになるよ ([Visual Studio Marketplace][1])
* **.NET Install Tool**：VS Codeから .NET SDK を入れたり確認できる🪄 ([Visual Studio Marketplace][2])

> ※C# Dev Kitは、個人・学校・OSSなら無償枠で使える（企業利用はVSサブスク範囲の扱い）って整理だよ〜👀 ([Microsoft Learn][3])

---

## 4) .NET SDK が入ってるか一瞬チェック⚡（ここが詰まりポイントNo.1）

VS Codeのターミナル（`Ctrl + @` か `Ctrl + Shift + @` 系）で👇

```bash
dotnet --info
```

* もし `dotnet` が見つからない系なら、.NET SDKが入ってない/Pathが通ってない可能性大😵‍💫
* .NET 10 系を使うなら、まず **.NET 10.0.2（2026-01-13時点の最新版）** が案内されてるよ ([Microsoft][4])

### VS Codeから入れる派の人へ🪄

**.NET Install Tool** には “SDKをシステム全体に入れる” コマンドがあるよ👇 ([Visual Studio Marketplace][2])
（コマンドパレット `Ctrl + Shift + P` → `Install the .NET SDK System-Wide` みたいなやつ）

---

## 5) VS Codeで「開き方」を固定する📂✨（迷子防止の核心！）

やり方は2択。どっちでもOK😊

### A. いちばん安全：**sln があるフォルダを開く**

* `MyApp/` を **フォルダごと** 開く（`MyApp.sln` が見える場所）

### B. すでに複数ある：ワークスペースは“極力1つ”

* マルチルート（複数フォルダ同時）は、初心者のうちは事故りやすい💥
* まずは「1フォルダだけ」にしておくと勝ち😊✨

---

## 6) テストを “見つけさせる” コツ🧪🔍（出ない時はだいたいコレ）

C# Dev Kitは **テスト探索（test discovery）** をしてくれるんだけど、探索されないと「テスト0件」になるのね😵

探索されない典型👇

* ✅ まだビルド/復元が終わってない
* ✅ テストプロジェクト扱いになってない（参照やパッケージが足りない）
* ✅ 直近でcsprojをいじって、再読込が必要

なので手順はこうすると安定するよ✨

1. ターミナルで復元

```bash
dotnet restore
```

2. ビルド

```bash
dotnet build
```

3. テスト実行（まずCLIで動けば勝ち）

```bash
dotnet test
```

この3つが通ったら、VS Code側のTestingビュー（フラスコ🧪）も基本ついてくる😊✨

---

## 7) xUnit v3 で始めるなら（超ミニ）🧪✨

このロードマップは **xUnit v3** 前提だったよね😊
v3は `dotnet new` のテンプレが用意されてるよ〜✨ ([xUnit.net][5])

### v3テンプレを入れる

```bash
dotnet new install xunit.v3.templates
```

（最新版は NuGet だと 3.2.2 が 2026-01-14 更新になってる） ([NuGet][6])

### v3テストプロジェクトを作る（カレントに作る）

`````bash
dotnet new xunit3
`````

> ちなみに最近のテンプレは、`dotnet test` や Test Explorer の “実行方式” を切り替えるオプションも増えてて、Microsoft Testing Platform（MTP）系の扱いも整ってきてるよ🧠✨

---

## 8) VS Codeでテストを実行する（操作の型）🧪▶️  
“毎回同じ動き”にすると超ラクだよ😊✨

### 🧪 まとめて実行  
- Testingビュー（フラスコ）を開く  
- ルートの ▶️（Run Tests）を押す

### 🧪 1本だけ実行  
- テスト名の横の ▶️ を押す  
（「1テスト1意図」の練習と相性バツグン🍰✨）

### 🐞 デバッグ実行（めちゃ大事！）  
- テストを右クリック → **Debug Test**（みたいな項目）  
- ブレークポイント置いて止める👀✨  
TDDは「失敗の理由を素早く見る」競技だから、ここ最強〜🏃‍♀️💨

---

## 9) VS Code “ハマりがち”図鑑🫠📚（すぐ直せるやつだけ！）  
### ① テストが0件（No tests found）🧪0️⃣  
だいたいこれ👇  
- `dotnet test` が通るか確認（通らないならVS Code以前の問題）  
- `dotnet restore → build → test` を順にやる  
- csprojいじったら、VS Codeを `Reload Window`（再読込）  

### ② dotnet が無い（SDK無い）😵  
- .NET 10系は **10.0.2 が最新版案内**になってるよ  
- .NET Install Toolで “SDK System-Wide” 入れるルートもある  

### ③ “企業PCでC# Dev Kitが使えない”っぽい🤔  
- 組織利用はVisual Studioサブスク範囲の扱い（個人/学校/OSSは無償枠）  
（ここは環境ルール次第だから、引っかかったら会社の規定確認だね🙏）

---

## 10) AIの使いどころ（この章はここだけでOK）🤖✨  
VS Code環境は「詰まった時の切り分け」が命だから、AIはこう使うのが強いよ😊

### ✅ おすすめプロンプト（コピペ用）  
- 「このエラー（ログ）から、原因候補を3つ → 確認手順を順番に出して」🔍  
- 「この `.csproj` とフォルダ構成で、テストが発見されない理由をチェックリスト化して」🧾  
- 「xUnit v3で `dotnet test` が通る最小構成を提案して（余計なものは入れないで）」🧪  

“AIの答え＝採用”じゃなくて、**チェックリストとして使う**のが安全だよ〜✅✨

---

## 11) ミニ演習（30〜40分）☕️🧪  
今日の提出（コミット）イメージはこれ😊✨

1) `src/` と `tests/` を作る  
2) `dotnet restore`  
3) `dotnet test` が通るのを確認  
4) VS CodeのTestingビューで  
   - まとめて実行 ▶️  
   - 1本だけ実行 ▶️  
   - Debug Test 🐞  
5) わざと失敗させて、失敗ログを読めたら勝ち🎉  

---

必要なら次は、**「VS CodeでもRed/Green/Refactorが気持ちよく回る」ための、テスト命名テンプレ＆コミット粒度テンプレ**も作るよ〜🧁✨

[1]: https://marketplace.visualstudio.com/items?itemName=ms-dotnettools.csdevkit "
        C# Dev Kit - Visual Studio Marketplace
    "
[2]: https://marketplace.visualstudio.com/items?itemName=ms-dotnettools.vscode-dotnet-runtime "
        .NET Install Tool - Visual Studio Marketplace
    "
[3]: https://learn.microsoft.com/en-us/visualstudio/subscriptions/vs-c-sharp-dev-kit "C# Dev Kit for Visual Studio Code - Visual Studio Subscription | Microsoft Learn"
[4]: https://dotnet.microsoft.com/en-US/download/dotnet/10.0?utm_source=chatgpt.com "Download .NET 10.0 (Linux, macOS, and Windows) | .NET"
[5]: https://xunit.net/docs/getting-started/v3/whats-new "What's New in v3? [2025 August 14] | xUnit.net "
[6]: https://www.nuget.org/packages/xunit.v3.templates "
        NuGet Gallery
        \| xunit.v3.templates 3.2.2
    "
