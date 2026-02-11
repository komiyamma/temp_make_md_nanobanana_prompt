# 第74章：「ディレクトリ名」で語る設計 📁🗺️

〜名前を見るだけで役割がわかる配置〜✨

## 今日のゴール 🎯

* 「このクラス、どこに置くの…？😵」を消す
* フォルダ名（＝ラベル）だけで **責務が伝わる** 状態にする
* AIにコード生成させても、**置き場所で迷わない** ようにする 🤖✨

---

## なんでディレクトリ名がそんなに大事なの？🧭

![ddd_cs_study_074_map_metaphor](./picture/ddd_cs_study_074_map_metaphor.png)

コードって、書くより **探す時間** の方が長くなりがちです😅
特に1人開発だと、未来の自分がこう言います👇

> 「え、これ何の層のコード…？どこから呼ばれる想定…？😇」

そしてAIも、置き場所が曖昧だとこうなります👇

* それっぽい場所に適当に増殖する 🧟‍♂️
* “便利そう” な `Utils` に何でも突っ込む 📦💥
* 結果、変更が怖くなる 😭

だから **フォルダ名は“設計の看板”** です✨
看板がちゃんとしてると、地図なしで歩けます🚶‍♀️🗺️

---

## まずは「置き場所の国境」を作ろう 🏰

初心者が最速で迷子を減らすなら、これが鉄板です👇

* **Domain**：ビジネスのルール（最重要）💎
* **Application**：ユースケース（やりたいことの手順）🧩
* **Infrastructure**：DBや外部APIなど現実の接続部分🔌
* **Web**：画面/API（受け口）🌐

「どこに何を置くか」が、フォルダ名で即わかる状態になります✅

![Directory Structure Concept](./picture/ddd_cs_study_074_directories.png)

---

## “見ただけでわかる” ディレクトリ構成（最小の正解例）📁✨

![ddd_cs_study_074_folder_signposts](./picture/ddd_cs_study_074_folder_signposts.png)
 
 ```mermaid
 mindmap
   root((MyApp.sln))
     Domain["💎 Domain (ルール)"]
       Aggregates
       ValueObjects
       Repositories_Interface
     Application["🧩 Application (手順)"]
       UseCases
       Dtos
       Ports_Interface
     Infrastructure["🔌 Infrastructure (実装)"]
       Persistence_EFCore
       External_API
       Repositories_Impl
     Web["🌐 Web (入り口)"]
       Controllers
       Contracts_Request_Response
 ```
 
 C#プロジェクトを4つに分けるイメージです（Solutionの中に4プロジェクト）💡

![ddd_cs_study_074_four_layers_tree](./picture/ddd_cs_study_074_four_layers_tree.png)

```text
MyApp.sln
  src/
    MyApp.Domain/
      Aggregates/
      ValueObjects/
      Events/
      Services/
      Repositories/          (← interface 置き場)
    MyApp.Application/
      UseCases/
      Commands/
      Queries/
      Dtos/
      Ports/                (← 外部に依存しない interface 置き場)
    MyApp.Infrastructure/
      Persistence/
      Repositories/         (← 実装置き場)
      ExternalServices/
      Migrations/
    MyApp.Web/
      Controllers/ or Endpoints/
      Contracts/            (Request/Response)
      Filters/
  tests/
    MyApp.Domain.Tests/
    MyApp.Application.Tests/
```

「見ただけで役割が読める」ってこういうことです📖✨

---

## 各フォルダに“何を入れるか”を一発で覚えるコツ 💡

### Domain（ルールの中心）💎

入れるもの（例）👇

* `Order`（集約ルート）
* `OrderId` / `Money`（値オブジェクト）
* `OrderPlaced`（ドメインイベント）
* `DiscountService`（ドメインサービス）
* `IOrderRepository`（リポジトリの **インターフェース**）

入れないもの 🚫

* EF Coreの `DbContext`
* SQL
* HTTPクライアント
* 設定ファイル読み込み

👉 Domainは「現実世界の事情」を知らないのがカッコいい😎✨

---

### Application（ユースケース係）🧩

入れるもの👇

* 「注文を作成する」「注文をキャンセルする」みたいな **やりたいこと単位**
* DTO（画面に返す形）
* 依存先のインターフェース（Ports）

