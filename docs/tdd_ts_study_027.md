# 第27章：明白な実装（迷いがない時は素直に）🌼

![明白な実装のデージー](./picture/tdd_ts_study_027_daisy.png)

## 🎯この章のゴール

* 「いまは **明白な実装でいける！**」って判断できるようになる✨
* **仮実装 / 三角測量 / 明白な実装** の使い分けができるようになる🧠💡
* “儀式TDD”にならずに、**スピードと品質を両立**できるようになる🏎️✅

---

## 0) 今日の前提（2026-01-19 時点の“今”メモ🗓️）

* TypeScript は **5.9 系が安定版として参照できる状態**（5.9 のリリースノート／GitHub Releases が確認しやすい） ([TypeScript][1])
* Node.js は **24 系が Active LTS**、2026-01-13 に 24.13.0 のセキュリティリリースも出てるよ（学習でも最新版追従が吉） ([Node.js][2])
* Vitest は **4.0 がメジャーとして現役**、移行ガイドも 2026-01-08 更新。さらに 4.1 の beta も出てる（学習は安定版推奨） ([Vitest][3])

---

![Three Strategies Map](./picture/tdd_ts_study_027_three_strategies_map.png)

## 1) 3つの手を“1枚の地図”にする🗺️✨

## 🩹 仮実装（Fake it）

* **とにかく最短で Green にする**
* ただし「仮」が **永住しやすい**ので、次の一手（一般化）を忘れない🫠

## 📐 三角測量（Triangulation）

* 2ケース目で **一般化の方向を決める**
* 「一般化したいけど、まだ確信がない…」時の味方🤝

## 🌼 明白な実装（Obvious implementation）

* 「答えがハッキリしてるなら、**素直に書いちゃう**」
* **TDDをサボる**のとは違うよ！
  → *“テストで約束を置いてから、迷いなく実装する”* のがコツ💖

---

![Decision Checklist](./picture/tdd_ts_study_027_decision_checklist.png)

## 2) 「明白」かどうかの判断チェック✅🧠

次のうち **多くが YES** なら、明白な実装でGOしやすいよ🌼

* ✅ 実装の形が **ほぼ1通り**（迷いがない）
* ✅ 仕様が **計算/変換/整形**などで、方法が明快
* ✅ 分岐が少なく、境界もイメージしやすい
* ✅ “将来の拡張”を考えなくても、いまの仕様が素直に書ける
* ✅ テスト1本目を書いた瞬間に「実装こうだな」が見える

逆に、こういうのは明白じゃないかも👇

* ❌ 例外/失敗の種類が曖昧（Result？throw？など迷う）
* ❌ モデルの責務が混ざってる（どこに置く？で迷う）
* ❌ ルールが増えそうで、設計の分岐が多い
* ❌ “正しさ”がぱっと検証できない（複雑な状態/時刻/乱数など）

---

## 3) ハンズオン：ポイント計算で「明白な実装」を体験🌼🎮

## お題🧸

* 購入金額（円）からポイントを計算する
* ルール：**100円につき1pt**、端数は切り捨て
* 0円なら0pt、マイナスはエラーにする🚫

---

![Hands-on Step 1 Tests](./picture/tdd_ts_study_027_hands_on_step1.png)

## 🧪 Step 1：まずテストで“約束”を置く（Red）🚦

```ts
// tests/calcPoints.test.ts
import { describe, it, expect } from "vitest";
import { calcPoints } from "../src/calcPoints";

describe("calcPoints", () => {
  it("250円なら2pt（100円につき1pt、端数切り捨て）", () => {
    expect(calcPoints(250)).toBe(2);
  });

  it("99円なら0pt", () => {
    expect(calcPoints(99)).toBe(0);
  });

  it("0円なら0pt", () => {
    expect(calcPoints(0)).toBe(0);
  });

  it("マイナスはエラー", () => {
    expect(() => calcPoints(-1)).toThrowError();
  });
});
```

💡ポイント：

* 1本目だけでもいいけど、今回は「明白さ」を強めるために **典型ケースを最小だけ追加**してるよ🧪✨
* こうすると「一般化の方向」がブレにくい👍

---

![Straightforward Logic](./picture/tdd_ts_study_027_straightforward_logic.png)

## 🌼 Step 2：明白な実装でいく（Green）✅

```ts
// src/calcPoints.ts
const POINT_UNIT_YEN = 100;

export function calcPoints(purchaseYen: number): number {
  if (purchaseYen < 0) throw new RangeError("purchaseYen must be >= 0");
  return Math.floor(purchaseYen / POINT_UNIT_YEN);
}
```

