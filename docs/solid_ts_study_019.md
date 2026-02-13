# 第19章：LSP実戦（型で守る置換可能性）🧠🛡️

（2026-01-09時点の前提メモ💡：TypeScriptは5.9系が最新として案内されていて、Vitestは4.0が出ています🧪✨　Node.jsは24系がLTS入りしています🚀） ([TypeScript][1])


![LSP Contract](./picture/solid_ts_study_019_lsp_contract.png)

---

## この章のゴール🎯💖

この章が終わるころには…

* 「差し替え可能（置換可能）」って、**実務でどう守るの？** が言えるようになる😊
* TypeScriptの「型」で、**“置換できない実装”を入り口で弾ける**ようになる🧱✨
* さらにテストで、**“型だけじゃ守れない約束”を自動チェック**できるようになる✅🧪

---

## まず大事なこと：LSPは「継承の話」だけじゃないよ😳🧩

TypeScriptは **構造的型付け（形が同じならOK）** だから…

* `implements` してなくても
* `extends` してなくても

**「たまたま同じ形」なら差し替えできちゃう**のね😇
だからこそ、LSPは「継承設計の作法」だけじゃなくて、**“差し替え口（interface）を作る時の契約（約束）”の作法**として超重要になるよ🫶✨

---

## LSPの“実戦”で見るべきポイント👀⚔️

![LSP Violations List](./picture/solid_ts_study_019_lsp_violations_list.png)

差し替えで壊れるのって、だいたいこの4つ😵‍💫

1. **入力の前提（事前条件）を勝手にキツくする**

* 例：インターフェースは「0以上の金額」を想定してたのに、実装Bだけ「100円以上しか無理」みたいにする💥

2. **出力の約束（事後条件）を弱くする**

* 例：成功ならレシートが必ず返るはずなのに、実装Bだけ `null` が返る😇

3. **例外やエラーの出し方が変わる**

* 例：他は `Result` で返すのに、実装Bだけ throw する🔥

4. **副作用が増える（勝手にログ保存・DB更新…）**

* 置換したら挙動が変わって、思わぬお金が飛ぶやつ😱💸

この章は、**1〜3を「型＋テスト」でガッチリ守る**のがメインだよ🧠🛡️

---

## “型で守る”の基本方針はこの3段ロケット🚀🚀🚀

### A) 変な状態を「型で作れない」ようにする🧱✨

代表例：金額はマイナス禁止、空文字禁止、などなど🙅‍♀️

### B) 失敗は `throw` じゃなく「返り値」で表現する🎁

`Result`（成功/失敗のユニオン）にして、**差し替えても制御フローが揺れない**ようにする✨

### C) “契約”は「共通テスト」で固定する🧪🔒

型がOKでも、**意味がズレる**ことはあるからね🥲
→ そこで「どの実装でも同じテストを通る」を作るよ✅

---

## 実戦題材：Campus Café の「支払い方法」☕️💳✨

「支払い方法（現金/クレカ/PayPay…）」って増えがちで、差し替えが起きがちで、LSPの練習に最高〜！🎯💕

ここから、**“差し替え口（interface）”を作って、型とテストで置換可能性を守る**よ🧩🛡️

---

# 1) まずは「金額」を型で守ろう💰🔐

![Money Brand](./picture/solid_ts_study_019_money_brand.png)

「numberでいいじゃん」と思うけど、numberは何でも入るから事故が起きる😇
なので **ブランド型（branded type）** で “ただのnumber” と区別しよ〜🪄✨

```ts
// Money は「円（0以上の整数）」だけを表す型にするよ💰
type Money = number & { readonly __brand: "Money" };

type MoneyError =
  | { type: "Negative"; value: number }
  | { type: "NotInteger"; value: number }
  | { type: "NaN"; value: number };

function createMoney(value: number): { ok: true; value: Money } | { ok: false; error: MoneyError } {
  if (Number.isNaN(value)) return { ok: false, error: { type: "NaN", value } };
  if (!Number.isInteger(value)) return { ok: false, error: { type: "NotInteger", value } };
  if (value < 0) return { ok: false, error: { type: "Negative", value } };
  return { ok: true, value: value as Money };
}
```

これで何が嬉しいかというと…👇

* `Money` を受け取る関数は、**「0以上の整数」だと信じていい**😊
* そのかわり `createMoney` で作る時に、入口で弾く✅

つまり **「前提条件」を型に寄せる**ってことだよ🧠✨

---

# 2) 失敗は `Result` で返す（throwしない）🎁🧯

![Result Type Gift](./picture/solid_ts_study_019_result_type_gift.png)

支払いって失敗するよね？（残高不足とか）😢
それを `throw` にすると、実装ごとにバラついて地獄になりがち🔥

なので Result を作るよ〜💕

```ts
type Ok<T> = { ok: true; value: T };
type Err<E> = { ok: false; error: E };
type Result<T, E> = Ok<T> | Err<E>;

function ok<T>(value: T): Ok<T> {
  return { ok: true, value };
}
function err<E>(error: E): Err<E> {
  return { ok: false, error };
}
```

