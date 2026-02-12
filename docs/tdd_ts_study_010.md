# 第10章：モジュール（import/export）で迷わない🌿

![モジュールの枝分かれ](./picture/tdd_ts_study_010_module_branch.png)

## 🎯この章のゴール

この章が終わったら、こんな感じになれるよ〜！🥰

* ファイルを分割しても `import/export` で迷わない✨
* 「なんで読み込めないの!?😵‍💫」系エラーを、落ち着いて直せる🔧
* **“設定を増やさずに”** まず動く形を作れる✅

---

## 📚まずは超ざっくり：モジュールって何？

**モジュール＝「別ファイルにある機能を、importして使えるしくみ」**だよ📦
TypeScriptのモジュールは基本 **ESM（ECMAScript Modules）** の `import/export` で考えるのが今どきの勝ち筋✨ ([nodejs.org][1])

---

## 🧭結論：迷わないための“2つの型”だけ覚えよ💡

実は詰まりポイントは「実行環境のルールの違い」から来ることが多いの…！😿

### ✅A）テスト/ビルドが“Vite/Vitest寄り（バンドラ寄り）”の型

* 体感：importがわりと自由でラク✨
* VitestはVite powered だよ🧪⚡ ([vitest.dev][2])

### ✅B）Node.jsで“そのまま実行（ESM）”の型

* 体感：**拡張子 `.js` を書け**など、ルールが厳しめ⚠️
* NodeのESMは **相対importに拡張子が必須**（例：`./a.js`） ([nodejs.org][1])
* ESMにする方法（例：`"type": "module"`）もNode側のルール ([nodejs.org][1])

> この教材の流れ（次章でVitest）だと、まずは **Aの型を基準**にすると安定しやすいよ🫶
> ただしBに行くときの罠もこの章で“地雷処理”しておくね💣✨

---

## 🧪基本フォーム：export / import（ここだけ固定でOK）

### ① “名前付きexport”が基本（おすすめ）🌟

```ts
// src/math/add.ts
export function add(a: number, b: number) {
  return a + b;
}
```

（名前付きは後で増えても整理しやすいよ🧺）

```ts
// src/main.ts
import { add } from "./math/add";

console.log(add(2, 3));
```

* `{ add }` は「名前が add のものを使うよ」って意味✅

---

### ② default export は“使うなら徹底”🎁

```ts
// src/math/add.ts
export default function add(a: number, b: number) {
  return a + b;
}
```

```ts
// src/main.ts
import add from "./math/add";
```

* default は **名前を自由に変えられる**から、チームだとブレやすいこともあるよ😵‍💫
* 迷ったら **名前付きexport** でOK🙆‍♀️

---

### ③ “型だけimport”は、はっきり書くと強い🛡️

TypeScriptは「型のためだけのimport」を自動で消してくれるけど、**明示すると事故が減る**よ✨
`import type` は **出力JSに残らない（＝実行時には存在しない）** って約束🧠 ([typescriptlang.org][3])

```ts
import type { UserId } from "./types";
import { add } from "./math/add";
```

* 「型だけのつもりが、実行時importになって副作用が…😱」を避けやすい！

---

## 🧱“モジュール解決”で詰まらないための最小知識

ここが詰まりポイントの正体だよ〜！🕵️‍♀️

### ✅ TypeScriptの `module` と `moduleResolution` はセットで動く

TypeScriptは `module` の値によって、`moduleResolution` のデフォルトが変わるよ📌 ([typescriptlang.org][4])
たとえば `module: "preserve"` だと `moduleResolution: "bundler"` が基本、みたいな感じ✨ ([typescriptlang.org][4])

---

## 🧪手を動かす：1ファイル→2ファイル→“整理import”まで（15分コース）⏱️💞

### Step 1：まず分ける（最小）

```ts
// src/price/calcTax.ts
export function calcTaxIncluded(price: number, rate: number) {
  return Math.floor(price * (1 + rate));
}
```

```ts
// src/main.ts
import { calcTaxIncluded } from "./price/calcTax";

console.log(calcTaxIncluded(1000, 0.1)); // 1100
```

✅ ここで「読み込めた！」の感覚を作るのが大事💓

---

