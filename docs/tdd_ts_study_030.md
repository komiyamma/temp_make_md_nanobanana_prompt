# 第30章：テスト側リファクタ（読み物として整える）🧹

![テストコードの掃除](./picture/tdd_ts_study_030_broom.png)

## 🎯 目的

* **テストを「仕様書として読める文章」にする**📖💕
* **重複を減らしつつ、意図はむしろハッキリ**させる🧠✨
* **失敗したときに“どの約束が破れたか”が一瞬で分かる**ようにする💥👀

---

## まず大事な前提（超重要）🚦

* **リファクタは “Greenのあと”** ✅
  つまり「テストも実装も全部通ってる状態」でやるやつだよ😊
* テスト側リファクタでやるのは **「意味を変えない」整形**だけ🧼
  （“仕様を変える”のは次の章や次のサイクルで✨）

---

## 今日の合言葉：DRYよりDAMP 🧴🌱

* アプリのコード：重複は悪になりがち（DRY）
* **テストコード：説明力が正義（DAMP＝Descriptive And Meaningful Phrases）**
  → **同じ言葉を繰り返すことが、仕様の強調になる**こともあるよ🫶

なので第30章はこれ👇
✅ **“共通化しすぎない”**
✅ **読めることを優先**
✅ **でもコピペ地獄は卒業** 🎓✨

---

## よくある「読みにくいテスト」あるある😵‍💫

* テスト名が `test1` とか `should work` とか…何が仕様？😇
* Arrangeが長すぎて、**何を試したいのか行方不明**🫥
* `beforeEach` に隠しすぎて、**条件が見えない**🕵️‍♀️
* 期待値が雑で、落ちたときのヒントゼロ🥲

---

## 🧪 ハンズオン：汚テストを「読み物」にする（Before → After）✨

題材：`calcTotalYen()`（税込み・値引き・下限0の計算をする関数）
※中身はもう出来ててテストも通ってる想定でOKだよ😊

---

## ① Before：動くけど読めないテスト😇（ありがち）

```ts
import { describe, it, expect } from "vitest";
import { calcTotalYen } from "../src/calcTotalYen";

describe("calcTotalYen", () => {
  it("test1", () => {
    const result = calcTotalYen({
      baseYen: 1000,
      taxRate: 0.1,
      discountYen: 0,
    });
    expect(result).toBe(1100);
  });

  it("test2", () => {
    const result = calcTotalYen({
      baseYen: 1000,
      taxRate: 0.1,
      discountYen: 100,
    });
    expect(result).toBe(1000);
  });

  it("test3", () => {
    const result = calcTotalYen({
      baseYen: 1000,
      taxRate: 0.1,
      discountYen: 2000,
    });
    expect(result).toBe(0);
  });
});
```

問題点👀

* `test1/test2/test3` が **仕様を語ってない**
* 数字が並んでるだけで **ルールが見えない**
* ケースが増えたらコピペ祭り確定🎆

---

## ② After：仕様が読めるテスト📘✨（おすすめ形）

ポイントはこの3つ💡

1. **テスト名を“約束”で書く**
2. **差分だけが見えるArrange**にする
3. **it.each（パラメータ化）で“同じ仕様の繰り返し”を整理**

Vitestは `test.each` / `it.each` が使えるよ🧪（同じテストをデータ違いで回せるやつ） ([Vitest][1])

```ts
import { describe, it, expect } from "vitest";
import { calcTotalYen } from "../src/calcTotalYen";

type Args = Parameters<typeof calcTotalYen>[0];

// ✅ “差分だけ見える”土台（共通化しすぎないのがコツ）
const baseArgs = (over: Partial<Args> = {}): Args => ({
  baseYen: 1000,
  taxRate: 0.1,
  discountYen: 0,
  ...over,
});

describe("calcTotalYen", () => {
  describe("税込み計算", () => {
    it("base=1000, tax=10% のとき 1100円になる", () => {
      const result = calcTotalYen(baseArgs());
      // ✅ Vitestは expect の第2引数に “失敗時メッセージ” を入れられるよ✨
      expect(result, "税込み(1000 * 1.1) は 1100 のはず").toBe(1100);
    });
  });

  describe("値引き", () => {
    it.each([
      { discountYen: 0, expected: 1100, label: "値引きなし" },
      { discountYen: 100, expected: 1000, label: "100円引き" },
    ])("$label のとき expected=$expected", ({ discountYen, expected }) => {
      const result = calcTotalYen(baseArgs({ discountYen }));
      expect(result, `discountYen=${discountYen} の結果`).toBe(expected);
    });
  });

  describe("下限0（マイナスにならない）", () => {
    it("値引きが大きすぎても 0円で止まる", () => {
      const result = calcTotalYen(baseArgs({ discountYen: 2000 }));
      expect(result, "合計がマイナスなら 0 に丸める").toBe(0);
    });
  });
});
```

