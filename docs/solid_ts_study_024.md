# 第24章：DI（依存性注入）でDIPを実装する💉✨

## この章でできるようになること🎯✨

* 「DIP（依存性逆転）」を **実装として成立** させるために、DIが必要な理由がわかる😊
* **コンストラクタ注入（最重要）** を使って、差し替え可能な設計にできる💪
* 「本番用」と「テスト用」の実装を、**コード改造ほぼゼロ**で入れ替えられる🎭
* “DIコンテナ（ライブラリ）”を **いつ使うべきか** 判断できるようになる🧰✨

※ちなみに2026年1月時点だと、TypeScriptは **5.9系が安定版ライン**（例：5.9.3）として参照されることが多いよ〜🧡 ([Microsoft for Developers][1])
テストはVitestが **4.0** を出してるので、章の例もそれ前提でOK👌 ([vitest.dev][2])


![DI Syringe](./picture/solid_ts_study_024_di_robot_battery.png)

---

## 1) DIPとDIって、どういう関係？🤝✨

### ✅ DIP（設計のルール）

「大事なロジック（上位）」が「細かい詳細（下位）」に振り回されないように、**上位は“抽象”に依存しようね**っていうルール💡

### ✅ DI（実装のテクニック）

でも…抽象だけに依存してると、最後にこうなるよね？😵
「え、じゃあ実際の実装（DB保存とか通知とか）って、どこで繋ぐの？」

そこで登場するのが **DI（依存性注入）** 💉✨
**外から必要な部品を渡してあげる**ことで、DIPを “ちゃんと動く形” にできるよ〜🎉

---

## 2) 依存を「外から渡す」ってこういうこと😺

### ❌ DIなし（newしちゃうパターン）

* 便利そうに見えるけど、差し替え不能になりやすい😢

```ts
class PlaceOrderUseCase {
  private repo = new FileOrderRepository(); // ← ここで固定されちゃう
  private notifier = new EmailNotifier();   // ← ここも固定

  async execute() {
    // ...
  }
}
```

これだと、

* テスト時に「インメモリ保存」にしたい
* 通知を「ダミー」にしたい
  …って思っても、UseCaseの中を直さないと無理😵‍💫

### ✅ DIあり（外から渡す）

```ts
class PlaceOrderUseCase {
  constructor(
    private repo: OrderRepository,
    private notifier: Notifier
  ) {}

  async execute() {
    // ...
  }
}
```

こうすると、UseCase側は「抽象（interface）」しか知らない✨
どの実装を使うかは **外（組み立てる場所）** が決める🎯

---

## 3) DIの注入スタイル3つ（まずは①だけで勝てる）🏆✨

### ① コンストラクタ注入（最優先で覚える）🥇

* いちばん安全・わかりやすい・テストしやすい✅
* “必要な依存が揃ってないと作れない”のが良いところ🧡

### ② ファクトリ注入（生成ルールを外に逃がす）🏭

* 「条件によって実装を変える」みたいな時に便利✨

### ③ メソッド注入（実行の直前だけ渡す）🪄

* 一時的な依存に使うことがある（多用はしないでOK）🙆‍♀️

この章は **①コンストラクタ注入** を主軸にするよ〜😊💕

---

## 4) ミニプロジェクトで体験☕️📦：Campus Café 注文アプリ（超ミニ）

### 今日のゴール🎯

* 注文を作る
* 合計を計算する
* 保存する（本番：ファイル保存 / テスト：メモリ保存）
* 通知する（本番：コンソール / テスト：ダミー）

---

## 5) まず「抽象（interface）」を用意しよう🧩✨

### domain/ports（外部との接続口）を作るイメージ👛🔌

```ts
// src/domain/ports/OrderRepository.ts
export interface OrderRepository {
  save(order: Order): Promise<void>;
}
```

```ts
// src/domain/ports/Notifier.ts
export interface Notifier {
  notify(message: string): Promise<void>;
}
```

```ts
// src/domain/Order.ts
export type OrderItem = { name: string; price: number; qty: number };

export class Order {
  constructor(public readonly items: OrderItem[]) {}

  total(): number {
    return this.items.reduce((sum, x) => sum + x.price * x.qty, 0);
  }
}
```

---

## 6) UseCase（上位ロジック）は抽象だけを見る👀✨

```ts
// src/app/PlaceOrderUseCase.ts
import { Order } from "../domain/Order";
import type { OrderRepository } from "../domain/ports/OrderRepository";
import type { Notifier } from "../domain/ports/Notifier";

export class PlaceOrderUseCase {
  constructor(
    private readonly repo: OrderRepository,
    private readonly notifier: Notifier
  ) {}

  async execute(order: Order): Promise<number> {
    const total = order.total();

    await this.repo.save(order);
    await this.notifier.notify(`注文を受けたよ〜！合計は ${total} 円だよ💰✨`);

    return total;
  }
}
```

