# 第37章：Result型入門（例外を乱用しない）🧯

![Result型](./picture/tdd_ts_study_037_result_box.png)

## 🎯この章のゴール

* 「失敗しうる処理」を **throw じゃなく Result で返す** 設計にできる🙂
* 失敗もテストで固定して、**“失敗が仕様”** になる感覚をつかむ🧪
* 呼び出し側が **失敗を握りつぶせない** 書き方（＝事故りにくい）を覚える🔒

---

## 📚まず：例外（throw）って、なにが困るの？🥺

例外は便利だけど、**“この関数が失敗するか” が型から見えない**のが弱点…！
つまり、呼び出し側が「失敗する前提」で書かなくても、コンパイルが通っちゃう😇

* ✅ 例外が向く：**プログラマのバグ**（ありえない状態、不変条件違反）\n\n![Throw vs Result](./picture/tdd_ts_study_037_throw_vs_result.png)
* ✅ Resultが向く：**想定内の失敗**（入力ミス、在庫切れ、権限なし、残高不足…）

Resultにすると「失敗が起きる前提」が **型とテストに出る**から、TDDと相性が最高だよ🫶✨

---

## 📦 Result型ってなに？（超ざっくり）🍙

Resultは「成功 or 失敗」を **値として返す** 型だよ！\n\n![Ok and Err Boxes](./picture/tdd_ts_study_037_ok_err_boxes.png)

* 成功：`Ok<T>`（値 `T` を持つ）
* 失敗：`Err<E>`（エラー `E` を持つ）

有名どころだと `neverthrow` が Result / ResultAsync を提供してるよ（READMEに説明あり）([GitHub][1])
最新タグは `v8.2.0 (2025-02-21)` まで確認できるよ([GitHub][2])

---

## 🧪手を動かす：自作 Result で感覚をつかもう（依存なし）✋✨

まずは「Resultってこういう形」を、自分の手で作って理解しよう🙂
（後半でライブラリ版にもつなげるよ！）

### 1) `src/shared/result.ts` を作る🧩

```ts
// src/shared/result.ts
export type Ok<T> = { ok: true; value: T }
export type Err<E> = { ok: false; error: E }
export type Result<T, E> = Ok<T> | Err<E>

export const ok = <T>(value: T): Ok<T> => ({ ok: true, value })
export const err = <E>(error: E): Err<E> => ({ ok: false, error })

export const match = <T, E, R>(
  r: Result<T, E>,
  handlers: { ok: (v: T) => R; err: (e: E) => R }
): R => (r.ok ? handlers.ok(r.value) : handlers.err(r.error))
```

---

## 🧪ミニ題材：ATMの「引き出し」🧾💸

**仕様**（＝テストで固定したい約束）👇

* 金額が 0 以下 → 失敗（InvalidAmount）
* 残高不足 → 失敗（InsufficientFunds）
* それ以外 → 成功（新しい残高を返す）

### 2) エラーを「分類」して union で表す🧷✨

```ts
// src/domain/withdraw.ts\n\n![ATM Logic Sorter](./picture/tdd_ts_study_037_atm_sorter.png)
import { Result, ok, err } from "../shared/result"

export type WithdrawError =
  | { type: "InvalidAmount"; amount: number }
  | { type: "InsufficientFunds"; balance: number; amount: number }

export const withdraw = (
  balance: number,
  amount: number
): Result<number, WithdrawError> => {
  if (amount <= 0) return err({ type: "InvalidAmount", amount })
  if (balance < amount) return err({ type: "InsufficientFunds", balance, amount })
  return ok(balance - amount)
}
```

ここ大事ポイント💡
👉 **エラーを文字列で雑にしないで、型で“意味”を持たせる**と、呼び出し側もテストも超ラクになるよ〜！🥰\n\n![Typed Error Tags](./picture/tdd_ts_study_037_typed_error_tags.png)

---

## 🧪TDD：テストから入ろう（Red→Green→Refactor）🚦✨

### 3) `tests/withdraw.test.ts`

```ts
import { describe, it, expect } from "vitest"
import { withdraw } from "../src/domain/withdraw"
import { match } from "../src/shared/result"

describe("withdraw", () => {
  it("amount が 0 以下なら InvalidAmount を返す", () => {
    const r = withdraw(1000, 0)

    const view = match(r, {\n\n![Match Railway](./picture/tdd_ts_study_037_match_railway.png)
      ok: () => "OK",
      err: (e) => e.type,
    })

    expect(view).toBe("InvalidAmount")
  })

  it("残高不足なら InsufficientFunds を返す", () => {
    const r = withdraw(1000, 1500)

    const view = match(r, {\n\n![Match Railway](./picture/tdd_ts_study_037_match_railway.png)
      ok: () => "OK",
      err: (e) => e.type,
    })

    expect(view).toBe("InsufficientFunds")
  })

  it("成功なら新しい残高を返す", () => {
    const r = withdraw(1000, 300)

    const value = match(r, {
      ok: (v) => v,
      err: () => -1,
    })

    expect(value).toBe(700)
  })
})
```

