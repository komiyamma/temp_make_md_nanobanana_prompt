# 第88章：エラー設計②：Result型で返す場合の型設計📦

## 🎯 ねらい

![🎯 ねらい](./picture/ddd_ts_study_088_visual_1.png)


* 「失敗」も型で表して、**返す側も使う側も迷わない**ようにする💪🙂
* **例外（throw）とResult（戻り値）を混ぜて地獄にならない**ルールを作る🧯🔥
* UI / API に返すための **errorCode・userMessage・details** を整える🧩✨

---

## まず結論🌸

* **ドメイン層**：不変条件違反などは「例外（throw）」でOK（前章の流れ）🧱🧯
* **アプリ層（ユースケース）**：UI/APIに返すのは **Result型** がめちゃ相性いい📦✅
* **境界**：例外はアプリ層でキャッチして **Resultに変換** する（ここが超大事！）🚪🔁

Resultの基本形はこれ👇
`成功: { ok: true, value: ... }` / `失敗: { ok: false, error: ... }`
こういう **判別可能Union** にすると、TypeScriptが分岐を助けてくれるよ🧠✨ ([typescriptlang.org][1])

---

## ✅ Result型が向いてる失敗・向いてない失敗

![✅ Result型が向いてる失敗・向いてない失敗](./picture/ddd_ts_study_088_visual_2.png)


### Result型が向いてる🥰

* 入力が不正（バリデーション）🧾❌
* 目的の注文が無い（NotFound）🔎❌
* 状態が違って操作できない（例：未払いなのに提供）🚦❌
* つまり **想定内の失敗**！

### 例外で良い（= Resultにするより上でまとめて扱う）😵‍💫

![例外で良い（= Resultにするより上でまとめて扱う）😵‍💫](./picture/ddd_ts_study_088_visual_3.png)


* バグ、想定外、落ちるべきもの（null前提崩壊、未対応分岐など）💥
* ただし最終的にはUI/APIに返すなら、アプリ層で `INTERNAL_ERROR` としてResult化しちゃうのが実務的🙆‍♀️

---

## 1️⃣ Result型を自作する ミニマム版📦

ポイントは **「ok で判別できる」**こと！
（Zodの `safeParse()` も `success` で判別できる同じ発想だよ😉） ([Zod][2])

```ts
// result.ts
export type Ok<T> = Readonly<{
  ok: true;
  value: T;
}>;

export type Err<E> = Readonly<{
  ok: false;
  error: E;
}>;

export type Result<T, E> = Ok<T> | Err<E>;

export const ok = <T>(value: T): Ok<T> => ({ ok: true, value });
export const err = <E>(error: E): Err<E> => ({ ok: false, error });

// あると便利✨
export const match = <T, E, A>(
  r: Result<T, E>,
  onOk: (v: T) => A,
  onErr: (e: E) => A
): A => (r.ok ? onOk(r.value) : onErr(r.error));
```

これだけで、ユースケースの返り値が超読みやすくなるよ📖✨

---

## 2️⃣ AppError の型設計💡

第88章の主役はここ！
**UI/APIへ返すエラー**は、最低この3点があると強い💪

* `code`：機械が読む（安定させる）🤖
* `userMessage`：人が読む（やさしい）👤💬
* `details`：開発者・ログ向け（解析できる）🛠️🔍

### エラーコードの作り方🧩

![エラーコードの作り方🧩](./picture/ddd_ts_study_088_visual_4.png)


`as const` + `satisfies` がめちゃ便利！
`satisfies` は「型チェックだけして、推論を壊しにくい」ための演算子だよ🧠✨ ([typescriptlang.org][3])

```ts
// appError.ts
export const ERROR_CODE = {
  INPUT_INVALID: "INPUT_INVALID",
  ORDER_NOT_FOUND: "ORDER_NOT_FOUND",
  ORDER_INVALID_STATE: "ORDER_INVALID_STATE",
  INTERNAL_ERROR: "INTERNAL_ERROR",
} as const satisfies Record<string, string>;

export type ErrorCode = (typeof ERROR_CODE)[keyof typeof ERROR_CODE];

// バリデーション詳細（例）
export type FieldViolation = Readonly<{
  field: string;
  message: string;
}>;

export type AppError =
  | Readonly<{
      code: typeof ERROR_CODE.INPUT_INVALID;
      userMessage: string;
      details: { violations: FieldViolation[] };
    }>
  | Readonly<{
      code: typeof ERROR_CODE.ORDER_NOT_FOUND;
      userMessage: string;
      details: { orderId: string };
    }>
  | Readonly<{
      code: typeof ERROR_CODE.ORDER_INVALID_STATE;
      userMessage: string;
      details: { currentState: string; action: string };
    }>
  | Readonly<{
      code: typeof ERROR_CODE.INTERNAL_ERROR;
      userMessage: string;
      details: { message?: string };
    }>;
```

