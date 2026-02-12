# 第28章：重複のにおい（設計アラーム）👃🚨

![重複へのアラーム](./picture/tdd_ts_study_028_red_alarm.png)

この章はね、**「あ、いま設計を良くするチャンス来た！」**って気づけるようになる回だよ〜😊💕
TDDって、テストを書いて進むだけじゃなくて、**“重複が見えた瞬間に設計が育つ”**のがめちゃ大事なんだ🧠🌱

---

## 🎯 この章でできるようになること

* **重複の種類**を見分けられる（コピペだけじゃないよ！）👀✨
* **テストの重さ＝設計のサイン**って分かるようになる⚖️
* 改善を **最小→中→大** の3段階で提案＆実行できる🪜✅
* “DRYしすぎ事故”を避けながら、読み物として強くできる📘🛡️

---

## 🧠 本日時点の「道具」ちょいアップデート（超短く）🧪🆕

* **Vitest 4** がリリースされて、VS Code拡張のデバッグ体験も改善が入ってるよ🔎🐛 ([Vitest][1])
* Nodeは **v24 がActive LTS** 扱いで、セキュリティリリースも定期的に来るから、ちゃんと追うのが安心🛡️🪟 ([Node.js][2])
* TypeScriptは **5.9系** のリリースノートが公開されていて、Node向けオプションも整理が進んでるよ🧷 ([TypeScript][3])
* カバレッジを使うなら `@vitest/coverage-v8` は **4.0.x** が継続更新中だよ📈 ([NPM][4])

（ここは章の主役じゃないので、必要な分だけね😉）

---

## 👃 “重複のにおい”ってなに？（コピペだけじゃない）🧠💡

「重複」はだいたいこの4タイプで出るよ👇

### 1) 📦 データの重複

同じオブジェクト生成、同じ配列、同じ入力…が何回も出てくるやつ。

### 2) 🔁 手順の重複

Arrangeが毎回長い、同じ準備を何度もやってる、みたいなやつ。

### 3) 🧭 ルール（知識）の重複 ← これが一番ヤバい🚨

同じ割引ルールが、実装のあちこちに散ってる
同じ分類（例：会員ランク）が、いろんなifで繰り返される
→ **変更に弱い設計**になりやすい😵‍💫

### 4) ✅ Assertの重複

同じ期待を何度も書いてる / 失敗したとき何が壊れたか分かりにくい、みたいなやつ。

---

## 👃 重複が「設計アラーム」になる理由🔔

![画像を挿入予定](./picture/tdd_ts_study_028_alarm_smell.png)

TDDだと、最初はどうしても重複が出るのね🙂
でもそれは悪じゃなくて、

> **「次に育てるべき設計の形が見えてきたよ！」**

っていうサインなの✨
特に、**テストのArrangeがつらい**ときは高確率で👇

* 依存が混ざってる（ロジックとI/Oがごちゃ）🧩💥
* 役割が大きすぎる（1クラスがなんでもやる）🧟‍♀️
* ドメインの言葉（型/モデル）が足りない（string地獄）🏜️

---

## 🧪 ハンズオン：つらいテストを1つ“診断→改善案3つ”するよ🩺✨

### 🧪 お題（例）：割引あり会計（軽め）🎟️🧾

※あなたの実案件や卒業制作のテストでもOKだよ！

#### 😵‍💫 まずは「つらい」例（わざと）

* Arrangeが毎回長い
* 同じ数字や商品が何回も出る
* ルールがテスト名から読み取れない

```ts
import { describe, it, expect } from "vitest";

type Item = { name: string; price: number; qty: number };
type Coupon = { code: "OFF10" | "OFF100"; };

function totalPrice(items: Item[], coupon?: Coupon): number {
  const subtotal = items.reduce((sum, x) => sum + x.price * x.qty, 0);

  // ルールがベタ書き（重複の温床）
  if (!coupon) return subtotal;

  if (coupon.code === "OFF10") return Math.floor(subtotal * 0.9);
  if (coupon.code === "OFF100") return Math.max(0, subtotal - 100);

  return subtotal;
}

describe("totalPrice", () => {
  it("OFF10: 10%引きになる", () => {
    const items: Item[] = [
      { name: "coffee", price: 300, qty: 2 },
      { name: "sandwich", price: 450, qty: 1 },
    ];
    const coupon: Coupon = { code: "OFF10" };

    const result = totalPrice(items, coupon);

    expect(result).toBe(Math.floor((300 * 2 + 450) * 0.9));
  });

  it("OFF100: 100円引きになる", () => {
    const items: Item[] = [
      { name: "coffee", price: 300, qty: 2 },
      { name: "sandwich", price: 450, qty: 1 },
    ];
    const coupon: Coupon = { code: "OFF100" };

    const result = totalPrice(items, coupon);

    expect(result).toBe((300 * 2 + 450) - 100);
  });
});
```

---

## 🩺 ステップ1：重複を「色分けメモ」する🖍️📝

上の例なら、こんな重複があるよ👇

* 📦 **itemsが丸ごと同じ**（データ重複）
* 🔁 **Arrangeが毎回同じ**（手順重複）
* 🧭 **割引ルールがベタ書き**（知識重複の温床）
* ✅ 期待値の式がその場で組み立て（読み物として弱い）

---

## 🪜 ステップ2：改善案を「最小→中→大」で3つ出す✨

### ✅ 改善案A（最小）：テストのデータ重複だけ消す📦✨

