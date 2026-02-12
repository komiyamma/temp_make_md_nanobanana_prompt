# 第02章：Red→Green→Refactor を1回体験🚦

![TDDサイクル](./picture/tdd_ts_study_002_cycle.png)

この章は「TDDって結局なにするの？」を、**1回だけ**ちゃんと回して “体に覚えさせる” 回だよ〜😊💕

---

## 🎯 この章でできるようになること

* **Red / Green / Refactor** を、口じゃなくて手で説明できる✋✨
* 「失敗させる」＝「バグらせる」じゃなくて、**仕様を確認する**って感覚がわかる🧠💡
* **Greenで作り込みすぎない**（ここ超大事！）🛑💚

---

## 🧰 今日つくる超ミニ題材：足し算 `add(a, b)` ➕➕

Vitest公式の “足し算テスト” を、TypeScriptでやる感じだよ🧁
（Vitestは今 v4 系が案内されてて、`vitest` は基本 watch、1回だけ回すなら `vitest run` って書き分けが公式にあるよ📌） ([Vitest][1])

---

## 0) まずは「テストが動く状態」を作る🛠️

> ここは最小だけ！設定沼は後の章でじっくりやるよ😊

1. 適当なフォルダを作って VS Code で開く📁
2. ターミナルでこれ👇

```bash
npm init -y
npm i -D vitest typescript
npx tsc --init
```

Vitestは **Node 20以上**が必要で、Vite 6以上に依存するよ〜って公式に書いてあるよ📌 ([Vitest][1])
（NodeはLTS運用が安定。直近だと Node 24 系がLTSとして案内されてるよ） ([Node.js][2])

次に `package.json` の scripts をこうする👇（最小！）

```json
{
  "scripts": {
    "test": "vitest",
    "test:once": "vitest run"
  }
}
```

* `npm run test`：基本 watch（保存したら勝手に回って気持ちいいやつ）🔁 ([Vitest][1])
* `npm run test:once`：CIみたいに1回だけ回す🏁 ([Vitest][1])

---

## 1) Red：まず「ちゃんと失敗するテスト」を作る🔴🧨

![ red state todo](./picture/tdd_ts_study_002_red_state_todo.png)

ここ、初心者がやりがちなのが
❌「テストが動かない（importできない等）」
❌「エラーが別の理由」
…みたいな “事故レッド” 😵‍💫

今日は **意味のあるレッド**＝「仕様に合ってないから落ちる」を作るよ✨

### ファイルを作る📄

`src/add.ts`

```ts
export function add(a: number, b: number): number {
  throw new Error("TODO: implement add");
}
```

`src/add.test.ts`（`.test.` が必要だよ〜って公式に書いてある📌） ([Vitest][1])

```ts
import { describe, it, expect } from "vitest";
import { add } from "./add";

describe("add", () => {
  it("1と2を足すと3になる", () => {
    expect(add(1, 2)).toBe(3);
  });
});
```

### テスト実行▶️

```bash
npm run test
```

✅ ここで落ちたら **Red成功**🎉
ポイントは「落ち方」が **読める** こと！

* “TODO: implement add” が出てる
  → **実装がまだ**っていう、超わかりやすい失敗💡

---

## 2) Green：最小の実装で通す🟢🌱

![ green state minimal](./picture/tdd_ts_study_002_green_state_minimal.png)

ここでの合言葉は👇

### 「勝つまで最短、盛るのは後」🏃‍♀️💨

`src/add.ts` をこうする👇

```ts
export function add(a: number, b: number): number {
  return a + b;
}
```

保存したら watch が走って ✅ になるはず！🥳
（もし watch じゃなければもう一回 `npm run test` でOK）

### 💚 Greenでやっちゃダメ例（あるある😇）

![ anti pattern overengineering](./picture/tdd_ts_study_002_anti_pattern_overengineering.png)

* 将来の拡張を考えてオプション引数・配列対応…とか始める
* 例外設計を凝り始める
* 入力チェックを過剰に盛る

👉 それ、**次のテストが要求してから**でいいよ😊

---

## 3) Refactor：仕様を変えずに、読みやすくする🧼✨

![ refactor state cleanup](./picture/tdd_ts_study_002_refactor_state_cleanup.png)

Refactor は「機能追加」じゃなくて、**掃除**🧹
テストが守ってくれるから、安心して整えられるよ💕

今回の例だと実装は十分シンプルだから、Refactorはテスト側を少しだけ “読み物” に寄せよう📘

### ✅ テストを読みやすく（AAAっぽく）整える

![ aaa pattern](./picture/tdd_ts_study_002_aaa_pattern.png)

```ts
import { describe, it, expect } from "vitest";
import { add } from "./add";

describe("add", () => {
  it("1と2を足すと3になる", () => {
    // Arrange
    const a = 1;
    const b = 2;

    // Act
    const result = add(a, b);

    // Assert
    expect(result).toBe(3);
  });
});
```

* こうすると「何してるか」が一瞬で読める👀✨
* **テストは仕様書**って感覚が育つよ🫶

### ✅ Refactorチェック（この章の合格ライン）💮

* テストは ✅ のまま
* 変更したのは “読みやすさ” だけ
* 「何を保証してるテスト？」って聞かれて答えられる

---

## 🤖 AI（Copilot/Codex）使い方：この章の正解ムーブ✨

![ ai usage do dont](./picture/tdd_ts_study_002_ai_usage_do_dont.png)

AIは便利だけど、**仕様をAIに決めさせない**のがコツだよ🧠🔒

### 使ってOK👍（おすすめ）

* 失敗ログ貼って「原因の説明」と「次の最小手」を聞く
* テスト名の改善案を3つ出させる
* Arrangeが重い時に「もっと短くできる？」って聞く

例プロンプト👇

```text
いまVitestでテストが落ちています。ログを貼るので、
1) 何が原因か
2) 次にやる最小の修正は何か
3) その修正が「作り込み」になってないか
を短く教えて。
```

### これはNG🙅‍♀️

* 「実装全部作って」→ テストが仕様じゃなくなる
* 「正しい仕様を考えて」→ 仕様が人間の手から離れる

---

## ✅ 最終チェックリスト（サクッと）🧾💕

* [ ] Red：**動くテスト**が、**意味のある理由**で落ちた🔴
* [ ] Green：最小の変更で通した🟢
* [ ] Refactor：仕様を変えずに読みやすくした🧼
* [ ] 「Greenで盛らない」を守れた🌱

---

## 🎁 おまけ（余力あれば）：2周目で “TDDっぽさ” が急に出る🔁✨

もう1本テストを足してみてね👇（また Red→Green になるよ！）

```ts
it("0と5を足すと5になる", () => {
  expect(add(0, 5)).toBe(5);
});
```

通ったらOK👌（通らなかったら、そこが学びポイント！）

---

## 📌 この章の提出物（自分用メモでOK）📝✨

* Redのときの失敗ログ（スクショでもコピペでも）📸
* Greenで直した差分（addの変更）🟢
* Refactorで何を良くしたか 1行メモ🧼

---

次の章（第3章）は、この “1回回せた感覚” を使って、**「小さく刻む」コツ**を身につけていくよ🔪🧪💕

[1]: https://vitest.dev/guide/ "Getting Started | Guide | Vitest"
[2]: https://nodejs.org/en/blog/release/v24.13.0?utm_source=chatgpt.com "Node.js 24.13.0 (LTS)"

