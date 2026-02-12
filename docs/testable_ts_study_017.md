# 第17章：時刻（Clock）を分離する⏰🧊

![testable_ts_study_017_frozen_clock.png](./picture/testable_ts_study_017_frozen_clock.png)

## この章のゴール🎯✨* 「時間が絡む処理」を **毎回ちゃんと同じ結果でテストできる** ようにする🧪🧡


* `Date.now()` や `new Date()` をロジックから追い出して、**Clockを注入**できる形にする🚪➡️🧩
* 期限判定・日付またぎ・タイムゾーン事故の“入口”を塞ぐ🧯🌏

---

## 1) なんで「時間」はテストの天敵なの？😵‍💫🕰️

時間が絡むと、テストはこうなりがち👇



* 実行するたびに結果が変わる（いわゆる **フレーク**）😇💥
* “たまたま今”は通るけど、数分後に落ちる😱
* 23:59付近、月末、年末、DST（夏時間）などで壊れる🌙📅🔥

つまり… **時間＝外の世界（I/O）** なんだよね🚪🌍
だから第17章は「時間をI/Oとして境界に押し出す」がテーマ✨

---

## 2) 事故りやすい“時間ロジック”あるある集👃

💨よくある地雷、先に見ておこ〜〜🫣💣



### あるあるA：期限判定がズレる⏳* 「期限は今日まで」なのに、23:59で落ちたり、逆に通ったり😵

### あるあるB：「今日」判定がタイムゾーンで爆発🌏💥* 画面では今日なのに、サーバーがUTCで昨日扱い…とか😇



### あるあるC：テストで`Date.now()`を直に使ってる⌛* テストが遅いPC／CIで落ちる🥺


* 実行順で結果が変わる😵‍💫

---

## 3) 解決方針：Clockを“境界”にする✂️

🧠合言葉はこれ👇

> ロジックは **「今っていつ？」を知らない**
> 必要なら **Clockに聞く**

なので、中心（ロジック）側はこうなる✨

* `Date.now()` を直接呼ばない🙅‍♀️
* `Clock` という **最小の約束** を引数で受け取る🎁
* テストでは `FixedClock`（止まった時計）を渡す🧊⏰

---

## 4) まずは最小セットでいこう🧩

✨（Clockを作る）### 4-1) `Clock` インターフェース（最小の約束）

📜「今」を返すだけ。これで十分👍



```ts
export interface Clock {
  now(): Date;
}
```

> ここで `Date` を返すのは“最小で理解しやすい”からだよ🧸
> （※あとで強化する案も出すね✨）

### 4-2) 実運用用：`SystemClock`（本物の時計）

⌚

```ts
import type { Clock } from "./clock";

export class SystemClock implements Clock {
  now(): Date {
    return new Date();
  }
}
```

### 4-3) テスト用：`FixedClock`（時間を止める🧊）

```ts
import type { Clock } from "./clock";

export class FixedClock implements Clock {
  constructor(private readonly fixed: Date) {}

  now(): Date {
    // Dateはミュータブルなので、念のためコピーを返すのが安全🛡️
    return new Date(this.fixed.getTime());
  }
}
```

---

## 5) ハンズオン題材：クーポンの期限判定🎟️

⏰「期限より前なら使える」みたいな、ありがちなやつで練習しよ〜🧁



### 要件🍓* `expiresAt` より **前** なら有効✅


* `expiresAt` ちょうど以降は無効❌（境界が大事！）

---

## 6) 悪い例（時間がロジックに直刺し）

😇💥こういうの、つい書きがち👇



```ts
export function isCouponValid(expiresAt: Date): boolean {
  return new Date() < expiresAt; // 👈 テストが不安定になる元凶
}
```

---

## 7) 良い例：Clock注入版（中心がI/Oを知らない）

🌟

```ts
import type { Clock } from "./clock";

export function isCouponValid(clock: Clock, expiresAt: Date): boolean {
  return clock.now().getTime() < expiresAt.getTime();
}
```

ポイント💡

* ロジックは「今」を **Clockに聞くだけ**
* `getTime()`（ミリ秒）で比較すると、余計なズレが減る👍

---

## 8) テスト：時間を止めて検証する🧪🧊テストランナーは最近の流れだとVitestが超使いやすいよ〜⚡
（Vitest 4系が出てるよ、って公式でも案内されてる） ([Vitest][1])

### テスト例（境界をしっかり叩く）

🥊

