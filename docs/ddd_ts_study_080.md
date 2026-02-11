# 第80章：中間演習：Repository差し替え体験🔁🎮

（テーマ：**「保存先を変えても、ユースケースは同じでOK！」**を体で覚える✨）

---

## この章でできるようになること🎯✨

* Repositoryを**「取り替え可能な部品」**として扱える🧩
* **InMemory → 永続化（ファイル保存）**に差し替えても、ユースケース側のコードをほぼ触らずに済む😎
* 「どこに何を書けばいいか」がブレなくなる（domain / app / infra の境界が固まる）🏰
* “差し替えられる”ことを**テストで保証**できる🧪✅

---

## まず大事な一言🌸

Repositoryは **「保存の詳細を隠すフタ」** だよ📦
だから、ユースケース（Application Service）は
「保存して」「取り出して」って頼むだけでOK🙆‍♀️
**どこに保存するか（DB/ファイル/メモリ）は infra が勝手に頑張る**💪✨

---

## 最新事情メモ（2026）🧡🆕

* TypeScript の最新版は **5.9 系**（npmの “latest” が 5.9 と明記）だよ🧡 ([typescriptlang.org][1])
* TypeScript 6.0 / 7.0 に向けた「大きい変化」も進行中（6.0は橋渡し、7.0はネイティブ化の流れ）🚀 ([Microsoft for Developers][2])
* Node.js は **v24 が Active LTS**、v25 は Current（用途により使い分け）🟢 ([nodejs.org][3])
* ESLint は **v10.0.0 が 2026-02-06 にリリース**されてるよ🧹✨ ([eslint.org][4])
* Vitest は **4.0 が出ていて**、4.1 のβも動いてる感じ🧪🔥 ([vitest.dev][5])

（※ここから先の教材コードは、**TS 5.9 + Vitest + ESLint Flat Config**あたりの前提で書くよ💡）

---

## 今日のゴール：Repositoryを2種類作って入れ替える🔁✨

作るものはこの2つ👇

1. **InMemoryOrderRepository**（メモリ保存：速い・簡単）🧠⚡
2. **JsonFileOrderRepository**（ファイル保存：永続化っぽい体験）💾📁

そして最後に…
✅ **同じユースケース（PlaceOrder / GetOrder）がそのまま動く**のを確認する🎉

---

## 1) 前提：domain に「Repositoryのinterface」だけ置く📚

ここがDDDの肝だよ〜！🌸
**domain は “保存の方法” を知らない** 🙅‍♀️
知っていいのは「こういう機能の保存箱が欲しい」だけ📦

例：`OrderRepository`（domain側）

```ts
// src/domain/order/OrderRepository.ts
import { Order } from "./Order";
import { OrderId } from "./OrderId";

export interface OrderRepository {
  save(order: Order): Promise<void>;
  findById(id: OrderId): Promise<Order | null>;
}
```

> ポイント💡
>
> * `interface` は domain
> * 実装（Mapで持つ、ファイルに書く、DBに入れる）は infra

---

## 2) 実装①：InMemoryOrderRepository（まずはMap）🗺️✨

「Repositoryってこういう感じか〜」を最速で掴めるやつ！

```ts
// src/infra/repository/InMemoryOrderRepository.ts
import { OrderRepository } from "../../domain/order/OrderRepository";
import { Order } from "../../domain/order/Order";
import { OrderId } from "../../domain/order/OrderId";

export class InMemoryOrderRepository implements OrderRepository {
  private readonly store = new Map<string, Order>();

  async save(order: Order): Promise<void> {
    this.store.set(order.id.value, order);
  }

  async findById(id: OrderId): Promise<Order | null> {
    return this.store.get(id.value) ?? null;
  }
}
```

### よくある落とし穴⚠️（ここで覚えると強い！）

* **Orderがミュータブル（中身が書き換え可能）**だと、外から参照して勝手に変えられるかも😵‍💫

  * 対策：Orderを不変寄りにする（理想）🧊
  * もしくは保存時・取得時に「複製」する（現実策）🪞

---

## 3) 実装②：JsonFileOrderRepository（永続化の雰囲気💾）

次は「保存先を変える」を体験するよ〜！🎮✨
ここで重要になるのが **“ドメインをそのままJSONにしない”** って感覚🧠

### 3-1) 永続化用DTO（infra側）を作る📦

OrderはVOやメソッドを持ってるから、保存用は**別の形**にするのがキレイ✨

```ts
// src/infra/repository/OrderRecord.ts
export type OrderRecord = {
  id: string;
  status: "Draft" | "Confirmed" | "Paid" | "Fulfilled" | "Canceled";
  lines: Array<{
    menuItemId: string;
    quantity: number;
    unitPriceYen: number;
  }>;
  createdAtIso: string;
};
```

### 3-2) Mapper（Order ⇄ OrderRecord）を作る🔁

