# 第16章：ファイルI/Oを境界にする 🗂️🚧✨（= 単体テストで「ファイル触らない」を実現！）

この章では、`File.ReadAllText()` みたいな“直呼び”を卒業して、**ファイル操作を「外の世界」として隔離**しちゃいます💪🌍
すると… **単体テストが爆速＆安定**になります🎉⚡

---

## 1. まず結論：ファイルは「外の世界」🗂️🌍

ファイルI/Oは、テストにとって敵になりがち😵‍💫💥

* ✅ PCの環境で結果が変わる（権限・パス・改行・文字コード…）🌀
* ✅ テストが遅くなる（SSDでも積み上がると重い）🐢
* ✅ 並列テストで競合しやすい（同じファイル触って事故）💣
* ✅ “準備と後片付け”が面倒（作る→消す→失敗したら残骸）🧹

だから合言葉👇
**「ファイルは境界の外！中に入れない！」** 🚪🧊

---

## 2. ダメな例：「重要ロジックの中で File を直呼び」💥

```csharp
public class UserProfileService
{
    public string GetDisplayName(string userId)
    {
        // 🔥ロジックの真ん中でファイル直読み（テストつらい）
        var json = File.ReadAllText($@"C:\app\data\users\{userId}.json");
        var user = System.Text.Json.JsonSerializer.Deserialize<User>(json)!;

        return user.IsPremium ? $"🌟 {user.Name}" : user.Name;
    }
}
```

これ、単体テストで **ファイルを用意しないと動かない** 😭
しかもパス固定で、環境が変わると崩壊します💥

---

## 3. 目標の形：「ファイルアクセスはインターフェースの向こう側」🧩🚪✨

やり方はシンプル👇

1. **必要なファイル操作だけ** を小さなIFにする🧩
2. 本番は `System.IO` で実装する🛠️
3. テストは **メモリ上のFake** に差し替える🧸🎭

---

## 4. 最小の境界：IFileStore を作ろう 📦🧩

### 4.1 インターフェース（境界）🚪

```csharp
public interface IFileStore
{
    bool Exists(string path);
    string ReadAllText(string path);
    void WriteAllText(string path, string content);
}
```

> ポイント💡：**最初から巨大なIFにしない**
> いま必要な操作だけでOK🙆‍♀️✨

---

### 4.2 本番実装（実ファイル）🗂️

```csharp
public class PhysicalFileStore : IFileStore
{
    public bool Exists(string path) => File.Exists(path);

    public string ReadAllText(string path) => File.ReadAllText(path);

    public void WriteAllText(string path, string content)
        => File.WriteAllText(path, content);
}
```

---

### 4.3 使う側（重要ロジック）📦✨

ここが主役！
**重要ロジックは IFileStore だけ見て生きる** 🙌

```csharp
using System.Text.Json;

public class UserProfileService
{
    private readonly IFileStore _files;

    public UserProfileService(IFileStore files)
    {
        _files = files;
    }

    public string GetDisplayName(string userId)
    {
        var path = $@"C:\app\data\users\{userId}.json";

        if (!_files.Exists(path))
            return "（未登録）";

        var json = _files.ReadAllText(path);
        var user = JsonSerializer.Deserialize<User>(json)!;

        return user.IsPremium ? $"🌟 {user.Name}" : user.Name;
    }
}

public record User(string Name, bool IsPremium);
```

✅ これで `UserProfileService` は **ファイルに依存してない** ので、テストが楽になります🎉

---

## 5. テスト用：メモリ上のFakeを作る 🧸📦🎭


![testable_cs_study_016_virtual_fs.png](./picture/testable_cs_study_016_virtual_fs.png)

```csharp
public class InMemoryFileStore : IFileStore
{
    private readonly Dictionary<string, string> _map = new();

    public bool Exists(string path) => _map.ContainsKey(path);

    public string ReadAllText(string path) => _map[path];

    public void WriteAllText(string path, string content) => _map[path] = content;

    // テスト準備がラクになるおまけ🎁
    public void Seed(string path, string content) => _map[path] = content;
}
```

---

## 6. xUnitで単体テストしてみよう 🧪✨（ファイル0秒！）

