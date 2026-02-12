# 第12章：Watch運用（保存→即テスト）🔁

![ウォッチモード](./picture/tdd_ts_study_012_infinite_loop.png)

この章はね、**TDDが“気持ちよく回る”ようにするための準備運動**だよ〜🧘‍♀️💖
「保存した瞬間にテストが走る」だけで、集中力がぜんぜん変わるの🥺⚡️

---

## 🎯この章のゴール（できるようになること）

* **Watch（監視）モード**で、保存→即テストを回せる🔁🧪
* テストが増えても、**“今見たいテストだけ”に絞れる**👀✨
* サイクルが遅いときに、**速くする逃げ道**を持てる🏃‍♀️💨

---

## 🧠Watchってなに？（超ざっくり）

![watch_mode_treadmill](./picture/tdd_ts_study_012_watch_mode_treadmill.png)


Vitestは開発中、基本は **watchモードが標準**で、ファイルを変えると関連するテストをいい感じに再実行してくれるよ（ViteのHMRっぽい賢いやつ✨）([Vitest][1])
逆に、1回だけ実行して終わりたいときは `vitest run` を使う感じ🧪✅([Vitest][2])

---

## 🛠️まずは「迷わないコマンド」を固定しよ（おすすめ scripts）

`package.json` の scripts は、いったんこれでOK🙆‍♀️💕

```json
{
  "scripts": {
    "test": "vitest",
    "test:run": "vitest run",
    "test:ui": "vitest --ui"
  }
}
```

* `npm test` → watchで常駐（開発の相棒）🔁
* `npm run test:run` → 1回だけ（CIや確認用）✅([Vitest][2])
* `npm run test:ui` → ブラウザUIで見える化（watch前提）🖥️✨([Vitest][3])

![ui_mode_cockpit](./picture/tdd_ts_study_012_ui_mode_cockpit.png)


---

## 🧪ハンズオン：WatchでRed→Greenを回してみよ🚦💓

### ① watchを起動（つけっぱなしが基本）🔁

```bash
npm test
```

起動したら、**テスト結果が出て「待機」状態**になるはずだよ☺️
（終了したいときは `h` でヘルプ、`q` で終了が案内されることが多いよ〜）([GitHub][4])

---

### ② Red：わざと落ちるテストを書く🔴

`tests/add.test.ts` を作って👇

```ts
import { describe, it, expect } from "vitest";
import { add } from "../src/add";

describe("add", () => {
  it("1 + 2 = 3", () => {
    expect(add(1, 2)).toBe(3);
  });
});
```

保存すると… **勝手にテストが走って Red** になるはず！😆🔴
（まだ `add` が無いからね✨）

---

### ③ Green：最小の実装で通す🟢

`src/add.ts` を作って👇

```ts
export const add = (a: number, b: number) => a + b;
```

保存 → **即Green**🟢🎉
この「保存＝判定」が、TDDのテンポを作るよ🥁✨

---

### ④ もう1周：小さく仕様を足す（watchの気持ちよさを体感）🔁💖

テストに1ケース足す👇

```ts
it("0 + 0 = 0", () => {
  expect(add(0, 0)).toBe(0);
});
```

保存 → 即テスト → 即結果✅
このリズムが作れたら勝ち〜🥳💕

---

## ⚡“今見たいところだけ”に絞る（watchを速く保つコツ）

watchが遅いのって、だいたい「見なくていいテストまで走ってる」からだよ😵‍💫💦
Vitestは絞り込みがけっこう強い✨([Vitest][2])

### ✅A) ファイルを絞る（パスに文字を含めるだけ）

![filter_spotlight](./picture/tdd_ts_study_012_filter_spotlight.png)


```bash
npx vitest add
```

これで **パスに`add`を含むテストだけ**走るよ🧠✨([Vitest][2])

### ✅B) “このテスト名だけ”走らせる（正規表現OK）

![filter_sniper_scope](./picture/tdd_ts_study_012_filter_sniper_scope.png)


```bash
npx vitest -t "1 \\+ 2"
```

`-t / --testNamePattern` で、テスト名で絞れるよ🎯([Vitest][2])

### ✅C) “この行から”走らせる（ピンポイント最強）📍

```bash
npx vitest tests/add.test.ts:10
```

ファイル名＋行番号で指定できるよ（Vitest 3以降）🧷([Vitest][2])

---

## 🧰VS Codeからwatchしたい人へ（クリック運用）

「ターミナルよりクリック派🥺」なら、**Vitest公式のVS Code拡張**で
実行・デバッグ・watchができるよ🧑‍💻🧪([GitHub][5])
（次の章の Testingビューにもつながるやつ✨）

---

## 🧯watchが暴れる/重いときの即効薬

### ① 関係ないファイル変更でテストが走る…🥲

![exclude_headphones](./picture/tdd_ts_study_012_exclude_headphones.png)


「テストとして拾ってほしくない場所」があるなら、`exclude` を足すのが定番だよ🧹✨
Vitestの `exclude` は設定やCLIで指定できる🧷([Vitest][6])

（例：大きい生成物フォルダを除外したい、みたいなときに使うイメージ🧺）

---

## 🤖AIの使い方（watch運用と相性よすぎ）

![ai_copilot_whisper](./picture/tdd_ts_study_012_ai_copilot_whisper.png)


watchって「失敗ログ→次の一手」が命だから、AIをここに当てると強いよ💪🤖✨

### 🪄おすすめプロンプト（コピペOK）

* 失敗ログ貼って：

  * 「原因の候補を3つ」
  * 「一番可能性高い順に」
  * 「次にやる最小の修正を1つ」
    を出して！🧯🔍
* テストを貼って：

  * 「このテスト、仕様として読みにくい所ある？」
  * 「名前と期待値、改善案3つ」📝✨
* 実装を貼って：

  * 「Greenのまま、リファクタ候補を“最小から”3段階で」🧹🟢

---

## ✅チェックリスト（この章の合格ライン）🎓💮

* [ ] `npm test` を起動して、**止めずに開発できる**🔁
* [ ] 保存するたびに **テストが勝手に走る**🧪
* [ ] 遅くなったら **絞り込み（`add` / `-t` / `file:line`）**ができる🎯([Vitest][2])
* [ ] “失敗ログ→次の一手”をAIに投げて、**最小修正でGreenに戻せる**🤖🟢

---

次の章（第13章）では、これをさらに「ワンクリック」で回す方向に進むよ〜🧰✨
もし今の時点で「watchが遅い😭」ってなったら、どのくらい遅いか（例：3秒？10秒？）と、テスト本数だけ教えてくれたら、**“今すぐ効く”高速化メニュー**作るね🐢➡️⚡️💖

[1]: https://vitest.dev/guide/features?utm_source=chatgpt.com "Features | Guide"
[2]: https://vitest.dev/guide/cli "Command Line Interface | Guide | Vitest"
[3]: https://vitest.dev/guide/ui.html?utm_source=chatgpt.com "Vitest UI | Guide"
[4]: https://github.com/vitest-dev/vitest/discussions/7672?utm_source=chatgpt.com "Could vitest default to \"run\" instead of \"watch ..."
[5]: https://github.com/vitest-dev/vscode?utm_source=chatgpt.com "vitest-dev/vscode: VS Code extension for Vitest"
[6]: https://vitest.dev/config/exclude?utm_source=chatgpt.com "exclude | Config"
