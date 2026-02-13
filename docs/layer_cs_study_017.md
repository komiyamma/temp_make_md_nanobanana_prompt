# 第17章：DI実践②（ライフサイクルは最低限）⏳

（Singleton / Scoped / Transient を“事故らず”使えるようになる回だよ〜！😊）

---

## 0. この章でできるようになること🎯💖

* 「いつ作られて、いつ捨てられるか」をイメージできる🧠✨
* **Singleton / Scoped / Transient** を“最低限のルール”で選べる✅
* 初心者がやりがちな **使い回し事故💥（スコープ違反・状態混入・DbContext事故）** を回避できる🛡️
* Webでもデスクトップでも「Scopedって何？」が腑に落ちる😺

※2026の最新前提として、.NET 10（LTS）+ Visual Studio 2026 + C# 14 でOKだよ〜🆕✨（例：.NET 10.0 は 2026-01-13 に 10.0.2 が出てるよ）([Microsoft][1])

---

## 1. まず“ライフサイクル”って何？⏳

DIの登録って、実は「どのくらい生きるインスタンスを作る？」を宣言してるだけ！😊

> **ライフサイクル＝インスタンスの寿命**

* いつ作る？（Resolve時 / 起動時 など）
* いつ捨てる？（リクエスト終了 / アプリ終了 など）

.NETのDIは主に **3つ**（これだけでOK！）

* **Transient**（毎回新品）
* **Scoped**（スコープ内で使い回し）
* **Singleton**（アプリ全体で使い回し）([Microsoft Learn][2])

---

## 2. 3つの寿命を“超ざっくり表”で掴む🧠✨

![ライフサイクル](./picture/layer_cs_study_017_lifecycles.png)

| 種類        | たとえ        | いつ増える？ | いつ捨てる？                  | 向いてるもの                  |
| --------- | ---------- | ------ | ----------------------- | ----------------------- |
| Transient | コンビニの割り箸🥢 | 使うたび   | 使い終わり（スコープ終わりで破棄されることも） | 軽い・状態を持たない処理            |
| Scoped    | 1回の注文の伝票🧾 | スコープごと | スコープ終了                  | リクエスト単位の仕事（DbContextなど） |
| Singleton | 家の冷蔵庫🧊    | 最初の1回  | アプリ終了                   | 共有してOKなもの（キャッシュ等）       |

```mermaid
gantt
    title ライフサイクルの比較
    dateFormat s
    axisFormat %S

    section Request 1
    Request Start  : 0
    Request End    : 10

    section Transient
    Instance A (Created) : 2, 3
    Instance B (Created) : 5, 2
    
    section Scoped
    Instance C (Shared in Req) : 0, 10
    
    section Singleton
    Instance D (Shared App-wide) : 0, 20
```

---

## 3. 超重要：「Scoped」って結局なに？（Webとデスクトップで違う）🤔💡

### 3.1 Web（ASP.NET Core）のScoped 🌐

Webでは **基本：1リクエスト＝1スコープ** だよ😊

* リクエストの間は同じインスタンスを使い回す
* リクエストが終わったらまとめて破棄

この性質のおかげで、`DbContext` は **Scopedが安全**って話になる（後でやるね）🗄️✨
※EF Core の `AddDbContext` は **既定で Scoped 登録**だよ ([Microsoft Learn][3])

---

### 3.2 デスクトップ / Console のScoped 🖥️

デスクトップやConsoleは「リクエスト」がないから、**自動スコープが生まれない**の🥺
だから Scoped を使うなら、**自分でスコープを作る**必要があるよ！

例：ボタン1回クリック＝1スコープ、みたいに決める感じ😊

---

## 4. 事故ポイントその①：Singleton が Scoped を抱えると爆発💥（超ある）

### 4.1 何が起きるの？😱

**Singleton**（ずっと生きる）
　↓（依存）
**Scoped**（本当は短命で捨てられるはず）

これ、設計として破綻しやすいの。
ASP.NET Core だと、これが原因で **「ScopedをSingleton扱いしてるよ！」** みたいなエラーになることがあるよ ([Microsoft Learn][4])

### 4.2 ありがちな例（背景だけ理解できればOK）

* `BackgroundService`（だいたいSingleton扱い）から `DbContext`（Scoped）を直inject
* Singletonなキャッシュサービスが、Scopedなユーザー情報サービスを保持しちゃう
* SingletonなミドルウェアがコンストラクタでScopedを受け取ってしまう（これも典型）([Microsoft Learn][4])

---

## 5. 事故ポイントその②：状態（mutable）をSingletonに置いて混ざる💥🌀

Singletonは **全員で共有**だから…

* 「前のユーザーの値が残る」
* 「並列アクセスで壊れる」
* 「スレッドセーフじゃなくて落ちる」

