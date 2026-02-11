# 第94章：他人のコードを「設計の目」で読む 👀✨

![他人のコードを設計の目で読む](./picture/ddd_cs_study_094_reading_code.png)

### 〜OSSやAI生成コードの“裏側”を見抜けるようになろう〜 🤖🧠

この章は、「自分で書く」よりちょい難しい **“読む力”** を鍛える回だよ〜！📚💪
AI（CopilotやCodex系）を使うほど、**「出てきたコードを正しく読んで判断する力」** が超大事になるのね…！🧯✨

---

## この章のゴール 🎯🌸

読み終わったら、こんなことができるようになるよ！

* OSSやAI生成コードを見たとき、**全体構造（設計）をサクッと把握**できる 👀📦
* 「良い・微妙」を **“感覚”じゃなくチェック項目で判断**できる ✅🧩
* AIにコードを読ませるときも、**ブレない質問（プロンプト）**が作れる 🗣️🧠
* 「直すべき場所」「触ったら危険な場所」を見分けられる 🚧💥

---

## 1) 「設計の目」ってなに？👁️✨（コードの“意味”じゃなく“意図”を見る）

初心者がコードを読むときって、ついこうなりがち👇🥺

* 「このifは何してるの？」
* 「このメソッドは何を返すの？」

もちろん大事なんだけど、**設計の目**で見るときはこう見るよ👇😎✨

* **なぜこの責務（役割）に分けた？** 🧩
* **変更が来たら、どこを直す想定？** 🔁
* **依存（つながり）の向きは安全？** 🧲
* **ルール（不変条件）はどこで守ってる？** 🛡️

DDDっぽく言うと、
「ドメイン（大事なルール）を守るための形になってる？」を見る感じだね🏰✨

---

## 2) 最初にやる「3分の全体把握」⏱️🗺️（ここが勝負！）

他人のコードを読むとき、いきなりクラスを開かない！🙅‍♀️💦
まずは **“地図”** を見るのが最強だよ📍✨

### 3分チェックリスト ✅

* README：目的・動かし方・思想（ここに全部出る）📄✨
* フォルダ/プロジェクト構成：レイヤー分けの方針が見える 📁
* `Program.cs`：依存性注入（DI）や起動の流れ＝“玄関”🚪
* `Tests`：テストの置き方＝設計の自信の表れ 🧪
* `*.csproj`：依存パッケージ＝思想がバレる 📦👀

---

## 3) 10分でできる「設計スキャン」🩻✨（読む順番のテンプレ）
 
 これ、超おすすめの順番！慣れると爆速になるよ🚀💨
 
 ```mermaid
 flowchart LR
     Map[1. Map<br/>README] --> Door[2. Door<br/>Program/DI]
     Door --> Border[3. Border<br/>Layers]
     Border --> Flow[4. Flow<br/>UseCase]
     
     style Map fill:#caffbf,stroke:#383
     style Border fill:#ffdfba,stroke:#f80
 ```
 
 ### Step A：入口を探す 🚪

* Webなら：Controller / Endpoint / Razor / Blazorの入口
* APIなら：Endpoint→Application→Domain の流れ
* バッチなら：`Main`やHostedServiceあたり

**コツ**：入口から「1つのユースケース」を追跡する👣✨
例）「注文する」「予約する」「ログインする」みたいな1本ね！

---

### Step B：境界線（レイヤー）を見つける 🧱

代表的にはこんな分かれ方👇

* **Domain**：ルールの中心（エンティティ、値オブジェクト、集約）👑
* **Application**：ユースケース（手順、取引の流れ）🧭
* **Infrastructure**：DBや外部API（差し替えたい部分）🔌
* **UI/Web**：画面・APIの入口（受け取って渡す）🎮

「ドメインが中心にいて、外側が差し替え可能」だと読みやすいことが多いよ✨
この発想はオニオン/クリーン系でよく出るやつね🧅✨

---

### Step C：依存の向きをチェックする 🧲⚠️

設計が崩れてると、だいたいこうなる👇😭

* DomainがInfrastructure（EF Coreとか）を直接参照してる
* ApplicationがUIの型（ViewModelとか）を参照してる
* どこからでもどこへでも参照できる（境界線なし）

