# 第13章：依存を外から渡す（引数注入）🎁➡️

![testable_ts_study_013_dependency_injection.png](./picture/testable_ts_study_013_dependency_injection.png)

この章はひとことで言うと、**「テストしにくい原因（外の世界＝I/O）を、関数の外へ追い出す最短ルート」**です✨
その方法が **引数注入**（＝依存を引数で受け取る）だよ〜！🧸🧪

---

## 1) この章でできるようになること🎯✨* 「依存（＝外の世界）

」がどこに混ざってるか見つけられる👀


* `Date` / `console` みたいな **直書き依存**を **引数にして差し替え可能**にできる🔁
* テストで **時間を止める**・**ログを記録する**ができるようになる⏰📝
* 次章の「組み立て場所（Composition Root）」に自然につながる🏗️

---

## 2) まず結論💡：「中心は依存を作らない」🙅‍♀️

中心（ロジック側）の関数はこうするのがコツ👇



* ✅ **必要な依存は “引数で受け取る”**
* ❌ 関数の中で `new Date()` / `console.log()` / `Math.random()` を直接呼ばない

最新のTypeScriptは **5.9 系が “latest”** になっていて（npmの「最新版」として案内されてるよ）、「Node向けの設定（node20）」みたいな“現実に合わせたモード”も整ってきてます。([TypeScript][1])
Node.jsは **v24 が Active LTS**（安定運用向き）なので、教材の前提としても安心枠だね🧡([Node.js][2])

---

## 3) 「依存」ってなに？（I/O寄りのやつ）

🌀🚪たとえば👇は全部「外の世界」に触れてる（＝テストで面倒になりやすい）やつ！



* ⏰ 時刻：`new Date()`
* 📝 ログ：`console.log()`
* 🎲 乱数：`Math.random()`
* 🌐 HTTP：`fetch()`
* 📁 ファイル：`fs`
* ⚙️ 環境変数：`process.env`

この章はまず **Clock（時刻）** と **Logger（ログ）** を引数で受け取れるようにして、テストをラクにするよ〜！🧪✨

---

## 4) つらい例：直 `Date` と直 `console` 😵‍💫「トライアル開始」みたいな処理を想像してね🛒🍰



```ts
// trial.ts（つらい版）
export function startTrial(userId: string) {
  const now = new Date(); // ← 直Date（依存が中にある）
  console.log(`[trial] start user=${userId} at=${now.toISOString()}`); // ← 直console

  const endsAt = new Date(now);
  endsAt.setDate(now.getDate() + 14);

  return { userId, startedAt: now, endsAt };
}
```

これ、テストで困るポイント👇

* ⏰ **今の時刻が毎回違う** → 期待値が揺れる
* 📝 **ログがコンソールに出るだけ** → 「出たかどうか」を検証しづらい

---

## 5) 解決：引数注入（Dependency Injection by Parameters）

🎁➡️### パターンA：依存を「関数」として渡す（最小で好き）

🧼✨* `now(): Date` だけ渡す


* `log(msg)` だけ渡す
  → **依存の契約が最小**で、シンプル！

### パターンB：依存を「オブジェクト」にまとめて渡す（増えたとき強い）

🎒✨* `{ clock, logger }` みたいに束ねる
  → 引数が増えても読みやすい！

この章では「増えても破綻しにくい」ので **B** をメインでいくね🧸🎀

---

## 6) ハンズオン：Clock/Loggerを引数で受け取る版に変える⏰📝

🧪### Step 1：依存の型（最小の約束）

を作る📜✨

```ts
// deps.ts
export type Clock = {
  now: () => Date;
};

export type Logger = {
  info: (message: string) => void;
};

export type TrialDeps = {
  clock: Clock;
  logger: Logger;
};
```

> ポイント💡
>
> * Clockは「今を返せる」だけ
> * Loggerは「infoを書ける」だけ
>   これ以上いらないなら増やさない✂️✨

---

### Step 2：関数の引数に deps を追加する🎁

➡️

```ts
// trial.ts（改善版）
import type { TrialDeps } from "./deps.js";

export type Trial = {
  userId: string;
  startedAt: Date;
  endsAt: Date;
};

export function startTrial(userId: string, deps: TrialDeps): Trial {
  const now = deps.clock.now(); // ← ここが差し替え可能✨
  deps.logger.info(`[trial] start user=${userId} at=${now.toISOString()}`);

  const endsAt = new Date(now);
  endsAt.setDate(now.getDate() + 14);

  return { userId, startedAt: now, endsAt };
}
```

> ここが大事〜！🧡
>
> * 中心は `new Date()` を作らない
> * 中心は `console.log()` しない
> * 必要なら **deps経由で呼ぶ**

---

### Step 3：本番用の deps（外側で用意）

🏗️✨

```ts
// prodDeps.ts
import type { Clock, Logger, TrialDeps } from "./deps.js";

export const systemClock: Clock = {
  now: () => new Date(),
};

export const consoleLogger: Logger = {
  info: (message: string) => console.log(message),
};

export const trialDeps: TrialDeps = {
  clock: systemClock,
  logger: consoleLogger,
};
```

