# 第20章：ISP（インターフェース分離）入門✂️😊

## この章でできるようになること🎯✨

* 「でっかい interface がしんどい理由」を説明できる🧠💡
* “使わないメソッドまで依存させられる”問題を見抜ける👀💥
* TypeScriptで **interface を分割して、依存を軽くする**流れが分かる🪶✨
* テスト（モック）がラクになる感覚をつかめる✅🧪


![ISP Huge Menu](./picture/solid_ts_study_020_isp_huge_menu.png)

---

## ISPってなに？🤔💭（超ざっくり）

![ISP Plug Mismatch](./picture/solid_ts_study_020_isp_plug_mismatch.png)

**ISP（Interface Segregation Principle）**は、ひとことで言うと👇

> **使わないメソッドに依存させないでね！**（＝必要なものだけ見せてね！）✂️😊

つまり、**1つの巨大 interface** をみんなで共有するんじゃなくて、
**利用者（クライアント）ごとに必要な最小の interface** に分けようね〜って話だよ🧸✨ ([ウィキペディア][1])

---

## 「巨大interface地獄」ってどんな感じ？😵‍💫🔥

![Mock Hell Scroll](./picture/solid_ts_study_020_mock_hell_scroll.png)

こんな症状が出たら、ISP違反のニオイがするよ👃💥

* ちょっとした変更なのに、関係ない場所まで修正が波及する🌊😇
* 使ってないメソッドのせいで、テスト用モックがムダに長い📏😫
* 実装クラスが「とりあえず空実装」「throw new Error()」だらけになる🧨
* interface名がふわっとしてくる（万能すぎ）🌀

---

## TypeScriptだと何がつらいの？🧩💦

TypeScriptは「形（構造）が合えばOK」な世界だから、interface自体は軽く見えがちなんだけど…
**依存が太ると、設計もテストも太る**のは同じだよ🐷💦

* 依存先の型が大きいほど、利用側が引っ張られる🧲
* モックが巨大化して「テスト準備が本体」になりがち🧪📦
* 変更時に「関係ないメソッドも壊れてない？」って不安が増える😨

---

## ハンズオン①：まずは「ダメな例」を見る👀💥

![Fat Interface Robot](./picture/solid_ts_study_020_fat_interface_robot.png)

題材：Campus Caféの「注文データ置き場（Repository）」っぽいもの☕️📦

### ❌ でかすぎ interface（Fat Interface）例

```ts
export type Order = {
  id: string;
  totalYen: number;
  createdAt: Date;
};

export interface OrderRepository {
  // 注文の保存・更新
  save(order: Order): Promise<void>;

  // 取得
  findById(id: string): Promise<Order | null>;
  findAll(): Promise<Order[]>;

  // 削除
  delete(id: string): Promise<void>;

  // 集計（分析っぽいの）
  countByDay(day: string): Promise<number>;

  // エクスポート（管理画面用）
  exportCsv(): Promise<string>;
}
```

### ある画面は「一覧表示」したいだけなのに…😇

```ts
export class OrderListService {
  constructor(private readonly repo: OrderRepository) {}

  async getList(): Promise<Order[]> {
    return this.repo.findAll(); // ← これしか使ってない
  }
}
```

**なのに `OrderRepository` の全部に依存しちゃってる**のがポイント⚠️
（save/delete/exportCsv/countByDay…全部の存在を“知ってる”状態）🧠💦

---

## ハンズオン②：テストで地獄を見る😵‍💫🧪

「一覧だけ欲しい」テストなのに、モックがムダにデカい例👇

```ts
import { describe, it, expect } from "vitest";

describe("OrderListService", () => {
  it("注文一覧を返す", async () => {
    const repoMock = {
      save: async () => {},
      findById: async () => null,
      findAll: async () => [{ id: "o1", totalYen: 1200, createdAt: new Date() }],
      delete: async () => {},
      countByDay: async () => 0,
      exportCsv: async () => "id,totalYen,createdAt\n",
    };

    const service = new OrderListService(repoMock);
    const list = await service.getList();

    expect(list.length).toBe(1);
  });
});
```

うわぁ…😇💦
**本題は findAll だけ**なのに、他のメソッドのダミーで埋まってるよね…🧻🧻🧻

---

## ISPの出番！✂️✨「使う分だけ」に分ける

![Interface Split Scissors](./picture/solid_ts_study_020_interface_split_scissors.png)

コツはこれ👇
**“利用者（クライアント）”を主語にして分ける**🎯

### ✅ 分割後：読み取り専用 / 書き込み専用 みたいに薄くする

```ts
export interface OrderReader {
  findById(id: string): Promise<Order | null>;
  findAll(): Promise<Order[]>;
}

export interface OrderWriter {
  save(order: Order): Promise<void>;
}

export interface OrderDeleter {
  delete(id: string): Promise<void>;
}

export interface OrderAnalytics {
  countByDay(day: string): Promise<number>;
}

export interface OrderExporter {
  exportCsv(): Promise<string>;
}
```

### ✅ 「一覧サービス」は OrderReader だけ依存する🪶✨

```ts
export class OrderListService {
  constructor(private readonly reader: OrderReader) {}

  async getList(): Promise<Order[]> {
    return this.reader.findAll();
  }
}
```

---

## ハンズオン③：テストが軽くなる🎉🧪

