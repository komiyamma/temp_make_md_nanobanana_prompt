# 第31章：ベイビーステップ（詰まらない進め方）👶

![ベイビーステップ](./picture/tdd_ts_study_031_baby_steps.png)

## 🎯この章のゴール

* 「詰まった…😵‍💫」を **前進に変える手順** を持つ
* 仕様を **“超小さいテスト”に分解** して、Red→Green→Refactor を回し続けられる
* 失敗してもダメージゼロで戻れる（＝メンタル最強）💪😌✨

---

## 🧠ベイビーステップってなに？（超かんたんに）

**“2〜5分で終わる単位”に切って、成功したら保存（コミット）✅ できなかったら即リセット🔙**
この「時間の縛り」があるから、無理な大改造をしなくなって、ちゃんと進むよ〜👶✨

有名なやり方の1つが **“2分でテスト＋実装を終わらせる。無理ならリバートして、もっと小さい振る舞いにする”** って流れ（Coding Dojoとかでよくやるやつ）だよ⏱️🧸 ([Adrian Bolboaca][1])

---

## 🌱なんで効くの？（詰まりの正体を潰す🔨）

詰まるときって、だいたいこれ👇

* 変更がデカすぎて、どこで壊したか分からない😇
* 仕様があいまいで、テストに落とせない🤔
* コードが絡まりすぎて、直すのが怖い🧟‍♀️

ベイビーステップは「小さく、確実に、戻れる」から、**“捨てる前提で試せる”** のが強い💡
ソフトウェア開発でも「小さく検証された前進のほうが、大きい一発勝負より安全」って原則があるよ〜🧩 ([softengbook.org][2])

---

## 🧪ルールは3つだけ（これだけ守ればOK）✅

1. **タイマーをかける**（最初は3分でもOK）⏱️
2. **1回で増やす仕様は“1つだけ”**（テストも1つ増やす）➕
3. **成功したら保存、失敗したら戻す**（未練ゼロ）🔙💨

---

## 🔁ベイビーステップの回し方（テンプレ）👣✨

1. **次の“1個だけ”の振る舞い**を決める（例：送料無料の条件だけ）🎯
2. タイマー開始 ⏱️
3. **Red：最小の失敗テスト**を書く 🔴
4. **Green：最小の実装**で通す 🟢
5. **Refactor：1〜2分だけ整える** 🧹
6. **コミット**（緑の状態を保存）✅
7. タイムオーバーしたら：**即リセットして、もっと小さく切り直し** 🔙✂️ ([Adrian Bolboaca][1])

---

## ✂️「小さく切れない…」時の分解ワザ 6選🧠💡

1. **具体例を1個に固定**（入力パターンを減らす）🧸
2. **条件を1個だけ導入**（ifが2個なら、まず1個）🚦
3. **境界は後回し**（まず普通のケース）🌼
4. **次元を落とす**（税計算が辛い→税なし版→税あり）🧾
5. **まず定数で通す（仮実装）**→次のテストで一般化 🩹
6. **“たった1行の変化”で通す方法を探す**（最強のベイビー）👶✨

---

## 🧪ハンズオン：送料計算を「5ベイビーステップ」で作る📦🚚✨

### ✅仕様（ちょい複雑で詰まりやすいタイプ）

`calcShipping(subtotal, isMember, isRemote)` で送料を返すよ💰

* 通常：送料 500円
* 小計が **5000円以上** なら送料無料（0円）🎉
* 会員なら：小計が **3000円以上** で送料無料、未満なら 200円
* 遠隔地 `isRemote=true` は **＋400円**（送料無料でも＋400）🏝️

---

## 0) テストの土台（ファイルだけ作る）📁

* `src/calcShipping.ts`
* `tests/calcShipping.test.ts`

（ここは“ベイビーステップ前の準備”ね😊）

---

## Step1：通常の基本（500円）🔴→🟢

### 🔴テスト（最小）

```ts
import { describe, it, expect } from "vitest";
import { calcShipping } from "../src/calcShipping";

describe("calcShipping", () => {
  it("通常は送料500円", () => {
    expect(calcShipping(1000, false, false)).toBe(500);
  });
});
```

### 🟢実装（最小）

```ts
export function calcShipping(subtotal: number, isMember: boolean, isRemote: boolean): number {
  return 500;
}
```

✅通ったらコミット！（“緑の保存ポイント”）🟢✅

---

## Step2：通常の送料無料（5000以上で0円）🎉

### 🔴テスト追加

```ts
it("通常は5000円以上で送料無料", () => {
  expect(calcShipping(5000, false, false)).toBe(0);
});
```

### 🟢実装を最小で拡張

```ts
export function calcShipping(subtotal: number, isMember: boolean, isRemote: boolean): number {
  if (subtotal >= 5000) return 0;
  return 500;
}
```

✅通ったらコミット！🟢✅

---

## Step3：会員の送料無料（3000以上で0円）🪪✨

### 🔴テスト追加

```ts
it("会員は3000円以上で送料無料", () => {
  expect(calcShipping(3000, true, false)).toBe(0);
});
```

