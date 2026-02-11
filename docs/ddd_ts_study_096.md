# 第96章：冪等性入門：同じ要求が来ても安全🔁🛡️

![冪等性入門：同じ要求が来ても安全](./picture/ddd_ts_study_096_idempotency_shield.png)

## この章でやること（ゴール）🎯

* 「リトライ（再送）」や「二重クリック」「イベント再配信」が起きても、**二重課金・二重処理にならない**設計をつくれるようになる💳🚫
* **冪等キー（Idempotency Key）**と**重複排除（Dedup）**の基本パターンを、TypeScriptで実装してテストする🧪✨
* 「ドメインの不変条件」と「アプリ層の冪等化」の役割分担が分かる🏗️💡

---

## 1) 冪等性ってなに？（超やさしく）🍭

**冪等性（べきとうせい）**は、ざっくり言うと👇

> 同じ要求が複数回届いても、結果が壊れない（1回分として扱える）性質🔁🛡️

たとえば「支払い確定」ボタンを2回押しちゃった、通信が遅くてアプリが再送した、メッセージが再配信された…
こういう**“現実に必ず起きる”**事故に強くなるための考え方だよ☺️🌪️

ちなみにHTTPでも「同じリクエストを何度送っても意図した効果が同じ」みたいな定義で **idempotent** が説明されてるよ（PUT/DELETEなど）📮✨ ([rfc-editor.org][1])

---

## 2) なぜ必要？（非同期・リトライ前提の世界）⏳🌍
![Retry Risk & Double Processing](./picture/ddd_ts_study_096_retry_risk.png)


第95章で出てきた「非同期」「リトライ」って、成功率を上げるために超大事なんだけど…
**リトライ = 同じ処理が2回走る可能性**を常に持つの🥲🔁

よくある原因👇

* ネットが一瞬切れて、クライアントが「失敗したかも？」で再送📶🔁
* サーバーは処理できてたけど、レスポンスが返る前にタイムアウト⏱️😵
* メッセージブローカーが「少なくとも1回配信（at-least-once）」で再配信📬🔁
* ユーザーが二重クリックしちゃう🖱️🖱️

だから「重複は起きる前提」で設計すると、運用がめちゃくちゃ強くなる💪🛡️✨

---

## 3) まず押さえる！冪等性の“守り方”は3段階あるよ🏰

冪等性って、ふわっと「同じでも安全！」じゃなくて、だいたい次の3つに分けて考えると整理しやすいよ📦✨

### A. ドメインの不変条件で防ぐ（最低限の城壁）🏯🔒
![Domain Invariant Protection](./picture/ddd_ts_study_096_domain_invariant.png)


例：**「支払い済みの注文は、もう支払えない」**
これは集約（Order）が守るべきルールだよね💡

でも…これだけだと **外部連携（決済）** が絡むと弱いことがある😵
「外部に課金リクエストを2回送っちゃった」みたいな事故が起きるから💳💥

---

### B. “要求”を冪等化する（冪等キー）🔑🔁
![Idempotency Key Mechanism](./picture/ddd_ts_study_096_idempotency_key_concept.png)


**同じ操作には同じキーを付ける**
→ サーバー側で「このキーはもう処理済み」なら **前回の結果を返す**（または何もしない）✨

外部APIもこの仕組みをサポートしてる例が多いよ。たとえば Stripe は「冪等キーで安全に再試行できる」ことを公式に説明してる🧾🔁 ([Stripe ドキュメント][2])

---

### C. “イベント処理”を冪等化する（重複排除）📮🚫
![Event Deduplication](./picture/ddd_ts_study_096_deduplication.png)


イベントは「同じイベントが再配信される」前提で設計するのが基本。
そのために、**イベントIDを記録して二重処理をスキップ**するよ✍️🛡️

メッセージング基盤側で重複検出が用意されてることもある（例：Azure Service BusのDuplicate detection）📬✨ ([Microsoft Learn][3])
他にも Amazon Web Services のSQS FIFOは「重複排除ウィンドウ（例：5分）」の仕組みがあるよ⏳📨 ([AWS ドキュメント][4])
ただし！基盤機能があっても、アプリ側でも冪等に作るのが堅い👍🛡️

---

## 4) 例題（カフェ注文）で起きる“二重処理”を具体化しよ☕🧾🔁
![Double Payment Prevention Scenario](./picture/ddd_ts_study_096_double_payment_prevention.png)


今回は **PayOrder（支払い）** を冪等化するよ💳✨

### 起きがちな事故シナリオ😵‍💫