が起きがち😇

**初心者ルール：Singletonは“状態を持たない”か“持っても不変”に寄せる**✅

---

## 6. 事故ポイントその③：DbContext を Scoped 以外にして地獄🗄️🔥

`DbContext` は基本 **Scopedが正解**。
`AddDbContext` が既定でScoped登録なのも、そのためだよ ([Microsoft Learn][3])

理由（やさしく）😊

* `DbContext` は「作業中の変更追跡」を持つ
* 共有しすぎると **追跡が溜まり続ける** / **並列で触って壊れる**
* Webでは「1リクエスト1スコープ」が自然に合う ([Microsoft Learn][3])

---

## 7. 事故ポイントその④：Validationが強くなって“開発時に爆発”するやつ💣

最近の.NETでは、開発環境で **DIの検証**が強めに効くことがあるよ（早期発見できるから基本は良い）😊

* Generic Host は Development 環境で **スコープ検証や依存関係検証**を有効にする、と説明されてるよ ([Microsoft Learn][5])
* .NET 9 では「開発環境で ValidateOnBuild / ValidateScopes が有効化される」変更が案内されてる ([Microsoft Learn][6])

要するに：
**“本番でたまたま動く”コードが、開発で止められる**ことがある（でもそれはありがたい）🙏✨

---

## 8. まずのおすすめ運用ルール（これだけで勝てる）🏆✅

ここ、章タイトルの「最低限」のコアだよ〜😊✨

### 8.1 迷ったらこの基本セット🧩

* **Application層（UseCase/Service）**：基本 **Scoped**

  * 1回の処理（＝1スコープ）で整合が取りやすい😊
* **Infrastructure層のRepository**：基本 **Scoped**

  * `DbContext` を使うなら揃える
* **DbContext**：**Scoped（固定）** ([Microsoft Learn][3])
* **軽くて状態を持たない部品**：**Transient**
* **キャッシュ・共有設定・重い変換器**：**Singleton（ただしスレッドセーフ！）**

### 8.2 「Singletonにしていい条件」3つだけ覚えて😺

Singletonにしていいのは、だいたいこれ全部満たすとき👇

1. **状態が不変**（または完全にスレッドセーフ）
2. **Scoped/Transient を保持しない**（抱えない）
3. `IDisposable` の扱いも理解してる（破棄タイミング）

---

## 9. 実装（超ミニ）：Program.csの登録パターン🧪✨

Web（最小APIでもMVCでも同じ考え方だよ😊）

```csharp
// 軽い・状態なし → Transient
builder.Services.AddTransient<PriceCalculator>();

// ユースケース（1回の処理単位） → Scoped
builder.Services.AddScoped<CreateTodoUseCase>();

// EF Core → AddDbContextは既定でScoped
builder.Services.AddDbContext<AppDbContext>();

// 共有キャッシュ（スレッドセーフ前提） → Singleton
builder.Services.AddSingleton<InMemoryCache>();
```

---

## 10. 実践ワーク①：寿命を“目で見る”👀✨（超おすすめ）

### ゴール🎯

「Scopedって1リクエストで同じ」「Transientは毎回違う」を体験する！

#### ステップ

1. 生成時にGUIDを作るサービスを作る
2. Controller/Handlerで2回使う
3. ログに出す

例（イメージ用）：

```csharp
public sealed class InstanceMarker
{
    public Guid Id { get; } = Guid.NewGuid();
}
```

* `AddTransient<InstanceMarker>()` → 使うたびにIDが変わる
* `AddScoped<InstanceMarker>()` → 同じリクエスト内ではIDが同じ
* `AddSingleton<InstanceMarker>()` → ずっと同じ

---

## 11. 実践ワーク②：わざと事故らせて直す💥➡️🛠️（最強の学び）

### 事故らせる例😇

* SingletonサービスがScoped（例：DbContext）をコンストラクタで受け取る

```csharp
// 悪い例（学習用！）
builder.Services.AddSingleton<BadSingleton>();
builder.Services.AddDbContext<AppDbContext>(); // scoped
```

**なぜダメ？**
ScopedをSingletonに閉じ込める（captive dependency）から。
ASP.NET CoreのDIでは、この手のミスを避けるための注意が明確に書かれてるよ ([Microsoft Learn][4])

### 直し方（よくある）✅

* そのSingletonを **Scopedに落とす**（一番簡単）
* どうしてもSingletonのままなら、**IServiceScopeFactory で都度スコープを切る**（上級寄り）

---

## 12. BackgroundService（常駐処理）とScopedの付き合い方🕰️🤖

`BackgroundService` は長生き（=Singleton的）になりやすいので、`DbContext` を直で持つと危ない😇
このときは「仕事1回ごとにスコープを作る」が基本！

