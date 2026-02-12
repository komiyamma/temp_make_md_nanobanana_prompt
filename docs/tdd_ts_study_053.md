# 第53章：UIテスト戦略（やる/やらないを決める）🧭

![望遠鏡でUIを覗く](./picture/tdd_ts_study_053_telescope.png)

## 🎯この章のゴール

UIテストで迷子にならないために、**「どこまで自動テストするか」**を自分で決められるようになるよ😊✨
テストを増やしすぎず、でも怖くないラインを作るのが目的〜！🛡️💕

---

## 1) まず“テストの種類”を4つに分ける（頭の地図）🗺️

![画像を挿入予定](./picture/tdd_ts_study_053_test_pyramid.png)

UIの世界は、だいたいこの4つで考えるとスッキリするよ👇
（これは **Testing Trophy** って呼ばれる整理で、現代フロントエンド向けの考え方として有名だよ）([kentcdodds.com][1])

* 🧱 **Static（静的）**：型チェック・Lintで「やらかし」を早めに止める
* 🧪 **Unit（単体）**：小さいロジックをピンポイントでテスト
* 🧩 **Integration（結合）**：UIや複数部品が“ユーザー操作として”動くか
* 🌐 **E2E**：ブラウザで本番っぽく最重要導線だけ守る

ここで大事なのは、**全部をE2Eにしない**こと！😵‍💫💦
E2Eは強いけどコストも高いから、**「ここぞ」だけ**にするのがコツだよ🙆‍♀️✨

---

## 2) UIテストは「ユーザーが見えるものだけ」を触る🫶

UIテストで壊れやすくなる原因はだいたいコレ👇
**“実装の中身”を触りすぎる**こと😇💥

Playwrightの公式ベストプラクティスでも、
**「ユーザーに見える振る舞いをテストして、実装詳細に寄らない」**が強く推されてるよ([playwright.dev][2])

✅ UIテストで見るべきもの

* 画面に表示される文言・ボタン・入力欄
* クリック/入力した結果の表示変化
* エラーメッセージが出る/出ない
* ページ遷移・保存された/されない

🚫 なるべく触らないもの（壊れやすい😵）

* CSSクラス名
* コンポーネント内部の関数名
* stateの持ち方の細部
* “実装した順番”に依存すること

---

## 3) 「UIで何をテストするか」を決める3つの質問🪄

UIテスト対象を選ぶときは、これでOK👇💕

### Q1：それ壊れたら“致命的”？😱

* ログインできない
* 購入できない
* データ保存できない
  → こういうのは最優先🔥

### Q2：ユーザーが“よく通る道”？🚶‍♀️🚶‍♂️

* 毎日使う検索
* よく押される「追加」「保存」
  → 回数が多いほど事故が痛い💥

### Q3：そこは“壊れやすい境界”？🔌

* API通信まわり
* 入力バリデーション
* 画面遷移
  → 仕様変更や連携変更が入りやすいところ！

この3つで「YES」が多いほど、**UIテストで守る価値が高い**よ😊✅

---

## 4) どの層で守る？“おすすめ振り分け”🧠✨

迷ったらこの感覚でいくと失敗しにくいよ👇

* 🧠 **ロジックはUnit/Integrationに寄せる**（速い・安定）
* 🖥️ **UIはIntegration中心**（クリック→表示変化を守る）
* 🌐 **E2Eは最重要導線だけ**（保険の最後の砦🛡️）

「Integrationを厚めにする」方向性は、Testing Trophyでもよく語られるよ([kentcdodds.com][1])

---

## 5) “壊れにくいUIテスト”のためのルール3つ🧷✨

### ルール①：セレクタは「役割」で取る（getByRole）🎯

Playwrightは **user-facing** な取り方として `getByRole()` を推してるよ([playwright.dev][3])
（Testing Libraryでも role 系が基本の考え方として案内されてるよ🫶）([testing-library.com][4])

例（イメージ）👇

```ts
await page.getByRole('button', { name: '保存' }).click()
```

💡「roleで取れない」＝ UIのアクセシビリティが弱いサインのことも多いよ🙈

### ルール②：UIテストは“独立”させる🧼

Playwrightも「各テストを独立させよう」って明言してるよ([playwright.dev][2])
前のテストの結果に乗っかった瞬間、**たまに落ちる地獄**が始まる…😇💥

