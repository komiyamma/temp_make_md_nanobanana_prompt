# 第25章：エラー設計（ドメイン vs インフラ）😇🚨

![testable_ts_study_025_error_sorting.png](./picture/testable_ts_study_025_error_sorting.png)

この章は、「失敗」をちゃんと“設計の一部”として扱えるようになる回だよ〜！💪✨
（※ 2026/01/16 時点の情報として、TypeScript は npm の latest が **5.9.3** だよ〜。([npm][1])）

---

## 25.0 ゴール🎯✨* 「この失敗は **仕様として起きる失敗**？それとも **外部都合の事故**？」を瞬時に分けられる🧠⚡


* 失敗を “型” として表現して、テストが安定する形にできる🧪💎
* 次章（第26章）でやる「境界で変換」がスムーズにできるようになる🔁🧯

---

## 25.1 まず結論：失敗は2種類に分けるとラク😌✨### A) ドメインエラー（仕様の失敗）

😇* 例：在庫が足りない、クーポンが無効、年齢制限に引っかかった、など


* **業務ルールにより“起きて当然”** な失敗
* だいたい「ユーザーにそのまま伝えてOK」寄り📣

### B) インフラエラー（外部都合の失敗）

🚨* 例：DB落ちた、ネットワークタイムアウト、外部APIが500返した、など


* **外部システムの都合で起きる事故**
* ユーザーには「ごめん、今ムリ🙏」系の表現になりがち（詳細はログへ）🪵

この分け方自体が、いろんな設計で使われる超基本の考え方だよ〜。([fsharpforfunandprofit.com][2])

---

## 25.2 どっち？判定のコツ✂️

![testable_ts_study_025_error_decision_tree.png](./picture/testable_ts_study_025_error_decision_tree.png)

🧠迷ったら、この質問👇



### ✅「仕様として想定してる失敗？」* YES → **ドメインエラー**😇


* NO → 次へ

### ✅「外部が落ちた／遅い／壊れた系？」* YES → **インフラエラー**🚨



### ✅「同じ入力で毎回同じ失敗になる？」* なりやすい → ドメイン寄り


* ならない（気分で落ちる😇）→ インフラ寄り

---

## 25.3 設計ルール：エラーは“データ”として持つのが最強🧊✨

![testable_ts_study_025_discriminated_union_switch.png](./picture/testable_ts_study_025_discriminated_union_switch.png)

TypeScript だと特に、



* `throw` を多用するより
* **判別可能な union（discriminated union）** で「エラーの種類」を型にする

これがめちゃ強い💪
`switch` で分岐すると、型がスッと絞れて安全になるよ〜。([TypeScript][3])

---

## 25.4 ハンズオン題材：注文（Place Order）

![testable_ts_study_025_order_error_examples.png](./picture/testable_ts_study_025_order_error_examples.png)

🛒🍕「注文する」って処理で起きそうな失敗を分けてみよ〜！✍️✨



### ドメインエラー候補😇* カートが空


* 在庫が足りない
* クーポン無効
* 支払いが拒否された（※“決済会社が正常に答えた結果として拒否”ならドメイン寄り）

### インフラエラー候補🚨* 決済APIがタイムアウト


* DB接続できない
* 外部サービスが落ちた（5xx）

---

## 25.5 型を作る（ドメイン vs インフラ）

![testable_ts_study_025_infra_retry_flag.png](./picture/testable_ts_study_025_infra_retry_flag.png)

🧩✨ここからコードだよ〜！🧸
（※ 例は最小構成。ファイル分割してもOK！）

```ts
// 1) ドメインエラー（仕様の失敗）😇
export type DomainError =
  | { type: "CartEmpty" }
  | { type: "OutOfStock"; sku: string; requested: number; available: number }
  | { type: "InvalidCoupon"; code: string }
  | { type: "PaymentDeclined"; reason: "INSUFFICIENT_FUNDS" | "FRAUD" | "UNKNOWN" };

// 2) インフラエラー（外部都合）🚨
// ★ポイント：ユーザーに見せる文言じゃなく「状況」を持つ！
export type InfraError =
  | { type: "NetworkTimeout"; service: "payment" | "inventory"; timeoutMs: number; retryable: true }
  | { type: "DbUnavailable"; operation: "loadCart" | "saveOrder"; retryable: true }
  | { type: "Unexpected"; message: string; retryable: false; cause?: unknown };
```

### いい感じポイント🌟* `type: "..."` があるから `switch` で安全に分岐できる（型が絞れる）

🛡️([TypeScript][3])


* インフラエラーに `retryable` を入れると、リトライ設計がラクになる🔁✨

---

## 25.6 Result型で「失敗も戻り値」にする📦🧪「throw じゃなくて戻り値で返す」やり方ね！

![testable_ts_study_025_result_vs_throw.png](./picture/testable_ts_study_025_result_vs_throw.png)
TypeScript だと `Result<T, E>` を使うとテストが超安定するよ〜🧊

```ts
export type Ok<T> = { ok: true; value: T };
export type Err<E> = { ok: false; error: E };
export type Result<T, E> = Ok<T> | Err<E>;

export const ok = <T>(value: T): Ok<T> => ({ ok: true, value });
export const err = <E>(error: E): Err<E> => ({ ok: false, error });
```

ちなみに「Result型を提供するライブラリ」として `neverthrow` が有名だよ〜（`ResultAsync` もある）📦✨([GitHub][4])
（この教材では自作でも全然OK！）

