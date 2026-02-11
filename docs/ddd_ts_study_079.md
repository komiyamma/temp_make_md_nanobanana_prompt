# 第79章：モジュール境界の実戦：禁止importルール🚧

## 1) 今日のゴール🎯✨

* 「domain が infra を import しちゃった😵‍💫」みたいな事故を **自動で検知**できる
* PRで境界違反が混ざっても **CIで落ちる**から安心💪
* チーム開発でも「崩れないDDDの骨格」になる🏰

---

## 2) なんで禁止importが必要なの？🥺

境界ルールって、最初はみんな守れるんだよね。
でもだんだんこうなる👇

* 「とりあえず急ぎだから domain から infra 呼ぶか〜」😇
* 「DTO便利だし domain でも使っちゃお」😇
* 「気づいたら循環参照でビルドが謎死」😇

つまり…
**“守ろうね” じゃ守れないから、仕組みで守る**が正解💡

---

## 3) まずは境界ルールを1分で確定📝

このロードマップの流れ（第78章）を、そのまま “禁止importルール” にするよ✨

### 依存（import）の向き🌊

イメージはこれ👇（左ほど内側＝強い💎）

![境界ルールの依存の向き](./picture/ddd_ts_study_079_boundary_flow.png)

**infra → app → domain**

* domain：誰にも依存しない（最強の核）💎
* app：domain を使う（手順・ユースケース）🎬
* infra：外の世界（DB/HTTP/UIなど）🌍

### 例外（なんでも見えていい場所）🧩

依存を組み立てる場所（Composition Root）は、だいたい別枠にするのが楽👍
例：`src/bootstrap` や `src/main` みたいな場所。

---

## 4) 実装①：最短で効く！禁止import（no-restricted-imports）⚡🧹

### まず知っておくポイント👀

* ESLintの `no-restricted-imports` は「このimport禁止！」を作れるルールだよ🚫
* ただし **静的importに適用**で、dynamic import には基本効かないよ（仕様）📌 ([ESLint][1])
* TypeScriptでは、ESLint本体ルールより **typescript-eslint版**を使うのが安全（型importなど考慮）✅ ([TypeScript ESLint][2])

---

### “簡単版” の設定例（境界を壊すimportを止める）🚧

ESLintは最近の主流が **Flat Config（eslint.config.mjs）** だよ🧁
（ESLintの最新メジャーでもこの流れが続いてる） ([GitHub][3])

#### eslint.config.mjs（例）

```js
import js from "@eslint/js";
import tseslint from "typescript-eslint";

export default [
  js.configs.recommended,
  ...tseslint.configs.recommended,

  // ✅ TypeScriptではこっちを使う（型import等に対応）
  {
    files: ["src/**/*.ts"],
    rules: {
      "no-restricted-imports": "off",
      "@typescript-eslint/no-restricted-imports": [
        "error",
        {
          // 🧱 app から infra を触らせない
          patterns: [
            {
              group: ["../infra/*", "../../infra/*", "../../../infra/*"],
              message: "🚧 app → infra は禁止だよ！依存の向きを守ってね",
            },
          ],
        },
      ],
    },
  },

  // 🧊 domain は app/infra を触らせない
  {
    files: ["src/domain/**/*.ts"],
    rules: {
      "@typescript-eslint/no-restricted-imports": [
        "error",
        {
          patterns: [
            { group: ["../app/*", "../../app/*"], message: "🚧 domain → app は禁止だよ！" },
            { group: ["../infra/*", "../../infra/*"], message: "🚧 domain → infra は禁止だよ！" },
          ],
        },
      ],
    },
  },
];
```

✅ これだけでも「うっかり境界違反」をかなり止められるよ！
ただし…相対パスの深さが増えるとパターンがつらい🥲（次で解決✨）

---

## 5) 実装②：境界を“ルールとして定義”する（eslint-plugin-boundaries）🏰✨

ここからが本命〜！🥳
相対パスの地獄をやめて、**“domain/app/infra” を種類として宣言**して守るやつ💎

* `eslint-plugin-boundaries` は「ファイルがどの領域か」を設定して、**どことどこがimportしていいか**をルール化できるよ📦 ([JS Boundaries][4])
* 直近でも更新されてて、最新版リリースが出てるよ🆕 ([GitHub][5])

### eslint.config.mjs（境界定義つき・おすすめ）

```js
import js from "@eslint/js";
import tseslint from "typescript-eslint";
import boundaries from "eslint-plugin-boundaries";

export default [
  js.configs.recommended,
  ...tseslint.configs.recommended,

  {
    files: ["src/**/*.ts"],
    plugins: { boundaries },
    settings: {
      // 👇 どのフォルダがどの“領域タイプ”か決める
      "boundaries/elements": [
        { type: "domain", pattern: "src/domain/**" },
        { type: "app", pattern: "src/app/**" },
        { type: "infra", pattern: "src/infra/**" },
        { type: "shared", pattern: "src/shared/**" },
        { type: "bootstrap", pattern: "src/bootstrap/**" },
      ],
    },
    rules: {
      // ✅ どの領域がどこを import していいかを宣言する
      "boundaries/element-types": [
        "error",
        {
          default: "disallow",
          message: "🚧 境界違反だよ！ import を見直してね",
          rules: [
            { from: "domain", allow: ["domain", "shared"] },
            { from: "app", allow: ["app", "domain", "shared"] },
            { from: "infra", allow: ["infra", "app", "domain", "shared"] },
            { from: "bootstrap", allow: ["bootstrap", "infra", "app", "domain", "shared"] },
            { from: "shared", allow: ["shared"] },
          ],
        },
      ],

      // ついでに：未分類ファイルを許さない（守り固め）🛡️
      "boundaries/no-unknown": "error",
    },
  },
];
```

