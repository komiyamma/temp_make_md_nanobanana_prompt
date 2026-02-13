# 第14章：コンストラクタ注入＆合成の置き場（組み立て場所）🏗️🧱

![testable_ts_study_014_composition_root.png](./picture/testable_ts_study_014_composition_root.png)

この章は「**アプリの部品を“どこで組み立てるか”**」を決める回だよ〜！😊
テスタブル設計って、突き詰めると **“ロジックの世界を、外部の都合から守る”** ことなんだけど、そのために **組み立て係（Composition Root）** がめちゃ重要になるの🧩💕

---

## 1) 今日のゴール🎯✨

できるようになったら勝ち〜！💪🌈



* ✅ **コンストラクタ注入**が何か説明できる（＆引数注入との違いがわかる）
* ✅ “`new` だらけのコード”を **一箇所に集める** 発想が持てる
* ✅ **Composition Root** を作って、中心（ロジック）へ依存を渡せる
* ✅ テストで依存を差し替えられる（Fake/Stub でOK）🧪✨

---

## 2) まず直感：アプリは「部品」と「組み立て係」でできてる🧸🧩

![testable_ts_study_014_app_structure.png](./picture/testable_ts_study_014_app_structure.png)

アプリって、ざっくりこう👇



* 🧠 **中心（ロジック）**：計算・判断・ルール（＝テストしたい場所）
* 🌍 **外側（I/O）**：DB、HTTP、ファイル、時刻、ログ…（＝現実世界）
* 🏗️ **組み立て係**：外側の実体を用意して、中心に渡す人

ここで大事なのが…
**中心が「外側の作り方（`new`）」を知らないこと**🙅‍♀️✨

> 中心は「これが欲しい（interface）」だけ言う。
> 外側が「はい、実物どうぞ！」って渡す。🎁

---

## 3) コンストラクタ注入ってなに？🏗️

![testable_ts_study_014_constructor_injection.png](./picture/testable_ts_study_014_constructor_injection.png)

➡️🎁**クラス**を使うとき、依存（Clock/Logger/Repositoryなど）を
**コンストラクタで受け取る**やり方だよ😊

* ✅ 依存が“最初に揃ってる”状態で動く
* ✅ テストで差し替えやすい
* ✅ 依存が増えたら「このクラス重いかも？」と気づきやすい（良い警報）🚨

---

## 4) 引数注入 vs コンストラクタ注入：使い分けのコツ🍰🧁**引数注入（第13章）**が得意なのは👇

![testable_ts_study_014_arg_vs_ctor.png](./picture/testable_ts_study_014_arg_vs_ctor.png)



* 🧠「関数1発」中心の小さいロジック
* ✅ 依存が少ない（1〜2個くらい）

**コンストラクタ注入**が得意なのは👇

* 🧱「状態を持つわけじゃないけど、複数の処理を束ねる」サービスクラス
* ✅ 依存を毎回引数に渡すのがダルい＆読みづらいとき

---

## 5) Composition Root（組み立て場所）

![testable_ts_study_014_composition_root_location.png](./picture/testable_ts_study_014_composition_root_location.png)

ってどこ？📌🏠超シンプルに言うと…

**“アプリの入り口（エントリポイント）に一番近い場所”** に作るのが基本！😊✨

例：

* CLIなら `src/main.ts`
* Webサーバなら `src/server.ts`（起動するファイル）
* バッチなら `src/batch/run.ts`
* （フロントなら `index.tsx` とかの起点）

ここに **`new` が集まる**のが理想💖
中心側のコードに `new ConsoleLogger()` とか書き出したら黄色信号〜！🚥😵‍💫

---

## 6) ハンズオン：ミニ機能を「組み立て係つき」にする🧪🏗️

![testable_ts_study_014_order_service_diagram.png](./picture/testable_ts_study_014_order_service_diagram.png)

✨題材：**注文を保存してログを出す**（ついでに受付時刻も使う）🛒🕒📝



### 6-1. まず「中心」が欲しいものを interface で言う📜✨

```ts
// src/core/ports.ts
export interface Clock {
  now(): Date;
}

export interface Logger {
  info(message: string, meta?: Record<string, unknown>): void;
}

export interface OrderRepository {
  save(order: Order): Promise<void>;
}

export type Order = {
  id: string;
  totalYen: number;
  createdAt: Date;
};
```