ここはAIに骨格を作ってもらって、最後は自分で“意味”を合わせるのが超おすすめ🤖🛠️

```ts
// src/infra/repository/orderMapper.ts
import { Order } from "../../domain/order/Order";
import { OrderId } from "../../domain/order/OrderId";
import { OrderRecord } from "./OrderRecord";

// ※ここはあなたの Order/VO 設計に合わせて調整してね✨
export function toRecord(order: Order): OrderRecord {
  return {
    id: order.id.value,
    status: order.status,
    lines: order.lines.map((l) => ({
      menuItemId: l.menuItemId.value,
      quantity: l.quantity.value,
      unitPriceYen: l.unitPrice.yen,
    })),
    createdAtIso: order.createdAt.toISOString(),
  };
}

export function fromRecord(rec: OrderRecord): Order {
  return Order.reconstruct({
    id: OrderId.fromString(rec.id),
    status: rec.status,
    lines: rec.lines.map((l) => ({
      menuItemId: l.menuItemId,
      quantity: l.quantity,
      unitPriceYen: l.unitPriceYen,
    })),
    createdAtIso: rec.createdAtIso,
  });
}
```

> コツ💡
>
> * `Order.create()` は「新規作成ルート」
> * `Order.reconstruct()` は「保存データから復元ルート」
>   こう分けると、生成ルールと復元が混ざらなくて超キレイ✨

---

### 3-3) JsonFileOrderRepository（ファイルに1注文=1ファイル）📁

「1注文ごとに `orders/{id}.json`」みたいにするとシンプルで分かりやすいよ🧡

```ts
// src/infra/repository/JsonFileOrderRepository.ts
import { promises as fs } from "node:fs";
import path from "node:path";
import { OrderRepository } from "../../domain/order/OrderRepository";
import { Order } from "../../domain/order/Order";
import { OrderId } from "../../domain/order/OrderId";
import { toRecord, fromRecord } from "./orderMapper";
import { OrderRecord } from "./OrderRecord";

export class JsonFileOrderRepository implements OrderRepository {
  constructor(private readonly baseDir: string) {}

  private filePath(id: string): string {
    return path.join(this.baseDir, "orders", `${id}.json`);
  }

  async save(order: Order): Promise<void> {
    const file = this.filePath(order.id.value);
    await fs.mkdir(path.dirname(file), { recursive: true });

    // ざっくり安全策：一旦 tmp に書いて rename（途中で落ちても壊れにくい）🛡️
    const tmp = `${file}.tmp`;
    const rec = toRecord(order);

    await fs.writeFile(tmp, JSON.stringify(rec, null, 2), "utf-8");
    await fs.rename(tmp, file);
  }

  async findById(id: OrderId): Promise<Order | null> {
    const file = this.filePath(id.value);

    try {
      const json = await fs.readFile(file, "utf-8");
      const rec = JSON.parse(json) as OrderRecord;
      return fromRecord(rec);
    } catch (e: any) {
      if (e?.code === "ENOENT") return null;
      throw e;
    }
  }
}
```

---

## 4) “差し替えできる”を感じる瞬間：Composition Rootで選ぶ🎛️✨

Repositoryは **注入**するだけでOK！

```ts
// src/main.ts
import { InMemoryOrderRepository } from "./infra/repository/InMemoryOrderRepository";
import { JsonFileOrderRepository } from "./infra/repository/JsonFileOrderRepository";
import { PlaceOrderService } from "./app/PlaceOrderService"; // 例
import path from "node:path";

const repo =
  process.env.REPO === "file"
    ? new JsonFileOrderRepository(path.join(process.cwd(), ".data"))
    : new InMemoryOrderRepository();

const placeOrder = new PlaceOrderService(repo);

// ここから先は「いつものユースケース呼び出し」🎬
await placeOrder.execute({
  customerId: "C001",
  items: [{ menuItemId: "LATTE", quantity: 1 }],
});
```

🎉 **ここが最高ポイント：PlaceOrderService は repo の種類を一切知らない！**
（だから取り替えられる！🔁✨）

---

## 5) 仕上げ：Repositoryの“契約テスト”を書く🧪✅

ここ、めちゃ気持ちいいよ…！🥹💓
同じテストを **InMemory と File の両方**に当てるの！

### 5-1) 契約テストの型（factoryを受け取る）

