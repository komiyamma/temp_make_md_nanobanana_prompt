# 第05章：Windows + VS Codeで“動く最小環境”を作る🪟💻

![testable_ts_study_005_toolbox.png](./picture/testable_ts_study_005_toolbox.png)

この章はね、「迷子にならない土台」を作る回だよ〜！🌱
ゴールは **“テストが走る✅”** まで。ここができると、次の章からの「I/Oを外に出す設計」がスイスイ進むよ🧪🚀

---

## 0) 今日時点の“おすすめ最新版”メモ📝

✨* **Node.js**：**v24 系が Active LTS**（例：**v24.13.0** は 2026-01-13 のセキュリティリリース）🔒🧯 ([Node.js][1])



  * v25 は “Current”（新しめだけど変化が多い）なので、学習＆安定重視なら **LTSが安心**だよ🙆‍♀️ ([Node.js][1])
* **TypeScript**：npm の最新は **5.9.3**（2025-09-30 公開）📘✨ ([npm][2])
* **Vitest**：**Vitest 4.0** が 2025-10-22 にリリース🎉（以後 4.x 系で更新中）🧪⚡ ([Vitest][3])
* **VS Code で Vitest**：Testingビューから触れる公式拡張あり🧩👀 ([GitHub][4])

---

## 1) “最低限”入ってればOKなもの🎒✨* Node.js（LTS）

🟩


* Git（後でGitHub連携に使うよ）🐙
* VS Code（拡張入れる）🧩

---

## 2) Node.js を入れて動作確認する🔧✅## 2-1. いちばん安心ルート：公式インストーラ🧑‍🏫✨

公式のダウンロードページから **LTS（今は v24 系）** を選んで入れるのが一番トラブル少ないよ🙆‍♀️ ([Node.js][5])



## 2-2. コマンド派：winget（※環境によってはクセあり）

⌨️🪄PowerShell（管理者）で：



```powershell
winget install -e --id OpenJS.NodeJS.LTS
```

ID 自体はこれでOK🙆‍♀️ ([Winget.run][6])
ただし winget は **PATH 周りの挙動や更新タイミング**でハマる報告もあるから、詰まったら公式インストーラに切り替えるのが早いよ💡 ([GitHub][7])

## 2-3. バージョン確認✅

```powershell
node -v
npm -v
```

`v24.x.x` みたいに出たらOK〜！🎉 ([Node.js][1])

---

## 3) “空プロジェクト”を作る📁✨

（テストが走る土台）ここからは、フォルダ作って、TypeScript と Vitest を入れて、**最初のテスト1本**を通すよ🧪🎀



## 3-1. フォルダ作成＆VS Codeで開く📂

```powershell
mkdir testable-ts
cd testable-ts
code .
```

## 3-2. npm 初期化📦

```powershell
npm init -y
```

## 3-3. 必要パッケージを入れる🧰✨

```powershell
npm i -D typescript vitest @types/node
```

* TypeScript は npm 最新だと 5.9.3 だよ📘 ([npm][2])
* Vitest は 4.x が現行ライン🧪 ([Vitest][3])

---

## 4) tsconfig を用意する🛠

️📘（“あとで困らない”設定）まず雛形を作るよ：



```powershell
npx tsc --init --strict
```

次に `tsconfig.json` を **この形に寄せる**のがおすすめ👇（コピペOK！）
ポイントは **module / moduleResolution を “node20” にして安定させる**ところだよ✨（TS 5.9 で “node20” が安定オプションとして用意されてる） ([TypeScript][8])

```json
{
  "compilerOptions": {
    "target": "es2023",
    "module": "node20",
    "moduleResolution": "node20",

    "rootDir": ".",
    "outDir": "dist",

    "strict": true,
    "skipLibCheck": true,
    "types": ["node"]
  },
  "include": ["src/**/*.ts"]
}
```

---

## 5) プロジェクト構成（I/O分離しやすい形）

を先に作る🧱✨この講座らしく、最初から「中心」と「外側」を置きやすい形にしちゃうよ🏠➡️🌍



```powershell
mkdir src
mkdir src\core
mkdir src\adapters
```

* `src/core`：**純粋ロジック置き場**🍰（テストが超書きやすい）
* `src/adapters`：**I/O（HTTP/ファイル/DB/時刻/ログなど）置き場**🚪🌀

---

## 6) “最初のテスト1本”を書いて走らせる🧪🎉## 6-1. 例：足し算（まず成功体験✨

）`src/core/add.ts`



```ts
export function add(a: number, b: number): number {
  return a + b;
}
```

`src/core/add.test.ts`

