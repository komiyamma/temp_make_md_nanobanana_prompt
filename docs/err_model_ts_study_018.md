# 第18章：Resultの使い勝手を上げる（ヘルパー）🪄🙂

Result型を入れたのに、こんな気持ちになってない？🥺
「成功/失敗が見えるのは最高！…でも `if (isErr)` が増えてコードが長い〜！😭」

この章は、そのモヤモヤを解決する章だよ💪🌸
**Resultを“いい感じに変換＆合成＆最後に取り出す”ためのヘルパー（map / mapErr / andThen / match など）**を作って、**ネストと分岐をスッキリ**させるよ〜🧹✨

---

## 0. この章でできるようになること🎯💖

* Resultを **変換**できる：`map` ✅
* エラーだけを **変換**できる：`mapErr` ✅
* 失敗するかもな処理を **つなげる**：`andThen` ✅
* 最後に読みやすく **分岐して取り出す**：`match` ✅
* “うっかりthrow”を **Resultに閉じ込める**：`tryCatch` ✅
* 3段階の処理を Result でつないで **ネストしない**コードにできる⛓️✨

---

## 1. まず、ヘルパーの役割を3つに分けるね🧠🗂️

Resultヘルパーはだいたいこの3カテゴリに分かれるよ〜👇

1. **変換（中身を加工）**🍳

* `map`：Okのvalueだけ変換
* `mapErr`：Errのerrorだけ変換

2. **合成（処理をつなぐ）**⛓️

* `andThen`：次の処理もResultを返すときに使う（ネスト防止✨）

3. **消費（最後に取り出す）**📦➡️🎁

* `match`：Ok/Errをきれいに分岐
* `unwrapOr`：失敗ならデフォ値で救う

（＋おまけ）

* `tap / tapErr`：ログとか副作用だけ挟む🪵
* `tryCatch`：throwをResultに変換🧯

実は、人気の Result ライブラリ **neverthrow** もこの系統のメソッドを揃えてるよ（`map / mapErr / unwrapOr / andThen / match` など）🧰✨  ([GitHub][1])

---

## 2. “最小で強い” Result ヘルパーを作ろう🧰✨

![result_toolbox](./picture/err_model_ts_study_018_result_toolbox.png)

ここでは **依存なし**で学習できるように、自分たちの `result.ts` を用意するよ🙂
（あとで本番では neverthrow 等に置き換えてもOK🙆‍♀️）

