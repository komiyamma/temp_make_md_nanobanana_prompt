# 第02章：2026最新版の開発環境セットアップ🧰🪟

この章は「SOLIDを学ぶための道具を、気持ちよく揃える章」だよ〜😊💖
次の章以降で **リファクタリング🧹・テスト🧪・AI支援🤖** をガンガン使うので、ここでスッキリ整えます✨

---

## 2-1. この章のゴール🎯✨

![開発者の作業台](./picture/solid_cs_study_002_setup_workbench.png)

終わるころに、あなたのPCでこれができればOK🥳🎉

* Visual Studio 2026 で C# 14 / .NET 10 のプロジェクトを作って実行できる✅ ([Microsoft Learn][1])
* .NET 10 SDK が入ってるか、コマンドで確認できる✅ ([Microsoft][2])
* GitHub Copilot を Visual Studio で使える（補完＆チャット）✅ ([Microsoft Learn][3])
* （任意）VS Code派でも C# Dev Kit で同じ教材を進められる✅ ([Visual Studio Code][4])
* “ずっと使うサンプル題材”のソリューション（空プロジェクト）を作って保存できる✅📦

---

## 2-2. インストール前のミニ準備🧃✨（つまずき予防）

### ✅ 空き容量チェック💾

Visual Studio は入れる機能（ワークロード）でサイズが変わるよ〜！
だいたい **20〜50GB** あると安心、最大だともっと使うこともあるよ🫣💦 ([Microsoft Learn][5])

### ✅ ネットが不安定なら「オフライン/ネットワーク用レイアウト」もアリ📦🌐

会社や回線の都合で落ちやすいときは、インストール用の“ローカル置き場”を作れるよ🧺
目安として **レイアウト作成に40GB前後** が必要になることがあるので、ディスクだけ注意ね🙏 ([Microsoft Learn][6])

---

## 2-3. Visual Studio 2026 の入れ方🧩✨（王道ルート）

### ① Visual Studio Installer でインストール開始🧰

公式手順は「Installer起動 → ワークロード選択 → インストール」って流れだよ😊 ([Microsoft Learn][7])

---

### ② ワークロード（Workloads）のおすすめ構成🧁✨

SOLID学習でよく使うのは、まずこのへん👇（最小からスタートしてOK！）

* **.NET desktop development**（コンソール/WPF/WinForms など）🖥️
* **ASP.NET and web development**（APIを作る練習がしやすい）🌐
* （任意）**Azure development**（クラウド連携を触りたくなったら）☁️

💡あとで増やせるので、迷ったら “2つだけ” でOKだよ〜🙆‍♀️✨

---

### ③ 「GitHub Copilot」を入れる（超大事🤖💞）

Visual Studio だと **Installer の Optional components** から Copilot を入れられるよ！
手順イメージはこんな感じ👇 ([Microsoft Learn][3])

* Visual Studio Installer を起動
* インストール済みの VS を選んで「Modify」
* どれかワークロードを開く（例：.NET desktop development）
* Optional components で **GitHub Copilot** にチェック
* 「Modify」で適用✅

---

### ④ 設定を引っ越したいなら「構成の移行」or「.vsconfig」📦✨

もし過去の Visual Studio が入ってるなら、
環境設定やワークロードを“コピー”して移行できるオプションがあるよ😊
チームで揃えるなら **.vsconfig のインポート** も便利✨ ([Microsoft Learn][7])

---

## 2-4. .NET 10 SDK の確認✅🧪

Visual Studio だけでも進められるけど、**コマンドで確認できると強い**よ💪✨
（SOLID学習は「小さく試す→直す」を繰り返すから、CLIがあると爆速🏎️💨）

### ✅ PowerShell で確認してみよ〜🖤

```text
dotnet --info
dotnet --list-sdks
```

* ここで **10.0.x** が見えたらOK🙆‍♀️✨
* 見えなかったら .NET 10 SDK を入れよう（公式ダウンロード）📥 ([Microsoft][2])

---

## 2-5. “この教材用”のソリューションを作る📦✨（ずっと使う箱）

ここでは中身を作り込まないよ！
「器（Solution）」だけ作って、次章でわざと最悪コードを作る😈🧱✨

### ✅ Visual Studio で作る（おすすめ）

1. 「新しいプロジェクトの作成」
2. まずは **Console App** を選ぶ🧁
3. ターゲットが **.NET 10** になってるのを確認（選べるはず） ([Microsoft Learn][1])
4. Solution 名をそれっぽく（例：MiniECommerce / BookRental）📚🛒
5. 実行（F5）して “Hello” が出ればOK🎉

> Visual Studio 2026 は .NET 10 と C# 14 を「追加設定なしでフルサポート」って明言されてるよ✅ ([Microsoft Learn][1])

---

## 2-6. C# 14 が使える状態になってる？（軽く確認）🧠✨

「C# 14 の機能は Visual Studio 2026 または .NET 10 SDK で試せる」って位置づけだよ✅ ([Microsoft Learn][8])
この章では深入りしないけど、次章以降で “最新言語の書き味” も自然に触れるよ〜😊💕

