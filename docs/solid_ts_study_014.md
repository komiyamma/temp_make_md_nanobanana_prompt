# 第14章：抽象化の「さじ加減」🍰⚖️（やりすぎ防止のOCP）

## この章でできるようになること 🎯✨

* 「抽象化した方がいい場面／しない方がいい場面」を見分けられる 👀✅
* **“差し替え口”**（拡張ポイント）を、必要な場所にだけ作れる 🚪🔁
* 未来の変更に強いけど、**今の自分が読める**コードにできる 🧸📖


![Rube Goldberg](./picture/solid_ts_study_014_rube_goldberg.png)

---

## まず結論：抽象化は「未来の変更のための穴」🚪🧩

OCPって「追加に強くする」イメージだけど、実際は…

* ✅ **変わりそうなところ**に“差し替え口”を作る
* ❌ **変わるか分からないところ**まで先回りして抽象化しない

このバランスがすべてだよ〜⚖️😊

ちなみに今の最新のTypeScriptは **5.9系**（公式の5.9リリースノートが2026/01/07更新）だよ📌✨ ([TypeScript][1])
（なので、下のコード例も「いま普通に使われる書き方」をベースにしてるよ〜）

---

## やりすぎ抽象化あるある 🥲💥（見つけたら黄色信号）

次の症状が出てたら「ちょい盛りすぎ」かも🚧⚠️

* 🌀 **抽象が増えてるのに、追加は楽になってない**
* 🧩 interface / abstract / generics が増えて、読むのがしんどい
* 🧙‍♂️ 「将来のために…」って言いながら、その将来が具体的じゃない
* 🧱 1個しか実装が無いのに、戦略・工場・基底クラスがいる
* 🧪 テストが無いのに抽象化してて、怖くて触れない

> 抽象化は “賢さ” じゃなくて、**変更コストを下げる道具**だよ🛠️✨

---

## 抽象化は「3段階」で育てるのが安全 🌱➡️🌳

![Abstraction Steps](./picture/solid_ts_study_014_abstraction_steps.png)

いきなり大きい仕組みにしないで、**段階的にレベルアップ**すると失敗しにくいよ😊✨

### 🥚Lv0：まずは素直に書く（if/switch）

「まず動く」「仕様が固まってない」ならこれでOK👌

```ts
type CouponCode = "STUDENT" | "RAIN";

function calcDiscount(code: CouponCode, totalYen: number): number {
  switch (code) {
    case "STUDENT":
      return Math.floor(totalYen * 0.1);
    case "RAIN":
      return 200;
  }
}
```

**いいところ**：読みやすい📖
**弱点**：種類が増えると分岐が育って地獄になりがち🌋

---

### 🐣Lv1：「データ駆動」にする（関数マップ）

分岐が増えそうだけど、まだ “仕組み” を作りたくないときに最強💪✨

ここで便利なのが `satisfies` 👑
「型チェックはするけど、推論のうまみは残す」って感じ🍯
（`satisfies` は TypeScript 4.9 からの機能だよ） ([TypeScript][2])

```ts
type CouponCode = "STUDENT" | "RAIN";
type DiscountFn = (totalYen: number) => number;

const discountRules = {
  STUDENT: (totalYen: number) => Math.floor(totalYen * 0.1),
  RAIN: (_totalYen: number) => 200,
} satisfies Record<CouponCode, DiscountFn>;

export function calcDiscount(code: CouponCode, totalYen: number): number {
  return discountRules[code](totalYen);
}
```

**いいところ**：

* 追加は1行でOK（分岐が増えない）🧩✨
* `CouponCode` を増やしたのにルールを書き忘れたら、型が怒ってくれる😤✅

**まだやらない方がいいこと**：

* この段階で interface + class にしない（必要になってからでOK）🙅‍♀️

---

### 🐥Lv2：本気の“差し替え口”（Strategy / DI）

次の条件がそろってきたら、戦略パターンが輝く🌟

* 割引の種類が増えるだけじゃなくて、**割引ごとに必要データが違う**
* 管理画面や外部設定で **動的に差し替えたい**
* テストで実装を差し替えたい（本番/テスト）🎭

```ts
type Money = number;

export interface DiscountPolicy {
  code: string;
  calc(total: Money): Money;
}

export class StudentDiscount implements DiscountPolicy {
  code = "STUDENT";
  calc(total: Money): Money {
    return Math.floor(total * 0.1);
  }
}

export class RainDiscount implements DiscountPolicy {
  code = "RAIN";
  calc(_total: Money): Money {
    return 200;
  }
}

export class DiscountService {
  private map: Map<string, DiscountPolicy>;

  constructor(policies: DiscountPolicy[]) {
    this.map = new Map(policies.map(p => [p.code, p]));
  }

  calc(code: string, total: Money): Money {
    const policy = this.map.get(code);
    if (!policy) return 0;
    return policy.calc(total);
  }
}
```

