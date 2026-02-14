# 第16章：エラーカタログ（エラー台帳）を作ろう📚🏷️

## 1) 今日のゴール🎯💖

この章が終わると、こんな状態になれるよ〜！😊

* エラーを **「番号（code）」で管理**できる📛
* 画面表示メッセージ・ログ・対処法が **毎回ブレない**🧭✨
* 「このエラー出たらどう動く？」が **台帳見れば一発**🔎
* 実装が進んでも **エラーが散らからない**🧹🧼

（※2026/01/19時点だと TypeScript の最新安定版は **5.9.3** だよ〜📌）([npmjs.com][1])

---

## 2) エラーカタログってなに？なんで要るの？🤔📚

エラーカタログ（エラー台帳）は、ざっくり言うと👇

> 「このアプリに存在するエラーの一覧表」＋「運用ルール」🗂️✨

![エラーカタログ（エラー台帳）[(./picture/err_model_ts_study_016_catalog_shelf.png)

### よくある地獄🔥😇

* A画面「不明なエラーです」🙃
* B画面「通信に失敗しました」😵
* C画面「Network error」😇
* ログは `console.error(e)` だけで情報スカスカ🫥
* どれが入力ミスで、どれが通信落ちで、どれがバグなのか分からん😱

### 台帳があると天国🌈😊

* **同じ失敗なら同じ表示**に揃う🪞✨
* **codeで検索**できる（ログ・問い合わせ・監視が楽）🔎🧵
* 「ユーザーに言うこと」「開発者が見る情報」が分離できる🔐
* リトライすべきか、問い合わせ誘導か、放置でいいかが決まる🔁📞✅

---

## 3) 台帳に書くべき項目（最小セット）🧩✨

まずはミニマムでOK！💪😊
おすすめはこの8つ👇

1. **code**：一意なエラーID（例：`INFRA_HTTP_TIMEOUT`）🏷️
2. **kind**：分類（domain / infra / bug）🗺️
3. **severity**：軽/中/重（運用の温度感）🌡️
4. **userMessage**：ユーザーに見せる文言💬💗
5. **logMessage**：ログ用（開発者向けの説明）🧾
6. **action**：推奨アクション（再試行/入力修正/問い合わせ 等）🧭
7. **retryable**：リトライ可能？（true/false）🔁
8. **httpStatus**（APIがあるなら）：4xx/5xxなど🚦

さらに余裕が出たら👇も強い💪✨

* `owner`（担当チーム）👩‍💻
* `docs`（詳細ページ/FAQ）📄
* `tags`（search用）🏷️
* `sampleCause`（原因例）🧨

---

## 4) codeの命名ルール（ここが超大事）📛⚖️

ここがゆるいと、台帳がすぐ崩壊するよ〜😱💥
おすすめルール👇（迷ったらコレで！）

### ✅ ルール案（おすすめ）

* 形式：`{KIND}_{CONTEXT}_{DETAIL}`

  * KIND：`DOMAIN` / `INFRA` / `BUG`
  * CONTEXT：`AUTH` `PAYMENT` `HTTP` `DB` `FILE` など
  * DETAIL：`INVALID_INPUT` `TIMEOUT` `NOT_FOUND` など

例👇

* `DOMAIN_AUTH_INVALID_PASSWORD` 🔐
* `INFRA_HTTP_TIMEOUT` 🌐⏳
* `BUG_INVARIANT_BROKEN` 🧱💥

### ✅ “番号”を付けたい派へ（運用強め）

* `INFRA_HTTP_1001_TIMEOUT` みたいにするのもアリ🙆‍♀️
* 大規模・問い合わせ多いなら番号は便利📞✨

---

## 5) 「台帳」と「実装」を二重管理しないコツ🧠🧹

台帳を作っても、**更新されなくなる**のが一番あるある😇
なので、どっちかを “正” にしよう！

### A案：TSを正にする（おすすめ・実装とズレにくい）🧡

* `catalog.ts` が正
* Markdownは生成 or コピペ更新（最初は手動でもOK）

### B案：Markdownを正にする（ドキュメント運用が強い）📘

* `error-catalog.md` が正
* そこからTSを生成（ちょい手間だけど強い）

この章では **A案（TSを正）** でいくね😊✨

---

## 6) TypeScriptで「codeの存在」を型で保証しよう🛡️✨

ここからが気持ちいいところ😆💖
**台帳にないcodeを使おうとするとコンパイルで怒られる**ようにするよ！

```ts
// src/errors/catalog.ts
export const errorCatalog = {
  DOMAIN_AUTH_INVALID_PASSWORD: {
    kind: "domain",
    severity: "low",
    userMessage: "パスワードが違うみたい…もう一度確認してね🔑💦",
    logMessage: "Invalid password provided.",
    action: "ユーザーに再入力を促す",
    retryable: false,
    httpStatus: 401,
  },

  INFRA_HTTP_TIMEOUT: {
    kind: "infra",
    severity: "medium",
    userMessage: "通信がタイムアウトしちゃった…！電波が良いところで再試行してね📶⏳🔁",
    logMessage: "HTTP request timed out.",
    action: "再試行導線を出す（可能なら自動リトライ）",
    retryable: true,
    httpStatus: 504,
  },

  BUG_INVARIANT_BROKEN: {
    kind: "bug",
    severity: "high",
    userMessage: "ごめんね、アプリの内部で問題が起きちゃった…🙏💦",
    logMessage: "Invariant broken: reached impossible state.",
    action: "監視アラート＋調査（requestIdで追跡）",
    retryable: false,
    httpStatus: 500,
  },
} as const;

export type ErrorCode = keyof typeof errorCatalog;
export type ErrorKind = (typeof errorCatalog)[ErrorCode]["kind"];
export type Severity = (typeof errorCatalog)[ErrorCode]["severity"];
```

### ここがポイント💡✨

* `as const` を付けると、型がキュッと固定される🧊
* `ErrorCode` が **台帳のキーのユニオン**になる🎁

---

## 7) AppError（アプリ標準エラー）を作って台帳と接続🔌🎀

「エラーの形」を揃えると、UIもログも超楽になるよ😊🧁

```ts
// src/errors/appError.ts
import { ErrorCode, errorCatalog } from "./catalog";

export type AppError = {
  code: ErrorCode;
  // ユーザーには見せないけど、ログで追うための情報たち🧵🔎
  detail?: string;
  cause?: unknown; // ここに元の例外を持たせる（あとで正規化する想定）🧯
  meta?: Record<string, unknown>;
};

export function createError(code: ErrorCode, opts: Omit<AppError, "code"> = {}): AppError {
  return { code, ...opts };
}

export function toUserMessage(err: AppError): string {
  return errorCatalog[err.code].userMessage;
}

export function toLogPayload(err: AppError) {
  const def = errorCatalog[err.code];
  return {
    code: err.code,
    kind: def.kind,
    severity: def.severity,
    logMessage: def.logMessage,
    detail: err.detail,
    meta: err.meta,
    // causeはそのままログに出さず、必要なら“安全に整形”するのが推奨🔒
  };
}
```

---

## 8) 「原因を失わない」ための設計メモ🧵🎁🧯

JavaScriptには `Error` に **cause** を付けられる仕組みがあるよ〜（エラー連鎖）🧵✨
MDNでも紹介されてる🧾([MDNウェブドキュメント][2])

たとえば「通信失敗」を「アプリの文脈つきエラー」に包むイメージ👇

```ts
try {
  await fetch("https://example.com");
} catch (e) {
  // e を cause として保持しておく🧵
  throw new Error("Failed to fetch user profile", { cause: e as unknown });
}
```

台帳と組み合わせると、

* ユーザー表示：やさしく一定💗
* ログ：causeチェーンで根っこまで追える🔎🧵
  ができて強いよ〜！😊✨

---

## 9) 台帳を育てる運用ルール（軽くでOK）🪴📈

エラーカタログは “作って終わり” じゃなくて、**育てるもの**🌱✨
まずはこの3つだけ守ると続くよ😊

### ルール①：新しい失敗を足すときは「必ず台帳」📌

* codeを作る → 実装で使う → UI/ログで統一✨

### ルール②：userMessageは「行動が書けてる？」🫶

* ❌「エラーが発生しました」
* ✅「通信が不安定みたい。もう一度やってみてね📶🔁」
* ✅「入力に不足があるよ。赤い項目を確認してね📝」

### ルール③：retryableがtrueなら“導線”も用意🔁🚪

* ボタン「再試行」
* 自動リトライ（回数・間隔は控えめ）
* タイムアウトも合わせて設計⏳

---

## 10) ミニ演習📝✨：エラーカタログ10件をMarkdownで作ろう📋💖

まずは “台帳の見た目” を作ってみよ〜！😊
（あとでTSに移してもOK👌）

```md
# Error Catalog 🏷️

| code | kind | severity | userMessage | action | retryable | httpStatus |
|---|---|---|---|---|---:|---:|
| DOMAIN_AUTH_INVALID_PASSWORD | domain | low | パスワードが違うみたい…🔑💦 | 再入力を促す | false | 401 |
| DOMAIN_FORM_REQUIRED | domain | low | 必須項目が未入力だよ📝 | 未入力箇所を案内 | false | 400 |
| DOMAIN_BUDGET_EXCEEDED | domain | medium | 予算オーバーだよ💸 | 予算変更を促す | false | 409 |
| INFRA_HTTP_TIMEOUT | infra | medium | 通信がタイムアウト…📶⏳ | 再試行導線 | true | 504 |
| INFRA_HTTP_OFFLINE | infra | medium | ネットに繋がってないかも📵 | 接続確認＋再試行 | true | 0 |
| INFRA_API_RATE_LIMIT | infra | medium | 混み合ってるみたい…少し待ってね🕒 | 待機＋再試行 | true | 429 |
| INFRA_DB_UNAVAILABLE | infra | high | ただいま利用しづらい状態…🙏 | 復旧待ち＋監視 | true | 503 |
| BUG_INVARIANT_BROKEN | bug | high | 内部で問題が起きちゃった…🙏💦 | 調査＋アラート | false | 500 |
| BUG_UNEXPECTED_THROWN | bug | high | 予期しない問題が起きたよ…😢 | 正規化＋記録 | false | 500 |
| BUG_NOT_IMPLEMENTED | bug | medium | まだ未対応の動作だった…🙇‍♀️ | 実装計画へ | false | 501 |
```

---

## 11) AI活用🤖💖：台帳づくりが爆速になるプロンプト例

コピペで使ってOKだよ〜！✨

* 「この機能で起こりうる失敗を domain/infra/bug に分類して10個出して」🗺️
* 「userMessage を “やさしい日本語” に統一して。責めない・次の行動が分かる感じで」💬💗
* 「retryable=true にすべきものだけ抜き出して、理由も書いて」🔁
* 「この台帳、code命名がブレてないかチェックして」👀✅
* 「重複してそうなcodeや意味かぶりを指摘して」🧹✨

---

## 12) まとめ🎀✨

エラーカタログは、アプリの失敗を **“設計として管理する土台”** だよ📚💖

* codeで統一🏷️
* 表示とログを分ける🔐
* retryや対処を台帳に埋め込む🧭
  これだけで、実装も運用もめちゃ楽になる〜！😊✨

次の章（Result型🎁🌈）に行くと、**「例外を減らして読みやすい失敗制御」**ができるようになるから、ここで作った台帳がさらに活きるよ〜！🚀💖

（ちなみに、HTTP APIの失敗形式を標準化する考え方としては RFC 7807 の “Problem Details” が有名だよ🧾🌐）([IETF Datatracker][3])

[1]: https://www.npmjs.com/package/typescript?utm_source=chatgpt.com "TypeScript"
[2]: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Error/cause?utm_source=chatgpt.com "Error: cause - JavaScript - MDN Web Docs"
[3]: https://datatracker.ietf.org/doc/html/rfc7807?utm_source=chatgpt.com "RFC 7807 - Problem Details for HTTP APIs - Datatracker - IETF"