1. アプリが `PayOrder` を送る
2. サーバーは決済処理して「支払い済み」にした
3. でもレスポンスが返る前にタイムアウト
4. アプリが同じ支払いをリトライ
5. **二重課金 or 二重で“支払い済み”処理**が走る💥

ここを **冪等キー**で止める🛑🔑

---

## 5) 実装方針（DDDっぽく役割を分ける）🧩🏗️

* **ドメイン（Order集約）**：

  * 「支払いは1回だけ」みたいな不変条件を守る🏯🔒
* **アプリ層（PayOrderユースケース）**：

  * 冪等キーを受け取って、**“同じ要求は1回扱い”**にする🔁🛡️
* **インフラ（IdempotencyStore）**：

  * 処理済みキーと結果を保存する📦🗄️

---

## 6) TypeScript実装（最小で体験）💻✨

### 6-1. 冪等キーVO（Value Object）🔑💎

```ts
export class IdempotencyKey {
  private constructor(public readonly value: string) {}

  static from(value: string): IdempotencyKey {
    const v = value.trim();
    if (v.length < 10) throw new Error("IdempotencyKey is too short");
    return new IdempotencyKey(v);
  }
}
```

> 本番ではUUIDを使うことが多いよ（例：`crypto.randomUUID()`）🎲✨

---

### 6-2. 冪等ストア（処理済みの記録）🗃️

「キー → 結果」を保存する仕組みを抽象化するよ📦

```ts
export type IdempotencyRecord<T> = {
  key: string;
  createdAt: Date;
  result: T;
};

export interface IdempotencyStore<T> {
  find(key: string): Promise<IdempotencyRecord<T> | null>;
  save(record: IdempotencyRecord<T>): Promise<void>;
}
```

#### InMemory版（学習用）🧪

```ts
export class InMemoryIdempotencyStore<T> implements IdempotencyStore<T> {
  private readonly map = new Map<string, IdempotencyRecord<T>>();

  async find(key: string): Promise<IdempotencyRecord<T> | null> {
    return this.map.get(key) ?? null;
  }

  async save(record: IdempotencyRecord<T>): Promise<void> {
    this.map.set(record.key, record);
  }
}
```

---

### 6-3. “冪等ラッパー”を作る（超便利）🎁🔁
![Idempotency Wrapper Pattern](./picture/ddd_ts_study_096_wrapper_pattern.png)


```ts
export async function withIdempotency<T>(
  store: IdempotencyStore<T>,
  key: IdempotencyKey,
  action: () => Promise<T>,
): Promise<T> {
  const existing = await store.find(key.value);
  if (existing) return existing.result; // ここが冪等✨

  const result = await action();

  await store.save({
    key: key.value,
    createdAt: new Date(),
    result,
  });

  return result;
}
```

> ⚠️本番では「同時に2つ来た」レースを防ぐ必要があるよ（後で説明するね）🏎️💥

---

### 6-4. PayOrderユースケースに組み込む💳🧾

（ここではRepositoryやOrder集約は“あるもの”として書くよ）

```ts
type PayOrderInput = {
  orderId: string;
  idempotencyKey: string;
};

type PayOrderOutput = {
  orderId: string;
  status: "PAID";
};

export class PayOrderUseCase {
  constructor(
    private readonly orderRepo: { findById(id: string): Promise<any>; save(order: any): Promise<void> },
    private readonly idempotencyStore: IdempotencyStore<PayOrderOutput>,
  ) {}

  async execute(input: PayOrderInput): Promise<PayOrderOutput> {
    const key = IdempotencyKey.from(input.idempotencyKey);

    return withIdempotency(this.idempotencyStore, key, async () => {
      const order = await this.orderRepo.findById(input.orderId);

      // ドメインの不変条件：「支払い済みは支払えない」などは order.pay() が守る想定🏯🔒
      order.pay(); // 例：状態遷移 + Domain Event追加など

      await this.orderRepo.save(order);

      return { orderId: input.orderId, status: "PAID" };
    });
  }
}
```

---

## 7) テストで“二重でも安全”を確認しよ🧪🔁✅

### 同じキーで2回叩いても「結果が同じ」になるテスト✨

```ts
import { describe, it, expect } from "vitest";

describe("PayOrderUseCase idempotency", () => {
  it("same idempotency key returns the same result without double processing", async () => {
    // fake order + repo
    const order = {
      paid: false,
      pay() {
        if (this.paid) throw new Error("Already paid");
        this.paid = true;
      },
    };

    let saveCount = 0;
    const repo = {
      async findById() { return order; },
      async save() { saveCount++; },
    };

    const store = new InMemoryIdempotencyStore<{ orderId: string; status: "PAID" }>();
    const uc = new PayOrderUseCase(repo, store);

    const input = { orderId: "order-1", idempotencyKey: "uuid-like-key-0000000001" };

    const r1 = await uc.execute(input);
    const r2 = await uc.execute(input);

    expect(r1).toEqual(r2);
    expect(saveCount).toBe(1); // 2回呼ばれても保存は1回分✨
  });
});
```

