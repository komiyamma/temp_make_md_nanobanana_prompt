# 第36章：ブランド型（ID取り違え防止）🏷️

![ブランド型](./picture/tdd_ts_study_036_brand_tag.png)

## 🎯目的

「`string` だから入れ替えても通っちゃう…😱」を **コンパイルで止める** ようにするよ！
`UserId` と `ProductId` を **別の型として扱える** ようにして、取り違え事故を消す🔥

---

## 📚学ぶこと

* 🧠 TypeScriptは「構造的型付け」なので、同じ `string` は基本同じ扱いになりがち\n\n![Structural Typing Risk](./picture/tdd_ts_study_036_structural_typing_risk.png)
* 🏷️ **ブランド型（Branded / Opaque / Nominalっぽくする）**で「意味」を型に乗せる\n\n![Brand Sticker](./picture/tdd_ts_study_036_brand_sticker.png)
* 🛡️ 2つの作り方

  * ① かんたん版：`__brand` を足す（学習しやすい）
  * ② 強つよ版：`unique symbol` を使う（衝突しにくい） ([DEV Community][1])
* 🧪 「型のテスト」＝**動かすテストじゃなくて**、コンパイルで保証する（Vitestでできる） ([Vitest][2])

※ちなみに現時点の最新安定版TypeScriptは GitHub Releases 上で **TypeScript 5.9.3** が “Latest” になってるよ🆕 ([GitHub][3])

---

## 🧪手を動かす（ミニ題材：カートに追加🛒）

「ユーザーID」と「商品ID」を取り違えるとヤバい、を型で止めるよ💥

### 1) まず“事故るコード”を用意する😵‍💫

#### ✅ 事故の構図

* `addToCart(userId: string, productId: string)`
  → 引数を入れ替えてもコンパイルが通る💀

```ts
// src/cart.ts
export function addToCart(userId: string, productId: string) {
  return { userId, productId }
}

// どっちも string だから、入れ替えても通っちゃう…\n\n![Swap Crash](./picture/tdd_ts_study_036_swap_crash.png)
addToCart("prd_001", "usr_001") // 😱
```

ここから「入れ替えたらコンパイルで落ちる」に進化させるよ💪

---

## 🧪🟥→🟩→🧹（TDDっぽく進めるよ）🚦✨

ポイント：今回は **“型の失敗＝Red”** だよ！
Vitest は `*.test-d.ts` を **型テスト**として扱えるよ🧪（実行はしないで、コンパイルチェックだけする） ([Vitest][2])

---

## 2) 🟥 Red：型テストで「入れ替えを禁止したい」を書く✍️

`@ts-expect-error` を使うと、**「ここはエラーになるのが正しい」**が書けるよ🙆‍♀️
（エラーにならなかったら、`@ts-expect-error` が “無駄” って扱いになってテストが落ちる＝Red！）

```ts
// src/ids.test-d.ts
import { addToCart2, UserId, ProductId } from "./ids.js"

// 正しい呼び出しはOKのはず
addToCart2(UserId("usr_001"), ProductId("prd_001"))

// 入れ替えたらコンパイルで落ちてほしい！
// @ts-expect-error - userId と productId を取り違えたらダメ🙅‍♀️\n\n![Compile Shield](./picture/tdd_ts_study_036_compile_shield.png)
addToCart2(ProductId("prd_001"), UserId("usr_001"))
```

この時点では `UserId` / `ProductId` / `addToCart2` が無いので当然落ちるね🟥😆
（もしくは “ただの string なら入れ替えても通る” ので `@ts-expect-error` が無効扱いになって落ちる🟥）

---

## 3) 🟩 Green：ブランド型を作る（かんたん版）🏷️

まずは一番わかりやすい版からいくね☺️
「`string` だけど、`UserId` という印がついた `string`」みたいにする✨

```ts
// src/ids.ts
type Brand<T, Name extends string> = T & { readonly __brand: Name }

export type UserId = Brand<string, "UserId">
export type ProductId = Brand<string, "ProductId">

// 💡 生成関数で “as” を隠す（アプリ側に撒かないのがコツ！）\n\n![Factory Gate](./picture/tdd_ts_study_036_factory_gate.png)
export function UserId(value: string): UserId {
  // ここは軽いチェックでもOK（好みで強化してね）
  if (!value.startsWith("usr_")) throw new Error("UserId must start with usr_")
  return value as UserId
}

export function ProductId(value: string): ProductId {
  if (!value.startsWith("prd_")) throw new Error("ProductId must start with prd_")
  return value as ProductId
}

export function addToCart2(userId: UserId, productId: ProductId) {
  return { userId, productId }
}
```

これで `ids.test-d.ts` の
`addToCart2(ProductId(...), UserId(...))` が **型エラー**になって、`@ts-expect-error` も満たせる＝🟩になるよ🎉