✅ UseCaseは「ファイル保存」も「メール通知」も知らない！
知ってるのは **OrderRepository / Notifier** だけ🎉

---

## 7) 下位（詳細）は infra に置いて、あとで差し替えよう🧱✨

### 本番っぽい実装：ファイル保存🗂️

```ts
// src/infra/FileOrderRepository.ts
import { promises as fs } from "node:fs";
import { Order } from "../domain/Order";
import type { OrderRepository } from "../domain/ports/OrderRepository";

export class FileOrderRepository implements OrderRepository {
  constructor(private readonly path: string) {}

  async save(order: Order): Promise<void> {
    const json = JSON.stringify(order, null, 2);
    await fs.writeFile(this.path, json, "utf-8");
  }
}
```

### 本番っぽい実装：コンソール通知📣

```ts
// src/infra/ConsoleNotifier.ts
import type { Notifier } from "../domain/ports/Notifier";

export class ConsoleNotifier implements Notifier {
  async notify(message: string): Promise<void> {
    console.log(`🔔通知：${message}`);
  }
}
```

---

## 8) いちばん大事！Composition Root（組み立て場所）🏗️✨

DIで超重要なのはここ！
「どの実装を使うか」を **アプリの入口** で決めるよ😊

```ts
// src/main.ts
import { Order } from "./domain/Order";
import { PlaceOrderUseCase } from "./app/PlaceOrderUseCase";
import { FileOrderRepository } from "./infra/FileOrderRepository";
import { ConsoleNotifier } from "./infra/ConsoleNotifier";

async function main() {
  // ここが “組み立て”（DI）💉✨
  const repo = new FileOrderRepository("./order.json");
  const notifier = new ConsoleNotifier();
  const useCase = new PlaceOrderUseCase(repo, notifier);

  const order = new Order([
    { name: "カフェラテ", price: 480, qty: 1 },
    { name: "スコーン", price: 320, qty: 2 },
  ]);

  const total = await useCase.execute(order);
  console.log(`✅完了！合計：${total} 円`);
}

main().catch((e) => {
  console.error("💥エラーだよ〜", e);
  process.exitCode = 1;
});
```

🎉 これでDI完成！
UseCaseは変えずに、入口だけで実装を差し替えできるようになったよ〜💕

---

## 9) テストが天国になる（これがDIのご褒美）👼✅

### テスト用の実装（Fake / InMemory）を作る🧪

```ts
// src/testdoubles/InMemoryOrderRepository.ts
import { Order } from "../domain/Order";
import type { OrderRepository } from "../domain/ports/OrderRepository";

export class InMemoryOrderRepository implements OrderRepository {
  public saved: Order[] = [];

  async save(order: Order): Promise<void> {
    this.saved.push(order);
  }
}
```

```ts
// src/testdoubles/DummyNotifier.ts
import type { Notifier } from "../domain/ports/Notifier";

export class DummyNotifier implements Notifier {
  public messages: string[] = [];

  async notify(message: string): Promise<void> {
    this.messages.push(message);
  }
}
```

### Vitestでテストを書く✅（Vitest 4系） ([vitest.dev][2])

```ts
// src/app/PlaceOrderUseCase.test.ts
import { describe, it, expect } from "vitest";
import { Order } from "../domain/Order";
import { PlaceOrderUseCase } from "./PlaceOrderUseCase";
import { InMemoryOrderRepository } from "../testdoubles/InMemoryOrderRepository";
import { DummyNotifier } from "../testdoubles/DummyNotifier";

describe("PlaceOrderUseCase", () => {
  it("注文を保存して通知する", async () => {
    const repo = new InMemoryOrderRepository();
    const notifier = new DummyNotifier();
    const useCase = new PlaceOrderUseCase(repo, notifier);

    const order = new Order([{ name: "紅茶", price: 400, qty: 1 }]);
    const total = await useCase.execute(order);

    expect(total).toBe(400);
    expect(repo.saved.length).toBe(1);
    expect(notifier.messages[0]).toContain("合計は 400 円");
  });
});
```

DIがあるから、**UseCaseの中身を一切いじらず**、テスト用の部品を注入できる🎉
これがめちゃ強い💪✨

---

## 10) 「手動DI」だけで十分？ DIコンテナ（ライブラリ）は？🧰🤔

### ✅ まずは手動DIでOK🙆‍♀️✨

この章みたいに

* 依存が少ない
* どこで組み立ててるか明確
  なら、手動DIがいちばん分かりやすいよ😊

