# 第41章：依存って何？（時間・乱数・I/O）⏰🎲

![不安定な地盤](./picture/tdd_ts_study_041_shaky_ground.png)

## 🎯この章のゴール

* 「テストが不安定になる原因＝依存」を、**自分の言葉で説明**できる🙂✨
* コードを見て、**依存（時間・乱数・I/O）を嗅ぎ分けてリスト化**できる👃📝
* 「どこを切り分ければテストしやすくなるか」を**見取り図で描ける**🗺️💡

---

## 📚今日の主役：「依存」ってなに？🤔

ざっくり言うと…

> **同じ入力でも、結果がブレる原因になる “外の世界”** 🌍⚡️

たとえば👇

* ⏰ **時間**：`new Date()` / `Date.now()` / タイマー（`setTimeout`）\n\n![Chaos Elements](./picture/tdd_ts_study_041_chaos_elements.png)
* 🎲 **乱数**：`Math.random()` / `crypto.getRandomValues()`
* 🌐 **I/O**：ファイル読み書き / ネット（`fetch`）/ DB / localStorage
* 🧊 **環境**：`process.env` / OSの設定 / グローバル状態

依存が多いほど、テストはこうなりがち😇

* 「たまに落ちる（フレーク）」💥\n\n![Flaky Balance](./picture/tdd_ts_study_041_flaky_balance.png)
* 遅くなる🐢
* 再現しない😵‍💫

テストの安定が崩れると、TDDのテンポが死ぬ…！なので **まず“依存を見つける目”** を作るよ🧪✨

---

## 🧠なぜ依存がヤバいの？（超イメージ）💣

![画像を挿入予定](./picture/tdd_ts_study_041_dependency_snake.png)

TDDで嬉しいのは「**同じことをしたら、いつも同じ結果**」だから安心して進められるところ😊

でも依存があると👇

* ⏰「今が何時か」で結果が変わる
* 🎲「たまたま」で結果が変わる
* 🌐「ネット/ファイル」が気分で失敗する

これがフレークの王道パターンだよ👑💥（まずは“隔離して安定化”が基本になる）([Trunk][1])

---

## 🔍依存を見つける“依存レーダー”📡✨\n\n![Dependency Radar](./picture/tdd_ts_study_041_dependency_radar.png)

コードを読んだら、次の質問を自分に投げてみてね👇

### ✅質問1：「同じ引数で、毎回同じ結果？」♻️

* YES → たぶんテストしやすい💕
* NO → どこかに依存が潜んでる😈

### ✅質問2：「この関数、外の世界を触ってない？」🕵️

チェックリスト（見つけたら丸つけてOK）👇

* ⏰ `Date` / `setTimeout` / `setInterval`
* 🎲 `Math.random` / `crypto`
* 🌐 `fetch` / HTTPクライアント
* 📁 `fs` / ファイルパス
* 🧠 グローバル変数 / シングルトン
* 🧪 `process.env` / 実行環境依存
* 🧵 並列実行で競合しそうな共有状態

### ✅質問3：「失敗した時、ログが“外部要因”っぽい？」📉

* “タイミング次第”っぽい
* “たまに”
* “CIだけ落ちる”
  → 依存が濃厚🫠

---

## ⏰依存①：時間（Time）を見抜くコツ\n\n![Time Dependency](./picture/tdd_ts_study_041_time_bomb.png)

時間が絡むと、**テストは一気に不安定**になりやすい💥

よくある時間依存👇

* 「今日がセール日なら割引」📅
* 「30秒経ったらリトライ」⏱️
* 「締切を過ぎたらエラー」⌛️

Vitestには “時間を固定する道具” があるよ🪄

* `vi.setSystemTime(...)` で「今」を固定できる（ただし**自動でリセットされない**ので注意！）([Vitest][2])
* `vi.useFakeTimers()` を使うとタイマーだけじゃなく **Dateの時間にも影響**がある（ここも注意ポイント）([Vitest][2])

> ただし！この章では「固定の仕方」より **“時間が依存になってるのを見つける”** が目的だよ😊
> （固定や注入は次章で気持ちよくやる💖）

---

## 🎲依存②：乱数（Random）を見抜くコツ\n\n![Random Dependency](./picture/tdd_ts_study_041_dice_roll.png)

乱数は “毎回違う” が本質だから、そのままユニットテストに入れると事故る😇

* `Math.random()` は一般に PRNG で、用途によっては不向き（とくにセキュリティ用途はNG）([DeepSource][3])
* クリプト系の乱数（例：`Crypto.getRandomValues()`）は “強い乱数” を返すよ([MDN Web Docs][4])

でもテスト目線ではどっちも同じで👇

> **乱数源をそのまま使うと、期待値が固定できない**😵‍💫

だからまずは、コード中に `Math.random` や `crypto` が出たら
「🎲依存だ！」って気づければ勝ち🏆✨

---

