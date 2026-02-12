# 第55章：発展：E2E/ビジュアルは少数精鋭（任意）⭐️

![視覚的カメラ](./picture/tdd_ts_study_055_visual_camera.png)

## 🎯目的

* **「E2EやVRT（ビジュアル回帰）」を“必要なぶんだけ”入れられる**ようになる😊
* 「増やしすぎて地獄😵‍💫」を避けて、**コスパ良く守る**感覚をつかむ💪✨

---

## 📚学ぶこと（この章のキモ）🧠💡

### 1) E2Eってなに？（ざっくり）

![e2e_journey](./picture/tdd_ts_study_055_e2e_journey.png)

* **ユーザーの操作を最初から最後まで通す**テスト（ログイン→購入…みたいな）🧑‍💻➡️🛒
* PlaywrightはE2E向けのテストランナーや並列実行などをまとめて持ってるよ🧪✨ ([playwright.dev][1])

### 2) ビジュアルテスト（VRT）ってなに？

![vrt_diff](./picture/tdd_ts_study_055_vrt_diff.png)

* **スクショを基準（ベースライン）にして、差分が出たら検知**するテスト📸👀
* Playwrightだと `toHaveScreenshot()` でスクショ比較ができる（初回は基準を生成、次から比較）🖼️✅ ([playwright.dev][2])

---

## 🧭「少数精鋭」にするための考え方（超大事）🚦✨

![selection_scale](./picture/tdd_ts_study_055_selection_scale.png)

E2E/VRTは強いけど…
**遅い🐢・壊れやすい💥・直すコスト高い💸**になりがち。

だからルールはこれ👇

### ✅やるのは「失敗したら致命傷」だけ

* 売上/課金/注文/予約/ログインなどの**重要導線**💰🔐
* “ここ壊れたら終わる”ってやつだけ守る🛡️

### ❌やらない（ユニット/統合で十分なもの）

* ちょこちょこ変わる見た目全部🎨（→VRT地獄になりやすい）
* 単純ロジック（→ユニットで速く守れる）⚡️

---

## 🧪手を動かす（この章のゴール：1本だけ設計して、骨組みを書く）🧱✨

### STEP 0：E2Eを“採用する基準”を書く✍️📌

以下を **READMEか docs に1ページ**でOK！

**採用する✅**

* その機能が壊れるとユーザーが帰る/損する😱
* ユニットだけじゃ守れない（画面遷移、フォーム、権限など）🧩
* 本番でやらかしやすい（過去に事故った）🔥

**採用しない❌**

* 仕様が週1で変わる・UIが揺れてる🌪️
* “とりあえず安心したい”だけ（目的が弱い）🙅‍♀️

---

### STEP 1：シナリオを1本だけ決める（Given/When/Then）📝💗

![storyboard](./picture/tdd_ts_study_055_storyboard.png)

例（注文系の最短パス）👇

* **Given**：商品一覧が見えている
* **When**：「カートに追加」を押す
* **Then**：カート件数が「1」になって、合計金額が更新される

ここでのコツ✨
✅ 画面を増やさない（まず1画面 or 2画面まで）
✅ “確認したい約束”を1〜2個に絞る（欲張らない）🍰❌

---

### STEP 2：壊れにくいセレクタ方針を決める🎯

![robust_shield](./picture/tdd_ts_study_055_robust_shield.png)

E2Eが壊れる最大原因のひとつは「要素の取り方」😵‍💫

**Playwrightは “role / text / test id” を優先して堅牢にしよう**って方針だよ✅ ([playwright.dev][3])
`data-testid` みたいな **テスト用属性**も使えるよ🧷 ([playwright.dev][4])
Cypressでも「data-*属性を使うのがベスト」ってはっきり書かれてる🧪 ([docs.cypress.io][5])

---

### STEP 3：E2Eテストの“骨組み”を書く（Playwright例）🦾

※この章は「設計」が主役だから、**動く最小の形**でOK！

```ts
// e2e/critical-path.spec.ts
import { test, expect } from '@playwright/test';

test('カートに追加すると件数と合計が更新される', async ({ page }) => {
  await page.goto('http://localhost:3000/');

  // できれば role ベースで触る（壊れにくい）
  await page.getByRole('button', { name: 'カートに追加' }).click();

  // 期待（Then）
  await expect(page.getByTestId('cart-count')).toHaveText('1');
  await expect(page.getByTestId('cart-total')).toHaveText(/¥/);
});
```

> `getByRole` など “ユーザー視点”のlocators を推すのがベストプラクティス寄りだよ✨ ([playwright.dev][3])

