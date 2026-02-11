# 第82章：Specification入門：条件をオブジェクト化🔎📄

今日は「条件（ルール）」を**コードの文章**みたいに読める形にする練習だよ〜😊✨
ifが増えてきても、設計がぐちゃぐちゃになりにくくなる“武器”です🛡️

---

## 今日のゴール🎯✨

* 「Specificationって何者？」を**一言で説明**できるようになる💬
* ifの条件を、**名前つきオブジェクト**にして取り出せるようになる📦
* **単体テストが超簡単**になるのを体感する🧪💕

---

## まず、if地獄ってどんな感じ？😂🔥

割引やキャンペーンが増えると、こうなりがち…👇

```ts
// どこかのUseCaseやServiceで…
if (
  order.status === "Confirmed" &&
  order.customerType === "Student" &&
  order.totalYen >= 500 &&
  !order.isExpired() &&
  !order.hasCouponConflict()
) {
  // 割引OK
}
```

これ、今は読めるけどね…
**条件が増えるほど「読むのがつらい」「再利用できない」「テストしにくい」**が一気に来ます😵‍💫💦

---

## Specificationってなに？（一言）💡

**「この条件を満たしてる？」を判定する“条件専用オブジェクト”**だよ✅

* 入力：ドメインの何か（例：Order）
* 出力：true / false
* 目的：条件に**名前**をつけて、**再利用**できて、**テスト**しやすくする🎉

---

## なんで嬉しいの？😍✨（効き目）

### 1) 条件が“文章”になる📖

`isSatisfiedBy` って形にすると、読む人が楽🫶

* `canApplyStudentDiscount.isSatisfiedBy(order)`

  * →「学生割引できる？」ってそのまま読める✨

### 2) 条件が使い回せる🔁

同じ条件を、**別ユースケース**でも使える💪
「支払いできる？」「キャンセルできる？」みたいな判定で超便利！

### 3) テストが“条件だけ”でできる🧪

Order全部の流れを再現しなくても、**判定だけ**テストできるから速い⚡

---

## 2026年2月7日時点の“最新寄り”メモ📝✨（安心のため）

* TypeScript の最新安定版は **5.9.3**（npmのlatest）だよ📌 ([NPM][1])
* TypeScript 6.0 は、**2026-02-10にBeta、2026-03-17にFinal予定**として計画が公開されてるよ📅 ([GitHub][2])
* Node.js は **v24 が Active LTS**（安定運用向き）で、v25 は Current（最新系列）だよ🟢 ([nodejs.org][3])
* テストは **Vitest 4 系**が安定（4.0.18 が latest stable 表示）で、4.1 betaも進行中🧪 ([vitest.dev][4])
* Jest は **30.0 が stable**として案内されてるよ🧪 ([jestjs.io][5])

（ここからのコードは、TypeScript 5.9系で普通に書ける範囲にしてあるよ👌）

---

## Specificationの基本形（最小）🧩

まずは「型」を作るよ〜！💕

```ts
// domain/specification/Specification.ts
export interface Specification<T> {
  isSatisfiedBy(candidate: T): boolean;
}
```

たったこれだけでOK✨
**Specificationは“判定だけ”**にして、副作用（DB保存とかログ出力とか）はしないのがコツだよ🙅‍♀️💥

---

## 例題：学生割引を“使えるか？”をSpecificationにする🎓🏷️✨

### 仕様（ゆるGiven/When/Then）📝

* **Given**：注文が「確定済み（Confirmed）」で、合計が500円以上
* **When**：学生のお客さんが割引を使いたい
* **Then**：割引OK（true）

> ここでは「条件をオブジェクト化」するのが目的だから、条件はあえてシンプルにするよ😊
> （複合条件の合成は次章で本格的にやる✨）

---

## まず、Order側に“必要な情報”がある想定☕🧾

（すでにOrder集約がある前提で、最低限こんな感じのプロパティがあるイメージね👇）

```ts
export type OrderStatus = "Draft" | "Confirmed" | "Paid" | "Fulfilled" | "Cancelled";
export type CustomerType = "Guest" | "Student";

export class Order {
  constructor(
    public readonly status: OrderStatus,
    public readonly customerType: CustomerType,
    public readonly totalYen: number,
  ) {}
}
```

---

## Specification実装：CanApplyStudentDiscountSpec 🎓✅

```ts
// domain/specification/CanApplyStudentDiscountSpec.ts
import { Specification } from "./Specification";
import { Order } from "../order/Order";

export class CanApplyStudentDiscountSpec implements Specification<Order> {
  isSatisfiedBy(order: Order): boolean {
    return (
      order.status === "Confirmed" &&
      order.customerType === "Student" &&
      order.totalYen >= 500
    );
  }
}
```

これで、呼び出し側はこうなるよ👇（読みやすい〜😍）

```ts
const spec = new CanApplyStudentDiscountSpec();

if (spec.isSatisfiedBy(order)) {
  // 割引OK
} else {
  // 割引NG
}
```

