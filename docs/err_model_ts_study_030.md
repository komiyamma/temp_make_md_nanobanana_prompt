# 第30章：総合演習（AI込み）ミニプロジェクト🎓🤝🤖💖

題材：**推し活グッズ管理**（予算💰・在庫📦・外部支払いAPI💳）

まず「最新情報メモ」だけ置いておくね📝✨（章の内容はこの後でガッツリ！）

* **TypeScript 5.9** が現行の安定ライン（公式ブログ＆Docsが更新継続） ([Microsoft for Developers][1])
* **Node.js** は **v24 が Active LTS**、v22 は Maintenance LTS（2026-01 の更新あり） ([Node.js][2])
* **Vite** は **7.3.1**（npm上の最新版） ([npmjs.com][3])
* **Problem Details** は **RFC 9457**（RFC 7807 を obsolete） ([RFCエディタ][4])
* catch の `unknown` 化は tsconfig の **useUnknownInCatchVariables** が基本路線🛡️ ([TypeScript][5])

---

## 0. この総合演習のゴール🎯💖

「失敗」を **思いつき対応**じゃなくて、**設計として統一**できるようになること！✨
最終的に、こんな“全部入り”を自分で作れるようにするよ😊

### 成果物チェックリスト✅📦

* 失敗の棚卸し＆分類表📋
* エラーカタログ（code / 表示文言 / 対処）🏷️
* Result型＋ Domain / Infra エラー型🎁
* 例外境界（UI/API）＋ Problem Details 🧾🚪
* requestIdログ＋安全ログ方針🧵🔎🔒
* 失敗ケース中心テスト🧪✨