```ts
import { describe, it, expect } from "vitest";

describe("OrderListService", () => {
  it("注文一覧を返す", async () => {
    const readerMock: OrderReader = {
      findById: async () => null,
      findAll: async () => [{ id: "o1", totalYen: 1200, createdAt: new Date() }],
    };

    const service = new OrderListService(readerMock);
    const list = await service.getList();

    expect(list.length).toBe(1);
  });
});
```

スッキリ〜〜！🥳✨
**関係ないメソッドを持たなくてよくなった**のが勝ち🏆

---

## 「でも実装クラスはどうするの？」🤔🔧

![One Class Many Masks](./picture/solid_ts_study_020_one_class_many_masks.png)

分割した interface を、**同じ1つのクラスが複数 implements**してOKだよ👌✨

```ts
export class InMemoryOrderRepo
  implements OrderReader, OrderWriter, OrderDeleter, OrderAnalytics, OrderExporter
{
  private orders: Order[] = [];

  async save(order: Order) {
    this.orders = this.orders.filter(o => o.id !== order.id).concat(order);
  }

  async findById(id: string) {
    return this.orders.find(o => o.id === id) ?? null;
  }

  async findAll() {
    return [...this.orders];
  }

  async delete(id: string) {
    this.orders = this.orders.filter(o => o.id !== id);
  }

  async countByDay(day: string) {
    return this.orders.filter(o => o.createdAt.toISOString().startsWith(day)).length;
  }

  async exportCsv() {
    return this.orders.map(o => `${o.id},${o.totalYen},${o.createdAt.toISOString()}`).join("\n");
  }
}
```

ここでの美味しさは👇🍰✨

* **利用側は小さい interface だけ見る**👀
* **実装側は必要なら全部やる**💪
* 依存の向きがキレイになる（次の章以降に効いてくる）🧠🌈

---

## ISPの「分け方」ミニルール🧭✨

![Client Perspective](./picture/solid_ts_study_020_client_perspective.png)

初心者は、まずこの3つだけ覚えれば強いよ💪😊

### 1) 利用者の単位で分ける👩‍💻👩‍🎓

* 画面Aが使うもの
* バッチが使うもの
* 管理画面が使うもの
  みたいに「誰が使う？」で切る✂️

### 2) 「読む」「書く」で分ける📖✍️

* Reader / Writer は鉄板💎
  （次章で Command/Query 分離にもつながるよ🔜✨）

### 3) 迷ったら「テストがラクになる方向」へ🧪🎯

モックが短くなるのは、だいたい正義😇✨

---

## よくあるミス集⚠️😇

* **分けすぎて interface が細かすぎる**（1メソッドinterfaceだらけ）🧂
  → “利用者のまとまり”があるなら、まとめてOK👌
* **名前がふわふわ**（OrderService2 とか）🌀
  → “何の役割の窓口？”が分かる名前にする（Reader/Writerなど）✨
* **「SRPと同じ？」って混乱**🤯

  * SRP：クラスの責務（変更理由）
  * ISP：利用者が不要なものに依存しない
    似てるけど主語が違うよ🧠✨

---

## AI活用コーナー🤖💡（そのままコピペでOK）

### ✨プロンプト1：分割案を出してもらう

「この interface を利用者ごとに分割したい。利用箇所（呼び出し元）を想定して、最小依存になる分割案を3パターン出して。命名も提案して。」

### ✨プロンプト2：既存コードから“利用者”を洗い出す

「この interface の各メソッドが、どのクラス/関数で使われるべきか分類して。分類結果をもとに interface を再設計して。」

### ✨プロンプト3：テスト目線でチェック

「この設計はモックが重くならない？重くなるなら理由と改善案（ISP適用）を教えて。」

※最近のVS Codeでは、Copilotの機能が“単一拡張（Copilot Chat）へ統合”される流れが進んでるよ🧩✨（旧Copilot拡張は早めに整理される予定）([Visual Studio Code][2])

---

## ミニ課題🎒✨（10〜20分）

### 課題A：巨大 interface を分割しよう✂️

* `OrderRepository` を「一覧表示用」「注文確定用」「管理用」に分ける
* 分けた interface に合わせて `OrderListService` の依存を修正する

### 課題B：テストを軽くしよう🧪

* `OrderListService` のテストで、モックが **必要最小**になるように書き直す

### 課題C：振り返りメモ📝

* 「分割前は何がつらかった？」
* 「分割後にラクになった点は？」
  を2〜3行でOK😊✨

---

## まとめ📌🎀

* ISPは **“使わないものに依存させない”** の原則だよ✂️😊 ([ウィキペディア][1])
* TypeScriptでも、巨大interfaceは **テストと変更を重くする**😵‍💫
* 分割は「利用者基準」「読む/書く」で始めると強い💪✨
* 実装クラスが複数interfaceを implements するのは全然アリ👌🌈

おつかれさま〜！🎉🥳
次の第21章では、分割テク（Read/Write、Query/Command、用途別）をもっと気持ちよく整理していくよ🧻✨

（おまけ：最近のTypeScriptは `tsc --init` の生成内容も少し変わってたりするから、プロジェクト作成時の初期設定も“今どき”を意識するとさらに安心だよ📦✨）([typescriptlang.org][3])

[1]: https://en.wikipedia.org/wiki/Interface_segregation_principle?utm_source=chatgpt.com "Interface segregation principle"
[2]: https://code.visualstudio.com/blogs/2025/11/04/openSourceAIEditorSecondMilestone "Open Source AI Editor: Second Milestone"
[3]: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-9.html "TypeScript: Documentation - TypeScript 5.9"
