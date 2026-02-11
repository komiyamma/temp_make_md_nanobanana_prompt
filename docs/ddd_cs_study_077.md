# 第77章：Active Record 〜DBを“そのまま触る”昔ながらの楽な方法📚✨

Active Record（アクティブレコード）は、ざっくり言うと……

**「1つのクラスが、データ（状態）も、DBへの保存/検索（永続化）も、ぜんぶ持っちゃう」**
という設計です🧸🗃️

たとえば `Memo` というクラスがあったら、

* `Memo.Title` や `Memo.Body` みたいな **データ** を持っていて
* `memo.Save()` / `Memo.Find(id)` みたいな **DB操作** も自分でやる

…って感じです🙌✨
DDDの文脈だと「ドメインとDBが密着しすぎる」ので嫌われがちだけど、**1人開発で爆速したい場面**では普通にアリです🚀💨

![Active Record Concept](./picture/ddd_cs_study_077_active_record.png)

---

## 1. Active Recordが“気持ちいい”理由😆💗

### ✅ 良いところ（強い！）
 
 ```mermaid
 classDiagram
     class Memo {
         +int Id
         +string Title
         +string Body
         +DateTime UpdatedAt
         
         +SaveAsync()
         +DeleteAsync()
         +FindAsync(id)$
     }
     
     note for Memo "データもDB操作も\n全部持ってる！💪"
 ```
 
 * **作るのが速い**（最短でCRUDができる）⚡
 * クラス1個見れば「何ができるか」だいたい分かる👀
 * 小規模アプリ、管理画面、ツール系でめちゃ便利🛠️

### ⚠️ つらいところ（育つと痛い）

* **ビジネスルールとDB都合が混ざりやすい**🍝（スパゲッティ化）
* テストがだんだん書きづらくなる😵‍💫
* 後からDDDっぽく分けたくなると、移植がちょい大変🏗️

「最初は勝ちやすいけど、長期戦は疲れやすい」タイプです🥺💦

---

## 2. どういう時にActive Recordを選ぶ？🎯

次のどれかに当てはまったら、Active Record はかなり有力です✨

* 仕様が軽い（ルールが少ない）📄
* まずは動くものを早く出したい（検証したい）🧪
* 管理画面・社内ツール・一時的なアプリ🧰
* 「あとで作り直してもいい」前提で進めたい🔁

逆に、次みたいな場合はDDD寄りの方がラクになりがち👇

* 価格計算、割引、在庫、権限、予約など **ルールが複雑**🧠
* 仕様変更が多く、育つのが確定🌱
* ドメインをちゃんと守りたい（DBに引っ張られたくない）🛡️

---

## 3. 最小のActive RecordをC#で作ってみよう🧁（EF Core + SQLite）

題材は「メモ帳」✍️✨
**Memoクラスが自分でDB保存/検索しちゃう**例です。

### 3-1. まずやること（サクッと）🧪

* コンソールアプリを作る
* EF Core（SQLite）を入れる
* `Memo` に `SaveAsync / DeleteAsync / FindAsync` を持たせる

---

## 4. サンプル実装（1ファイルで動く系）💻✨

> 「作りやすさ優先」で、**わざと密結合**にしています😈
> ここが Active Record の“味”です🍭

```csharp
using Microsoft.EntityFrameworkCore;

await Demo.RunAsync();

public static class Demo
{
    public static async Task RunAsync()
    {
        // 1) 新規作成して保存
        var memo = new Memo("はじめてのActive Record", "DB保存までクラス1個でやっちゃう✨");
        await memo.SaveAsync();

        // 2) 取得
        var loaded = await Memo.FindAsync(memo.Id);
        Console.WriteLine($"Load: {loaded?.Title} / {loaded?.Body}");

        // 3) 更新して保存
        loaded!.Body = "更新したよ〜📝✨";
        await loaded.SaveAsync();

        // 4) 削除
        await loaded.DeleteAsync();
        Console.WriteLine("Deleted 🗑️");
    }
}

public class AppDbContext : DbContext
{
    public DbSet<Memo> Memos => Set<Memo>();

    protected override void OnConfiguring(DbContextOptionsBuilder options)
        => options.UseSqlite("Data Source=app.db");
}

public class Memo
{
    public int Id { get; private set; }
    public string Title { get; private set; }
    public string Body { get; set; }
    public DateTime UpdatedAt { get; private set; }

    // EF Core用（空コンストラクタ）
    private Memo() { Title = ""; Body = ""; }

    public Memo(string title, string body)
    {
        Title = title;
        Body = body;
        UpdatedAt = DateTime.UtcNow;
    }

    public async Task SaveAsync()
    {
        UpdatedAt = DateTime.UtcNow;

        await using var db = new AppDbContext();
        await db.Database.EnsureCreatedAsync();

        if (Id == 0)
        {
            db.Memos.Add(this);
        }
        else
        {
            db.Memos.Update(this);
        }

        await db.SaveChangesAsync();
    }

    public async Task DeleteAsync()
    {
        if (Id == 0) return;

        await using var db = new AppDbContext();
        db.Memos.Remove(this);
        await db.SaveChangesAsync();
    }

    public static async Task<Memo?> FindAsync(int id)
    {
        await using var db = new AppDbContext();
        return await db.Memos.FirstOrDefaultAsync(x => x.Id == id);
    }
}
```

