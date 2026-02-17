# 第23章：`tsconfig.json` は “まず薄く”🧊➡️🧠

この章はひとことで言うと——
**「TS設定で溺れずに、ちゃんと動く“最低ライン”だけ先に固める」**回です😆✨
`tsconfig.json` は “正しさ” だけじゃなく **ビルド結果・実行・デバッグ体験**まで変えます🧩

---

## 1) そもそも `tsconfig.json` って何者？🧠📄

`tsconfig.json` は **TypeScriptコンパイラ（`tsc`）の設定ファイル**です⚙️
ここが重いとこうなります👇

* 設定が多すぎて「何を変えたらいいの…😵」
* ESM/CJSやimport解決で「なんで動かないの…😇」
* デバッグの行番号がズレて「どこで落ちたの…🫠」

だから方針はこれです👇

✅ **“まず薄く” = 必要最低限だけ置く**

![Heavy vs Light Config](./picture/docker_runtime_fix_ts_study_023_01_complexity_trap.png)

✅ 増やすのは「困ってから」でOK🙆‍♂️✨

---

## 2) 2026年のスタート地点はこう考える🛫✨

最近のTypeScriptは、`tsc --init` が **いきなり現代寄りの設定で生成**される流れになっています（TS 5.9で方針がかなり整理された）🧹✨
特に **`module` や `target` を現代寄りに寄せる**のがデフォルトの方向性です。([Microsoft for Developers][1])

さらにTS 5.9では、Nodeの挙動を “固定的に” 近似するための **`--module node20`** も安定オプションとして入ってきました（`nodenext`は将来追従寄り、`node20`は安定寄り）🧭([Microsoft for Developers][1])

---

## 3) 今回のゴール🎯💡

この章でできるようになること👇

* `tsconfig.json` を **“薄い版”**で作れる🧊✨
* **Nodeで動かす前提**の最低限（import解決ふくむ）が分かる🧯
* `tsc` が本当にその設定を読んでるか確認できる✅
* デバッグが幸せになる下準備（source map）までできる🕵️‍♂️✨

---

## 4) まずは “薄い tsconfig” を置こう📄🧊

構成の前提はよくあるこれ👇

* `src/` にTSソース
* `dist/` にビルド結果

おすすめの **薄い `tsconfig.json`** はこれです👇（まずこれでOK！）

![Minimal tsconfig Structure](./picture/docker_runtime_fix_ts_study_023_02_minimal_structure.png)

```json
{
  "compilerOptions": {
    "target": "ESNext",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",

    "rootDir": "./src",
    "outDir": "./dist",

    "strict": true,
    "skipLibCheck": true,

    "sourceMap": true,

    "types": ["node"]
  },
  "include": ["src/**/*.ts"],
  "exclude": ["node_modules", "dist"]
}
```

### これだけ入ってれば勝てる理由🏆✨

* **`module` + `moduleResolution` をセット**にしておくと、import周りの事故が激減します🧯
  （`node16` / `nodenext` は “Nodeで実行する” 前提の解決方式）([TypeScript][2])
* **`types: ["node"]`** を明示すると、`process` や `Buffer` が急に未定義にならず安心😌
  （TS 5.9の `tsc --init` が `types: []` を生成するのも「勝手に色々読み過ぎない」方向性の一環）([Microsoft for Developers][1])
* **`sourceMap: true`** はデバッグの幸福度が上がります🕵️‍♂️✨（後で効く！）

---

## 5) 依存も “最小で” 揃える📦✨

![Types Node Adapter](./picture/docker_runtime_fix_ts_study_023_03_types_adapter.png)

最低限これだけ入れればOK👇

```bash
npm i -D typescript @types/node
```

* `@types/node` がないと、`types: ["node"]` を書いても型が見つからずコケます💥🙂

---

## 6) “このtsconfig読んでる？”を一発で確認する✅👀

![Config Truth Reveal](./picture/docker_runtime_fix_ts_study_023_04_truth_reveal.png)

設定が効いてるか怪しい時はこれが最強です👇

```bash
npx tsc --showConfig
```

出力の中に、あなたが書いた `module` / `target` / `outDir` が反映されてたら勝ち🏁🎉

---

## 7) よくある詰まりポイント3つ（先に潰す）💣🧯

### ❶ `import` の解決が謎すぎる😇

Nodeでそのまま動かす前提だと、**“Nodeが嫌がるimport”** を早めに弾きたいんですよね。