> ブランド型は「意味が違うのに同じ型に見える」を分離する定番パターンだよ🧠 ([Total TypeScript][4])

---

## 4) 🧹 Refactor：強つよ版（unique symbol）も知っておく💪✨

チームや規模が大きいと「同名ブランド」衝突が怖いことがあるのね🫠
その対策として **`unique symbol` をキーにする**やり方があるよ\n\n![Unique Symbol Seal](./picture/tdd_ts_study_036_unique_symbol_seal.png)（より衝突しにくい） ([DEV Community][1])

```ts
// src/ids-unique.ts
declare const userIdBrand: unique symbol
declare const productIdBrand: unique symbol

export type UserId = string & { readonly [userIdBrand]: "UserId" }
export type ProductId = string & { readonly [productIdBrand]: "ProductId" }

export function UserId(value: string): UserId {
  if (!value.startsWith("usr_")) throw new Error("UserId must start with usr_")
  return value as UserId
}

export function ProductId(value: string): ProductId {
  if (!value.startsWith("prd_")) throw new Error("ProductId must start with prd_")
  return value as ProductId
}
```

どっちを使えばいい？🤔

* 👶 学習＆アプリ開発：`__brand` 版でぜんぜんOK🙆‍♀️
* 🏢 ライブラリ化 / 超巨大：`unique symbol` 版が安心寄り🛡️ ([DEV Community][1])

---

## 🧪 型テストをVitestで回す（サクッと）🔁

Vitestは **型テスト**を公式にサポートしてるよ🧪
`*.test-d.ts` は「実行しないで型チェックだけ」って扱いになる✨ ([Vitest][2])
`expectTypeOf` みたいな型アサーションも使えるよ🧠 ([Vitest][5])

「Vitestじゃなくて型テスト専用が良い」なら `tsd` みたいな選択肢もあるよ🧰 ([GitHub][6])

---

## 🤖AIの使いどころ（コピペ用）🤖✨

### ① ブランド化の設計レビュー🧑‍⚖️

```text
UserId と ProductId をブランド型にしたいです。
「as をアプリ側に撒かない」前提で、生成関数の設計案と注意点を3つ出して。
```

### ② “取り違え事故”の洗い出し🔍

```text
このコードで「同じ型に見えるけど意味が違う値」を列挙して。
ID/金額/日付/メール等の取り違え事故になりそうな箇所を指摘して。
```

### ③ 型テストのネタ出し🧪

```text
ブランド型にしたので、@ts-expect-error を使った「間違い呼び出し」テスト例を5個作って。
```

---

## ✅チェックリスト（合格ライン）💮

* ✅ `addToCart2(UserId, ProductId)` は通る
* ✅ `addToCart2(ProductId, UserId)` は **型で落ちる**（＝事故が消える）
* ✅ `as UserId` をアプリのあちこちに書いてない（生成関数に封じ込めた）
* ✅ ブランド型を導入したことで「引数の意味」が読みやすくなった📖✨

---

## ☠️よくある落とし穴（ここだけ注意！）⚠️

* 😈 **`as UserId` をどこでも使い始める** → 型安全が崩壊するので、生成関数へ隔離しよ！\n\n![As Cast Risk](./picture/tdd_ts_study_036_as_cast_risk.png)
* 🫠 IDの形式チェックをゼロにすると「なんでもUserId」になりがち
  → 最低限 `usr_` / `prd_` だけでも守ると事故が激減するよ👍
* 🧩 似た概念もブランド分け推奨：`Email` / `Url` / `Money` / `ISODateString` など✨

---

## 🎀まとめ

ブランド型は「string地獄😵‍💫」を抜ける最初の一歩🏃‍♀️💨
テスト（型テスト）にすると、**“取り違えが起きない設計”**がずっと維持できるよ🧪💕

---

## 次（第37章）チラ見せ👀✨

次は **Result型** で「失敗を仕様にする」🧯
例外を乱用しないで、呼び出し側も含めて安全にできるようになるよ〜！

[1]: https://dev.to/silentwatcher_95/preventing-accidental-interchangeability-in-typescript-branding-the-unique-property-pattern-hda?utm_source=chatgpt.com "typescript - Branding & the Unique Property Pattern"
[2]: https://vitest.dev/guide/testing-types "Testing Types | Guide | Vitest"
[3]: https://github.com/microsoft/typescript/releases "Releases · microsoft/TypeScript · GitHub"
[4]: https://www.totaltypescript.com/workshops/advanced-typescript-patterns/branded-types/what-is-a-branded-type?utm_source=chatgpt.com "What is a Branded Type?"
[5]: https://vitest.dev/api/expect-typeof "expectTypeOf | Vitest"
[6]: https://github.com/tsdjs/tsd?utm_source=chatgpt.com "tsdjs/tsd: Check TypeScript type definitions"