## 🌐依存③：I/O（ファイル・ネット・DB）を見抜くコツ\n\n![I/O Turtle](./picture/tdd_ts_study_041_slow_turtle.png)

I/Oはだいたい **遅い＆壊れやすい**🐢💥

例👇

* 🌐 `fetch()`：相手が落ちる、遅い、レート制限…
* 📁 ファイル：パス違い、権限、文字コード、ロック…
* 🗄️ DB：起動してない、状態が残る、データ競合…

TDDでは基本方針がこれ👇

> **“中心のロジック” は外部から切り離し、I/Oは境界に寄せる**🧱➡️🚪

この章では「I/Oが混ざってたら黄色信号🚥」を覚えるだけでOK👌

---

## 🧪手を動かす：依存さがしトレーニング（30分）🎮✨

### ①まずは“依存まみれ関数”を読む👀

次の関数、依存がいくつあるか数えてみてね🧠💪

```ts
// coupon.ts
export function createCouponCode(userId: string) {
  // ⏰ 時間
  const ymd = new Date().toISOString().slice(0, 10).replace(/-/g, "");

  // 🎲 乱数
  const rand = Math.floor(Math.random() * 10000).toString().padStart(4, "0");

  // 🧊 環境
  const prefix = process.env.COUPON_PREFIX ?? "CP";

  return `${prefix}-${userId}-${ymd}-${rand}`;
}
```

**あなたの答え（目標）**👇

* 依存は **⏰🎲🧊 の3つ**！
* しかもこのままだと「毎回コードが変わる」→ テストがつらい🥲

---

### ②“依存マップ”を作る🗺️📝（これが提出物🎁）\n\n![Dependency Map](./picture/tdd_ts_study_041_heat_map.png)

`docs/dependency-map.md` を作って、こんな感じで書くよ👇

```md
## dependency-map（第41章）

## createCouponCode の依存
- ⏰ Time: new Date() に依存（今日の日付で結果が変わる）
- 🎲 Random: Math.random() に依存（毎回値が変わる）
- 🧊 Env: process.env.COUPON_PREFIX に依存（環境で変わる）

## リスク
- テストで期待値を固定しにくい
- CI/ローカルで挙動が変わる可能性
```

---

### ③テストを書いて “つらさ” を体験する😇（わざと！）

```ts
// coupon.test.ts
import { describe, it, expect } from "vitest";
import { createCouponCode } from "./coupon";

describe("createCouponCode", () => {
  it("クーポンコードの形式が正しい", () => {
    const code = createCouponCode("u1");
    // 形式だけなら一応テストできる（でも弱い）
    expect(code).toMatch(/^CP-u1-\d{8}-\d{4}$/);
  });
});
```

このテスト、通るかもだけど…
「値そのもの」を固定できないから、仕様が弱い感じになるよね🥺💦
（ここが “依存を切りたい欲” が育つポイント🌱✨）

---

## 🤖AIの使いどころ（この章はここが最強）💪🤖

AIには「実装を書かせる」よりも、まず **依存検出** をやらせるのが超相性いいよ💕

コピペ用プロンプト👇

```text
このTypeScript関数の「依存（時間・乱数・I/O・環境・グローバル状態）」をすべて列挙して、
それぞれがテストを不安定にする理由を1行で説明して。
最後に、依存を注入できる形にする“最小の方針”を3案（小/中/大）で出して。
```

ポイントは「列挙 → 理由 → 方針案」まで一気に出すこと🧠✨
（次章で “方針案” を実際に手でやるよ！）

---

## ✅チェック（ここまでできたら合格💮）

* [ ] コードを見て、`Date` / `Math.random` / `fetch` / `fs` / `process.env` を **依存として指摘**できる🔍
* [ ] 依存を **⏰🎲🌐🧊** みたいにカテゴリ分けして書ける🗂️
* [ ] 「このテストが弱い理由＝依存で期待値が固定できない」を説明できる🗣️✨

---

## 🌟次章の予告（第42章）📦➡️

次は今日見つけた依存を、**関数引数DI（注入）**で差し替え可能にして、
テストを **“気持ちよく安定”** させるよ〜〜〜！🥳🧪

* ⏰ Clockを注入して時間を固定
* 🎲 Randomを注入して乱数を固定
* 🌐 I/Oを境界に押し出す

ここから一気に「TDDって楽しい💕」に入っていくよ😉✨

[1]: https://trunk.io/learn/best-practices-for-finding-and-mitigating-flaky-tests?utm_source=chatgpt.com "Best Practices for Finding and Mitigating Flaky Tests"
[2]: https://vitest.dev/guide/mocking?utm_source=chatgpt.com "Mocking | Guide"
[3]: https://deepsource.com/blog/dont-use-math-random?utm_source=chatgpt.com "Don't use Math.random()"
[4]: https://developer.mozilla.org/ja/docs/Web/API/Crypto/getRandomValues?utm_source=chatgpt.com "Crypto: getRandomValues() メソッド - Web API | MDN"