ここ、めちゃ明白だよね🌼

* 100円 → 1pt
* 端数切り捨て → `Math.floor`
* マイナス → 仕様でエラー、なのでガード

---

## 🧹 Step 3：Refactor（読みやすく・意図が伝わる形へ）✨

### ✅改善アイデア例（やりすぎ注意）

* エラーメッセージをテストで固定するか？（今は固定しなくてOK🙆‍♀️）
* “円”の型を表現したくなる？（この段階では軽くでOK🏷️）

たとえば、もう少し説明的にしたいなら👇

```ts
const POINT_UNIT_YEN = 100;

export function calcPoints(purchaseYen: number): number {
  assertNonNegative(purchaseYen);
  return Math.floor(purchaseYen / POINT_UNIT_YEN);
}

function assertNonNegative(value: number): void {
  if (value < 0) throw new RangeError("value must be >= 0");
}
```

---

## 4) 同じお題を「別手」でやって比較してみよ🧪🔍（章のメイン！）

![Comparison Fake It](./picture/tdd_ts_study_027_comparison_fake_it.png)

## 🩹仮実装でやると…

* 1本目（250円→2pt）だけなら、こう書けちゃう：

```ts
export function calcPoints(_: number): number {
  return 2; // 仮！
}
```

➡️ すぐGreenだけど、**仮が永住**しやすい😇
次のテスト（99円→0pt）で死ぬから、そこで一般化する流れ。

---

![Comparison Triangulation](./picture/tdd_ts_study_027_comparison_triangulation.png)

## 📐三角測量でやると…

* 1本目：250→2
* 2本目：99→0
* そこで「あ、割り算だな」って一般化へ

➡️「一般化はしたいけど確信がない」時に気持ちいいやつ💖

---

## 🌼明白な実装でやると…

* 最初のテストを書いた瞬間に
  「`Math.floor(purchaseYen / 100)` でしょ」って確信がある

➡️ だから **素直に書いてOK** 🙆‍♀️✨
（ただしテストは置く！ここ大事💘）

---

![YAGNI Warning](./picture/tdd_ts_study_027_yagni_warning.png)

## 5) ありがち事故まとめ🚧🫠

* 😵‍💫 **“明白”の名のもとにテストを省略** → それ、ただのノーテスト実装だよ〜！
* 😵‍💫 未来を考えすぎて、先に抽象化しすぎる（YAGNI地獄）🕳️
* 😵‍💫 1ステップが大きくなって、どこで壊したか分からない💥
  → 明白でも「小さめコミット」は正義💪✨

---

## 6) 🤖AIの使いどころ（“判断”を手伝わせる）🧠✨

## ✅おすすめプロンプト（コピペでOK）

* 「この仕様は *仮実装/三角測量/明白な実装* のどれが向きそう？理由も短く✨」
* 「このテストケース、足りない境界がある？（追加は最大2個まで）🧪」
* 「この実装、未来のこと考えすぎてない？やりすぎなら削る案ちょうだい✂️」

## 🚫やらないこと

* AIに仕様を決めさせる（それは危ない😵‍💫）
* 便利そうだからって抽象化し始める（沼りがち🫠）

---

## 7) ✅チェック（セルフ採点）💯

* ✅ テストを置いてから実装した
* ✅ 「明白だから素直に書いた」が説明できる
* ✅ 仮実装や三角測量に逃げる必要がなかった理由が言える
* ✅ Refactorで読みやすくなった（やりすぎてない）
* ✅ 仕様が増えても破綻しにくそう（少なくとも今は！）✨

---

## 8) 🧪宿題（10〜20分でOK）🎀

次の3つ、どの手が向くか選んで、理由を1行で書いてみてね😊✍️
（余裕あれば1個だけ実装まで！）

1. 文字列を「trimして小文字にする」関数
2. 会計：合計金額に「クーポン割引（上限あり）」を適用
3. 現在時刻を使って「期限切れ判定」する

---

次の章（28章：重複のにおい👃🚨）に進むと、今日の「明白に書いたコード」から **“設計アラーム”** を見つける練習に入れるよ〜🧪✨

[1]: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-9.html?utm_source=chatgpt.com "Documentation - TypeScript 5.9"
[2]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
[3]: https://vitest.dev/blog/vitest-4?utm_source=chatgpt.com "Vitest 4.0 is out!"
