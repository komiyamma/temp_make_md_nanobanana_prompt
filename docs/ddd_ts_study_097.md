# 第97章：Outbox入門：更新と通知のズレ対策📤📬

![Outbox入門：更新と通知のズレ対策](./picture/ddd_ts_study_097_outbox_pattern.png)

今日は「**DB更新は成功したのに、イベント通知が飛ばなくて他サービスが気づかない**😱」みたいな事故を、設計でつぶす章だよ〜！
この事故の正体は **dual write（2か所書き込み）問題**。まずはそこから見ていこっ🧠💡 ([AWS ドキュメント][1])

---

## 1) まず起きる事故（Outboxが無い世界）💥😵

![Dual Write問題](./picture/ddd_ts_study_097_dual_write_problem.png)

例：カフェ注文☕
「支払い完了したら、レシート発行サービスに `PaymentCompleted` を通知する」ってしたい。

でもよくある実装はこう👇

1. `orders` を更新（Paidにする）✅
2. そのあとメッセージ（イベント）を送信📮

ここで…

* DB更新✅ → イベント送信❌（ネットワーク断・ブローカー障害）
  → **注文はPaidなのに、レシート側は知らない**😱
* 逆に、イベント送信✅ → DB更新❌（ロールバック）
  → **レシート側はPaidと思い込む**😱

これが「dual write」の不整合だよ〜⚠️ ([AWS ドキュメント][1])

---

## 2) Outboxパターンの結論（やることはシンプル）📦✨
![Transactional Outbox Boundary](./picture/ddd_ts_study_097_transaction_boundary.png)


**「ビジネス更新」と「イベント送信予定」を、同じDBトランザクションで一緒に保存する**💾🔒
そして、**別プロセス（または別スレッド）**があとから確実に送る📤

* 先に **outboxテーブル**に「送るべきイベント」を保存📝
* 別の処理が outbox を読んで、メッセージブローカーへ送信📮
* 成功したら outbox を「送信済み」にする✅

この構造がTransactional Outboxの基本だよ！ ([microservices.io][2])

---

## 3) イメージ図（超ざっくり）🖼️✨
![Outbox Pattern Workflow](./picture/ddd_ts_study_097_outbox_flow.png)


```text
(ユースケース) PayOrder
   |
   | ① DBトランザクション
   |   - orders を Paid に更新
   |   - outbox に "PaymentCompleted" をINSERT
   v
[DB] orders / outbox
              |
              | ② 後で別処理が読む（ポーリング or CDC）
              v
        [Publisher] ----> メッセージブローカー（Kafka等）📮
              |
              v
        outbox を送信済みに✅
```

> ✅ これで「DB更新だけ成功」「通知だけ成功」みたいな“ズレ”を減らせる！ ([microservices.io][2])

---

## 4) 最小設計（この章で作るもの）🧩🛠️

### Outboxレコード（おすすめ項目）📝

* `id`：イベントの一意ID（冪等性にも使える）🔁
* `eventType`：例 `PaymentCompleted`
* `aggregateId`：例 `orderId`
* `payload`：JSON（必要最小限）📦
* `occurredAt`：発生時刻⏰
* `publishedAt`：送信済み時刻（nullなら未送信）✅

💡「payloadは詰め込みすぎ注意！」は前章（第93章）とセットで効くよ〜📦⚖️

---

## 5) TypeScriptで“動く最小Outbox”を作るよ 📤🧪

ここでは **SQLite（ローカルDB） + Outboxポーリング**で体験するよ！
SQLiteは学習にちょうど良いし、Windowsでも手軽〜🪟✨
（例では `better-sqlite3` を使う想定。Nodeは安定版のLTSを使うのが無難だよ〜🧠🔧 ([Node.js][3])）

---

### 5-1) DBスキーマ（orders / outbox）🗄️

```ts
// infra/db.ts
import Database from "better-sqlite3";

export const db = new Database("app.db");

db.exec(`
  PRAGMA journal_mode = WAL;

  CREATE TABLE IF NOT EXISTS orders (
    id TEXT PRIMARY KEY,
    status TEXT NOT NULL
  );

  CREATE TABLE IF NOT EXISTS outbox_messages (
    id TEXT PRIMARY KEY,
    event_type TEXT NOT NULL,
    aggregate_id TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    occurred_at TEXT NOT NULL,
    published_at TEXT NULL
  );

  CREATE INDEX IF NOT EXISTS idx_outbox_unpublished
    ON outbox_messages(published_at, occurred_at);
`);
```

---

