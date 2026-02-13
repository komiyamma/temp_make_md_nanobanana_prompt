# 第02章：Windows開発環境セットアップ＋AI相棒の使い方🤝🛠️🤖

この章は「**迷わずプロジェクトを作って、実行できる**」状態にする回だよ〜！🎉
ついでに、Copilot / Codex みたいなAI相棒と**ケンカせずに仲良くやるコツ**も身につける💞✨

---

## この章のゴール🎯✨

* Visual Studioで **C#プロジェクトを作成→実行**できる🚀
* VS Code（必要なら）でも **.NET CLIで作成→実行**できる🧭
* AIに頼むときの「**安全な型**」を覚える（丸呑み禁止🙅‍♀️）🤖

---

## まずは今日のチェックリスト✅🪄

* [ ] Visual Studioを用意して起動できる🪟
* [ ] .NET SDKが入っていて `dotnet --info` が動く🔎（VS Codeルートでも使う）
* [ ] GitHubにサインインできる（後で超ラク）🔑
* [ ] Copilot等のAIが使える状態になってる🤖
* [ ] Helloアプリを実行して「動いた！」を確認🎉

※ .NETは **.NET 10 が最新のLTS**として配布されてるよ（2026/01時点）📌 ([Microsoft][1])

---

## 1) Visual Studioルート（いちばんおすすめ）🛠️✨

### 1-1. Visual Studioの選び方（迷ったらこれ！）🌟

* **Visual Studio 2026**：最新世代のIDE（AI統合が強め）🧠✨ ([Microsoft Learn][2])
* すでに **Visual Studio 2022** が入ってるなら、それでも全然OK（最新の17.14系が配布されてる）📌 ([Microsoft Learn][3])

### 1-2. インストールで入れるもの（チェックを入れるだけ✅）

インストーラーの「ワークロード」で、まずはこれを入れるのが安心👇

* **.NET デスクトップ開発**（Console/Winアプリの土台）🧱
* **ASP.NET と Web 開発**（MVCで後から絶対使う）🌐

> Visual Studioは開発用の.NETをまとめて管理してくれるタイプだよ🧺 ([Microsoft Learn][4])

---

## 2) VS Codeルート（軽くやりたい・補助ルート）🧭💡

### 2-1. .NET SDK を入れる（VS Codeルートの必須アイテム）🔧

.NETのダウンロードページでは **.NET 10 SDK** が提供されてるよ（2026/01の最新更新も載ってる）📌 ([Microsoft][1])

確認コマンド（PowerShell）👇

```powershell
dotnet --info
dotnet --version
```

### 2-2. VS Codeに入れる拡張（C#開発の定番セット）🧩✨

* **C# Dev Kit**（Solution Explorerが出て開発しやすい）🧰 ([Microsoft Learn][5])
* **GitHub Copilot**（入れておくと後の章が快適）🤖

> Microsoftの手順でも、VS Codeなら「C# Dev Kit」を使う流れが案内されてるよ📌 ([Microsoft Learn][4])

---

## 3) GitHub Copilot（AI相棒）のセットアップ🤖💞

### 3-1. Visual StudioでCopilotを有効にする🧠

Visual Studio側でCopilotの状態を管理する案内があるよ（設定場所など）⚙️ ([Microsoft Learn][6])
GitHub公式の案内でも「Visual Studioに拡張を入れて、GitHubアカウント連携が必要」って流れになってるよ🔑 ([GitHub Docs][7])

---

## 4) AI相棒の“正しい使い方”ルール（超大事）⚠️🤝

![AI Partner](./picture/mvc_cs_study_002_ai_partner.png)


AIは便利だけど、**使い方が雑だと事故る**😇
ここから先の章がずっとラクになる「型」を作っちゃおう✨

### 4-1. AIに頼むときの黄金3ステップ🥇

1. **小さく頼む**（一気に全部作らせない）✂️
2. **差分で見る**（生成結果は“提案”）👀
3. **意図を説明させる**（理解してから採用）🧠

```mermaid
flowchart LR
    A[1. 小さく頼む✂️] --> B[2. 差分を確認👀]
    B --> C[3. 意図を理解🧠]
    C --> D[採用・修正🎉]
```

### 4-2. 丸呑み禁止のチェック項目✅🙅‍♀️

