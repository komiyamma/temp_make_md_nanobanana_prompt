# 第09章：tsconfig最小セット（まず strict）🧷

![安全ピン](./picture/tdd_ts_study_009_safety_pin.png)

## 🎯目的

* **tsconfig を“必要十分”で作れる**ようになる🧠
* **strict を味方**にして、TDDのサイクルを安定させる🧪
* import周りで詰まりやすい **module / moduleResolution** の方向性を決める🌿

---

## 📚まずイメージ：tsconfig は「型チェックのルールブック」📘

![画像を挿入予定](./picture/tdd_ts_study_009_rulebook_strict.png)

TypeScriptは、コードを読むときに「どう解釈する？どこまで厳しく見る？」を決めないと迷子になっちゃうのね😵‍💫
その**ルールが tsconfig.json** で、ここが整うと：

* テストを書く前に **型で事故が減る**🛡️
* 「たまに落ちる」「環境差で動かない」が減る✨
* AIに聞いたときも、**前提が揃う**から回答が安定する🤖

---

## ✅この章の結論（最小セットで大事なのはココだけ！）💡

![strict_master_switch](./picture/tdd_ts_study_009_strict_master_switch.png)


1. **`"strict": true`**（まずON）
   　→ strict は“まとめスイッチ”で、将来のTSアップデートでチェックが増えることもあるよ（＝新しい型エラーが出ることがある）🧠✨ ([typescriptlang.org][1])

2. **`module` と `moduleResolution` を「実行環境」に合わせる**

![module_resolution_plugs](./picture/tdd_ts_study_009_module_resolution_plugs.png)


* Node寄りなら **`nodenext`** が基本になりやすい（公式もそう案内してるよ） ([typescriptlang.org][2])
* バンドラー（Vite/Vitest）寄りなら **`bundler`** が楽（相対importで拡張子を強制しない、など） ([typescriptlang.org][3])

3. **`target` は今のJSに合わせる（ES2023あたり）**

![target_es2023_archer](./picture/tdd_ts_study_009_target_es2023_archer.png)

   TypeScript 5.9 だと Node向け設定として **`node20`** みたいな“安定モード”も用意されてるよ（`target es2023` を暗黙に使う、など）🧩 ([typescriptlang.org][4])
   （※2026-01-19 時点の安定版は npm 上は 5.9 系） ([NPM][5])

---

## 🧷まずはテンプレを1つ選ぼう（迷ったらAが無難）🙂

### A) バンドラー/Vitest寄り（おすすめ）🧪🧩

Vite/Vitest系の雰囲気で進めるならこっちがラク！
（相対importで拡張子問題が起きにくいよ） ([typescriptlang.org][3])

```json
{
  "compilerOptions": {
    "target": "ES2023",
    "module": "ESNext",
    "moduleResolution": "Bundler",

    "strict": true,

    "noEmit": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true
  },
  "include": ["src", "tests"]
}
```

### B) Node（サーバー/CLI）寄り 🟩🖥️

Nodeの実行と相性を取りにいくならこっち。公式的にも Node なら `nodenext` が基本寄りだよ🌿 ([typescriptlang.org][2])

```json
{
  "compilerOptions": {
    "target": "ES2023",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",

    "strict": true,

    "outDir": "dist",
    "rootDir": "src",
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true
  },
  "include": ["src", "tests"]
}
```

> 💬ちなみに：Node は 2026-01-13 時点で **24.13.0 (LTS)** が出てるよ（参考）🟢 ([nodejs.org][6])
> でも tsconfig は **「安定」優先**でOK！“今の最新”に追いかけ回されるより、TDDが気持ちよく回るほうが勝ち🏁✨

---

## 🧪手を動かす（この章のゴール：型チェックが安定して通る）🔧💨

### 1) tsconfig を作る（生成→最小に整える）🧰

```powershell
## まだ tsconfig が無いなら
npx tsc --init --strict
```

できた `tsconfig.json` を開いて、上の **A or B** に寄せて整えるよ✍️✨
（コメントだらけでもOK。まず“動く最小”が正義👑）

---

### 2) 型チェック用の npm script を用意する🧪

`package.json` にこれを足す👇