> 「本物の依存を作る場所」は外側だよ〜🏠➡️🌍
> 次章でここ（組み立て場所）をもっときれいにするよ！🏗️✨

---

### Step 4：テストで差し替える（時間を止める＆ログを拾う）

🧪⏰📝最近は **Vitest 4** がメジャーとして進んでるので、例はVitestでいくね🧡（Vitest 4.0 の告知あり）([vitest.dev][3])



```ts
// trial.test.ts
import { describe, it, expect } from "vitest";
import { startTrial } from "./trial.js";
import type { TrialDeps } from "./deps.js";

describe("startTrial", () => {
  it("開始時刻を固定できて、終了日が14日後になる 🎯", () => {
    const fixedNow = new Date("2026-01-16T00:00:00.000Z");

    const logs: string[] = [];
    const deps: TrialDeps = {
      clock: { now: () => fixedNow }, // ← 時間を止める⏰🧊
      logger: { info: (m) => logs.push(m) }, // ← ログを配列に記録📝
    };

    const trial = startTrial("u-123", deps);

    expect(trial.startedAt.toISOString()).toBe("2026-01-16T00:00:00.000Z");
    expect(trial.endsAt.toISOString()).toBe("2026-01-30T00:00:00.000Z");

    expect(logs.length).toBe(1);
    expect(logs[0]).toContain("u-123");
  });
});
```

🎉 これで、テストが「安定」した！

* 毎回同じ時刻でテストできる
* ログも「出たかどうか」検証できる

---

## 7) よくある落とし穴あるある👃

💨（回避テク付き）### 落とし穴1：引数が増えすぎてつらい😇✅ 対策：**depsをオブジェクトにまとめる**（もうやってる！

えらい👏）

さらに増えたら👇もあり

* `{ clock, logger, config }` みたいに「用途ごと」に束ねる🎒

### 落とし穴2：depsが巨大になって、なんでも入り始める🧟‍♀️

✅ 対策：**最小の約束**に戻す✂️✨



* 「この関数に必要な操作だけ」
* ライブラリ丸ごと渡さない（例：loggerライブラリ全部、みたいなのは避ける）

### 落とし穴3：「一応注入できるけど、デフォルトで依存を作っちゃう」🙃例えばこういうの👇（初心者がやりがち）



```ts
export function startTrial(
  userId: string,
  deps = { clock: { now: () => new Date() }, logger: { info: console.log } }
) {
  // ...
}
```

便利そうだけど、**依存がまた中心に戻ってくる**感じになることもあるので、基本は「外側で渡す」を優先してね🏠➡️🌍

---

## 8) ミニ練習🎲🎁

：Randomも引数で渡してみよ！### お題「抽選でクーポンが当たる」機能を作りたい🎯
でも `Math.random()` 直だとテストが不安定😵‍💫

### ゴール* `random()` を引数で受け取る


* テストでは「必ず当たる乱数」にする🎲🧪

ヒントだけ置くね👇

```ts
export type Random = { next: () => number };

export function drawCoupon(deps: { random: Random }) {
  const r = deps.random.next(); // 0〜1
  return r < 0.1 ? "WIN" : "LOSE";
}
```

テストではこう👇

* `deps.random.next = () => 0.05` → WIN固定🎉
* `deps.random.next = () => 0.5` → LOSE固定🙂

---

## 9) AI拡張の使いどころ🤖🎀（引数注入は相性よい！

）AIにお願いしやすいのはここ👇



* ✅ **deps型からフェイク実装を作る**
* ✅ テストケースの洗い出し（境界値・例外系）
* ✅ AAA（Arrange/Act/Assert）の整形

プロンプト例（そのまま投げてOK）💌

* 「`TrialDeps` のフェイク（固定Clockと配列Logger）を作って」
* 「Vitestで `startTrial` のテストをAAAで書いて。時刻固定とログ検証も入れて」
* 「`TrialDeps` を最小化できる？不要メソッドがあれば削って提案して」

⚠️ 逆に丸投げしない方がいい👇

* どこに境界線を引くか（責務の分け方）
* “何を依存として扱うか” の判断（ここが設計のキモ！）🧠✨

---

## 10) まとめ🍀

✨* 依存（I/O）は **引数で受け取る**とテストが安定する🧪


* Clock/Loggerみたいな「外の世界」は **中心に直置きしない**🙅‍♀️
* 依存の契約は **最小**にして、巨大deps化を防ぐ✂️
* 本物の依存を作るのは **外側**（次章で“組み立て場所”を作るよ🏗️）

---

## 11) ちいさな確認クイズ🧠💖1. `new Date()` を関数の中心で呼ぶと、テストがつらくなる理由は？⏰
2. Loggerを注入すると、テストで何が嬉しい？📝
3. depsが巨大化しそうなとき、まずやるべきことは？✂️

---

次は **第14章：コンストラクタ注入＆合成の置き場（組み立て場所）**🏗️🧱
「depsを渡すのは分かった！…でも毎回渡すのだるいよ〜🥺」を、きれいに解決するよ✨

[1]: https://www.typescriptlang.org/download/?utm_source=chatgpt.com "How to set up TypeScript"
[2]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
[3]: https://vitest.dev/blog/vitest-4?utm_source=chatgpt.com "Vitest 4.0 is out!"
