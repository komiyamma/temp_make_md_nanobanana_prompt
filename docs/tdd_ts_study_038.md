# 第38章：網羅性（exhaustive）で抜け漏れ防止🕳️🚫

![網羅性チェックの土台](./picture/tdd_ts_study_038_no_leak.png)

状態（status）や種類（type）が増えてくると、**switchの分岐追加を忘れてバグる**こと、めっちゃあります🥲💦
そこでこの章は、**「追加漏れ」を“コンパイルで気づける形”にして、事故を減らす**のがゴールだよ〜！🧠🔒

---

## 🎯 目的

* union型（例：`"draft" | "paid" | "cancelled"`）や判別可能Unionで、**分岐漏れをコンパイルエラーで検知**できるようになる🧷✨
* 「テストで守る」と「型で守る」をセットで使い分けられるようになる🧪🛡️
* ESLintのルールも使って、**チームでも漏れにくい運用**にできる👭📏

---

## 📚 学ぶこと（この章のキモ💡）

### 1) `never` を使った “到達しないはず” チェック🧨\n\n![Never Void](./picture/tdd_ts_study_038_never_void.png)

`never` は「ここに来るはずがない」型。
**全部のcaseを書けてたら、最後に残る型は `never` になる** → これを利用して漏れを検出するよ✨

### 2) `switch` の “網羅性” を「型で強制」するパターン✅

* `assertNever(x: never)` を作る
* `switch` のあとに `assertNever(status)` を置く
  → **caseを追加し忘れた瞬間にコンパイルエラー**🔥

### 3) `Record<Union, ...>` で “対応表” を網羅させる📒

UIラベルやメッセージは `switch` より **対応表の方が読みやすい**ことも多いよ〜😊

### 4) ESLintの `switch-exhaustiveness-check` で “人間のミス” を減らす🧹

`@typescript-eslint/switch-exhaustiveness-check` は **union/enumのswitchでcase漏れを指摘**してくれるよ📣
（ただし “defaultがあると指摘しない” 方向なので、運用が大事！） ([typescript-eslint.io][1])

---

## 🧪 手を動かす：ミニ題材「注文ステータス」🍔🧾

### 題材の仕様（テストで固定するよ）🧪✨

注文ステータス `OrderStatus` があって、UI表示ラベルを返す `statusLabel` を作る！

* `"draft"` → `下書き`
* `"submitted"` → `送信済み`
* `"paid"` → `支払い済み`

---

### 1) テストを書く（Red）🔴🧪

`src/status.test.ts`

```ts
import { describe, it, expect } from "vitest";
import { statusLabel, type OrderStatus } from "./status";

describe("statusLabel", () => {
  it("draft は 下書き", () => {
    const s: OrderStatus = "draft";
    expect(statusLabel(s)).toBe("下書き");
  });

  it("submitted は 送信済み", () => {
    const s: OrderStatus = "submitted";
    expect(statusLabel(s)).toBe("送信済み");
  });

  it("paid は 支払い済み", () => {
    const s: OrderStatus = "paid";
    expect(statusLabel(s)).toBe("支払い済み");
  });
});
```

---

### 2) 最小実装（Green）🟢✨

`src/status.ts`

```ts
export type OrderStatus = "draft" | "submitted" | "paid";

export function assertNever(x: never, message = "Unreachable"): never {
  throw new Error(`${message}: ${String(x)}`);
}

export function statusLabel(status: OrderStatus): string {
  switch (status) {
    case "draft":
      return "下書き";
    case "submitted":
      return "送信済み";
    case "paid":
      return "支払い済み";
  }
  // ここが “網羅性のカギ” 🔑✨\n\n![Assert Guard](./picture/tdd_ts_study_038_assert_guard.png)
  return assertNever(status);
}
```

ポイントはここ👇😍

* `switch` の **caseが全部揃ってる**なら、最後の `status` は `never` になって `assertNever(status)` が通る
* **どれか漏れてる**と、`status` が `never` にならなくて **コンパイルエラー**になる🔥

---

### 3) 「状態を追加」して、漏れをコンパイルで検知してみる🧯🚨

ここでわざと仕様追加！✨
`OrderStatus` に `"cancelled"` を足すよ！

```ts
export type OrderStatus = "draft" | "submitted" | "paid" | "cancelled";
```

すると… `statusLabel` の最後の `assertNever(status)` が **コンパイルで怒られる**はず！😳⚡
「cancelled の case ないよ〜」ってことが、テスト実行前にバレるのが最高👏✨\n\n![Compile Alarm](./picture/tdd_ts_study_038_compile_alarm.png)