### ✅ここで得られる “気持ちよさ” 😆💞

* 「失敗」もちゃんとテストで固定できる
* 例外みたいに “突然落ちる” じゃなくて、**必ずハンドリングされる流れ**になる
* 関数の型だけで「失敗しうる」が伝わる

---

## 🧠設計の超入門ポイント：Resultにしたら「責務」が分かれる✨\n\n![Responsibility Split](./picture/tdd_ts_study_037_responsibility_split.png)

Resultを使うと、自然にこう分かれるよ👇

* **ドメイン関数（withdraw）**：
  「何が失敗で、どういう情報が必要か」を決めて返す🧠
* **呼び出し側**：
  失敗を UI/ログ/メッセージに変換する（＝表現の責務）🎨

この分離ができると、あとで **UIが変わってもドメインが揺れない**よ！最強🛡️✨

---

## 🤖AIの使いどころ（この章は相性いいよ〜！）🤖💗

AIは「エラー分類」と「テスト観点洗い出し」にめちゃ強い！

### 使えるプロンプト例（そのままコピペOK）📝✨

* 「withdraw の失敗ケースを **ユーザー起因/システム起因** に分類して、型（union）案を出して」
* 「この Result を返す関数のテスト観点、**正常→境界→異常** の順で最小ステップ案ちょうだい」
* 「この Err 型、呼び出し側が表示文を作りやすい？足りない情報ある？」

⚠️注意：AIの案は採用前に、あなたが「仕様として妥当か」を必ずチェックね🙂🫶

---

## 🌟発展：ライブラリを使うなら（最新の雰囲気）📦

### ✅ neverthrow（Result / ResultAsync）\n\n![Neverthrow Toolkit](./picture/tdd_ts_study_037_neverthrow_toolkit.png)

* Result と、Promise向けの `ResultAsync` があるよ([GitHub][1])
* `fromPromise` みたいに Promise を ResultAsync に包める話もある（和訳記事でも例あり）([Zenn][3])

さらに嬉しいのが **eslint-plugin-neverthrow** 系💖
Result を「必ず処理しろ！」って lint で強制できる✨
neverthrow のREADMEでも推奨されてるよ([GitHub][4])

* 代表的な実装（GitHubにある本家）([GitHub][5])
* 2025-11-21 に更新が見える派生パッケージもある（npm）([NPM][6])

> 「Result返したのに放置」を機械的に潰せるの、チーム開発だと超助かるやつ…！🥹🫶

### ✅ ts-results（Rust風 Result/Option）

RustっぽいAPIが好きなら候補。READMEに例もあるよ([GitHub][7])

### ✅ Effect（Either/Option と pattern match）

「もっと強い抽象（Either/Effect）で大きめに組みたい」派向け。公式ドキュメントに Either.match / pattern matching があるよ([Effect][8])

---

## ✅チェック（この章の合格ライン）🎓💮

* ✅ 「想定内の失敗」を throw じゃなく Result で返してる
* ✅ Err が видно（見える）で、**呼び出し側が欲しい情報**を持ってる
* ✅ テストが「失敗の種類」を仕様として固定してる
* ✅ 呼び出し側は `match`（または isOk/isErr）で **必ず分岐**してる
* ✅ “成功時しか読めない値” を Err のときに読めない（型で守られてる）

---

## 🧪おかわり課題（余裕あったら）🍰✨

1. `WithdrawError` に `{ type: "DailyLimitExceeded"; limit: number; amount: number }` を追加して、TDDで拡張してみよ💪
2. `match` の代わりに `if (r.ok) ... else ...` を書いて、読みやすさ比較してみよ👀
3. 「エラー表示文」を作る関数を別にして、**ドメインから表現を追い出す**練習してみよ🎨✨

---

次の第38章（網羅性/exhaustive）に行くと、いま作った `WithdrawError` みたいな union を **“抜け漏れゼロ”** で扱う方法ができるようになるよ🕳️🚫✨

[1]: https://github.com/supermacro/neverthrow "GitHub - supermacro/neverthrow: Type-Safe Errors for JS & TypeScript"
[2]: https://github.com/supermacro/neverthrow/tags "Tags · supermacro/neverthrow · GitHub"
[3]: https://zenn.dev/coji/articles/neverthrow-result-async?utm_source=chatgpt.com "neverthrow: ResultAsync の使い方 (和訳)"
[4]: https://github.com/supermacro/neverthrow?utm_source=chatgpt.com "supermacro/neverthrow: Type-Safe Errors for JS & TypeScript"
[5]: https://github.com/mdbetancourt/eslint-plugin-neverthrow?utm_source=chatgpt.com "mdbetancourt/eslint-plugin-neverthrow"
[6]: https://www.npmjs.com/package/%40okee-tech%2Feslint-plugin-neverthrow?utm_source=chatgpt.com "@okee-tech/eslint-plugin-neverthrow"
[7]: https://github.com/vultix/ts-results "GitHub - vultix/ts-results: A typescript implementation of Rust's Result object."
[8]: https://effect.website/docs/data-types/either/?utm_source=chatgpt.com "Either | Effect Documentation"