### コツ🌷

* `code` は **ログ・監視・翻訳キー**にもなるから、後から変えない前提で命名するのが安全🔒
* `userMessage` は「次に何をすればいいか」まで書くと親切💖
  例：「支払いが終わっていません。先にお支払いをお願いします💳」

---

## 3️⃣ 例題 カフェ注文のユースケースで使ってみる☕🧾

![3️⃣ 例題 カフェ注文のユースケースで使ってみる☕🧾](./picture/ddd_ts_study_088_visual_5.png)


今回は「PayOrder」を想像して書くね！

* ドメイン層：状態が違ったら例外投げる（前章）🧯
* アプリ層：それをキャッチして Result で返す📦

```ts
// payOrderUseCase.ts
import { Result, ok, err } from "./result";
import { AppError, ERROR_CODE } from "./appError";

// 例：ドメイン例外（前章の流れを想定）
class OrderNotFoundError extends Error {
  constructor(public readonly orderId: string) {
    super("Order not found");
  }
}
class InvalidOrderStateError extends Error {
  constructor(
    public readonly currentState: string,
    public readonly action: string
  ) {
    super("Invalid state");
  }
}

// 例：戻り値DTO
export type PayOrderOutput = Readonly<{
  orderId: string;
  paidAt: string; // 本当はClock注入で作る（第86章）
}>;

export async function payOrder(
  input: { orderId: string },
): Promise<Result<PayOrderOutput, AppError>> {
  try {
    // ここで repository から取ってきて、order.pay() するイメージ
    // throw new OrderNotFoundError(input.orderId);
    // throw new InvalidOrderStateError("Draft", "PayOrder");

    const result: PayOrderOutput = {
      orderId: input.orderId,
      paidAt: new Date().toISOString(),
    };
    return ok(result);

  } catch (e) {
    if (e instanceof OrderNotFoundError) {
      return err({
        code: ERROR_CODE.ORDER_NOT_FOUND,
        userMessage: "注文が見つかりませんでした🙇‍♀️ 注文番号を確認してね！",
        details: { orderId: e.orderId },
      });
    }
    if (e instanceof InvalidOrderStateError) {
      return err({
        code: ERROR_CODE.ORDER_INVALID_STATE,
        userMessage: "この注文は今の状態だと支払いできません😢",
        details: { currentState: e.currentState, action: e.action },
      });
    }
    return err({
      code: ERROR_CODE.INTERNAL_ERROR,
      userMessage: "ごめんね、内部エラーが起きました💦 もう一回試してみてね！",
      details: { message: e instanceof Error ? e.message : undefined },
    });
  }
}
```

✅ これで「呼び出し側」が超ラクになる！

```ts
import { payOrder } from "./payOrderUseCase";

const r = await payOrder({ orderId: "o_123" });

if (r.ok) {
  console.log("支払い完了🎉", r.value);
} else {
  // r.error は code で分岐できる
  console.log("エラー😵", r.error.code, r.error.userMessage);
}
```

---

## 4️⃣ 入力バリデーションを Result に統一する🧾✨

Zodの `safeParse()` は「成功か失敗か」を判別可能Unionで返すよ。([Zod][2])
だから、Result型とめっちゃ相性いい🤝💕

```ts
import { z } from "zod";
import { Result, ok, err } from "./result";
import { AppError, ERROR_CODE } from "./appError";

const PayOrderInputSchema = z.object({
  orderId: z.string().min(1),
});

export function validatePayOrderInput(
  raw: unknown
): Result<{ orderId: string }, AppError> {
  const parsed = PayOrderInputSchema.safeParse(raw);
  if (!parsed.success) {
    const violations = parsed.error.issues.map(i => ({
      field: i.path.join(".") || "(root)",
      message: i.message,
    }));
    return err({
      code: ERROR_CODE.INPUT_INVALID,
      userMessage: "入力にまちがいがあるみたい😢 もう一度チェックしてね！",
      details: { violations },
    });
  }
  return ok(parsed.data);
}
```

---

## 5️⃣ Resultを APIレスポンスに変換する小ネタ📮