```ts
import { describe, it, expect } from "vitest";
import { FixedClock } from "./fixedClock";
import { isCouponValid } from "./coupon";

describe("isCouponValid", () => {
  it("期限より前なら有効✅", () => {
    const clock = new FixedClock(new Date("2026-01-16T10:00:00.000Z"));
    const expiresAt = new Date("2026-01-16T10:00:01.000Z");

    expect(isCouponValid(clock, expiresAt)).toBe(true);
  });

  it("期限ちょうどは無効❌（境界テスト）", () => {
    const clock = new FixedClock(new Date("2026-01-16T10:00:00.000Z"));
    const expiresAt = new Date("2026-01-16T10:00:00.000Z");

    expect(isCouponValid(clock, expiresAt)).toBe(false);
  });

  it("期限を過ぎたら無効❌", () => {
    const clock = new FixedClock(new Date("2026-01-16T10:00:01.000Z"));
    const expiresAt = new Date("2026-01-16T10:00:00.000Z");

    expect(isCouponValid(clock, expiresAt)).toBe(false);
  });
});
```

✅これでテストは「いつ実行しても同じ」になるよ〜〜🎉🧡

---

## 9) さらに一段よくするコツ🛡

️✨（時間バグの入口封鎖）### 9-1) ロジックでは“表示用フォーマット”しない🙅‍♀️

🖼️`toLocaleString()` とかは **境界の外側（UI/出力）** に置くのが安全✨
ロジックは「ミリ秒」や「比較」だけに寄せると事故が減る🧯

### 9-2) `new Date("2026-01-16")`は危険寄り⚠️

環境や解釈でズレることがあるから、テストでは



* `2026-01-16T00:00:00.000Z`（Zつき）
  みたいに **明示** すると安心🧸🛡️

---

## 10) 発展：Temporalってどうなの？🧠🌈

最近の最新動向だと、JSには **Temporal** という新しい日時APIが進んでるよ✨



* 仕様は **Stage 3**（かなり固まってきてる） ([TC39][2])
* でも **ブラウザ全体での標準（Baseline）ではまだ弱め** で「限定的」扱いのところもある ([MDNウェブドキュメント][3])

なのでこの講座では、まずは「Clock分離」で勝てるようにして、
Temporalは「選べるオプション」くらいでOK👍🧁

（もしTemporalを使うなら、polyfill運用が現実的なケースもあるよ） ([GitHub][4])

---

## 11) AI拡張の使いどころ🤖🎀（丸投げ禁止ポイントも）### 使ってOK🙆‍♀️* 境界テストの洗い出し（例：期限ちょうど、直前、直後）


* テストケースの表（入力→期待）を作らせる📝
* `FixedClock` の実装の雛形を作らせる

### ここは自分が握る🔥* 「何を境界にするか」（Clockは境界にする、はあなたの判断）


* 仕様の読み取り（“期限ちょうど”を有効にするか無効にするか等）

おすすめプロンプト例🪄

* 「`isCouponValid`の境界値テストを網羅して、テスト名も提案して」
* 「Dateの比較でミスりやすい点を3つ挙げて、対策も書いて」

---

## 12) ミニ演習（やってみよ〜💪🍓）### 演習A：会員期限🎫* `isMembershipActive(clock, expiresAt)` を作る


* 境界（ちょうど）をどう扱うか仕様にしてテスト固定🧪

### 演習B：「○分以内」判定⏱️* `wasPostedWithin(clock, postedAt, minutes)`


* minutes=0、postedAt=now、1ms差などをテストで叩く🥊

### 演習C：Clockを差し替える組み立て🧱* アプリ起動時に `SystemClock` を作って中心へ渡す


* テストでは `FixedClock` を渡す
  （“組み立て場所”が自然に見えてきたら大勝利🏆✨）

---

## まとめ🎀✨* 時間はI/O！

ロジックに直で入れるとテストが壊れやすい😵‍💫


* `Clock` を境界にして注入すれば、時間を止められる🧊⏰
* 境界テスト（直前・ちょうど・直後）を固定できるのが超強い🧪💪
* Temporalは進んでるけど、まずはClock分離で“勝てる形”にしよ🌈 ([TC39][2])

次章（乱数🎲）も、やることはほぼ同じで気持ちよく進めるよ〜〜😆✨

[1]: https://vitest.dev/blog/vitest-4?utm_source=chatgpt.com "Vitest 4.0 is out!"
[2]: https://tc39.es/proposal-temporal/?utm_source=chatgpt.com "Temporal"
[3]: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Temporal?utm_source=chatgpt.com "Temporal - JavaScript - MDN Web Docs - Mozilla"
[4]: https://github.com/js-temporal/temporal-polyfill?utm_source=chatgpt.com "Polyfill for Temporal (under construction)"
