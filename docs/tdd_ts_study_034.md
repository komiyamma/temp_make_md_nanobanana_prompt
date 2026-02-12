# 第34章：ミニ演習②：会計（割引・クーポン）🎟️🧾

![カフェ会計（演習）](./picture/tdd_ts_study_034_cafe_exercise.png)

## 🎯 この章のゴール

* ルールが増えても破綻しないように、**条件と結果を“表”で整理**できるようになる🙌
* その表から、**最小限で強いテストケース**を作れるようになる💪
* そして **パラメータ化テスト**でサクッと回せるようになる🔁✨（Vitestの `test.each / test.for` を使うよ） ([vitest.dev][1])

---

## まず気づいてほしい：if地獄の正体😵‍💫

ifが増えてツラくなる理由はだいたいコレ👇

* ルールが頭の中だけにあって、**全体像が見えない**🫥
* 「この条件とこの条件が同時のとき…」が増えて、**組み合わせ爆発**💥

![Combo Explosion](./picture/tdd_ts_study_034_combo_explosion.png)

* テストが「思いつき追加」になって、**抜け**と**重複**が混ざる🕳️🌀

そこで使うのが **決定表（Decision Table）** だよ📋✨
条件（Condition）× 結果（Action/Outcome）を表にして、**漏れと矛盾を見える化**するやつ！ ([BrowserStack][2])

---

## 📚 決定表の作り方（超実践テンプレ）🧷

以下の順でやると、ほぼ迷わないよ😊

1. **条件を箇条書き**（判断材料）🧠
2. **結果（やること）を箇条書き**（割引する/しない等）🎬
3. 条件の組み合わせを「列（ルール）」として並べる📊
4. 使う記号を決める（例：Y/N/—）

![Symbols YN](./picture/tdd_ts_study_034_symbols_yn.png)

   * **Y** = はい
   * **N** = いいえ
   * **—** = どっちでもいい（気にしない）🙆‍♀️
5. **各列の結果を埋める**（このルールなら何が起きる？）✅
6. 最後にチェック👀

   * 列が重複してない？
   * ありえない列が混ざってない？
   * “—”でまとめられる列がない？

---

## 🧪 例題：割引ルールを決定表にする🎟️🧾

今日は、会計の割引を例にするね（次の章の演習にもつながるやつ✨）

### ルール（文章）

* VIPは **いつでも10%OFF** 🌟
* VIPじゃない場合：

  * `percent10` クーポンは **合計が1000円以上なら10%OFF**
  * `yen100` クーポンは **合計が500円以上なら100円引き**
  * それ以外は割引なし

### 条件（Condition）

* C1: VIP？
* C2: クーポンは `percent10`？
* C3: クーポンは `yen100`？
* C4: 合計が1000円以上？
* C5: 合計が500円以上？

### 結果（Outcome）

* O1: 10%OFFする
* O2: 100円引きする
* O3: 割引なし

---

## 🗂️ 決定表（これが“全体像”！）✨

（列 = ルール R1, R2… だよ）

|                      | R1         | R2         | R3     | R4       | R5     | R6     |
| -------------------- | ---------- | ---------- | ------ | -------- | ------ | ------ |
| C1 VIP?              | Y          | N          | N      | N        | N      | N      |
| C2 coupon=percent10? | —          | Y          | Y      | N        | N      | N      |
| C3 coupon=yen100?    | —          | N          | N      | Y        | Y      | N      |
| C4 total>=1000?      | —          | Y          | N      | —        | —      | —      |
| C5 total>=500?       | —          | —          | —      | Y        | N      | —      |
| **結果**               | **10%OFF** | **10%OFF** | **なし** | **-100** | **なし** | **なし** |

ポイント💡

![VIP Column](./picture/tdd_ts_study_034_vip_column.png)

* VIPの列（R1）は他の条件が全部 **—（気にしない）** でOK。これが “表のパワー”🔥
* 「percent10 なのに 500以上？」みたいな条件は、今回のルールだと不要なので表に入れない（必要な判断だけ残す）✂️

決定表って「条件–結果の対応を見える化する」って説明されることが多いよ📋 ([Katalon][3])

---

## ✅ 決定表 → テストケースに落とすコツ（ここが勝ち筋）🏆

**コツは2つだけ！**

### ① “列＝最低1テスト”にする

R1〜R6のそれぞれを、最低1本のテストで守る🛡️

### ② 境界値は“代表値”を選ぶ

![Boundary Gap](./picture/tdd_ts_study_034_boundary_gap.png)

* `>=1000` なら：`999 / 1000` を選ぶ
* `>=500` なら：`499 / 500` を選ぶ
  （境界値はバグが出やすいからね😈）

---

## 🧪 手を動かす：パラメータ化テストにする（Vitest）🔁

Vitestは **`test.each`** でJest互換のパラメータ化テストができるし、最近は **`test.for`** も用意されてるよ（型＆TestContextと相性が良い選択肢） ([vitest.dev][1])

### ① まずはテストを書こう（決定表→ケース配列）

![Case Array](./picture/tdd_ts_study_034_case_array.png)

（1ケースに「名前」「入力」「期待」を入れると読み物になる📘）

