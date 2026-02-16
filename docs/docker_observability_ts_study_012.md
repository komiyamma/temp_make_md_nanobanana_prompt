# 第12章：秘密情報を守る：マスキングと禁止ルール 🙈🔒

## ① 今日のゴール 🎯

* ログに**出しちゃダメな情報**を言えるようになる🧾❌
* **ヘッダ/ボディを安全にログ化**できる（マスキング）🧤
* 事故が起きにくいように、**「ログの入口」を1つに寄せる**🚪
* “漏れてない”を **コマンドで確認**できる🔎✅

---

## ② 図（1枚）🖼️：ログに出す前に“洗う”🚿

```
(入力) HTTPリクエスト
   ├─ headers: Authorization / Cookie / ...
   ├─ body: password / token / ...
   v
[サニタイズ層]  ←ここが第12章の主役🙈🔒
   ├─ 禁止キーは [REDACTED] or 削除
   ├─ PIIは必要最小限（できれば匿名化）
   v
(出力) 構造化ログ(JSON) 🧱
   v
ログ保存/検索（例：Loki/Grafana）🔍📊
```

---

## ③ まず「ログに出しちゃダメ」を決めよう 🚫🧾

ログって、**開発者だけが見るとは限りません**👀
集約先（ログ基盤）や共有範囲が広がるほど、漏えいリスクは上がります📈

OWASP では「ログに直接記録すべきでないもの」として、たとえば👇を挙げています（**消す/マスク/ハッシュ/暗号化**などを推奨）([OWASP Cheat Sheet Series][1])

* **セッションID**（必要ならハッシュ化）
* **アクセストークン**
* **パスワード**
* **DB接続文字列**
* **暗号鍵などの秘密情報**
* **クレカ等の決済情報**
* **機微な個人情報（PII）** など([OWASP Cheat Sheet Series][1])

### よくある「事故のタネ」💣

* `Authorization: Bearer ...` をそのままログ😇
* `Cookie` / `Set-Cookie` をそのままログ🍪
* `/login` のリクエストボディ（password）を丸ごとログ🔑
* 例外オブジェクトに **内部的に入ってる request/config** がログに混ざる（HTTPクライアント系で起きがち）🧨

---

## ④ 禁止ルールを“短く固定”する 🧷📌

ここはチームの憲法🧑‍⚖️✨ 迷いを減らすために、**短く・強く**いきます。

### ✅ ルール（おすすめ）

1. **Authorization / Cookie / Set-Cookie はログに出さない**（値もキーも基本NG）🙅‍♂️
2. **password / token / secret / apiKey 系はログに出さない**🙈
3. リクエスト/レスポンスの **ボディ丸ごと出力は禁止**（どうしても必要なら“許可リスト方式”）📜
4. 個人情報（email/電話/IPなど）は**最小限**（必要なら匿名化/ハッシュ）🕵️‍♀️
5. 「デバッグのために一時的に増やす」はOK。でも **秘密は絶対に出さない**🔥

---

## ⑤ ハンズオン：マスキング関数を作る 🛠️🧤

今回の作戦は **二重ロック**です🔒🔒

* **(A) 自前のマスキング**：ログに載せる前に “洗う”🚿
* **(B) ロガー側の redaction**：万が一混ざっても “最後に削る”🧯

> Pino には `redact` があり、指定したパスの値を置換（`censor`）したり、キーごと削除（`remove`）できます([app.unpkg.com][2])
> ※「置換」より「削除」の方が、うっかり露出が起きにくくておすすめです🙆‍♂️

---

### 1) `src/observability/mask.ts` を追加 🧤

```ts
// src/observability/mask.ts
export const REDACTED = "[REDACTED]";

// Node/Expressのheadersは小文字キーになりがち
const SENSITIVE_HEADERS = new Set([
  "authorization",
  "cookie",
  "set-cookie",
  "x-api-key",
  "x-auth-token",
]);

// 「このキー名っぽいやつは危険」ルール（雑に広げすぎないのがコツ）
const SENSITIVE_KEY_LIKE = /(pass(word)?|token|secret|api[-_]?key|authorization|cookie)/i;

// headersを安全にする：危険キーは値を潰す（または削除）
export function maskHeaders(
  headers: Record<string, unknown>,
  options: { remove?: boolean } = { remove: true }
): Record<string, unknown> {
  const out: Record<string, unknown> = {};
  for (const [k, v] of Object.entries(headers ?? {})) {
    const key = k.toLowerCase();
    const isSensitive = SENSITIVE_HEADERS.has(key) || SENSITIVE_KEY_LIKE.test(key);

    if (isSensitive) {
      if (!options.remove) out[key] = REDACTED;
      continue; // remove=true ならキーごと消す
    }

    // 値が長すぎるヘッダはログを汚しやすいので、軽く制限（任意）
    if (typeof v === "string" && v.length > 200) {
      out[key] = v.slice(0, 200) + "...";
    } else {
      out[key] = v;
    }
  }
  return out;
}

// bodyを安全にする：基本は「許可リスト方式」が安全
export function pickBodyAllowlist<T extends Record<string, unknown>>(
  body: T,
  allow: string[]
): Record<string, unknown> {
  const out: Record<string, unknown> = {};
  for (const key of allow) {
    if (key in (body ?? {})) out[key] = body[key];
  }
  // allowした中にも危険そうなキーが混ざったら念のため潰す
  for (const [k, v] of Object.entries(out)) {
    if (SENSITIVE_KEY_LIKE.test(k)) out[k] = REDACTED;
    else out[k] = v;
  }
  return out;
}
```

ポイント🧠✨

