# 第12章：分離の基本手順（押し出す→薄くする）🧹➡️🧩

![testable_ts_study_012_push_out.png](./picture/testable_ts_study_012_push_out.png)

この章は「ぐちゃっとした最悪コード」から出発して、**安全に** I/O を外へ押し出して、**境界を薄く**して、最後にテストで守るところまでやるよ〜！🧪✨

（いまの主流ツール感としては、Node は Active LTS が 24 系、TypeScript は npm の最新が 5.9.3、テストは Vitest 4 系が人気どころだよ〜📌） ([Node.js][1])

---

## 0. 今日のゴール🎯💖章が終わったら、これができるようになるよ👇



* 「最悪コード」を見て **I/O とロジックの境目**を言語化できる🗣️
* **中心（ロジック）を先に抽出**できる🧠✨
* I/O を **外へ押し出して**、境界を **薄く保つ**コツがわかる🧼
* 最後に **ユニットテスト**で中心をガッチリ守れる🧪🛡️

---

## 1. 「押し出す→薄くする」ってなに？🧹🪄### 押し出す（Push out）

➡️* **I/O（外の世界）**を中心から追い出す！



  * 例：`fetch` / ファイル / `Date` / `process.env` / `console.log` …ぜんぶ外側へ🚪

### 薄くする（Make thin）

🧩* 境界（アダプタ）は **変換して渡すだけ**にする


* “ビジネスルール” を境界に置かない（置くとテストが地獄😇）

**合言葉：**
「中心は計算と判断だけ」「外側は取得と保存だけ」☕✨

---

## 2. ハンズオン題材：最悪コードから救出しよ😵‍💫➡️

😆題材：**注文合計**を計算して、最後にログ保存する処理🛒🧾
（I/O がいっぱい混ざってる“ありがち地獄”をわざと作るよ🔥）

---

## 3. Step0：最悪コード（まずは現状を直視👀💦）

```ts
// src/checkout.ts
import { promises as fs } from "node:fs";

type Item = { id: string; qty: number };

export async function checkout(userId: string, items: Item[]) {
  const discountRate = Number(process.env.DISCOUNT_RATE ?? "0"); // env(I/O)
  const isWeekend = [0, 6].includes(new Date().getDay());        // Date(I/O)

  // HTTP(I/O)
  const ids = items.map((x) => x.id).join(",");
  const res = await fetch(`https://example.com/api/prices?ids=${ids}`);
  if (!res.ok) throw new Error("price api failed");
  const prices = (await res.json()) as Record<string, number>;

  // ロジック(中心っぽいの)がI/Oに埋もれてる…
  let total = 0;
  for (const item of items) {
    total += (prices[item.id] ?? 0) * item.qty;
  }
  if (isWeekend) total *= 0.9;         // 週末10%OFF
  total *= 1 - discountRate;           // envの割引

  console.log("TOTAL", total);         // log(I/O)
  await fs.appendFile("orders.log", `${userId}\t${total}\n`, "utf-8"); // file(I/O)

  return total;
}
```

### どこがツライ？😇💥* `Date` と `process.env` があると **テストが不安定**になりがち⏰⚙️


* `fetch` と `fs` があると **テストが遅い＆壊れやすい**🌐📁
* しかも全部が1つに混ざってて、**どこをテストすればいいか不明**🫠

---

## 4. Step1：中心抽出（まずはロジックを“外に出す”🧠✨

）コツはこれ👇
**「コピペでいいから中心候補を別関数にして、あとで整える」**🧼

```ts
// src/core/pricing.ts
type Item = { id: string; qty: number };

export function calculateTotal(args: {
  items: Item[];
  prices: Record<string, number>;
  discountRate: number;
  isWeekend: boolean;
}) {
  const { items, prices, discountRate, isWeekend } = args;

  let total = 0;
  for (const item of items) {
    total += (prices[item.id] ?? 0) * item.qty;
  }
  if (isWeekend) total *= 0.9;
  total *= 1 - discountRate;

  // 小数の扱いは一旦そのまま（後で設計できるよ🪙）
  return total;
}
```

そして元の関数は「呼ぶだけ」に近づける👇

```ts
// src/checkout.ts
import { promises as fs } from "node:fs";
import { calculateTotal } from "./core/pricing";

type Item = { id: string; qty: number };

