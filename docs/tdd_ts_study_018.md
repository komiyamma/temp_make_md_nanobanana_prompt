# 第18章：Assert基礎③（配列・順序・含有）📦

![配列の箱](./picture/tdd_ts_study_018_array_box.png)

〜「配列のテストって、どこまで厳しく見るべき？」がスッキリする章だよ〜😊💕

---

## 🎯 この章のゴール

* 配列のテストで **「順序が仕様かどうか」** を自分で決められる🧠✨
* Vitestで **配列の一致・含有・順序なし検証** をサクッと書ける✍️🧪
* **“たまに落ちる”テスト（フレーク）** の原因になりやすい「順序依存」を避けられる🚫🎲

---

## 📚 まず超重要：順序は「仕様」？それとも「ただの都合」？🤔

![018 order matters vs not](./picture/tdd_ts_study_018_order_matters_vs_not.png)


配列テストが難しい理由はコレ👇

* ✅ **順序が仕様**：ランキング / 並び順が意味を持つ（例：おすすめ上位3件）🏆
* ✅ **順序が仕様じゃない**：タグ一覧 / 権限一覧 / 検索条件の結果の集合（例：含まれてればOK）🧺

ここを決めると、使うAssertが一気に決まるよ💡

---

## 🧪 配列Assertの基本セット（これだけで戦える）💪✨

### 1) 配列が **完全一致**（順序も要素も全部同じ）✅

![018 array exact](./picture/tdd_ts_study_018_array_exact.png)


* `toEqual`：中身の値を再帰的に比較（配列・オブジェクト向き）
* `toStrictEqual`：より厳密（`undefined`の扱い等も厳しめ）

（「配列の完全一致」は `expect.arrayContaining` じゃなくて、まずここが基本だよ✨）

```ts
import { expect, test } from "vitest";

test("順序も含めて完全一致", () => {
  const actual = ["A", "B", "C"];
  expect(actual).toEqual(["A", "B", "C"]);
});
```

> ※ Vitestの `expect` は Jest互換のマッチャーを多く使えるよ🧪 ([Vitest][1])

---

### 2) 配列が **要素を含む**（プリミティブ向け）🍓

![018 array contains](./picture/tdd_ts_study_018_array_contains.png)


* `toContain("A")`：`string / number / boolean` みたいな単純値向け

```ts
import { expect, test } from "vitest";

test("Aを含む", () => {
  const actual = ["A", "B", "C"];
  expect(actual).toContain("A");
});
```

---

### 3) 配列が **オブジェクト要素を含む**（ここが沼ポイント！）🌀

![018 object in array](./picture/tdd_ts_study_018_object_in_array.png)


* `toContainEqual({ ... })`：オブジェクトの「値」として含まれてるか（deep equal）
* `expect.objectContaining({ ... })`：オブジェクトの一部だけ一致（超便利）✨ ([Vitest][2])

```ts
import { expect, test } from "vitest";

test("オブジェクト要素を含む（完全一致）", () => {
  const actual = [{ id: 1, name: "A" }, { id: 2, name: "B" }];
  expect(actual).toContainEqual({ id: 1, name: "A" });
});

test("オブジェクト要素を含む（一部一致）", () => {
  const actual = [{ id: 1, name: "A" }, { id: 2, name: "B" }];
  expect(actual).toEqual(
    expect.arrayContaining([
      expect.objectContaining({ id: 1 }),
    ])
  );
});
```

---

## 📦 「順序なしで含まれてればOK」を綺麗に書く方法（超頻出）✨

### ✅ パターンA：`arrayContaining`（順序を無視して“含有”）🧺

![018 subset checklist](./picture/tdd_ts_study_018_subset_checklist.png)


`expect.arrayContaining([...])` は
「配列にこの要素たちが入ってればOK」っていう非対称マッチャーだよ✨ ([Vitest][2])

```ts
import { expect, test } from "vitest";

test("順序は問わず、AとBが入ってればOK", () => {
  const actual = ["B", "C", "A"];
  expect(actual).toEqual(expect.arrayContaining(["A", "B"]));
});
```

### ✅ ただし注意！⚠️ 「余計な要素」があっても通っちゃう

「AとBが入ってること」しか見ないから、`["A","B","Z"]` でもOKになっちゃう💦

👉 **“ちょうどそれだけ”** を確認したいときは、長さもセットで見るのが定番💡

```ts
import { expect, test } from "vitest";

test("順序は問わず、AとBだけ（他はダメ）", () => {
  const actual = ["B", "A"];
  expect(actual).toHaveLength(2);
  expect(actual).toEqual(expect.arrayContaining(["A", "B"]));
});
```

---

### ✅ パターンB：ソートしてから `toEqual`（集合比較っぽくする）🔀