---

# 3) 差し替え口（interface）を「契約」として設計する🧩📜

![Interface Contract Scroll](./picture/solid_ts_study_019_interface_contract_scroll.png)

今回の契約はこんな感じにするよ👇
（ポイントは **“どの実装でも守れる” ちょうどよい約束** にすること！）

```ts
type PaymentError =
  | { type: "Unsupported"; reason: string }
  | { type: "Declined"; reason: string }
  | { type: "TemporaryFailure"; reason: string };

type PaymentReceipt = {
  methodId: string;
  paid: Money;
  message: string;
};

type PaymentRequest = {
  total: Money;
};

interface PaymentMethod {
  readonly id: string;

  // これは「できる/できない」を判定するだけ（副作用なし）✨
  canHandle(req: PaymentRequest): boolean;

  // 失敗は Result で返す（throwしない）🧯
  pay(req: PaymentRequest): Promise<Result<PaymentReceipt, PaymentError>>;
}
```

ここでLSP的に超大事な“契約の文章化”をしておくと強いよ📝✨
（コメントでもREADMEでもOK）

* `canHandle` は **判定だけ**（支払い処理しない）
* `pay` は **絶対にthrowしない**（全部Resultで返す）
* 成功したら receipt の `paid` は **必ず req.total と一致**（今回は簡単に一致に統一！）

> この「成功条件」を揃えるのが、置換可能性のコアだよ🧠🛡️

---

# 4) 実装を2つ作る（現金・カード）💴💳✨

## 現金（いつでもOK）💴

```ts
class CashPayment implements PaymentMethod {
  readonly id = "cash";

  canHandle(_req: PaymentRequest): boolean {
    return true;
  }

  async pay(req: PaymentRequest): Promise<Result<PaymentReceipt, PaymentError>> {
    // 現金は今回は「必ず成功」とする（例として簡単に😊）
    return ok({
      methodId: this.id,
      paid: req.total,
      message: "現金でお支払いしました💴✨",
    });
  }
}
```

## カード（例：上限あり・通信失敗あり）💳📡

```ts
class CardPayment implements PaymentMethod {
  readonly id = "card";

  canHandle(req: PaymentRequest): boolean {
    // 例：カードは 100万円未満まで…みたいな上限ルール（仮）
    return req.total < (1_000_000 as Money);
  }

  async pay(req: PaymentRequest): Promise<Result<PaymentReceipt, PaymentError>> {
    if (!this.canHandle(req)) {
      return err({ type: "Unsupported", reason: "カード上限を超えています💦" });
    }

    // 例：たまに通信失敗する想定（仮）
    const dice = Math.random();
    if (dice < 0.05) {
      return err({ type: "TemporaryFailure", reason: "通信が不安定です📡💦 もう一度試してね" });
    }

    return ok({
      methodId: this.id,
      paid: req.total,
      message: "カードでお支払いしました💳✨",
    });
  }
}
```

### ここがLSP的にえらい👏✨

* 上限超えを **throw** じゃなく **Unsupportedとして返す**
* `canHandle` と `pay` の整合がある（できないならUnsupported）
* 成功時の `paid` のルールが揃ってる（現金でもカードでも同じ）

---

# 5) 「LSP違反」をわざと作ってみよう😈💥

![Bad Implementation Trap](./picture/solid_ts_study_019_bad_implementation_trap.png)

やりがちな事故：**実装だけ勝手に throw しちゃう**やつ🔥

```ts
class BadCardPayment implements PaymentMethod {
  readonly id = "bad-card";

  canHandle(_req: PaymentRequest): boolean {
    return true; // なんでもOKと言っておいて…
  }

  async pay(req: PaymentRequest) {
    // ここで throw しちゃう😇（呼び出し側が崩壊する）
    if (req.total > (10_000 as Money)) {
      throw new Error("限度額オーバー！");
    }
    return ok({ methodId: this.id, paid: req.total, message: "OK" });
  }
}
```

これ、呼び出し側が `Result` 前提で書いてると即死するよね🥲
**「差し替えた瞬間に例外が飛ぶ」＝ 置換できてない**ってこと💣

---

# 6) 共通テストで「契約」を固定する🧪🔒✨（ここが本番）

![Universal Tester](./picture/solid_ts_study_019_universal_tester.png)

ここからが第19章のメインディッシュ🍰✨
**“どの実装でも同じテストが通る”** を作って、置換可能性を守るよ！

Vitestは4.0が出てて、いまのTS案件でも採用増えてるよ〜🧪✨ ([Vitest][2])

## テスト用の「実装リスト」を用意する📦

```ts
const methods: PaymentMethod[] = [
  new CashPayment(),
  new CardPayment(),
  // new BadCardPayment(), // ← 入れるとテストで落ちて気持ちいい😈💥
];
```

## “契約テスト” を書く（全実装に対して同じテスト）🧪✨