ポイント💡

* interface は **最小**にする（巨大化すると地獄👻）
* 中心は「実装」じゃなく「約束」だけ見る

---

### 6-2. 中心：依存をコンストラクタで受け取る🏗️

🎁

```ts
// src/core/orderService.ts
import type { Clock, Logger, OrderRepository, Order } from "./ports.js";

export class OrderService {
  constructor(
    private readonly repo: OrderRepository,
    private readonly clock: Clock,
    private readonly logger: Logger,
  ) {}

  async placeOrder(input: { id: string; totalYen: number }): Promise<Order> {
    // 中心のロジックは「外側の実装」を知らない✨
    const order: Order = {
      id: input.id,
      totalYen: input.totalYen,
      createdAt: this.clock.now(),
    };

    await this.repo.save(order);
    this.logger.info("Order placed", { orderId: order.id, totalYen: order.totalYen });

    return order;
  }
}
```

ここ、最高にえらい点🌟

* `new Date()` してない（Clock経由）
* `console.log` してない（Logger経由）
* DB直書きしてない（Repository経由）

---

### 6-3. 外側：実体（アダプタ）

を作る🌍🧩

```ts
// src/adapters/systemClock.ts
import type { Clock } from "../core/ports.js";

export class SystemClock implements Clock {
  now(): Date {
    return new Date();
  }
}
```

```ts
// src/adapters/consoleLogger.ts
import type { Logger } from "../core/ports.js";

export class ConsoleLogger implements Logger {
  info(message: string, meta?: Record<string, unknown>): void {
    // 実際のログ出しは外側の役目📝
    console.log(message, meta ?? {});
  }
}
```

```ts
// src/adapters/inMemoryOrderRepository.ts
import type { OrderRepository, Order } from "../core/ports.js";

export class InMemoryOrderRepository implements OrderRepository {
  private readonly store: Order[] = [];

  async save(order: Order): Promise<void> {
    this.store.push(order);
  }

  // デバッグ用（中心は呼ばない）
  dump(): Order[] {
    return [...this.store];
  }
}
```

---

### 6-4. そして主役：Composition Root（組み立て係）

🏗️🧱✨**ここに `new` を集める！**（超大事）🔥



```ts
// src/main.ts
import { OrderService } from "./core/orderService.js";
import { SystemClock } from "./adapters/systemClock.js";
import { ConsoleLogger } from "./adapters/consoleLogger.js";
import { InMemoryOrderRepository } from "./adapters/inMemoryOrderRepository.js";

function buildOrderService(): OrderService {
  const repo = new InMemoryOrderRepository();
  const clock = new SystemClock();
  const logger = new ConsoleLogger();

  // ✅ 依存を組み立てて中心へ渡す（これが合成！）
  return new OrderService(repo, clock, logger);
}

async function main() {
  const orderService = buildOrderService();

  const order = await orderService.placeOrder({ id: "A-001", totalYen: 1200 });
  console.log("RESULT:", order);
}

main().catch((e) => {
  console.error(e);
  process.exitCode = 1;
});
```

🎉 これで、「中心」はテストしやすくなるし、外側も差し替え自由になるよ〜！

---

## 7) テスト：依存を差し替えて“中心だけ”を守る🧪💕テストランナーは **Vitest** が最近も活発で、Vite系と相性よく進化してるよ〜（Vitest 4 系が出てる）

![testable_ts_study_014_test_replacement.png](./picture/testable_ts_study_014_test_replacement.png)

🧪⚡ ([Vitest][1])
（※ここは章の主題じゃないので、テスト環境の細かい話は最小限ね😊）

