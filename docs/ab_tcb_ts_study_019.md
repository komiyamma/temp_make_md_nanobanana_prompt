# 第19章：CQS  読みと書きを分ける 🔀👀

## この章でできるようになること ✅✨

* **CQS**（Command/Query Separation）の考え方がわかる🧠✨
* 「参照なのに更新してた😱」みたいな事故を避けられる🚧
* `getOrderDetails`（Query）と `placeOrder`（Command）を **別の入口** にできる🚪🚪
* 命名がスッキリして「この関数、何するの？」が一瞬でわかる👀💡

---

## 1. CQSってなに？ ざっくり一言で 🥤✨

![CQS Concept](./picture/ab_tcb_ts_study_019_cqs_concept.png)

CQSはこういう約束だよ👇

* **Query（読む）**：状態を変えない。情報を返す📖🔎
* **Command（書く）**：状態を変える。基本は情報を返さない（返しても最小）✍️🔥

つまり…

> **「読むなら読むだけ」「書くなら書くだけ」** にして、コードを読みやすくする作戦✨

---

## 2. なんで分けるの？ ありがちな地獄 😇🔥

![Side Effect Trap](./picture/ab_tcb_ts_study_019_side_effect_trap.png)

### あるある①：getなのに更新してた 🤯

* `getOrderDetails()` の中で「最終閲覧日時」を更新しちゃう…
* すると、**読むだけのつもり** で呼んだ画面表示が、裏でDB更新してたりする😱

✅ CQSだと「読む関数」は更新禁止ルールにできるので、こういう事故が減るよ🧯✨

### あるある②：副作用が混ざってテストがツラい 🧪💥

* Queryに更新が混ざると、テストが「読んだだけなのに状態が変わる」になって混乱する😵‍💫

✅ Queryは “純粋に読み取るだけ” にすると、テストが超ラクになる💖

---

## 3. CQS と CQRS の違い まぎらわしいやつ整理 🧹✨

* **CQS**：関数・メソッドの設計ルール（小さめの話）🧩
* **CQRS**：読み書きでモデルやDBまで分けることもある（大きめの話）🏗️

この章はまず **CQS（小さい方）** を体に入れようね💪😊

---

## 4. 今回のミニECで「読み」と「書き」を分ける 🛒📦💳

![Read Write Pipelines](./picture/ab_tcb_ts_study_019_read_write_pipelines.png)

### 目標🎯

* Query：`getOrderDetails(orderId)` → 画面表示用DTOを返す👀📄
* Command：`placeOrder(cmd)` → 注文を作って保存する✍️💾

---

## 5. フォルダ構成 迷子防止 🧭📁

![Folder Separation](./picture/ab_tcb_ts_study_019_folder_separation.png)

第18章の構成をそのまま活かして、application配下を分けるよ👇

* `src/domain/...` 🧠（集約・VO・不変条件）
* `src/application/commands/...` ✍️（Command＝書くユースケース）
* `src/application/queries/...` 🔎（Query＝読むサービス）
* `src/infrastructure/...` 🔌（DBなど。今はインメモリでもOK）
* `src/tests/...` 🧪（テスト）

---

## 6. 命名ルール これだけで見通し爆上げ 💡✨

### Queryっぽい動詞（読むだけ）📖

* `get` / `find` / `fetch` / `list` / `search`

### Commandっぽい動詞（書く）✍️

* `place` / `create` / `add` / `remove` / `cancel` / `pay` / `change`

✅ 迷ったらこう考えると楽だよ👇
「**呼んだだけで世界が変わる？**」→ 変わるならCommand🔥

---

## 7. 手を動かす まず Query から作る 🔎✨

### 7-1. Queryの返り値は DTO にしよう 📦

![Query DTO](./picture/ab_tcb_ts_study_019_query_dto.png)

Queryは **集約そのものを返さない** のがコツだよ（返すと、外からいじれて事故りやすい😇）

```ts
// src/application/queries/dto/OrderDetailsDto.ts
export type OrderDetailsDto = {
  orderId: string;
  status: "Draft" | "Paid" | "Cancelled";
  items: Array<{
    productId: string;
    unitPrice: number; // JPY
    quantity: number;
    lineTotal: number; // JPY
  }>;
  totalAmount: number; // JPY
  version: number;
};
```

