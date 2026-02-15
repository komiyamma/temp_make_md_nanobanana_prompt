# 第22章：HTTP失敗を分ける（通信 vs HTTPステータス）🌐🚦

この章でやりたいことはシンプル👇✨
**「HTTPが失敗したっぽい」を、ちゃんと“別の失敗”に分ける**ことです😊

* ✅ **通信に失敗した**（そもそも届いてない）
* ✅ **HTTPとして返ってきたけど失敗**（404/500 など）
* ✅ **タイムアウト**（待つのをやめた）
* ✅ **キャンセル**（ユーザーが戻った等で中断）
* ✅ **JSON壊れてる / 期待と違う**（パース or 検証で失敗）

これが分けられると、UIも運用もめっちゃ強くなります💪💖

---

## 1) まず知っておく「fetchの罠」🕳️😱

![Fetch Promise Resolution](./picture/err_model_ts_study_022_fetch_gotcha.png)

`fetch()` は **ネットワーク系の失敗だけ** Promise を reject します。
**404 や 500 は reject しません**（普通に resolve して `Response` が返ってきます）😵‍💫
だから **`catch` だけ見てると事故る**んだよね💥 ([MDN Web Docs][1])

そして「成功かどうか」は `response.ok`（200〜299）で判断します✅ ([MDN Web Docs][2])

---

## 2) “失敗の種類”を地図にする🗺️🏷️

![HTTP Failure Categories](./picture/err_model_ts_study_022_failure_bins.png)

ここから先、HTTPクライアントの結果を **いつも同じ形**に揃えます✨

### A. 通信失敗（ネットワーク）📡❌

例：

* オフライン、DNS失敗、接続拒否、TLS失敗
* ブラウザだと **CORSもネットワークエラーっぽく**見える（詳細は隠されがち） ([MDN Web Docs][1])

### B. タイムアウト⏳💥

`fetch` はタイムアウトを自動でやってくれないので、自分で中断する必要あり。
`AbortSignal.timeout(ms)` が使える環境なら超ラク（Node.js でも定義あり）⏱️ ([Node.js][3])

### C. キャンセル（Abort）🛑👋

画面遷移・検索入力の連打などで「前の通信いらない！」ってなるやつ。

### D. HTTPステータス失敗（4xx/5xx）🚦

**返ってきてる**のがポイント。届いてる。だから“通信”とは別。

* 4xx = クライアント側がミスってそう ([RFCエディタ][4])
* 5xx = サーバー側が死んでそう ([IETF Datatracker][5])
* ステータス一覧はMDNが見やすいよ📚 ([MDN Web Docs][6])

さらに、**429/503** は `Retry-After` で「何秒待って」って来ることがあるので、リトライ設計と相性がいい✨ ([MDN Web Docs][7])

### E. パース失敗 / 形式違い🧩😵

* 204 No Content なのに `json()` 呼んで爆死
* JSON壊れてる
* `Content-Type` が想定と違う

---

## 3) “統一結果”の設計（Resultで返す）🎁🌈

![Unified Result Wrapper](./picture/err_model_ts_study_022_unified_box.png)

ここでは **`Promise<Result<T, HttpError>>`** を返す形にします😊
（第19章の AsyncResult のノリだね⚡）

### エラー型の例（判別可能ユニオン）🏷️

```ts
export type Result<T, E> =
  | { ok: true; value: T }
  | { ok: false; error: E };

export const Ok = <T>(value: T): Result<T, never> => ({ ok: true, value });
export const Err = <E>(error: E): Result<never, E> => ({ ok: false, error });

export type HttpError =
  | {
      kind: "Network";
      message: string;
      url: string;
      retryable: true;
      cause?: unknown;
    }
  | {
      kind: "Timeout";
      message: string;
      url: string;
      retryable: true;
      timeoutMs: number;
      cause?: unknown;
    }
  | {
      kind: "Aborted";
      message: string;
      url: string;
      retryable: false;
      cause?: unknown;
    }
  | {
      kind: "HttpStatus";
      message: string;
      url: string;
      status: number;
      retryable: boolean;
      retryAfterMs?: number;
      // 取り出せた範囲で（安全な範囲で）ボディを少しだけ持つのもアリ
      bodyText?: string;
    }
  | {
      kind: "Parse";
      message: string;
      url: string;
      retryable: false;
      contentType?: string | null;
      cause?: unknown;
    };
```

---

## 4) fetchラッパー実装（成功/失敗を統一する）🧰✨

![Fetch Wrapper Logic](./picture/err_model_ts_study_022_pipeline_funnel.png)

ポイントは3つ👇