ポイント：**読みやすさ優先で、やりすぎない**🙂

```ts
const sampleItems = (): Item[] => [
  { name: "coffee", price: 300, qty: 2 },
  { name: "sandwich", price: 450, qty: 1 },
];

describe("totalPrice", () => {
  it("OFF10: 10%引きになる", () => {
    const result = totalPrice(sampleItems(), { code: "OFF10" });
    expect(result).toBe(945); // 1050の10%引き（床）
  });

  it("OFF100: 100円引きになる", () => {
    const result = totalPrice(sampleItems(), { code: "OFF100" });
    expect(result).toBe(950); // 1050-100
  });
});
```

💡 ここでの狙い：

* Arrangeが短くなる🧸✨
* テストが「計算式」じゃなくて「仕様」に見える📘✅

---

### ✅ 改善案B（中）：割引ルール（知識）を“名前”にする🧭🏷️

ポイント：**“知識は1か所に集める”**（変更に強くなる）💪✨

```ts
type CouponCode = "OFF10" | "OFF100";

function applyCoupon(subtotal: number, code: CouponCode): number {
  if (code === "OFF10") return Math.floor(subtotal * 0.9);
  return Math.max(0, subtotal - 100);
}

function totalPrice(items: Item[], coupon?: Coupon): number {
  const subtotal = items.reduce((sum, x) => sum + x.price * x.qty, 0);
  if (!coupon) return subtotal;
  return applyCoupon(subtotal, coupon.code);
}
```

💡 ここでの狙い：

* 「割引の知識」が `applyCoupon` に集まる📌
* ルール追加（OFF200とか）が怖くなくなる➕🛡️

---

### ✅ 改善案C（大）：テストの意図を“表”に寄せる（パラメータ化）🗂️🔁

ポイント：ケースが増える未来に強い✨（第22章とつながるよ）

```ts
describe("totalPrice coupon", () => {
  const items = sampleItems(); // 固定でOK（仕様の前提）

  const cases: Array<{ code: CouponCode; expected: number }> = [
    { code: "OFF10", expected: 945 },
    { code: "OFF100", expected: 950 },
  ];

  it.each(cases)("$code: クーポン仕様どおりになる", ({ code, expected }) => {
    expect(totalPrice(items, { code })).toBe(expected);
  });
});
```

💡 ここでの狙い：

* ケース追加が1行で済む🧠✨
* “仕様の一覧”がそのままテストになる📘✅

---

## ⚠️ DRYしすぎ注意（テストでやりがちな事故）🚑💦

テストは「読み物」だから、**重複を消しすぎると逆に読めなくなる**の😵‍💫

### 🚫 ありがち

* `makeEverything()` みたいな万能Factoryが増える
* helperの中に意図が隠れて「何を検証してるか」が見えない
* beforeEachで全部作って、各テストの前提が消える

### ✅ いい目安

* **2回出たらメモ**📝
* **3回出たら抽出検討**🧠
* 抽出しても、テスト本文から「前提と期待」が読めること📘✨

---

## 🤖 AIの使い方（この章は相性◎）💞🤖

AIには「診断と案出し」をやらせると強いよ💪✨
（ただし、仕様決めは人間側ね😉）

### 🤖 プロンプト①：重複の分類（まず観察）👀

```text
このVitestテストと実装を見て、「重複のにおい」を
(1)データ (2)手順 (3)知識(ルール) (4)assert の4分類で指摘して。
各分類につき、なぜ危険かを1行で。
```

### 🤖 プロンプト②：改善案を3段階（最小→中→大）🪜

```text
このコードの重複に対して、改善案を
A:最小（安全・短時間）
B:中（設計が一段よくなる）
C:大（将来の拡張に強い）
の3つ出して。各案のメリデメも1行ずつ。
```

### 🤖 プロンプト③：DRYしすぎ警告🚨

```text
提案したリファクタ案について、
「テストが読めなくなる危険」「抽象化しすぎの危険」がある点を列挙して。
避けるルールも提案して。
```

---

## ✅ チェック（合格ライン）🎓✅

* [ ] 重複を4分類で説明できる👃
* [ ] 改善案を「最小→中→大」で3つ言える🪜
* [ ] 最小案を実際にやって、テストが短く読みやすくなった📘✨
* [ ] ルール（知識）の重複が1か所に寄った🧭📌
* [ ] helperを作っても、テスト本文から意図が読める🙂✅

---

## 🧾 提出物（この章の“手を動かす”のゴール）🎁✨

1. 「つらいテスト」1つ選ぶ
2. 重複を4分類でメモ📝
3. 改善案A/B/Cを文章で書く（各3行くらいでOK）💬
4. まずAを実装してコミット✅
   （余裕あればBまで！）

---

次の第29章は「リファクタ安全運転（小さく）」だから、
この章で出した改善案を **“壊さず進める順番”** に落としていくよ🛡️✨

「つらいテスト」の題材、もし今ちょうど手元にあるなら、そのコード貼ってくれたら、いっしょに“重複診断→A/B/C案”まで一気に作るよ〜👃🚨💕

[1]: https://vitest.dev/blog/vitest-4?utm_source=chatgpt.com "Vitest 4.0 is out!"
[2]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
[3]: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-9.html?utm_source=chatgpt.com "Documentation - TypeScript 5.9"
[4]: https://www.npmjs.com/package/%40vitest/coverage-v8?utm_source=chatgpt.com "vitest/coverage-v8"
