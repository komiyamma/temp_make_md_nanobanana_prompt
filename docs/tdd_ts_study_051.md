# 第51章：カバレッジの正しい距離感📈

![カバレッジの地図](./picture/tdd_ts_study_051_map_coverage.png)

## 🎯この章のゴール

* 「カバレッジ＝点数」じゃなくて、「**テストの穴を見つける地図**」として使えるようになる🗺️💕
* **どこを優先して埋めるべきか**を、落ち着いて判断できるようになる🧠✨
* Vitestでカバレッジを出して、**HTMLレポートで穴を特定→テスト追加**まで一気にできるようになる💪📈

---

## 📚まず知る：カバレッジって何を測ってるの？🤔

![metrics_gauges](./picture/tdd_ts_study_051_metrics_gauges.png)

カバレッジはだいたいこの4つが出ます👇（Vitestのしきい値設定でも、この4種が中心だよ） ([Vitest][1])

* **Lines**：行が通った？🧵
* **Statements**：文が通った？（だいたいLinesと近い）🧾
* **Functions**：関数が呼ばれた？☎️
* **Branches**：if/else や switch の分岐が両方通った？🌿🌿

ここで超大事ポイント💥
**「Linesが高い＝安心」じゃない**です😵‍💫
特に **Branches** が低いときは「条件の片側しかテストしてない」ことが多くて、バグの温床になりがち⚠️

---

## 🧪手を動かす：まずカバレッジを“出せる状態”にする🚀

### 1) カバレッジ用パッケージ（v8）を入れる📦

Vitestのカバレッジは **v8がデフォルト**で、必要なら対応パッケージを入れます✨ ([Vitest][2])

```bash
npm i -D @vitest/coverage-v8
```

（Vitest側が実行時にインストールを促してくれるケースもあるよ👍） ([Vitest][2])

---

### 2) コマンドでレポートを出す🖨️

まずはシンプルにCLIでOK！

```bash
npx vitest run --coverage
```

公式ガイドでも `vitest run --coverage` の形が紹介されています✅ ([Vitest][2])

---

### 3) HTMLレポートを開く🌈

デフォルトの出力先は `./coverage` です📁 ([Vitest][1])
なので、次を開くと視覚的にめちゃ分かりやすい😍

* `coverage/index.html`

---

## 🧪ミニ題材：分岐があるロジックで“地図の読み方”を覚える🗺️✨

### 仕様（テストで保証したい約束）📜

送料を計算するよ📦

* 合計が **5000円以上**なら送料無料🎉
* それ未満なら送料 **500円**
* ただし会員（member）なら **300円** に割引💕

---

### 実装（わざと穴が出やすい形）🧩

![logic_flow](./picture/tdd_ts_study_051_logic_flow.png)

```ts
// src/shipping/calcShippingFee.ts
export function calcShippingFee(totalYen: number, member: boolean): number {
  if (totalYen >= 5000) return 0
  if (member) return 300
  return 500
}
```

---

### テスト（最初は“穴を残す”）🕳️

```ts
// src/shipping/calcShippingFee.test.ts
import { describe, it, expect } from "vitest"
import { calcShippingFee } from "./calcShippingFee"

describe("calcShippingFee", () => {
  it("5000円以上なら送料無料", () => {
    expect(calcShippingFee(5000, false)).toBe(0)
  })

  it("5000円未満で非会員なら500円", () => {
    expect(calcShippingFee(4999, false)).toBe(500)
  })
})
```

この状態で `--coverage` すると…
たぶん **member=true の分岐が赤い**（未カバー）になります😈✨
つまり「会員割引ルートが未検証」って地図が教えてくれる！

---

### 穴を埋めるテスト追加🪄

```ts
it("5000円未満で会員なら300円", () => {
  expect(calcShippingFee(4999, true)).toBe(300)
})
```

これで Branches が上がって、安心度が一段上がるはず💗

---

## 📈カバレッジの“正しい距離感”ルール7つ🧭✨

### ルール1：カバレッジは「点数」じゃなく「発見装置」🔍

* 低い場所＝「テストがない」だけじゃなく
  **“仕様が曖昧な場所”**だったりする😳
* だから、数字に焦るより「ここ何が起きるべき？」を言語化すると強い💪

---

### ルール2：優先度は「壊れたら痛い順」💥➡️🩹

![priority_triage](./picture/tdd_ts_study_051_priority_triage.png)

おすすめ優先順位👇

1. お金・権限・状態遷移・分岐が多い（＝バグると痛い）💸🔐
2. 変換・検証・境界（外から来るデータを守る所）🧱
3. ただのgetter/setterや薄いラッパー（痛くない）🫧

---

### ルール3：「Lines高いのに不安」は“Branches”を見る🌿