```ts
import { describe, it, expect } from "vitest";
import { add } from "./add";

describe("add", () => {
  it("2 + 3 = 5", () => {
    expect(add(2, 3)).toBe(5);
  });
});
```

## 6-2. package.json に scripts を追加🎀`package.json` の `"scripts"` をこうするよ👇



```json
{
  "scripts": {
    "test": "vitest run",
    "test:watch": "vitest"
  }
}
```

## 6-3. 実行！

✅

```powershell
npm test
```

`PASS` っぽいのが出たら **勝ち〜！！** 🎉🧪✨

---

## 7) VS Code で “ぽちぽち実行”できるようにする🖱️

🧩## 7-1. Vitest の VS Code 拡張を入れる🧩

拡張で **Vitest** を入れると、VS Code の **Testingビュー** からテストを実行できるよ👀✨ ([GitHub][4])



* 左のフラスコ🧪みたいなアイコン（Testing）を開く
* テストが一覧で出てきたら、▶ボタンで実行できる🎮✨

---

## 8) つまずきやすいポイント（最短で直す）

🩹💡## ❓ `vitest: command not found`→ だいたい “依存は入ったけど、パスが…” のやつ。まずこれでOK：



```powershell
npx vitest run
```

## ❓ テストが検出されない* ファイル名が `*.test.ts` になってる？👀


* `src` 配下に置けてる？📁

## ❓ 型エラーがうるさい* まずは `skipLibCheck: true` を入れて落ち着かせよう🧘‍♀️

✨（上の tsconfig には入れてあるよ）

---

## 9) ちょい大事：npm の安全チェック🔒

🍀最近も **typosquatting（紛らわしい名前）** の悪意ある npm パッケージが話題になってたから、入れる時は名前をよく見るのが大事だよ〜🕵️‍♀️💦 ([BleepingComputer][9])

最低限これだけやると安心度UP⬆️：

```powershell
npm audit
```

`npm audit` は依存関係の脆弱性レポートを出してくれるよ🔍 ([Sonatype Help][10])

---

## 10) AI拡張を“ここで”使うと超ラク🤖🎀## おすすめプロンプト例（そのまま貼ってOK）

✨* 「`npm test` が失敗。エラーログはこれ👇（貼る）。Windows + TypeScript + Vitest 4 で直して。**最小変更**でお願い。`src/core` と `src/adapters` 構成は維持してね」


* 「tsconfig の `module` と `moduleResolution` を Node 向けに安定させたい。TypeScript 5.9 のおすすめ設定にして、理由も短く教えて」 ([TypeScript][8])

---

## 章末ミニ課題🎒🧪✨

（5〜10分）1. `src/core/money.ts` を作って
   `calcTotal(price: number, quantity: number): number` を実装💰
2. `calcTotal.test.ts` を書いて

* `price=120, quantity=2 => 240`
* `price=0, quantity=10 => 0`

3. `npm test` が通ったらクリア🎉✅

---

## まとめ🎯🌈

この章でできたことはこれ👇✨



* TypeScript + Vitest の最小構成ができた🧪
* `src/core`（中心）と `src/adapters`（外側）の“置き場”ができた🏠➡️🌍
* テストが走る✅（ここ超えたら、設計の練習が一気に楽になるよ〜！）

次の章（第6章）は、この環境で **テストランナーの使い方を“まず1本通す”** をやるよ🧪🎉

[1]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
[2]: https://www.npmjs.com/package/typescript?utm_source=chatgpt.com "TypeScript"
[3]: https://vitest.dev/blog/vitest-4?utm_source=chatgpt.com "Vitest 4.0 is out!"
[4]: https://github.com/vitest-dev/vscode?utm_source=chatgpt.com "vitest-dev/vscode: VS Code extension for Vitest"
[5]: https://nodejs.org/en/download/archive/current?utm_source=chatgpt.com "Node.js® Download Archive"
[6]: https://winget.run/pkg/OpenJS/NodeJS.LTS?utm_source=chatgpt.com "Download and install Node.js LTS with winget"
[7]: https://github.com/nodejs/node/issues/61087?utm_source=chatgpt.com "winget installer for 'OpenJS.NodeJS.LTS' overwrites User ..."
[8]: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-9.html?utm_source=chatgpt.com "Documentation - TypeScript 5.9"
[9]: https://www.bleepingcomputer.com/news/security/malicious-npm-packages-fetch-infostealer-for-windows-linux-macos/?utm_source=chatgpt.com "Malicious NPM packages fetch infostealer for Windows ..."
[10]: https://help.sonatype.com/en/npm-audit.html?utm_source=chatgpt.com "npm audit"
