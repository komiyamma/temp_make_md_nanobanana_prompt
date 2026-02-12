# 第43章：スタブ（返すだけの偽物）🧸

![スタブの人形](./picture/tdd_ts_study_043_dummy_doll.png)

ねらいはシンプル！**「外部（DB/HTTPなど）なしで、ロジックだけを速く・安定してテストする」**だよ〜💨🧪

---

## 🎯 この章のゴール

* 「スタブって何？」を**一言で説明**できる🙂
* **DB/HTTPみたいな外部依存をスタブで置き換えて**、TDDを回せる🔁
* 「スタブ」と「モック/スパイ」を**混ぜずに**使い分けできる🎭

---

## 📚 学ぶこと（超やさしく）💗

### 1) スタブってなに？🧸

**スタブ＝“決まった値を返すだけの代役”**だよ！

* 本物のDBやHTTPを呼ばない
* テストの中では「この値が返ってくる前提」で話を進める
* **検証したいのは“呼ばれ方”じゃなくて“結果（戻り値）”**が中心✨

![stub_sign](./picture/tdd_ts_study_043_stub_sign.png)

### 2) ざっくり使い分け（ここ大事）⚡

* **スタブ**：返す値を固定して、結果を検証する🧸
* **スパイ**：呼ばれたか・回数・引数を“観察”する👀
* **モック**：呼ばれ方を“仕様として固定”する🎭（第44章でやるよ！）

![stub_spy_mock](./picture/tdd_ts_study_043_stub_spy_mock.png)

Vitestの `vi.fn()` や `vi.spyOn()` / `vi.mock()` は公式のモック系APIの中心だよ〜📌 ([Vitest][1])

---

## 🧪 手を動かす（ミニ題材：会員割引💳✨）

### 🧩 お題

「ユーザーのポイントを見て割引率を決める」

* 0〜99点 → 0%
* 100〜499点 → 5%
* 500点〜 → 10%

ポイント取得は本来DBだけど、今回は **スタブで置き換える**よ🧸

![replace_heavy](./picture/tdd_ts_study_043_replace_heavy.png)

---

## ① まずはテストを書く（Red）🚦🔴

**tests/discount.test.ts**

```ts
import { describe, it, expect } from "vitest";
import { calcDiscountRate, type PointsRepository } from "../src/discount";

describe("calcDiscountRate", () => {
  it("0〜99点なら割引0%", async () => {
    const repoStub: PointsRepository = {
      getPoints: async () => 20, // ← 返すだけ🧸
    };

    const rate = await calcDiscountRate("u1", repoStub);
    expect(rate).toBe(0);
  });

  it("100〜499点なら割引5%", async () => {
    const repoStub: PointsRepository = {
      getPoints: async () => 120,
    };

    const rate = await calcDiscountRate("u1", repoStub);
    expect(rate).toBe(5);
  });

  it("500点以上なら割引10%", async () => {
    const repoStub: PointsRepository = {
      getPoints: async () => 800,
    };

    const rate = await calcDiscountRate("u1", repoStub);
    expect(rate).toBe(10);
  });
});
```

ポイント：

* スタブは **「返す値」しか持たない**（余計なことしない）🧸✨

![simple_return](./picture/tdd_ts_study_043_simple_return.png)
* この段階ではDBゼロ！ネットゼロ！超安定！🧪💕

---

## ② 最小の実装（Green）✅🟢

**src/discount.ts**

```ts
export type PointsRepository = {
  getPoints(userId: string): Promise<number>;
};

export async function calcDiscountRate(
  userId: string,
  repo: PointsRepository
): Promise<number> {
  const points = await repo.getPoints(userId);

  if (points >= 500) return 10;
  if (points >= 100) return 5;

![points_logic](./picture/tdd_ts_study_043_points_logic.png)
  return 0;
}
```

---

## ③ リファクタ（Refactor）🧹✨

ここでは「テストはそのまま」「実装だけ読みやすく」を意識するよ〜🙂

たとえば条件を表っぽくしたいなら（やりすぎ注意だけど💦）：