```ts
// tests/discount.test.ts
import { describe, expect, test } from "vitest";
import { calcPayable } from "../src/discount";

type Member = "normal" | "vip";
type Coupon = "none" | "percent10" | "yen100";

const cases: Array<{
  name: string;
  total: number;
  member: Member;
  coupon: Coupon;
  expected: number;
}> = [
  // R1: VIPはいつでも10%OFF（— を具体値で代表させる）
  { name: "R1: VIPはいつでも10%OFF", total: 300, member: "vip", coupon: "none", expected: 270 },

  // R2: percent10 & >=1000 → 10%OFF（境界1000）
  { name: "R2: percent10 & 1000以上 → 10%OFF", total: 1000, member: "normal", coupon: "percent10", expected: 900 },

  // R3: percent10 & 1000未満 → 割引なし（境界999）
  { name: "R3: percent10 & 1000未満 → なし", total: 999, member: "normal", coupon: "percent10", expected: 999 },

  // R4: yen100 & >=500 → -100（境界500）
  { name: "R4: yen100 & 500以上 → -100", total: 500, member: "normal", coupon: "yen100", expected: 400 },

  // R5: yen100 & 500未満 → なし（境界499）
  { name: "R5: yen100 & 500未満 → なし", total: 499, member: "normal", coupon: "yen100", expected: 499 },

  // R6: クーポンなし → なし
  { name: "R6: クーポンなし → なし", total: 1200, member: "normal", coupon: "none", expected: 1200 },
];

// まずは test.each でOK（読みやすい！）
describe("calcPayable（決定表ベース）", () => {
  test.each(cases)("$name", ({ total, member, coupon, expected }) => {
    expect(calcPayable({ total, member, coupon })).toBe(expected);
  });
});
```

### ② 実装は“最小”で通す（Green優先）🟢

```ts
// src/discount.ts
type Member = "normal" | "vip";
type Coupon = "none" | "percent10" | "yen100";

export function calcPayable(input: { total: number; member: Member; coupon: Coupon }): number {
  const { total, member, coupon } = input;

  // R1
  if (member === "vip") return Math.floor(total * 0.9);

  // R2 / R3
  if (coupon === "percent10") {
    if (total >= 1000) return Math.floor(total * 0.9);
    return total;
  }

  // R4 / R5
  if (coupon === "yen100") {
    if (total >= 500) return total - 100;
    return total;
  }

  // R6
  return total;
}
```

---

## ✨ 仕上げ：`test.for` も知っておく（2026の“今っぽい選択肢”）🧠

![Test For Loop](./picture/tdd_ts_study_034_test_for_loop.png)

VitestのAPIには **`test.each`** のほかに **`test.for`** があって、配列ケースの扱い方が違う＆TestContextとも合わせやすいよ〜って位置づけだよ ([vitest.dev][1])

「今は `test.each` で十分」だけど、チームで統一したくなったら候補にできる👍

---

## 🤖 AIの使い方（この章は相性バツグン！）💖

AIは“表づくり”と“抜け探し”が得意だよ✨（でも最終判断はあなた🫵）

### ① 決定表のたたき台を作らせる🗂️

**プロンプト例👇**

* 「この割引ルールを、条件（Y/N/—）の決定表にして。列は最小化して、重複列がないかもチェックして」

### ② 表からテストケース候補を作らせる🧪

* 「決定表の各列を満たす代表値（境界値含む）を提案して。`999/1000` と `499/500` みたいな境界値を優先して」

### ③ “ありえない列”や“矛盾”を見つけさせる🚨

![AI Review](./picture/tdd_ts_study_034_ai_review.png)

* 「この表に矛盾（同じ条件で結果が違う列）や、到達不能な列がないかレビューして」

---

## ✅ チェックリスト（できたら合格💮）

* 決定表の列が **重複してない**（同じ条件なのに2列ある…になってない）✅
* `—` を使って **まとめられる条件をまとめた**✅
* 各列に対応するテストが **最低1本ある**✅
* 境界値（`999/1000`,`499/500`）を入れた✅
* テスト名が「仕様」になってて、落ちたら理由が分かる✅

---

## 🧸 ミニ課題（ちょい足しで強くなる）🎀

次の仕様追加を、**決定表→テスト→実装**の順でやってみてね✨

* 仕様追加：`yen100` は **合計が80円未満なら 0円に丸める（マイナス禁止）**

  * ヒント：決定表に「total < 100？」みたいな条件を足すより、**結果側（Outcome）**で「下限0」を表現する方がスッキリすること多いよ😉

---

必要なら、この章の内容を「ワークシート化」して、
✅決定表テンプレ（コピペ用）／✅AIプロンプト固定テンプレ（毎回同じ型）／✅採点基準（提出物）
まで付けた“教材パック”にもできるよ📦💕

[1]: https://vitest.dev/api/ "Test API Reference | Vitest"
[2]: https://www.browserstack.com/guide/decision-table?utm_source=chatgpt.com "What is Decision Table in Software Testing?"
[3]: https://katalon.com/resources-center/blog/decision-table-testing-guide?utm_source=chatgpt.com "Decision Table Testing: A Complete Guide"
