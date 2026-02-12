# 第02章：Windows + VS Code 開発環境セットアップ🛠️💻

この章が終わったら…👇
「TSプロジェクトを作る → ビルドする → きれいに整形する → ルール違反を見つける → Gitで管理する」まで一気にできるようになるよ〜！🎉😆


![Dev Toolkit](./picture/solid_ts_study_002_dev_toolkit.png)

---

## 0. まずは完成形イメージ🌈✨

![Project Structure](./picture/solid_ts_study_002_project_structure.png)

最終的に、プロジェクト直下がこんな感じになってればOKだよ👇📁

* `src/index.ts`（コード置き場）
* `dist/`（ビルド結果）
* `tsconfig.json`（TypeScript設定）
* `eslint.config.js`（ESLint設定：Flat Config）
* `.prettierrc`（Prettier設定）
* `package.json`（コマンド集）

---

## 1. VS Code を最新にする🧠✨

![VS Code Update](./picture/solid_ts_study_002_vscode_update.png)

VS Codeは月1くらいで新しいバージョンが出るよ🗓️（自動更新もOK）([Visual Studio Code][1])
直近のリリースノート例だと **2026-01-08に “December 2025 (1.108)” が出てる** みたいな感じで更新が回るよ📦✨([Visual Studio Code][2])

**やること**✅

* VS Codeを起動
* メニューから **ヘルプ → 更新の確認**（または自動更新に任せる）🔄✨

---

## 2. Node.js（LTS）を入れる🟩⚡

![Foundation Blocks](./picture/solid_ts_study_002_foundation_blocks.png)

TypeScript開発は Node.js が土台だよ〜！🧱✨
**Node.js 24.x は LTS（長期サポート）に移行**していて、サポートは **2028年4月末まで**の予定だよ📅🛡️([Node.js][3])
（現場はだいたい LTS 使うのが安心💞）

### インストール後の確認コマンド🔍

PowerShell / Windows Terminal で👇

```bash
node -v
npm -v
```

数字が出たら成功〜！🎉

---

## 3. Git を入れる🐙📌

Gitは「変更履歴を安全に保存するタイムマシン」だよ⏳✨
Windows向けの最新Gitは **2.52.0（2025-11-17）**って案内されてるよ🧰([Git][4])

### Gitの確認🔍

```bash
git --version
```

### 最低限の初期設定（これだけでOK）📝

```bash
git config --global user.name "あなたの名前"
git config --global user.email "you@example.com"
git config --global init.defaultBranch main
git config --global core.autocrlf true
```

> `core.autocrlf true` は Windowsの改行（CRLF）事故を減らす定番のやつだよ〜🧯✨

---

## 4. VS Code 拡張を入れる🧩✨（必須セット）

![Lint Format Tools](./picture/solid_ts_study_002_lint_format_tools.png)

入れておくと「ミスが減る」「読みやすくなる」「レビューが楽」になるよ〜💖🥳

### 4-1. ESLint（ルールチェック）🧹

* 拡張：**ESLint**（dbaeumer.vscode-eslint）

ESLintは最近 **Flat Config（`eslint.config.js`）が新しい標準**になってるよ📘([ESLint][5])
VS CodeのESLint拡張側も、Flat config前提の説明があるよ🧠([Visual Studio Marketplace][6])

### 4-2. Prettier（自動整形）💅✨

* 拡張：**Prettier - Code formatter**

最近の Prettier 3.7 は TypeScriptまわりの整形も磨いてるよ〜✨([Prettier][7])

### 4-3. AI支援（Copilot系）🤖💡

VS CodeまわりはAI機能がどんどん統合されてて、**Copilot拡張は“早めに廃止予定”でMarketplaceから消える予定**って明言があるよ⚠️([Visual Studio Code][8])
なので今後は「拡張を入れる」より、VS Code内の **Copilot/Chat/Agent系UIにサインインして使う**流れが強くなるはずだよ〜🔐✨

---

## 5. いよいよ TypeScript プロジェクト作成🎮✨（超ミニ）

### 5-1. フォルダ作って開く📁

```bash
mkdir solid-ts-ch02
cd solid-ts-ch02
code .
```

### 5-2. npm初期化📦

```bash
npm init -y
```

### 5-3. TypeScriptを入れる（プロジェクト内に入れるのが安定）🧠

![TSC Machine](./picture/solid_ts_study_002_tsc_machine.png)

TypeScript公式の案内は `npm install -g typescript` だけど、教材では **プロジェクトごとに入れる**のが事故りにくいよ〜🫶
（とはいえ “最新は 5.9 系” って公式も案内してるよ）([TypeScript][9])

```bash
npm i -D typescript
npx tsc --init
```

---

## 6. tsconfig を「いい感じ」にする🛡️✨