---

## 2-7. GitHub Copilot の初期チェック🤖💬✨（30秒だけ）

### ✅ Visual Studio 側

* Visual Studio に **GitHub アカウントでサインイン**
* Copilot が有効になっていれば、入力中にスッと提案が出るよ✍️✨
* チャットが使える環境なら、短い質問から試そ〜！

#### おすすめ最初の一言（教材向け）💞

「このソリューションで、注文→支払い→発送の流れのクラス構成を“超ざっくり”提案して」
→ まだ実装しない！“案を出させる”だけ😌✨

Copilot の導入/状態管理は公式にもまとまってるよ✅ ([Microsoft Learn][3])

---

## 2-8. （任意）VS Code 派のセットアップ💙✨

軽さ重視なら VS Code でも進められるよ😊
C# は **C# Dev Kit** が中心✨ ([Visual Studio Code][4])

### ✅ VS Code 側の基本

1. VS Code を入れる
2. 拡張機能で **C# Dev Kit** を入れる（検索して追加） ([Visual Studio Code][4])
3. .NET 10 SDK が入ってるのを確認（さっきの dotnet コマンド） ([Microsoft][2])
4. Copilot も使うなら、VS Code の Copilot セットアップ手順に沿ってサインイン✨ ([Visual Studio Code][9])

---

## 2-9. 最終チェックリスト✅✅✅（ここまでできたら合格🎓✨）

* [ ] Visual Studio 2026 が起動できる🪟
* [ ] Console App（.NET 10）を作って実行できる▶️ ([Microsoft Learn][1])
* [ ] PowerShell で dotnet の SDK 一覧が出る📜 ([Microsoft][2])
* [ ] Copilot が Visual Studio に入ってる（Installer の Optional components で管理）🤖 ([Microsoft Learn][3])
* [ ] （任意）VS Code + C# Dev Kit でも C# が気持ちよく書ける💙 ([Visual Studio Code][4])

---

## 2-10. よくあるつまずき集🧯💦（困ったらここ）

### 🥲 インストールが途中で失敗する

* 空き容量が足りないパターンが多いよ〜！まず容量確認💾 ([Microsoft Learn][5])
* 回線が不安定なら、オフライン/ネットワーク用レイアウトを検討📦 ([Microsoft Learn][6])

### 🥲 dotnet コマンドが見つからない

* .NET 10 SDK のインストール状態を見直してね（公式ページから入れ直しでもOK）📥 ([Microsoft][2])

### 🥲 C# 14 っぽい機能が効かない

* Visual Studio 2026 と .NET 10 SDK の組み合わせが基本だよ✅ ([Microsoft Learn][8])

---

## 2-11. ミニ課題🎒✨（5〜10分）

### 課題A：環境確認🧪

```text
dotnet --info
dotnet --list-sdks
```

### 課題B：空ソリューション作成📦

* Console App（.NET 10）を作って実行
* そのSolutionを「この教材用フォルダ」に保存✨

### 課題C：Copilot ひとこと練習🤖💬

* チャットでOK：
  「このソリューションで“ミニEC”を作るなら、登場人物（クラス）を10個くらい箇条書きして」
  → 次章で“最悪コード”を作る前に、素材を集める感じだよ🧺💕

---

次は第3章で、**わざと最悪のコード**を作って「つらさ」を体験しにいくよ😈🧱✨
（ここで環境が整ってると、壊して直すのが超スムーズ！）

[1]: https://learn.microsoft.com/ja-jp/visualstudio/releases/2026/release-notes?utm_source=chatgpt.com "Visual Studio 2026 リリース ノート"
[2]: https://dotnet.microsoft.com/en-US/download/dotnet/10.0?utm_source=chatgpt.com "Download .NET 10.0 (Linux, macOS, and Windows) | .NET"
[3]: https://learn.microsoft.com/en-us/visualstudio/ide/visual-studio-github-copilot-install-and-states?view=visualstudio&utm_source=chatgpt.com "Manage GitHub Copilot installation and state"
[4]: https://code.visualstudio.com/docs/languages/csharp?utm_source=chatgpt.com "Installing C# support"
[5]: https://learn.microsoft.com/ja-jp/visualstudio/releases/2026/vs-system-requirements?utm_source=chatgpt.com "Visual Studio 2026 のシステム要件"
[6]: https://learn.microsoft.com/en-us/visualstudio/install/create-a-network-installation-of-visual-studio?view=visualstudio&utm_source=chatgpt.com "Create and maintain a network installation of Visual Studio"
[7]: https://learn.microsoft.com/ja-jp/visualstudio/install/install-visual-studio?view=visualstudio&utm_source=chatgpt.com "Visual Studio をインストールし、お好みの機能を選択する"
[8]: https://learn.microsoft.com/ja-jp/dotnet/csharp/whats-new/csharp-14?utm_source=chatgpt.com "C# 14 の新機能"
[9]: https://code.visualstudio.com/docs/copilot/setup?utm_source=chatgpt.com "Set up GitHub Copilot in VS Code"
