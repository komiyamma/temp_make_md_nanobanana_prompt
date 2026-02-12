# 第11章：interfaceの使いどころ（型だけで差し替えを作る）🧩

## ねらい🎯

* 「あとで差し替えたい所」を **interfaceで“差し替え可能”** にできるようになる✨
* 「値（実装）に依存」じゃなくて「型（約束）に依存」へ寄せる感覚をつかむ🧠

---

## 1) 今日いちばん大事なこと🌟

## ✅ interfaceは「形（shape）の約束」🧩

TypeScriptは **構造的型付け（structural typing）** だから、
「このメンバー（プロパティ/関数）を持ってるならOK！」って感じで型が合います。([TypeScript][1])

つまり…

* **“実装が何か”より、“できること（形）”が合ってるか** が大事✨

## ✅ interfaceはランタイムには存在しない（＝型は消える）👻

interfaceは **コンパイル時の道具** で、実行時に `instanceof` みたいな判定はできません。([TypeScript][2])
（ここ、最初に知っておくと事故が減るよ〜🧯）

---

## 2) 「interfaceが必要になる瞬間」あるある集🫠

次みたいになったら出番！👇

* 🌀 if/switchが増えて「分岐の森🌳」になる
* 🔁 似た処理なのに“ちょい違い”が増えてコピペ地獄になる
* 🧪 テストしたいのに、外部依存（API/DB/時間/乱数）が邪魔で差し替えたい
* 🎛️ 「通常」「会員」「学割」みたいに、**計算ルールを切り替えたい**

この章は、カフェ題材で **「料金計算ルール」** を差し替え可能にするよ☕🧾

「差し替え可能にする」って、こういうこと！🔁✨

![interfaceによる実装の差し替え（カード決済と現金決済）。](./picture/gof_ts_study_011_interface_swap.png)


---

## 3) まず「つらいコード」を見てみよ🥲（Before）

「会員なら5%引き」「学割なら10%引き」…が増えると👇みたいに育ちがち🌱

```ts
type OrderItem = { name: string; unitPriceYen: number; qty: number };

function calcTotalYen(items: readonly OrderItem[], kind: "regular" | "member" | "student") {
  const subtotal = items.reduce((sum, it) => sum + it.unitPriceYen * it.qty, 0);

  if (kind === "member") return Math.floor((subtotal * 95) / 100);
  if (kind === "student") return Math.floor((subtotal * 90) / 100);

  return subtotal;
}
```

つらさポイント👃💦

* ルール追加のたびに `if` が増える
* 「割引の計算」ロジックがここにべったり張り付く
* テストも「kind全部」パターンが膨れていく

---

## 4) interfaceで「差し替え口」を作る🥳（After）

## 4-1) ルールは “関数として” 差し替えるのがTypeScript的🧁

クラスを増やさなくてもOK！
**「関数の形」をinterfaceで約束** しちゃうのがスッキリ✨

```ts
type Yen = number;

type OrderItem = Readonly<{
  name: string;
  unitPriceYen: Yen;
  qty: number;
}>;

interface PricingPolicy {
  (items: readonly OrderItem[]): Yen;
}
```

ここがポイント💡

* `PricingPolicy` は「こういう関数を渡してね」という約束🧩
* TypeScriptは構造的型付けだから、この形の関数なら何でもOK！([TypeScript][1])

---

## 4-2) ルール実装（＝差し替えたい中身）を用意する🎛️✨

```ts
const subtotalYen = (items: readonly OrderItem[]) =>
  items.reduce((sum, it) => sum + it.unitPriceYen * it.qty, 0);

export const regularPricing: PricingPolicy = (items) => {
  return subtotalYen(items);
};

export const memberPricing: PricingPolicy = (items) => {
  const subtotal = subtotalYen(items);
  return Math.floor((subtotal * 95) / 100); // 5% OFF
};

export const studentPricing: PricingPolicy = (items) => {
  const subtotal = subtotalYen(items);
  return Math.floor((subtotal * 90) / 100); // 10% OFF
};
```