ここで大事なのが👇

* **`moduleResolution: "bundler"` は便利だけど “感染する”**（バンドラでしか動かないimportを許しやすい）
* **Node実行前提なら `nodenext` の方が安全寄り**（Nodeで動く形に寄せる）([TypeScript][3])

※この話は次章（ESM/CJS）で完全に回収するので、ここでは「Nodeで動く寄りに倒す」だけ覚えればOKです🧠✨

---

### ❷ `process is not defined` / `Cannot find name 'Buffer'` 😵

だいたいこれ👇

* `@types/node` 入れてない
* `types: ["node"]` 書いてない（または別tsconfigを読んでる）

✅ さっきの「薄いtsconfig」＋ `@types/node` で解決します👍✨

---

### ❸ `dist` に出力されない / 変な場所に出る🫠

原因はだいたい👇

* `rootDir` / `outDir` がない
* `include` がズレてる
* `exclude` に `src` を入れちゃってる（あるある😂）

✅ まずはこの章のテンプレから動かすのが最短です🏃‍♂️💨

---

## 8) デバッグを “気持ちよく” する小ワザ🕵️‍♂️✨

![Source Map Lens](./picture/docker_runtime_fix_ts_study_023_05_source_map_lens.png)

`sourceMap: true` を付けたら、実行側でも source map を使うと幸せです😊

Nodeは `--enable-source-maps` で **スタックトレースを元ソース寄りにしてくれます**✨
ただし **有効化はコストがある**（`Error.stack` 参照時に遅くなる可能性）ので、必要な場面で使うのがコツです⚖️([Node.js][4])

例👇

```bash
node --enable-source-maps dist/index.js
```

---

## 9) VS Code側の “効いてる感” チェック✅🧠

![VS Code Version Alignment](./picture/docker_runtime_fix_ts_study_023_06_vscode_alignment.png)

VS Codeで「なんか型が変…🤔」って時はこれ👇

* コマンドパレットで **TypeScript: Select TypeScript Version**
  → **Use Workspace Version**（プロジェクトのTSを使う）を選ぶ🎯

これで “エディタが見てるTS” と “コンパイルしてるTS” がズレにくくなります😌✨

---

## 10) AIに投げると爆速になる指示例🤖⚡

✅ `tsconfig` を薄くしたい時：

> 「Nodeで実行するTypeScriptプロジェクト。tsconfigを最小構成にして、import解決はNodeNext、出力はdist、src配下だけ対象、sourceMapは有効にして。」

✅ 変なエラーが出た時：

> 「このエラーを“tsconfigの観点”で原因候補を3つ出して。どれが濃厚か順番もつけて。」

---

## 11) ミニ課題🎒🔥（5分で終わる）

1. `src/index.ts` を作る✍️
2. `npx tsc` で `dist/index.js` が出るのを確認✅
3. わざと `throw new Error("boom")` して
4. `node dist/index.js` と `node --enable-source-maps dist/index.js` の **スタック表示の違い**を見る👀✨([Node.js][4])

---

## まとめ🎁✨

* `tsconfig.json` は **まず薄く**でOK🧊
* Nodeで動かす前提なら、`module/moduleResolution` を **Node寄りに倒す**と事故りにくい🧯([TypeScript][2])
* TS 5.9 以降は `tsc --init` も現代寄りになってる（ただしアプリ用途なら削るのも正解）🧹([Microsoft for Developers][1])
* source map は後で効く！デバッグが幸せになる🕵️‍♂️✨([Node.js][4])

---

次の第24章は、ここで触れた **ESM/CJSと `"type": "module"` の地雷**を「最低ラインだけ」で超えます🧯🔥
（`import` でコケた時に “何を確認すべきか” が分かる回！）

[1]: https://devblogs.microsoft.com/typescript/announcing-typescript-5-9/ "Announcing TypeScript 5.9 - TypeScript"
[2]: https://www.typescriptlang.org/tsconfig/moduleResolution.html "TypeScript: TSConfig Option: moduleResolution"
[3]: https://www.typescriptlang.org/docs/handbook/modules/guides/choosing-compiler-options.html "TypeScript: Documentation - Modules - Choosing Compiler Options"
[4]: https://nodejs.org/api/cli.html?utm_source=chatgpt.com "Command-line API | Node.js v25.6.0 Documentation"
