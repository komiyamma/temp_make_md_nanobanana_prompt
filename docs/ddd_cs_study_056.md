# 第56章：レイヤードアーキテクチャ 🧁✨

![レイヤードアーキテクチャ](./picture/ddd_cs_study_056_layered_stack.png)

**〜古典的だけど、1人開発なら「これで十分」になりやすい〜**😊

---

## 今日のゴール 🎯

この章が終わったら、次ができるようになります👇✨

* 「このコード、どこに置くの？」で迷いにくくなる 🧭
* 変更に強い“置き場所ルール”を持てる 🧱
* AIに頼んでも構造がグチャらない指示ができる 🤖💡

---

## 1. レイヤードアーキテクチャってなに？🍰

一言でいうと…

> **役割が違うものを、層（レイヤー）で分ける設計**だよ😊

ミルフィーユみたいに「層」を作って、役割が混ざらないようにします🧁✨
混ざるとどうなるかというと…
**UIの都合がビジネスルールを壊したり**、**DBの事情で仕様が歪んだり**します😱💦

---

## 2. 1人開発でレイヤードが効く理由 🏃‍♀️💨

1人開発って「スピード」が命だけど、**未来の自分が敵**になりがち…👻💦
レイヤードにすると、未来の自分がこう思えるようになるよ👇😊

* 「画面の変更？じゃあ Presentation だな」📱
* 「ルール変更？ Domain だな」⚖️
* 「DB差し替え？ Infrastructure だな」🗄️

つまり、**変更の着地地点がすぐ分かる**のが最強ポイントです✨

---

## 3. レイヤードの定番4層 🧩

DDD寄りに“今どきの分け方”でいくと、だいたいこの4つが安定です👇😊

### ① Presentation（表示・入口）🚪📱

* 画面、API、Controller、Endpoint、UI入力など
* **“受け取って渡す”が仕事**
* ルールは基本ここに置かない🙅‍♀️

### ② Application（ユースケース）🧭

* 「ユーザーがやりたいこと」を実行する係
* 例：会員登録する、注文する、予約する
* **ドメインを呼び出して流れを組み立てる**✨

### ③ Domain（ビジネスルールの中心）👑📚

* Entity / Value Object / Domain Service / Domain Event
* **“このアプリの正しさ”がここ**
* DBもWebも知らないのが理想😊

### ④ Infrastructure（外部と接続）🔌🗄️

* DB、外部API、メール送信、ファイル保存など
* Repository の実装もここに置きがち✨
 
 ```mermaid
 block-beta
   columns 1
   Presentation["Presentation (UI/API)"]
   Application["Application (UseCase)"]
   Domain["Domain (Rules) 👑"]
   Infrastructure["Infrastructure (DB/Ext) 🔌"]
 
   Presentation --> Application
   Application --> Domain
   Infrastructure --> Domain
   
   style Domain fill:#f9f,stroke:#333,stroke-width:2px
 ```
 
 （ちなみに、2025の最新C#は **C# 14**、対応は **.NET 10** だよ🧡） ([Microsoft Learn][1])
（IDEも最新版ラインとして **Visual Studio 2026** が案内されてます） ([Visual Studio][2])

---

## 4. 「どこに置く？」迷わないルール 🧭✨

迷ったら、この質問を自分に投げてね😊

* **Q1：画面やAPIの都合？** → Presentation 📱
* **Q2：操作の手順（ユースケース）？** → Application 🧭
* **Q3：業務ルール（正しさ）？** → Domain 👑
* **Q4：DB/外部サービス都合？** → Infrastructure 🔌

そして超重要ルール👇🔥
✅ **Domain は外側（DBやWeb）を知らない**
これだけで世界がキレイになります✨

---

## 5. 最小サンプル：本を借りる（超ミニ）📚😊

「会員は最大5冊まで借りられる」ってルールがあるとします！

### フォルダ（プロジェクト）例 🧱

```text
MyLibrary
├─ MyLibrary.Web            (Presentation)
├─ MyLibrary.Application    (Application)
├─ MyLibrary.Domain         (Domain)
└─ MyLibrary.Infrastructure (Infrastructure)
```

---

### Domain：ルールの中心 👑

```csharp
namespace MyLibrary.Domain;

public readonly record struct MemberId(Guid Value);
public readonly record struct BookId(Guid Value);

public sealed class Member
{
    private readonly List<BookId> _borrowed = new();
    public MemberId Id { get; }

    public IReadOnlyList<BookId> Borrowed => _borrowed;

    public Member(MemberId id) => Id = id;

    public Result Borrow(BookId bookId)
    {
        if (_borrowed.Count >= 5)
            return Result.Fail("これ以上借りられません（最大5冊）😢");

        if (_borrowed.Contains(bookId))
            return Result.Fail("同じ本を二重に借りるのはNGだよ😵‍💫");

        _borrowed.Add(bookId);
        return Result.Ok();
    }
}

public sealed record Result(bool IsSuccess, string? Error)
{
    public static Result Ok() => new(true, null);
    public static Result Fail(string message) => new(false, message);
}

public interface IMemberRepository
{
    Task<Member?> FindAsync(MemberId id, CancellationToken ct);
    Task SaveAsync(Member member, CancellationToken ct);
}
```

👉ポイント😊

