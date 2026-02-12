# 第40章：小さな設計ルール（境界を守る）📏

![お城の堀（境界）](./picture/tdd_ts_study_040_castle_moat.png)

## 🎯この章のゴール

この章が終わると…👇

* 「**ドメイン（中心のロジック）**」が **外部（ファイル/HTTP/環境変数/時間）に触らない**ように整理できる🙆‍♀️
* テストが **速い・安定・書きやすい**状態になる🏃‍♀️💨
* 変更（仕様追加やAPI変更）が来ても、壊れる範囲を小さくできる🧯✨

---

## 🧠そもそも「境界」ってなに？🚪

ざっくり言うと、こういう“線引き”だよ👇

* **内側（守る）**：ビジネスルール・計算・判定（＝ドメイン）💎
* **外側（変わりやすい）**：HTTP、DB、ファイル、UI、環境変数、時計、乱数…🌪️

**境界を守る**＝「内側は外側を直接触らない」ってこと！

> こうするとテストがラクになるのが超でかい👏
> 外側って、落ちたり遅かったり、状態でブレたりしがちだからね🥲

---

## 📏小さな設計ルール（これだけ守ればOK）✅✨

難しい言葉は置いといて、まずは **5つだけ**でいこ〜！🥳

### ルール1：ドメインは `fetch` / `fs` / `process.env` / `Date.now()` を直接触らない🙅‍♀️

触りたくなったら「外に追い出す」🏃‍♀️💨

### ルール2：外部と話す窓口は“1か所”に集める🪟

あちこちでAPI呼び出ししない！
「ここが外部だよ」って場所を決めると迷子にならない🧭✨

### ルール3：依存の向きは“内向き”⬅️

ドメイン（内側）→ 外側に依存しない
外側がドメインに合わせる（あとで差し替えられる）🔁

### ルール4：外部は「関数」か「小さいインターフェース」で渡す📦

TypeScriptだとこれが超やりやすい！
「必要な能力だけ」渡すのがコツ💡

### ルール5：テストは“内側の約束”を固定する📌

外部の事情じゃなく、**仕様（計算結果/判定）**をテストする✨

---

## 🧪ミニ演習：境界越えを1つ直してみよ〜！🐣🔧

題材：**会計（Checkout）**で「税率」と「クーポン」を使う💰🎟️
ありがちなダメ例：ドメインが外部を直触りしちゃうやつ🥲

---

## 🚫ダメな実装（境界がぐちゃぐちゃ）例

「計算」なのに、環境変数や外部データに触ってる…😵‍💫

```ts
// src/checkoutBad.ts
export function calcTotalBad(subtotal: number, couponCode?: string) {
  const taxRate = Number(process.env.TAX_RATE ?? "0.1"); // 外部① env
  const couponsJson = process.env.COUPONS_JSON ?? "[]";  // 外部② env
  const coupons = JSON.parse(couponsJson) as Array<{ code: string; off: number }>;

  const coupon = coupons.find(c => c.code === couponCode);
  const discounted = coupon ? Math.max(0, subtotal - coupon.off) : subtotal;

  return Math.floor(discounted * (1 + taxRate));
}
```

これ、テストがつらいポイント👇

* `process.env` の設定が必要（忘れると落ちる）😇
* 実行環境の差でブレる😵
* ドメインが“外側”を知りすぎてる（変更に弱い）💥

---

## ✅良い形に直す（境界を守る）✨

作戦はシンプル！

* **ドメイン：純粋な計算**だけにする🧠
* 税率/クーポン取得は **外側**に追い出す🏃‍♀️💨
* ドメインには「必要な情報だけ」渡す📦

---

## 🗂️ファイル構成（最小）

```txt
src/
  domain/
    checkout.ts
  ports/
    couponRepository.ts
    taxRateProvider.ts
  app/
    checkoutService.ts
test/
  checkout.test.ts
```

---

## 1) ドメイン（内側）— 計算だけする💎

```ts
// src/domain/checkout.ts
export type Coupon = { code: string; off: number };

export function calcTotal(subtotal: number, taxRate: number, coupon?: Coupon): number {
  const discounted = coupon ? Math.max(0, subtotal - coupon.off) : subtotal;
  return Math.floor(discounted * (1 + taxRate));
}
```

ポイント👉

* `process.env` も `fetch` も無し！🥳
* つまり **テストが爆速＆安定**になる💨✨

---

## 2) ポート（内側に置く“要求仕様”）📮

「クーポン取ってきて〜」「税率ちょうだい〜」を **型で宣言**するだけ！

```ts
// src/ports/couponRepository.ts
import type { Coupon } from "../domain/checkout";

export type CouponRepository = {
  findByCode(code: string): Promise<Coupon | undefined>;
};
```

```ts
// src/ports/taxRateProvider.ts
export type TaxRateProvider = () => number;
```

---

## 3) アプリ層（外側寄り）— 依存をまとめて扱う📦

```ts
// src/app/checkoutService.ts
import { calcTotal, type Coupon } from "../domain/checkout";
import type { CouponRepository } from "../ports/couponRepository";
import type { TaxRateProvider } from "../ports/taxRateProvider";

export class CheckoutService {
  constructor(
    private readonly deps: {
      couponRepo: CouponRepository;
      taxRate: TaxRateProvider;
    }
  ) {}

  async total(subtotal: number, couponCode?: string): Promise<number> {
    const taxRate = this.deps.taxRate();

    let coupon: Coupon | undefined;
    if (couponCode) {
      coupon = await this.deps.couponRepo.findByCode(couponCode);
    }

    return calcTotal(subtotal, taxRate, coupon);
  }
}
```

