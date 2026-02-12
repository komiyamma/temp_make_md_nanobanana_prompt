# 第22章：ISP実戦（注文通知まわりを整理）🔔📦

この章は「通知まわり」がごちゃついてくる“あるある地獄”を、**ISP（インターフェース分離）**でスッキリ救出する回だよ〜🧹💖
（※2026/01/09 時点の最新：TypeScript は 5.9 系のリリースノートが公開されているよ📌） ([typescriptlang.org][1])


![Notification Center](./picture/solid_ts_study_022_isp_email_knife.png)

---

## 0. 今日のゴール🎯✨

次の状態を作れるようになるよ😊🌸

* 「通知したいだけ」なのに **巨大な Notifier に依存してる**状態をやめる🙅‍♀️💥
* **必要な機能だけ**を持つ小さな interface に分ける✂️🧩
* テストで「差し替え」が超ラクになる✅🧪
* “通知手段が増えても”注文ロジックが汚れない🌱✨

---

## 1. まずは地獄の例を見てみよ😇🔥（ISP違反の匂い）

通知って増えがちだよね…📲✉️🧾
「メール」「アプリ通知」「店員向け通知」「監査ログ」「Slack」…って増えた結果、こうなりがち👇

```ts
// ❌ でかすぎ Notifier（なんでも屋）
export interface Notifier {
  sendEmail(to: string, subject: string, body: string): Promise<void>;
  sendPush(userId: string, message: string): Promise<void>;
  postSlack(channel: string, message: string): Promise<void>;
  writeAuditLog(message: string): void;
}

// 注文ロジック（高レベル）なのに、通知の詳細に巻き込まれる…
export class PlaceOrderUseCase {
  constructor(private notifier: Notifier) {}

  async execute() {
    // ほんとは「監査ログだけ」使いたい日もあるのに…
    this.notifier.writeAuditLog("order placed");
  }
}
```

### これの何がツラいの？😵‍💫

* `PlaceOrderUseCase` は `sendEmail` も `sendPush` も使ってないのに、**依存させられてる**🌀
* テストでモック作るとき、使わないメソッドまで用意しがち（＝ノイズ増）😇
* 後から `sendLINE()` とか増えたら、関係ないところまで修正が波及💥

ここが ISP の出番だよ✂️✨

> **「使わないメソッドを持たされない」** が超大事😊

---

## 2. ISPの考え方（通知で一番効くやつ）✂️🔔

ISPはざっくり言うと👇

* **呼び出し側（クライアント）ごとに interface を薄くする**🧻✨
* 「注文処理が必要な通知」と「厨房が必要な通知」は違うよね？って分ける🧠
* 依存は **“必要最小限”** にする🪶

---

## 3. 改善方針：通知を「役割」で分ける🧩✨

今回は Campus Café の例でこう分けるよ☕️📦

* ✅ お客さん向け：レシートメール送信 ✉️
* ✅ 厨房向け：調理開始の通知 📣
* ✅ 監査向け：監査ログ 🧾

つまり interface をこう分割👇

* `ReceiptEmailSender`（レシート送信だけ）
* `KitchenNotifier`（厨房通知だけ）
* `AuditLogger`（監査ログだけ）

---

## 4. ISPで“勝てる形”に書き直し✍️✨（完成形）

### 4-1. 小さな interface を作る🧻✂️

```ts
export type Order = {
  id: string;
  customerEmail: string;
  items: Array<{ name: string; price: number }>;
  total: number;
};

export interface ReceiptEmailSender {
  sendReceipt(order: Order): Promise<void>;
}

export interface KitchenNotifier {
  notifyNewOrder(order: Order): Promise<void>;
}

export interface AuditLogger {
  record(eventName: string, payload: unknown): void;
}
```

### 4-2. 注文ユースケースは「必要なものだけ」依存する🪶✨

```ts
export class PlaceOrderUseCase {
  constructor(
    private receiptEmail: ReceiptEmailSender,
    private kitchen: KitchenNotifier,
    private audit: AuditLogger
  ) {}

  async execute(order: Order) {
    // 注文ロジックは注文ロジックに集中できる🧠✨
    this.audit.record("order.placed", { orderId: order.id, total: order.total });

    await this.kitchen.notifyNewOrder(order);
    await this.receiptEmail.sendReceipt(order);

    this.audit.record("order.notified", { orderId: order.id });
  }
}
```

ここが最高ポイント👇😍

* `PlaceOrderUseCase` は **sendSlack() とか知らなくていい**
* 追加通知が増えても、**必要な場所だけ増やせばOK**

---

## 5. 実装例：通知の“中身”は好きに差し替えOK🎭✨

例えば Email は SMTP でも外部APIでも何でもOKだよ〜📮
（ここでは形だけ！）

```ts
export class ConsoleAuditLogger implements AuditLogger {
  record(eventName: string, payload: unknown) {
    console.log(`[AUDIT] ${eventName}`, payload);
  }
}

export class FakeReceiptEmailSender implements ReceiptEmailSender {
  async sendReceipt(order: Order) {
    console.log(`[MAIL] to=${order.customerEmail} total=${order.total}`);
  }
}

export class FakeKitchenNotifier implements KitchenNotifier {
  async notifyNewOrder(order: Order) {
    console.log(`[KITCHEN] new order id=${order.id}`);
  }
}
```

