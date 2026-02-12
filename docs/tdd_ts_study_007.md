# 第07章：プロジェクト作成（フォルダだけ決める）📁

![フォルダの構成](./picture/tdd_ts_study_007_folders.png)

## 🎯この章のゴール

* 迷わない“土台の形”を作る（あとで何度も助かるやつ💪）
* **src** と **tests** を分けて、頭の中もスッキリ🧠✨
* いったん“空の構成”でコミットして、安心して次へ進める✅🎉

---

## 🧭まず決めるのは「フォルダ名」だけ！

フォルダ名は悩みがちだけど、ルールを固定するとラクだよ😊💡

✅おすすめルール

* 英小文字＋ハイフン（例：`tdd-ts-practice`）
* 何の練習か分かる名前（あとで見返したとき助かる📌）

---

## 🧪手を動かす：空プロジェクトを作ってコミットする（最小手順）🪄

### 1) フォルダ作成 → VS Codeで開く🧑‍💻

```powershell
mkdir tdd-ts-practice
cd tdd-ts-practice
code .
```

---

### 2) Gitを初期化して main にする🌿

![git_init_foundation](./picture/tdd_ts_study_007_git_init_foundation.png)


```powershell
git init
git branch -M main
```

---

### 3) package.json だけ作る（まだ何も盛らない）📦

![package_json_nametag](./picture/tdd_ts_study_007_package_json_nametag.png)


ここは“名札をつけるだけ”🎀

```powershell
npm init -y
```

---

### 4) src / tests のフォルダを作る📁📁

```powershell
mkdir src
mkdir tests
```

> 💡Vitestは「ファイル名に .test. / .spec. が入ったテスト」を標準で見つけてくれるよ（あとで tests に置けばOK）🧪✨ ([vitest.dev][1])

---

### 5) 空フォルダをコミットできるように “目印ファイル” を置く📌

![gitkeep_placeholder](./picture/tdd_ts_study_007_gitkeep_placeholder.png)


Gitは空フォルダをそのままは管理できないので、よく **.gitkeep** を置くよ🧸

```powershell
ni src/.gitkeep -ItemType File
ni tests/.gitkeep -ItemType File
```

---

### 6) .gitignore を最小で入れる（今は“最低限だけ”）🙅‍♀️🗑️

```powershell
ni .gitignore -ItemType File
```

中身はこれでOK（あとで増やせばいいよ）👇

```text
node_modules/
dist/
coverage/
.env
.DS_Store
```

---

### 7) README を“見出しだけ”書く（中身は後でOK）📝✨

```powershell
ni README.md -ItemType File
```

README.md のたたき台（コピペOK）👇

```md
## tdd-ts-practice

## 目的
- TypeScriptでTDDを練習する

## コマンド（後で埋める）
- test:
- typecheck:

## メモ
- 気づいたことを書く
```

（今はこれで十分！✨）

---

### 8) ここまでをコミット🎉✅

```powershell
git add .
git commit -m "chore: init project skeleton"
```

---

## 🧠なぜ src / tests を分けるの？（超やさしく）💞

![src_vs_tests_separation](./picture/tdd_ts_study_007_src_vs_tests_separation.png)


* **src**：アプリ本体（“作るもの”）🏗️
* **tests**：仕様（“約束を確認するもの”）🧪

混ざると「今見てるのどっち！？」ってなるので、最初は分けた方が安心😊✨
※ちなみに Vitest自体は置き場所に強いこだわりがなく、見つけ方を設定でも調整できるよ🧰 ([vitest.dev][2])

---

## 🤖AIの使いどころ（この章は“整えすぎない”が正解）✨

![ai_over_engineering_warning](./picture/tdd_ts_study_007_ai_over_engineering_warning.png)


### 使ってOKなお願い例🪄

* READMEの見出し案を3つ出して
* このプロジェクト用に最小の .gitignore を提案して（理由つきで）
* フォルダ構成が初心者に優しいか、チェックして改善案ちょうだい

### ⚠️使わない方がいいお願い（今やると盛りすぎ）🙅‍♀️

* ESLint/Prettier/パスエイリアス/複雑な設定を全部入れて
  → 後の章で“意味が分かる状態”で入れたほうが強い💪✨

---

## ✅チェックリスト（合格ライン）🎓✨

![clean_workspace_goal](./picture/tdd_ts_study_007_clean_workspace_goal.png)


* **src/** と **tests/** がある📁
* ルートに **package.json / README.md / .gitignore** がある📄
* Gitに初回コミットが1つある✅
* 「設定を盛りすぎてない」←これ超重要🌱💕

---

## 🔎最新情報メモ（2026年1月時点）📌🆕

* Node.js は **v24 が Active LTS**（安定運用向き）で、2026-01-13 に **24.13.0 (LTS) のセキュリティリリース**も出てるよ🔒✨ ([nodejs.org][3])
* TypeScript は npm 上の最新が **5.9.3**（この教材も当面は“安定版”前提で進めるのが安心）🧷 ([NPM][4])
* Vitest は 4系が現行で、直近だと **4.0.17** が出てる（この先の章で入れるよ🧪） ([Yarn][5])

---

次の第8章では「Node/TSの方針（最新版より“安定”）」を、**迷子にならない決め方**でいくよ🧭✨

[1]: https://vitest.dev/guide/?utm_source=chatgpt.com "Getting Started | Guide"
[2]: https://vitest.dev/guide/migration.html?utm_source=chatgpt.com "Migration Guide"
[3]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
[4]: https://www.npmjs.com/package/typescript?utm_source=chatgpt.com "TypeScript"
[5]: https://classic.yarnpkg.com/en/package/vitest?utm_source=chatgpt.com "vitest"