もし将来HTTP APIにするなら、エラー形式は **Problem Details**（RFC 9457）が有名だよ📄✨
RFC 9457 は RFC 7807 を置き換える形で標準化されてる！ ([RFCエディタ][4])

ここでは雰囲気だけ👇（本格実装は好きなフレームワークでOK）

```ts
type ProblemDetails = {
  type: string;
  title: string;
  status: number;
  detail?: string;
  instance?: string;
  extensions?: Record<string, unknown>;
};

function toProblem(e: AppError): ProblemDetails {
  switch (e.code) {
    case "INPUT_INVALID":
      return {
        type: "https://example.com/problems/input-invalid",
        title: "Invalid input",
        status: 400,
        detail: e.userMessage,
        extensions: { violations: e.details.violations },
      };
    case "ORDER_NOT_FOUND":
      return {
        type: "https://example.com/problems/order-not-found",
        title: "Order not found",
        status: 404,
        detail: e.userMessage,
        extensions: { orderId: e.details.orderId },
      };
    case "ORDER_INVALID_STATE":
      return {
        type: "https://example.com/problems/order-invalid-state",
        title: "Invalid state",
        status: 409,
        detail: e.userMessage,
        extensions: e.details,
      };
    case "INTERNAL_ERROR":
      return {
        type: "about:blank",
        title: "Internal error",
        status: 500,
        detail: e.userMessage,
      };
  }
}
```

---

## 6️⃣ ライブラリを使う選択肢🥐

![6️⃣ ライブラリを使う選択肢🥐](./picture/ddd_ts_study_088_visual_6.png)


Resultを自作してもOKだけど、実務だと **neverthrow** を使う人も多いよ✨
`match` や `andThen` で「成功のときだけ次へ」をきれいに繋げられる系📦➡️📦 ([GitHub][5])

「学習目的なら自作→慣れたらneverthrow」がおすすめ！🙂

---

## 7️⃣ よくある落とし穴😂⚠️

* **例外とResultを混ぜる**

  * 例：半分throw、半分Result → 呼び出し側が泣く😭
  * ルール：**アプリ層の外へはResultで統一**が安全✨
* **errorCodeが増えるほど運用が雑になる**

  * 似たコード乱立 → 解析できない😇
  * 対策：`code` は「分類（カテゴリ）」に寄せる（細かい差は details）
* **detailsに個人情報を入れちゃう**

  * ログ流出で終わる😱
  * 対策：detailsは「解析に必要最小限」＋マスク方針

---

## 🤖 AIの使いどころテンプレ

![🤖 AIの使いどころテンプレ](./picture/ddd_ts_study_088_visual_7.png)


そのままコピペで使えるよ✨

* 「`AppError` の union を、コード重複が少ない形に整理して。codeは固定、detailsは型安全に」
* 「`ORDER_INVALID_STATE` のテストケースを Given/When/Then で10個出して」
* 「Resultの `map / mapErr / andThen` を初心者にも読める実装で追加して」

---

## ✅ ミニ演習🎓✨

1. `CANNOT_PAY_TWICE` を追加してみよう💳🔁

* 仕様：支払い済みなら二重支払い不可
* やること：`ERROR_CODE` と `AppError` union を拡張
* `payOrder()` でそのエラーに変換して返す

2. `validatePayOrderInput()` の violations に **エラー数**を入れてみよう📊

* `details: { violations, count }` にする
* UIで「エラーが3つあるよ！」って出せる😆

---

## ✅ ゴール🎉

* Result型で「成功/失敗」が型に出て、呼び出し側が迷わない📦✨
* `errorCode / userMessage / details` の3点セットで、UIにも運用にも強い🛠️💖
* 例外はアプリ層で受け止めてResult化、混ぜない！🚪🔁🧯

次の第89章で「ユーザー向け」と「開発者向け」をもっと綺麗に分離して、運用で詰まらない形に仕上げるよ〜👤🛠️✨

[1]: https://www.typescriptlang.org/docs/handbook/unions-and-intersections.html?utm_source=chatgpt.com "Handbook - Unions and Intersection Types"
[2]: https://zod.dev/basics?utm_source=chatgpt.com "Basic usage"
[3]: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-4-9.html?utm_source=chatgpt.com "Documentation - TypeScript 4.9"
[4]: https://www.rfc-editor.org/rfc/rfc9457.html "RFC 9457: Problem Details for HTTP APIs"
[5]: https://github.com/supermacro/neverthrow?utm_source=chatgpt.com "supermacro/neverthrow: Type-Safe Errors for JS & TypeScript"
