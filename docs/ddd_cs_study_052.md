# 第52章：Resultパターンの導入 🎁

![Resultパターンの導入](./picture/ddd_cs_study_052_result_obj.png)

**例外を投げずに、エラーを「戻り値」として扱う**やり方だよ〜😊✨

---

## 1. 例外（throw）って、実は「爆弾」になりやすい💣😵

例外は便利なんだけど、こんな使い方をするとつらい…👇

* メールアドレスが不正 → `throw`
* パスワード短い → `throw`
* 在庫が足りない → `throw`

これ、ぜんぶ「よく起こる」「想定内の失敗」だよね？🤔
想定内の失敗で `throw` を多用すると…

* どこで落ちるか追いにくい 🌀
* 画面に出すエラーの組み立てが散らかる 🧩
* AIにコード作らせたとき、例外まみれになりがち 🤖💥

そこで登場するのが **Resultパターン** だよ🎉

---

## 2. Resultパターンってなに？✅❌

関数の返り値をこうする感じ👇

* 成功：`Success(値)` ✅
* 失敗：`Failure(エラー情報)` ❌

つまり、「失敗するかも」を**型として表現**するのがポイント✨
呼び出し側は **必ず** 成功/失敗を処理する流れになるよ😊
 
 ```mermaid
 flowchart LR
    Call["関数呼び出し 📞"] --> Check{"成功した？"}
    
    Check -- Yes --> Success["Success ✅<br/>(値が入ってる)"]
    Check -- No --> Failure["Failure ❌<br/>(エラー情報)"]
    
    Success --> Next["次の処理へ ➡️"]
    Failure --> ErrorHandle["エラーハンドリング 🛡️"]
 ```
 
 ---

## 3. いつResult？いつ例外？ざっくりルール🌈

迷ったら、まずこれでOK👇

### Resultが向いてる（想定内）🙂

* 入力チェック（メール形式が違う等）✉️
* ビジネスルール違反（残高不足・予約不可など）💰📅
* 重複・整合性エラー（同じユーザー名がいる等）👥

### 例外が向いてる（想定外）😱

* DB接続が落ちた、ネットワーク死んだ 🌩️
* ファイルが読めない、権限がない 🔒
* ライブラリのバグっぽい挙動 🧨

DDD的には、**ドメインの失敗＝Result**にすると気持ちいいよ👍✨

---

## 4. 最小のResult型を作ろう（コピペでOK）🧩✨

まずは「小さく」作るのが正義😊
（あとで育てられる🌱）

```csharp
namespace MyApp.Shared;

// 失敗の情報。Codeは機械向け、Messageは人向け
public readonly record struct Error(string Code, string Message);

public readonly record struct Result(bool IsSuccess, Error? Error)
{
    public bool IsFailure => !IsSuccess;

    public static Result Success() => new(true, null);
    public static Result Failure(string code, string message) => new(false, new Error(code, message));
}

public readonly record struct Result<T>(bool IsSuccess, T? Value, Error? Error)
{
    public bool IsFailure => !IsSuccess;

    public static Result<T> Success(T value) => new(true, value, null);
    public static Result<T> Failure(string code, string message) => new(false, default, new Error(code, message));

    // ちょい便利：成功なら変換、失敗ならそのまま失敗を流す
    public Result<U> Map<U>(Func<T, U> mapper)
        => IsSuccess ? Result<U>.Success(mapper(Value!)) : Result<U>.Failure(Error!.Value.Code, Error!.Value.Message);

    // ちょい便利：次のResultをつなぐ（失敗なら途中で止まる）
    public Result<U> Bind<U>(Func<T, Result<U>> binder)
        => IsSuccess ? binder(Value!) : Result<U>.Failure(Error!.Value.Code, Error!.Value.Message);
}
```

> `Map` と `Bind` は最初は“おまけ”でもOKだよ😊
> でも後で「if地獄」を減らすのにめっちゃ効く✨

---

## 5. 値オブジェクトでResultを使う（超DDDっぽい）💎📦

例：Email（不正なら“そもそも生まれない”）👶❌