✅ 改善されたこと🎉

* describe が **章立て**になって、仕様が目に入る📚
* `baseArgs({ discountYen: 100 })` みたいに **差分が1行**でわかる✨
* `it.each` で同系統のケースが **読みやすく増やせる**🧪 ([Vitest][1])
* `expect(actual, "メッセージ")` で、落ちたときのヒントが強い💪（Vitestの仕様だよ） ([Vitest][2])

---

## 🧠 テスト側リファクタの「安全な手順」🛡️✨

おすすめの順番はこれ👇（事故りにくいよ😊）

1. **テスト名を直す**📝

   * `何をしたら / どうなる` を文章にする
2. **AAAに整える**🧱

   * Arrange（準備）
   * Act（実行）
   * Assert（確認）
3. **“重複の種類”を見分ける**👀

   * **データの重複** → `baseArgs()` みたいな薄いヘルパーでOK
   * **手順の重複** → まずは放置でもOK（隠すと読みにくくなること多い）
4. **パラメータ化できるところだけ it.each**🔁

   * “同じルールの入力違い” だけね！（違うルールまで混ぜない）
5. **失敗時メッセージを足す**💬✨

   * 「何の約束が破れた？」が出ると神👼
6. 必要なら **カスタムMatcher**（やりすぎ注意！）🎭

   * Vitestは `expect.extend` で拡張できるよ ([Vitest][3])

---

## 🙅‍♀️ 共通化しすぎチェック（ここ超大事）🚨

次の匂いが出たら、共通化をやめるサイン💡

* ヘルパーの中でさらにヘルパー呼んでて **追跡がだるい**🌀
* `beforeEach` が長くて **テスト本文がスカスカ**🍃
* “そのテストに必要な条件” が本文から見えない🫥
* 失敗ログを見ても「え、何が起きたの？」ってなる😇

テストって **読者（未来の自分＆仲間）** がいる文章だからね📘💕

---

## 🤖 AIの使い方（第30章向けテンプレ）✨

AIはめっちゃ相性いい章だよ😍（ただし判断は自分！）

## 1) 命名だけ助けてもらう📝

* 「このテストの意図を日本語1文にして」
* 「describe/itの名前案を5つ出して。誤解が少ない順に並べて」

## 2) 共通化しすぎ警察👮‍♀️

* 「このリファクタ案、意図が隠れてない？隠れてるなら指摘して」
* 「beforeEachに寄せた場合のデメリットを列挙して」

## 3) it.each 化の仕分け🧪

* 「同じルールとして it.each にまとめていいケースだけ選んで。混ぜたら危険なものも教えて」

---

## ✅ チェックリスト（合格ライン）💮✨

* [ ] テスト名だけ見て仕様が想像できる🙂
* [ ] Arrangeは“差分だけ”が目に入る👀
* [ ] `it.each` は「同じルール」の範囲で使えてる🔁 ([Vitest][1])
* [ ] 落ちたときに「何の約束が破れたか」分かる（メッセージ or 命名）💥 ([Vitest][2])
* [ ] 共通化しすぎて本文がスカスカになってない🌿

---

## 🧾 第30章の“提出物”イメージ（3コミットでOK）📦✨

* ✅ commit1: `test: テスト名を仕様表現にする`
* ✅ commit2: `refactor(test): AAA整形 + baseArgs導入`
* ✅ commit3: `refactor(test): it.eachで同ルールを整理` ([Vitest][1])

---

## 🔥 おまけ：最新ツール周りの注意（軽くでOK）

* Vitestは 4.0 が出ていて、メジャーアップデート時は migration をチラ見すると安心だよ🧭 ([Vitest][4])
* NodeはLTS系が継続更新されていて、セキュリティリリースも出るから、たまにアップデートしてね🔒✨ ([Node.js][5])
* TypeScriptも5.9系のリリースノートが公開されてるよ📌 ([TypeScript][6])

---

次、もしよければ😊✨
あなたの「今いちばん読みにくいテスト」を（そのまま貼って）くれたら、**第30章のルールで“読み物化”**を一緒にやるよ🧹📘💕

[1]: https://vitest.dev/api/?utm_source=chatgpt.com "Test API Reference"
[2]: https://vitest.dev/api/expect.html?utm_source=chatgpt.com "expect"
[3]: https://vitest.dev/guide/extending-matchers?utm_source=chatgpt.com "Extending Matchers | Guide"
[4]: https://vitest.dev/blog/vitest-4?utm_source=chatgpt.com "Vitest 4.0 is out!"
[5]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
[6]: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-9.html?utm_source=chatgpt.com "Documentation - TypeScript 5.9"
