# 第04章：YAGNIを支える実装スタイル（小さく作って育てる）🧱🌿

この章はひとことで言うと――
**「今ちょうどいい最小サイズで作って、あとから気持ちよく育てられる形にする」** だよ〜😊🌱

---

## 4-0. この章でできるようになること 🎯✨

* 「あとで足せる」最小の作り方がわかる🧰
* ちょいリファクタ前提で進める“安全な手順”が身につく🔧💡
* テストを**ほんの少し**だけ入れて、YAGNIでも安心して進められる🧪🙂
* AI（Copilot / Codex系）に**盛られずに**手伝ってもらえる🤖✂️

ちなみに今どきの基準だと、**.NET 10（LTS）＋ C# 14**が“最新のど真ん中”だよ〜🆕✨（C# 14は最新で .NET 10 対応って明記されてるよ） ([Microsoft Learn][1])
Visual Studio も **Visual Studio 2026** が出てる〜💻✨ ([Microsoft Learn][2])

---

## 4-1. YAGNIを支える「実装の4つのクセ」🍀

### クセ①：まず“動く最小”を作る（完成を先に見に行く）🏃‍♀️💨

![Start Small and Grow](./picture/yagni_cs_study_004_seedling_code.png)


* 最初に「登録できる」「一覧で見れる」だけ作る📌
* UIがキレイとか、保存がDBとか、検索とかは**一旦ぜんぶ置いとく**🧊

✅ 合言葉：**「まず動く。次に整える。」** ✨

---

### クセ②：拡張ポイントは“作らない”。代わりに“切り出しやすく”する✂️

よくある「未来に備えた拡張ポイント」は👇みたいなやつ：

* `IRepository` を先に作る📦
* DIコンテナ前提の構造にする🧩
* なんでも汎用化ジェネリクスにする🧬

これ、今の段階だと **コスト先払い** になりがち😵‍💫

代わりにやるのはコレ👇

* **クラスやメソッドを小さめに**して、あとで分けやすくする🧱
* **責務の境目だけ**うっすら作る（“分けられる形”だけ作る）🌿

---

### クセ③：リファクタは「小さく・すぐ・こまめに」🔧✨

YAGNIは「作らない」けど、**整えるのはサボらない**🙂
おすすめのリズム👇

1. まず通す（動く）✅
2. 目立つ1箇所だけ整える（名前、分割、重複除去）🧹
3. すぐ止める（やりすぎない）🛑✨

---

### クセ④：テストは“最小の防波堤”だけ作る🧪🧱

![Minimal Tests for Safety](./picture/yagni_cs_study_004_test_breakwater.png)


「全部テストしよう！」ってやると、逆にYAGNI違反になりがち😅
この章では **2〜3本だけ**入れるよ👇

* 入力のルール（空文字はダメ、長すぎはダメなど）🧾
* 追加したら件数が増える✅
* 一覧が期待どおり返る✅

xUnit は v3 系が進んでて、.NET 8 以降対応って書かれてるよ〜📦 ([nuget.org][3])

---

## 4-2. ミニ演習：小さなアプリを作る（登録 → 一覧）☕📝✨

題材はゆるくてOK！ここでは
**「カフェメモ」☕：行ったお店を登録して一覧で見る** を作るよ〜😊🌸

---

## 4-3. プロジェクト構成（“最小なのに育つ”）📁🌱

最初から分厚い層は作らないけど、**育てやすさ**は残すために、こうするよ👇

* `CafeMemo.Core`：アプリの中心（ルール＆処理）🧠
* `CafeMemo.App`：コンソールで動かすだけ（UIっぽい所）🖥️
* `CafeMemo.Tests`：最小テスト🧪

![Project Layers](./picture/yagni_cs_study_004_project_layers.png)


> 「Webにしたい」「保存したい」が来たら、あとで増築できる形🏗️✨

---

## 4-4. 実装（コード）👩‍💻✨

![CafeLog Logic](./picture/yagni_cs_study_004_cafelog_logic.png)


### ① `CafeMemo.Core`：ドメイン＆処理（いちばん大事な所）🧠

```csharp
namespace CafeMemo.Core;

public sealed record CafeVisit(
    Guid Id,
    string ShopName,
    string? Note,
    DateTimeOffset VisitedAt
);

public sealed class CafeLog
{
    private readonly List<CafeVisit> _visits = new();

    public CafeVisit Add(string shopName, string? note, DateTimeOffset? visitedAt = null)
    {
        shopName = (shopName ?? "").Trim();

        if (shopName.Length == 0)
            throw new ArgumentException("店名は必須だよ🥺", nameof(shopName));

        if (shopName.Length > 50)
            throw new ArgumentException("店名が長すぎるよ🥺（50文字まで）", nameof(shopName));

        var visit = new CafeVisit(
            Id: Guid.NewGuid(),
            ShopName: shopName,
            Note: string.IsNullOrWhiteSpace(note) ? null : note.Trim(),
            VisitedAt: visitedAt ?? DateTimeOffset.Now
        );

        _visits.Add(visit);
        return visit;
    }

    public IReadOnlyList<CafeVisit> GetAll()
        => _visits
            .OrderByDescending(v => v.VisitedAt)
            .ToList();
}
```

ポイントはここ👇😊✨

* `CafeLog` の中に保存は **とりあえず List**（今必要）🧺
* でも `Add` / `GetAll` に**入口を寄せて**、あとで差し替えやすい形🌿
* `DateTimeOffset` で時刻を扱って、将来の困りごとを減らす🕰️✨（これは“お得な最小”）

---

![Console UI Interaction](./picture/yagni_cs_study_004_console_ui.png)


