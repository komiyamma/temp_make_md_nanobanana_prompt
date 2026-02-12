# 第18章：乱数（Random）を分離する🎲🎯

![testable_ts_study_018_controlled_dice.png](./picture/testable_ts_study_018_controlled_dice.png)

## 18.1 今日のゴール🎯✨* 乱数が入ってもテストが**毎回同じ結果で安定**するようにする🧪✅


* 「くじ引き／ガチャ」みたいな処理を、**再現できるテスト**で守れるようにする🎁🔁
* 乱数を「外の世界（I/O寄り）」として扱い、**中心ロジックから追い出す**感覚をつかむ🚪🏠

---

## 18.2 なんで乱数があるとテストが不安定になるの？😵‍💫🎲乱数を直に使うと…



* ✅ たまに通る／たまに落ちる（フレイキー）😇💥
* ✅ 失敗しても**再現できない**（原因が追えない）🕵️‍♀️💦
* ✅ 「確率の話」をテストしだして地獄（分布テストは沼）🌀

つまり、乱数は **テストにとって“敵”になりやすい**のです🥺

---

## 18.3 乱数はI/O！

だから境界に押し出す🚪✨乱数は `Math.random()` で取れて便利だけど、テスト視点では「外部依存」っぽい存在です🎲🧊
`Math.random()` 自体は **0以上1未満の数を返す**けど、**暗号用途には向かない**（セキュリティ用途に使わない）という注意もあります🔐⚠️ ([MDNウェブドキュメント][1])

なので設計の方針はこれ👇

* 中心ロジック：**乱数を“もらう”だけ**（＝純粋に近づく）🍰
* 外側：**本物の乱数を用意して渡す**（＝アダプタ）🔌

---

## 18.4 分離の“型”を作ろう：最小のRandomインターフェース📜🎲ここでは一番シンプルに👇



* `next()` が **0以上1未満**の number を返す、ただそれだけ✨

```ts
// src/random.ts
export interface RandomSource {
  /** 0 <= x < 1 */
  next(): number;
}

// おまけ：よく使う「整数」も関数で用意すると便利✨
export function nextInt(rng: RandomSource, maxExclusive: number): number {
  if (!Number.isInteger(maxExclusive) || maxExclusive <= 0) {
    throw new Error("maxExclusive must be a positive integer");
  }
  // rng.next() は本来 1 未満だけど、念のためクランプ（超安全）🧸
  const x = Math.min(0.999999999999, Math.max(0, rng.next()));
  return Math.floor(x * maxExclusive);
}
```

---

## 18.5 ハンズオン：くじ引きロジックをテスト可能にする🎁

🧪### 18.5.1 まず“悪い例”😱（直 `Math.random()`）

```ts
// src/lottery_bad.ts
export function drawPrizeBad(prizes: string[]): string {
  const i = Math.floor(Math.random() * prizes.length);
  return prizes[i];
}
```

これ、テストで「特定の景品が選ばれる」状況を作りにくいです😵‍💫

---

### 18.5.2 “良い例”：乱数を注入して、中心を安定させる🎯✨

```ts
// src/lottery.ts
import { RandomSource, nextInt } from "./random";

export function drawPrize(prizes: readonly string[], rng: RandomSource): string {
  if (prizes.length === 0) throw new Error("prizes must not be empty");
  const i = nextInt(rng, prizes.length);
  return prizes[i];
}
```

ポイントは「中心が `Math.random()` を知らない」こと🏠✨

---

### 18.5.3 外側：本物の乱数アダプタを用意🎲🔌

```ts
// src/random_math.ts
import { RandomSource } from "./random";

export class MathRandom implements RandomSource {
  next(): number {
    return Math.random();
  }
}
```

---

### 18.5.4 テスト用：固定乱数（テストダブル）

を作る🧸🎲

```ts
// test/helpers/fixedRandom.ts
import { RandomSource } from "../../src/random";

export class FixedRandom implements RandomSource {
  private i = 0;

  constructor(private readonly values: number[]) {}

  next(): number {
    if (this.i >= this.values.length) {
      throw new Error("FixedRandom exhausted");
    }
    const v = this.values[this.i++];
    if (!(0 <= v && v < 1)) {
      throw new Error("FixedRandom values must be in [0, 1)");
    }
    return v;
  }
}
```

---

### 18.5.5 テストを書く（例：Vitest）

🧪🎉Vitest は v4 系が公開されていて（4.0の告知も出てます）今どきの構成で使いやすいです💨 ([Vitest][2])



```ts
// test/lottery.test.ts
import { describe, it, expect } from "vitest";
import { drawPrize } from "../src/lottery";
import { FixedRandom } from "./helpers/fixedRandom";

describe("drawPrize", () => {
  it("rng=0.0 なら先頭が選ばれる🎁", () => {
    const rng = new FixedRandom([0.0]);
    const prize = drawPrize(["A", "B", "C"], rng);
    expect(prize).toBe("A");
  });

  it("rngが大きい値なら後ろが選ばれる🎯", () => {
    const rng = new FixedRandom([0.999999]);
    const prize = drawPrize(["A", "B", "C"], rng);
    expect(prize).toBe("C");
  });
});
```

これでテストが**毎回100%同じ結果**になります😆✅

---

## 18.6 もう一段リアル：重み付きガチャ（確率テーブル）

🎰✨「SSR 5%！」みたいなの、よくありますよね😂🎀
でもテストで「SSRが出るまで回す」はやっちゃダメです🙅‍♀️（不安定すぎる）