export async function checkout(userId: string, items: Item[]) {
  const discountRate = Number(process.env.DISCOUNT_RATE ?? "0");
  const isWeekend = [0, 6].includes(new Date().getDay());

  const ids = items.map((x) => x.id).join(",");
  const res = await fetch(`https://example.com/api/prices?ids=${ids}`);
  if (!res.ok) throw new Error("price api failed");
  const prices = (await res.json()) as Record<string, number>;

  const total = calculateTotal({ items, prices, discountRate, isWeekend });

  console.log("TOTAL", total);
  await fs.appendFile("orders.log", `${userId}\t${total}\n`, "utf-8");
  return total;
}
```

✅ **この時点での勝ち**：中心が「I/Oなし」で独立した！🎉

---

## 5. Step2：I/Oを外へ押し出す（中心に“値だけ”渡す📦➡️

🧠）次は、中心に渡すものを **“I/Oの結果（値）だけ”**に揃えるよ✨
（中心は `fetch` も `fs` も `Date` も知らない世界へ…！）

ここでやるのは主に2つ👇

* I/Oの取得：外側でやる（価格取得、週末判定、割引率取得）
* I/Oの保存：外側でやる（ログ、ファイル保存）

この段階では interface まで急がなくてOK🙆‍♀️
**まず “中心＝純粋” を徹底**しよ〜！

---

## 6. Step3：境界をinterface化（差し替え可能にする📜✨

）ここからが「薄くする」の本番だよ〜🧼🫶
中心が欲しいのは「HTTPの詳細」じゃなくて、**“価格が取れること”**だけ！

### 境界（最小の約束）

を定義📌

```ts
// src/boundary.ts
export type Item = { id: string; qty: number };

export interface PriceProvider {
  getPrices(ids: string[]): Promise<Record<string, number>>;
}

export interface Clock {
  now(): Date;
}

export interface OrderLog {
  write(line: string): Promise<void>;
}
```

### 中心（ユースケース）

を作る🧠✨「やりたいこと」をまとめて、I/O は interface 越しに使う！



```ts
// src/usecase/checkoutUsecase.ts
import { calculateTotal } from "../core/pricing";
import type { Clock, Item, OrderLog, PriceProvider } from "../boundary";

export async function checkoutUsecase(args: {
  userId: string;
  items: Item[];
  discountRate: number; // envの“結果”だけ渡す
  priceProvider: PriceProvider;
  clock: Clock;
  orderLog: OrderLog;
}) {
  const { userId, items, discountRate, priceProvider, clock, orderLog } = args;

  const isWeekend = [0, 6].includes(clock.now().getDay());
  const ids = items.map((x) => x.id);

  const prices = await priceProvider.getPrices(ids);

  const total = calculateTotal({ items, prices, discountRate, isWeekend });

  await orderLog.write(`${userId}\t${total}`);
  return total;
}
```

### 外側（実装＝アダプタ）

は“薄く”🧩✨

```ts
// src/adapters/httpPriceProvider.ts
import type { PriceProvider } from "../boundary";

export class HttpPriceProvider implements PriceProvider {
  async getPrices(ids: string[]) {
    const res = await fetch(`https://example.com/api/prices?ids=${ids.join(",")}`);
    if (!res.ok) throw new Error("price api failed");
    return (await res.json()) as Record<string, number>;
  }
}
```

```ts
// src/adapters/systemClock.ts
import type { Clock } from "../boundary";

export class SystemClock implements Clock {
  now() {
    return new Date();
  }
}
```

```ts
// src/adapters/fileOrderLog.ts
import { promises as fs } from "node:fs";
import type { OrderLog } from "../boundary";

export class FileOrderLog implements OrderLog {
  constructor(private path: string) {}
  async write(line: string) {
    await fs.appendFile(this.path, line + "\n", "utf-8");
  }
}
```

**薄い境界のチェック✅**

* アダプタに **割引ルール**とか入ってない？🙅‍♀️
* 変換して呼ぶだけ？（理想：ほぼ “配線”）🔌✨

---

## 7. Step4：テスト追加（中心を速く・確実に守る🧪🛡

️）### まず中心（純粋関数）

をテスト🍰✨Vitest は TypeScript でも導入が軽いよ〜 ([Vitest][2])



```ts
// src/core/pricing.test.ts
import { describe, it, expect } from "vitest";
import { calculateTotal } from "./pricing";

