# 第17章：LSP違反の典型パターン集（あるある）📛

（＝「差し替えたら壊れる」を未然に防ぐコーナーだよ〜！🫶✨）

この章のゴールはシンプル💡
**「interface / 継承で“型が合ってる”のに、実行すると壊れる」**の典型を知って、**早めに気づける目👀**を作ることだよ〜🙂‍↕️🌸
LSPは「型の互換」じゃなくて、**振る舞い（約束）の互換**がテーマ！📜✨ ([ウィキペディア][1])


![LSP Unexpected Fish](./picture/solid_ts_study_017_lsp_unexpected_fish.png)

---

## 0) まず最重要：LSP違反って、何が“困る”の？😵‍💫💥

![LSP Chaos](./picture/solid_ts_study_017_lsp_chaos.png)

たとえば `DiscountPolicy` を差し替えられる設計にしたのに…

* Aの割引は動く✅
* Bの割引に差し替えたら **例外で落ちる**💥
* Cの割引は **値がマイナス**で合計がバグる😇
* Dの割引は **注文を勝手に書き換える**😱

これ、全部「置換できてない」＝LSP違反の香り👃💨

---

## 1) 典型①：前提条件を“強くする”（入力にうるさくなる）🚫🧨

![Precondition Funnel](./picture/solid_ts_study_017_precondition_funnel.png)

**親（契約）よりも、子（実装）が要求を増やす**やつ！

### あるある例💡

「割引計算はどんな注文でも呼べる（該当しなければ0円）」が契約なのに…
子が「学生じゃない注文が来たら例外」みたいにしてしまう😵

```ts
type Order = { total: number; customerType: "student" | "normal" };

interface DiscountPolicy {
  calcDiscount(order: Order): number; // 契約：どんな order でも呼べる想定
}

class StudentOnlyDiscount implements DiscountPolicy {
  calcDiscount(order: Order): number {
    if (order.customerType !== "student") {
      throw new Error("学生以外は呼ばないで！"); // ❌ 前提条件を強化しちゃってる
    }
    return Math.floor(order.total * 0.2);
  }
}
```

### 直し方（定番）✅✨

「該当しないなら0円」に寄せる（＝契約を守る）🫶

```ts
class StudentOnlyDiscount implements DiscountPolicy {
  calcDiscount(order: Order): number {
    if (order.customerType !== "student") return 0; // ✅ 契約どおり：呼べる
    return Math.floor(order.total * 0.2);
  }
}
```

### チェックの合言葉🎯

* 「この実装、**呼べるケースが減ってない？**」👀

---

## 2) 典型②：事後条件を“弱くする”（出力の品質が下がる）📉😇

![Postcondition Guarantee](./picture/solid_ts_study_017_postcondition_guarantee.png)

**親（契約）が保証してた結果を、子が保証しなくなる**やつ！

### あるある例💡

契約：`0〜注文合計までの割引額を返す`
なのに、子が `-100` とか `NaN` とか返す💥

```ts
class BuggyDiscount implements DiscountPolicy {
  calcDiscount(order: Order): number {
    return -100; // ❌ ありえない（割引はマイナスにならない契約のはず）
  }
}
```

### 直し方（定番）✅✨

* **返して良い範囲を“契約として明文化”**（コメントでもテストでもOK）
* 実装側でガードする🛡️

```ts
class SafeDiscount implements DiscountPolicy {
  calcDiscount(order: Order): number {
    const raw = Math.floor(order.total * 0.1);
    const clamped = Math.max(0, Math.min(raw, order.total));
    return clamped; // ✅ 0..total を守る
  }
}
```

### チェックの合言葉🎯

* 「この実装、**返す値の範囲**が雑になってない？」🧮

---

## 3) 典型③：例外を“増やす / 種類を変える”（呼び出し側が死ぬ）💣😵

LSPの有名ルールのひとつに
**「子が新しい例外を投げ始めるな」**系の話があるよ（呼び出し側が想定できないから）📛 ([ウィキペディア][1])

### あるある例💡

「割引計算は落ちない」前提で使ってたのに、急に落ちる💥