### 🟢実装（条件を1個だけ追加）

```ts
export function calcShipping(subtotal: number, isMember: boolean, isRemote: boolean): number {
  if (isMember) {
    if (subtotal >= 3000) return 0;
    return 200;
  }

  if (subtotal >= 5000) return 0;
  return 500;
}
```

✅通ったらコミット！🟢✅

---

## Step4：会員だけど未満（200円）🧾

### 🔴テスト追加（すでに実装入ってるけど、仕様として固定するよ）

```ts
it("会員は3000円未満だと送料200円", () => {
  expect(calcShipping(2999, true, false)).toBe(200);
});
```

🟢多分この時点で通るはず！通ったらコミット！✅

---

## Step5：遠隔地は＋400（送料無料でも足す）🏝️➕

### 🔴テスト追加（普通のケース）

```ts
it("遠隔地は送料に+400される", () => {
  expect(calcShipping(1000, false, true)).toBe(900); // 500 + 400
});
```

### 🔴テスト追加（送料無料でも＋400）

```ts
it("送料無料でも遠隔地は+400される", () => {
  expect(calcShipping(5000, false, true)).toBe(400); // 0 + 400
});
```

### 🟢実装（最後に“足し込み”を1か所に寄せる）🧹

```ts
export function calcShipping(subtotal: number, isMember: boolean, isRemote: boolean): number {
  let base: number;

  if (isMember) {
    base = subtotal >= 3000 ? 0 : 200;
  } else {
    base = subtotal >= 5000 ? 0 : 500;
  }

  if (isRemote) base += 400;
  return base;
}
```

✅通ったらコミット！🎉🎉🎉

---

## 🤖AI（Copilot/Codex）に頼るときの“良い聞き方”テンプレ💬✨

### ① 分解が苦しいとき（ベイビーステップ生成）

* 「この仕様を、1回2〜3分で終わる“振る舞いの追加”に5〜8ステップで分解して。各ステップはテスト名と具体例（入力→期待値）付きで。」

### ② Redで詰まったとき（最小Green案）

* 「この失敗テストを最小変更で通す実装を2案。1案は仮実装、もう1案は一般化。差分が小さい順に。」

### ③ やりすぎ防止（Refactorの範囲）

* 「今のコードで、1〜2分で終わる安全なリファクタ候補を3つ。やりすぎになりそうな変更は却下理由も添えて。」

ポイントは、**AIに“仕様を決めさせない”** で、**分解と候補出し**に使うことだよ🤖🧸✨（最終判断はテスト＝仕様で！）

---

## 🔙リセットのやり方（Windowsで安全に）🪟🧯

ベイビーステップで大事なのは「戻れる安心感」☺️

* コミットしてあるなら：**直近の緑に戻す**（Source Controlから戻すでもOK）🔙
* コマンド派なら（例）：変更を全部捨てて戻す

```powershell
git restore .
```

（※やる前に、捨てていい変更かだけは確認ね🙏）

---

## ✅この章のチェックリスト（できたら合格💮）🧪✨

* [ ] 仕様を **5つ以上の“小テスト”** に分解できた👶
* [ ] 1ステップで増やす仕様が **1個だけ** になってる➕
* [ ] **緑になったら保存（コミット）** ができた✅
* [ ] 詰まったときに **戻して切り直す** を実行できた🔙
* [ ] “大改造したくなる衝動”を抑えられた😇🧘‍♀️

---

## 🔎（最新メモ）いまの周辺ツール事情（2026/01時点）🧭✨

* Vitest は **4.0** がメジャーとして出ていて、Browser Mode の安定化やビジュアル回帰テスト系も拡張されてるよ🧪🖥️ ([Vitest][3])
* TypeScript は **5.9** がリリース済みで、次世代（6/7）に向けた動きも進んでるよ🧩🚀 ([Microsoft for Developers][4])
* Node は **v24 が Active LTS** として案内されてる（安定運用向き）🟩 ([Node.js][5])
* VS Code 側もテスト体験（カバレッジ表示の導線など）が更新されてるよ🧰✨ ([Visual Studio Code][6])

---

必要なら次は、**「ベイビーステップ用の“詰まり診断チェックシート”」**（どこで詰まってるか→切り方が決まるやつ）も作るよ🩺📝💖

[1]: https://blog.adrianbolboaca.ro/2012/12/teddy-bear-xp-germany-2012/?utm_source=chatgpt.com "My Teddy Bear went to XP Days Germany 2012"
[2]: https://softengbook.org/chapter2?utm_source=chatgpt.com "Chapter 2: Processes – Software Engineering"
[3]: https://vitest.dev/blog/vitest-4?utm_source=chatgpt.com "Vitest 4.0 is out!"
[4]: https://devblogs.microsoft.com/typescript/announcing-typescript-5-9/?utm_source=chatgpt.com "Announcing TypeScript 5.9"
[5]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
[6]: https://code.visualstudio.com/updates?utm_source=chatgpt.com "December 2025 (version 1.108)"
