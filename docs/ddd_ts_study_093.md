# 第93章：イベントの持つ情報：入れすぎ注意📦⚖️

![イベントの持つ情報：入れすぎ注意](./picture/ddd_ts_study_093_thin_vs_fat_event.png)

この章のテーマはひとことで言うと…
**「イベントは“通知”であって“全部入りレポート”にしない」**だよ〜🔔✨
（イベントが太ると、後々しんどくなる率がめちゃ高い…！😵‍💫）

---

## 1) まず結論：イベントは「薄く」するのが基本 🥗✨

イベント設計には「薄いイベント（Thin）」と「厚いイベント（Thick / Fat）」って考え方があるよ〜📮
厚いイベントは「必要そうな情報を全部詰めて送る」やり方。薄いイベントは「起きた事実＋最小限の識別情報だけ送る」やり方。

そして実務では、**薄いイベントが“筋肉”💪**になりやすい（疎結合を保ちやすい）って話がよく出るよ〜。([Thoughtworks][1])

---

## 2) 「入れすぎ」が何を壊すの？（ありがち事故）💥😇

イベントが太ると、だいたいこのへんが壊れるよ〜👇

* **密結合になる**：購読側が「このフィールドある前提」になって、発行側が変えられなくなる🔗😵
* **変更が地獄**：フィールド追加・削除が“契約変更”になって、互換性が怖い🧨
* **情報漏えいリスク**：個人情報とか内部データが混ざりやすい🙅‍♀️🔐
* **サイズ増で遅くなる**：配信コスト・保存コスト・ログも重くなる🐘
* **“どれが正”か分からなくなる**：イベント内の値が「計算済みの表示用」だったりして、真実がブレる😵‍💫

---

## 3) そもそも：ドメインイベントは「内側の合図」📣🏠

ここ、超大事ポイント！💡
**ドメインイベント**は「同じ境界の中（同じドメインの内側）で、何かが起きたよ〜」って伝える合図。
**外のシステムに公開する“契約”にするのは別物**で、そっちはよく「統合イベント（Integration Event）」として分けて扱うよ〜🌍📨 ([Microsoft for Developers][2])

なので基本方針はこう👇

* 🏠 **ドメインイベント**：内部用。ドメインの言葉でOK（ただし太らせない）
* 🌍 **統合イベント**：外部向け。互換性・バージョン・個人情報・契約を超意識（さらに薄くしがち）

（このロードマップは戦術DDD中心なので、まずは**内部のドメインイベントを上手に扱う**のが主役だよ〜🎀）

---

## 4) “イベントの情報”を2種類に分けよう：メタ情報とデータ 🧾🧩

イベントって、実務ではよく「封筒（エンベロープ）」＋「中身（データ）」の2階建てで考えるよ〜📩✨

### A. メタ情報（追跡のための情報）🧭

たとえば **CloudEvents** って標準仕様だと、イベントには `id / source / type / specversion` みたいな“最低限の文脈”を必須にしてるよ〜。([GitHub][3])
さらに `time`（いつ起きたか）は任意属性として定義されてる。([cloudevents.github.io][4])

DDDの内部イベントでCloudEventsをそのまま使う必要はないけど、**「最低限のメタ情報を持つ発想」**はめちゃ参考になるよ〜📌✨

DDD的におすすめのメタ情報セット（例）👇

* `eventId`：イベントの一意ID（重複処理対策にも効く）🆔
* `type`：イベント種類（例：`PaymentCompleted`）🏷️
* `occurredAt`：発生時刻⏰
* `aggregateId`：どの集約の話？🪪
* `aggregateVersion`：集約の何番目の変化？（あれば強い）🔢
* `correlationId` / `causationId`：追跡したいなら（最初は任意でOK）🧵

### B. データ（“起きた事実”そのもの）📦

ここが今日の主役！
**データは「起きた事実」を表すのに必要最小限**にするよ〜⚖️✨

---

## 5) ルール：イベントに「入れてOK / 基本NG」早見 🧁📌

### ✅ 入れてOK（入れる価値が高い）✨

* **識別子**（`orderId` など）🪪
* **その瞬間の“事実として残したい値”**（支払金額、通貨、確定した割引額など）💴
* **購読側が“どうしてもその時点で必要”で、後から取りに行けない情報**（ただし慎重に）🧐

### ❌ 基本NG（入れると後で泣く）😭

* 集約を丸ごと（Order全部）🏯🚫
* 表示用に整形した文字列（`"支払い完了です"` みたいな）🖼️🚫
* いつでも計算できる派生値（合計・ポイント残高など）➕🚫
* DB行っぽいデータ（内部カラム、フラグ乱舞）🧱🚫
* 個人情報（メール・住所など）は“最小限”でも慎重に🔐🚫