じゃあ追加👇

```ts
case "cancelled":
  return "キャンセル";
```

---

## ✨ 別解：`Record` 対応表で “必ず全部埋める” 📒🧷\n\n![Record Map](./picture/tdd_ts_study_038_record_map.png)

UIラベルみたいな「対応表」は `switch` よりコレが読みやすいこと多いよ〜😊

```ts
export type OrderStatus = "draft" | "submitted" | "paid";

const LABELS = {
  draft: "下書き",
  submitted: "送信済み",
  paid: "支払い済み",
} satisfies Record<OrderStatus, string>;

export function statusLabel(status: OrderStatus): string {
  return LABELS[status];
}
```

これの良いところ💖

* `OrderStatus` に追加したら、`LABELS` にキーがないと **コンパイルエラー**になる👏
* 「漏れ」が起きにくいし、読みやすい〜📖✨

---

## 🧹 ESLintでさらに漏れを減らす（おすすめ）📣\n\n![ESLint Robot](./picture/tdd_ts_study_038_eslint_robot.png)

`@typescript-eslint/switch-exhaustiveness-check` を有効にすると、**union/enumのswitchでcase漏れを検出**してくれるよ✨ ([typescript-eslint.io][1])

ただし注意点⚠️

* このルールは「defaultが無いswitch」を前提に検出しがち（defaultがあると見逃しやすい）ので、
  **この章の“assertNeverをswitchの後ろに置く”形式**と相性がいいよ😊

---

## ⭐ 発展：`ts-pattern` の `.exhaustive()` で “網羅性” をもっと書きやすく🎨

条件分岐が複雑になってくると、`ts-pattern` のパターンマッチが便利な場面もあるよ〜！
`.exhaustive()` をつけると **網羅できてないとエラー**にできる✨ ([GitHub][2])

（「switchがごちゃごちゃして読みにくい…🥲」って時の選択肢！）\n\n![TS Pattern Machine](./picture/tdd_ts_study_038_ts_pattern_machine.png)

---

## 🤖 AIの使い方（この章向けプロンプト例）💬🤖✨

コピペで使えるよ〜🫶

* 「`OrderStatus` を増やすときに、漏れやすい箇所をリストアップして。`switch` と `Record` の両方で」📝\n\n![AI Test Generation](./picture/tdd_ts_study_038_ai_test_gen.png)
* 「この `switch` を “網羅性チェック付き” に直して（`assertNever` 方式）」🧷
* 「UIラベル、色、ボタン表示可否を status ごとに返したい。`Record` と型で漏れなく書く形にして」🎨🔘
* 「このunionに1つ追加した想定で、壊れる箇所を予測して」🔮✨

---

## ✅ チェック（できたら合格🎉）

* `assertNever` 方式で、**case漏れがコンパイルで検知**できる✅
* `Record<Union, ...>` 方式で、**対応表のキー漏れがコンパイルで検知**できる✅
* 「UIラベルは対応表」「分岐ロジックはswitch」みたいに、**読みやすさで選べる**✅
* ESLintの `switch-exhaustiveness-check` の役割が説明できる✅ ([typescript-eslint.io][1])

---

## 🧁 おまけ：2026年1月時点の“最新”メモ📌

* TypeScript の最新は **5.9系（npmのlatestは 5.9.3）**だよ🧪✨ ([NPM][3])
* さらに先の話として、TypeScriptのネイティブ実装プレビュー（高速化の流れ）も進んでるみたい👀⚡ ([Microsoft Developer][4])

---

次は、ここで作った `OrderStatus` をもう少し育てて、
「statusごとに *次に押せるボタン* を変える」みたいなUI寄り仕様にして、**漏れゼロ設計**を体に染み込ませるのも超おすすめだよ〜😆🧡

[1]: https://typescript-eslint.io/rules/switch-exhaustiveness-check/?utm_source=chatgpt.com "switch-exhaustiveness-check"
[2]: https://github.com/gvergnaud/ts-pattern?utm_source=chatgpt.com "gvergnaud/ts-pattern: 🎨 The exhaustive Pattern Matching ..."
[3]: https://www.npmjs.com/package/typescript?utm_source=chatgpt.com "TypeScript"
[4]: https://developer.microsoft.com/blog/typescript-7-native-preview-in-visual-studio-2026?utm_source=chatgpt.com "TypeScript 7 native preview in Visual Studio 2026"