これの良さはね…
✅ **相対パスの深さに左右されない**
✅ 境界ルールが **文章みたいに読める**
✅ “例外（bootstrap）” をちゃんと作れる

最高〜〜〜！🥹✨

---

## 6) 実装③：依存グラフで“循環参照”も潰す（dependency-cruiser）🗺️🔁

ESLintは「その場のimport違反」には強いけど、
**循環参照（A→B→C→A）**みたいな “全体の形” は別ツールが便利👍

そこで `dependency-cruiser` 💣

* 依存グラフを解析して、Forbiddenルールや循環参照を検知できるよ📌 ([Medium][6])
* リリースも継続して出てる（＝現役）🆕 ([GitHub][7])

### ざっくり導入イメージ（ルール例）

* `domain` から `infra` へ行く依存は禁止🚫
* 循環参照は禁止🚫
* `infra` だけが外部（DB/HTTP）に触れてOK🌍

（ここはプロジェクトに合わせて少しずつ育てるのがコツだよ🌱）

---

## 7) （おまけ）モノレポならNxの境界ルールも強い🧩💪

もし将来、複数アプリ/複数ライブラリのモノレポになったら、Nxの **Enforce Module Boundaries** がめちゃ強いよ🔥
タグ（例：`type:domain`）で依存ルールを宣言して、違反を止められる〜！ ([npmdiff.dev][8])

---

## 8) よくあるハマりポイント集😂🧯

### Q1. domain から便利関数使いたい…でも infra にある🥲

👉 **shared を作ってそこへ移動**が定番✨
「どの層でも使える純粋ロジック」だけ置くよ🧊

### Q2. “barrel export（index.ts）” で境界をすり抜ける…😵

👉 barrel は便利だけど、境界チェックが弱くなることあるよ💦
最初は **やりすぎない**のがおすすめ！

### Q3. 型だけ import したい！（実体importは禁止したい）🥺

👉 TypeScriptなら `@typescript-eslint/no-restricted-imports` が、型import構文に対応してるよ✅ ([TypeScript ESLint][2])
さらに、ESLint側でも `allowTypeImports` が入ってきてる流れがあるよ🧠 ([ESLint][9])
（プロジェクトの方針次第で使い分けると◎）

---

## 9) ミニ演習🎮✨（15〜25分）

### ミッションA：わざと境界違反してみる😈

1. `src/app` のどこかで `src/infra` を import してみる
2. lint を実行
3. ちゃんと怒られたら勝ち🏆🎉

### ミッションB：正しい形に直す🛠️

* 「infra で実装したもの」は interface を domain に置く
* app は interface を使う
* 依存の組み立ては bootstrap でやる

DDDの気持ちよさ、ここで出るよ🥹✨

---

## 10) AIに頼むと爆速になるプロンプト集🤖💬

コピペで使えるやつ置いとくね〜🫶

* 「このフォルダ構成（domain/app/infra/bootstrap/shared）で、境界の許可import表を作って。例外（bootstrap）も含めて」
* 「このimport違反を直したい。依存の向きを守ったまま、最小変更でリファクタ案を3つ出して」
* 「循環参照が出た。依存グラフを想像して、切るべき依存と移動先（shared/domain/app）を提案して」

---

## 11) 仕上げチェックリスト✅💖

* [ ] domain が app/infra を import してない
* [ ] app が infra を import してない
* [ ] 依存の組み立ては bootstrap に寄せた
* [ ] lint が CI でも動く（PRで落ちる）
* [ ] shared が “便利箱化” してない（純粋ロジックだけ）

---

次の第80章は、ここで作った抽象（Repository）を「差し替えできて嬉しい〜〜！」って体験する回だよ🔁🎮✨

[1]: https://eslint.org/docs/latest/rules/no-restricted-imports?utm_source=chatgpt.com "no-restricted-imports - ESLint - Pluggable JavaScript Linter"
[2]: https://typescript-eslint.io/rules/no-restricted-imports/?utm_source=chatgpt.com "no-restricted-imports"
[3]: https://github.com/eslint/eslint/releases "Releases · eslint/eslint · GitHub"
[4]: https://www.jsboundaries.dev/docs/quick-start/?utm_source=chatgpt.com "Quick Start | JS Boundaries"
[5]: https://github.com/javierbrea/eslint-plugin-boundaries/releases "Releases · javierbrea/eslint-plugin-boundaries · GitHub"
[6]: https://sanyamaggarwal.medium.com/automate-circular-dependency-detection-in-your-node-js-project-394ed08f64bf?utm_source=chatgpt.com "Automate Circular Dependency Detection in your Node.js ..."
[7]: https://github.com/sverweij/dependency-cruiser/releases "Releases · sverweij/dependency-cruiser · GitHub"
[8]: https://npmdiff.dev/typescript/6.0.0-dev.20251228/6.0.0-dev.20251229/ "typescript 6.0.0-dev.20251228 → 6.0.0-dev.20251229 - npm diff"
[9]: https://eslint.org/blog/2025/10/eslint-v9.37.0-released/?utm_source=chatgpt.com "ESLint v9.37.0 released"