### ルール③：待ち時間（sleep）で殴らない😵‍💫

UIは非同期が多いから、**「出るまで待つ」**が基本。
Testing Libraryにも `findBy...` や `waitFor` など“待つ仕組み”が整理されてるよ([testing-library.com][5])

---

## 6) 2026の“選びやすい道具セット”🧰✨（最新事情）

### 🧪 UIコンポーネント寄り：Vitest + Browser Mode（選択肢が強い！）

Vitestには **Browser Mode** があって、**ブラウザでネイティブ実行**できるよ🖥️✨
しかも `vitest init browser` でセットアップできたり、providerに **playwright** を選べる構成になってる！([Vitest][6])

* CIで回すなら playwright / webdriverio が必要
* そして **Playwright推し（並列実行で速い）** とVitest側が書いてるよ([Vitest][6])

さらに、Browser Modeだと「本物のブラウザ上でイベント実行」寄りになるので、モック地獄を減らせる方向性も紹介されてるよ([gihyo.jp][7])

### 🌐 E2E：Playwright（重要導線の保険）🛡️

* “ユーザーが見える動き”をテストする哲学が公式で強い([playwright.dev][2])
* locatorも `getByRole()` など **壊れにくい推奨**が明確([playwright.dev][3])

---

## 🧪手を動かす：あなたのアプリで「守る導線3つ」を決めよう🎀

今日の作業はコードより **設計メモ** が主役だよ😊📝

### Step 1：重要導線を3つ書く（例）

* ✅ ログインできる
* ✅ 商品をカートに入れられる
* ✅ 購入確定できる

### Step 2：各導線を3段に振り分ける

それぞれについて👇を書くだけ！

* 🧠 Unitで守る部分（例：合計金額計算、割引計算）
* 🧩 Integrationで守る部分（例：クリック→表示変化、エラー表示）
* 🌐 E2Eで守る部分（例：ログイン→購入完了の1本だけ）

### Step 3：やらないことリストも書く（超大事！）🚫✨

* 「全画面のスナップショット」全部はやらない
* 「CSSクラス指定のセレクタ」は基本やらない
* 「細かいUIの見た目」は後の章（発展）で必要な時だけ

---

## 🤖AIの使い方（この章の鉄板プロンプト）💬✨

コピペで使えるよ〜！😍

1. **導線抽出**

```text
この機能の「ユーザーの重要導線」を最大5つ挙げて。
それぞれ、壊れた時の致命度（高/中/低）もつけて。
```

2. **テスト振り分け**

```text
この導線を Unit / Integration / E2E に振り分けたい。
「どこをどの層で守るべきか」を理由つきで提案して。
```

3. **壊れやすさ診断（セレクタ）**

```text
UIテストが壊れやすくなるポイントを列挙して。
roleベース（getByRole）に寄せる改善案も出して。
```

---

## ✅チェック（できたら合格〜！）🎉

* ✅ 重要導線が3つ言える
* ✅ 導線ごとに「Unit/Integration/E2E」の役割分担が書けた
* ✅ 「やらないこと」も決めた（←えらい！！🥹✨）
* ✅ UIテストは“ユーザーに見える動き”中心って言える([playwright.dev][2])
* ✅ セレクタは `getByRole` 優先の理由が説明できる([playwright.dev][3])

---

次の第54章では、ここで決めた方針をもとに **DOM/コンポーネントの最小テストを1本**ちゃんと書いて、「壊れにくい形」に仕上げるよ🧱🧪✨

[1]: https://kentcdodds.com/blog/static-vs-unit-vs-integration-vs-e2e-tests?utm_source=chatgpt.com "Static vs Unit vs Integration vs E2E Testing for Frontend Apps"
[2]: https://playwright.dev/docs/best-practices "Best Practices | Playwright"
[3]: https://playwright.dev/docs/locators "Locators | Playwright"
[4]: https://testing-library.com/docs/queries/byrole/?utm_source=chatgpt.com "ByRole"
[5]: https://testing-library.com/docs/queries/about/ "About Queries | Testing Library"
[6]: https://vitest.dev/guide/browser/ "Browser Mode | Guide | Vitest"
[7]: https://gihyo.jp/article/2025/06/ride-modern-frontend-09?utm_source=chatgpt.com "モダンなフロントエンドにおけるテストについて"