### 5-2) ドメインイベント（最小）📣

```ts
// domain/events.ts
export type DomainEvent =
  | {
      id: string;              // イベントID（冪等性キーにもなる）🔁
      type: "PaymentCompleted";
      occurredAt: Date;
      aggregateId: string;     // orderId
      payload: {
        orderId: string;
        paidAmountYen: number;
      };
    };
```

---

### 5-3) “支払い完了”ユースケース（重要：同一トランザクション！）💳✅
![Atomic Commit Sequence](./picture/ddd_ts_study_097_atomic_commit.png)


ポイントはここ👇
**orders更新と outbox insert を、同じ `transaction` に入れること**🔒✨

```ts
// app/payOrder.ts
import { db } from "../infra/db";
import { randomUUID } from "node:crypto";
import type { DomainEvent } from "../domain/events";

export function payOrder(orderId: string, paidAmountYen: number) {
  const tx = db.transaction(() => {
    // 1) 注文をPaidに更新
    const updated = db
      .prepare("UPDATE orders SET status = ? WHERE id = ? AND status != ?")
      .run("Paid", orderId, "Paid");

    if (updated.changes === 0) {
      // すでにPaid or 存在しない等。ここはあなたの設計方針で例外/ResultどちらでもOK🧯
      throw new Error("Order cannot be paid (not found or already paid).");
    }

    // 2) Outboxにイベントを保存（送信はまだしない！）
    const ev: DomainEvent = {
      id: randomUUID(),
      type: "PaymentCompleted",
      occurredAt: new Date(),
      aggregateId: orderId,
      payload: { orderId, paidAmountYen },
    };

    db.prepare(`
      INSERT INTO outbox_messages(id, event_type, aggregate_id, payload_json, occurred_at, published_at)
      VALUES (?, ?, ?, ?, ?, NULL)
    `).run(
      ev.id,
      ev.type,
      ev.aggregateId,
      JSON.stringify(ev.payload),
      ev.occurredAt.toISOString()
    );
  });

  tx(); // ←ここで一括コミット！✨
}
```

✅ これで「DB更新は成功したのに outbox書けてなかった」みたいなズレを減らせる！

---

### 5-4) Outbox Dispatcher（未送信を拾って送る）📤🔁
![Outbox Dispatcher Logic](./picture/ddd_ts_study_097_dispatcher_process.png)


ここでは「メッセージブローカー」の代わりに `publish()` を用意して、送れたら `published_at` を埋めるよ✅

```ts
// infra/outboxDispatcher.ts
import { db } from "./db";

type Publisher = {
  publish: (eventType: string, payload: unknown, eventId: string) => Promise<void>;
};

export function startOutboxDispatcher(publisher: Publisher) {
  const tick = async () => {
    // 1) 未送信を古い順に取る
    const rows = db.prepare(`
      SELECT id, event_type, payload_json
      FROM outbox_messages
      WHERE published_at IS NULL
      ORDER BY occurred_at ASC
      LIMIT 20
    `).all() as Array<{ id: string; event_type: string; payload_json: string }>;

    for (const r of rows) {
      try {
        await publisher.publish(r.event_type, JSON.parse(r.payload_json), r.id);

        // 2) 成功したら送信済みに✅
        db.prepare(`
          UPDATE outbox_messages
          SET published_at = ?
          WHERE id = ? AND published_at IS NULL
        `).run(new Date().toISOString(), r.id);
      } catch (e) {
        // 失敗したら今回はスルー（次回リトライ）🔁
        // 実務では attempts / next_retry_at / last_error を持つことが多いよ🧠
        console.error("publish failed:", r.id, e);
      }
    }
  };

  // ざっくり：1秒ごとに回す（学習用）⏱️
  const timer = setInterval(() => void tick(), 1000);
  return () => clearInterval(timer);
}
```

---

### 5-5) Publisher（今回はコンソールでOK）🧾📮

```ts
// infra/consolePublisher.ts
export const consolePublisher = {
  async publish(eventType: string, payload: unknown, eventId: string) {
    // ここが本来は Kafka / RabbitMQ / SNS/SQS などに送る場所📮
    console.log("[PUBLISH]", { eventId, eventType, payload });
  },
};
```

---

### 5-6) 動かす（超ミニ）🚀✨

```ts
// main.ts
import { db } from "./infra/db";
import { payOrder } from "./app/payOrder";
import { startOutboxDispatcher } from "./infra/outboxDispatcher";
import { consolePublisher } from "./infra/consolePublisher";

db.prepare("INSERT OR IGNORE INTO orders(id, status) VALUES(?, ?)").run("order-1", "Draft");

const stop = startOutboxDispatcher(consolePublisher);

payOrder("order-1", 1200);

// ちょい待ってから止める（デモ用）⏳
setTimeout(() => stop(), 5000);
```

