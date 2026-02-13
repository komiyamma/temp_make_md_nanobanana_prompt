# 第09章：TypeScriptの型でテストを減らす🛡️📘

![testable_ts_study_009_type_shield.png](./picture/testable_ts_study_009_type_shield.png)

この章はね、「**テストをサボる**」じゃなくて「**そもそも壊れにくくして、テストの量を減らす**」回だよ〜！🧁
TypeScriptの型って、上手に使うと **“不正な入力・不正な状態” をコンパイル時点で入れない**ようにできるの。すると、**毎回テストで守ってた “つまづきポイント” がごっそり減る**よ！😆✨

ちなみに最近のTypeScriptは 5.9 系が最新ラインで、GitHub Releases では **TypeScript 5.9.3（Latest）** が 2025-10-01 に出てるよ。 ([GitHub][1])
あと TypeScript 5.9 から `tsc --init` の初期設定が強めになって、`noUncheckedIndexedAccess` と `exactOptionalPropertyTypes` がデフォルトで入るのも “型で事故を減らす” 流れとして大きいよ。 ([Microsoft for Developers][2])

---

## 9-1. 今日のゴール🎯💕この章を終えると、こんなことができるようになるよ👇✨



* ✅ **不正な値**（例：存在しないステータス、nullっぽい事故）を **型で入れない**
* ✅ 「入力チェック」や「状態の組み合わせミス」みたいな **テストを減らす**
* ✅ I/O境界（外側）で“整形・検証”して、中心（ロジック）をスッキリ保つ🧼🏠

---

## 9-2. 「型でテストが減る」ってどういうこと？🧠🪄### 💡減らせるテストの代表例* 「この関数に `undefined` 渡したらどうなる？」系

![testable_ts_study_009_type_shield_concept.png](./picture/testable_ts_study_009_type_shield_concept.png)


* 「ステータスに `delivereddd`（typo）入ったら？」系
* 「オプションプロパティがある前提で触って落ちる」系

これ、型が強いと **そもそもコードが書けない** or **コンパイルで怒られる** から、**テストで守る必要が薄くなる**の。

たとえば `strictNullChecks` を有効にすると、`null/undefined` を雑に扱うとコンパイルで止めてくれるよ。 ([TypeScript][3])

> ただし注意⚠️：
> “外から来るデータ” は現実では壊れてる可能性があるよね？
> だから **境界で検証して Domain 型に変換**して、中心は「正しい前提で」書くのが王道だよ〜！🚪➡️🏠✨

---

## 9-3. 型で「不正」を締め出す4大テク🧰✨### ① リテラル型 + ユニオン型（typo を物理的に消す）

![testable_ts_study_009_union_gate.png](./picture/testable_ts_study_009_union_gate.png)

🧯「文字列で状態を持つ」のが一番事故るポイント！😭
まずはこれを “決め打ちの集合” にしちゃう👇

```ts
type OrderStatus = "draft" | "paid" | "shipped" | "canceled";

function canShip(status: OrderStatus): boolean {
  return status === "paid";
}

// canShip("paidd"); // ❌ typo はコンパイルで死亡👍
```

✅ これだけで「typo系テスト」はかなり減るよ〜！🎉

---

### ② Discriminated Union（状態×データの矛盾を消す）

![testable_ts_study_009_discriminated_union.png](./picture/testable_ts_study_009_discriminated_union.png)

🧩「ステータスは shipped なのに trackingNumber が無い」みたいな矛盾、あるある…😇
それ、型で “ありえない形” にしちゃお！

```ts
type Shipping =
  | { kind: "notShipped" }
  | { kind: "shipped"; trackingNumber: string };

function label(shipping: Shipping): string {
  if (shipping.kind === "shipped") {
    return `追跡番号: ${shipping.trackingNumber}`;
  }
  return "未発送";
}
```

✅ “状態に必要なデータが揃ってるか” をテストで守る量が減るよ！💕

---

### ③ Exhaustive Check（switch漏れをコンパイルで発見）

