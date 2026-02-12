# 第19章：例外・失敗のテスト（異常系入門）🚫

![進入禁止の標識](./picture/tdd_ts_study_019_prohibition_sign.png)

この章は「失敗も仕様にする」練習だよ〜！🙂✨
正常系が通るだけだと、入力ミスや想定外の値でアプリが壊れやすいの。だから **“落ち方” もテストで決める** よ〜！🛡️💕

---

## 🎯 この章のゴール（できるようになること）✨

* 無効な入力のときに **throw（同期）** するテストが書ける✅
* Promiseが失敗するときに **reject（非同期）** するテストが書ける✅
* エラーの **種類（クラス）** と **メッセージ** を“ちょうどよく”検証できる✅
* 「どんな失敗が仕様なの？」を整理できる✅

---

## 🧠 まず超重要：失敗には“種類”があるよ🗂️✨

![019 spec vs bug](./picture/tdd_ts_study_019_spec_vs_bug.png)


失敗（エラー）って全部同じじゃないの〜！😵‍💫💦
ここを分けると、テストも設計もスッキリするよ💕

### ① 仕様としての失敗（テストする）✅

* 無効な入力（マイナス、空、桁あふれ、形式違い）
* ビジネスルール違反（上限超え、在庫なし、権限なし）
  → **「こう失敗してね」って決めたい** からテストする💪✨

### ② バグとしての失敗（基本テストしない）⚠️

* null参照、型の勘違い、分岐ミス
  → これは **直すべきバグ**。仕様にしない🧯

### ③ 外部要因の失敗（境界で扱う）🌐

* ネットワーク、DB、ファイル、API落ち
  → 後の章（依存の切り方）で強くなるやつ💪🔥

---

## ✅ Vitestで「throw / reject」をテストする基本形🧪

### 1) 同期の throw をテストする形（超大事）⚡

![019 throw bubble](./picture/tdd_ts_study_019_throw_bubble.png)


Vitestは「throwするコード」を **関数で包む** 必要があるよ！
包まないと、expectの外で落ちちゃうの😇💥 ([Vitest][1])

```ts
import { expect, test } from "vitest";

function parseAge(input: number) {
  if (input < 0) throw new Error("age must be >= 0");
  return input;
}

test("マイナスはエラーになる", () => {
  expect(() => parseAge(-1)).toThrowError("age must be >= 0");
});
```

### 2) 非同期の reject をテストする形（Promise）⏳

![019 async reject](./picture/tdd_ts_study_019_async_reject.png)


Promiseは `rejects` で中身をほどいて検証できるよ〜！
（この場合は “関数で包む/包まない” の注意点がちょい違うから、下の例を真似してね🙂） ([Vitest][1])

```ts
import { expect, test } from "vitest";

test("Promiseが失敗するとき", async () => {
  const promise = Promise.reject(new Error("nope"));
  await expect(promise).rejects.toThrowError("nope");
});
```

---

## 🛠️ ハンズオン：カフェ会計で「無効入力」を仕様にする☕️🧾🚫

### 🧩 お題：注文の入力チェックを作るよ💕

* 数量（qty）が 1以上じゃないとダメ
* 値段（price）が 0以上じゃないとダメ
* 注文が空（items.length === 0）もダメ

失敗時は **ValidationError** を投げることにするよ🙂✨

![019 validation error](./picture/tdd_ts_study_019_validation_error.png)

（普通の Error でもいいけど、後々ラクになるからここで慣れちゃお！）

---

## 🔴 Step 1：まずテストを書く（Red）🚦

ポイント：

* いきなりケースを増やしすぎない🙅‍♀️
* まず “一番ありそうな無効入力” を1つでOK✨

```ts
import { describe, expect, it } from "vitest";
import { calcTotal, ValidationError } from "../src/calcTotal";

describe("calcTotal（異常系）", () => {
  it("注文が空なら ValidationError", () => {
    expect(() => calcTotal([])).toThrowError(
      expect.objectContaining({ name: "ValidationError", message: "items must not be empty" })
    );
  });

  it("数量が0以下なら ValidationError", () => {
    expect(() =>
      calcTotal([{ name: "Coffee", qty: 0, price: 450 }])
    ).toThrowError(/qty must be >= 1/);
  });

  it("価格がマイナスなら ValidationError", () => {
    expect(() =>
      calcTotal([{ name: "Coffee", qty: 1, price: -1 }])
    ).toThrowError("price must be >= 0");
  });
});
```

* メッセージは **完全一致より、部分一致（文字列/正規表現）** を多用すると折れにくいよ🙂✨ ([Vitest][1])

![019 message match](./picture/tdd_ts_study_019_message_match.png)

* `expect.objectContaining` でエラーの形も見れるよ（Vitestの例にもあるよ）💡 ([Vitest][1])

---

## 🟢 Step 2：最小実装で通す（Green）🌱

「まず通す」が最優先！✨
（ここでキレイにしようとして沼りがちなので注意😵‍💫）