### 18.6.1 実装（重みで区間を作って選ぶ）

📏🎲

```ts
// src/weighted.ts
import { RandomSource } from "./random";

export type Weighted<T> = { value: T; weight: number };

export function drawWeighted<T>(items: readonly Weighted<T>[], rng: RandomSource): T {
  if (items.length === 0) throw new Error("items must not be empty");

  const total = items.reduce((sum, x) => sum + x.weight, 0);
  if (total <= 0) throw new Error("total weight must be > 0");

  const r = rng.next() * total; // 0 <= r < total
  let acc = 0;

  for (const item of items) {
    if (item.weight < 0) throw new Error("weight must be >= 0");
    acc += item.weight;
    if (r < acc) return item.value;
  }

  // 浮動小数の誤差お守り🧸（理屈上ここには来ない想定）
  return items[items.length - 1].value;
}
```

### 18.6.2 テスト：狙って各景品を当てる🎯🧪

```ts
// test/weighted.test.ts
import { describe, it, expect } from "vitest";
import { drawWeighted } from "../src/weighted";
import { FixedRandom } from "./helpers/fixedRandom";

describe("drawWeighted", () => {
  const table = [
    { value: "N",  weight: 70 },
    { value: "R",  weight: 25 },
    { value: "SSR", weight: 5 },
  ] as const;

  it("0.0 なら最初の区間（N）🎁", () => {
    const rng = new FixedRandom([0.0]); // r=0
    expect(drawWeighted(table, rng)).toBe("N");
  });

  it("0.7 なら境界を越えてR🎯", () => {
    const rng = new FixedRandom([0.7]); // r=70
    expect(drawWeighted(table, rng)).toBe("R");
  });

  it("0.95 ならSSR🔥", () => {
    const rng = new FixedRandom([0.95]); // r=95
    expect(drawWeighted(table, rng)).toBe("SSR");
  });
});
```

**“確率の分布”ではなく “区間の割り当てロジック” をテストする**のがコツです💡✨

---

## 18.7 よくある落とし穴あるある👀💥* **「SSRが5%だから、100回回して3〜7回出るはず！

」**みたいなテストはNG🙅‍♀️🎲
  → たまたま外れたら落ちるし、CIで地獄になります😇
* `array.sort(() => Math.random() - 0.5)` でシャッフルもNG寄り（偏りが出る話がよくある）🌀
  → シャッフルも「乱数注入 + 正しいアルゴリズム」で扱うのが吉🧠✨

---

## 18.8 セキュア乱数の話（ちょい注意）

🔐🎲* `Math.random()` は **暗号学的に安全じゃない**ので、トークンやパスワード系には使わないでね⚠️ ([MDNウェブドキュメント][1])


* ブラウザなら `Crypto.getRandomValues()` が暗号強度の強い乱数を提供します🔒 ([MDNウェブドキュメント][3])
* Node.js 側なら `node:crypto` の `randomInt` が使えます（範囲 `[min, max)` の整数を返して、modulo bias 回避の説明もあります）🎲✨ ([Node.js][4])

※ただし！この章の主役は「テストを安定させる設計」なので、まずは **注入できる形にする**のが勝ちです🏆

---

## 18.9 ちょい未来メモ：seed付き乱数の提案もあるよ🌱🎲JS/TS界隈では「seed付き乱数」の仕様提案も進んでます（同じseedなら同じ乱数列が出て再現できるやつ）

🌈 ([GitHub][5])
でも「今この瞬間に確実に使える設計」は、今日やった **RandomSource注入**が最強です💪✨

---

## 18.10 AI（Copilot/Codex）

に頼むときのプロンプト例🤖🎀コピペでOKだよ〜👇



* **インターフェース設計を出してもらう**

  * 「TypeScriptで乱数を注入可能にしたい。`RandomSource` interface と、`MathRandom` adapter、`FixedRandom` テストダブルを作って。`next(): number` は 0<=x<1 を返す前提で。」

* **テストケース洗い出し**

  * 「重み付き抽選ロジック（累積重み）で、境界 `r=70` や `r=95` を確実に通すテストケースを考えて。」

AIの出力は便利だけど、**境界の引き方（中心に `Math.random` を入れない）**だけは自分が握ってね✋✨

---

## 18.11 章末ミニ課題📚💖1. `drawPrize` に「景品が空ならエラー」を入れて、テストも追加しよう😆✅
2. `drawWeighted` を使って「3段階の割引（0〜0.5→5%、0.5〜0.9→10%、0.9〜→20%）」を実装してテストしよう💸🎯
3. （余裕あれば）`shuffle(items, rng)` を作って、FixedRandomで並び替え結果を固定してテストしてみよう🃏✨

---

必要なら次は、「Seed付き疑似乱数（テスト専用PRNG）」を自作して、テストで“ランダムっぽい入力を大量生成しつつ再現可能”にするやつも一緒にやれるよ🌱🎲

[1]: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Math/random?utm_source=chatgpt.com "Math.random() - JavaScript - MDN Web Docs"
[2]: https://vitest.dev/blog/vitest-4?utm_source=chatgpt.com "Vitest 4.0 is out!"
[3]: https://developer.mozilla.org/ja/docs/Web/API/Crypto/getRandomValues?utm_source=chatgpt.com "Crypto: getRandomValues() メソッド - Web API | MDN"
[4]: https://nodejs.org/api/crypto.html "Crypto | Node.js v25.3.0 Documentation"
[5]: https://github.com/tc39/proposal-seeded-random?utm_source=chatgpt.com "tc39/proposal-seeded-random"
