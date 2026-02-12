# 第42章：依存の注入（関数引数DI）📦➡️

![差し替え可能なプラグ](./picture/tdd_ts_study_042_pluggable.png)

「テストを安定させる魔法」じゃなくて、**“差し替え可能にする設計”**だよ〜🧙‍♀️💕

---

## 🎯この章のゴール

* 「時間・乱数・I/O」みたいな**不安定の元（依存）**を、テストで差し替えられるようにする🧩
* TypeScriptでいちばん軽いDI（依存性注入）＝**関数引数で注入**を身につける🙌
* テストが **安定💎・速い⚡・読みやすい📘** になるのを体感する！

---

## 1) まず“依存”って何が困るの？😵‍💫⏰

たとえば、こんなコード👇

```ts
export function isCouponValid(expireAt: Date): boolean {
  return new Date() <= expireAt
}
```

これ、ぱっと見シンプルだけど…

* テスト時に「今」を固定できない😵
* テストの実行タイミングで結果が変わる（フレーク）💥
* 将来リファクタしたときに、別の“今”参照が混ざると地獄👻

Vitestでも日付をモックする機能はあるけど、**“グローバルに時間を変える”**系は取り扱い注意（リセット忘れで事故りやすい）っていうクセがあるよ〜⚠️（例：`vi.setSystemTime` はテスト間で自動リセットされないので、戻す運用が必要） ([Vitest][1])

---

## 2) 解決：関数引数DI（いちばん軽い注入）🧸✨

ポイントはこれ👇
✅ **「今の時刻を取得する責務」を外から渡す**
✅ 本番では本物、テストでは偽物（スタブ）を渡す🎭

## いちばんミニな形：`now()` 関数を渡す☘️

```ts
export type Now = () => Date

export function isCouponValid(expireAt: Date, now: Now): boolean {
  return now() <= expireAt
}
```

* 本番：`isCouponValid(expireAt, () => new Date())`
* テスト：`isCouponValid(expireAt, () => fixedDate)`

これが **関数引数DI** だよ📦➡️
「依存（時間）」を、引数で注入してるの🫶

TypeScript的にも「関数の型」をちゃんと付けられるから安心😊 ([typescriptlang.org][2])

---

## 3) 🧪ハンズオン：クーポン期限をTDDで安定テストにする🎟️✅

## 🧪ステップA：まずテストを書く（Red）🚦

Vitestのモック関数（`vi.fn`）を使うと、偽物の `now()` が作りやすいよ✨ ([Vitest][3])

```ts
import { describe, it, expect, vi } from "vitest"
import { isCouponValid, type Now } from "../src/isCouponValid"

describe("isCouponValid", () => {
  it("期限前なら true 💕", () => {
    const expireAt = new Date("2026-02-01T00:00:00.000Z")
    const now: Now = vi.fn(() => new Date("2026-01-31T23:59:59.000Z"))

    expect(isCouponValid(expireAt, now)).toBe(true)
  })

  it("期限を過ぎたら false 💔", () => {
    const expireAt = new Date("2026-02-01T00:00:00.000Z")
    const now: Now = vi.fn(() => new Date("2026-02-01T00:00:01.000Z"))

    expect(isCouponValid(expireAt, now)).toBe(false)
  })
})
```

ここでの気持ちよさポイント😍

* 「今」が固定されるから、**何回実行しても同じ結果**✨
* 速い⚡（待ち時間ゼロ）
* テストが仕様書っぽくなる📘

---

## 🟢ステップB：最小実装（Green）🌱

```ts
export type Now = () => Date

export function isCouponValid(expireAt: Date, now: Now): boolean {
  return now().valueOf() <= expireAt.valueOf()
}
```

---

## 🧹ステップC：リファクタ（Refactor）🧼✨

でも毎回 `now` を渡すの、ちょい面倒…ってなるよね？😆
そこで「本番用デフォルト」を付けると超便利💡

