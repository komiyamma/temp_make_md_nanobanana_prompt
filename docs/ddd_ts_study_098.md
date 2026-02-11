# 第98章：ACL入門：外部の都合を内側に入れない🛡️

![ACL入門：外部の都合を内側に入れない](./picture/ddd_ts_study_098_acl_filter.png)

## 今日のゴール🎯💖

* 「外部APIの変更・クセ・雑さ」から、**ドメイン（内側）を守る壁＝ACL**の役割がわかる😌🧱
* **“外部DTO → 変換 → ドメイン”** の流れを、TypeScriptでサクッと実装できるようになる💪🧡
* 将来、外部サービスを乗り換えても「内側が壊れない」設計の感覚が身につく🔁✨

---

## ACLってなに？（超ざっくり）🧠🛡️

ACL（Anti-Corruption Layer / 腐敗防止層）は、

* 外部システムのデータや概念を
* **自分たちのドメインの言葉に“翻訳”して**
* **内側に外部のクセが侵入するのを防ぐ**

ための層だよ〜🥰

「外部の都合（命名、ステータス、例外、仕様の穴）」がそのままドメインに入ると、あとで地獄😵‍💫
ACLはそれを防ぐ“防波堤”🌊🧱

この考え方は、外部サブシステムの影響でアプリ設計が縛られないように、ファサード/アダプター層で翻訳するパターンとして紹介されてるよ📘🛠️ ([Microsoft Learn][1])
（Eric Evans がDDDで説明した、という位置づけも明記されてる🙆‍♀️） ([Microsoft Learn][1])

---

## 2) ありがちな「腐敗」パターン😱💥（ACLがない世界）

![ロジックの腐敗](./picture/ddd_ts_study_098_logic_corruption.png)

たとえば外部決済APIがこんな感じだとするね👇

* ステータスが `OK / NG / PENDING / ERROR_42` みたいに独特
* 金額が `"1200"`（文字列）で返ってくる
* タイムゾーンが謎（UTCなの？ローカルなの？）
* エラーが「メッセージ1本」だけ（機械処理できない）

ここでやりがちなのが…

❌ **ドメインが外部DTOをそのまま受け取る**
❌ **ドメインが外部ステータス文字列を保持する**
❌ **外部のエラーコードにドメインの判断が依存する**

これ、外部が1ミリ変わっただけで内側も崩れる🥲🧨

---

## ACLの“基本セット”🧰✨

ACLはだいたいこの4点セットで作ると安定するよ💞

1. **Gateway（外部呼び出し担当）** 🌉
2. **External DTO（外の形）** 📦
3. **Translator / Mapper（翻訳担当）** 🈂️
4. **ACL Facade（内側が使う窓口）** 🚪

ポイントはただ1つ👇
✅ **内側は「自分たちの言葉」しか知らない**

---

## 例題：決済サービス連携（カフェ注文）☕💳✨

今回は「外部決済サービス」を想定して、支払い結果を受け取るよ！

### ドメイン側で使いたい “自分たちの言葉”🗣️💎

* `PaymentStatus` は `Succeeded / Failed / Pending` だけで十分
* 外部の `OK/NG/WAIT/...` は知らなくていい🙅‍♀️

---

## 実装してみよ〜！🧑‍🍳💻✨（ACLの最小構成）

### 1) ドメインモデル（外部を一切知らない）🛡️

```ts
// src/domain/payment/PaymentStatus.ts
export type PaymentStatus = "Succeeded" | "Failed" | "Pending";

// src/domain/payment/PaymentResult.ts
export type PaymentResult = Readonly<{
  status: PaymentStatus;
  paidAt?: Date;        // 成功なら入る、みたいな設計もOK
  reason?: string;      // 失敗理由（内側の言葉）
}>;
```

---

### 2) “内側が期待する窓口” を interface で決める（Port）🚪✨

```ts
// src/application/ports/PaymentGateway.ts
import type { PaymentResult } from "../../domain/payment/PaymentResult";

export type PayCommand = Readonly<{
  orderId: string;
  amountYen: number;
}>;

export interface PaymentGateway {
  pay(command: PayCommand): Promise<PaymentResult>;
}
```

ここが超大事🧡
✅ アプリ層は「決済できること」だけ知ってればOK
✅ どの会社のAPIか、どういうJSONかは知らない🙆‍♀️

---

### 3) 外部DTO（外の形）📦🌍

（ここは外部の仕様に寄せる。寄せていい。だって“外側”だから😆）

