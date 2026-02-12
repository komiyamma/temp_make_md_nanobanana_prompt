# 第44章：モック/スパイ（呼ばれ方を仕様に）🎭📣

![スパイのマイク](./picture/tdd_ts_study_044_microphone.png)

## 🎯 この章のゴール

* 「副作用（通知・ログ・イベント発火など）」を **テストで保証**できるようになるよ✨
* 「返り値」じゃなくて **“呼ばれ方”**（呼ぶ/呼ばない・回数・引数）を仕様として固定できるよ🧷
* モック（vi.fn）とスパイ（vi.spyOn）の **使い分け**ができるよ🎯 ([Vitest][1])

---

## 📚 今日覚えるコト（超だいじ）🧠✨

### 1) モックとスパイ、ざっくり何が違うの？👀

* **モック（vi.fn）**：ニセの関数を自分で作る🎭
  → 依存を「差し替えて」呼ばれ方を見るのが得意✨ ([Vitest][1])
* **スパイ（vi.spyOn）**：すでにあるオブジェクトのメソッドに「盗聴器」を付ける📣

![mock_vs_spy](./picture/tdd_ts_study_044_mock_vs_spy.png)
  → 「どんなふうに呼ばれたか」を記録して、必要なら挙動も差し替えできるよ ([Vitest][1])

> どっちも「呼び出し履歴」を持つし、同じようなメソッド（mockImplementationOnceとか）を使えるよ✅ ([Vitest][1])

---

### 2) “呼ばれ方を仕様にする”ってどういう意味？🧾

例：注文確定で「通知を送る」📨

* ✅ 注文OK → 通知を **1回** 送る
* ✅ 引数は「誰に」「何を」
* ✅ 注文NG → 通知は **送らない**

この「送る/送らない・回数・引数」が、そのまま仕様になる感じだよ🫶

![behavior_spec](./picture/tdd_ts_study_044_behavior_spec.png)

---

## 🧪 手を動かす（ミニ題材）🍰

### 題材：注文が確定したら通知する📦➡️📨

「placeOrder（注文確定）」が、依存の notifier.send を呼ぶかどうかをテストするよ！

---

## 🧩 まずは “モック（vi.fn）” でいくパターン🎭

### ✅ 仕様

* 合計金額 total が 1以上なら notifier.send が 1回呼ばれる
* total が 0なら呼ばれない

---

### 1) テストを書く（Red）🔴

```ts
// src/order.ts
export type Order = { userId: string; total: number }
export type Notifier = { send: (userId: string, message: string) => void }

export function placeOrder(order: Order, deps: { notifier: Notifier }) {
  // ここはあとで実装（最初は空でOK）
}
```

```ts
// src/order.test.ts
import { describe, it, expect, vi } from 'vitest'
import { placeOrder, type Notifier } from './order'

describe('placeOrder', () => {
  it('total >= 1 のとき通知を1回送る 📩', () => {
    const send = vi.fn()
    const notifier: Notifier = { send }

    placeOrder({ userId: 'u1', total: 1200 }, { notifier })

    expect(send).toHaveBeenCalledTimes(1)

![expect_call](./picture/tdd_ts_study_044_expect_call.png)
    expect(send).toHaveBeenCalledWith('u1', '注文が確定しました')
  })

  it('total = 0 のとき通知しない 🙅‍♀️', () => {
    const send = vi.fn()
    const notifier: Notifier = { send }

    placeOrder({ userId: 'u1', total: 0 }, { notifier })

    expect(send).not.toHaveBeenCalled()
  })
})
```

※「toHaveBeenCalledTimes / toHaveBeenCalledWith」みたいな呼び方チェックができるよ✅ ([Vitest][1])

---

### 2) 最小実装（Green）🟢

```ts
// src/order.ts
export type Order = { userId: string; total: number }
export type Notifier = { send: (userId: string, message: string) => void }

export function placeOrder(order: Order, deps: { notifier: Notifier }) {
  if (order.total <= 0) return
  deps.notifier.send(order.userId, '注文が確定しました')

![conditional_gate](./picture/tdd_ts_study_044_conditional_gate.png)
}
```

---

### 3) リファクタ（Refactor）🧹✨

ここでやりがちなのが「通知文言があちこちに散る」問題😵‍💫
→ 文字列をまとめたり、条件判定を小関数にしたりしてOKだよ！

---

## 🕵️ 次は “スパイ（vi.spyOn）” のパターン📣

「依存として注入してない既存オブジェクト」を監視したいときに便利！

### 例：logger.info が呼ばれたかを確認📝