---

## 6) この設計の“強さ”と“注意点”💪⚠️
![Dual Write vs Outbox Reliability](./picture/ddd_ts_study_097_reliability_comparison.png)


### 強さ 💪✨

* 「更新✅ 通知❌」みたいな事故を減らせる（DBに“送る予定”が残る）📤
* イベント送信をアプリの本処理から分離できる（重い処理でもOK）⏳

この考え方は、パターンとしても広く整理されてるよ📚 ([microservices.io][2])

### 注意点 ⚠️😵

* Outboxは通常 **at-least-once（最低1回は届く）**になりやすい
  → **重複**が起きる前提で、受け手は冪等にするのが大事🔁🛡️（第96章とセット！）
* 複数インスタンスでDispatcherを回すなら、**取り合い防止（ロック/claim）**が必要
  （PostgreSQLなら `SKIP LOCKED` などで実装することが多いよ🧠）

---

## 7) “ポーリング以外”の最新っぽい選択肢も知っておこ 📡✨

### CDC（変更データキャプチャ）で outbox を拾う

DBの変更ログから outbox テーブルのINSERTを拾って配信するやつ。
たとえば Debezium は outbox をキャプチャしてイベントとして流す方法を公式に案内してるよ📘✨ ([Debezium][4])

### “ランタイムに任せる”系（Outbox機能付き）

Dapr みたいに、状態管理＋pub/subと組み合わせてOutboxをサポートする仕組みもあるよ📦🔁 ([Dapr Docs][5])

> 学習段階では「自前ポーリングで仕組み理解」→ 実務で「CDC or ランタイム活用」って流れが気持ちいい☺️✨

---

## 8) ありがち設計ミス集（先に潰す）😂🧯

* ❌ Outboxに入れずに「DB更新→即publish」だけ
  → dual write地獄へ😇 ([AWS ドキュメント][1])
* ❌ Outbox payload に“画面表示用DTO全部”入れる
  → イベント肥大化📦💥
* ❌ published_at を付けず「送れたか不明」
  → 再送制御できない🔁
* ❌ 受け手が冪等じゃない
  → 重複で「レシート2枚」爆誕🧾🧾😱

---

## 9) 小課題（手を動かすやつ）🎮✨

1. `outbox_messages` に `attempts` と `last_error` を追加して、失敗回数を見える化してみよ🔁🧠
2. Publisher側で「たまに失敗する」ようにして、Outboxに残るのを確認しよ😈📤
3. 受け手（レシート側）で `eventId` を保存して「二度来ても無視」する簡易Inboxを作ろ🛡️✨

---

## 10) AI（Copilot/ChatGPT）に頼むと速いプロンプト例 🤖💬

* 「Outboxテーブルに `attempts / next_retry_at` を追加して、指数バックオフの疑似コードを提案して」🔁⏳
* 「Dispatcherが複数起動しても二重送信しにくい“claim方式”をSQLで3案出して（PostgreSQL想定）」🧠🗄️
* 「イベントpayloadを最小にするチェックリストを作って」📦✅

---

## 参考にした一次情報（この章の“根拠”）📚✨

* Transactional outbox（パターン定義と構造） ([microservices.io][2])
* Dual write問題とTransactional outboxの意図（クラウド設計ガイド） ([AWS ドキュメント][1])
* Outbox + CDC の実装観点（Debezium公式） ([Debezium][4])
* Outboxを機能として提供する例（Dapr公式） ([Dapr Docs][5])

---

次の第98章（ACL）に行く前に、もしよければ👇だけ答えて〜😊💞
「今の理解だと Outbox は **“確実に送るための送信予約箱”** って言い換えでしっくり来る？」📤📦✨

[1]: https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html?utm_source=chatgpt.com "Transactional outbox pattern - AWS Prescriptive Guidance"
[2]: https://microservices.io/patterns/data/transactional-outbox.html?utm_source=chatgpt.com "Pattern: Transactional outbox"
[3]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
[4]: https://debezium.io/documentation/reference/stable/transformations/outbox-event-router.html?utm_source=chatgpt.com "Outbox Event Router"
[5]: https://docs.dapr.io/developing-applications/building-blocks/state-management/howto-outbox/?utm_source=chatgpt.com "How-To: Enable the transactional outbox pattern"