`tsconfig.json` をちょこっと編集しよ〜✍️
（迷ったらこれでOKなバランス⚖️）

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",

    "rootDir": "src",
    "outDir": "dist",

    "strict": true,
    "noUncheckedIndexedAccess": true,

    "esModuleInterop": true,
    "skipLibCheck": true
  },
  "include": ["src"]
}
```

---

## 7. まず動くコードを書く🚀✨

`src/index.ts` を作って👇

```ts
const name: string = "Campus Café";
console.log(`Hello, ${name}! ☕️✨`);
```

---

## 8. npmスクリプト（コマンド）を登録する🎛️✨

`package.json` の `"scripts"` をこんな感じにしておくと超ラク🧸

```json
{
  "scripts": {
    "build": "tsc",
    "dev": "tsc -w",
    "start": "node dist/index.js",
    "typecheck": "tsc --noEmit"
  }
}
```

動作確認いくよ〜！💨

```bash
npm run build
npm run start
```

☕️✨ が表示されたら勝ち〜！！🎉🥳

---

## 9. ESLint + Prettier をセットアップ🧹💅✨

### 9-1. インストール📦

```bash
npm i -D @eslint/js eslint typescript-eslint prettier
```

TypeScript向けESLintの公式Quickstartは **typescript-eslint** の “flat config” ルートが用意されてるよ🧠✨([TypeScript ESLint][10])

### 9-2. `eslint.config.js` を作る🧩

プロジェクト直下に `eslint.config.js` 👇

```js
import eslint from "@eslint/js";
import tseslint from "typescript-eslint";

export default [
  eslint.configs.recommended,
  ...tseslint.configs.recommended,

  {
    files: ["**/*.ts"],
    languageOptions: {
      parserOptions: {
        project: true
      }
    }
  },
  {
    ignores: ["dist/**", "node_modules/**"]
  }
];
```

### 9-3. ESLintコマンド追加🧪

`package.json` に追記👇

```json
{
  "scripts": {
    "lint": "eslint .",
    "lint:fix": "eslint . --fix"
  }
}
```

実行っ✨

```bash
npm run lint
```

### 9-4. Prettier設定💅

`.prettierrc` を作って👇（超ベーシック）

```json
{
  "singleQuote": true,
  "semi": true
}
```

`package.json` に追記👇

```json
{
  "scripts": {
    "format": "prettier . --write"
  }
}
```

実行っ✨

```bash
npm run format
```

---

## 10. Gitで「保存」しておく📌✨

![Git Time Machine](./picture/solid_ts_study_002_git_timemachine.png)

```bash
git init
git add .
git commit -m "ch02: setup TypeScript project"
```

ここまでできたら、もう一生強い💪🥹✨

---

# ミニ課題（この章のゴール）🎓🎉

次を全部クリアしたら合格〜！✅💮

1. `npm run build` が通る🎯
2. `npm run start` でメッセージが出る☕️✨
3. `npm run lint` が動く🧹
4. `npm run format` が動く💅
5. `git commit` まで完了📌

---

# よくある詰まりポイント集🧯😵‍💫

### ❌ `node` が見つからない

✅ ターミナルを開き直す🔄
✅ それでもダメなら再インストール（PATHが通ってない系）🛠️

### ❌ `tsc` が見つからない

✅ グローバルじゃなくてOK！
`npx tsc -v` で確認してね🫶

### ❌ VS CodeでESLintが効かない

✅ ESLint拡張が入ってるか確認
✅ `eslint.config.js` がプロジェクト直下にあるか確認（Flat Config前提）([ESLint][5])
✅ “フォルダを開く” がルートになってるか確認📁（サブフォルダだけ開くと迷子になりがち💦）

---

次の章（第3章）では、この環境の上で「クラス設計の最低限（class / interface / private / readonly）」を“注文アプリ題材”で作り始めるよ〜🏫📦✨

[1]: https://code.visualstudio.com/docs/setup/setup-overview?utm_source=chatgpt.com "Setting up Visual Studio Code"
[2]: https://code.visualstudio.com/updates?utm_source=chatgpt.com "December 2025 (version 1.108)"
[3]: https://nodejs.org/en/blog/release/v24.11.0?utm_source=chatgpt.com "Node.js v24.11.0 (LTS)"
[4]: https://git-scm.com/install/windows?utm_source=chatgpt.com "Git - Install for Windows"
[5]: https://eslint.org/docs/latest/use/configure/migration-guide?utm_source=chatgpt.com "Configuration Migration Guide"
[6]: https://marketplace.visualstudio.com/items?itemName=dbaeumer.vscode-eslint&utm_source=chatgpt.com "VS Code ESLint extension"
[7]: https://prettier.io/blog/2025/11/27/3.7.0?utm_source=chatgpt.com "Prettier 3.7: Improved formatting consistency and new ..."
[8]: https://code.visualstudio.com/blogs/2025/11/04/openSourceAIEditorSecondMilestone?utm_source=chatgpt.com "Open Source AI Editor: Second Milestone"
[9]: https://www.typescriptlang.org/download/?utm_source=chatgpt.com "How to set up TypeScript"
[10]: https://typescript-eslint.io/getting-started/?utm_source=chatgpt.com "Getting Started"