🎉 これで「計算ルール」だけを自由に差し替えられる！

---

## 4-3) 使う側は “ルールの中身を知らない” 🕶️

使う側（呼び出し側）がシンプルになるのが最高なんよ…🥺✨

```ts
export function calcTotalYen(items: readonly OrderItem[], policy: PricingPolicy): Yen {
  return policy(items);
}
```

呼び出し例☕🧾

```ts
const items: OrderItem[] = [
  { name: "Latte", unitPriceYen: 520, qty: 1 },
  { name: "Cookie", unitPriceYen: 180, qty: 2 },
];

const totalRegular = calcTotalYen(items, regularPricing);
const totalMember = calcTotalYen(items, memberPricing);
```

```mermaid
classDiagram
    class PricingPolicy {
        &lt;&lt;interface&gt;&gt;
        (items: OrderItem[]): Yen
    }
    class RegularPricing {
        subtotal
    }
    class MemberPricing {
        subtotal * 0.95
    }
    class StudentPricing {
        subtotal * 0.90
    }

    PricingPolicy <|.. RegularPricing
    PricingPolicy <|.. MemberPricing
    PricingPolicy <|.. StudentPricing
    
    Client --> PricingPolicy : "使う (依存)"
```

---

## 5) 「ルール表（Registry）」を作るとさらに実務っぽい🗂️✨

「会員/学割/通常」みたいに選びたいときは **Map/オブジェクトで登録** が定番💡
ここで便利なのが `Record` と `satisfies` 💫

* `Record<K, V>`：キーと値の形を強制できる（標準のUtility Types）([TypeScript][3])
* `satisfies`：**型チェックはするけど、値の型推論を潰しにくい**（TS 4.9〜）([TypeScript][4])

```ts
type PricingKind = "regular" | "member" | "student";

export const pricingPolicies = {
  regular: regularPricing,
  member: memberPricing,
  student: studentPricing,
} satisfies Record<PricingKind, PricingPolicy>;

export function calcTotalByKind(items: readonly OrderItem[], kind: PricingKind): Yen {
  return pricingPolicies[kind](items);
}
```

うれしい🎁

* `student` を書き忘れたら **コンパイルで怒られる** 😤✨
* 追加もこれで、呼び出し側は `strategyMap[kind]` で取り出すだけ！
分岐（if文）が消えて、スッキリ！✨

![料金計算ロジックをカートリッジのように差し替える様子。](./picture/gof_ts_study_011_pricing_plug.png)
）

---

## 6) テストで「差し替え最高…」を体感しよ🧪🎉

VitestはTypeScriptと相性よく、Vite系でよく使われるテスト環境だよ〜🧁([vitest.dev][5])
（第6章でテスト環境を作ってある前提で、ここは最小だけ！）

```ts
import { describe, it, expect } from "vitest";
import { calcTotalYen, regularPricing, memberPricing, studentPricing } from "./pricing";

const items = [
  { name: "Latte", unitPriceYen: 520, qty: 1 },
  { name: "Cookie", unitPriceYen: 180, qty: 2 },
] as const;

describe("pricing policies", () => {
  it("regular", () => {
    expect(calcTotalYen(items, regularPricing)).toBe(520 + 180 * 2);
  });

  it("member 5% off", () => {
    const subtotal = 520 + 180 * 2;
    expect(calcTotalYen(items, memberPricing)).toBe(Math.floor((subtotal * 95) / 100));
  });

  it("student 10% off", () => {
    const subtotal = 520 + 180 * 2;
    expect(calcTotalYen(items, studentPricing)).toBe(Math.floor((subtotal * 90) / 100));
  });
});
```

ポイント💡

* “policyを差し替えるだけ”でテストできる
* 呼び出し側がスッキリして、テストも読みやすい📖✨