```csharp
using Xunit;

public class UserProfileServiceTests
{
    [Fact]
    public void プレミアムなら星を付ける()
    {
        var files = new InMemoryFileStore();
        var path = @"C:\app\data\users\001.json";
        files.Seed(path, """{"Name":"Mika","IsPremium":true}""");

        var sut = new UserProfileService(files);

        var result = sut.GetDisplayName("001");

        Assert.Equal("🌟 Mika", result);
    }

    [Fact]
    public void ファイルが無ければ未登録()
    {
        var files = new InMemoryFileStore();
        var sut = new UserProfileService(files);

        var result = sut.GetDisplayName("999");

        Assert.Equal("（未登録）", result);
    }
}
```

🎉 **実ファイルいらない！**
🎉 **速い！安定！並列でも安心！** ⚡🧘‍♀️

---

## 7. もう一段うまくするコツ（初心者がハマりやすい所）🧠⚠️

### 7.1 パスをロジックに埋め込まない 🧨

上の例は説明のため固定パスにしたけど、実戦では👇がオススメ！

* 「どこに保存するか」は外側で決める（設定・引数・別IF）📌
* 内側は「渡されたパス」を使うだけ🧊

たとえば `IAppPaths` を作ってもOK🙆‍♀️

---

### 7.2 例外はどこで握る？🤔💥

`ReadAllText` は失敗しうる（権限・ロック・壊れたファイル等）😵
コツは👇

* **内側（ルール）は例外を増やさない** 🧼
* **外側（I/O境界）で失敗を扱う** 🚧

（第20章の「例外と戻り値」に繋がります🔗✨）

---

## 8. 便利ライブラリ案：System.IO.Abstractions を使う手もある 🧰✨

「自前でIFileStore作るのもいいけど、もっと網羅したい！」って時は
**System.IO.Abstractions** が定番です💡

* `System.IO` を抽象化した `IFileSystem` が使える🧩
* テストでは `MockFileSystem` 的な仕組みで差し替えやすい🎭
* NuGet上でも活発に更新されていて、最近は v22.1.0 が出ています（2025-11-22）📦✨ ([NuGet][1])

「どっちがいい？」の目安👇

* 🌱学習＆小規模：**自前IFileStore**（必要な分だけ）
* 🏢中〜大規模：**System.IO.Abstractions**（守備範囲広い）

---

## 9. AI（Copilot/Codex）活用のしかた 🤖💡✨

そのままコピペで使える指示例👇

* 「`File.ReadAllText` を直呼びしている箇所を探して、`IFileStore` に置き換えるリファクタ案を出して」🔍🧩
* 「`InMemoryFileStore` のFake実装を、必要メソッドだけで書いて」🧸
* 「xUnitで AAA（Arrange/Act/Assert）になるようにテストケースを3つ提案して」🧪📝

⚠️ 注意：AIはIFを巨大化させがち！
→ **“今必要な操作だけ”** に絞ってね✂️✨

---

## 10. 演習（ミニ課題）🎒✨：ファイル保存できるToDo

### お題🧩

ToDoをJSONで保存・読み込みする `TodoRepository` を作ろう！

* `Save(List<Todo> todos)`
* `Load()`

✅ ただし Repository は **IFileStore 越し** にすること！🚪
✅ 単体テストは **InMemoryFileStore** でやること！🧸🧪

### クリア条件🎯

* テストがファイル無しで全部通る⚡
* 本番だけ `PhysicalFileStore` に差し替えて動く🚀

---

## まとめ：第16章で覚える一言 ✨

**「ファイルはI/O。境界の外へ！テストはメモリで！」** 🗂️🚪🧪🎉

おまけの最新メモ：いまのC#の最新は **C# 14** で、**.NET 10** 上で使えるよ📌 ([Microsoft Learn][2])

---

次の章（第17章）は **DBを境界にする（Repository入門）** 🗄️🚧✨
今回のファイル版とほぼ同じ発想で、もっと強くなれます💪💖

[1]: https://www.nuget.org/packages/System.IO.Abstractions/?utm_source=chatgpt.com "System.IO.Abstractions 22.1.0"
[2]: https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-14?utm_source=chatgpt.com "What's new in C# 14"
