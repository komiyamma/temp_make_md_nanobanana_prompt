# 第52章：遅い/不安定（フレーク）を潰す手順🐢💥

![カタツムリからロケットへ](./picture/tdd_ts_study_052_snail_rocket.png)

テストって、**速い＆信頼できる**ほど気持ちよく回るよね🙂
この章は「テストが遅い…」「たまに落ちる…」を、**手順で確実に直せる**ようになる回だよ〜！💪💕

---

## 🎯 目的

* 「遅いテスト」「フレーク（たまに落ちるテスト）」を **見つけて→原因を絞って→直して→再発防止**できるようになる🧠✨
* 最後に **10回回して0落ち**を達成する✅🔁

---

## 📚 学ぶこと（この章の武器）🧰

**1) “遅い”の正体**

* だいたいコレ👇

  * 💤 **本物の待ち時間**（`setTimeout` / リトライ待ち / backoff）
  * 🌐 **外部依存**（HTTP / DB / ファイル / OS）
  * 🧱 **重い準備**（巨大データ生成・初期化）
  * 🧵 **並列が裏目**（ロック・競合・リソース奪い合い）

**2) “フレーク”の定番犯人**

* 🎲 乱数（`Math.random`）
* ⏰ 時刻・タイムゾーン（`Date.now()` / `new Date()`）
* 🧺 共有状態（グローバル変数・シングルトン・キャッシュ）
* 🧵 並列実行による干渉（同じポート/同じファイル名/同じDB）
* 🌐 ネットワークや実行環境の揺れ

**3) Vitestの便利オプション（この章の主役）**

* 失敗を再現しやすくする：`--sequence.shuffle` と `--sequence.seed` 🌀🌱 ([main.vitest.dev][1])
* フレーク検出に使える：`--retry`（※“直すまでの一時しのぎ”として）🔁 ([Vitest][2])
* 並列が原因か切り分け：`--no-file-parallelism`（ファイル並列を止める）🧵✂️ ([Vitest][3])
* タイマー待ちを消す：`vi.useFakeTimers()` / `vi.advanceTimersByTime()` ⏱️✨ ([Vitest][4])
* “今日”問題を消す：`vi.setSystemTime()` 📅🧊 ([Vitest][5])

---

## 🧪 手を動かす：遅い＆フレークを「わざと作って」直す🧪✨

ここから3つのミニ実験で、直し方を体に入れよ〜！💕

---

## 実験A：遅いテスト（本物の待ち時間）を即終了させる🐢➡️⚡

## ❌ 悪い例：本当に待ってる（遅い）

```ts
import { test, expect } from 'vitest'

function retry3Times(fn: () => boolean) {
  let ok = fn()
  if (ok) return true
  // ほんとは待つ系（遅くなる原因）
  // 例として 100ms * 2 回待つ想定
  // 実装はわざと雑にしてるよ
  return new Promise<boolean>((resolve) => {
    setTimeout(() => {
      ok = fn()
      if (ok) return resolve(true)
      setTimeout(() => resolve(fn()), 100)
    }, 100)
  })
}

test('retry3Times: 最後は成功する', async () => {
  let count = 0
  const result = await retry3Times(() => ++count >= 3)
  expect(result).toBe(true)
})
```

これ、テストが増えると地獄…😵‍💫（待ちが積み上がる）

## ✅ 良い例：Fake Timersで“待ち時間をスキップ”⏱️✨

```ts
import { test, expect, vi } from 'vitest'

function retry3Times(fn: () => boolean) {
  let ok = fn()
  if (ok) return Promise.resolve(true)

  return new Promise<boolean>((resolve) => {
    setTimeout(() => {
      ok = fn()
      if (ok) return resolve(true)
      setTimeout(() => resolve(fn()), 100)
    }, 100)
  })
}

test('retry3Times: 最後は成功する（Fake Timers）', async () => {
  vi.useFakeTimers() // ✅ タイマーを偽物に

  let count = 0
  const p = retry3Times(() => ++count >= 3)

  // ✅ “時間を進める”だけでOK（実時間は待たない）
  vi.advanceTimersByTime(200)

  await expect(p).resolves.toBe(true)

  vi.useRealTimers() // ✅ 後片付け
})
```

ポイント💡

* `vi.useFakeTimers()` でタイマーを偽物にして
* `vi.advanceTimersByTime(ms)` で **時間を瞬間移動**させる🌟 ([Vitest][4])

---

## 実験B：フレーク（乱数）を“注入”で固定する🎲🚫

## ❌ 悪い例：乱数に頼ってる（たまに落ちる）

```ts
import { test, expect } from 'vitest'

function pickBonus() {
  return Math.random() < 0.1 ? 'BIG' : 'SMALL'
}

test('pickBonus: BIGが出る', () => {
  expect(pickBonus()).toBe('BIG') // 😱 たまにしか出ない
})
```

## ✅ 良い例：乱数源を注入して固定🎯

```ts
import { test, expect } from 'vitest'

type Rng = () => number

function pickBonus(rng: Rng) {
  return rng() < 0.1 ? 'BIG' : 'SMALL'
}

test('pickBonus: BIGが出る（固定）', () => {
  const rng = () => 0.05 // ✅ いつでもBIG
  expect(pickBonus(rng)).toBe('BIG')
})

test('pickBonus: SMALLが出る（固定）', () => {
  const rng = () => 0.5 // ✅ いつでもSMALL
  expect(pickBonus(rng)).toBe('SMALL')
})
```

これで「たまに落ちる」が消える🎉✨
（“運ゲー”をやめて、“仕様”に戻す感じ🙂）

---

## 実験C：順序依存フレークを「シャッフル」で炙り出して直す🌀🔥

## ❌ 悪い例：共有状態が残ってる