1. **タイムアウト or Abort** を用意
2. `fetch` の `try/catch` は **通信系**を拾う
3. `response.ok` で **HTTP失敗**を拾う ([MDN Web Docs][1])

```ts
const getRetryAfterMs = (res: Response): number | undefined => {
  const v = res.headers.get("Retry-After");
  if (!v) return undefined;

  // Retry-After は seconds か HTTP-date
  const seconds = Number(v);
  if (Number.isFinite(seconds)) return Math.max(0, seconds) * 1000;

  const dateMs = Date.parse(v);
  if (!Number.isNaN(dateMs)) return Math.max(0, dateMs - Date.now());

  return undefined;
};

const isAbortError = (e: unknown): boolean =>
  typeof e === "object" &&
  e !== null &&
  "name" in e &&
  (e as any).name === "AbortError";

const toNetworkLikeError = (url: string, e: unknown): HttpError => {
  // ブラウザの fetch はネットワークエラーを TypeError で返すことが多い
  // CORS もここに寄ることがある :contentReference[oaicite:9]{index=9}
  return {
    kind: "Network",
    message: "通信に失敗したよ…（ネットワーク）",
    url,
    retryable: true,
    cause: e,
  };
};

export async function fetchJson<T>(
  url: string,
  init: RequestInit & { timeoutMs?: number } = {}
): Promise<Result<T, HttpError>> {
  const { timeoutMs = 10_000, ...rest } = init;

  // AbortSignal.timeout がある環境なら使う（Node.js でも定義あり） :contentReference[oaicite:10]{index=10}
  const controller = new AbortController();

  let timeoutId: number | undefined;
  const signal =
    typeof (AbortSignal as any)?.timeout === "function"
      ? (AbortSignal as any).timeout(timeoutMs)
      : undefined;

  // 2つの signal をまとめたい時は AbortSignal.any が便利だけど、
  // 環境差や既知の挙動差もありえるので、ここでは “手動で中断” の安定版に寄せる🙆‍♀️
  // （＝タイマーで controller.abort()）
  timeoutId = window.setTimeout(() => controller.abort(), timeoutMs);

  try {
    const res = await fetch(url, { ...rest, signal: controller.signal });

    // HTTPとして返ってきたけど失敗（404/500など）
    if (!res.ok) {
      const retryAfterMs = getRetryAfterMs(res); // 429/503 で来ることがある :contentReference[oaicite:11]{index=11}

      // 可能ならボディを少し読む（読みすぎ注意）
      let bodyText: string | undefined;
      try {
        bodyText = await res.text();
        if (bodyText.length > 500) bodyText = bodyText.slice(0, 500) + "…";
      } catch {
        // 読めないなら無視でOK
      }

      const retryable =
        res.status === 429 || res.status === 503 || res.status === 502 || res.status === 504;

      return Err({
        kind: "HttpStatus",
        message: `サーバーがエラーを返したよ（HTTP ${res.status}）`,
        url,
        status: res.status,
        retryable,
        retryAfterMs,
        bodyText,
      });
    }

    // 成功：JSONを読む（Content-Typeチェックは好みで強化）
    try {
      const data = (await res.json()) as T;
      return Ok(data);
    } catch (e) {
      return Err({
        kind: "Parse",
        message: "JSONの読み取りに失敗したよ…（形式が想定と違うかも）",
        url,
        retryable: false,
        contentType: res.headers.get("Content-Type"),
        cause: e,
      });
    }
  } catch (e) {
    if (isAbortError(e)) {
      // タイムアウト or キャンセルを区別したいなら、別のフラグを持つとさらに良い
      return Err({
        kind: "Timeout",
        message: "タイムアウトしたよ…（待ち時間オーバー）",
        url,
        retryable: true,
        timeoutMs,
        cause: e,
      });
    }

    return Err(toNetworkLikeError(url, e));
  } finally {
    if (timeoutId !== undefined) window.clearTimeout(timeoutId);
  }
}
```

> ※ `fetch` 自体の仕様は Fetch Standard（Living Standard）で定義されてて、更新も続いてるよ📜✨（最終更新 2026-01-13） ([Fetch Standard][8])

---

## 5) 使う側：UIで“反応”を変える😊🎀

![UI Reaction to Errors](./picture/err_model_ts_study_022_dashboard_reaction.png)

