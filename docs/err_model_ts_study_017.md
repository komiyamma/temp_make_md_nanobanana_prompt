# 第17章：Result型の考え方（TSはユニオンが強い）🎁🌈

ここから一気に「例外（throw）に頼りすぎない設計」に入っていくよ〜！😊✨
TypeScriptは **判別可能ユニオン（discriminated union）** が超強いので、Result型がめちゃ相性いいのです💪🌈 ([TypeScript][1])

ちなみに本日時点（2026/01）で TypeScript のnpm最新は **5.9.3** だよ🆕✨（今後も上がっていくけど、Resultの考え方はずっと使える🫶） ([npm][2])
（あと、TypeScript 7 の大型アップデート計画も進んでるよ〜🚀） ([Microsoft for Developers][3])

---

## 1) Result型ってなに？（一言で）🎯

**成功 or 失敗を「戻り値で」表す** 型だよ😊

![Result型：成功（Ok）と失敗（Err）の箱[(./picture/err_model_ts_study_017_ok_err_boxes.png)
throwしないで、

* 成功なら ✅ Ok（値が入ってる）
* 失敗なら ❌ Err（エラー情報が入ってる）

…って返すやつ🎁✨

---

## 2) なんでResultにすると嬉しいの？💡✨

### ✅ try/catchより「見落としにくい」👀

throwって、呼び出し側が **try/catch書き忘れる** と事故るよね😇💥
Resultだと「戻り値がResult」なので、呼び出し側が **分岐を書かないと先に進めない** 形にしやすいよ🧠✨

### ✅ “想定内の失敗”が設計に乗る🚋

入力ミス、在庫なし、期限切れ…みたいな「よく起きる失敗」は、例外じゃなくて **仕様の分岐** として扱うほうが読みやすい💗🙂

### ✅ TypeScriptはユニオンで分岐が気持ちいい🌈

`if (result.ok)` でスッ…と型が絞り込まれるのがTSの得意技だよ✨ ([TypeScript][1])

---

## 3) まずは最小のResult型を作ろう（Ok/Errだけ）🧩✨

ここでは「2分岐だけ」に絞るよ！（便利ヘルパーは次章でモリモリやる🪄🙂）

```ts
// result.ts
export type Ok<T> = {
  ok: true;
  value: T;
};

export type Err<E> = {
  ok: false;
  error: E;
};

export type Result<T, E> = Ok<T> | Err<E>;

export const ok = <T>(value: T): Ok<T> => ({ ok: true, value });
export const err = <E>(error: E): Err<E> => ({ ok: false, error });
```

### 使う側はこう！😊

```ts
import { Result, ok, err } from "./result";

type DivideError =
  | { type: "ZeroDivision"; message: string }
  | { type: "NotANumber"; message: string };

export function safeDivide(a: number, b: number): Result<number, DivideError> {
  if (Number.isNaN(a) || Number.isNaN(b)) {
    return err({ type: "NotANumber", message: "数じゃないよ〜😵" });
  }
  if (b === 0) {
    return err({ type: "ZeroDivision", message: "0では割れないよ〜🫠" });
  }
  return ok(a / b);
}
```

呼ぶ側👇

```ts
const r = safeDivide(10, 0);

if (r.ok) {
  console.log("結果:", r.value);
} else {
  // ここは error が型で守られる✨
  console.log("失敗:", r.error.type, r.error.message);
}
```

---

## 4) 「例外」じゃなくて「Result」にすべき境界（判断ルール）🧭✨

迷ったらこのルールでOKだよ😊🌸

### Resultで返す（＝仕様として起きる）✅

* ユーザー入力ミス（バリデーション）📝
* 業務ルール違反（在庫なし、期限切れ）🏷️
* 外部I/O失敗で“起こりうる”もの（通信失敗、タイムアウト）🌩️
  → ただし「どこでResult化するか」は設計（例外境界）で決めるよ🚪✨

### 例外（throw）に寄せる（＝バグ/不変条件違反）⚡

* 「ここに来たらおかしい」状態（不変条件違反）🧱
* 型の想定が崩れた（nullのはずがないのにnull）😇
* プログラムの誤りを早く気づきたい（Fail Fast）💥

---

## 5) エラー型は「分類」と相性バツグン🧠🏷️

Resultの `E`（エラー側）に、前の章までの分類をそのまま入れられるよ✨

例：

* DomainError（想定内）💗
* InfraError（外部I/O）🔌
* BugError（不変条件）⚡

```ts
type DomainError =
  | { kind: "Domain"; code: "EmailInvalid"; message: string }
  | { kind: "Domain"; code: "BudgetExceeded"; message: string };

type InfraError =
  | { kind: "Infra"; code: "Network"; message: string; retryable: true }
  | { kind: "Infra"; code: "Timeout"; message: string; retryable: true }
  | { kind: "Infra"; code: "UnexpectedResponse"; message: string; retryable: false };

type BugError = { kind: "Bug"; message: string; detail?: unknown };

type AppError = DomainError | InfraError | BugError;
```

こうすると呼び出し側で `kind` で分岐できて、表示やログ方針が揃うよ🪞✨（TSの判別可能ユニオンが効く！） ([TypeScript][4])

---

## 6) Result設計でありがちな罠3つ😵‍💫🧨

### 罠①：Resultなのに結局throwしちゃう💥

* 「この関数はResult返す」なら **基本はthrow禁止**（バグ系だけ例外）
* throwが混ざると、呼び出し側が地獄になるよ😇

### 罠②：`null` / `undefined` で失敗を表現しちゃう🫥

* 「なんで失敗したか」が消える…！
* Resultならエラー情報が残せる📌

### 罠③：エラーが `string` だけ😇

* 後から分類できない
* UI文言・ログ詳細・推奨アクションが分離できない
  → **最低でも code/kind は持とう**🏷️✨

---

## 7) ミニ演習📝✨（Ok/Errの2分岐だけでOK）

### 演習A：入力チェックをResultで返す🧁

1. `parsePrice(input: string): Result<number, DomainError>` を作る
2. 失敗条件：空、数字じゃない、0以下
3. 成功なら `number` を返す

### 演習B：呼び出し側でUI文言を決める🎀

* `if (r.ok)` / `else` の2分岐で
* 失敗なら `error.code` で表示文言を分ける💬

### 演習C：InfraErrorの `retryable` を使う🔁

* `retryable: true` のときだけ「再試行ボタン」を出す…みたいな分岐を書いてみてね😊

---

## 8) AI活用🤖✨（Copilot / Codexで爆速にするやつ）

### そのまま使えるプロンプト例💌

* 「TypeScriptでResult型（ok:true/value と ok:false/error）の最小実装を書いて。ジェネリクス付きで」
* 「この関数を throw じゃなく Result で返す形にリファクタして。DomainError/InfraErrorの2系統にして」
* 「Resultを受け取る呼び出し側の分岐を、読みやすく整理して（ネストを増やさない範囲で）」
* 「このエラー型の命名案を10個出して。初心者にも分かりやすい日本語寄りのmessageも」

### AIの出力をチェックする観点✅

* `E` が `string` だけになってない？😇
* 成功/失敗のどちらも必要な情報が入ってる？📦
* throwが混ざってない？（混ざるなら境界で統一）🚪

---

## 9) まとめ🎀✨

* Result型は「成功/失敗を戻り値で表す」🎁
* TypeScriptは判別可能ユニオンが強いのでResultと相性最高🌈 ([TypeScript][1])
* まずは **Ok/Errの2分岐だけ** をちゃんと回せるようになれば勝ち😊🏆
* 次章で、`map / andThen` みたいな「分岐地獄を防ぐ小技🪄」を入れていくよ〜🙂✨

---

次は第18章で「Resultを気持ちよく合成する」方向に進むよ！⛓️🪄

[1]: https://www.typescriptlang.org/docs/handbook/2/narrowing.html?utm_source=chatgpt.com "Documentation - Narrowing"
[2]: https://www.npmjs.com/package/typescript?utm_source=chatgpt.com "typescript"
[3]: https://devblogs.microsoft.com/typescript/progress-on-typescript-7-december-2025/?utm_source=chatgpt.com "Progress on TypeScript 7 - December 2025"
[4]: https://www.typescriptlang.org/docs/handbook/unions-and-intersections.html?utm_source=chatgpt.com "Handbook - Unions and Intersection Types"
