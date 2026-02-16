# 第22章：`package.json` の最小設計📦📝

この章は「**コマンドが迷子にならない設計**」を作る回です😆✨
`package.json` は、言い換えると **“このプロジェクトの操作パネル🎛️”**。
ここが整うと、Docker/Compose からも VS Code からも CI からも、ぜんぶ同じ合言葉で動きます🔁💪

---

#### 🎯 この章のゴール

* `npm run dev / build / start` の3点セットで **操作が固定**できる🧭✨
* 「開発はTS直実行」「本番はdistをnodeで実行」みたいに **役割が分かれる**🎭
* `compose.yml` の `command:` でも迷わない（= どこから起動しても同じ）🐳✅

---

## 1) 最小設計の“結論”はこれ🧩

最小で強いのは **この3本柱**です👇

* `dev`：開発用（監視して即リロード👀🔁）
* `build`：配布・本番用にビルド（`dist/` を作る🏗️）
* `start`：本番実行（`dist/` を `node` で起動🚀）

この形にしておけば、たいていの人が一発で理解できます👍✨
（`npm` の scripts は公式に「任意のコマンドを定義して `npm run` で実行できる」仕組みとして整理されています。([docs.npmjs.com][1])）

---

## 2) “TSをラクに動かす”前提の最小 `package.json` 例🧪✨

第21章で触れた **tsxルート（開発が速い🥳）** をベースにすると、こうなります👇
（tsx の Watch mode は `tsx watch ./file.ts` で再実行してくれます👀🔁 ([tsx][2])）

```json
{
  "name": "node-ts-runtime-fixed",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "tsx watch src/index.ts",
    "build": "tsc -p tsconfig.json",
    "start": "node --enable-source-maps dist/index.js"
  },
  "devDependencies": {
    "tsx": "^4.21.0",
    "typescript": "^5.9.3"
  }
}
```

ポイント解説👇✨

* **`dev`**：`tsx watch` で保存のたびに再実行 → 開発が気持ちいい😆
  （tsx公式ドキュメントの Watch mode 解説。([tsx][2])）
* **`build`**：`tsc` で `dist/` を作る（`outDir: "dist"` は次章で整えればOK👌）
* **`start`**：`node dist/...` で “ビルド済み” を動かす（本番の形）🚀
  さらに `--enable-source-maps` を付けると、TSの行番号で追いやすくなります🕵️‍♂️✨（Nodeの起動フラグ例として広く案内されています。([Stack Overflow][3])）

> `typescript` の “Latest” が 5.9.3 として案内されているのも確認済みです。([npm][4])
> （TypeScript 5.9 の公式リリースノートもあります。([TypeScript][5])）

---

## 3) よくある「最小の罠」3つ💣（ここだけ避ければ勝ち）

### 罠①：`start` が “開発用” になってしまう😵

`start` は **本番起動の合言葉**にしておくのが超おすすめです👍
開発は `dev`、本番は `start` に分けると、未来の自分が助かります🛟✨

---

### 罠②：Windowsで scripts が動かない（`rm -rf` 問題）🪟⚠️

scripts にこんなの入れると👇

* `rm -rf dist`
* `export NODE_ENV=production`

Windowsだと死にがちです💀
この章では「最小」に絞って、**OS依存コマンドは極力入れない**のが安全です👌✨
（どうしてもやるなら、後で `rimraf` や `cross-env` を足すのが王道です🧰）

---

### 罠③：`tsx` は “型チェックしない” ので不安になる😰

大丈夫です😆✨
`tsx` は開発体験を速くする方向で、型チェックは IDE や別コマンドに任せる設計です（tsx公式ドキュメントでも「型エラーにブロックされず実行できる」趣旨が説明されています。([tsx][6])）

なので、最小構成では次を足すと安心感が爆上がり👇

```json
{
  "scripts": {
    "typecheck": "tsc --noEmit"
  }
}
```

> これで「実行は速い」「型は別で守る」になって強いです🛡️✨

---

## 4) scripts の命名ルール（迷子ゼロの型）🧠🧭

### ✅ 基本3つは固定で覚える

* `dev`
* `build`
* `start`（`npm start` で起動できるのも便利✨）

### ✅ 増やす時は `:` でグルーピング

* `build:prod`
* `test:unit`
* `db:migrate`

こうすると一覧が見やすいです👀✨

---

## 5) “自動で前後に挟む”小技：`pre` / `post` 🪄

npm scripts は、`preX` / `postX` を置くと **自動で前後に走る**仕組みがあります🔁✨ ([docs.npmjs.com][1])

例：`build` の前に型チェックを必ず走らせたい👇

```json
{
  "scripts": {
    "prebuild": "npm run typecheck",
    "build": "tsc -p tsconfig.json",
    "typecheck": "tsc --noEmit"
  }
}
```

* `npm run build` すると
  ✅ `prebuild` → ✅ `build` の順で走ります🎬✨ ([docs.npmjs.com][1])

---

## 6) 動作確認チェックリスト✅🧪

最後に、これだけ確認すればOKです👇

1. `npm run`（scripts一覧が出る👀）([docs.npmjs.com][1])
2. `npm run dev`（保存で再起動する👀🔁）([tsx][2])
3. `npm run build`（`dist/` ができる🏗️）
4. `npm start`（`dist/` が起動する🚀）

---

## まとめ🎁✨

この章の最重要ポイントはコレです👇

* **`dev/build/start` の3点セット**が “最小で強い”📦💪
* 開発は `tsx watch` で爆速👀🔁 ([tsx][2])
* 本番は `node dist/...`（+ source maps でデバッグ快適）🕵️‍♂️✨ ([Stack Overflow][3])
* `prebuild` などのフックで「ミスしない流れ」を作れる🪄 ([docs.npmjs.com][1])

---

次の第23章では、この `build` を受け取る側の **`tsconfig.json` を“薄く・安全に”** 整えて、`dist/` をちゃんと作れる状態にします🧊➡️🧠✨

[1]: https://docs.npmjs.com/cli/v10/using-npm/scripts/?utm_source=chatgpt.com "scripts"
[2]: https://tsx.is/watch-mode?utm_source=chatgpt.com "Watch mode"
[3]: https://stackoverflow.com/questions/53265182/how-to-use-source-maps-in-node-js?utm_source=chatgpt.com "How to use source maps in node js?"
[4]: https://www.npmjs.com/package/typescript?activeTab=versions&utm_source=chatgpt.com "typescript"
[5]: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-9.html?utm_source=chatgpt.com "Documentation - TypeScript 5.9"
[6]: https://tsx.is/typescript?utm_source=chatgpt.com "TypeScript"
