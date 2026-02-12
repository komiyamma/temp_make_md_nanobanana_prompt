# 第20章：例外と戻り値の境界（エラー設計の入口）🚨🧩

この章は「**エラーをどこで扱うとテストがラクになる？**」を学ぶ回だよ〜😊
結論から言うと、

* **内側（ルール）**：なるべく「戻り値（Resultっぽい）」で伝える🧾✨
* **外側（I/O）**：例外が起きやすいので、**境界で受け止めて“意味のある失敗”に変換**する🛡️
* **バグ**：基本「直してね」のやつなので、無理に握らない（握るならログして落とす）💥

…って整理すると、テストが一気に安定するよ🎉

---

## 1) まずは“エラーの種類”を3つに分けよう🧠✨


![testable_cs_study_020_error_triad.png](./picture/testable_cs_study_020_error_triad.png)

エラーって全部同じに見えるけど、**性格が違う**んだよね😳

### A. ルール違反（期待される失敗）📦✅

例：

* パスワード短すぎる
* 期限切れ
* すでに登録済み

👉 これは「よく起こる」ので、**例外にするとテストも実行もややこしい**。
**Result（成功/失敗）で返す**のが相性良い🙆‍♀️✨

### B. I/O失敗（外の世界が壊れた）🌍💥

例：

* DB落ちた
* ファイル読めない
* 外部APIタイムアウト

👉 これは **外側の都合**。.NETは例外が飛びやすい世界だよね。
ただし「そのまま例外ドーン」だと、アプリ内側が汚れるので、**境界で変換**がコツ🧩

※例外の扱い方のベストプラクティスはMS公式にもまとまってるよ。([Microsoft Learn][1])

### C. バグ（想定外）🐛🔥

例：

* null参照
* index範囲外
* 絶対起きないはずの分岐に来た

👉 これは「握っても直らない」タイプ。
**ログ出して落とす**か、上位で共通ハンドリング（例：画面にはごめんね表示）に寄せるのが多いよ〜。

---

## 2) 「どこまで投げる？どこで握る？」の基本ルール📍✨

ここが今日のメイン！🎯

### ルール①：内側（ルール層）は、I/O例外を知らない🙅‍♀️

内側は**純粋ロジック寄り**に保ちたいから、

* `IOException` とか
* `HttpRequestException` とか
  そういう「外側の事情」を持ち込まない🌱

### ルール②：外側（I/O境界）で、例外→意味のある失敗に翻訳する🈂️✨

![testable_cs_study_020_exception_translator.png](./picture/testable_cs_study_020_exception_translator.png)

たとえば「DB接続失敗」が起きたら、内側にはこう言わせたい：

* 「今は登録できない（再試行してね）」
* 「一時的にサービス利用不可」

っていう **アプリにとっての意味**に変換して返す🧩

### ルール③：よく起きる失敗を例外で流さない⚠️

MS公式でも「よくある条件は例外を避ける」方向が推奨だよ。([Microsoft Learn][1])
（例外を投げるのはコストが高い＆読みづらくなることがある💦）

---

## 3) Result型っぽい考え方（チラ見せ👀✨）

C#/.NETに標準の `Result<T>` は（基本）用意されてないので、**最小自作**が理解しやすいよ😊
（「TryParse」系が“戻り値で失敗を表す文化”の代表だよね🧠）

ここでは **超ミニResult** を作ってみよ〜🎀

```csharp
public readonly record struct Result<T>(bool IsSuccess, T? Value, Error? Error)
{
    public static Result<T> Ok(T value) => new(true, value, null);
    public static Result<T> Fail(Error error) => new(false, default, error);
}

public abstract record Error(string Code, string Message);

public sealed record DomainError(string Code, string Message) : Error(Code, Message);
public sealed record InfrastructureError(string Code, string Message) : Error(Code, Message);
```

ポイント💡