依存の向きがキレイだと、**変更の爆発が起きにくい**よ💣➡️🧯

---

## 4) DDD初心者向け：「ここだけ見ればOK」ポイント7つ 🥰✅

DDD初めてでも、まずはここだけで十分強いよ💪✨

### ① “言葉”が揃ってる？（ユビキタス言語っぽいやつ）🗣️📘

クラス名やメソッド名が
**業務の言葉**になってると読みやすい！

例：`Order`, `Money`, `EmailAddress`, `PlaceOrder()` みたいな感じ💡

---

### ② 値がそのまま `string/int` で流れてない？ 🧨

設計が弱いと、どこもかしこも `string` と `int` だらけになる😇
DDD寄りだと、**型で意味を持たせる**ことが多いよ✨

* `EmailAddress`
* `UserId`
* `Money`

---

### ③ ルール（不変条件）が “散ってない”？ 🧷

「ここでもチェック、あっちでもチェック」だと破綻しやすい💥
いい感じだと、**生成時や操作時に一箇所で守る**🛡️

---

### ④ 集約ルートっぽい“司令塔”がいる？ 🧑‍✈️

外から子オブジェクトを直接いじれないようにしてると、破壊されにくい✨

---

### ⑤ Repositoryは “保存の詳細” を隠せてる？ 📦

ドメイン層がSQLやEFの詳細を知らないと、だいぶ健康体🌿

---

### ⑥ Applicationが “手順”、Domainが “ルール” になってる？ 🧭👑

* Application：フロー（AしてBしてCする）
* Domain：ルール（これはダメ・これはOK）

これが混ざると読みにくい〜😭

---

### ⑦ テストが “境界線の味方” になってる？ 🧪🧡

テストがある場所は、だいたい「守りたい設計」がある場所✨
逆にテストが薄いと、**設計も崩れてる**こと多い…（あるある）🥺

---

## 5) AI生成コードを「設計の目」で読むコツ 🤖🔍（あるある7連発）

AIコードは便利だけど、**設計目線だと“クセ”が出やすい**よ👇😇

### AIコードあるある 😅

1. **1ファイルが太りがち**（責務が混ざる）🍔
2. **命名がフワッとする**（言葉が揃わない）🌫️
3. **境界線をまたいで参照しがち**（Domainが外部に依存）🧲💥
4. **例外処理が雑**（何でもException）🧨
5. **DTOが増殖**（何のための型か分からない）👻
6. **コピペ構造が増える**（同じ形のメソッドが量産）📎
7. **“正しいっぽい”けどルールが抜ける**（仕様の穴）🕳️

だからAIを使うほど、こっちがやるべきはこれ👇✨
✅ **「境界線」と「ルールの置き場所」をチェックする**
これだけで一気に事故が減るよ🧯✨

---

## 6) AIと一緒に“読む”ためのプロンプト集 🗣️🤖✨

Copilot Chatみたいなチャット系は、「読む」の相棒として強いよ💬
（Copilot ChatはIDEやGitHub上などで使えるよ） ([GitHub Docs][1])

### プロンプト①：全体像を3行で

```text
このリポジトリの「レイヤー構造」と「責務分担」を、初心者向けに3行で説明して。
入口（UI）→アプリ層→ドメイン層→インフラ層の流れが分かるように。
```

### プロンプト②：境界線が破れてる場所を探して

```text
Domain層がInfrastructureやEF Coreの型に依存している箇所があるか探して、候補ファイルと理由を教えて。
（“依存の向きが危ない”観点で）
```

### プロンプト③：ユビキタス言語チェック📘

```text
ドメイン用語（ユビキタス言語）っぽいクラス名・メソッド名を一覧化して。
逆に「曖昧で意図が読み取りにくい命名」もピックアップして改善案を出して。
```

### プロンプト④：1ユースケース追跡👣

```text
「注文を確定する（または主要ユースケース）」処理の呼び出し経路を、入口から順に箇条書きで追跡して。
各ステップの責務（なぜそこにあるべきか）も一言で。
```

### プロンプト⑤：AI生成コードの監査モード🧯

```text
この変更（またはこのクラス）がAI生成っぽいとして、設計的に危ない点を7つの観点でレビューして：
1)責務 2)境界線 3)命名 4)例外 5)ルールの置き場所 6)重複 7)テスト容易性
```