* **denylist（危険っぽいものを消す）**は漏れがち
* **allowlist（出して良いものだけ出す）**は強い💪
* Cookie/Authorization は **値じゃなくキーごと消す**のが安全寄り🙈

---

### 2) “ログの入口”を1つに寄せる 🚪🧱

「誰かが `console.log(req.headers)` しちゃった…」を防ぐため、**ログはこの関数を通す**作戦です😇

```ts
// src/observability/safeLog.ts
import type { Request } from "express";
import { maskHeaders, pickBodyAllowlist } from "./mask";
import { logger } from "./logger"; // 既存のlogger（第9章のJSONロガー想定）

export function logRequestSafe(req: Request, extra?: Record<string, unknown>) {
  logger.info({
    msg: "access",
    method: req.method,
    path: req.path,
    // クエリはtokenが混ざることがあるので注意（必要ならallowlist化）
    // query: req.query,
    headers: maskHeaders(req.headers as Record<string, unknown>),
    reqId: (req as any).id, // 第10章のreqId想定
    ...extra,
  });
}

export function logLoginAttemptSafe(req: Request) {
  // bodyは「必要最小限」だけ！
  const safeBody = pickBodyAllowlist(req.body ?? {}, ["email"]); // passwordは絶対に入れない
  logger.info({
    msg: "login_attempt",
    reqId: (req as any).id,
    body: safeBody,
    headers: maskHeaders(req.headers as Record<string, unknown>),
  });
}
```

---

### 3) わざと“危険なログ”を出して → 直す 🧨➡️🩹

例：`/login` を作って、最初は失敗例を体験します（この体験、めちゃ大事）😈

```ts
// src/routes/login.ts（例）
import type { Request, Response } from "express";
import { logLoginAttemptSafe } from "../observability/safeLog";

export function postLogin(req: Request, res: Response) {
  // ✅ safe版：emailだけログ
  logLoginAttemptSafe(req);

  // ダミー：本物は認証処理やDBが入る
  const token = "dummy-token-should-never-appear-in-logs";
  res.json({ ok: true, token });
}
```

---

## ⑥ “最後の砦”：Pinoのredact（使ってる人向け）🧯🧱

Pinoを使っているなら、**redactをON**にしておくと安心感が跳ね上がります🆙
`paths` に指定したフィールドを、置換（`censor`）または削除（`remove`）できます([app.unpkg.com][2])

さらに、Pinoの redaction は「passwordやtoken、PIIのような機微データに便利」とも説明されています([Dash0][3])

例（logger初期化で）👇

```ts
// src/observability/logger.ts（例：pino）
import pino from "pino";

export const logger = pino({
  redact: {
    paths: [
      "headers.authorization",
      "headers.cookie",
      "headers.set-cookie",
      "body.password",
      "body.token",
      "*.password",
      "*.token",
    ],
    remove: true, // 置換より安全寄り🙆‍♂️
  },
});
```

---

## ⑦ つまづきポイント（3つ）🪤😵‍💫

1. **「debugだから…」で出しちゃう**
   → デバッグでも秘密はNG🙈（一度出たログは回収が大変…）

2. **“丸ごとログ”が便利すぎる**
   → `req.headers` / `req.body` / `error` を丸ごと投げない💥
   代わりに **safe関数**を通す🚪✨

3. **クエリ文字列にtokenが混ざる**
   → `?token=...` みたいな設計、現実にあります😇
   **queryは原則ログしない**か、allowlist化📜

---

## ⑧ ミニ課題（15分）⏳🧪

1. `/login` に対して、ヘッダに `Authorization: Bearer SECRET123` を付けて叩く🧨
2. `docker compose logs` を見て、**Bearerがログに出てない**ことを確認✅
3. `Cookie: session=SECRET456` でも同様に確認🍪✅

PowerShell例👇（雑チェックだけど強い）🔎

```powershell
docker compose logs api | Select-String -Pattern "Bearer|Authorization|Cookie|SECRET" -CaseSensitive:$false
```

---

## ⑨ AIに投げるプロンプト例（コピペOK）🤖📋

* 「Expressのアクセスログで、**出していい項目のallowlist**を提案して。method/path/status/ms/reqId みたいに最小構成で」🧾
* 「`maskHeaders` の**テストケース**を10個作って。Cookie/Authorization/長いヘッダ/大文字小文字混在も含めて」🧪
* 「既存コードに `console.log(req.headers)` が残ってないか、プロジェクト全体で探す方法を教えて（ripgrep想定）」🔍
* 「Pinoの `redact.paths` を、今のログ構造（このJSON）に合わせて最適化して」🧱

---

## ⑩ まとめ 🌈

* **禁止ルールを決める**（Authorization/Cookie/password/tokenは絶対NG）🙅‍♂️
* **ログに載せる前に洗う**（mask/allowlist）🚿
* **ログの入口を1つに寄せる**（safeLog関数）🚪
* **コマンドで漏えい検査**（grep/Select-String）🔎✅

OWASPも「アクセストークン、パスワード、暗号鍵などはログに直接記録しない」方針を明確にしています([OWASP Cheat Sheet Series][1])
ここまでやれば、ログ漏えい事故の確率がグッと下がります💪🔒✨

---

次の第13章（ログ量と保存）では、ここで作った安全ログを前提にして、**「多すぎて読めない問題」**を倒しにいきましょう😇💽🌀

[1]: https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html "Logging - OWASP Cheat Sheet Series"
[2]: https://app.unpkg.com/%40types/pino%406.3.6/files/index.d.ts "UNPKG"
[3]: https://www.dash0.com/guides/logging-in-node-js-with-pino?utm_source=chatgpt.com "Production-Grade Logging in Node.js with Pino"