```ts
import { describe, it, expect, vi, afterEach } from 'vitest'

describe('logger の呼ばれ方を見る 📣', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('info が1回呼ばれる 🗣️', () => {
    const logger = {
      info: (msg: string) => { /* 本当はここでログ出す */ },
    }

    const spy = vi.spyOn(logger, 'info').mockImplementation(() => {})

    logger.info('hello')

    expect(spy).toHaveBeenCalledTimes(1)
    expect(spy).toHaveBeenCalledWith('hello')
  })
})
```

* vi.spyOn は「既存メソッドにスパイを貼る」感じだよ📌

![spy_logger](./picture/tdd_ts_study_044_spy_logger.png) ([Vitest][2])
* 後始末はけっこう大事！テストの外に影響を残しがちなので、まとめて元に戻すのが安心🧯 ([Vitest][2])

---

## 🧼 後片付け：clear / reset / restore の使い分け🧽✨

ここ、テストが不安定になる原因No.1になりがち！🥺

* **vi.clearAllMocks**：呼び出し履歴だけ消す（実装はそのまま）🧼 ([Vitest][2])
* **vi.resetAllMocks**：履歴も消すし、モック実装もリセット🧯 ([Vitest][2])
* **vi.restoreAllMocks**：spyOn したものを “元の実装に戻す” 🏠

![cleanup_modes](./picture/tdd_ts_study_044_cleanup_modes.png)
  ただし「履歴は消えない」などクセがあるよ🧠 ([Vitest][2])

👉 迷ったらこの運用がラク：

* vi.fn を多用 → 基本は clearAllMocks でOK
* vi.spyOn を使う → afterEach で restoreAllMocks（元に戻すのが最優先） ([Vitest][2])

---

## ⚠️ よくある落とし穴（ここハマりやすい）🕳️💥

### 1) “ログが呼ばれた” を仕様にしすぎる😇

* ログは実装都合で変わりやすいので、**大事な副作用だけ**を仕様にするのがおすすめ✨
  （例：ユーザー通知、決済、メール送信、イベント発火 など）

### 2) モジュールを mock したのに効かない？🤔

「外から呼ばれた分」は差し替わっても、**同じモジュール内で直接呼んでる関数**は差し替わらないことがあるよ⚠️

![internal_call](./picture/tdd_ts_study_044_internal_call.png) ([Vitest][3])
→ この場合は「設計として依存を外から渡す」形に寄せるとスッキリすることが多いよ🧩

### 3) クラス/コンストラクタを spyOn して変なエラー🧨

クラス系を差し替えるとき、書き方によっては「コンストラクタじゃない」系で落ちることがあるよ（矢印関数とか）💦 ([Vitest][2])
→ そういうときは docs の例みたいに function / class で差し替えるのが安全🛡️ ([Vitest][2])

---

## 🤖 AIの使いどころ（この章向け）✨

### AIに頼むと強いこと💪

* 「この処理の副作用って何？」を洗い出してもらう👀
* 「呼ばれ方として仕様にすべき観点」を列挙してもらう🗂️
* テスト名の改善案を出してもらう📝

### コピペ用プロンプト例（そのまま使ってOK）🪄

* 「この関数の副作用（呼ばれ方で仕様にすべき点）を列挙して。回数・引数・呼ぶ/呼ばないの観点で。」
* 「Vitestで vi.fn / vi.spyOn を使って “呼ばれ方” を検証するテスト案を2通り（モック/スパイ）出して。過剰に細かくしない方針で。」 ([Vitest][1])

---

## ✅ チェックリスト（できたら合格💮）

* ✅ モック（vi.fn）で「呼ぶ/呼ばない」「回数」「引数」をテストできた
* ✅ スパイ（vi.spyOn）で既存メソッドの呼ばれ方を検証できた ([Vitest][1])
* ✅ テスト後に restoreAllMocks / clearAllMocks のどちらが必要か説明できる ([Vitest][2])
* ✅ “仕様にすべき呼ばれ方” と “実装都合の呼ばれ方” を分けて考えられた🎯

---

## 🌟 ミニ課題（10〜20分）⏰💖

次のどれか1つだけやってみてね！（短くてOK✨）

1. 「ログイン成功で analytics.track を呼ぶ」📊
2. 「購入成功で mailer.send を呼ぶ」📨
3. 「失敗時は notifier.send を呼ばない」🙅‍♀️

**ポイント**：

* 大事なのは “何を返すか” じゃなくて “何を呼ぶか” 🎭📣

---

次の第45章は「ファイルI/O境界（本物/偽物の判断）📁」だから、今回の“副作用を境界で扱う感覚”がそのまま効いてくるよ〜！🧠✨

[1]: https://vitest.dev/guide/mocking/functions "Mocking Functions | Vitest"
[2]: https://vitest.dev/api/vi.html "Vi | Vitest"
[3]: https://vitest.dev/guide/mocking "Mocking | Guide | Vitest"
