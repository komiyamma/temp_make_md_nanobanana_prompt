# 第09章：バグ（不変条件違反）とFail Fast⚡🧱

この章はね、「**ここに来たらおかしい**」をハッキリさせて、**バグを早く見つけて早く直す**ための回だよ〜😊🔍✨
（本日時点では .NET 10 が LTS で、最新パッチは **10.0.2（2026-01-13）** だよ📅🧩 ([Microsoft][1]) ）

---

## 1) まず整理！「想定内の失敗」vs「バグ」🚦💥

ここ、超大事ポイントだよ🫶✨

### ✅ 想定内の失敗（＝仕様の範囲内）

* ユーザーの入力ミス（数量が0、メール形式が違う、など）✍️
* 業務ルール違反（在庫不足、期限切れ、など）📦
* 一時的な通信失敗（タイムアウト等）🌩️

➡️ **アプリは“普通に起きる”ものとして扱う**
➡️ 後で Result 型で扱う（この先の章でやるよ🎁）

### ❌ バグ（＝不変条件違反 / ここに来たらおかしい）

* 「絶対に起きない前提」を破った状態😱
* 例：在庫がマイナス、合計金額が負、nullが来ないはずなのに来た、など

➡️ **Fail Fast（すぐ止めて気づく）**の対象⚡
➡️ “隠さない”のが正解🙅‍♀️

---

## 2) 不変条件（Invariant）ってなに？🧱✨

**不変条件**は「そのオブジェクト（や処理）が正しいなら、常に成立してる条件」だよ✅

たとえば「推し活グッズ購入管理🛍️💖」なら…

* 予算（Budget）は **0以上** 💰
* 購入数量は **1以上** 🔢
* 在庫は **0以上** 📦
* 合計金額 = 単価×数量 は **0以上** 🧾

こういうのが「崩れたらバグ」になりやすいの😊

---

## 3) Fail Fast ってなに？⚡🚨

Fail Fast は、ざっくり言うと

> **おかしい状態を見つけたら、早めに大きく転ぶ（=気づけるようにする）**

だよ💥
「よく分からんけど進めちゃえ〜」が一番危ない😵‍💫

実際、エラーモデルの文脈でも「**プログラミングバグは fail-fast**」みたいに扱う考え方があるよ🧠 ([ジョー・ダフィーのブログ][2])

---

## 4) Fail Fast の実装パターン3つ（超よく使う）🧰✨

### パターンA：ガード節（Guard Clauses）で入口で落とす🚪🛑

![Fail Fast Guard](./picture/err_model_cs_study_009_fail_fast_guard.png)

「この引数おかしいよ？」を最初に止めるやつ！

```csharp
public static void GuardPositive(int value, string paramName)
{
    if (value <= 0) throw new ArgumentOutOfRangeException(paramName, "1以上である必要があります");
}
```

* これは「**呼び出し側が間違えた**」系に強い💪
* 例外のベストプラクティス的にも「通常フローに例外を使わない」は基本方針だよ📌 ([Microsoft Learn][3])

---

### パターンB：不変条件はコンストラクタで守る（“常に正しい”モデル）🧱💎

「作れた時点で正しい」を目指すと、バグ激減するよ😊

```csharp
public readonly record struct Budget(decimal Amount)
{
    public Budget(decimal amount) : this()
    {
        if (amount < 0) throw new InvalidOperationException("Invariant violated: Budget must be >= 0");
        Amount = amount;
    }
}
```

ポイント👇

* これは「ユーザーが悪い」じゃなくて、**コード（設計/実装）が悪い**のサイン💥
* だから **Fail FastでOK**⚡

---

### パターンC：アサーション（Debug.Assert / Trace.Assert）で“ここ絶対おかしい”を明示する🧨🧠

「ここ通ったらバグだよ！」の旗を立てるやつ🚩

```csharp
using System.Diagnostics;

Debug.Assert(total >= 0, "total should never be negative");
```

* **Debug.Assert は基本的にデバッグビルドでのみ動く**よ🧪 ([Microsoft Learn][4])
* リリースでも検査したいときは **Trace.Assert**（トレース有効前提）って選択肢もあるよ📌 ([Microsoft Learn][5])

---

## 5) 「ユーザー表示」と「ログ」を分ける考え方🫶🧾🔎

Fail Fast って「ユーザーに怖いエラーを見せる」って意味じゃないよ🙅‍♀️💦

