# 第16章：Result<T>を“最小構成”で作る🧰

この章は「Result型って結局なにが嬉しいの？どう作ればいいの？」を **自分の手で腹落ち**させる回だよ😊✨
（ライブラリを使う前に、まず “仕組み” を理解しちゃおう〜！）

---

## 0) 2026の前提（情報アップデート）🗓️✨

いま（**2026/01/19**）の時点だと、**.NET 10 は 2025/11/11 に正式リリースされた LTS**で、**2028/11/10 までサポート**って位置づけだよ📌 ([Microsoft for Developers][1])
そして **C# 14**も同時期の世代で、Microsoft Learn に “What’s new” がまとまってるよ🧠 ([Microsoft Learn][2])
テストは **xUnit.net v3** が .NET 8+ 対応で、VS 2026 での話も公式に載ってる🧪 ([xUnit.net][3])

---

## 1) Result<T>の超ざっくりイメージ🎁✅❌

![Toggle Switch](./picture/err_model_cs_study_016_toggle_switch.png)

Result<T> は「成功 or 失敗」を **1つの箱**に入れる型だよ。

* ✅ 成功：**Value（値）**を持つ
* ❌ 失敗：**Error（失敗理由）**を持つ
* そして **同時に両方は持たない**（←これ大事！）💡

例：在庫チェック

* 在庫OK → `Result<int>.Success(残り数)`
* 在庫NG → `Result<int>.Failure(Error("OUT_OF_STOCK", "在庫がありません"))`

---

## 2) この章で作る“最小セット”🧩

![Result Components](./picture/err_model_cs_study_016_result_components.png)

第16章のゴールは「最低限これだけあれば動くよね」の形👇

* `IsSuccess`（成功？）
* `Value`（成功時の値）
* `Error`（失敗時の情報）
* `Success(...) / Failure(...)`（作り方を統一）

そして “初心者が事故りやすい点” を防ぐために、**不正状態を作れない**ようにするよ🛡️✨
（成功なのにErrorが入ってる、みたいな矛盾を禁止！）

---

## 3) まずは Error 型（最小）🏷️

![Error Record Anatomy](./picture/err_model_cs_study_016_error_anatomy.png)

「失敗理由」を型にしておくと、あとで **分類・ログ・ProblemDetails** に繋げやすくなるよ🧾✨

```csharp
namespace ErrorModeling;

public sealed record Error(string Code, string Message);
```

* `Code`：機械が扱う（分類・翻訳・HTTP化に強い）🤖
* `Message`：人が読む（表示文言の元）💬

---

## 4) Result（値なし版）も最小で作る（あると便利）🎁

![Constructor Guard Logic](./picture/err_model_cs_study_016_constructor_guard.png)

「ただ成功/失敗だけ返したい」ケースって結構あるの。なので先に作っちゃう😊

```csharp
namespace ErrorModeling;

public sealed class Result
{
    private readonly Error? _error;

    private Result(bool isSuccess, Error? error)
    {
        if (isSuccess && error is not null)
            throw new ArgumentException("SuccessなのにErrorが入ってるのはNGだよ😵");

        if (!isSuccess && error is null)
            throw new ArgumentException("FailureなのにErrorが無いのはNGだよ😵");

        IsSuccess = isSuccess;
        _error = error;
    }

    public bool IsSuccess { get; }
    public bool IsFailure => !IsSuccess;

    public Error Error =>
        IsFailure ? _error! : throw new InvalidOperationException("SuccessのときはErrorは読めないよ🙅‍♀️");

    public static Result Success() => new(isSuccess: true, error: null);

    public static Result Failure(Error error) =>
        new(isSuccess: false, error: error ?? throw new ArgumentNullException(nameof(error)));
}
```

ここでやってることはシンプルで、**矛盾した状態をコンストラクタで拒否**してるだけだよ👌✨

---

## 5) 本命！Result<T>（値あり）を作る🧰✨

![Result<T> Generic Box](./picture/err_model_cs_study_016_result_t_box.png)

次は「成功なら値」「失敗ならエラー」を持つバージョン！

```csharp
namespace ErrorModeling;

public sealed class Result<T>
{
    private readonly T? _value;
    private readonly Error? _error;

    private Result(bool isSuccess, T? value, Error? error)
    {
        if (isSuccess && error is not null)
            throw new ArgumentException("SuccessなのにErrorが入ってるのはNGだよ😵");

        if (!isSuccess && error is null)
            throw new ArgumentException("FailureなのにErrorが無いのはNGだよ😵");

        IsSuccess = isSuccess;
        _value = value;
        _error = error;
    }

    public bool IsSuccess { get; }
    public bool IsFailure => !IsSuccess;

    public T Value =>
        IsSuccess ? _value! : throw new InvalidOperationException("FailureのときはValueは読めないよ🙅‍♀️");

    public Error Error =>
        IsFailure ? _error! : throw new InvalidOperationException("SuccessのときはErrorは読めないよ🙅‍♀️");

    public static Result<T> Success(T value) => new(isSuccess: true, value: value, error: null);

    public static Result<T> Failure(Error error) =>
        new(isSuccess: false, value: default, error: error ?? throw new ArgumentNullException(nameof(error)));
}
```