```ts
const r = await fetchJson<{ name: string }>("/api/me");

if (r.ok) {
  console.log("こんにちは", r.value.name);
} else {
  switch (r.error.kind) {
    case "Network":
      // 例：トースト「通信環境を確認してね」
      break;

    case "Timeout":
      // 例：再試行ボタンを出す
      break;

    case "Aborted":
      // 例：何もしない（検索の途中キャンセルとか）
      break;

    case "HttpStatus":
      // 例：401ならログイン誘導、429/503なら少し待って再試行など
      break;

    case "Parse":
      // 例：障害報告導線（ログは詳しく、表示は簡潔に）
      break;
  }
}
```

---

## 6) “リトライしていい？”の目安🔁🧠

![Retry Gatekeeper](./picture/err_model_ts_study_022_gatekeeper.png)

HTTPの意味としてはざっくりこんな感じ👇（超実用だけに絞るね😊）

* ✅ **リトライしがち**：Network / Timeout / 502 / 503 / 504 / 429

  * 503 は “一時的に無理” が多い ([MDN Web Docs][9])
  * 429/503 は `Retry-After` が来ることがある ([MDN Web Docs][7])
* ❌ **だいたいリトライしない**：400 / 401 / 403 / 404 / 422
  （入力・認証・権限・URLミスのことが多い）
* ⚠️ **POST等はリトライ注意**：二重購入みたいな事故が起きるので、やるなら「冪等性キー」等が必要（第29章でやる予定の領域だよ🧷🙂）

---

## 7) ミニ演習📝💖

![Fetch Experiment](./picture/err_model_ts_study_022_lab_experiment.png)

### 演習1：失敗をわざと起こして分類する🧪

* 404 を返すURL（存在しない）
* 500 を返すURL（テスト用）
* オフラインにして Network
* timeoutMs を短くして Timeout

「どれがどの `kind` になる？」を表にしてね📋✨

### 演習2：`HttpStatus` の扱いを丁寧にする🎀

* 401 → ログイン導線
* 403 → 権限なし表示
* 404 → “見つからない”
* 429/503 → “少し待って再試行” + Retry-Afterがあれば秒数表示

### 演習3：`Parse` を強化する🧼

* `Content-Type` が `application/json` じゃなかったら Parse 扱い
* 204 No Content は `Ok(undefined)` にするとか、方針を決めて実装✨

---

## 8) AI活用プロンプト🤖💬（コピペOK）

* 「このAPI呼び出しの失敗ケースを、Network/Timeout/HttpStatus/Parse に分類して一覧にして」
* 「HTTP 4xx/5xx のうち、ユーザーに“再試行”を出すべきものだけ理由付きで選んで」 ([RFCエディタ][4])
* 「この `HttpError` 型、情報が多すぎ/少なすぎをレビューして。改善案も」
* 「Retry-After を seconds と HTTP-date の両方で解釈する実装にして」 ([MDN Web Docs][7])

---

## まとめ🎉✨

* `fetch` は **通信失敗だけ catch**、HTTPエラー（404/500）は **`response.ok` で拾う** ([MDN Web Docs][1])
* 失敗を **Network / Timeout / Abort / HttpStatus / Parse** に分けると、UIも運用も強くなる💪💖
* 429/503 は `Retry-After` も見て、リトライ設計に活かすとスマート🔁✨ ([MDN Web Docs][7])

次の章（第23章）は、相手APIのエラー形式がバラバラでも、こっち側で“正規化”して統一する話に繋がるよ〜🌩️🧼

[1]: https://developer.mozilla.org/ja/docs/Web/API/Fetch_API/Using_Fetch?utm_source=chatgpt.com "フェッチ API の使用 - MDN Web Docs"
[2]: https://developer.mozilla.org/ja/docs/Web/API/Response/ok?utm_source=chatgpt.com "Response: ok プロパティ - Web API - MDN Web Docs"
[3]: https://nodejs.org/download/release//v16.14.0/docs/api/globals.html?utm_source=chatgpt.com "Global objects | Node.js v16.14.0 Documentation"
[4]: https://www.rfc-editor.org/rfc/rfc9110.html?utm_source=chatgpt.com "RFC 9110: HTTP Semantics"
[5]: https://datatracker.ietf.org/doc/html/rfc9110?utm_source=chatgpt.com "RFC 9110 - HTTP Semantics - Datatracker - IETF"
[6]: https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status?utm_source=chatgpt.com "HTTP response status codes - MDN Web Docs - Mozilla"
[7]: https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Retry-After?utm_source=chatgpt.com "Retry-After header - HTTP - MDN Web Docs"
[8]: https://fetch.spec.whatwg.org/ "Fetch Standard"
[9]: https://developer.mozilla.org/ja/docs/Web/HTTP/Reference/Status/503?utm_source=chatgpt.com "503 Service Unavailable - HTTP - MDN Web Docs"