### Step 2：フォルダに“窓口（index）”を作る（ちょい整理）🪟

```ts
// src/price/index.ts
export { calcTaxIncluded } from "./calcTax";
```

```ts
// src/main.ts
import { calcTaxIncluded } from "./price";
```

> もし `./price` が解決されなくて詰まったら、無理せず `./price/index` にしてOK🙆‍♀️
> （環境の解決ルールで「フォルダ＝index」が効かないことがあるの🌀）

---

### Step 3：型チェックだけ先に回す（安心✨）

ビルドや実行の前に、まずこれだけでOK：

```bash
npx tsc --noEmit
```

* **importパスのミス**とかもここで見つかるよ🔍

---

## 💥あるある詰まりポイント辞典（ここが本題😎✨）

### 1) `Cannot find module './xxx'` 😭

✅ まず見る順番：

* **スペル**（大文字/小文字も！）
* **相対パスの基準**（今いるファイルから見てる？）
* **エイリアス（paths/baseUrl）を使ってない？**
  Vitest/Viteは `tsconfig` の `paths` をデフォで見ないことがあるよ〜！ ([vitest.dev][5])

---

### 2) Nodeで `ERR_MODULE_NOT_FOUND` / 拡張子のせい？😵

NodeのESMは **相対importに拡張子が必要**（例：`./a.js`） ([nodejs.org][1])
TypeScriptのドキュメント例も、`.ts` から `./module.js` をimportする形で書かれてたりするよ📘 ([typescriptlang.org][3])

🔧対処の考え方（どれか選ぶ）

* Node直実行なら、importに `.js` を書く流儀に寄せる
* もしくはビルド結果に合わせて、TypeScript側で拡張子を書き換える設定を検討
  （例：`rewriteRelativeImportExtensions` というオプションがあるよ） ([typescriptlang.org][4])

---

### 3) `exports is not defined in ES module scope` 😨

CommonJS（`module.exports`）っぽいコードが混ざってるサインかも⚠️
NodeのESMは `import/export` 前提で動くよ📦 ([nodejs.org][1])

---

### 4) `default export がない` / `named export がない` 🤯

* `import add from` ← default前提
* `import { add } from` ← named前提
  ここがズレると即死する😂
  ✅ **プロジェクト内のルールを1個に統一**しよ〜！

---

### 5) 型だけのimportが実行時に悪さしてる気がする👻

`import type` を使って「型は型！」って明示すると安定するよ🛡️ ([typescriptlang.org][3])

---

## 🤖AIの使い方（この章はここが強い✨）

AIには“設定を盛る”方向に走らせず、**原因当てゲーム**をさせるのがコツ🎯

### 🧾おすすめプロンプト（コピペOK）

* 「このエラーは **①パスミス ②拡張子問題 ③module/moduleResolution問題 ④default/named不一致** のどれ？理由つきで一個に絞って」
* 「最小の修正で直すならどれ？“設定追加なし案”→“設定追加あり案”の順で出して」
* 「この `import` が **実行時に必要**？ **型だけ**？判定して `import type` に直して」

---

## ✅チェック（できたら合格っ💕）

* [ ] `export` と `import` を “named中心” で書けた✨
* [ ] ファイル分割しても、importが迷子にならない🧭
* [ ] 1回は「読み込めない😭」を経験して、直せた🔧
* [ ] `import type` を1回使った🛡️

---

## 🌈次章につながる一言

次の第11章でVitestを入れると、**import周りの違和感（特にpaths/alias）**が一気に出やすいの！🧪
だからこの章で「詰まりポイントの分類」ができたの、めちゃ強いよ💪✨

[1]: https://nodejs.org/api/esm.html "Modules: ECMAScript modules | Node.js v25.3.0 Documentation"
[2]: https://vitest.dev/guide/ "Getting Started | Guide | Vitest"
[3]: https://www.typescriptlang.org/docs/handbook/modules/reference.html "TypeScript: Documentation - Modules - Reference"
[4]: https://www.typescriptlang.org/docs/handbook/compiler-options.html "TypeScript: Documentation - tsc CLI Options"
[5]: https://vitest.dev/guide/common-errors "Common Errors | Guide | Vitest"