* **ルール（最大5冊）はDomainに置いた**👑
* DomainはDBを知らない（IMemberRepositoryだけ）✨

---

### Application：ユースケース 🧭

```csharp
using MyLibrary.Domain;

namespace MyLibrary.Application;

public sealed class BorrowBookUseCase
{
    private readonly IMemberRepository _repo;

    public BorrowBookUseCase(IMemberRepository repo) => _repo = repo;

    public async Task<Result> HandleAsync(MemberId memberId, BookId bookId, CancellationToken ct)
    {
        var member = await _repo.FindAsync(memberId, ct);
        if (member is null) return Result.Fail("会員が見つからないよ🥲");

        var result = member.Borrow(bookId);
        if (!result.IsSuccess) return result;

        await _repo.SaveAsync(member, ct);
        return Result.Ok();
    }
}
```

👉ポイント😊

* Applicationは「手順」を書く場所
* ルールそのものはDomainへ委譲✨

---

### Infrastructure：保存の実装（今回はインメモリで）🗄️

```csharp
using System.Collections.Concurrent;
using MyLibrary.Domain;

namespace MyLibrary.Infrastructure;

public sealed class InMemoryMemberRepository : IMemberRepository
{
    private readonly ConcurrentDictionary<MemberId, Member> _store = new();

    public Task<Member?> FindAsync(MemberId id, CancellationToken ct)
        => Task.FromResult(_store.TryGetValue(id, out var m) ? m : null);

    public Task SaveAsync(Member member, CancellationToken ct)
    {
        _store[member.Id] = member;
        return Task.CompletedTask;
    }

    // デモ用：会員を事前に入れておく
    public void Seed(Member member) => _store[member.Id] = member;
}
```

---

### Presentation：入口（最小APIっぽく）🚪✨

```csharp
using Microsoft.AspNetCore.Builder;
using Microsoft.Extensions.DependencyInjection;
using MyLibrary.Application;
using MyLibrary.Domain;
using MyLibrary.Infrastructure;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddSingleton<InMemoryMemberRepository>();
builder.Services.AddSingleton<IMemberRepository>(sp => sp.GetRequiredService<InMemoryMemberRepository>());
builder.Services.AddScoped<BorrowBookUseCase>();

var app = builder.Build();

// デモ用 seed
var repo = app.Services.GetRequiredService<InMemoryMemberRepository>();
var memberId = new MemberId(Guid.NewGuid());
repo.Seed(new Member(memberId));

app.MapPost("/members/{memberId:guid}/borrow/{bookId:guid}", async (Guid memberId, Guid bookId, BorrowBookUseCase useCase) =>
{
    var result = await useCase.HandleAsync(new MemberId(memberId), new BookId(bookId), CancellationToken.None);
    return result.IsSuccess ? Results.Ok("借りたよ〜📚✨") : Results.BadRequest(result.Error);
});

app.Run();
```

👉ポイント😊

* Presentationは「受け取って返す」係
* ルールをここに書き始めたら黄色信号🚥💦

---

## 6. よくある事故あるある 😇💥

### 😵‍💫 事故1：Controllerにルールが増殖

「最大5冊」判定をControllerに書き始める → 画面が増えるほど崩壊💣

### 😵‍💫 事故2：DomainがDBを知ってしまう

Domainで `DbContext` を使い始める → ルールがDBの都合に支配される🫠

### 😵‍💫 事故3：Applicationが巨大な神クラス

UseCaseが何百行→「結局どこ直すの？」状態に😱
👉 小さく分けるのが正義✨

---

## 7. AIに頼むときの“崩れない”指示テンプレ 🤖🧡

コピペして使ってOKだよ😊✨

* 「この機能を **Presentation / Application / Domain / Infrastructure** に分けて、配置理由も書いて」🧠
* 「Domainには **ビジネスルールだけ**、DBやWeb依存は入れないで」🚫
* 「UseCaseは手順だけ。ルールはEntityのメソッドに寄せて」🧭
* 「Controllerを薄くして。入力→UseCase→結果返すだけに」📱

---

## 8. ミニ演習 📝✨（15〜30分）

### 演習A：置き場所クイズ🎮

次のコードはどこに置く？（理由も！）

1. 「メールアドレス形式チェック」📧
2. 「注文合計金額を計算」🧾
3. 「DBから注文を取得するSQL」🗄️
4. 「画面の入力をDTOに詰める」📦

### 演習B：あなたの過去コードを3層に分ける🧹

昔の小さめプロジェクトから1画面（1機能）選んで、

* Presentation：入口
* Application：手順
* Domain：ルール
  に分けてみてね😊✨
  AIには「どこに置くべきかレビューして」って頼むと爆速です⚡🤖

---

## まとめ 🍀

レイヤードは派手じゃないけど、**1人開発の“迷い”を消す武器**だよ😊🧡
まずはこれで「置き場所の筋」を作るのが、AI時代の最短ルートです✨

次の章（オニオン）では、さらに **“依存の向き”** を美しくしていくよ〜🧅✨

[1]: https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-14?utm_source=chatgpt.com "What's new in C# 14"
[2]: https://visualstudio.microsoft.com/downloads/?utm_source=chatgpt.com "VS Code Downloads for Windows, Mac, Linux - Visual Studio"