## ポイント3つ🌟

1. `Value` と `Error` は **読んじゃダメな時に例外**を投げる（事故を早く見つける⚡）
2. `Success/Failure` の **作り方を統一**（呼び出し側が迷わない🧭）
3. “失敗はErrorを必ず持つ” を強制（失敗理由が消えない🔎）

---

## 6) 使ってみる（超ミニ例）🧪✨

![Usage Flow Example](./picture/err_model_cs_study_016_usage_flow.png)

「空文字は想定内の失敗」にしてみよう〜！

```csharp
using ErrorModeling;

static Result<string> ValidateName(string? name)
{
    if (string.IsNullOrWhiteSpace(name))
        return Result<string>.Failure(new Error("NAME_EMPTY", "名前を入力してね🌸"));

    return Result<string>.Success(name.Trim());
}

// 使う側
var r = ValidateName("  こみやんま  ");

if (r.IsFailure)
{
    Console.WriteLine(r.Error.Message);
    return;
}

Console.WriteLine($"Hello, {r.Value}!");
```

---

## 7) ミニ演習：ユニットテストちょっと書く🧪💖

![Unit Test Visualization](./picture/err_model_cs_study_016_unit_test_visual.png)

ここは「Resultが正しく動く」証拠を作る感じ！
xUnit は v3 が .NET 8+ 対応だよ🧪 ([xUnit.net][3])

## テスト例（最小）✅❌

```csharp
using ErrorModeling;
using Xunit;

public class ResultTests
{
    [Fact]
    public void Success_should_have_value()
    {
        var r = Result<int>.Success(42);

        Assert.True(r.IsSuccess);
        Assert.Equal(42, r.Value);
    }

    [Fact]
    public void Failure_should_have_error()
    {
        var r = Result<int>.Failure(new Error("NG", "だめだよ🥲"));

        Assert.True(r.IsFailure);
        Assert.Equal("NG", r.Error.Code);
    }

    [Fact]
    public void Accessing_value_on_failure_should_throw()
    {
        var r = Result<int>.Failure(new Error("NG", "だめだよ🥲"));

        Assert.Throws<InvalidOperationException>(() => _ = r.Value);
    }

    [Fact]
    public void Accessing_error_on_success_should_throw()
    {
        var r = Result<int>.Success(1);

        Assert.Throws<InvalidOperationException>(() => _ = r.Error);
    }
}
```

---

## 8) よくあるつまずき（先に潰す）🧯

* **成功/失敗の両方が入る設計**にしちゃう（矛盾）😵
  → コンストラクタで弾くのが正解👍
* `Value` を `null` 許容にして混乱する🤔
  → まずは「成功なら値がある」前提でOK。必要なら第17章で情報設計を強化しよう🧾✨
* “想定内の失敗” を例外で投げ続ける💥
  → Resultに寄せると「呼び出し側が読むだけで分かるコード」になっていくよ📖✨

---

## 9) AI活用（この章で効く使い方）🤖🧑‍🏫

Copilot / Codex に投げるときは、**お願いの型**を揃えるとめちゃ強いよ💪✨

## ① テストケース候補を増やす🧪

「Result<T>のユニットテストを追加したい。境界ケース（null/default/値型/参照型）を考えて、テスト案を箇条書きで出して」

## ② 不正状態レビュー役👀

「この Result<T> 実装に、矛盾状態（SuccessなのにErrorなど）が入り込む経路があるかレビューして。あれば修正案も」

## ③ 例外メッセージ改善💬

「初心者が読んで分かる例外メッセージにしたい。短くてやさしい文言を提案して」

---

## 10) この章のゴール達成チェック✅✨

できたら勝ち〜！🎉

* ✅ `Result` と `Result<T>` が作れた
* ✅ 不正状態が作れない（コンストラクタで防御）
* ✅ 成功/失敗で `Value/Error` の読み分けができる
* ✅ xUnitで最低4本テストを書けた🧪

---

次の **第17章**では、このResultに「どんな情報を持たせると運用・UXが強くなるか」🧾🧠（code/message/detail/retryable/action みたいなやつ）を育てていくよ〜😊✨

[1]: https://devblogs.microsoft.com/dotnet/announcing-dotnet-10/?utm_source=chatgpt.com "Announcing .NET 10"
[2]: https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-14?utm_source=chatgpt.com "What's new in C# 14"
[3]: https://xunit.net/?utm_source=chatgpt.com "xUnit.net: Home"