**いいところ**：

* 追加はクラス1個増やして配列に入れるだけ🎉
* テストで「偽の割引」を差し込める🧪✨

**注意点**：

* 「2種類しかない」「当面固定」なら Lv1 で十分なことも多いよ😊

---

## じゃあ、いつ抽象化するの？👀🧠（判断チェックリスト）

迷ったら、この質問に答えてみて📝✨

1. 🔁 **同じ形の変更**が、今後2回以上来そう？
2. 🧨 追加のたびに **同じ場所を毎回修正**してる？（分岐の中心とか）
3. 🧱 追加するときに、既存のテストが壊れやすい？
4. 🧩 追加対象が「割引」「支払い」「通知」みたいに、明確な“種類”で増える？
5. 🔌 追加が「差し替え」っぽい？（A/B、環境、本番/テスト）
6. 🧑‍🤝‍🧑 チーム（未来の自分）が読める？（読めないなら負債）
7. ✅ テストで守れる？（守れない抽象化は怖いだけ）

**3つ以上 YES** なら、抽象化を検討してOK👌✨
**1つもYESが無い**なら、今はやらないのが正解率高め😊

---

## 抽象化の「粒度」：大きく作らないコツ 🍡✨

抽象化って、でかくすると失敗しやすいの…🥲

### ✅ 良い抽象の特徴

* 役割が1行で言える（例：「割引を計算する」）🗣️
* メソッドが少ない（1〜3個くらい）🧼
* 名前が「実装」じゃなくて「意図」になってる（`DiscountPolicy` など）🎯

### ❌ 事故る抽象の特徴

* `IDiscountStrategy<TContext, TResult, TEnv>` みたいにジェネリクス盛り盛り🍔💥
* `BaseService` / `AbstractManager` みたいな “何でも屋” 👷‍♂️
* 使われてないメソッドが多い（ISP的にもNG寄り）🧻

---

## ミニ演習（Campus Café）☕️📦✨

### 演習1：どれを選ぶ？当てはめクイズ 🎯

次の未来、あなたなら Lv0/Lv1/Lv2 どれ？🤔

* A) クーポンは2種類固定。増える予定なし
* B) 月1で増える。増えるたびに分岐が長くなる
* C) 店舗ごとに割引が違う。設定で切り替えたい

答え（目安）👇

* A) Lv0 ✅
* B) Lv1 ✅
* C) Lv2 ✅

---

### 演習2：Lv0 → Lv1 リファクタしてみよ🧼✨

やることはこれだけ👇

1. `switch` をやめる
2. 関数マップにする
3. `satisfies` で「書き忘れ」を防ぐ

（上の Lv1 コードを写経でOKだよ📝💗）

---

### 演習3：Lv1 → Lv2 が必要になる条件を“自分の言葉”で書く📝✨

たとえばこんな感じ👇

* 「店舗ごとに割引が違うから、起動時にポリシー差し替えたい」
* 「テストで割引の実装を入れ替えたい」
* 「割引ごとに必要な外部データが増えてきた」

---

## AI活用コーナー 🤖💡（抽象化を“盛らせない”指示がコツ）

AIに相談するときは、**最初に“軽い案”を出させる**のが安全だよ😊

### 使えるプロンプト例 🪄

* 「まずLv0（素直な実装）で書いて、その後にLv1案（関数マップ）も出して。最後にLv2案（Strategy）も出して。**メリット/デメリット**を比較して」
* 「将来の変更が“月1で増える”想定。**最小の抽象化**でOCPに寄せたい」
* 「今あるテストを壊さない手順で、小さくリファクタのステップを書いて」

### AIの出力を採用する前のチェック✅

* 🧠 “将来”が具体的か？（妄想抽象化になってない？）
* 🧪 テストが増えてるか？（増えてないなら危ない）
* 📖 自分が3日後に読んで理解できるか？

---

## まとめ 🌸✨

* 抽象化は「差し替え口」だけど、作りすぎると逆に弱くなる⚖️
* **Lv0 → Lv1 → Lv2** の順で育てると安全🌱
* `satisfies` を使うと「追加時の書き忘れ」を型で防げて気持ちいい💎 ([TypeScript][2])
* 迷ったらチェックリスト。YESが少ないなら、今は素直に行こう😊👍

---

## ミニ課題（提出用）🎁📝

1. クーポンを1つ追加（例：`SET` = 300円引き）
2. Lv1方式で追加して、既存コードの修正が最小になってるか確認✨
3. 「このケースはLv2が必要？」を2〜3行で説明💬😊

やってみよ〜〜っ！🎉☕️✨

[1]: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-9.html "TypeScript: Documentation - TypeScript 5.9"
[2]: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-4-9.html?utm_source=chatgpt.com "Documentation - TypeScript 4.9"