* **DomainError**：ルール違反（入力ミス・条件未達）
* **InfrastructureError**：I/O失敗（DB/ネット/ファイル）

この2種類を分けるだけで「どこで処理する？」が急に見える👓✨

---

## 4) 具体例：ユーザー登録（ルール違反 vs DB障害）🧑‍💻🗄️

### 4-1) 内側：ルールは Result で返す📦🧾

```csharp
public static class PasswordRules
{
    public static Result<string> Validate(string password)
    {
        if (string.IsNullOrWhiteSpace(password))
            return Result<string>.Fail(new DomainError("PW_EMPTY", "パスワードが空だよ😵"));

        if (password.Length < 8)
            return Result<string>.Fail(new DomainError("PW_SHORT", "8文字以上にしてね🙏"));

        return Result<string>.Ok(password);
    }
}
```

✅ これ、**爆速で単体テストできる**やつ！⚡

---

### 4-2) 境界：I/Oは例外が飛ぶので、ここで翻訳する🌍➡️🧩

リポジトリは「インターフェース」で包んでたよね（第17章のノリ）🗄️✨

```csharp
public interface IUserRepository
{
    // 既に存在したらtrue
    Task<bool> ExistsByEmailAsync(string email, CancellationToken ct);

    // 保存してUserIdを返す
    Task<Guid> SaveAsync(string email, string password, CancellationToken ct);
}
```

ユースケース（アプリ内側寄り）は「I/O失敗をドメインに混ぜない」方針で書くよ😊

```csharp
public sealed class RegisterUserUseCase
{
    private readonly IUserRepository _repo;

    public RegisterUserUseCase(IUserRepository repo) => _repo = repo;

    public async Task<Result<Guid>> ExecuteAsync(string email, string password, CancellationToken ct)
    {
        // ルール違反（期待される失敗）
        var pw = PasswordRules.Validate(password);
        if (!pw.IsSuccess) return Result<Guid>.Fail(pw.Error!);

        try
        {
            // I/O（外の世界）
            if (await _repo.ExistsByEmailAsync(email, ct))
                return Result<Guid>.Fail(new DomainError("EMAIL_EXISTS", "そのメールは既に登録済みだよ📮💦"));

            var id = await _repo.SaveAsync(email, password, ct);
            return Result<Guid>.Ok(id);
        }
        catch (OperationCanceledException)
        {
            // キャンセルは“エラー”というより「やめた」なので、そのまま投げ直す派も多いよ👌
            throw;
        }
        catch (Exception ex) when (IsInfrastructureException(ex))
        {
            // ここが“境界の翻訳”✨
            return Result<Guid>.Fail(new InfrastructureError(
                "INFRA_TEMP",
                "今は登録できないみたい…少し待ってもう一回やってみてね🙏"
            ));
        }
    }

    private static bool IsInfrastructureException(Exception ex)
        => ex is TimeoutException
           or System.IO.IOException;
           // DBやHTTPの例外型は利用技術で増えるので、最初は大雑把でOK😊
}
```

ここで使ってる **例外フィルター（when）** は、条件で catch を分岐できる便利機能だよ。([Microsoft Learn][2])
（必要な例外だけ拾って、それ以外は上に任せられるのがキレイ✨）

---

## 5) テストの書き方：揺れない！速い！🧪⚡

### 5-1) ルール違反は超かんたん（純粋ロジック）🌿

```csharp
using Xunit;

public class PasswordRulesTests
{
    [Fact]
    public void ShortPassword_ReturnsDomainError()
    {
        var r = PasswordRules.Validate("123");

        Assert.False(r.IsSuccess);
        Assert.Equal("PW_SHORT", r.Error!.Code);
    }
}
```

### 5-2) I/O失敗は「例外を投げるFake」で再現する🎭💥