```ts
import { test, expect } from 'vitest'

const cache: string[] = []

test('キャッシュに追加できる', () => {
  cache.push('A')
  expect(cache.length).toBe(1)
})

test('キャッシュは空である', () => {
  expect(cache.length).toBe(0) // 😱 実行順で死ぬ
})
```

## ✅ まず炙り出す：テスト順をシャッフル🌀

* `--sequence.shuffle` で順番をランダムにできるよ ([main.vitest.dev][1])
* さらに `--sequence.seed=1000` みたいに **seed固定**で再現できる🌱 ([main.vitest.dev][1])

（たとえば）

```sh
npx vitest run --sequence.shuffle --sequence.seed=1000
```

## ✅ 直し方：`beforeEach` で毎回リセット（テスト独立性）

```ts
import { test, expect, beforeEach } from 'vitest'

let cache: string[] = []

beforeEach(() => {
  cache = [] // ✅ 毎回まっさらに
})

test('キャッシュに追加できる', () => {
  cache.push('A')
  expect(cache.length).toBe(1)
})

test('キャッシュは空である', () => {
  expect(cache.length).toBe(0)
})
```

---

## 🧪 切り分けテンプレ：遅い/フレークを見つけたらこの順でOK✅

## Step 1：まず「再現」させる🔁

* **フレークっぽい**なら

  * `--sequence.shuffle --sequence.seed=...` で順序問題を炙る🌀🌱 ([main.vitest.dev][1])
  * `--retry 20` で「たまに落ちる」を表に出す（ただし直すのが本命）🔁 ([Vitest][2])

## Step 2：並列が原因か切る🧵✂️

* まずは安全に **ファイル並列を止めて**様子を見る

  * `--no-file-parallelism` ([Vitest][3])
* これで安定するなら「競合・共有リソース」が本命！

## Step 3：時間・乱数・日付を固定する⏰🎲📅

* タイマー待ち → `vi.useFakeTimers()` + `vi.advanceTimersByTime()` ⏱️ ([Vitest][4])
* “今日”依存 → `vi.setSystemTime()` 📅 ([Vitest][5])
* 乱数依存 → 乱数源を注入して固定🎯

## Step 4：外部依存を“境界で偽物化”🌐🚫

* HTTP/DB/ファイル/OS は、**境界でラップ**してユニットテストでは偽物にする（外部は統合テストに寄せる）
  （この方針が遅さ＆フレークの一番の予防になるよ🙂）

---

## 🧪 “遅いテスト”高速化の定番レシピ5️⃣🐢➡️⚡

1. **sleepを消す**（Fake Timersへ）⏱️✨ ([Vitest][4])
2. **巨大データを減らす**（必要最小のArrangeへ）🧸
3. **重い初期化を分離**（境界でラップ）🚪
4. **後片付け漏れをなくす**（リソースclose忘れは遅さ＆フレークの元）🧹
5. **並列設定を見直す**（安定優先なら並列を落とす/速度優先ならpool検討）🧵

   * `pool` は `forks/threads/...` を選べるよ（速度の代わりに相性問題もある） ([Vitest][6])

---

## 🤖 AIの使いどころ（“診断”だけAIにやらせると強い）🕵️‍♀️✨

そのままコピペで使えるプロンプト例だよ💕

**① 遅い原因の推理**

* 「このテストが遅いです。原因候補を *外部依存/待ち時間/重い準備/並列競合* に分類して、最小修正→中修正→大修正の順に3案ください」

**② フレーク原因チェック**

* 「この“たまに落ちる”テストの原因候補を *時間/乱数/共有状態/順序/並列/外部* の観点で列挙して、再現手順（seed固定など）も提案して」

**③ 直した後の再発防止**

* 「この修正で再発しそうなポイントを指摘して、予防ルールを5つにまとめて」

※注意💡：AIの提案は“答え”じゃなくて“仮説”！最後はテストで確定ね🙂🤝

---

## ✅ チェック（合格ライン）🎉

* [ ] `--sequence.shuffle --sequence.seed=1000` で回しても落ちない🌀🌱 ([main.vitest.dev][1])
* [ ] `--retry 20` をかけても落ちない（= フレークっぽさが消えた）🔁 ([Vitest][2])
* [ ] 10回連続でグリーン✅🔁
* [ ] “待ち時間テスト”が Fake Timers に置き換わってる⏱️✨ ([Vitest][4])
* [ ] “今日/乱数/共有状態”が固定 or 注入で制御できてる📅🎲🧼 ([Vitest][5])

---

## 🧾 この章の提出物（作ると強い！）📌

* **「遅い/フレーク診断メモ」**（テンプレ）

  * 症状：遅い or たまに落ちる
  * 再現コマンド：shuffle/seed/retry/並列OFF
  * 原因：時間/乱数/共有/外部/並列 のどれ？
  * 対策：最小→中→大（3段）
  * 再発防止：ルール3つ

---

次の章に進む前に、もし「最近あなたのプロジェクトで遅い/落ちるテスト」が1本でもあれば、そのテストコード（1ファイルでOK）貼ってくれたら、この手順で一緒に“最短ルートで安定化”まで持っていけるよ🧪💞

[1]: https://main.vitest.dev/config/sequence?utm_source=chatgpt.com "sequence | Config"
[2]: https://vitest.dev/guide/cli?utm_source=chatgpt.com "Command Line Interface | Guide"
[3]: https://vitest.dev/guide/improving-performance?utm_source=chatgpt.com "Improving Performance"
[4]: https://vitest.dev/api/vi.html?utm_source=chatgpt.com "Vitest"
[5]: https://vitest.dev/guide/mocking?utm_source=chatgpt.com "Mocking | Guide"
[6]: https://vitest.dev/config/pool?utm_source=chatgpt.com "pool | Config"