* ユーザーに見せる：
  **「問題が発生しました。もう一度お試しください」**みたいに優しく🎀
* 開発者が見る：
  stack trace / 相関ID / 状態（どのIDで何が起きた）をログにガッツリ🔎🧵

例外を扱うときも「状態を復元」「適切に再throw」などベストプラクティスがあるよ📚 ([Microsoft Learn][6])

---

## 6) ミニ演習①：「不変条件」3つ決めよう📝💗

題材はこの先のミニPJと合わせて「推し活グッズ購入管理🛍️💖」にしよっ😊

### ステップ

1. まず “常に正しい状態” を3つ書く✍️
   例：

   * 予算は0以上
   * 在庫は0以上
   * 購入数量は1以上
2. それぞれ「破ったらどうする？」を書く🧠

   * **例外でFail Fast（InvalidOperationException など）**⚡
   * そのときログに残したい情報も1つ書く（商品IDとか）🔎

---

## 7) ミニ演習②：Fail Fast をコードに入れてみよう🔧✨

### 例：購入処理（まだResult型は出てきてないので超簡単に）

```csharp
public sealed class PurchaseService
{
    public void Purchase(int quantity, Budget budget, int stock, decimal unitPrice)
    {
        // 入力・引数の“おかしさ”は入口で落とす（呼び出し側ミス）
        if (quantity <= 0) throw new ArgumentOutOfRangeException(nameof(quantity));
        if (unitPrice < 0) throw new ArgumentOutOfRangeException(nameof(unitPrice));

        // 不変条件（ここが壊れてたらバグ）
        if (stock < 0) throw new InvalidOperationException("Invariant violated: stock must be >= 0");

        var total = unitPrice * quantity;

        // ここも不変条件（負になるのはバグ）
        if (total < 0) throw new InvalidOperationException("Invariant violated: total must be >= 0");

        // この先：想定内の失敗（予算不足、在庫不足）は Result型で扱う予定🎁
        // 今は章の目的が「バグ検知」なのでここまででOK😊
    }
}
```

✅ やること

* quantity=0 / stock=-1 などで呼び出して、落ち方の違いを観察👀✨
* 「どれが想定内」「どれがバグ」か言語化してみてね🗣️💕

---

## 8) AI活用（Copilot / Codex）テンプレ🤖💬✨

### ✅ 不変条件の洗い出し

* 「このクラスの不変条件候補を10個出して。業務ルールと不変条件を分けて」🧠

### ✅ Fail Fast のチェックポイント

* 「このメソッドで Fail Fast を入れるべき箇所を指摘して。例外型も提案して」🔍

### ✅ “ユーザー表示”と“ログ情報”の分離案

* 「ユーザー向けメッセージは優しく、ログ向けは調査に必要な項目を提案して」🧾🔎

（AIの案は便利だけど、最後の判断は自分でね😊🫶）

---

## 9) まとめ🎓✨（この章で身につけたこと）

* バグ（不変条件違反）は **Fail Fast** で早期発見⚡🧱
* Guard / コンストラクタ防衛 / Assert の3点セットが強い🧰✨
* ユーザー表示は優しく🎀、開発者向けはログで濃く🔎🧵

次の章で「例外境界🚪」に入ると、**“落ちてもアプリ全体が綺麗に扱える”**ようになってさらに気持ちよくなるよ〜😊📚✨

[1]: https://dotnet.microsoft.com/en-us/platform/support/policy/dotnet-core ".NET and .NET Core official support policy | .NET"
[2]: https://joeduffyblog.com/2016/02/07/the-error-model/?utm_source=chatgpt.com "Joe Duffy - The Error Model"
[3]: https://learn.microsoft.com/en-us/dotnet/standard/design-guidelines/exception-throwing?utm_source=chatgpt.com "Exception Throwing - Framework Design Guidelines"
[4]: https://learn.microsoft.com/ja-jp/dotnet/api/system.diagnostics.debug.assert?view=net-8.0&utm_source=chatgpt.com "Debug.Assert メソッド (System.Diagnostics)"
[5]: https://learn.microsoft.com/ja-jp/dotnet/api/system.diagnostics.trace.assert?view=net-10.0&utm_source=chatgpt.com "Trace.Assert Method (System.Diagnostics)"
[6]: https://learn.microsoft.com/en-us/dotnet/standard/exceptions/best-practices-for-exceptions?utm_source=chatgpt.com "Best practices for exceptions - .NET"