```ts
const rules = [
  { min: 500, rate: 10 },
  { min: 100, rate: 5 },
  { min: 0, rate: 0 },
] as const;

export async function calcDiscountRate(userId: string, repo: PointsRepository) {
  const points = await repo.getPoints(userId);
  return rules.find(r => points >= r.min)!.rate;
}
```

---

## 🧪 もう一段：`vi.fn()` で“関数スタブ”にする版🧸🪄

「オブジェクト丸ごと作るの面倒〜」って時、関数だけスタブにするのもアリ！

```ts
import { describe, it, expect, vi } from "vitest";
import { calcDiscountRate } from "../src/discount";

describe("calcDiscountRate (vi.fn stub)", () => {
  it("スタブ関数で点数を返す", async () => {
    const getPointsStub = vi.fn(async () => 120);

![magic_wand](./picture/tdd_ts_study_043_magic_wand.png)

    const repoStub = { getPoints: getPointsStub };
    const rate = await calcDiscountRate("u1", repoStub);

    expect(rate).toBe(5);
  });
});
```

ここでの注意⚠️

* **スタブの章なので**「呼ばれた回数チェック」は基本やらない🙅‍♀️
  （それはスパイ/モックの領域！第44章で気持ちよくやろう🎭✨）

---

## 🧠 スタブ設計の“ちょうどよさ”ルール📏💕

### ✅ 良いスタブ

* 返す値がシンプル（固定）🧸
* テストごとに意図が見える（「120点だから5%」みたいに）🙂
* 状態を持たない（持つなら注意してリセット）🧯

### ❌ ダメになりがちなスタブ

* スタブの中にロジックが増えて「もう本物じゃん…」ってなる😵‍💫

![clean_vs_messy](./picture/tdd_ts_study_043_clean_vs_messy.png)
* 使い回しで状態が残って、テストがたまに落ちる💥
* “呼ばれ方”までテストし始めて、モックと混線する🎭🌀

---

## 🤖 AIの使いどころ（この章の勝ちパターン）🤖✨

### 🪄 その1：スタブ案を作らせる

「PointsRepository のスタブを3種類（固定値/境界値/異常値）で作って」って頼む💗

### 🪄 その2：テストケースの抜け探し

「この仕様で抜けやすい境界値を列挙して」→ 100/499/500 あたりを出してもらう🎯

### 🪄 その3：スタブが“賢くなりすぎ”警報🚨

「このスタブ、やりすぎ？テストの意図が薄くなる点ある？」って聞く🙂

---

## ✅ チェック（できたら合格〜！）🎉

* スタブを使って **DB/ネット無しで**テストが回ってる🧪✨
* テストは **戻り値（結果）** を見てる（呼ばれ方を見てない）👀❌
* テストが速い！気持ちいい！🔁⚡
* スタブが“本物っぽく”なりすぎてない🧸💦

---

## 🌟 おまけ：2026年1月時点の「環境ネタ」ちょいメモ🪟🧑‍💻

* TypeScript は 5.9 が “現在の最新” として案内されてるよ（公式サイト＆downloadページ＆npm）([typescriptlang.org][2])
* Vitest は 4.0 のメジャーが出てる（公式ブログ）([Vitest][3])
* Node.js は v24 系が Active LTS 扱いで、2026-01-13 に 24.13.0 (LTS) のリリースが出てるよ([Node.js][4])

---

## 👉 次（第44章）予告🎭📣

次はついに **モック/スパイ**！
「通知した？ログ吐いた？イベント飛ばした？」みたいな **“呼ばれ方を仕様にする”** をやるよ〜😍✨

[1]: https://vitest.dev/guide/mocking?utm_source=chatgpt.com "Mocking | Guide"
[2]: https://www.typescriptlang.org/?utm_source=chatgpt.com "TypeScript: JavaScript With Syntax For Types."
[3]: https://vitest.dev/blog/vitest-4?utm_source=chatgpt.com "Vitest 4.0 is out!"
[4]: https://nodejs.org/en/blog/release/v24.13.0?utm_source=chatgpt.com "Node.js 24.13.0 (LTS)"