---

## 25.7 中心ロジックは「ドメインエラー」を返すのが基本🍰✨

![testable_ts_study_025_safe_return_box.png](./picture/testable_ts_study_025_safe_return_box.png)

中心（ロジック）は、できるだけ **外部の事故を知らない** ほうがキレイ！🙈
なので、中心ロジックは「仕様としての失敗」を丁寧に返すのが王道だよ〜😇

```ts
import { Result, ok, err } from "./result";
import { DomainError } from "./errors";

type CartItem = { sku: string; qty: number; price: number };
type Cart = { items: CartItem[]; coupon?: string };

export function validateCart(cart: Cart): Result<Cart, DomainError> {
  if (cart.items.length === 0) return err({ type: "CartEmpty" });

  // 例：クーポンの形だけチェック（詳細は別関数でもOK）
  if (cart.coupon && !/^[A-Z0-9]{6,10}$/.test(cart.coupon)) {
    return err({ type: "InvalidCoupon", code: cart.coupon });
  }

  return ok(cart);
}
```

---

## 25.8 テストが「気分で落ちない」世界へ🧪🌈

ドメインエラーが `Result` で返ると、テストはこうなる👇



```ts
import { describe, it, expect } from "vitest";
import { validateCart } from "./validateCart";

describe("validateCart", () => {
  it("カートが空なら CartEmpty 😇", () => {
    const r = validateCart({ items: [] });
    expect(r).toEqual({ ok: false, error: { type: "CartEmpty" } });
  });

  it("クーポン形式が変なら InvalidCoupon 😇", () => {
    const r = validateCart({ items: [{ sku: "A", qty: 1, price: 1000 }], coupon: "!?!" });
    expect(r.ok).toBe(false);
    if (!r.ok) {
      expect(r.error.type).toBe("InvalidCoupon");
    }
  });
});
```

テスト基盤としては、最近だと Vitest 4 系が大きめの更新が入ってるよ（4.0 のアナウンスや、GitHub のリリースで 4.0.17 などが確認できる）🧪⚡([Vitest][5])

---

## 25.9 よくある事故パターン（ここ注意！

![testable_ts_study_025_throw_chaos_vs_return_peace.png](./picture/testable_ts_study_025_throw_chaos_vs_return_peace.png)

）⚠️😵‍💫### ❌ 1) ドメインエラーを全部 `throw` にする* 使う側が毎回 `try/catch` 地獄になりがち😇🌀


* “仕様の失敗” は戻り値で返すほうが読みやすいことが多い📦

### ❌ 2) インフラの例外メッセージを中心に持ち込む* DBのエラー文言とかが中心を汚す😵


* 次章（第26章）で「境界で変換」するのがキレイ✨

### ❌ 3) エラーが「文字列」だけ* `"error"` とかにすると、後で分類不能で泣く😭


* `type` + 必要データ、が正義🛡️([TypeScript][3])

---

## 25.10 章末ミニ課題📝

![testable_ts_study_025_sorting_game_ui.png](./picture/testable_ts_study_025_sorting_game_ui.png)

✨### 課題A：分類ゲーム🎮次を「ドメイン/インフラ」に分けてね👇

1. 在庫が0だった
2. 決済APIが502返した
3. クーポン期限切れ
4. DB接続タイムアウト
5. 年齢制限NG

### 課題B：型を増やす✍️* `DomainError` に `TooManyItems` を追加（例：上限 99 個）


* `InfraError` に `RateLimited`（429）を追加（`retryAfterSec` を持たせる）

---

## 25.11 AIに手伝ってもらう小ワザ🤖🎀AIには「列挙」と「抜け漏れチェック」が超得意だよ〜✨
プロンプト例👇

* 「注文処理で起きうるドメインエラーを10個列挙して、ユーザー向け文言は書かず“状況データ”だけ提案して」
* 「インフラエラーに入れるべきフィールド候補（retryable, service, operation…）を提案して」

（ただし “境界をどこに引くか” は自分が決めるのが大事！✂️🧠）

---

## 25.12 まとめ🎁

✨* 失敗は **ドメイン（仕様）** と **インフラ（外部事故）** に分けると整理が爆速😇🚨([fsharpforfunandprofit.com][2])


* TypeScript では **判別可能 union** がエラー設計に相性バツグン🛡️([TypeScript][3])
* `Result<T, E>` で返すとテストが安定して幸福度UP🧪🌈（`neverthrow` みたいな選択肢もあるよ）([GitHub][4])

---

## 次章予告👀✨

（第26章）次はついに！
**境界でエラー変換（例外→結果、結果→表示）** 🔁🧯
「インフラ例外を中心が扱える形に変換する」一本槍で、めちゃキレイに繋げるよ〜！🎀

[1]: https://www.npmjs.com/package/typescript?utm_source=chatgpt.com "TypeScript"
[2]: https://fsharpforfunandprofit.com/posts/against-railway-oriented-programming/?utm_source=chatgpt.com "Against Railway-Oriented Programming"
[3]: https://www.typescriptlang.org/docs/handbook/unions-and-intersections.html?utm_source=chatgpt.com "Handbook - Unions and Intersection Types"
[4]: https://github.com/supermacro/neverthrow?utm_source=chatgpt.com "supermacro/neverthrow: Type-Safe Errors for JS & TypeScript"
[5]: https://vitest.dev/blog/vitest-4?utm_source=chatgpt.com "Vitest 4.0 is out!"
