# 第13章：Domain Serviceは“最後の手段”🧩

〜Serviceに逃げすぎない、でも“必要なときは堂々と使う”回〜

---

## この章でできるようになること🎯💖

* 「それ、Entity/Value Objectに置けない？」をちゃんと判断できる👀✨
* Domain Serviceを“必要最小”で作れる（巨大Serviceにしない）🧼
* UseCase（Interactor）とDomain Serviceの違いを説明できる🗣️
* “Serviceに逃げて貧血ドメイン”になるのを防げる🩸🛡️

---

## まず超大事な結論🌟

**Domain Serviceは「置き場所がない重要なドメイン処理」のための最終手段**だよ🧩
Eric Evans（DDD）でも「Entity/Value Objectの責務として自然じゃない重要処理なら、サービスとして切り出す」と説明されてるよ📌 ([Domain Language][1])

でもね、ここで事故る人が多いの…🥺💦
**“なんでもService”**にすると、Domainがスカスカになって、結局変更に弱くなるんだ〜🫠

---

## Domain Serviceってなに？🤔🧠

### ✅ ざっくり定義

* **複数のEntity/VOにまたがる**
* だけど、**どれか1つのEntityに置くと不自然**（責務が歪む）
* **ドメインの言葉（ユビキタス言語）で命名**する
* 入出力は**ドメインオブジェクト中心**（DTOじゃない）
* できるだけ**ステートレス**（状態を持って溜めない）

「サービス契約（どう振る舞うか）を定義し、ユビキタス言語で名前を付ける」って点も強調されてるよ📘 ([Domain Language][1])

---

## 3秒でわかる！置き場所の判定フロー🧭✨

![Placement Logic](./picture/clean_cs_study_013_placement_logic.png)

### ① まずEntityに置けない？👑

* その処理が「そのEntityの自然な振る舞い」なら **Entity**

  * 例：`Memo.Rename(title)`、`Account.Withdraw(money)`

### ② Value Objectに置けない？💎

* 値そのものの計算や正規化なら **Value Object**

  * 例：`Money.Add()`、`Email.Normalize()`

### ③ それでも置けない（でもドメイン的に超重要）？🧩

* 複数Entityにまたがって、どっちにも所属しない感じなら **Domain Service**

  * 例：A口座→B口座への送金（2つの口座が絡む）

![Domain Serviceってなに](./picture/clean_cs_study_013_domain_service.png)

### ④ もし「DB保存」「メール送信」「外部API」みたいな“段取り”なら？📦

![Domain Service vs UseCase](./picture/clean_cs_study_013_ds_vs_usecase.png)

* それは **UseCase（Interactor）** の仕事🎮
* Domain Serviceは“段取り屋”になっちゃダメ🙅‍♀️

（Domain ServiceとApplication Serviceの役割の分け方は、定番の整理でもこう説明されるよ）([Enterprise Craftsmanship][2])

---

## よくある事故パターン🧨😇

![The "All-Service" Mistake](./picture/clean_cs_study_013_all_service_mistake.png)

### ❌ 事故1：CRUD Serviceになってる

* `UserService.CreateUser()`
* `MemoService.Save()`
  → だいたいUseCaseかRepository側の話だよ〜😵‍💫

### ❌ 事故2：なんでもServiceに寄せてEntityが空っぽ

* Entityが `Id` と `get/set` しかない
* ルールが全部 `HogeService` にいる
  → “貧血ドメイン”一直線🩸🫠

### ❌ 事故3：Domain Serviceが外部都合を知ってる

* HttpClient、DbContext、Controllerの型、DTO
  → それ入れた瞬間「中心が汚れる」やつ😱

---

## ハンズオン🎮：Domain Serviceが必要になる典型例「送金」💸🏦

![Money Transfer Domain Service](./picture/clean_cs_study_013_money_transfer.png)

（メモ題材と別だけど、Domain Serviceが一番わかりやすい王道例だよ✨）

### 登場人物👥

* `Account`（口座Entity）
* `Money`（金額VO）
* `MoneyTransferService`（送金Domain Service）

ポイントはこれ👇

* 引き出す/預けるは **Accountの自然な振る舞い**
* 「2つの口座を同時に扱う送金」は **どっちの口座の責務でもない**
  → だからDomain Serviceが“ちょうどいい”🧩✨

---

### 1) Value Object：Money💎

```csharp
public readonly record struct Money(decimal Amount, string Currency)
{
    public Money
    {
        if (Amount <= 0) throw new ArgumentOutOfRangeException(nameof(Amount), "金額は正の値にしてね");
        if (string.IsNullOrWhiteSpace(Currency)) throw new ArgumentException("通貨が必要だよ", nameof(Currency));
    }

    public static void EnsureSameCurrency(Money a, Money b)
    {
        if (!string.Equals(a.Currency, b.Currency, StringComparison.OrdinalIgnoreCase))
            throw new InvalidOperationException("通貨が違うと送金できないよ");
    }
}
```

---

### 2) Entity：Account👑