### どこがActive Recordっぽい？👀✨

* `Memo.SaveAsync()` が **自分でDBを開いて保存**してる📦
* `Memo.FindAsync(id)` が **自分で検索して返す**🔎
* “データの入れ物”じゃなくて、**DB操作できる生き物**になってる🧬

---

## 5. この方式の「地雷ポイント」も知っておこう🧨😇

### 地雷①：DBの事情がクラスに染み込む🍛

`AppDbContext` や `EnsureCreated` がクラス内に出てきて、
だんだん「ドメイン」じゃなく「DB操作クラス」っぽくなります😵‍💫

### 地雷②：テストが重くなりやすい🧪💦

`SaveAsync()` がDB必須になると、ユニットテストがつらい…
（結局、結合テストっぽくなる）😢

### 地雷③：成長すると分割したくなる🌱

「保存は別の層に逃がしたい…」って気持ちが来ます。
その時に Repository 方式へ引っ越し🏠✨（第46章〜の世界）

---

## 6. Active Record を使うときの“割り切りルール”📏✨

おすすめの割り切りはこれ👇（超効く）

* ✅ **“CRUDしかない”領域に限定**する（複雑な計算を入れない）🍡
* ✅ ルールが増えたら **引っ越し前提**でOK（いま勝つ！）🏃‍♀️💨
* ✅ 複雑になりそうなら、`Save` ではなく **Serviceへ寄せる**🤝

---

## 7. AI（Copilot/Codex）で爆速するコツ🤖⚡

### ✅ AIに投げていいこと

* CRUDの雛形生成（`Find`, `Save`, `Delete`）🧱
* EF Coreの設定・マイグレーション系の手順🔧
* 例外処理やログの追加📜

### ⚠️ AIに丸投げしないこと

* 「どこまでをActive Recordで許すか」の境界線🧭
* その機能は“育つ”のか？捨てるのか？という判断🌱🗑️

### そのまま使えるプロンプト例💬✨

* 「この `Memo` を Active Record 風にして、`SaveAsync/FindAsync/DeleteAsync` を追加して」🤖
* 「この設計が肥大化しそうなポイントを3つ指摘して、改善案も出して」🧠
* 「将来Repositoryに移す場合の移行手順をざっくり作って」📦➡️📦

---

## 8. ミニ演習（やってみよう！）🎓💖

### 演習A：項目を増やす🧁

`Memo` に以下を追加して、保存・取得できるようにしてね✨

* `IsPinned`（ピン留め）📌
* `Tags`（カンマ区切り文字列でもOK）🏷️

### 演習B：“太り始めたサイン”を探す🔍

次の処理を足したくなったら、Active Recordを卒業する合図かも👇

* 「タグの正規化」
* 「検索条件が増殖（AND/OR地獄）」
* 「更新時の複雑なルール（禁止ワード、権限、履歴…）」😵‍💫

---

## まとめ🌸✨

Active Record は、

* **最速で作れる**🚀
* でも **育つと苦しくなる**🌱💦

だからこそ、1人開発ではめちゃ強い選択肢です💪✨
「まず勝つ」ための武器として、気持ちよく使ってOKです😆🎉

---

次の第78章（使い分けの基準）では、
「Active Record / トランザクションスクリプト / DDD」の切り替え判断を、もっとスパッとできるようにしていくよ✂️✨