（雰囲気だけ）

```csharp
public sealed class Worker : BackgroundService
{
    private readonly IServiceScopeFactory _scopeFactory;

    public Worker(IServiceScopeFactory scopeFactory) => _scopeFactory = scopeFactory;

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        while (!stoppingToken.IsCancellationRequested)
        {
            using var scope = _scopeFactory.CreateScope();
            var useCase = scope.ServiceProvider.GetRequiredService<CreateTodoUseCase>();

            await useCase.ExecuteAsync(stoppingToken);

            await Task.Delay(TimeSpan.FromSeconds(10), stoppingToken);
        }
    }
}
```

---

## 13. HTTP通信とライフサイクル：HttpClientはどうする？🌐📮

昔よくあった事故：

* `new HttpClient()` をいっぱい作る → ソケット枯渇😇

.NETでは `IHttpClientFactory` を使う設計が用意されていて、
ハンドラーの寿命管理なども面倒見てくれるよ ([Microsoft Learn][7])

ただし注意点もある：

* **Cookieが必要なアプリでは注意/非推奨になるケース**がある（ハンドラー共有でCookieContainerが共有される等） ([Microsoft Learn][8])

---

## 14. 章末チェックリスト✅🎀

次の質問に「うん！」って言えたら勝ち😺✨

* [ ] Singletonが **状態（mutable）** を持ってない？🌀
* [ ] Singletonが **Scopedをコンストラクタで受け取ってない？** 💥
* [ ] `DbContext` は **Scoped** になってる？🗄️
* [ ] Repositoryが `DbContext` と同じ寿命（だいたいScoped）？🔗
* [ ] 背景処理やデスクトップでScopedを使うなら、**スコープを自分で切ってる？** ✂️

---

## 15. よくある質問Q&A🙋‍♀️💬

### Q1. 「全部Singletonにしたら速そう」では？

A. 速さより先に **データ混入・並列事故・メモリ肥大** が来がちだよ🥺
まずは「安全な寿命」を優先しよう😊

### Q2. ScopedとTransient、どっちがいいの？

A. “1回の処理で共有したいか”で決めるのが楽！

* 共有したい → Scoped
* 共有いらない（軽い）→ Transient

### Q3. デスクトップでScopedってどう使うの？

A. **「操作1回＝1スコープ」** を自分で決めて切る！
例：ボタン押下 / 1画面表示 / 1ファイル保存 など😊

---

## 16. AIプロンプト例（Copilot/Codex向け）🤖✨

そのまま貼って使えるよ〜！

### 16.1 ライフサイクル診断🩺

* 「この `Program.cs` のDI登録を見て、**SingletonがScopedを参照している可能性**を指摘して。修正案を3つ出して」

### 16.2 初心者向けルール化📏

* 「このプロジェクトのサービスを **Scoped/Transient/Singleton** に分類して。**理由**も一行で添えて」

### 16.3 DbContext事故防止🗄️

* 「`DbContext` の使い方で、**並列アクセスや長寿命化**につながる危険箇所がないかレビューして」

---

## 次章につながる一言🎁✨

第18章では、例外やエラーを「どの層で握って」「どう変換して」「UIへどう返すか」⚠️📮 をやるよ！
DIの寿命が分かると、**“どこで例外を捕まえるべきか”**もスッキリしてくるので相性バツグン😊💖

[1]: https://dotnet.microsoft.com/en-US/download/dotnet/10.0?utm_source=chatgpt.com "Download .NET 10.0 (Linux, macOS, and Windows) | .NET"
[2]: https://learn.microsoft.com/en-us/dotnet/core/extensions/dependency-injection?utm_source=chatgpt.com "Dependency injection - .NET"
[3]: https://learn.microsoft.com/en-us/ef/core/dbcontext-configuration/?utm_source=chatgpt.com "DbContext Lifetime, Configuration, and Initialization"
[4]: https://learn.microsoft.com/en-us/aspnet/core/fundamentals/dependency-injection?view=aspnetcore-10.0&utm_source=chatgpt.com "Dependency injection in ASP.NET Core"
[5]: https://learn.microsoft.com/en-us/dotnet/core/extensions/generic-host?utm_source=chatgpt.com "NET Generic Host"
[6]: https://learn.microsoft.com/en-us/dotnet/core/compatibility/9.0?utm_source=chatgpt.com "Breaking changes in .NET 9"
[7]: https://learn.microsoft.com/ja-jp/dotnet/core/extensions/httpclient-factory-troubleshooting?utm_source=chatgpt.com "IHttpClientFactory の問題のトラブルシューティング - .NET"
[8]: https://learn.microsoft.com/en-us/dotnet/core/extensions/httpclient-factory?utm_source=chatgpt.com "Use the IHttpClientFactory - .NET"

