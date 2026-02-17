# 第21章：まずは“ラクな方”で成功体験😆✨（tsxルート）

この章は **「TypeScript を“ビルドせずに”そのまま動かす」** で、まず **動いた！🎉** を最速で取りにいきます💨
（ランタイム固定＝コンテナ内で動かす前提だから、PC側のNode事情に左右されにくくて気持ちいいやつ😆）

---

## この章のゴール🎯✨

* ✅ `src/index.ts` を **そのまま実行**できる（`npm run dev` で起動）
* ✅ 保存したら **自動で再実行**される（`tsx watch`）👀🔁
* ✅ “開発に必要なコマンド”が **迷子にならない scripts 設計**ができる📦🧭
* ✅ 「型チェックは別でやる」も理解する🧠🧷

---

## tsxって何者？🤔🧩

![tsx Speed Concept](./picture/docker_runtime_fix_ts_study_021_01_tsx_rocket.png)

`tsx` は **Node.js を拡張して**、TypeScript/ESM を **手間少なく実行**するためのツールです。内部的には esbuild を使って高速に動かします⚡（開発向け）([npm][1])
公式サイトでも **Watch mode（変更で自動再実行）** を強く推してます👀✨([tsx][2])

> 重要ポイント⚠️
> **tsx は “型チェックをしません”**（実行はするけど、型の正しさは保証しない）
> → だからこの章では **`typecheck` コマンド**も一緒に作ります🧼✅（後で事故りにくくなる）

---

## まず作るもの（最小セット）🧱✨

ディレクトリはこれだけでOK👇

```text
my-app/
  src/
    index.ts
  package.json
  tsconfig.json
```

---

## 1) 依存を入れる📦💿

コンテナ内（または compose で入ったシェル）で👇

```bash
npm i -D typescript tsx
```

参考：TypeScript の最新版は npm で配布されていて、5.9 系が “currently 5.9” と案内されています([TypeScript][3])
tsx も npm で配布され、最近まで更新されています([npm][1])

---

## 2) `package.json` を “迷子にならない形”にする🧭📦

ポイントはこれ👇

* `dev`：開発用（watchで回す）👀
* `typecheck`：型チェック（tsxがやらない分ここで担保）✅
* `build/start`：将来の本番ルート用（今は置くだけでOK）🏗️

```json
{
  "name": "my-app",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "tsx watch src/index.ts",
    "typecheck": "tsc --noEmit",
    "build": "tsc -p tsconfig.json",
    "start": "node dist/index.js"
  },
  "devDependencies": {
    "tsx": "^4.21.0",
    "typescript": "^5.9.3"
  }
}
```

### ここが“設計の超入門”ポイント🧠✨

![Scripts Architecture](./picture/docker_runtime_fix_ts_study_021_02_scripts_design.png)

「実行」と「検査」を分けるのがコツです👇

* 実行（速さ優先）🚀 → `npm run dev`
* 検査（安全優先）🛡️ → `npm run typecheck`

この分離だけで、未来の自分が助かります😂🙏

---

## 3) `tsconfig.json` は “薄くてOK”🧊📝

![Minimal tsconfig](./picture/docker_runtime_fix_ts_study_021_03_minimal_tsconfig.png)

TypeScript 5.9 では `tsc --init` の生成が **よりミニマル寄り**になった流れがあります([TypeScript][4])
ここでは最小の実用ラインだけ置きます👇

```json
{
  "compilerOptions": {
    "target": "ES2023",
    "module": "node20",
    "moduleResolution": "node20",
    "outDir": "dist",
    "strict": true,
    "skipLibCheck": true
  },
  "include": ["src"]
}
```

* `outDir: dist` は **後で build/start ルート**に移る時に効きます🏗️
* `module/moduleResolution: node20` は TypeScript 5.9 の “安定オプション”として説明されています([TypeScript][4])

---

## 4) `src/index.ts` を作る（超ミニAPI）🧪🌱

外部ライブラリなしで、HTTPサーバだけ立てます👇
（余計な依存を増やさない＝トラブル減る💡）

```ts
import { createServer } from "node:http";

const server = createServer((req, res) => {
  res.writeHead(200, { "content-type": "text/plain; charset=utf-8" });
  res.end("Hello from tsx 😆✨\n");
});

server.listen(3000, "0.0.0.0", () => {
  console.log("Server ready 🚀 http://localhost:3000");
});
```