```csharp
using Xunit;
using System.Threading;
using System.Threading.Tasks;

public class RegisterUserUseCaseTests
{
    private sealed class ThrowingRepo : IUserRepository
    {
        public Task<bool> ExistsByEmailAsync(string email, CancellationToken ct)
            => throw new System.IO.IOException("disk/network broken");

        public Task<Guid> SaveAsync(string email, string password, CancellationToken ct)
            => Task.FromResult(Guid.NewGuid());
    }

    [Fact]
    public async Task InfraFailure_ReturnsInfrastructureError()
    {
        var useCase = new RegisterUserUseCase(new ThrowingRepo());

        var r = await useCase.ExecuteAsync("a@b.com", "password123", CancellationToken.None);

        Assert.False(r.IsSuccess);
        Assert.Equal("INFRA_TEMP", r.Error!.Code);
    }
}
```

✅ これで「DBが落ちた時の挙動」も、**実DB無しで再現できる**🎉

---

## 6) よくある落とし穴ベスト3⚠️😵‍💫

### 落とし穴①：例外で分岐してしまう（例外＝if代わり）🙅‍♀️

「ログイン失敗＝例外」とかやると、テストもしんどいし読みづらい💦
MS公式も「よくある条件は例外を避ける」方向でまとめてるよ。([Microsoft Learn][1])

### 落とし穴②：`throw ex;` で投げ直す😱

スタックトレースが壊れて泣くやつ…
投げ直すなら基本 `throw;` が安全（“捕まえた例外そのまま再スロー”）
※この系の注意も例外ベストプラクティスで触れられてるよ。([Microsoft Learn][1])

### 落とし穴③：何でも `catch (Exception)` で握って成功扱いにする🤝💣

それ“静かに壊れる”ので超危険…
握るなら「**失敗として返す**」か「ログして落とす」かを決めよ〜。

---

## 7) ミニ演習（手を動かすと一気に腹落ちするよ🧁✨）

### 演習A：DomainErrorを増やす🍓

* メールが空なら `EMAIL_EMPTY`
* `@`が無ければ `EMAIL_INVALID`
  みたいにして、戻り値で返してみよう😊

### 演習B：InfrastructureErrorのメッセージを状況別に🧊

* Timeoutなら「混み合ってるかも」
* IOExceptionなら「保存に失敗しちゃった」
  みたいに、翻訳を作ってみよう🧩✨

### 演習C：UI側での表示（握る場所を外へ）🖥️

* UseCaseは Result を返すだけ
* UIは Result を見て表示を変えるだけ
  にして「UIが薄くなる」感覚をつかもう🎯

---

## 8) AI（Copilot/Codex）活用プロンプト例🤖💡

コピペで使ってOKだよ〜🧠✨

* 「このメソッドの失敗を **DomainError と InfrastructureError に分類**して Result で返したい。候補のErrorコード案を出して」
* 「この try/catch を **境界での翻訳**になるように整理して。例外フィルター（when）も使っていい」
* 「xUnitで、I/O失敗（例外発生）を **Fakeで再現するテスト**を書いて」
* 「この処理、**例外で分岐**してない？してたら戻り値設計に寄せる案を出して」

---

## 9) 今日のまとめ🎀✨

* **ルール違反（期待される失敗）**：Resultで返すのが気持ちいい🧾
* **I/O失敗（外の世界）**：境界で例外を受けて、意味のある失敗に翻訳🧩
* **バグ**：握らず直す（握るならログ＋共通ハンドリング）🐛🔥
* 例外の扱いはMS公式のベストプラクティスも参考になるよ。([Microsoft Learn][1])

次の第21章は「**分解の練習**」だよ〜✂️🧱
“判断（if）”と“I/O”をもっときれいに分けられるようになるから、ここで学んだエラー整理がめっちゃ効いてくるよ💖

[1]: https://learn.microsoft.com/en-us/dotnet/standard/exceptions/best-practices-for-exceptions?utm_source=chatgpt.com "Best practices for exceptions - .NET"
[2]: https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/keywords/when?utm_source=chatgpt.com "when contextual keyword - C# reference"