describe("calculateTotal", () => {
  it("平日は割引なし", () => {
    const total = calculateTotal({
      items: [{ id: "A", qty: 2 }],
      prices: { A: 100 },
      discountRate: 0,
      isWeekend: false,
    });
    expect(total).toBe(200);
  });

  it("週末は10%OFF", () => {
    const total = calculateTotal({
      items: [{ id: "A", qty: 2 }],
      prices: { A: 100 },
      discountRate: 0,
      isWeekend: true,
    });
    expect(total).toBe(180);
  });

  it("env割引も効く（例：20%）", () => {
    const total = calculateTotal({
      items: [{ id: "A", qty: 1 }],
      prices: { A: 1000 },
      discountRate: 0.2,
      isWeekend: false,
    });
    expect(total).toBe(800);
  });
});
```

### 次にユースケースをテスト（差し替えで爆速🧸💨

）

```ts
// src/usecase/checkoutUsecase.test.ts
import { describe, it, expect } from "vitest";
import { checkoutUsecase } from "./checkoutUsecase";
import type { Clock, OrderLog, PriceProvider } from "../boundary";

class FakeClock implements Clock {
  constructor(private d: Date) {}
  now() { return this.d; }
}

class FakePriceProvider implements PriceProvider {
  constructor(private prices: Record<string, number>) {}
  async getPrices() { return this.prices; }
}

class SpyOrderLog implements OrderLog {
  lines: string[] = [];
  async write(line: string) { this.lines.push(line); }
}

describe("checkoutUsecase", () => {
  it("週末判定＋価格取得＋ログ出力がつながる", async () => {
    const log = new SpyOrderLog();

    const total = await checkoutUsecase({
      userId: "u1",
      items: [{ id: "A", qty: 2 }],
      discountRate: 0.1,
      priceProvider: new FakePriceProvider({ A: 100 }),
      clock: new FakeClock(new Date("2026-01-17T12:00:00Z")), // 土曜
      orderLog: log,
    });

    // 200 -> 週末10%OFFで180 -> env 10%OFFで162
    expect(total).toBe(162);
    expect(log.lines[0]).toContain("u1");
  });
});
```

---

## 8. ちょい最新メモ：NodeはTypeScriptを“そのまま実行”もできるよ🧠⚡Node は v22.18.0 以降なら「消せる型」だけの TypeScript を **フラグなしで実行**できるよ（型を剥がして実行する感じ）

📌 ([Node.js][3])
だから「動作確認だけならサクッと」もやりやすい〜！✨
（ただし **型チェックはしてくれない**ので、`tsc` やテストで守るのが大事🛡️）

---

## 9. よくある事故＆回避術🚑💡* **境界が太る**：アダプタに if/ルールが増え始めたら黄色信号🟡
  → ルールは中心へ！境界は変換だけ！
* **interfaceがデカくなる**：何でも入れると地獄💀
  → “今回必要な操作だけ” にする（最小の約束📜）
* **一気に全部リファクタしたくなる**：気持ちはわかる…！😂
  → 小さく刻んで、1ステップごとに動作確認✅

---

## 10. 🤖 AI拡張に投げると強いプロンプト例（丸投げ禁止ね🫶）### ①中心抽出の下書き* 「この関数から I/O を除いた純粋関数 `calculateTotal` を抽出して。入力と出力の設計も提案して。」



### ②境界の最小化* 「`PriceProvider` を最小の interface にしたい。usecase が本当に必要なメソッドだけに絞って提案して。」

### ③テストケース洗い出し* 「週末割引・env割引・価格欠損・qty=0・小数の丸め、の観点でユニットテストケースを列挙して。」

AIの答えは **“境界が薄いか？”** で採点するとハズレにくいよ👀✨

---

## 11. まとめ（今日の型🧁🧪）* ✅ まず **中心を抽出**（ロジックを見える化）


* ✅ 次に **I/O を外へ押し出す**（中心に値だけ渡す）
* ✅ さらに **interface で境界を固定**（差し替え可能に）
* ✅ 最後に **中心をテストで守る**（速い・安定・安心）

---

## 12. 練習問題（ちょい宿題🎒✨

）1. `discountRate` の扱いを「0〜1の範囲に丸める」ルールにしたい！
   → そのルールはどこに置く？中心？境界？理由もセットで✍️😊

2. 価格取得 API のレスポンスが `{ prices: {...} }` に変わった！
   → どのファイルの変更で済ませるのが理想？🧩✨

3. “ログは保存失敗しても注文自体は成功扱い”にしたい！
   → 境界で握りつぶす？中心で扱う？どう設計する？🤔

---

次の章（第13章）は、この流れをさらに気持ちよくする **「引数注入（依存を外から渡す）」**に入っていくよ〜🎁➡️✨

[1]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
[2]: https://vitest.dev/blog/vitest-4?utm_source=chatgpt.com "Vitest 4.0 is out!"
[3]: https://nodejs.org/en/learn/typescript/run-natively?utm_source=chatgpt.com "Running TypeScript Natively"