---

## 7) VS Codeで「設計改善」を手で覚える🧰✨

やることはこれだけでOK〜！🫶

* ✏️ **Rename Symbol**：`PricingPolicy` / `calcTotalYen` の名前を変えてみる
* 🔎 **Find All References**：どこで呼ばれてるか追う
* 🧩 **Extract Function**：`subtotalYen` を抽出して責務を分ける
* 🧪 テストを1本追加して、壊れてないか確認する

---

## 8) AIに聞くときのプロンプト例🤖💬

## 例1：差し替えポイントを見つけたい👀

```text
このコードで「あとで差し替えたくなりそう」な処理を3つ見つけて、
TypeScriptのinterface（または関数型）で差し替え口を作る最小案をください。
独自クラスは増やしすぎないでください。
```

## 例2：satisfiesで登録を型安全にしたい🧷

```text
pricingPoliciesの登録オブジェクトを、Recordとsatisfiesで型安全にしたい。
キーの追加漏れがコンパイルで分かるようにする例をTypeScriptで。
```

## 例3：テストケースを増やしたい🧪

```text
割引ロジックのテストケースを、代表ケース＋境界ケースで10個提案して。
（端数処理や0件、qty=0なども含めて）
```

---

## 9) つまずき回避💡（超あるある！）

## 🚫 interfaceを増やしすぎ問題

「なんでもinterface化！」は逆に迷子になるよ〜😵‍💫
✅ 最初は **1個だけ**：「差し替えたい所」だけに作るのが正解✨

## 🚫 interfaceで実行時チェックしようとする

`instanceof PricingPolicy` みたいなのはできません🙅‍♀️
TypeScriptの型は実行時に残らないよ〜👻([TypeScript][2])

## 🚫 “データ形”まで全部interfaceにする

データ構造は `type` やインラインでもOKな場面が多いよ🧁
interfaceは特に **「役割（振る舞い）を差し替えたい」** ときに強い💪

---

## 10) ハンズオン🛠️（今日の課題）☕✨

## 課題A：新ルールを1個追加🎁

* `happyHourPricing` を作る

  * 例：合計が1000円以上なら **100円引き**（マイナスにならないように！）

## 課題B：登録漏れをコンパイルで検出🧷

* `PricingKind` に `"happyHour"` を追加
* `pricingPolicies` に追加し忘れて、ちゃんと怒られるか確認😈✨

## 課題C：テストを1本増やす🧪

* 「1000円ちょうど」「999円」の境界をテストしてね📏✨

---

## 11) まとめ✅🎉

* interfaceは「差し替え口」を作る道具🧩
* TypeScriptは構造的型付けだから、“形が合えばOK” で差し替えしやすい([TypeScript][1])
* 料金計算みたいな **ルール（ポリシー）** は、interface＋関数でキレイに切り替えられる☕✨
* `Record`＋`satisfies` で「登録漏れ」をコンパイルで潰せる🧷([TypeScript][3])

※ ちなみに本日時点のTypeScript最新安定版は 5.9.3 として公開されています。([GitHub][6])

[1]: https://www.typescriptlang.org/docs/handbook/type-compatibility.html?utm_source=chatgpt.com "Documentation - Type Compatibility"
[2]: https://www.typescriptlang.org/docs/handbook/typescript-in-5-minutes-oop.html?utm_source=chatgpt.com "Documentation - TypeScript for Java/C# Programmers"
[3]: https://www.typescriptlang.org/docs/handbook/utility-types.html?utm_source=chatgpt.com "Documentation - Utility Types"
[4]: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-0.html?utm_source=chatgpt.com "Documentation - TypeScript 5.0"
[5]: https://vitest.dev/guide/comparisons.html?utm_source=chatgpt.com "Comparisons with Other Test Runners | Guide"
[6]: https://github.com/microsoft/typescript/releases "Releases · microsoft/TypeScript · GitHub"