![testable_ts_study_009_exhaustive_check.png](./picture/testable_ts_study_009_exhaustive_check.png)

🕵️‍♀️「新しい状態を増やしたのに、分岐追加し忘れ」って事故を型で止めるやつ！✨



```ts
type PayMethod = "card" | "bank" | "cash";

function fee(method: PayMethod): number {
  switch (method) {
    case "card":
      return 120;
    case "bank":
      return 80;
    case "cash":
      return 0;
    default: {
      const _never: never = method; // ✅ ここが保険
      return _never;
    }
  }
}
```

✅ ケース追加漏れのテストを “型” が肩代わりしてくれるよ〜！💪✨

---

### ④ Brand 型（ID・金額・率の取り違えを消す）

![testable_ts_study_009_brand_type_keys.png](./picture/testable_ts_study_009_brand_type_keys.png)

🏷️💎`userId` と `orderId` が同じ `string` だと、取り違え事故が起きるよね…😵‍💫
Brand 型で「同じstringでも別物」にできる！

```ts
declare const userIdBrand: unique symbol;
declare const orderIdBrand: unique symbol;

type UserId = string & { readonly [userIdBrand]: "UserId" };
type OrderId = string & { readonly [orderIdBrand]: "OrderId" };

function toUserId(raw: string): UserId | null {
  // 例：簡易チェック
  if (!raw.startsWith("u_")) return null;
  return raw as UserId;
}

function loadUser(userId: UserId) {
  // ...
}

const uid = toUserId("u_123");
if (uid) loadUser(uid);

// loadUser("u_123"); // ❌ 生stringは渡せない
```

✅ 「取り違え」テストが激減するタイプのやつ！🥳

---

## 9-4. 型ガード（Type Guard）

![testable_ts_study_009_boundary_guard.png](./picture/testable_ts_study_009_boundary_guard.png)

で “境界の検証” をうまく書く🚧✅外から来るデータ（API/フォーム/JSON）は信用しない！🙅‍♀️
境界でチェックして **Domain 型** に変換してから中心へ渡すと、中心のテストがスリムになるよ✨

```ts
type Coupon =
  | { kind: "percent"; value: number } // 0〜100
  | { kind: "fixed"; value: number };  // 円

function isCoupon(x: unknown): x is Coupon {
  if (typeof x !== "object" || x === null) return false;
  const obj = x as any;
  if (obj.kind === "percent") return typeof obj.value === "number";
  if (obj.kind === "fixed") return typeof obj.value === "number";
  return false;
}
```

ポイントは👇

* ✅ 境界：`unknown` から安全に `Coupon` へ
* ✅ 中心：`Coupon` が来る前提でロジックが書ける
  → 中心の「変な入力テスト」が減る！🎉

---

## 9-5. “最近の推奨” tsconfig の強化ポイント⚙️

![testable_ts_study_009_tsconfig_strong.png](./picture/testable_ts_study_009_tsconfig_strong.png)

🧊TypeScript 5.9 の `tsc --init` では、最初からけっこう強い設定が出るよ。
特にこの2つは “事故を減らす” のに効く！ ([Microsoft for Developers][2])

### ✅ `noUncheckedIndexedAccess`「存在しないかも」なキーアクセスに `undefined` が混ざるようになる。
つまり “取り出した値がある前提で触る事故” が減る！ ([TypeScript][3])

### ✅ `exactOptionalPropertyTypes`「optional は optional」と厳密に扱う設定。
地味だけど「optional を雑に扱ってバグる」を減らせるよ。 ([TypeScript][3])

### ✅ `strictNullChecks`（strictの一部）`null/undefined` の扱いが雑だとコンパイルで止まる！
`strict` を有効にするとデフォルトで `true` 扱いだよ。 ([TypeScript][3])

#### 例：差分だけ入れるならこんな感じ💡

```json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true
  }
}
```

---

## 9-6. ハンズオン：入力型を強くして “テストを減らす”🚧➡️

