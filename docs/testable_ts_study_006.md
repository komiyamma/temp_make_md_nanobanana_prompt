# 第06章：テストランナー入門（まず1本通す）🧪🎉

![testable_ts_study_006_test_runner.png](./picture/testable_ts_study_006_test_runner.png)

この章は「テストって怖くない！」って思える成功体験を作る回だよ〜😊✨
**“超小さい純粋関数”にテストを1本通して、失敗ログの読み方まで**いっきに慣れちゃおう💪🌸

※2026年1月時点の最新寄りの前提で組んでるよ：TypeScriptは **5.9** 系のリリースノートが公開されてる（2026-01-12更新）し、Node.jsは **v24 LTS** の更新が出てる感じ！([TypeScript][1])
テストランナーは今どきの “速い＆気持ちいい” 代表として **Vitest 4系** を使うよ〜🚀（4.0が大きい節目）([Vitest][2])
（Jestも現役で、Jest 30系が安定版として案内されてるよ）([Jest][3])

---

## 6-1. 今日のゴール🎯✨

この章が終わったら、これができるようになるよ👇💖



* ✅ テストを**実行**できる（まず1本！）
* ✅ テストが**失敗したときの見方**がわかる（ここ超大事！）
* ✅ よく使う **基本アサーション** を使える（`toBe` / `toEqual` など）
* ✅ “直して緑にする”流れが体に入る（気持ちいいやつ😆🟢）

---

## 6-2. テストランナーってなに？🚦🧠テストランナーはね、超ざっくり言うと👇

![testable_ts_study_006_runner_process.png](./picture/testable_ts_study_006_runner_process.png)



* 🧪 **テストファイルを見つけて**
* ▶️ **順番に実行して**
* 📣 **成功/失敗を見やすく報告してくれる**
* 👀 さらに、**変更を監視して自動で再実行**してくれたりする（めちゃ便利！）

今回のVitestは、そういう体験がかなり気持ちいい寄りだよ〜🚀([Vitest][4])

---

## 6-3. まずは “1本” 通す（最短コース）

🏁🧪ここからハンズオン！🎮✨
（前章で作ったプロジェクトを使う想定で進めるよ）

## ① Vitest を入れる📦✨

ターミナルでプロジェクト直下に移動して、これ👇



```bash
npm i -D vitest
```

> すでにTypeScriptを入れてる想定だけど、もし未導入なら👇

```bash
npm i -D typescript
```

Vitestの導入・使い方の基本は公式ガイドにまとまってるよ📚([Vitest][4])

---

## ② テスト用のスクリプトを用意する🧷✨`package.json` の scripts に `test` を用意（コマンドで足すのが楽）

![testable_ts_study_006_npm_scripts.png](./picture/testable_ts_study_006_npm_scripts.png)

👇



```bash
npm pkg set scripts.test="vitest"
npm pkg set scripts.test:run="vitest run"
```

* `npm test`：ふだん用（開発中に気持ちいいやつ）
* `npm run test:run`：一回だけ実行（CIっぽいやつ）

---

## ③ “超小さい純粋関数” を作る🍬✨`src/sum.ts`

![testable_ts_study_006_pure_function_code.png](./picture/testable_ts_study_006_pure_function_code.png)



```ts
export function sum(a: number, b: number): number {
  return a + b;
}
```

---

## ④ テストを書く（1本でOK！

）✍️🧪`src/sum.test.ts`



```ts
import { describe, it, expect } from "vitest";
import { sum } from "./sum";

describe("sum", () => {
  it("2 + 3 = 5", () => {
    expect(sum(2, 3)).toBe(5);
  });
});
```

---

## ⑤ 実行！

![testable_ts_study_006_success_green.png](./picture/testable_ts_study_006_success_green.png)

🟢🎉

```bash
npm test
```

うまくいくと、だいたいこんな感じで「PASS」的な表示になるよ😊✨
（表示の細部は環境で違うけど、**緑っぽい成功**が出ればOK！）

---

## 6-4. わざと失敗させて「読み方」を覚える😈📣テストが書けても、**失敗ログが読めないと詰む**のでここが本番💥



## ① わざと間違える🙃`sum.ts` をこうしちゃう👇



```ts
export function sum(a: number, b: number): number {
  return a - b; // わざと！
}
```

で、`npm test` をもう一回！

