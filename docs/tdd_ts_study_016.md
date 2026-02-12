# 第16章：Assert基礎①（数・文字・真偽）✅

![アサートの基本アイコン](./picture/tdd_ts_study_016_assert_icons.png)

テストって「書く」よりも、「どこをどう確認するか（Assert）」で強さが決まるよ〜！💪🧪
この章は **“通るだけテスト” → “守れるテスト”** に進化させる回だよ😊🌸

---

## 🎯 この章のゴール

* 数値・文字列・真偽の **基本Assertを迷わず選べる** ✅
* **失敗した時に一発で原因がわかる** Assertを書ける 🔍✨
* 「弱いAssert」を「強いAssert」に直せる 🛠️💕

---

## 📚 学ぶこと（使うAssertたち）

Vitestの `expect()` には **Jest互換のAssert** があり、さらに **2つ目の引数で失敗メッセージも付けられる**よ📝✨（地味に便利！） ([Vitest][1])

### 今日の主役🎬

* 数値：`toBe` / `toBeCloseTo` / `toBeGreaterThan` / `toBeLessThanOrEqual` / `toBeNaN`

  * 浮動小数は `toBe` じゃなくて `toBeCloseTo` 推奨！（0.1+0.2問題） ([Vitest][1])
  * 比較系（大小）はこのへん： ([Vitest][1])
  * `NaN` 専用：`toBeNaN` ([Vitest][1])
* 文字列：`toBe` / `toContain` / `toMatch`

  * `toContain` は「部分文字列」もOK ([Vitest][1])
  * `toMatch` は「正規表現 or 文字列」 ([Vitest][1])
* 真偽：`toBe(true/false)` / `toBeTruthy` / `toBeFalsy`

  * truthy/falsy の説明と「何がfalsyか」一覧は公式にも載ってるよ ([Vitest][1])

---

## 🧠 まず結論：Assert選びのコツ（超大事）🌟

### ✅ 1) “仕様の言葉”に一番近いAssertを選ぶ

* 「結果は 13 である」→ `toBe(13)`
* 「結果は 10より大きい」→ `toBeGreaterThan(10)` ([Vitest][1])
* 「文字列に 'apple' を含む」→ `toContain('apple')` ([Vitest][1])

### ✅ 2) “弱いAssert”はバグを素通りする😇

例：`toBeDefined()` は「何か返った」しか見ない
→ 本当は「何が返ったか」を守りたいことが多いよね？🤔

---

## 🧪 手を動かす①：数値Assert（強くする）🔢✨

### 1) まずは `toBe`（プリミティブの一致）

```ts
import { test, expect } from "vitest";

function add(a: number, b: number) {
  return a + b;
}

test("addは足し算できる", () => {
  expect(add(2, 3)).toBe(5);
});
```

`toBe` はプリミティブの一致に強いよ✅ ([Vitest][1])

---

### 2) 小数は `toBeCloseTo`（0.1+0.2問題）🫠

![016 float target](./picture/tdd_ts_study_016_float_target.png)


Vitest公式でも「小数に toBe は避けてね」って言ってるよ〜！ ([Vitest][1])

```ts
import { test, expect } from "vitest";

test("小数はtoBeCloseToで比べる", () => {
  expect(0.1 + 0.2).toBeCloseTo(0.3, 5);
});
```

`numDigits` で「小数点以下何桁まで見るか」指定できるよ✅ ([Vitest][1])

---

### 3) “範囲”で守る（大小比較）📏

![画像を挿入予定](./picture/tdd_ts_study_016_range_compare.png)

```ts
import { test, expect } from "vitest";

function calcDiscounted(total: number) {
  // 例：どんな処理でもいい（ここはassert練習用）
  return total * 0.9;
}

test("割引後は元より小さい", () => {
  const after = calcDiscounted(1000);
  expect(after).toBeLessThan(1000);
});
```

比較系 Assert：`toBeGreaterThan` / `toBeLessThanOrEqual` など ([Vitest][1])

---

### 4) `NaN` だけは専用Assert（罠回避）🕳️

![016 nan trap](./picture/tdd_ts_study_016_nan_trap.png)


```ts
import { test, expect } from "vitest";

test("NaNはtoBeNaNで確認する", () => {
  expect(Number("???")).toBeNaN();
});
```

`toBeNaN` が用意されてるよ✅ ([Vitest][1])

---

## 🧪 手を動かす②：文字列Assert（意図が伝わる）🧵💕

### 1) 完全一致：`toBe`

