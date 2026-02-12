# 第08章：Node/TSの方針（最新版より“安定”）🧩

![安定した柱](./picture/tdd_ts_study_008_stable_pillar.png)

TDDって「サクサク回せる環境」が命だよね🧪💨 なのでこの章は、**“新しさ”より“安定”を優先して、バージョン違いの沼を回避する**のがゴールだよ〜😊💖

---

## 🎯 この章のゴール

* Node.js と TypeScript の**採用方針**を決められる✅
* **チーム/自分のPC差でテストが落ちる事故**を減らせる✅
* 「なんか動かない…」の原因が **“バージョンかも？”**ってすぐ気づける✅

---

## 1) まず結論：2026/01/19 時点のおすすめ 🌟

![lts_vs_current](./picture/tdd_ts_study_008_lts_vs_current.png)


## ✅ Node.js：**LTS（安定版）を使う**

* Node は **Current（最新）** と **LTS（安定）** があるよ
* **TDD教材では LTS を推奨**（突然の破壊的変更に巻き込まれにくい）
* 2026/01 時点：**v24 が Active LTS**、v25 は Current（最新系）だよ📌 ([nodejs.org][1])

## ✅ TypeScript：**安定版をプロジェクトに固定**

* 2026/01 時点、npm の `typescript` 最新は **5.9.3**（安定）📌 ([NPM][2])
* TypeScript 6.0/7.0 の大きい動きも出てきてるので、教材ではまず **5.9.x を固定して堅くいく**のが安心だよ😊 ([Microsoft for Developers][3])

---

## 2) “安定”って具体的に何するの？🧠💡

![global_vs_local](./picture/tdd_ts_study_008_global_vs_local.png)


ここが超たいじ！👇

## ✅ やることは3つだけ

1. **Node は LTS を使う**（今なら v24）
2. **TypeScript は devDependency に入れて固定**（例：5.9.3）
3. **プロジェクトに「このバージョン使ってね」情報を残す**（ピン留め）

---

## 3) 🧪 手を動かす：バージョンを固定して「環境差ゼロ」を作る

![pinning_versions](./picture/tdd_ts_study_008_pinning_versions.png)


この教材では、Windows でラクに固定できる **Volta** を推すよ〜🤖✨
（公式も Windows は winget をおすすめしてるよ📌） ([Volta][4])

## 3-1) Volta を入れる（バージョン管理の土台）🧰

![volta_tool](./picture/tdd_ts_study_008_volta_tool.png)


PowerShell（またはターミナル）で：

```bash
winget install Volta.Volta
```

入ったか確認：

```bash
volta --version
```

> もし `volta` が見つからなかったら、**VS Code / ターミナルを再起動**してね🔄（PATHが反映されてないだけが多いよ〜）

---

## 3-2) Node を LTS にする（今なら v24）🟩

まずは LTS を入れる：

```bash
volta install node@lts
```

確認：

```bash
node -v
npm -v
```

2026/01 時点だと、LTS の最新版は **v24 系**になってるはずだよ（Node の LTS は v24 が “Latest LTS” 表示）📌 ([nodejs.org][5])

---

## 3-3) プロジェクトを作って “ピン留め” する📌✨

フォルダ作って移動：

```bash
mkdir tdd-ts-2026
cd tdd-ts-2026
npm init -y
```

このプロジェクトで使う Node を固定（おすすめ：LTSのメジャー固定）：

```bash
volta pin node@24
```

✅ `package.json` に `"volta": { ... }` が増えてたら成功だよ🎉
（これで「別PCでもこのNodeが使われる」状態に近づく！）

---

## 3-4) TypeScript を “プロジェクトに固定” する🧷

TypeScript を devDependency に入れる（2026/01 時点の安定最新版は 5.9.3）📌 ([NPM][2])

```bash
npm i -D typescript@5.9.3
```

確認：

```bash
npx tsc -v
```

---

## 3-5) “型チェック用コマンド”を用意しておく（TDDの回転が良くなる）🌀

`package.json` の scripts にこれ追加（手で編集してOK）👇

```json
{
  "scripts": {
    "typecheck": "tsc --noEmit"
  }
}
```

実行してみよう：

```bash
npm run typecheck
```

> まだ `tsconfig.json` は次章で作るから、ここは「コマンド入口を作れたらOK」って感じで😊

---

## 4) ✅ チェック（この章の合格ライン）🎓💖

* `node -v` が **v24 系**になってる（LTS）🟩 ([nodejs.org][1])
* `npx tsc -v` が **5.9.3** になってる🧷 ([NPM][2])
* `package.json` に **volta の pin 情報**が入ってる📌
* `npm run typecheck` という入口ができた✅

---

## 5) つまずきポイント集（ここで詰まりがち🥺）🧯

![environment_consistency](./picture/tdd_ts_study_008_environment_consistency.png)


## 🧨 (A) `volta` が認識されない

* **VS Code を再起動**（ターミナルだけじゃダメな時ある）🔁
* それでもなら `where volta` で場所を確認👀

## 🧨 (B) Node のバージョンが変わらない

* `where node` で **どの node が呼ばれてるか**確認しよ！
* Volta の node が優先されてない時は PATH 順序の問題が多いよ💦

## 🧨 (C) `EBADENGINE` が出た（npm install で怒られる）

* だいたい「Node が古いよ！」って意味
* 例えば Vitest 系ツールは Node 18+ が最低ラインのことがあるよ📌 ([GitHub][6])
  → 今回は v24 LTS だから基本は安全圏🏖️

---

## 6) 🤖 AI の使い方（この章の“勝ちパターン”）

![ai_troubleshooting](./picture/tdd_ts_study_008_ai_troubleshooting.png)


AI は「原因切り分け係」にすると強いよ💪✨
（丸コピ実装係にすると、逆に沼りやすい🥺）

## 🧠 そのまま貼って使えるプロンプト例

* エラー文を貼って👇みたいに聞くのがおすすめ！

```text
以下のエラーを「原因カテゴリ」で分類して、最短の解決手順を3つ提案して。
カテゴリ例：PATH / Nodeのバージョン違い / npmキャッシュ / ESM-CJS / TypeScriptのバージョン違い

--- エラー ---
（ここにコピペ）

--- いまの状況 ---
node -v: （ここ）
npm -v: （ここ）
npx tsc -v: （ここ）
where node: （ここ）
```

---

## 7) まとめ（この章で得た“強さ”）💎

* **LTS を選ぶ**だけで、TDDの失速がかなり減る🧪💨
* **TypeScript はプロジェクトに固定**が正義（グローバルは事故りやすい）🧷
* Volta で **“このプロジェクトはこのNodeね”** ができると、未来の自分が助かる🥹💖

---

次の第9章では、いよいよ **tsconfig を最小＆強め（strict）で組む**よ〜🧷✨
その前に、もし今の `package.json` 見せてくれたら「ここ、より事故りにくくできるよ！」って軽く整えて返せるよ😊🎀

[1]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
[2]: https://www.npmjs.com/package/typescript?utm_source=chatgpt.com "TypeScript"
[3]: https://devblogs.microsoft.com/typescript/progress-on-typescript-7-december-2025/?utm_source=chatgpt.com "Progress on TypeScript 7 - December 2025"
[4]: https://docs.volta.sh/guide/getting-started?utm_source=chatgpt.com "Getting Started | Volta"
[5]: https://nodejs.org/en/about/eol?utm_source=chatgpt.com "End-of-Life (EOL)"
[6]: https://github.com/vitest-dev/vscode/discussions/482?utm_source=chatgpt.com "Vitest not accessing the correct version of node; startup fails"