* 変数名/クラス名が「今の目的」に合ってる？🧾
* 例外処理・入力チェックが変に増えてない？🧯
* 依存関係が増えてない？（謎ライブラリ追加とか）🧲
* 「なぜそうしたか」を説明できる？🗣️

### 4-3. “うまくいくプロンプト”テンプレ集📦✨

困ったらこの形で投げると強いよ〜！💪

**A) エラー調査（おすすめ）**🔎

```text
次のエラーが出ました。原因候補を3つ、確認手順をそれぞれ箇条書きでください。
最後に「まず最初にやるべき順番」も提案して。
（エラー全文：ここに貼る）
（状況：何をしたら出たか）
```

**B) コードレビュー（責務まぜまぜ防止）🧼**

```text
このコードはMVCで言うと責務が混ざっていないかレビューして。
混ざっているなら「どこを」「どう分けるか」を最小修正で提案して。
```

**C) テスト案づくり（漏れ防止）🧪**

```text
この処理に必要なテストケースを「正常/異常/境界値」で列挙して。
各ケースは1行で、理由も短く添えて。
```

### 4-4. AI利用の地雷⚡️（ここだけは守って🙏）

* **秘密情報（APIキー/パスワード）を貼らない**🔒
* 不明点を“それっぽく断言”してきたら、**根拠を聞く**🧐
* 生成されたコードは、**まず動く最小形にしてから**育てる🌱

---

## 5) ミニ演習：Hello Console を作って実行🎉🧪

### 5-1. Visual Studioでやる（王道）👑

1. 「新しいプロジェクトの作成」
2. **Console App** を選ぶ（C#）
3. フレームワークは **.NET 10** を選ぶ（あれば）✨ ([Microsoft][1])
4. 実行（▶）して出力を確認！

サンプル👇

```csharp
Console.WriteLine("Hello CampusTodo! 🎀✅");
```

### 5-2. VS Code + CLI でやる（軽量ルート）🧭

```powershell
mkdir CampusTodo
cd CampusTodo
dotnet new console
dotnet run
```

---

## 6) つまずきポイント早見表（あるある）😵‍💫➡️😌

* `dotnet` が見つからない
  → .NET SDKが入ってない/Path未設定の可能性。まず `dotnet --info` で確認🔎
* Visual Studioでテンプレが出ない
  → ワークロード不足の可能性（.NET desktop / ASP.NET）🧩
* VS CodeでC#がうまく動かない
  → C# Dev Kit + .NET SDK の組み合わせを確認🧰 ([Microsoft Learn][5])
* Copilotが出てこない
  → 拡張の状態・サインインを確認（VSのCopilot状態管理の案内あり）⚙️ ([Microsoft Learn][6])

---

## 今日の成果物📦✨（次章に繋げる！）

* Hello Consoleが動いた🎉
* `CampusTodo` フォルダ（空でもOK）📁
* AIに「エラー確認手順3つ」を聞ける型ができた🤖💡

次の第3章から、いよいよ **CampusTodo を“作るもの”として決めていく**よ〜！🧁📚✨

[1]: https://dotnet.microsoft.com/en-us/download?utm_source=chatgpt.com "Download .NET (Linux, macOS, and Windows) | .NET"
[2]: https://learn.microsoft.com/en-us/visualstudio/releases/2026/release-notes?utm_source=chatgpt.com "Visual Studio 2026 Release Notes"
[3]: https://learn.microsoft.com/en-us/visualstudio/releases/2022/release-notes?utm_source=chatgpt.com "Visual Studio 2022 version 17.14 Release Notes"
[4]: https://learn.microsoft.com/en-us/dotnet/core/install/windows?utm_source=chatgpt.com "Install .NET on Windows"
[5]: https://learn.microsoft.com/en-us/visualstudio/subscriptions/vs-c-sharp-dev-kit?utm_source=chatgpt.com "C# Dev Kit for Visual Studio Code"
[6]: https://learn.microsoft.com/en-us/visualstudio/ide/visual-studio-github-copilot-install-and-states?view=visualstudio&utm_source=chatgpt.com "Manage GitHub Copilot installation and state"
[7]: https://docs.github.com/copilot/managing-copilot/configure-personal-settings/installing-the-github-copilot-extension-in-your-environment?utm_source=chatgpt.com "Installing the GitHub Copilot extension in your environment"