---

## 6) 例題：カフェ注文で「太いイベント」→「薄いイベント」へ 🥤➡️🥗

![Fat vs Thin](./picture/ddd_ts_study_093_fat_vs_thin.png)

### 😇 悪い例：全部盛りイベント（やりがち）

「購読側が欲しそうだから」って、Orderの中身を丸ごと入れちゃうパターン💥

```ts
// ❌ 太い（Thick）イベント例：Orderの中身を詰め込みすぎ
type PaymentCompleted_Fat = {
  eventId: string;
  type: "PaymentCompleted";
  occurredAt: string;

  // ぜんぶ入り…😵‍💫
  order: {
    id: string;
    status: "Paid";
    items: Array<{ menuId: string; name: string; price: number; qty: number }>;
    totalPrice: number;
    customer: { id: string; name: string; email: string };
    // ...将来どんどん増える
  };
};
```

これ、最初は便利に見えるんだけど…
**Order構造を変えた瞬間にイベント契約が壊れる**し、購読者が増えるほど地獄になるよ〜😇🧨

---

### 🥰 良い例：薄いイベント（おすすめ）

「起きた事実」と「識別子」を中心にする✨

```ts
// ✅ 薄い（Thin）イベント例：必要最小限
type PaymentCompleted = {
  eventId: string;
  type: "PaymentCompleted";
  occurredAt: string;

  aggregate: {
    name: "Order";
    id: string;              // orderId
    version: number;         // あれば強い（任意でもOK）
  };

  data: {
    paymentId: string;       // 支払いの同一性
    amount: number;          // “事実として残したい値”
    currency: "JPY";         // 例題なので固定でもOK
  };
};
```

ポイントはこれ👇

* **Orderの構造を送ってない**（購読側は必要なら取得する）
* **イベントは「支払い完了」という事実**に集中してる📣✨
* `amount` みたいな“その時点の確定値”は入れてOK（後から変えない前提）💴

---

## 7) 「購読側が欲しい情報」はどうするの？🔎📚

答え：**購読側で取りに行く**ことが多いよ〜🏃‍♀️💨
（だから“薄いイベント”が成立する✨）

たとえば「レシート作成」側は、イベントを受け取ったら…

```ts
async function onPaymentCompleted(ev: PaymentCompleted) {
  // 1) orderIdで集約を取得
  const order = await orderRepository.findById(ev.aggregate.id);

  // 2) 必要な情報を使って副作用（レシート作成など）
  const receipt = Receipt.issueFrom(order, ev.data.paymentId, ev.data.amount);

  // 3) 保存・通知など
  await receiptRepository.save(receipt);
}
```

この形にしておくと、Orderの内部構造が変わっても
**イベント契約が壊れにくい**んだ〜🥰🔧

---

## 8) でも薄すぎると困らない？（トレードオフ）⚖️🤔

薄いイベントにも弱点はあるよ〜👇

* 取得先が落ちてたら処理できない（同期購読だと特に）😵
* 取得時点で状態が変わってるかも（整合性の話）⏳

だから実務では、だいたいこうバランス取るよ〜🍰

* **購読の目的が“監査・記録”なら、事実として残す値はイベントに入れる**🧾✨
* **購読の目的が“何か作業する”なら、識別子＋最小の確定値**（不足分は取得）🔎
* **「後から絶対再現したい」なら、イベントソーシングやスナップショットの世界**（別の設計になる）📚

---

## 9) “重複配信”が起きる世界なので、IDは超だいじ 🔁🛡️

メッセージングは「少なくとも1回配信（at-least-once）」が多くて、**同じイベントが2回届く**ことがあるよ〜😇
だから購読側は「同じイベントを2回処理しても壊れない（冪等）」が基本ルール！([microservices.io][5])

そのためにも `eventId`（一意ID）をメタ情報として持っておくのが強いよ〜🆔✨
さらに、追跡ID（tracking ID）をイベントに入れて重複検知する、という実務パターンもよく紹介されるよ〜。([Confluent][6])

（このロードマップだと冪等性は後の章でガッツリやるけど、第93章の時点でも “IDは太らせずに守備力を上げる” って覚え方が最高だよ🛡️💛）

---

## 10) 実装テンプレ：TypeScriptで「太らない」イベント型を作る 🧩✨

### ベース型（おすすめ）

