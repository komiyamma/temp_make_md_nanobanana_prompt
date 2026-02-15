# 第23章：Outbound Port：Clockなど小さな外部依存を切る ⏰🔌

![hex_ts_study_023[(./picture/hex_ts_study_023_domain_services.png)

## 1) この章のゴール 🎯💖

![Sweep Dependencies](./picture/hex_ts_study_023_sweep_dependencies.png)

* 「時間」「UUID」「乱数」みたいな **小さな外部依存**を、中心（ユースケース/ドメイン）から追い出せるようになるよ🏃‍♀️💨
* その結果…

  * テストが **一瞬で・安定して** 書ける🧪✨
  * 「今日だけ落ちる」「たまに落ちる」みたいな地獄を減らせる😇🌈
* 合言葉：**“今”は値として受け取る**（中心で `Date.now()` しない）🛡️

> 💡2026/01 時点メモ：Node は v24 が Active LTS（安定運用向き）で、v25 が Current（最新系）だよ📌 ([Node.js][1])
> 💡TypeScript は「最新（currently 5.9）」として配布されてるよ📌 ([TypeScript][2])

---

## 2) 「小さな依存」って何がダメなの？😵‍💫💥

![Moving Target](./picture/hex_ts_study_023_moving_target.png)

たとえばユースケースでこう書いちゃう👇

* `Date.now()` / `new Date()` をそのまま使う⏱️
* `crypto.randomUUID()` をそのまま呼ぶ🆔
* `Math.random()` で抽選する🎲

これ、動くんだけど…テストが急にツラくなるの😭

* 時刻が毎回変わって **期待値が固定できない** 😭
* UUID も毎回変わって **比較できない** 😭
* “たまたま”で落ちる **フレークテスト** が生まれる😇💣

✅ だからやることはシンプル：
中心が欲しいのは「システム時刻そのもの」じゃなくて、**“今という値”**なんだよね🍀
→ その “値をくれる人” を **Outbound Port** にする🔌✨

---

## 3) 設計方針：Portは「最小の約束」✂️🔌

今回切るのは代表例としてこの2つ😊

* **ClockPort**：今の時刻をくれる⏰
* **IdGeneratorPort**：新しいIDをくれる🆔

> ✅ Portは小さく！
> 「便利だから UtilPort に全部入れよ〜」は破滅への近道だよ🐘💥（巨大Port問題）

---

## 4) 実装：Port を作る（中心側）🧠🔌

![Small Ports](./picture/hex_ts_study_023_small_ports.png)

`src/app/ports/ClockPort.ts` ⏰

```ts
export interface ClockPort {
  now(): Date;
}
```

`src/app/ports/IdGeneratorPort.ts` 🆔

```ts
export interface IdGeneratorPort {
  newId(): string;
}
```

### 返り値、`Date` がいい？ `number` がいい？🤔

* 初学者おすすめ：**`Date`**（扱いやすいし読みやすい）😊
* ガチ運用だと：UTC epoch（number）も強い💪
  どっちでもOK！大事なのは **中心が “取得方法” を知らない** こと🛡️

---

## 5) Adapter を作る（外側）🧩🚀

![Small Adapters](./picture/hex_ts_study_023_small_adapters.png)

### 5-1) SystemClockAdapter（実際の現在時刻）⏰🌍

`src/adapters/outbound/SystemClockAdapter.ts`

```ts
import type { ClockPort } from "../../app/ports/ClockPort";

export class SystemClockAdapter implements ClockPort {
  now(): Date {
    return new Date();
  }
}
```

### 5-2) CryptoIdGeneratorAdapter（UUID v4）🆔🔐

Node は `node:crypto` に `randomUUID` があるよ（標準で用意されてるの強い）✨ ([Node.js][3])
`src/adapters/outbound/CryptoIdGeneratorAdapter.ts`

```ts
import { randomUUID } from "node:crypto";
import type { IdGeneratorPort } from "../../app/ports/IdGeneratorPort";

export class CryptoIdGeneratorAdapter implements IdGeneratorPort {
  newId(): string {
    return randomUUID();
  }
}
```

> ちなみに `randomUUID()` は “暗号学的に安全な乱数で v4 UUID を作る” API だよ🔐 ([MDN Web Docs][4])

---

## 6) ユースケースで使う（中心は外側を知らない）🧠🛡️

![Ingredient Delivery](./picture/hex_ts_study_023_ingredient_delivery.png)

例：Todo に `createdAt` を足してみよう📝✨（“時間が必要になる瞬間” をわざと作る）

### 6-1) ドメイン（Todo）例 🧩📝

```ts
export type Todo = {
  id: string;
  title: string;
  completed: boolean;
  createdAt: Date;
};
```

### 6-2) AddTodoUseCase（Clock/Id を注入）🚪➡️🧠

`src/app/usecases/AddTodoUseCase.ts`

```ts
import type { ClockPort } from "../ports/ClockPort";
import type { IdGeneratorPort } from "../ports/IdGeneratorPort";
import type { TodoRepositoryPort } from "../ports/TodoRepositoryPort";

export class AddTodoUseCase {
  constructor(
    private readonly repo: TodoRepositoryPort,
    private readonly clock: ClockPort,
    private readonly idGen: IdGeneratorPort,
  ) {}

  async execute(input: { title: string }): Promise<{ id: string }> {
    const title = input.title.trim();
    if (title.length === 0) {
      throw new Error("タイトルは必須だよ🚫");
    }

    const todo = {
      id: this.idGen.newId(),
      title,
      completed: false,
      createdAt: this.clock.now(),
    };

    await this.repo.save(todo);
    return { id: todo.id };
  }
}
```

✅ ポイント

* 中心は **`new Date()` を知らない** 🙅‍♀️
* 中心は **`randomUUID()` を知らない** 🙅‍♀️
* “必要な値” を Port から受け取ってるだけ🫶

---

## 7) テストがラクになる（ここがご褒美）🧪🍰✨

![Fake Control](./picture/hex_ts_study_023_fake_control.png)

### 7-1) FakeClock（固定の時間）⏰🧊

```ts
import type { ClockPort } from "../../src/app/ports/ClockPort";

export class FakeClock implements ClockPort {
  constructor(private current: Date) {}

  now(): Date {
    return new Date(this.current); // 事故防止にコピー返すのおすすめ✨
  }

  set(d: Date) {
    this.current = d;
  }
}
```

### 7-2) FakeIdGenerator（固定ID）🆔🧊

```ts
import type { IdGeneratorPort } from "../../src/app/ports/IdGeneratorPort";

export class FakeIdGenerator implements IdGeneratorPort {
  constructor(private next: string) {}

  newId(): string {
    return this.next;
  }
}
```

### 7-3) Vitest でテスト例（超安定）🧪✅

```ts
import { describe, it, expect } from "vitest";
import { AddTodoUseCase } from "../../src/app/usecases/AddTodoUseCase";
import { FakeClock } from "../fakes/FakeClock";
import { FakeIdGenerator } from "../fakes/FakeIdGenerator";

describe("AddTodoUseCase", () => {
  it("作成日時とIDが固定できる🎉", async () => {
    const clock = new FakeClock(new Date("2026-01-01T00:00:00Z"));
    const idGen = new FakeIdGenerator("todo-0001");
    const repo = /* InMemoryRepository を差し込む */ null as any;

    const uc = new AddTodoUseCase(repo, clock, idGen);
    const result = await uc.execute({ title: "  牛乳を買う  " });

    expect(result.id).toBe("todo-0001");
    // createdAt も期待値固定で比較できるようになるよ✨
  });
});
```

---

## 8) もう1つのやり方：Fake Timers（でも“注入”が基本）⏳🧪

Vitest には fake timers 設定があるよ（`fakeTimers.now` など）⏰ ([Vitest][5])
ただしこのロードマップでは、まず **Port 注入**を推したい😊💖
理由：

* 時刻以外（UUID/乱数/通知）も同じ考え方で切れる🔌✨
* テストが「魔法」じゃなくて「設計の結果」になる🧠🛡️

---

## 9) 発展：Temporal は使う？🗓️✨

JS には `Temporal`（Date の置き換えを目指す新API）があるよ📌
でも **対応はまだ限定的** で “Baseline ではない” と明記されてる（= どこでも動く前提にしにくい）よ⚠️ ([MDN Web Docs][6])

なので現時点は：

* サーバー内部は `Date` で十分な場面が多い😊
* “より安全な日時処理” が要るなら **polyfill + Port** で包むのがキレイ🧩✨

---

## 10) アンチパターン警報 🚨😱

![Dependency Anti-Patterns](./picture/hex_ts_study_023_anti_patterns.png)

### ❌ 中心で直接呼ぶ

* `Date.now()` / `new Date()`
* `randomUUID()`
* `Math.random()`

→ テストが不安定＆差し替え不能になりがち😵‍💫

### ❌ 「UtilsPort」に全部詰める🐘🍔

* `TimeAndUuidAndRandomAndNotificationPort` みたいなの
  → だんだん巨大化して境界が死ぬ😇

### ✅ 合格ライン（この章のチェック）✅✨

* 中心（domain/app）に **`Date` 取得・UUID生成の“方法”が存在しない**🛡️
* Adapter は **薄い**（呼び出して返すだけ）🥗
* テストは Fake で **期待値が固定**できる🧪🎉

---

## 11) AI活用：この章で使えるプロンプト集 🤖📝✨

### ① 直呼び検出（中心の汚れチェック）🧼

* 「`src/domain` と `src/app` の中で `Date.now/new Date/randomUUID/Math.random` を使ってる箇所を列挙して、Port化の提案をして」

### ② Port最小化レビュー✂️

* 「ClockPort / IdGeneratorPort が大きすぎない？メソッドを減らせる？“今必要な最小”だけにして提案して」

### ③ Adapter薄さチェック🥗

* 「Adapter に業務ルールが混ざってない？if/ループ/集計があったら理由つきで指摘して」

---

## 12) 自主課題 🎀📝✨

### 課題A：`completedAt` を追加して、Clockで入れる⏰✅

* `CompleteTodoUseCase` で完了時刻を入れる
* 二重完了は禁止（既存ルールの強化）🚫

### 課題B：IdGenerator を “連番” に差し替え（テスト用）🔁🆔

* 本番：UUID
* テスト：`todo-0001` `todo-0002`…（Fake）
  → 差し替えが気持ちよくなるよ😊💕

---

## まとめ 🎁💖

* 「時間/UUID/乱数」みたいな小さな外部依存は **Outbound Port にする**🔌✨
* 中心は **“欲しい値” だけ知る**（取り方は知らない）🛡️
* その瞬間、テストが **速い・安定・書きやすい** に変わるよ🧪🚀✨

[1]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
[2]: https://www.typescriptlang.org/download/?utm_source=chatgpt.com "How to set up TypeScript"
[3]: https://nodejs.org/api/crypto.html "Crypto | Node.js v25.4.0 Documentation"
[4]: https://developer.mozilla.org/en-US/docs/Web/API/Crypto/randomUUID?utm_source=chatgpt.com "Crypto: randomUUID() method - Web APIs | MDN"
[5]: https://vitest.dev/config/faketimers?utm_source=chatgpt.com "fakeTimers | Config"
[6]: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Temporal?utm_source=chatgpt.com "Temporal - JavaScript - MDN Web Docs"