![branch_trap](./picture/tdd_ts_study_051_branch_trap.png)

* if/else の片側しか通してないと、Linesはそれなりに出ちゃうことがある💦
* ルールが絡むロジックは **Branches** を意識すると一気に強くなる🔥

---

### ルール4：カバレッジの対象を“適切に絞る”🎯

![画像を挿入予定](./picture/tdd_ts_study_051_coverage_spotlight.png)

Vitestは、デフォルトだと「テスト実行中にimportされたファイル」中心でレポートに出ます。
未importのファイルも含めたいなら `coverage.include` を指定するのが定番✨ ([Vitest][2])

```ts
// vitest.config.ts
import { defineConfig } from "vitest/config"

export default defineConfig({
  test: {
    coverage: {
      include: ["src/**/*.{ts,tsx}"],
      exclude: ["**/*.d.ts"],
    },
  },
})
```

---

### ルール5：レポート形式は「HTML＋text」がおすすめ🖥️🧾

![red_lines](./picture/tdd_ts_study_051_red_lines.png)

Vitestの `coverage.reporter` は複数指定できて、デフォルトでも `text` と `html` を含みます📊 ([Vitest][1])
HTMLは“赤い行がクリックで見える”ので、初心者ほど強い味方💕

---

### ルール6：「しきい値」は“ゆるく始めて、守りを固める”🛡️

![threshold_ratchet](./picture/tdd_ts_study_051_threshold_ratchet.png)

Vitestは **しきい値（thresholds）**を設定できます。
しかも面白くて、%だけじゃなく「未カバー行数の上限（マイナス指定）」もできる！ ([Vitest][1])

```ts
// vitest.config.ts
import { defineConfig } from "vitest/config"

export default defineConfig({
  test: {
    coverage: {
      thresholds: {
        // まずは“最低限の守り”から
        branches: 60,
        functions: 70,

        // 未カバー行が増えすぎないように（例：10行まで）
        lines: -10,
      },
    },
  },
})
```

さらに、ファイルパターンごとのしきい値も設定できます✨ ([Vitest][1])

---

### ルール7：「無理な100%」は事故るので、最後の手段だけ用意🧯

どうしても通らない分岐（例：本番だけの防御コード）に対して、v8系では `c8 ignore` コメントが使われることがあります。 ([GitHub][3])

```ts
/* c8 ignore next */
if (process.env.NODE_ENV === "production") {
  // 本番だけのガード
}
```

でもね…これは強い薬💊
**「テストで保証できるなら保証する」**が基本で、ignoreは最終手段にしよ〜！🥺✨

---

## 🤖AIの使い方（この章向けテンプレ）💬✨

### 1) “穴の説明”をAIにさせる🧠

* 「このカバレッジ結果で、未検証になってる仕様の可能性を3つ挙げて」
* 「Branchesが低い原因を、ifの条件ごとに言語化して」

### 2) “追加テストの最小セット”を作らせる🧪

* 「今のテストに追加するなら、最小で何ケース？理由つきで」
* 「境界値候補だけ列挙して（実装はいらない）」

### 3) 断る訓練もする🙅‍♀️

* 「その追加テストは“実装の写し”になってない？なってたら直して」

---

## ✅チェックリスト（合格ライン）🎓💕

* [ ] HTMLカバレッジレポートを開いて、赤い行を説明できる🖥️
* [ ] **Branchesの穴**を見つけて、追加テストで埋められる🌿
* [ ] 「壊れたら痛い場所」から優先できる💥
* [ ] しきい値を“ゆるく”設定して、増悪を防げる🛡️ ([Vitest][1])
* [ ] ignoreコメントを乱用しない（使うなら理由を説明できる）🧯 ([GitHub][3])

---

## 🧪提出物（ミニ課題）📮✨

1. 自分のプロジェクトで `vitest run --coverage` を実行📈 ([Vitest][2])
2. 赤い行を **3つ**選んで、

   * 「本来保証したい仕様」
   * 「追加するテスト案（最小）」
     をメモ📝💕
3. 実際にテストを追加して、Branchesが上がったスクショ（または数値メモ）📸✨

---

次の章（第52章）は「遅い/不安定（フレーク）を潰す手順🐢💥」だよね？
第51章で“地図を読める”ようになったから、次は“ずっと回る状態に整える”って流れで最高だよ〜！🫶🧪✨

[1]: https://vitest.dev/config/coverage "coverage | Config | Vitest"
[2]: https://vitest.dev/guide/coverage.html "Coverage | Guide | Vitest"
[3]: https://github.com/bcoe/c8/blob/main/README.md?utm_source=chatgpt.com "c8/README.md at main · bcoe/c8"