---

## 「どこで使うのがいいの？」📍✨（超大事）

### パターンA：ユースケース側で使う（よくある）

* UI入力や流れの中で「割引使える？」をチェックしたい時

### パターンB：ドメイン（Orderのメソッド内）で使う

* 「割引を適用する」みたいな操作が**Orderの責務**なら、Order内で守ってもOK
* ただし、Specificationを使うなら「条件の名前」が残って読みやすいのがメリット💕

どっちでもいいけど、初心者のうちはこう覚えると迷いにくいよ👇

* **“条件があちこちで再利用されそう” → Specificationにする**
* **“その1か所だけで完結” → まずは普通にifでもOK**
  （でも将来増えそうなら早めにSpecificationにしておくと安心✨）

---

## テスト：Specificationは“単体テストが神”🧪✨

Vitestで例を作るね（Jestでもほぼ同じ書き味だよ）🫶 ([vitest.dev][4])

```ts
// domain/specification/CanApplyStudentDiscountSpec.test.ts
import { describe, it, expect } from "vitest";
import { CanApplyStudentDiscountSpec } from "./CanApplyStudentDiscountSpec";
import { Order } from "../order/Order";

describe("CanApplyStudentDiscountSpec", () => {
  it("Confirmed + Student + total>=500 なら true", () => {
    const order = new Order("Confirmed", "Student", 500);
    const spec = new CanApplyStudentDiscountSpec();

    expect(spec.isSatisfiedBy(order)).toBe(true);
  });

  it("StudentでもDraftなら false", () => {
    const order = new Order("Draft", "Student", 999);
    const spec = new CanApplyStudentDiscountSpec();

    expect(spec.isSatisfiedBy(order)).toBe(false);
  });

  it("Confirmedでも合計が足りないなら false", () => {
    const order = new Order("Confirmed", "Student", 499);
    const spec = new CanApplyStudentDiscountSpec();

    expect(spec.isSatisfiedBy(order)).toBe(false);
  });
});
```

**ポイント**💡

* テストが「条件の説明」みたいになってるのが最高😍
* Orderの保存とか、UseCaseの流れとか、やらなくていい！ラク！🎉

---

## ありがちミス集⚠️😂（先に潰す！）

### ❌ ミス1：Specificationの中で状態変更しちゃう

* Specificationは **判定だけ**✨
* 変更したくなったら、それは多分「Policy」か「ドメイン操作」だよ🚦

### ❌ ミス2：DB問い合わせを混ぜちゃう

* “判定”が「外部」依存になると、テストが地獄に戻る😇
* まずは **純粋関数っぽい判定**を守るのが安全🛡️

### ❌ ミス3：名前がふわっとしてる

* `OrderSpec1` とかは未来の自分が泣く😭
* **「文章にできる名前」**が正義✨

  * 例：`CanApplyStudentDiscountSpec` / `IsPayableOrderSpec`

---

## AIの使いどころ🤖✨（今日のおすすめ）

### 1) “条件→名前”を作ってもらう

* 条件を書いて、「自然な英語名3つちょうだい」って頼むと便利👍

### 2) テストケースの抜けを洗う

* 「この条件で落とし穴ある？」って聞くと、境界値を提案してくれる🧠✨

### 使えるプロンプト例💬

```text
Orderに対する判定条件があります。
条件: statusがConfirmed、customerTypeがStudent、totalYenが500以上。
この条件のSpecification名を英語で3案。さらにVitestのテストケース（正常系/異常系）を5つ提案して。
```

---

## 章末ミニ課題🎒✨

### 課題A（やさしめ）😊

「支払いできる？」を判定するSpecificationを作ってみて✨
例：`status === "Confirmed"` のときだけOK、みたいにシンプルでOK！

### 課題B（ちょい実務寄り）🔥

「キャンセルできる？」を判定してみて✨
例：`Paid` になってたらキャンセル不可、みたいなルールね🚫

---

## 理解チェック✅💖（5問）

1. Specificationは何を返す？（true/false？それとも何かする？）
2. Specificationの嬉しさを2つ言える？
3. Specificationの中に入れちゃダメな“匂い”を1つ言える？
4. 「名前が大事」なのはなぜ？
5. 条件が増えてきたら次章で何ができるようになる？（ヒント：合成🧷）

---

## 次章予告👀✨

次は **Specificationを合成（AND/OR/NOT）**して、
条件が増えても「文章みたいに読める」状態を作るよ〜！📚💗

[1]: https://www.npmjs.com/package/typescript?utm_source=chatgpt.com "typescript"
[2]: https://github.com/microsoft/TypeScript/issues/63085?utm_source=chatgpt.com "TypeScript 6.0 Iteration Plan · Issue #63085"
[3]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
[4]: https://vitest.dev/blog/vitest-4?utm_source=chatgpt.com "Vitest 4.0 is out!"
[5]: https://jestjs.io/versions?utm_source=chatgpt.com "Jest Versions"
