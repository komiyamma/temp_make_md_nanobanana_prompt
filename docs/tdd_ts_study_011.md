# 第11章：Vitest導入（成功/失敗を体験）🧪

![テスト成功](./picture/tdd_ts_study_011_check_mark.png)

「テストが動く！」と「わざと落として読める！」を今日いっぺんに体験しちゃう章だよ〜😆💕

---

## 🎯 この章のゴール

* Vitest を入れて、テストを **1本成功✅** させる
* わざと **1本失敗❌** させて、ログから原因が読めるようになる
* 「次に何を書けばいいか」を **TDDの手順で言える** ようになる🚦

---

## 📚 まず知っておくこと（超ざっくり）

* Vitest は Vite 由来の爆速テスト環境で、今は **Vitest 4 系**が主流だよ🧪⚡️（4.0 は 2025/10 公開）([Vitest][1])
* 2026/01 時点だと、安定版は **v4.0.17** が出ていて、βだと **v4.1.0-beta.1** も出てるよ（βは実験っぽいので基本は安定版でOK🙆‍♀️）([GitHub][2])
* Vitest は **Node 20+** と **Vite 6+** が必要だよ（ここが古いと詰まりやすいポイント！）([Vitest][3])

---

## 🧪 手を動かす：導入〜成功✅（まずは気持ちよく通す）

ここでは「純粋な関数」をテストするよ🧁（外部I/Oなし＝やさしい✨）

### 1) バージョン確認（30秒）⏱️

ターミナルで👇

```bash
node -v
```

`v20` 以上ならOK🙆‍♀️（Vitest の要件だよ）([Vitest][3])

---

### 2) インストール（基本これ）📦

Vitest を devDependencies に追加するよ✨ ([Vitest][3])

```bash
npm install -D vitest
```

もしここで「Vite が足りないよ〜」っぽい警告が出たら、これも足してね👇（Vitest は Vite 6+ が必要）([Vitest][3])

```bash
npm install -D vite
```

---

### 3) package.json にスクリプト追加 🧾

`package.json` の `"scripts"` をこうするよ👇 ([Vitest][3])

```json
{
  "scripts": {
    "test": "vitest",
    "test:run": "vitest run"
  }
}
```

* `npm test`：ふだん用（開発中に便利）🌀
* `npm run test:run`：1回だけ実行（CIっぽい）🏁

---

### 4) 1本「成功✅」させる（最小セット）🌱

例：`src/sum.ts`

```ts
export function sum(a: number, b: number): number {
  return a + b;
}
```

例：`tests/sum.test.ts`（tests フォルダでOK📁）

```ts
import { expect, test } from "vitest";
import { sum } from "../src/sum";

test("1 + 2 = 3 になる", () => {
  expect(sum(1, 2)).toBe(3);
});
```

実行👇

```bash
npm test
```

うまくいくと、こういう「✓」が出るよ（例）✨ ([Vitest][3])

> ✓ sum.test... / ✓ ...

そして大事ポイント👇

* テストファイル名は `.test.` か `.spec.` を含む必要があるよ（見つからない時の原因No.1！）([Vitest][3])

---

## 💥 手を動かす：わざと失敗❌させてログを読む（ここが本番）

次に「失敗ログが読める」を体験しよ〜😈🧪

`tests/sum.test.ts` に、あえて間違いの期待値を追加👇

```ts
import { expect, test } from "vitest";
import { sum } from "../src/sum";

test("1 + 2 = 3 になる", () => {
  expect(sum(1, 2)).toBe(3);
});

// わざと失敗させる❌（ログの読み方練習）
test("1 + 2 = 4 ...のはず（間違い）", () => {
  expect(sum(1, 2)).toBe(4);
});
```

もう一回実行👇

```bash
npm test
```

---

## 👀 失敗ログの読み方（これだけ見ればOK）🔍✨

失敗したとき、見る順番はこの3つだよ👇

1. **どのテスト名が落ちた？**（テスト名＝仕様の見出し📝）
2. **expected / received**（期待と実際の差分）
3. **どの行？**（ファイル名＋行番号）

これが読めるだけで、TDD が一気に楽になるよ〜🥹💕

---

## 🚦 ここでTDDにつなげる（Red→Greenの超ミニ）

今の失敗は「仕様が間違い」だから直すのはテスト側だけど、TDD っぽくするなら👇

* ✅ **正しい仕様を1つ追加**して Red にする（例：`0 + 0 = 0` とか）
* ✅ 最小実装で Green
* ✅ まとめて Refactor ✨

---

## 🤖 AI の使い方（この章で一番おいしい使い所）🍯✨

### 1) テスト雛形だけ作らせる（盛りすぎ防止）🧁

AIにこう聞く👇

* 「Vitestで `sum` のテストを *最小の1本* だけ作って。describeは不要。testとexpectだけで。」

→ 出てきたら、**余計な部分は削る✂️**（“最小化”が大事！）

### 2) 失敗ログを「日本語で1行ずつ」説明させる📣

* 「このVitestの失敗ログを、(1)どこが違う？(2)次に何を直す？の2点で説明して」

### 3) テスト名の改善案を3つ出させる📝✨

* 「このテスト名を “落ちた瞬間に原因がわかる” 名前に3案。短めで！」

---

## 🧰 よくある詰まりポイント（ここだけ見て助かって…！🧯）

### ✅ テストが0件になる😭

* ファイル名に `.test.` または `.spec.` が入ってる？（例：`sum.test.ts`）([Vitest][3])

### ✅ Node が古くて動かない🥶

* Vitest は **Node 20+** が要件だよ([Vitest][3])

### ✅ Vite の条件で怒られる😵‍💫

* Vitest は **Vite 6+** が要件だよ([Vitest][3])

### ✅ 設定ファイルで型が効かない/警告が出る💭

* `vite.config.ts` に `test:` を書くなら、先頭にこれが必要になることがあるよ👇([Vitest][3])

```ts
/// <reference types="vitest/config" />
```

---

## 🧑‍💻（おまけ）VS Code で “実行ボタンぽち” をしたい人へ🖱️✨

Vitest 公式の VS Code 拡張があって、**Run / Debug / Watch** ができるよ〜！便利😆🧪
要件はざっくり「VS Code」「Vitest」「Node」あたりが満たされてればOK（拡張の要件は README にあるよ）([GitHub][4])

---

## ✅ チェック（できたら合格🎉）

* [ ] `npm test` でテストが **1本成功✅** した
* [ ] テストを **わざと失敗❌** させた
* [ ] 失敗ログから「期待値の違い」と「落ちた行」を読めた
* [ ] “次にやること” を **テスト追加→実装→整理** の順で言えた🚦✨

---

## 🧾 ミニ提出物（1〜3コミットでOK）📌

* `test: add first passing test` ✅
* `test: add failing test to read output` ❌
* `test: fix expectation` ✅

---

次の章（Watch運用🔁）に行くと、保存した瞬間にテストが回って「気持ちよさ」が爆上がりするよ〜😆💖

[1]: https://vitest.dev/blog/vitest-4 "Vitest 4.0 is out! | Vitest"
[2]: https://github.com/vitest-dev/vitest/releases "Releases · vitest-dev/vitest · GitHub"
[3]: https://vitest.dev/guide/ "Getting Started | Guide | Vitest"
[4]: https://github.com/vitest-dev/vscode "GitHub - vitest-dev/vscode: VS Code extension for Vitest"