---

### 7-2. Query専用の入口  OrderQueryService 🔎🎀

ここでは「インメモリRepositoryから読んでDTOに整形する」だけにするよ😊

```ts
// src/application/queries/GetOrderDetailsQueryService.ts
import { OrderId } from "../../domain/order/OrderId";
import { OrderRepository } from "../../domain/order/OrderRepository";
import { OrderDetailsDto } from "./dto/OrderDetailsDto";

export class GetOrderDetailsQueryService {
  constructor(private readonly orders: OrderRepository) {}

  async execute(orderId: string): Promise<OrderDetailsDto | null> {
    if (!orderId?.trim()) return null;

    const id = OrderId.from(orderId.trim());
    const order = await this.orders.findById(id);
    if (!order) return null;

    // ✅ ここは「読むだけ」：order.addItem みたいな変更は絶対しない！
    const items = order.items.map((x) => ({
      productId: x.productId,
      unitPrice: x.unitPrice.amount,
      quantity: x.quantity.value,
      lineTotal: x.lineTotal.amount
    }));

    return {
      orderId: order.id.value,
      status: order.status,
      items,
      totalAmount: order.total().amount,
      version: order.version
    };
  }
}
```

💡ポイント

* Queryは **状態を変えるメソッドを呼ばない**（`addItem` などは呼ばない）🚫
* 返すのは **DTOだけ**（集約は外に出さない）📦✨

---

## 8. 次に Command  placeOrder を作る ✍️🔥

![Command Flow](./picture/ab_tcb_ts_study_019_command_flow.png)

`placeOrder` は「注文作成して、明細入れて、保存して、ID返す」みたいな **書く処理の入口** にするよ🛒💨

第18章で使った `Result` をそのまま使ってOK（第20章でさらに強化するやつ）😊

```ts
// src/application/commands/PlaceOrderUseCase.ts
import { Order } from "../../domain/order/Order";
import { OrderId } from "../../domain/order/OrderId";
import { OrderRepository } from "../../domain/order/OrderRepository";
import { OrderItem } from "../../domain/order/Order";
import { Money } from "../../domain/shared/Money";
import { Quantity } from "../../domain/shared/Quantity";
import { Result, Ok, Err } from "../shared/Result";

export type PlaceOrderCommand = {
  orderId: string;
  items: Array<{
    productId: string;
    unitPrice: number; // JPY
    quantity: number;
  }>;
};

export type PlaceOrderError =
  | { type: "INVALID_INPUT"; message: string }
  | { type: "ALREADY_EXISTS" }
  | { type: "DOMAIN_ERROR"; code: string };

export type PlaceOrderOutput = {
  orderId: string;
};

export class PlaceOrderUseCase {
  constructor(private readonly orders: OrderRepository) {}

  async execute(cmd: PlaceOrderCommand): Promise<Result<PlaceOrderOutput, PlaceOrderError>> {
    // 0) 入力の最低限チェック🧼
    if (!cmd.orderId?.trim()) return Err({ type: "INVALID_INPUT", message: "orderId is required" });
    if (!cmd.items || cmd.items.length === 0) return Err({ type: "INVALID_INPUT", message: "items is required" });

    const id = OrderId.from(cmd.orderId.trim());

    // 1) 重複チェック🧯
    const exists = await this.orders.findById(id);
    if (exists) return Err({ type: "ALREADY_EXISTS" });

    // 2) 集約生成👑
    const order = Order.create(id);

    // 3) 変更（ここが“書く”）✍️🔥
    try {
      for (const it of cmd.items) {
        const item = new OrderItem(
          it.productId.trim(),
          Money.jpy(it.unitPrice),
          new Quantity(it.quantity)
        );
        order.addItem(item); // ✅ 集約の操作は Command 側でだけ呼ぶイメージ✨
      }
    } catch (e) {
      const code = e instanceof Error ? e.message : "UNKNOWN";
      return Err({ type: "DOMAIN_ERROR", code });
    }

    // 4) 保存💾
    await this.orders.save(order);

    // 5) 返すのは最小（IDだけ）📌
    return Ok({ orderId: order.id.value });
  }
}
```

💡ポイント

