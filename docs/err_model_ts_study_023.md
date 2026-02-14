# 第23章：外部APIエラーの正規化（相手はバラバラ）🌩️🧼

外部APIって、**失敗のしかたが本当にバラバラ**なんだよね…🥲

* A社は `{"error": {...}}`
* B社は `{ "message": "..." }`
* SDKは「謎の例外」を投げる
* `fetch` は **404でもPromiseがrejectされない**（えっ！？）😱 ([MDN Web Docs][1])

この章では、そのバラバラをぜ〜んぶ **アプリ内の“同じ形”**にそろえる（＝正規化）方法を作るよ🧼✨

---

## この章のゴール🎯💖

最後にこうなるのがゴールだよ👇

* 外部APIの失敗を **InfraError（インフラ系エラー）** にまとめる🧺
* **リトライできる？できない？** を機械的に判断できる🔁
* ログやユーザー表示が **ブレない**（運用がラク）🧾✨
* 外部API特有の事情を、ドメイン側に漏らさない（設計がきれい）🧼🧠

---

## まず“正規化”ってなに？🧠🫧

正規化は一言でいうと…

![アダプタープラグ：バラバラなコンセントを統一規格に変換[(./picture/err_model_ts_study_023_adapter_plug.png)

> **外部APIの失敗（形も意味もバラバラ）を、アプリ標準の失敗フォーマットに変換すること**🧼✨

### 正規化しないと起きる事故あるある💥🙅‍♀️

* 画面A：`status === 401` を見てる
* 画面B：`error.code === "AUTH"` を見てる
* 画面C：`message.includes("token")` で判定してる（地雷）💣
  → 仕様変更で全部死ぬ☺️🔪

---

## “外部API境界”を1か所に集めよう🚪🧱

外部APIまわりは、**ここだけで完結**させるのがコツだよ👇

* `ExternalApiClient`（外部呼び出し）
* `normalizeExternalApiError`（正規化）
* 返り値は `Result`（成功/失敗が型で分かる🎁）

---

## 先に「正規化後のエラー型」を決める🧱✨

ここがブレると全部ブレるので、まず **標準のInfraError** を作るよ💪🥰

```ts
// 章の主役：外部API向けの正規化エラー
export type InfraError =
  | {
      kind: "infra";
      code:
        | "EXTERNAL_TIMEOUT"
        | "EXTERNAL_NETWORK"
        | "EXTERNAL_RATE_LIMIT"
        | "EXTERNAL_UNAVAILABLE"
        | "EXTERNAL_UNAUTHORIZED"
        | "EXTERNAL_FORBIDDEN"
        | "EXTERNAL_BAD_RESPONSE"
        | "EXTERNAL_UNKNOWN";
      provider: string;        // 例: "FakePay"
      operation: string;       // 例: "CreatePayment"
      userMessage: string;     // ユーザーに見せてもOKな文言
      canRetry: boolean;       // 機械的に使える
      retryAfterMs?: number;   // RateLimit / 503等で使う
      httpStatus?: number;     // 分かるなら
      providerCode?: string;   // 分かるなら（外部API固有）
      detail?: string;         // ログ向け（個人情報は入れない）
      cause?: unknown;         // 元エラー（チェーン用）
    };

export type Result<T, E> =
  | { ok: true; value: T }
  | { ok: false; error: E };

export const Ok = <T>(value: T): Result<T, never> => ({ ok: true, value });
export const Err = <E>(error: E): Result<never, E> => ({ ok: false, error });
```

### ここが“2026っぽい”ポイント💡

* `cause` を持てると「元エラー」を失わないよ🎁（Error.cause の流れ） ([MDN Web Docs][2])

---

## 失敗の入力を“2種類”に分けるのがコツ🧠✌️

外部APIの失敗は大きく2つ：

1. **通信や実行が失敗して例外になる**（ネットワーク/タイムアウト/SDK例外）🌩️
2. **HTTP応答は返ったけど失敗ステータス**（401/429/503/500…）🚦

`fetch` は特にここが大事で、**404/500でもPromiseがresolve**するよ！😳 ([MDN Web Docs][1])

なので、正規化関数の入力もこう分けちゃう👇

```ts
export type ExternalFailure =
  | { kind: "thrown"; error: unknown }
  | {
      kind: "http";
      status: number;
      statusText: string;
      headers: Headers;
      bodyText: string; // JSONとは限らないのでまず文字列で持つ
    };

export type ExternalContext = {
  provider: string;
  operation: string;
};
```

---

## Retry-After を読めると“強い”🔁⏳

レート制限（429）や一時停止（503）で、サーバーが `Retry-After` を返すことがあるよ🧾
これは「どれくらい待って再試行してね」を表すヘッダーだよ⏳ ([IETF Datatracker][3])

```ts
function parseRetryAfterMs(headers: Headers): number | undefined {
  const v = headers.get("retry-after");
  if (!v) return undefined;

  // 1) 秒数形式: "120"
  const asSeconds = Number(v);
  if (Number.isFinite(asSeconds)) return Math.max(0, asSeconds) * 1000;

  // 2) HTTP-date形式: "Wed, 21 Oct 2015 07:28:00 GMT"
  const asDate = Date.parse(v);
  if (!Number.isNaN(asDate)) return Math.max(0, asDate - Date.now());

  return undefined;
}
```

---

## 正規化関数：normalizeExternalApiError 🧼🧠

ここが本章のメインだよ〜！✨
**「入力（thrown/http）」→「InfraError」**へ変換するだけの、なるべく純粋な関数にするのがコツ🧼

```ts
function safeJsonParse(text: string): unknown {
  try {
    return JSON.parse(text);
  } catch {
    return undefined;
  }
}

function pickProviderCode(maybeJson: unknown): string | undefined {
  // 例: { error: { code: "RATE_LIMIT" } } や { code: "..." } などを雑に拾う
  if (!maybeJson || typeof maybeJson !== "object") return undefined;
  const o = maybeJson as Record<string, unknown>;

  const code1 = o["code"];
  if (typeof code1 === "string") return code1;

  const err = o["error"];
  if (err && typeof err === "object") {
    const e = err as Record<string, unknown>;
    const code2 = e["code"];
    if (typeof code2 === "string") return code2;
  }
  return undefined;
}

export function normalizeExternalApiError(
  ctx: ExternalContext,
  failure: ExternalFailure
): InfraError {
  // 1) HTTP応答が返った系（401/429/503/5xx…）
  if (failure.kind === "http") {
    const json = safeJsonParse(failure.bodyText);
    const providerCode = pickProviderCode(json);
    const retryAfterMs = parseRetryAfterMs(failure.headers);

    // よく使うものから先に判定するのが実戦的✨
    if (failure.status === 401) {
      return {
        kind: "infra",
        code: "EXTERNAL_UNAUTHORIZED",
        provider: ctx.provider,
        operation: ctx.operation,
        httpStatus: failure.status,
        providerCode,
        userMessage: "認証に失敗しました。少し時間を置いてからもう一度お試しください🙏",
        canRetry: true,
        retryAfterMs,
        detail: `status=${failure.status} ${failure.statusText}`,
      };
    }

    if (failure.status === 403) {
      return {
        kind: "infra",
        code: "EXTERNAL_FORBIDDEN",
        provider: ctx.provider,
        operation: ctx.operation,
        httpStatus: failure.status,
        providerCode,
        userMessage: "権限が足りないみたい…！管理者に連絡してね🙏",
        canRetry: false,
        detail: `status=${failure.status} ${failure.statusText}`,
      };
    }

    if (failure.status === 429) {
      return {
        kind: "infra",
        code: "EXTERNAL_RATE_LIMIT",
        provider: ctx.provider,
        operation: ctx.operation,
        httpStatus: failure.status,
        providerCode,
        userMessage: "アクセスが集中してるよ🥺 少し待ってから再試行してね⏳",
        canRetry: true,
        retryAfterMs: retryAfterMs ?? 10_000, // 無ければ控えめに既定
        detail: `status=429 retryAfterMs=${retryAfterMs ?? "n/a"}`,
      };
    }

    if (failure.status === 503) {
      return {
        kind: "infra",
        code: "EXTERNAL_UNAVAILABLE",
        provider: ctx.provider,
        operation: ctx.operation,
        httpStatus: failure.status,
        providerCode,
        userMessage: "ただいま混み合っています🥺 少し待ってから再試行してね⏳",
        canRetry: true,
        retryAfterMs,
        detail: `status=503 retryAfterMs=${retryAfterMs ?? "n/a"}`,
      };
    }

    // 5xx は一時障害の可能性が高いので “基本リトライ寄り”
    if (failure.status >= 500) {
      return {
        kind: "infra",
        code: "EXTERNAL_UNAVAILABLE",
        provider: ctx.provider,
        operation: ctx.operation,
        httpStatus: failure.status,
        providerCode,
        userMessage: "外部サービス側で問題が起きてるみたい🥲 少し待って再試行してね🔁",
        canRetry: true,
        retryAfterMs,
        detail: `status=${failure.status} ${failure.statusText}`,
      };
    }

    // 4xxその他：相手の仕様 or こちらの送信内容が原因のことが多い
    return {
      kind: "infra",
      code: "EXTERNAL_BAD_RESPONSE",
      provider: ctx.provider,
      operation: ctx.operation,
      httpStatus: failure.status,
      providerCode,
      userMessage: "外部サービスとのやり取りで問題が起きました🥲 サポートに連絡してね🙏",
      canRetry: false,
      detail: `status=${failure.status} body=${failure.bodyText.slice(0, 200)}`,
    };
  }

  // 2) 例外で落ちた系（ネットワーク/タイムアウト/SDK例外）
  const e = failure.error;

  // AbortController系（タイムアウト/キャンセル）はAbortErrorになりがち🛑
  // AbortController / AbortSignal は fetch の中止にも使えるよ :contentReference[oaicite:4]{index=4}
  if (e && typeof e === "object" && "name" in e && (e as any).name === "AbortError") {
    return {
      kind: "infra",
      code: "EXTERNAL_TIMEOUT",
      provider: ctx.provider,
      operation: ctx.operation,
      userMessage: "通信がタイムアウトしちゃった🥺 電波の良いところで再試行してね📶",
      canRetry: true,
      detail: "AbortError",
      cause: e,
    };
  }

  // それ以外は “ネットワーク系 or 不明”
  return {
    kind: "infra",
    code: "EXTERNAL_NETWORK",
    provider: ctx.provider,
    operation: ctx.operation,
    userMessage: "通信に失敗しちゃった🥲 少し待ってから再試行してね🔁",
    canRetry: true,
    detail: "thrown",
    cause: e,
  };
}
```

補足メモ📝

* `Retry-After` の意味（待ち時間の指示）は HTTP仕様にあるよ⏳ ([IETF Datatracker][3])
* `AbortSignal.timeout()` は比較的新しめだけど、タイムアウト実装がスッキリするよ⏱️ ([MDN Web Docs][4])

---

## fetch 版：外部API呼び出しを Result で返す🎁🌐

ここでは **「HTTP失敗でも例外にならない」** fetch の性質を踏まえて、失敗を `ExternalFailure` に変換してから正規化するよ🧼 ([MDN Web Docs][1])

（Nodeでも `fetch` が使えるのは、Node v18+ の流れ＆ undici由来だよ🧠） ([Node.js][5])

```ts
export async function callExternalJson<T>(
  ctx: ExternalContext,
  input: { url: string; method: "GET" | "POST"; body?: unknown; timeoutMs: number }
): Promise<Result<T, InfraError>> {
  try {
    const res = await fetch(input.url, {
      method: input.method,
      headers: { "content-type": "application/json" },
      body: input.body ? JSON.stringify(input.body) : undefined,
      signal: AbortSignal.timeout(input.timeoutMs),
    });

    const bodyText = await res.text();

    if (!res.ok) {
      const failure: ExternalFailure = {
        kind: "http",
        status: res.status,
        statusText: res.statusText,
        headers: res.headers,
        bodyText,
      };
      return Err(normalizeExternalApiError(ctx, failure));
    }

    // 成功でも JSONじゃない事故があるので try で守る
    try {
      const data = JSON.parse(bodyText) as T;
      return Ok(data);
    } catch (e) {
      return Err(
        normalizeExternalApiError(ctx, {
          kind: "thrown",
          error: new Error("Invalid JSON from external API", { cause: e }),
        })
      );
    }
  } catch (e) {
    return Err(normalizeExternalApiError(ctx, { kind: "thrown", error: e }));
  }
}
```

---

## axios 版：エラーの形が“独自”なので吸収する🧽📦

axios は **エラーオブジェクトの構造**（message/name/config/code…など）が決まってるので、それを境界で吸収するのが◎だよ🧼 ([Axios][6])

（この章では「axiosかどうかの判定」より、まず“境界で形を吸収する”感覚を優先するね🙂）

---

## ミニ演習📝✨：正規化マップを作ってみよう🗺️🏷️

題材：架空の外部API「FakePay」💳🌟

### FakePayの失敗例（想定）

1. 429 で `Retry-After: 30` が返る
2. 503 でボディがプレーンテキスト `"maintenance"`
3. 400 で JSON `{ "error": { "code": "INVALID_REQUEST", "message": "..." } }`
4. ネットワーク断で例外

✅やること

* 上の4つを `ExternalFailure` に落として
* `normalizeExternalApiError` が **期待どおりのcode/canRetry/retryAfterMs** を返すか確認しよう💪😊

---

## AI活用🤖💖（この章で“めちゃ効く”使い方）

### 1) 変換ルールの抜け漏れチェック✅

* 「外部APIが返しがちなエラー（429/503/401/5xx/timeout/network/invalid json）を列挙して、正規化ルールの穴を指摘して」

### 2) “相手のエラー形式”から正規化マップ生成🗺️

* 「このAPIドキュメント（貼り付け）を読んで、`providerCode`→`EXTERNAL_*` の対応表を作って」

### 3) テスト観点づくり🧪

* 「この正規化関数のテストケースを表形式で20個出して（入力→期待出力）」

---

## できたかチェック✅🎀

* [ ] `fetch` の「HTTPエラーでもresolve」問題を吸収できた？ ([MDN Web Docs][1])
* [ ] 429/503 の `Retry-After` を読める？ ([IETF Datatracker][3])
* [ ] “外部API固有”の情報がドメイン側に漏れてない？🧼
* [ ] ユーザー文言（userMessage）とログ向け（detail）が分離できてる？🔒

---

## 次章につながるよ📚✨

この章で「外部APIの失敗をInfraErrorへ正規化」できたから、次は **“サーバ側の例外境界”**で最終的に受け止めて、レスポンスへ変換していけるよ🧱🚪

続き（第24章）に進める準備、ばっちりだね〜！🥳🎉

[1]: https://developer.mozilla.org/en-US/docs/Web/API/Window/fetch?utm_source=chatgpt.com "Window: fetch() method - Web APIs - MDN Web Docs"
[2]: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Error/cause?utm_source=chatgpt.com "Error: cause - JavaScript - MDN Web Docs"
[3]: https://datatracker.ietf.org/doc/html/rfc9110?utm_source=chatgpt.com "RFC 9110 - HTTP Semantics - Datatracker - IETF"
[4]: https://developer.mozilla.org/en-US/docs/Web/API/AbortSignal/timeout_static?utm_source=chatgpt.com "AbortSignal: timeout() static method - Web APIs | MDN"
[5]: https://nodejs.org/en/blog/announcements/v18-release-announce?utm_source=chatgpt.com "Node.js 18 is now available!"
[6]: https://axios-http.com/docs/handling_errors?utm_source=chatgpt.com "Handling Errors | Axios Docs"