```ts
// src/infrastructure/paymentProvider/externalTypes.ts
export type ExternalPaymentResponse = {
  result: "OK" | "NG" | "PENDING";
  paid_at?: string;           // ISO文字列
  error_code?: string;        // 例: "E42"
  message?: string;           // 例: "card expired"
};
```

---

### 4) 翻訳（Translator / Mapper）🈂️🔁

外のクセはここで吸収するよ〜！🥰

```ts
// src/infrastructure/paymentProvider/translator.ts
import type { ExternalPaymentResponse } from "./externalTypes";
import type { PaymentResult } from "../../domain/payment/PaymentResult";
import type { PaymentStatus } from "../../domain/payment/PaymentStatus";

function toDomainStatus(result: ExternalPaymentResponse["result"]): PaymentStatus {
  switch (result) {
    case "OK":
      return "Succeeded";
    case "NG":
      return "Failed";
    case "PENDING":
      return "Pending";
    default: {
      // 将来外部が増やしても、ここで安全に止められる
      // (never到達チェックにしておくと、型でも守れる)
      const _exhaustive: never = result;
      return _exhaustive;
    }
  }
}

function toDomainReason(r: ExternalPaymentResponse): string | undefined {
  if (r.result !== "NG") return undefined;

  // 外部の error_code を “そのまま” ドメインに持ち込まない！
  // 内側の言葉に丸める✨
  switch (r.error_code) {
    case "E42":
      return "CardExpired";
    case "E13":
      return "InsufficientFunds";
    default:
      return "PaymentRejected";
  }
}

export function translatePaymentResponse(r: ExternalPaymentResponse): PaymentResult {
  const status = toDomainStatus(r.result);
  const paidAt = r.paid_at ? new Date(r.paid_at) : undefined;
  const reason = toDomainReason(r);

  // ドメインが期待する形にする
  return { status, paidAt, reason };
}
```

この translator があるおかげで👇
✅ 外部が `OK` → `SUCCESS` に変えても、直す場所はここだけ💪✨
✅ ドメインの型や言葉は守られる🛡️💕

---

### 5) ACL Facade（内側が使う実装）🚪🧱

```ts
// src/infrastructure/paymentProvider/PaymentGatewayAcl.ts
import type { PaymentGateway, PayCommand } from "../../application/ports/PaymentGateway";
import { translatePaymentResponse } from "./translator";
import type { ExternalPaymentResponse } from "./externalTypes";

async function callExternalApi(_cmd: PayCommand): Promise<ExternalPaymentResponse> {
  // ここは本来fetch/SDKなど。今はダミーでOK✨
  return { result: "OK", paid_at: new Date().toISOString() };
}

export class PaymentGatewayAcl implements PaymentGateway {
  async pay(command: PayCommand) {
    const external = await callExternalApi(command);
    return translatePaymentResponse(external);
  }
}
```

---

## “外部レスポンスが壊れてた” をどうする？🧯😵‍💫

外部って、たまに平気で壊れたJSON返してくる…（あるある）😂
そこで **スキーマバリデーション** をACLに入れると強いよ💪

たとえば Zod は「型推論もできるバリデーション」ライブラリで、2026年1月下旬時点で `4.3.6` が “Latest” として表示されてるよ📌 ([npm][2])

```ts
// src/infrastructure/paymentProvider/schema.ts
import { z } from "zod";

export const ExternalPaymentResponseSchema = z.object({
  result: z.enum(["OK", "NG", "PENDING"]),
  paid_at: z.string().optional(),
  error_code: z.string().optional(),
  message: z.string().optional(),
});
```

```ts
// 呼び出し後に検証してから翻訳する
import { ExternalPaymentResponseSchema } from "./schema";
import { translatePaymentResponse } from "./translator";

const parsed = ExternalPaymentResponseSchema.parse(external);
return translatePaymentResponse(parsed);
```

✅ 壊れた入力は **ACLで止める**
✅ ドメインまで持ち込まない
これがめちゃくちゃ効く〜🛡️✨

---

## テストどうする？🧪💖（翻訳はテストしやすい！）

ACLの翻訳は「純粋関数」になりやすいから、テストが超ラク😆✨

テスト基盤は好みでOKだけど、参考として：

* Jest は “Current version (Stable) が 30.0” として案内されてるよ📌 ([Jest][3])
* Vitest も 4.0 のアナウンスが出てて、4.1 beta 開始の動きもあるよ📌 ([Vitest][4])

ここでは例として Vitest っぽく書くね👇