ここが“境界の玄関”🚪✨

* ドメインは `calcTotal` で純粋
* 外部取得は `deps` 経由（差し替え可能）🔁

---

## 🧪テスト（Vitest）— 外部なしで安定！⚡️

テストでは **スタブ**や **スパイ**で差し替えるだけ🙆‍♀️
（モック/スパイを使う時は、状態が残らないようにクリア/リストアが大事だよ〜🧼✨）([Vitest][1])

```ts
// test/checkout.test.ts
import { describe, it, expect, vi } from "vitest";
import { CheckoutService } from "../src/app/checkoutService";

describe("CheckoutService（境界を守る版）", () => {
  it("クーポンなし：税だけ乗る", async () => {
    const service = new CheckoutService({
      taxRate: () => 0.1,
      couponRepo: {
        findByCode: async () => undefined,
      },
    });

    await expect(service.total(1000)).resolves.toBe(1100);
  });

  it("クーポンあり：割引してから税", async () => {
    const service = new CheckoutService({
      taxRate: () => 0.1,
      couponRepo: {
        findByCode: async (code) => (code === "OFF200" ? { code, off: 200 } : undefined),
      },
    });

    await expect(service.total(1000, "OFF200")).resolves.toBe(880); // (1000-200)*1.1=880
  });

  it("クーポン取得が呼ばれたことも確認できる（スパイ）", async () => {
    const findByCode = vi.fn(async (code: string) =>
      code === "OFF200" ? { code, off: 200 } : undefined
    );

    const service = new CheckoutService({
      taxRate: () => 0.1,
      couponRepo: { findByCode },
    });

    await service.total(1000, "OFF200");

    expect(findByCode).toHaveBeenCalledWith("OFF200");
    expect(findByCode).toHaveBeenCalledTimes(1);
  });
});
```

---

## 🌟この形が“2026でも強い”理由（最新動向もちら見せ）👀✨

* **Node.jsはLTSが継続更新**されるので、セキュリティ更新や挙動差分が普通に来るよね🛡️（例：2026-01-13 の Node.js 24.13.0 LTS など）([nodejs.org][2])
* **TypeScriptも最新版（npm: 5.9.3）**でモジュール解決や周辺の“現実寄り”が進んでるから、外部境界を薄くするのが効く〜！🧩([NPM][3])
* **Vitestも最新（npm: 4.0.17）**でどんどん進化中。だから「外部を差し替えやすい設計」はテスト基盤の変化にも強い💪([NPM][4])

---

## 🤖AI（Copilot/Codex）に頼むなら：使えるプロンプト例💬✨

そのまま貼ってOKだよ〜！🫶

* 「この関数、`process.env` を直接触ってる。**ドメイン層が外部に依存しない**形にリファクタして。`TaxRateProvider` と `CouponRepository` を作って差し込む案にして」
* 「Vitestで、**外部なし**で `CheckoutService.total()` をテストしたい。スタブ版 `couponRepo` を使って3ケース作って（クーポンなし/あり/未登録）」
* 「テストがフレークしないように、モック状態が残らない注意点も一言添えて」

---

## 🚧よくあるミス（かわいい顔して地雷）💣🥹

* **全部インターフェースにしすぎる**
  → まずは「外部だけ」！ドメイン内部は素直でOK🙆‍♀️
* **ドメインに `Date` や `Math.random()` が残る**
  → それも外部だよ〜！⏰🎲（次パートで効いてくる）
* **アプリ層が太りすぎる**
  → “外部を集める”だけにして、判断はなるべくドメインへ💎

---

## ✅チェックリスト（合格ライン）🎓✨

* [ ] ドメイン関数が `fetch/fs/process.env/Date.now` を触ってない🙅‍♀️
* [ ] 外部は `TaxRateProvider` / `CouponRepository` みたいに“渡してる”📦
* [ ] テストが外部なしで動く（env不要）⚡️
* [ ] 仕様（計算結果）がテストに書いてある📌
* [ ] 依存の向きが内向き（ドメインが外側を知らない）⬅️✨

---

## 🎀まとめ

境界を守るって、難しい設計論じゃなくて **“外部を触りたくなったら追い出す”**だけでだいぶ勝てるよ〜！🥳✨
この章の形ができると、次の「依存を切る（DI/スタブ/モック）」がめっちゃ気持ちよく進む💨🧪

---

必要なら、この章の演習を「あなたの既存コード（1ファイル）」に当てはめて、**どこが境界越えか赤ペン添削**みたいに一緒に直すこともできるよ〜🖍️💕

[1]: https://vitest.dev/guide/mocking?utm_source=chatgpt.com "Mocking | Guide"
[2]: https://nodejs.org/en/blog/release/v24.13.0?utm_source=chatgpt.com "Node.js 24.13.0 (LTS)"
[3]: https://www.npmjs.com/package/typescript?utm_source=chatgpt.com "TypeScript"
[4]: https://www.npmjs.com/package/vitest?utm_source=chatgpt.com "vitest"