```ts
import { describe, test, expect } from "vitest";

function mustNotThrow<T>(fn: () => Promise<T>): Promise<{ ok: true; value: T } | { ok: false; error: unknown }> {
  return fn()
    .then((value) => ({ ok: true as const, value }))
    .catch((error) => ({ ok: false as const, error }));
}

describe("PaymentMethod contract tests 🧪✨", () => {
  test("全実装: pay は throw しない（Resultで返す）🔥→🧯", async () => {
    const m = createMoney(500);
    if (!m.ok) throw new Error("test setup failed");

    for (const method of methods) {
      const outcome = await mustNotThrow(() => method.pay({ total: m.value }));
      expect(outcome.ok).toBe(true);
    }
  });

  test("全実装: canHandle=false なら Unsupported を返す（契約）🧩", async () => {
    const big = createMoney(2_000_000);
    if (!big.ok) throw new Error("test setup failed");

    for (const method of methods) {
      const req = { total: big.value };
      if (method.canHandle(req)) continue;

      const res = await method.pay(req);
      expect(res.ok).toBe(false);
      if (!res.ok) {
        expect(res.error.type).toBe("Unsupported");
      }
    }
  });

  test("全実装: 成功したら paid は total と一致する💰✅", async () => {
    const m = createMoney(1200);
    if (!m.ok) throw new Error("test setup failed");

    for (const method of methods) {
      const req = { total: m.value };

      if (!method.canHandle(req)) continue;

      const res = await method.pay(req);
      if (res.ok) {
        expect(res.value.paid).toBe(req.total);
        expect(res.value.methodId).toBe(method.id);
      }
    }
  });
});
```

### これで何が守れるの？😍

* **throwしない**（差し替えても呼び出し側が壊れない）
* `canHandle` と `pay` の整合がズレたら落ちる
* 成功時の意味（paidのルール）を共通化できる

→ **置換可能性が“テストで保証”される**のが最高なんだよね🧠🛡️🧪✨

---

# 7) TypeScriptの小ワザ：`satisfies` で “形はOK” を安全に確認🧷✨

![Satisfies Check](./picture/solid_ts_study_019_satisfies_check.png)

たとえば実装を class じゃなくオブジェクトで用意したい時、
`as PaymentMethod` でゴリ押しすると危ない😇

そんな時は `satisfies` が便利だよ💡（TS 4.9で入ったやつ！） ([TypeScript][3])

```ts
const paypay = {
  id: "paypay",
  canHandle: (req: PaymentRequest) => req.total < (300_000 as Money),
  pay: async (req: PaymentRequest) => ok({ methodId: "paypay", paid: req.total, message: "PayPay✨" }),
} satisfies PaymentMethod;
```

`satisfies` は

* 「PaymentMethodを満たしてるか」チェックしつつ✅
* 変数自体の型推論は潰さない（余計に widen しない）✨

って感じで、**契約チェックにちょうどいい**んだ〜😊

---

# 8) よくある「置換できない」設計の匂いチェック👃💥

次のどれかが見えたら、LSP赤信号〜🚨

* `canHandle` が true なのに、`pay` で Unsupported を返す（整合崩れ）😵
* ある実装だけ `pay` が throw する🔥
* ある実装だけ成功時に `paid` の意味が違う（手数料込み/別…）💸
* ある実装だけ「ログ保存」や「DB更新」を勝手にやる🧨

---

# 9) ミニ課題（やってみよ〜！）🎓✨

## 課題A：PayPayPayment を追加しよう📱✨

* `canHandle`：30万円未満だけOK
* `pay`：たまに `TemporaryFailure` を返す（throw禁止）🧯

## 課題B：契約テストを1本追加しよう🧪

例：

* 成功時 `message` は空文字禁止（NonEmptyString型にしてもOK！）📝✨

---

# 10) AI活用（うまい使い方だけ置いとくね🤖💡）

Copilot / Codex系に投げるなら、こんな感じが強いよ〜💪✨

* 「`PaymentMethod` の contract tests を vitest で書いて。条件：payはthrowしない、成功時paidはtotalと一致」
* 「LSP違反になりやすいケースをこの設計で3つ挙げて、テスト追加案も出して」

でも！最後は必ず👀✨

* **契約（成功条件・失敗条件）が文章として筋が通ってるか**
  を人間がチェックしてね🫶（AIは“それっぽい嘘”も混ぜるから🥲）

---

## まとめ🌸✨

この章でやったことはコレだよ🎁

* LSPは「差し替えた瞬間に壊れない」こと🧩
* TypeScriptでは **interfaceが差し替え口**になるから、契約設計が命📜
* **型（Money/Result/satisfies）**で置換可能性を強くする🧠🛡️
* 最後は **共通テスト（契約テスト）**で“意味”を固定する🧪🔒

次の章（ISP）に行くと、「差し替え口がデカすぎて置換できない」問題をスパッと切れるようになるよ✂️😊✨

[1]: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-9.html?utm_source=chatgpt.com "Documentation - TypeScript 5.9"
[2]: https://vitest.dev/blog/vitest-4?utm_source=chatgpt.com "Vitest 4.0 is out!"
[3]: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-4-9.html?utm_source=chatgpt.com "Documentation - TypeScript 4.9"