```ts
class SometimesThrowsDiscount implements DiscountPolicy {
  calcDiscount(order: Order): number {
    if (order.total > 100_000) throw new Error("高額すぎ！"); // ❌
    return 500;
  }
}
```

### 直し方（おすすめ）✅✨

**“落ちうる”契約にしたいなら、型で表現**しちゃうのが強い💪

```ts
type DiscountResult =
  | { ok: true; discount: number }
  | { ok: false; reason: string };

interface DiscountPolicy2 {
  calcDiscount(order: Order): DiscountResult;
}
```

### チェックの合言葉🎯

* 「差し替えたら **try/catch が必要になった**」←それ違反の匂い👃💨

---

## 4) 典型④：意味を“すり替える”（同じメソッド名なのに別物）🎭😱

![Meaning Mismatch](./picture/solid_ts_study_017_meaning_mismatch.png)

型は合ってる。でも**人間の期待**がズレるやつ！

### あるある例💡

契約：`calcDiscount` は「割引“金額”を返す（円）」
なのに子が「割引“率”」を返す（0.2 とか）😇

```ts
class RateDiscount implements DiscountPolicy {
  calcDiscount(order: Order): number {
    return 0.2; // ❌ 金額のはずなのに率を返してる
  }
}
```

### 直し方✅✨

**型で区別**するのが最強🥇（お作法：ブランド型）

```ts
type Yen = number & { readonly __brand: "Yen" };
type Rate = number & { readonly __brand: "Rate" };

interface AmountDiscountPolicy {
  calcDiscountYen(order: Order): Yen;
}

interface RateDiscountPolicy {
  calcDiscountRate(order: Order): Rate;
}
```

### チェックの合言葉🎯

* 「この戻り値、**単位がズレてない？**」💴📏

---

## 5) 典型⑤：不変条件（invariant）を壊す（親が守ってた世界を壊す）🧱💥

![Invariant Thief](./picture/solid_ts_study_017_invariant_thief.png)

LSPは「前提/事後」だけじゃなく **不変条件**も大事だよ〜🧠✨ ([ウィキペディア][1])

### あるある例💡

契約：注文は計算中に書き換えない（読み取り専用）
なのに子が、こっそり注文を書き換える😱

```ts
type Order2 = { total: number; notes: string[] };

interface DiscountPolicy3 {
  calcDiscount(order: Order2): number; // 契約：orderを変更しない想定
}

class MutatingDiscount implements DiscountPolicy3 {
  calcDiscount(order: Order2): number {
    order.notes.push("割引したよ！"); // ❌ 呼び出し側の想定を破壊
    return 100;
  }
}
```

### 直し方✅✨

* **入力をイミュータブルに寄せる**
* 変更したいなら「戻り値」に出す

```ts
type DiscountWithNote = { discount: number; note?: string };

interface DiscountPolicy4 {
  calcDiscount(order: Readonly<Order2>): DiscountWithNote;
}
```

### チェックの合言葉🎯

* 「差し替えたら、**呼び出し後に引数の中身が変わってた**」←だいぶ危険⚠️

---

## 6) 典型⑥：呼び出し順の“隠しルール”を増やす（状態マシン化）🔁🫠

![Hidden State Trap](./picture/solid_ts_study_017_hidden_state_trap.png)

「先に `init()` 呼んでね！」みたいな **隠し前提**を足すと置換できない😵

### あるある例💡

A実装はそのまま使えるのに、B実装は「先に準備が必要」になる

```ts
interface Notifier {
  notify(message: string): void;
}

class LazyInitNotifier implements Notifier {
  private ready = false;

  init() { this.ready = true; }

  notify(message: string) {
    if (!this.ready) throw new Error("initしてから！"); // ❌ 隠し前提
    console.log(message);
  }
}
```

### 直し方✅✨

* `init()` が必要なら **別の抽象に分ける**（ISPっぽいね✂️）
* もしくは **生成時に準備完了**にする（DIで解決しがち💉）

---

## 7) TypeScript特有の罠：型システムが“見逃す”置換不能（特にメソッド）🕳️😵‍💫

ここ、2026のTSでも「油断ポイント」だから知っておくと強いよ💪✨

### ポイント🧠