```json
{
  "scripts": {
    "typecheck": "tsc -p tsconfig.json"
  }
}
```

実行✨

```powershell
npm run typecheck
```

---

## 🧪ミニ演習：strict が“守ってくれる感じ”を体験しよ🛡️✨

![strict_guard_any](./picture/tdd_ts_study_009_strict_guard_any.png)


### ❌わざと「strict に怒られる」コードを置く（体験が大事！）😈

`src/demo.ts` を作ってこれ👇

```ts
export function priceLabel(yen) {
  try {
    return yen.toFixed(0) + "円";
  } catch (e) {
    return e.message;
  }
}
```

`npm run typecheck` をすると、だいたいこんな系で怒られるはず👇

* `yen` が **any 扱い**っぽい（暗黙any）😵
* `catch (e)` の `e` が **unknown** で、`message` が読めない💥（strictの一部）

---

### ✅「strict と仲良くする」直し方（最小でOK）🙂

```ts
export function priceLabel(yen: number): string {
  try {
    return yen.toFixed(0) + "円";
  } catch (e: unknown) {
    if (e instanceof Error) return e.message;
    return "unknown error";
  }
}
```

ポイントはこれだけ💡

* **引数・戻り値**をまず置く（TDDの“仕様っぽさ”が出る）🧪
* `catch` は **unknown 前提で絞り込み**（事故りにくい）🛡️

---

## 🌿よくある詰まりポイント（ここだけ先に潰す）🧯

### ① import が地獄…😵‍💫 → `moduleResolution` を見直す

* バンドラー寄りなら `Bundler` がラク（相対importで拡張子必須になりにくい） ([typescriptlang.org][3])
* Node寄りなら `NodeNext`（Nodeの挙動に合わせる） ([typescriptlang.org][2])

### ② Windowsでは動くのにCIで落ちる😇

![case_sensitivity_teacher](./picture/tdd_ts_study_009_case_sensitivity_teacher.png)


だから **`forceConsistentCasingInFileNames: true`** は入れとくのが安心だよ🧷
（Windowsは大文字小文字に甘い→CIで爆発💥を予防）

### ③ `skipLibCheck` ってズル？🥺

* ズルじゃないよ！🫶
* まずは学習の足を止めないのが大事。必要になったら外せばOK✨

---

## 🤖AIの使い方（この章のおすすめプロンプト）💬✨

VS CodeのAIにこう聞くと超スムーズだよ〜！🥰

* 「この tsconfig の各オプションを **“中学生にも分かる言葉”で1行ずつ**説明して」📘
* 「`npm run typecheck` のエラー貼るね。**原因→最小修正→直した結果どう変わるか**で教えて」🧑‍🏫
* 「このプロジェクトは（Node / Vite）寄り。**module と moduleResolution の最適セット**を2案出して、メリデメも書いて」🧩

> ⚠️コツ：AIの提案はそのまま採用せず、**typecheck が通るか**で判断ね🧪✅

---

## ✅チェック（合格ライン）🎓✨

* `npm run typecheck` が **安定して通る**✅
* わざと壊したとき、**strict がどこで怒るか説明できる**🗣️
* `module / moduleResolution` を **A（Bundler）かB（NodeNext）で選べる**🙂

---

必要なら次で、あなたの想定（ライブラリ？小アプリ？NodeのAPI多め？）に合わせて、**A/Bどっちが本命か**と、**“後で困らない最小追加オプション3つ”**（例：`types` の入れ方、`lib` の考え方、テスト用 tsconfig 分離）までセットで整えるよ〜🧸✨

[1]: https://www.typescriptlang.org/tsconfig/strict.html "TypeScript: TSConfig Option: strict"
[2]: https://www.typescriptlang.org/tsconfig/module "TypeScript: TSConfig Option: module"
[3]: https://www.typescriptlang.org/tsconfig/moduleResolution.html "TypeScript: TSConfig Option: moduleResolution"
[4]: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-9.html?utm_source=chatgpt.com "Documentation - TypeScript 5.9"
[5]: https://www.npmjs.com/package/typescript?utm_source=chatgpt.com "TypeScript"
[6]: https://nodejs.org/en/blog/release/v24.13.0?utm_source=chatgpt.com "Node.js 24.13.0 (LTS)"