```ts
import { test, expect } from "vitest";

function normalizeName(name: string) {
  return name.trim();
}

test("前後の空白を消す", () => {
  expect(normalizeName("  Alice  ")).toBe("Alice");
});
```

### 2) 部分一致：`toContain`

![016 string contains](./picture/tdd_ts_study_016_string_contains.png)


`toContain` は「配列に含まれる」だけじゃなく、**文字列の部分一致**にも使えるよ✨ ([Vitest][1])

```ts
import { test, expect } from "vitest";

test("メッセージにキーワードを含む", () => {
  const msg = "top fruits include apple, orange and grape";
  expect(msg).toContain("apple");
});
```

### 3) パターン一致：`toMatch`（正規表現OK）🧙‍♀️

![016 regex stencil](./picture/tdd_ts_study_016_regex_stencil.png)


```ts
import { test, expect } from "vitest";

test("ID形式をざっくり確認する", () => {
  const id = "user_12345";
  expect(id).toMatch(/^user_\d+$/);
});
```

`toMatch` は「正規表現 or 文字列」でマッチできるよ✅ ([Vitest][1])

---

## 🧪 手を動かす③：真偽Assert（“boolean”と“truthy”は別！）⚪️⚫️

### 1) booleanを守るなら：`toBe(true/false)` が基本👍

![016 boolean vs truthy](./picture/tdd_ts_study_016_boolean_vs_truthy.png)


```ts
import { test, expect } from "vitest";

function isAdult(age: number) {
  return age >= 18;
}

test("18歳以上はtrue", () => {
  expect(isAdult(18)).toBe(true);
});
```

### 2) truthy/falsy は「booleanに変換したら…」の世界🌫️

`toBeTruthy` / `toBeFalsy` は「値そのもの」じゃなく **boolean変換結果**を見るよ〜 ([Vitest][1])
falsy は `false/null/undefined/NaN/0/""` などがあるって公式に明記されてる✅ ([Vitest][1])

```ts
import { test, expect } from "vitest";

test("truthy/falsyは『変換したら』の確認", () => {
  expect("hello").toBeTruthy();
  expect("").toBeFalsy();
});
```

💡使い分けの目安

* **仕様が boolean（true/false）** → `toBe(true)` / `toBe(false)` ✅
* **仕様が「存在する/しない」「空じゃない」** → `toBeTruthy` / `toBeFalsy` が便利✨ ([Vitest][1])

---

## 🧨 “弱いAssert” → “強いAssert” 変換ドリル（ミニ演習）🎮✨

### お題：このテスト、どこが弱い？😇

```ts
import { test, expect } from "vitest";

function getUserLabel(isPremium: boolean) {
  return isPremium ? "PREMIUM_USER" : "FREE_USER";
}

test("ユーザーラベルが返る", () => {
  const label = getUserLabel(true);
  expect(label).toBeDefined(); // ←弱い！
});
```

✅ 改善例（仕様を守る！）

```ts
test("プレミアムはPREMIUM_USERになる", () => {
  expect(getUserLabel(true)).toBe("PREMIUM_USER");
});

test("無料はFREE_USERになる", () => {
  expect(getUserLabel(false)).toBe("FREE_USER");
});
```

---

## 🤖 AIの使い方（この章のおすすめプロンプト）✨

![016 ai selector](./picture/tdd_ts_study_016_ai_selector.png)


* 「このテストのAssertが弱いところを指摘して、**より仕様に近いAssert**へ直して。候補を3つ出して」
* 「`toBe` と `toContain` と `toMatch` のどれが仕様に近い？理由つきで」
* 「truthy/falsy を使っていいケースか、booleanを厳密に見るべきか判定して」

※AIに“仕様そのもの”を決めさせるんじゃなくて、**Assert選びの候補出し**に使うのが安全だよ🤖🛡️

---

## ✅ チェックリスト（合格ライン）💮

* [ ] 数値は **一致 / 範囲 / 小数 / NaN** を使い分けできる（小数は `toBeCloseTo`） ([Vitest][1])
* [ ] 文字列は **完全一致 / 部分一致 / パターン** を使い分けできる ([Vitest][1])
* [ ] boolean と truthy/falsy を混同してない ([Vitest][1])
* [ ] `toBeDefined()` だけで満足してない（“何が返るか”を守ってる）✅

---

次の第17章は「オブジェクト比較（toEqual / toMatchObject）」で、Assertが一気に楽しくなるところだよ〜！🧸✨

[1]: https://vitest.dev/api/expect.html "expect | Vitest"
