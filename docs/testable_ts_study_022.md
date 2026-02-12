# 第22章：設定・環境変数を外に押し出す⚙️📦

![testable_ts_study_022_config_card.png](./picture/testable_ts_study_022_config_card.png)

〜「環境が違うと壊れる😱」と「テストがダルい😵‍💫」を卒業する回〜🎓✨

---

## この章のゴール🎯💖* `process.env` を **中心（ロジック）

から消す** 🙅‍♀️🧼


* 設定を **Configとして注入** できるようになる🎁✨
* テストで **Config差し替え** して分岐をサクッと検証✅🧪

---

## 22-1 「設定」って実はI/Oだよね？🌍🚪

環境変数って、アプリの外から入ってくる情報だよね？👀
つまり `process.env` は **外の世界（I/O）** そのもの⚡

* ローカルと本番で値が違う💥
* そもそも環境変数が未設定で `undefined` になる💥
* 数値のはずが文字列で入ってきて事故る💥

だから **中心（ロジック）に直で触らせない** のがコツだよ〜🧁✨

ちなみに最近のNodeは `.env` を **CLIオプションで読み込める** ようになってるよ（`--env-file` / `--env-file-if-exists`）🆕✨ ([Node.js][1])
`.env` サポートは Node 20 で実験的に導入→今は普通に使える流れだよ〜📦 ([Node.js][2])

---

## 22-2 まず「ダメな例」😵‍💫（中心が env を直読み）

たとえば「送料無料ライン」の金額が設定で変わるケース🛒💰



```ts
// ❌ 中心ロジックが process.env を直読みしちゃってる例
export function calcShippingFee(orderTotal: number): number {
  const threshold = Number(process.env.FREE_SHIPPING_THRESHOLD); // 文字列→数値変換もここで…
  if (orderTotal >= threshold) return 0;
  return 500;
}
```

これの困るところ👃💨

* テストのたびに env をいじる必要がある😵
* 未設定だと `Number(undefined)` で `NaN` になって、挙動が謎になる😇
* 「設定の読み方」まで中心に混ざって責務がぐちゃぐちゃ🍝

---

## 22-3 ゴール形：Configを注入する✨

🎁中心はこうなってほしい👇💕



```ts
// ✅ 中心ロジックは「Configを受け取るだけ」
export type AppConfig = {
  freeShippingThreshold: number;
  shippingFee: number;
};

export function calcShippingFee(orderTotal: number, config: AppConfig): number {
  return orderTotal >= config.freeShippingThreshold ? 0 : config.shippingFee;
}
```

これだけで世界が変わる🌈✨

* テストが超ラク（Configを渡すだけ）🧪🎉
* env未設定の事故は「外側」で止められる🛑
* 中心は計算だけに集中できる🧠💎

---

## 22-4 ハンズオン：Configを外側で作って中心に渡す🛠

️✨## ステップ1：Configの「必要最小限」を決める✂️

📜まずは「この機能に必要な設定だけ」を書き出すよ📝
例：

* `FREE_SHIPPING_THRESHOLD`（送料無料ライン）
* `SHIPPING_FEE`（送料）

> ✅ いきなり全部まとめない！
> 必要になったら増やす、が安全だよ〜😊✨

---

## ステップ2：Config Loader（外側）

を作る📦🚪外側の仕事：



* `process.env` を読む👀
* 文字列を数値にする🔁
* 必須チェックする✅
* 変だったら **起動時に落とす**（静かに壊れない）💥

ここでおすすめなのが **スキーマ検証**（例：Zod）🛡️✨
Zodは “型と実行時チェック” をセットでできる人気ライブラリだよ〜。Zod 4が安定版で、最新版も4系で更新が続いてる感じ📈 ([Zod][3])

```ts
// src/infra/config/loadConfig.ts
import { z } from "zod";

const EnvSchema = z.object({
  FREE_SHIPPING_THRESHOLD: z.coerce.number().int().nonnegative(),
  SHIPPING_FEE: z.coerce.number().int().nonnegative(),
});

// ✅ 外側：env を「安全なConfig」に変換する
export type AppConfig = {
  freeShippingThreshold: number;
  shippingFee: number;
};

export function loadConfigFromEnv(env: NodeJS.ProcessEnv): AppConfig {
  const parsed = EnvSchema.parse(env);

  return {
    freeShippingThreshold: parsed.FREE_SHIPPING_THRESHOLD,
    shippingFee: parsed.SHIPPING_FEE,
  };
}
```

ポイント💡😊

* `z.coerce.number()` で `"3000"` みたいな文字列を数値へ🔁
* おかしい値なら **起動時に例外**（早く気づける）🚨

---

## ステップ3：組み立て場所（main）

で注入する🏗️✨中心は env を知らない。外側で config を作って渡すだけ🎁



```ts
// src/main.ts
import { loadConfigFromEnv } from "./infra/config/loadConfig";
import { calcShippingFee } from "./core/calcShippingFee";

const config = loadConfigFromEnv(process.env);

const total = 4200;
const fee = calcShippingFee(total, config);

console.log({ total, fee });
```

---

## 22-5 `.env` をどう読み込む？（今どき選択肢）