```ts
type ISODateTime = string;

type DomainEvent<TType extends string, TData> = Readonly<{
  eventId: string;
  type: TType;
  occurredAt: ISODateTime;

  aggregate: Readonly<{
    name: string;     // "Order" など
    id: string;       // AggregateId
    version?: number; // あれば
  }>;

  data: Readonly<TData>;
}>;
```

### 具体イベント

```ts
type PaymentCompleted = DomainEvent<
  "PaymentCompleted",
  Readonly<{
    paymentId: string;
    amount: number;
    currency: "JPY";
  }>
>;
```

**`Readonly` を強めに使う**と、イベントが“改ざんされない事実”っぽくなって気持ちいいよ〜🧊✨

---

## 11) テスト：イベントが太らないように“見張る”👀🧪

型だけでもかなり守れるけど、最低限これもやると強いよ〜💪

### ✅ 1) シリアライズサイズを雑チェック（太り検知）

```ts
import { test, expect } from "vitest";

test("PaymentCompleted event should be small", () => {
  const ev = {
    eventId: "e-001",
    type: "PaymentCompleted",
    occurredAt: "2026-02-07T00:00:00Z",
    aggregate: { name: "Order", id: "o-001", version: 12 },
    data: { paymentId: "p-999", amount: 1200, currency: "JPY" },
  } satisfies PaymentCompleted;

  const bytes = Buffer.byteLength(JSON.stringify(ev), "utf8");
  expect(bytes).toBeLessThan(800); // 目安：適当に始めてOK👍
});
```

### ✅ 2) dataのキー数を固定（増えたら気づける）

```ts
test("PaymentCompleted.data keys should stay minimal", () => {
  const data = { paymentId: "p-999", amount: 1200, currency: "JPY" };

  expect(Object.keys(data).sort()).toEqual(["amount", "currency", "paymentId"]);
});
```

こういうテストがあると、誰かが「つい便利だから追加😇」しても、すぐ止まるよ〜🚦✨

---

## 12) AIの使い方（第93章向けプロンプト集）🤖💞

コピペして使えるやつ置いとくね〜🧁

### 🧠 イベント項目の棚卸し

* 「このイベントの購読者（利用者）を想定して、**必須情報 / あれば便利 / いらない**に分類して。理由も短く。」

### 🧹 入れすぎ検知

* 「次のイベントpayloadを見て、**密結合・個人情報・派生値・過剰な構造**の観点で危険箇所を指摘して。削った最小案も出して。」

### 🧪 テスト追加

* 「イベントが肥大化しないためのテスト戦略を、TypeScript + Vitestで提案して。サイズ、キー固定、バージョン互換の観点も入れて。」

---

## 章末ミニ演習 🎓✨

### 🧁 お題

`OrderPlaced`（注文作成）イベントを作ってみよう！

### ✅ やること

1. まず“太い版”をわざと作る（Order丸ごと）😇
2. そこから「本当に必要？」って質問しながら削る✂️
3. 最後に「薄い版」にして、テスト（キー固定 or サイズ）を追加🧪✨

---

## 理解チェック（サクッと5問）📝💡

1. イベントに「集約を丸ごと入れる」と何が起きやすい？😵‍💫
2. “事実として残す値”と“派生値”の違いって？📌
3. `eventId` を持つと何が嬉しい？🆔
4. 薄いイベントの弱点は？どうバランス取る？⚖️
5. 「ドメインイベント」と「統合イベント」を分ける理由は？🏠🌍

---

次の第94章では、いよいよ **イベント購読（同期でまず簡単に）🔔** を実装して、「イベントが役に立つ瞬間」を体験していくよ〜🎉✨

[1]: https://www.thoughtworks.com/en-gb/insights/blog/architecture/thin-events-the-lean-muscle-of-event-driven-architecture?utm_source=chatgpt.com "Thin Events: The lean muscle of event-driven architecture"
[2]: https://devblogs.microsoft.com/cesardelatorre/domain-events-vs-integration-events-in-domain-driven-design-and-microservices-architectures/?utm_source=chatgpt.com "Domain Events vs. Integration Events in Domain-Driven ..."
[3]: https://github.com/cloudevents/spec/blob/main/cloudevents/spec.md?utm_source=chatgpt.com "spec/cloudevents/spec.md at main"
[4]: https://cloudevents.github.io/sdk-javascript/interfaces/CloudEventV1.html?utm_source=chatgpt.com "CloudEventV1"
[5]: https://microservices.io/patterns/communication-style/idempotent-consumer.html?utm_source=chatgpt.com "Pattern: Idempotent Consumer"
[6]: https://developer.confluent.io/patterns/event-processing/idempotent-reader/?utm_source=chatgpt.com "Idempotent Reader"