---

## ② 失敗ログの “見る場所” はここ👀🔍失敗したら、注目するのはだいたいこの3点！

![testable_ts_study_006_failure_analysis.png](./picture/testable_ts_study_006_failure_analysis.png)

1. ❌ **どのテストが落ちた？**（テスト名：`2 + 3 = 5` のところ）
2. 🧾 **期待値(Expected) と 実際(Received)** の差
3. 🧭 **落ちた場所（ファイル名と行番号）** ← VS Codeでそこに飛べる✨

Vitestは差分が見やすいのが嬉しいタイプだよ〜🚀([Vitest][4])

---

## ③ 直して緑に戻す🟢✨`sum.ts` を元に戻して



```ts
export function sum(a: number, b: number): number {
  return a + b;
}
```

→ `npm test` → 🟢🎉✨

この「赤→直す→緑」が、テストの基本リズムだよ🥁💕

---

## 6-5. 基本アサーション入門（よく使うやつだけ）

![testable_ts_study_006_assertion_types.png](./picture/testable_ts_study_006_assertion_types.png)

🧰🧪ここだけ覚えれば当面戦えるよ〜！⚔️✨



## 数値・文字列の基本💡* `toBe`：**同じ**（プリミティブ向き）


* `toEqual`：**中身が同じ**（配列/オブジェクト向き）

例：

```ts
expect(1 + 1).toBe(2);
expect({ a: 1 }).toEqual({ a: 1 });
```

## 文字列チェック🪄

```ts
expect("hello world").toMatch("world");
```

## 配列チェック🍱

```ts
expect([1, 2, 3]).toContain(2);
```

## 例外（throw）

チェック💥

```ts
function boom(): void {
  throw new Error("nope");
}

expect(boom).toThrow();
expect(boom).toThrow("nope");
```

---

## 6-6. VS Codeで “気持ちよく回す” 小技💻✨* 🧪 ターミナルは **分割**して `npm test` 専用にすると快適

![testable_ts_study_006_vscode_tips.png](./picture/testable_ts_study_006_vscode_tips.png)


* 👀 失敗ログの **ファイル:行番号** をクリックして即ジャンプ
* 🔁 Vitestは開発時に “見張りながら回す” 体験が売りなので、**テストを頻繁に回す癖**がつくと強い💪([Vitest][4])

---

## 6-7. AI（Copilot/Codex）

で爆速にするコツ🤖⚡AIはこの章だと **「テストの下書き」** がめっちゃ得意🎀



## 使えるプロンプト例📝

✨* 「`sum(a,b)` のテストをVitestで1本書いて。境界値も1つ足して」


* 「この関数の仕様を短く要約して、テスト名をいい感じに3つ提案して」

## 注意ポイント🚧* AIが勝手に **仕様を盛る** ことがあるので、テスト名と期待値は自分の頭で確認ね👀✨


* まずは **1本を確実に緑** → 次に増やす、が安全だよ🟢➡️🟢🟢

---

## 6-8. 章末ミニ課題🎒🌟## 課題A：関数を1つ増やしてテスト1本✅例：`double(n)` を作って `double(3)=6` をテスト！



## 課題B：わざと失敗→ログ読む→直す🔁“赤→緑”をもう1回やるだけで、成長が確定するよ😆✨

## 課題C：`toEqual` を使う🎁

配列を返す関数を作って、`toEqual` で検証してみよ〜！

---

## 6-9. まとめ🍀

✨* テストランナーは「見つけて、実行して、報告する」係🧪📣


* まずは**1本**通すのが最強のスタート🏁
* 失敗ログは「どれが落ちた？」「期待と実際」「行番号」を見る👀
* `toBe` / `toEqual` あたりから慣れればOK👌✨

次の第7章では、テストの書き方を **AAA（Arrange/Act/Assert）** で型にして、毎回迷わないようにするよ〜📐🧪😊

[1]: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-9.html?utm_source=chatgpt.com "Documentation - TypeScript 5.9"
[2]: https://vitest.dev/blog/vitest-4?utm_source=chatgpt.com "Vitest 4.0 is out!"
[3]: https://jestjs.io/versions?utm_source=chatgpt.com "Jest Versions"
[4]: https://vitest.dev/guide/?utm_source=chatgpt.com "Getting Started | Guide"