---

## 🖼️＋α：ビジュアル（VRT）を1枚だけ入れる（任意）⭐️

「レイアウト崩れだけは検知したい🥲」って時に使うやつ！

Playwrightは `toHaveScreenshot()` でスクショ比較できる📸
初回に基準ができて、次から差分比較になるよ🧪 ([playwright.dev][2])

```ts
import { test, expect } from '@playwright/test';

test('カート表示の見た目が崩れてない', async ({ page }) => {
  await page.goto('http://localhost:3000/cart');

  // “待っても揺れる”原因（アニメ等）を減らす設定ができる
  await expect(page).toHaveScreenshot('cart.png', {
    animations: 'disabled',
  });
});
```

* `toHaveScreenshot` は「連続して同じ見た目になるまで待ってから比較」してくれる性質があるので、VRTのフレークを減らしやすい✨ ([playwright.dev][6])

### 🧼スナップショット更新のルール（超重要）✅

![approval_stamp](./picture/tdd_ts_study_055_approval_stamp.png)

デザイン変更で差分が出たとき、**雑に更新しない**🙅‍♀️
ちゃんとレビューしてから更新する！

更新コマンドはこれ👇（Playwright公式のやつ） ([playwright.dev][2])

```bash
npx playwright test --update-snapshots
```

---

## 🧰導入コマンド（最短）⚙️✨

Playwrightは `npm init playwright@latest` で雛形や設定も作れるよ🧪 ([playwright.dev][7])

```bash
npm init playwright@latest
```

テストレポート（HTML）を見るならこれ👇 ([playwright.dev][8])

```bash
npx playwright show-report
```

---

## 🤖AIの使い方（この章の勝ちパターン）🧠💗

### 🪄プロンプト1：少数精鋭シナリオを選ぶ

*「このアプリの重要導線を3つ提案して。各導線について、E2Eで守る価値（高/中/低）と理由も書いて」*

### 🪄プロンプト2：フレーク予防

*「このE2Eがフレークになりそうな原因を列挙して。特に時間・非同期・アニメ・外部通信・セレクタの観点で」*

### 🪄プロンプト3：VRT採用判断

*「この画面はVRTに向く？向かない？理由と、もしVRTするなら“撮るべき1枚”の候補を決めて」*

---

## ✅チェック（合格ライン）🎓✨

* [ ] **E2E/VRTを入れる基準**が1ページで書けてる📄
* [ ] **E2Eシナリオが1本**、Given/When/Thenで説明できる📝
* [ ] **セレクタ方針**が決まってる（role / data-testid など）🎯 ([playwright.dev][3])
* [ ] VRTを入れたなら、**更新コマンドを乱用しないルール**がある🧼 ([playwright.dev][2])

---

## 🎁おまけ：外部サービス系VRTを使うなら（超ざっくり）🌈

* Storybook＋ChromaticでVRT運用、みたいな選択肢もあるよ（CI連携も想定されてる）📚✨ ([NRIネットコムBlog][9])
* Percy（Playwright連携）みたいな方向もある🧪📸 ([GitHub][10])

（※この章では深追いしないでOK！“知っておく”だけで強い😊）

---

次の第56章（卒業制作）で、この第55章で決めた「少数精鋭E2E」をほんとにCIに乗せて “完成まで持っていく” とめちゃ気持ちいいよ〜🎓🎉🧪✨

[1]: https://playwright.dev/docs/intro?utm_source=chatgpt.com "Installation"
[2]: https://playwright.dev/docs/test-snapshots?utm_source=chatgpt.com "Visual comparisons"
[3]: https://playwright.dev/docs/best-practices?utm_source=chatgpt.com "Best Practices"
[4]: https://playwright.dev/docs/locators?utm_source=chatgpt.com "Locators"
[5]: https://docs.cypress.io/app/core-concepts/best-practices?utm_source=chatgpt.com "Best Practices"
[6]: https://playwright.dev/docs/api/class-pageassertions?utm_source=chatgpt.com "PageAssertions"
[7]: https://playwright.dev/docs/release-notes?utm_source=chatgpt.com "Release notes"
[8]: https://playwright.dev/docs/test-reporters?utm_source=chatgpt.com "Reporters"
[9]: https://tech.nri-net.com/entry/storybook_visual_test_addon?utm_source=chatgpt.com "【Storybook】Visual Tests addonを使ってみる"
[10]: https://github.com/percy/percy-playwright?utm_source=chatgpt.com "Playwright client library for visual testing with Percy"