```csharp
using System.Text.RegularExpressions;
using MyApp.Shared;

namespace MyApp.Domain.ValueObjects;

public sealed class Email
{
    private static readonly Regex Pattern =
        new(@"^[^@\s]+@[^@\s]+\.[^@\s]+$", RegexOptions.Compiled);

    public string Value { get; }

    private Email(string value) => Value = value;

    public static Result<Email> Create(string raw)
    {
        raw = (raw ?? "").Trim();

        if (raw.Length == 0)
            return Result<Email>.Failure("email.empty", "メールアドレスが空だよ🥺");

        if (!Pattern.IsMatch(raw))
            return Result<Email>.Failure("email.invalid", "メールアドレスの形式が変だよ✉️💦");

        return Result<Email>.Success(new Email(raw));
    }

    public override string ToString() => Value;
}
```

✅ **ポイント**：不正なEmailは「存在しない」扱いになる
→ ドメインがキレイになる😍✨

---

## 6. ユースケース（Application層）での扱い方🎮🧠

「登録したい！」みたいな処理で、Resultをつないでいくよ😊

```csharp
using MyApp.Domain.ValueObjects;
using MyApp.Shared;

public sealed record RegisterUserCommand(string Email);

public sealed class RegisterUserService
{
    // 本当はRepositoryとか注入する想定だよ👍
    public Result<Guid> Register(RegisterUserCommand cmd)
    {
        // まずEmailを作る（失敗ならここで終了）
        var emailResult = Email.Create(cmd.Email);
        if (emailResult.IsFailure)
            return Result<Guid>.Failure(emailResult.Error!.Value.Code, emailResult.Error!.Value.Message);

        // ここまで来たら成功が保証されてる✨
        var userId = Guid.NewGuid();

        // ここでDB保存…など（DBが死んだら例外でもOK）
        return Result<Guid>.Success(userId);
    }
}
```

慣れてきたら `Bind` でスッキリもできるよ✨（将来のお楽しみ🎁）

---

## 7. Web APIに返すときの考え方（超ざっくり）🌐📮

* Result失敗 → 400（BadRequest）にしてMessageを返す
* 例外 → 500（InternalServerError）にしてログ取る

「想定内の失敗」はResultで **丁寧に返せる**のが強いよ😊✨

---

## 8. AI（Copilot/Codex）に頼むときの“良い指示”🤖📝

こう言うと暴走しにくいよ👇

* 「ドメインの入力不正・業務ルール違反は例外禁止。Resultで返して」
* 「Errorは code と message を持つ」
* 「Result<T> を返す Create メソッドを用意」
* 「ユニットテストも一緒に生成して（成功/失敗ケース）」

プロンプト例：

```text
C#でResultパターンを導入したいです。
- ドメインの入力不正や業務ルール違反では例外を投げない
- Result / Result<T> と Error(code, message) を実装
- ValueObjectのCreateは Result<ValueObject> を返す
- xUnitで成功/失敗のテストも作る
```

---

## 9. よくある落とし穴ベスト3 😵‍💫⚠️

1. **失敗なのに message だけ返す**
   → `code` がないとUI側の分岐がしんどい💦

2. **Resultなのに例外も投げる**
   → “どっちで処理すればいいの？”って混乱する🌀

3. **Errorをstringで雑に持つ**
   → 後で絶対に整理したくなる（早めに型にしよう）📦✨

---

## 10. ミニ演習 🎯✨（30分でOK）

### 演習A：Moneyを作ってみよう💰

* 0未満は失敗（`money.negative`）
* 小数点は許可（decimal）

### 演習B：ユーザー登録を拡張しよう👤

* Emailが空 → 失敗
* Email形式NG → 失敗
* 成功 → `Guid` を返す

### 演習C：テストを書く🧪

* Email成功ケース
* Email失敗ケース（空、形式NG）

---

## まとめ 🎀

Resultパターンは、**「失敗を普通の道として設計する」**ための武器だよ😊✨
DDD初心者ほど、ここを入れると世界が一気に見やすくなる🌈

次の章（第53章）で「型でビジネスルールを表現して `if` を減らす」方向に繋がるから、ここは土台として超大事だよ〜🧱💕