```ts
export type Item = { name: string; qty: number; price: number };

export class ValidationError extends Error {
  override name = "ValidationError";
}

export function calcTotal(items: Item[]): number {
  if (items.length === 0) throw new ValidationError("items must not be empty");

  for (const item of items) {
    if (item.qty < 1) throw new ValidationError("qty must be >= 1");
    if (item.price < 0) throw new ValidationError("price must be >= 0");
  }

  return items.reduce((sum, x) => sum + x.qty * x.price, 0);
}
```

---

## 🔵 Step 3：整える（Refactor）🧹✨

ここで「読める形」にするよ〜！💕

### ✅ リファクタ方針（この章の“ちょうどよさ”）

* チェック処理を `validateItems` に分ける
* エラーメッセージを **仕様として読みやすく**する
* ただし “共通化しすぎ” はまだしない（初心者が迷子になる）🙂

```ts
export type Item = { name: string; qty: number; price: number };

export class ValidationError extends Error {
  override name = "ValidationError";
}

function validateItems(items: Item[]): void {
  if (items.length === 0) throw new ValidationError("items must not be empty");

  for (const item of items) {
    if (item.qty < 1) throw new ValidationError("qty must be >= 1");
    if (item.price < 0) throw new ValidationError("price must be >= 0");
  }
}

export function calcTotal(items: Item[]): number {
  validateItems(items);
  return items.reduce((sum, x) => sum + x.qty * x.price, 0);
}
```

---

## 🌙 追加ミニ：async関数の異常系（reject）も1本だけ書こう⏳✨

「将来、割引クーポンの確認が非同期」みたいな想定で、雑に例を作るね🙂

```ts
import { expect, test } from "vitest";

async function loadCoupon(code: string): Promise<{ rate: number }> {
  if (!code) throw new Error("code is required");
  return Promise.reject(new Error("coupon not found"));
}

test("存在しないクーポンは reject", async () => {
  await expect(loadCoupon("NOPE")).rejects.toThrowError("coupon not found");
});
```

`rejects` の使い方はVitestの説明でも出てるよ🧪✨ ([Vitest][1])

---

## 🤖 AIの使い方（この章での“勝ちパターン”）🧠✨

![019 ai error brainstorm](./picture/tdd_ts_study_019_ai_error_brainstorm.png)


AIはめっちゃ便利だけど、**仕様を決めるのはあなた** だよ〜！👑💕
使いどころは「候補出し」と「抜けチェック」がおすすめ🙂

### 💡 おすすめプロンプト（そのまま貼ってOK）✨

```text
calcTotal(items) の異常系テストを書きたいです。
items は { name: string, qty: number, price: number } の配列です。
「仕様として扱うべき無効入力」を、重要度順に10個列挙して。
それぞれに “期待する失敗の種類（throw/reject）” と “メッセージ案（短く）” も付けて。
ただし、過剰に厳密なメッセージ一致は避けたいです。
```

### ✅ AIを使ったあとの“自分チェック”🪞

* その無効入力、ほんとにユーザーがやりそう？🙂
* 「落ち方」が一貫してる？（ValidationErrorに寄せる等）🧠
* メッセージが “仕様として読める”？📘✨

---

## 😵‍💫 よくあるミス集（ここで詰まりやすい！）🧯

### ❌ 1) throwテストで包んでなくて落ちる

* ダメ： `expect(calcTotal([])).toThrowError(...)`
* 正解： `expect(() => calcTotal([])).toThrowError(...)`
  （Vitestも「包んでね」って言ってるよ） ([Vitest][1])

### ❌ 2) asyncなのに rejects を使ってない / awaitしない

* ダメ： `expect(loadCoupon("NOPE")).toThrowError(...)`
* 正解： `await expect(loadCoupon("NOPE")).rejects.toThrowError(...)` ([Vitest][1])

### ❌ 3) メッセージ完全一致にしすぎてテストが折れる

* まずは部分一致（文字列/正規表現）で十分🙂
  （Vitestの例も正規表現や部分一致を推してる感じだよ） ([Vitest][1])

---

## ✅ 章末チェック（セルフ採点）📝💕

* [ ] “仕様としての失敗” を3つテストにできた✅
* [ ] throwテストは必ず関数で包めた✅ ([Vitest][1])
* [ ] rejectテストは rejects を使えてる✅ ([Vitest][1])
* [ ] メッセージを厳密一致しすぎず、読みやすさ優先にできた✅
* [ ] 失敗の種類がブレてない（例：ValidationErrorで統一）✅

---

## 🧷 ちょい最新メモ（2026-01-19時点）📌✨

* TypeScript は「現在 5.9」が最新として案内されてるよ🧠 ([typescriptlang.org][2])
* Vitest は “latest 4.0.17（2026-01-12）” が見えてるよ🧪✨ ([Yarn][3])

---

## 🌸 次章（第20章）につながるよ！

異常系テストが増えると、**テスト名の良さ**が効いてくるよ〜！📝✨
次は「落ちた瞬間に原因が分かる命名」へ進もうね🙂💕

必要なら、この章の提出物（合格ライン）もセットで作るよ〜！🎓💖

[1]: https://vitest.dev/api/expect.html "expect | Vitest"
[2]: https://www.typescriptlang.org/download/?utm_source=chatgpt.com "How to set up TypeScript"
[3]: https://classic.yarnpkg.com/en/package/vitest "vitest | Yarn"