![018 sort strategy](./picture/tdd_ts_study_018_sort_strategy.png)


**順序が仕様じゃないなら**、テスト側でソートして「比較しやすい形」にしちゃうのも超アリ😊

```ts
import { expect, test } from "vitest";

test("順序は仕様じゃないのでソートして比較", () => {
  const actual = ["B", "C", "A"];
  const expected = ["A", "B", "C"];

  expect([...actual].sort()).toEqual([...expected].sort());
});
```

> ✅ `[...]` でコピーしてるのえらい！
> 元配列を破壊しないから、テストが安定しやすいよ🧊✨

---

## 😵 「順序依存のテスト」がフレークの原因になりやすい話💥

![018 flaky order](./picture/tdd_ts_study_018_flaky_order.png)


ありがちな例👇
**本当は順序が仕様じゃない**のに、たまたま今はこの順で返ってる…みたいなやつ😇

* DBやAPIの返す順序が変わる
* オブジェクトのキー順や実装都合が変わる
* 並列処理で順序が揺れる

👉 だから、**順序が仕様じゃないなら順序をテストしない**のが超大事💖

---

## 🧪 手を動かす：順序あり／なしのテストを作ってみよ🔧✨

### お題：検索サジェスト（候補）を返す関数🔍

仕様（テストが仕様書だよ📘✨）

* 入力：候補の配列 `items` と、入力文字 `q`
* 出力：`q` を含むものだけ返す
* ただし…

  * **Case1：順序は元の並びのまま（順序が仕様）**
  * **Case2：順序はどうでもよい（含まれてればOK）**

#### まずは「順序が仕様」版のテスト 🏆

```ts
import { expect, test } from "vitest";

function suggest(items: string[], q: string): string[] {
  // いまは未実装でOK（TDDなので！）
  return [];
}

test("順序が仕様：元の順を保ったままフィルタされる", () => {
  const items = ["apple", "apricot", "banana", "pineapple"];
  const actual = suggest(items, "ap");
  expect(actual).toEqual(["apple", "apricot", "pineapple"]);
});
```

#### 次に「順序が仕様じゃない」版のテスト 🧺

```ts
import { expect, test } from "vitest";

test("順序が仕様じゃない：含まれていればOK（かつ件数も一致）", () => {
  const items = ["apple", "apricot", "banana", "pineapple"];
  const actual = suggest(items, "ap");

  expect(actual).toHaveLength(3);
  expect(actual).toEqual(expect.arrayContaining(["apple", "apricot", "pineapple"]));
});
```

---

## 🤖 AIの使いどころ（Copilot/Codex想定）💡✨

### ✅ 使うと強いプロンプト例（そのままコピペOK）📋

```txt
Vitestで「配列のテスト」を書きたい。
順序が仕様の場合は toEqual で比較する。
順序が仕様じゃない場合は arrayContaining + toHaveLength を使う。
この方針で、テストケースを3つ提案して。
（正常/境界/異常の順で）
```

### ✅ AIにレビューさせる観点（超大事）👀

```txt
このテスト、順序に依存してない？
順序が仕様かどうか、仕様文を1行で言い直して。
もし順序が仕様じゃないなら、より安定するassertに直して提案して。
```

---

## ✅ チェックリスト（この章の合格ライン）🎓💮

* [ ] 「順序が仕様か？」を **仕様文で説明**できる📝
* [ ] 順序が仕様なら `toEqual([...])` で **完全一致**できる✅
* [ ] 順序が仕様じゃないなら `arrayContaining` を使える🧺 ([Vitest][2])
* [ ] “ちょうどそれだけ”を確認したい時に `toHaveLength` をセットにできる📏
* [ ] オブジェクト配列で `toContainEqual` / `objectContaining` を使い分けできる🧸 ([Vitest][2])

---

## 📌 おまけ：2026時点の「最新版」メモ（教材の鮮度チェック）🗓️✨

* TypeScript は GitHub Releases 上で **5.9.3 が Latest** と表示されてるよ（本日時点）🧠 ([GitHub][3])
* Node.js は **v24 が Active LTS** と整理されてるよ（本日時点）🧩 ([nodejs.org][4])

---

次の章（第19章）は「例外・失敗のテスト（異常系入門）🚫」だから、
今回の「含有・順序・配列の考え方」を持ってるとめちゃ楽になるよ〜😊💖

[1]: https://vitest.dev/guide/extending-matchers?utm_source=chatgpt.com "Extending Matchers | Guide"
[2]: https://vitest.dev/api/expect.html "expect | Vitest"
[3]: https://github.com/microsoft/typescript/releases "Releases · microsoft/TypeScript · GitHub"
[4]: https://nodejs.org/en/about/previous-releases "Node.js — Node.js Releases"
