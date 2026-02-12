# 第13章：VS Code Testingビュー（ワンクリック化）🧰

![テスティングパネルのUI](./picture/tdd_ts_study_013_testing_ui.png)

## 🎯 目的

テスト実行の「めんどくさい」を消して、**1クリック（or 1ショートカット）で**

* ①全部実行
* ②1本だけ実行
* ③失敗だけ見直し
* ④デバッグ実行
  ができる状態にするよ〜😆💕

## 📚 学ぶこと

* VS Codeの**Testingビュー（ビーカー🧪）**の基本（テスト一覧・結果・フィルタ） ([Visual Studio Code][1])
* **Vitest公式のVS Code拡張**で、Testingビュー＆エディタ内（行番号の左）から実行する方法 ([Visual Studio Marketplace][2])
* テストが増えても迷子にならない「絞り込み」「再読み込み」「ログの見方」 ([Visual Studio Code][1])

---

## 🧪 手を動かす（今日ここで “ワンクリック化” する）🪄

### 1) Testingビューを開く（ビーカー🧪）

左のサイドバーにある🧪（Testing）を押すと **Test Explorer** が出るよ！
VS Codeはテスト機能をここに集約してくれるのが強み✨ ([Visual Studio Code][1])

もしビーカーが見つからなかったら、コマンドパレットで
`Testing: Focus on Test Explorer View` を実行してOK👍 ([Visual Studio Code][1])

---

### 2) VitestをTestingビューに“接続”する（公式拡張）🔌🧪

Vitestは **公式のVS Code拡張**が用意されてて、Testingビューで **Run / Debug / Watch / Coverage** までできるよ！ ([Vitest][3])

この拡張、Testingビュー上部のツールバーにこんなボタンを出してくれる👇 ([Visual Studio Marketplace][2])

* **Refresh Tests**（テスト再検出）
* **Run All Tests**（表示されてる範囲を全部実行）
* **Debug Tests**（デバッグ実行）
* **Run Tests with Coverage**（カバレッジ付き）
* **Continuous Run**（ウォッチで自動実行）
* **Show Output**（ログ表示）

さらに、**console.log がエディタ内にインライン表示**されたりもするのが便利〜😍 ([Visual Studio Marketplace][2])

> うまく動かない時は、拡張の要件（VS Code / Vitest / Node）もサクッと確認してね🧠
> VS Code >= 1.77 / Vitest >= 1.4 / Node >= 18 など ([Visual Studio Marketplace][2])

---

### 3) 「1本だけ実行」を“行番号の左”からやる（最強）👆✨

テストファイルを開くと、左側のガター（行番号の左）に**テスト用アイコン**が出るよ！
そこをクリックするだけで👇ができる😆 ([Visual Studio Marketplace][2])

* **Run a Single Test**（その1本だけ実行）
* 右クリックで **Debug Test / Run with coverage / Reveal in Test Explorer** など

> コツ：まずは **失敗したテストだけ**を、ガターから1本ずつ直すのが超気持ちいい💖

---

### 4) テストが増えたら「絞り込み」が命🔎🧪

Testingビューはフィルタが強いよ〜！ ([Visual Studio Code][1])

* ステータスで絞る（成功/失敗/未実行 など）
* **現在のファイルだけ表示**にする
* 検索ボックスで名前検索
* `@` を使って **ステータスで検索**もできる ([Visual Studio Code][1])
* Vitest拡張なら `@open` タグで「開いてるテストだけ」も絞れるよ ([Visual Studio Marketplace][2])

---

### 5) 「テストが増えたのに出てこない！」時の即効薬💊

新しいテストを足したのに一覧に出ない時は、まずこれ👇 ([Visual Studio Code][1])

* Testingビューの **Refresh Tests**
* またはコマンドパレットで **`Test Explorer: Reload tests`** ([Visual Studio Code][1])

それでもダメなら、Vitest拡張の設定で「どの設定ファイルを見るか」を指定できるよ👇 ([Visual Studio Marketplace][2])

* `vitest.rootConfig`
* `vitest.workspaceConfig`
* `vitest.ignoreWorkspace`
* `vitest.configSearchPatternInclude / Exclude`

---

### 6) 失敗時に“バーン💥”と出る画面がうるさい時（落ち着こ？😇）

テスト失敗すると、エディタ上に **Peek View（エラーの小窓）** が自動で出ることがあるのね。
これ、設定で **出ないように**できるよ〜！ ([Visual Studio Code][4])

* 設定検索で **「Testing: Automatically Open Peek View」**
* 値を `never` にすると静かになる🫶 ([Visual Studio Code][4])

（settings.json派なら例👇）

```json
{
  "testing.automaticallyOpenPeekView": "never"
}
```

---

## 🧪 ミニ演習（“3回”やって指に覚えさせる）💪🧠✨

今日のゴールはこれだよ👇（ほんとに3周してね😂💕）

1. **Testingビューで Run All Tests** → 結果を見る 👀 ([Visual Studio Marketplace][2])
2. わざと1本失敗させて（expect変えるとか）

   * ガターのアイコンから **その1本だけ Run** → 直す → もう1回Run ([Visual Studio Marketplace][2])
3. Testingビューで **フィルタ**を使って「失敗だけ」「このファイルだけ」に絞る 🔎 ([Visual Studio Code][1])

---

## 🤖 AIの使い方（この章での“勝ちパターン”）🤖🎀

AIには「設定を盛る」じゃなくて、**“自分の操作を短縮する”**方向で使うのが最高👍✨

おすすめプロンプト例（そのまま貼ってOK）👇

* 「VS CodeのTestingビューで、私が毎日やる操作トップ5をショートカット化したい。候補キー案も出して」 ([Visual Studio Code][1])
* 「VitestのVS Code拡張でテストが出てこない。`vitest.config` とディレクトリ構成を前提に、原因チェックリストを作って」 ([Visual Studio Marketplace][2])
* 「失敗したテストのログを貼るので、原因→最小修正案→追加すべきテスト観点を順に出して」🧪✨

---

## ✅ チェック（できたら合格💮）

* 🧪 Testingビューを開いて、テスト一覧が見える ([Visual Studio Code][1])
* ▶️ **Run All** と、ガターから **1本Run** ができる ([Visual Studio Marketplace][2])
* 🔎 フィルタで「欲しいテスト」へ一瞬で辿り着ける ([Visual Studio Code][1])
* 🔄 テストが増えたら **Reload tests** できる ([Visual Studio Code][1])
* 😇 Peek Viewが邪魔なら止められる ([Visual Studio Code][4])

---

次の章（第14章）は、この快適環境を崩さないために「1章＝1ゴール＝1〜3コミット」みたいな運用ルールを作って、学習も開発も“続く形”にしていくよ〜📏💖

[1]: https://code.visualstudio.com/docs/debugtest/testing "Testing"
[2]: https://marketplace.visualstudio.com/items?itemName=vitest.explorer "
        Vitest - Visual Studio Marketplace
    "
[3]: https://vitest.dev/guide/ "Getting Started | Guide | Vitest"
[4]: https://code.visualstudio.com/docs/python/testing?utm_source=chatgpt.com "Python testing in Visual Studio Code"
