# 第11章：Windows＋VS Code準備②：VS Codeの必須設定 🧰✨

![hex_ts_study_011[(./picture/hex_ts_study_011_testing_in_isolation.png)

この章は「**VS Codeの設定を“最低限だけ”整えて、開発がスムーズに進む状態にする**」のが目的だよ〜😊💖
ここが整うと、あとで作る Ports & Adapters のコードも **読みやすい・直しやすい・壊れにくい** に育つ🌱✨

---

![hex_ts_study_011_user_vs_workspace.png](./picture/hex_ts_study_011_user_vs_workspace.png)

### 11-1. 設定はどこに入れる？（User / Workspace の使い分け）🗂️✨

VS Codeの設定には大きく2種類あるよ👇

* **User Settings**：あなたのPC全体に効く（どのプロジェクトでも共通）
* **Workspace Settings**：そのプロジェクトだけに効く（`.vscode/settings.json` に入る）

プロジェクトに配りたい（共有したい）設定は Workspace に置くのが便利だよ〜📦✨
この区別や開き方は公式ドキュメントでも説明されてるよ。([Visual Studio Code][1])

開き方はこのへんを覚えるだけでOK✅

* 設定画面：`Ctrl + ,`（ユーザー設定を開ける）([Visual Studio Code][1])
* コマンドパレット：`Ctrl + Shift + P`（なんでも呼び出せる魔法の窓）([Visual Studio Code][1])
* JSONで直接いじる：`Preferences: Open User Settings (JSON)` / `Preferences: Open Workspace Settings (JSON)`([Visual Studio Code][1])

あと便利なのがこれ👇

* **Default Settings（既定値）を丸ごと読む**：`Preferences: Open Default Settings (JSON)`
  → `defaultSettings.json` が開くよ（読み取り専用）([Visual Studio Code][2])

> 「この設定って何が入ってるの？」って迷ったら、まず Default Settings を見に行けばだいたい解決するよ😊🔍✨ ([Visual Studio Code][2])

---

![hex_ts_study_011_format_on_save.png](./picture/hex_ts_study_011_format_on_save.png)

### 11-2. 保存時整形（Format on Save）をONにする ✨🧼

整形は“人の手”じゃなくて“機械”に任せるのがいちばんラク！🤖💖
VS Codeは **保存時に自動整形**できるよ。

* `editor.formatOnSave`：保存したときにファイルを整形する ([Visual Studio Code][3])

設定はこんな感じ👇（Workspace に入れるのがおすすめ）

```json
{
  "editor.formatOnSave": true
}
```

VS Codeは JavaScript / TypeScript などに **標準フォーマッター**も持ってるから、まずはこれだけでも体感できるよ✨ ([Visual Studio Code][3])

#### 💡「保存したのに整形されない！」ときのあるある

* フォーマッターが複数あると、どれ使うか迷って止まることがある
  → `editor.defaultFormatter` を決めると安定しやすい（あとでPrettierを入れるならなおさら）😊✨

---

### 11-3. 自動import＆import整理（コードの見た目が一気に綺麗）🧹🔁

![hex_ts_study_011_organize_imports.png](./picture/hex_ts_study_011_organize_imports.png)

#### ① 保存時に import を整理する（Organize Imports）📦✨

VS Codeは「保存した瞬間に import を整える」もできるよ！

`editor.codeActionsOnSave` で、保存時に実行するアクションを指定できる😊
しかも最近のVS Codeは **true/false じゃなくて**、`explicit / always / never` みたいな指定もできるよ（けっこう大事）([Visual Studio Code][4])

* `explicit`：自分で保存したときだけ（デフォルト）([Visual Studio Code][4])
* `always`：自動保存でも走る([Visual Studio Code][4])
* `never`：走らない([Visual Studio Code][4])

まずは安全に **explicit** が超おすすめ🙆‍♀️✨（勝手に暴れにくい）

```json
{
  "editor.codeActionsOnSave": {
    "source.organizeImports": "explicit"
  }
}
```

> これで、使ってないimport消えたり、順番整ったりして気持ちいい〜〜🥰🧹✨

![hex_ts_study_011_import_update.png](./picture/hex_ts_study_011_import_update.png)

#### ② ファイル移動・リネームで import パスも追従させる 🧳➡️

地味に神なのがこれ！！
ファイル名変えたとき、importが壊れる事故を減らせる😊

* `typescript.updateImportsOnFileMove.enabled`：`prompt / always / never` ([Visual Studio Code][4])

おすすめは **prompt** か **always**（迷ったら prompt）✨

```json
{
  "typescript.updateImportsOnFileMove.enabled": "prompt"
}
```

---

![hex_ts_study_011_search_exclude.png](./picture/hex_ts_study_011_search_exclude.png)

### 11-4. 検索を“強くする”設定（大規模でも迷子にならない）🔎🧭✨

VS Codeの検索は超強いんだけど、`node_modules` とか `dist` とかが混ざると
**検索が重い＆ノイズだらけ**になりがち😵‍💫

公式も「重いなら除外しよ〜」って言ってるよ📌
`files.exclude` / `search.exclude` でフォルダ除外できる([Visual Studio Code][3])

#### ① まず除外の基本（超定番）📁🚫

```json
{
  "files.exclude": {
    "**/node_modules": true,
    "**/dist": true
  },
  "search.exclude": {
    "**/node_modules": true,
    "**/dist": true
  }
}
```

#### ② 検索UIの小ワザ（覚えると速い）⚡

* 全文検索：`Ctrl + Shift + F`
* 詳細検索（include / exclude欄を出す）：検索欄の「…」か `Ctrl + Shift + J`([Visual Studio Code][3])
* パターンは **スラッシュは forward slash（`/`）** で書くのが基本（Windowsでも）([Visual Studio Code][3])
* globパターンの考え方はこれ（公式）([Visual Studio Code][5])

---

![hex_ts_study_011_line_endings.png](./picture/hex_ts_study_011_line_endings.png)

### 11-5. よくある詰まり①：改行コード（CRLF/LF）🧷💥

Windowsだと、ファイルによって `CRLF` と `LF` が混ざって
「なんか差分だらけ😱」ってなりがち。

VS Codeには `files.eol` って設定があって、**新規ファイルの改行**を決められるよ。
ただし注意⚠️：

* `files.eol` は **新規ファイル向け**
* 既存ファイルは **今の改行が保持される**
* 既存ファイルを変えたいときは **Change End Of Line Sequence** コマンドを使う ([Visual Studio Code][6])

たとえば TypeScript 系は LF にしたいなら👇

```json
{
  "[typescript]": { "files.eol": "\n" },
  "[typescriptreact]": { "files.eol": "\n" }
}
```

> 「え、LFにしただけでGitの差分がいっぱい…」ってなるのは普通だよ🥹
> 改行コードもファイル内容の一部だから、変えたら差分になるのは自然な動き！

---

### 11-6. よくある詰まり②：設定が増えすぎて迷子😵‍💫🌀

そんなときは “設定の辞書” を使えばOK✨

* `Preferences: Open Default Settings (JSON)` で既定値を読む
  → `defaultSettings.json` が開くよ([Visual Studio Code][2])

「この設定って何のため？」ってなったら、まずここを見ると安心😊📖✨

---

## 11-7. ミニ演習（5分で“効いてる感”を体験）⏱️🎀

### 演習A：保存時整形が効くか確認🧼✨

1. 適当な `.ts` を開く
2. わざとインデントを崩す（スペースぐちゃぐちゃにする）😈
3. 保存（`Ctrl + S`）
4. 整形されたら成功🎉（Format on Save ばんざい🙌）

※手動整形は `Shift + Alt + F`（公式の操作説明にもあるよ）([Visual Studio Code][3])

### 演習B：import整理が効くか確認📦✨

1. 使ってない import を1個作る
2. 保存
3. 消えたり並び替えされたら成功🎉（Organize Imports〜！）

### 演習C：検索除外が効くか確認🔎🚫

1. `Ctrl + Shift + F` で検索
2. `node_modules` が検索に出てこない（or かなり減る）ならOK😊✨

---

## この章のまとめ 🎁💖

* 設定は **User / Workspace** がある（プロジェクト共有はWorkspaceが便利）([Visual Studio Code][1])
* **保存時整形**は `editor.formatOnSave` が基本([Visual Studio Code][3])
* **保存時アクション**は `editor.codeActionsOnSave`（`explicit/always/never` が使える）([Visual Studio Code][4])
* **ファイル移動でimport追従**は `typescript.updateImportsOnFileMove.enabled`([Visual Studio Code][4])
* **除外設定**で検索と補完が軽くなる（公式も推奨）([Visual Studio Code][7])
* 改行コードは `files.eol`（新規向け）＋既存はコマンドで変更([Visual Studio Code][6])

---

次の章（第12章）では、ここで整えたVS Codeを“AI込み”でさらに使いやすくしていくよ〜🤖💖
（雛形作りや命名相談のコツとか、やりすぎ注意ポイントも🫶✨）

[1]: https://code.visualstudio.com/docs/configure/settings "User and workspace settings"
[2]: https://code.visualstudio.com/docs/reference/default-settings "Default settings reference"
[3]: https://code.visualstudio.com/docs/editing/codebasics "Basic editing"
[4]: https://code.visualstudio.com/docs/typescript/typescript-refactoring "Refactoring TypeScript"
[5]: https://code.visualstudio.com/docs/editor/glob-patterns "Glob Patterns Reference"
[6]: https://code.visualstudio.com/updates/v1_40 "October 2019 (version 1.40)"
[7]: https://code.visualstudio.com/docs/editing/intellisense "IntelliSense"