### ② `CafeMemo.App`：動かして確認（登録→一覧）🖥️☕

```csharp
using CafeMemo.Core;

var log = new CafeLog();

while (true)
{
    Console.WriteLine();
    Console.WriteLine("=== カフェメモ ☕ ===");
    Console.WriteLine("1) 登録する");
    Console.WriteLine("2) 一覧を見る");
    Console.WriteLine("0) 終了");
    Console.Write("選んでね👉 ");

    var input = Console.ReadLine()?.Trim();

    if (input == "0") break;

    if (input == "1")
    {
        Console.Write("店名：");
        var shop = Console.ReadLine();

        Console.Write("メモ（任意）：");
        var note = Console.ReadLine();

        try
        {
            var added = log.Add(shop ?? "", note);
            Console.WriteLine($"登録したよ〜✨ ID={added.Id}");
        }
        catch (ArgumentException ex)
        {
            Console.WriteLine($"エラーだよ💦 {ex.Message}");
        }
    }
    else if (input == "2")
    {
        var all = log.GetAll();

        if (all.Count == 0)
        {
            Console.WriteLine("まだ0件だよ〜🙂");
            continue;
        }

        Console.WriteLine("---- 一覧 ----");
        foreach (var v in all)
        {
            Console.WriteLine($"{v.VisitedAt:yyyy-MM-dd HH:mm}  {v.ShopName}  ({v.Note ?? "メモなし"})");
        }
    }
    else
    {
        Console.WriteLine("0〜2で選んでね🙂");
    }
}
```

🎉これで「登録→一覧」が完成！
ここまでが **MVP** だよ〜✅✨

---

## 4-5. テスト（“最小の防波堤”2〜3本）🧪🧱✨

### `CafeMemo.Tests`：xUnitで守る

```csharp
using CafeMemo.Core;
using Xunit;

public sealed class CafeLogTests
{
    [Fact]
    public void Add_店名が空なら例外()
    {
        var log = new CafeLog();
        Assert.Throws<ArgumentException>(() => log.Add("   ", "note"));
    }

    [Fact]
    public void Add_追加したら一覧が1件になる()
    {
        var log = new CafeLog();
        log.Add("コーヒー天国", "おいしかった");

        var all = log.GetAll();
        Assert.Single(all);
        Assert.Equal("コーヒー天国", all[0].ShopName);
    }
}
```

このくらいで十分だよ〜😊✨
「未来の拡張」じゃなくて、**今日の安心**のためのテスト🧡

---

## 4-6. “小リファクタ”の例：やるならコレだけ🔧✨

![Tiny Refactoring](./picture/yagni_cs_study_004_tiny_refactor.png)


### ✅ いまやってOK（効果がすぐ出る）🙆‍♀️

* 変数名をわかりやすくする（`v` → `visit`）📝
* 長いメソッドを2つに分ける（入力処理と表示処理）✂️
* `Trim()` と空チェックをまとめる🧹

### ❌ いまはやらない（盛りやすい）🙅‍♀️🎈

* `IRepository` 作る
* DIコンテナ導入
* “将来の検索”のための抽象化
* “汎用ログ基盤”を先に整備

> こういうのは「痛み」が出た瞬間が買い時だよ🛒✨（第5章以降で判断が上手くなる！）

---

## 4-7. AI活用：盛らせないプロンプト集🤖✂️💡

![AI Constraint](./picture/yagni_cs_study_004_ai_constraint.png)


Copilot/Codexに投げるときは、最初にこれを付けるだけで事故りにくいよ〜🙂✨

### 🧾 ① 雛形づくり（盛り禁止）

```text
C#で「登録→一覧」だけの最小実装にして。
将来拡張のためのRepository/DI/抽象化は入れないで。
データはListでOK。クラスは少なめ、読みやすさ重視。
```

### 🧪 ② テスト（最小の2本だけ）

```text
テストは2本だけ提案して。
(1) 店名が空なら例外 (2) 追加したら件数が増える
それ以外は不要。
```

### 🕵️‍♀️ ③ 過剰設計チェック

```text
このコード、YAGNI的に“今いらない仕組み”が混ざってない？
混ざってたら、削る案を短く3つ出して。
```

Visual Studio 2026 は AI の統合も強めていく流れが書かれてるので、こういう使い方がめちゃ相性いいよ〜🤖✨ ([Microsoft Learn][2])

---

## 4-8. 仕上げチェック（この章のゴール）✅🎉

次の条件を満たしたら合格〜💮✨

* [ ] 登録できる☕
* [ ] 一覧が見れる📋
* [ ] 店名が空だとちゃんと止まる🧯
* [ ] テストが2本通る🧪✅
* [ ] 「将来のための仕組み」を増やしてない✂️🙂

---

## 4-9. まとめ（今日のいちばん大事）🧡

YAGNIで詰まないコツはこれ👇😊✨

* **小さく完成させる**（完成が先）🏁
* **リファクタ前提**で、ちょいちょい整える🔧
* **テストは最小**（安心のためにちょっとだけ）🧪
* **AIは盛らせず**、最小で出させる🤖✂️

次の章では、C#で特にやりがちな「未来用設計」をどう安全に先送りするかを、もっと具体例つきでいくよ〜🧯🧠✨

[1]: https://learn.microsoft.com/en-us/dotnet/core/releases-and-support?utm_source=chatgpt.com ".NET releases, patches, and support - .NET"
[2]: https://learn.microsoft.com/en-us/visualstudio/releases/2026/release-notes?utm_source=chatgpt.com "Visual Studio 2026 Release Notes"
[3]: https://www.nuget.org/packages/xunit.v3?utm_source=chatgpt.com "xunit.v3 3.2.1"