### 🧰 DIコンテナが欲しくなる瞬間

* 組み立てが増えて `new new new ...` が長い😵
* 実装の登録（bind/register）をまとめたい
* スコープ（singleton / per request）管理が欲しい

---

## 11) 2026年の注意点：デコレータDIは「前提」を確認してね⚠️🪄

DIコンテナの中には、**デコレータ＋メタデータ**に頼るものがあるよ（例：Inversifyなど）🧙‍♀️✨
その場合、TypeScript設定で `experimentalDecorators` や `emitDecoratorMetadata` が必要になることが多いの。 ([inversify.io][3])

さらにややこしいのがここ👇
TypeScript 5.0で “新しい標準デコレータ（Stage 3）” が入って、`experimentalDecorators` は **レガシー側** になったよ、という流れがあるのね。 ([typescriptlang.org][4])
しかも “標準側のメタデータ提案” は **型メタデータ（emitDecoratorMetadata的なやつ）を含まない** ので、デコレータDIの事情が絡むと注意が必要〜！って感じ🥺 ([typescript-eslint.io][5])

### 例：tsyringe系を触るときによく見るやつ🧪

`reflect-metadata` を入口で読み込む、みたいな話が出てくる（エントリーポイントで最初にimport、など） ([CADDi Tech Blog][6])

👉 結論：この教材では **手動DIを基本**にして、
「ライブラリDIは、必要になったらちゃんと前提確認して導入」がおすすめだよ😊🧡

---

## 12) よくあるミス集（ここ踏むとつらい）🕳️💥

### ❌ UseCaseの中で `new` しちゃう

→ 差し替え不能、テスト地獄😢

### ❌ “なんでもコンテナから取る” になってService Locator化

→ 依存が見えなくなって、逆に読みにくい🥲

### ❌ interfaceを実行時に使おうとして混乱

TypeScriptの`interface`は **実行時に消える**よ〜🫠
（だからDIライブラリが token（Symbol等）を要求することがある）

### ❌ 循環依存（AがBを、BがAを…）

→ 設計の分割点を見直す合図🔁✨

---

## 13) AI（Copilot等）活用のコツ🤖💡（使うと爆速！でも最後は人間判断🧠）

### ① 組み立てコードを生成させるプロンプト例🪄

* 「`PlaceOrderUseCase` を手動DIで組み立てる `main.ts` を作って。依存の生成は入口に寄せて、UseCase内でnewしないで」

### ② テストダブル生成🧸

* 「`OrderRepository` のInMemory実装と、`Notifier` のDummy実装を作って。VitestでUseCaseテストも」

### ③ レビュー観点（AIの出力チェック）🔍

* UseCase内でnewしてない？
* interface（抽象）に依存できてる？
* “入口で組み立て”が守れてる？

---

## 章末ミニ課題🎁✨（手を動かす用）

### 課題A：差し替え体験🎭

1. `ConsoleNotifier` を `FileNotifier`（ログファイル出力）に差し替え
2. `main.ts` の差し替えだけで動くことを確認✅

### 課題B：テスト強化✅

1. 「通知メッセージの文言が想定通りか」もテストする
2. 「合計0円（空注文）」を渡した時の挙動を決めてテストする（例：エラーにする？0円OK？）🤔

### 課題C：設計メモ📝

* 「どれが上位（ルール）で、どれが下位（詳細）か」を1分で説明できるようにする🎤✨

---

## まとめ🌈✨

* **DIPは設計ルール**、**DIは実装テク** 💡
* UseCaseは **抽象に依存**、実装は **入口で注入** 💉
* DIがあると **差し替え＆テストが激ラク** 🎉✅

次の章は「SOLID統合リファクタ」だよ〜🧶✨
ここまでの武器がつながって、急に“設計っぽい”景色になるから楽しみにしててね😆💖

[1]: https://devblogs.microsoft.com/typescript/announcing-typescript-5-9/?utm_source=chatgpt.com "Announcing TypeScript 5.9"
[2]: https://vitest.dev/blog/vitest-4?utm_source=chatgpt.com "Vitest 4.0 is out!"
[3]: https://inversify.io/docs/faq/requirements/?utm_source=chatgpt.com "TypeScript Requirements"
[4]: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-0.html?utm_source=chatgpt.com "Documentation - TypeScript 5.0"
[5]: https://typescript-eslint.io/blog/changes-to-consistent-type-imports-with-decorators/?utm_source=chatgpt.com "Changes to `consistent-type-imports` with Legacy ..."
[6]: https://caddi.tech/2025/12/12/092241?utm_source=chatgpt.com "tsyringe で迷わない：Clean Architecture の DI 実装"