```ts
// src/infrastructure/paymentProvider/translator.test.ts
import { describe, it, expect } from "vitest";
import { translatePaymentResponse } from "./translator";

describe("translatePaymentResponse", () => {
  it("OK -> Succeeded", () => {
    const r = translatePaymentResponse({ result: "OK", paid_at: "2026-02-07T00:00:00.000Z" });
    expect(r.status).toBe("Succeeded");
    expect(r.paidAt?.toISOString()).toBe("2026-02-07T00:00:00.000Z");
  });

  it("NG -> Failed with reason mapping", () => {
    const r = translatePaymentResponse({ result: "NG", error_code: "E42" });
    expect(r.status).toBe("Failed");
    expect(r.reason).toBe("CardExpired");
  });

  it("PENDING -> Pending", () => {
    const r = translatePaymentResponse({ result: "PENDING" });
    expect(r.status).toBe("Pending");
  });
});
```

---

## ここが“設計のキモ”だよ🧡（超重要）💡

### ✅ 1) ドメインに「外部の言葉」を入れない

* 外部ステータス
* 外部エラーコード
* 外部のDTO型
* 外部SDKの型
  ぜんぶNG🙅‍♀️🧨

### ✅ 2) “翻訳点” を1か所に固定する

外部変更に強くなる最短ルート🚀✨

### ✅ 3) 変換に失敗したらACLで止める

* バリデーション失敗
* 未知ステータス
* 日付が変
  → ドメインに流さず、ACLで安全に扱う🧯🛡️

---

## よくある失敗あるある😂⚠️（回避しよ！）

* 「とりあえず外部DTOをドメインに渡しちゃえ」😇 → **あとで全滅**
* ドメインに `externalErrorCode: string` を生やす → **腐敗ルート確定**
* 翻訳をアプリ層のあちこちでやる → **変換ルールが分裂して事故る**
* “外部のnull/undefined地獄” を内側に持ち込む → **型が信用できなくなる**

---

## AIの使い方（ACLは相性いい！）🤖💞

AIには「外部仕様の要約」「変換表」「境界のレビュー」を頼むとめちゃ便利✨

### 使えるプロンプト例📝

* 「この外部レスポンスを **自分のドメイン用のDTO** に変換する設計案を3つ。内側に外部の言葉を入れない方針で。」
* 「外部ステータスが増えた時に壊れないよう、**exhaustiveチェック**込みの変換関数を書いて。」
* 「このtranslatorのテストケース、抜けてる観点を追加して（異常系中心で）」

---

## 章末ミニチェック✅🌸

あなたのACL、次を満たしてたら勝ち〜🎉✨

* [ ] ドメイン層に外部DTOが1つも出てこない
* [ ] 外部ステータス/コードは translator で “内側の言葉” に変換されてる
* [ ] 変換関数がテストされてる
* [ ] 外部レスポンスのバリデーション（または防御）がACLにある
* [ ] 外部が変わっても「直す場所が1か所」と言える

---

## 理解チェック（ゆるクイズ）🧠🎀

1. ACLがないと、なぜドメインが壊れやすいの？😵‍💫
2. `externalErrorCode` をドメインに持つのが危ない理由は？🧨
3. translator はどの層に置くのが自然？（domain/app/infra）どれ？🤔
4. 外部のステータスが増えたとき、どこを直せば済む形が理想？🔁✨

---

## おまけ：2026/02/07時点の“足場”メモ🧷✨

* TypeScript は 5.9 のリリースノートが公開・更新されてるよ📌 ([typescriptlang.org][5])
* Node.js は v24 が Active LTS、v25 が Current として案内されてるよ📌 ([Node.js][6])

（このへんは「環境の流行り」は変わっても、ACLの価値はずっと変わらないタイプのやつだよ🛡️💕）

---

次の第99章は、ACLも混ぜて「イベント連携の統合演習」になるから、**今回の translator / gateway がそのまま武器になる**よ〜🥳⚔️

[1]: https://learn.microsoft.com/en-us/azure/architecture/patterns/anti-corruption-layer?utm_source=chatgpt.com "Anti-corruption Layer pattern - Azure Architecture Center"
[2]: https://www.npmjs.com/package/zod?utm_source=chatgpt.com "Zod"
[3]: https://jestjs.io/versions?utm_source=chatgpt.com "Jest Versions"
[4]: https://vitest.dev/blog/vitest-4?utm_source=chatgpt.com "Vitest 4.0 is out!"
[5]: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-9.html?utm_source=chatgpt.com "Documentation - TypeScript 5.9"
[6]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