💎題材：**割引を適用して合計金額を返す**🛒🍰



### Step 0：ありがちな弱い版（テストが増えるやつ）

😇

```ts
function applyDiscount(total: number, discountType: string, value: number): number {
  if (discountType === "percent") return Math.floor(total * (1 - value / 100));
  if (discountType === "fixed") return Math.max(0, total - value);
  return total; // え？unknownなタイプ来たら？😵‍💫
}
```

この形だとテストがこう増える👇

* discountType が変な文字列のとき
* percent なのに value が 1000 のとき
* total が負のとき… etc 😱

---

### Step 1：まずユニオンで「タイプのtypo」を消す🧯

```ts
type DiscountType = "percent" | "fixed";
```

---

### Step 2：Discriminated Unionで「組み合わせ矛盾」を消す🧩

```ts
type Discount =
  | { kind: "percent"; value: number } // 0〜100 を想定
  | { kind: "fixed"; value: number };  // 0以上を想定

function applyDiscount(total: number, discount: Discount): number {
  switch (discount.kind) {
    case "percent":
      return Math.floor(total * (1 - discount.value / 100));
    case "fixed":
      return Math.max(0, total - discount.value);
    default: {
      const _never: never = discount;
      return _never;
    }
  }
}
```

✅ これで「unknownなdiscountType来たら？」系のテストが減るよ🎉

---

### Step 3：境界で “検証してから” 中心へ渡す（中心のテストをスリム化）

🚪✨境界で `unknown` を `Discount` にしてから中心へ👇



```ts
type ParseResult<T> = { ok: true; value: T } | { ok: false; message: string };

function parseDiscount(input: unknown): ParseResult<Discount> {
  if (typeof input !== "object" || input === null) return { ok: false, message: "not object" };
  const x = input as any;

  if (x.kind === "percent" && typeof x.value === "number" && 0 <= x.value && x.value <= 100) {
    return { ok: true, value: { kind: "percent", value: x.value } };
  }
  if (x.kind === "fixed" && typeof x.value === "number" && 0 <= x.value) {
    return { ok: true, value: { kind: "fixed", value: x.value } };
  }
  return { ok: false, message: "invalid discount" };
}
```

ここが超大事💖

* ✅ 境界のテスト：`parseDiscount` に集中（入力のバリエーション多めOK）
* ✅ 中心のテスト：`applyDiscount` は “正しいDiscountが来る前提” でシンプルに（ケース少なめ）

→ 「中心が変な入力で壊れる系テスト」がごっそり減るよ！🥳

---

## 9-7. 章末チェックリスト✅🌸* [ ] 状態や種別は `string` 直書きじゃなくて **ユニオン型** にした？


* [ ] 状態によって必要なデータが変わるなら **Discriminated Union** にした？
* [ ] `switch` には **neverチェック** を入れた？
* [ ] 外から来る値は `unknown` → **境界で検証してDomain型へ** にした？
* [ ] `strict` + `noUncheckedIndexedAccess` + `exactOptionalPropertyTypes` を意識できた？ ([Microsoft for Developers][2])

---

## まとめ🍀

✨型を強くすると…



* 🧯 “そもそも書けないバグ” が増える（最高！）
* 🧪 テストは「中心のロジック」へ集中できる
* 🚪 境界で検証してDomain型に変換できると、中心がどんどん綺麗になる

次の章（第10章）は「テストしにくい臭い」カタログ👃💨だよ！
今日の内容を知ってると、「あ、ここ型と境界で直せるやつだ！」って嗅ぎ分けが上手くなるよ〜😆🫶

[1]: https://github.com/microsoft/typescript/releases "Releases · microsoft/TypeScript · GitHub"
[2]: https://devblogs.microsoft.com/typescript/announcing-typescript-5-9/ "Announcing TypeScript 5.9 - TypeScript"
[3]: https://www.typescriptlang.org/tsconfig/ "TypeScript: TSConfig Reference - Docs on every TSConfig option"