![総合演習の設計図：エラー設計の全貌を広げる[(./picture/err_model_ts_study_030_blueprint_roll.png)

---

## 1. ミニプロジェクトの仕様（小さくてリアル）🛍️✨

### 1-1. 画面（最低限）🖥️🎀

* グッズ一覧📦（名前・価格・在庫）
* 追加フォーム➕📝
* 購入フォーム💳（商品＋個数）
* エラーの見せ方統一（トースト/フォーム/ダイアログ）🔔🧾

### 1-2. API（最低限）🌐🚪

* `GET /items`
* `POST /items`（追加）
* `POST /purchase`（購入：予算・在庫・支払いAPI）

### 1-3. “必ず起こる失敗”を仕込む😈✨

* 予算オーバー💸
* 在庫不足📉
* 入力ミス（個数0、負の価格、空文字）✍️🙅‍♀️
* 外部支払いAPIが落ちる/遅い/拒否する🌩️⏳🚫

---

## 2. まず最初にやる：失敗の棚卸し＆分類表📋🗺️

ここが総合演習の「核」だよ🧠🔥
コードを書く前に、失敗を先に出し切る！

### 2-1. 失敗を30個出す（AIでブースト🤖⚡）

#### AIプロンプト例🤖📝

* 「推し活グッズ管理で起きる失敗ケースを30個。ユーザー入力、業務ルール、外部API、運用を混ぜて」
* 「それぞれを domain / infra / bug に分類して、理由も1行で」
* 「リトライOK/NGも付けて」

### 2-2. 分類の型（迷ったらこれ）🧭

* **DomainError**：ユーザーや業務ルール的に起こりうる失敗（例：予算超え）🙂
* **InfraError**：外部I/Oの失敗（例：支払いAPIタイムアウト）🌩️
* **Bug**：本来あり得ない（不変条件違反）🧱⚡

---

## 3. エラーカタログ（台帳）を作る🏷️📚✨

「エラー名」じゃなくて、**運用できる形**にするよ😊

### 3-1. カタログの項目（最小セット）📌

* `code`：例 `GDS-001`
* `userMessage`：画面に出す文言（やさしく💗）
* `logMessage`：ログ用の詳細（技術寄り🔧）
* `action`：推奨アクション（再入力/再試行/問い合わせ）
* `retryable`：再試行OK？🔁

#### AIプロンプト例🤖📝

* 「DomainError 8個の code と userMessage を、女子大生向けの優しい文体で統一して」
* 「InfraError 8個の retryable を判定して理由も」

---

## 4. 型設計：Result と “アプリ標準エラー” を作る🎁🧼

ここで「設計が統一」されるよ✨

### 4-1. Result型（判別可能ユニオン）🎁🌈

```ts
export type Ok<T> = { ok: true; value: T };
export type Err<E> = { ok: false; error: E };
export type Result<T, E> = Ok<T> | Err<E>;

export const ok = <T>(value: T): Ok<T> => ({ ok: true, value });
export const err = <E>(error: E): Err<E> => ({ ok: false, error });
```

### 4-2. エラー型（Domain / Infra / Bug）🧱🌩️🙂

ポイントは **判別タグ（kind）** を必ず入れること！🏷️

```ts
export type DomainError =
  | { kind: "domain"; code: "GDS-001"; message: "予算が足りません"; required: number; remaining: number }
  | { kind: "domain"; code: "GDS-002"; message: "在庫が足りません"; itemId: string; requested: number; stock: number }
  | { kind: "domain"; code: "GDS-003"; message: "入力が不正です"; field: string; reason: string };

export type InfraError =
  | { kind: "infra"; code: "GDS-101"; message: "支払いAPIに接続できません"; retryable: true }
  | { kind: "infra"; code: "GDS-102"; message: "支払いAPIがタイムアウトしました"; retryable: true; timeoutMs: number }
  | { kind: "infra"; code: "GDS-103"; message: "支払いが拒否されました"; retryable: false; reason?: string };

export type BugError =
  | { kind: "bug"; code: "GDS-901"; message: "不変条件違反"; detail?: string };

export type AppError = DomainError | InfraError | BugError;
```

---

## 5. unknown を “正規化” する（最後の砦）🛡️🧼

**どんな throw が来ても同じ形にする**のが目的！✨
（tsconfig の `useUnknownInCatchVariables` と相性バツグン🛡️） ([TypeScript][5])

```ts
export function normalizeUnknown(e: unknown): BugError | InfraError {
  if (e instanceof Error) {
    // ここで e.cause や name を見て分類してもOK（必要に応じて拡張）
    return { kind: "infra", code: "GDS-101", message: "支払いAPIに接続できません", retryable: true };
  }
  return { kind: "bug", code: "GDS-901", message: "不変条件違反", detail: "throw された値が Error ではありません" };
}
```

---

## 6. APIの例外境界：Problem Details で返す🧾🚪

**RFC 9457** に沿って `application/problem+json` で統一すると、フロントが機械的に扱えて超ラク！ ([RFCエディタ][4])

### 6-1. Problem Details 変換

```ts
export type ProblemDetails = {
  type: string;
  title: string;
  status: number;
  detail?: string;
  instance?: string;

  // 拡張：RFC的にOK（好きに足していい）
  code?: string;
  retryable?: boolean;
  fieldErrors?: Record<string, string>;
  requestId?: string;
};

export function toProblemDetails(err: AppError, instance: string, requestId: string): ProblemDetails {
  if (err.kind === "domain") {
    return {
      type: `https://example.com/problems/${err.code}`,
      title: "入力または業務ルールのエラー",
      status: 400,
      detail: err.message,
      instance,
      code: err.code,
      requestId,
      ...(err.code === "GDS-003" ? { fieldErrors: { [err.field]: err.reason } } : {}),
    };
  }

  if (err.kind === "infra") {
    return {
      type: `https://example.com/problems/${err.code}`,
      title: "外部サービスのエラー",
      status: err.code === "GDS-103" ? 402 : 503,
      detail: err.message,
      instance,
      code: err.code,
      retryable: err.retryable,
      requestId,
    };
  }

  return {
    type: `https://example.com/problems/${err.code}`,
    title: "予期しないエラー",
    status: 500,
    detail: err.message,
    instance,
    code: err.code,
    requestId,
  };
}
```

---

## 7. requestId を通す（ログが“一本道”になる）🧵🚶‍♀️✨

* API入口で `requestId` 作る
* レスポンスヘッダに `X-Request-Id`
* ログにも必ず入れる

（AIに「requestIdが全ログに入ってるか監査して」って頼むと便利👮‍♀️✨）

---

## 8. レジリエンス：タイムアウト/キャンセル/リトライ⏳🛑🔁

支払いAPIは「落ちる前提」でいこう🌩️✨

### 8-1. タイムアウトつき fetch（AbortController）⏳✂️

```ts
export async function fetchWithTimeout(url: string, timeoutMs: number): Promise<Response> {
  const ac = new AbortController();
  const t = setTimeout(() => ac.abort(), timeoutMs);
  try {
    return await fetch(url, { signal: ac.signal });
  } finally {
    clearTimeout(t);
  }
}
```

### 8-2. リトライ条件（超大事）⚖️

* ✅ リトライOK：タイムアウト、ネットワーク切断（多くは一時的）
* ❌ リトライNG：支払い拒否、入力ミス（やっても無駄）

#### AIプロンプト例🤖📝

* 「この InfraError 一覧のうち、リトライすると地獄になるケースを反例で説明して」😱

---

## 9. テストは“失敗中心”で作る🧪💖

最新の流れとして **Vitest 4** が安定運用ラインだよ（4.0告知あり） ([Vitest][6])

### 9-1. 最低限のテスト構成✅

* Domain：予算超え→ DomainError を返す💸
* Domain：在庫不足→ DomainError 📉
* Infra：支払いタイムアウト→ InfraError ⏳
* API：Problem Details の形が崩れない🧾
* ログ：requestId が付く🧵

#### AIプロンプト例🤖🧪

* 「この purchase の仕様で、落とし穴になりがちな失敗テスト観点を10個」
* 「Vitestで domain の境界値テストを追加して」

---

## 10. 進め方：おすすめ“3コマ”進行🎬💖

### ① 設計コマ（30〜60分）🧠🗺️

* 失敗30個 → 分類 → 重要度
* エラーカタログ10〜20件作る
* UIの表示方針（フォーム/トースト/ダイアログ）を先に決める

### ② 実装コマ（90〜180分）🧰🔥

* Result型 → Domain処理 → 支払い（失敗注入）
* API境界（normalize → Problem Details）
* requestId → ログへ

### ③ テスト＆運用コマ（60〜120分）🧪🔎

* 失敗中心テストを追加
* ログの危険物（個人情報/秘密）混入チェック🔒
* 「問い合わせ時は requestId を聞く」導線にする📞🧵

---

## 11. 最終提出物テンプレ（そのまま使ってOK）📦✨

### 11-1. 失敗棚卸し＆分類表（例）📋

* 失敗：予算超え → domain → GDS-001 → 400 → 再入力
* 失敗：支払いAPIタイムアウト → infra → GDS-102 → 503 → リトライ導線🔁
* 失敗：在庫がマイナスになった → bug → GDS-901 → 500 → 調査

### 11-2. エラーカタログ（例）🏷️

* GDS-001：予算が足りません（購入数を減らしてね💗）
* GDS-102：混み合ってるみたい…少し待って再試行してね⏳🔁
* GDS-901：ごめんね、内部で想定外が起きたよ🙇‍♀️（requestId付きで問い合わせ）

---

## 12. 仕上げ：AIを“相棒”にするコツ🤝🤖✨

AIは **実装スピード**は爆上げできるけど、**設計の最終判断**はあなたが握るのが大事だよ💗

### AIにやらせて強いこと💪

* 失敗ケース列挙（漏れ防止）
* 文言トーン統一（優しい日本語）
* テスト観点の追加
* リトライ反例の発掘😱

### AIに任せない方がいいこと🙅‍♀️

* 「どの失敗を Domain にするか」の最終決定
* エラーコード体系の採用（運用に直結）
* “握りつぶし”の正当化（AIはたまにやる😂）

---

## 13. クリア条件（合格ライン）🎓✅💖

* 例外境界が **1箇所**に集約されてる🚪
* unknown を **正規化**できる🧼
* Domain/Infra/Bug が混ざってない🧭
* UIが Problem Details を読んで機械的に表示を分ける🎀
* requestId が「ログ」と「レスポンス」に必ずいる🧵
* 失敗中心テストが最低5本ある🧪

---

必要なら、この章の内容をそのまま“教材ページ化”できるように、

* エラーカタログの雛形（Markdown）📄
* Problem Details の設計シート🧾
* テスト観点チェックリスト✅
  も一緒に吐き出せるよ😊💖

[1]: https://devblogs.microsoft.com/typescript/announcing-typescript-5-9/?utm_source=chatgpt.com "Announcing TypeScript 5.9"
[2]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
[3]: https://www.npmjs.com/package/vite?activeTab=versions&utm_source=chatgpt.com "vite"
[4]: https://www.rfc-editor.org/rfc/rfc9457.html?utm_source=chatgpt.com "RFC 9457: Problem Details for HTTP APIs"
[5]: https://www.typescriptlang.org/tsconfig/useUnknownInCatchVariables.html?utm_source=chatgpt.com "useUnknownInCatchVariables - TSConfig Option"
[6]: https://vitest.dev/blog/vitest-4?utm_source=chatgpt.com "Vitest 4.0 is out!"