```ts
// src/core/orderService.test.ts
import { describe, it, expect } from "vitest";
import { OrderService } from "./orderService.js";
import type { Clock, Logger, OrderRepository, Order } from "./ports.js";

class FakeClock implements Clock {
  constructor(private readonly fixed: Date) {}
  now(): Date {
    return this.fixed;
  }
}

class SpyLogger implements Logger {
  logs: Array<{ message: string; meta?: Record<string, unknown> }> = [];
  info(message: string, meta?: Record<string, unknown>): void {
    this.logs.push({ message, meta });
  }
}

class SpyRepo implements OrderRepository {
  saved: Order[] = [];
  async save(order: Order): Promise<void> {
    this.saved.push(order);
  }
}

describe("OrderService", () => {
  it("placeOrder は注文を保存してログを出す", async () => {
    const repo = new SpyRepo();
    const clock = new FakeClock(new Date("2026-01-01T00:00:00Z"));
    const logger = new SpyLogger();

    const sut = new OrderService(repo, clock, logger);

    const order = await sut.placeOrder({ id: "A-001", totalYen: 1200 });

    expect(repo.saved).toHaveLength(1);
    expect(repo.saved[0]?.id).toBe("A-001");
    expect(order.createdAt.toISOString()).toBe("2026-01-01T00:00:00.000Z");

    expect(logger.logs[0]?.message).toBe("Order placed");
    expect(logger.logs[0]?.meta?.orderId).toBe("A-001");
  });
});
```

気持ちよさポイント💖

* 時刻が止められる🧊⏰
* 保存されたものが確認できる📦
* ログも「出たこと」を検証できる👀✨

---

## 8) よくある事故🔥（あるあるすぎて泣く🥲）### ❌ 事故1：Composition Root が散らばる🧨いろんなファイルで `new` し始めると、差し替えが地獄に…😱
✅ **“組み立てはここ！”** を決めて、そこに寄せよう！

### ❌ 事故2：interface がデカくなる🐘`OrderRepository` に `find/save/update/delete/list/search/export...` みたいに増えるやつ💀
✅ **用途ごとに分ける**（小さい約束が正義）✂️✨

### ❌ 事故3：DIコンテナを早期導入しちゃう📦😵‍💫最初から Inversify みたいなの入れると、初心者さんは迷子になりがち🌀
✅ まずは **関数 `buildX()`** で十分！（今回の `buildOrderService()` みたいにね😊）

---

## 9) “最新事情”メモ🗞️

✨（設計が効いてくる背景）* TypeScript は現在 **5.9 系**が最新ラインとして案内されてるよ（npm / 公式DLページ） ([npm][2])


* Node.js は **v24 が Active LTS**、v22 は Maintenance LTS など、LTSの世代が進んでる（公式リリース一覧） ([Node.js][3])
* TypeScript は今後 **6.0（橋渡し）→ 7.0（Go移植）** へ大きく変わる計画が進行中で、「外側の都合が変わっても中心を守る」設計がますます効いてくる流れだよ🧠✨ ([Microsoft for Developers][4])

---

## 10) 章末ミニ課題🎒✨

（15〜30分）### 課題A：`new` を追放せよ！

🏃‍♀️💨次のコード（ダメ例）を、**Composition Root に `new` を集める形**に直してね👇



```ts
// ダメ例：中心っぽい場所で new しちゃってる
export async function doSomething() {
  const logger = console;
  const now = new Date();
  logger.log("NOW", now);
}
```

✅ ゴール：

* Clock と Logger を interface にして
* 中心は注入で受け取り
* `main.ts` 側で組み立てる

---

### 課題B：依存を1個増やしてみよ🍳✨`OrderService` に「通知（Notifier）

」を追加して、テストで差し替えてみてね📩
（実装は外側、中心は interface だけ！）

---

## まとめ🎀✨* コンストラクタ注入は「クラスの依存を最初に揃える」やり方🏗️

🎁


* Composition Root は「`new` を集めて、中心に渡す」場所📌
* これができると、中心が **ユニットテストで守れる世界**に近づくよ〜🧪🌈

次の章（第15章）は、**interface を“最小の約束”にするコツ**だよ✂️📜✨
巨大interface地獄を回避しよ〜！😆💖

[1]: https://vitest.dev/blog/vitest-4?utm_source=chatgpt.com "Vitest 4.0 is out!"
[2]: https://www.npmjs.com/package/typescript?utm_source=chatgpt.com "TypeScript"
[3]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
[4]: https://devblogs.microsoft.com/typescript/progress-on-typescript-7-december-2025/?utm_source=chatgpt.com "Progress on TypeScript 7 - December 2025"