```ts
// test/orderRepository.contract.test.ts
import { describe, it, expect, beforeEach, afterEach } from "vitest";
import { OrderRepository } from "../src/domain/order/OrderRepository";
import { InMemoryOrderRepository } from "../src/infra/repository/InMemoryOrderRepository";
import { JsonFileOrderRepository } from "../src/infra/repository/JsonFileOrderRepository";
import { promises as fs } from "node:fs";
import path from "node:path";

// あなたの Order の作り方に合わせてね✨
import { Order } from "../src/domain/order/Order";
import { OrderId } from "../src/domain/order/OrderId";

type RepoFactory = () => Promise<{ repo: OrderRepository; dispose: () => Promise<void> }>;

function contract(name: string, factory: RepoFactory) {
  describe(name, () => {
    let repo: OrderRepository;
    let dispose: () => Promise<void>;

    beforeEach(async () => {
      const created = await factory();
      repo = created.repo;
      dispose = created.dispose;
    });

    afterEach(async () => {
      await dispose();
    });

    it("saveしたものをfindByIdで取れる💾🔎", async () => {
      const order = Order.createNew({
        id: OrderId.new(),
        customerId: "C001",
        items: [{ menuItemId: "LATTE", quantity: 1, unitPriceYen: 500 }],
      });

      await repo.save(order);

      const loaded = await repo.findById(order.id);
      expect(loaded).not.toBeNull();
      expect(loaded!.id.value).toBe(order.id.value);
    });

    it("存在しないIDはnullになる🙂‍↕️", async () => {
      const loaded = await repo.findById(OrderId.fromString("NOPE"));
      expect(loaded).toBeNull();
    });
  });
}

contract("InMemoryOrderRepository", async () => ({
  repo: new InMemoryOrderRepository(),
  dispose: async () => {},
}));

contract("JsonFileOrderRepository", async () => {
  const dir = path.join(process.cwd(), ".tmp-test-data", crypto.randomUUID());
  await fs.mkdir(dir, { recursive: true });

  return {
    repo: new JsonFileOrderRepository(dir),
    dispose: async () => {
      await fs.rm(dir, { recursive: true, force: true });
    },
  };
});
```

> ここでの学び🌸
>
> * 「Repositoryはこの振る舞いを守ってね」という**共通ルール**がテストで固定される✅
> * 新しいDB版Repositoryを作っても、このテストを通せば安心😌💕

---

## 6) AIの使いどころ（この章はめっちゃ相性いい🤖✨）

ここは **GitHub Copilot** / **OpenAI Codex** みたいなAI相棒が輝くよ〜🌟

おすすめプロンプト例👇（そのまま投げてOK）

* 「OrderをJSON保存するための OrderRecord DTO を提案して」📦
* 「Order ⇄ OrderRecord の mapper の雛形を作って（ただし domain に永続化知識を入れない）」🧠
* 「Repository契約テストを Vitest で書いて。factory で repo を差し替え可能にして」🧪
* 「このRepository実装の“境界違反”をレビューして（domainにIOが入ってないかチェックして）」🚧

---

## よくある失敗パターン集😂⚠️（先に潰そ！）

* domain の Order が `fs` を import してしまう（境界崩壊）💥
* 「保存形式（JSONの形）」を domain が知ってしまう（未来のDB移行で泣く）😭
* InMemory では通るのに File で落ちる（Dateや数値の変換ミス）⏰🧨
* テストが「片方のrepoにしか当たってない」（差し替え体験が半減）🥲

---

## 章末ミニ演習🎓✨（楽しくレベルアップ🎮）

### 演習A：保存形式をちょい進化💾✨

* `createdAtIso` を追加して「注文がいつ作られたか」も復元できるようにしてみよ⏰

### 演習B：Repositoryを“ラップ”してみる🎁

* `CachingOrderRepository` を作って、`findById` の結果をメモリキャッシュする（中身は別repoに委譲）🧠⚡

  * これ、差し替え設計ができてると超簡単にできるよ！

### 演習C：契約テストを増やす🧪

* 「saveを2回したら上書きになる」など、チームで欲しい“契約”を足していこう✅✨

---

## まとめ🎀

この章のゴールはこれだけ！👇
**「保存先を変えても、ユースケースが変わらない」**を体験すること🔁🎉

Repositoryをちゃんと分けられると…

* 設計が育つ🌱
* 実装が怖くなくなる🧪
* 変更に強くなる🛡️✨

次（第81章〜）の **if地獄** を綺麗にさばく準備も、ここで整ったよ〜！🥳💕

---

必要なら、いまの第70章までの「カフェ注文コード」に合わせて、`Order.reconstruct()` の形（復元専用コンストラクタ）を“あなたのモデルにピッタリ”に組み直した版も書けるよ🧩✨

[1]: https://www.typescriptlang.org/download/?utm_source=chatgpt.com "How to set up TypeScript"
[2]: https://devblogs.microsoft.com/typescript/progress-on-typescript-7-december-2025/?utm_source=chatgpt.com "Progress on TypeScript 7 - December 2025"
[3]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
[4]: https://eslint.org/blog/2026/02/eslint-v10.0.0-released/?utm_source=chatgpt.com "ESLint v10.0.0 released"
[5]: https://vitest.dev/blog/vitest-4?utm_source=chatgpt.com "Vitest 4.0 is out!"