---

## 5) 起動して成功体験🎉🔥

![Success Output](./picture/docker_runtime_fix_ts_study_021_04_hello_tsx.png)

```bash
npm run dev
```

* ブラウザで `http://localhost:3000` を開く
* `Hello from tsx 😆✨` が出たら勝ち🏆🎊

さらに **ファイルを保存**してログが再実行されたら、watchも勝ち👀🔁([tsx][5])

---

## 6) Watchが効かないときの“現実的対処”🧯🪟🐧

Windows + Docker（WSL2まわり）だと、**ファイル変更イベントが届かない**系のハマりが起きることがあります😇
WSL2 が Windows ドライブ上のファイル（9P 経由）を扱うとき、inotify 系イベントがうまく伝播しない…という話が有名です([Stack Overflow][6])
さらに tsx の watch が Docker で反応しないケース報告もあります([GitHub][7])

### 対処A（いちばん効く）🥇

**プロジェクトを WSL2 側の Linux ファイルシステムに置く**（例：`\\wsl$\Ubuntu\home\...`）
→ 監視が安定しやすい✨

### 対処B（いったん進む）🚶‍♂️

![Manual Restart Fallback](./picture/docker_runtime_fix_ts_study_021_05_manual_restart.png)

tsx watch には「**Enter（Return）で手動再実行**」があります⌨️🔁([tsx][5])
監視が死んでも、最悪これで前に進めます（教材的に大事！）

### 対処C（監視対象を明示）🎯

`--include` / `--exclude` で watch 対象を調整できます👀🧰([tsx][5])

---

## 7) VS Codeでデバッグしたい（tsx + inspector）🕵️‍♂️✨

![VS Code Debugger Attach](./picture/docker_runtime_fix_ts_study_021_06_vscode_attach.png)

tsx公式に **VS Codeでのアタッチ手順**があります👍([tsx][8])
やることはシンプル👇

### ① tsx を inspector 付きで起動

```bash
tsx --inspect-brk src/index.ts
```

### ② VS Code 側の `launch.json`（例）

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Attach to tsx",
      "type": "node",
      "request": "attach",
      "port": 9229,
      "skipFiles": ["<node_internals>/**", "${workspaceFolder}/node_modules/**"]
    }
  ]
}
```

ちなみに Node の `--inspect-brk` 自体も公式ドキュメントで説明されています🧠🔍([Node.js][9])

---

## 8) AIに投げるときの“ちょうどいい一言”🤖💬

* 「tsx で TypeScript を watch 実行する `package.json` scripts 作って。`typecheck` も入れて」
* 「tsconfig を薄くして、ESM で詰まりにくい設定にして（module=node20 で）」
* 「`src/index.ts` を最小のHTTPサーバで作って。ポート3000で」

“自分のゴール（dev/typecheck）”を先に言うと、AIがブレにくいです😆✨

---

## まとめ🎁✨（この章で手に入ったもの）

* 🚀 TSを **即実行**できた（ビルド待ちゼロ）
* 👀 保存で **自動再実行**の開発ループができた([tsx][5])
* ✅ 「型チェックは別」もセットで理解できた
* 🧭 scripts を “設計”できた（迷子にならない）

次の章以降で、ここから **`tsc -w` ルート（王道）**に移して「本番も安心」にしていくと最強になります💪🔥

[1]: https://www.npmjs.com/package/tsx?utm_source=chatgpt.com "tsx"
[2]: https://tsx.is/?utm_source=chatgpt.com "TypeScript Execute (tsx) | tsx"
[3]: https://www.typescriptlang.org/download/?utm_source=chatgpt.com "How to set up TypeScript"
[4]: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-9.html?utm_source=chatgpt.com "Documentation - TypeScript 5.9"
[5]: https://tsx.is/watch-mode?utm_source=chatgpt.com "Watch mode"
[6]: https://stackoverflow.com/questions/78258259/development-tools-wont-watch-for-changes-in-wsl2?utm_source=chatgpt.com "Development tools won't watch for changes in WSL2"
[7]: https://github.com/privatenumber/tsx/issues/266?utm_source=chatgpt.com "Watch not working with docker · Issue #266"
[8]: https://tsx.is/vscode?utm_source=chatgpt.com "VS Code debugging"
[9]: https://nodejs.org/en/learn/getting-started/debugging?utm_source=chatgpt.com "Debugging Node.js"