![Resultヘルパーの道具箱[(./picture/err_model_ts_study_018_helper_toolbox.png)

### 2-1. Result型（復習）📦

```ts
// result.ts
export type Ok<T> = { ok: true; value: T };
export type Err<E> = { ok: false; error: E };
export type Result<T, E> = Ok<T> | Err<E>;

export const ok = <T>(value: T): Ok<T> => ({ ok: true, value });
export const err = <E>(error: E): Err<E> => ({ ok: false, error });

export const isOk = <T, E>(r: Result<T, E>): r is Ok<T> => r.ok;
export const isErr = <T, E>(r: Result<T, E>): r is Err<E> => !r.ok;
```

---

## 3. map：Okのときだけ value を変換する🍳✨

![map_transformation](./picture/err_model_ts_study_018_map_transformation.png)

### 3-1. 何が嬉しいの？🥰

* `if (isOk)` を毎回書かなくてよくなる
* “成功したときの変換だけ” を安全に書ける

```ts
export const map =
  <T, U>(f: (value: T) => U) =>
  <E>(r: Result<T, E>): Result<U, E> =>
    isOk(r) ? ok(f(r.value)) : r;
```

### 3-2. 例：数値を文字列にする🧁

```ts
const r1: Result<number, string> = ok(3);

const r2 = map((n: number) => `合計は ${n} 円だよ✨`)(r1);
// -> Ok("合計は 3 円だよ✨")
```

---

## 4. mapErr：Errのときだけ error を変換する🧯✨

![map_err_polish](./picture/err_model_ts_study_018_map_err_polish.png)

### 4-1. どこで使うの？🧐

* エラー型を **統一**したい（例：DomainError → AppError）
* 文脈を足したい（例：`"支払い処理で失敗"` を付与）

```ts
export const mapErr =
  <E, F>(f: (error: E) => F) =>
  <T>(r: Result<T, E>): Result<T, F> =>
    isErr(r) ? err(f(r.error)) : r;
```

### 4-2. 例：エラーメッセージを丁寧にする💬🌸

```ts
type RawError = { message: string };
type FriendlyError = { userMessage: string };

const toFriendly = (e: RawError): FriendlyError => ({
  userMessage: `ごめんね、うまくいかなかった🥺（${e.message}）`,
});

const r1: Result<number, RawError> = err({ message: "在庫がありません" });
const r2 = mapErr(toFriendly)(r1);
// -> Err({ userMessage: "ごめんね、うまくいかなかった🥺（在庫がありません）" })
```

---

## 5. andThen：Resultを返す処理をつなぐ（最重要）⛓️🔥

![and_then_chain](./picture/err_model_ts_study_018_and_then_chain.png)

### 5-1. map と andThen の違い（ここ超大事！）⚡

* `map`：**普通の値**を返す変換（失敗しない前提の加工）
* `andThen`：**Resultを返す**変換（次の処理でも失敗しうる）

```ts
export const andThen =
  <T, E, U>(f: (value: T) => Result<U, E>) =>
  (r: Result<T, E>): Result<U, E> =>
    isOk(r) ? f(r.value) : r;
```

### 5-2. “mapでResultを返す”とどうなる？😱（ネスト地獄）

```ts
const bad = map((n: number) => ok(n + 1))(ok(1));
// Result<Result<number, E>, E> みたいになりがち😵‍💫
```

### 5-3. andThenで解決！✨

```ts
const good = andThen((n: number) => ok(n + 1))(ok(1));
// Result<number, E> のまま🥰
```

---

## 6. match：最後に“読みやすく”取り出す🎀📦

![match_merge](./picture/err_model_ts_study_018_match_merge.png)

`if (isErr) return ...` を最後に散らさないために、**出口で match** するのが気持ちいいよ🙂✨

```ts
export const match =
  <T, E, R>(onOk: (value: T) => R, onErr: (error: E) => R) =>
  (r: Result<T, E>): R =>
    isOk(r) ? onOk(r.value) : onErr(r.error);
```

---

## 7. unwrapOr：失敗ならデフォ値で救う🛟🙂

![unwrap_parachute](./picture/err_model_ts_study_018_unwrap_parachute.png)

「失敗したらとりあえず 0 で続けたい」みたいな時に使うよ（乱用は注意⚠️）

```ts
export const unwrapOr =
  <T>(fallback: T) =>
  <E>(r: Result<T, E>): T =>
    isOk(r) ? r.value : fallback;
```

---

## 8. tryCatch：throw を Result に閉じ込める🧯🧼

現実はライブラリが throw することあるよね😭
だから「throwする関数」を **Resultに変換**できると便利！

```ts
export const tryCatch = <T, E>(
  f: () => T,
  onThrow: (cause: unknown) => E
): Result<T, E> => {
  try {
    return ok(f());
  } catch (cause) {
    return err(onThrow(cause));
  }
};
```

---

## 9. 3段階処理を Result でつなぐ（ミニ演習）⛓️📝✨

![pipeline_factory](./picture/err_model_ts_study_018_pipeline_factory.png)

題材：**「入力された予算（文字列）→ 数値化 → 上限チェック → 表示用フォーマット」**💖

### 9-1. エラー型（例）🏷️

```ts
type DomainError =
  | { type: "InvalidNumber"; input: string }
  | { type: "OverLimit"; limit: number; actual: number };
```

### 9-2. 3ステップ関数を作る🧩

```ts
import { Result, ok, err } from "./result";

const parseBudget = (input: string): Result<number, DomainError> => {
  const n = Number(input);
  return Number.isFinite(n)
    ? ok(n)
    : err({ type: "InvalidNumber", input });
};

const ensureWithinLimit =
  (limit: number) =>
  (n: number): Result<number, DomainError> =>
    n <= limit ? ok(n) : err({ type: "OverLimit", limit, actual: n });

const formatYen = (n: number): string => `${n.toLocaleString()}円`;
```

### 9-3. ヘルパーで“ネストなし”につなぐ💫

```ts
import { andThen, map, match } from "./result-helpers"; // さっき作ったやつ

const limit = 10000;

const result = andThen(ensureWithinLimit(limit))(
  parseBudget("12000")
);

const message = match(
  (n) => `OKだよ〜🙆‍♀️ 予算は ${formatYen(n)} だね✨`,
  (e) => {
    if (e.type === "InvalidNumber") return `数字で入れてね🥺（入力: ${e.input}）`;
    return `ごめんね、上限は ${formatYen(e.limit)} までだよ😭（入力: ${formatYen(e.actual)}）`;
  }
)(result);

console.log(message);
```

### ✅ ミニ演習（やってみてね）📝💖

1. 入力を `"9999"` に変えて、成功メッセージを確認😊
2. `map(formatYen)` を足して、表示用文字列への変換をパイプっぽくしてみる✨
3. `mapErr` を使って、エラー文言の生成を **1か所に寄せる**（おすすめ！）🎀

---

## 10. AI活用テンプレ🤖💞（レビュー役にして強くなる！）

### 🧑‍⚖️ 読みやすさレビュー

* 「この Result チェーン、読みやすくするリファクタ案を3つ出して。`map` と `andThen` の使い分けも指摘して」

### 🧪 テスト作成

* 「`map/mapErr/andThen/match/tryCatch` の最小テストケースを vitest で作って。境界値も入れて」

### 🧹 エラーメッセージ整形

* 「DomainError を受け取って、ユーザー向け文言を統一トーンで返す関数を作って。優しい言い回し多めで」

---

## 11. 実務での選択肢：ライブラリを使うのも全然アリ🧰✨

学習で仕組みを理解したら、実務は **neverthrow** みたいな実績ある実装に寄せるのもアリだよ🙆‍♀️
`Result` と `ResultAsync(Promise<Result>)` を持ってて、`map / mapErr / unwrapOr / andThen / match` など揃ってる🪄  ([GitHub][1])
（`unwrap` 事故を減らす eslint プラグイン推しもしてるよ）([GitHub][1])

---

## 12. まとめ：迷ったらこの早見でOK🧠✨

* `map`：Okの値を変換（関数が Result を返さない）🍳
* `andThen`：次の処理が Result を返す時に使う（ネスト回避）⛓️
* `mapErr`：Errだけ変換（エラー統一・文脈付け）🧯
* `match`：出口で分岐して取り出す（UI/API変換の手前で便利）🎀
* `tryCatch`：throw を Result に閉じ込める🧯🧼

次の章（第19章）では、この考え方を **Promise<Result>（AsyncResult）** に広げて、非同期でも崩れない形にするよ〜⚡🎁✨

[1]: https://github.com/supermacro/neverthrow "GitHub - supermacro/neverthrow: Type-Safe Errors for JS & TypeScript"