---

## 8) 超重要：本番の落とし穴（レース対策）🏎️💥🛡️

![レースコンディション](./picture/ddd_ts_study_096_race_condition.png)

「同じ冪等キーのリクエストが**ほぼ同時**に2つ来た」場合、これが起きる😵

* Aが `find()` → まだ無い
* Bも `find()` → まだ無い
* Aが `action()` 実行
* Bも `action()` 実行
  → **二重処理発生**💥

### 本番での定番対策🍀

* DBに `idempotency_key` の **UNIQUE制約**を貼る🔒
* 「なければINSERT（原子的）」にする（トランザクション）🧾
* INSERT競合したら「先に入れた結果を読む」に切り替える🔁

このへんはインフラ層の責務で、アプリ層のコードはスッキリ保てるよ✨🏗️

---

## 9) 冪等キー設計のコツ（地味に効く）🔑✨

* **キーのスコープ**を決める：

  * 「この操作（PayOrder）に対して一意」なのか
  * 「ユーザー × 操作 × 注文」なのか👤🧾
* **保存期間（TTL）**を決める：

  * ずっと保存だと肥大化する🥲 → 期間を決めて掃除🧹
* **結果を保存するか**：

  * 「同じレスポンスを返したい」なら保存が便利📦
  * 「処理をスキップするだけ」なら“処理済み印”でもOK✅
* **イベント側は eventId で重複排除**が分かりやすい📮🛡️

---

## 10) “イベント購読”の冪等化（ミニ版）🔔🔁

イベントハンドラは、基本こうするよ👇

* `handled_events` みたいな保存先に

  * `eventId`
  * `handlerName`
  * `handledAt`
    を記録✍️
* すでに記録があったら **処理をスキップ**✨

クラウド側で重複検出機能があっても（例：Azure Service Bus）📬、アプリも冪等にしておくと“安心感”が段違いだよ🛡️💖 ([Microsoft Learn][3])

---

## 11) AI（Copilot/Codex）に頼むなら、この聞き方が強いよ🤖💬✨

そのまま貼れるプロンプト例👇

* 「PayOrderを冪等化したい。冪等キーを受け取り、処理済みなら前回結果を返すラッパー関数をTypeScriptで。ストレージはinterfaceで抽象化して」🔁🧩
* 「同時に2件来るレースを防ぐために、DBのUNIQUE制約前提の疑似コードも併記して」🏎️🔒
* 「イベント購読側で eventId を保存して重複排除するInbox（ProcessedMessage）パターンの雛形を出して」📮✅

“コード生成”は骨格だけ出してもらって、**ルール（不変条件）と責務分担**は自分が握るのがコツだよ✊💡

---

## 12) まとめ（この章のチェックリスト）✅🛡️

* 冪等性は「重複が来る前提」の防御設計🔁
* **ドメインの不変条件**だけでは外部連携で負けることがある💳
* **冪等キー（要求の冪等化）**と **重複排除（イベントの冪等化）**を使い分ける🔑📮
* 本番は **レース対策（原子性 + UNIQUE）** が必須🏎️🔒

---

## ちょい課題（次章に効くやつ）🎓✨

1. `PlaceOrder` にも `idempotencyKey` を付けて冪等化してみよう🧾🔁
2. “同じキーだけど入力が違う”場合（悪意 or バグ）にどうする？を考えてみよう😈🧠

   * 例：キーに「入力ハッシュ」を紐づけて検出する案など💡

次の第97章（Outbox）で、「DB更新と通知のズレ」までまとめて強くしていくよ📤📬🔥

[1]: https://www.rfc-editor.org/rfc/rfc9110.html?utm_source=chatgpt.com "RFC 9110: HTTP Semantics"
[2]: https://docs.stripe.com/api/idempotent_requests?utm_source=chatgpt.com "Idempotent requests | Stripe API Reference"
[3]: https://learn.microsoft.com/en-us/azure/service-bus-messaging/duplicate-detection?utm_source=chatgpt.com "Azure Service Bus duplicate message detection"
[4]: https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/using-messagededuplicationid-property.html?utm_source=chatgpt.com "Using the message deduplication ID in Amazon SQS"