`--strictFunctionTypes` は関数型を厳しくしてくれるけど、**メソッド宣言由来の関数は対象外**になりやすい（互換性のため）って事情があるよ〜📌 ([TypeScript][2])

「実装が受け取れる引数が減ってる（＝前提条件強化）」みたいな危険が、
**型だけだとスルッと通る**ことがある😇

### 対策の方向性✅✨

* コールバックは **メソッドじゃなく“関数プロパティ”**で持つ（厳しく効かせやすい）
* 契約は **テストで守る**（次の章の“共通テスト”にもつながるよ🧪）

---

## 8) 継承を使うなら：`override` と `noImplicitOverride` は味方だよ🛡️✨

「つもりでオーバーライドしてなかった」みたいな事故を減らせるやつ！
TypeScriptの `noImplicitOverride` を使うと、オーバーライドには `override` を必須にできるよ✅ ([TypeScript][3])

（※これで防げるのは“形の事故”で、**振る舞いのLSP**はやっぱテスト・契約で守るのが大事だよ〜🙂‍↕️）

---

## 最強の守り：契約テスト（“どの実装でも通るテスト”）🧪✨

LSPは最終的にここが強い！💪
「差し替え可能」って言うなら、**同じテストを全実装に流す**のが超効くよ🎯

```ts
// どの DiscountPolicy でも守るべき契約テスト（例）
function contractTest(policy: DiscountPolicy, order: Order) {
  const d = policy.calcDiscount(order);

  if (!Number.isFinite(d)) throw new Error("discountは有限数！");
  if (d < 0) throw new Error("discountはマイナス禁止！");
  if (d > order.total) throw new Error("discountがtotal超えた！");
}

// 実装ごとに同じ契約テストを流す
const policies: DiscountPolicy[] = [
  new StudentOnlyDiscount(),
  new SafeDiscount(),
];

for (const p of policies) {
  contractTest(p, { total: 1000, customerType: "normal" });
  contractTest(p, { total: 1000, customerType: "student" });
}
```

---

## ミニ課題（3つ）🎒✨

### 課題A：前提条件強化を見つけよう🔍

* 「この実装、受け取れる入力が減ってない？」を探して
* **例外を0円返却に変える**か、**Result型にする**か、どっちかで直してね🙂‍↕️

### 課題B：意味すり替えを型で防ごう🧷

* 「金額」と「率」をブランド型で分けて
* 間違えるとコンパイルで落ちるようにしてみてね💥✨

### 課題C：契約テストを1本増やそう🧪

* `discount % 10 === 0` みたいな“勝手ルール”を足してる実装がいたら落ちるようにしてみてね😈（※やりすぎ注意！笑）

---

## まとめ：LSP違反あるあるチェックリスト✅👀

* 入力にうるさくなってない？（前提条件強化）🚫
* 戻り値の品質が落ちてない？（事後条件弱化）📉
* 例外が増えてない？💣
* 単位・意味が変わってない？🎭
* 引数や内部状態をこっそり変えてない？🧨
* 呼び出し順の隠しルールない？🔁
* TSの型だけで安心してない？（振る舞いはテスト！）🧪

---

## おまけ：いまのTypeScript事情メモ📝✨

現時点の安定版は **TypeScript 5.9 系**だよ〜（インストール案内でも “currently 5.9” になってるよ）📌 ([TypeScript][4])
なので、この章のテク（`noImplicitOverride` とか）も **現役で使える**やつだよ🫶✨

---

次の章（第18章）では、このLSP違反を減らす最強ムーブ
**「継承より合成」🧱🤝** を、もっと実戦っぽくやっていくよ〜！☕️📦✨

[1]: https://en.wikipedia.org/wiki/Liskov_substitution_principle?utm_source=chatgpt.com "Liskov substitution principle"
[2]: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-2-6.html?utm_source=chatgpt.com "Documentation - TypeScript 2.6"
[3]: https://www.typescriptlang.org/tsconfig/noImplicitOverride.html?utm_source=chatgpt.com "noImplicitOverride - TSConfig Option"
[4]: https://www.typescriptlang.org/download/?utm_source=chatgpt.com "How to set up TypeScript"