* Commandは **集約を変更する**（`addItem` など）🔥
* 返すのは **最小限**（画面表示用の詳細は Query で取る）🔎✨

---

## 9. 使い方のイメージ  Command → Query の順にする 🧭✨

「注文を作る」→「画面に詳細表示」みたいな流れ、よくあるよね😊

```ts
// 例：UI / API っぽいところ（ここは教材用の擬似コード）
const placeRes = await placeOrder.execute({
  orderId: "ord-100",
  items: [
    { productId: "p-1", unitPrice: 500, quantity: 2 },
    { productId: "p-2", unitPrice: 1200, quantity: 1 }
  ]
});

if (placeRes.ok) {
  const details = await getOrderDetails.execute(placeRes.value.orderId);
  console.log(details);
}
```

✅ これが気持ちいいところ😍

* 更新したら Command
* 表示したいなら Query
  って分かれるので、**責務が迷子にならない** 🧠✨

---

## 10. テストで「読みは読んだだけ」「書きは変わる」を確認 🧪💕

### 10-1. Queryは状態が変わらないことをチェック🔎✅

```ts
// src/tests/CqsQuery.test.ts
import { describe, it, expect } from "vitest";
import { InMemoryOrderRepository } from "./InMemoryOrderRepository";
import { PlaceOrderUseCase } from "../application/commands/PlaceOrderUseCase";
import { GetOrderDetailsQueryService } from "../application/queries/GetOrderDetailsQueryService";

describe("CQS Query", () => {
  it("query does not change state", async () => {
    const repo = new InMemoryOrderRepository();
    const place = new PlaceOrderUseCase(repo);
    const get = new GetOrderDetailsQueryService(repo);

    await place.execute({
      orderId: "ord-200",
      items: [{ productId: "p-9", unitPrice: 1000, quantity: 1 }]
    });

    const a = await get.execute("ord-200");
    const b = await get.execute("ord-200");

    expect(a).toEqual(b); // 2回読んでも同じ（読むだけ）✨
  });
});
```

---

## 11. よくあるミス集 ここだけは踏まないで😇🧨

### ミス①：Queryの中で集約をいじる🚫

![Query Mutation Mistake](./picture/ab_tcb_ts_study_019_query_mutation_mistake.png)

* `getOrderDetails()` の中で `order.addItem(...)` とかやっちゃう
  → **それ、Queryじゃない** 😭

✅ 対策：
Queryは **DTOを作って返すだけ** にする📦✨

### ミス②：Commandが画面表示用の巨大DTOを返す📦💥

* Commandが「あれもこれも」返し始めると、だんだん読みにくくなる😵

✅ 対策：
Commandは **IDなど最小** → 必要なら Query で取り直す🔎💡

### ミス③：命名がふわっとして判定不能🤔

* `handleOrder()` とか `process()` とか
  → 何するか読めない😇

✅ 対策：
Command/Queryの動詞に寄せる（さっきの表）🗣️✨

---

## 12. AI活用  CopilotやCodexに投げると強いプロンプト 🤖✨

※開発環境は VS Code 前提で、GitHub の Copilot か OpenAI 系のAI拡張が使える想定でOKだよ🧠💕

### ① これCommand？Query？判定してもらう🔀

「この関数は Command / Query どっち？理由も。
もし混ざってたら分離案を出して」

### ② 命名をCQSっぽく整える🗣️

「このメソッド名が Query/Command として自然になるようにリネーム案を複数出して
（get/find/list vs create/add/cancel/pay）」

### ③ Queryが副作用を持ってないかレビュー👀

「このQueryの実装に“状態変更”が混ざってないかレビューして。
混ざってたら、Command側へ移す提案をして」

---

## 13. まとめ 🧾✨

* **CQS = 読むなら読め、書くなら書け** 🔀👀
* Queryは **状態を変えない** ＋ **DTOを返す** 📦
* Commandは **状態を変える** ＋ **返すのは最小** ✍️
* これで「副作用が読めるコード」になって、設計が一段わかりやすくなるよ😊💖

---

次の第20章は、いよいよ **エラーを仕様にする（Result型と例外境界）🚨📦** で、いま簡易にしてた `DOMAIN_ERROR` などをもっとキレイに整理していくよ〜✨