イメージ例👇

```text
MyApp.Application/
  UseCases/Orders/CreateOrder/
    CreateOrderCommand.cs
    CreateOrderHandler.cs
    CreateOrderResultDto.cs
```

👉 ここは **“手順書”**。ルールはDomainに任せる✨

---

### Infrastructure（現実に接続する係）🔌

入れるもの👇

* EF Coreの `DbContext`、Entity設定、Migration
* Repositoryの実装（DomainのIRepositoryを実装する）
* 外部API呼び出しの実装
* メール送信、ファイル保存など

👉 “汚れ役”を全部ここに引き受けさせる😈（でも大事）

---

### Web（入口）🌐

入れるもの👇

* Controller / Minimal API Endpoint
* Request/Response（Contracts）
* 認証やフィルタ

👉 Webは **受け取って渡すだけ** が理想✨
（ルールを入れ始めたら赤信号🚥）

---

## 絶対に避けたい「迷子フォルダ」たち 😇

![ddd_cs_study_074_lost_in_utils](./picture/ddd_cs_study_074_lost_in_utils.png)

以下が増えたら、将来の自分が泣きます😭

* `Common/`（何でも屋）
* `Utils/`（ブラックホール）🕳️
* `Helpers/`（説明放棄）
* `Managers/`（責務が曖昧）
* 巨大な `Services/`（何でも入る）

どうしても共通化したいなら、せめてこう👇

* `DateTimeProvider` → `Infrastructure/Time/`
* `EmailSender` → `Infrastructure/Mail/`
* `Money` → `Domain/ValueObjects/`

**“用途が名前に出てる”** のが正義です✅✨

---

## 命名ルール：フォルダ名で嘘をつかない 🧠✨

おすすめの小ルール👇（迷いが減ります）

* **名詞で統一**：`Repositories`, `ValueObjects`, `UseCases`
* **役割が伝わる単語**を使う：`Persistence`, `ExternalServices`
* **略語は控えめ**：読み手（未来の自分）に優しく🥺
* **“どこから呼ばれるか”が想像できる**名前にする

---

## AIを“置き場所係”にするプロンプト例 🤖📁

「生成はAI、判断はあなた」…なんだけど、判断もAIに手伝わせてOKです😆✨
（ただし最後の決定はあなたがやるとブレません✅）

### 1) 置き場所を相談する

```text
次のC#クラスは Domain / Application / Infrastructure / Web のどこに置くべき？
理由も1行で。候補が複数あるなら優先順位も出して。

クラス概要：
- 役割：
- 依存しているもの：
- 呼ばれ方：
```

### 2) フォルダ構成を“看板として”評価させる

```text
このフォルダ構成は「見ただけで役割がわかる」？
迷子になりそうな場所を3つ指摘して、改善案も出して。

（ツリー貼り付け）
```

### 3) “Utils化”しそうなコードを分解させる

```text
この Utils に入れようとしてる処理、責務ごとに分割して
適切なフォルダ名とクラス名を提案して。
（コード貼る）
```

---

## 迷わないための「置き場所クイズ」🧪✨

![ddd_cs_study_074_sorting_quiz](./picture/ddd_cs_study_074_sorting_quiz.png)

次のクラス、どこに置く？（答えも下にあるよ✅）

1. `Money`（通貨と小数点ルールを守る）
2. `CreateOrderHandler`（注文作成の手順）
3. `OrderDbContext`（EF Core）
4. `StripePaymentClient`（外部決済API）
5. `CreateOrderRequest`（APIの受け取り用）

**答え👇**
1→Domain 💎 / 2→Application 🧩 / 3→Infrastructure 🔌 / 4→Infrastructure 🔌 / 5→Web 🌐

---

## まとめ 🎉

* ディレクトリ名は **設計の言葉** 📁🗣️
* 最初は **Domain / Application / Infrastructure / Web** の4つでOK ✅
* `Common/Utils` は未来の自分にダメージ大 💥😇
* AIには「生成」だけじゃなく **置き場所レビュー** もやらせると強い 🤖✨

---

次の第75章の演習で、この構成を実際にASP.NET Coreで最小実装して「置き場が気持ちよく決まる感覚」まで体験しようね😆🔥