---

## 7) 実戦演習：OSSを「設計の目」で読む 🏋️‍♀️✨

“読む筋トレ”は、短時間で回すのがコツだよ⏱️💕

### 演習A：テンプレ系で境界線を見る（おすすめ）📦

まずは「設計の型」が分かりやすいリポが読みやすい！
例：**ardalis/CleanArchitecture** や **jasontaylordev/CleanArchitecture** みたいな、クリーンアーキ寄りのテンプレたち。 ([GitHub][2])

**やること（45分）**

1. READMEを読む（目的と思想）📄
2. プロジェクト構成を図にする（手書きでOK）🗺️
3. `Program.cs` を見てDI登録を眺める（どこが差し替え点？）🔌
4. Domain層で「値オブジェクトっぽい型」を3つ探す👀
5. 「この設計は何の変更に強い？」を1行で書く✍️

---

### 演習B：実アプリ系で“現実”を見る 🛒✨

Microsoft系の参照アプリとして **eShop** 系も有名だよ（サービスベース構成の参考）。 ([GitHub][3])
（ただ、でっかいので“読む筋トレ”は部分だけでOK！）

**やること（30分）**

* 入口→Application→Domain（っぽい所）を、1ユースケースだけ追う👣
* 「境界線が守られてる所 / 破れてそうな所」を各1つメモ📝

---

### 演習C：AI生成コードをレビューして“見抜く”🧨→🧯

AIに適当にCRUDを生成させて（CopilotでもCodexでもOK）、この章のチェックで監査するよ！

**やること（30分）**

* 生成コードから「境界線をまたいでる参照」を探す🧲
* `string/int` のまま流れてる“意味のある値”を3つ型にする🧩
* ルールが分散してたら「ここに集める」と決める🛡️
* その変更に対して、AIにテスト雛形を作らせる🧪✨

---

## 8) ここまでのまとめ 🌸✨

他人のコードを読むときは、こう考えるとラクだよ😊

* **最初に地図**（README・構成・入口）🗺️
* **ユースケース1本だけ追う**👣
* **境界線と依存の向き**を見る🧲
* **ルールの置き場所**を見る🛡️
* AIには「要約」じゃなくて「設計の観点」で質問する🤖💬

C#はどんどん進化してて（.NET 10 / C# 14、Visual Studio 2026など）、新しい書き方も増えてるけど、**設計の見方はずっと使える武器**だよ🔧✨ ([Microsoft Learn][4])

---

## ミニ確認クイズ（3問）📝🐣

1. 他人のコードを読むとき、最初にクラスを開かずに見るべきものは？👀
2. 「境界線が破れてる」って、具体的にどういう状態？🧱💥
3. AI生成コードで特に事故りやすいのは「どこ」と「どこ」の境界？🤖🧲

（答えは自分の言葉でOK！AIに採点させてもOKだよ〜😆✨）

---

* [theverge.com](https://www.theverge.com/news/808032/github-ai-agent-hq-coding-openai-anthropic?utm_source=chatgpt.com)
* [theverge.com](https://www.theverge.com/news/669339/github-ai-coding-agent-fix-bugs?utm_source=chatgpt.com)
* [theverge.com](https://www.theverge.com/news/753984/microsoft-copilot-gpt-5-model-update?utm_source=chatgpt.com)
* [itpro.com](https://www.itpro.com/software/development/github-just-launched-a-new-mission-control-center-for-developers-to-delegate-tasks-to-ai-coding-agents?utm_source=chatgpt.com)
* [techradar.com](https://www.techradar.com/pro/angry-github-users-want-to-ditch-copilot-features-forced-upon-them?utm_source=chatgpt.com)

[1]: https://docs.github.com/en/copilot/get-started/features?utm_source=chatgpt.com "GitHub Copilot features"
[2]: https://github.com/ardalis/CleanArchitecture?utm_source=chatgpt.com "ardalis/CleanArchitecture: Clean Architecture Solution ..."
[3]: https://github.com/dotnet/eShop?utm_source=chatgpt.com "dotnet/eShop: A reference .NET application implementing ..."
[4]: https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-14?utm_source=chatgpt.com "What's new in C# 14"