---

## 6. テストが一気にラクになる✅🧪（ISPのご褒美）

Vitest は公式サイトがあり、最近の大きなリリース情報も出てるよ📌 ([vitest.dev][2])
（“テストの話題”として最新動向を押さえたよ、って意味での参照ね😊）

### 6-1. 「必要な分だけ」モックすればOK🎉

```ts
import { describe, it, expect, vi } from "vitest";

describe("PlaceOrderUseCase", () => {
  it("注文時に厨房通知とレシート送信と監査ログを行う", async () => {
    const receiptEmail = { sendReceipt: vi.fn().mockResolvedValue(undefined) };
    const kitchen = { notifyNewOrder: vi.fn().mockResolvedValue(undefined) };
    const audit = { record: vi.fn() };

    const useCase = new PlaceOrderUseCase(receiptEmail, kitchen, audit);

    const order = {
      id: "o-1",
      customerEmail: "a@example.com",
      items: [{ name: "Latte", price: 500 }],
      total: 500,
    };

    await useCase.execute(order);

    expect(audit.record).toHaveBeenCalled();
    expect(kitchen.notifyNewOrder).toHaveBeenCalledWith(order);
    expect(receiptEmail.sendReceipt).toHaveBeenCalledWith(order);
  });
});
```

**でかい Notifier 方式**だと「使わない sendSlack までモック…」みたいになりがちだけど、ISPだとそれが消えるよ🧹✨

---

## 7. “通知手段が増えた”ときの増やし方（壊れない）🧱🌱

例：新しく「アプリ通知」を追加したい📲✨
👉 追加するのは **新しい interface**（または既存の薄い interface を増やす）だけ。

### パターンA：新しい用途なら interface を増やす🧻✨

* `CustomerAppNotifier` を追加して、必要なユースケースだけが依存する

### パターンB：同じ用途なら実装を差し替える🎭✨

* `ReceiptEmailSender` の実装を

  * `SendGridReceiptEmailSender`
  * `SESReceiptEmailSender`
    みたいに差し替えるだけ

「注文ロジック」はほぼ触らない、が理想だよ😊🌸

---

## 8. AI拡張を使うときのコツ🤖✨（うまく使うテンプレ）

### 8-1. “分割案”を出させるプロンプト例🪄

* 「この Notifier インターフェースを、利用側（PlaceOrderUseCase / KitchenUseCase / AuditJob）ごとに ISP に従って分割して。分割理由も添えて」

### 8-2. そのまま採用しないチェック✅

* 「分割後の interface は、**どのクラスがクライアントか**が自然に説明できる？」
* 「分割した結果、**逆に増やしすぎてない？**（用途が同じなのに乱立してない？）」

AIは“案出し担当”、採用判断はあなた担当👩‍💻💖

---

## 9. よくある失敗あるある⚠️😵‍💫

* ❌ 「1メソッドinterface」を無限に作って、逆に迷子🌀
  → ✅ **用途（誰が使うか）**でまとめると安定するよ😊
* ❌ “通知全部”を1つの usecase に押し込む
  → ✅ 注文は注文、通知は通知で責務を分けやすくする（SRPとも仲良し）🤝✨
* ❌ 「汎用通知 interface」に戻ってしまう
  → ✅ それ、だいたい **巨大化の再発**だよ〜😇

---

## 10. ミニ課題（手を動かそう）🧸📝✨

### 課題A：でかい Notifier を分割✂️

1. でかい `Notifier` を `ReceiptEmailSender / KitchenNotifier / AuditLogger` に分割
2. `PlaceOrderUseCase` の依存を差し替える
3. テストのモックが小さくなったか確認✅

### 課題B：通知手段追加📲

* `KitchenNotifier` の実装をもう1個作る（例：`SlackKitchenNotifier` 的な名前）
* でも `PlaceOrderUseCase` は触らずに差し替えだけで動かす🎭✨

### 課題C：設計メモ📝

* 「この interface は誰のため？」を1行で書く

  * 例：`KitchenNotifier` は “厨房向けの新規注文通知が必要なユースケースのため”

---

## 11. まとめ🌸✨

* ISPは **「使わない機能に依存させない」** 原則だよ✂️🧻
* 通知は増えやすいから、最初から **用途別の薄い interface** が超効く🔔✨
* その結果、テストがラク！変更が怖くない！保守が気持ちいい！🎉

---

次の章（第23章）は、ここで分割した “通知の差し替え口” を使って、**DIP（依存性逆転）**の気持ちよさに繋げていくよ〜🙌✨

[1]: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-9.html?utm_source=chatgpt.com "Documentation - TypeScript 5.9"
[2]: https://vitest.dev/?utm_source=chatgpt.com "Vitest | Next Generation testing framework"
[![SOLID: Guidelines for Better Software Development - αlphαrithms](https://tse1.mm.bing.net/th/id/OIP.6mEgfc1uIVPt_gEnJyUGpgHaE8?pid=Api)](https://www.alpharithms.com/solid-guidelines-for-better-software-development-055500/?utm_source=chatgpt.com)