🧃📄## 選択肢A：Nodeの `--env-file` を使う（軽い✨

）Nodeの公式ドキュメントでも `.env` を `process.env` に入れられる、と案内されてるよ〜📘 ([Node.js][1])

例（Windowsのターミナルで）👇

```bash
node --env-file=.env dist/main.js
```

* `--env-file` はファイルが無いとエラーになる（見落としにくい）⚠️ ([Node.js][4])
* あるか分からない環境では `--env-file-if-exists` が便利🧸 ([Node.js][1])

## 選択肢B：dotenv を使う（定番✨

）dotenv の最新版は 17系で更新されてるよ📦 ([npm][5])
ただし、ここで超大事なのは👇

> **どっちを使ってもOK**
> でも **中心に env を入れない** のが本題だよ〜🫶✨

---

## 22-6 テスト：Config差し替えで分岐を固定する🧪✅テストランナーは Vitest が最近も活発で、4系が出てるよ〜⚡ ([Vitest][6])



```ts
// src/core/calcShippingFee.test.ts
import { describe, it, expect } from "vitest";
import { calcShippingFee, type AppConfig } from "./calcShippingFee";

describe("calcShippingFee", () => {
  it("送料無料ライン以上なら0円", () => {
    const config: AppConfig = { freeShippingThreshold: 3000, shippingFee: 500 };
    expect(calcShippingFee(3000, config)).toBe(0);
    expect(calcShippingFee(9999, config)).toBe(0);
  });

  it("ライン未満なら送料がかかる", () => {
    const config: AppConfig = { freeShippingThreshold: 3000, shippingFee: 500 };
    expect(calcShippingFee(2999, config)).toBe(500);
  });

  it("送料自体もConfigで変わる", () => {
    const config: AppConfig = { freeShippingThreshold: 3000, shippingFee: 800 };
    expect(calcShippingFee(1000, config)).toBe(800);
  });
});
```

最高ポイント🌟

* env いじりゼロ🙆‍♀️
* テストが速い⚡
* 分岐が読みやすい👀💖

---

## 22-7 よくある落とし穴まとめ🕳️

😱（回避テク）* `Number(process.env.X)` を中心でやる → ❌
  → 外側でスキーマ検証して、中心は型付きConfigだけ✅
* `undefined` を黙って通す → ❌
  → 起動時に落として気づく✅
* Configが巨大化して何でも入る箱になる → ❌
  → 「機能ごとの必要最小限」から増やす✅

---

## 22-8 チェックリスト✅🧸* [ ] 中心コードに `process.env` が出てこない🙆‍♀️


* [ ] Configは “型付き” で渡してる📘
* [ ] 文字列→数値/URLなどの変換は外側でやってる🔁
* [ ] 必須項目が無いと起動時に止まる🛑
* [ ] テストはConfigを直接作って差し替えてる🧪

---

## 22-9 練習問題（3つ）

✍️🎀## 問題1：割引率をConfig化しよう💸✨* `DISCOUNT_RATE`（例：0.1）

を追加して、合計計算に反映


* テストで `0.0 / 0.1 / 0.2` を差し替えて検証🧪

## 問題2：Configの必須チェックを強くしよう🛡

️* `DISCOUNT_RATE` は `0 <= rate <= 0.5` に制限してみてね😊



## 問題3：`--env-file-if-exists` を使う起動コマンドを作ろう🧃* `.env` が無い環境でも動く起動方法にしてみよう✨ ([Node.js][1])

---

## 22-10 AI活用（ここは任せてOK🤖💕）## いい感じの頼み方例📝* 「このenv一覧から、Zodのスキーマを作って。数値はcoerceで、範囲制約も付けて」🧁


* 「この分岐のテストケースをAAAで列挙して、境界値も入れて」🧪

## ダメな丸投げ例🙅‍♀️* 「全部いい感じに設計して」→ 境界が混ざりやすい😵‍💫

---

## まとめ🌈

🎓* `process.env` はI/Oだから **中心に入れない** 🙅‍♀️🚪


* 外側で **Configに変換・検証** して中心へ🎁✨
* テストは **Config差し替え** で秒速になる🧪⚡
* `.env` は Node の `--env-file` でも読み込める時代🆕 ([Node.js][1])

次の第23章は「境界でデータ変換（DTO ↔ Domain）」🔁✨
今回の “Config変換” と同じノリで、「外の形を中心に入れない」練習をもっと強くするよ〜💖💪

[1]: https://nodejs.org/api/environment_variables.html?utm_source=chatgpt.com "Environment Variables | Node.js v25.3.0 Documentation"
[2]: https://nodejs.org/en/learn/command-line/how-to-read-environment-variables-from-nodejs?utm_source=chatgpt.com "How to read environment variables from Node.js"
[3]: https://zod.dev/v4?utm_source=chatgpt.com "Release notes"
[4]: https://nodejs.org/api/cli.html?utm_source=chatgpt.com "Command-line API | Node.js v25.3.0 Documentation"
[5]: https://www.npmjs.com/package/dotenv?utm_source=chatgpt.com "dotenv"
[6]: https://vitest.dev/blog/vitest-4?utm_source=chatgpt.com "Vitest 4.0 is out!"