```ts
export type Now = () => Date
const systemNow: Now = () => new Date()

export function isCouponValid(expireAt: Date, now: Now = systemNow): boolean {
  return now().valueOf() <= expireAt.valueOf()
}
```

* 本番：`isCouponValid(expireAt)`（自動で本物の時計⏰）
* テスト：`isCouponValid(expireAt, fakeNow)`（偽物注入🎭）

---

## 4) “依存”が増えたらどうする？🧩📦

`now` だけなら引数1個でいいけど、依存が増えると引数が渋滞しがち🚗🚗🚗

## ✅おすすめ：depsオブジェクトでまとめる🧺

```ts
export type Deps = {
  now: () => Date
  random: () => number
}

const defaultDeps: Deps = {
  now: () => new Date(),
  random: () => Math.random(),
}

export function pickDailyCoupon(deps: Deps = defaultDeps): string {
  const r = deps.random()
  return r < 0.5 ? "A" : "B"
}
```

こうすると…

* テストで差し替えがラク😍
* 「この関数は何に依存してるか」が見える化される👀✨
  （依存が見えるのはDIの大きな利点、って話も有名だよ） ([martinfowler.com][4])

---

## 5) じゃあ `vi.setSystemTime` と DI どっち？🤔⏰

Vitestには「日付をモックする」公式ガイドもあるよ（`vi.setSystemTime` や fake timers など） ([Vitest][5])

でもこの章の結論はこれ👇

* ✅ **まずDI（引数注入）を優先**：影響範囲が狭い、事故りにくい💎
* 🟡 `vi.setSystemTime` は「既存コードが Date 直叩きで、今すぐ直せない」時の救急箱🧰

  * 使ったら最後に戻す（`vi.useRealTimers()` など）を徹底しよ〜⚠️ ([Vitest][1])

---

## 🤖AIの使いどころ（この章は超うまく使える！）✨

AIには「実装そのもの」より、**差分最小でDIにする案**を出してもらうのが強いよ💪💕

## そのままコピペで使えるプロンプト例🪄

* 「この関数が `new Date()` に依存しててテストが不安定。**引数DI（now関数注入）で差分最小**にリファクタ案を出して。変更後のテスト例も」
* 「依存が増えそう。`deps` オブジェクトにまとめる案と、やりすぎない粒度の案を2つ出して」
* 「このテスト、読み物としてテスト名を改善して。Given/When/Thenで3案」

---

## ✅チェックリスト（合格ライン）💮✨

* [ ] テストが **時間に左右されず**、何回実行しても同じ結果🎯
* [ ] 本番コードで `new Date()` を直叩きしてる場所が **“境界”に寄った**（または注入された）🧭
* [ ] `vi.fn` などで **偽物依存を作れる**ようになった🎭 ([Vitest][3])
* [ ] 「本番はデフォルト、テストは差し替え」ができる💡
* [ ] 依存が増えたら `deps` で整理できそう🧺

---

## 🎁ミニ課題（10〜20分）⏳💕

「クーポンが“毎日1回だけ”引ける」関数を作ってみよ〜🎟️✨

* 依存：`now()`（日付）
* 要件：同じ日なら同じ結果、日が変わったら変わる
* テストで `now()` を固定して、日付を2パターン作る☀️🌙

---

次の第43章（スタブ）では、今日やった「偽物の渡し方」をさらに体系化して、**DB/HTTPみたいな外部も丸ごと差し替え**できるようにするよ〜🧸🔌✨

[1]: https://v3.vitest.dev/guide/mocking?utm_source=chatgpt.com "Mocking | Guide"
[2]: https://www.typescriptlang.org/docs/handbook/functions.html?utm_source=chatgpt.com "Handbook - Functions"
[3]: https://vitest.dev/guide/mocking?utm_source=chatgpt.com "Mocking | Guide"
[4]: https://martinfowler.com/articles/injection.html?utm_source=chatgpt.com "Inversion of Control Containers and the Dependency ..."
[5]: https://vitest.dev/guide/mocking/dates?utm_source=chatgpt.com "Mocking Dates"