```csharp
public sealed class Account
{
    public Guid Id { get; }
    public Money Balance { get; private set; }

    public Account(Guid id, Money initialBalance)
    {
        Id = id;
        Balance = initialBalance;
    }

    public bool CanWithdraw(Money money)
    {
        Money.EnsureSameCurrency(Balance, money);
        return Balance.Amount >= money.Amount;
    }

    public void Withdraw(Money money)
    {
        Money.EnsureSameCurrency(Balance, money);
        if (!CanWithdraw(money)) throw new InvalidOperationException("残高が足りないよ");
        Balance = new Money(Balance.Amount - money.Amount, Balance.Currency);
    }

    public void Deposit(Money money)
    {
        Money.EnsureSameCurrency(Balance, money);
        Balance = new Money(Balance.Amount + money.Amount, Balance.Currency);
    }
}
```

---

### 3) Domain Service：MoneyTransferService🧩

```csharp
public interface IMoneyTransferService
{
    void Transfer(Account from, Account to, Money amount);
}

public sealed class MoneyTransferService : IMoneyTransferService
{
    public void Transfer(Account from, Account to, Money amount)
    {
        if (from.Id == to.Id) throw new InvalidOperationException("同じ口座には送金できないよ");

        // ここが “複数Entityにまたがるドメインルール” の置き場所✨
        Money.EnsureSameCurrency(from.Balance, amount);
        Money.EnsureSameCurrency(to.Balance, amount);

        from.Withdraw(amount);
        to.Deposit(amount);
    }
}
```

✅ このService、えらいところ👇

* DB保存しない🗄️❌
* HTTPも知らない🌐❌
* DTOも知らない🍱❌
* 口座とお金（ドメイン）だけで完結👑💎

---

## じゃあUseCase（Interactor）は何するの？🎮🧵

UseCaseは「段取り係」だよ〜📋✨

* 口座をRepositoryから取ってくる
* Domain Serviceを呼ぶ
* 保存する
* 成功/失敗をPresenterへ渡す

（Domain ServiceとUseCaseの役割をちゃんと分けるのがコツだよ🧼）

```csharp
public sealed class TransferMoneyInteractor
{
    private readonly IAccountRepository _repo;
    private readonly IMoneyTransferService _transfer;

    public TransferMoneyInteractor(IAccountRepository repo, IMoneyTransferService transfer)
    {
        _repo = repo;
        _transfer = transfer;
    }

    public void Handle(Guid fromId, Guid toId, Money amount)
    {
        var from = _repo.Get(fromId);
        var to = _repo.Get(toId);

        _transfer.Transfer(from, to, amount);

        _repo.Save(from);
        _repo.Save(to);
    }
}
```

---

## ミニ課題💪✨（“Serviceに逃げない筋トレ”）

### 課題1：置き場所クイズ🧠🎯

![Placement Quiz](./picture/clean_cs_study_013_placement_quiz.png)

次の処理、どこに置く？（Entity / VO / Domain Service / UseCase）

1. `メール送信して完了通知する` 📧
2. `Moneyの通貨が一致するか検証する` 💱
3. `2つのAccount間で送金する` 💸
4. `DBからAccountを検索して取ってくる` 🗄️
5. `Memoのタイトル文字数を制限する` ✍️

**答え**👇

1. UseCase（段取り）
2. VO
3. Domain Service
4. UseCase（＋Repository）
5. Entity か VO（TitleをVOにするならVOが強い💎）

---

## AI活用🤖✨（Copilot / Codex向けプロンプト例）

* 「この処理、Entityに置くべき？Domain Serviceに置くべき？理由もセットで提案して」🧠
* 「Domain Serviceが肥大化しそう。責務分割案を3つ出して」🧩
* 「UseCaseとDomain Serviceの責務が混ざってないかレビューして、混ざってたら直して」🧼
* 「“貧血ドメイン”っぽい匂いがする箇所を指摘して、Entityに戻すリファクタ案ちょうだい」🩸

---

## まとめ🎀✅

* **まずEntity/VOに置けないか粘る**👑💎
* それでもダメで、**複数Entityにまたがる重要ルール**ならDomain Service🧩
* Domain Serviceは**段取りをしない**（保存・通知・外部呼び出しはUseCaseへ）🎮
* “なんでもService”にすると設計が崩れるから、**最後の手段として丁寧に**🛟✨

---

## ちいさな最新メモ🆕📌

2026年1月時点では、.NET 10.0系の更新（1/13付など）や、.NET 8/9/10の月例アップデート情報がMicrosoftから出てるよ🧰✨ ([Microsoft for Developers][3])

---

次は「第13章のミニ課題」を、あなたの題材（メモアプリ）に寄せて **“Domain Serviceが本当に必要になる場面”** を一緒に作っちゃう？📝💖

[1]: https://www.domainlanguage.com/wp-content/uploads/2016/05/DDD_Reference_2015-03.pdf "Microsoft Word - pdf version of final doc - Mar 2015.docx"
[2]: https://enterprisecraftsmanship.com/posts/domain-vs-application-services/?utm_source=chatgpt.com "Domain services vs Application services"
[3]: https://devblogs.microsoft.com/dotnet/dotnet-and-dotnet-framework-january-2026-servicing-updates/?utm_source=chatgpt.com ".NET and .NET Framework January 2026 servicing ..."
